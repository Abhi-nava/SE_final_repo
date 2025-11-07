"use client"

import { useState, useEffect } from "react"
import { useToast } from "@/hooks/use-toast"
import { ArrowLeft, Star } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

interface DeliveryAgent {
  id: string
  name: string
  email: string
  phone: string
  total_deliveries: number
  completed_deliveries: number
  rating: number
  is_active: boolean
  created_at: string
}

export default function DeliveryAgentsManagement() {
  const [agents, setAgents] = useState<DeliveryAgent[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    try {
      setIsLoading(true)
      const response = await fetch("/api/admin/delivery-agents")
      if (response.ok) {
        const data = await response.json()
        setAgents(data)
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

      <h1 className="text-3xl font-bold mb-8">Manage Delivery Agents</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => (
          <Card key={agent.id} className="p-6">
            <h3 className="font-bold text-lg">{agent.name}</h3>
            <p className="text-sm text-muted mb-3">{agent.email}</p>

            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span>Total Deliveries</span>
                <span className="font-semibold">{agent.total_deliveries}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Completed</span>
                <span className="font-semibold text-green-600">{agent.completed_deliveries}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Rating</span>
                <span className="flex items-center gap-1">
                  <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  {agent.rating.toFixed(1)}
                </span>
              </div>
            </div>

            <div className="flex gap-2">
              <span
                className={`px-2 py-1 rounded-full text-xs font-semibold flex-1 text-center ${
                  agent.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                }`}
              >
                {agent.is_active ? "Active" : "Inactive"}
              </span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
