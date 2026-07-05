"use client"

import { useState, useEffect } from "react"
import { Moon, Sun, Monitor } from "lucide-react"
import { cn } from "@/lib/utils"

type Theme = "light" | "dark" | "system"

function getSystemTheme(): "light" | "dark" {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"
}

function applyTheme(theme: Theme) {
  const root = document.documentElement
  const resolved = theme === "system" ? getSystemTheme() : theme
  root.classList.toggle("dark", resolved === "dark")
  localStorage.setItem("forgeai-theme", theme)
}

export function ThemeToggle({ compact = false }: { compact?: boolean }) {
  const [theme, setTheme] = useState<Theme>("dark")
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    const stored = (localStorage.getItem("forgeai-theme") as Theme) || "dark"
    setTheme(stored)
    applyTheme(stored)
    setMounted(true)
  }, [])

  const cycle = () => {
    const next: Record<Theme, Theme> = { light: "dark", dark: "system", system: "light" }
    const newTheme = next[theme]
    setTheme(newTheme)
    applyTheme(newTheme)
  }

  if (!mounted) return <div className="size-9 rounded-xl" />

  const icons = { light: Sun, dark: Moon, system: Monitor }
  const Icon = icons[theme]

  return (
    <button
      onClick={cycle}
      title={`Theme: ${theme}`}
      className={cn(
        "p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800/50 transition-colors",
        "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
      )}
    >
      <Icon className="size-4.5" />
    </button>
  )
}

// Script for <head> to prevent flash of unstyled content
export const themeScript = `
(function() {
  try {
    var t = localStorage.getItem('forgeai-theme') || 'dark';
    var d = t === 'system'
      ? window.matchMedia('(prefers-color-scheme: dark)').matches
      : t === 'dark';
    if (d) document.documentElement.classList.add('dark');
  } catch(e) {
    document.documentElement.classList.add('dark');
  }
})();
`
