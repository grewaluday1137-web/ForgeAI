"use client"

import { useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  triggerTesterAgent,
  getTestSuites,
  getCoverage,
  getQualityReport,
  getFailures,
} from "@/services/testing"
import { listExecutions } from "@/services/repositories"
import { cn } from "@/lib/utils"
import {
  ShieldCheck, ShieldAlert, Activity, RefreshCw, BarChart, ChevronDown, CheckCircle2, XCircle, FileText, Zap, ChevronRight, Beaker
} from "lucide-react"

export default function QualityDashboardPage() {
  const params = useParams()
  const repositoryId = params.id as string
  const router = useRouter()
  const queryClient = useQueryClient()

  // Get the most recent execution job
  const { data: executions = [] } = useQuery({
    queryKey: ["executions", repositoryId],
    queryFn: () => listExecutions(repositoryId),
  })
  
  const latestJobId = executions.length > 0 ? executions[0].id : null

  const { data: quality, isLoading: loadingQuality } = useQuery({
    queryKey: ["quality", latestJobId],
    queryFn: () => getQualityReport(latestJobId!),
    enabled: !!latestJobId,
  })

  const { data: coverage } = useQuery({
    queryKey: ["coverage", latestJobId],
    queryFn: () => getCoverage(latestJobId!),
    enabled: !!latestJobId,
  })

  const { data: failures = [] } = useQuery({
    queryKey: ["failures", latestJobId],
    queryFn: () => getFailures(latestJobId!),
    enabled: !!latestJobId,
  })

  const { mutate: runTests, isPending: isTesting } = useMutation({
    mutationFn: () => triggerTesterAgent(latestJobId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["quality", latestJobId] })
      queryClient.invalidateQueries({ queryKey: ["failures", latestJobId] })
      queryClient.invalidateQueries({ queryKey: ["coverage", latestJobId] })
    },
  })

  const [expandedFailure, setExpandedFailure] = useState<string | null>(null)

  if (!latestJobId) {
    return (
      <div className="flex-1 p-8 max-w-7xl mx-auto flex flex-col items-center justify-center text-center">
        <Beaker className="size-16 text-slate-700 mb-4" />
        <h2 className="text-xl font-bold text-slate-300">No Executions Found</h2>
        <p className="text-slate-500 mt-2">Run the Developer Agent to generate an execution job before accessing the Quality Dashboard.</p>
      </div>
    )
  }

  return (
    <div className="flex-1 p-6 lg:p-8 max-w-7xl mx-auto w-full space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="size-12 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <ShieldCheck className="size-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Quality Dashboard</h1>
            <p className="text-sm text-slate-500">Autonomous QA & Tester Agent Results</p>
          </div>
        </div>
        <button
          onClick={() => runTests()}
          disabled={isTesting}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 text-white font-semibold shadow-lg shadow-emerald-500/20 transition-all"
        >
          <RefreshCw className={cn("size-4", isTesting && "animate-spin")} />
          {isTesting ? "Running Tests..." : "Trigger QA Pipeline"}
        </button>
      </div>

      {loadingQuality ? (
        <div className="animate-pulse h-64 bg-slate-100 dark:bg-slate-900 rounded-3xl" />
      ) : !quality ? (
        <div className="flex flex-col items-center justify-center h-64 rounded-3xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50">
          <ShieldAlert className="size-10 text-slate-400 mb-2" />
          <p className="text-slate-500 font-medium">No quality report found.</p>
          <p className="text-sm text-slate-400">Trigger the QA pipeline to analyze the latest execution.</p>
        </div>
      ) : (
        <>
          {/* Top Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Score Card */}
            <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 flex flex-col justify-between shadow-sm relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl -mr-10 -mt-10"></div>
              <div>
                <h3 className="text-slate-500 font-semibold mb-1 flex items-center gap-2">
                  <Activity className="size-4" /> Quality Score
                </h3>
                <div className="flex items-end gap-2">
                  <span className={cn(
                    "text-6xl font-black tracking-tight",
                    quality.quality_score >= 80 ? "text-emerald-500" :
                    quality.quality_score >= 50 ? "text-amber-500" : "text-red-500"
                  )}>
                    {Math.round(quality.quality_score)}
                  </span>
                  <span className="text-2xl text-slate-400 font-bold mb-1">/100</span>
                </div>
              </div>
              <div className="mt-4 flex items-center justify-between border-t border-slate-100 dark:border-slate-800 pt-4">
                <span className="text-sm font-medium text-slate-500">Recommendation</span>
                <span className={cn(
                  "px-3 py-1 rounded-full text-xs font-bold",
                  quality.recommendation === "APPROVE" ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400" :
                  quality.recommendation === "RETRY" ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400" :
                  "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                )}>
                  {quality.recommendation}
                </span>
              </div>
            </div>

            {/* Test Summary */}
            <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm">
              <h3 className="text-slate-500 font-semibold mb-4 flex items-center gap-2">
                <Beaker className="size-4" /> Test Results
              </h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-emerald-500">Passed</span>
                    <span className="font-bold">{quality.passed_tests}</span>
                  </div>
                  <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${(quality.passed_tests / (quality.total_tests || 1)) * 100}%` }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-red-500">Failed</span>
                    <span className="font-bold">{quality.failed_tests}</span>
                  </div>
                  <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-red-500 rounded-full" style={{ width: `${(quality.failed_tests / (quality.total_tests || 1)) * 100}%` }}></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Coverage */}
            <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm">
              <h3 className="text-slate-500 font-semibold mb-4 flex items-center gap-2">
                <BarChart className="size-4" /> Coverage
              </h3>
              <div className="flex items-center gap-6">
                <div className="relative size-24 flex items-center justify-center shrink-0">
                  <svg className="size-full -rotate-90" viewBox="0 0 36 36">
                    <path className="text-slate-100 dark:text-slate-800" strokeWidth="3" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    <path className="text-indigo-500" strokeDasharray={`${quality.coverage_score}, 100`} strokeWidth="3" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                  </svg>
                  <span className="absolute text-xl font-bold text-slate-900 dark:text-white">
                    {Math.round(quality.coverage_score)}%
                  </span>
                </div>
                <div className="flex-1 space-y-2">
                  <p className="text-xs text-slate-500">Line Coverage: <span className="font-bold text-slate-900 dark:text-white">{coverage?.line_coverage ?? 0}%</span></p>
                  <p className="text-xs text-slate-500">Branch Coverage: <span className="font-bold text-slate-900 dark:text-white">{coverage?.branch_coverage ?? 0}%</span></p>
                </div>
              </div>
            </div>
            
          </div>

          {/* Failures List */}
          {failures.length > 0 && (
            <div className="rounded-3xl border border-red-200 dark:border-red-900/50 bg-white dark:bg-slate-900 overflow-hidden shadow-sm">
              <div className="p-4 md:p-6 bg-red-50 dark:bg-red-900/10 border-b border-red-100 dark:border-red-900/30 flex items-center gap-3">
                <XCircle className="size-5 text-red-500" />
                <h3 className="text-lg font-bold text-red-900 dark:text-red-400">Failed Tests ({failures.length})</h3>
              </div>
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {failures.map((f, i) => (
                  <div key={i} className="flex flex-col">
                    <button 
                      onClick={() => setExpandedFailure(expandedFailure === f.test_name ? null : f.test_name)}
                      className="p-4 md:p-6 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-800/50 text-left transition-colors"
                    >
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400">
                            {f.category}
                          </span>
                          {f.is_flaky && (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400">
                              FLAKY
                            </span>
                          )}
                          <span className="text-xs text-slate-500 font-mono">{f.suite_file}</span>
                        </div>
                        <p className="font-semibold text-slate-900 dark:text-white font-mono text-sm">{f.test_name}</p>
                      </div>
                      <ChevronDown className={cn("size-5 text-slate-400 transition-transform", expandedFailure === f.test_name && "rotate-180")} />
                    </button>
                    
                    {expandedFailure === f.test_name && (
                      <div className="p-4 md:p-6 bg-slate-50 dark:bg-slate-800/30 space-y-4">
                        <div>
                          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Error Message</p>
                          <div className="bg-slate-950 p-4 rounded-xl text-red-400 font-mono text-xs overflow-x-auto whitespace-pre-wrap">
                            {f.error_message}
                          </div>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
                            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">AI Diagnosed Root Cause</p>
                            <p className="text-sm text-slate-700 dark:text-slate-300">{f.root_cause}</p>
                          </div>
                          <div className="bg-emerald-50 dark:bg-emerald-900/10 p-4 rounded-xl border border-emerald-100 dark:border-emerald-900/30">
                            <p className="text-xs font-bold text-emerald-600 dark:text-emerald-500 uppercase tracking-wider mb-2">Suggested Fix</p>
                            <p className="text-sm text-emerald-800 dark:text-emerald-300">{f.suggested_fix}</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
