import { FileBox } from "lucide-react"

interface EmptyStateProps {
  title: string
  description: string
  action?: React.ReactNode
  icon?: React.ReactNode
}

export function EmptyState({ title, description, action, icon }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/20">
      <div className="flex items-center justify-center size-12 rounded-full bg-slate-100 dark:bg-slate-800 mb-4 text-slate-500 dark:text-slate-400">
        {icon || <FileBox className="size-6" />}
      </div>
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-1">{title}</h3>
      <p className="text-sm text-slate-500 dark:text-slate-400 mb-6 max-w-sm">{description}</p>
      {action}
    </div>
  )
}
