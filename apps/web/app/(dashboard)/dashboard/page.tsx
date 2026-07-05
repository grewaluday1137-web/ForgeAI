"use client"

import { useAuth } from "@/hooks/use-auth"
import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { SkeletonDashboard } from "@/components/ui/skeleton"
import { Activity, CreditCard, DollarSign, Users } from "lucide-react"

export default function DashboardPage() {
  const { user } = useAuth()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const t = setTimeout(() => setIsLoading(false), 800)
    return () => clearTimeout(t)
  }, [])

  if (isLoading) return <SkeletonDashboard />

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 ease-out">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
          Welcome back, {user?.full_name || user?.username}!
        </h2>
        <p className="text-slate-500 dark:text-slate-400 mt-2">
          Here is an overview of your AI engineering environment.
        </p>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Workflows</CardTitle>
            <Activity className="size-4 text-slate-500 dark:text-slate-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-slate-500 dark:text-slate-400">+2 from last week</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
            <Users className="size-4 text-slate-500 dark:text-slate-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">4</div>
            <p className="text-xs text-emerald-500">All systems operational</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compute Hours</CardTitle>
            <CreditCard className="size-4 text-slate-500 dark:text-slate-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">142.5h</div>
            <p className="text-xs text-slate-500 dark:text-slate-400">+19% from last month</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Credits Used</CardTitle>
            <DollarSign className="size-4 text-slate-500 dark:text-slate-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$240.00</div>
            <p className="text-xs text-slate-500 dark:text-slate-400">Next billing on Jul 15</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Your agents have made 24 code commits today.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[250px] flex items-center justify-center text-slate-500 bg-slate-100/50 dark:bg-slate-900/50 rounded-xl border border-slate-200/50 dark:border-slate-800/50">
              Activity Chart Placeholder
            </div>
          </CardContent>
        </Card>
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>System Status</CardTitle>
            <CardDescription>Current health of your services.</CardDescription>
          </CardHeader>
          <CardContent>
             <div className="space-y-6 mt-4">
                <div className="flex items-center">
                  <span className="relative flex size-3 mr-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full size-3 bg-emerald-500"></span>
                  </span>
                  <span className="text-sm font-medium">Core API</span>
                  <span className="ml-auto text-sm text-slate-500">99.9% Uptime</span>
                </div>
                <div className="flex items-center">
                  <span className="relative flex size-3 mr-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full size-3 bg-emerald-500"></span>
                  </span>
                  <span className="text-sm font-medium">PostgreSQL Database</span>
                  <span className="ml-auto text-sm text-slate-500">99.9% Uptime</span>
                </div>
                <div className="flex items-center">
                  <span className="relative flex size-3 mr-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full size-3 bg-emerald-500"></span>
                  </span>
                  <span className="text-sm font-medium">Redis Cache</span>
                  <span className="ml-auto text-sm text-slate-500">99.9% Uptime</span>
                </div>
             </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
