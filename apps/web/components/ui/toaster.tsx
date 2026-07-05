"use client"

import { useToastStore, type ToastType } from "@/hooks/use-toast"
import { X, CheckCircle2, AlertCircle, AlertTriangle, Info } from "lucide-react"
import { cn } from "@/lib/utils"

const icons: Record<ToastType, React.ReactNode> = {
  success: <CheckCircle2 className="size-5 text-emerald-500" />,
  error: <AlertCircle className="size-5 text-red-500" />,
  warning: <AlertTriangle className="size-5 text-amber-500" />,
  info: <Info className="size-5 text-blue-500" />,
}

const styles: Record<ToastType, string> = {
  success: "border-emerald-200/60 dark:border-emerald-800/40 bg-emerald-50/90 dark:bg-emerald-950/80",
  error: "border-red-200/60 dark:border-red-800/40 bg-red-50/90 dark:bg-red-950/80",
  warning: "border-amber-200/60 dark:border-amber-800/40 bg-amber-50/90 dark:bg-amber-950/80",
  info: "border-blue-200/60 dark:border-blue-800/40 bg-blue-50/90 dark:bg-blue-950/80",
}

export function Toaster() {
  const { toasts, removeToast } = useToastStore()

  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 w-full max-w-sm">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={cn(
            "flex items-start gap-3 p-4 rounded-xl border backdrop-blur-xl shadow-xl",
            "animate-in slide-in-from-right-4 fade-in duration-300",
            styles[toast.type]
          )}
        >
          <span className="mt-0.5 shrink-0">{icons[toast.type]}</span>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-slate-900 dark:text-slate-50">{toast.title}</p>
            {toast.description && (
              <p className="text-sm text-slate-600 dark:text-slate-400 mt-0.5">{toast.description}</p>
            )}
          </div>
          <button
            onClick={() => removeToast(toast.id)}
            className="shrink-0 p-0.5 rounded-md hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
          >
            <X className="size-3.5 text-slate-500" />
          </button>
        </div>
      ))}
    </div>
  )
}
