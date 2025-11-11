// "use client"

// import type React from "react"

// import { useState } from "react"
// import { useAuth } from "@/lib/auth-context"
// import { Button } from "@/components/ui/button"
// import { Input } from "@/components/ui/input"
// import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
// import { useToast } from "@/hooks/use-toast"

// interface AuthModalProps {
//   open: boolean
//   onOpenChange: (open: boolean) => void
//   mode: "login" | "register"
//   role?: string
// }

// async function sha256(str: string): Promise<string> {
//   const encoder = new TextEncoder()
//   const data = encoder.encode(str)
//   const hashBuffer = await crypto.subtle.digest("SHA-256", data)
//   const hashArray = Array.from(new Uint8Array(hashBuffer))
//   return hashArray.map(b => b.toString(16).padStart(2, "0")).join("")
// }

// export function AuthModal({ open, onOpenChange, mode: initialMode, role = "customer" }: AuthModalProps) {
//   const [mode, setMode] = useState<"login" | "register">(initialMode)
//   const [isLoading, setIsLoading] = useState(false)
//   const { login, register } = useAuth()
//   const { toast } = useToast()

//   const [formData, setFormData] = useState({
//     email: "",
//     password: "",
//     fullName: "",
//     phone: "",
//   })

//   const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
//     const { name, value } = e.target
//     setFormData((prev) => ({ ...prev, [name]: value }))
//   }

//   const handleSubmit = async (e: React.FormEvent) => {
//     e.preventDefault()
//     setIsLoading(true)

//     try {
//       console.log("[v0] Submitting auth form", { mode, email: formData.email })
//       if (mode === "login") {
//         await login(formData.email, formData.password)
//       } else {
//         await register(formData.email, formData.password, formData.fullName, formData.phone, role)
//       }

//       toast({
//         title: "Success",
//         description: mode === "login" ? "Logged in successfully" : "Account created successfully",
//       })

//       onOpenChange(false)
//       setFormData({ email: "", password: "", fullName: "", phone: "" })
//     } catch (error: any) {
//       console.error("[v0] Auth error:", error)
//       toast({
//         title: "Error",
//         description: error.message,
//         variant: "destructive",
//       })
//     } finally {
//       setIsLoading(false)
//     }
//   }

//   const handleDevLogin = async (email: string) => {
//     setIsLoading(true)
//     console.log("[v0] Dev login attempt:", email)
//     try {
//       await login(email, "dev")
//       toast({
//         title: "Dev Login Successful",
//         description: `Logged in as ${email}`,
//       })
//       onOpenChange(false)
//     } catch (error: any) {
//       console.error("[v0] Dev login error:", error)
//       toast({
//         title: "Error",
//         description: error.message,
//         variant: "destructive",
//       })
//     } finally {
//       setIsLoading(false)
//     }
//   }

//   const devCredentials = [
//     { email: "customer@dev", role: "Customer" },
//     { email: "restaurant@dev", role: "Restaurant" },
//     { email: "delivery@dev", role: "Delivery Agent" },
//     { email: "admin@dev", role: "Admin" },
//   ]

//   return (
//     <Dialog open={open} onOpenChange={onOpenChange}>
//       <DialogContent className="sm:max-w-[400px]">
//         <DialogHeader>
//           <DialogTitle>{mode === "login" ? "Welcome Back" : "Create Account"}</DialogTitle>
//           <DialogDescription>{mode === "login" ? "Sign in to your account" : `Sign up as ${role}`}</DialogDescription>
//         </DialogHeader>

//         <form onSubmit={handleSubmit} className="space-y-4">
//           {mode === "register" && (
//             <>
//               <Input
//                 placeholder="Full Name"
//                 name="fullName"
//                 value={formData.fullName}
//                 onChange={handleInputChange}
//                 required
//               />
//               <Input
//                 placeholder="Phone"
//                 name="phone"
//                 type="tel"
//                 value={formData.phone}
//                 onChange={handleInputChange}
//                 required
//               />
//             </>
//           )}

//           <Input
//             placeholder="Email"
//             name="email"
//             type="email"
//             value={formData.email}
//             onChange={handleInputChange}
//             required
//           />

//           <Input
//             placeholder="Password"
//             name="password"
//             type="password"
//             value={formData.password}
//             onChange={handleInputChange}
//             required
//           />

//           <Button type="submit" className="w-full" disabled={isLoading}>
//             {isLoading ? "Loading..." : mode === "login" ? "Sign In" : "Create Account"}
//           </Button>

//           <p className="text-center text-sm dark">
//             {mode === "login" ? "Don't have an account?" : "Already have an account?"}
//             <button
//               type="button"
//               onClick={() => setMode(mode === "login" ? "register" : "login")}
//               className="ml-1 text-primary hover:underline"
//             >
//               {mode === "login" ? "Sign up" : "Sign in"}
//             </button>
//           </p>

//           {mode === "login" && (
//             <div className="mt-6 pt-6 border-t border-border">
//               <p className="text-xs dark mb-3 font-semibold">Quick Dev Login (Password: dev)</p>
//               <div className="grid grid-cols-2 gap-2">
//                 {devCredentials.map((cred) => (
//                   <Button
//                     key={cred.email}
//                     type="button"
//                     variant="outline"
//                     size="sm"
//                     disabled={isLoading}
//                     onClick={() => handleDevLogin(cred.email)}
//                     className="text-xs"
//                   >
//                     {cred.role}
//                   </Button>
//                 ))}
//               </div>
//             </div>
//           )}
//         </form>
//       </DialogContent>
//     </Dialog>
//   )
// }


"use client"

import type React from "react"
import { useState } from "react"
import { useAuth } from "@/lib/auth-context"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { useToast } from "@/hooks/use-toast"
import { Utensils, ChefHat, Bike, Shield } from "lucide-react"

// 🔐 SHA-256 hashing helper
async function sha256(str: string): Promise<string> {
  const encoder = new TextEncoder()
  const data = encoder.encode(str)
  const hashBuffer = await crypto.subtle.digest("SHA-256", data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map(b => b.toString(16).padStart(2, "0")).join("")
}

interface AuthModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  mode: "login" | "register"
}

export function AuthModal({ open, onOpenChange, mode: initialMode }: AuthModalProps) {
  const [mode, setMode] = useState<"login" | "register">(initialMode)
  const [isLoading, setIsLoading] = useState(false)
  const [selectedRole, setSelectedRole] = useState<string>("")
  const { login, register, pending2FA, verify2fa, cancel2fa, updateUser } = useAuth()
  const { toast } = useToast()

  const [formData, setFormData] = useState({
    email: "",
    password: "",
    fullName: "",
    phone: "",
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      console.log("[v0] Submitting auth form", { mode, email: formData.email, role: selectedRole })
      const hashedPassword = await sha256(formData.password)

      if (mode === "login") {
        const status = await login(formData.email, hashedPassword)
        if (status === "2fa") {
          toast({ title: "OTP sent", description: "Enter the 6-digit code. Check backend terminal for now." })
          return
        }
      } else {
        const status = await register(formData.email, hashedPassword, formData.fullName, formData.phone, selectedRole)
        if (status === "2fa") {
          toast({ title: "OTP sent", description: "Enter the 6-digit code. Check backend terminal for now." })
          return
        }
      }

      toast({ title: "Success", description: mode === "login" ? "Logged in successfully" : "Account created successfully" })

      onOpenChange(false)
      setSelectedRole("")
      setFormData({ email: "", password: "", fullName: "", phone: "" })
    } catch (error: any) {
      console.error("[v0] Auth error:", error)
      toast({
        title: "Error",
        description: error.message || "Something went wrong",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const [otp, setOtp] = useState("")
  const [isForgot, setIsForgot] = useState(false)
  const [forgotStep, setForgotStep] = useState<"email" | "otp" | "newpass">("email")
  const [resetTempToken, setResetTempToken] = useState<string | null>(null)
  const [resetSessionToken, setResetSessionToken] = useState<string | null>(null)
  const [newPass, setNewPass] = useState("")
  const [confirmPass, setConfirmPass] = useState("")
  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    try {
      if (isForgot) {
        const res = await fetch("http://localhost:8000/api/auth/forgot-password/verify", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ reset_temp_token: resetTempToken, otp }),
        })
        if (!res.ok) {
          const err = await res.json().catch(() => ({}))
          throw new Error(err.detail || "Invalid OTP")
        }
        const data = await res.json()
        setResetSessionToken(data.reset_session_token)
        setForgotStep("newpass")
        toast({ title: "OTP verified", description: "Enter a new password." })
      } else {
        await verify2fa(otp)
        toast({ title: "Success", description: "2FA verified. Logged in successfully." })
        onOpenChange(false)
        setSelectedRole("")
        setFormData({ email: "", password: "", fullName: "", phone: "" })
        setOtp("")
      }
    } catch (error: any) {
      toast({ title: "Invalid OTP", description: error.message || "Please try again", variant: "destructive" })
    } finally {
      setIsLoading(false)
    }
  }

  const handleForgotStart = async () => {
    // Require email input
    if (!formData.email) {
      toast({ title: "Email required", description: "Please enter your email first.", variant: "destructive" })
      return
    }
    setIsLoading(true)
    try {
      const res = await fetch("http://localhost:8000/api/auth/forgot-password/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: formData.email }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || "Failed to start reset")
      }
      const data = await res.json()
      setResetTempToken(data.reset_temp_token)
      setIsForgot(true)
      setForgotStep("otp")
      toast({ title: "OTP sent", description: "Enter the 6-digit code sent to your email." })
    } catch (error: any) {
      toast({ title: "Error", description: error.message || "Couldn't start password reset", variant: "destructive" })
    } finally {
      setIsLoading(false)
    }
  }

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    if (newPass.length < 8) {
      toast({ title: "Weak password", description: "Password must be at least 8 characters.", variant: "destructive" })
      return
    }
    if (newPass !== confirmPass) {
      toast({ title: "Passwords do not match", description: "Please re-enter.", variant: "destructive" })
      return
    }
    setIsLoading(true)
    try {
      const res = await fetch("http://localhost:8000/api/auth/forgot-password/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reset_session_token: resetSessionToken, new_password: await sha256(newPass) }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || "Failed to reset password")
      }
      const data = await res.json()
      localStorage.setItem("access_token", data.access_token)
      localStorage.setItem("refresh_token", data.refresh_token)
      if (data.user) {
        updateUser(data.user)
      }
      toast({ title: "Password reset", description: "You're now signed in." })
      onOpenChange(false)
      setSelectedRole("")
      setFormData({ email: "", password: "", fullName: "", phone: "" })
      setOtp("")
      setIsForgot(false)
      setForgotStep("email")
      setResetTempToken(null)
      setResetSessionToken(null)
      setNewPass("")
      setConfirmPass("")
    } catch (error: any) {
      toast({ title: "Error", description: error.message || "Couldn't reset password", variant: "destructive" })
    } finally {
      setIsLoading(false)
    }
  }

  const roles = [
    { id: "customer", name: "Customer", icon: Utensils, color: "text-orange-500" },
    { id: "restaurant", name: "Restaurant", icon: ChefHat, color: "text-red-500" },
    { id: "delivery_agent", name: "Delivery Agent", icon: Bike, color: "text-green-500" },
    { id: "admin", name: "Admin", icon: Shield, color: "text-blue-500" },
  ]

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[400px]">
        <DialogHeader>
          <DialogTitle>
            {selectedRole
              ? mode === "login"
                ? "Welcome Back"
                : "Create Account"
              : "Select Your Role"}
          </DialogTitle>
          <DialogDescription>
            {selectedRole
              ? mode === "login"
                ? "Sign in to your account"
                : `Sign up as ${selectedRole.replace("_", " ")}`
              : "Choose how you want to use FoodFlow"}
          </DialogDescription>
        </DialogHeader>

        {/* Step 1: Role Selection (hidden during OTP step) */}
        {!pending2FA && !selectedRole && (
          <div className="grid grid-cols-1 gap-3">
            {roles.map((role) => {
              const Icon = role.icon
              return (
                <Button
                  key={role.id}
                  variant="outline"
                  onClick={() => setSelectedRole(role.id)}
                  className="flex items-center justify-start gap-3 py-3 border border-border hover:bg-muted transition"
                >
                  <Icon className={`w-6 h-6 ${role.color}`} />
                  <span className="font-medium text-foreground">{role.name}</span>
                </Button>
              )
            })}
          </div>
        )}

        {/* Step 2: Auth Form (hidden during OTP step) */}
        {!pending2FA && selectedRole && !isForgot && (
          <form onSubmit={handleSubmit} className="space-y-4 mt-4">
            {mode === "register" && (
              <>
                <Input
                  placeholder="Full Name"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleInputChange}
                  required
                />
                <Input
                  placeholder="Phone"
                  name="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={handleInputChange}
                  required
                />
              </>
            )}

            <Input
              placeholder="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              required
            />

            <Input
              placeholder="Password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleInputChange}
              required
            />

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Loading..." : mode === "login" ? "Sign In" : "Create Account"}
            </Button>

            {mode === "login" && (
              <div className="text-center">
                <button type="button" className="text-sm text-primary-dark hover:underline" onClick={handleForgotStart}>
                  Forgot Password?
                </button>
              </div>
            )}

            <div className="text-center text-sm dark">
              {mode === "login" ? "Don't have an account?" : "Already have an account?"}{" "}
              <button
                type="button"
                onClick={() => setMode(mode === "login" ? "register" : "login")}
                className="text-primary-dark hover:underline"
              >
                {mode === "login" ? "Sign up" : "Sign in"}
              </button>
            </div>

            <div className="text-center">
              <button
                type="button"
                onClick={() => setSelectedRole("")}
                className="text-xs dark hover:underline mt-2"
              >
                ← Change Role
              </button>
            </div>
          </form>
        )}

        {/* Step 3: OTP Verification */}
        {(pending2FA || (isForgot && forgotStep === "otp")) && (
          <form onSubmit={handleVerifyOtp} className="space-y-4 mt-4">
            <Input
              placeholder={isForgot ? "Enter password reset OTP" : "Enter 6-digit OTP"}
              name="otp"
              type="text"
              inputMode="numeric"
              pattern="[0-9]{6}"
              maxLength={6}
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/[^0-9]/g, ""))}
              required
            />
            <Button type="submit" className="w-full" disabled={isLoading || otp.length !== 6}>
              {isLoading ? "Verifying..." : isForgot ? "Verify Reset OTP" : "Verify OTP"}
            </Button>
            <Button
              type="button"
              variant="outline"
              className="w-full"
              onClick={() => {
                if (isForgot) {
                  setIsForgot(false)
                  setForgotStep("email")
                  setResetTempToken(null)
                  setResetSessionToken(null)
                  setOtp("")
                } else {
                  cancel2fa()
                  setOtp("")
                }
              }}
            >
              ← Back to login
            </Button>
            <p className="text-center text-xs text-muted">
              {isForgot ? "Password reset OTP has been sent to your email. It expires in 5 minutes." : "OTP has been sent to your email. It expires in 5 minutes."}
            </p>
          </form>
        )}

        {isForgot && forgotStep === "newpass" && (
          <form onSubmit={handleResetPassword} className="space-y-4 mt-4">
            <Input
              placeholder="New Password"
              name="new_password"
              type="password"
              value={newPass}
              onChange={(e) => setNewPass(e.target.value)}
              required
            />
            <Input
              placeholder="Confirm New Password"
              name="confirm_password"
              type="password"
              value={confirmPass}
              onChange={(e) => setConfirmPass(e.target.value)}
              required
            />
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Saving..." : "Set New Password"}
            </Button>
            <Button
              type="button"
              variant="outline"
              className="w-full"
              onClick={() => {
                setIsForgot(false)
                setForgotStep("email")
                setResetTempToken(null)
                setResetSessionToken(null)
                setNewPass("")
                setConfirmPass("")
              }}
            >
              ← Cancel
            </Button>
          </form>
        )}
      </DialogContent>
    </Dialog>
  )
}
