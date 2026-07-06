"""
Failure Analyzer

Parses raw test execution output (stdout/stderr) and classifies each failure
into a structured FailureAnalysis with a category, root cause, and suggested fix.

Supports both rule-based classification (fast) and AI-assisted diagnosis (deep).
"""
import re
import logging
from dataclasses import dataclass

from src.models.enums import FailureCategory

logger = logging.getLogger(__name__)


@dataclass
class ParsedTestResult:
    name: str
    status: str  # PASSED, FAILED, SKIPPED, ERROR
    duration_ms: float = 0.0
    error_message: str = ""
    stack_trace: str = ""


@dataclass
class DiagnosedFailure:
    test_name: str
    category: FailureCategory
    root_cause: str
    suggested_fix: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    is_flaky: bool = False


# ─── Rule-based classifiers ───────────────────────────────────────────────────

CLASSIFICATION_RULES = [
    (FailureCategory.SYNTAX,      r"SyntaxError|IndentationError|invalid syntax|ParseError|Unexpected token"),
    (FailureCategory.ASSERTION,   r"AssertionError|assert|expect\(|toBe|toEqual|FAILED.*assert"),
    (FailureCategory.DEPENDENCY,  r"ModuleNotFoundError|ImportError|Cannot find module|No module named|npm ERR"),
    (FailureCategory.RUNTIME,     r"TypeError|AttributeError|NameError|RuntimeError|ReferenceError|undefined is not"),
    (FailureCategory.BUILD,       r"Build failed|compilation failed|FAILED to compile|error TS"),
    (FailureCategory.ENVIRONMENT, r"ConnectionRefused|timeout|ECONNREFUSED|database.*error|redis.*error"),
    (FailureCategory.FLAKY,       r"flaky|intermittent|race condition|timing|sleep"),
]

SEVERITY_MAP = {
    FailureCategory.SYNTAX:      "CRITICAL",
    FailureCategory.BUILD:       "CRITICAL",
    FailureCategory.DEPENDENCY:  "HIGH",
    FailureCategory.RUNTIME:     "HIGH",
    FailureCategory.ASSERTION:   "MEDIUM",
    FailureCategory.ENVIRONMENT: "MEDIUM",
    FailureCategory.FLAKY:       "LOW",
    FailureCategory.UNKNOWN:     "MEDIUM",
}

SUGGESTED_FIXES = {
    FailureCategory.SYNTAX:      "Fix the syntax error indicated in the stack trace. Check for missing colons, brackets, or indentation issues.",
    FailureCategory.ASSERTION:   "The test expectation doesn't match the actual output. Review the function's return value and update either the implementation or the test assertion.",
    FailureCategory.DEPENDENCY:  "A required module is missing. Check imports and run the install command to update dependencies.",
    FailureCategory.RUNTIME:     "A runtime exception occurred. Add null checks, validate input types, and handle edge cases in the implementation.",
    FailureCategory.BUILD:       "The build step failed. Check for TypeScript errors or compilation issues before running tests.",
    FailureCategory.ENVIRONMENT: "An environment-level failure occurred (DB/Redis/network). Ensure all services are running and check connection config.",
    FailureCategory.FLAKY:       "This test may be flaky. Consider adding retry logic or improving test isolation.",
    FailureCategory.UNKNOWN:     "Review the full stack trace to identify the root cause.",
}


class FailureAnalyzer:
    """
    Parses stdout/stderr from test runners and produces structured DiagnosedFailure records.
    """

    def parse_pytest_output(self, stdout: str, stderr: str) -> list[ParsedTestResult]:
        """Parse pytest verbose output into individual test results."""
        results = []
        lines = (stdout + "\n" + stderr).splitlines()

        for line in lines:
            # Match lines like: PASSED tests/test_x.py::test_foo (0.01s)
            # or: FAILED tests/test_x.py::test_bar - AssertionError
            passed = re.match(r"^(PASSED|FAILED|ERROR|SKIPPED)\s+(.+?)(\s+\([\d.]+s\))?$", line)
            if passed:
                status = passed.group(1)
                name = passed.group(2).strip()
                results.append(ParsedTestResult(name=name, status=status))

        # If no structured results found, create a summary result from raw output
        if not results and ("FAILED" in stdout or "ERROR" in stdout):
            results.append(ParsedTestResult(
                name="test_run",
                status="FAILED",
                error_message=(stdout + stderr)[:2000],
            ))
        elif not results and "passed" in stdout.lower():
            results.append(ParsedTestResult(name="test_run", status="PASSED"))

        return results

    def parse_jest_output(self, stdout: str, stderr: str) -> list[ParsedTestResult]:
        """Parse Jest/Vitest output into individual test results."""
        results = []
        # Try to parse structured output
        lines = (stdout + "\n" + stderr).splitlines()
        for line in lines:
            if "✓" in line or "✗" in line or "×" in line or "PASS" in line or "FAIL" in line:
                status = "PASSED" if ("✓" in line or "PASS" in line) else "FAILED"
                results.append(ParsedTestResult(name=line.strip()[:200], status=status))

        if not results:
            overall = "PASSED" if "Tests:" in stdout and "failed" not in stdout.lower() else "FAILED"
            results.append(ParsedTestResult(
                name="jest_run",
                status=overall,
                error_message=(stdout + stderr)[:2000],
            ))
        return results

    def classify_failure(self, test_result: ParsedTestResult) -> DiagnosedFailure:
        """Classify a failed test result into a structured diagnosis."""
        text = f"{test_result.error_message}\n{test_result.stack_trace}"
        category = FailureCategory.UNKNOWN

        for cat, pattern in CLASSIFICATION_RULES:
            if re.search(pattern, text, re.IGNORECASE):
                category = cat
                break

        # Detect potential flakiness
        is_flaky = bool(re.search(CLASSIFICATION_RULES[-1][1], text, re.IGNORECASE))

        return DiagnosedFailure(
            test_name=test_result.name,
            category=category,
            root_cause=self._extract_root_cause(text),
            suggested_fix=SUGGESTED_FIXES[category],
            severity=SEVERITY_MAP[category],
            is_flaky=is_flaky,
        )

    def analyze_all(
        self,
        framework: str,
        stdout: str,
        stderr: str,
        exit_code: int,
    ) -> tuple[list[ParsedTestResult], list[DiagnosedFailure]]:
        """
        Full analysis: parse test output then diagnose all failures.
        Returns (parsed_results, diagnosed_failures).
        """
        # Parse based on framework
        if framework in ("jest", "vitest"):
            parsed = self.parse_jest_output(stdout, stderr)
        else:
            parsed = self.parse_pytest_output(stdout, stderr)

        failures = [
            self.classify_failure(r)
            for r in parsed
            if r.status in ("FAILED", "ERROR")
        ]

        logger.info(
            f"[FailureAnalyzer] framework={framework} "
            f"results={len(parsed)} failures={len(failures)}"
        )
        return parsed, failures

    def _extract_root_cause(self, text: str) -> str:
        """Extract the most informative error line from the output."""
        lines = text.splitlines()
        # Look for lines with Error: or FAILED
        for line in lines:
            stripped = line.strip()
            if any(kw in stripped for kw in ("Error:", "FAILED", "assert", "expected", "received")):
                return stripped[:300]
        # Fallback to first non-empty line
        for line in lines:
            if line.strip():
                return line.strip()[:300]
        return "Unknown error"


failure_analyzer = FailureAnalyzer()
