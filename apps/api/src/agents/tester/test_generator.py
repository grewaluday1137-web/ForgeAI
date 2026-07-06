"""
AI Test Generator

Uses the configured LLM provider to generate missing unit tests for source files
that were identified as lacking coverage by the TestDiscoveryEngine.

Builds a rich prompt including:
  - Architecture summary
  - Source file content (capped to avoid token limits)
  - Example existing test patterns
  - The target framework and language

Returns structured TestGenerationResult objects parsed from the AI JSON response.
"""
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field

from src.agents.prompts.tester import TESTER_SYSTEM_PROMPT
from src.agents.tester.test_discovery import TestDiscoveryResult
from src.agents.providers.factory import get_provider

logger = logging.getLogger(__name__)

MAX_SOURCE_CHARS = 6000
MAX_EXAMPLE_CHARS = 2000
MAX_FILES_TO_TEST = 5


@dataclass
class GeneratedTestSuite:
    file_path: str
    framework: str
    test_code: str
    test_cases: list[dict] = field(default_factory=list)


@dataclass
class TestGenerationResult:
    suites: list[GeneratedTestSuite] = field(default_factory=list)
    notes: str = ""
    raw_response: str = ""


class TestGenerator:
    """
    Builds context-rich prompts and calls the LLM to generate test suites.
    """

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path

    async def generate(
        self,
        discovery: TestDiscoveryResult,
        architecture_summary: str = "",
        task_description: str = "",
    ) -> TestGenerationResult:
        """
        Generate tests for uncovered source files.
        Returns a TestGenerationResult with all generated suites.
        """
        if not discovery.source_files_without_tests:
            logger.info("[TestGenerator] No uncovered source files found, skipping generation")
            return TestGenerationResult()

        source_snippets = self._collect_source_snippets(discovery)
        existing_examples = self._collect_example_tests(discovery)

        prompt = self._build_prompt(
            discovery=discovery,
            source_snippets=source_snippets,
            existing_examples=existing_examples,
            architecture_summary=architecture_summary,
            task_description=task_description,
        )

        try:
            provider = get_provider()
            messages = [
                {"role": "system", "content": TESTER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]
            raw = await provider.complete(messages)
            return self._parse_response(raw)
        except Exception as e:
            logger.error(f"[TestGenerator] LLM call failed: {e}")
            return TestGenerationResult(notes=f"Generation failed: {e}")

    def _collect_source_snippets(self, discovery: TestDiscoveryResult) -> str:
        snippets = []
        for rel_path_str in discovery.source_files_without_tests[:MAX_FILES_TO_TEST]:
            full_path = self.workspace_path / rel_path_str
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding="utf-8", errors="replace")
                    snippet = content[:MAX_SOURCE_CHARS]
                    snippets.append(f"### {rel_path_str}\n```\n{snippet}\n```")
                except Exception:
                    pass
        return "\n\n".join(snippets)

    def _collect_example_tests(self, discovery: TestDiscoveryResult) -> str:
        if not discovery.existing_test_files:
            return ""
        example_path = self.workspace_path / discovery.existing_test_files[0]
        try:
            content = example_path.read_text(encoding="utf-8", errors="replace")
            return content[:MAX_EXAMPLE_CHARS]
        except Exception:
            return ""

    def _build_prompt(
        self,
        discovery: TestDiscoveryResult,
        source_snippets: str,
        existing_examples: str,
        architecture_summary: str,
        task_description: str,
    ) -> str:
        parts = [
            f"## Project Context",
            f"Framework: {discovery.framework}",
            f"Language: {discovery.language}",
            f"Test directory: {discovery.test_dir}",
        ]

        if architecture_summary:
            parts.append(f"\n## Architecture Summary\n{architecture_summary[:1000]}")

        if task_description:
            parts.append(f"\n## Recent Change\n{task_description}")

        if existing_examples:
            parts.append(f"\n## Existing Test Style (follow this pattern)\n```\n{existing_examples}\n```")

        parts.append(f"\n## Source Files to Test\n{source_snippets}")
        parts.append("\nGenerate comprehensive tests. Return JSON only.")

        return "\n".join(parts)

    def _parse_response(self, raw: str) -> TestGenerationResult:
        """Parses the LLM JSON response into a TestGenerationResult."""
        # Strip markdown fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[1:])
        if cleaned.endswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[:-1])

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to find JSON within the response
            start = cleaned.find("{")
            end = cleaned.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    data = json.loads(cleaned[start:end])
                except Exception:
                    logger.warning("[TestGenerator] Could not parse LLM response as JSON")
                    return TestGenerationResult(raw_response=raw, notes="Parse error")
            else:
                return TestGenerationResult(raw_response=raw, notes="Parse error")

        suites = []
        for suite_data in data.get("test_suites", []):
            suites.append(GeneratedTestSuite(
                file_path=suite_data.get("file_path", "tests/test_generated.py"),
                framework=suite_data.get("framework", "pytest"),
                test_code=suite_data.get("test_code", ""),
                test_cases=suite_data.get("test_cases", []),
            ))

        return TestGenerationResult(
            suites=suites,
            notes=data.get("notes", ""),
            raw_response=raw,
        )
