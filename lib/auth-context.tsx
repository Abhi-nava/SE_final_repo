"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { useRouter } from "next/navigation"



interface User {
  id: string
  email: string
  full_name: string
  phone: string
  role: "customer" | "restaurant" | "delivery_agent" | "admin"
  address?: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<"2fa" | "done">
  register: (email: string, password: string, fullName: string, phone: string, role: string) => Promise<"2fa" | "done">
  logout: () => void
  updateUser: (user: User) => void
  pending2FA: boolean
  verify2fa: (otp: string) => Promise<void>
  cancel2fa: () => void
}



const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [pending2FA, setPending2FA] = useState(false)
  const [tempToken, setTempToken] = useState<string | null>(null)
  const [pendingEmail, setPendingEmail] = useState<string | null>(null)
  const router = useRouter()

  // Initialize auth on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = localStorage.getItem("access_token")
        console.log("[v0] Initializing auth, token exists:", !!token)
        if (token) {
          const response = await fetch("http://localhost:8000/api/auth/me", {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          })

          console.log("[v0] Auth init response status:", response.status)
          if (response.ok) {
            const userData = await response.json()
            console.log("[v0] User data fetched:", userData)
            setUser(userData)
          } else {
            console.log("[v0] Auth init failed, clearing tokens")
            localStorage.removeItem("access_token")
            localStorage.removeItem("refresh_token")
          }

        }
      } catch (error) {
        console.error("[v0] Auth initialization error:", error)
      } finally {
        setIsLoading(false)
      }
    }

    initAuth()
  }, [])

  const login = async (email: string, password: string): Promise<"2fa" | "done"> => {
    console.log("[v0] Login attempt:", { email })
    const response = await fetch("http://localhost:8000/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({email, password }),
    })

    console.log("[v0] Login response status:", response.status)
    if (!response.ok) {
      const error = await response.json()
      console.error("[v0] Login error:", error)
      throw new Error(error.detail || "Login failed")
    }

    const data = await response.json()
    // 2FA-first response
    if (data?.requires_2fa && data?.temp_token) {
      console.log("[v0] 2FA required, temp token received")
      setPending2FA(true)
      setTempToken(data.temp_token)
      setPendingEmail(email)
      return "2fa"
    }

    // Backward compatibility if server returns tokens directly
    if (data?.access_token && data?.refresh_token && data?.user) {
      console.log("[v0] Login successful, user:", data.user)
      localStorage.setItem("access_token", data.access_token)
      localStorage.setItem("refresh_token", data.refresh_token)
      setUser(data.user)
      return "done"
    }

    throw new Error("Unexpected login response")
  }

  const verify2fa = async (otp: string) => {
    if (!pending2FA || !tempToken) throw new Error("No 2FA session in progress")
    const response = await fetch("http://localhost:8000/api/auth/verify-2fa", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ temp_token: tempToken, otp }),
    })

    if (!response.ok) {
      const error = await response.json()
      console.error("[v0] 2FA verify error:", error)
      throw new Error(error.detail || "2FA verification failed")
    }

    const data = await response.json()
    console.log("[v0] 2FA verification successful, user:", data.user)
    localStorage.setItem("access_token", data.access_token)
    localStorage.setItem("refresh_token", data.refresh_token)
    setUser(data.user)
    setPending2FA(false)
    setTempToken(null)
    setPendingEmail(null)
  }

  const cancel2fa = () => {
    setPending2FA(false)
    setTempToken(null)
    setPendingEmail(null)
  }

  const register = async (email: string, password: string, fullName: string, phone: string, role: string): Promise<"2fa" | "done"> => {
    console.log("[v0] Register attempt:", { email, role })
    const response = await fetch("http://localhost:8000/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, full_name: fullName, phone, role }),
    })

    console.log("[v0] Register response status:", response.status)
    if (!response.ok) {
      const error = await response.json()
      console.error("[v0] Register error:", error)
      throw new Error(error.detail || "Registration failed")
    }

    const data = await response.json()
    if (data?.requires_2fa && data?.temp_token) {
      console.log("[v0] Signup requires 2FA, temp token received")
      setPending2FA(true)
      setTempToken(data.temp_token)
      setPendingEmail(email)
      return "2fa"
    }

    if (data?.access_token && data?.refresh_token && data?.user) {
      console.log("[v0] Registration successful, user:", data.user)
      localStorage.setItem("access_token", data.access_token)
      localStorage.setItem("refresh_token", data.refresh_token)
      setUser(data.user)
      return "done"
    }

    throw new Error("Unexpected register response")
  }

  const logout = () => {
    console.log("[v0] Logout")
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    setUser(null)
    router.push("/")
  }

  const updateUser = (updatedUser: User) => {
    console.log("[v0] Updating user:", updatedUser)
    setUser(updatedUser)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        updateUser,
        pending2FA,
        verify2fa,
        cancel2fa,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within AuthProvider")
  }
  return context
}
