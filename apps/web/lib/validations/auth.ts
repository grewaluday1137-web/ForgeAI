import * as z from "zod"

const passwordRules = z
  .string()
  .min(8, { message: "Password must be at least 8 characters long." })
  .regex(/[A-Z]/, { message: "Password must contain at least one uppercase letter." })
  .regex(/[a-z]/, { message: "Password must contain at least one lowercase letter." })
  .regex(/\d/, { message: "Password must contain at least one number." })

export const loginSchema = z.object({
  email: z.string().email({ message: "Please enter a valid email address." }),
  password: z.string().min(1, { message: "Password is required." }),
})

export const registerSchema = z.object({
  email: z.string().email({ message: "Please enter a valid email address." }),
  username: z.string().min(3, { message: "Username must be at least 3 characters long." }).max(50).regex(/^[a-zA-Z0-9_]+$/, { message: "Username can only contain letters, numbers, and underscores."}),
  full_name: z.string().min(2, { message: "Full name must be at least 2 characters long." }),
  password: passwordRules,
})

export const forgotPasswordSchema = z.object({
  email: z.string().email({ message: "Please enter a valid email address." }),
})

export const resetPasswordSchema = z.object({
  password: z.string().min(8, { message: "Password must be at least 8 characters long." }),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords do not match.",
  path: ["confirmPassword"],
})

export type LoginInput = z.infer<typeof loginSchema>
export type RegisterInput = z.infer<typeof registerSchema>
export type ForgotPasswordInput = z.infer<typeof forgotPasswordSchema>
export type ResetPasswordInput = z.infer<typeof resetPasswordSchema>
