// "use client"

// import { useState, useEffect } from "react"
// import { ordersAPI } from "@/lib/api"
// import { Card } from "@/components/ui/card"
// import { Button } from "@/components/ui/button"
// import { useToast } from "@/hooks/use-toast"
// import { ChevronDown } from "lucide-react"

// interface Order {
//   id: string
//   order_status: string
//   total: number
//   items: { name: string; quantity: number; price: number }[]
//   delivery_address: string
//   delivery_phone: string
//   created_at: string
//   delivery_agent_id?: string
// }

// export default function RestaurantOrdersPage() {
//   const [orders, setOrders] = useState<Order[]>([])
//   const [loading, setLoading] = useState(true)
//   const [expanded, setExpanded] = useState<string[]>([])
//   const { toast } = useToast()

//   useEffect(() => {
//     loadOrders()
//     const interval = setInterval(loadOrders, 15000) // auto-refresh
//     return () => clearInterval(interval)
//   }, [])

//   const loadOrders = async () => {
//     try {
//       const data = await ordersAPI.getRestaurantOrders()
//       setOrders(data)
//     } catch (e: any) {
//       toast({ title: "Error", description: e.message, variant: "destructive" })
//     } finally {
//       setLoading(false)
//     }
//   }

//   const updateOrderStatus = async (id: string, newStatus: string) => {
//     try {
//       await ordersAPI.updateOrderStatus(id, newStatus)
//       toast({
//         title: "Status Updated",
//         description: `Order marked as ${newStatus}`,
//       })
//       loadOrders()
//     } catch (e: any) {
//       toast({ title: "Error", description: e.message, variant: "destructive" })
//     }
//   }

//   const nextStatusMap: Record<string, string> = {
//     preparing: "searching",
//     searching: "arriving",
//     arriving: "in-transit",
//     "in-transit": "delivered",
//   }

//   const statusColors: Record<string, string> = {
//     preparing: "bg-yellow-100 text-yellow-800",
//     searching: "bg-blue-100 text-blue-800",
//     arriving: "bg-orange-100 text-orange-800",
//     "in-transit": "bg-indigo-100 text-indigo-800",
//     delivered: "bg-green-100 text-green-800",
//   }

//   if (loading)
//     return (
//       <div className="flex items-center justify-center min-h-screen">
//         <div className="text-center">
//           <div className="w-10 h-10 border-4 border-primary border-t-transparent animate-spin mx-auto mb-3 rounded-full"></div>
//           <p>Loading orders...</p>
//         </div>
//       </div>
//     )

//   const activeOrders = orders.filter(
//     (o) => o.order_status !== "delivered"
//   )
//   const completedOrders = orders.filter(
//     (o) => o.order_status === "delivered"
//   )

//   return (
//     <div className="max-w-5xl mx-auto py-8">
//       <h1 className="text-4xl font-bold mb-8">Orders Dashboard</h1>

//       <section className="mb-10">
//         <h2 className="text-2xl font-semibold mb-4 text-primary">
//           Active Orders ({activeOrders.length})
//         </h2>

//         {activeOrders.length === 0 ? (
//           <Card className="p-8 text-center text-muted">No active orders</Card>
//         ) : (
//           <div className="space-y-4">
//             {activeOrders.map((order) => (
//               <Card key={order.id} className="p-6">
//                 <div className="flex justify-between items-start">
//                   <div className="flex-1">
//                     <div className="flex items-center gap-2 mb-2">
//                       <p className="font-mono text-sm"># {order.id}</p>
//                       <span
//                         className={`px-3 py-1 rounded text-xs font-semibold ${statusColors[order.order_status]}`}
//                       >
//                         {order.order_status.toUpperCase()}
//                       </span>
//                     </div>

//                     <p className="text-sm text-muted">
//                       Phone: {order.delivery_phone}
//                     </p>
//                     <p className="text-sm text-muted">
//                       Address: {order.delivery_address}
//                     </p>

//                     <button
//                       className="text-primary text-sm flex items-center gap-1 mt-3"
//                       onClick={() =>
//                         setExpanded((prev) =>
//                           prev.includes(order.id)
//                             ? prev.filter((x) => x !== order.id)
//                             : [...prev, order.id]
//                         )
//                       }
//                     >
//                       <ChevronDown
//                         className={`w-4 h-4 transition-transform ${
//                           expanded.includes(order.id) ? "rotate-180" : ""
//                         }`}
//                       />
//                       View Items ({order.items.length})
//                     </button>

//                     {expanded.includes(order.id) && (
//                       <div className="mt-3 bg-muted/10 p-4 rounded text-sm">
//                         {order.items.map((item, i) => (
//                           <div
//                             key={i}
//                             className="flex justify-between mb-1 last:mb-0"
//                           >
//                             <span>
//                               {item.name} × {item.quantity}
//                             </span>
//                             <span>₹{item.price * item.quantity}</span>
//                           </div>
//                         ))}
//                       </div>
//                     )}

//                     <p className="font-bold mt-4">
//                       Total: ₹{order.total.toFixed(2)}
//                     </p>
//                   </div>

//                   <div className="ml-4 flex flex-col gap-2">
//                     {nextStatusMap[order.order_status] && (
//                       <Button
//                         className="bg-primary text-white"
//                         onClick={() =>
//                           updateOrderStatus(
//                             order.id,
//                             nextStatusMap[order.order_status]
//                           )
//                         }
//                       >
//                         Mark as {nextStatusMap[order.order_status]}
//                       </Button>
//                     )}
//                   </div>
//                 </div>
//               </Card>
//             ))}
//           </div>
//         )}
//       </section>

//       <section>
//         <h2 className="text-2xl font-semibold mb-4 text-success">
//           Completed Orders ({completedOrders.length})
//         </h2>

//         {completedOrders.length === 0 ? (
//           <Card className="p-8 text-center text-muted">
//             No delivered orders
//           </Card>
//         ) : (
//           <div className="space-y-3">
//             {completedOrders.map((o) => (
//               <Card key={o.id} className="p-4 flex justify-between items-center">
//                 <div>
//                   <p className="font-mono text-sm"># {o.id}</p>
//                   <span
//                     className={`px-3 py-1 rounded text-xs font-semibold ${statusColors[o.order_status]}`}
//                   >
//                     {o.order_status.toUpperCase()}
//                   </span>
//                 </div>
//                 <p className="font-bold">₹{o.total.toFixed(2)}</p>
//               </Card>
//             ))}
//           </div>
//         )}
//       </section>
//     </div>
//   )
// }


"use client"

import { useState, useEffect } from "react"
import { ordersAPI } from "@/lib/api"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"
import { ChevronDown } from "lucide-react"

interface Order {
  id: string
  order_status: string
  total: number
  items: { name: string; quantity: number; price: number }[]
  delivery_address: string
  delivery_phone: string
  created_at: string
  delivery_agent_id?: string
}

interface Agent {
  id: string
  rating?: number
}

export default function RestaurantOrdersPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [agents, setAgents] = useState<Agent[]>([])
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [selectedAgent, setSelectedAgent] = useState<string>("")
  const [assignOpen, setAssignOpen] = useState(false)
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<string[]>([])
  const { toast } = useToast()

  useEffect(() => {
    loadOrders()
    const interval = setInterval(loadOrders, 15000)
    return () => clearInterval(interval)
  }, [])

  const loadOrders = async () => {
    try {
      const data = await ordersAPI.getRestaurantOrders()
      setOrders(data)
    } catch (e: any) {
      toast({ title: "Error", description: e.message, variant: "destructive" })
    } finally {
      setLoading(false)
    }
  }

  const openAssignModal = async (order: Order) => {
    try {
      const data = await ordersAPI.listAgents()
      setAgents(data)
      setSelectedOrder(order)
      setAssignOpen(true)
    } catch (e: any) {
      toast({ title: "Error", description: e.message, variant: "destructive" })
    }
  }


//   const assignAgent = async () => {
//   if (!selectedOrder || !selectedAgent) return
//   try {
//     await ordersAPI.assignAgent(selectedOrder.id, selectedAgent)
//     toast({
//       title: "Agent Assigned",
//       description: "Delivery agent assigned. Driver arriving.",
//     })
//     setAssignOpen(false)
//     setSelectedAgent("")
//     loadOrders()
//   } catch (e: any) {
//     toast({ title: "Error", description: e.message, variant: "destructive" })
//   }
// }
const assignAgent = async () => {
  if (!selectedOrder || !selectedAgent) return
  try {
    await ordersAPI.assignAgent(selectedOrder.id, selectedAgent)
    toast({
      title: "Agent Assigned",
      description: "Driver is arriving at your restaurant.",
    })
    setAssignOpen(false)
    setSelectedAgent("")
    loadOrders()
  } catch (e: any) {
    toast({ title: "Error", description: e.message, variant: "destructive" })
  }
}



// const updateOrderStatus = async (order: Order, newStatus: string) => {
//   if (newStatus === "searching") {
//     try {
//       // Step 1: Mark as searching
//       await ordersAPI.updateOrderStatus(order.id, "searching")

//       // Step 2: Open assignment modal
//       await openAssignModal(order)
//     } catch (e: any) {
//       toast({ title: "Error", description: e.message, variant: "destructive" })
//     }
//     return
//   }

//   try {
//     await ordersAPI.updateOrderStatus(order.id, newStatus)
//     toast({
//       title: "Status Updated",
//       description: `Order marked as ${newStatus}`,
//     })
//     loadOrders()
//   } catch (e: any) {
//     toast({ title: "Error", description: e.message, variant: "destructive" })
//   }
// }

const updateOrderStatus = async (order: Order, newStatus: string) => {
  if (newStatus === "searching") {
    try {
      // Step 1: Set to searching
      await ordersAPI.updateOrderStatus(order.id, "searching")
      toast({ title: "Searching for agents..." })
      // Step 2: Open the assign modal
      await openAssignModal(order)
    } catch (e: any) {
      toast({ title: "Error", description: e.message, variant: "destructive" })
    }
    return
  }

  try {
    await ordersAPI.updateOrderStatus(order.id, newStatus)
    toast({ title: "Status Updated", description: `Order marked as ${newStatus}` })
    loadOrders()
  } catch (e: any) {
    toast({ title: "Error", description: e.message, variant: "destructive" })
  }
}



const nextStatusMap: Record<string, string> = {
  preparing: "searching",
  searching: "arriving", 
  arriving: "in-transit",
  "in-transit": "delivered",
  delivered: "",
};


const statusColors: Record<string, string> = {
  preparing: "bg-yellow-100 text-yellow-800",
  searching: "bg-blue-100 text-blue-800",
  arriving: "bg-orange-100 text-orange-800",
  waiting: "bg-purple-100 text-purple-800",
  "in-transit": "bg-indigo-100 text-indigo-800",
  delivered: "bg-green-100 text-green-800",
}

  if (loading)
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-primary border-t-transparent animate-spin mx-auto mb-3 rounded-full"></div>
          <p>Loading orders...</p>
        </div>
      </div>
    )

  const activeOrders = orders.filter((o) => o.order_status !== "delivered")
  const completedOrders = orders.filter((o) => o.order_status === "delivered")

  return (
    <div className="max-w-5xl mx-auto py-8">
      <h1 className="text-4xl font-bold mb-8">Orders Dashboard</h1>

      <section className="mb-10">
        <h2 className="text-2xl font-semibold mb-4 text-primary">
          Active Orders ({activeOrders.length})
        </h2>

        {activeOrders.length === 0 ? (
          <Card className="p-8 text-center text-muted">No active orders</Card>
        ) : (
          <div className="space-y-4">
            {activeOrders.map((order) => {
              const currentStatus = order.order_status ?? "preparing"
              return (
                <Card key={order.id} className="p-6">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <p className="font-mono text-sm"># {order.id}</p>
                        <span
                          className={`px-3 py-1 rounded text-xs font-semibold ${statusColors[currentStatus]}`}
                        >
                          {currentStatus.toUpperCase()}
                        </span>
                      </div>

                      <p className="text-sm text-muted">
                        Phone: {order.delivery_phone}
                      </p>
                      <p className="text-sm text-muted">
                        Address: {order.delivery_address}
                      </p>

                      <button
                        className="text-primary text-sm flex items-center gap-1 mt-3"
                        onClick={() =>
                          setExpanded((prev) =>
                            prev.includes(order.id)
                              ? prev.filter((x) => x !== order.id)
                              : [...prev, order.id]
                          )
                        }
                      >
                        <ChevronDown
                          className={`w-4 h-4 transition-transform ${
                            expanded.includes(order.id) ? "rotate-180" : ""
                          }`}
                        />
                        View Items ({order.items.length})
                      </button>

                      {expanded.includes(order.id) && (
                        <div className="mt-3 bg-muted/10 p-4 rounded text-sm">
                          {order.items.map((item, i) => (
                            <div
                              key={i}
                              className="flex justify-between mb-1 last:mb-0"
                            >
                              <span>
                                {item.name} × {item.quantity}
                              </span>
                              <span>₹{item.price * item.quantity}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      <p className="font-bold mt-4">
                        Total: ₹{order.total.toFixed(2)}
                      </p>
                    </div>

                    <div className="ml-4 flex flex-col gap-2">
                      {nextStatusMap[currentStatus] && (
                        <Button
                          className="bg-primary text-white"
                          onClick={() =>
                            updateOrderStatus(order, nextStatusMap[currentStatus])
                          }
                        >
                          Mark as {nextStatusMap[currentStatus]}
                        </Button>
                      )}
                    </div>
                  </div>
                </Card>
              )
            })}
          </div>
        )}
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-4 text-success">
          Completed Orders ({completedOrders.length})
        </h2>

        {completedOrders.length === 0 ? (
          <Card className="p-8 text-center text-muted">
            No delivered orders
          </Card>
        ) : (
          <div className="space-y-3">
            {completedOrders.map((o) => (
              <Card key={o.id} className="p-4 flex justify-between items-center">
                <div>
                  <p className="font-mono text-sm"># {o.id}</p>
                  <span
                    className={`px-3 py-1 rounded text-xs font-semibold ${statusColors[o.order_status ?? "preparing"]}`}
                  >
                    {(o.order_status ?? "preparing").toUpperCase()}
                  </span>
                </div>
                <p className="font-bold">₹{o.total.toFixed(2)}</p>
              </Card>
            ))}
          </div>
        )}
      </section>

      {/* Assign Delivery Agent Modal */}
      {/* <Dialog open={assignOpen} onOpenChange={setAssignOpen}> */}
      {/* <Dialog open={assignOpen} onOpenChange={(open) => { if (!open && selectedOrder) {
      ordersAPI.updateOrderStatus(selectedOrder.id, "preparing").catch(() => {})
    }
    setAssignOpen(open)
  }}
> */}

<Dialog
  open={assignOpen}
  onOpenChange={(open) => {
    if (!open && selectedOrder) {
      ordersAPI.updateOrderStatus(selectedOrder.id, "preparing").catch(() => {})
    }
    setAssignOpen(open)
  }}
>

        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Assign Delivery Agent</DialogTitle>
          </DialogHeader>

          {agents.length === 0 ? (
            <p className="text-sm text-muted">
              No verified delivery agents available.
            </p>
          ) : (
            <>
              <Select
                value={selectedAgent}
                onValueChange={setSelectedAgent}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select delivery agent" />
                </SelectTrigger>
                <SelectContent>
                  {agents.map((a) => (
                    <SelectItem key={a.id} value={a.id}>
                      Agent #{a.id.slice(-6)} • ⭐ {a.rating?.toFixed(1) ?? 0}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Button
                className="mt-4 w-full"
                disabled={!selectedAgent}
                onClick={assignAgent}
              >
                Assign Agent
              </Button>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
