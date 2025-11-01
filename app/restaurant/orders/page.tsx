"use client"

import { useState, useEffect } from "react"
// import { ordersAPI } from "@/lib/api"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { ChevronDown } from "lucide-react"

interface Order {
  id: string
  status: string
  total: number
  customer_id: string
  items: any[]
  created_at: string
}

export default function RestaurantOrdersPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [expandedOrders, setExpandedOrders] = useState<string[]>([])
  const { toast } = useToast()

  useEffect(() => {
    loadOrders()
    const interval = setInterval(loadOrders, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const loadOrders = async () => {
    try {
      const data = await ordersAPI.getRestaurantOrders()
      setOrders(data)
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

  const updateOrderStatus = async (orderId: string, newStatus: string) => {
    try {
      await ordersAPI.updateOrderStatus(orderId, newStatus)
      toast({
        title: "Success",
        description: `Order status updated to ${newStatus}`,
      })
      loadOrders()
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    }
  }

  const getNextStatus = (currentStatus: string) => {
    const statusFlow = {
      pending: "confirmed",
      confirmed: "preparing",
      preparing: "ready",
      ready: "assigned",
      assigned: "picked_up",
      picked_up: "in_transit",
      in_transit: "delivered",
    }
    return statusFlow[currentStatus as keyof typeof statusFlow]
  }

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      pending: "bg-yellow-100 text-yellow-800",
      confirmed: "bg-blue-100 text-blue-800",
      preparing: "bg-purple-100 text-purple-800",
      ready: "bg-indigo-100 text-indigo-800",
      assigned: "bg-orange-100 text-orange-800",
      picked_up: "bg-orange-100 text-orange-800",
      in_transit: "bg-orange-100 text-orange-800",
      delivered: "bg-green-100 text-green-800",
    }
    return colors[status] || "bg-gray-100 text-gray-800"
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin mx-auto mb-4"></div>
          <p>Loading orders...</p>
        </div>
      </div>
    )
  }

  const pendingOrders = orders.filter((o) => !["delivered", "cancelled"].includes(o.status))
  const completedOrders = orders.filter((o) => ["delivered", "cancelled"].includes(o.status))

  return (
    <div>
      <h1 className="text-4xl font-bold mb-8">Orders</h1>

      {/* Pending Orders */}
      <div className="mb-12">
        <h2 className="text-2xl font-bold mb-6 text-warning">Active Orders ({pendingOrders.length})</h2>

        {pendingOrders.length === 0 ? (
          <Card className="p-8 text-center">
            <p className="text-muted">No active orders</p>
          </Card>
        ) : (
          <div className="space-y-4">
            {pendingOrders.map((order) => (
              <Card key={order.id} className="p-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <p className="font-mono text-sm"># {order.id}</p>
                      <span
                        className={`inline-block px-3 py-1 rounded text-xs font-semibold ${getStatusColor(order.status)}`}
                      >
                        {order.status.toUpperCase()}
                      </span>
                    </div>

                    <button
                      onClick={() =>
                        setExpandedOrders((prev) =>
                          prev.includes(order.id) ? prev.filter((id) => id !== order.id) : [...prev, order.id],
                        )
                      }
                      className="flex items-center gap-2 mb-4 text-primary hover:underline"
                    >
                      <ChevronDown
                        className={`w-4 h-4 transition-transform ${expandedOrders.includes(order.id) ? "rotate-180" : ""}`}
                      />
                      View Items ({order.items.length})
                    </button>

                    {expandedOrders.includes(order.id) && (
                      <div className="mb-4 bg-bg-alt p-4 rounded">
                        {order.items.map((item, idx) => (
                          <div key={idx} className="flex justify-between text-sm mb-2 last:mb-0">
                            <span>
                              {item.name} x{item.quantity}
                            </span>
                            <span className="font-semibold">₹{(item.price * item.quantity).toFixed(2)}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    <p className="text-sm text-muted">
                      Total: <span className="font-bold text-foreground">₹{order.total.toFixed(2)}</span>
                    </p>
                  </div>

                  <div className="ml-4">
                    {getNextStatus(order.status) && (
                      <Button
                        onClick={() => updateOrderStatus(order.id, getNextStatus(order.status) || "")}
                        className="bg-primary text-white whitespace-nowrap"
                      >
                        Mark as {getNextStatus(order.status)}
                      </Button>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Completed Orders */}
      <div>
        <h2 className="text-2xl font-bold mb-6 text-success">Completed Orders ({completedOrders.length})</h2>

        {completedOrders.length === 0 ? (
          <Card className="p-8 text-center">
            <p className="text-muted">No completed orders</p>
          </Card>
        ) : (
          <div className="space-y-2">
            {completedOrders.map((order) => (
              <Card key={order.id} className="p-4">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-mono text-sm"># {order.id}</p>
                    <span
                      className={`inline-block px-2 py-1 rounded text-xs font-semibold ${getStatusColor(order.status)}`}
                    >
                      {order.status.toUpperCase()}
                    </span>
                  </div>
                  <span className="font-bold">₹{order.total.toFixed(2)}</span>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
