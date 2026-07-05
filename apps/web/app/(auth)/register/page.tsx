"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { registerSchema, RegisterInput } from "@/lib/validations/auth"
import { useMutation } from "@tanstack/react-query"
import { registerUser } from "@/services/auth"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { toast } from "@/hooks/use-toast"
import { useEffect, useState } from "react"

export default function RegisterPage() {
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  
  useEffect(() => { setMounted(true) }, [])
  
  const form = useForm<RegisterInput>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: "", username: "", full_name: "", password: "" }
  })

  const { mutate: register, isPending } = useMutation({
    mutationFn: registerUser,
    onSuccess: () => {
      toast.success("Account created!", "Please sign in with your new account.")
      router.push("/login")
    },
    onError: (error: Error) => {
      toast.error("Registration failed", error.message)
      form.setError("root", { message: error.message })
    }
  })

  return (
    <Card className="border-0 shadow-2xl ring-1 ring-slate-200/50 dark:ring-slate-800/50">
      <CardHeader className="space-y-1 pb-6">
        <CardTitle className="text-3xl font-bold">Create an account</CardTitle>
        <CardDescription>Enter your details below to create your account</CardDescription>
      </CardHeader>
      <CardContent>
        {mounted ? (
          <form onSubmit={form.handleSubmit((data) => register(data))} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="m@example.com" {...form.register("email")} />
              {form.formState.errors.email && (
                <p className="text-sm text-red-500">{form.formState.errors.email.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input id="username" placeholder="johndoe" {...form.register("username")} />
              {form.formState.errors.username && (
                <p className="text-sm text-red-500">{form.formState.errors.username.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="full_name">Full Name</Label>
              <Input id="full_name" placeholder="John Doe" {...form.register("full_name")} />
              {form.formState.errors.full_name && (
                <p className="text-sm text-red-500">{form.formState.errors.full_name.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" {...form.register("password")} />
              {form.formState.errors.password && (
                <p className="text-sm text-red-500">{form.formState.errors.password.message}</p>
              )}
            </div>
            {form.formState.errors.root && (
              <p className="text-sm text-red-500 text-center font-medium">{form.formState.errors.root.message}</p>
            )}
            <Button type="submit" className="w-full" disabled={isPending}>
              {isPending ? "Creating account..." : "Create Account"}
            </Button>
          </form>
        ) : (
          <div className="space-y-4 h-[440px] animate-pulse bg-slate-50 dark:bg-slate-900 rounded-lg" />
        )}
      </CardContent>
      <CardFooter>
        <div className="text-sm text-center w-full text-slate-500 dark:text-slate-400">
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">
            Sign in
          </Link>
        </div>
      </CardFooter>
    </Card>
  )
}
