import Link from "next/link"
import { Project } from "@/services/projects"
import { FolderOpen, GitFork, Activity, ChevronRight, Boxes } from "lucide-react"
import { cn } from "@/lib/utils"

const colorMap: Record<string, string> = {
  violet: "from-violet-500 to-fuchsia-600 shadow-violet-500/20",
  blue: "from-blue-500 to-indigo-600 shadow-blue-500/20",
  cyan: "from-cyan-400 to-blue-500 shadow-cyan-500/20",
  emerald: "from-emerald-400 to-teal-500 shadow-emerald-500/20",
  orange: "from-orange-400 to-amber-500 shadow-orange-500/20",
  rose: "from-rose-400 to-pink-500 shadow-rose-500/20",
  amber: "from-amber-400 to-orange-500 shadow-amber-500/20",
}

export function ProjectCard({ project }: { project: Project }) {
  const gradient = colorMap[project.color] || colorMap.blue

  return (
    <Link
      href={`/projects/${project.slug}`}
      className="group relative flex flex-col rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm p-5 hover:shadow-xl hover:shadow-indigo-500/5 hover:-translate-y-1 transition-all duration-300"
    >
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-indigo-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
      
      <div className="relative flex items-start justify-between mb-4">
        <div className={cn("size-12 rounded-xl bg-gradient-to-br flex items-center justify-center shadow-lg text-white font-bold text-xl", gradient)}>
          {project.name.charAt(0).toUpperCase()}
        </div>
        <div className="flex items-center gap-2">
          {project.visibility === "PUBLIC" && (
            <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400 text-xs font-medium">Public</span>
          )}
          {project.visibility === "TEAM" && (
            <span className="px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400 text-xs font-medium">Team</span>
          )}
          {project.visibility === "PRIVATE" && (
            <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 text-xs font-medium">Private</span>
          )}
        </div>
      </div>

      <div className="relative">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-1 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
          {project.name}
        </h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 line-clamp-2 min-h-[40px]">
          {project.description || "No description provided."}
        </p>
      </div>

      <div className="relative mt-6 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 border-t border-slate-100 dark:border-slate-800/60 pt-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5" title="Repositories">
            <GitFork className="size-3.5" />
            <span>0</span>
          </div>
          <div className="flex items-center gap-1.5" title="Workspaces">
            <Boxes className="size-3.5" />
            <span>0</span>
          </div>
          <div className="flex items-center gap-1.5" title="Workflows">
            <Activity className="size-3.5" />
            <span>0</span>
          </div>
        </div>
        <div className="opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300">
          <ChevronRight className="size-4 text-indigo-500" />
        </div>
      </div>
    </Link>
  )
}
