"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { forgotPasswordSchema, ForgotPasswordInput } from "@/lib/validations/auth"
import Link from "next/link"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { useState } from "react"

export default function ForgotPasswordPage() {
  const [isSubmitted, setIsSubmitted] = useState(false)

  const form = useForm<ForgotPasswordInput>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: "" }
  })

  const onSubmit = (data: ForgotPasswordInput) => {
    // Placeholder for actual logic
    setIsSubmitted(true)
  }

  return (
    <Card className="border-0 shadow-2xl ring-1 ring-slate-200/50 dark:ring-slate-800/50">
      <CardHeader className="space-y-1 pb-8">
        <CardTitle className="text-3xl font-bold">Reset Password</CardTitle>
        <CardDescription>
          {isSubmitted 
            ? "Check your email for a reset link." 
            : "Enter your email address and we'll send you a recovery link."}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {!isSubmitted ? (
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="m@example.com" {...form.register("email")} />
              {form.formState.errors.email && (
                <p className="text-sm text-red-500">{form.formState.errors.email.message}</p>
              )}
            </div>
            <Button type="submit" className="w-full">
              Send Reset Link
            </Button>
          </form>
        ) : (
          <Button variant="outline" className="w-full" onClick={() => setIsSubmitted(false)}>
            Send another email
          </Button>
        )}
      </CardContent>
      <CardFooter>
        <div className="text-sm text-center w-full text-slate-500 dark:text-slate-400">
          Remember your password?{" "}
          <Link href="/login" className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">
            Sign in
          </Link>
        </div>
      </CardFooter>
    </Card>
  )
}
