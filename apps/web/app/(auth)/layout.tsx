import * as React from "react"
import Link from "next/link"

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen grid grid-cols-1 md:grid-cols-2">
      {/* Left side graphic (Glassmorphism + Gradients) */}
      <div className="hidden md:flex flex-col justify-center items-center relative overflow-hidden bg-slate-950">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/20 via-purple-500/20 to-slate-900/80 z-0" />
        <div className="absolute w-[500px] h-[500px] bg-indigo-500/30 rounded-full blur-[100px] -top-20 -left-20 z-0 animate-pulse" />
        <div className="absolute w-[400px] h-[400px] bg-purple-500/20 rounded-full blur-[80px] bottom-0 right-0 z-0" />
        
        <div className="z-10 text-center max-w-md">
          <h1 className="text-5xl font-bold text-white tracking-tight mb-6">ForgeAI</h1>
          <p className="text-lg text-slate-300">
            Your autonomous software engineering team. Build faster, scale securely, and ship effortlessly.
          </p>
        </div>
      </div>

      {/* Right side forms */}
      <div className="flex flex-col justify-center items-center p-8 bg-slate-50 dark:bg-slate-950 relative">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] z-0" />
        
        <div className="w-full max-w-md z-10">
          <div className="md:hidden text-center mb-8">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">ForgeAI</h1>
          </div>
          {children}
        </div>
      </div>
    </div>
  )
}
