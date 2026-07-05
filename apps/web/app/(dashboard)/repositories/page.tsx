"use client"

import { GitFork } from "lucide-react"

export default function RepositoriesPage() {
  return (
    <div className="flex-1 p-6 lg:p-8 max-w-7xl mx-auto w-full space-y-6">
      <div className="flex items-center gap-3 mb-8">
        <GitFork className="size-6 text-blue-500" />
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Repositories
        </h1>
      </div>

      <div className="rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/20 p-12 text-center">
        <div className="inline-flex items-center justify-center size-16 rounded-full bg-blue-100 dark:bg-blue-500/10 mb-4">
          <GitFork className="size-8 text-blue-500" />
        </div>
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">Repositories Module</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mx-auto mb-6">
          The GitHub integration and repository management UI will be implemented in the upcoming Architect/Developer agent milestones.
        </p>
      </div>
    </div>
  )
}
