import { apiClient } from "@/lib/api-client"

export interface WorkflowStatus {
  id: string
  title: string
  status: string
  user_request: string | null
  task_count: number
  completed_tasks: number
  updated_at: string
}

export interface ExecutionPlanTask {
  order: number
  title: string
  description: string
  agent_type: string
  priority: number
  dependencies: string[]
}

export interface ExecutionPlanPhase {
  id: string
  name: string
  description: string
  agents: string[]
}

export interface ExecutionPlan {
  id: string
  workflow_id: string
  objective: string
  scope: string
  assumptions: string[]
  risks: string[]
  estimated_complexity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
  phases: ExecutionPlanPhase[]
  ordered_tasks: ExecutionPlanTask[]
  recommended_agents: string[]
  created_at: string
}

export interface AgentInfo {
  agent_type: string
  active: boolean
  description: string
}

export interface WorkflowEvent {
  id: string
  agent_type: string
  level: string
  message: string
  metadata: Record<string, unknown>
  created_at: string
}

export async function getWorkflows(): Promise<WorkflowStatus[]> {
  return apiClient('/workflows')
}

export async function getWorkflowStatus(workflowId: string): Promise<WorkflowStatus> {
  return apiClient(`/workflows/${workflowId}/status`)
}

export async function getWorkflowPlan(workflowId: string): Promise<ExecutionPlan> {
  return apiClient(`/workflows/${workflowId}/plan`)
}

export async function triggerPlan(
  workflowId: string,
  projectId: string,
  userRequest: string
): Promise<{ message: string; workflow_id: string; status: string }> {
  return apiClient(`/workflows/${workflowId}/plan`, {
    method: "POST",
    body: JSON.stringify({ project_id: projectId, user_request: userRequest }),
  })
}

export async function getWorkflowEvents(workflowId: string): Promise<{ events: WorkflowEvent[] }> {
  return apiClient(`/workflows/${workflowId}/events`)
}

export async function getAgentRegistry(): Promise<AgentInfo[]> {
  return apiClient(`/workflows/agents/registry`)
}
