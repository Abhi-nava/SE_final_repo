"use client"

import { useState, useEffect, useRef } from "react"
import { useAuth } from "@/lib/auth-context"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { AuthModal } from "@/components/auth-modal"
import { Utensils, Bike, ChefHat, Star, Zap, Users } from "lucide-react"

export default function Home() {
  const { user, isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const [authOpen, setAuthOpen] = useState(false)
  const [selectedRole, setSelectedRole] = useState<string>("customer")
  const [authMode, setAuthMode] = useState<"login" | "register">("login")
  const hasRedirected = useRef(false)



 useEffect(() => {
  if (isAuthenticated && user) {
    const routes: Record<string, string> = {
      customer: "/customer",
      restaurant: "/restaurant",
      delivery_agent: "/delivery",
      admin: "/admin",
    }

    const path = routes[user.role] || "/"
    console.log(`[v0] Redirecting to ${path} for role ${user.role}`)
    if (window.location.pathname !== path) {
      router.replace(path)
    }
    console.log("[v0] Redirected to:", path)
  }
}, [isAuthenticated, user, router])

  const handleRoleSelect = (role: string, mode: "login" | "register") => {
    setSelectedRole(role)
    setAuthMode(mode)
    setAuthOpen(true)
  }

  const roles = [
    {
      id: "customer",
      title: "Order Food",
      description: "Browse restaurants and order your favorite meals",
      icon: Utensils,
      color: "from-orange-400 to-orange-600",
    },
    {
      id: "restaurant",
      title: "Manage Restaurant",
      description: "Manage your restaurant, menu, and orders",
      icon: ChefHat,
      color: "from-red-400 to-red-600",
    },
    {
      id: "delivery_agent",
      title: "Deliver Orders",
      description: "Join our delivery team and earn money",
      icon: Bike,
      color: "from-green-400 to-green-600",
    },
  ]

  const stats = [
    { label: "Active Restaurants", value: "5000+", icon: ChefHat },
    { label: "Delivery Partners", value: "10K+", icon: Bike },
    { label: "Happy Customers", value: "100K+", icon: Users },
  ]

  const features = [
    { icon: Zap, title: "Fast Delivery", description: "Get your food in 30-45 minutes" },
    { icon: Star, title: "Quality Guaranteed", description: "Verified restaurants and partners" },
    { icon: Utensils, title: "Wide Selection", description: "Thousands of restaurants and cuisines" },
  ]

  if (isLoading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </main>
    )
  }

  if (isAuthenticated && user) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <p>Redirecting...</p>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-background">
      <nav className="border-b border-border">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Utensils className="w-8 h-8 text-primary" />
            <span className="text-2xl font-bold text-foreground">FoodHub</span>
          </div>
          <Button
            onClick={() => {
              setSelectedRole("customer")
              setAuthMode("login")
              setAuthOpen(true)
            }}
            className="bg-primary text-white hover:bg-primary-dark"
          >
            Sign In
          </Button>
        </div>
      </nav>

      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-12">
          <h1 className="text-5xl sm:text-6xl font-bold text-foreground mb-4">
            Food Delivery Made Easy
          </h1>
          <p className="text-xl text-muted mb-8">
            Order from your favorite restaurants and get it delivered hot and fresh
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-20">
          {stats.map((stat) => (
            <Card key={stat.label} className="p-6 text-center">
              <stat.icon className="w-8 h-8 text-primary mx-auto mb-3" />
              <div className="text-3xl font-bold text-foreground mb-1">{stat.value}</div>
              <p className="ttext-sm text-gray-700 dark:text-gray-300">{stat.label}</p>
            </Card>
          ))}
        </div>

        <div className="mb-20">
          <h2 className="text-3xl font-bold text-foreground mb-8 text-center">Get Started</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {roles.map((role) => {
              const Icon = role.icon
              return (
                <Card key={role.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                  <div className={`bg-gradient-to-r ${role.color} h-32 flex items-center justify-center`}>
                    <Icon className="w-16 h-16 text-white" />
                  </div>
                  <div className="p-6">
                    <h3 className="text-xl font-bold text-foreground mb-2">{role.title}</h3>
                    <p className="text-muted mb-6">{role.description}</p>
                    <div className="space-y-2">
                      <Button onClick={() => handleRoleSelect(role.id, "login")} variant="outline" className="w-full">
                        Sign In
                      </Button>
                      <Button
                        onClick={() => handleRoleSelect(role.id, "register")}
                        className="w-full bg-primary text-white hover:bg-primary-dark"
                      >
                        Create Account
                      </Button>
                    </div>
                  </div>
                </Card>
              )
            })}
          </div>
        </div>

        <div className="mb-20">
          <h2 className="text-3xl font-bold text-foreground mb-8 text-center">Why Choose Us?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, idx) => {
              const Icon = feature.icon
              return (
                <div key={idx} className="text-center">
                  <Icon className="w-12 h-12 text-primary mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-foreground mb-2">{feature.title}</h3>
                  <p className="text-muted">{feature.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      <footer className="border-t border-border bg-bg-alt">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center text-muted">
          <p>&copy; 2025 FoodHub. All rights reserved.</p>
        </div>
      </footer>

      <AuthModal open={authOpen} onOpenChange={setAuthOpen} mode={authMode} role={selectedRole} />
    </main>
  )
}
