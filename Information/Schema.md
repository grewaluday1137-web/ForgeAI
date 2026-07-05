# SCHEMA.md (Part 1)

# Database Schema

**Project:** ForgeAI — Autonomous Software Engineering Team

**Database:** PostgreSQL

**ORM Recommendation:** SQLAlchemy + Alembic (Backend), Prisma (optional for tooling)

**Version:** 1.0

---

# 1. Database Philosophy

The database is designed around five core domains:

1. Identity
2. Projects & Repositories
3. AI Execution
4. Collaboration & Notifications
5. System Configuration

Every entity is normalized to reduce duplication while maintaining efficient querying.

---

# 2. High-Level ER Diagram

```text
Users
│
├── Projects
│      │
│      ├── Repositories
│      │       │
│      │       ├── Branches
│      │       ├── Tasks
│      │       ├── PullRequests
│      │       └── RepositoryAnalysis
│      │
│      └── Settings
│
├── Notifications
├── Sessions
└── AuditLogs

Tasks
│
├── AgentRuns
│      │
│      ├── AgentLogs
│      ├── ToolExecutions
│      └── GeneratedArtifacts
│
├── Reviews
├── SecurityReports
├── TestReports
└── DocumentationReports
```

---

# 3. Common Columns

Every primary table should include:

| Column     | Type           |
| ---------- | -------------- |
| id         | UUID           |
| created_at | TIMESTAMP      |
| updated_at | TIMESTAMP      |
| deleted_at | TIMESTAMP NULL |
| created_by | UUID           |
| updated_by | UUID           |

Soft deletes should be used where appropriate.

---

# 4. Users

## Table

users

---

Fields

| Column     | Type      | Notes       |
| ---------- | --------- | ----------- |
| id         | UUID      | Primary Key |
| github_id  | TEXT      |             |
| google_id  | TEXT      |             |
| username   | TEXT      |             |
| email      | TEXT      |             |
| avatar_url | TEXT      |             |
| full_name  | TEXT      |             |
| role       | USER_ROLE |             |
| is_active  | BOOLEAN   |             |
| last_login | TIMESTAMP |             |
| created_at | TIMESTAMP |             |
| updated_at | TIMESTAMP |             |

Indexes

* username
* email
* github_id

Relationships

User

↓

Projects

↓

Notifications

↓

Sessions

↓

Audit Logs

---

# 5. Projects

Each workspace is a project.

Table

projects

Fields

| Column         | Type               |
| -------------- | ------------------ |
| id             | UUID               |
| owner_id       | UUID               |
| name           | TEXT               |
| description    | TEXT               |
| icon           | TEXT               |
| visibility     | PROJECT_VISIBILITY |
| default_branch | TEXT               |
| archived       | BOOLEAN            |
| created_at     | TIMESTAMP          |

Indexes

owner_id

name

Relationships

User → Projects

Project → Repositories

---

# 6. Repositories

Table

repositories

Fields

| Column          | Type      |
| --------------- | --------- |
| id              | UUID      |
| project_id      | UUID      |
| github_repo_id  | TEXT      |
| name            | TEXT      |
| owner           | TEXT      |
| clone_url       | TEXT      |
| language        | TEXT      |
| framework       | TEXT      |
| package_manager | TEXT      |
| default_branch  | TEXT      |
| latest_commit   | TEXT      |
| stars           | INTEGER   |
| forks           | INTEGER   |
| issues          | INTEGER   |
| size            | BIGINT    |
| last_synced     | TIMESTAMP |
| created_at      | TIMESTAMP |

Indexes

project_id

github_repo_id

language

framework

---

# 7. Repository Analysis

Stores AI understanding.

Table

repository_analysis

Fields

| Column                | Type      |
| --------------------- | --------- |
| id                    | UUID      |
| repository_id         | UUID      |
| architecture          | JSONB     |
| dependency_graph      | JSONB     |
| folder_tree           | JSONB     |
| framework             | TEXT      |
| language              | TEXT      |
| complexity_score      | FLOAT     |
| security_score        | FLOAT     |
| maintainability_score | FLOAT     |
| health_score          | FLOAT     |
| analyzed_at           | TIMESTAMP |

---

# 8. Branches

Table

branches

Fields

| Column        | Type      |
| ------------- | --------- |
| id            | UUID      |
| repository_id | UUID      |
| branch_name   | TEXT      |
| latest_commit | TEXT      |
| protected     | BOOLEAN   |
| created_at    | TIMESTAMP |

---

# 9. Tasks

Central entity.

Every engineering request becomes a task.

Table

tasks

Fields

| Column         | Type          |
| -------------- | ------------- |
| id             | UUID          |
| repository_id  | UUID          |
| user_id        | UUID          |
| title          | TEXT          |
| description    | TEXT          |
| priority       | TASK_PRIORITY |
| status         | TASK_STATUS   |
| branch_name    | TEXT          |
| estimated_time | INTEGER       |
| started_at     | TIMESTAMP     |
| completed_at   | TIMESTAMP     |
| created_at     | TIMESTAMP     |

Indexes

status

priority

repository_id

user_id

---

# 10. Agent Runs

Every agent execution.

Table

agent_runs

Fields

| Column      | Type         |
| ----------- | ------------ |
| id          | UUID         |
| task_id     | UUID         |
| agent       | AGENT_TYPE   |
| status      | AGENT_STATUS |
| started_at  | TIMESTAMP    |
| finished_at | TIMESTAMP    |
| duration_ms | INTEGER      |
| retry_count | INTEGER      |
| input       | JSONB        |
| output      | JSONB        |
| metadata    | JSONB        |

Indexes

task_id

agent

status

---

# 11. Agent Logs

Table

agent_logs

Fields

| Column    | Type      |
| --------- | --------- |
| id        | UUID      |
| run_id    | UUID      |
| timestamp | TIMESTAMP |
| level     | LOG_LEVEL |
| message   | TEXT      |
| metadata  | JSONB     |

---

# 12. Tool Executions

Every MCP call.

Table

tool_executions

Fields

| Column      | Type      |
| ----------- | --------- |
| id          | UUID      |
| run_id      | UUID      |
| tool        | MCP_TOOL  |
| action      | TEXT      |
| request     | JSONB     |
| response    | JSONB     |
| success     | BOOLEAN   |
| duration_ms | INTEGER   |
| executed_at | TIMESTAMP |

---

# 13. Pull Requests

Table

pull_requests

Fields

| Column        | Type      |
| ------------- | --------- |
| id            | UUID      |
| repository_id | UUID      |
| task_id       | UUID      |
| github_pr_id  | TEXT      |
| branch        | TEXT      |
| title         | TEXT      |
| description   | TEXT      |
| status        | PR_STATUS |
| url           | TEXT      |
| created_at    | TIMESTAMP |

---

# 14. Test Reports

Table

test_reports

Fields

| Column      | Type      |
| ----------- | --------- |
| id          | UUID      |
| task_id     | UUID      |
| total_tests | INTEGER   |
| passed      | INTEGER   |
| failed      | INTEGER   |
| skipped     | INTEGER   |
| coverage    | FLOAT     |
| summary     | TEXT      |
| raw_output  | JSONB     |
| created_at  | TIMESTAMP |

---

# 15. Security Reports

Table

security_reports

Fields

| Column          | Type           |
| --------------- | -------------- |
| id              | UUID           |
| task_id         | UUID           |
| score           | FLOAT          |
| vulnerabilities | JSONB          |
| recommendations | JSONB          |
| severity        | SECURITY_LEVEL |
| created_at      | TIMESTAMP      |

---

# 16. Documentation Reports

Table

documentation_reports

Fields

| Column              | Type    |
| ------------------- | ------- |
| id                  | UUID    |
| task_id             | UUID    |
| readme_updated      | BOOLEAN |
| api_docs_generated  | BOOLEAN |
| changelog_generated | BOOLEAN |
| comments_added      | INTEGER |
| summary             | TEXT    |

---

# 17. Reviews

Table

reviews

Fields

| Column          | Type      |
| --------------- | --------- |
| id              | UUID      |
| task_id         | UUID      |
| reviewer_agent  | TEXT      |
| quality_score   | FLOAT     |
| maintainability | FLOAT     |
| security        | FLOAT     |
| readability     | FLOAT     |
| comments        | JSONB     |
| approved        | BOOLEAN   |
| reviewed_at     | TIMESTAMP |

---

# 18. Notifications

Table

notifications

Fields

| Column     | Type              |
| ---------- | ----------------- |
| id         | UUID              |
| user_id    | UUID              |
| title      | TEXT              |
| body       | TEXT              |
| type       | NOTIFICATION_TYPE |
| read       | BOOLEAN           |
| created_at | TIMESTAMP         |

---

# 19. Sessions

Table

sessions

Fields

| Column     | Type      |
| ---------- | --------- |
| id         | UUID      |
| user_id    | UUID      |
| ip_address | TEXT      |
| device     | TEXT      |
| browser    | TEXT      |
| expires_at | TIMESTAMP |
| created_at | TIMESTAMP |

---

# 20. Audit Logs

Table

audit_logs

Fields

| Column    | Type      |
| --------- | --------- |
| id        | UUID      |
| user_id   | UUID      |
| entity    | TEXT      |
| entity_id | UUID      |
| action    | TEXT      |
| before    | JSONB     |
| after     | JSONB     |
| timestamp | TIMESTAMP |

---

# 21. User Settings

Table

user_settings

Fields

| Column        | Type      |
| ------------- | --------- |
| id            | UUID      |
| user_id       | UUID      |
| theme         | THEME     |
| default_model | TEXT      |
| notifications | BOOLEAN   |
| auto_refresh  | BOOLEAN   |
| created_at    | TIMESTAMP |

---

# 22. Enums

## USER_ROLE

```text
OWNER
ADMIN
MEMBER
VIEWER
```

---

## PROJECT_VISIBILITY

```text
PRIVATE
PUBLIC
```

---

## TASK_STATUS

```text
CREATED
QUEUED
PLANNING
ARCHITECTING
DEVELOPING
TESTING
SECURITY
DOCUMENTATION
REVIEW
WAITING_APPROVAL
PR_CREATED
COMPLETED
FAILED
CANCELLED
```

---

## TASK_PRIORITY

```text
LOW
MEDIUM
HIGH
CRITICAL
```

---

## AGENT_TYPE

```text
PLANNER
ARCHITECT
DEVELOPER
TESTER
SECURITY
DOCUMENTATION
REVIEWER
DEPLOYMENT
```

---

## AGENT_STATUS

```text
PENDING
RUNNING
COMPLETED
FAILED
RETRYING
SKIPPED
```

---

## MCP_TOOL

```text
GITHUB
FILESYSTEM
TERMINAL
DOCKER
BROWSER
DATABASE
```

---

## LOG_LEVEL

```text
INFO
WARNING
ERROR
DEBUG
SUCCESS
```

---

## PR_STATUS

```text
DRAFT
OPEN
APPROVED
MERGED
CLOSED
```

---

## SECURITY_LEVEL

```text
LOW
MEDIUM
HIGH
CRITICAL
```

---

## NOTIFICATION_TYPE

```text
TASK
SYSTEM
REPOSITORY
SECURITY
REVIEW
PULL_REQUEST
```

---

## THEME

```text
LIGHT
DARK
SYSTEM
```

---

# 23. Foreign Key Relationships

```text
users.id
    ├── projects.owner_id
    ├── tasks.user_id
    ├── notifications.user_id
    ├── sessions.user_id
    ├── audit_logs.user_id
    └── user_settings.user_id

projects.id
    └── repositories.project_id

repositories.id
    ├── repository_analysis.repository_id
    ├── branches.repository_id
    ├── tasks.repository_id
    └── pull_requests.repository_id

tasks.id
    ├── agent_runs.task_id
    ├── reviews.task_id
    ├── security_reports.task_id
    ├── test_reports.task_id
    ├── documentation_reports.task_id
    └── pull_requests.task_id

agent_runs.id
    ├── agent_logs.run_id
    └── tool_executions.run_id
```

---

# 24. Indexing Strategy

Primary indexes:

* email
* username
* github_repo_id
* repository_id
* task_id
* status
* priority
* created_at

Composite indexes:

* (repository_id, status)
* (task_id, agent)
* (user_id, created_at)
* (project_id, created_at)
* (run_id, timestamp)

---

# 25. Database Design Principles

* UUIDs for all primary keys.
* Soft deletes for user-facing entities.
* JSONB for flexible AI outputs and tool payloads.
* Strong foreign key constraints.
* Indexed status fields for dashboards.
* Immutable audit logs.
* Normalized core entities with denormalized JSON only where AI-generated structured content benefits from flexibility.

# SCHEMA.md (Part 2)

# API Schemas

**Project:** ForgeAI — Autonomous Software Engineering Team

**Version:** 1.0

---

# 1. API Design Principles

ForgeAI follows RESTful API principles.

Every endpoint should:

* Be predictable
* Be versioned
* Return typed responses
* Return consistent error objects
* Support pagination where applicable
* Be fully documented

---

# Base URL

```
/api/v1
```

Future versions:

```
/api/v2
```

---

# Content Type

All requests

```
application/json
```

File uploads

```
multipart/form-data
```

Streaming

```
text/event-stream
```

WebSockets

```
ws://
```

or

```
wss://
```

---

# Authentication

Every protected endpoint requires

```
Authorization: Bearer <JWT_TOKEN>
```

---

# Standard Response Format

Every successful API returns

```json
{
  "success": true,
  "message": "Human readable message",
  "data": {},
  "meta": {},
  "timestamp": "2026-01-01T10:00:00Z"
}
```

---

# Standard Error Format

Every failed request returns

```json
{
  "success": false,
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task could not be found.",
    "details": {}
  },
  "timestamp": "2026-01-01T10:00:00Z"
}
```

---

# Pagination Format

```json
{
  "success": true,
  "data": [],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalPages": 12,
    "totalItems": 231
  }
}
```

---

# Authentication APIs

## Login

POST

```
/auth/login
```

Request

```json
{
  "provider": "github"
}
```

Response

```json
{
  "token": "...",
  "refreshToken": "...",
  "user": {}
}
```

Validation

* Provider required
* Provider supported

---

## Refresh Token

POST

```
/auth/refresh
```

Request

```json
{
  "refreshToken": "..."
}
```

---

## Logout

POST

```
/auth/logout
```

No body required.

---

# User APIs

## Get Current User

GET

```
/users/me
```

Response

```json
{
  "id": "...",
  "username": "...",
  "email": "...",
  "avatar": "...",
  "role": "OWNER"
}
```

---

## Update Profile

PATCH

```
/users/me
```

Request

```json
{
  "fullName": "",
  "avatarUrl": ""
}
```

---

# Project APIs

## Create Project

POST

```
/projects
```

Request

```json
{
  "name": "Forge Demo",
  "description": "Demo Project"
}
```

Validation

* Name required
* Maximum length 100

---

Response

```json
{
  "id": "...",
  "name": "...",
  "createdAt": "..."
}
```

---

## Get Projects

GET

```
/projects
```

Supports

page

pageSize

search

sort

---

## Get Project

GET

```
/projects/{id}
```

---

## Update Project

PATCH

```
/projects/{id}
```

---

## Delete Project

DELETE

```
/projects/{id}
```

Soft delete only.

---

# Repository APIs

## Connect GitHub Repository

POST

```
/repositories/connect
```

Request

```json
{
  "projectId": "...",
  "githubRepoId": "...",
  "branch": "main"
}
```

Validation

* Repository exists
* User has access

---

Response

```json
{
  "repositoryId": "...",
  "status": "CONNECTED"
}
```

---

## Repository Analysis

POST

```
/repositories/{id}/analyze
```

Triggers Architect Agent.

---

Response

```json
{
  "analysisId": "...",
  "status": "RUNNING"
}
```

---

## Get Repository

GET

```
/repositories/{id}
```

---

## Repository Insights

GET

```
/repositories/{id}/insights
```

Returns

* Architecture
* Framework
* Complexity
* Health
* Security

---

# Task APIs

## Create Task

POST

```
/tasks
```

Request

```json
{
  "repositoryId": "...",
  "title": "Implement JWT",
  "description": "...",
  "priority": "HIGH"
}
```

Validation

* Repository required
* Title required
* Priority valid

---

Response

```json
{
  "taskId": "...",
  "status": "CREATED"
}
```

---

## Get Tasks

GET

```
/tasks
```

Supports

status

priority

repository

search

---

## Get Task

GET

```
/tasks/{id}
```

Returns

Task

Timeline

Agents

Reports

Logs

---

## Cancel Task

POST

```
/tasks/{id}/cancel
```

---

## Retry Task

POST

```
/tasks/{id}/retry
```

---

# Execution APIs

## Start Task

POST

```
/tasks/{id}/execute
```

Starts Planner Agent.

---

## Pause Task

POST

```
/tasks/{id}/pause
```

---

## Resume Task

POST

```
/tasks/{id}/resume
```

---

# Agent APIs

## Get All Agents

GET

```
/agents
```

---

Response

```json
[
  {
    "name": "Planner",
    "status": "RUNNING",
    "currentTask": "..."
  }
]
```

---

## Agent Details

GET

```
/agents/{agent}
```

---

## Agent Logs

GET

```
/agents/{agent}/logs
```

---

# Review APIs

## Submit Review

POST

```
/reviews
```

---

## Get Review

GET

```
/reviews/{taskId}
```

---

# Pull Request APIs

## Create PR

POST

```
/pull-requests
```

Request

```json
{
  "taskId": "...",
  "title": "...",
  "description": "..."
}
```

Requires approval.

---

## Get PR

GET

```
/pull-requests/{id}
```

---

# Security APIs

## Security Report

GET

```
/security/{taskId}
```

---

Response

```json
{
  "score": 93,
  "severity": "LOW",
  "issues": []
}
```

---

# Testing APIs

## Test Report

GET

```
/tests/{taskId}
```

---

Returns

Coverage

Passed

Failed

Skipped

Logs

---

# Documentation APIs

GET

```
/documentation/{taskId}
```

Returns

README

API Docs

Release Notes

Generated Comments

---

# Notification APIs

GET

```
/notifications
```

---

PATCH

```
/notifications/{id}/read
```

---

DELETE

```
/notifications/{id}
```

---

# Settings APIs

GET

```
/settings
```

---

PATCH

```
/settings
```

---

# Audit APIs

GET

```
/audit
```

Supports

Date

Entity

Action

User

---

# Dashboard APIs

GET

```
/dashboard
```

Returns

Projects

Tasks

Repositories

Recent Activity

Agent Status

Notifications

Statistics

---

# Analytics APIs

GET

```
/analytics
```

Returns

Task Completion

Execution Time

Repositories

Security Score

Agent Performance

---

# WebSocket Events

Endpoint

```
/ws/tasks/{id}
```

---

Client Receives

```json
{
  "event": "AGENT_STARTED",
  "agent": "Developer",
  "timestamp": "..."
}
```

---

Supported Events

TASK_CREATED

TASK_STARTED

TASK_COMPLETED

TASK_FAILED

AGENT_STARTED

AGENT_FINISHED

AGENT_FAILED

LOG_CREATED

TEST_STARTED

TEST_COMPLETED

SECURITY_SCAN_STARTED

SECURITY_SCAN_COMPLETED

REVIEW_STARTED

REVIEW_COMPLETED

PR_CREATED

NOTIFICATION

---

# Validation Rules

UUID

Must be valid UUID.

---

Repository Name

1–100 characters.

---

Project Name

1–100 characters.

---

Task Title

5–200 characters.

---

Description

Maximum 10,000 characters.

---

Priority

LOW

MEDIUM

HIGH

CRITICAL

---

Branch Name

Git-compliant format.

---

Email

RFC-compliant email format.

---

GitHub Repository

Must exist.

Must be accessible.

---

# HTTP Status Codes

200

Success

201

Created

202

Accepted

204

No Content

400

Validation Error

401

Unauthorized

403

Forbidden

404

Not Found

409

Conflict

422

Unprocessable Entity

429

Rate Limited

500

Internal Error

503

Service Unavailable

---

# Error Codes

AUTH_REQUIRED

INVALID_TOKEN

TOKEN_EXPIRED

USER_NOT_FOUND

PROJECT_NOT_FOUND

REPOSITORY_NOT_FOUND

TASK_NOT_FOUND

AGENT_NOT_FOUND

INVALID_PRIORITY

INVALID_BRANCH

MCP_CONNECTION_FAILED

GITHUB_API_ERROR

TERMINAL_EXECUTION_FAILED

DOCKER_ERROR

SECURITY_SCAN_FAILED

TEST_EXECUTION_FAILED

REVIEW_FAILED

VALIDATION_ERROR

DATABASE_ERROR

UNKNOWN_ERROR

---

# Rate Limits

Authenticated Users

* 100 requests/minute

Repository Analysis

* 10/hour

Task Creation

* 30/hour

AI Task Execution

* 20 concurrent tasks

WebSocket Connections

* 5 per user

---

# API Versioning

Current

```
/api/v1
```

Future

```
/api/v2
```

Breaking changes only occur in new versions.

---

# API Design Principles

* Every endpoint is idempotent where appropriate.
* Every response follows the standard envelope.
* Validation occurs before business logic.
* Business logic resides in services, not controllers.
* Sensitive data is never returned.
* Every request is authenticated unless explicitly public.
* Errors are structured and machine-readable.
* Long-running operations stream progress through WebSockets or server-sent events rather than blocking HTTP requests.

# SCHEMA.md (Part 3.1)

# Shared AI Agent Schema

**Project:** ForgeAI — Autonomous Software Engineering Team

**Version:** 1.0

**Purpose:**
This document defines the shared schemas, contracts, execution lifecycle, memory model, communication protocol, and base interfaces used by every AI agent in ForgeAI.

All agents **must** conform to these specifications.

---

# 1. AI System Philosophy

ForgeAI is not a chatbot.

ForgeAI is a collaborative autonomous software engineering platform.

Every AI component is a specialized engineering agent.

Agents never act independently.

Every action is coordinated by the **Orchestrator**.

Agents never call each other directly.

Agents communicate only through structured contracts.

---

# 2. AI Architecture

```text
                        User
                          │
                          ▼
                 AI Orchestrator
                          │
      ┌───────────────────┼───────────────────┐
      │                   │                   │
  Planner Agent      Architect Agent     Developer Agent
      │                   │                   │
      └──────────────┬────┴──────────────┬────┘
                     ▼                   ▼
             Testing Agent        Security Agent
                     │                   │
                     └────────────┬──────┘
                                  ▼
                      Documentation Agent
                                  │
                                  ▼
                          Reviewer Agent
                                  │
                                  ▼
                          Deployment Agent
```

---

# 3. Base Agent Interface

Every agent implements the same interface.

```typescript
interface BaseAgent {

    id: UUID

    name: string

    version: string

    description: string

    capabilities: Capability[]

    tools: MCPTool[]

    execute(context)

    validate(input)

    retry()

    cancel()

    report()

}
```

---

# 4. Agent Identity Schema

```json
{
    "id": "uuid",
    "name": "Planner",
    "displayName": "Planning Agent",
    "version": "1.0.0",
    "type": "PLANNER",
    "status": "IDLE",
    "description": "",
    "capabilities": [],
    "supportedTools": []
}
```

---

# 5. Shared Execution Context

Every agent receives exactly the same execution context.

```json
{
    "task": {},
    "repository": {},
    "project": {},
    "user": {},
    "execution": {},
    "memory": {},
    "artifacts": {},
    "configuration": {}
}
```

This ensures agents are stateless outside the provided context.

---

# 6. Execution Context Schema

## Task

```json
{
    "id": "",
    "title": "",
    "description": "",
    "priority": "HIGH",
    "status": "RUNNING"
}
```

---

## Repository

```json
{
    "id": "",
    "name": "",
    "language": "",
    "framework": "",
    "defaultBranch": "main"
}
```

---

## Project

```json
{
    "id": "",
    "name": "",
    "description": ""
}
```

---

## User

```json
{
    "id": "",
    "username": "",
    "role": "OWNER"
}
```

---

## Configuration

```json
{
    "model": "gemini",
    "temperature": 0.2,
    "maxTokens": 4096,
    "stream": true
}
```

---

# 7. Shared Memory Model

Memory is divided into three levels.

---

## Working Memory

Temporary.

Exists only while an agent executes.

Contains:

* Current reasoning
* Temporary calculations
* Parsed code
* Intermediate decisions

Destroyed after completion.

---

## Task Memory

Shared by every agent.

Contains:

* Repository analysis
* Task plan
* Previous outputs
* Reports
* Artifacts
* Logs

Lives until task completion.

---

## Long-Term Memory

Persistent.

Contains:

* User preferences
* Coding conventions
* Project standards
* Learned preferences

Future Feature.

---

# 8. Memory Object

```json
{
    "working": {},
    "task": {},
    "persistent": {}
}
```

---

# 9. Shared Artifact Store

Every generated output becomes an artifact.

Example:

```json
{
    "id":"artifact-id",

    "type":"PATCH",

    "agent":"Developer",

    "name":"auth.py",

    "path":"src/auth.py",

    "createdAt":"..."
}
```

Artifact Types

CODE

PATCH

TEST

REPORT

README

DOCS

CONFIG

LOG

SECURITY

DIFF

PR

---

# 10. Base Input Contract

Every agent receives:

```json
{
    "executionId":"",

    "agent":"Planner",

    "context":{},

    "input":{},

    "memory":{},

    "artifacts":[]
}
```

---

# 11. Base Output Contract

Every agent returns:

```json
{
    "success":true,

    "status":"COMPLETED",

    "summary":"",

    "artifacts":[],

    "logs":[],

    "nextAgent":"Architect",

    "executionTime":0,

    "metrics":{}
}
```

---

# 12. Metrics Schema

```json
{
    "tokensUsed":0,

    "duration":0,

    "toolCalls":0,

    "filesRead":0,

    "filesModified":0,

    "confidence":0.94
}
```

---

# 13. Validation Contract

Every agent validates before execution.

Validation checks:

Required Inputs

Repository Exists

Task Exists

Permissions

Tool Availability

Memory Integrity

Schema Version

---

Validation Result

```json
{
    "valid":true,

    "errors":[],

    "warnings":[]
}
```

---

# 14. Execution Lifecycle

Every agent follows identical stages.

```text
RECEIVED

↓

VALIDATING

↓

READY

↓

RUNNING

↓

GENERATING

↓

VERIFYING

↓

COMPLETED

or

FAILED
```

---

# 15. Agent States

IDLE

INITIALIZING

VALIDATING

WAITING

RUNNING

PAUSED

COMPLETED

FAILED

RETRYING

CANCELLED

---

# 16. Event Schema

Every action emits an event.

```json
{
    "eventId":"",

    "type":"AGENT_STARTED",

    "agent":"Planner",

    "timestamp":"",

    "payload":{}
}
```

---

# 17. Supported Events

SYSTEM_INITIALIZED

TASK_CREATED

TASK_STARTED

TASK_COMPLETED

TASK_FAILED

AGENT_STARTED

AGENT_PROGRESS

AGENT_COMPLETED

AGENT_FAILED

TOOL_REQUESTED

TOOL_COMPLETED

ARTIFACT_CREATED

MEMORY_UPDATED

REVIEW_REQUIRED

PR_CREATED

WORKFLOW_COMPLETED

---

# 18. Log Schema

```json
{
    "timestamp":"",

    "agent":"Planner",

    "level":"INFO",

    "message":"Analyzing repository",

    "metadata":{}
}
```

---

# 19. Shared JSON Contract

Agents never return free-form text.

Everything is structured.

Example

```json
{
    "summary":"",

    "recommendations":[],

    "artifacts":[],

    "metrics":{}
}
```

---

# 20. Retry Schema

If execution fails

```json
{
    "retry":{

        "count":1,

        "maxRetries":3,

        "reason":"Tool Timeout",

        "nextRetry":"2026..."
    }
}
```

---

# 21. Failure Schema

```json
{
    "success":false,

    "error":{

        "code":"MCP_TIMEOUT",

        "message":"GitHub unavailable",

        "recoverable":true

    }
}
```

---

# 22. Tool Access Contract

Agents never call tools directly.

Instead

```json
{
    "tool":"github",

    "action":"read_repository",

    "parameters":{}
}
```

Orchestrator executes.

Returns

```json
{
    "success":true,

    "response":{}
}
```

---

# 23. Capability Schema

Each capability is registered.

```json
{
    "name":"Repository Analysis",

    "description":"Analyze repository",

    "requiresTools":[

        "github"

    ]
}
```

---

# 24. Context Versioning

Every execution contains

```json
{
    "schemaVersion":"1.0",

    "agentVersion":"1.2",

    "workflowVersion":"1.0"
}
```

Allows upgrades without breaking compatibility.

---

# 25. Agent Configuration

```json
{
    "temperature":0.2,

    "topP":0.9,

    "maxTokens":4096,

    "timeout":120,

    "stream":true
}
```

---

# 26. Shared Security Rules

Every agent must:

Never expose secrets.

Never execute arbitrary shell commands directly.

Never overwrite user files without approval.

Never fabricate tool results.

Never modify shared memory outside approved schemas.

Validate all inputs before execution.

Emit audit events for every action.

---

# 27. Shared Design Principles

Every agent should be:

Deterministic where possible.

Transparent.

Observable.

Recoverable.

Modular.

Stateless beyond provided context.

Tool-driven rather than assumption-driven.

Human-supervised for critical actions.

---

# 28. Definition of a Well-Behaved Agent

A compliant ForgeAI agent:

* Accepts only validated structured input.
* Produces structured JSON output.
* Uses MCP tools only through the orchestrator.
* Reads and writes shared task memory using defined contracts.
* Emits lifecycle events.
* Logs every meaningful action.
* Reports metrics.
* Supports retries.
* Handles failures gracefully.
* Never performs hidden side effects.
* Is interchangeable with another implementation that follows the same schema.

---

# 29. Shared Workflow Contract

Every execution follows this sequence:

```text
Receive Context
      │
Validate Input
      │
Load Task Memory
      │
Acquire Required Tools
      │
Execute Assigned Responsibility
      │
Generate Structured Output
      │
Store Artifacts
      │
Update Task Memory
      │
Emit Events
      │
Return Result to Orchestrator
```

This lifecycle is mandatory for every current and future ForgeAI agent.

---

# 30. Final Principle

The Shared AI Schema is the backbone of ForgeAI. It ensures every agent behaves predictably, communicates through well-defined contracts, remains independent of specific LLM implementations, and can be orchestrated, monitored, retried, and evolved without changing the surrounding system architecture.

# SCHEMA.md (Part 3.2.1)

# Planner Agent Specification

**Project:** ForgeAI — Autonomous Software Engineering Team

**Agent Name:** Planner Agent

**Agent ID:** planner-agent

**Version:** 1.0

**Priority:** Highest

---

# 1. Purpose

The Planner Agent is the **brain** of the AI engineering team.

Its responsibility is **not to write code**.

Instead, it analyzes the engineering request, understands the repository context, decomposes the work into manageable engineering tasks, determines dependencies, estimates complexity, and creates an execution plan for the remaining agents.

The Planner Agent is always the first agent executed after task creation.

---

# 2. Mission Statement

Convert an ambiguous human request into a structured engineering execution plan.

Example:

User:

> "Add JWT authentication."

Planner Output:

* Analyze authentication module
* Create auth routes
* Implement JWT middleware
* Update frontend login
* Add refresh tokens
* Generate tests
* Run security scan
* Update documentation

---

# 3. Responsibilities

The Planner Agent is responsible for:

✓ Understanding user intent

✓ Understanding repository context

✓ Identifying engineering goals

✓ Breaking work into subtasks

✓ Prioritizing execution

✓ Selecting required agents

✓ Estimating complexity

✓ Estimating execution time

✓ Detecting risks

✓ Creating dependency graphs

✓ Producing a complete execution plan

---

# 4. Explicit Non-Responsibilities

The Planner Agent MUST NOT:

* Generate production code
* Modify repository files
* Execute shell commands
* Run tests
* Create pull requests
* Perform security scans
* Edit documentation

Those responsibilities belong to other agents.

---

# 5. Position in Workflow

```text
Task Created
      │
      ▼
Planner Agent
      │
      ▼
Architect Agent
      │
      ▼
Developer Agent
```

Planner always executes first.

---

# 6. Required Inputs

The Planner Agent receives:

```json
{
  "task": {},
  "repository": {},
  "repositoryAnalysis": {},
  "project": {},
  "user": {},
  "memory": {},
  "configuration": {}
}
```

---

# 7. Required Context

Planner should understand:

Repository language

Framework

Architecture

Folder structure

Dependencies

Current branch

Open issues

Previous execution history

Coding conventions

Repository health

---

# 8. Allowed MCP Tools

Planner has READ ONLY permissions.

Allowed:

✓ GitHub

✓ Filesystem

✓ Browser

Disallowed:

✗ Terminal

✗ Docker

✗ File modification

✗ Git commits

---

# 9. Capabilities

Repository inspection

Task analysis

Natural language understanding

Engineering planning

Dependency mapping

Complexity estimation

Workflow generation

Agent delegation

Risk assessment

Priority assignment

---

# 10. Execution Lifecycle

```text
Receive Context

↓

Validate Inputs

↓

Understand User Request

↓

Analyze Repository

↓

Identify Engineering Goals

↓

Generate Work Breakdown

↓

Estimate Complexity

↓

Determine Agent Order

↓

Create Execution Graph

↓

Generate Plan

↓

Store Task Memory

↓

Return Plan
```

---

# 11. Internal Workflow

## Step 1

Read task.

Example

"Implement OAuth login."

---

## Step 2

Understand engineering objective.

Questions:

What feature?

What modules?

Frontend?

Backend?

Database?

Security implications?

Documentation?

---

## Step 3

Read repository analysis.

Understand:

Architecture

Folder structure

Framework

Dependencies

Authentication

Testing

---

## Step 4

Determine affected systems.

Example

Frontend

Backend

Database

Configuration

Documentation

Tests

---

## Step 5

Break into subtasks.

Example

Backend API

↓

Middleware

↓

Database

↓

Frontend

↓

Tests

↓

Security

↓

Docs

---

## Step 6

Determine dependencies.

Example

Database

↓

Backend

↓

Frontend

↓

Testing

↓

Documentation

---

## Step 7

Assign agents.

Example

Architect

↓

Developer

↓

Tester

↓

Security

↓

Reviewer

---

## Step 8

Estimate complexity.

Output:

LOW

MEDIUM

HIGH

CRITICAL

---

## Step 9

Return execution plan.

---

# 12. Output Schema

```json
{
  "planId":"",

  "summary":"",

  "complexity":"HIGH",

  "estimatedMinutes":24,

  "requiredAgents":[],

  "executionGraph":[],

  "risks":[],

  "dependencies":[],

  "milestones":[],

  "recommendations":[]

}
```

---

# 13. Work Breakdown Schema

```json
{
  "tasks":[

      {

          "id":"",

          "title":"Implement backend authentication",

          "priority":"HIGH",

          "dependsOn":[],

          "agent":"Developer"

      }

  ]
}
```

---

# 14. Dependency Graph

Example

```text
Database

↓

Authentication

↓

API

↓

Frontend

↓

Testing

↓

Documentation

↓

Deployment
```

---

# 15. Complexity Estimation

Factors

Repository size

Architecture complexity

Framework familiarity

Number of affected files

Database changes

API changes

Security impact

Testing requirements

Documentation impact

---

Output

```json
{
  "complexity":"HIGH",

  "estimatedHours":3.5,

  "confidence":0.93
}
```

---

# 16. Risk Detection

Planner identifies risks.

Examples

Authentication changes

Breaking API changes

Database migration

Large refactoring

Circular dependencies

Missing tests

Legacy code

Risk Output

```json
{
  "severity":"HIGH",

  "reason":"Authentication affects multiple modules."
}
```

---

# 17. Agent Delegation

Planner determines execution order.

Example

Architect

↓

Developer

↓

Tester

↓

Security

↓

Documentation

↓

Reviewer

↓

Deployment

Planner never executes those tasks.

---

# 18. Memory Usage

Reads

Repository Memory

Task Memory

Project Memory

Writes

Execution Plan

Dependencies

Estimated Time

Risk Analysis

Milestones

---

# 19. Artifacts Produced

Execution Plan

Task Graph

Dependency Graph

Complexity Report

Milestones

Risk Report

Execution Timeline

---

# 20. Validation Rules

Task title required.

Repository exists.

Repository analyzed.

Supported framework.

User authorized.

Memory valid.

Schema version compatible.

---

# 21. Failure Conditions

Planner fails if

Repository unavailable

Repository not analyzed

Task invalid

Context corrupted

MCP unavailable

Invalid schema

---

# 22. Retry Policy

Planner retries:

Maximum

3

Delay

Exponential Backoff

5s

10s

20s

---

# 23. Events

Planner emits

PLANNER_STARTED

TASK_ANALYZED

PLAN_CREATED

DEPENDENCIES_IDENTIFIED

RISKS_FOUND

PLAN_COMPLETED

PLANNER_FAILED

---

# 24. Logs

Example

```json
{
    "agent":"Planner",

    "message":"Analyzing repository structure",

    "level":"INFO"
}
```

---

# 25. Metrics

Tracks

Execution Time

Planning Accuracy

Estimated vs Actual

Task Count

Dependency Count

Risk Count

Confidence Score

Tool Calls

---

# 26. Success Criteria

Planner succeeds when:

Task understood.

Repository understood.

Execution graph created.

Dependencies mapped.

Required agents selected.

Complexity estimated.

No ambiguity remains.

---

# 27. Prompt Contract

System Prompt Goals

Understand engineering intent.

Never write implementation code.

Think like a technical lead.

Prefer modular implementation.

Identify hidden dependencies.

Optimize execution order.

Always produce structured JSON.

Never return markdown or prose in agent outputs.

---

# 28. Example Input

```json
{
  "title":"Add JWT Authentication",

  "description":"Implement JWT login and protected routes."
}
```

---

# 29. Example Output

```json
{
  "summary":"Implement JWT authentication using middleware and refresh tokens.",

  "complexity":"HIGH",

  "estimatedMinutes":45,

  "requiredAgents":[
      "Architect",
      "Developer",
      "Tester",
      "Security",
      "Documentation",
      "Reviewer"
  ],

  "tasks":[

      {

          "title":"Analyze authentication architecture",

          "agent":"Architect"

      },

      {

          "title":"Implement JWT middleware",

          "agent":"Developer"

      },

      {

          "title":"Generate authentication tests",

          "agent":"Tester"

      },

      {

          "title":"Run security audit",

          "agent":"Security"

      },

      {

          "title":"Update documentation",

          "agent":"Documentation"

      },

      {

          "title":"Review implementation",

          "agent":"Reviewer"

      }

  ]
}
```

---

# 30. Planner Design Principles

The Planner Agent should behave like an experienced Engineering Manager or Technical Lead.

It focuses on:

* Understanding objectives before execution.
* Creating structured plans rather than immediate solutions.
* Delegating work to specialists.
* Identifying dependencies early.
* Minimizing risk through careful sequencing.
* Producing deterministic, machine-readable plans.

The Planner is successful when every downstream agent receives a clear, unambiguous roadmap that enables efficient and coordinated execution.

# SCHEMA.md (Part 3.2.2)

# Architect Agent Specification

**Project:** ForgeAI — Autonomous Software Engineering Team

**Agent Name:** Architect Agent

**Agent ID:** architect-agent

**Version:** 1.0

**Priority:** High

---

# 1. Purpose

The Architect Agent is responsible for understanding the technical structure of a software project before any implementation begins.

Unlike the Planner Agent, which understands *what* needs to be done, the Architect Agent determines *how* the requested change should fit into the existing system.

Its primary goal is to ensure every implementation follows the repository's architecture, coding standards, design patterns, and framework conventions.

The Architect Agent never writes production code.

---

# 2. Mission Statement

Act as a Senior Software Architect that understands an unfamiliar repository, identifies the safest implementation strategy, minimizes architectural debt, and provides a precise implementation blueprint for the Developer Agent.

---

# 3. Responsibilities

The Architect Agent is responsible for:

✓ Understanding repository architecture

✓ Detecting technologies

✓ Identifying frameworks

✓ Understanding project structure

✓ Mapping dependencies

✓ Understanding module relationships

✓ Detecting design patterns

✓ Identifying affected files

✓ Recommending implementation strategy

✓ Identifying architectural risks

✓ Producing an implementation blueprint

---

# 4. Explicit Non-Responsibilities

The Architect Agent MUST NOT:

* Generate production code
* Execute tests
* Modify repository files
* Run shell commands
* Create pull requests
* Deploy applications
* Perform security scans
* Review generated code

---

# 5. Workflow Position

```text
Planner
    │
    ▼
Architect
    │
    ▼
Developer
```

The Architect Agent executes immediately after the Planner Agent.

---

# 6. Required Inputs

```json
{
  "task": {},
  "executionPlan": {},
  "repository": {},
  "repositoryAnalysis": {},
  "memory": {},
  "artifacts": {}
}
```

---

# 7. Repository Context

The Architect Agent should understand:

Repository layout

Programming language

Framework

Application architecture

Database

Authentication

State management

Routing

Testing strategy

CI/CD

Docker

Dependencies

Build system

Configuration

---

# 8. Allowed MCP Tools

READ ONLY

Allowed

✓ GitHub

✓ Filesystem

✓ Browser

Future

✓ Dependency graph service

Not Allowed

✗ Terminal

✗ Docker execution

✗ Git write operations

✗ File modification

---

# 9. Capabilities

Repository analysis

Dependency graph generation

Architecture recognition

Framework detection

Folder analysis

Module mapping

Code navigation

Configuration discovery

Impact analysis

Risk identification

---

# 10. Internal Workflow

```text
Receive Context
        │
Validate
        │
Load Repository
        │
Detect Technology
        │
Analyze Architecture
        │
Locate Relevant Modules
        │
Map Dependencies
        │
Determine Affected Files
        │
Identify Risks
        │
Generate Blueprint
        │
Return Report
```

---

# 11. Repository Analysis

The Architect Agent should inspect:

Repository root

Directory layout

Configuration files

Dependency files

Framework files

Docker files

Environment configuration

Database configuration

API routes

Frontend routes

Services

Utilities

Middleware

Tests

Documentation

---

# 12. Technology Detection

Automatically detect

Programming Language

Examples

Python

TypeScript

JavaScript

Java

Go

Rust

C#

---

Framework

Examples

FastAPI

Next.js

React

Angular

Vue

Django

Flask

Express

Spring Boot

---

Database

Examples

PostgreSQL

MySQL

MongoDB

SQLite

Redis

---

Package Manager

npm

pnpm

yarn

pip

poetry

cargo

---

Testing Framework

pytest

Jest

Vitest

Playwright

Cypress

JUnit

---

# 13. Folder Analysis

Generate a logical view.

Example

```text
src/
 ├── api/
 ├── auth/
 ├── services/
 ├── database/
 ├── middleware/
 ├── models/
 ├── routes/
 └── utils/
```

Identify

Entry points

Shared modules

Core services

Configuration

Business logic

Infrastructure

---

# 14. Architecture Detection

Recognize patterns such as

MVC

Layered Architecture

Hexagonal

Clean Architecture

DDD

Microservices

Modular Monolith

Feature-based

Component-based

---

Output

```json
{
    "architecture":"Layered",

    "confidence":0.94
}
```

---

# 15. Dependency Mapping

Determine relationships.

Example

```text
API

↓

Service

↓

Repository

↓

Database
```

or

```text
UI

↓

Hooks

↓

API Client

↓

Backend
```

---

# 16. Impact Analysis

Determine

Files affected

Classes affected

Functions affected

Modules affected

Configurations affected

Tests affected

Documentation affected

---

Output

```json
{
  "files":[
      "auth.py",
      "middleware.py",
      "login.tsx"
  ]
}
```

---

# 17. Design Pattern Detection

Recognize

Repository Pattern

Factory

Singleton

Dependency Injection

Strategy

Observer

Adapter

Facade

Command

Builder

---

Purpose

Developer Agent should follow existing patterns instead of introducing new ones.

---

# 18. Configuration Analysis

Inspect

package.json

requirements.txt

pyproject.toml

Dockerfile

docker-compose.yml

.env.example

tsconfig

vite.config

next.config

eslint

prettier

---

# 19. API Mapping

Identify

Routes

Controllers

Services

Middlewares

Authentication

Validation

Error handling

Output

```json
{
    "routes":[
        "/login",
        "/users",
        "/auth"
    ]
}
```

---

# 20. Database Mapping

Identify

Tables

Models

ORM

Relationships

Indexes

Migration system

---

# 21. Risk Detection

Examples

Breaking API

Circular dependency

Legacy code

Large file

Deprecated package

Missing tests

Authentication changes

Database migration

---

Risk Output

```json
{
    "severity":"HIGH",

    "reason":"Authentication middleware shared across application."
}
```

---

# 22. Implementation Blueprint

The Architect Agent generates a complete implementation strategy.

Example

```json
{
    "steps":[

        "Create authentication service",

        "Add middleware",

        "Update login endpoint",

        "Protect API routes",

        "Update frontend authentication",

        "Generate tests"

    ]
}
```

---

# 23. Artifact Generation

Produces

Architecture Report

Dependency Graph

Folder Map

Impact Report

Blueprint

Technology Report

Risk Report

Affected Files List

Implementation Strategy

---

# 24. Memory Usage

Reads

Repository Memory

Planner Output

Task Memory

Previous Reports

Writes

Architecture Report

Dependency Graph

Blueprint

Impact Analysis

Affected Files

---

# 25. Validation Rules

Repository exists

Repository analyzed

Task exists

Planner output available

Repository readable

Framework supported

---

# 26. Failure Conditions

Repository inaccessible

Unsupported repository

Corrupted repository

Missing configuration

Unreadable source code

Dependency graph failure

---

# 27. Retry Policy

Maximum retries

3

Retry reasons

Repository timeout

GitHub timeout

Filesystem timeout

Network interruption

---

# 28. Events

ARCHITECT_STARTED

REPOSITORY_ANALYZED

FRAMEWORK_DETECTED

DEPENDENCIES_MAPPED

FILES_IDENTIFIED

RISKS_IDENTIFIED

BLUEPRINT_CREATED

ARCHITECT_COMPLETED

ARCHITECT_FAILED

---

# 29. Logs

Example

```json
{
  "agent":"Architect",

  "level":"INFO",

  "message":"Detected FastAPI backend and Next.js frontend."
}
```

---

# 30. Metrics

Repository size

Files analyzed

Dependencies discovered

Architecture confidence

Execution time

Tool calls

Affected files

Complexity score

---

# 31. Success Criteria

The Architect Agent succeeds when:

Repository structure is fully understood.

Technology stack is identified.

Affected files are mapped.

Implementation strategy is documented.

Dependencies are resolved.

Architectural risks are identified.

Developer Agent can begin implementation without ambiguity.

---

# 32. Prompt Contract

The Architect Agent should think like a Principal Software Architect.

Objectives

Understand before recommending.

Respect existing architecture.

Avoid unnecessary refactoring.

Favor consistency.

Minimize technical debt.

Never invent repository structure.

Never assume frameworks without evidence.

Produce structured JSON only.

---

# 33. Example Input

```json
{
  "task":"Add JWT authentication",

  "repository":"FastAPI + Next.js"
}
```

---

# 34. Example Output

```json
{
  "architecture":"Layered",

  "frameworks":[
      "FastAPI",
      "Next.js"
  ],

  "affectedFiles":[
      "backend/auth/routes.py",
      "backend/auth/service.py",
      "frontend/app/login/page.tsx",
      "frontend/lib/auth.ts"
  ],

  "dependencies":[
      "python-jose",
      "passlib"
  ],

  "risks":[
      "Authentication middleware impacts all protected routes."
  ],

  "implementationStrategy":[
      "Create authentication service",
      "Implement JWT middleware",
      "Protect existing routes",
      "Update login UI",
      "Generate authentication tests"
  ]
}
```

---

# 35. Quality Principles

The Architect Agent should always:

* Analyze before recommending.
* Follow the repository's existing conventions.
* Minimize architectural disruption.
* Preserve consistency across modules.
* Identify risks early.
* Produce deterministic, structured outputs.
* Provide a clear blueprint that enables downstream agents to implement changes confidently.

The Architect Agent's success is measured not by code generation, but by the quality, completeness, and accuracy of the implementation plan it provides to the Developer Agent.

# SCHEMA.md (Part 3.2.3)

# Developer Agent Specification

**Project:** ForgeAI — Autonomous Software Engineering Team

**Agent Name:** Developer Agent

**Agent ID:** developer-agent

**Version:** 1.0

**Priority:** Critical

---

# 1. Purpose

The Developer Agent is responsible for implementing software changes defined by the Planner Agent and Architect Agent.

Unlike the Planner Agent, which decides **what** should be built, and the Architect Agent, which determines **how** it should fit into the existing system, the Developer Agent is responsible for **writing, modifying, and refactoring production-quality code**.

It behaves like a Senior Software Engineer who understands existing architecture, follows project conventions, and produces maintainable code.

The Developer Agent is the only agent permitted to generate production code.

---

# 2. Mission Statement

Transform architectural plans into high-quality, maintainable software while preserving project conventions, minimizing technical debt, and producing implementation artifacts suitable for human review.

---

# 3. Responsibilities

The Developer Agent is responsible for:

✓ Reading implementation blueprints

✓ Understanding repository context

✓ Writing production code

✓ Refactoring existing code

✓ Creating new modules

✓ Updating existing modules

✓ Preserving project architecture

✓ Following coding conventions

✓ Adding comments where appropriate

✓ Producing implementation summaries

✓ Creating structured code patches

---

# 4. Explicit Non-Responsibilities

The Developer Agent MUST NOT:

* Create implementation plans
* Decide overall architecture
* Approve code quality
* Merge pull requests
* Execute tests
* Perform security audits
* Deploy applications
* Modify repository settings

---

# 5. Workflow Position

```text
Planner
    │
Architect
    │
Developer
    │
Tester
```

The Developer Agent executes only after the Architect Agent has completed successfully.

---

# 6. Required Inputs

```json
{
  "task": {},
  "executionPlan": {},
  "architectureBlueprint": {},
  "repository": {},
  "repositoryAnalysis": {},
  "memory": {},
  "artifacts": {}
}
```

---

# 7. Repository Context

The Developer Agent must understand:

Programming language

Framework

Architecture pattern

Folder structure

Naming conventions

Formatting rules

Dependency management

Database layer

API layer

UI structure

Testing strategy

Coding standards

---

# 8. Allowed MCP Tools

Read

✓ GitHub

✓ Filesystem

✓ Browser

Write

✓ Filesystem

Allowed

✓ Terminal (restricted)

Not Allowed

✗ Git Push

✗ Merge Pull Requests

✗ Delete Repository

✗ Modify Secrets

---

# 9. Capabilities

Production code generation

Code modification

File creation

File editing

Refactoring

Dependency updates

Configuration updates

Code explanation

Patch generation

Implementation documentation

---

# 10. Internal Workflow

```text
Receive Context
      │
Validate Inputs
      │
Read Blueprint
      │
Load Files
      │
Understand Existing Code
      │
Generate Changes
      │
Validate Syntax
      │
Check Conventions
      │
Generate Patch
      │
Create Artifacts
      │
Update Task Memory
      │
Return Result
```

---

# 11. Code Generation Principles

The Developer Agent should:

Reuse existing code where appropriate.

Avoid duplicate logic.

Respect project architecture.

Use existing utilities.

Minimize unnecessary changes.

Keep implementations modular.

Prefer readability over cleverness.

Avoid introducing breaking changes unless explicitly requested.

---

# 12. File Modification Strategy

The Developer Agent should classify changes as:

Create

Update

Refactor

Rename

Delete (requires approval)

Each file modification must include a justification.

---

# 13. Implementation Strategy

Before writing code, the Developer Agent should:

Understand the task.

Understand affected modules.

Inspect existing implementation.

Identify reusable components.

Determine required dependencies.

Generate implementation sequence.

Only then begin coding.

---

# 14. Supported Code Operations

Create files

Modify files

Refactor methods

Refactor classes

Create APIs

Update APIs

Create UI components

Update UI

Create models

Update models

Create services

Update services

Update configuration

Generate migrations (future)

---

# 15. Coding Standards

The Developer Agent must:

Follow language idioms.

Use repository formatting.

Follow naming conventions.

Respect linting rules.

Use dependency injection where applicable.

Avoid hardcoded values.

Write self-documenting code.

Keep functions focused.

---

# 16. Refactoring Rules

Safe refactoring only.

Allowed:

Extract method

Extract class

Rename variables

Improve readability

Reduce duplication

Improve modularity

Disallowed:

Large architectural rewrites unless explicitly requested.

---

# 17. Dependency Management

The Developer Agent may recommend adding dependencies.

Before adding one, it must verify:

Necessity

Compatibility

Maintenance status

License compatibility

Version stability

Alternatives

---

# 18. Artifact Generation

The Developer Agent produces:

Code patches

Modified files

New files

Implementation summary

Dependency changes

Configuration updates

Code comments

Patch metadata

---

# 19. Output Schema

```json
{
  "status":"COMPLETED",

  "summary":"JWT authentication implemented.",

  "filesModified":[
    "backend/auth/service.py",
    "frontend/app/login/page.tsx"
  ],

  "filesCreated":[
    "backend/auth/jwt.py"
  ],

  "dependencies":[
    "python-jose"
  ],

  "artifacts":[]
}
```

---

# 20. Patch Schema

```json
{
  "file":"backend/auth/service.py",

  "operation":"UPDATE",

  "reason":"Add JWT authentication service.",

  "diff":"..."
}
```

---

# 21. Validation Rules

The Developer Agent validates:

Syntax

File paths

Repository structure

Imports

Dependency compatibility

Architecture constraints

Blueprint compliance

---

# 22. Failure Conditions

Invalid blueprint

Missing files

Unsupported language

Repository corruption

Dependency conflicts

Filesystem failure

Tool timeout

---

# 23. Retry Policy

Maximum retries

3

Retry triggers

File lock

Filesystem timeout

Tool failure

Temporary dependency resolution failure

---

# 24. Events

DEVELOPER_STARTED

FILES_LOADED

CODE_GENERATION_STARTED

FILE_CREATED

FILE_UPDATED

PATCH_GENERATED

IMPLEMENTATION_COMPLETED

DEVELOPER_FAILED

---

# 25. Logging

Example

```json
{
  "agent":"Developer",
  "level":"INFO",
  "message":"Updated authentication middleware."
}
```

---

# 26. Metrics

Files read

Files modified

Files created

Lines added

Lines removed

Lines modified

Dependencies added

Execution time

Confidence score

Tool calls

---

# 27. Memory Usage

Reads:

Execution Plan

Architecture Blueprint

Repository Memory

Task Memory

Affected Files

Writes:

Implementation Summary

Patch Metadata

Generated Artifacts

File Change List

Updated Task Memory

---

# 28. Human Approval Requirements

The Developer Agent may propose but not finalize:

Deleting files

Renaming directories

Breaking API changes

Database schema changes

Dependency removal

Repository-wide refactors

These require downstream review and human approval.

---

# 29. Prompt Contract

The Developer Agent should think like a Senior Software Engineer.

Objectives:

Write maintainable code.

Respect repository conventions.

Prefer minimal, targeted changes.

Avoid speculative implementation.

Do not invent missing requirements.

Produce deterministic, structured outputs.

Never bypass architectural guidance.

---

# 30. Example Input

```json
{
  "task":"Implement JWT authentication",

  "blueprint":{
    "affectedFiles":[
      "backend/auth/routes.py",
      "backend/auth/service.py"
    ]
  }
}
```

---

# 31. Example Output

```json
{
  "summary":"JWT authentication implemented successfully.",

  "filesModified":[
    "backend/auth/routes.py",
    "backend/auth/service.py",
    "frontend/app/login/page.tsx"
  ],

  "filesCreated":[
    "backend/auth/jwt.py"
  ],

  "dependencies":[
    "python-jose",
    "passlib"
  ],

  "artifacts":[
    {
      "type":"PATCH",
      "name":"jwt-auth-implementation"
    }
  ]
}
```

---

# 32. Quality Principles

The Developer Agent should always:

* Implement only what has been planned.
* Preserve existing architecture.
* Minimize technical debt.
* Prefer readable, maintainable code.
* Produce small, reviewable changes.
* Avoid unnecessary refactoring.
* Generate deterministic, structured outputs.
* Clearly explain every significant modification.

The Developer Agent is successful when it transforms architectural blueprints into production-ready code that integrates cleanly with the existing repository and can proceed confidently to testing, security analysis, and review.

# SCHEMA.md (Part 3.2.4)

# Tester Agent Specification

**Project:** ForgeAI — Autonomous Software Engineering Team

**Agent Name:** Tester Agent

**Agent ID:** tester-agent

**Version:** 1.0

**Priority:** Critical

---

# 1. Purpose

The Tester Agent is responsible for validating that the implementation produced by the Developer Agent behaves correctly, satisfies the original requirements, integrates safely with the existing codebase, and does not introduce regressions.

Unlike the Developer Agent, which creates code, the Tester Agent acts as a Senior QA Automation Engineer by designing, generating, executing, and analyzing tests.

The Tester Agent never changes production code.

---

# 2. Mission Statement

Automatically verify that software changes are correct, reliable, secure, and production-ready through comprehensive testing while producing actionable reports for downstream agents.

---

# 3. Responsibilities

The Tester Agent is responsible for:

✓ Understanding implementation changes

✓ Reading execution plans

✓ Understanding acceptance criteria

✓ Generating test cases

✓ Generating unit tests

✓ Generating integration tests

✓ Generating API tests

✓ Executing tests

✓ Collecting coverage

✓ Detecting regressions

✓ Producing testing reports

✓ Recommending fixes

---

# 4. Explicit Non-Responsibilities

The Tester Agent MUST NOT:

* Modify production code
* Approve implementations
* Perform security audits
* Deploy software
* Merge pull requests
* Change repository architecture

---

# 5. Workflow Position

```text
Planner
    │
Architect
    │
Developer
    │
Tester
    │
Security
```

Testing occurs immediately after implementation.

---

# 6. Required Inputs

```json
{
  "task": {},
  "executionPlan": {},
  "repository": {},
  "implementation": {},
  "modifiedFiles": [],
  "artifacts": [],
  "memory": {}
}
```

---

# 7. Repository Context

The Tester Agent understands:

Programming language

Testing framework

Repository architecture

Package manager

Build system

Existing tests

Mock strategy

Coverage tools

CI configuration

Testing conventions

---

# 8. Allowed MCP Tools

Read

✓ GitHub

✓ Filesystem

Write

✓ Filesystem (tests only)

Execute

✓ Terminal

Allowed Commands

pytest

npm test

pnpm test

yarn test

vitest

jest

go test

cargo test

mvn test

gradle test

Not Allowed

Repository modification

Git push

Production deployment

---

# 9. Capabilities

Generate tests

Execute tests

Analyze failures

Generate mocks

Measure coverage

Detect regressions

Validate acceptance criteria

Benchmark execution

Generate QA reports

---

# 10. Internal Workflow

```text
Receive Context
      │
Validate Inputs
      │
Load Modified Files
      │
Understand Requirements
      │
Inspect Existing Tests
      │
Generate Missing Tests
      │
Execute Test Suite
      │
Collect Results
      │
Analyze Failures
      │
Measure Coverage
      │
Generate Report
      │
Return Results
```

---

# 11. Test Strategy

The Tester Agent should execute tests in this order:

Static validation

↓

Unit Tests

↓

Integration Tests

↓

API Tests

↓

Regression Tests

↓

Performance Smoke Tests (future)

↓

UI Tests (future)

---

# 12. Test Types

## Unit Tests

Validate isolated functions.

---

## Integration Tests

Validate communication between modules.

---

## API Tests

Validate REST endpoints.

---

## Authentication Tests

Login

Authorization

JWT

Sessions

Permissions

---

## Database Tests

CRUD

Transactions

Constraints

Indexes

---

## Validation Tests

Invalid input

Boundary values

Required fields

---

## Error Handling Tests

Exceptions

Timeouts

Missing resources

Permission failures

---

# 13. Test Generation Principles

The Tester Agent should:

Reuse existing testing patterns.

Follow repository conventions.

Avoid duplicate tests.

Generate deterministic tests.

Prefer readability.

Create isolated tests.

Use mocks where appropriate.

---

# 14. Coverage Goals

Target minimums

Unit Coverage

90%

Critical Modules

100%

Authentication

100%

Business Logic

95%

Utilities

85%

Overall

90%

---

# 15. Generated Artifacts

Unit Tests

Integration Tests

Mock Data

Fixtures

Coverage Report

QA Report

Failure Report

Execution Logs

---

# 16. Output Schema

```json
{
  "status":"COMPLETED",

  "testsGenerated":18,

  "testsExecuted":74,

  "passed":72,

  "failed":2,

  "coverage":91.8,

  "summary":"Authentication tests successful."
}
```

---

# 17. Coverage Schema

```json
{
  "overall":91.4,

  "backend":94.1,

  "frontend":88.7,

  "critical":100
}
```

---

# 18. Failure Report Schema

```json
{
  "file":"tests/test_auth.py",

  "test":"test_refresh_token",

  "status":"FAILED",

  "reason":"Token expiration mismatch."
}
```

---

# 19. Regression Detection

Compare

Existing behavior

↓

New implementation

↓

Unexpected changes

↓

Regression Report

Regression categories

API

Authentication

Database

Performance

Configuration

UI

---

# 20. Validation Rules

Repository accessible

Implementation exists

Blueprint available

Testing framework detected

Build succeeds

Dependencies installed

---

# 21. Failure Conditions

Missing test framework

Compilation failure

Dependency error

Repository corruption

Tool timeout

Terminal failure

Coverage tool failure

---

# 22. Retry Policy

Maximum retries

3

Retry triggers

Test timeout

Tool crash

Temporary dependency issue

CI interruption

---

# 23. Events

TESTER_STARTED

TEST_DISCOVERY_COMPLETED

TEST_GENERATION_STARTED

TEST_GENERATED

TEST_EXECUTION_STARTED

TEST_EXECUTION_COMPLETED

COVERAGE_GENERATED

TESTER_COMPLETED

TESTER_FAILED

---

# 24. Logging

Example

```json
{
  "agent":"Tester",

  "level":"INFO",

  "message":"Generated 12 authentication tests."
}
```

---

# 25. Metrics

Tests generated

Tests executed

Tests passed

Tests failed

Coverage percentage

Execution duration

Average execution time

Regression count

Mock count

Tool calls

---

# 26. Memory Usage

Reads

Execution Plan

Architecture Blueprint

Implementation Artifacts

Repository Memory

Task Memory

Writes

Coverage Report

Failure Report

QA Report

Generated Tests

Updated Task Memory

---

# 27. Human Approval Requirements

The Tester Agent cannot approve implementations.

Its responsibility ends after reporting:

Pass/fail status

Coverage

Failures

Recommendations

Final approval belongs to the Reviewer Agent and the human user.

---

# 28. Prompt Contract

The Tester Agent should think like a Senior QA Automation Engineer.

Objectives

Verify functionality.

Challenge assumptions.

Detect regressions.

Maximize coverage.

Produce reliable tests.

Never fabricate passing results.

Never ignore failures.

Always produce structured JSON.

---

# 29. Example Input

```json
{
  "task":"Implement JWT authentication",

  "modifiedFiles":[
    "backend/auth/service.py",
    "backend/auth/routes.py"
  ]
}
```

---

# 30. Example Output

```json
{
  "summary":"Authentication implementation validated.",

  "testsGenerated":16,

  "testsExecuted":68,

  "passed":68,

  "failed":0,

  "coverage":94.6,

  "artifacts":[
    {
      "type":"TEST_REPORT"
    },
    {
      "type":"COVERAGE_REPORT"
    }
  ]
}
```

---

# 31. Quality Principles

The Tester Agent should always:

* Test behavior, not implementation details.
* Generate meaningful, maintainable tests.
* Detect regressions before downstream review.
* Measure and report coverage honestly.
* Never suppress or ignore failures.
* Provide structured, reproducible reports.
* Keep testing deterministic and repeatable.
* Produce artifacts that allow the Security Agent and Reviewer Agent to continue with confidence.

The Tester Agent is successful when every software change has been validated against its requirements, regressions have been identified, and downstream agents receive a complete, trustworthy testing report.

# SCHEMA.md (Part 3.2.5)

# Security Agent Specification

**Project:** ForgeAI — Autonomous Software Engineering Team

**Agent Name:** Security Agent

**Agent ID:** security-agent

**Version:** 1.0

**Priority:** Critical

---

# 1. Purpose

The Security Agent is responsible for evaluating the security posture of all code changes before they proceed to documentation, review, and pull request generation.

Unlike the Developer Agent, which focuses on functionality, the Security Agent thinks like an experienced Application Security (AppSec) Engineer. It identifies vulnerabilities, insecure coding patterns, dependency risks, exposed secrets, authentication weaknesses, authorization flaws, and configuration issues.

The Security Agent never modifies production code directly. Instead, it produces detailed findings and actionable recommendations.

---

# 2. Mission Statement

Ensure every implementation meets modern application security standards by identifying vulnerabilities, validating security controls, and preventing insecure code from progressing through the engineering workflow.

---

# 3. Responsibilities

The Security Agent is responsible for:

✓ Reviewing implementation changes

✓ Performing static security analysis

✓ Detecting insecure coding patterns

✓ Reviewing authentication

✓ Reviewing authorization

✓ Detecting exposed secrets

✓ Checking dependency vulnerabilities

✓ Reviewing configuration security

✓ Evaluating API security

✓ Assessing input validation

✓ Assessing output encoding

✓ Producing security reports

✓ Assigning security severity

✓ Recommending mitigations

---

# 4. Explicit Non-Responsibilities

The Security Agent MUST NOT:

* Modify production code
* Deploy software
* Merge pull requests
* Generate application features
* Rewrite architecture
* Ignore security findings

---

# 5. Workflow Position

```text id="i6n8fd"
Planner
    │
Architect
    │
Developer
    │
Tester
    │
Security
    │
Documentation
```

The Security Agent executes after testing has completed.

---

# 6. Required Inputs

```json id="z6hknq"
{
  "task": {},
  "repository": {},
  "executionPlan": {},
  "implementation": {},
  "testReport": {},
  "modifiedFiles": [],
  "artifacts": [],
  "memory": {}
}
```

---

# 7. Repository Context

The Security Agent should understand:

Programming language

Framework

Authentication system

Authorization model

API architecture

Database access

Configuration files

Dependency management

Environment variables

Secrets management

Container configuration

---

# 8. Allowed MCP Tools

Read

✓ GitHub

✓ Filesystem

✓ Browser

Execute

✓ Terminal (security scanning only)

Future

✓ SCA scanners

✓ SBOM generators

✓ Container scanners

Not Allowed

✗ Git write operations

✗ Repository deletion

✗ Infrastructure modification

✗ Secret management changes

---

# 9. Capabilities

Static Application Security Testing (SAST)

Dependency analysis

Secret detection

Authentication review

Authorization review

Configuration analysis

Input validation review

Output encoding review

Session management review

Security scoring

Risk classification

Compliance reporting

---

# 10. Internal Workflow

```text id="mewxkp"
Receive Context
      │
Validate Inputs
      │
Load Modified Files
      │
Analyze Source Code
      │
Analyze Dependencies
      │
Analyze Configuration
      │
Analyze Authentication
      │
Analyze Authorization
      │
Classify Findings
      │
Generate Security Report
      │
Update Memory
      │
Return Results
```

---

# 11. Security Categories

The Security Agent evaluates:

Authentication

Authorization

Input Validation

Output Encoding

Dependency Security

Secrets

API Security

Database Security

Session Security

Logging

Error Handling

Configuration

Container Security

Infrastructure Readiness

---

# 12. Secret Detection

Detect exposed:

API Keys

JWT Secrets

Database Passwords

Private Keys

SSH Keys

Cloud Credentials

OAuth Tokens

Service Accounts

Environment Variables

Certificates

Never expose discovered secrets in reports.

Instead, report their locations and risk level.

---

# 13. Dependency Security

Inspect:

package.json

package-lock.json

pnpm-lock.yaml

requirements.txt

poetry.lock

pom.xml

build.gradle

Cargo.lock

go.mod

Identify:

Known CVEs

Deprecated packages

Unsupported libraries

License concerns

Version conflicts

Unmaintained dependencies

---

# 14. Authentication Review

Validate:

Password storage

JWT implementation

Token expiration

Refresh token handling

Session management

Password reset flow

Account lockout

Multi-factor support (future)

---

# 15. Authorization Review

Review:

Role checks

Permission checks

Route protection

Object-level authorization

Privilege escalation risks

Horizontal privilege escalation

Vertical privilege escalation

---

# 16. Input Validation

Verify:

Required fields

Length limits

Type validation

Sanitization

SQL Injection prevention

Command Injection prevention

NoSQL Injection prevention

Path traversal prevention

XML injection prevention

---

# 17. API Security

Inspect:

Authentication headers

Authorization middleware

Rate limiting

Error responses

Sensitive data exposure

CORS configuration

HTTP methods

API versioning

---

# 18. Configuration Review

Analyze:

Dockerfile

docker-compose.yml

.env.example

nginx.conf

GitHub Actions

CI configuration

Security headers

TLS configuration (future)

---

# 19. Security Severity

Levels

INFORMATIONAL

LOW

MEDIUM

HIGH

CRITICAL

Critical findings should block progression to the Reviewer Agent until acknowledged.

---

# 20. Generated Artifacts

Security Report

Dependency Report

Secret Scan Report

Configuration Report

Risk Assessment

Compliance Summary

Security Score

Remediation Recommendations

---

# 21. Output Schema

```json id="j1xvls"
{
  "status":"COMPLETED",

  "securityScore":94,

  "severity":"LOW",

  "issues":2,

  "criticalIssues":0,

  "recommendations":[]
}
```

---

# 22. Finding Schema

```json id="18e1d4"
{
  "id":"SEC-001",

  "category":"Authentication",

  "severity":"MEDIUM",

  "title":"Refresh token lacks rotation.",

  "description":"Refresh tokens are reusable indefinitely.",

  "affectedFiles":[
    "backend/auth/service.py"
  ],

  "recommendation":"Implement refresh token rotation."
}
```

---

# 23. Security Score

Calculate a normalized score (0–100) based on:

Critical findings

High findings

Medium findings

Low findings

Dependency health

Configuration quality

Authentication robustness

Authorization robustness

Secret exposure

Input validation

---

# 24. Validation Rules

Repository accessible

Implementation available

Dependencies readable

Configuration readable

Testing completed

Task context valid

---

# 25. Failure Conditions

Repository inaccessible

Dependency manifest missing

Filesystem failure

Security tool timeout

Malformed configuration

Unsupported language

---

# 26. Retry Policy

Maximum retries

3

Retry triggers

Tool timeout

Dependency database unavailable

Temporary filesystem failure

---

# 27. Events

SECURITY_STARTED

DEPENDENCIES_ANALYZED

SECRETS_SCANNED

AUTHENTICATION_REVIEWED

AUTHORIZATION_REVIEWED

CONFIGURATION_REVIEWED

SECURITY_REPORT_CREATED

SECURITY_COMPLETED

SECURITY_FAILED

---

# 28. Logging

Example

```json id="3x0wrv"
{
  "agent":"Security",

  "level":"INFO",

  "message":"Dependency scan completed. No critical vulnerabilities detected."
}
```

---

# 29. Metrics

Files analyzed

Dependencies analyzed

Secrets scanned

Findings count

Critical findings

Security score

Execution duration

Tool calls

False-positive count (future)

---

# 30. Memory Usage

Reads

Execution Plan

Architecture Blueprint

Implementation Artifacts

Test Report

Repository Memory

Task Memory

Writes

Security Report

Risk Assessment

Security Score

Finding List

Updated Task Memory

---

# 31. Human Approval Requirements

The Security Agent cannot block the workflow permanently.

Instead:

Critical findings

↓

Flag task

↓

Require human acknowledgement

↓

Reviewer receives findings

↓

Human decides whether to proceed

---

# 32. Prompt Contract

The Security Agent should think like a Senior Application Security Engineer.

Objectives

Assume nothing is secure by default.

Validate every trust boundary.

Prefer least privilege.

Identify realistic attack paths.

Avoid speculative findings.

Never fabricate vulnerabilities.

Never expose secrets in reports.

Produce structured JSON only.

---

# 33. Example Input

```json id="l8mq8w"
{
  "task":"Implement JWT authentication",

  "modifiedFiles":[
    "backend/auth/service.py",
    "backend/auth/routes.py"
  ]
}
```

---

# 34. Example Output

```json id="5wivcb"
{
  "summary":"Security review completed.",

  "securityScore":96,

  "severity":"LOW",

  "issues":[
    {
      "id":"SEC-001",
      "severity":"LOW",
      "title":"JWT expiration should be configurable."
    }
  ],

  "artifacts":[
    {
      "type":"SECURITY_REPORT"
    },
    {
      "type":"DEPENDENCY_REPORT"
    }
  ]
}
```

---

# 35. Security Standards

The Security Agent should evaluate implementations against widely accepted security practices, including:

* Least privilege
* Defense in depth
* Secure defaults
* Input validation
* Output encoding
* Principle of fail-safe behavior
* Secure secret management
* Dependency hygiene
* Authentication and authorization best practices

Specific compliance frameworks may be added in future versions.

---

# 36. Quality Principles

The Security Agent should always:

* Focus on practical, reproducible security risks.
* Avoid overwhelming developers with low-value findings.
* Prioritize vulnerabilities by impact and exploitability.
* Never modify production code.
* Produce clear remediation guidance.
* Generate deterministic, structured outputs.
* Preserve confidentiality by masking or omitting sensitive values.
* Enable downstream agents and human reviewers to make informed security decisions.

The Security Agent is successful when it provides an accurate, actionable assessment of implementation security, helping ensure that only well-understood and appropriately reviewed changes continue through the ForgeAI engineering workflow.

# SCHEMA.md (Part 3.2.6)

# Documentation Agent Specification

**Project:** ForgeAI — Autonomous Software Engineering Team

**Agent Name:** Documentation Agent

**Agent ID:** documentation-agent

**Version:** 1.0

**Priority:** High

---

# 1. Purpose

The Documentation Agent is responsible for ensuring that every software change is accompanied by accurate, complete, and maintainable documentation.

Unlike the Developer Agent, which focuses on implementation, the Documentation Agent focuses on explaining **what changed, why it changed, how it works, and how developers should use it.**

It acts as a Senior Technical Writer working alongside the engineering team.

The Documentation Agent never changes application behavior.

---

# 2. Mission Statement

Automatically maintain high-quality technical documentation that evolves with the codebase, ensuring developers always have accurate and up-to-date information.

---

# 3. Responsibilities

The Documentation Agent is responsible for:

✓ Updating README files

✓ Generating API documentation

✓ Updating architecture documentation

✓ Writing implementation notes

✓ Writing migration guides

✓ Generating release notes

✓ Updating configuration documentation

✓ Creating code documentation

✓ Creating onboarding documentation

✓ Summarizing engineering changes

---

# 4. Explicit Non-Responsibilities

The Documentation Agent MUST NOT:

* Modify production logic
* Refactor application code
* Execute tests
* Perform security reviews
* Merge pull requests
* Deploy applications

---

# 5. Workflow Position

```text id="udotj2"
Planner
    │
Architect
    │
Developer
    │
Tester
    │
Security
    │
Documentation
    │
Reviewer
```

Documentation occurs only after implementation, testing, and security review are complete.

---

# 6. Required Inputs

```json id="vkz6jq"
{
  "task": {},
  "executionPlan": {},
  "implementation": {},
  "architectureReport": {},
  "testReport": {},
  "securityReport": {},
  "modifiedFiles": [],
  "artifacts": [],
  "memory": {}
}
```

---

# 7. Repository Context

The Documentation Agent understands:

Repository structure

Project architecture

Programming language

Framework

Existing documentation

API endpoints

Configuration files

Environment variables

Build process

Deployment process

Coding conventions

---

# 8. Allowed MCP Tools

Read

✓ GitHub

✓ Filesystem

✓ Browser

Write

✓ Filesystem (documentation only)

Not Allowed

✗ Production source files

✗ Git operations

✗ Terminal execution

✗ Repository configuration

---

# 9. Capabilities

README generation

Markdown generation

API documentation

Architecture documentation

Code comments

Configuration documentation

Release note generation

Migration guide generation

Change summaries

Developer onboarding

---

# 10. Internal Workflow

```text id="jz4m2y"
Receive Context
      │
Validate Inputs
      │
Analyze Implementation
      │
Detect Documentation Impact
      │
Update README
      │
Generate API Docs
      │
Generate Release Notes
      │
Generate Migration Notes
      │
Generate Change Summary
      │
Store Artifacts
      │
Return Result
```

---

# 11. Documentation Categories

The Documentation Agent maintains:

README

API Documentation

Architecture Documentation

Developer Guides

Configuration Documentation

Deployment Documentation

Migration Guides

Release Notes

Code Comments

Changelog

Troubleshooting

FAQ (future)

---

# 12. README Maintenance

The Documentation Agent updates:

Features

Requirements

Installation

Usage

Configuration

Architecture

Directory Structure

Examples

Known Limitations

Roadmap

Contributors

License

Only relevant sections should be modified.

---

# 13. API Documentation

Generate documentation for:

Endpoints

Request objects

Response objects

Authentication

Authorization

Headers

Status codes

Examples

Error responses

Pagination

Rate limits

---

# 14. Release Notes

Each implementation should produce release notes.

Example sections:

New Features

Improvements

Bug Fixes

Breaking Changes

Security Updates

Performance Improvements

Migration Notes

Known Issues

---

# 15. Migration Guides

Generate when changes affect:

Database schema

Configuration

API contracts

Authentication

Dependencies

Environment variables

Deployment

---

# 16. Configuration Documentation

Document changes to:

Environment variables

Configuration files

Docker

Compose

CI/CD

Package dependencies

Runtime requirements

---

# 17. Code Documentation

Generate:

Docstrings

Function comments

Class documentation

Module documentation

API descriptions

Inline comments (only where beneficial)

Avoid excessive commenting.

---

# 18. Change Summary

Every task should produce:

Purpose

Files changed

Features added

Features modified

Features removed

Dependencies added

Configuration changes

Testing summary

Security summary

---

# 19. Generated Artifacts

README

API Documentation

Release Notes

Migration Guide

Implementation Notes

Configuration Guide

Architecture Notes

Change Summary

Markdown Files

Documentation Metadata

---

# 20. Output Schema

```json id="1tf0pd"
{
  "status":"COMPLETED",

  "documentsGenerated":5,

  "readmeUpdated":true,

  "apiDocsGenerated":true,

  "releaseNotesGenerated":true,

  "migrationGuideGenerated":false
}
```

---

# 21. Documentation Artifact Schema

```json id="5u4bch"
{
  "type":"README",

  "file":"README.md",

  "operation":"UPDATE",

  "summary":"Added JWT authentication documentation."
}
```

---

# 22. Validation Rules

Repository available

Implementation complete

Architecture report available

Testing complete

Security review complete

Markdown valid

Required files accessible

---

# 23. Failure Conditions

Missing implementation

Repository inaccessible

Filesystem error

Documentation templates unavailable

Corrupted markdown

Unsupported project layout

---

# 24. Retry Policy

Maximum retries

3

Retry triggers

Filesystem failure

Markdown generation error

Temporary repository access issue

---

# 25. Events

DOCUMENTATION_STARTED

README_UPDATED

API_DOCS_GENERATED

RELEASE_NOTES_GENERATED

MIGRATION_GUIDE_CREATED

CHANGELOG_UPDATED

DOCUMENTATION_COMPLETED

DOCUMENTATION_FAILED

---

# 26. Logging

Example

```json id="4qrm8p"
{
  "agent":"Documentation",

  "level":"INFO",

  "message":"README updated with authentication feature."
}
```

---

# 27. Metrics

Documents generated

README updates

API endpoints documented

Code comments added

Release notes generated

Execution duration

Markdown files modified

Documentation coverage (future)

---

# 28. Memory Usage

Reads

Execution Plan

Architecture Report

Implementation Artifacts

Test Report

Security Report

Repository Memory

Task Memory

Writes

Documentation Artifacts

Release Notes

Migration Guide

Documentation Summary

Updated Task Memory

---

# 29. Human Approval Requirements

The Documentation Agent cannot publish documentation.

It prepares documentation for:

Reviewer validation

Human review

Pull request inclusion

Final approval remains with the Reviewer Agent and the human user.

---

# 30. Prompt Contract

The Documentation Agent should think like a Senior Technical Writer.

Objectives

Explain changes clearly.

Keep documentation concise.

Remain technically accurate.

Update only affected sections.

Avoid redundant information.

Do not invent undocumented features.

Produce structured outputs.

Never modify unrelated documentation.

---

# 31. Example Input

```json id="zm68ht"
{
  "task":"Implement JWT authentication",

  "modifiedFiles":[
    "backend/auth/service.py",
    "backend/auth/routes.py"
  ]
}
```

---

# 32. Example Output

```json id="5e4hk6"
{
  "summary":"Documentation updated successfully.",

  "documentsGenerated":4,

  "artifacts":[
    {
      "type":"README"
    },
    {
      "type":"API_DOCUMENTATION"
    },
    {
      "type":"RELEASE_NOTES"
    },
    {
      "type":"CHANGELOG"
    }
  ]
}
```

---

# 33. Documentation Standards

Documentation should be:

Accurate

Current

Readable

Version-aware

Consistent

Searchable

Markdown compliant

Developer-focused

Every generated document should clearly identify:

Purpose

Audience

Prerequisites

Examples where appropriate

Related components

---

# 34. Quality Principles

The Documentation Agent should always:

* Keep documentation synchronized with implementation.
* Document behavior rather than implementation details where appropriate.
* Minimize unnecessary updates to unchanged content.
* Produce clear, concise, and technically accurate explanations.
* Follow the repository's existing documentation style.
* Generate deterministic, structured outputs.
* Ensure every significant code change has corresponding documentation.

The Documentation Agent is successful when developers can understand, use, configure, and maintain the implemented feature without reading the underlying source code, while the repository documentation remains complete, consistent, and up to date.

# SCHEMA.md (Part 3.2.7)

# Reviewer Agent Specification

**Project:** ForgeAI — Autonomous Software Engineering Team

**Agent Name:** Reviewer Agent

**Agent ID:** reviewer-agent

**Version:** 1.0

**Priority:** Critical

---

# 1. Purpose

The Reviewer Agent serves as the final technical quality gate before changes are presented to the user or packaged into a Pull Request.

Unlike the Developer Agent, whose goal is to implement features, the Reviewer Agent evaluates the **quality, correctness, maintainability, architecture, testing, documentation, and security** of the complete implementation.

The Reviewer Agent behaves like an experienced Staff Engineer performing a professional code review.

It does **not** modify production code.

---

# 2. Mission Statement

Evaluate the complete implementation objectively, identify weaknesses, request improvements when necessary, and ensure only high-quality engineering work proceeds to human approval.

---

# 3. Responsibilities

The Reviewer Agent is responsible for:

✓ Reviewing implementation quality

✓ Reviewing architecture compliance

✓ Reviewing testing completeness

✓ Reviewing security findings

✓ Reviewing documentation

✓ Detecting maintainability issues

✓ Identifying unnecessary complexity

✓ Detecting duplicated logic

✓ Scoring implementation quality

✓ Generating review comments

✓ Requesting revisions

✓ Approving high-quality implementations

---

# 4. Explicit Non-Responsibilities

The Reviewer Agent MUST NOT:

* Generate production code
* Modify source files
* Execute deployments
* Perform planning
* Ignore failed tests
* Ignore critical security findings
* Merge Pull Requests

---

# 5. Workflow Position

```text id="w0hk2m"
Planner
    │
Architect
    │
Developer
    │
Tester
    │
Security
    │
Documentation
    │
Reviewer
    │
Human Approval
```

The Reviewer Agent is the final AI agent before human approval.

---

# 6. Required Inputs

```json id="y2lx8t"
{
  "task": {},
  "executionPlan": {},
  "architectureReport": {},
  "implementation": {},
  "testReport": {},
  "securityReport": {},
  "documentationReport": {},
  "artifacts": [],
  "memory": {}
}
```

---

# 7. Repository Context

The Reviewer Agent understands:

Repository architecture

Coding conventions

Project standards

Testing strategy

Documentation standards

Security policies

Implementation blueprint

Acceptance criteria

---

# 8. Allowed MCP Tools

Read

✓ GitHub

✓ Filesystem

✓ Browser

Not Allowed

✗ Source code modification

✗ Git commits

✗ Pull request merge

✗ Deployment

✗ Terminal execution (except future read-only analysis)

---

# 9. Capabilities

Code review

Architecture review

Testing review

Security review

Documentation review

Style review

Complexity analysis

Maintainability analysis

Scoring

Revision generation

Approval recommendation

---

# 10. Internal Workflow

```text id="8g9qz4"
Receive Context
      │
Validate Inputs
      │
Load Reports
      │
Review Implementation
      │
Review Tests
      │
Review Security
      │
Review Documentation
      │
Calculate Scores
      │
Generate Findings
      │
Determine Outcome
      │
Generate Review Report
      │
Return Result
```

---

# 11. Review Categories

The Reviewer Agent evaluates:

Architecture

Implementation Quality

Code Style

Readability

Maintainability

Complexity

Performance

Testing

Security

Documentation

Configuration

Dependency Management

Developer Experience

---

# 12. Review Principles

The Reviewer Agent should:

Review objectively.

Prefer maintainability.

Reward simplicity.

Reject unnecessary complexity.

Encourage modular design.

Prioritize correctness.

Respect repository conventions.

Never approve code solely because it compiles.

---

# 13. Architecture Review

Validate:

Architecture consistency

Module boundaries

Layer separation

Dependency direction

Design patterns

Folder organization

Naming consistency

Blueprint compliance

---

# 14. Code Quality Review

Evaluate:

Function size

Class size

Readability

Variable names

Method names

Comments

Error handling

Code duplication

Dead code

Magic values

---

# 15. Testing Review

Review:

Coverage

Critical path testing

Authentication testing

Regression testing

Failure scenarios

Boundary conditions

Mock quality

Assertions

Test maintainability

---

# 16. Security Review

Review Security Agent output.

Confirm:

Critical findings resolved

Authentication safe

Authorization appropriate

Secrets protected

Dependencies acceptable

Configuration secure

If unresolved critical findings exist, approval should not be recommended.

---

# 17. Documentation Review

Validate:

README updated

API docs updated

Release notes generated

Migration guide included when necessary

Documentation accuracy

Consistency with implementation

---

# 18. Scoring Model

Each category receives a score (0–100).

Architecture

Implementation

Maintainability

Readability

Testing

Security

Documentation

Performance

Overall Score

Weighted average determines the recommendation.

---

# 19. Recommendation Levels

APPROVED

APPROVED_WITH_SUGGESTIONS

CHANGES_REQUIRED

REJECTED

---

# 20. Generated Artifacts

Review Report

Review Comments

Quality Scorecard

Approval Recommendation

Revision Requests

Summary Report

Review Metadata

---

# 21. Output Schema

```json id="1wctz0"
{
  "status":"COMPLETED",

  "overallScore":94,

  "recommendation":"APPROVED",

  "summary":"Implementation meets engineering standards.",

  "revisionRequests":[]
}
```

---

# 22. Review Comment Schema

```json id="k6gx3r"
{
  "category":"Maintainability",

  "severity":"LOW",

  "file":"backend/auth/service.py",

  "line":82,

  "message":"Consider extracting token validation into a helper function."
}
```

---

# 23. Revision Request Schema

```json id="q5fs2b"
{
  "priority":"HIGH",

  "reason":"Authentication middleware lacks refresh token validation.",

  "requiredAgent":"Developer"
}
```

---

# 24. Approval Rules

Automatically recommend **CHANGES_REQUIRED** if:

Critical tests fail

Critical security findings exist

Architecture is violated

Implementation incomplete

Acceptance criteria unmet

Documentation missing

Recommend **APPROVED** only if all required checks pass.

---

# 25. Validation Rules

Implementation complete

Testing complete

Security review complete

Documentation complete

Artifacts available

Repository context valid

---

# 26. Failure Conditions

Missing reports

Incomplete implementation

Corrupted artifacts

Repository unavailable

Memory inconsistency

---

# 27. Retry Policy

Maximum retries

3

Retry triggers

Missing artifact

Repository timeout

Temporary read failure

---

# 28. Events

REVIEW_STARTED

CODE_REVIEW_COMPLETED

TEST_REVIEW_COMPLETED

SECURITY_REVIEW_COMPLETED

DOCUMENTATION_REVIEW_COMPLETED

QUALITY_SCORE_CALCULATED

REVISION_REQUESTED

IMPLEMENTATION_APPROVED

REVIEW_COMPLETED

REVIEW_FAILED

---

# 29. Logging

Example

```json id="d9tx7v"
{
  "agent":"Reviewer",

  "level":"INFO",

  "message":"Implementation approved with maintainability suggestions."
}
```

---

# 30. Metrics

Files reviewed

Artifacts reviewed

Review duration

Overall score

Architecture score

Testing score

Security score

Documentation score

Revision requests

Approval rate

---

# 31. Memory Usage

Reads

Execution Plan

Architecture Report

Implementation Artifacts

Test Report

Security Report

Documentation Report

Repository Memory

Task Memory

Writes

Review Report

Quality Scorecard

Revision Requests

Approval Recommendation

Updated Task Memory

---

# 32. Human Approval Requirements

The Reviewer Agent **does not** replace the human reviewer.

Its output is advisory.

The human user always has the final decision to:

Approve

Reject

Request changes

Cancel

---

# 33. Prompt Contract

The Reviewer Agent should think like a Staff Software Engineer performing a professional pull request review.

Objectives

Protect code quality.

Enforce engineering standards.

Be objective.

Provide actionable feedback.

Avoid subjective preferences.

Never fabricate issues.

Do not request unnecessary refactoring.

Produce structured JSON only.

---

# 34. Example Input

```json id="oqn3q4"
{
  "task":"Implement JWT authentication",

  "implementation":{},

  "testReport":{},

  "securityReport":{}
}
```

---

# 35. Example Output

```json id="n0nslw"
{
  "summary":"Implementation approved after review.",

  "overallScore":96,

  "recommendation":"APPROVED",

  "categoryScores":{
    "architecture":95,
    "implementation":97,
    "testing":94,
    "security":96,
    "documentation":98
  },

  "revisionRequests":[],

  "artifacts":[
    {
      "type":"REVIEW_REPORT"
    },
    {
      "type":"QUALITY_SCORECARD"
    }
  ]
}
```

---

# 36. Review Standards

The Reviewer Agent should evaluate implementations against the following engineering principles:

* Correctness
* Simplicity
* Maintainability
* Modularity
* Consistency
* Readability
* Testability
* Security
* Performance
* Documentation completeness

Reviews should be evidence-based and tied to observable implementation details.

---

# 37. Quality Principles

The Reviewer Agent should always:

* Review the complete implementation, not isolated files.
* Balance strictness with practicality.
* Prioritize correctness over stylistic preferences.
* Recommend improvements with clear reasoning.
* Respect existing repository conventions.
* Produce deterministic, structured outputs.
* Ensure recommendations are actionable and proportional to their impact.
* Preserve human authority by providing guidance rather than making irreversible decisions.

The Reviewer Agent is successful when it provides an accurate, comprehensive, and trustworthy assessment that helps human reviewers confidently decide whether an implementation is ready for production.

# SCHEMA.md (Part 3.2.8)

# Deployment Agent Specification

**Project:** ForgeAI — Autonomous Software Engineering Team

**Agent Name:** Deployment Agent

**Agent ID:** deployment-agent

**Version:** 1.0

**Priority:** High

---

# 1. Purpose

The Deployment Agent is responsible for preparing the application for deployment after the implementation has successfully passed planning, architecture review, development, testing, security review, documentation, and code review.

The Deployment Agent **does not deploy applications automatically**.

Instead, it verifies deployment readiness, prepares deployment artifacts, validates runtime configuration, generates deployment documentation, and creates release packages.

It behaves like an experienced DevOps Engineer preparing software for production.

---

# 2. Mission Statement

Ensure every approved implementation is deployment-ready by validating infrastructure requirements, packaging deployment artifacts, generating release documentation, and identifying deployment risks before human approval.

---

# 3. Responsibilities

The Deployment Agent is responsible for:

✓ Preparing deployment artifacts

✓ Validating runtime configuration

✓ Validating environment variables

✓ Verifying dependency installation

✓ Validating Docker configuration

✓ Validating Docker Compose

✓ Preparing release metadata

✓ Generating deployment checklists

✓ Generating release packages

✓ Creating deployment reports

✓ Assessing deployment readiness

---

# 4. Explicit Non-Responsibilities

The Deployment Agent MUST NOT:

* Automatically deploy applications
* Merge Pull Requests
* Modify production infrastructure
* Provision cloud resources
* Change application logic
* Ignore deployment failures

Deployment always requires explicit human approval.

---

# 5. Workflow Position

```text id="nm6twg"
Planner
    │
Architect
    │
Developer
    │
Tester
    │
Security
    │
Documentation
    │
Reviewer
    │
Deployment
    │
Human Approval
```

The Deployment Agent is the final AI agent before the workflow is handed to the user.

---

# 6. Required Inputs

```json id="gtlwm6"
{
  "task": {},
  "executionPlan": {},
  "implementation": {},
  "reviewReport": {},
  "securityReport": {},
  "documentationReport": {},
  "repository": {},
  "artifacts": [],
  "memory": {}
}
```

---

# 7. Repository Context

The Deployment Agent understands:

Repository layout

Build system

Package manager

Runtime

Framework

Docker

Docker Compose

Environment variables

Build scripts

CI/CD configuration

Release process

Deployment targets

---

# 8. Allowed MCP Tools

Read

✓ GitHub

✓ Filesystem

Execute

✓ Terminal (build and validation only)

✓ Docker

Future

✓ Kubernetes

✓ Cloud providers

✓ Container registries

Not Allowed

✗ Production deployment

✗ Infrastructure modification

✗ Secret rotation

✗ DNS modification

---

# 9. Capabilities

Build validation

Docker validation

Dependency verification

Environment validation

Release packaging

Artifact generation

Deployment checklist generation

Deployment readiness scoring

Container validation

Release metadata generation

---

# 10. Internal Workflow

```text id="d1h4xu"
Receive Context
      │
Validate Inputs
      │
Load Repository
      │
Validate Build
      │
Validate Dependencies
      │
Validate Docker
      │
Validate Environment
      │
Generate Release Package
      │
Generate Deployment Checklist
      │
Generate Release Report
      │
Return Results
```

---

# 11. Deployment Validation

Verify:

Project builds successfully

Required dependencies exist

Runtime compatible

Environment variables documented

Configuration valid

Container configuration valid

Required artifacts present

No unresolved review blockers

---

# 12. Build Validation

Validate:

Package installation

Compilation

Type checking

Linting (if configured)

Build generation

Build artifacts

Exit status

---

# 13. Docker Validation

Inspect:

Dockerfile

docker-compose.yml

Container configuration

Ports

Volumes

Environment variables

Entrypoint

Health checks

Image size (future)

---

# 14. Environment Validation

Verify required variables:

Database URL

API keys

Secrets

Ports

Runtime options

Storage

Cache

Logging

Variables should be documented but never expose secret values.

---

# 15. Release Packaging

Prepare:

Build artifacts

Documentation bundle

Release notes

Version metadata

Deployment instructions

Configuration template

Change summary

Checksums (future)

---

# 16. Deployment Checklist

Generate a checklist covering:

Build successful

Tests passed

Security review passed

Documentation updated

Environment configured

Dependencies verified

Containers validated

Human approval pending

---

# 17. Deployment Targets

Current support

Docker

Docker Compose

Future

Kubernetes

Google Cloud Run

AWS ECS

Azure Container Apps

DigitalOcean

Vercel

Railway

Fly.io

---

# 18. Generated Artifacts

Deployment Report

Deployment Checklist

Release Package

Release Metadata

Build Summary

Docker Validation Report

Environment Validation Report

Deployment Instructions

---

# 19. Output Schema

```json id="jblkn3"
{
  "status":"COMPLETED",

  "deploymentReady":true,

  "buildPassed":true,

  "dockerValidated":true,

  "releasePackageGenerated":true,

  "readinessScore":97
}
```

---

# 20. Deployment Report Schema

```json id="tifwvm"
{
  "deploymentTarget":"Docker",

  "runtime":"Python 3.12",

  "status":"READY",

  "warnings":[],

  "recommendations":[]
}
```

---

# 21. Validation Rules

Implementation approved

Security review complete

Documentation complete

Required files exist

Build configuration detected

Repository accessible

---

# 22. Failure Conditions

Build failure

Missing dependency

Invalid Dockerfile

Invalid Compose configuration

Missing environment template

Unsupported runtime

Terminal timeout

---

# 23. Retry Policy

Maximum retries

3

Retry triggers

Build timeout

Docker validation failure

Temporary filesystem issue

Package installation interruption

---

# 24. Events

DEPLOYMENT_STARTED

BUILD_VALIDATED

DEPENDENCIES_VERIFIED

DOCKER_VALIDATED

ENVIRONMENT_VALIDATED

RELEASE_PACKAGE_CREATED

DEPLOYMENT_REPORT_GENERATED

DEPLOYMENT_COMPLETED

DEPLOYMENT_FAILED

---

# 25. Logging

Example

```json id="wtrw6m"
{
  "agent":"Deployment",

  "level":"INFO",

  "message":"Docker configuration validated successfully."
}
```

---

# 26. Metrics

Build duration

Dependencies verified

Docker files validated

Environment variables documented

Artifacts generated

Readiness score

Execution duration

Tool calls

---

# 27. Memory Usage

Reads

Execution Plan

Implementation Artifacts

Review Report

Security Report

Documentation Report

Repository Memory

Task Memory

Writes

Deployment Report

Deployment Checklist

Release Metadata

Release Package

Updated Task Memory

---

# 28. Human Approval Requirements

The Deployment Agent prepares releases but cannot deploy them.

Final actions require human approval, including:

Creating release tags

Publishing releases

Pushing containers

Deploying infrastructure

Promoting environments

Executing production deployments

---

# 29. Prompt Contract

The Deployment Agent should think like a Senior DevOps Engineer.

Objectives

Validate deployment readiness.

Protect production environments.

Verify reproducibility.

Generate deployment artifacts.

Avoid assumptions about infrastructure.

Never deploy automatically.

Produce structured JSON only.

---

# 30. Example Input

```json id="g77c7v"
{
  "task":"Implement JWT authentication",

  "reviewReport":{},

  "securityReport":{}
}
```

---

# 31. Example Output

```json id="8r1tlv"
{
  "summary":"Application is ready for deployment.",

  "deploymentReady":true,

  "readinessScore":98,

  "artifacts":[
    {
      "type":"DEPLOYMENT_REPORT"
    },
    {
      "type":"DEPLOYMENT_CHECKLIST"
    },
    {
      "type":"RELEASE_PACKAGE"
    }
  ]
}
```

---

# 32. Deployment Readiness Score

The Deployment Agent calculates a readiness score (0–100) using weighted factors:

Build Success

25%

Testing Status

20%

Security Status

20%

Documentation Completeness

10%

Configuration Validation

10%

Dependency Health

10%

Container Validation

5%

Scores below a configurable threshold (for example, 80) should be flagged for additional review before release.

---

# 33. Release Metadata

Each release package should include:

Version

Build timestamp

Git commit hash

Target branch

Supported runtime

Dependency summary

Feature summary

Bug fixes

Security changes

Migration requirements

Known limitations

---

# 34. Quality Principles

The Deployment Agent should always:

* Prioritize safe, repeatable deployments.
* Validate rather than assume.
* Produce deterministic deployment artifacts.
* Clearly distinguish warnings from blockers.
* Preserve human control over production releases.
* Never expose secrets in generated artifacts.
* Keep deployment documentation synchronized with the implementation.
* Generate actionable recommendations when deployment readiness is incomplete.

The Deployment Agent is successful when it produces a complete, reproducible, and well-documented deployment package that enables a human operator to confidently release the application while maintaining operational safety and transparency.

# SCHEMA.md (Part 3.3)

# Orchestrator & Communication Specification

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** AI Orchestrator

**Version:** 1.0

**Priority:** Critical

---

# 1. Purpose

The AI Orchestrator is the central intelligence coordinator of ForgeAI.

It is **not** an AI agent.

Instead, it functions as the operating system of the entire multi-agent ecosystem by managing execution, communication, task delegation, memory synchronization, event streaming, retries, approvals, and workflow state.

Every agent communicates **only** with the Orchestrator.

No direct agent-to-agent communication is permitted.

---

# 2. Mission Statement

Coordinate a team of specialized AI agents in a deterministic, observable, secure, and fault-tolerant manner while maintaining complete workflow transparency and human oversight.

---

# 3. Responsibilities

The Orchestrator is responsible for:

✓ Workflow creation

✓ Task scheduling

✓ Agent lifecycle management

✓ Agent delegation

✓ Memory synchronization

✓ Artifact management

✓ Event streaming

✓ Retry coordination

✓ Error recovery

✓ Human approval checkpoints

✓ Progress tracking

✓ Metrics collection

✓ Workflow termination

---

# 4. Explicit Non-Responsibilities

The Orchestrator MUST NOT:

* Generate code
* Review code
* Write documentation
* Analyze repositories
* Execute shell commands
* Call MCP tools directly
* Replace agent reasoning

It coordinates agents but never performs their responsibilities.

---

# 5. High-Level Architecture

```text id="w9f3ka"
                     User
                       │
                       ▼
                API Controller
                       │
                       ▼
                AI Orchestrator
                       │
 ┌─────────────────────┼─────────────────────┐
 │                     │                     │
Planner          Architect          Developer
 │                     │                     │
 └──────────────┬──────┴──────────────┬─────┘
                ▼                     ▼
           Tester              Security
                │                     │
                └──────────┬──────────┘
                           ▼
                    Documentation
                           │
                           ▼
                      Reviewer
                           │
                           ▼
                     Deployment
                           │
                           ▼
                   Human Approval
```

---

# 6. Orchestrator Lifecycle

Every task follows this lifecycle.

```text id="9x8zfh"
Task Created

↓

Workflow Initialized

↓

Planner

↓

Architect

↓

Developer

↓

Tester

↓

Security

↓

Documentation

↓

Reviewer

↓

Deployment

↓

Human Approval

↓

Pull Request

↓

Completed
```

---

# 7. Workflow State Machine

Each task transitions through predefined states.

```text id="4ngsht"
CREATED

↓

QUEUED

↓

PLANNING

↓

ARCHITECTING

↓

DEVELOPING

↓

TESTING

↓

SECURITY

↓

DOCUMENTING

↓

REVIEWING

↓

DEPLOYMENT_READY

↓

WAITING_FOR_APPROVAL

↓

PR_READY

↓

COMPLETED

or

FAILED

or

CANCELLED
```

Transitions are strictly controlled by the Orchestrator.

---

# 8. Workflow Graph

Every task is represented as a Directed Acyclic Graph (DAG).

Example

```text id="4f6k5n"
Planner
   │
   ▼
Architect
   │
   ▼
Developer
   │
   ▼
Tester
   │
 ┌─┴─────────┐
 ▼           ▼
Security Documentation
 └──────┬────┘
        ▼
    Reviewer
        │
        ▼
   Deployment
        │
        ▼
 Human Approval
```

The Orchestrator determines execution order based on dependencies.

---

# 9. Task Graph Schema

```json id="0vzz4h"
{
  "taskId":"",

  "nodes":[

  ],

  "edges":[

  ],

  "status":"RUNNING"
}
```

---

# 10. Agent Scheduling

Agents are executed only when:

Dependencies satisfied

Previous stage completed

Required artifacts available

Required memory synchronized

No blocking errors exist

---

# 11. Delegation Rules

The Orchestrator delegates work.

Example

Planner

↓

Architect

↓

Developer

↓

Tester

↓

Security

↓

Reviewer

↓

Deployment

Agents never choose the next agent.

The Orchestrator makes every scheduling decision.

---

# 12. Parallel Execution

Independent agents may run simultaneously.

Example

```text id="m1gwq5"
Developer

↓

Tester

↓

┌───────────────┐

Security   Documentation

└───────┬───────┘

        ▼

    Reviewer
```

Parallel execution allowed only if:

No shared write conflicts

Dependencies satisfied

Task graph permits parallelism

---

# 13. Shared Memory Management

The Orchestrator owns Task Memory.

Agents receive copies.

Agents never directly edit shared memory.

Memory update flow

```text id="w7pdcb"
Agent

↓

Output

↓

Validation

↓

Memory Merge

↓

Next Agent
```

---

# 14. Artifact Management

Artifacts include:

Code patches

Reports

Tests

Documentation

Security reports

Review reports

Deployment package

Every artifact receives

UUID

Version

Author

Timestamp

Checksum

Status

---

# 15. Communication Protocol

Communication always follows:

```text id="6fh8cv"
Orchestrator

↓

Agent

↓

Structured Output

↓

Validation

↓

Orchestrator

↓

Next Agent
```

Direct communication is forbidden.

---

# 16. Event Bus

Every workflow event is published.

Examples

TASK_CREATED

AGENT_STARTED

AGENT_COMPLETED

AGENT_FAILED

ARTIFACT_CREATED

MEMORY_UPDATED

WORKFLOW_COMPLETED

---

# 17. Event Schema

```json id="k8q0f8"
{
  "eventId":"",

  "workflowId":"",

  "taskId":"",

  "agent":"Developer",

  "type":"AGENT_COMPLETED",

  "timestamp":"",

  "payload":{}
}
```

---

# 18. WebSocket Streaming

The Orchestrator streams:

Current agent

Progress

Logs

Artifacts

Timeline

Failures

Retry status

Metrics

The frontend never polls long-running tasks.

---

# 19. Retry Strategy

Each agent declares

Recoverable

Non-recoverable

Maximum retries

Backoff policy

The Orchestrator manages retries.

Example

```text id="gvtjlwm"
Failure

↓

Retry

↓

Retry

↓

Retry

↓

Failed
```

---

# 20. Retry Policy

Default

Maximum

3

Backoff

5 seconds

10 seconds

20 seconds

Retry only for recoverable failures.

---

# 21. Failure Recovery

Recoverable

Timeout

Temporary MCP failure

Network interruption

Filesystem lock

Non-recoverable

Invalid repository

Corrupted artifacts

Invalid schema

Missing permissions

Unsupported language

---

# 22. Approval Gates

The Orchestrator pauses execution for:

Deleting files

Breaking API changes

Database migrations

Dependency removal

Pull Request creation

Deployment preparation

Human approval is mandatory.

---

# 23. Human Approval Schema

```json id="3yd5jr"
{
  "approvalId":"",

  "taskId":"",

  "reason":"Database migration",

  "status":"PENDING"
}
```

Possible states

PENDING

APPROVED

REJECTED

EXPIRED

---

# 24. Cancellation

Users may cancel.

The Orchestrator

Stops active agents

Persists artifacts

Marks workflow cancelled

Preserves logs

---

# 25. Pause & Resume

Workflow supports

Pause

↓

Persist State

↓

Resume

↓

Continue From Previous Stage

No completed work is repeated unless explicitly requested.

---

# 26. State Persistence

Persist

Workflow

Artifacts

Logs

Task memory

Metrics

Current agent

Execution graph

Retry count

Allows crash recovery.

---

# 27. Logging

Everything is logged.

Workflow

Agent execution

Tool usage

Approvals

Errors

Retries

Memory updates

Artifacts

User actions

---

# 28. Metrics

Workflow duration

Agent duration

Queue time

Retries

Failures

Artifacts generated

Memory size

Token usage

Approval latency

Success rate

---

# 29. Validation Pipeline

Every agent output passes:

Schema validation

↓

Artifact validation

↓

Memory validation

↓

Dependency validation

↓

Workflow validation

↓

Next Agent

---

# 30. Orchestrator Output Schema

```json id="1nibbs"
{
  "workflowId":"",

  "currentState":"TESTING",

  "currentAgent":"Tester",

  "progress":64,

  "completedStages":[

  ],

  "remainingStages":[

  ]
}
```

---

# 31. Workflow Completion

A workflow is complete only when:

Planner completed

Architect completed

Developer completed

Tester completed

Security completed

Documentation completed

Reviewer completed

Deployment completed

Human approval completed

Pull request prepared

---

# 32. Workflow Failure

Workflow fails when:

Critical agent failure

Human rejection

Repository unavailable

Maximum retries exceeded

Corrupted workflow state

Failure artifacts are preserved.

---

# 33. Prompt Contract

Although the Orchestrator is not an AI agent, its scheduling logic should follow these principles:

* Never skip mandatory workflow stages.
* Never bypass human approval gates.
* Prefer deterministic execution.
* Maximize safe parallelism.
* Preserve auditability.
* Ensure downstream agents receive validated context only.
* Isolate failures and recover whenever possible.
* Maintain a complete execution history.

---

# 34. Example Workflow

User Request

↓

Planner

↓

Architecture Blueprint

↓

Developer

↓

Generated Code

↓

Tester

↓

Tests Pass

↓

Security

↓

No Critical Findings

↓

Documentation

↓

README Updated

↓

Reviewer

↓

Approved

↓

Deployment

↓

Release Package

↓

Human Approval

↓

Pull Request Ready

---

# 35. Design Principles

The Orchestrator should always:

* Serve as the single source of truth for workflow state.
* Own scheduling, coordination, and lifecycle management.
* Keep agents independent and loosely coupled.
* Maintain deterministic task execution.
* Support safe parallel execution where dependencies allow.
* Guarantee complete observability through events and logs.
* Preserve all artifacts and execution history.
* Enforce human oversight before irreversible actions.
* Enable fault tolerance through retries, persistence, and resumable workflows.

The Orchestrator is successful when every engineering task progresses through a transparent, reproducible, and auditable workflow, allowing specialized AI agents to collaborate efficiently while maintaining security, reliability, and human control.

# SCHEMA.md (Part 4.1)

# MCP Foundation Specification

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** Model Context Protocol (MCP) Foundation

**Version:** 1.0

**Status:** Core Infrastructure

---

# 1. Purpose

The Model Context Protocol (MCP) Foundation defines the standard communication layer between ForgeAI agents and external tools.

The MCP layer abstracts all external systems behind a unified interface, allowing AI agents to request actions without knowing implementation details.

Examples of MCP Servers:

* GitHub
* Filesystem
* Terminal
* Docker
* Browser
* Database (Future)
* Kubernetes (Future)
* Cloud Providers (Future)

The MCP Foundation ensures:

* Standardized communication
* Security
* Auditability
* Permission enforcement
* Extensibility
* Tool independence

---

# 2. Architecture

```text
                        AI Agent
                           │
                           ▼
                    AI Orchestrator
                           │
                           ▼
                    MCP Manager
                           │
      ┌────────────┬─────────────┬──────────────┬─────────────┐
      ▼            ▼             ▼              ▼
 GitHub MCP   Filesystem MCP  Terminal MCP  Docker MCP
      │            │             │              │
      ▼            ▼             ▼              ▼
 External APIs  Local Files   Shell Runtime   Docker Engine
```

The AI Agent never communicates directly with external tools.

All communication passes through:

Agent

↓

Orchestrator

↓

MCP Manager

↓

Tool

↓

Orchestrator

↓

Agent

---

# 3. MCP Design Principles

Every MCP implementation must:

* Be stateless where possible
* Use structured JSON communication
* Validate every request
* Enforce permissions
* Produce deterministic responses
* Support audit logging
* Return standardized errors
* Be replaceable without changing agents

---

# 4. MCP Components

Every MCP server consists of:

Tool Definition

↓

Permission Manager

↓

Request Validator

↓

Execution Engine

↓

Response Formatter

↓

Audit Logger

↓

Error Handler

---

# 5. MCP Manager

The MCP Manager is responsible for:

✓ Tool discovery

✓ Tool registration

✓ Request routing

✓ Permission checks

✓ Authentication

✓ Execution

✓ Response validation

✓ Audit logging

✓ Error normalization

---

# 6. Tool Registration

Each tool registers itself during application startup.

Registration Schema

```json
{
  "toolId":"github",

  "name":"GitHub MCP",

  "version":"1.0",

  "capabilities":[
      "read_repository",
      "create_branch",
      "create_pull_request"
  ],

  "permissions":[
      "repository.read"
  ]
}
```

---

# 7. Tool Metadata

Every registered tool contains

Tool ID

Display Name

Version

Description

Supported Actions

Permissions

Status

Health

Timeout

Maximum Execution Time

---

# 8. Tool Lifecycle

Every MCP tool follows the same lifecycle.

```text
REGISTERED

↓

INITIALIZED

↓

READY

↓

EXECUTING

↓

COMPLETED

or

FAILED

↓

READY
```

---

# 9. Tool Health States

UNKNOWN

INITIALIZING

READY

BUSY

DEGRADED

OFFLINE

FAILED

---

# 10. Base MCP Request Schema

Every request follows the same format.

```json
{
  "requestId":"uuid",

  "workflowId":"uuid",

  "taskId":"uuid",

  "agent":"Developer",

  "tool":"github",

  "action":"read_repository",

  "parameters":{

  },

  "timestamp":"..."
}
```

---

# 11. Base MCP Response Schema

```json
{
  "success":true,

  "requestId":"uuid",

  "tool":"github",

  "action":"read_repository",

  "executionTime":145,

  "data":{

  },

  "metadata":{

  }
}
```

---

# 12. Tool Parameters

Parameters must be

Typed

Validated

Documented

Immutable during execution

Example

```json
{
  "repository":"ForgeAI",

  "branch":"main",

  "path":"README.md"
}
```

---

# 13. Response Metadata

Every response includes

Execution Time

Tool Version

Timestamp

Warnings

Rate Limit Information

Cache Status

Example

```json
{
  "executionTime":145,

  "cached":false,

  "toolVersion":"1.0.0"
}
```

---

# 14. Authentication

Every MCP server must authenticate before execution.

Supported methods

OAuth

Personal Access Token

JWT

Service Account

Local Trust

Future

OIDC

mTLS

---

# 15. Authentication Schema

```json
{
  "type":"OAuth",

  "credentialId":"github-default"
}
```

Secrets are never stored in workflow memory.

---

# 16. Authorization

Authentication proves identity.

Authorization determines permissions.

Permission evaluation occurs before execution.

---

# 17. Permission Model

Permissions are action-based.

Examples

repository.read

repository.write

filesystem.read

filesystem.write

terminal.execute

docker.run

browser.navigate

browser.read

---

# 18. Agent Permission Matrix

| Agent         | GitHub     | Filesystem         | Terminal | Docker | Browser |
| ------------- | ---------- | ------------------ | -------- | ------ | ------- |
| Planner       | Read       | Read               | No       | No     | Read    |
| Architect     | Read       | Read               | No       | No     | Read    |
| Developer     | Read/Write | Read/Write         | Limited  | No     | Read    |
| Tester        | Read       | Write (tests only) | Limited  | Yes    | Read    |
| Security      | Read       | Read               | Limited  | Yes    | Read    |
| Documentation | Read       | Write (docs only)  | No       | No     | Read    |
| Reviewer      | Read       | Read               | No       | No     | Read    |
| Deployment    | Read       | Read               | Limited  | Yes    | Read    |

---

# 19. Permission Validation

Execution Pipeline

```text
Request

↓

Authentication

↓

Authorization

↓

Parameter Validation

↓

Execution

↓

Audit Log

↓

Response
```

---

# 20. Request Validation

Every request validates

Tool exists

Action exists

Parameters valid

Permissions valid

Authentication valid

Workflow active

Agent authorized

---

# 21. Input Validation Rules

Reject

Missing fields

Unknown actions

Malformed JSON

Oversized payloads

Unsupported file types

Invalid repository

Invalid path

---

# 22. Execution States

QUEUED

VALIDATING

RUNNING

WAITING

COMPLETED

FAILED

TIMEOUT

CANCELLED

---

# 23. Timeout Policy

Every tool defines

Connection timeout

Execution timeout

Maximum runtime

Default

120 seconds

---

# 24. Retry Policy

Retry only when

Network failure

Temporary API outage

Rate limiting

Filesystem lock

Never retry

Permission denied

Invalid parameters

Authentication failure

---

# 25. Standard Error Schema

```json
{
  "success":false,

  "error":{

      "code":"PERMISSION_DENIED",

      "message":"Developer Agent cannot delete repositories.",

      "recoverable":false

  }
}
```

---

# 26. Error Categories

VALIDATION_ERROR

AUTHENTICATION_ERROR

AUTHORIZATION_ERROR

NOT_FOUND

TIMEOUT

NETWORK_ERROR

RATE_LIMIT

EXECUTION_ERROR

INTERNAL_ERROR

UNKNOWN_ERROR

---

# 27. Audit Logging

Every tool call is logged.

Captured fields

Workflow

Task

Agent

Tool

Action

Parameters

Execution Time

Success

Failure

Timestamp

---

# 28. Audit Log Schema

```json
{
  "logId":"",

  "workflowId":"",

  "agent":"Developer",

  "tool":"github",

  "action":"commit",

  "status":"SUCCESS",

  "duration":210,

  "timestamp":"..."
}
```

Sensitive parameters must be redacted before logging.

---

# 29. Event Integration

Every tool execution emits events.

Examples

TOOL_REQUESTED

TOOL_STARTED

TOOL_COMPLETED

TOOL_FAILED

TOOL_TIMEOUT

TOOL_RETRIED

PERMISSION_DENIED

---

# 30. Event Schema

```json
{
  "event":"TOOL_COMPLETED",

  "tool":"filesystem",

  "requestId":"",

  "workflowId":"",

  "timestamp":"..."
}
```

---

# 31. Rate Limiting

Each tool may define:

Requests per minute

Concurrent executions

Daily quotas

Burst limits

The MCP Manager enforces limits centrally.

---

# 32. Caching

Read-only operations may be cached.

Cache metadata

```json
{
  "cached":true,

  "ttl":300
}
```

Write operations are never cached.

---

# 33. Security Principles

Every MCP server must:

* Validate every request.
* Follow least-privilege access.
* Never expose secrets.
* Sanitize user inputs.
* Restrict file system scope where applicable.
* Prevent arbitrary command execution.
* Record all actions in the audit log.
* Return structured, non-sensitive error messages.

---

# 34. Versioning

Every tool exposes:

Tool Version

Schema Version

API Version

Example

```json
{
  "toolVersion":"1.0.0",

  "schemaVersion":"1.0",

  "apiVersion":"v1"
}
```

This allows tools to evolve independently while remaining compatible with the Orchestrator.

---

# 35. Tool Capability Discovery

The MCP Manager can query registered tools.

Example response

```json
{
  "tool":"github",

  "capabilities":[
      "read_repository",
      "read_file",
      "create_branch",
      "create_pull_request"
  ]
}
```

Agents should rely on declared capabilities rather than hardcoded assumptions.

---

# 36. Extensibility

New MCP servers can be added without modifying existing agents, provided they implement the base MCP contract defined in this document.

Future integrations may include:

* Kubernetes
* Cloud providers
* SQL databases
* Vector databases
* Package registries
* CI/CD platforms
* Monitoring systems
* Issue trackers

---

# 37. Quality Principles

The MCP Foundation should always:

* Present a single, consistent interface to all external tools.
* Separate agent reasoning from tool execution.
* Enforce authentication and authorization on every request.
* Provide deterministic request and response schemas.
* Maintain complete audit trails for observability.
* Handle failures gracefully with standardized error contracts.
* Support extensibility without breaking existing workflows.
* Preserve security by isolating tool execution from agent logic.

The MCP Foundation is successful when AI agents can safely, reliably, and transparently interact with external systems through a unified protocol while maintaining strict security, observability, and operational consistency.

# SCHEMA.md (Part 4.2.1)

# GitHub MCP Specification — Repository Operations

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** GitHub MCP Server

**Module:** Repository Operations

**Version:** 1.0

**Status:** Core MCP Tool

---

# 1. Purpose

The Repository Operations module provides ForgeAI agents with a secure, standardized interface for interacting with GitHub repositories.

It abstracts the GitHub REST and GraphQL APIs behind a consistent MCP contract, allowing agents to discover repositories, retrieve metadata, inspect repository structure, and prepare repositories for downstream engineering tasks.

The GitHub MCP never exposes raw GitHub API responses directly to agents.

---

# 2. Responsibilities

The Repository Operations module is responsible for:

✓ Connecting repositories

✓ Validating repository access

✓ Retrieving repository metadata

✓ Retrieving repository tree

✓ Discovering default branch

✓ Reading repository configuration

✓ Repository synchronization

✓ Repository health information

✓ Repository capability discovery

---

# 3. Supported Operations

| Operation                 | Description                   |
| ------------------------- | ----------------------------- |
| connect_repository        | Connect repository to ForgeAI |
| validate_repository       | Validate access               |
| repository_info           | Retrieve repository metadata  |
| repository_tree           | Retrieve directory tree       |
| repository_languages      | Detect languages              |
| repository_branches       | List branches                 |
| repository_default_branch | Retrieve default branch       |
| repository_statistics     | Repository statistics         |
| repository_sync           | Refresh repository metadata   |

---

# 4. MCP Capability Declaration

```json id="ghrepo01"
{
  "tool":"github",
  "module":"repository",
  "version":"1.0",
  "capabilities":[
    "connect_repository",
    "repository_info",
    "repository_tree",
    "repository_languages",
    "repository_statistics",
    "repository_sync"
  ]
}
```

---

# 5. Authentication

Supported

OAuth App

GitHub App

Personal Access Token

Fine-grained Personal Access Token

Enterprise GitHub

Authentication occurs before every operation.

---

# 6. Permission Requirements

Repository Read

Repository Metadata

Repository Contents (Read)

Branch Read

Actions Read (optional)

The Repository module never requires write permissions.

---

# 7. Connect Repository

Purpose

Register a GitHub repository inside ForgeAI.

Operation

```text id="repoop01"
connect_repository
```

---

Request Schema

```json id="repoop02"
{
  "repository":"owner/repository",
  "provider":"github",
  "branch":"main"
}
```

---

Validation

Repository exists

Authentication valid

User has access

Repository supported

---

Response

```json id="repoop03"
{
  "repositoryId":"uuid",
  "status":"CONNECTED",
  "defaultBranch":"main"
}
```

---

Events

REPOSITORY_CONNECTING

REPOSITORY_CONNECTED

REPOSITORY_CONNECTION_FAILED

---

# 8. Validate Repository

Purpose

Verify repository accessibility.

Operation

```text id="repoop04"
validate_repository
```

---

Response

```json id="repoop05"
{
  "accessible":true,
  "permissions":"READ",
  "private":true
}
```

---

# 9. Repository Metadata

Purpose

Retrieve repository metadata.

Operation

```text id="repoop06"
repository_info
```

---

Response Schema

```json id="repoop07"
{
  "id":"",

  "name":"ForgeAI",

  "owner":"OpenAI",

  "private":true,

  "visibility":"PRIVATE",

  "defaultBranch":"main",

  "description":"",

  "homepage":"",

  "license":"MIT",

  "language":"Python",

  "stars":100,

  "forks":20,

  "watchers":50,

  "openIssues":4,

  "createdAt":"",

  "updatedAt":""
}
```

---

# 10. Repository Languages

Purpose

Identify repository languages.

Operation

```text id="repoop08"
repository_languages
```

---

Example Response

```json id="repoop09"
{
  "languages":[
    {
      "name":"Python",
      "percentage":78
    },
    {
      "name":"TypeScript",
      "percentage":22
    }
  ]
}
```

---

# 11. Repository Statistics

Retrieve

Stars

Forks

Contributors

Commits

Open Issues

Open Pull Requests

Releases

Tags

Latest Commit

Response

```json id="repoop10"
{
  "stars":120,

  "forks":12,

  "contributors":5,

  "commits":814
}
```

---

# 12. Repository Tree

Purpose

Retrieve repository directory structure.

Operation

```text id="repoop11"
repository_tree
```

---

Example Response

```json id="repoop12"
{
  "root":[
    {
      "name":"backend",
      "type":"directory"
    },
    {
      "name":"frontend",
      "type":"directory"
    },
    {
      "name":"README.md",
      "type":"file"
    }
  ]
}
```

---

Tree Depth

Configurable

Default

10

Maximum

25

---

# 13. Repository Structure

Returned information

Folders

Files

File Types

Depth

File Size

Path

Extension

SHA

Example

```json id="repoop13"
{
  "path":"backend/auth/service.py",

  "type":"file",

  "extension":"py",

  "size":8214,

  "sha":"..."
}
```

---

# 14. Default Branch

Purpose

Retrieve default branch.

Operation

```text id="repoop14"
repository_default_branch
```

---

Response

```json id="repoop15"
{
  "defaultBranch":"main"
}
```

---

# 15. Branch Discovery

Retrieve

Name

Latest Commit

Protected

Created Date

Example

```json id="repoop16"
{
  "branches":[
    {
      "name":"main",
      "protected":true
    },
    {
      "name":"feature/auth",
      "protected":false
    }
  ]
}
```

---

# 16. Repository Sync

Purpose

Refresh repository metadata.

Operation

```text id="repoop17"
repository_sync
```

Refreshes

Metadata

Tree

Statistics

Branches

Languages

Latest Commit

---

# 17. Request Schema

Every repository request follows

```json id="repoop18"
{
  "requestId":"",

  "workflowId":"",

  "agent":"Architect",

  "action":"repository_tree",

  "parameters":{

  }
}
```

---

# 18. Response Schema

```json id="repoop19"
{
  "success":true,

  "executionTime":210,

  "data":{

  },

  "metadata":{

      "cached":false,

      "rateLimitRemaining":4923

  }
}
```

---

# 19. Validation Rules

Repository exists

Valid owner

Repository accessible

Supported provider

Authentication valid

Repository not archived

Repository size below configured limit

---

# 20. Repository Limits

Maximum repository size

5 GB

Maximum file size

20 MB

Maximum tree depth

25

Maximum request duration

120 seconds

These limits are configurable.

---

# 21. Caching

Cache

Repository metadata

Repository tree

Language statistics

Branch list

Default cache TTL

300 seconds

Write operations invalidate cache automatically.

---

# 22. Error Codes

REPOSITORY_NOT_FOUND

ACCESS_DENIED

INVALID_OWNER

INVALID_REPOSITORY

REPOSITORY_ARCHIVED

RATE_LIMIT_EXCEEDED

AUTHENTICATION_FAILED

NETWORK_ERROR

TIMEOUT

UNKNOWN_ERROR

---

# 23. Audit Logging

Every repository operation logs

Repository

Agent

Action

Execution Time

Authentication Method

Success

Failure

Timestamp

Example

```json id="repoop20"
{
  "tool":"GitHub",

  "operation":"repository_tree",

  "repository":"ForgeAI",

  "agent":"Architect",

  "status":"SUCCESS"
}
```

---

# 24. Events

REPOSITORY_CONNECTED

REPOSITORY_SYNCED

METADATA_UPDATED

TREE_GENERATED

DEFAULT_BRANCH_FOUND

REPOSITORY_VALIDATED

REPOSITORY_FAILED

---

# 25. Performance Goals

Metadata retrieval

< 500 ms

Tree generation

< 2 s

Repository validation

< 500 ms

Branch discovery

< 1 s

Repository synchronization

< 5 s

Targets depend on repository size and network conditions.

---

# 26. Security Principles

Repository Operations must:

Never expose authentication tokens.

Never expose private repository information to unauthorized users.

Validate permissions before every request.

Respect GitHub rate limits.

Sanitize repository names.

Redact sensitive metadata.

Use HTTPS for all communication.

---

# 27. Example Workflow

```text id="repoop21"
Planner

↓

Repository Validation

↓

Metadata Retrieval

↓

Repository Tree

↓

Default Branch

↓

Language Detection

↓

Statistics

↓

Repository Ready
```

---

# 28. Future Enhancements

Planned capabilities include:

* Monorepo awareness
* Sparse checkout support
* Submodule discovery
* Git LFS awareness
* Dependency graph retrieval
* CODEOWNERS parsing
* Repository topics and labels
* Security advisory integration
* Repository ruleset inspection

---

# 29. Quality Principles

The GitHub MCP Repository Operations module should always:

* Provide a consistent abstraction over GitHub APIs.
* Return normalized, structured data independent of GitHub's native response formats.
* Validate authentication and permissions before every operation.
* Cache safe read-only responses to improve performance.
* Preserve repository integrity by remaining read-only within this module.
* Produce deterministic request and response schemas.
* Maintain complete audit trails for every repository interaction.
* Be extensible to support future repository providers without changing the agent interface.

The Repository Operations module is successful when ForgeAI agents can reliably discover, understand, and synchronize repositories through a secure, observable, and provider-agnostic interface.

# SCHEMA.md (Part 4.2.2.1)

# GitHub MCP Specification — Branch Operations

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** GitHub MCP Server

**Module:** Branch Operations

**Version:** 1.0

**Status:** Core MCP Tool

---

# 1. Purpose

The Branch Operations module provides ForgeAI with a secure and standardized interface for managing Git branches within GitHub repositories.

Every implementation performed by ForgeAI occurs on an isolated feature branch. The default branch (`main`, `master`, or repository default) must never be modified directly by AI agents.

All branch operations are routed through the MCP Manager and validated before execution.

---

# 2. Responsibilities

The Branch Operations module is responsible for:

✓ Creating feature branches

✓ Validating branch names

✓ Listing branches

✓ Retrieving branch metadata

✓ Checking out branches

✓ Renaming branches

✓ Deleting branches

✓ Detecting branch conflicts

✓ Verifying branch protection rules

✓ Auditing all branch activity

---

# 3. Supported Operations

| Operation         | Description                  |
| ----------------- | ---------------------------- |
| create_branch     | Create a new branch          |
| delete_branch     | Delete a branch              |
| rename_branch     | Rename a branch              |
| checkout_branch   | Switch working branch        |
| list_branches     | Retrieve repository branches |
| branch_info       | Retrieve branch metadata     |
| validate_branch   | Validate branch rules        |
| branch_protection | Retrieve protection rules    |

---

# 4. Branch Naming Convention

ForgeAI automatically generates branch names.

Pattern

```text id="ghbranch01"
feature/<task-id>-<slug>
```

Examples

```text id="ghbranch02"
feature/task-104-jwt-auth

feature/task-205-user-profile

feature/task-908-fix-login
```

Other supported prefixes

```text id="ghbranch03"
feature/

bugfix/

hotfix/

refactor/

docs/

test/

release/

experiment/
```

---

# 5. Branch Lifecycle

```text id="ghbranch04"
Create Branch

↓

Checkout Branch

↓

Implementation

↓

Testing

↓

Security Review

↓

Pull Request

↓

Merge

↓

Delete Branch (Optional)
```

---

# 6. Create Branch

Purpose

Create an isolated feature branch.

Operation

```text id="ghbranch05"
create_branch
```

---

Request Schema

```json id="ghbranch06"
{
  "repository":"owner/repository",

  "baseBranch":"main",

  "branchName":"feature/task-104-jwt-auth"
}
```

---

Validation

Repository exists

Base branch exists

Branch name valid

Branch does not already exist

User has write permission

---

Response

```json id="ghbranch07"
{
  "success":true,

  "branch":"feature/task-104-jwt-auth",

  "baseBranch":"main",

  "commit":"f8b7d1..."
}
```

---

Events

BRANCH_CREATED

---

# 7. Delete Branch

Purpose

Delete a feature branch after merge or cancellation.

Operation

```text id="ghbranch08"
delete_branch
```

---

Validation

Cannot delete default branch.

Cannot delete protected branch.

Cannot delete active working branch.

Must have delete permission.

---

Request

```json id="ghbranch09"
{
  "repository":"owner/repository",

  "branch":"feature/task-104-jwt-auth"
}
```

---

Response

```json id="ghbranch10"
{
  "success":true,

  "deleted":true
}
```

---

Events

BRANCH_DELETED

---

# 8. Rename Branch

Purpose

Rename an existing branch.

Operation

```text id="ghbranch11"
rename_branch
```

---

Request

```json id="ghbranch12"
{
  "repository":"owner/repository",

  "oldName":"feature/task-104-auth",

  "newName":"feature/task-104-jwt-auth"
}
```

---

Validation

Old branch exists.

New branch does not exist.

New name valid.

Branch not protected.

---

Response

```json id="ghbranch13"
{
  "success":true,

  "oldName":"feature/task-104-auth",

  "newName":"feature/task-104-jwt-auth"
}
```

---

Events

BRANCH_RENAMED

---

# 9. Checkout Branch

Purpose

Select the working branch for subsequent file operations.

Operation

```text id="ghbranch14"
checkout_branch
```

---

Request

```json id="ghbranch15"
{
  "repository":"owner/repository",

  "branch":"feature/task-104-jwt-auth"
}
```

---

Response

```json id="ghbranch16"
{
  "success":true,

  "currentBranch":"feature/task-104-jwt-auth"
}
```

---

Events

BRANCH_CHECKED_OUT

---

# 10. List Branches

Operation

```text id="ghbranch17"
list_branches
```

---

Response

```json id="ghbranch18"
{
  "branches":[
    {
      "name":"main",
      "protected":true
    },
    {
      "name":"feature/task-104-jwt-auth",
      "protected":false
    }
  ]
}
```

---

# 11. Branch Information

Operation

```text id="ghbranch19"
branch_info
```

---

Response

```json id="ghbranch20"
{
  "name":"feature/task-104-jwt-auth",

  "latestCommit":"f8b7d1",

  "author":"ForgeAI",

  "protected":false,

  "ahead":3,

  "behind":0,

  "createdAt":"..."
}
```

---

# 12. Branch Validation

Purpose

Validate branch before execution.

Validation Rules

Repository exists

Branch exists

Branch accessible

Branch not archived

Branch not locked

Branch not protected (for write operations)

Branch name valid

No merge conflicts (optional future)

---

Response

```json id="ghbranch21"
{
  "valid":true,

  "warnings":[],

  "errors":[]
}
```

---

# 13. Branch Protection

Operation

```text id="ghbranch22"
branch_protection
```

---

Response

```json id="ghbranch23"
{
  "protected":true,

  "allowForcePush":false,

  "requireReviews":true,

  "requiredApprovals":1,

  "requireStatusChecks":true
}
```

---

ForgeAI respects all protection rules.

It never bypasses repository protection.

---

# 14. Request Schema

Every request

```json id="ghbranch24"
{
  "requestId":"",

  "workflowId":"",

  "taskId":"",

  "agent":"Developer",

  "tool":"github",

  "action":"create_branch",

  "parameters":{

  }
}
```

---

# 15. Response Schema

```json id="ghbranch25"
{
  "success":true,

  "executionTime":130,

  "data":{

  },

  "metadata":{

      "rateLimitRemaining":4980,

      "cached":false

  }
}
```

---

# 16. Validation Rules

Branch names

* Maximum 255 characters
* Cannot contain spaces
* Cannot start or end with '/'
* Cannot contain '..'
* Cannot contain '~', '^', ':', '?', '*', '[', '\'
* Must be UTF-8 compatible

Repository

* Must exist
* Must be writable
* Must not be archived

---

# 17. Error Codes

BRANCH_ALREADY_EXISTS

BRANCH_NOT_FOUND

INVALID_BRANCH_NAME

DEFAULT_BRANCH_PROTECTED

PROTECTED_BRANCH

CHECKOUT_FAILED

RENAME_FAILED

DELETE_FAILED

INSUFFICIENT_PERMISSIONS

RATE_LIMIT_EXCEEDED

AUTHENTICATION_FAILED

TIMEOUT

UNKNOWN_ERROR

---

# 18. Audit Logging

Every branch operation logs

Workflow ID

Task ID

Repository

Branch

Agent

Operation

Execution Time

Status

Timestamp

Example

```json id="ghbranch26"
{
  "tool":"GitHub",

  "operation":"create_branch",

  "repository":"ForgeAI",

  "branch":"feature/task-104-jwt-auth",

  "agent":"Developer",

  "status":"SUCCESS"
}
```

---

# 19. Events

BRANCH_CREATED

BRANCH_DELETED

BRANCH_RENAMED

BRANCH_CHECKED_OUT

BRANCH_VALIDATED

BRANCH_PROTECTION_VERIFIED

BRANCH_OPERATION_FAILED

---

# 20. Security Rules

The Branch Operations module must:

* Never allow modifications to the default branch by AI agents.
* Respect all GitHub branch protection rules.
* Require explicit write permissions for branch creation and deletion.
* Prevent branch name injection attacks.
* Validate all repository and branch identifiers.
* Log every branch operation.
* Never perform force pushes.

---

# 21. Performance Targets

Branch validation

< 300 ms

Branch creation

< 1 s

Checkout

< 500 ms

List branches

< 1 s

Protection retrieval

< 500 ms

Performance depends on repository size and network conditions.

---

# 22. Future Enhancements

Planned capabilities include:

* Automatic conflict detection
* Branch synchronization with base branch
* Automatic rebase recommendations
* Temporary workspace branches
* Branch templates
* Multi-repository branch coordination
* Protected release branch workflows

---

# 23. Quality Principles

The Branch Operations module should always:

* Isolate every engineering task on its own feature branch.
* Preserve the integrity of protected branches.
* Enforce consistent naming conventions.
* Validate all branch operations before execution.
* Maintain complete auditability.
* Produce deterministic request and response schemas.
* Prevent destructive operations without explicit authorization.
* Ensure compatibility with standard Git and GitHub workflows.

The Branch Operations module is successful when every ForgeAI implementation occurs safely within isolated feature branches, enabling parallel development, reliable review workflows, and secure integration into the target repository.

# SCHEMA.md (Part 4.2.2.2.1)

# GitHub MCP Specification — Read & Directory Operations

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** GitHub MCP Server

**Module:** File & Directory Operations (Read)

**Version:** 1.0

**Status:** Core MCP Tool

---

# 1. Purpose

The Read & Directory Operations module provides ForgeAI agents with secure, read-only access to repository contents.

It enables agents to inspect files, traverse directory structures, retrieve metadata, search the repository, and understand project layout without modifying repository contents.

This module is heavily used by:

* Planner Agent
* Architect Agent
* Developer Agent
* Tester Agent
* Security Agent
* Documentation Agent
* Reviewer Agent

---

# 2. Responsibilities

The module is responsible for:

✓ Reading files

✓ Reading directories

✓ Listing directory contents

✓ Retrieving metadata

✓ Searching files

✓ Searching directories

✓ Detecting file types

✓ Detecting encodings

✓ Retrieving repository structure

✓ Returning normalized responses

---

# 3. Supported Operations

| Operation      | Description                    |
| -------------- | ------------------------------ |
| read_file      | Read file contents             |
| read_directory | Retrieve directory information |
| list_directory | List files and folders         |
| file_metadata  | Retrieve metadata              |
| search_files   | Search repository              |
| search_content | Search file contents           |

---

# 4. Supported File Types

Text

Markdown

Python

TypeScript

JavaScript

Java

Go

Rust

JSON

YAML

XML

HTML

CSS

SQL

Dockerfile

Shell Scripts

Configuration Files

Binary files are supported only for metadata retrieval.

---

# 5. Read File

Purpose

Retrieve a file.

Operation

```text id="ghread01"
read_file
```

---

Request

```json id="ghread02"
{
  "repository":"owner/repository",

  "branch":"main",

  "path":"backend/auth/service.py"
}
```

---

Validation

Repository exists

Branch exists

File exists

File readable

Path valid

---

Response

```json id="ghread03"
{
  "path":"backend/auth/service.py",

  "encoding":"utf-8",

  "language":"Python",

  "size":8214,

  "sha":"abc123",

  "content":"..."
}
```

---

Events

FILE_READ

---

# 6. File Encoding

Supported

UTF-8

UTF-16

ASCII

UTF-8 with BOM

Unsupported encodings should return

UNSUPPORTED_ENCODING

---

# 7. Large Files

Default limits

Maximum file size

20 MB

Maximum text response

5 MB

Larger files

↓

Truncated

↓

Metadata returned

↓

Warning emitted

---

# 8. Read Directory

Purpose

Retrieve directory contents.

Operation

```text id="ghread04"
read_directory
```

---

Request

```json id="ghread05"
{
  "repository":"owner/repository",

  "branch":"main",

  "path":"backend/"
}
```

---

Response

```json id="ghread06"
{
  "directory":"backend",

  "children":[

      {

          "name":"auth",

          "type":"directory"

      },

      {

          "name":"main.py",

          "type":"file"

      }

  ]
}
```

---

# 9. Directory Tree Depth

Default

3

Maximum

20

Recursive traversal is configurable.

---

# 10. List Directory

Operation

```text id="ghread07"
list_directory
```

---

Returns

Folders

Files

Hidden files (optional)

Extensions

Sizes

Last modified

SHA

---

Example

```json id="ghread08"
{
  "items":[

      {

          "name":"auth",

          "type":"directory"

      },

      {

          "name":"README.md",

          "type":"file"

      }

  ]
}
```

---

# 11. File Metadata

Operation

```text id="ghread09"
file_metadata
```

---

Response

```json id="ghread10"
{
  "path":"backend/auth/service.py",

  "size":8214,

  "extension":"py",

  "language":"Python",

  "sha":"...",

  "lastModified":"...",

  "binary":false
}
```

---

# 12. Directory Metadata

Returns

Directory name

Child count

File count

Folder count

Depth

Repository root

Permissions

---

# 13. Repository Search

Operation

```text id="ghread11"
search_files
```

Search by

Filename

Extension

Directory

Language

Glob pattern

Examples

```text id="ghread12"
*.py

README*

*.tsx

Dockerfile
```

---

Request

```json id="ghread13"
{
  "repository":"owner/repository",

  "query":"*.py"
}
```

---

Response

```json id="ghread14"
{
  "results":[

      "backend/main.py",

      "backend/auth/service.py"

  ]
}
```

---

# 14. Content Search

Purpose

Search inside files.

Operation

```text id="ghread15"
search_content
```

Example

Search

JWT

Returns

```json id="ghread16"
{
  "matches":[

      {

          "file":"backend/auth/service.py",

          "line":42,

          "snippet":"create_jwt_token(...)"

      }

  ]
}
```

---

# 15. Search Filters

Language

Extension

Directory

Case Sensitive

Regex

Whole Word

File Size

Hidden Files

---

# 16. Search Limits

Maximum results

500

Maximum search duration

30 seconds

Maximum file size searched

10 MB

---

# 17. Request Schema

Every request

```json id="ghread17"
{
  "requestId":"",

  "workflowId":"",

  "taskId":"",

  "agent":"Architect",

  "tool":"github",

  "action":"read_file",

  "parameters":{

  }
}
```

---

# 18. Response Schema

```json id="ghread18"
{
  "success":true,

  "executionTime":102,

  "data":{

  },

  "metadata":{

      "cached":true,

      "rateLimitRemaining":4912

  }
}
```

---

# 19. Validation Rules

Repository exists

Branch exists

Path exists

Path normalized

No path traversal

No null bytes

Encoding supported

File size within limits

---

# 20. Path Security

Forbidden

```text id="ghread19"
../

../../

~/

C:\

\\

null bytes
```

Every path is normalized before execution.

---

# 21. Error Codes

FILE_NOT_FOUND

DIRECTORY_NOT_FOUND

INVALID_PATH

INVALID_BRANCH

UNSUPPORTED_ENCODING

FILE_TOO_LARGE

SEARCH_TIMEOUT

SEARCH_LIMIT_EXCEEDED

AUTHENTICATION_FAILED

ACCESS_DENIED

UNKNOWN_ERROR

---

# 22. Caching

Cache

Metadata

Directory listings

Repository tree

Search results (optional)

Default TTL

300 seconds

Write operations invalidate affected cache entries.

---

# 23. Audit Logging

Every operation records

Repository

Branch

Path

Operation

Agent

Execution Time

Success

Timestamp

Example

```json id="ghread20"
{
  "tool":"GitHub",

  "operation":"read_file",

  "repository":"ForgeAI",

  "path":"backend/auth/service.py",

  "agent":"Developer",

  "status":"SUCCESS"
}
```

---

# 24. Events

FILE_READ

DIRECTORY_READ

DIRECTORY_LISTED

METADATA_RETRIEVED

SEARCH_STARTED

SEARCH_COMPLETED

SEARCH_FAILED

READ_OPERATION_FAILED

---

# 25. Performance Targets

Read file

< 300 ms

Read directory

< 500 ms

Metadata

< 200 ms

Directory listing

< 500 ms

Repository search

< 2 s

Content search

< 5 s

Performance targets depend on repository size and network latency.

---

# 26. Security Principles

The Read & Directory Operations module must:

* Enforce repository read permissions before every operation.
* Normalize and validate all file paths.
* Prevent path traversal attacks.
* Never expose authentication credentials.
* Never return repository contents outside authorized scope.
* Sanitize search queries where appropriate.
* Respect GitHub API rate limits.
* Maintain complete audit logs for all read operations.

---

# 27. Future Enhancements

Planned capabilities include:

* Semantic code search
* Symbol search (classes, functions, interfaces)
* AST-based navigation
* Cross-reference discovery
* Dependency graph navigation
* Code ownership lookup (CODEOWNERS)
* Incremental repository indexing
* Vector-based repository search

---

# 28. Quality Principles

The Read & Directory Operations module should always:

* Provide fast, deterministic access to repository contents.
* Return normalized, provider-independent data structures.
* Preserve repository integrity through read-only behavior.
* Validate every request before execution.
* Prevent unauthorized or unsafe file access.
* Support efficient repository exploration for all ForgeAI agents.
* Produce consistent request and response schemas.
* Maintain full observability through logging and events.

The Read & Directory Operations module is successful when ForgeAI agents can safely inspect repository structure, discover relevant files, retrieve metadata, and search codebases efficiently without modifying repository contents or compromising security.

# SCHEMA.md (Part 4.2.2.2.2-A)

# GitHub MCP Specification — File Creation & Writing

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** GitHub MCP Server

**Module:** File Operations – Creation & Writing

**Version:** 1.0

**Status:** Core MCP Tool

---

# 1. Purpose

The File Creation & Writing module provides ForgeAI agents with secure, controlled write access to repository contents.

Unlike the Read Operations module, this module performs repository modifications by creating new files and writing content while preserving repository integrity, respecting branch isolation, and maintaining complete auditability.

Every write operation occurs only on a non-protected working branch.

---

# 2. Responsibilities

The module is responsible for:

✓ Creating new files

✓ Writing file contents

✓ Creating intermediate directories

✓ Validating paths

✓ Detecting overwrite conflicts

✓ Verifying permissions

✓ Recording audit logs

✓ Emitting workflow events

✓ Returning standardized responses

---

# 3. Supported Operations

| Operation        | Description                |
| ---------------- | -------------------------- |
| create_file      | Create a new file          |
| write_file       | Write file contents        |
| create_directory | Create directory hierarchy |
| file_exists      | Check existence            |
| validate_path    | Validate repository path   |

---

# 4. Operation Lifecycle

```text
Request
    │
Validate Request
    │
Validate Branch
    │
Validate Permissions
    │
Normalize Path
    │
Check File Exists
    │
Create Directories
    │
Write File
    │
Verify SHA
    │
Audit Log
    │
Return Response
```

---

# 5. Create File

Purpose

Create a new file inside the repository.

Operation

```text
create_file
```

---

## Request Schema

```json
{
  "repository":"owner/repository",
  "branch":"feature/task-104-auth",
  "path":"backend/auth/jwt_service.py",
  "content":"...",
  "encoding":"utf-8"
}
```

---

Validation

Repository exists

Branch exists

Directory valid

File does not already exist

User has write permission

Content size within limits

---

Response

```json
{
  "success":true,
  "path":"backend/auth/jwt_service.py",
  "operation":"CREATE",
  "sha":"4d7b5fa..."
}
```

---

Events

FILE_CREATED

---

# 6. Write File

Purpose

Write complete file contents.

Operation

```text
write_file
```

Write operations replace the entire file contents unless Update File is used.

---

Request

```json
{
  "repository":"owner/repository",
  "branch":"feature/task-104-auth",
  "path":"backend/auth/jwt_service.py",
  "content":"...",
  "overwrite":false
}
```

---

Response

```json
{
  "success":true,
  "bytesWritten":8124,
  "sha":"71aa8c..."
}
```

---

# 7. File Size Limits

Default

Maximum text file

20 MB

Maximum request payload

25 MB

Maximum generated file

20 MB

Larger files rejected.

---

# 8. Directory Creation

Purpose

Automatically create missing directories.

Example

```text
backend/security/auth/jwt/
```

If

backend/security/

exists

ForgeAI creates

```text
auth/

jwt/
```

---

Operation

```text
create_directory
```

---

Request

```json
{
  "repository":"owner/repository",
  "branch":"feature/task-104-auth",
  "path":"backend/security/auth/"
}
```

---

Response

```json
{
  "success":true,
  "createdDirectories":[
    "backend/security",
    "backend/security/auth"
  ]
}
```

---

# 9. Nested Directory Rules

Directories

May contain

Letters

Numbers

Hyphen

Underscore

Periods

Must not

Contain

..

~

:

*

?

Null bytes

Windows reserved names

---

# 10. Overwrite Rules

Default

overwrite = false

If file exists

↓

Reject

↓

Return

FILE_ALREADY_EXISTS

---

When

overwrite = true

↓

Existing file replaced

↓

Old SHA recorded

↓

Audit entry created

---

Example

```json
{
  "overwrite":true
}
```

---

# 11. Safe Write Rules

The MCP must never overwrite

.git

.github/workflows (unless explicitly approved)

LICENSE

Protected configuration

Protected branches

Repository metadata

Protected files are configurable.

---

# 12. Encoding

Supported

UTF-8

UTF-16

ASCII

UTF-8 BOM

Normalize

Line endings

↓

LF

Unless repository policy specifies CRLF.

---

Rejected

Unsupported encodings

Binary payloads

Malformed UTF

---

# 13. Content Validation

Validate

Encoding

File size

File extension

Language detection

Repository policy

Null bytes

Invalid Unicode

---

# 14. File Extensions

Supported

.py

.ts

.tsx

.js

.jsx

.java

.go

.rs

.json

.yaml

.yml

.xml

.sql

.md

.html

.css

.env.example

Dockerfile

Binary files require future support.

---

# 15. Permission Requirements

Developer

Read + Write

Documentation

Documentation paths only

Tester

Generated tests only

Security

Read only

Planner

Read only

Architect

Read only

Reviewer

Read only

Deployment

Read only

---

# 16. Request Schema

Every request

```json
{
  "requestId":"uuid",

  "workflowId":"uuid",

  "taskId":"uuid",

  "agent":"Developer",

  "tool":"github",

  "action":"create_file",

  "parameters":{

  }
}
```

---

# 17. Response Schema

```json
{
  "success":true,

  "executionTime":184,

  "data":{

  },

  "metadata":{

      "cached":false,

      "repository":"ForgeAI",

      "branch":"feature/task-104-auth"

  }
}
```

---

# 18. Validation Rules

Repository exists

Branch exists

Write permission granted

Path normalized

Path inside repository

Extension allowed

Encoding valid

Content valid

Size within limits

---

# 19. Atomic Writes

All write operations are atomic.

Sequence

Temporary object

↓

Validation

↓

Commit

↓

Verification

↓

Success

Failure

↓

Rollback

No partial writes are permitted.

---

# 20. Error Codes

FILE_ALREADY_EXISTS

DIRECTORY_NOT_FOUND

DIRECTORY_CREATION_FAILED

INVALID_PATH

INVALID_ENCODING

INVALID_EXTENSION

FILE_TOO_LARGE

WRITE_FAILED

INSUFFICIENT_PERMISSIONS

PROTECTED_FILE

BRANCH_PROTECTED

AUTHENTICATION_FAILED

TIMEOUT

UNKNOWN_ERROR

---

# 21. Audit Logging

Every write records

Workflow ID

Task ID

Repository

Branch

Path

Operation

Agent

Old SHA (if overwritten)

New SHA

Execution time

Timestamp

Example

```json
{
  "tool":"GitHub",

  "operation":"create_file",

  "repository":"ForgeAI",

  "branch":"feature/task-104-auth",

  "path":"backend/auth/jwt_service.py",

  "agent":"Developer",

  "status":"SUCCESS"
}
```

---

# 22. Events

DIRECTORY_CREATED

FILE_CREATED

FILE_WRITTEN

FILE_OVERWRITTEN

WRITE_VALIDATED

WRITE_FAILED

PERMISSION_DENIED

---

# 23. Performance Targets

Create file

< 500 ms

Write file

< 1 s

Create directory

< 300 ms

Validation

< 200 ms

Targets depend on repository size and network conditions.

---

# 24. Security Rules

The File Creation & Writing module must:

* Require authenticated write access.
* Validate all repository paths.
* Prevent path traversal attacks.
* Reject writes to protected branches.
* Respect repository protection policies.
* Reject unsupported encodings.
* Record every write operation in the audit log.
* Never overwrite protected files without explicit approval.
* Never expose credentials or secrets in responses.

---

# 25. Future Enhancements

Planned capabilities include:

* Binary file support
* Template-based file generation
* Automatic formatting before write
* Language-aware validation
* Content signing
* Large file streaming
* Repository policy enforcement
* Content encryption for generated artifacts

---

# 26. Quality Principles

The File Creation & Writing module should always:

* Produce deterministic and atomic write operations.
* Preserve repository integrity through strict validation.
* Respect repository and branch protection rules.
* Automatically create valid directory structures when required.
* Normalize file encoding and line endings.
* Provide consistent request and response contracts.
* Maintain complete auditability for every modification.
* Fail safely with clear, structured error reporting.

The File Creation & Writing module is successful when ForgeAI agents can reliably create new repository content while ensuring safety, traceability, consistency, and compatibility with standard GitHub workflows.

# SCHEMA.md (Part 4.2.2.2.2-B)

# GitHub MCP Specification — File Updates, Rename & Move Operations

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** GitHub MCP Server

**Module:** File Operations – Update, Rename & Move

**Version:** 1.0

**Status:** Core MCP Tool

---

# 1. Purpose

The File Updates, Rename & Move module enables ForgeAI agents to safely modify existing repository files while preserving repository integrity, minimizing conflicts, and maintaining a complete audit trail.

Unlike the File Creation module, these operations work only on **existing repository assets**. Every modification is validated, version-aware, and executed atomically to ensure consistency.

All update operations occur only on an isolated feature branch.

---

# 2. Responsibilities

The module is responsible for:

✓ Updating existing files

✓ Renaming files

✓ Moving files between directories

✓ Preserving file history

✓ Detecting update conflicts

✓ Validating file integrity

✓ Performing atomic operations

✓ Creating audit records

✓ Publishing workflow events

✓ Returning standardized responses

---

# 3. Supported Operations

| Operation       | Description             |
| --------------- | ----------------------- |
| update_file     | Modify an existing file |
| rename_file     | Rename a file           |
| move_file       | Move a file             |
| validate_update | Validate update request |
| validate_move   | Validate destination    |

---

# 4. Operation Lifecycle

```text id="ghupdate01"
Receive Request
      │
Validate Repository
      │
Validate Branch
      │
Locate File
      │
Validate SHA
      │
Check Permissions
      │
Execute Update
      │
Verify Integrity
      │
Commit Changes
      │
Audit Log
      │
Return Response
```

---

# 5. Update File

Purpose

Modify the contents of an existing file while preserving repository history.

Operation

```text id="ghupdate02"
update_file
```

---

Request

```json id="ghupdate03"
{
  "repository":"owner/repository",
  "branch":"feature/task-104-auth",
  "path":"backend/auth/service.py",
  "sha":"4a8f23c",
  "content":"...",
  "message":"Implement JWT authentication"
}
```

---

Validation

Repository exists

Branch exists

File exists

SHA matches latest version

Encoding valid

Extension supported

Write permission granted

---

Response

```json id="ghupdate04"
{
  "success":true,
  "operation":"UPDATE",
  "path":"backend/auth/service.py",
  "oldSha":"4a8f23c",
  "newSha":"72bc9fe"
}
```

---

Events

FILE_UPDATED

---

# 6. Update Strategies

Supported strategies

Replace Entire File

Append Content

Prepend Content

Replace Selected Range

Structured Patch (future)

Default strategy

Replace Entire File

---

# 7. Rename File

Purpose

Rename an existing file while preserving Git history.

Operation

```text id="ghupdate05"
rename_file
```

---

Request

```json id="ghupdate06"
{
  "repository":"owner/repository",
  "branch":"feature/task-104-auth",
  "source":"backend/auth/token.py",
  "destination":"backend/auth/jwt_service.py"
}
```

---

Validation

Source exists

Destination does not exist

Destination path valid

Repository writable

---

Response

```json id="ghupdate07"
{
  "success":true,
  "operation":"RENAME",
  "oldPath":"backend/auth/token.py",
  "newPath":"backend/auth/jwt_service.py"
}
```

---

Events

FILE_RENAMED

---

# 8. Move File

Purpose

Move a file into another directory while preserving file history.

Operation

```text id="ghupdate08"
move_file
```

---

Request

```json id="ghupdate09"
{
  "repository":"owner/repository",
  "branch":"feature/task-104-auth",
  "source":"backend/auth/service.py",
  "destination":"backend/security/service.py"
}
```

---

Response

```json id="ghupdate10"
{
  "success":true,
  "operation":"MOVE",
  "source":"backend/auth/service.py",
  "destination":"backend/security/service.py"
}
```

---

Events

FILE_MOVED

---

# 9. Rename Rules

Allowed

Rename within same directory

Rename across directories

Change filename

Change extension (when compatible)

Not Allowed

Rename protected files

Rename to reserved names

Rename outside repository

Overwrite existing destination

---

# 10. Move Rules

Destination directory

Must exist

or

Auto-create enabled

Destination

Cannot overwrite existing files

Move operations preserve

History

Permissions

Metadata

Audit trail

---

# 11. Atomic Operations

All update operations are atomic.

Workflow

```text id="ghupdate11"
Validate
      │
Create Temporary Object
      │
Apply Change
      │
Verify SHA
      │
Commit
      │
Success
```

If any stage fails

↓

Rollback

↓

Restore original state

↓

Return structured error

Partial updates are never permitted.

---

# 12. Conflict Detection

The module validates

SHA

Latest commit

Repository state

Branch synchronization

If repository changed

↓

Return

UPDATE_CONFLICT

No automatic overwrite occurs.

---

# 13. Merge Conflict Handling

Conflict types

Modified remotely

Deleted remotely

Renamed remotely

Moved remotely

Binary conflict

Future support

Three-way merge

Interactive conflict resolution

AI-assisted merge suggestions

---

# 14. Validation Rules

Repository exists

Repository writable

Branch exists

Branch not protected

File exists

SHA valid

Encoding valid

Extension supported

Destination valid

No duplicate destination

---

# 15. Path Validation

Allowed

Relative repository paths

Normalized separators

UTF-8 filenames

Forbidden

Absolute paths

Path traversal

Null bytes

Reserved device names

Invalid Unicode sequences

---

# 16. Permission Matrix

Developer

Update

Rename

Move

Documentation

Documentation files only

Tester

Generated test files only

Deployment

No write access

Reviewer

Read only

Security

Read only

Planner

Read only

Architect

Read only

---

# 17. Request Schema

```json id="ghupdate12"
{
  "requestId":"uuid",
  "workflowId":"uuid",
  "taskId":"uuid",
  "agent":"Developer",
  "tool":"github",
  "action":"update_file",
  "parameters":{}
}
```

---

# 18. Response Schema

```json id="ghupdate13"
{
  "success":true,
  "executionTime":216,
  "data":{},
  "metadata":{
    "repository":"ForgeAI",
    "branch":"feature/task-104-auth",
    "cached":false
  }
}
```

---

# 19. Validation Pipeline

```text id="ghupdate14"
Repository
      │
Branch
      │
Permissions
      │
Path
      │
SHA
      │
Encoding
      │
Repository Rules
      │
Operation
```

---

# 20. Error Codes

FILE_NOT_FOUND

INVALID_SHA

UPDATE_CONFLICT

MOVE_CONFLICT

DESTINATION_EXISTS

INVALID_DESTINATION

INVALID_PATH

PROTECTED_FILE

PROTECTED_BRANCH

RENAME_FAILED

MOVE_FAILED

WRITE_FAILED

AUTHENTICATION_FAILED

ACCESS_DENIED

TIMEOUT

UNKNOWN_ERROR

---

# 21. Audit Logging

Every modification records

Workflow ID

Task ID

Repository

Branch

Source path

Destination path

Old SHA

New SHA

Operation

Agent

Execution time

Timestamp

Example

```json id="ghupdate15"
{
  "tool":"GitHub",
  "operation":"rename_file",
  "repository":"ForgeAI",
  "source":"backend/auth/token.py",
  "destination":"backend/auth/jwt_service.py",
  "agent":"Developer",
  "status":"SUCCESS"
}
```

---

# 22. Events

FILE_UPDATED

FILE_RENAMED

FILE_MOVED

UPDATE_VALIDATED

UPDATE_CONFLICT

MOVE_COMPLETED

RENAME_COMPLETED

UPDATE_FAILED

---

# 23. Performance Targets

Update file

< 800 ms

Rename file

< 500 ms

Move file

< 600 ms

Validation

< 250 ms

Conflict detection

< 400 ms

Performance targets may vary depending on repository size and network conditions.

---

# 24. Security Rules

The File Updates, Rename & Move module must:

* Verify write permissions before every operation.
* Reject updates on protected branches.
* Prevent modifications to protected files unless explicitly approved.
* Validate SHA hashes to prevent lost updates.
* Normalize all paths before execution.
* Prevent path traversal attacks.
* Record every change in the audit log.
* Never expose repository credentials or authentication tokens.

---

# 25. Future Enhancements

Planned capabilities include:

* AST-aware code modifications
* Semantic refactoring
* Multi-file atomic transactions
* Symbol-based renaming
* AI-assisted merge conflict resolution
* Incremental patch application
* Repository policy enforcement
* Cross-repository file moves

---

# 26. Quality Principles

The File Updates, Rename & Move module should always:

* Preserve Git history whenever possible.
* Execute all modifications atomically.
* Detect and prevent conflicting updates.
* Respect repository protection policies.
* Produce deterministic, validated operations.
* Maintain complete traceability through audit logs.
* Return consistent request and response contracts.
* Fail safely with automatic rollback on any unsuccessful operation.

The File Updates, Rename & Move module is successful when ForgeAI agents can reliably modify, rename, and reorganize repository files without compromising repository integrity, losing history, or introducing inconsistent states.

# SCHEMA.md (Part 4.2.2.2.3-A)

# GitHub MCP Specification — Delete Operations

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** GitHub MCP Server

**Module:** File & Directory Delete Operations

**Version:** 1.0

**Status:** Core MCP Tool

---

# 1. Purpose

The Delete Operations module provides ForgeAI with a secure mechanism for deleting repository files and directories while preserving repository integrity, respecting branch protection rules, and ensuring all destructive operations remain fully auditable.

Deletion is considered a **high-risk operation**.

Unlike file creation or updates, deletion always requires additional validation and may require human approval depending on repository policy.

All delete operations occur only on feature branches.

---

# 2. Responsibilities

The module is responsible for:

✓ Deleting files

✓ Deleting directories

✓ Recursive deletion

✓ Validation

✓ Permission verification

✓ Safety checks

✓ Dependency validation

✓ Audit logging

✓ Event publishing

✓ Rollback preparation

---

# 3. Supported Operations

| Operation               | Description             |
| ----------------------- | ----------------------- |
| delete_file             | Delete a file           |
| delete_directory        | Delete a directory      |
| validate_delete         | Validate deletion       |
| dependency_check        | Check references        |
| restore_delete (future) | Restore deleted content |

---

# 4. Delete Workflow

```text id="ghdelete01"
Delete Request
      │
Validate Repository
      │
Validate Branch
      │
Validate Permissions
      │
Check Protection Rules
      │
Dependency Analysis
      │
Delete Resource
      │
Verify Repository State
      │
Audit Log
      │
Return Response
```

---

# 5. Delete File

Purpose

Delete a single repository file.

Operation

```text id="ghdelete02"
delete_file
```

---

## Request

```json id="ghdelete03"
{
  "repository":"owner/repository",
  "branch":"feature/task-204-cleanup",
  "path":"backend/legacy/auth_old.py",
  "sha":"4e29ab9",
  "force":false
}
```

---

## Validation

Repository exists

Branch exists

File exists

SHA matches latest version

File not protected

Write permission granted

Deletion allowed by repository policy

---

## Response

```json id="ghdelete04"
{
  "success":true,
  "operation":"DELETE_FILE",
  "path":"backend/legacy/auth_old.py",
  "deleted":true
}
```

---

## Events

FILE_DELETED

---

# 6. Delete Directory

Purpose

Delete an entire directory.

Operation

```text id="ghdelete05"
delete_directory
```

---

## Request

```json id="ghdelete06"
{
  "repository":"owner/repository",
  "branch":"feature/task-204-cleanup",
  "path":"backend/legacy/",
  "recursive":true
}
```

---

## Response

```json id="ghdelete07"
{
  "success":true,
  "operation":"DELETE_DIRECTORY",
  "deletedFiles":24,
  "deletedDirectories":5
}
```

---

# 7. Recursive Delete

Recursive deletion is disabled by default.

When enabled:

```json id="ghdelete08"
{
  "recursive":true
}
```

The MCP validates every child resource before deletion.

Partial recursive deletion is never permitted.

---

# 8. Protected Resources

The following resources cannot be deleted by AI agents unless explicitly approved:

```text id="ghdelete09"
.git/

.github/

LICENSE

README.md

package-lock.json

pnpm-lock.yaml

Cargo.lock

go.sum

Dockerfile

docker-compose.yml

.github/workflows/

.gitignore
```

Repository administrators may extend this list.

---

# 9. Repository Safety Rules

Deletion is prohibited when:

Current branch is protected

Repository archived

Repository locked

Required approvals missing

Human approval required

Operation targets repository root

---

# 10. Dependency Validation

Before deletion, the MCP checks:

Imports

References

Configuration

Routes

Dependency injection

Tests

Documentation

Build configuration

Future:

AST dependency analysis

---

# 11. Validation Pipeline

```text id="ghdelete10"
Repository

↓

Branch

↓

Permissions

↓

Protection Rules

↓

Dependency Analysis

↓

Delete

↓

Verification

↓

Audit
```

---

# 12. Delete Permissions

| Agent         | Delete Files                 | Delete Directories |
| ------------- | ---------------------------- | ------------------ |
| Planner       | ❌                            | ❌                  |
| Architect     | ❌                            | ❌                  |
| Developer     | ✅ (approval may be required) | ⚠️ Limited         |
| Tester        | ❌                            | ❌                  |
| Security      | ❌                            | ❌                  |
| Documentation | ⚠️ Documentation only        | ❌                  |
| Reviewer      | ❌                            | ❌                  |
| Deployment    | ❌                            | ❌                  |

---

# 13. Human Approval Policy

The following operations require approval:

Deleting more than 10 files

Deleting directories

Deleting configuration files

Deleting build scripts

Deleting infrastructure files

Deleting documentation

Deleting generated artifacts marked as permanent

---

Approval Flow

```text id="ghdelete11"
Delete Request

↓

Approval Required

↓

Human Approval

↓

Delete

↓

Audit
```

---

# 14. Atomic Delete

Deletion is atomic.

```text id="ghdelete12"
Validate

↓

Temporary Delete Plan

↓

Delete Objects

↓

Repository Verification

↓

Commit

↓

Success
```

Failure

↓

Rollback

↓

Repository Restored

---

# 15. Rollback

Rollback restores:

Files

Directories

Metadata

Permissions

Git history remains intact through Git commits.

---

# 16. Request Schema

```json id="ghdelete13"
{
  "requestId":"uuid",
  "workflowId":"uuid",
  "taskId":"uuid",
  "agent":"Developer",
  "tool":"github",
  "action":"delete_file",
  "parameters":{}
}
```

---

# 17. Response Schema

```json id="ghdelete14"
{
  "success":true,
  "executionTime":236,
  "data":{},
  "metadata":{
    "repository":"ForgeAI",
    "branch":"feature/task-204-cleanup",
    "cached":false
  }
}
```

---

# 18. Validation Rules

Repository exists

Branch exists

Branch writable

File exists

SHA valid

Delete permission granted

Not protected

Repository policy satisfied

Human approval obtained (when required)

---

# 19. Error Codes

FILE_NOT_FOUND

DIRECTORY_NOT_FOUND

DELETE_NOT_ALLOWED

PROTECTED_RESOURCE

DIRECTORY_NOT_EMPTY

DEPENDENCY_EXISTS

INVALID_SHA

DELETE_CONFLICT

BRANCH_PROTECTED

APPROVAL_REQUIRED

AUTHENTICATION_FAILED

ACCESS_DENIED

TIMEOUT

UNKNOWN_ERROR

---

# 20. Audit Logging

Every delete operation records:

Workflow ID

Task ID

Repository

Branch

Target path

Target type

Recursive flag

Agent

Approval ID (if applicable)

Execution time

Timestamp

Example

```json id="ghdelete15"
{
  "tool":"GitHub",
  "operation":"delete_directory",
  "repository":"ForgeAI",
  "path":"backend/legacy/",
  "recursive":true,
  "agent":"Developer",
  "status":"SUCCESS"
}
```

---

# 21. Events

FILE_DELETE_REQUESTED

DIRECTORY_DELETE_REQUESTED

DELETE_VALIDATED

DELETE_APPROVED

FILE_DELETED

DIRECTORY_DELETED

DELETE_ROLLED_BACK

DELETE_FAILED

---

# 22. Performance Targets

Delete file

< 500 ms

Delete directory

< 2 s

Validation

< 300 ms

Dependency analysis

< 2 s

Rollback

< 3 s

Performance depends on repository size and dependency graph complexity.

---

# 23. Security Rules

The Delete Operations module must:

* Treat every delete request as a destructive action.
* Require explicit write permissions.
* Respect repository protection rules.
* Prevent deletion of protected resources.
* Require human approval where policy demands.
* Validate dependencies before deletion.
* Execute deletes atomically with rollback support.
* Record all delete operations in the audit log.
* Never bypass branch protection or repository rules.

---

# 24. Future Enhancements

Planned capabilities include:

* Soft delete / recycle bin
* Git-based restore operation
* AI-assisted dependency impact analysis
* Cross-repository delete validation
* Policy-driven delete approval workflows
* Bulk delete optimization
* Delete preview mode
* Interactive deletion review

---

# 25. Quality Principles

The Delete Operations module should always:

* Prioritize repository safety over convenience.
* Validate every deletion request thoroughly.
* Minimize the risk of accidental data loss.
* Preserve repository consistency through atomic execution.
* Require additional safeguards for destructive actions.
* Produce deterministic request and response schemas.
* Maintain complete auditability and rollback capability.
* Ensure human oversight for high-impact deletions.

The Delete Operations module is successful when ForgeAI can safely remove obsolete repository resources without compromising project integrity, violating repository policies, or risking irreversible data loss.

# SCHEMA.md (Part 4.2.2.2.3-B)

# GitHub MCP Specification — Conflict Handling & Safety

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** GitHub MCP Server

**Module:** Conflict Handling & Safety

**Version:** 1.0

**Status:** Core MCP Tool

---

# 1. Purpose

The Conflict Handling & Safety module protects repository integrity by preventing concurrent modifications, detecting merge conflicts before they occur, coordinating file locking, enforcing repository safety policies, and ensuring all write operations remain deterministic and auditable.

This module acts as the safety layer for every GitHub MCP write operation.

All write-related MCP modules (Create, Update, Rename, Move, Delete, Commit, Pull Request) depend on this component.

---

# 2. Responsibilities

The module is responsible for:

✓ Detecting file conflicts

✓ Detecting branch conflicts

✓ Detecting repository conflicts

✓ Managing optimistic file locking

✓ Validating SHA consistency

✓ Detecting merge conflicts

✓ Providing merge recommendations

✓ Preventing race conditions

✓ Maintaining audit trails

✓ Publishing workflow events

---

# 3. Safety Principles

Every repository modification must satisfy:

Repository valid

↓

Branch valid

↓

Permissions valid

↓

Latest SHA confirmed

↓

No active lock

↓

No merge conflict

↓

Repository policy validated

↓

Execute operation

---

# 4. Conflict Categories

The module detects:

File conflicts

Directory conflicts

Branch conflicts

Merge conflicts

Rename conflicts

Delete conflicts

Move conflicts

Permission conflicts

Repository policy conflicts

Concurrent workflow conflicts

---

# 5. Conflict Detection Workflow

```text id="ghconflict01"
Receive Request
      │
Load Latest Repository State
      │
Verify Branch
      │
Verify SHA
      │
Check Active Locks
      │
Analyze Repository Changes
      │
Detect Conflicts
      │
Return Safe Result
```

---

# 6. SHA Validation

Every write request includes the latest Git object SHA.

Before modification:

Stored SHA

↓

Current Repository SHA

↓

Compare

↓

Match

↓

Continue

Mismatch

↓

UPDATE_CONFLICT

No overwrite occurs.

---

# 7. Conflict Types

### File Modified

Current file changed after retrieval.

Resolution

Reject operation.

---

### File Deleted

File removed by another workflow.

Resolution

Return FILE_NOT_FOUND.

---

### File Renamed

Original path no longer exists.

Resolution

Return FILE_MOVED.

---

### Directory Deleted

Parent directory removed.

Resolution

Reject request.

---

### Branch Diverged

Branch differs from expected commit history.

Resolution

Require synchronization.

---

# 8. Conflict Severity

LOW

Independent modifications

MEDIUM

Concurrent file updates

HIGH

Repository divergence

CRITICAL

Protected branch conflict

Repository corruption

Critical conflicts block execution.

---

# 9. Conflict Resolution Policy

Default behavior

Fail safely.

ForgeAI never silently overwrites user changes.

Possible outcomes:

Retry

Manual review

Merge recommendation

Operation rejection

Future AI-assisted merge

---

# 10. Merge Strategies

Supported strategies

Fast Forward

Three-Way Merge

Squash Merge

Rebase

Merge Commit

Default recommendation

Three-Way Merge

Automatic merging occurs only when repository policy allows.

---

# 11. Merge Strategy Schema

```json id="ghconflict02"
{
  "strategy":"THREE_WAY",
  "autoResolve":false,
  "requiresApproval":true
}
```

---

# 12. Automatic Merge Rules

Automatic merge permitted only when:

No overlapping changes

No protected files

Repository policy allows

No failed tests

Security review passed

Otherwise:

Manual approval required.

---

# 13. File Locking

The MCP uses optimistic locking.

Workflow

```text id="ghconflict03"
Read File
      │
Record SHA
      │
Modify File
      │
Compare SHA
      │
Commit
```

No long-lived repository locks are created.

---

# 14. Temporary Write Locks

During execution:

File

↓

Temporary Lock

↓

Write

↓

Verify

↓

Unlock

Locks expire automatically.

Default timeout

60 seconds

---

# 15. Lock Schema

```json id="ghconflict04"
{
  "lockId":"uuid",
  "repository":"owner/repository",
  "path":"backend/auth/service.py",
  "agent":"Developer",
  "workflowId":"wf-102",
  "expiresAt":"2026-07-06T14:22:00Z"
}
```

---

# 16. Lock States

AVAILABLE

LOCKED

EXPIRED

RELEASED

FAILED

Only one active write lock per file.

---

# 17. Concurrent Workflows

Multiple workflows may execute simultaneously.

Safe example

```text id="ghconflict05"
Workflow A

backend/auth/

Workflow B

frontend/login/
```

Unsafe example

```text id="ghconflict06"
Workflow A

backend/auth/service.py

Workflow B

backend/auth/service.py
```

Second workflow receives

RESOURCE_LOCKED.

---

# 18. Repository Safety Rules

Never modify

Protected branches

Protected files

Archived repositories

Read-only repositories

Deleted branches

Locked repositories

---

# 19. Repository Consistency Checks

Before every write:

Repository exists

↓

Branch exists

↓

Latest commit retrieved

↓

Repository not archived

↓

Repository writable

↓

Workflow valid

---

# 20. Safety Validation Pipeline

```text id="ghconflict07"
Authentication
      │
Authorization
      │
Repository Validation
      │
Branch Validation
      │
SHA Validation
      │
Lock Validation
      │
Conflict Detection
      │
Repository Policy
      │
Execute
```

---

# 21. Request Schema

```json id="ghconflict08"
{
  "requestId":"uuid",
  "workflowId":"uuid",
  "taskId":"uuid",
  "agent":"Developer",
  "tool":"github",
  "action":"validate_conflict",
  "parameters":{
    "repository":"owner/repository",
    "branch":"feature/task-104-auth",
    "path":"backend/auth/service.py",
    "sha":"4a8f23c"
  }
}
```

---

# 22. Response Schema

```json id="ghconflict09"
{
  "success":true,
  "conflict":false,
  "locked":false,
  "mergeRequired":false,
  "executionTime":132,
  "metadata":{
    "repository":"ForgeAI",
    "branch":"feature/task-104-auth"
  }
}
```

---

# 23. Conflict Response Schema

```json id="ghconflict10"
{
  "success":false,
  "error":{
    "code":"UPDATE_CONFLICT",
    "severity":"HIGH",
    "message":"Repository changed since last read.",
    "recommendedAction":"REFRESH_AND_RETRY"
  }
}
```

---

# 24. Error Codes

UPDATE_CONFLICT

MERGE_CONFLICT

RESOURCE_LOCKED

INVALID_SHA

STALE_BRANCH

PROTECTED_BRANCH

PROTECTED_FILE

REPOSITORY_ARCHIVED

REPOSITORY_LOCKED

WORKFLOW_CONFLICT

LOCK_TIMEOUT

UNKNOWN_ERROR

---

# 25. Audit Logging

Every safety check records:

Workflow ID

Task ID

Repository

Branch

File path

Operation

Conflict status

Lock status

Merge strategy

Execution time

Timestamp

Example

```json id="ghconflict11"
{
  "tool":"GitHub",
  "operation":"validate_conflict",
  "repository":"ForgeAI",
  "path":"backend/auth/service.py",
  "agent":"Developer",
  "status":"SUCCESS",
  "conflict":false,
  "locked":false
}
```

---

# 26. Events

CONFLICT_CHECK_STARTED

CONFLICT_DETECTED

CONFLICT_RESOLVED

LOCK_ACQUIRED

LOCK_RELEASED

LOCK_EXPIRED

MERGE_REQUIRED

MERGE_COMPLETED

SAFETY_VALIDATION_COMPLETED

SAFETY_VALIDATION_FAILED

---

# 27. Retry Policy

Recoverable

Temporary lock

Rate limit

Network interruption

Repository synchronization delay

Maximum retries

3

Exponential backoff

5 s

10 s

20 s

Non-recoverable conflicts require human intervention.

---

# 28. Performance Targets

Conflict validation

< 300 ms

SHA validation

< 100 ms

Lock acquisition

< 200 ms

Merge analysis

< 1 s

Safety validation

< 500 ms

Performance varies with repository size and branch divergence.

---

# 29. Security Principles

The Conflict Handling & Safety module must:

* Prevent accidental overwrites of concurrent changes.
* Respect all repository and branch protection policies.
* Enforce optimistic locking for every write operation.
* Reject stale or invalid SHA values.
* Never bypass merge conflicts automatically unless explicitly allowed by repository policy.
* Maintain complete audit logs for every safety decision.
* Fail safely rather than risking repository corruption.
* Preserve deterministic execution across concurrent workflows.

---

# 30. Future Enhancements

Planned capabilities include:

* AI-assisted merge conflict resolution
* Semantic merge engine
* AST-aware conflict detection
* Multi-file transaction locking
* Distributed lock manager
* Repository-wide dependency impact analysis
* GitHub Checks integration
* Policy-driven merge automation

---

# 31. Quality Principles

The Conflict Handling & Safety module should always:

* Prioritize repository integrity above workflow speed.
* Detect conflicts before any destructive operation.
* Preserve user changes by preventing unintended overwrites.
* Use optimistic locking to maximize concurrency while maintaining consistency.
* Produce deterministic conflict detection and resolution decisions.
* Maintain complete observability through audit logs and events.
* Integrate seamlessly with all GitHub MCP write operations.
* Ensure that every repository modification is safe, traceable, and recoverable.

The Conflict Handling & Safety module is successful when ForgeAI can execute concurrent engineering workflows safely, detect and prevent conflicting modifications, enforce repository policies, and maintain the integrity and auditability of every change made through the GitHub MCP.

# SCHEMA.md (Part 4.2.4-A)

# GitHub MCP Specification — Search Operations

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** GitHub MCP Server

**Module:** Search Operations

**Version:** 1.0

**Status:** Core MCP Module

---

# 1. Purpose

The Search Operations module enables ForgeAI agents to efficiently discover repositories, files, symbols, commits, and source code without manually traversing the repository tree.

Rather than relying on directory iteration, the Search module provides indexed lookup capabilities optimized for AI-assisted software engineering workflows.

This module is read-only and does not modify repository contents.

---

# 2. Responsibilities

The Search Operations module is responsible for:

✓ Repository search

✓ Code search

✓ Commit search

✓ Symbol search (future)

✓ File search

✓ Directory search

✓ Language-aware filtering

✓ Indexed lookup

✓ Search ranking

✓ Result normalization

✓ Audit logging

---

# 3. Supported Operations

| Operation         | Description                       |
| ----------------- | --------------------------------- |
| search_repository | Search repositories               |
| search_files      | Search filenames                  |
| search_code       | Search source code                |
| search_commits    | Search commit history             |
| search_paths      | Search directories                |
| search_symbols    | Search classes/functions (future) |

---

# 4. Search Architecture

```text id="ghsearch01"
AI Agent
     │
     ▼
GitHub MCP
     │
Query Parser
     │
Filter Engine
     │
GitHub Search API
     │
Normalizer
     │
Response Builder
```

---

# 5. Repository Search

Purpose

Locate repositories available to the authenticated user.

Operation

```text id="ghsearch02"
search_repository
```

---

Request

```json id="ghsearch03"
{
  "query":"forge",
  "visibility":"private",
  "limit":20
}
```

---

Response

```json id="ghsearch04"
{
  "repositories":[
    {
      "name":"ForgeAI",
      "owner":"OpenAI",
      "visibility":"private",
      "defaultBranch":"main",
      "language":"Python"
    }
  ]
}
```

---

# 6. Repository Search Fields

Supported fields

Repository name

Owner

Description

Primary language

Visibility

Topics

License

Default branch

Archived status

---

# 7. File Search

Purpose

Locate files by filename or extension.

Operation

```text id="ghsearch05"
search_files
```

---

Example

```json id="ghsearch06"
{
  "repository":"owner/repository",
  "query":"README"
}
```

---

Response

```json id="ghsearch07"
{
  "matches":[
    {
      "path":"README.md",
      "type":"Markdown"
    }
  ]
}
```

---

# 8. Code Search

Purpose

Search repository source code.

Operation

```text id="ghsearch08"
search_code
```

---

Example

Search

```text id="ghsearch09"
create_jwt
```

---

Response

```json id="ghsearch10"
{
  "results":[
    {
      "file":"backend/auth/service.py",
      "line":81,
      "column":14,
      "snippet":"create_jwt_token()"
    }
  ]
}
```

---

# 9. Supported Search Targets

Functions

Classes

Interfaces

Variables

Constants

Imports

Comments

Strings

Annotations

Documentation

Configuration

SQL

---

# 10. Commit Search

Purpose

Search repository history.

Operation

```text id="ghsearch11"
search_commits
```

---

Request

```json id="ghsearch12"
{
  "repository":"owner/repository",
  "query":"authentication"
}
```

---

Response

```json id="ghsearch13"
{
  "commits":[
    {
      "sha":"a72b4d9",
      "author":"ForgeAI",
      "message":"Implement JWT authentication",
      "date":"2026-07-06"
    }
  ]
}
```

---

# 11. Commit Search Fields

SHA

Author

Committer

Message

Branch

Date

Files modified

Tags

---

# 12. Search Filters

Supported filters

Language

Extension

Directory

Filename

Branch

Author

Commit date

Commit SHA

Visibility

Repository

Regular expression (optional)

Case sensitivity

Whole word

---

Example

```json id="ghsearch14"
{
  "query":"token",
  "language":"Python",
  "directory":"backend/auth"
}
```

---

# 13. Search Ranking

Ranking factors

Exact filename match

Exact symbol match

Code relevance

Repository priority

Recency

Branch priority

Path proximity

Result popularity (future)

---

# 14. Search Indexing

Indexed resources

Repositories

Directories

Files

Commits

Branches

Languages

Extensions

Metadata

Future

Symbols

Dependencies

AST

Semantic vectors

---

# 15. Index Refresh

Automatic refresh

Repository synchronization

Branch changes

Pull request merge

Commit creation

Manual refresh API available.

---

# 16. Search Modes

Exact

Prefix

Substring

Regular expression

Case sensitive

Case insensitive

Semantic (future)

---

# 17. Search Limits

Maximum repositories

100

Maximum results

500

Maximum query length

512 characters

Maximum execution time

30 seconds

---

# 18. Request Schema

```json id="ghsearch15"
{
  "requestId":"uuid",
  "workflowId":"uuid",
  "taskId":"uuid",
  "agent":"Architect",
  "tool":"github",
  "action":"search_code",
  "parameters":{
    "repository":"owner/repository",
    "query":"create_jwt"
  }
}
```

---

# 19. Response Schema

```json id="ghsearch16"
{
  "success":true,
  "executionTime":164,
  "data":{
    "results":[]
  },
  "metadata":{
    "totalResults":42,
    "returnedResults":20,
    "cached":true,
    "indexVersion":"1.0"
  }
}
```

---

# 20. Search Result Schema

```json id="ghsearch17"
{
  "path":"backend/auth/service.py",
  "repository":"ForgeAI",
  "branch":"main",
  "line":81,
  "column":14,
  "matchType":"FUNCTION",
  "score":98.7,
  "snippet":"create_jwt_token()"
}
```

---

# 21. Validation Rules

Repository exists

Repository accessible

Branch exists

Search query valid

Search length within limits

Search mode supported

Filters valid

Authentication verified

---

# 22. Error Codes

SEARCH_TIMEOUT

SEARCH_LIMIT_EXCEEDED

INVALID_QUERY

INVALID_FILTER

INVALID_BRANCH

INVALID_REPOSITORY

REPOSITORY_NOT_FOUND

AUTHENTICATION_FAILED

ACCESS_DENIED

RATE_LIMIT_EXCEEDED

INDEX_UNAVAILABLE

UNKNOWN_ERROR

---

# 23. Audit Logging

Every search operation records:

Workflow ID

Task ID

Repository

Search type

Query

Filters

Returned results

Execution time

Agent

Timestamp

Example

```json id="ghsearch18"
{
  "tool":"GitHub",
  "operation":"search_code",
  "repository":"ForgeAI",
  "query":"create_jwt",
  "agent":"Architect",
  "results":6,
  "status":"SUCCESS"
}
```

---

# 24. Events

SEARCH_STARTED

SEARCH_COMPLETED

SEARCH_FAILED

REPOSITORY_SEARCH_COMPLETED

CODE_SEARCH_COMPLETED

COMMIT_SEARCH_COMPLETED

INDEX_REFRESHED

INDEX_UPDATED

---

# 25. Performance Targets

Repository search

< 500 ms

File search

< 500 ms

Code search

< 2 s

Commit search

< 2 s

Index refresh

< 10 s

Performance depends on repository size, indexing state, and GitHub API latency.

---

# 26. Security Principles

The Search Operations module must:

* Enforce repository read permissions before every query.
* Never expose repositories outside the authenticated scope.
* Sanitize all search inputs.
* Prevent injection through search expressions.
* Respect GitHub API rate limits.
* Redact sensitive information from snippets when required by repository policy.
* Maintain complete audit trails for all search operations.
* Return deterministic, normalized search results.

---

# 27. Future Enhancements

Planned capabilities include:

* Semantic code search using embeddings
* AST-aware symbol search
* Cross-repository dependency search
* Natural-language repository queries
* Call graph search
* Reference and implementation lookup
* Security-focused code search
* AI-powered relevance ranking

---

# 28. Quality Principles

The Search Operations module should always:

* Provide fast, accurate, and deterministic repository search capabilities.
* Normalize GitHub search results into provider-independent schemas.
* Support efficient code discovery for all ForgeAI agents.
* Scale to large repositories through indexing and filtering.
* Respect repository permissions and security policies.
* Maintain observability through audit logs and events.
* Deliver structured request and response contracts for every search operation.
* Remain extensible for future semantic and AI-assisted search capabilities.

The Search Operations module is successful when ForgeAI agents can rapidly locate repositories, files, code fragments, and commits through secure, indexed, and highly relevant search interfaces, enabling efficient autonomous software engineering workflows.

# SCHEMA.md (Part 4.4.1-A)

# Terminal MCP Specification

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** Terminal MCP Server

**Module:** Command Execution Foundation

**Version:** 1.0

**Status:** Core MCP Tool

---

# 1. Purpose

The Terminal MCP provides ForgeAI agents with a secure, sandboxed interface for executing terminal commands required during software engineering workflows.

The Terminal MCP abstracts the underlying operating system and shell implementation behind a standardized MCP contract.

Agents never invoke the operating system directly.

All terminal interactions are routed through:

Agent

↓

Orchestrator

↓

Terminal MCP

↓

Sandbox

↓

Operating System

---

# 2. Responsibilities

The Terminal MCP is responsible for:

✓ Executing approved commands

✓ Managing working directories

✓ Providing isolated execution

✓ Capturing stdout/stderr

✓ Returning structured results

✓ Streaming execution logs

✓ Enforcing resource limits

✓ Validating commands

✓ Recording audit logs

✓ Publishing execution events

---

# 3. Supported Operations

| Operation        | Description              |
| ---------------- | ------------------------ |
| execute_command  | Execute terminal command |
| execute_build    | Run build pipeline       |
| execute_tests    | Run automated tests      |
| stream_logs      | Stream command output    |
| cancel_execution | Cancel running process   |
| process_status   | Retrieve process status  |

---

# 4. Execution Architecture

```text
AI Agent
     │
     ▼
AI Orchestrator
     │
     ▼
Terminal MCP
     │
Command Validator
     │
Sandbox
     │
Shell Process
     │
stdout / stderr
     │
Response Builder
```

---

# 5. Command Execution Lifecycle

```text
Request

↓

Authentication

↓

Authorization

↓

Command Validation

↓

Environment Preparation

↓

Process Creation

↓

Execution

↓

Log Streaming

↓

Exit Code

↓

Cleanup

↓

Audit Log

↓

Response
```

---

# 6. Allowed Commands

The default allowlist includes development tooling only.

Build

```
npm
pnpm
yarn
bun
gradle
maven
cargo
go
dotnet
```

Testing

```
pytest
jest
vitest
playwright
cypress
junit
cargo test
go test
```

Utilities

```
git
ls
pwd
cat
find
grep
tree
echo
whoami
```

Package Managers

```
pip
pipx
uv
poetry
npm
pnpm
yarn
cargo
```

Project Tools

```
docker
docker compose
make
cmake
```

---

# 7. Forbidden Commands

The Terminal MCP rejects dangerous commands.

Examples

```
sudo

su

shutdown

reboot

halt

mkfs

fdisk

dd

chmod 777 /

rm -rf /

curl | bash

wget | bash
```

Execution immediately returns

```
COMMAND_NOT_ALLOWED
```

---

# 8. Command Validation

Validation checks

Executable allowed

Arguments valid

Working directory valid

No shell injection

Maximum command length

Maximum argument count

Repository scope

---

# 9. Working Directory

Every execution occurs inside the active workspace.

Example

```
/workspace/ForgeAI
```

Rules

Cannot escape workspace

Cannot access host filesystem

Cannot execute outside repository root

Working directory is configurable per workflow.

---

# 10. Environment Variables

Supported

```
NODE_ENV

PYTHONPATH

JAVA_HOME

GOROOT

CARGO_HOME

CI

FORGEAI_WORKFLOW_ID
```

Secrets are injected securely.

Agents never receive raw secret values.

---

# 11. Build Execution

Operation

```
execute_build
```

Purpose

Compile or package the current project.

Example

```json
{
  "tool":"terminal",
  "action":"execute_build",
  "parameters":{
    "command":"npm run build"
  }
}
```

---

# 12. Test Execution

Operation

```
execute_tests
```

Supported frameworks

PyTest

Jest

Vitest

JUnit

Go Test

Cargo Test

Playwright

Cypress

Example

```json
{
  "tool":"terminal",
  "action":"execute_tests",
  "parameters":{
    "command":"pytest"
  }
}
```

---

# 13. Streaming Logs

The Terminal MCP streams execution in real time.

Stream includes

stdout

stderr

warnings

progress messages

timestamps

Each log entry contains

```json
{
  "timestamp":"2026-07-06T10:30:14Z",
  "stream":"stdout",
  "message":"Running unit tests..."
}
```

---

# 14. Exit Codes

Standard POSIX exit codes are normalized.

| Exit Code | Meaning              |
| --------: | -------------------- |
|         0 | Success              |
|         1 | General error        |
|         2 | Misuse of command    |
|       126 | Cannot execute       |
|       127 | Command not found    |
|       130 | Interrupted          |
|       137 | Process killed       |
|       143 | Graceful termination |

Normalized response

```json
{
  "exitCode":0,
  "status":"SUCCESS"
}
```

---

# 15. Request Schema

```json
{
  "requestId":"uuid",
  "workflowId":"uuid",
  "taskId":"uuid",
  "agent":"Developer",
  "tool":"terminal",
  "action":"execute_command",
  "parameters":{
    "command":"npm test",
    "workingDirectory":"/workspace/ForgeAI"
  }
}
```

---

# 16. Response Schema

```json
{
  "success":true,
  "executionTime":5234,
  "exitCode":0,
  "stdout":"All tests passed.",
  "stderr":"",
  "metadata":{
    "workingDirectory":"/workspace/ForgeAI",
    "timedOut":false
  }
}
```

---

# 17. Design Principles

The Terminal MCP should always:

* Execute only approved commands.
* Run every process inside an isolated sandbox.
* Prevent access outside the active workspace.
* Stream logs in real time.
* Return structured, deterministic responses.
* Normalize exit codes across platforms.
* Never expose secrets or host system information.
* Record every execution for auditing.

# SCHEMA.md (Part 4.4.2-A1)

# Docker MCP Specification — Docker Foundation

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** Docker MCP Server

**Module:** Docker Foundation

**Version:** 1.0

**Status:** Core MCP Tool

---

# 1. Purpose

The Docker MCP provides ForgeAI agents with a secure, standardized interface for building, running, testing, and managing isolated containerized environments.

Rather than allowing agents to execute directly on the host machine, every build, test, and runtime operation occurs inside disposable Docker containers.

This ensures:

* Environment consistency
* Dependency isolation
* Platform independence
* Safe execution
* Reproducible builds
* Secure testing

The Docker MCP abstracts the Docker Engine behind a unified MCP contract, allowing agents to interact with containers without direct access to Docker commands.

---

# 2. Design Goals

The Docker MCP is designed to provide:

* Secure container execution
* Reproducible environments
* Fast container startup
* Disposable execution environments
* Standardized APIs
* Resource isolation
* Auditability
* Extensibility

---

# 3. Responsibilities

The Docker MCP is responsible for:

✓ Image management

✓ Container lifecycle management

✓ Container execution

✓ Build environment preparation

✓ Runtime isolation

✓ Filesystem mounting

✓ Environment injection

✓ Resource monitoring

✓ Log streaming

✓ Cleanup

✓ Security enforcement

✓ Audit logging

---

# 4. High-Level Architecture

```text
               AI Agent
                   │
                   ▼
            AI Orchestrator
                   │
                   ▼
              Docker MCP
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
 Image Manager         Container Manager
        │                     │
        └──────────┬──────────┘
                   ▼
             Docker Engine
                   │
                   ▼
         Running Containers
```

---

# 5. Docker Lifecycle

Every container follows the same deterministic lifecycle.

```text
IMAGE_SELECTED

↓

IMAGE_PULLED

↓

IMAGE_VERIFIED

↓

CONTAINER_CREATED

↓

CONTAINER_STARTED

↓

TASK_RUNNING

↓

TASK_COMPLETED

↓

LOG_COLLECTION

↓

CONTAINER_STOPPED

↓

CONTAINER_REMOVED

↓

CLEANUP_COMPLETE
```

Failure at any stage immediately triggers cleanup.

---

# 6. Lifecycle States

Available states:

REGISTERED

IMAGE_PENDING

IMAGE_READY

CONTAINER_CREATED

STARTING

RUNNING

PAUSED

STOPPED

FAILED

REMOVED

CLEANUP_COMPLETE

UNKNOWN

---

# 7. Docker Components

The Docker MCP consists of:

Image Manager

↓

Image Cache

↓

Container Manager

↓

Execution Manager

↓

Resource Monitor

↓

Log Streamer

↓

Cleanup Manager

↓

Audit Logger

---

# 8. Image Management

The Image Manager controls all Docker images used by ForgeAI.

Responsibilities:

* Pull images
* Cache images
* Verify image integrity
* Track image versions
* Remove unused images
* Maintain image metadata

Agents never pull images directly.

---

# 9. Supported Images

Default approved images include:

Python

```text
python:3.12
```

Node.js

```text
node:22
```

Java

```text
eclipse-temurin:21
```

Go

```text
golang:1.23
```

Rust

```text
rust:latest
```

.NET

```text
mcr.microsoft.com/dotnet/sdk:9.0
```

Ubuntu

```text
ubuntu:24.04
```

Alpine

```text
alpine:latest
```

Additional images may be registered by administrators.

---

# 10. Image Sources

Supported registries:

Docker Hub

GitHub Container Registry

Google Artifact Registry

Azure Container Registry

Amazon ECR

Private OCI Registry

Custom registries require administrator approval.

---

# 11. Image Pull Workflow

```text
Image Requested

↓

Registry Validation

↓

Authentication

↓

Pull Image

↓

Verify Digest

↓

Store Cache

↓

Image Ready
```

---

# 12. Image Verification

Every downloaded image is verified using:

Repository name

Tag

Digest (SHA256)

Registry signature (if available)

Image size

Manifest checksum

Verification failure prevents execution.

---

# 13. Image Metadata

Each image stores:

Image ID

Repository

Tag

Digest

Architecture

Operating System

Creation date

Pull date

Size

Registry

Status

---

Example

```json
{
  "imageId":"sha256:abc123...",
  "repository":"python",
  "tag":"3.12",
  "size":"178MB",
  "status":"READY"
}
```

---

# 14. Image Cache

Frequently used images are cached locally.

Cache Policy

Maximum cache size

20 GB

Unused images

↓

Eligible for cleanup

Cache replacement strategy

Least Recently Used (LRU)

---

# 15. Image Refresh

Images are refreshed when:

New version detected

Security advisory published

Administrator requests refresh

Cache expires

Integrity verification fails

---

# 16. Image Policies

Allowed:

Official images

Verified publishers

Organization-approved images

Forbidden:

Untrusted registries

Unsigned images (optional policy)

Images with known critical vulnerabilities

Locally modified images

---

# 17. Image Selection

The Orchestrator selects images based on:

Programming language

Framework

Repository configuration

Task requirements

User configuration

Example

Python repository

↓

python:3.12

React repository

↓

node:22

---

# 18. Request Schema

```json
{
  "requestId":"uuid",
  "workflowId":"uuid",
  "agent":"Developer",
  "tool":"docker",
  "action":"pull_image",
  "parameters":{
    "repository":"python",
    "tag":"3.12"
  }
}
```

---

# 19. Response Schema

```json
{
  "success":true,
  "executionTime":2450,
  "data":{
    "imageId":"sha256:abc123...",
    "status":"READY"
  },
  "metadata":{
    "cached":false,
    "registry":"docker.io"
  }
}
```

---

# 20. Validation Rules

Every image request validates:

Repository exists

Registry trusted

Tag exists

Digest verified

Architecture supported

Image policy satisfied

Authentication valid

Image size within limits

---

# 21. Error Codes

IMAGE_NOT_FOUND

INVALID_TAG

REGISTRY_UNAVAILABLE

AUTHENTICATION_FAILED

IMAGE_VERIFICATION_FAILED

IMAGE_TOO_LARGE

REGISTRY_TIMEOUT

UNSUPPORTED_ARCHITECTURE

POLICY_VIOLATION

UNKNOWN_ERROR

---

# 22. Audit Logging

Every image operation records:

Workflow ID

Task ID

Agent

Repository

Tag

Digest

Registry

Execution time

Result

Timestamp

Example

```json
{
  "tool":"Docker",
  "operation":"pull_image",
  "repository":"python",
  "tag":"3.12",
  "status":"SUCCESS"
}
```

---

# 23. Events

IMAGE_REQUESTED

IMAGE_PULL_STARTED

IMAGE_PULL_COMPLETED

IMAGE_VERIFIED

IMAGE_CACHED

IMAGE_REFRESHED

IMAGE_REMOVED

IMAGE_PULL_FAILED

---

# 24. Performance Targets

Image lookup

< 100 ms

Cached image load

< 300 ms

Image verification

< 500 ms

Image pull

< 30 s

Metadata retrieval

< 100 ms

Performance targets depend on registry availability and image size.

---

# 25. Security Principles

The Docker Foundation module must:

* Use only trusted container registries.
* Verify image integrity before execution.
* Reject images that violate organizational policies.
* Never expose registry credentials to AI agents.
* Isolate image management from container execution.
* Maintain complete audit trails for every image operation.
* Prevent execution of unverified or tampered images.
* Support future image signing and attestation mechanisms.

---

# 26. Future Enhancements

Planned capabilities include:

* OCI image signing verification (Sigstore/Cosign)
* Software Bill of Materials (SBOM) validation
* Automatic vulnerability scanning
* Multi-architecture image selection
* Layer deduplication
* Distributed image cache
* Private registry federation
* Policy-as-code integration

---

# 27. Quality Principles

The Docker Foundation module should always:

* Provide deterministic and reproducible execution environments.
* Ensure all container images originate from trusted sources.
* Validate every image before use.
* Optimize performance through intelligent caching.
* Maintain complete observability through events and audit logs.
* Abstract Docker Engine complexity behind stable MCP contracts.
* Support extensibility for additional registries and runtimes.
* Prioritize security, reliability, and reproducibility over convenience.

The Docker Foundation module is successful when ForgeAI agents can consistently provision secure, verified, and isolated container environments for software engineering tasks without requiring direct interaction with the Docker Engine.

# SCHEMA.md (Part 4.4.2-A2.1)

# Docker MCP Specification — Container Management

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** Docker MCP Server

**Module:** Container Management

**Version:** 1.0

**Status:** Core MCP Module

---

# 1. Purpose

The Container Management module provides ForgeAI agents with a secure, deterministic interface for creating, managing, monitoring, and disposing of Docker containers throughout the software engineering lifecycle.

Unlike direct Docker CLI access, all container operations are performed through standardized MCP APIs with built-in validation, security enforcement, lifecycle management, and observability.

Each workflow executes within an isolated, disposable container to ensure reproducibility, prevent host contamination, and enable safe parallel execution.

---

# 2. Responsibilities

The Container Management module is responsible for:

✓ Creating containers

✓ Starting containers

✓ Stopping containers

✓ Restarting containers

✓ Pausing and resuming execution

✓ Monitoring container health

✓ Tracking runtime state

✓ Removing containers

✓ Cleaning temporary resources

✓ Validating lifecycle transitions

✓ Publishing lifecycle events

✓ Maintaining audit logs

---

# 3. High-Level Architecture

```text id="dockercm01"
               AI Agent
                   │
                   ▼
            AI Orchestrator
                   │
                   ▼
             Docker MCP API
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
 Container Manager     Resource Monitor
        │                     │
        └──────────┬──────────┘
                   ▼
             Docker Engine
                   │
                   ▼
         Running Containers
```

---

# 4. Container Lifecycle

Every container follows a deterministic lifecycle.

```text id="dockercm02"
REQUESTED

↓

VALIDATED

↓

CREATED

↓

INITIALIZED

↓

STARTING

↓

RUNNING

↓

TASK_EXECUTION

↓

STOPPING

↓

STOPPED

↓

REMOVED

↓

CLEANUP_COMPLETE
```

Failure at any stage transitions the container into **FAILED**, followed by automatic cleanup.

---

# 5. Lifecycle States

| State            | Description                        |
| ---------------- | ---------------------------------- |
| REQUESTED        | Container requested                |
| VALIDATED        | Request successfully validated     |
| CREATED          | Docker container created           |
| INITIALIZED      | Workspace mounted and configured   |
| STARTING         | Runtime initialization in progress |
| RUNNING          | Ready to execute commands          |
| PAUSED           | Execution temporarily suspended    |
| STOPPING         | Shutdown initiated                 |
| STOPPED          | Execution completed                |
| FAILED           | Runtime or validation failure      |
| REMOVED          | Container deleted                  |
| CLEANUP_COMPLETE | Resources released                 |

---

# 6. Container Creation

Operation

```text id="dockercm03"
create_container
```

Purpose

Create an isolated execution environment using an approved Docker image.

The Container Manager automatically:

* Selects the correct image
* Creates the workspace mount
* Configures networking
* Injects approved environment variables
* Applies resource limits
* Registers the container with the orchestrator

---

# 7. Container Start

Operation

```text id="dockercm04"
start_container
```

Before starting, the MCP verifies:

* Image availability
* Workspace mount
* Runtime configuration
* Resource allocation
* Network policy
* Security profile

Only validated containers may enter the **RUNNING** state.

---

# 8. Container Stop

Operation

```text id="dockercm05"
stop_container
```

A graceful shutdown sequence is performed:

```text id="dockercm06"
Signal Process

↓

Flush Logs

↓

Sync Filesystem

↓

Terminate Process

↓

Release Resources

↓

Container Stopped
```

If graceful termination fails, the container may be forcefully terminated according to policy.

---

# 9. Restart Operation

Operation

```text id="dockercm07"
restart_container
```

Restart sequence:

```text id="dockercm08"
Stop

↓

Validate

↓

Reinitialize

↓

Start

↓

Health Check

↓

Running
```

Restart preserves mounted workspace data but resets process state.

---

# 10. Pause & Resume

Supported operations:

```text id="dockercm09"
pause_container

resume_container
```

Pause temporarily suspends execution without terminating the container.

Typical use cases:

* Human approval
* Resource scheduling
* Debugging
* Temporary workflow suspension

---

# 11. Container Removal

Operation

```text id="dockercm10"
remove_container
```

Removal includes:

* Stop running processes
* Flush remaining logs
* Unmount volumes
* Delete temporary resources
* Remove container metadata
* Notify orchestrator

Containers are never reused across independent workflows.

---

# 12. Automatic Cleanup

Cleanup occurs after:

* Successful completion
* Task failure
* Timeout
* Cancellation
* Security violation
* Resource exhaustion

Cleanup guarantees no orphaned containers remain.

---

# 13. State Transitions

Allowed transitions:

```text id="dockercm11"
REQUESTED
      │
      ▼
VALIDATED
      │
      ▼
CREATED
      │
      ▼
INITIALIZED
      │
      ▼
RUNNING
      │
 ┌────┴────┐
 ▼         ▼
PAUSED   STOPPING
 │         │
 ▼         ▼
RUNNING  STOPPED
            │
            ▼
         REMOVED
```

Illegal transitions are rejected.

Example:

RUNNING → CREATED

STOPPED → INITIALIZED

REMOVED → RUNNING

---

# 14. Failure State

Any unrecoverable error places the container into:

```text id="dockercm12"
FAILED
```

Recovery policy:

* Record diagnostics
* Preserve logs
* Release resources
* Remove container
* Notify orchestrator

---

# 15. Validation Pipeline

Before every lifecycle transition, the MCP validates:

Repository workspace exists

Approved image selected

Container configuration valid

Container not already removed

Requested transition allowed

Resource limits configured

Security policy satisfied

Docker daemon available

---

# 16. Lifecycle Validation Matrix

| Current State | Allowed Next States      |
| ------------- | ------------------------ |
| REQUESTED     | VALIDATED                |
| VALIDATED     | CREATED, FAILED          |
| CREATED       | INITIALIZED, FAILED      |
| INITIALIZED   | STARTING, FAILED         |
| STARTING      | RUNNING, FAILED          |
| RUNNING       | PAUSED, STOPPING, FAILED |
| PAUSED        | RUNNING, STOPPING        |
| STOPPING      | STOPPED                  |
| STOPPED       | REMOVED                  |
| FAILED        | REMOVED                  |
| REMOVED       | —                        |

Any transition not listed is considered invalid.

---

# 17. Health Verification

During execution the Container Manager monitors:

Container running status

Process availability

Memory allocation

CPU usage

Disk availability

Workspace accessibility

Docker daemon connectivity

Health status is continuously reported to the Orchestrator.

---

# 18. Validation Rules

Every container request validates:

Approved Docker image

Valid workflow ID

Authorized agent

Supported runtime

Workspace available

Container name unique

Resource configuration valid

Container state transition valid

Security policy satisfied

---

# 19. Error Codes

CONTAINER_NOT_FOUND

CONTAINER_ALREADY_EXISTS

INVALID_CONTAINER_STATE

INVALID_STATE_TRANSITION

CONTAINER_CREATION_FAILED

CONTAINER_START_FAILED

CONTAINER_STOP_FAILED

CONTAINER_REMOVE_FAILED

HEALTH_CHECK_FAILED

DOCKER_ENGINE_UNAVAILABLE

VALIDATION_FAILED

UNKNOWN_ERROR

---

# 20. Lifecycle Events

The Container Manager publishes:

CONTAINER_REQUESTED

CONTAINER_VALIDATED

CONTAINER_CREATED

CONTAINER_INITIALIZED

CONTAINER_STARTED

CONTAINER_PAUSED

CONTAINER_RESUMED

CONTAINER_STOPPED

CONTAINER_REMOVED

CONTAINER_FAILED

CLEANUP_STARTED

CLEANUP_COMPLETED

---

# 21. Audit Logging

Every lifecycle operation records:

Workflow ID

Task ID

Container ID

Image ID

Current state

Next state

Agent

Execution time

Timestamp

Result

Example

```json id="dockercm13"
{
  "tool":"Docker",
  "operation":"start_container",
  "containerId":"ctr-8f2d4",
  "workflowId":"wf-104",
  "agent":"Developer",
  "status":"SUCCESS"
}
```

---

# 22. Design Principles

The Container Management module should always:

* Execute every workflow inside a disposable container.
* Maintain deterministic lifecycle transitions.
* Reject invalid state changes.
* Ensure automatic cleanup after execution.
* Isolate workflows from one another.
* Preserve reproducibility across environments.
* Provide complete observability through events and audit logs.
* Keep container management independent from higher-level orchestration logic.

The Container Management module is successful when ForgeAI can reliably provision, manage, monitor, and dispose of isolated execution environments while maintaining security, consistency, and deterministic lifecycle behavior across all autonomous software engineering workflows.

# SCHEMA.md (Part 4.4.2-A2.2.1-A)

# Docker MCP Specification — Volume Mount Architecture

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** Docker MCP Server

**Module:** Volume Mount Architecture

**Version:** 1.0

**Status:** Core MCP Module

---

# 1. Purpose

The Volume Mount Architecture defines how ForgeAI securely exposes project files and persistent storage to Docker containers.

Rather than copying repositories into containers, ForgeAI mounts controlled filesystem locations into isolated execution environments. This enables containers to read and modify project files while preventing unauthorized access to the host operating system.

The architecture prioritizes:

* Workspace isolation
* High-performance file access
* Reproducible execution
* Secure filesystem boundaries
* Cross-platform compatibility
* Persistent development state where required

---

# 2. Design Goals

The volume subsystem is designed to:

* Minimize container startup time
* Eliminate unnecessary file duplication
* Prevent host filesystem exposure
* Support multiple concurrent workflows
* Isolate project workspaces
* Provide deterministic mount paths
* Support both ephemeral and persistent storage

---

# 3. Architecture Overview

```text
                 Host Machine
                      │
      ┌───────────────┴────────────────┐
      │                                │
 Workspace Directory             Named Volumes
      │                                │
      └───────────────┬────────────────┘
                      │
                 Docker Engine
                      │
               Mounted Container
                      │
      /workspace      /cache      /tmp
```

Only approved mount points are exposed to containers.

---

# 4. Volume Types

ForgeAI supports two primary volume types:

| Volume Type  | Purpose                                            |
| ------------ | -------------------------------------------------- |
| Bind Mount   | Maps an existing host directory into the container |
| Named Volume | Docker-managed persistent storage                  |

Additional volume types may be introduced in future releases.

---

# 5. Workspace Mounts

Every workflow receives an isolated workspace mounted inside the container.

Example:

```text
Host:
/forgeai/workspaces/wf-104/

↓

Container:
/workspace
```

All agent file operations occur relative to `/workspace`.

Agents are never aware of the underlying host path.

---

# 6. Workspace Layout

Example container filesystem:

```text
/
├── workspace/
│   ├── backend/
│   ├── frontend/
│   ├── docs/
│   ├── tests/
│   └── README.md
│
├── cache/
│
├── tmp/
│
└── logs/
```

Reserved directories are managed by the Docker MCP.

---

# 7. Workspace Isolation

Each workflow receives its own isolated workspace.

Example:

```text
Workflow A

/workspaces/wf-101/

Workflow B

/workspaces/wf-102/

Workflow C

/workspaces/wf-103/
```

Containers cannot access another workflow's workspace.

---

# 8. Bind Mounts

Bind mounts map an existing host directory into the container.

Example:

```text
Host

/projects/ForgeAI

↓

Container

/workspace
```

Characteristics:

* Direct filesystem access
* High performance
* Real-time synchronization
* Suitable for active development

---

# 9. Supported Bind Mounts

Default mappings:

| Host                | Container    |
| ------------------- | ------------ |
| Workspace           | `/workspace` |
| Temporary Directory | `/tmp`       |
| Build Cache         | `/cache`     |
| Logs                | `/logs`      |

Additional bind mounts require administrator approval.

---

# 10. Bind Mount Policies

Allowed:

* Project workspace
* Temporary build directory
* Compiler cache
* Package cache
* Log directory

Forbidden:

* System root (`/`)
* Home directories
* SSH configuration
* Docker socket
* System configuration directories
* Other user workspaces

---

# 11. Named Volumes

Named volumes provide persistent Docker-managed storage.

Example:

```text
forgeai-node-cache

↓

/cache/node
```

Typical uses:

* Dependency cache
* Build cache
* Package manager cache
* Language runtime cache

Named volumes persist across container lifecycles.

---

# 12. Standard Named Volumes

ForgeAI may provision:

```text
forgeai-node-cache

forgeai-python-cache

forgeai-gradle-cache

forgeai-maven-cache

forgeai-rust-cache

forgeai-go-cache
```

These volumes improve build performance while keeping project files separate from cached artifacts.

---

# 13. Volume Selection

The Orchestrator selects volume configurations based on:

* Programming language
* Framework
* Build tool
* Workflow type
* Agent requirements

Example:

Python project:

* Workspace bind mount
* Python package cache
* Temporary build directory

Node.js project:

* Workspace bind mount
* npm/pnpm cache
* Build cache

---

# 14. Mount Lifecycle

```text
Create Workspace

↓

Create Volume

↓

Validate Mount

↓

Attach Container

↓

Execute Workflow

↓

Detach Volume

↓

Cleanup (if ephemeral)

↓

Complete
```

Persistent named volumes remain available for future workflows.

---

# 15. Mount Properties

Each mount records:

* Mount ID
* Volume type
* Source path
* Target path
* Read/write mode
* Persistence
* Owner workflow
* Status

Example:

```json
{
  "mountId":"mnt-104",
  "type":"bind",
  "source":"/forgeai/workspaces/wf-104",
  "target":"/workspace",
  "mode":"rw",
  "persistent":false
}
```

---

# 16. Mount Constraints

The Docker MCP enforces:

* One workspace mount per workflow
* Unique mount targets
* No overlapping mounts
* No duplicate source paths
* Deterministic mount ordering

Violations result in request rejection.

---

# 17. Performance Targets

Workspace mount:

* < 100 ms

Named volume attachment:

* < 200 ms

Mount validation:

* < 100 ms

Volume initialization:

* < 500 ms

Performance depends on the host filesystem and Docker runtime.

---

# 18. Future Enhancements

Planned improvements include:

* Read-only dependency layers
* Incremental workspace snapshots
* Distributed cache volumes
* Cloud-backed persistent volumes
* Encrypted workspace mounts
* Remote development workspaces
* OCI-compatible volume drivers
* Cross-host volume replication

---

# 19. Design Principles

The Volume Mount Architecture should always:

* Mount only approved filesystem locations.
* Keep project workspaces isolated between workflows.
* Separate persistent caches from source code.
* Provide deterministic mount paths across all containers.
* Prevent containers from accessing arbitrary host directories.
* Support efficient development workflows through bind mounts.
* Improve build performance through reusable named volumes.
* Remain portable across Linux, macOS, and Windows Docker environments.

The Volume Mount Architecture is successful when every ForgeAI container receives a secure, isolated, and reproducible filesystem environment that enables autonomous software engineering tasks while protecting the host system and maintaining consistent execution across workflows.

# SCHEMA.md (Part 4.4.2-A2.2.1-B)

# Docker MCP Specification — Named Volumes & Mount Security

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** Docker MCP Server

**Module:** Named Volumes & Mount Security

**Version:** 1.0

**Status:** Core MCP Module

---

# 1. Named Volumes

## Purpose

Named volumes provide Docker-managed persistent storage that survives container deletion. Unlike bind mounts, named volumes are managed entirely by the Docker Engine and are used for reusable caches, build artifacts, and runtime data that should persist across multiple workflow executions.

Named volumes improve performance by avoiding repeated downloads of dependencies while keeping project source code isolated within workspace bind mounts.

---

# 2. Named Volume Architecture

```text
             Docker Engine
                  │
      ┌───────────┴───────────┐
      │                       │
 Named Volume          Running Container
 forgeai-python-cache        │
      │                      │
      └────────────► /cache/python
```

Named volumes are never mounted directly into the project workspace.

---

# 3. Supported Named Volumes

| Volume               | Purpose                   |
| -------------------- | ------------------------- |
| forgeai-python-cache | Python package cache      |
| forgeai-node-cache   | npm/pnpm/yarn cache       |
| forgeai-gradle-cache | Gradle dependency cache   |
| forgeai-maven-cache  | Maven repository cache    |
| forgeai-rust-cache   | Cargo registry cache      |
| forgeai-go-cache     | Go module cache           |
| forgeai-build-cache  | General build artifacts   |
| forgeai-temp-storage | Temporary runtime storage |

---

# 4. Volume Lifecycle

```text
Create Volume
      │
Validate
      │
Attach
      │
Use During Workflow
      │
Detach
      │
Retain or Delete
```

Persistent cache volumes remain after container removal.

Temporary volumes are automatically deleted during cleanup.

---

# 5. Volume Policies

Persistent:

* Language dependency caches
* Build caches
* Package manager metadata

Ephemeral:

* Temporary runtime files
* Intermediate build outputs
* Session data
* Scratch storage

Project source code must never be stored inside named volumes.

---

# 6. Mount Validation

Every mount request passes the following validation pipeline.

```text
Mount Request
      │
Path Validation
      │
Volume Validation
      │
Permission Validation
      │
Duplicate Check
      │
Security Policy Check
      │
Container Validation
      │
Mount Approved
```

Any failed validation immediately rejects the request.

---

# 7. Validation Rules

The Docker MCP validates:

* Source path exists
* Target path is valid
* Target path not already mounted
* Volume name follows naming convention
* Volume type supported
* Read/write mode valid
* Container exists
* Workflow authorized
* Mount policy satisfied

---

# 8. Path Restrictions

Allowed mount targets include:

```text
/workspace

/cache

/tmp

/logs

/home/forgeai
```

Forbidden targets include:

```text
/

 /etc

 /usr

 /bin

 /boot

 /proc

 /sys

 /dev

 /var/run/docker.sock
```

System directories are never exposed to containers.

---

# 9. Security Rules

The Volume Mount subsystem enforces the following rules:

* Mount only approved directories.
* Never expose the host root filesystem.
* Never mount another workflow's workspace.
* Never mount SSH keys or credential stores.
* Prevent access to Docker daemon sockets.
* Prevent nested container control.
* Enforce least-privilege access.
* Restrict mounts to the active workflow.

---

# 10. Read/Write Policies

| Mount Type        | Default Mode |
| ----------------- | ------------ |
| Workspace         | Read/Write   |
| Cache             | Read/Write   |
| Logs              | Read/Write   |
| Configuration     | Read-Only    |
| Runtime Libraries | Read-Only    |

Read-only mounts cannot be modified by any agent.

---

# 11. Mount Isolation

Each workflow receives isolated mount namespaces.

```text
Workflow A
/workspace
/cache

Workflow B
/workspace
/cache
```

No shared writable workspace exists between concurrent workflows.

---

# 12. Security Validation

Before every mount, the Docker MCP verifies:

* Agent authorization
* Active workflow ownership
* Container state
* Filesystem boundaries
* Path normalization
* Symbolic link safety
* Duplicate mount prevention
* Security policy compliance

---

# 13. Events

The Docker MCP publishes lifecycle events for all mount operations.

Supported events:

MOUNT_REQUESTED

MOUNT_VALIDATED

MOUNT_CREATED

MOUNT_ATTACHED

MOUNT_DETACHED

MOUNT_REMOVED

MOUNT_FAILED

VOLUME_CREATED

VOLUME_DELETED

CACHE_REUSED

SECURITY_VIOLATION

---

# 14. Event Schema

```json
{
  "eventId":"evt-104",
  "type":"MOUNT_ATTACHED",
  "workflowId":"wf-104",
  "containerId":"ctr-204",
  "timestamp":"2026-07-06T12:10:18Z",
  "payload":{
    "source":"/forgeai/workspaces/wf-104",
    "target":"/workspace"
  }
}
```

---

# 15. Audit Logging

Every mount operation generates an immutable audit record.

Recorded fields:

* Workflow ID
* Task ID
* Container ID
* Agent
* Source path
* Target path
* Mount type
* Access mode
* Validation result
* Timestamp
* Execution time

Example:

```json
{
  "tool":"Docker",
  "operation":"attach_mount",
  "containerId":"ctr-204",
  "workflowId":"wf-104",
  "mountType":"bind",
  "target":"/workspace",
  "status":"SUCCESS"
}
```

---

# 16. Error Codes

MOUNT_NOT_FOUND

INVALID_MOUNT_PATH

INVALID_VOLUME

DUPLICATE_MOUNT

MOUNT_ALREADY_EXISTS

MOUNT_PERMISSION_DENIED

READ_ONLY_VIOLATION

INVALID_CONTAINER

WORKFLOW_NOT_AUTHORIZED

SECURITY_POLICY_VIOLATION

HOST_PATH_FORBIDDEN

DOCKER_ENGINE_UNAVAILABLE

UNKNOWN_ERROR

---

# 17. Performance Targets

Bind mount creation:

* < 100 ms

Named volume attachment:

* < 200 ms

Mount validation:

* < 100 ms

Mount removal:

* < 100 ms

Audit log creation:

* < 20 ms

Event publication:

* < 10 ms

Performance may vary depending on host storage and Docker runtime.

---

# 18. Design Principles

The Mount Security subsystem should always:

* Protect the host filesystem from container access.
* Isolate every workflow into its own filesystem namespace.
* Use bind mounts only for project workspaces.
* Use named volumes only for persistent caches and reusable runtime data.
* Validate every mount request before execution.
* Reject unsafe paths deterministically.
* Produce complete audit logs and lifecycle events.
* Maintain reproducible and secure execution across all ForgeAI workflows.

The Mount Security subsystem is successful when every ForgeAI container receives only the filesystem resources required for its task, while preventing privilege escalation, cross-workflow interference, and unauthorized access to the host operating system.

# SCHEMA.md (Part 4.4.2-B)

# Docker MCP Specification — Docker Runtime

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** Docker MCP Server

**Module:** Docker Runtime

**Version:** 1.0

**Status:** Core MCP Module

---

# 1. Purpose

The Docker Runtime module governs the execution environment for all ForgeAI containers. It is responsible for enforcing runtime resource limits, network isolation, health monitoring, log streaming, runtime event generation, audit logging, and secure execution policies.

The Runtime module ensures that every AI agent executes inside a predictable, observable, and isolated container environment while protecting the host system and maintaining reproducible software engineering workflows.

---

# 2. Responsibilities

The Docker Runtime is responsible for:

✓ CPU and memory allocation

✓ Disk usage monitoring

✓ Network isolation

✓ Log streaming

✓ Container health monitoring

✓ Runtime event publication

✓ Runtime audit logging

✓ Error reporting

✓ Security enforcement

✓ Runtime cleanup

---

# 3. Runtime Architecture

```text id="dockerruntime01"
          AI Orchestrator
                │
                ▼
          Docker Runtime
                │
     ┌──────────┴──────────┐
     ▼                     ▼
 Resource Manager    Health Monitor
     │                     │
     └──────────┬──────────┘
                ▼
         Docker Container
```

---

# 4. Resource Limits

Each container executes with predefined resource quotas to prevent resource exhaustion.

Default limits:

| Resource          | Default    |
| ----------------- | ---------- |
| CPU               | 2 vCPU     |
| Memory            | 4 GB       |
| Disk              | 20 GB      |
| PIDs              | 512        |
| Open Files        | 4096       |
| Execution Timeout | 30 minutes |

Administrators may override these values based on workflow requirements.

---

# 5. Runtime Resource Policies

The Docker Runtime enforces:

* Maximum CPU utilization
* Memory quotas
* Disk usage limits
* Temporary storage quotas
* File descriptor limits
* Process count limits
* Automatic timeout termination

Containers exceeding limits are gracefully terminated.

---

# 6. Network Policies

Containers execute inside isolated virtual networks.

Allowed network operations:

* HTTPS requests
* Git repository access
* Package registry downloads
* Approved MCP service communication

Blocked operations:

* Host network access
* Docker daemon access
* Local network scanning
* Raw socket creation
* Peer-to-peer networking
* Unauthorized outbound traffic

All network policies follow a default-deny model.

---

# 7. Log Streaming

Runtime logs are streamed in real time to the Orchestrator.

Supported log streams:

* Standard Output (stdout)
* Standard Error (stderr)
* Build logs
* Test logs
* Runtime diagnostics
* Health events

Each log entry includes:

```json id="dockerruntime02"
{
  "timestamp":"2026-07-06T12:30:18Z",
  "containerId":"ctr-204",
  "stream":"stdout",
  "level":"INFO",
  "message":"Running integration tests..."
}
```

Log streams are immutable and timestamped.

---

# 8. Health Checks

The Runtime continuously monitors:

* Container running state
* Process availability
* CPU usage
* Memory consumption
* Disk usage
* Filesystem accessibility
* Network connectivity
* Exit status

Health checks occur at configurable intervals.

---

# 9. Health States

| State      | Description                       |
| ---------- | --------------------------------- |
| HEALTHY    | Container operating normally      |
| STARTING   | Runtime initializing              |
| DEGRADED   | Resource usage approaching limits |
| UNHEALTHY  | Health check failure detected     |
| TERMINATED | Execution stopped                 |
| UNKNOWN    | Status unavailable                |

Containers entering the **UNHEALTHY** state may be restarted or terminated according to workflow policy.

---

# 10. Error Handling

Runtime errors are normalized into structured responses.

Common runtime errors:

CONTAINER_TIMEOUT

MEMORY_LIMIT_EXCEEDED

CPU_LIMIT_EXCEEDED

DISK_LIMIT_EXCEEDED

NETWORK_POLICY_VIOLATION

HEALTH_CHECK_FAILED

LOG_STREAM_FAILURE

DOCKER_ENGINE_UNAVAILABLE

CONTAINER_CRASHED

UNKNOWN_RUNTIME_ERROR

Every runtime error includes:

* Error code
* Severity
* Timestamp
* Workflow ID
* Container ID
* Recommended recovery action

---

# 11. Runtime Events

The Docker Runtime publishes the following events:

RUNTIME_STARTED

RESOURCE_LIMIT_REACHED

HEALTH_CHECK_PASSED

HEALTH_CHECK_FAILED

LOG_STREAM_STARTED

LOG_STREAM_STOPPED

NETWORK_POLICY_TRIGGERED

CONTAINER_TERMINATED

TIMEOUT_REACHED

RUNTIME_COMPLETED

RUNTIME_FAILED

All events are delivered to the ForgeAI Event Bus.

---

# 12. Event Schema

```json id="dockerruntime03"
{
  "eventId":"evt-204",
  "type":"HEALTH_CHECK_FAILED",
  "workflowId":"wf-204",
  "containerId":"ctr-204",
  "timestamp":"2026-07-06T12:42:31Z",
  "payload":{
    "reason":"Memory limit exceeded"
  }
}
```

---

# 13. Audit Logging

Every runtime operation produces an immutable audit record.

Recorded fields:

* Workflow ID
* Task ID
* Container ID
* Agent
* Runtime state
* Resource utilization
* Network activity summary
* Exit code
* Execution duration
* Timestamp
* Result

Example:

```json id="dockerruntime04"
{
  "tool":"Docker",
  "operation":"runtime_execution",
  "workflowId":"wf-204",
  "containerId":"ctr-204",
  "status":"SUCCESS",
  "executionTime":842000
}
```

Audit logs are retained according to organizational retention policies.

---

# 14. Performance Targets

| Operation          | Target   |
| ------------------ | -------- |
| Container startup  | < 2 s    |
| Health check       | < 100 ms |
| Log latency        | < 250 ms |
| Event publication  | < 20 ms  |
| Runtime shutdown   | < 2 s    |
| Audit log creation | < 20 ms  |

Performance targets are measured under normal operating conditions.

---

# 15. Security Principles

The Docker Runtime must:

* Enforce strict resource isolation.
* Operate with least privilege.
* Prevent host filesystem access outside approved mounts.
* Restrict network communication to approved destinations.
* Prevent privilege escalation inside containers.
* Protect runtime secrets from AI agents.
* Monitor and terminate abnormal execution.
* Maintain complete runtime observability.
* Ensure deterministic execution across all workflows.

---

# 16. Quality Principles

The Docker Runtime should always:

* Provide reproducible execution environments.
* Fail safely under resource exhaustion.
* Maintain complete visibility through logs and events.
* Detect runtime failures as early as possible.
* Isolate every workflow from all others.
* Scale to concurrent autonomous engineering tasks.
* Produce deterministic runtime behavior regardless of host platform.
* Integrate seamlessly with the Terminal MCP, GitHub MCP, Filesystem MCP, and ForgeAI Orchestrator.

The Docker Runtime module is successful when every ForgeAI workflow executes inside a secure, isolated, observable, and resource-controlled container environment, enabling reliable autonomous software engineering while protecting the host system and maintaining reproducible execution across all supported platforms.

# SCHEMA.md (Part 4.4.3-A)

# Terminal & Docker MCP Specification — Terminal Security

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** Terminal & Docker MCP Server

**Module:** Terminal Security

**Version:** 1.0

**Status:** Core Security Module

---

# 1. Purpose

The Terminal Security module provides the primary security boundary between ForgeAI agents and the underlying operating system. It ensures that all terminal commands are executed within a controlled, sandboxed environment, preventing unauthorized system access, privilege escalation, host modification, and malicious command execution.

Rather than allowing unrestricted shell access, ForgeAI agents interact exclusively through validated MCP requests. Every command is authenticated, authorized, validated, sandboxed, monitored, and audited before execution.

The Terminal Security module follows a **default-deny** security model: only explicitly approved commands and operations are permitted.

---

# 2. Security Objectives

The module is designed to:

* Protect the host operating system
* Prevent privilege escalation
* Restrict filesystem access
* Limit resource consumption
* Prevent shell injection
* Isolate concurrent workflows
* Support reproducible execution
* Maintain complete observability
* Produce deterministic security decisions

---

# 3. Security Architecture

```text id="termsec01"
              AI Agent
                  │
                  ▼
          AI Orchestrator
                  │
                  ▼
          Terminal Security
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
 Command Validator     Policy Engine
      │                       │
      └───────────┬───────────┘
                  ▼
           Docker Sandbox
                  │
                  ▼
         Approved Command
```

All command execution passes through the security layer before reaching the container runtime.

---

# 4. Command Allowlist

Only commands explicitly approved by ForgeAI may be executed.

### Build Tools

```text id="termsec02"
npm
pnpm
yarn
bun
make
cmake
gradle
mvn
cargo
go
dotnet
```

### Testing Tools

```text id="termsec03"
pytest
jest
vitest
playwright
cypress
go test
cargo test
mvn test
gradle test
```

### Version Control

```text id="termsec04"
git
git status
git diff
git log
git branch
git checkout
git fetch
```

### File Utilities

```text id="termsec05"
ls
pwd
cat
find
grep
tree
echo
mkdir
cp
mv
```

### Language Toolchains

```text id="termsec06"
python
node
java
javac
go
rustc
cargo
dotnet
```

Administrators may extend the allowlist through policy configuration.

---

# 5. Command Categories

| Category          | Examples           |
| ----------------- | ------------------ |
| Build             | npm, gradle, cargo |
| Testing           | pytest, jest       |
| Version Control   | git                |
| File Operations   | ls, cat            |
| Package Managers  | pip, npm, cargo    |
| Language Runtimes | python, node       |

Every category has independent security policies.

---

# 6. Forbidden Commands

The following commands are permanently blocked:

### Privilege Escalation

```text id="termsec07"
sudo
su
passwd
```

### System Shutdown

```text id="termsec08"
shutdown
reboot
halt
poweroff
```

### Filesystem Destruction

```text id="termsec09"
rm -rf /
mkfs
fdisk
dd
```

### Permission Manipulation

```text id="termsec10"
chmod 777 /
chown root
setfacl
```

### Network Abuse

```text id="termsec11"
nmap
tcpdump
netcat
socat
```

### Remote Script Execution

```text id="termsec12"
curl | bash
wget | bash
```

### Container Management

```text id="termsec13"
docker system prune
docker rm -f
docker exec
docker run --privileged
```

Execution of forbidden commands immediately returns:

```text id="termsec14"
COMMAND_NOT_ALLOWED
```

---

# 7. Sandboxing

All terminal commands execute inside isolated Docker containers.

Sandbox characteristics:

* No host shell access
* No root privileges
* Isolated PID namespace
* Isolated mount namespace
* Isolated network namespace
* Restricted capabilities
* Disposable runtime
* Automatic cleanup

The sandbox is recreated for every workflow.

---

# 8. Filesystem Restrictions

The sandbox exposes only approved directories:

```text id="termsec15"
/workspace
/cache
/tmp
/logs
```

The following paths are inaccessible:

```text id="termsec16"
/
/etc
/usr
/bin
/proc
/sys
/dev
/root
/home
```

Access outside approved mount points is denied.

---

# 9. Timeouts

Every command executes within a bounded execution window.

Default limits:

| Operation         | Timeout |
| ----------------- | ------- |
| File Operations   | 30 s    |
| Build             | 15 min  |
| Unit Tests        | 20 min  |
| Integration Tests | 30 min  |
| Generic Command   | 5 min   |

On timeout:

1. Process receives SIGTERM.
2. Grace period is applied.
3. Remaining processes receive SIGKILL.
4. Resources are released.
5. Audit log is written.

---

# 10. CPU Limits

Default CPU allocation:

| Workflow Type |    CPU |
| ------------- | -----: |
| Standard      | 2 vCPU |
| Large Build   | 4 vCPU |
| Heavy Testing | 6 vCPU |

CPU quotas prevent a single workflow from monopolizing host resources.

---

# 11. Memory Limits

Default memory allocation:

| Workflow Type | Memory |
| ------------- | -----: |
| Standard      |   4 GB |
| Large Build   |   8 GB |
| Heavy Testing |  12 GB |

Containers exceeding memory limits are terminated by the runtime.

---

# 12. Additional Runtime Limits

Maximum processes:

512

Maximum open files:

4096

Maximum disk usage:

20 GB

Maximum log size:

500 MB

Maximum concurrent terminal sessions:

1 per workflow

---

# 13. Validation Pipeline

Every terminal request passes through:

```text id="termsec17"
Authentication
      │
Authorization
      │
Command Parsing
      │
Allowlist Validation
      │
Argument Validation
      │
Filesystem Validation
      │
Resource Policy Check
      │
Sandbox Creation
      │
Execution
```

Failure at any stage aborts execution.

---

# 14. Validation Rules

The Terminal Security module validates:

* Agent identity
* Active workflow ownership
* Authorized MCP tool
* Approved executable
* Valid arguments
* Working directory inside workspace
* No forbidden characters
* No shell injection patterns
* Resource limits available
* Sandbox successfully initialized

Invalid requests are rejected before execution.

---

# 15. Security Violations

Examples include:

* Attempting a forbidden command
* Accessing restricted paths
* Exceeding resource limits
* Executing outside the sandbox
* Unauthorized workflow access
* Shell injection attempts
* Privilege escalation attempts

Security violations are logged and reported to the Orchestrator.

---

# 16. Performance Targets

| Operation              | Target   |
| ---------------------- | -------- |
| Command validation     | < 50 ms  |
| Sandbox initialization | < 1 s    |
| Policy evaluation      | < 20 ms  |
| Security decision      | < 100 ms |

---

# 17. Design Principles

The Terminal Security module should always:

* Default to denying unapproved operations.
* Execute every command inside an isolated container.
* Prevent direct interaction with the host operating system.
* Enforce deterministic resource limits.
* Validate every command before execution.
* Reject dangerous operations without exception.
* Keep security policies independent from business logic.
* Provide reproducible, secure execution environments for every ForgeAI workflow.

The Terminal Security module is successful when ForgeAI agents can perform legitimate software engineering tasks through terminal operations while remaining fully isolated from the host environment, constrained by policy, and protected against misuse, accidental damage, or malicious execution.

# SCHEMA.md (Part 4.4.3-B)

# Terminal & Docker MCP Specification — Runtime Security

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** Terminal & Docker MCP Server

**Module:** Runtime Security

**Version:** 1.0

**Status:** Core Security Module

---

# 1. Purpose

The Runtime Security module provides continuous monitoring, auditing, event generation, error handling, and standardized API contracts for all Terminal MCP and Docker MCP operations.

Unlike Terminal Security, which validates execution before a command runs, Runtime Security continuously observes execution while commands and containers are running, ensuring that every action is traceable, recoverable, and compliant with organizational security policies.

---

# 2. Responsibilities

The Runtime Security module is responsible for:

✓ Runtime audit logging

✓ Security event generation

✓ Error normalization

✓ Incident reporting

✓ API contract enforcement

✓ Runtime monitoring

✓ Policy violation reporting

✓ Execution traceability

✓ Workflow observability

---

# 3. Runtime Audit Logging

Every terminal and Docker operation produces an immutable audit record.

Audit logging is mandatory and cannot be disabled.

Audit records are written asynchronously to prevent execution delays.

---

# 4. Logged Operations

The following operations are always logged:

* Command execution
* Build execution
* Test execution
* Docker image pull
* Container creation
* Container startup
* Container shutdown
* Volume attachment
* Filesystem access
* Security validation
* Policy violations
* Runtime failures
* Workflow completion

---

# 5. Audit Record Structure

Each audit record contains:

* Audit ID
* Workflow ID
* Task ID
* Agent ID
* MCP Tool
* Operation
* Timestamp
* Execution duration
* Status
* Resource usage
* Exit code
* Security outcome

Example:

```json id="runtime01"
{
  "auditId":"audit-104",
  "workflowId":"wf-104",
  "taskId":"task-17",
  "agent":"Developer",
  "tool":"Terminal MCP",
  "operation":"execute_command",
  "status":"SUCCESS",
  "executionTime":2481,
  "exitCode":0,
  "timestamp":"2026-07-06T15:20:14Z"
}
```

---

# 6. Security Events

Runtime Security publishes structured events to the ForgeAI Event Bus.

Supported events include:

COMMAND_EXECUTION_STARTED

COMMAND_EXECUTION_COMPLETED

COMMAND_EXECUTION_FAILED

BUILD_STARTED

BUILD_COMPLETED

TEST_STARTED

TEST_COMPLETED

CONTAINER_CREATED

CONTAINER_STARTED

CONTAINER_STOPPED

CONTAINER_TERMINATED

SECURITY_POLICY_TRIGGERED

RESOURCE_LIMIT_REACHED

WORKFLOW_COMPLETED

WORKFLOW_FAILED

AUDIT_LOG_CREATED

---

# 7. Event Structure

```json id="runtime02"
{
  "eventId":"evt-812",
  "type":"COMMAND_EXECUTION_COMPLETED",
  "workflowId":"wf-104",
  "taskId":"task-17",
  "containerId":"ctr-204",
  "timestamp":"2026-07-06T15:22:08Z",
  "severity":"INFO",
  "payload":{
    "command":"npm test",
    "exitCode":0
  }
}
```

Event delivery is asynchronous and ordered within a workflow.

---

# 8. Error Handling

All runtime failures are normalized into a consistent error model.

Errors are classified as:

| Severity | Description                   |
| -------- | ----------------------------- |
| INFO     | Informational                 |
| WARNING  | Recoverable issue             |
| ERROR    | Operation failed              |
| CRITICAL | Workflow termination required |

---

# 9. Standard Error Codes

Authentication:

AUTHENTICATION_FAILED

AUTHORIZATION_FAILED

Execution:

COMMAND_NOT_ALLOWED

COMMAND_TIMEOUT

PROCESS_TERMINATED

PROCESS_CRASHED

Container:

CONTAINER_NOT_FOUND

CONTAINER_START_FAILED

CONTAINER_STOP_FAILED

Docker:

DOCKER_ENGINE_UNAVAILABLE

IMAGE_NOT_FOUND

IMAGE_PULL_FAILED

Filesystem:

INVALID_WORKSPACE

READ_ONLY_VIOLATION

INVALID_PATH

Security:

POLICY_VIOLATION

RESOURCE_LIMIT_EXCEEDED

NETWORK_ACCESS_DENIED

SANDBOX_FAILURE

Generic:

VALIDATION_FAILED

UNKNOWN_ERROR

---

# 10. Error Response Schema

```json id="runtime03"
{
  "success":false,
  "error":{
    "code":"COMMAND_TIMEOUT",
    "severity":"ERROR",
    "message":"Command exceeded maximum execution time.",
    "recoverable":true,
    "recommendedAction":"Retry execution."
  }
}
```

---

# 11. Success Response Schema

```json id="runtime04"
{
  "success":true,
  "executionTime":3248,
  "workflowId":"wf-104",
  "taskId":"task-17",
  "status":"COMPLETED",
  "metadata":{
    "exitCode":0,
    "containerId":"ctr-204",
    "resourceUsage":{
      "cpu":"42%",
      "memory":"1.6GB"
    }
  }
}
```

---

# 12. Generic MCP Request Schema

All runtime security operations follow a common request contract.

```json id="runtime05"
{
  "requestId":"uuid",
  "workflowId":"wf-104",
  "taskId":"task-17",
  "agent":"Developer",
  "tool":"terminal",
  "action":"execute_command",
  "parameters":{
    "command":"npm test"
  }
}
```

---

# 13. Generic MCP Response Schema

```json id="runtime06"
{
  "success":true,
  "executionTime":1834,
  "data":{},
  "metadata":{
    "auditId":"audit-104",
    "eventId":"evt-812"
  }
}
```

---

# 14. Runtime Monitoring

The Runtime Security module continuously monitors:

* CPU utilization
* Memory usage
* Disk usage
* Process state
* Container health
* Network activity
* Log generation
* Timeout status
* Security policy compliance

Monitoring data is available to the Orchestrator for workflow decisions.

---

# 15. Incident Handling

When a security incident is detected:

```text id="runtime07"
Detect Incident
      │
Classify Severity
      │
Generate Event
      │
Write Audit Log
      │
Terminate or Recover
      │
Notify Orchestrator
```

Critical incidents immediately halt the affected workflow.

---

# 16. Performance Targets

| Operation                  | Target   |
| -------------------------- | -------- |
| Audit log creation         | < 20 ms  |
| Event publication          | < 10 ms  |
| Error normalization        | < 5 ms   |
| Runtime monitoring cycle   | < 100 ms |
| Security policy evaluation | < 20 ms  |

---

# 17. Security Principles

The Runtime Security module must:

* Record every security-relevant operation.
* Generate immutable audit logs.
* Publish deterministic runtime events.
* Normalize all runtime failures into structured responses.
* Prevent loss of audit data.
* Protect workflow metadata from unauthorized access.
* Fail securely under unexpected runtime conditions.
* Preserve complete traceability across every ForgeAI workflow.

---

# 18. Quality Principles

The Runtime Security subsystem should always:

* Provide complete observability into Terminal MCP and Docker MCP execution.
* Ensure every runtime action is auditable and reproducible.
* Produce consistent API contracts across all MCP tools.
* Detect and report security incidents with minimal latency.
* Integrate seamlessly with the ForgeAI Event Bus and Orchestrator.
* Support scalable concurrent workflows without compromising security.
* Maintain deterministic behavior regardless of execution environment.
* Prioritize correctness, traceability, and security over performance optimizations.

The Runtime Security module is successful when every ForgeAI terminal and Docker operation can be securely executed, continuously monitored, fully audited, and reliably integrated into the autonomous software engineering workflow while maintaining complete visibility, reproducibility, and compliance.

# SCHEMA.md (Part 4.5.1)

# Browser MCP Specification — Browser Navigation

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** Browser MCP Server

**Module:** Browser Navigation

**Version:** 1.0

**Status:** Core MCP Tool

---

# 1. Purpose

The Browser MCP enables ForgeAI agents to safely interact with web resources required during autonomous software engineering workflows.

Instead of allowing unrestricted browser automation, the Browser MCP provides a controlled interface for navigating documentation websites, retrieving technical content, extracting structured information, and supporting research tasks.

The Browser MCP is optimized for developer workflows such as:

* Reading framework documentation
* Searching API references
* Looking up library usage
* Accessing official specifications
* Retrieving technical articles
* Extracting structured webpage content

All browser operations occur through standardized MCP requests under strict security and rate-limiting policies.

---

# 2. Responsibilities

The Browser Navigation module is responsible for:

✓ Navigating web pages

✓ Loading documentation sites

✓ Searching technical documentation

✓ Extracting HTML content

✓ Extracting page metadata

✓ Tracking navigation history

✓ Normalizing extracted content

✓ Returning structured responses

✓ Publishing navigation events

✓ Recording audit logs

---

# 3. Browser Architecture

```text id="browser01"
              AI Agent
                  │
                  ▼
          AI Orchestrator
                  │
                  ▼
            Browser MCP
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
 Navigation Engine      HTML Extractor
      │                       │
      └───────────┬───────────┘
                  ▼
          Headless Browser
                  │
                  ▼
            Target Website
```

---

# 4. Supported Operations

| Operation            | Description                    |
| -------------------- | ------------------------------ |
| navigate             | Open a URL                     |
| search_documentation | Search technical documentation |
| extract_html         | Retrieve HTML source           |
| extract_metadata     | Retrieve page metadata         |
| refresh_page         | Reload current page            |
| get_page_title       | Retrieve page title            |
| get_current_url      | Retrieve active URL            |

---

# 5. Web Navigation

## Purpose

Open and load a webpage within the Browser MCP sandbox.

Operation

```text id="browser02"
navigate
```

Navigation follows a deterministic lifecycle:

```text id="browser03"
Validate Request

↓

Validate URL

↓

Open Browser

↓

Load Page

↓

Wait for DOM Ready

↓

Extract Metadata

↓

Return Response
```

---

# 6. Supported URL Types

The Browser MCP supports:

* HTTPS
* HTTP (configurable)
* Local documentation servers
* Internal documentation portals
* Static HTML resources

Unsupported protocols:

* file://
* ftp://
* ssh://
* data://
* chrome://

---

# 7. Documentation Search

## Purpose

Search official documentation for frameworks, SDKs, APIs, and programming languages.

Operation

```text id="browser04"
search_documentation
```

Typical use cases:

* React documentation
* Next.js documentation
* Python documentation
* FastAPI reference
* Docker documentation
* Kubernetes documentation
* MDN Web Docs
* GitHub Docs

---

# 8. Documentation Search Workflow

```text id="browser05"
Receive Query

↓

Select Documentation Source

↓

Execute Search

↓

Rank Results

↓

Open Matching Page

↓

Extract Content

↓

Return Structured Result
```

---

# 9. Search Parameters

Supported parameters:

* Query text
* Documentation source
* Programming language
* Framework
* Version
* Result limit
* Exact match
* Partial match

Example:

```json id="browser06"
{
  "query":"Next.js Route Handlers",
  "source":"nextjs",
  "version":"15",
  "limit":5
}
```

---

# 10. HTML Extraction

## Purpose

Retrieve the rendered HTML of the current page.

Operation

```text id="browser07"
extract_html
```

The Browser MCP returns normalized HTML after JavaScript execution when applicable.

Extraction includes:

* DOM structure
* Head section
* Body content
* Links
* Images
* Tables
* Lists
* Code blocks

Scripts and tracking elements may be removed according to security policy.

---

# 11. HTML Processing Pipeline

```text id="browser08"
Load Page

↓

Wait for Render

↓

Build DOM

↓

Normalize HTML

↓

Remove Unsafe Elements

↓

Return HTML
```

---

# 12. Metadata Extraction

Available metadata includes:

* Page title
* URL
* Canonical URL
* Description
* Language
* Charset
* Last modified
* Open Graph metadata

Example:

```json id="browser09"
{
  "title":"FastAPI Documentation",
  "url":"https://fastapi.tiangolo.com/",
  "language":"en",
  "description":"FastAPI framework documentation"
}
```

---

# 13. Request Schema

```json id="browser10"
{
  "requestId":"uuid",
  "workflowId":"wf-204",
  "taskId":"task-17",
  "agent":"Architect",
  "tool":"browser",
  "action":"navigate",
  "parameters":{
    "url":"https://nextjs.org/docs"
  }
}
```

---

# 14. Documentation Search Request

```json id="browser11"
{
  "requestId":"uuid",
  "workflowId":"wf-204",
  "agent":"Developer",
  "tool":"browser",
  "action":"search_documentation",
  "parameters":{
    "query":"React Suspense",
    "source":"react",
    "limit":10
  }
}
```

---

# 15. Response Schema

```json id="browser12"
{
  "success":true,
  "executionTime":1342,
  "data":{
    "title":"React Suspense",
    "url":"https://react.dev/reference/react/Suspense"
  },
  "metadata":{
    "statusCode":200,
    "contentType":"text/html"
  }
}
```

---

# 16. HTML Response Schema

```json id="browser13"
{
  "success":true,
  "data":{
    "url":"https://nextjs.org/docs",
    "title":"Next.js Documentation",
    "html":"<html>...</html>"
  }
}
```

---

# 17. Validation Rules

Every browser request validates:

* Authenticated workflow
* Authorized agent
* Valid URL format
* Supported protocol
* Allowed domain policy
* Maximum request size
* Search query length
* Action type
* Browser session availability

Invalid requests are rejected before navigation.

---

# 18. Error Codes

INVALID_URL

UNSUPPORTED_PROTOCOL

PAGE_NOT_FOUND

NAVIGATION_TIMEOUT

DOCUMENTATION_NOT_FOUND

INVALID_SEARCH_QUERY

ACCESS_DENIED

RATE_LIMIT_EXCEEDED

BROWSER_SESSION_FAILED

HTML_EXTRACTION_FAILED

UNKNOWN_BROWSER_ERROR

---

# 19. Navigation Events

The Browser MCP publishes:

BROWSER_STARTED

NAVIGATION_STARTED

PAGE_LOADED

DOCUMENTATION_SEARCH_STARTED

DOCUMENTATION_SEARCH_COMPLETED

HTML_EXTRACTION_COMPLETED

NAVIGATION_FAILED

BROWSER_CLOSED

---

# 20. Audit Logging

Every browser operation records:

* Workflow ID
* Task ID
* Agent
* URL
* Operation
* Execution time
* HTTP status
* Result
* Timestamp

Example:

```json id="browser14"
{
  "tool":"Browser MCP",
  "operation":"navigate",
  "workflowId":"wf-204",
  "url":"https://react.dev",
  "status":"SUCCESS"
}
```

---

# 21. Performance Targets

| Operation            | Target   |
| -------------------- | -------- |
| Browser startup      | < 2 s    |
| Page navigation      | < 5 s    |
| Documentation search | < 3 s    |
| HTML extraction      | < 1 s    |
| Metadata extraction  | < 250 ms |

---

# 22. Design Principles

The Browser Navigation module should always:

* Use secure, sandboxed browser sessions.
* Provide deterministic navigation behavior.
* Prioritize official documentation sources.
* Return normalized HTML and metadata.
* Validate all navigation requests before execution.
* Maintain complete audit trails for browser activity.
* Support structured request and response contracts.
* Integrate seamlessly with the ForgeAI Orchestrator and other MCP tools.

The Browser Navigation module is successful when ForgeAI agents can reliably navigate documentation websites, retrieve structured technical content, and perform web-based research through secure, observable, and reproducible browser interactions.

# SCHEMA.md (Part 4.5.2)

# Browser MCP Specification — Browser Runtime

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** Browser MCP Server

**Module:** Browser Runtime

**Version:** 1.0

**Status:** Core MCP Module

---

# 1. Purpose

The Browser Runtime module manages the execution environment for all browser-based operations performed by ForgeAI agents. It is responsible for screenshot generation, safe browsing enforcement, rate limiting, runtime events, audit logging, standardized error handling, and secure API contracts.

Unlike the Browser Navigation module, which focuses on navigation and content retrieval, the Runtime module ensures that browser sessions remain secure, observable, and compliant throughout execution.

---

# 2. Responsibilities

The Browser Runtime is responsible for:

✓ Screenshot capture

✓ Browser session management

✓ Safe browsing enforcement

✓ Rate limiting

✓ Runtime monitoring

✓ Event publication

✓ Audit logging

✓ Error normalization

✓ API contract enforcement

---

# 3. Screenshot Support

The Browser MCP supports deterministic screenshot capture of rendered web pages.

Supported capture modes:

* Full page
* Viewport
* Element-specific (future)
* Documentation section (future)

Screenshot workflow:

```text id="browserrt01"
Navigate

↓

Wait for DOM Ready

↓

Wait for Network Idle

↓

Capture Screenshot

↓

Compress Image

↓

Store Artifact

↓

Return Reference
```

Supported formats:

* PNG (default)
* JPEG
* WebP (future)

---

# 4. Screenshot Metadata

Each screenshot includes:

* Screenshot ID
* Workflow ID
* Page URL
* Resolution
* Format
* Capture timestamp
* Browser version
* Render time

Example:

```json id="browserrt02"
{
  "screenshotId":"img-204",
  "url":"https://react.dev",
  "format":"png",
  "resolution":"1920x1080",
  "timestamp":"2026-07-06T15:30:00Z"
}
```

---

# 5. Safe Browsing Rules

The Browser Runtime follows a **default-deny** browsing policy.

Allowed destinations:

* Official framework documentation
* API documentation
* Public Git repositories
* Developer blogs (approved)
* Standards organizations
* Organization-approved domains

Blocked destinations:

* Malware domains
* Phishing sites
* Adult content
* Cryptocurrency mining sites
* Unauthorized file sharing
* Unknown executable downloads

Navigation requests violating policy are rejected before page loading.

---

# 6. Browser Session Policies

Each workflow receives:

* One isolated browser session
* Independent cookies
* Separate cache
* Separate local storage
* Independent navigation history

Sessions are destroyed after workflow completion.

---

# 7. Rate Limiting

To protect external services and prevent abuse, Browser MCP enforces request quotas.

Default limits:

| Operation            |              Limit |
| -------------------- | -----------------: |
| Navigation           | 60 requests/minute |
| Documentation search |   120 queries/hour |
| Screenshot capture   |   30 captures/hour |
| HTML extraction      |  120 requests/hour |

Exceeding limits returns a structured `RATE_LIMIT_EXCEEDED` error.

---

# 8. Runtime Events

The Browser Runtime publishes the following events:

BROWSER_STARTED

SESSION_CREATED

PAGE_NAVIGATION_STARTED

PAGE_NAVIGATION_COMPLETED

SCREENSHOT_CAPTURED

HTML_EXTRACTED

RATE_LIMIT_TRIGGERED

SECURITY_POLICY_TRIGGERED

SESSION_CLOSED

BROWSER_RUNTIME_COMPLETED

BROWSER_RUNTIME_FAILED

---

# 9. Event Schema

```json id="browserrt03"
{
  "eventId":"evt-420",
  "type":"SCREENSHOT_CAPTURED",
  "workflowId":"wf-204",
  "timestamp":"2026-07-06T15:31:08Z",
  "payload":{
    "url":"https://nextjs.org/docs",
    "format":"png"
  }
}
```

Events are published asynchronously to the ForgeAI Event Bus.

---

# 10. Audit Logging

Every browser runtime operation produces an immutable audit record.

Recorded fields:

* Audit ID
* Workflow ID
* Task ID
* Agent
* Browser session ID
* URL
* Operation
* HTTP status
* Execution time
* Result
* Timestamp

Example:

```json id="browserrt04"
{
  "auditId":"audit-420",
  "tool":"Browser MCP",
  "operation":"capture_screenshot",
  "workflowId":"wf-204",
  "status":"SUCCESS",
  "executionTime":812
}
```

Audit records are retained according to ForgeAI retention policies.

---

# 11. Error Handling

Runtime failures are normalized into structured responses.

Common error codes:

INVALID_URL

NAVIGATION_TIMEOUT

PAGE_NOT_FOUND

SCREENSHOT_FAILED

HTML_EXTRACTION_FAILED

SESSION_CREATION_FAILED

RATE_LIMIT_EXCEEDED

SECURITY_POLICY_VIOLATION

NETWORK_UNAVAILABLE

BROWSER_CRASHED

UNKNOWN_BROWSER_ERROR

Every error includes:

* Code
* Severity
* Message
* Recoverable flag
* Recommended action

---

# 12. API Request Schema

```json id="browserrt05"
{
  "requestId":"uuid",
  "workflowId":"wf-204",
  "taskId":"task-18",
  "agent":"Architect",
  "tool":"browser",
  "action":"capture_screenshot",
  "parameters":{
    "url":"https://react.dev",
    "mode":"full-page"
  }
}
```

---

# 13. API Success Response

```json id="browserrt06"
{
  "success":true,
  "executionTime":1432,
  "data":{
    "artifactId":"img-204",
    "format":"png"
  },
  "metadata":{
    "sessionId":"session-17",
    "resolution":"1920x1080"
  }
}
```

---

# 14. API Error Response

```json id="browserrt07"
{
  "success":false,
  "error":{
    "code":"RATE_LIMIT_EXCEEDED",
    "severity":"WARNING",
    "message":"Navigation quota exceeded.",
    "recoverable":true,
    "recommendedAction":"Retry after cooldown period."
  }
}
```

---

# 15. Runtime Monitoring

The Browser Runtime continuously monitors:

* Session health
* Page load duration
* Network latency
* Browser memory usage
* Screenshot execution
* HTML extraction success
* Security policy compliance
* Rate limit usage

---

# 16. Performance Targets

| Operation           | Target   |
| ------------------- | -------- |
| Browser startup     | < 2 s    |
| Screenshot capture  | < 1 s    |
| Session creation    | < 500 ms |
| Event publication   | < 20 ms  |
| Audit log creation  | < 20 ms  |
| Error normalization | < 5 ms   |

---

# 17. Security Principles

The Browser Runtime must:

* Restrict navigation to approved domains.
* Isolate browser sessions between workflows.
* Prevent unauthorized downloads and file execution.
* Block unsafe URLs before navigation.
* Protect cookies and session data.
* Record all security-relevant browser actions.
* Enforce rate limits consistently.
* Fail securely under unexpected runtime conditions.

---

# 18. Quality Principles

The Browser Runtime should always:

* Provide deterministic browser behavior.
* Maintain isolated and disposable browser sessions.
* Produce complete audit trails and runtime events.
* Normalize runtime errors into consistent API responses.
* Support reproducible browser automation across platforms.
* Integrate seamlessly with the ForgeAI Orchestrator and Event Bus.
* Prioritize security, observability, and reliability over raw performance.
* Deliver stable browser execution for autonomous software engineering workflows.

The Browser Runtime module is successful when ForgeAI agents can safely browse documentation, capture visual artifacts, extract web content, and interact with approved online resources through secure, observable, and reproducible browser sessions while maintaining strict security policies and operational reliability.

# SCHEMA.md (Part 5.1)

# WebSocket Protocol Specification

**Project:** ForgeAI — Autonomous Software Engineering Team

**Component:** Real-Time Communication Layer

**Module:** WebSocket Protocol

**Version:** 1.0

**Status:** Core Infrastructure

---

# 1. Purpose

The WebSocket Protocol provides ForgeAI with a persistent, bidirectional communication channel between the frontend, backend, AI Orchestrator, MCP servers, and autonomous agents.

Unlike REST APIs, which are request-response based, WebSockets enable real-time streaming of workflow progress, agent execution, logs, notifications, runtime events, and live collaboration.

Every workflow execution uses WebSockets as its primary communication protocol.

---

# 2. Responsibilities

The WebSocket Protocol is responsible for:

✓ Persistent connections

✓ Real-time event streaming

✓ Agent communication

✓ Workflow updates

✓ Task progress

✓ Runtime notifications

✓ Log streaming

✓ Session synchronization

✓ Connection recovery

✓ Message delivery guarantees

---

# 3. High-Level Architecture

```text
                Frontend
                    │
         Secure WebSocket (WSS)
                    │
                    ▼
          WebSocket Gateway
                    │
      ┌─────────────┴─────────────┐
      ▼                           ▼
 AI Orchestrator            Event Broker
      │                           │
      └─────────────┬─────────────┘
                    ▼
             MCP Services
```

The WebSocket Gateway acts as the central routing hub for all real-time communication.

---

# 4. Supported Communication Types

The protocol supports:

* Client → Server
* Server → Client
* Agent → Orchestrator
* MCP → Orchestrator
* Orchestrator → UI
* Broadcast events
* Targeted events

---

# 5. Connection Lifecycle

Every WebSocket connection follows a deterministic lifecycle.

```text
CONNECT_REQUEST

↓

AUTHENTICATION

↓

SESSION_CREATION

↓

CONNECTION_ESTABLISHED

↓

EVENT_STREAMING

↓

HEARTBEAT

↓

DISCONNECT

↓

SESSION_CLOSED
```

Unexpected failures trigger automatic reconnection.

---

# 6. Connection States

| State          | Description                  |
| -------------- | ---------------------------- |
| CONNECTING     | Handshake in progress        |
| AUTHENTICATING | Credentials being verified   |
| CONNECTED      | Active session               |
| RECONNECTING   | Recovering from interruption |
| DISCONNECTED   | Connection closed            |
| FAILED         | Connection failed            |

---

# 7. Authentication

Authentication occurs before any messages are exchanged.

Supported methods:

* JWT Access Token
* OAuth Bearer Token
* API Token (server-to-server)
* Development Mode Token

Authentication flow:

```text
Client Connect

↓

Token Validation

↓

Permission Check

↓

Session Creation

↓

Connection Accepted
```

Unauthenticated connections are immediately rejected.

---

# 8. Session Management

Each WebSocket session stores:

* Session ID
* User ID
* Workflow ID
* Connected Agents
* Active Subscriptions
* Connection Timestamp
* Last Heartbeat
* Client Version

Sessions expire automatically after inactivity.

---

# 9. Heartbeat

Heartbeat packets verify connection health.

Default interval:

30 seconds

If three consecutive heartbeats are missed:

* Session marked inactive
* Resources released
* Client notified
* Reconnection allowed

---

# 10. Message Envelope

Every WebSocket message follows a standardized envelope.

```json
{
  "messageId":"uuid",
  "timestamp":"2026-07-06T18:00:00Z",
  "workflowId":"wf-104",
  "taskId":"task-12",
  "source":"PlannerAgent",
  "destination":"Frontend",
  "type":"WORKFLOW_EVENT",
  "payload":{}
}
```

The envelope provides consistent routing and observability across all services.

---

# 11. Message Types

Supported message types:

* WORKFLOW_EVENT
* TASK_EVENT
* AGENT_EVENT
* MCP_EVENT
* LOG_EVENT
* NOTIFICATION
* SYSTEM_EVENT
* ERROR_EVENT
* HEARTBEAT
* RESPONSE

---

# 12. Event Routing

The WebSocket Gateway routes events based on destination.

Routing modes:

### Direct

Single recipient.

### Broadcast

All subscribed clients.

### Workflow

All clients participating in a workflow.

### Agent

Specific AI agent.

### MCP

Specific MCP service.

---

Routing example:

```text
Developer Agent

↓

Event Broker

↓

Workflow Channel

↓

Frontend Dashboard
```

---

# 13. Channel Model

Standard channels:

```text
/workflow/{workflowId}

/task/{taskId}

/agent/{agentId}

/system

/logs

/notifications
```

Clients subscribe only to authorized channels.

---

# 14. Request Schema

Client request:

```json
{
  "requestId":"uuid",
  "action":"subscribe",
  "channel":"/workflow/wf-104",
  "parameters":{}
}
```

---

# 15. Success Response Schema

```json
{
  "success":true,
  "requestId":"uuid",
  "channel":"/workflow/wf-104",
  "status":"SUBSCRIBED"
}
```

---

# 16. Event Response Schema

```json
{
  "messageId":"uuid",
  "type":"TASK_EVENT",
  "workflowId":"wf-104",
  "taskId":"task-12",
  "payload":{
    "status":"RUNNING",
    "progress":65
  }
}
```

---

# 17. Error Response Schema

```json
{
  "success":false,
  "error":{
    "code":"UNAUTHORIZED_CHANNEL",
    "message":"Subscription denied."
  }
}
```

---

# 18. Validation Rules

The WebSocket Gateway validates:

* Authentication token
* Active session
* Workflow membership
* Channel authorization
* Message size
* Payload schema
* Protocol version
* Rate limits

Invalid messages are rejected before routing.

---

# 19. Error Codes

AUTHENTICATION_FAILED

INVALID_SESSION

INVALID_CHANNEL

UNAUTHORIZED_CHANNEL

INVALID_MESSAGE

MESSAGE_TOO_LARGE

RATE_LIMIT_EXCEEDED

PROTOCOL_VERSION_MISMATCH

HEARTBEAT_TIMEOUT

UNKNOWN_ERROR

---

# 20. Performance Targets

| Operation                | Target   |
| ------------------------ | -------- |
| Connection establishment | < 500 ms |
| Authentication           | < 100 ms |
| Event routing            | < 20 ms  |
| Heartbeat processing     | < 10 ms  |
| Message delivery         | < 50 ms  |

---

# 21. Security Principles

The WebSocket Protocol must:

* Require authentication before communication.
* Encrypt all traffic using WSS.
* Authorize every channel subscription.
* Validate every message against its schema.
* Prevent unauthorized event routing.
* Isolate workflow channels.
* Protect against replay and malformed-message attacks.
* Maintain complete auditability of connections and events.

---

# 22. Quality Principles

The WebSocket Protocol should always:

* Provide reliable real-time communication.
* Support deterministic message delivery.
* Scale to thousands of concurrent workflow events.
* Recover gracefully from temporary connection failures.
* Maintain protocol compatibility through versioned schemas.
* Integrate seamlessly with the ForgeAI Orchestrator, Event Bus, MCP services, and frontend.
* Minimize latency while preserving message integrity.
* Deliver secure, observable, and resilient communication across all autonomous software engineering workflows.

The WebSocket Protocol is successful when every ForgeAI component can exchange real-time events, workflow updates, and execution data through authenticated, low-latency, and fault-tolerant communication channels.

SCHEMA.md — Part 5.2 Event Schemas
> **Project:** ForgeAI — Autonomous Software Engineering Team  
> **Component:** Event Bus & Real-Time Messaging  
> **Module:** Event Schemas  
> **Version:** 1.0
---
Purpose
ForgeAI uses an event-driven architecture to coordinate communication between the Orchestrator, AI Agents, MCP servers, frontend, backend, and external integrations.
All events follow a standardized envelope and are immutable after publication.
---
Base Event Schema
```json
{
  "eventId": "evt-uuid",
  "eventType": "WORKFLOW_STARTED",
  "version": "1.0",
  "timestamp": "2026-07-06T18:30:00Z",
  "workflowId": "wf-001",
  "taskId": "task-001",
  "agentId": "planner-001",
  "source": "PlannerAgent",
  "target": "Orchestrator",
  "correlationId": "corr-001",
  "causationId": "evt-parent",
  "severity": "INFO",
  "payload": {}
}
```
---
Workflow Events
Lifecycle:
WORKFLOW_CREATED
WORKFLOW_STARTED
WORKFLOW_PAUSED
WORKFLOW_RESUMED
WORKFLOW_CANCELLED
WORKFLOW_COMPLETED
WORKFLOW_FAILED
WORKFLOW_ARCHIVED
Example payload:
```json
{
  "eventType":"WORKFLOW_STARTED",
  "payload":{
    "workflowName":"Implement Feature",
    "repository":"forgeai",
    "initiator":"user"
  }
}
```
---
Agent Events
Supported events:
AGENT_CREATED
AGENT_INITIALIZED
AGENT_ASSIGNED
AGENT_STARTED
AGENT_PROGRESS
AGENT_WAITING
AGENT_RETRYING
AGENT_COMPLETED
AGENT_FAILED
AGENT_STOPPED
Payload example:
```json
{
  "eventType":"AGENT_PROGRESS",
  "payload":{
    "agent":"Developer",
    "progress":67,
    "currentTask":"Implement authentication"
  }
}
```
---
Task Events
Lifecycle:
TASK_CREATED
TASK_QUEUED
TASK_ASSIGNED
TASK_STARTED
TASK_PROGRESS
TASK_BLOCKED
TASK_RETRY
TASK_COMPLETED
TASK_FAILED
TASK_CANCELLED
Payload example:
```json
{
  "eventType":"TASK_COMPLETED",
  "payload":{
    "taskId":"task-17",
    "durationMs":52341,
    "status":"SUCCESS"
  }
}
```
---
MCP Events
Supported events:
MCP_CONNECTED
MCP_DISCONNECTED
MCP_REQUEST_SENT
MCP_RESPONSE_RECEIVED
MCP_TIMEOUT
MCP_ERROR
MCP_RETRY
MCP_OPERATION_COMPLETED
Payload example:
```json
{
  "eventType":"MCP_REQUEST_SENT",
  "payload":{
    "server":"GitHub MCP",
    "operation":"create_pull_request"
  }
}
```
---
User Events
Supported events:
USER_LOGIN
USER_LOGOUT
USER_CONNECTED
USER_DISCONNECTED
USER_APPROVAL_REQUIRED
USER_APPROVED
USER_REJECTED
USER_NOTIFICATION_SENT
Payload example:
```json
{
  "eventType":"USER_APPROVED",
  "payload":{
    "approvalType":"Merge Pull Request",
    "decision":"APPROVED"
  }
}
```
---
System Events
Supported events:
SYSTEM_STARTUP
SYSTEM_READY
SYSTEM_WARNING
SYSTEM_ERROR
SYSTEM_SHUTDOWN
CACHE_REFRESHED
CONFIG_UPDATED
HEALTH_CHECK_PASSED
HEALTH_CHECK_FAILED
Payload example:
```json
{
  "eventType":"SYSTEM_WARNING",
  "payload":{
    "component":"Docker MCP",
    "message":"Memory usage above threshold"
  }
}
```
---
Validation Rules
Every event must include:
eventId
eventType
version
timestamp
workflowId (if applicable)
source
payload
Rules:
UUID identifiers only
ISO-8601 timestamps
Immutable payloads
Versioned schemas
Unknown fields ignored by older clients
Events are append-only
---
Error Event
```json
{
  "eventType":"SYSTEM_ERROR",
  "payload":{
    "code":"MCP_TIMEOUT",
    "message":"GitHub MCP request timed out",
    "recoverable":true
  }
}
```
---
Design Principles
Immutable events
Versioned contracts
Correlation IDs for traceability
Event sourcing compatible
Asynchronous delivery
Idempotent consumers
Schema validation before publication
Complete auditability
Backward-compatible evolution
This specification forms the canonical event contract for all ForgeAI services.

SCHEMA.md — Part 5.3 Logging & Notifications
Project
ForgeAI — Autonomous Software Engineering Team
Component
Observability Layer
Version
1.0
---
Purpose
The Logging & Notifications subsystem provides end-to-end observability for ForgeAI by collecting runtime telemetry, maintaining immutable audit records, reporting errors, and delivering real-time notifications and alerts.
Goals:
Full traceability
Operational visibility
Security auditing
Incident response
User notifications
Compliance support
---
5.3.1 Runtime Logs
Runtime logs capture live execution from workflows, agents, MCP servers, Docker containers, Browser MCP, Terminal MCP, and the Orchestrator.
Log Levels
TRACE
DEBUG
INFO
WARNING
ERROR
CRITICAL
Runtime Log Schema
```json
{
  "logId":"log-001",
  "timestamp":"2026-07-06T18:00:00Z",
  "workflowId":"wf-001",
  "taskId":"task-004",
  "agent":"Developer",
  "component":"Terminal MCP",
  "level":"INFO",
  "message":"Running unit tests",
  "metadata":{
    "executionTimeMs":352
  }
}
```
Retention:
Live stream: immediate
Persistent logs: configurable
Searchable by workflow, task, agent, component, severity
---
5.3.2 Audit Logs
Audit logs are immutable records of security-sensitive operations.
Tracked actions:
User authentication
Workflow creation/deletion
Agent execution
MCP requests
File modifications
Git operations
Deployment actions
Security violations
Permission changes
Audit Schema
```json
{
  "auditId":"audit-001",
  "timestamp":"2026-07-06T18:01:00Z",
  "actor":"DeveloperAgent",
  "action":"CREATE_PULL_REQUEST",
  "resource":"repository",
  "workflowId":"wf-001",
  "status":"SUCCESS",
  "ip":"internal",
  "details":{}
}
```
Properties:
Immutable
Digitally attributable
Chronological
Queryable
Exportable
---
5.3.3 Notification Schemas
Notifications communicate important events to users and administrators.
Notification types:
Workflow Complete
Workflow Failed
Human Approval Required
Pull Request Ready
Deployment Complete
Security Warning
System Maintenance
Agent Mention
Notification Schema
```json
{
  "notificationId":"notif-001",
  "type":"WORKFLOW_COMPLETED",
  "recipient":"user-001",
  "title":"Workflow Finished",
  "message":"Authentication feature completed successfully.",
  "severity":"INFO",
  "timestamp":"2026-07-06T18:05:00Z",
  "read":false,
  "actions":[
    {
      "label":"Open Workflow",
      "action":"OPEN_WORKFLOW"
    }
  ]
}
```
Delivery channels:
In-app
WebSocket
Email (future)
Mobile Push (future)
Slack/Teams (future)
---
5.3.4 Error Reporting
Errors are standardized across all services.
Severity:
INFO
WARNING
ERROR
CRITICAL
Error Schema
```json
{
  "errorId":"err-001",
  "code":"MCP_TIMEOUT",
  "message":"GitHub MCP request timed out.",
  "severity":"ERROR",
  "recoverable":true,
  "workflowId":"wf-001",
  "component":"GitHub MCP",
  "stackTrace":"optional",
  "timestamp":"2026-07-06T18:06:00Z"
}
```
Lifecycle:
Detect
Normalize
Log
Publish event
Notify (if required)
Recover or terminate
---
5.3.5 Alerting
Alerts represent actionable operational incidents.
Alert categories:
Security
Infrastructure
Performance
Runtime Failure
Deployment
Resource Limits
External Service Failure
Priority:
LOW
MEDIUM
HIGH
CRITICAL
Alert Schema
```json
{
  "alertId":"alert-001",
  "priority":"HIGH",
  "category":"RESOURCE_LIMIT",
  "title":"Memory Limit Exceeded",
  "description":"Developer container exceeded memory quota.",
  "workflowId":"wf-001",
  "status":"OPEN",
  "createdAt":"2026-07-06T18:07:00Z"
}
```
Alert lifecycle:
OPEN → ACKNOWLEDGED → INVESTIGATING → RESOLVED → CLOSED
---
Validation Rules
Every log, notification, error, and alert must include:
UUID identifier
ISO-8601 timestamp
Severity or priority
Origin component
Version-compatible payload
---
Design Principles
Structured JSON records
Immutable audit history
Real-time streaming
Correlation via workflow and task IDs
Low-latency notifications
Centralized observability
Backward-compatible schemas
Secure storage and access control

SCHEMA.md — Part 5.4 Analytics & Telemetry
Project
ForgeAI — Autonomous Software Engineering Team
Component
Analytics & Telemetry Platform
Version
1.0
---
Purpose
The Analytics & Telemetry subsystem provides continuous measurement of ForgeAI's operational health, AI agent performance, workflow efficiency, infrastructure utilization, and user adoption. All telemetry is collected using structured, versioned schemas and is designed to support dashboards, reporting, optimization, and capacity planning.
---
5.4.1 Metrics
Categories
Workflow Metrics
Task Metrics
Agent Metrics
MCP Metrics
Runtime Metrics
User Metrics
System Metrics
Common Metric Schema
```json
{
  "metricId":"metric-001",
  "timestamp":"2026-07-06T19:00:00Z",
  "category":"WORKFLOW",
  "name":"workflow_duration_ms",
  "value":84523,
  "unit":"ms",
  "workflowId":"wf-001",
  "tags":{
    "environment":"production",
    "repository":"forgeai"
  }
}
```
Common KPIs:
Workflow success rate
Average execution time
Average task duration
Error rate
Agent utilization
MCP latency
API response time
Build duration
Test pass rate
---
5.4.2 Performance Analytics
Performance analytics identify bottlenecks and optimize execution.
Tracked metrics:
Workflow latency
Task queue wait time
Agent execution time
Docker startup time
Browser load time
GitHub MCP latency
Filesystem throughput
CPU utilization
Memory usage
Disk usage
Example:
```json
{
  "analysisType":"PERFORMANCE",
  "workflowId":"wf-001",
  "executionTimeMs":84523,
  "cpuAverage":41.8,
  "memoryPeakMb":1854,
  "bottleneck":"DeveloperAgent"
}
```
---
5.4.3 Agent Analytics
Measures effectiveness of every autonomous agent.
Metrics:
Tasks completed
Average completion time
Retry count
Failure rate
Token usage
Tool invocations
Approval requests
Quality score
Review score
Success percentage
Schema:
```json
{
  "agentId":"developer-01",
  "agentType":"Developer",
  "completedTasks":214,
  "averageExecutionMs":21453,
  "failureRate":0.03,
  "toolCalls":1324,
  "qualityScore":94.8
}
```
---
5.4.4 Usage Analytics
Tracks user interaction with ForgeAI.
Captured data:
Active users
Sessions
Workflow creation
Feature usage
MCP usage
Dashboard views
Notification interactions
Search queries
Repository connections
Schema:
```json
{
  "userId":"user-001",
  "sessionId":"session-010",
  "event":"CREATE_WORKFLOW",
  "timestamp":"2026-07-06T19:05:00Z",
  "metadata":{
    "project":"ForgeAI",
    "platform":"Web"
  }
}
```
Privacy principles:
Collect minimum required data
No secrets in analytics
Configurable retention
Role-based access
---
5.4.5 Dashboard Schemas
Dashboards aggregate telemetry for visualization.
Workflow Dashboard
Running workflows
Completed workflows
Failed workflows
Queue depth
Success rate
Agent Dashboard
Active agents
Agent health
Agent utilization
Task distribution
Quality scores
Infrastructure Dashboard
CPU
Memory
Disk
Network
Docker containers
MCP availability
User Dashboard
Active sessions
Daily users
Notifications
Approvals pending
Dashboard Schema:
```json
{
  "dashboardId":"ops-main",
  "generatedAt":"2026-07-06T19:10:00Z",
  "widgets":[
    {
      "type":"metric",
      "title":"Workflow Success Rate",
      "value":98.7,
      "unit":"%"
    },
    {
      "type":"chart",
      "title":"Agent Execution Time",
      "source":"agent_execution_ms"
    }
  ]
}
```
---
Validation Rules
Every telemetry record must include:
UUID identifier
ISO-8601 timestamp
Metric category
Version-compatible payload
Source component
Numeric values with units where applicable
---
Design Principles
Structured JSON telemetry
Low-overhead collection
Immutable historical metrics
Real-time streaming support
Correlation using workflow, task, and agent IDs
Extensible metric catalog
Privacy-aware analytics
Dashboard-first data modeling
Backward-compatible schema evolution

SCHEMA.md — Part 5.5 Schema Evolution
Project
ForgeAI — Autonomous Software Engineering Team
Component
Schema Governance & Evolution
Version
1.0
---
Purpose
The Schema Evolution framework defines how ForgeAI data contracts evolve over time while preserving stability, interoperability, and backward compatibility across clients, services, AI agents, MCP servers, APIs, and persistent storage.
Objectives:
Stable contracts
Predictable upgrades
Backward compatibility
Controlled breaking changes
Safe migrations
Long-term maintainability
---
5.5.1 Versioning
ForgeAI uses semantic versioning for all schemas.
Format:
MAJOR.MINOR.PATCH
Rules:
MAJOR: Breaking changes
MINOR: Backward-compatible additions
PATCH: Documentation or non-breaking fixes
Example:
```json
{
  "schema":"WorkflowEvent",
  "version":"2.1.0"
}
```
Every schema must include:
schemaName
version
generatedAt
compatibilityLevel
---
5.5.2 Compatibility
Compatibility goals:
Older clients continue functioning
New clients understand older payloads
Unknown fields ignored
Required fields remain stable within a major version
Compatibility matrix
Producer	Consumer	Supported
v1	v1	Yes
v2	v2	Yes
v2	v1	Additive fields only
v1	v2	Yes
v3	v1	Only if compatibility layer exists
Rules:
Never reuse field names with different meanings.
Preserve identifiers across versions.
Add fields as optional before making them required.
Remove fields only in a new major version.
---
5.5.3 Migration Strategy
Schema migrations follow four phases.
Introduce
Add new schema version
Keep previous version active
Dual Support
Read old and new payloads
Write latest version
Migration
Convert stored records
Validate transformed data
Monitor adoption
Retirement
Disable obsolete version
Archive migration reports
Migration metadata:
```json
{
  "migrationId":"mig-001",
  "fromVersion":"1.4.0",
  "toVersion":"2.0.0",
  "status":"COMPLETED",
  "recordsMigrated":14205,
  "startedAt":"2026-07-06T20:00:00Z"
}
```
---
5.5.4 Deprecation Policy
Every deprecated field must include:
Deprecated version
Planned removal version
Replacement field
Migration guidance
Example:
```json
{
  "field":"executionStatus",
  "deprecatedIn":"2.2.0",
  "removedIn":"3.0.0",
  "replacement":"status"
}
```
Deprecation lifecycle:
ANNOUNCED
↓
DEPRECATED
↓
WARNING EMITTED
↓
READ-ONLY SUPPORT
↓
REMOVED
Policy:
Minimum one major release before removal
Publish migration notes
Provide automated migration where possible
---
5.5.5 Future Extensions
Planned areas:
Multi-tenant schemas
Distributed event sourcing
Cross-region replication
GraphQL schema generation
OpenTelemetry integration
AI memory schemas
Plugin-defined extensions
Custom MCP contracts
Schema registry
Automatic code generation
JSON Schema & OpenAPI export
Protocol Buffers support
Avro support
Event replay support
Extension model:
```json
{
  "extensionId":"ext-ai-memory",
  "targetSchema":"AgentExecution",
  "version":"1.0.0",
  "status":"experimental"
}
```
---
Governance
All schema changes require:
Design review
Compatibility assessment
Version increment
Documentation update
Migration plan
Automated validation
Regression testing
---
Validation Rules
Every schema version must define:
Unique name
Semantic version
Owner
Change history
Compatibility guarantees
Validation rules
Example payload
---
Design Principles
Schema-first development
Backward compatibility by default
Explicit versioning
Immutable historical contracts
Automated validation
Safe incremental evolution
Transparent migration guidance
Extensible architecture
Stable long-term API contracts
This Schema Evolution specification establishes the governance model for every ForgeAI contract, ensuring the platform can evolve without disrupting autonomous agents, services, integrations, or user workflows.