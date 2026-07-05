"use client"

import { Boxes } from "lucide-react"

export default function WorkspacesPage() {
  return (
    <div className="flex-1 p-6 lg:p-8 max-w-7xl mx-auto w-full space-y-6">
      <div className="flex items-center gap-3 mb-8">
        <Boxes className="size-6 text-indigo-500" />
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Workspaces
        </h1>
      </div>

      <div className="rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/20 p-12 text-center">
        <div className="inline-flex items-center justify-center size-16 rounded-full bg-indigo-100 dark:bg-indigo-500/10 mb-4">
          <Boxes className="size-8 text-indigo-500" />
        </div>
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">Workspaces Module</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mx-auto mb-6">
          The Workspace management UI allows you to isolate tasks and agents for different branches and environments. Full UI coming soon.
        </p>
      </div>
    </div>
  )
}
