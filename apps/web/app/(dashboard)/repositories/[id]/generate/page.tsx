"use client"

import { useState } from "react"
import { useParams } from "next/navigation"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { generateCode, getPatches, approvePatch } from "@/services/repositories"
import { toast } from "@/hooks/use-toast"
import { 
  Terminal, Play, CheckCircle2, XCircle, Code2, 
  MessageSquare, History, FileText, Bot, AlertTriangle
} from "lucide-react"
import { cn } from "@/lib/utils"

export default function CodeGenerationPage() {
  const params = useParams()
  const repositoryId = params.id as string
  const queryClient = useQueryClient()
  
  const [task, setTask] = useState("")
  const [activePatch, setActivePatch] = useState<any>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  const { data: patches = [], isLoading: loadingPatches } = useQuery({
    queryKey: ["repo-patches", repositoryId],
    queryFn: () => getPatches(repositoryId),
  })

  const handleGenerate = async () => {
    if (!task.trim()) return toast.error("Error", "Please enter a task description.")
    
    setIsGenerating(true)
    toast.success("Agent Started", "Developer agent is analyzing the request...")
    
    try {
      const res = await generateCode(repositoryId, task)
      toast.success("Patch Generated", "Review the changes below.")
      setActivePatch({
        id: res.patch_id,
        ...res.patch
      })
      queryClient.invalidateQueries({ queryKey: ["repo-patches"] })
    } catch (err: any) {
      toast.error("Generation Failed", err.message)
    } finally {
      setIsGenerating(false)
    }
  }

  const { mutate: apply, isPending: isApplying } = useMutation({
    mutationFn: () => approvePatch(repositoryId, activePatch.id, activePatch),
    onSuccess: (data) => {
      toast.success("Patch Applied", `Changes committed successfully (${data.commit_hash.slice(0, 7)})`)
      setActivePatch(null)
      queryClient.invalidateQueries({ queryKey: ["repo-patches"] })
    },
    onError: (err: any) => {
      toast.error("Failed to Apply", err.message)
    }
  })

  return (
    <div className="flex-1 p-6 lg:p-8 max-w-[1600px] mx-auto w-full flex flex-col md:flex-row gap-6 h-[calc(100vh-64px)] overflow-hidden">
      
      {/* Left Column: Task Input & History */}
      <div className="w-full md:w-[400px] flex flex-col gap-6 shrink-0 h-full overflow-y-auto pr-2 pb-8">
        <div className="flex items-center gap-3">
          <div className="size-10 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center shadow-lg shadow-violet-500/30">
            <Terminal className="size-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">Developer Agent</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">Autonomous Code Generation</p>
          </div>
        </div>

        {/* Task Input */}
        <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-5 flex flex-col">
          <label className="text-sm font-semibold text-slate-900 dark:text-white mb-2">What should I build?</label>
          <textarea
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="E.g., Add a health check endpoint, or refactor the user model..."
            className="w-full h-32 p-3 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-violet-500/50 resize-none mb-4"
          />
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !task.trim()}
            className="w-full py-2.5 rounded-xl bg-violet-600 hover:bg-violet-700 disabled:opacity-60 text-white text-sm font-semibold shadow-lg shadow-violet-500/30 transition-all flex items-center justify-center gap-2"
          >
            {isGenerating ? (
              <div className="size-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : <Play className="size-4" />}
            {isGenerating ? "Generating..." : "Generate Code"}
          </button>
        </div>

        {/* History */}
        <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-5 flex-1 flex flex-col min-h-0">
          <h2 className="text-sm font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
            <History className="size-4 text-blue-500" />
            Patch History
          </h2>
          <div className="flex-1 overflow-y-auto space-y-2">
            {loadingPatches ? (
              <div className="animate-pulse space-y-2">
                {[1, 2, 3].map(i => <div key={i} className="h-12 bg-slate-100 dark:bg-slate-800 rounded-lg" />)}
              </div>
            ) : patches.length === 0 ? (
              <p className="text-xs text-slate-400 text-center py-4">No generated patches yet.</p>
            ) : patches.map((p: any) => (
              <div key={p.id} className="p-3 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
                <p className="text-xs font-medium text-slate-900 dark:text-white truncate mb-2" title={p.task}>{p.task}</p>
                <div className="flex items-center justify-between">
                  <span className={cn("text-[10px] px-2 py-0.5 rounded-full font-semibold", 
                    p.status === 'APPLIED' ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400" :
                    p.status === 'FAILED' ? "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400" :
                    "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400"
                  )}>
                    {p.status}
                  </span>
                  <span className="text-[10px] text-slate-400">{new Date(p.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right Column: Code Diff & Approval */}
      <div className="flex-1 flex flex-col h-full overflow-hidden rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white dark:bg-slate-900 shadow-sm">
        {!activePatch ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
            <Bot className="size-16 text-slate-300 dark:text-slate-700 mb-4" />
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">Code Generation Workspace</h2>
            <p className="text-sm text-slate-500 max-w-sm">
              Enter a task description on the left to have the Developer Agent generate a unified patch for review.
            </p>
          </div>
        ) : (
          <div className="flex flex-col h-full">
            {/* Header / Explanation */}
            <div className="p-6 border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
              <div className="flex items-start justify-between gap-4 mb-4">
                <div className="flex items-center gap-2 text-violet-600 dark:text-violet-400">
                  <MessageSquare className="size-5" />
                  <h3 className="font-semibold text-slate-900 dark:text-white">AI Explanation</h3>
                </div>
                <div className="flex gap-2">
                  <button 
                    onClick={() => setActivePatch(null)}
                    disabled={isApplying}
                    className="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-sm font-medium transition-colors text-slate-600 dark:text-slate-300 flex items-center gap-2"
                  >
                    <XCircle className="size-4" /> Reject
                  </button>
                  <button 
                    onClick={() => apply()}
                    disabled={isApplying}
                    className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold shadow-lg shadow-emerald-500/30 transition-all flex items-center gap-2"
                  >
                    {isApplying ? <div className="size-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <CheckCircle2 className="size-4" />}
                    {isApplying ? "Applying..." : "Approve & Apply"}
                  </button>
                </div>
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                {activePatch.explanation}
              </p>
            </div>

            {/* Diffs */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-950">
              {/* Modifications */}
              {activePatch.patches?.map((p: any, idx: number) => (
                <div key={`mod-${idx}`} className="rounded-xl border border-slate-800 overflow-hidden">
                  <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 flex items-center gap-2">
                    <FileText className="size-3.5 text-blue-400" />
                    <span className="text-xs font-mono text-slate-300">{p.file_path}</span>
                  </div>
                  <pre className="p-4 text-xs font-mono overflow-x-auto whitespace-pre-wrap">
                    {p.diff.split('\n').map((line: string, i: number) => {
                      let color = "text-slate-400"
                      if (line.startsWith("+")) color = "text-emerald-400 bg-emerald-400/10"
                      if (line.startsWith("-")) color = "text-red-400 bg-red-400/10"
                      if (line.startsWith("@@")) color = "text-blue-400"
                      return <div key={i} className={cn("px-2", color)}>{line}</div>
                    })}
                  </pre>
                </div>
              ))}

              {/* New Files */}
              {activePatch.new_files?.map((p: any, idx: number) => (
                <div key={`new-${idx}`} className="rounded-xl border border-slate-800 overflow-hidden">
                  <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 flex items-center gap-2">
                    <Code2 className="size-3.5 text-emerald-400" />
                    <span className="text-xs font-mono text-slate-300">{p.file_path} <span className="text-emerald-500 bg-emerald-500/20 px-1.5 py-0.5 rounded ml-2">New</span></span>
                  </div>
                  <pre className="p-4 text-xs font-mono overflow-x-auto text-emerald-400 whitespace-pre-wrap">
                    {p.content}
                  </pre>
                </div>
              ))}

              {/* Deleted Files */}
              {activePatch.deleted_files?.map((path: string, idx: number) => (
                <div key={`del-${idx}`} className="rounded-xl border border-red-900/50 bg-red-500/5 px-4 py-3 flex items-center gap-2">
                  <AlertTriangle className="size-4 text-red-500" />
                  <span className="text-xs font-mono text-red-400 line-through">{path}</span>
                  <span className="text-xs font-semibold text-red-500 ml-auto">Deleted</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
