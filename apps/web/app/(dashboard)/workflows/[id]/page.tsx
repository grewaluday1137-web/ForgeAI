"use client"

import { useState, useEffect, useRef } from "react"
import { useParams } from "next/navigation"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  getWorkflowStatus, getWorkflowPlan, triggerPlan, getAgentRegistry,
  type ExecutionPlanTask, type AgentInfo
} from "@/services/workflows"
import { useWorkflowEvents } from "@/hooks/use-workflow-events"
import { toast } from "@/hooks/use-toast"
import {
  Zap, CheckCircle2, XCircle, Clock, Loader2, Activity,
  ChevronRight, AlertTriangle, Info, Wifi, WifiOff,
  Brain, Code2, TestTube, ShieldCheck, FileText, Search, Rocket, GitBranch
} from "lucide-react"
import { cn } from "@/lib/utils"

const AGENT_ICONS: Record<string, React.ReactNode> = {
  PLANNER:       <Brain className="size-4" />,
  ARCHITECT:     <Search className="size-4" />,
  DEVELOPER:     <Code2 className="size-4" />,
  TESTER:        <TestTube className="size-4" />,
  SECURITY:      <ShieldCheck className="size-4" />,
  DOCUMENTATION: <FileText className="size-4" />,
  REVIEWER:      <GitBranch className="size-4" />,
  DEPLOYMENT:    <Rocket className="size-4" />,
}

const AGENT_COLORS: Record<string, string> = {
  PLANNER:       "from-violet-500 to-fuchsia-600",
  ARCHITECT:     "from-blue-500 to-indigo-600",
  DEVELOPER:     "from-cyan-400 to-blue-500",
  TESTER:        "from-emerald-400 to-teal-500",
  SECURITY:      "from-orange-400 to-red-500",
  DOCUMENTATION: "from-amber-400 to-orange-500",
  REVIEWER:      "from-pink-400 to-rose-500",
  DEPLOYMENT:    "from-slate-400 to-slate-600",
}

const COMPLEXITY_COLOR: Record<string, string> = {
  LOW:      "text-emerald-500",
  MEDIUM:   "text-amber-500",
  HIGH:     "text-orange-500",
  CRITICAL: "text-red-500",
}

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

const EVENT_COLORS: Record<string, string> = {
  INFO:     "text-blue-500",
  WARNING:  "text-amber-500",
  ERROR:    "text-red-500",
  CRITICAL: "text-red-600",
  DEBUG:    "text-slate-400",
}

export default function WorkflowDetailPage() {
  const params = useParams()
  const workflowId = params.id as string
  const queryClient = useQueryClient()
  const [userRequest, setUserRequest] = useState("")
  const [hasPlan, setHasPlan] = useState(false)
  const eventScrollRef = useRef<HTMLDivElement>(null)

  // Queries
  const { data: status, refetch: refetchStatus } = useQuery({
    queryKey: ["workflow-status", workflowId],
    queryFn: () => getWorkflowStatus(workflowId),
    refetchInterval: 3000, // poll every 3s while running
  })

  const { data: plan, refetch: refetchPlan } = useQuery({
    queryKey: ["workflow-plan", workflowId],
    queryFn: () => getWorkflowPlan(workflowId),
    retry: false,
    enabled: hasPlan,
  })

  const { data: agents } = useQuery({
    queryKey: ["agent-registry"],
    queryFn: getAgentRegistry,
  })

  // Real-time WebSocket events
  const { events, connected } = useWorkflowEvents(workflowId)

  // Auto-scroll event log
  useEffect(() => {
    if (eventScrollRef.current) {
      eventScrollRef.current.scrollTop = eventScrollRef.current.scrollHeight
    }
  }, [events])

  // Refetch status and plan when planning completes
  useEffect(() => {
    const completionEvents = ["workflow.ready", "workflow.failed", "agent.planner.completed"]
    const latest = events[events.length - 1]
    if (latest && completionEvents.includes(latest.event)) {
      refetchStatus()
      setHasPlan(true)
      refetchPlan()
    }
  }, [events, refetchStatus, refetchPlan])

  useEffect(() => {
    if (status?.status === "READY" || status?.status === "COMPLETED") {
      setHasPlan(true)
    }
  }, [status])

  // Trigger planning
  const { mutate: startPlan, isPending: isStarting } = useMutation({
    mutationFn: () => triggerPlan(workflowId, "", userRequest || status?.title || ""),
    onSuccess: () => {
      toast.success("Planning started!", "The Planner Agent is analyzing your request.")
      refetchStatus()
    },
    onError: (err: any) => {
      toast.error("Error", err.message)
    },
  })

  const isPlanning = status?.status === "PLANNING"
  const canPlan = status?.status === "CREATED" || status?.status === "FAILED"

  return (
    <div className="flex-1 p-6 lg:p-8 max-w-7xl mx-auto w-full space-y-6">

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <Zap className="size-6 text-violet-500" />
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
              {status?.title || "Workflow"}
            </h1>
            {status && (
              <span className={cn("px-2.5 py-0.5 rounded-full text-xs font-semibold", STATUS_COLORS[status.status])}>
                {status.status.replace(/_/g, " ")}
              </span>
            )}
          </div>
          {status?.user_request && (
            <p className="text-sm text-slate-500 dark:text-slate-400 max-w-2xl pl-9">
              "{status.user_request}"
            </p>
          )}
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

          {canPlan && (
            <button
              onClick={() => startPlan()}
              disabled={isStarting}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-700 disabled:opacity-60 text-white text-sm font-semibold shadow-lg shadow-violet-500/30 transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              {isStarting ? <Loader2 className="size-4 animate-spin" /> : <Brain className="size-4" />}
              {isStarting ? "Starting..." : "Start Planning"}
            </button>
          )}
          {isPlanning && (
            <div className="flex items-center gap-2 text-sm text-violet-600 dark:text-violet-400 font-medium">
              <Loader2 className="size-4 animate-spin" />
              Planner is thinking...
            </div>
          )}
        </div>
      </div>

      {/* Agent Pipeline */}
      <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-5">
        <h2 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-4">Agent Pipeline</h2>
        <div className="flex flex-wrap gap-3">
          {(agents || []).map((agent: AgentInfo, i: number) => {
            const isActive = agent.active
            const gradient = AGENT_COLORS[agent.agent_type] || "from-slate-400 to-slate-500"
            return (
              <div key={agent.agent_type} className="flex items-center gap-2">
                <div className={cn(
                  "flex items-center gap-2 px-3 py-2 rounded-xl border transition-all",
                  isActive
                    ? "border-transparent bg-gradient-to-br text-white shadow-sm " + gradient
                    : "border-slate-200 dark:border-slate-700 text-slate-400 dark:text-slate-600 bg-slate-50 dark:bg-slate-900/50"
                )}>
                  <span className={isActive ? "text-white" : "text-slate-400"}>
                    {AGENT_ICONS[agent.agent_type]}
                  </span>
                  <span className="text-xs font-semibold">
                    {agent.agent_type.charAt(0) + agent.agent_type.slice(1).toLowerCase()}
                  </span>
                  {!isActive && <span className="text-[10px] opacity-60">Soon</span>}
                </div>
                {i < (agents?.length ?? 0) - 1 && (
                  <ChevronRight className="size-3 text-slate-300 dark:text-slate-700 flex-shrink-0" />
                )}
              </div>
            )
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Plan + Tasks */}
        <div className="lg:col-span-2 space-y-6">

          {/* Execution Plan */}
          {plan ? (
            <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-base font-semibold text-slate-900 dark:text-white">Execution Plan</h2>
                <span className={cn("text-sm font-bold", COMPLEXITY_COLOR[plan.estimated_complexity])}>
                  {plan.estimated_complexity} complexity
                </span>
              </div>

              <div>
                <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-1">Objective</p>
                <p className="text-sm text-slate-700 dark:text-slate-300">{plan.objective}</p>
              </div>

              <div>
                <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-1">Scope</p>
                <p className="text-sm text-slate-700 dark:text-slate-300">{plan.scope}</p>
              </div>

              {plan.assumptions.length > 0 && (
                <div>
                  <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-2">Assumptions</p>
                  <ul className="space-y-1">
                    {plan.assumptions.map((a, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                        <Info className="size-3.5 mt-0.5 text-blue-400 flex-shrink-0" />
                        {a}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {plan.risks.length > 0 && (
                <div>
                  <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-2">Risks</p>
                  <ul className="space-y-1">
                    {plan.risks.map((r, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                        <AlertTriangle className="size-3.5 mt-0.5 text-amber-400 flex-shrink-0" />
                        {r}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/20 p-8 text-center">
              <Brain className="size-8 text-slate-300 dark:text-slate-700 mx-auto mb-3" />
              <p className="text-sm font-medium text-slate-500">No execution plan yet</p>
              <p className="text-xs text-slate-400 mt-1">Click "Start Planning" to run the Planner Agent</p>
            </div>
          )}

          {/* Task Graph */}
          {plan && plan.ordered_tasks.length > 0 && (
            <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-6">
              <h2 className="text-base font-semibold text-slate-900 dark:text-white mb-4">
                Task Graph — {plan.ordered_tasks.length} tasks
              </h2>
              <div className="space-y-2">
                {plan.ordered_tasks.map((task: ExecutionPlanTask) => {
                  const gradient = AGENT_COLORS[task.agent_type] || "from-slate-400 to-slate-500"
                  return (
                    <div
                      key={task.order}
                      className="flex items-start gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800"
                    >
                      <div className={cn(
                        "size-8 rounded-lg bg-gradient-to-br flex items-center justify-center text-white flex-shrink-0 shadow-sm",
                        gradient
                      )}>
                        <span className="text-xs font-bold">{task.order}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <p className="text-sm font-medium text-slate-900 dark:text-white">{task.title}</p>
                          <span className="px-1.5 py-0.5 rounded-md bg-slate-100 dark:bg-slate-700 text-xs text-slate-500 dark:text-slate-400">
                            {task.agent_type}
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">{task.description}</p>
                        {task.dependencies.length > 0 && (
                          <div className="flex items-center gap-1 mt-1 flex-wrap">
                            <span className="text-[10px] text-slate-400">Needs:</span>
                            {task.dependencies.map((dep, di) => (
                              <span key={di} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-700 text-slate-500 dark:text-slate-400">{dep}</span>
                            ))}
                          </div>
                        )}
                      </div>
                      <Clock className="size-4 text-slate-300 dark:text-slate-600 flex-shrink-0 mt-1" />
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>

        {/* Right: Live Event Stream */}
        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-5 flex flex-col" style={{ height: "600px" }}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                <Activity className="size-4 text-violet-500" />
                Live Events
              </h2>
              <span className="text-xs text-slate-400">{events.length} events</span>
            </div>

            <div
              ref={eventScrollRef}
              className="flex-1 overflow-y-auto space-y-2 pr-1 scrollbar-thin"
            >
              {events.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-slate-400">
                  <Activity className="size-6 mb-2 opacity-30" />
                  <p className="text-xs">Waiting for events...</p>
                </div>
              ) : (
                events.map((evt, i) => (
                  <div key={i} className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800/50">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] font-mono font-semibold text-violet-600 dark:text-violet-400">
                        {evt.event}
                      </span>
                      <span className="text-[10px] text-slate-400">
                        {new Date(evt.receivedAt).toLocaleTimeString()}
                      </span>
                    </div>
                    {evt.data?.message && (
                      <p className="text-xs text-slate-600 dark:text-slate-400">
                        {String(evt.data.message)}
                      </p>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Stats */}
          {status && (
            <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 p-5 space-y-3">
              <h2 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-widest">Progress</h2>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600 dark:text-slate-400">Tasks</span>
                  <span className="font-semibold text-slate-900 dark:text-white">
                    {status.completed_tasks} / {status.task_count}
                  </span>
                </div>
                <div className="h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-violet-500 to-fuchsia-600 transition-all duration-500"
                    style={{ width: status.task_count ? `${(status.completed_tasks / status.task_count) * 100}%` : "0%" }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
