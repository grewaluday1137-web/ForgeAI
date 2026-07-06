"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useParams, useRouter } from "next/navigation"
import Link from "next/link"
import {
  getRepositoryOverview,
  getRepositoryTree,
  getArchitectureReport,
  searchRepository,
  connectRepository,
} from "@/services/repositories"
import { useWorkflowEvents } from "@/hooks/use-workflow-events"
import { toast } from "@/hooks/use-toast"
import {
  GitFork, Search, Folder, FileText, Wifi, WifiOff, Activity,
  RefreshCw, Layers, Code2, Terminal, Box, Zap, ChevronRight,
  BarChart3, BookOpen, AlertTriangle, CheckCircle2, ShieldCheck
} from "lucide-react"
import { cn } from "@/lib/utils"

const FILE_TYPE_COLOR: Record<string, string> = {
  python: "text-blue-500",
  typescript: "text-cyan-500",
  "typescript-react": "text-cyan-400",
  javascript: "text-yellow-500",
  "javascript-react": "text-yellow-400",
  html: "text-orange-500",
  css: "text-pink-500",
  json: "text-amber-500",
  yaml: "text-violet-500",
  toml: "text-violet-400",
  markdown: "text-slate-400",
  go: "text-teal-500",
  rust: "text-orange-600",
  java: "text-red-500",
  config: "text-emerald-500",
  unknown: "text-slate-500",
}

const FRAMEWORK_GRADIENTS: Record<string, string> = {
  "Next.js": "from-slate-700 to-slate-900",
  React: "from-cyan-500 to-blue-600",
  FastAPI: "from-teal-500 to-emerald-600",
  Django: "from-green-600 to-green-800",
  Express: "from-slate-500 to-slate-700",
  "Spring Boot": "from-green-500 to-lime-600",
  default: "from-violet-500 to-fuchsia-600",
}

function buildFileTree(files: { path: string; type: string }[]) {
  const tree: Record<string, any[]> = {}
  const roots: { name: string; type: string; children?: any[] }[] = []

  for (const f of files) {
    const parts = f.path.split("/")
    if (parts.length === 1) {
      roots.push({ name: parts[0], type: f.type })
    } else {
      const dir = parts[0]
      if (!tree[dir]) tree[dir] = []
      tree[dir].push({ name: parts.slice(1).join("/"), type: f.type })
    }
  }

  const dirs = Object.keys(tree).sort()
  return {
    dirs: dirs.map(d => ({ name: d, files: tree[d].slice(0, 20) })),
    rootFiles: roots.slice(0, 20),
  }
}

export default function RepositoryOverviewPage() {
  const params = useParams()
  const repositoryId = params.id as string
  const [searchQuery, setSearchQuery] = useState("")
  const [activeTab, setActiveTab] = useState<"overview" | "tree" | "architecture" | "search">("overview")
  const queryClient = useQueryClient()

  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: ["repo-overview", repositoryId],
    queryFn: () => getRepositoryOverview(repositoryId),
  })

  const { data: treeData } = useQuery({
    queryKey: ["repo-tree", repositoryId],
    queryFn: () => getRepositoryTree(repositoryId),
    enabled: activeTab === "tree",
  })

  const { data: architectureData, isLoading: archLoading } = useQuery({
    queryKey: ["repo-architecture", repositoryId],
    queryFn: () => getArchitectureReport(repositoryId),
    enabled: activeTab === "architecture",
    retry: false,
  })

  const { data: searchResults, isLoading: searchLoading } = useQuery({
    queryKey: ["repo-search", repositoryId, searchQuery],
    queryFn: () => searchRepository(repositoryId, searchQuery),
    enabled: activeTab === "search" && searchQuery.length > 1,
  })

  const { mutate: connect, isPending: isConnecting } = useMutation({
    mutationFn: () => connectRepository(repositoryId),
    onSuccess: () => {
      toast.success("Analysis started!", "Cloning and indexing your repository...")
    },
    onError: (err: any) => toast.error("Error", err.message),
  })

  const { events, connected } = useWorkflowEvents(repositoryId)

  const tabs = [
    { id: "overview", label: "Overview", icon: <BarChart3 className="size-3.5" /> },
    { id: "tree", label: "File Tree", icon: <Folder className="size-3.5" /> },
    { id: "architecture", label: "Architecture", icon: <Layers className="size-3.5" /> },
    { id: "search", label: "Search", icon: <Search className="size-3.5" /> },
  ] as const

  const isAnalyzed = (overview?.file_count ?? 0) > 0

  return (
    <div className="flex-1 p-6 lg:p-8 max-w-7xl mx-auto w-full space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="size-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
            <GitFork className="size-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Repository Overview</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400">Architect Agent Intelligence</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className={cn("flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded-full",
            connected
              ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400"
              : "bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400"
          )}>
            {connected ? <Wifi className="size-3" /> : <WifiOff className="size-3" />}
            {connected ? "Live" : "Offline"}
          </div>
          <button
            onClick={() => connect()}
            disabled={isConnecting}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-semibold shadow-lg shadow-blue-500/30 transition-all hover:scale-[1.02]"
          >
            <RefreshCw className={cn("size-4", isConnecting && "animate-spin")} />
            {isConnecting ? "Analyzing..." : isAnalyzed ? "Re-analyze" : "Connect & Analyze"}
          </button>
          <Link
            href={`/repositories/${repositoryId}/generate`}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-700 text-white text-sm font-semibold shadow-lg shadow-violet-500/30 transition-all hover:scale-[1.02]"
          >
            <Terminal className="size-4" />
            Developer Agent
          </Link>
          <Link
            href={`/repositories/${repositoryId}/executions`}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-700 hover:bg-slate-600 text-white text-sm font-semibold transition-all hover:scale-[1.02]"
          >
            <Zap className="size-4" />
            Executions
          </Link>
          <Link
            href={`/repositories/${repositoryId}/quality`}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold shadow-lg shadow-emerald-500/30 transition-all hover:scale-[1.02]"
          >
            <ShieldCheck className="size-4" />
            Quality
          </Link>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Files Indexed", value: overviewLoading ? "..." : String(overview?.file_count ?? 0), icon: <FileText className="size-4" />, gradient: "from-blue-500 to-indigo-600" },
          { label: "Languages", value: overviewLoading ? "..." : String(overview?.languages?.length ?? 0), icon: <Code2 className="size-4" />, gradient: "from-violet-500 to-fuchsia-600" },
          { label: "Frameworks", value: overviewLoading ? "..." : String(overview?.frameworks?.length ?? 0), icon: <Box className="size-4" />, gradient: "from-cyan-500 to-blue-600" },
          { label: "Components", value: overviewLoading ? "..." : String(overview?.key_components?.length ?? 0), icon: <Layers className="size-4" />, gradient: "from-emerald-500 to-teal-600" },
        ].map((stat) => (
          <div key={stat.label} className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-4 flex items-center gap-3">
            <div className={cn("size-10 rounded-xl bg-gradient-to-br flex items-center justify-center text-white flex-shrink-0 shadow-sm", stat.gradient)}>
              {stat.icon}
            </div>
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">{stat.label}</p>
              <p className="text-xl font-bold text-slate-900 dark:text-white">{stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 p-1 bg-slate-100 dark:bg-slate-800/60 rounded-xl w-fit">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all",
              activeTab === tab.id
                ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm"
                : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300"
            )}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">

          {/* Overview Tab */}
          {activeTab === "overview" && (
            <>
              {/* Languages */}
              <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-6">
                <h2 className="text-base font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                  <Code2 className="size-4 text-violet-500" /> Languages
                </h2>
                {overviewLoading ? (
                  <div className="h-8 bg-slate-100 dark:bg-slate-800 rounded animate-pulse" />
                ) : (overview?.languages?.length ?? 0) === 0 ? (
                  <p className="text-sm text-slate-400">No languages detected yet. Connect the repository first.</p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {overview?.languages.map((lang) => (
                      <span key={lang} className="px-3 py-1.5 rounded-full bg-violet-50 dark:bg-violet-500/10 text-violet-700 dark:text-violet-400 text-sm font-semibold border border-violet-200 dark:border-violet-500/20">
                        {lang}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Frameworks */}
              <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-6">
                <h2 className="text-base font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                  <Box className="size-4 text-cyan-500" /> Frameworks & Libraries
                </h2>
                {(overview?.frameworks?.length ?? 0) === 0 ? (
                  <p className="text-sm text-slate-400">No frameworks detected yet.</p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {overview?.frameworks.map((fw) => {
                      const gradient = FRAMEWORK_GRADIENTS[fw] || FRAMEWORK_GRADIENTS.default
                      return (
                        <span key={fw} className={cn("px-3 py-1.5 rounded-full bg-gradient-to-r text-white text-sm font-semibold shadow-sm", gradient)}>
                          {fw}
                        </span>
                      )
                    })}
                  </div>
                )}
              </div>

              {/* Architecture Patterns */}
              <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-6">
                <h2 className="text-base font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                  <Layers className="size-4 text-blue-500" /> Architecture Patterns
                </h2>
                {(overview?.architecture_patterns?.length ?? 0) === 0 ? (
                  <p className="text-sm text-slate-400">No patterns detected yet.</p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {overview?.architecture_patterns.map((p) => (
                      <span key={p} className="px-3 py-1.5 rounded-full bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-400 text-sm font-semibold border border-blue-200 dark:border-blue-500/20">
                        {p}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Summary */}
              {overview?.architecture_summary && (
                <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-6">
                  <h2 className="text-base font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
                    <BookOpen className="size-4 text-emerald-500" /> Architecture Summary
                  </h2>
                  <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">{overview.architecture_summary}</p>
                </div>
              )}
            </>
          )}

          {/* File Tree Tab */}
          {activeTab === "tree" && (
            <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-6">
              <h2 className="text-base font-semibold text-slate-900 dark:text-white mb-4">File Tree</h2>
              {!treeData ? (
                <div className="space-y-2">
                  {Array.from({ length: 8 }).map((_, i) => (
                    <div key={i} className="h-6 bg-slate-100 dark:bg-slate-800 rounded animate-pulse" style={{ width: `${60 + Math.random() * 30}%` }} />
                  ))}
                </div>
              ) : treeData.files.length === 0 ? (
                <p className="text-sm text-slate-400">No files indexed yet. Connect the repository first.</p>
              ) : (
                <div className="font-mono text-xs space-y-1">
                  {(() => {
                    const { dirs, rootFiles } = buildFileTree(treeData.files)
                    return (
                      <>
                        {rootFiles.map(f => (
                          <div key={f.path} className="flex items-center gap-2 px-2 py-0.5 rounded hover:bg-slate-50 dark:hover:bg-slate-800/50">
                            <FileText className={cn("size-3 flex-shrink-0", FILE_TYPE_COLOR[f.type] || FILE_TYPE_COLOR.unknown)} />
                            <span className="text-slate-600 dark:text-slate-400">{f.name}</span>
                          </div>
                        ))}
                        {dirs.map(dir => (
                          <div key={dir.name}>
                            <div className="flex items-center gap-2 px-2 py-0.5 text-slate-700 dark:text-slate-300 font-semibold">
                              <Folder className="size-3 text-amber-500 flex-shrink-0" />
                              {dir.name}/
                            </div>
                            <div className="ml-4 space-y-0.5">
                              {dir.files.map((f: any) => (
                                <div key={f.name} className="flex items-center gap-2 px-2 py-0.5 rounded hover:bg-slate-50 dark:hover:bg-slate-800/50">
                                  <FileText className={cn("size-3 flex-shrink-0", FILE_TYPE_COLOR[f.type] || FILE_TYPE_COLOR.unknown)} />
                                  <span className="text-slate-500 dark:text-slate-400">{f.name}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </>
                    )
                  })()}
                </div>
              )}
            </div>
          )}

          {/* Architecture Tab */}
          {activeTab === "architecture" && (
            <div className="space-y-6">
              {archLoading ? (
                <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-8 text-center">
                  <div className="size-8 rounded-full border-2 border-blue-500 border-t-transparent animate-spin mx-auto mb-3" />
                  <p className="text-sm text-slate-500">Loading architecture report...</p>
                </div>
              ) : !architectureData ? (
                <div className="rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 p-8 text-center">
                  <AlertTriangle className="size-8 text-amber-400 mx-auto mb-3" />
                  <p className="text-sm font-medium text-slate-500">No architecture report yet.</p>
                  <p className="text-xs text-slate-400 mt-1">Click "Connect & Analyze" to run the Architect Agent.</p>
                </div>
              ) : (
                <>
                  <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-6">
                    <h2 className="text-base font-semibold text-slate-900 dark:text-white mb-4">Package Managers</h2>
                    <div className="flex flex-wrap gap-2">
                      {architectureData.analysis.package_managers.map(pm => (
                        <span key={pm} className="px-3 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-sm font-mono font-medium">{pm}</span>
                      ))}
                    </div>
                  </div>
                  <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-6">
                    <h2 className="text-base font-semibold text-slate-900 dark:text-white mb-4">Knowledge Graph — Key Components</h2>
                    <div className="space-y-2">
                      {architectureData.knowledge_nodes.map((n, i) => (
                        <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
                          <div className="size-7 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center flex-shrink-0 shadow-sm">
                            <Layers className="size-3.5 text-white" />
                          </div>
                          <div className="min-w-0">
                            <p className="text-sm font-semibold text-slate-900 dark:text-white">{n.name}</p>
                            <div className="flex items-center gap-2 mt-0.5">
                              <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-700 text-slate-500 dark:text-slate-400 font-mono">{n.type}</span>
                              {n.path && <span className="text-[10px] text-slate-400 font-mono truncate">{n.path}</span>}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>
          )}

          {/* Search Tab */}
          {activeTab === "search" && (
            <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-6">
              <div className="relative mb-4">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search files, symbols, paths..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
                />
              </div>
              {searchQuery.length < 2 ? (
                <p className="text-sm text-slate-400 text-center py-6">Type at least 2 characters to search.</p>
              ) : searchLoading ? (
                <div className="space-y-2">
                  {Array.from({ length: 4 }).map((_, i) => (
                    <div key={i} className="h-10 bg-slate-100 dark:bg-slate-800 rounded animate-pulse" />
                  ))}
                </div>
              ) : !searchResults || searchResults.length === 0 ? (
                <p className="text-sm text-slate-400 text-center py-6">No results for "{searchQuery}"</p>
              ) : (
                <div className="space-y-1">
                  {searchResults.map((r) => (
                    <div key={r.id} className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 group">
                      <FileText className={cn("size-4 flex-shrink-0", FILE_TYPE_COLOR[r.file_type] || FILE_TYPE_COLOR.unknown)} />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-slate-700 dark:text-slate-300 truncate font-mono">{r.file_path}</p>
                        <p className="text-[10px] text-slate-400">{r.file_type} · {(r.size_bytes / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right: Live Events */}
        <div className="space-y-4">
          <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-5 flex flex-col" style={{ height: "500px" }}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                <Activity className="size-4 text-blue-500" />
                Live Events
              </h2>
              <span className="text-xs text-slate-400">{events.length}</span>
            </div>
            <div className="flex-1 overflow-y-auto space-y-2">
              {events.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-slate-400">
                  <Activity className="size-6 mb-2 opacity-30" />
                  <p className="text-xs">Waiting for events...</p>
                </div>
              ) : (
                events.map((evt, i) => (
                  <div key={i} className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800/50">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] font-mono font-semibold text-blue-600 dark:text-blue-400">{evt.event}</span>
                      <span className="text-[10px] text-slate-400">{new Date(evt.receivedAt).toLocaleTimeString()}</span>
                    </div>
                    {evt.data?.message && (
                      <p className="text-xs text-slate-600 dark:text-slate-400">{String(evt.data.message)}</p>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Key Components */}
          {(overview?.key_components?.length ?? 0) > 0 && (
            <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-5">
              <h2 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-3">Key Components</h2>
              <div className="space-y-1.5">
                {overview?.key_components.map((c, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
                    <CheckCircle2 className="size-3.5 text-emerald-500 flex-shrink-0" />
                    {c}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
