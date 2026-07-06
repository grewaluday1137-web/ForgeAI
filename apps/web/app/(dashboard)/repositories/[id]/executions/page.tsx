"use client"

import { useState, useEffect, useRef } from "react"
import { useParams } from "next/navigation"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  listExecutions,
  getExecution,
  cancelExecution,
  type ExecutionJob,
  type ExecutionLog,
} from "@/services/repositories"
import { cn } from "@/lib/utils"
import {
  Terminal, Container, CheckCircle2, XCircle, Clock,
  ChevronRight, Loader2, RefreshCw, Play, AlertOctagon,
  Download, Zap, PackageOpen, Hammer, ShieldCheck
} from "lucide-react"

// ─── Status Configuration ────────────────────────────────────────────────────

const STATUS_STEPS = [
  { id: "PROVISIONING", label: "Provision",     icon: Container },
  { id: "INSTALLING",   label: "Dependencies",  icon: PackageOpen },
  { id: "BUILDING",     label: "Build",         icon: Hammer },
  { id: "VALIDATING",   label: "Validate",      icon: ShieldCheck },
  { id: "COMPLETED",    label: "Complete",      icon: CheckCircle2 },
] as const

type StepState = "done" | "active" | "failed" | "pending"

function getStepState(stepId: string, jobStatus: string): StepState {
  const order = STATUS_STEPS.map(s => s.id)
  const stepIdx = order.indexOf(stepId as any)
  const currentIdx = order.indexOf(jobStatus as any)

  if (jobStatus === "FAILED") {
    if (stepIdx < currentIdx) return "done"
    if (stepIdx === currentIdx) return "failed"
    return "pending"
  }
  if (stepIdx < currentIdx || jobStatus === "COMPLETED") return "done"
  if (stepIdx === currentIdx) return "active"
  return "pending"
}

const PHASE_COLORS: Record<string, string> = {
  stdout: "text-slate-200",
  stderr: "text-red-400",
}

const STATUS_BADGES: Record<string, { label: string; cls: string }> = {
  PENDING:      { label: "Pending",      cls: "bg-slate-700 text-slate-300" },
  PROVISIONING: { label: "Provisioning", cls: "bg-blue-900/60 text-blue-300 animate-pulse" },
  INSTALLING:   { label: "Installing",   cls: "bg-amber-900/60 text-amber-300 animate-pulse" },
  BUILDING:     { label: "Building",     cls: "bg-violet-900/60 text-violet-300 animate-pulse" },
  VALIDATING:   { label: "Validating",   cls: "bg-cyan-900/60 text-cyan-300 animate-pulse" },
  COMPLETED:    { label: "Completed",    cls: "bg-emerald-900/60 text-emerald-300" },
  FAILED:       { label: "Failed",       cls: "bg-red-900/60 text-red-300" },
}

// ─── Main Page ───────────────────────────────────────────────────────────────

export default function ExecutionsPage() {
  const params = useParams()
  const repositoryId = params.id as string
  const queryClient = useQueryClient()
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null)
  const logEndRef = useRef<HTMLDivElement>(null)

  const { data: executions = [], isLoading: loadingList } = useQuery({
    queryKey: ["executions", repositoryId],
    queryFn: () => listExecutions(repositoryId),
    refetchInterval: 5000,
  })

  const { data: activeJob, isLoading: loadingJob } = useQuery({
    queryKey: ["execution", repositoryId, selectedJobId],
    queryFn: () => getExecution(repositoryId, selectedJobId!),
    enabled: !!selectedJobId,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      if (!status) return 2000
      return ["COMPLETED", "FAILED"].includes(status) ? false : 2000
    },
  })

  const { mutate: cancel, isPending: isCancelling } = useMutation({
    mutationFn: () => cancelExecution(repositoryId, selectedJobId!),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["executions", repositoryId] }),
  })

  // Auto-select latest job
  useEffect(() => {
    if (executions.length > 0 && !selectedJobId) {
      setSelectedJobId(executions[0].id)
    }
  }, [executions, selectedJobId])

  // Auto-scroll logs
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [activeJob?.logs?.length])

  const badge = activeJob ? STATUS_BADGES[activeJob.status] : null
  const isRunning = activeJob && !["COMPLETED", "FAILED"].includes(activeJob.status)

  return (
    <div className="flex-1 flex flex-col md:flex-row h-[calc(100vh-64px)] overflow-hidden bg-slate-950">

      {/* Left Sidebar: Execution History */}
      <aside className="w-full md:w-[280px] shrink-0 border-r border-slate-800 bg-slate-900 flex flex-col h-full overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2">
            <Zap className="size-4 text-violet-400" />
            Execution History
          </h2>
          <button
            onClick={() => queryClient.invalidateQueries({ queryKey: ["executions", repositoryId] })}
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <RefreshCw className="size-3.5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {loadingList ? (
            <div className="animate-pulse space-y-2 p-2">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-16 bg-slate-800 rounded-lg" />
              ))}
            </div>
          ) : executions.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-32 text-center">
              <Container className="size-8 text-slate-700 mb-2" />
              <p className="text-xs text-slate-500">No executions yet</p>
            </div>
          ) : (
            executions.map((job) => {
              const b = STATUS_BADGES[job.status]
              return (
                <button
                  key={job.id}
                  onClick={() => setSelectedJobId(job.id)}
                  className={cn(
                    "w-full text-left p-3 rounded-xl transition-all border",
                    selectedJobId === job.id
                      ? "bg-violet-600/20 border-violet-500/50"
                      : "border-transparent hover:bg-slate-800"
                  )}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className={cn("text-[10px] font-bold px-2 py-0.5 rounded-full", b.cls)}>
                      {b.label}
                    </span>
                    <span className="text-[10px] text-slate-500">
                      {new Date(job.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 truncate font-mono">
                    {job.id.slice(0, 12)}...
                  </p>
                </button>
              )
            })
          )}
        </div>
      </aside>

      {/* Main Console */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {!selectedJobId || !activeJob ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
            <Terminal className="size-16 text-slate-700 mb-4" />
            <h2 className="text-lg font-semibold text-slate-300 mb-2">Execution Console</h2>
            <p className="text-sm text-slate-500 max-w-sm">
              Select an execution job from the sidebar, or approve a patch to trigger a new sandbox run.
            </p>
          </div>
        ) : (
          <div className="flex-1 flex flex-col overflow-hidden">

            {/* Header */}
            <div className="shrink-0 p-4 md:p-6 border-b border-slate-800 flex items-center justify-between gap-4 bg-slate-900">
              <div className="flex items-center gap-3">
                <div className="size-9 rounded-xl bg-violet-600/20 flex items-center justify-center">
                  <Container className="size-5 text-violet-400" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-mono">Job ID: {activeJob.id.slice(0, 16)}...</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    {badge && (
                      <span className={cn("text-[10px] font-bold px-2 py-0.5 rounded-full", badge.cls)}>
                        {isRunning && <Loader2 className="size-2.5 inline mr-1 animate-spin" />}
                        {badge.label}
                      </span>
                    )}
                    {activeJob.started_at && (
                      <span className="text-[10px] text-slate-500 flex items-center gap-1">
                        <Clock className="size-3" />
                        {new Date(activeJob.started_at).toLocaleString()}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {isRunning && (
                  <button
                    onClick={() => cancel()}
                    disabled={isCancelling}
                    className="px-3 py-1.5 rounded-lg border border-red-700 text-red-400 hover:bg-red-900/30 text-xs font-semibold transition-colors flex items-center gap-1.5"
                  >
                    <XCircle className="size-3.5" /> Cancel
                  </button>
                )}
              </div>
            </div>

            {/* Step Timeline */}
            <div className="shrink-0 p-4 md:px-6 border-b border-slate-800 bg-slate-900/60">
              <div className="flex items-center gap-2 overflow-x-auto pb-1">
                {STATUS_STEPS.map((step, idx) => {
                  const state = getStepState(step.id, activeJob.status)
                  const Icon = step.icon
                  return (
                    <div key={step.id} className="flex items-center gap-2 shrink-0">
                      <div className={cn(
                        "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border transition-all",
                        state === "done"    && "bg-emerald-900/40 border-emerald-700 text-emerald-300",
                        state === "active"  && "bg-violet-900/60 border-violet-500 text-violet-200 animate-pulse",
                        state === "failed"  && "bg-red-900/40 border-red-700 text-red-400",
                        state === "pending" && "bg-slate-800/40 border-slate-700 text-slate-500",
                      )}>
                        {state === "done"   && <CheckCircle2 className="size-3" />}
                        {state === "active" && <Loader2 className="size-3 animate-spin" />}
                        {state === "failed" && <AlertOctagon className="size-3" />}
                        {state === "pending" && <Icon className="size-3 opacity-50" />}
                        {step.label}
                      </div>
                      {idx < STATUS_STEPS.length - 1 && (
                        <ChevronRight className="size-3 text-slate-600 shrink-0" />
                      )}
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Terminal Log Output */}
            <div className="flex-1 overflow-y-auto p-4 md:p-6 font-mono text-xs leading-relaxed bg-slate-950">
              {(activeJob.logs ?? []).length === 0 ? (
                <p className="text-slate-600 italic">Waiting for logs...</p>
              ) : (
                (activeJob.logs ?? []).map((log, i) => (
                  <div key={i} className="mb-0.5">
                    <span className="text-slate-600 select-none mr-2">
                      [{log.phase}]
                    </span>
                    <span className={cn(PHASE_COLORS[log.stream] || "text-slate-300", "whitespace-pre-wrap break-all")}>
                      {log.content}
                    </span>
                  </div>
                ))
              )}
              {isRunning && (
                <div className="flex items-center gap-2 mt-2 text-violet-400">
                  <Loader2 className="size-3 animate-spin" />
                  <span className="animate-pulse">Running...</span>
                </div>
              )}
              {activeJob.status === "COMPLETED" && (
                <div className="flex items-center gap-2 mt-4 text-emerald-400 font-bold">
                  <CheckCircle2 className="size-4" />
                  Execution completed successfully.
                </div>
              )}
              {activeJob.status === "FAILED" && (
                <div className="mt-4">
                  <div className="flex items-center gap-2 text-red-400 font-bold mb-1">
                    <XCircle className="size-4" />
                    Execution failed.
                  </div>
                  {activeJob.error_message && (
                    <p className="text-red-500/80 pl-6">{activeJob.error_message}</p>
                  )}
                </div>
              )}
              <div ref={logEndRef} />
            </div>

          </div>
        )}
      </div>
    </div>
  )
}
