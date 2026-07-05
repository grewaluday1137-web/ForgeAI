"use client"

import { useAuth } from "@/hooks/use-auth"
import { useRouter } from "next/navigation"
import { useState, useRef, useEffect } from "react"
import { LogOut, User, Settings, ChevronDown } from "lucide-react"
import Link from "next/link"
import { cn } from "@/lib/utils"
import { logoutUser } from "@/services/auth"

export function UserNav() {
  const { user, logout } = useAuth()
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  if (!user) return null

  const handleLogout = async () => {
    const { refreshToken } = useAuth.getState()
    try {
      if (refreshToken) await logoutUser(refreshToken)
    } catch { /* best-effort server logout */ }
    logout()
    router.push("/login")
  }

  const initials = user.full_name
    ? user.full_name.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase()
    : user.username.slice(0, 2).toUpperCase()

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2.5 px-2 py-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800/50 transition-colors"
      >
        <div className="size-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold shadow-md ring-2 ring-white dark:ring-slate-900">
          {initials}
        </div>
        <div className="hidden sm:block text-left">
          <p className="text-sm font-semibold leading-none text-slate-900 dark:text-slate-50">
            {user.full_name || user.username}
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{user.email}</p>
        </div>
        <ChevronDown className={cn("size-4 text-slate-400 transition-transform duration-200", open && "rotate-180")} />
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-52 rounded-xl border border-slate-200/60 bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl shadow-xl dark:border-slate-800/60 py-1.5 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
          <div className="px-3 py-2 border-b border-slate-100 dark:border-slate-800 mb-1">
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400">Signed in as</p>
            <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">{user.email}</p>
          </div>
          <Link href="/profile" onClick={() => setOpen(false)} className="flex items-center gap-2.5 px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 mx-1 rounded-lg transition-colors">
            <User className="size-4 text-slate-400" />
            Profile
          </Link>
          <Link href="/settings" onClick={() => setOpen(false)} className="flex items-center gap-2.5 px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 mx-1 rounded-lg transition-colors">
            <Settings className="size-4 text-slate-400" />
            Settings
          </Link>
          <div className="border-t border-slate-100 dark:border-slate-800 mt-1 pt-1">
            <button
              onClick={handleLogout}
              className="flex items-center gap-2.5 px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 mx-1 rounded-lg transition-colors w-full text-left"
            >
              <LogOut className="size-4" />
              Log out
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
