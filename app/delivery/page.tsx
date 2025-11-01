"use client"

import { useState, useEffect } from "react"
// import { deliveryAPI } from "@/lib/api"
import { Card } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import { TrendingUp, Truck, Star, DollarSign } from "lucide-react"

interface DeliveryStats {
  total_deliveries: number
  completed_today: number
  rating: number
  earnings_today: number
}

export default function DeliveryDashboard() {
  const [stats, setStats] = useState<DeliveryStats>({
    total_deliveries: 0,
    completed_today: 0,
    rating: 0,
    earnings_today: 0,
  })
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const profile = await deliveryAPI.getProfile()
      const deliveries = await deliveryAPI.getMyDeliveries()

      const completedToday = deliveries.filter((d) => d.status === "delivered").length
      const earningsToday = deliveries
        .filter((d) => d.status === "delivered")
        .reduce((sum, d) => sum + (d.delivery_fee || 0), 0)

      setStats({
        total_deliveries: profile.total_deliveries || 0,
        completed_today: completedToday,
        rating: profile.rating || 0,
        earnings_today: earningsToday,
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
      <h1 className="text-4xl font-bold mb-8">Delivery Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted text-sm">Total Deliveries</p>
              <p className="text-3xl font-bold">{stats.total_deliveries}</p>
            </div>
            <Truck className="w-10 h-10 text-primary opacity-20" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted text-sm">Completed Today</p>
              <p className="text-3xl font-bold">{stats.completed_today}</p>
            </div>
            <TrendingUp className="w-10 h-10 text-success opacity-20" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted text-sm">Rating</p>
              <p className="text-3xl font-bold">{stats.rating.toFixed(1)}</p>
            </div>
            <Star className="w-10 h-10 text-yellow-500 opacity-20" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted text-sm">Earnings Today</p>
              <p className="text-3xl font-bold text-primary">₹{stats.earnings_today.toFixed(0)}</p>
            </div>
            <DollarSign className="w-10 h-10 text-primary opacity-20" />
          </div>
        </Card>
      </div>
    </div>
  )
}
