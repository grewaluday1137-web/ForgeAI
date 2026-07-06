import { apiClient } from "./api"

export interface TestSuite {
  id: string
  file_path: string
  framework: string
  is_generated: boolean
  total_tests: number
}

export interface CoverageReport {
  line_coverage: number
  branch_coverage: number
  function_coverage: number
  raw_data: any
}

export interface FailureAnalysis {
  test_name: string
  suite_file: string
  error_message: string
  category: string
  root_cause: string
  suggested_fix: string
  severity: string
  is_flaky: boolean
}

export interface QualityReport {
  quality_score: number
  pass_rate: number
  coverage_score: number
  recommendation: string
  summary: string
  total_tests: number
  passed_tests: number
  failed_tests: number
}

export async function triggerTesterAgent(jobId: string): Promise<any> {
  return apiClient(`/executions/${jobId}/test`, { method: "POST" })
}

export async function getTestSuites(jobId: string): Promise<TestSuite[]> {
  return apiClient(`/executions/${jobId}/test-suites`)
}

export async function getCoverage(jobId: string): Promise<CoverageReport> {
  return apiClient(`/executions/${jobId}/coverage`)
}

export async function getQualityReport(jobId: string): Promise<QualityReport> {
  return apiClient(`/executions/${jobId}/quality`)
}

export async function getFailures(jobId: string): Promise<FailureAnalysis[]> {
  return apiClient(`/executions/${jobId}/failures`)
}
