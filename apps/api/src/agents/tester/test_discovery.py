"""
Test Discovery Engine

Scans a repository workspace to find:
  - Test frameworks in use (pytest, jest, vitest, cargo test, go test)
  - Existing test files and naming patterns
  - Coverage configuration (pytest.ini, jest.config.js, etc.)
  - Test folders

Returns a structured TestDiscoveryResult used by the TesterAgent to decide
which files need tests generated and which already have coverage.
"""
import logging
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ─── Framework Signatures ────────────────────────────────────────────────────

FRAMEWORK_SIGNATURES = {
    "pytest": {
        "config_files": ["pytest.ini", "pyproject.toml", "setup.cfg", "conftest.py"],
        "test_patterns": ["test_*.py", "*_test.py"],
        "test_dirs": ["tests", "test"],
        "run_cmd": "pytest --tb=short -v --json-report --json-report-file=/tmp/test_results.json",
        "coverage_cmd": "pytest --cov=. --cov-report=json:/tmp/coverage.json",
        "language": "python",
    },
    "jest": {
        "config_files": ["jest.config.js", "jest.config.ts", "jest.config.json"],
        "test_patterns": ["*.test.ts", "*.test.js", "*.spec.ts", "*.spec.js"],
        "test_dirs": ["__tests__", "tests", "test"],
        "run_cmd": "npx jest --json --outputFile=/tmp/test_results.json",
        "coverage_cmd": "npx jest --coverage --json --outputFile=/tmp/test_results.json",
        "language": "typescript",
    },
    "vitest": {
        "config_files": ["vitest.config.ts", "vitest.config.js", "vite.config.ts"],
        "test_patterns": ["*.test.ts", "*.spec.ts"],
        "test_dirs": ["__tests__", "tests"],
        "run_cmd": "npx vitest run --reporter=json --outputFile=/tmp/test_results.json",
        "coverage_cmd": "npx vitest run --coverage",
        "language": "typescript",
    },
    "cargo": {
        "config_files": ["Cargo.toml"],
        "test_patterns": [],  # Cargo tests are inline
        "test_dirs": ["tests"],
        "run_cmd": "cargo test -- -Z unstable-options --format json 2>/tmp/test_results.json",
        "coverage_cmd": "cargo test",
        "language": "rust",
    },
    "go": {
        "config_files": ["go.mod"],
        "test_patterns": ["*_test.go"],
        "test_dirs": ["."],
        "run_cmd": "go test ./... -v -json > /tmp/test_results.json",
        "coverage_cmd": "go test ./... -coverprofile=/tmp/coverage.out",
        "language": "go",
    },
}


@dataclass
class TestDiscoveryResult:
    framework: str
    language: str
    existing_test_files: list[str] = field(default_factory=list)
    source_files_without_tests: list[str] = field(default_factory=list)
    config_files: list[str] = field(default_factory=list)
    run_command: str = ""
    coverage_command: str = ""
    test_dir: str = "tests"


class TestDiscoveryEngine:
    """
    Scans the workspace directory and returns a TestDiscoveryResult
    identifying the framework, existing tests, and files needing coverage.
    """

    def discover(self, workspace_path: Path) -> TestDiscoveryResult:
        logger.info(f"[TestDiscovery] Scanning {workspace_path}")

        framework, config = self._detect_framework(workspace_path)
        logger.info(f"[TestDiscovery] Detected framework: {framework}")

        existing_tests = self._find_test_files(workspace_path, config)
        source_files = self._find_source_files(workspace_path, config["language"])
        uncovered = self._find_uncovered_files(source_files, existing_tests, workspace_path)
        found_configs = self._find_config_files(workspace_path, config["config_files"])

        result = TestDiscoveryResult(
            framework=framework,
            language=config["language"],
            existing_test_files=[str(f.relative_to(workspace_path)) for f in existing_tests],
            source_files_without_tests=[str(f) for f in uncovered],
            config_files=[str(f.relative_to(workspace_path)) for f in found_configs],
            run_command=config["run_cmd"],
            coverage_command=config["coverage_cmd"],
            test_dir=config["test_dirs"][0] if config["test_dirs"] else "tests",
        )
        logger.info(
            f"[TestDiscovery] Found {len(existing_tests)} test files, "
            f"{len(uncovered)} source files needing tests"
        )
        return result

    def _detect_framework(self, workspace_path: Path) -> tuple[str, dict]:
        for framework, config in FRAMEWORK_SIGNATURES.items():
            for config_file in config["config_files"]:
                if (workspace_path / config_file).exists():
                    return framework, config
        # Default to pytest for unknown
        return "pytest", FRAMEWORK_SIGNATURES["pytest"]

    def _find_test_files(self, workspace_path: Path, config: dict) -> list[Path]:
        results = []
        patterns = config["test_patterns"]
        for pattern in patterns:
            results.extend(workspace_path.rglob(pattern))
        # Exclude common non-test dirs
        return [f for f in results if ".git" not in f.parts and "node_modules" not in f.parts]

    def _find_source_files(self, workspace_path: Path, language: str) -> list[Path]:
        ext_map = {
            "python": ["*.py"],
            "typescript": ["*.ts", "*.tsx"],
            "javascript": ["*.js", "*.jsx"],
            "rust": ["*.rs"],
            "go": ["*.go"],
        }
        exts = ext_map.get(language, ["*.py"])
        results = []
        for ext in exts:
            results.extend(workspace_path.rglob(ext))

        # Filter out test files, migrations, configs, __pycache__
        excluded = {"node_modules", ".git", "__pycache__", "migrations", "dist", "build", ".venv"}
        return [
            f for f in results
            if not any(part in excluded for part in f.parts)
            and "test" not in f.name.lower()
            and "conftest" not in f.name.lower()
        ]

    def _find_uncovered_files(
        self,
        source_files: list[Path],
        test_files: list[Path],
        workspace_path: Path
    ) -> list[Path]:
        """Find source files that don't have a corresponding test file."""
        tested_modules = set()
        for tf in test_files:
            stem = tf.stem.replace("test_", "").replace("_test", "")
            tested_modules.add(stem)

        uncovered = []
        for sf in source_files:
            if sf.stem not in tested_modules and sf.stat().st_size > 100:
                uncovered.append(sf.relative_to(workspace_path))

        return uncovered[:10]  # Cap to avoid token overflow

    def _find_config_files(self, workspace_path: Path, config_files: list[str]) -> list[Path]:
        found = []
        for cfg in config_files:
            p = workspace_path / cfg
            if p.exists():
                found.append(p)
        return found


test_discovery = TestDiscoveryEngine()
