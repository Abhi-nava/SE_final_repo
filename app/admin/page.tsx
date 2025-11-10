"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import Link from "next/link"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts"
import { TrendingUp, Users, Store, Bike } from "lucide-react"
import { adminAPI } from "@/lib/api"

interface Analytics {
  total_orders: number
  total_revenue: number
  active_restaurants: number
  active_delivery_agents: number
  avg_order_value: number
  status_breakdown: Record<string, number>
}

interface DailyRevenue {
  _id: string
  revenue: number
  orders: number
}

export default function AdminDashboard() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [revenueData, setRevenueData] = useState<DailyRevenue[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    try {
      setIsLoading(true)
      const [analyticsRes, revenueRes] = await Promise.all([adminAPI.getAnalytics(), adminAPI.getDailyRevenue(30)])

      setAnalytics(analyticsRes)
      setRevenueData(revenueRes)
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

  if (isLoading || !analytics) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin mx-auto mb-4"></div>
          <p>Loading analytics...</p>
        </div>
      </div>
    )
  }

  const statCards = [
    {
      icon: TrendingUp,
      label: "Total Orders",
      value: analytics.total_orders,
      color: "bg-blue-500/10 text-blue-600",
    },
    {
      icon: TrendingUp,
      label: "Total Revenue",
      value: `₹${analytics.total_revenue.toLocaleString("en-IN")}`,
      color: "bg-green-500/10 text-green-600",
    },
    {
      icon: Store,
      label: "Active Restaurants",
      value: analytics.active_restaurants,
      color: "bg-orange-500/10 text-orange-600",
    },
    {
      icon: Bike,
      label: "Active Delivery Agents",
      value: analytics.active_delivery_agents,
      color: "bg-purple-500/10 text-purple-600",
    },
  ]

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        <p className="text-muted mt-2">Platform overview and analytics</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statCards.map((stat, idx) => {
          const Icon = stat.icon
          return (
            <Card key={idx} className="p-6">
              <div className={`w-12 h-12 rounded-lg ${stat.color} flex items-center justify-center mb-4`}>
                <Icon className="w-6 h-6" />
              </div>
              <p className="text-sm text-muted">{stat.label}</p>
              <p className="text-2xl font-bold mt-2">{stat.value}</p>
            </Card>
          )
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Revenue Chart */}
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-4">Daily Revenue (30 days)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="_id" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Orders Chart */}
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-4">Daily Orders (30 days)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="_id" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="orders" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Status Breakdown */}
      <Card className="p-6 mb-8">
        <h2 className="text-lg font-bold mb-4">Order Status Breakdown</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {Object.entries(analytics.status_breakdown).map(([status, count]) => (
            <div key={status} className="p-4 border rounded-lg text-center">
              <p className="text-sm font-medium capitalize">{status}</p>
              <p className="text-2xl font-bold mt-2">{count}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Navigation */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link href="/admin/restaurants">
          <Card className="p-6 cursor-pointer hover:shadow-lg transition-shadow">
            <Store className="w-8 h-8 text-orange-600 mb-2" />
            <h3 className="font-semibold">Manage Restaurants</h3>
            <p className="text-sm text-muted mt-1">{analytics.active_restaurants} active</p>
          </Card>
        </Link>

        <Link href="/admin/delivery-agents">
          <Card className="p-6 cursor-pointer hover:shadow-lg transition-shadow">
            <Bike className="w-8 h-8 text-purple-600 mb-2" />
            <h3 className="font-semibold">Manage Delivery Agents</h3>
            <p className="text-sm text-muted mt-1">{analytics.active_delivery_agents} active</p>
          </Card>
        </Link>

        <Link href="/admin/users">
          <Card className="p-6 cursor-pointer hover:shadow-lg transition-shadow">
            <Users className="w-8 h-8 text-green-600 mb-2" />
            <h3 className="font-semibold">Manage Users</h3>
            <p className="text-sm text-muted mt-1">All customers</p>
          </Card>
        </Link>
      </div>
    </div>
  )
}
