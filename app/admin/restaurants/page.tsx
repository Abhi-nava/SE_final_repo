"use client"

import { useState, useEffect } from "react"
import { useToast } from "@/hooks/use-toast"
import { ArrowLeft, Trash2 } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"

interface Restaurant {
  id: string
  name: string
  email: string
  phone: string
  orders_count: number
  revenue: number
  is_active: boolean
  created_at: string
}

export default function RestaurantsManagement() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    loadRestaurants()
  }, [])

  const loadRestaurants = async () => {
    try {
      setIsLoading(true)
      const response = await fetch("/api/admin/restaurants")
      if (response.ok) {
        const data = await response.json()
        setRestaurants(data)
      }
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
        <div className="animate-spin">Loading...</div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <Link href="/admin">
        <Button variant="ghost" className="mb-6 gap-2">
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Button>
      </Link>

      <h1 className="text-3xl font-bold mb-8">Manage Restaurants</h1>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left p-4 font-semibold">Name</th>
              <th className="text-left p-4 font-semibold">Email</th>
              <th className="text-left p-4 font-semibold">Orders</th>
              <th className="text-left p-4 font-semibold">Revenue</th>
              <th className="text-left p-4 font-semibold">Status</th>
              <th className="text-left p-4 font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody>
            {restaurants.map((restaurant) => (
              <tr key={restaurant.id} className="border-b hover:bg-secondary/50">
                <td className="p-4">{restaurant.name}</td>
                <td className="p-4 text-sm dark">{restaurant.email}</td>
                <td className="p-4">{restaurant.orders_count}</td>
                <td className="p-4 font-semibold">₹{restaurant.revenue.toFixed(2)}</td>
                <td className="p-4">
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      restaurant.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                    }`}
                  >
                    {restaurant.is_active ? "Active" : "Inactive"}
                  </span>
                </td>
                <td className="p-4">
                  <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700">
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
