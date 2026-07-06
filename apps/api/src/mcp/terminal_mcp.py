"""
Terminal MCP — Secure command runner for sandbox execution.

Provides a whitelist-based command validator that prevents dangerous commands from
being executed inside the sandbox container.

Allowed commands cover:
  - Node.js / JS toolchains: npm, pnpm, yarn, bun
  - Python toolchains: pip, pip3, python, python3, poetry, pytest, ruff
  - Rust: cargo
  - Go: go
  - Java: mvn, gradle
  - .NET: dotnet
  - Build/Utils: make, bash -c (limited)

Rejected by default:
  - rm -rf / or rm -rf /important
  - curl | sh, wget | bash (pipe to shell)
  - chmod, chown on system dirs
  - Any command starting with sudo
"""
import re
import logging
from typing import Literal

logger = logging.getLogger(__name__)

# Commands that are explicitly allowed as the starting token
ALLOWED_PREFIXES = {
    "npm",
    "npx",
    "pnpm",
    "yarn",
    "bun",
    "pip",
    "pip3",
    "python",
    "python3",
    "poetry",
    "pytest",
    "ruff",
    "mypy",
    "flake8",
    "cargo",
    "go",
    "mvn",
    "gradle",
    "gradlew",
    "mvnw",
    "dotnet",
    "make",
    "node",
    "vitest",
    "jest",
    "mocha",
    "eslint",
    "prettier",
    "tsc",
    "vite",
    "next",
    "nuxt",
    "svelte-kit",
    "gatsby",
    "turbo",
}

# Patterns that are always rejected regardless of prefix
REJECTED_PATTERNS = [
    r"rm\s+-rf?\s+/",          # rm -rf /
    r"curl.+\|\s*(bash|sh)",   # curl | bash / sh
    r"wget.+\|\s*(bash|sh)",   # wget | bash / sh
    r"sudo\b",                 # sudo anything
    r"dd\s+if=",               # dd disk write
    r"mkfs\.",                 # filesystem format
    r">\s*/dev/",              # write to /dev
    r"chmod\s+777",            # chmod 777
    r":\(\)\s*\{.*\}&",        # fork bomb
]

REJECTED_REGEXES = [re.compile(p, re.IGNORECASE) for p in REJECTED_PATTERNS]


class CommandValidationError(Exception):
    pass


class TerminalMCP:
    """
    Validates and executes commands safely inside a SandboxContainer.
    """

    def validate(self, command: str) -> None:
        """
        Validates a command against the allowlist and reject patterns.
        Raises CommandValidationError if the command is not permitted.
        """
        cmd = command.strip()

        # Check rejected patterns first (highest priority)
        for pattern in REJECTED_REGEXES:
            if pattern.search(cmd):
                raise CommandValidationError(f"Command blocked by security policy: '{cmd}'")

        # Extract the first token (the executable)
        first_token = cmd.split()[0] if cmd.split() else ""
        # Strip any path prefix (e.g. ./gradlew -> gradlew)
        executable = first_token.lstrip("./").lower()

        if executable not in ALLOWED_PREFIXES:
            raise CommandValidationError(
                f"Command '{executable}' is not in the allowlist. "
                f"Allowed: {sorted(ALLOWED_PREFIXES)}"
            )

    def run(
        self,
        container,
        command: str,
        phase: str = "UNKNOWN",
    ) -> tuple[int, str, str]:
        """
        Validates and executes a command in the sandbox container.
        Returns (exit_code, stdout, stderr).
        """
        self.validate(command)
        logger.info(f"[TerminalMCP] [{phase}] Running: {command}")
        exit_code, stdout, stderr = container.exec_command(command)
        logger.info(f"[TerminalMCP] [{phase}] exit_code={exit_code}")
        return exit_code, stdout, stderr


terminal_mcp = TerminalMCP()
