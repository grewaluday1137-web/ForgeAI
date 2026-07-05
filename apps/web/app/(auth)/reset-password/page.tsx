"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { resetPasswordSchema, ResetPasswordInput } from "@/lib/validations/auth"
import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { useState } from "react"

export default function ResetPasswordPage() {
  const [isSuccess, setIsSuccess] = useState(false)

  const form = useForm<ResetPasswordInput>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: { password: "", confirmPassword: "" }
  })

  const onSubmit = (data: ResetPasswordInput) => {
    // Placeholder for actual logic
    setIsSuccess(true)
  }

  return (
    <Card className="border-0 shadow-2xl ring-1 ring-slate-200/50 dark:ring-slate-800/50">
      <CardHeader className="space-y-1 pb-8">
        <CardTitle className="text-3xl font-bold">New Password</CardTitle>
        <CardDescription>
          {isSuccess
            ? "Your password has been successfully reset."
            : "Enter your new password below."}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {!isSuccess ? (
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="password">New Password</Label>
              <Input id="password" type="password" {...form.register("password")} />
              {form.formState.errors.password && (
                <p className="text-sm text-red-500">{form.formState.errors.password.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input id="confirmPassword" type="password" {...form.register("confirmPassword")} />
              {form.formState.errors.confirmPassword && (
                <p className="text-sm text-red-500">{form.formState.errors.confirmPassword.message}</p>
              )}
            </div>
            <Button type="submit" className="w-full">
              Save Password
            </Button>
          </form>
        ) : (
          <Link href="/login" className="w-full">
            <Button className="w-full">Return to Sign In</Button>
          </Link>
        )}
      </CardContent>
    </Card>
  )
}
