"""
Tester Agent

The autonomous Quality Assurance agent.
Orchestrates test discovery, AI test generation, sandbox execution, failure analysis,
and quality scoring.
"""
import time
# Force Docker Sync
import logging
import json
import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.agents.base import BaseAgent, AgentResult
from src.agents.context import ExecutionContext
from src.models.enums import AgentType, TestStatus, ExecutionStatus
from src.models.execution_runtime import ExecutionJob
from src.models.testing import TestSuite, TestCase, TestExecution, CoverageReport, FailureAnalysis, QualityReport
from src.db.session import AsyncSessionLocal
from src.websocket.manager import manager

from src.agents.tester.test_discovery import test_discovery
from src.agents.tester.test_generator import TestGenerator
from src.agents.tester.failure_analyzer import failure_analyzer
from src.agents.tester.quality_scorer import quality_scorer
from src.mcp.terminal_mcp import terminal_mcp
from src.mcp.docker_client import docker_mcp
from src.services.sandbox_engine import SandboxEngine
from src.services.git import git_service
from src.services.context_engine import ContextEngine

logger = logging.getLogger(__name__)


class TesterAgent(BaseAgent):
    @property
    def agent_type(self) -> AgentType:
        return AgentType.TESTER

    async def run(self, context: ExecutionContext) -> AgentResult:
        start_time = time.time()
        logger.info(f"[{self.agent_type.value}] Starting QA pipeline for workflow {context.workflow_id}")

        async with AsyncSessionLocal() as db:
            await self._emit("tester.started", context.workflow_id, "Tester Agent initialized.")

            # 1. Resolve workspace path
            owner, repo_name = context.repository_url.rstrip("/").split("/")[-2:]
            if repo_name.endswith(".git"):
                repo_name = repo_name[:-4]
            workspace_path = git_service.get_repo_path(owner, repo_name)
            
            # 2. Get the latest execution job to test against
            stmt = select(ExecutionJob).where(ExecutionJob.repository_id == context.repository_id).order_by(ExecutionJob.created_at.desc())
            res = await db.execute(stmt)
            job = res.scalars().first()
            if not job:
                return AgentResult(self.agent_type, False, {}, error="No ExecutionJob found to test.", duration_ms=0)
            
            # 3. Discovery
            discovery = test_discovery.discover(workspace_path)
            await self._emit("tester.discovery.completed", context.workflow_id, f"Found {len(discovery.existing_test_files)} existing test files.")
            
            # 4. Generate Missing Tests
            generator = TestGenerator(workspace_path)
            context_engine = ContextEngine(db)
            arch_ctx = await context_engine.get_repository_context(context.repository_id)
            
            gen_result = await generator.generate(
                discovery=discovery,
                architecture_summary=arch_ctx.get("architecture", {}).get("summary", ""),
                task_description=context.user_request,
            )
            
            for suite_data in gen_result.suites:
                # Write generated tests to the workspace
                out_path = workspace_path / suite_data.file_path
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(suite_data.test_code, encoding="utf-8")
                
                # Persist to DB
                suite = TestSuite(
                    execution_job_id=job.id,
                    repository_id=context.repository_id,
                    file_path=suite_data.file_path,
                    framework=suite_data.framework,
                    is_generated=True,
                    source_code=suite_data.test_code,
                    total_tests=len(suite_data.test_cases)
                )
                db.add(suite)
                await db.flush()
                
                for tc_data in suite_data.test_cases:
                    tc = TestCase(
                        suite_id=suite.id,
                        name=tc_data.get("name", "unnamed_test"),
                        description=tc_data.get("description", "")
                    )
                    db.add(tc)
            
            if gen_result.suites:
                await self._emit("tester.tests.generated", context.workflow_id, f"Generated {len(gen_result.suites)} new test suites.")
                await db.commit()

            # 5. Run tests via Sandbox
            await self._emit("tester.execution.started", context.workflow_id, "Running tests in isolated sandbox...")
            
            # Re-provision sandbox for testing
            sandbox = None
            try:
                sandbox = docker_mcp.create_sandbox(
                    image=test_discovery._detect_framework(workspace_path)[1]["image"],
                    workspace_path=str(workspace_path)
                )
                sandbox.start()
                
                # We assume dependencies are cached from the build step, but let's ensure install
                terminal_mcp.run(sandbox, test_discovery._detect_framework(workspace_path)[1]["install_cmd"], "TEST_INSTALL")
                
                # Run Tests
                exit_code, stdout, stderr = terminal_mcp.run(sandbox, discovery.run_command, "TEST_RUN")
                
                # Optional: Coverage (if command available)
                coverage_data = {}
                if discovery.coverage_command:
                    cov_exit, cov_out, cov_err = terminal_mcp.run(sandbox, discovery.coverage_command, "COVERAGE_RUN")
                    # Naive JSON parsing for coverage, assuming the framework dumped coverage to /tmp/test_results.json
                    try:
                        # For pytest/jest json reports
                        _, cat_out, _ = terminal_mcp.run(sandbox, "cat /tmp/test_results.json", "COVERAGE_READ")
                        coverage_data = json.loads(cat_out)
                    except Exception:
                        pass
                
                await self._emit("tester.execution.completed", context.workflow_id, "Test execution completed.")

            except Exception as e:
                logger.error(f"Sandbox test execution failed: {e}")
                exit_code, stdout, stderr = 1, "", str(e)
                coverage_data = {}
            finally:
                if sandbox:
                    sandbox.stop()
                    sandbox.remove()
                    
            # 6. Analyze Failures
            parsed_results, diagnosed_failures = failure_analyzer.analyze_all(discovery.framework, stdout, stderr, exit_code)
            
            # Link parsed results to DB (simplified for now, creating a single pseudo-suite for parsed results if we didn't generate them)
            # In a full implementation, we'd map test names to actual files.
            default_suite = TestSuite(
                execution_job_id=job.id,
                repository_id=context.repository_id,
                file_path="all_tests",
                framework=discovery.framework
            )
            db.add(default_suite)
            await db.flush()
            
            for pr in parsed_results:
                tc = TestCase(
                    suite_id=default_suite.id,
                    name=pr.name,
                    status=TestStatus[pr.status],
                    error_message=pr.error_message
                )
                db.add(tc)
                await db.flush()
                
                # If failed, add analysis
                df = next((f for f in diagnosed_failures if f.test_name == pr.name), None)
                if df:
                    analysis = FailureAnalysis(
                        test_case_id=tc.id,
                        category=df.category,
                        root_cause=df.root_cause,
                        suggested_fix=df.suggested_fix,
                        severity=df.severity,
                        is_flaky=df.is_flaky
                    )
                    db.add(analysis)
                    
            if diagnosed_failures:
                await self._emit("tester.failure.detected", context.workflow_id, f"Detected {len(diagnosed_failures)} test failures.")

            # 7. Coverage Report
            line_cov = 0.0
            if coverage_data:
                # Basic mapping for Jest/Pytest structure
                if "totals" in coverage_data: # Pytest cov
                    line_cov = coverage_data["totals"].get("percent_covered", 0.0)
                elif "total" in coverage_data: # Jest
                    line_cov = coverage_data["total"].get("lines", {}).get("pct", 0.0)
            
            cov_report = CoverageReport(
                execution_job_id=job.id,
                line_coverage=line_cov,
                raw_data=coverage_data
            )
            db.add(cov_report)
            await self._emit("tester.coverage.updated", context.workflow_id, f"Coverage calculated: {line_cov:.1f}%")

            # 8. Quality Scoring
            score_data = quality_scorer.score(parsed_results, diagnosed_failures, line_cov)
            quality_report = QualityReport(
                execution_job_id=job.id,
                **score_data
            )
            db.add(quality_report)
            
            await db.commit()
            
            duration = int((time.time() - start_time) * 1000)
            await self._emit("tester.completed", context.workflow_id, f"QA Pipeline completed. Recommendation: {score_data['recommendation']}")

            return AgentResult(
                agent_type=self.agent_type,
                success=True,
                output=score_data,
                duration_ms=duration
            )

    def validate(self, result: AgentResult) -> bool:
        return True

    async def _emit(self, event: str, workflow_id: str, message: str) -> None:
        payload = {"workflow_id": str(workflow_id), "message": message}
        try:
            await manager.broadcast_event(event, payload)
        except Exception:
            pass
