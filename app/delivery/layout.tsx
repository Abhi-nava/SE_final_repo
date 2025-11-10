"use client"

import type React from "react"

import { useAuth } from "@/lib/auth-context"
import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Utensils, LogOut, Home, Truck, Settings } from "lucide-react"
import Link from "next/link"

export default function DeliveryLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { user, logout, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && (!user || user.role !== "delivery_agent")) {
      router.push("/")
    }
  }, [user, isLoading, router])

  if (isLoading || !user || user.role !== "delivery_agent") {
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
      <div className="fixed left-0 top-0 w-64 h-screen bg-white border-r border-border">
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-2 mb-6">
            <Utensils className="w-6 h-6 text-primary" />
            <span className="text-xl font-bold">FoodFlow</span>
          </div>
          <div className="text-sm">
            <p className="font-semibold">{user.full_name}</p>
            <p className="text-muted text-xs">Delivery Partner</p>
          </div>
        </div>

        <nav className="p-6 space-y-2">
          <Link href="/delivery">
            <Button variant="ghost" className="w-full justify-start gap-2">
              <Home className="w-4 h-4" />
              Dashboard
            </Button>
          </Link>
          <Link href="/delivery/available">
            <Button variant="ghost" className="w-full justify-start gap-2">
              <Truck className="w-4 h-4" />
              Available Orders
            </Button>
          </Link>
          <Link href="/delivery/active">
            <Button variant="ghost" className="w-full justify-start gap-2">
              <Truck className="w-4 h-4" />
              Active Deliveries
            </Button>
          </Link>
          <Link href="/delivery/history">
            <Button variant="ghost" className="w-full justify-start gap-2">
              <Truck className="w-4 h-4" />
              History
            </Button>
          </Link>
          <Link href="/delivery/profile">
            <Button variant="ghost" className="w-full justify-start gap-2">
              <Settings className="w-4 h-4" />
              Profile
            </Button>
          </Link>
        </nav>

        <div className="absolute bottom-6 left-6 right-6">
          <Button onClick={logout} variant="outline" className="w-full justify-start gap-2 text-error bg-transparent">
            <LogOut className="w-4 h-4" />
            Logout
          </Button>
        </div>
      </div>

      <div className="ml-64">
        <div className="p-8">{children}</div>
      </div>
    </div>
  )
}
