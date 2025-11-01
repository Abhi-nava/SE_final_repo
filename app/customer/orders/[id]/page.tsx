"use client"

import { useState, useEffect, useRef } from "react"
import { ordersAPI } from "@/lib/api"
import { useParams, useRouter } from "next/navigation"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { ArrowLeft, Clock, Truck, CheckCircle, MapPin } from "lucide-react"
import Link from "next/link"
import { OrderTrackingWebSocket } from "@/lib/websocket"

interface Order {
  id: string
  status: string
  total: number
  subtotal: number
  delivery_fee: number
  discount: number
  delivery_address: string
  delivery_phone: string
  payment_method: string
  created_at: string
  items: any[]
  estimated_delivery_time?: number
}

interface DeliveryLocation {
  latitude: number
  longitude: number
  delivery_agent_id: string
}

export default function OrderDetailsPage() {
  const params = useParams()
  const orderId = params.id as string
  const router = useRouter()

  const [order, setOrder] = useState<Order | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [deliveryLocation, setDeliveryLocation] = useState<DeliveryLocation | null>(null)
  const [wsConnected, setWsConnected] = useState(false)
  const { toast } = useToast()
  const wsRef = useRef<OrderTrackingWebSocket | null>(null)

  useEffect(() => {
    loadOrder()
  }, [orderId])

  // Setup WebSocket connection
  useEffect(() => {
    const setupWebSocket = async () => {
      try {
        const userId = localStorage.getItem("user_id") || "unknown"
        wsRef.current = new OrderTrackingWebSocket(orderId, userId)

        await wsRef.current.connect()
        setWsConnected(true)

        // Listen for order status updates
        wsRef.current.on("order_status", (message: any) => {
          if (message.data) {
            setOrder((prev) => (prev ? { ...prev, status: message.data.status } : null))
          }
        })

        // Listen for delivery location updates
        wsRef.current.on("delivery_location_update", (message: any) => {
          if (message.data) {
            setDeliveryLocation(message.data)
          }
        })

        // Request initial order status
        wsRef.current.getOrderStatus()

        // Setup ping-pong to keep connection alive
        const pingInterval = setInterval(() => {
          if (wsRef.current) {
            wsRef.current.ping()
          }
        }, 30000)

        return () => clearInterval(pingInterval)
      } catch (error) {
        console.error("[v0] WebSocket setup failed:", error)
        setWsConnected(false)
        // Fallback to polling if WebSocket fails
        const interval = setInterval(loadOrder, 5000)
        return () => clearInterval(interval)
      }
    }

    setupWebSocket()

    return () => {
      if (wsRef.current) {
        wsRef.current.disconnect()
      }
    }
  }, [orderId])

  const loadOrder = async () => {
    try {
      const data = await ordersAPI.getOrder(orderId)
      setOrder(data)
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
      router.push("/customer/orders")
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusSteps = () => {
    const steps = [
      { key: "pending", label: "Order Placed" },
      { key: "confirmed", label: "Confirmed" },
      { key: "preparing", label: "Preparing" },
      { key: "ready", label: "Ready" },
      { key: "assigned", label: "Assigned" },
      { key: "picked_up", label: "Picked Up" },
      { key: "in_transit", label: "In Transit" },
      { key: "delivered", label: "Delivered" },
    ]

    return steps
  }

  const getStatusIndex = (status: string) => {
    const steps = getStatusSteps()
    return steps.findIndex((s) => s.key === status)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin mx-auto mb-4"></div>
          <p>Loading order details...</p>
        </div>
      </div>
    )
  }

  if (!order) {
    return <div>Order not found</div>
  }

  const statusIndex = getStatusIndex(order.status)
  const steps = getStatusSteps()

  return (
    <div>
      <Link href="/customer/orders">
        <Button variant="ghost" className="mb-6 gap-2">
          <ArrowLeft className="w-4 h-4" />
          Back to Orders
        </Button>
      </Link>

      {/* Order Header */}
      <Card className="p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-muted">Order ID</p>
            <p className="font-mono font-semibold">{order.id}</p>
          </div>
          <div>
            <p className="text-sm text-muted">Order Date</p>
            <p>{new Date(order.created_at).toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-muted">Total Amount</p>
            <p className="text-2xl font-bold text-primary">₹{order.total?.toFixed(2)}</p>
          </div>
        </div>
      </Card>

      {/* Status Timeline with real-time indicator */}
      <Card className="p-6 mb-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-bold">Order Status</h2>
          {wsConnected && (
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-muted">Live Tracking</span>
            </div>
          )}
        </div>
        <div className="space-y-4">
          {steps.map((step, idx) => (
            <div key={step.key} className="flex gap-4">
              <div className="flex flex-col items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-white transition-all ${
                    idx <= statusIndex ? "bg-primary" : "bg-border"
                  }`}
                >
                  {idx < statusIndex ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : idx === statusIndex ? (
                    <Clock className="w-5 h-5 animate-spin" />
                  ) : (
                    <span className="text-xs">{idx + 1}</span>
                  )}
                </div>
                {idx < steps.length - 1 && (
                  <div className={`w-0.5 h-12 mt-2 ${idx < statusIndex ? "bg-primary" : "bg-border"}`}></div>
                )}
              </div>
              <div className="py-2">
                <p className={`font-semibold ${idx === statusIndex ? "text-primary" : "text-foreground"}`}>
                  {step.label}
                </p>
                {idx === statusIndex && <p className="text-sm text-muted">Currently here...</p>}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Live Delivery Location */}
      {deliveryLocation && order.status === "in_transit" && (
        <Card className="p-6 mb-6 border-primary/50 bg-primary/5">
          <div className="flex items-start gap-4">
            <MapPin className="w-5 h-5 text-primary mt-1 flex-shrink-0" />
            <div>
              <h3 className="font-bold text-primary mb-2">Delivery in Progress</h3>
              <p className="text-sm text-muted">
                Your delivery is on the way! Current location: {deliveryLocation.latitude.toFixed(4)},{" "}
                {deliveryLocation.longitude.toFixed(4)}
              </p>
            </div>
          </div>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Order Items */}
        <div className="lg:col-span-2">
          <Card className="p-6">
            <h2 className="text-lg font-bold mb-4">Order Items</h2>
            <div className="space-y-3">
              {order.items?.map((item, idx) => (
                <div
                  key={idx}
                  className="flex justify-between items-center pb-3 border-b border-border last:border-b-0"
                >
                  <div>
                    <p className="font-semibold">{item.name}</p>
                    <p className="text-sm text-muted">Qty: {item.quantity}</p>
                  </div>
                  <p className="font-bold">₹{(item.price * item.quantity).toFixed(2)}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Delivery Details */}
        <div className="space-y-6">
          <Card className="p-6">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Truck className="w-5 h-5" />
              Delivery Details
            </h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-muted">Delivery Address</p>
                <p className="font-semibold">{order.delivery_address}</p>
              </div>
              <div>
                <p className="text-sm text-muted">Delivery Phone</p>
                <p className="font-semibold">{order.delivery_phone}</p>
              </div>
              {order.estimated_delivery_time && (
                <div>
                  <p className="text-sm text-muted">Est. Delivery Time</p>
                  <p className="font-semibold">{order.estimated_delivery_time} minutes</p>
                </div>
              )}
            </div>
          </Card>

          <Card className="p-6">
            <h2 className="text-lg font-bold mb-4">Price Breakdown</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Subtotal</span>
                <span>₹{order.subtotal?.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>Delivery Fee</span>
                <span>₹{order.delivery_fee?.toFixed(2)}</span>
              </div>
              {order.discount > 0 && (
                <div className="flex justify-between text-green-600">
                  <span>Discount</span>
                  <span>-₹{order.discount?.toFixed(2)}</span>
                </div>
              )}
              <div className="border-t border-border pt-2 font-bold flex justify-between">
                <span>Total</span>
                <span className="text-primary">₹{order.total?.toFixed(2)}</span>
              </div>
              <div className="mt-4 pt-2 border-t border-border">
                <p className="text-muted">Payment: {order.payment_method?.toUpperCase()}</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
