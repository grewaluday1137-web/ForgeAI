"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { loginSchema, LoginInput } from "@/lib/validations/auth"
import { useMutation } from "@tanstack/react-query"
import { loginUser, getMe } from "@/services/auth"
import { useAuth } from "@/hooks/use-auth"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { toast } from "@/hooks/use-toast"
import { useEffect, useState } from "react"

export default function LoginPage() {
  const router = useRouter()
  const setAuth = useAuth((state) => state.setAuth)
  const [mounted, setMounted] = useState(false)
  
  useEffect(() => { setMounted(true) }, [])
  
  const form = useForm<LoginInput>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" }
  })

  const { mutate: login, isPending } = useMutation({
    mutationFn: loginUser,
    onSuccess: async (data) => {
      const user = await getMe(data.access_token)
      setAuth(user, data.access_token, data.refresh_token)
      toast.success("Welcome back!", `Logged in as ${user.email}`)
      router.push("/dashboard")
    },
    onError: (error: Error) => {
      toast.error("Login failed", error.message)
      form.setError("root", { message: error.message })
    }
  })

  return (
    <Card className="border-0 shadow-2xl ring-1 ring-slate-200/50 dark:ring-slate-800/50">
      <CardHeader className="space-y-1 pb-8">
        <CardTitle className="text-3xl font-bold">Welcome back</CardTitle>
        <CardDescription>Enter your email to sign in to your account</CardDescription>
      </CardHeader>
      <CardContent>
        {mounted ? (
          <form onSubmit={form.handleSubmit((data) => login(data))} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="m@example.com" {...form.register("email")} />
              {form.formState.errors.email && (
                <p className="text-sm text-red-500">{form.formState.errors.email.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Password</Label>
                <Link href="/forgot-password" className="text-sm font-medium text-indigo-600 hover:underline dark:text-indigo-400">
                  Forgot password?
                </Link>
              </div>
              <Input id="password" type="password" {...form.register("password")} />
              {form.formState.errors.password && (
                <p className="text-sm text-red-500">{form.formState.errors.password.message}</p>
              )}
            </div>
            {form.formState.errors.root && (
              <p className="text-sm text-red-500 text-center font-medium">{form.formState.errors.root.message}</p>
            )}
            <Button type="submit" className="w-full" disabled={isPending}>
              {isPending ? "Signing in..." : "Sign In"}
            </Button>
          </form>
        ) : (
          <div className="space-y-4 h-[252px] animate-pulse bg-slate-50 dark:bg-slate-900 rounded-lg" />
        )}
      </CardContent>
      <CardFooter className="flex flex-col space-y-4">
        <div className="text-sm text-center text-slate-500 dark:text-slate-400">
          Don't have an account?{" "}
          <Link href="/register" className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">
            Sign up
          </Link>
        </div>
      </CardFooter>
    </Card>
  )
}
