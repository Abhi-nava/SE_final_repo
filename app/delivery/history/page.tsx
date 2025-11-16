"use client"

import { useState, useEffect } from "react"
// import { deliveryAPI } from "@/lib/api"
import { Card } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import { Calendar } from "lucide-react"

interface CompletedDelivery {
  id: string
  status: string
  total: number
  delivery_fee: number
  created_at: string
  delivery_address: string
}

export default function DeliveryHistoryPage() {
  const [deliveries, setDeliveries] = useState<CompletedDelivery[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    loadDeliveryHistory()
  }, [])

  const loadDeliveryHistory = async () => {
    try {
      const data = await deliveryAPI.getMyDeliveries()
      const completed = data.filter((d) => ["delivered", "cancelled"].includes(d.status))
      setDeliveries(completed)
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
          <p>Loading history...</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-4xl font-bold mb-2">Delivery History</h1>
      <p className="text-muted mb-8">{deliveries.length} completed deliveries</p>

      {deliveries.length === 0 ? (
        <Card className="p-12 text-center">
          <Calendar className="w-12 h-12 text-muted opacity-50 mx-auto mb-4" />
          <p className="text-lg text-muted">No delivery history yet</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {deliveries.map((delivery) => (
            <Card key={delivery.id} className="p-4">
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-center">
                <div>
                  <p className="text-xs text-muted">Order ID</p>
                  <p className="font-mono text-sm font-semibold">{delivery.id}</p>
                </div>
                <div>
                  <p className="text-xs text-muted">Date</p>
                  <p className="text-sm">{new Date(delivery.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-xs text-muted">Address</p>
                  <p className="text-sm line-clamp-1">{delivery.delivery_address}</p>
                </div>
                <div>
                  <p className="text-xs text-muted">Fee Earned</p>
                  <p className="font-bold text-primary">₹{delivery.delivery_fee?.toFixed(0)}</p>
                </div>
                <div>
                  <span
                    className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                      delivery.status === "delivered" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                    }`}
                  >
                    {delivery.status.toUpperCase()}
                  </span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
