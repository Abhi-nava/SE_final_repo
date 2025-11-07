"use client"

import { useState, useEffect } from "react"
import { restaurantsAPI } from "@/lib/api"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import Link from "next/link"
import { ShoppingBag, Clock, TrendingUp, Star } from "lucide-react"

interface RestaurantInfo {
  id: string
  name: string
  phone: string
  address: string
  opening_time: string
  closing_time: string
}

interface DashboardStats {
  total_orders: number
  pending_orders: number
  completed_today: number
  revenue_today: number
}

interface RatingsInfo {
  count: number
  avg_restaurant: number
  avg_delivery: number
  avg_food_quality: number
  avg_delivery_speed: number
  avg_packaging_quality: number
}

interface DashboardData {
  restaurant: RestaurantInfo
  stats: DashboardStats
  ratings: RatingsInfo
}

export default function RestaurantDashboard() {
  const [restaurant, setRestaurant] = useState<RestaurantInfo | null>(null)
  const [summary, setSummary] = useState<DashboardStats>({
    total_orders: 0,
    pending_orders: 0,
    completed_today: 0,
    revenue_today: 0,
  })
  const [ratings, setRatings] = useState<RatingsInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const data: DashboardData = await restaurantsAPI.getDashboardSummary()
      
      setRestaurant(data.restaurant)
      setSummary(data.stats)
      setRatings(data.ratings)
      
    } catch (e: any) {
      console.error("Dashboard error:", e)
      toast({ 
        title: "Error", 
        description: e.message || "Failed to load dashboard", 
        variant: "destructive" 
      })
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (!restaurant) {
    return (
      <div className="p-8 text-center">
        <p className="text-muted-foreground mb-4">No restaurant found</p>
        <Link href="/restaurant/create">
          <Button>Create Restaurant</Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">{restaurant.name}</h1>
        <p className="text-muted-foreground">{restaurant.address}</p>
        <p className="text-sm text-muted-foreground">
          Open: {restaurant.opening_time} - {restaurant.closing_time}
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-2">
            <p className="text-muted-foreground text-sm">Total Orders</p>
            <ShoppingBag className="h-5 w-5 text-blue-500" />
          </div>
          <p className="text-3xl font-bold">{summary.total_orders}</p>
        </Card>

        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-2">
            <p className="text-muted-foreground text-sm">Pending Orders</p>
            <Clock className="h-5 w-5 text-orange-500" />
          </div>
          <p className="text-3xl font-bold text-orange-600">{summary.pending_orders}</p>
        </Card>

        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-2">
            <p className="text-muted-foreground text-sm">Completed Today</p>
            <TrendingUp className="h-5 w-5 text-green-500" />
          </div>
          <p className="text-3xl font-bold text-green-600">{summary.completed_today}</p>
        </Card>

        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-2">
            <p className="text-muted-foreground text-sm">Revenue Today</p>
            <span className="text-xl">₹</span>
          </div>
          <p className="text-3xl font-bold text-primary">₹{summary.revenue_today.toLocaleString()}</p>
        </Card>
      </div>

      {/* Ratings Summary */}
      {ratings && ratings.count > 0 && (
        <Card className="p-6 mb-10">
          <div className="flex items-center gap-2 mb-4">
            <Star className="h-6 w-6 text-yellow-500 fill-yellow-500" />
            <h2 className="text-xl font-bold">Ratings Summary</h2>
            <span className="text-sm text-muted-foreground">({ratings.count} reviews)</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-primary">{ratings.avg_restaurant.toFixed(1)}</p>
              <p className="text-xs text-muted-foreground mt-1">Restaurant</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-primary">{ratings.avg_delivery.toFixed(1)}</p>
              <p className="text-xs text-muted-foreground mt-1">Delivery</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-primary">{ratings.avg_food_quality.toFixed(1)}</p>
              <p className="text-xs text-muted-foreground mt-1">Food Quality</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-primary">{ratings.avg_delivery_speed.toFixed(1)}</p>
              <p className="text-xs text-muted-foreground mt-1">Speed</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-primary">{ratings.avg_packaging_quality.toFixed(1)}</p>
              <p className="text-xs text-muted-foreground mt-1">Packaging</p>
            </div>
          </div>
        </Card>
      )}

      {/* No Ratings Message */}
      {ratings && ratings.count === 0 && (
        <Card className="p-6 mb-10 text-center">
          <Star className="h-12 w-12 text-gray-300 mx-auto mb-2" />
          <p className="text-muted-foreground">No ratings yet. Complete orders to start receiving reviews!</p>
        </Card>
      )}

      {/* Quick Links */}
      <div className="flex gap-4">
        <Link href="/restaurant/orders">
          <Button className="bg-primary text-white">
            <ShoppingBag className="h-4 w-4 mr-2" />
            Manage Orders
          </Button>
        </Link>

        <Link href="/restaurant/menu">
          <Button variant="outline">
            <TrendingUp className="h-4 w-4 mr-2" />
            Manage Menu
          </Button>
        </Link>
      </div>
    </div>
  )
}