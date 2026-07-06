"use client"

import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { toast } from "@/hooks/use-toast"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, X, Zap } from "lucide-react"

import { getProjects, createProject } from "@/services/projects"
import { apiClient } from "@/lib/api-client"

const workflowSchema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters").max(255),
  user_request: z.string().min(10, "Please provide a more detailed request").max(1000),
})

type FormData = z.infer<typeof workflowSchema>

export function CreateWorkflowDialog() {
  const [open, setOpen] = useState(false)
  const queryClient = useQueryClient()
  const router = useRouter()

  useEffect(() => {
    if (open) document.body.style.overflow = "hidden"
    else document.body.style.overflow = ""
    return () => { document.body.style.overflow = "" }
  }, [open])

  const form = useForm<FormData>({
    resolver: zodResolver(workflowSchema),
    defaultValues: { title: "", user_request: "" },
  })

  // The "magic" Quickstart mutation that scaffolds Project -> Repo -> Workspace -> Workflow
  const { mutate, isPending } = useMutation({
    mutationFn: async (data: FormData) => {
      // 1. Get or Create Project
      const projects = await getProjects()
      let projectId = projects?.[0]?.id
      
      if (!projectId) {
        const project = await createProject({
          name: "ForgeAI Demo App",
          description: "Auto-generated project for testing workflows",
          color: "violet",
          visibility: "PRIVATE"
        })
        projectId = project.id
      }

      // 2. Create a dummy repository for the project
      // Note: The backend route is POST /repositories/project/{project_id}
      const repo = await apiClient(`/repositories/project/${projectId}`, {
        method: "POST",
        body: JSON.stringify({
          provider: "GITHUB",
          remote_url: "https://github.com/demo/app",
          default_branch: "main"
        })
      })

      // 3. Create a workspace for the repository
      const workspace = await apiClient(`/workspaces`, {
        method: "POST",
        body: JSON.stringify({
          repository_id: repo.id,
          name: "development",
          description: "Demo workspace",
          type: "development"
        })
      })

      // 4. Create the Workflow!
      const workflow = await apiClient(`/workflows`, {
        method: "POST",
        body: JSON.stringify({
          workspace_id: workspace.id,
          title: data.title,
          user_request: data.user_request,
          status: "CREATED",
          priority: 1
        })
      })

      return workflow
    },
    onSuccess: (workflow) => {
      queryClient.invalidateQueries({ queryKey: ["workflows"] })
      toast.success("Workflow created!", "Scaffolded required workspace and created workflow.")
      setOpen(false)
      form.reset()
      router.push(`/workflows/${workflow.id}`)
    },
    onError: (error: any) => {
      toast.error("Error", error.message)
    },
  })

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-700 text-white text-sm font-semibold shadow-lg shadow-violet-500/30 transition-all duration-150 hover:scale-[1.02] active:scale-[0.98]"
      >
        <Plus className="size-4" />
        Create Workflow
      </button>
    )
  }

  return (
    <>
      <div
        className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200"
        onClick={() => setOpen(false)}
      />

      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
        <div
          className="pointer-events-auto w-full max-w-lg rounded-2xl border border-slate-200/60 dark:border-slate-700/60 bg-white dark:bg-slate-900 shadow-2xl shadow-black/20 animate-in fade-in zoom-in-95 duration-200"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-start justify-between p-6 border-b border-slate-100 dark:border-slate-800">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Zap className="size-5 text-violet-500" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">New Workflow</h2>
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Describe what you want the AI Planner to build or solve.
              </p>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <X className="size-4" />
            </button>
          </div>

          {/* Body */}
          <form onSubmit={form.handleSubmit((data) => mutate(data))}>
            <div className="p-6 space-y-5">

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Title</label>
                <Input
                  placeholder="E.g., Implement Stripe Checkout"
                  {...form.register("title")}
                  className="w-full"
                />
                {form.formState.errors.title && (
                  <p className="text-xs text-red-500">{form.formState.errors.title.message}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Detailed Prompt</label>
                <textarea
                  placeholder="I want to integrate Stripe subscriptions into my Next.js app..."
                  rows={4}
                  {...form.register("user_request")}
                  className="w-full resize-none rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500/50 transition"
                />
                {form.formState.errors.user_request && (
                  <p className="text-xs text-red-500">{form.formState.errors.user_request.message}</p>
                )}
              </div>

            </div>

            {/* Footer */}
            <div className="flex items-center justify-end gap-2 px-6 py-4 border-t border-slate-100 dark:border-slate-800">
              <button
                type="button"
                onClick={() => setOpen(false)}
                disabled={isPending}
                className="px-4 py-2 rounded-xl text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isPending}
                className="inline-flex items-center gap-2 px-5 py-2 rounded-xl bg-violet-600 hover:bg-violet-700 disabled:opacity-60 text-white text-sm font-semibold shadow-lg shadow-violet-500/30 transition-all duration-150 hover:scale-[1.02] active:scale-[0.98]"
              >
                {isPending ? (
                  <>
                    <span className="size-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Initializing…
                  </>
                ) : (
                  "Create & Start Planning"
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  )
}
