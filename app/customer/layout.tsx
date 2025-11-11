"use client"

import type React from "react"

import { useAuth } from "@/lib/auth-context"
import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Utensils, LogOut, Home, ShoppingCart, User } from "lucide-react"
import Link from "next/link"

export default function CustomerLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { user, logout, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && (!user || user.role !== "customer")) {
      router.push("/")
    }
  }, [user, isLoading, router])

  if (isLoading || !user || user.role !== "customer") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar Navigation */}
      <div className="fixed left-0 top-0 w-64 h-screen bg-white border-r border-border">
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-2 mb-6">
            <Utensils className="w-6 h-6 text-primary" />
            <span className="text-xl font-bold">FoodFlow</span>
          </div>
          <div className="text-sm">
            <p className="font-semibold">{user.full_name}</p>
            <p className="dark text-xs">{user.email}</p>
          </div>
        </div>

        <nav className="p-6 space-y-2">
          <Link href="/customer">
            <Button variant="ghost" className="w-full justify-start gap-2">
              <Home className="w-4 h-4" />
              Browse Restaurants
            </Button>
          </Link>
          <Link href="/customer/orders">
            <Button variant="ghost" className="w-full justify-start gap-2">
              <ShoppingCart className="w-4 h-4" />
              My Orders
            </Button>
          </Link>
          <Link href="/customer/profile">
            <Button variant="ghost" className="w-full justify-start gap-2">
              <User className="w-4 h-4" />
              Profile
            </Button>
          </Link>
        </nav>

        <div className="absolute bottom-6 left-6 right-6">
          <Button
            onClick={logout}
            variant="outline"
            className="w-full justify-start gap-2 text-error hover:text-error bg-transparent"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-64">
        <div className="p-8">{children}</div>
      </div>
    </div>
  )
}
