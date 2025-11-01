"use client"

import { useState, useEffect } from "react"
import { deliveryAPI } from "@/lib/api"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { MapPin, Clock, Truck } from "lucide-react"

interface AvailableOrder {
  id: string
  delivery_address: string
  delivery_phone: string
  total: number
  items: any[]
  estimated_delivery_time: number
}

export default function AvailableOrdersPage() {
  const [orders, setOrders] = useState<AvailableOrder[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [acceptingOrder, setAcceptingOrder] = useState<string | null>(null)
  const { toast } = useToast()

  useEffect(() => {
    loadAvailableOrders()
    const interval = setInterval(loadAvailableOrders, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadAvailableOrders = async () => {
    try {
      const data = await deliveryAPI.getAvailableOrders()
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

  const handleAcceptOrder = async (orderId: string) => {
    try {
      setAcceptingOrder(orderId)
      await deliveryAPI.acceptDelivery(orderId)
      toast({
        title: "Success",
        description: "Order accepted! Head to the restaurant to pick up.",
      })
      loadAvailableOrders()
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setAcceptingOrder(null)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin mx-auto mb-4"></div>
          <p>Loading available orders...</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-4xl font-bold mb-2">Available Orders</h1>
      <p className="text-muted mb-8">Showing {orders.length} orders ready for delivery</p>

      {orders.length === 0 ? (
        <Card className="p-12 text-center">
          <Truck className="w-12 h-12 text-muted opacity-50 mx-auto mb-4" />
          <p className="text-lg text-muted">No available orders at the moment</p>
          <p className="text-sm text-muted mt-2">Check back soon!</p>
        </Card>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <Card key={order.id} className="p-6 hover:shadow-lg transition-shadow">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <p className="text-sm text-muted">Order ID</p>
                  <p className="font-mono font-semibold text-sm">{order.id}</p>
                </div>
                <div>
                  <p className="text-sm text-muted">Total Amount</p>
                  <p className="text-lg font-bold text-primary">₹{order.total?.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted">Est. Delivery</p>
                  <p className="font-semibold flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {order.estimated_delivery_time} min
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted">Items</p>
                  <p className="font-semibold">{order.items?.length} items</p>
                </div>
              </div>

              <div className="flex items-start gap-2 mb-4 pb-4 border-b border-border">
                <MapPin className="w-4 h-4 text-primary mt-1 flex-shrink-0" />
                <div>
                  <p className="text-sm text-muted">Delivery Address</p>
                  <p className="font-semibold">{order.delivery_address}</p>
                  <p className="text-sm text-muted mt-1">Phone: {order.delivery_phone}</p>
                </div>
              </div>

              <Button
                onClick={() => handleAcceptOrder(order.id)}
                disabled={acceptingOrder === order.id}
                className="w-full bg-primary text-white hover:bg-primary-dark"
              >
                {acceptingOrder === order.id ? "Accepting..." : "Accept Delivery"}
              </Button>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
