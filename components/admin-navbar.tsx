"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { BarChart3, Users, Bike, LogOut } from "lucide-react"

export function AdminNavbar() {
  const router = useRouter()

  const handleLogout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("user_id")
    router.push("/auth/login")
  }

  return (
    <nav className="border-b border-border bg-background sticky top-0 z-40">
      <div className="flex items-center justify-between p-4 max-w-7xl mx-auto">
        <Link href="/admin" className="flex items-center gap-2 text-lg font-bold">
          <BarChart3 className="w-6 h-6" />
          Admin Panel
        </Link>

        <div className="flex items-center gap-6">
          <Link href="/admin">
            <Button variant="ghost" className="gap-2">
              <BarChart3 className="w-4 h-4" />
              Dashboard
            </Button>
          </Link>

          <Link href="/admin/restaurants">
            <Button variant="ghost" className="gap-2">
              <Users className="w-4 h-4" />
              Restaurants
            </Button>
          </Link>

          <Link href="/admin/delivery-agents">
            <Button variant="ghost" className="gap-2">
              <Bike className="w-4 h-4" />
              Delivery Agents
            </Button>
          </Link>

          <Link href="/admin/users">
            <Button variant="ghost" className="gap-2">
              <Users className="w-4 h-4" />
              Users
            </Button>
          </Link>

          <Button onClick={handleLogout} variant="destructive" className="gap-2">
            <LogOut className="w-4 h-4" />
            Logout
          </Button>
        </div>
      </div>
    </nav>
  )
}
