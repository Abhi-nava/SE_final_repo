"use client"

import { useState, useEffect } from "react"
// import { restaurantsAPI, ordersAPI } from "@/lib/api"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { Plus, TrendingUp, ShoppingBag, Clock } from "lucide-react"
import Link from "next/link"

interface RestaurantData {
  id: string
  name: string
  phone: string
  address: string
  opening_time: string
  closing_time: string
  is_active: boolean
}

interface OrderSummary {
  total_orders: number
  pending_orders: number
  completed_today: number
  revenue_today: number
}

export default function RestaurantDashboard() {
  const [restaurant, setRestaurant] = useState<RestaurantData | null>(null)
  const [summary, setSummary] = useState<OrderSummary>({
    total_orders: 0,
    pending_orders: 0,
    completed_today: 0,
    revenue_today: 0,
  })
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setIsLoading(true)
      const restaurantData = await restaurantsAPI.getMyRestaurant()
      setRestaurant(restaurantData)

      const ordersData = await ordersAPI.getRestaurantOrders()
      const pending = ordersData.filter((o) => !["delivered", "cancelled"].includes(o.status)).length
      const completed = ordersData.filter((o) => o.status === "delivered").length
      const revenue = ordersData.filter((o) => o.status === "delivered").reduce((sum, o) => sum + o.total, 0)

      setSummary({
        total_orders: ordersData.length,
        pending_orders: pending,
        completed_today: completed,
        revenue_today: revenue,
      })
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin mx-auto mb-4"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold">{restaurant?.name || "Restaurant Dashboard"}</h1>
        <Link href="/restaurant/menu/add-item">
          <Button className="bg-primary text-white gap-2">
            <Plus className="w-4 h-4" />
            Add Menu Item
          </Button>
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted text-sm">Total Orders</p>
              <p className="text-3xl font-bold text-foreground">{summary.total_orders}</p>
            </div>
            <ShoppingBag className="w-10 h-10 text-primary opacity-20" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted text-sm">Pending Orders</p>
              <p className="text-3xl font-bold text-foreground">{summary.pending_orders}</p>
            </div>
            <Clock className="w-10 h-10 text-warning opacity-20" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted text-sm">Completed Today</p>
              <p className="text-3xl font-bold text-foreground">{summary.completed_today}</p>
            </div>
            <TrendingUp className="w-10 h-10 text-success opacity-20" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted text-sm">Revenue Today</p>
              <p className="text-3xl font-bold text-primary">₹{summary.revenue_today.toFixed(0)}</p>
            </div>
            <TrendingUp className="w-10 h-10 text-primary opacity-20" />
          </div>
        </Card>
      </div>

      {/* Restaurant Info */}
      <Card className="p-6">
        <h2 className="text-lg font-bold mb-4">Restaurant Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-muted">Phone</p>
            <p className="font-semibold">{restaurant?.phone}</p>
          </div>
          <div>
            <p className="text-sm text-muted">Address</p>
            <p className="font-semibold">{restaurant?.address}</p>
          </div>
          <div>
            <p className="text-sm text-muted">Opening Time</p>
            <p className="font-semibold">{restaurant?.opening_time}</p>
          </div>
          <div>
            <p className="text-sm text-muted">Closing Time</p>
            <p className="font-semibold">{restaurant?.closing_time}</p>
          </div>
        </div>
      </Card>
    </div>
  )
}
