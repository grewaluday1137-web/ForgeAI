"use client"

import { useQuery } from "@tanstack/react-query"
import { useParams } from "next/navigation"
import { getProjectBySlug } from "@/services/projects"
import { GitFork, Activity, Boxes, Users } from "lucide-react"

export default function ProjectOverviewPage() {
  const params = useParams()
  const slug = params.slug as string

  const { data: project, isLoading } = useQuery({
    queryKey: ["project", slug],
    queryFn: () => getProjectBySlug(slug),
  })

  if (isLoading) {
    return (
      <div className="flex-1 p-8 space-y-6 max-w-7xl mx-auto w-full">
        <div className="h-12 w-1/3 bg-slate-100 dark:bg-slate-800 animate-pulse rounded-lg" />
        <div className="h-6 w-2/3 bg-slate-100 dark:bg-slate-800 animate-pulse rounded-lg" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-8">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-32 bg-slate-100 dark:bg-slate-800 animate-pulse rounded-2xl" />)}
        </div>
      </div>
    )
  }

  if (!project) return null

  return (
    <div className="flex-1 space-y-6 p-8 w-full max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
              {project.name}
            </h1>
            <span className="px-2.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-xs font-medium text-slate-600 dark:text-slate-300">
              {project.visibility}
            </span>
          </div>
          <p className="text-base text-slate-500 dark:text-slate-400 max-w-2xl">
            {project.description || "No description provided."}
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
        
        <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-5 shadow-sm">
          <div className="flex flex-col gap-3">
            <div className="size-10 rounded-xl bg-blue-50 dark:bg-blue-500/10 flex items-center justify-center text-blue-600 dark:text-blue-400">
              <GitFork className="size-5" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Repositories</p>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white">0</h3>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-5 shadow-sm">
          <div className="flex flex-col gap-3">
            <div className="size-10 rounded-xl bg-violet-50 dark:bg-violet-500/10 flex items-center justify-center text-violet-600 dark:text-violet-400">
              <Boxes className="size-5" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Workspaces</p>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white">0</h3>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-5 shadow-sm">
          <div className="flex flex-col gap-3">
            <div className="size-10 rounded-xl bg-emerald-50 dark:bg-emerald-500/10 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
              <Activity className="size-5" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Workflows</p>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white">0</h3>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-5 shadow-sm">
          <div className="flex flex-col gap-3">
            <div className="size-10 rounded-xl bg-orange-50 dark:bg-orange-500/10 flex items-center justify-center text-orange-600 dark:text-orange-400">
              <Users className="size-5" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Members</p>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white">1</h3>
            </div>
          </div>
        </div>

      </div>

      {/* Layout for future sections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Workspaces List placeholder */}
          <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-6 min-h-[400px]">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Workspaces</h3>
            <div className="text-center py-12 text-slate-500">No workspaces configured yet.</div>
          </div>
        </div>
        <div className="space-y-6">
          {/* Activity Feed placeholder */}
          <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-6 min-h-[400px]">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Recent Activity</h3>
            <div className="text-center py-12 text-slate-500">No recent activity.</div>
          </div>
        </div>
      </div>
    </div>
  )
}
