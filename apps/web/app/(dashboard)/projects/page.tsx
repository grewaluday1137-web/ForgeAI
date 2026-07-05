"use client"

import { useQuery } from "@tanstack/react-query"
import { getProjects } from "@/services/projects"
import { ProjectCard } from "@/components/ui/cards"
import { EmptyState } from "@/components/ui/empty-states"
import { CreateProjectDialog } from "@/components/projects/create-project-dialog"

export default function ProjectsPage() {
  const { data: projects, isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: getProjects,
  })

  return (
    <div className="flex-1 space-y-6 p-8 w-full max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Projects</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Manage your repositories, agents, and workspaces.</p>
        </div>
        <CreateProjectDialog />
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-48 rounded-2xl bg-slate-100 dark:bg-slate-800/50 animate-pulse" />
          ))}
        </div>
      ) : projects?.length === 0 ? (
        <div className="mt-10">
          <EmptyState
            title="No projects yet"
            description="Create your first project to start building with autonomous AI agents."
            action={<CreateProjectDialog />}
          />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
          {projects?.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}
    </div>
  )
}
