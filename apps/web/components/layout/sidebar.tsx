"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  FolderOpen,
  GitFork,
  Boxes,
  Zap,
  Settings,
  User,
  ChevronRight,
  X,
} from "lucide-react"
import { cn } from "@/lib/utils"


const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/projects", label: "Projects", icon: FolderOpen },
  { href: "/repositories", label: "Repositories", icon: GitFork },
  { href: "/workspaces", label: "Workspaces", icon: Boxes },
  { href: "/workflows", label: "Workflows", icon: Zap },
]

const bottomNavItems = [
  { href: "/settings", label: "Settings", icon: Settings },
  { href: "/profile", label: "Profile", icon: User },
]

export function Sidebar({ onClose }: { onClose?: () => void }) {
  const pathname = usePathname()

  return (
    <aside className="inset-y-0 left-0 w-64 flex flex-col z-40 h-screen bg-white/60 backdrop-blur-2xl border-r border-slate-200/60 dark:bg-slate-950/80 dark:border-slate-800/60">
      {/* Logo */}
      <div className="h-16 flex items-center justify-between gap-2 px-5 border-b border-slate-200/60 dark:border-slate-800/60">
        <div className="flex items-center gap-2">
          <div className="size-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <span className="text-white font-bold text-sm">F</span>
          </div>
          <span className="text-lg font-bold tracking-tight text-slate-900 dark:text-white">ForgeAI</span>
        </div>
        {onClose && (
          <button onClick={onClose} className="md:hidden p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
            <X className="size-4 text-slate-500" />
          </button>
        )}
      </div>

      {/* Main Nav */}
      <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
        <p className="px-3 py-1 text-[10px] font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-600 mb-2">
          Main
        </p>
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href || pathname.startsWith(href + "/")
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "group flex items-center justify-between gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150",
                isActive
                  ? "bg-indigo-50 text-indigo-600 shadow-sm dark:bg-indigo-500/10 dark:text-indigo-400"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/50 dark:hover:text-slate-50"
              )}
            >
              <span className="flex items-center gap-3">
                <Icon className={cn("size-4.5", isActive ? "text-indigo-500" : "text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300")} />
                {label}
              </span>
              {isActive && <ChevronRight className="size-3.5 text-indigo-400" />}
            </Link>
          )
        })}
      </nav>

      {/* Bottom Nav */}
      <div className="px-3 pb-4 space-y-1 border-t border-slate-200/60 dark:border-slate-800/60 pt-3">
        {bottomNavItems.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150",
                isActive
                  ? "bg-indigo-50 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-400"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/50 dark:hover:text-slate-50"
              )}
            >
              <Icon className={cn("size-4.5", isActive ? "text-indigo-500" : "text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300")} />
              {label}
            </Link>
          )
        })}
      </div>
    </aside>
  )
}
