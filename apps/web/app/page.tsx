"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/hooks/use-auth"

export default function Home() {
  const { isAuthenticated } = useAuth()
  const router = useRouter()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return
    if (isAuthenticated) {
      router.replace("/dashboard")
    } else {
      router.replace("/login")
    }
  }, [isAuthenticated, router, mounted])

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
      <div className="size-8 rounded-full border-4 border-indigo-200 border-t-indigo-600 animate-spin" />
    </div>
  )
}
