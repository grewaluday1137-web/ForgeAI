import { cn } from "@/lib/utils"

interface SkeletonProps {
  className?: string
  lines?: number
}

export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn("skeleton rounded-lg", className)}
      aria-hidden="true"
    />
  )
}

export function SkeletonCard() {
  return (
    <div className="rounded-2xl border border-slate-200/50 dark:border-slate-800/50 bg-white/70 dark:bg-slate-950/70 p-6 space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="size-8 rounded-lg" />
      </div>
      <Skeleton className="h-8 w-20" />
      <Skeleton className="h-3 w-40" />
    </div>
  )
}

export function SkeletonDashboard() {
  return (
    <div className="space-y-8 animate-fade-in">
      <div className="space-y-2">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-96" />
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <div className="col-span-4 rounded-2xl border border-slate-200/50 dark:border-slate-800/50 bg-white/70 dark:bg-slate-950/70 p-6 space-y-4">
          <Skeleton className="h-5 w-36" />
          <Skeleton className="h-[250px] w-full rounded-xl" />
        </div>
        <div className="col-span-3 rounded-2xl border border-slate-200/50 dark:border-slate-800/50 bg-white/70 dark:bg-slate-950/70 p-6 space-y-6">
          <Skeleton className="h-5 w-28" />
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="flex items-center gap-3">
              <Skeleton className="size-3 rounded-full" />
              <Skeleton className="h-4 flex-1" />
              <Skeleton className="h-4 w-20" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
