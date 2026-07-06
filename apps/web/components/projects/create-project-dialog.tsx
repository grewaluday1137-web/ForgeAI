"use client"

import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { createProject } from "@/services/projects"
import { toast } from "@/hooks/use-toast"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, X } from "lucide-react"

const projectSchema = z.object({
  name: z.string().min(3, "Name must be at least 3 characters").max(60),
  description: z.string().max(500).optional(),
  color: z.enum(["violet", "blue", "cyan", "emerald", "orange", "rose", "amber"]),
  visibility: z.enum(["PRIVATE", "TEAM", "PUBLIC"]),
})

type FormData = z.infer<typeof projectSchema>

const COLORS = ["violet", "blue", "cyan", "emerald", "orange", "rose", "amber"] as const
const COLOR_CLASSES: Record<string, string> = {
  violet: "bg-gradient-to-br from-violet-500 to-fuchsia-600",
  blue:   "bg-gradient-to-br from-blue-500 to-indigo-600",
  cyan:   "bg-gradient-to-br from-cyan-400 to-blue-500",
  emerald:"bg-gradient-to-br from-emerald-400 to-teal-500",
  orange: "bg-gradient-to-br from-orange-400 to-amber-500",
  rose:   "bg-gradient-to-br from-rose-400 to-pink-500",
  amber:  "bg-gradient-to-br from-amber-400 to-orange-500",
}

export function CreateProjectDialog() {
  const [open, setOpen] = useState(false)
  const queryClient = useQueryClient()

  // Lock body scroll when modal is open
  useEffect(() => {
    if (open) document.body.style.overflow = "hidden"
    else document.body.style.overflow = ""
    return () => { document.body.style.overflow = "" }
  }, [open])

  const form = useForm<FormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: { name: "", description: "", color: "violet", visibility: "PRIVATE" },
  })

  const selectedColor = form.watch("color")
  const selectedVisibility = form.watch("visibility")

  const { mutate, isPending } = useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] })
      toast.success("Project created!", "Your new project is ready.")
      setOpen(false)
      form.reset()
    },
    onError: (error: any) => {
      toast.error("Error", error.message)
    },
  })

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold shadow-lg shadow-indigo-500/30 transition-all duration-150 hover:scale-[1.02] active:scale-[0.98]"
      >
        <Plus className="size-4" />
        New Project
      </button>
    )
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200"
        onClick={() => setOpen(false)}
      />

      {/* Modal Panel */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
        <div
          className="pointer-events-auto w-full max-w-md rounded-2xl border border-slate-200/60 dark:border-slate-700/60 bg-white dark:bg-slate-900 shadow-2xl shadow-black/20 animate-in fade-in zoom-in-95 duration-200"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-start justify-between p-6 border-b border-slate-100 dark:border-slate-800">
            <div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">Create New Project</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
                A project organises your repositories, workspaces, and agents.
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

              {/* Name */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Project Name</label>
                <Input
                  placeholder="E.g., Forge AI"
                  {...form.register("name")}
                  className="w-full"
                />
                {form.formState.errors.name && (
                  <p className="text-xs text-red-500">{form.formState.errors.name.message}</p>
                )}
              </div>

              {/* Description */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Description <span className="text-slate-400">(optional)</span></label>
                <textarea
                  placeholder="What are you building?"
                  rows={3}
                  {...form.register("description")}
                  className="w-full resize-none rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition"
                />
              </div>

              {/* Color Picker */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Theme Color</label>
                <div className="flex items-center gap-2 flex-wrap">
                  {COLORS.map((c) => (
                    <button
                      key={c}
                      type="button"
                      onClick={() => form.setValue("color", c)}
                      className={`size-7 rounded-full ${COLOR_CLASSES[c]} transition-all duration-150 ${
                        selectedColor === c
                          ? "ring-2 ring-offset-2 ring-slate-900 dark:ring-white scale-110"
                          : "opacity-60 hover:opacity-100 hover:scale-110"
                      }`}
                      title={c}
                    />
                  ))}
                </div>
              </div>

              {/* Visibility */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Visibility</label>
                <div className="flex gap-2">
                  {(["PRIVATE", "TEAM", "PUBLIC"] as const).map((v) => (
                    <button
                      key={v}
                      type="button"
                      onClick={() => form.setValue("visibility", v)}
                      className={`flex-1 py-2 rounded-xl text-xs font-semibold border transition-all duration-150 ${
                        selectedVisibility === v
                          ? "bg-indigo-600 border-indigo-600 text-white shadow-lg shadow-indigo-500/20"
                          : "border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-600"
                      }`}
                    >
                      {v.charAt(0) + v.slice(1).toLowerCase()}
                    </button>
                  ))}
                </div>
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
                className="inline-flex items-center gap-2 px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white text-sm font-semibold shadow-lg shadow-indigo-500/30 transition-all duration-150 hover:scale-[1.02] active:scale-[0.98]"
              >
                {isPending ? (
                  <>
                    <span className="size-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Creating…
                  </>
                ) : (
                  "Create Project"
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  )
}

