"use client"

import Link from "next/link"
import { useState } from "react"
import { GitFork, GitBranch, Clock, ChevronRight, Search, RefreshCw, CheckCircle2, AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"

// Note: Repositories are project-scoped, but this page shows a global list for quick navigation.
// For now we show a beautiful landing with guidance on how to connect a repo.
export default function RepositoriesPage() {
  return (
    <div className="flex-1 p-6 lg:p-8 max-w-7xl mx-auto w-full space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className="size-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
          <GitFork className="size-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Repositories</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Connect a GitHub repository to enable the Architect Agent</p>
        </div>
      </div>

      {/* How it works */}
      <div className="grid md:grid-cols-3 gap-4">
        {[
          {
            step: "01",
            icon: <GitFork className="size-6" />,
            title: "Connect Repository",
            desc: "Link a GitHub repository to your project. ForgeAI uses your PAT to securely clone it.",
            gradient: "from-blue-500 to-indigo-600",
          },
          {
            step: "02",
            icon: <Search className="size-6" />,
            title: "Architect Agent Analyzes",
            desc: "The Architect scans every file, detects languages, frameworks, and patterns to build a knowledge graph.",
            gradient: "from-violet-500 to-fuchsia-600",
          },
          {
            step: "03",
            icon: <CheckCircle2 className="size-6" />,
            title: "Context Available",
            desc: "Every future agent — Developer, Tester, Reviewer — draws from this knowledge instead of re-scanning.",
            gradient: "from-emerald-500 to-teal-600",
          },
        ].map((item) => (
          <div key={item.step} className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-6 group hover:border-blue-500/30 transition-all hover:shadow-xl hover:shadow-blue-500/5">
            <div className="flex items-start gap-4">
              <div className={cn("size-12 rounded-xl bg-gradient-to-br flex items-center justify-center text-white shadow-sm flex-shrink-0", item.gradient)}>
                {item.icon}
              </div>
              <div>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Step {item.step}</p>
                <h3 className="text-base font-semibold text-slate-900 dark:text-white mb-1">{item.title}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed">{item.desc}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Instructions */}
      <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-6">
        <h2 className="text-base font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
          <GitBranch className="size-4 text-blue-500" />
          Connecting a Repository
        </h2>
        <ol className="space-y-3 text-sm text-slate-600 dark:text-slate-400">
          <li className="flex items-start gap-3">
            <span className="flex-shrink-0 size-5 rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 text-[10px] font-bold flex items-center justify-center mt-0.5">1</span>
            Navigate to your <strong className="text-slate-700 dark:text-slate-300">Project</strong> and open the Repositories tab.
          </li>
          <li className="flex items-start gap-3">
            <span className="flex-shrink-0 size-5 rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 text-[10px] font-bold flex items-center justify-center mt-0.5">2</span>
            Create a repository record with the GitHub URL (e.g. <code className="bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded font-mono text-xs">https://github.com/owner/repo</code>).
          </li>
          <li className="flex items-start gap-3">
            <span className="flex-shrink-0 size-5 rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 text-[10px] font-bold flex items-center justify-center mt-0.5">3</span>
            Open the repository detail page and click <strong className="text-slate-700 dark:text-slate-300">"Connect & Analyze"</strong> to trigger the full pipeline.
          </li>
          <li className="flex items-start gap-3">
            <span className="flex-shrink-0 size-5 rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 text-[10px] font-bold flex items-center justify-center mt-0.5">4</span>
            Watch the <strong className="text-slate-700 dark:text-slate-300">Live Events</strong> panel as the Architect Agent clones, indexes, and analyzes in real-time.
          </li>
        </ol>

        <div className="mt-5 p-4 rounded-xl bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20">
          <p className="text-sm text-amber-700 dark:text-amber-400">
            <strong>Required:</strong> Set your <code className="bg-amber-100 dark:bg-amber-500/20 px-1.5 py-0.5 rounded font-mono text-xs">GITHUB_PAT</code> environment variable in <code className="bg-amber-100 dark:bg-amber-500/20 px-1.5 py-0.5 rounded font-mono text-xs">docker-compose.yml</code> to enable private repository access.
          </p>
        </div>
      </div>
    </div>
  )
}
