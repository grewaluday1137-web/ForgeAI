"use client"

import Link from "next/link"
import { useQuery } from "@tanstack/react-query"
import { getWorkflows } from "@/services/workflows"
import { Zap, Clock, ChevronRight, Activity, Plus } from "lucide-react"
import { cn } from "@/lib/utils"

const STATUS_COLORS: Record<string, string> = {
  CREATED:              "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300",
  PLANNING:             "bg-violet-100 text-violet-700 dark:bg-violet-500/10 dark:text-violet-400",
  READY:                "bg-blue-100 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400",
  RUNNING:              "bg-amber-100 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400",
  WAITING_FOR_APPROVAL: "bg-orange-100 text-orange-700 dark:bg-orange-500/10 dark:text-orange-400",
  COMPLETED:            "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400",
  FAILED:               "bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400",
  CANCELLED:            "bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400",
}

export default function WorkflowsPage() {
  const { data: workflows, isLoading } = useQuery({
    queryKey: ["workflows"],
    queryFn: getWorkflows,
  })

  return (
    <div className="flex-1 p-6 lg:p-8 max-w-7xl mx-auto w-full space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <Zap className="size-6 text-violet-500" />
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
              Workflows
            </h1>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 pl-9">
            Monitor and manage your AI orchestration pipelines.
          </p>
        </div>

        <Link
          href="/workspaces"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-700 text-white text-sm font-semibold shadow-lg shadow-violet-500/30 transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          <Plus className="size-4" />
          Create Workflow
        </Link>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20 text-slate-400">
          <Activity className="size-8 animate-pulse mb-4 text-violet-400 opacity-50" />
          <p className="text-sm font-medium">Loading workflows...</p>
        </div>
      ) : workflows?.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/20 p-12 text-center">
          <div className="inline-flex items-center justify-center size-16 rounded-full bg-violet-100 dark:bg-violet-500/10 mb-4">
            <Zap className="size-8 text-violet-500" />
          </div>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">No workflows yet</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mx-auto mb-6">
            Workflows represent a series of AI-driven tasks orchestrated to achieve a specific goal within a Workspace.
          </p>
          <Link
            href="/workspaces"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-900 dark:text-white text-sm font-semibold transition-all"
          >
            Go to Workspaces to create one
          </Link>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {workflows?.map((workflow) => (
            <Link
              key={workflow.id}
              href={`/workflows/${workflow.id}`}
              className="group relative flex flex-col p-5 rounded-2xl bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 hover:border-violet-500/50 dark:hover:border-violet-500/50 transition-all hover:shadow-xl hover:shadow-violet-500/5 overflow-hidden"
            >
              <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
                <ChevronRight className="size-5 text-violet-500" />
              </div>
              
              <div className="flex items-center gap-3 mb-3">
                <div className="size-10 rounded-xl bg-violet-50 dark:bg-violet-500/10 flex items-center justify-center flex-shrink-0">
                  <Zap className="size-5 text-violet-600 dark:text-violet-400" />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="font-semibold text-slate-900 dark:text-white truncate pr-6">
                    {workflow.title}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={cn("px-2 py-0.5 rounded text-[10px] font-bold tracking-wider", STATUS_COLORS[workflow.status] || STATUS_COLORS.CREATED)}>
                      {workflow.status.replace(/_/g, " ")}
                    </span>
                  </div>
                </div>
              </div>

              {workflow.user_request && (
                <p className="text-sm text-slate-500 dark:text-slate-400 line-clamp-2 mb-4 mt-2">
                  "{workflow.user_request}"
                </p>
              )}
              
              <div className="mt-auto pt-4 flex items-center justify-between border-t border-slate-100 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400">
                <div className="flex items-center gap-1.5">
                  <Clock className="size-3.5" />
                  {new Date(workflow.updated_at).toLocaleDateString()}
                </div>
                
                {/* Fallback to 0 if task fields aren't present since we reused WorkflowStatus interface */}
                <div className="font-medium">
                  Tasks: {workflow.completed_tasks ?? 0} / {workflow.task_count ?? 0}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
