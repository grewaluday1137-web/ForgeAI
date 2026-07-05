# RULES.md

# ForgeAI Development Rules & Engineering Standards

**Project:** ForgeAI — Autonomous Software Engineering Team

**Version:** 1.0

---

# Purpose

This document defines the engineering principles, coding standards, architecture rules, AI development guidelines, and implementation constraints for ForgeAI.

Every contributor, AI coding assistant, and future developer should follow these rules to ensure the project remains maintainable, scalable, secure, and consistent.

When in doubt:

**These rules take precedence over implementation convenience.**

---

# Core Philosophy

ForgeAI is not a chatbot.

ForgeAI is a software engineering platform powered by collaborating AI agents.

Every implementation decision must reinforce this philosophy.

---

# Golden Rules

## Rule 1

One Responsibility Per Component.

Every:

* Agent
* API
* Component
* Service
* Hook
* Utility
* Worker

should have one clearly defined purpose.

Never combine unrelated responsibilities.

---

## Rule 2

Build for Scalability.

Always assume:

* More agents will be added.
* More MCP servers will be added.
* More repositories will be supported.
* More users will use the platform.

Never hardcode assumptions that limit future growth.

---

## Rule 3

Keep Components Small.

Large files become difficult to maintain.

Recommended limits:

Component: < 300 lines

API Route: < 200 lines

Service: < 300 lines

Utility: < 150 lines

If a file becomes too large, refactor it.

---

## Rule 4

No Business Logic in the Frontend.

Frontend responsibilities:

* UI
* State
* User interaction
* Visualization

Business logic belongs in the backend.

---

## Rule 5

Agents Never Communicate Directly.

All communication flows through the orchestrator.

Correct:

Planner → Orchestrator → Developer

Incorrect:

Planner → Developer

This keeps workflows observable and manageable.

---

## Rule 6

Never Skip Human Approval.

ForgeAI never performs critical repository actions automatically.

Examples requiring approval:

* Create Pull Request
* Commit Changes
* Delete Files
* Overwrite Existing Code
* Execute Risky Commands

Human approval is mandatory.

---

# Architecture Rules

## Layer Separation

The application consists of distinct layers.

Presentation Layer

↓

API Layer

↓

Business Logic Layer

↓

Agent Layer

↓

MCP Layer

↓

Persistence Layer

Never bypass layers.

---

## Backend Owns Logic

The backend owns:

* Repository management
* AI orchestration
* Task execution
* Authentication
* Validation
* Security
* MCP communication

The frontend must never duplicate backend logic.

---

## Modular Design

Every feature should be independently removable.

Removing one module should not break unrelated modules.

---

# Agent Rules

Each agent must have:

* A single responsibility.
* A defined input schema.
* A defined output schema.
* Error handling.
* Logging.
* Retry support.
* Validation.

Every agent should behave predictably.

---

## Agent Independence

Agents must not:

* Share mutable state directly.
* Depend on UI state.
* Depend on implementation details of other agents.

They communicate through structured outputs only.

---

## Agent Memory

Working memory should exist only for the current task.

Long-term memory should be explicit and persisted only when required.

Agents must not rely on hidden conversation history.

---

# Prompt Rules

Every agent must use:

* A dedicated system prompt.
* Clear responsibilities.
* Explicit constraints.
* Structured output.

Prompts should be stored in dedicated files, not scattered throughout the codebase.

---

# MCP Rules

All external tools must be accessed through MCP.

Examples:

GitHub

Filesystem

Terminal

Docker

Browser

Future integrations should follow the same abstraction.

---

## No Direct Tool Calls

Agents should never call external services directly.

The orchestrator coordinates tool access through MCP.

---

# Repository Rules

Repositories must remain read-only until the user approves modifications.

Every file change should be:

* Logged
* Traceable
* Reviewable

Never overwrite user code silently.

---

# API Rules

REST endpoints should:

* Be predictable.
* Return consistent response formats.
* Validate inputs.
* Return meaningful error messages.

Use standard HTTP status codes.

---

# Naming Rules

Names should be descriptive.

Good:

PlannerAgent

RepositoryService

SecurityReport

Bad:

Manager

Helper

Stuff

Utils2

Avoid abbreviations unless they are industry standard.

---

# Folder Rules

Every folder must have a clear purpose.

Avoid dumping unrelated files into generic folders.

Examples to avoid:

misc/

temp/

random/

helpers/

Prefer descriptive names such as:

repositories/

security/

notifications/

execution/

---

# Frontend Rules

Use reusable components.

Avoid duplicated UI.

Prefer composition over copy-paste.

Pages should orchestrate components rather than contain complex logic.

---

## UI Consistency

Every page should follow the same design language.

Spacing

Typography

Buttons

Cards

Colors

Icons

Animations

should remain consistent.

---

# State Management Rules

Global state only for application-wide data.

Local state for component-specific interactions.

Avoid unnecessary global stores.

---

# Backend Rules

Business logic belongs in services.

API routes should be thin.

Routes:

Validate request

Call service

Return response

Nothing more.

---

# Database Rules

Never access the database directly from API routes.

Use repositories or service layers.

Every table should have:

Primary Key

Created At

Updated At

Optional soft delete where appropriate.

---

# Error Handling Rules

Never swallow exceptions.

Always:

Log the error

Return meaningful messages

Provide recovery options where possible

Avoid exposing internal details to users.

---

# Logging Rules

Everything important must be logged.

Repository imported

Task created

Agent started

Agent completed

Agent failed

Tests executed

Security scan

Pull request created

Logs should include:

Timestamp

Task ID

Agent

Status

Duration

---

# Security Rules

Never commit:

API keys

Passwords

Tokens

Secrets

Environment files

Use environment variables for configuration.

Validate all user input.

Restrict command execution.

Require approval before critical operations.

---

# Performance Rules

Avoid unnecessary API requests.

Cache repository metadata where appropriate.

Stream progress updates instead of polling.

Lazy load heavy UI components.

Run independent work in parallel only when safe.

---

# Testing Rules

Every major feature should have tests.

Target:

Unit Tests

Integration Tests

End-to-End Tests

Regression Tests

New features should not reduce existing test coverage.

---

# Documentation Rules

Every major module should include:

Purpose

Responsibilities

Dependencies

Usage

Important implementation notes

Keep documentation synchronized with the code.

---

# Git Rules

Branch naming:

feature/

fix/

refactor/

docs/

test/

Commits should be small and focused.

Write meaningful commit messages.

---

# AI Development Rules

When generating code with AI:

Review all generated code.

Never accept code blindly.

Preserve project architecture.

Refactor when needed.

Do not sacrifice maintainability for speed.

---

# User Experience Rules

Users should always know:

What is happening

Why it is happening

What happens next

How to recover from errors

Avoid hidden background actions.

---

# Accessibility Rules

Support:

Keyboard navigation

Readable typography

High contrast

Visible focus states

Accessible labels

Responsive layouts

Accessibility is a requirement, not an enhancement.

---

# Future-Proofing Rules

All new features should be:

Modular

Configurable

Documented

Testable

Extensible

Avoid hardcoding assumptions.

---

# Things We Never Do

❌ Hide AI actions.

❌ Merge pull requests automatically.

❌ Execute dangerous commands without approval.

❌ Store secrets in source code.

❌ Duplicate business logic.

❌ Create massive "God" components.

❌ Ignore errors.

❌ Skip documentation.

❌ Bypass the orchestrator.

❌ Introduce breaking changes without migration.

---

# Code Quality Checklist

Before merging any feature, verify:

✓ Architecture remains modular.

✓ Feature has a single responsibility.

✓ Code follows project conventions.

✓ Errors are handled.

✓ Logging is implemented.

✓ Documentation is updated.

✓ Tests pass.

✓ UI is responsive.

✓ Security considerations are addressed.

✓ Human approval remains in place for critical actions.

---

# Definition of Done

A feature is considered complete only when:

* It satisfies the functional requirements.
* It follows all architecture rules.
* It includes appropriate documentation.
* It is tested.
* It integrates cleanly with existing modules.
* It follows the design system.
* It does not introduce security risks.
* It has been reviewed for maintainability.

If any of these conditions are not met, the feature is **not** complete.

---

# Final Principle

ForgeAI should always prioritize **clarity over cleverness**, **maintainability over shortcuts**, and **transparency over hidden automation**. Every line of code, every AI agent, and every user interaction should contribute to a platform that feels trustworthy, modular, and production-ready.
