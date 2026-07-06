import { apiClient } from "@/lib/api-client"

export interface Repository {
  id: string
  project_id: string
  provider: string
  remote_url: string | null
  default_branch: string
  local_path: string | null
  is_connected: boolean
  last_sync: string | null
  created_at: string
  updated_at: string
}

export interface RepositoryOverview {
  file_count: number
  languages: string[]
  frameworks: string[]
  architecture_patterns: string[]
  architecture_summary: string
  key_components: string[]
}

export interface RepositoryTreeFile {
  path: string
  type: string
}

export interface KnowledgeNode {
  name: string
  type: string
  path: string | null
}

export interface ArchitectureReport {
  analysis: {
    languages: string[]
    frameworks: string[]
    package_managers: string[]
    architecture_patterns: string[]
    architecture_summary: string
  }
  knowledge_nodes: KnowledgeNode[]
}

export interface SearchResult {
  id: string
  file_path: string
  file_type: string
  size_bytes: number
}

export async function getRepositoriesByProject(projectId: string): Promise<Repository[]> {
  return apiClient(`/projects/${projectId}/repositories`)
}

export async function connectRepository(repositoryId: string): Promise<{ message: string }> {
  return apiClient(`/repositories/${repositoryId}/connect`, { method: "POST" })
}

export async function getRepositoryOverview(repositoryId: string): Promise<RepositoryOverview> {
  return apiClient(`/repositories/${repositoryId}/overview`)
}

export async function getRepositoryTree(repositoryId: string): Promise<{ files: RepositoryTreeFile[] }> {
  return apiClient(`/repositories/${repositoryId}/tree`)
}

export async function searchRepository(repositoryId: string, query: string): Promise<SearchResult[]> {
  return apiClient(`/repositories/${repositoryId}/search?q=${encodeURIComponent(query)}`)
}

export async function getArchitectureReport(repositoryId: string): Promise<ArchitectureReport> {
  return apiClient(`/repositories/${repositoryId}/architecture`)
}

export async function generateCode(repositoryId: string, task: string): Promise<any> {
  return apiClient(`/repositories/${repositoryId}/generate`, {
    method: "POST",
    body: JSON.stringify({ task })
  })
}

export async function getPatches(repositoryId: string): Promise<any[]> {
  return apiClient(`/repositories/${repositoryId}/patches`)
}

export async function approvePatch(repositoryId: string, patchId: string, patchData: any): Promise<any> {
  return apiClient(`/repositories/${repositoryId}/patches/${patchId}/approve`, {
    method: "POST",
    body: JSON.stringify(patchData)
  })
}

export interface ExecutionLog {
  phase: string
  stream: "stdout" | "stderr"
  content: string
  created_at: string
}

export interface ExecutionJob {
  id: string
  patch_id: string | null
  status: "PENDING" | "PROVISIONING" | "INSTALLING" | "BUILDING" | "VALIDATING" | "COMPLETED" | "FAILED"
  started_at: string | null
  completed_at: string | null
  error_message: string | null
  created_at: string
  logs?: ExecutionLog[]
}

export async function listExecutions(repositoryId: string): Promise<ExecutionJob[]> {
  return apiClient(`/repositories/${repositoryId}/executions`)
}

export async function getExecution(repositoryId: string, jobId: string): Promise<ExecutionJob> {
  return apiClient(`/repositories/${repositoryId}/executions/${jobId}`)
}

export async function executePatche(repositoryId: string, patchId: string, workflowId?: string): Promise<any> {
  return apiClient(`/repositories/${repositoryId}/patches/${patchId}/execute`, {
    method: "POST",
    body: JSON.stringify({ workflow_id: workflowId ?? null })
  })
}

export async function cancelExecution(repositoryId: string, jobId: string): Promise<void> {
  return apiClient(`/repositories/${repositoryId}/executions/${jobId}`, { method: "DELETE" })
}
