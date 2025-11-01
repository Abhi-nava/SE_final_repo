"use client"

import { useState, useEffect } from "react"
// import { deliveryAPI } from "@/lib/api"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { MapPin, Phone, CheckCircle } from "lucide-react"

interface ActiveDelivery {
  id: string
  status: string
  delivery_address: string
  delivery_phone: string
  total: number
  items: any[]
}

export default function ActiveDeliveriesPage() {
  const [deliveries, setDeliveries] = useState<ActiveDelivery[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [updatingStatus, setUpdatingStatus] = useState<string | null>(null)
  const { toast } = useToast()

  useEffect(() => {
    loadActiveDeliveries()
    const interval = setInterval(loadActiveDeliveries, 10000)
    return () => clearInterval(interval)
  }, [])

  const loadActiveDeliveries = async () => {
    try {
      const data = await deliveryAPI.getMyDeliveries()
      const active = data.filter((d) => !["delivered", "cancelled"].includes(d.status))
      setDeliveries(active)
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

  const handleUpdateStatus = async (orderId: string, newStatus: string) => {
    try {
      setUpdatingStatus(orderId)
      await deliveryAPI.updateDeliveryStatus(orderId, newStatus)
      toast({
        title: "Success",
        description: `Status updated to ${newStatus}`,
      })
      loadActiveDeliveries()
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setUpdatingStatus(null)
    }
  }

  const getNextStatus = (currentStatus: string) => {
    const statusFlow = {
      assigned: "picked_up",
      picked_up: "in_transit",
      in_transit: "delivered",
    }
    return statusFlow[currentStatus as keyof typeof statusFlow]
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin mx-auto mb-4"></div>
          <p>Loading deliveries...</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-4xl font-bold mb-2">Active Deliveries</h1>
      <p className="text-muted mb-8">{deliveries.length} deliveries in progress</p>

      {deliveries.length === 0 ? (
        <Card className="p-12 text-center">
          <CheckCircle className="w-12 h-12 text-success opacity-50 mx-auto mb-4" />
          <p className="text-lg text-muted">No active deliveries</p>
        </Card>
      ) : (
        <div className="space-y-4">
          {deliveries.map((delivery) => (
            <Card key={delivery.id} className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <p className="text-sm text-muted">Order ID</p>
                  <p className="font-mono font-semibold text-sm">{delivery.id}</p>
                </div>
                <div>
                  <p className="text-sm text-muted">Status</p>
                  <p className="font-semibold text-primary">{delivery.status.toUpperCase().replace("_", " ")}</p>
                </div>
                <div>
                  <p className="text-sm text-muted">Delivery Value</p>
                  <p className="font-bold">₹{delivery.total?.toFixed(2)}</p>
                </div>
              </div>

              <div className="mb-4 pb-4 border-b border-border">
                <div className="flex items-start gap-2 mb-2">
                  <MapPin className="w-4 h-4 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <p className="text-sm text-muted">Delivery Address</p>
                    <p className="font-semibold">{delivery.delivery_address}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-6">
                  <Phone className="w-4 h-4 text-muted" />
                  <a href={`tel:${delivery.delivery_phone}`} className="text-primary hover:underline">
                    {delivery.delivery_phone}
                  </a>
                </div>
              </div>

              {getNextStatus(delivery.status) && (
                <Button
                  onClick={() => handleUpdateStatus(delivery.id, getNextStatus(delivery.status) || "")}
                  disabled={updatingStatus === delivery.id}
                  className="bg-primary text-white hover:bg-primary-dark"
                >
                  {updatingStatus === delivery.id
                    ? "Updating..."
                    : `Mark as ${getNextStatus(delivery.status)?.toUpperCase().replace("_", " ")}`}
                </Button>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
