// "use client"

// import { useState, useEffect } from "react"
// import { ordersAPI } from "@/lib/api"
// import { useRouter } from "next/navigation"
// import { Card } from "@/components/ui/card"
// import { Button } from "@/components/ui/button"
// import { useToast } from "@/hooks/use-toast"
// import { MapPin, Clock, FileText, Trash2 } from "lucide-react"
// import Link from "next/link"

// interface Order {
//   id: string
//   status: string
//   total: number
//   restaurant_id: string
//   delivery_address: string
//   created_at: string
//   items: any[]
//   restaurant?: {
//     name: string
//     image?: string
//   }
// }

// export default function OrdersPage() {
//   const [orders, setOrders] = useState<Order[]>([])
//   const [isLoading, setIsLoading] = useState(true)
//   const { toast } = useToast()
//   const router = useRouter()

//   useEffect(() => {
//     loadOrders()
//   }, [])

// const loadOrders = async () => {
//   try {
//     setIsLoading(true)
//     const data = await ordersAPI.getMyOrders()
//     const enriched = await attachRestaurantData(data)
//     setOrders(enriched)
//   } catch (error: any) {
//     toast({
//       title: "Error",
//       description: error.message,
//       variant: "destructive",
//     })
//   } finally {
//     setIsLoading(false)
//   }
// }


// const attachRestaurantData = async (orders: Order[]) => {
//   const updated = await Promise.all(
//     orders.map(async (order) => {
//       try {
//         const res = await fetch(
//           `${process.env.NEXT_PUBLIC_API_URL}/api/customers/restaurants/${order.restaurant_id}`,
//           { credentials: "include" }
//         )
//         const restaurant = await res.json()

//         return {
//           ...order,
//           restaurant: {
//             name: restaurant.name,
//             image: restaurant.image_url
//           }
//         }
//       } catch (err) {
//         return order
//       }
//     })
//   )

//   return updated
// }

  

//   const handleCancelOrder = async (orderId: string) => {
//     if (!window.confirm("Are you sure you want to cancel this order?")) return

//     try {
//       await ordersAPI.cancelOrder(orderId)
//       toast({
//         title: "Order cancelled",
//         description: "Your order has been cancelled successfully",
//       })
//       loadOrders()
//     } catch (error: any) {
//       toast({
//         title: "Error",
//         description: error.message,
//         variant: "destructive",
//       })
//     }
//   }

//   const getStatusColor = (status: string) => {
//     const colors: { [key: string]: string } = {
//       pending: "bg-yellow-100 text-yellow-800",
//       confirmed: "bg-blue-100 text-blue-800",
//       preparing: "bg-purple-100 text-purple-800",
//       ready: "bg-indigo-100 text-indigo-800",
//       assigned: "bg-orange-100 text-orange-800",
//       picked_up: "bg-orange-100 text-orange-800",
//       in_transit: "bg-orange-100 text-orange-800",
//       delivered: "bg-green-100 text-green-800",
//       cancelled: "bg-red-100 text-red-800",
//     }
//     return colors[status] || "bg-gray-100 text-gray-800"
//   }

//   if (isLoading) {
//     return (
//       <div className="flex items-center justify-center min-h-screen">
//         <div className="text-center">
//           <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin mx-auto mb-4"></div>
//           <p>Loading orders...</p>
//         </div>
//       </div>
//     )
//   }

//   return (
//     <div>
//       <h1 className="text-4xl font-bold mb-8">My Orders</h1>

//       {orders.length === 0 ? (
//         <Card className="p-12 text-center">
//           <p className="text-lg text-muted mb-4">You haven't placed any orders yet.</p>
//           <Link href="/customer">
//             <Button className="bg-primary text-white">Browse Restaurants</Button>
//           </Link>
//         </Card>
//       ) : (
//         <div className="space-y-6">
//           {orders.map((order) => (
//             <Card key={order.id} className="p-6">
//               <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
//                 <div>
//                   <p className="text-sm text-muted">Order ID</p>
//                   <p className="font-mono text-sm font-semibold">{order.id}</p>
//                 </div>
//                 <div>
//                   <p className="text-sm text-muted">Status</p>
//                   <span
//                     className={`inline-block px-3 py-1 rounded text-sm font-semibold ${getStatusColor(order.status)}`}
//                   >
//                     {order.status.toUpperCase().replace("_", " ")}
//                   </span>
//                 </div>
//                 <div>
//                   <p className="text-sm text-muted">Total</p>
//                   <p className="font-bold text-lg text-primary">₹{order.total?.toFixed(2)}</p>
//                 </div>
//                 <div>
//                   <p className="text-sm text-muted">Items</p>
//                   <p className="font-semibold">{order.items?.length || 0} items</p>
//                 </div>
//               </div>

//               <div className="flex items-center gap-2 text-sm text-muted mb-4 pb-4 border-b border-border">
//                 <MapPin className="w-4 h-4" />
//                 <span>{order.delivery_address}</span>
//               </div>

//               <div className="flex items-center justify-between">
//                 <div className="flex items-center gap-2 text-xs text-muted">
//                   <Clock className="w-4 h-4" />
//                   <span>{new Date(order.created_at).toLocaleDateString()}</span>
//                 </div>

//                 <div className="flex gap-2">
//                   <Link href={`/customer/orders/${order.id}`}>
//                     <Button size="sm" variant="outline" className="gap-2 bg-transparent">
//                       <FileText className="w-4 h-4" />
//                       View Details
//                     </Button>
//                   </Link>

//                   {["pending", "confirmed"].includes(order.status) && (
//                     <Button
//                       size="sm"
//                       variant="outline"
//                       onClick={() => handleCancelOrder(order.id)}
//                       className="gap-2 text-error hover:text-error"
//                     >
//                       <Trash2 className="w-4 h-4" />
//                       Cancel
//                     </Button>
//                   )}
//                 </div>
//               </div>
//             </Card>
//           ))}
//         </div>
//       )}
//     </div>
//   )
// }
"use client"

import { useState, useEffect } from "react"
import { ordersAPI } from "@/lib/api"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { MapPin, Clock, FileText, Trash2 } from "lucide-react"
import Link from "next/link"

interface Order {
  id: string
  status: string
  total: number
  restaurant_id: string
  delivery_address: string
  created_at: string
  items: any[]
  restaurant?: {
    name: string
    image?: string
  }
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    loadOrders()
  }, [])

  const loadOrders = async () => {
    try {
      setIsLoading(true)
      const data = await ordersAPI.getMyOrders()
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

  const handleCancelOrder = async (orderId: string) => {
    if (!window.confirm("Are you sure you want to cancel this order?")) return

    try {
      await ordersAPI.cancelOrder(orderId)
      toast({
        title: "Order cancelled",
        description: "Your order has been cancelled successfully",
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
      cancelled: "bg-red-100 text-red-800",
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

  return (
    <div>
      <h1 className="text-4xl font-bold mb-8">My Orders</h1>

      {orders.length === 0 ? (
        <Card className="p-12 text-center">
          <p className="text-lg text-muted mb-4">You haven't placed any orders yet.</p>
          <Link href="/customer">
            <Button className="bg-primary text-white">Browse Restaurants</Button>
          </Link>
        </Card>
      ) : (
        <div className="space-y-6">
          {orders.map((order) => (
            <Card key={order.id} className="p-6">
              
              {order.restaurant && (
                <div className="flex items-center gap-4 mb-6">
                  <img
                    src={order.restaurant.image}
                    alt={order.restaurant.name}
                    className="w-16 h-16 rounded-md object-cover"
                  />
                  <div>
                    <p className="font-bold text-lg">{order.restaurant.name}</p>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <p className="text-sm text-muted">Order ID</p>
                  <p className="font-mono text-sm font-semibold">{order.id}</p>
                </div>
                <div>
                  <p className="text-sm text-muted">Status</p>
                  <span
                    className={`inline-block px-3 py-1 rounded text-sm font-semibold ${getStatusColor(order.status)}`}
                  >
                    {order.status.toUpperCase().replace("_", " ")}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-muted">Total</p>
                  <p className="font-bold text-lg text-primary">₹{order.total?.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted">Items</p>
                  <p className="font-semibold">{order.items?.length || 0} items</p>
                </div>
              </div>

              <div className="flex items-center gap-2 text-sm text-muted mb-4 pb-4 border-b border-border">
                <MapPin className="w-4 h-4" />
                <span>{order.delivery_address}</span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs text-muted">
                  <Clock className="w-4 h-4" />
                  <span>{new Date(order.created_at).toLocaleDateString()}</span>
                </div>

                <div className="flex gap-2">
                  <Link href={`/customer/orders/${order.id}`}>
                    <Button size="sm" variant="outline" className="gap-2 bg-transparent">
                      <FileText className="w-4 h-4" />
                      View Details
                    </Button>
                  </Link>

                  {["pending", "confirmed"].includes(order.status) && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleCancelOrder(order.id)}
                      className="gap-2 text-error hover:text-error"
                    >
                      <Trash2 className="w-4 h-4" />
                      Cancel
                    </Button>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
