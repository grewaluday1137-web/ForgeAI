import { apiClient } from "@/lib/api-client"

export interface Project {
  id: string
  owner_id: string
  name: string
  slug: string
  description?: string
  icon?: string
  color: string
  visibility: "PRIVATE" | "TEAM" | "PUBLIC"
  status: "ACTIVE" | "ARCHIVED" | "DELETED"
  created_at: string
  updated_at: string
}

export type ProjectCreateInput = Pick<Project, "name" | "description" | "icon" | "color" | "visibility">

export async function getProjects(): Promise<Project[]> {
  return apiClient("/projects")
}

export async function getProject(id: string): Promise<Project> {
  return apiClient(`/projects/${id}`)
}

export async function getProjectBySlug(slug: string): Promise<Project> {
  return apiClient(`/projects/slug/${slug}`)
}

export async function createProject(data: ProjectCreateInput): Promise<Project> {
  return apiClient("/projects", {
    method: "POST",
    body: JSON.stringify(data),
  })
}
