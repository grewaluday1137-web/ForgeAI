"use client"

import { UserNav } from "./user-nav"
import { Bell, Search, Menu } from "lucide-react"
import { useState } from "react"
import { cn } from "@/lib/utils"
import { ThemeToggle } from "@/components/ui/theme-toggle"

export function TopNav({ onMenuClick }: { onMenuClick?: () => void }) {
  const [searchFocused, setSearchFocused] = useState(false)
  const [hasNotifications] = useState(true)

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-slate-200/60 bg-white/60 px-4 md:px-6 backdrop-blur-2xl dark:border-slate-800/60 dark:bg-slate-950/60">
      {/* Mobile menu button */}
      <button
        onClick={onMenuClick}
        className="md:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
      >
        <Menu className="size-5 text-slate-600 dark:text-slate-400" />
      </button>

      {/* Search */}
      <div className={cn(
        "flex-1 max-w-md relative transition-all duration-200",
        searchFocused ? "max-w-lg" : ""
      )}>
        <Search className={cn(
          "absolute left-3 top-1/2 -translate-y-1/2 size-4 transition-colors duration-150",
          searchFocused ? "text-indigo-500" : "text-slate-400"
        )} />
        <input
          type="text"
          placeholder="Search projects, workflows, agents..."
          onFocus={() => setSearchFocused(true)}
          onBlur={() => setSearchFocused(false)}
          className={cn(
            "w-full pl-9 pr-4 py-2 rounded-xl border text-sm transition-all duration-200 bg-slate-100/70 dark:bg-slate-800/50 placeholder:text-slate-400 dark:placeholder:text-slate-500 text-slate-900 dark:text-slate-50 outline-none",
            searchFocused
              ? "border-indigo-400 ring-2 ring-indigo-500/20 bg-white dark:bg-slate-900"
              : "border-transparent hover:border-slate-200 dark:hover:border-slate-700"
          )}
        />
        <kbd className={cn(
          "absolute right-3 top-1/2 -translate-y-1/2 hidden sm:inline-flex items-center gap-1 px-1.5 py-0.5 text-[10px] font-medium text-slate-400 border border-slate-200 dark:border-slate-700 rounded transition-opacity",
          searchFocused ? "opacity-0" : "opacity-100"
        )}>
          ⌘K
        </kbd>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Right side actions */}
      <div className="flex items-center gap-2">
        {/* Notifications */}
        <button className="relative p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors group">
          <Bell className="size-5 text-slate-500 group-hover:text-slate-700 dark:text-slate-400 dark:group-hover:text-slate-200 transition-colors" />
          {hasNotifications && (
            <span className="absolute top-1.5 right-1.5 size-2 rounded-full bg-indigo-500 ring-2 ring-white dark:ring-slate-950">
              <span className="absolute inset-0 rounded-full bg-indigo-400 animate-ping opacity-75" />
            </span>
          )}
        </button>

        {/* Divider */}
        <div className="w-px h-6 bg-slate-200 dark:bg-slate-700 mx-1" />
        <ThemeToggle />
        <div className="w-px h-6 bg-slate-200 dark:bg-slate-700 mx-1" />
        {/* Profile Menu */}
        <UserNav />
      </div>
    </header>
  )
}
