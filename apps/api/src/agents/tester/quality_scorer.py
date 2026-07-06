"""
Quality Scorer

Evaluates test coverage, pass rates, and failure severity to produce a final 
QualityReport with a calculated score (0-100) and an orchestration recommendation.
"""
import logging
from src.agents.tester.failure_analyzer import DiagnosedFailure, ParsedTestResult

logger = logging.getLogger(__name__)


class QualityScorer:
    """
    Calculates overall quality metrics and recommends an orchestration action.
    """

    def score(
        self,
        results: list[ParsedTestResult],
        failures: list[DiagnosedFailure],
        line_coverage: float = 0.0,
    ) -> dict:
        """
        Calculates quality metrics.
        Returns a dict that maps directly to the QualityReport database model.
        """
        total = len(results)
        if total == 0:
            return {
                "quality_score": 0.0,
                "pass_rate": 0.0,
                "coverage_score": line_coverage,
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0,
                "recommendation": "ESCALATE",
                "summary": "No tests were found or executed.",
            }

        passed = sum(1 for r in results if r.status == "PASSED")
        failed = sum(1 for r in results if r.status in ("FAILED", "ERROR"))
        skipped = sum(1 for r in results if r.status == "SKIPPED")

        pass_rate = (passed / (total - skipped)) * 100.0 if (total - skipped) > 0 else 0.0

        # Base score is pass rate
        quality_score = pass_rate

        # Penalty for critical failures
        critical_failures = sum(1 for f in failures if f.severity == "CRITICAL")
        high_failures = sum(1 for f in failures if f.severity == "HIGH")

        quality_score -= (critical_failures * 10.0)
        quality_score -= (high_failures * 5.0)

        # Factor in coverage (up to 20% boost if pass rate is good)
        if pass_rate > 80.0 and line_coverage > 50.0:
            quality_score += ((line_coverage - 50.0) / 50.0) * 10.0

        # Clamp between 0 and 100
        quality_score = max(0.0, min(100.0, quality_score))

        # Recommendation logic
        if pass_rate == 100.0:
            recommendation = "APPROVE"
            summary = "All tests passed successfully."
        elif quality_score >= 80.0 and critical_failures == 0:
            recommendation = "APPROVE"
            summary = f"Good quality ({quality_score:.1f}/100), some minor failures."
        elif quality_score >= 40.0:
            recommendation = "RETRY"
            summary = f"Failures detected ({failed}). Recommending a retry cycle."
        else:
            recommendation = "ESCALATE"
            summary = f"Critical failures detected ({critical_failures}). Escalating to human."

        logger.info(
            f"[QualityScorer] pass_rate={pass_rate:.1f}% coverage={line_coverage:.1f}% "
            f"score={quality_score:.1f} rec={recommendation}"
        )

        return {
            "quality_score": quality_score,
            "pass_rate": pass_rate,
            "coverage_score": line_coverage,
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "skipped_tests": skipped,
            "recommendation": recommendation,
            "summary": summary,
        }

quality_scorer = QualityScorer()
