// "use client"

// import { useState, useEffect } from "react"
// import { useParams, useRouter } from "next/navigation"
// import { ordersAPI } from "@/lib/api"
// import { useToast } from "@/hooks/use-toast"
// import { Card } from "@/components/ui/card"
// import { Button } from "@/components/ui/button"
// import { ArrowLeft, Clock, Truck, CheckCircle } from "lucide-react"
// import Link from "next/link"

// interface OrderItem {
//   name: string
//   quantity: number
//   price: number
//   image?: string
// }

// interface RestaurantMeta {
//   name: string
//   image?: string
// }

// interface Order {
//   id: string
//   order_status: string
//   total: number
//   subtotal: number
//   delivery_fee: number
//   discount: number
//   delivery_address: string
//   delivery_phone: string
//   payment_method: string
//   created_at: string
//   items: OrderItem[]
//   estimated_delivery_time?: number
//   restaurant?: RestaurantMeta
// }

// export default function OrderDetailsPage() {
//   const params = useParams()
//   const orderId = params.id as string
//   const router = useRouter()
//   const { toast } = useToast()

//   const [order, setOrder] = useState<Order | null>(null)
//   const [isLoading, setIsLoading] = useState(true)

//   // poll every 5 seconds
//   useEffect(() => {
//     loadOrder()
//     const interval = setInterval(loadOrder, 5000)
//     return () => clearInterval(interval)
//   }, [orderId])

//   const loadOrder = async () => {
//     try {
//       const data = await ordersAPI.getOrder(orderId)
//       setOrder(data)
//     } catch (error: any) {
//       toast({
//         title: "Error loading order",
//         description: error.message,
//         variant: "destructive",
//       })
//       router.push("/customer/orders")
//     } finally {
//       setIsLoading(false)
//     }
//   }

//   const steps = [
//     { key: "preparing", label: "Preparing", icon: <Clock className="w-4 h-4" /> },
//     { key: "searching", label: "Searching Delivery Partner", icon: <Truck className="w-4 h-4" /> },
//     { key: "arriving", label: "Driver Arriving", icon: <Truck className="w-4 h-4" /> },
//     { key: "in-transit", label: "In Transit", icon: <Truck className="w-4 h-4" /> },
//     { key: "delivered", label: "Delivered", icon: <CheckCircle className="w-4 h-4" /> },
//   ]

//   const getStatusIndex = (status: string) => {
//     return steps.findIndex((s) => s.key === status)
//   }

//   if (isLoading) {
//     return (
//       <div className="flex items-center justify-center min-h-screen">
//         <div className="text-center">
//           <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin mx-auto mb-4"></div>
//           <p>Loading order details...</p>
//         </div>
//       </div>
//     )
//   }

//   if (!order) {
//     return <div className="p-6">Order not found.</div>
//   }

//   const currentIndex = getStatusIndex(order.order_status)

//   return (
//     <div className="p-6">
//       <Link href="/customer/orders">
//         <Button variant="ghost" className="mb-6 gap-2">
//           <ArrowLeft className="w-4 h-4" /> Back to Orders
//         </Button>
//       </Link>

//       {/* Restaurant Info */}
//       {order.restaurant && (
//         <Card className="p-4 mb-6 flex items-center gap-4">
//           <img
//             src={order.restaurant.image || "/placeholder.jpg"}
//             alt={order.restaurant.name}
//             className="w-20 h-20 rounded-lg object-cover"
//           />
//           <div>
//             <p className="font-bold text-xl">{order.restaurant.name}</p>
//             <p className="text-sm dark">Ordered from this restaurant</p>
//           </div>
//         </Card>
//       )}

//       {/* Order Info */}
//       <Card className="p-6 mb-6">
//         <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
//           <div>
//             <p className="text-sm dark">Order ID</p>
//             <p className="font-mono font-semibold">{order.id}</p>
//           </div>
//           <div>
//             <p className="text-sm dark">Order Date</p>
//             <p>{new Date(order.created_at).toLocaleString()}</p>
//           </div>
//           <div>
//             <p className="text-sm dark">Total</p>
//             <p className="text-2xl font-bold text-primary">₹{order.total?.toFixed(2)}</p>
//           </div>
//         </div>
//       </Card>

//       {/* Vertical progress */}
//       <Card className="p-6 mb-6">
//         <h2 className="text-lg font-bold mb-4">Order Progress</h2>
//         <div className="relative flex flex-col space-y-6">
//           {steps.map((step, index) => {
//             const isCompleted = index <= currentIndex
//             const isActive = index === currentIndex

//             return (
//               <div key={step.key} className="flex items-center space-x-4">
//                 <div className="flex flex-col items-center">
//                   <div
//                     className={`w-8 h-8 rounded-full flex items-center justify-center text-white ${
//                       isCompleted ? "bg-primary" : "bg-gray-300"
//                     } ${isActive ? "ring-4 ring-primary/30" : ""}`}
//                   >
//                     {step.icon}
//                   </div>
//                   {index < steps.length - 1 && (
//                     <div className="h-8 w-1 bg-gray-300 relative">
//                       <div
//                         className={`absolute top-0 left-0 w-1 ${
//                           isCompleted ? "bg-primary" : "bg-gray-300"
//                         }`}
//                         style={{
//                           height: isCompleted ? "100%" : "0%",
//                           transition: "height 0.3s ease",
//                         }}
//                       ></div>
//                     </div>
//                   )}
//                 </div>
//                 <div className="flex-1">
//                   <p className={`font-semibold ${isActive ? "text-primary" : ""}`}>
//                     {step.label}
//                   </p>
//                   {isActive && (
//                     <p className="text-xs dark mt-1">
//                       Current stage: {step.label.toLowerCase()}
//                     </p>
//                   )}
//                 </div>
//               </div>
//             )
//           })}
//         </div>
//       </Card>

//       {/* Items Section */}
//       <Card className="p-6 mb-6">
//         <h2 className="text-lg font-bold mb-4">Ordered Items</h2>
//         <div className="space-y-4">
//           {order.items.map((item, idx) => (
//             <div
//               key={idx}
//               className="flex items-center justify-between border-b border-border pb-3 last:border-b-0"
//             >
//               <div className="flex items-center gap-4">
//                 <img
//                   src={item.image || "/placeholder-food.jpg"}
//                   alt={item.name}
//                   className="w-16 h-16 rounded-lg object-cover"
//                 />
//                 <div>
//                   <p className="font-semibold">{item.name}</p>
//                   <p className="text-sm dark">Qty: {item.quantity}</p>
//                 </div>
//               </div>
//               <p className="font-bold">₹{(item.price * item.quantity).toFixed(2)}</p>
//             </div>
//           ))}
//         </div>
//       </Card>

//       {/* Delivery Details */}
//       <Card className="p-6 mb-6">
//         <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
//           <Truck className="w-5 h-5" /> Delivery Details
//         </h2>
//         <div className="space-y-3">
//           <div>
//             <p className="text-sm dark">Delivery Address</p>
//             <p className="font-semibold">{order.delivery_address}</p>
//           </div>
//           <div>
//             <p className="text-sm dark">Phone</p>
//             <p className="font-semibold">{order.delivery_phone}</p>
//           </div>
//           {order.estimated_delivery_time && (
//             <div>
//               <p className="text-sm dark">Est. Delivery Time</p>
//               <p className="font-semibold">{order.estimated_delivery_time} mins</p>
//             </div>
//           )}
//         </div>
//       </Card>

//       {/* Price Breakdown */}
//       <Card className="p-6">
//         <h2 className="text-lg font-bold mb-4">Price Breakdown</h2>
//         <div className="space-y-2 text-sm">
//           <div className="flex justify-between">
//             <span>Subtotal</span>
//             <span>₹{order.subtotal?.toFixed(2)}</span>
//           </div>
//           <div className="flex justify-between">
//             <span>Delivery Fee</span>
//             <span>₹{order.delivery_fee?.toFixed(2)}</span>
//           </div>
//           {order.discount > 0 && (
//             <div className="flex justify-between text-green-600">
//               <span>Discount</span>
//               <span>-₹{order.discount?.toFixed(2)}</span>
//             </div>
//           )}
//           <div className="border-t border-border pt-2 font-bold flex justify-between">
//             <span>Total</span>
//             <span className="text-primary">₹{order.total?.toFixed(2)}</span>
//           </div>
//           <div className="mt-4 pt-2 border-t border-border">
//             <p className="dark">Payment: {order.payment_method?.toUpperCase()}</p>
//           </div>
//         </div>
//       </Card>
//     </div>
//   )
// }
"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { ordersAPI } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Clock, Truck, CheckCircle } from "lucide-react"
import Link from "next/link"

interface OrderItem {
  name: string
  quantity: number
  price: number
  image?: string
}

interface RestaurantMeta {
  name: string
  image?: string
}

interface Order {
  id: string
  status: string // Payment status (paid, pending, etc.)
  order_status: string // Order tracking status (preparing, searching, etc.)
  total: number
  subtotal: number
  delivery_fee: number
  discount: number
  delivery_address: string
  delivery_phone: string
  payment_method: string
  created_at: string
  items: OrderItem[]
  estimated_delivery_time?: number
  restaurant?: RestaurantMeta
}

export default function OrderDetailsPage() {
  const params = useParams()
  const orderId = params.id as string
  const router = useRouter()
  const { toast } = useToast()

  const [order, setOrder] = useState<Order | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // poll every 5 seconds
  useEffect(() => {
    loadOrder()
    const interval = setInterval(loadOrder, 5000)
    return () => clearInterval(interval)
  }, [orderId])

  const loadOrder = async () => {
    try {
      const data = await ordersAPI.getOrder(orderId)
      console.log("Order data received:", data) // Debug log
      setOrder(data)
    } catch (error: any) {
      console.error("Error loading order:", error) // Debug log
      toast({
        title: "Error loading order",
        description: error.message,
        variant: "destructive",
      })
      // Don't redirect immediately on first load, only if not loading
      if (!isLoading) {
        router.push("/customer/orders")
      }
    } finally {
      setIsLoading(false)
    }
  }

  // Map order_status (not payment status) to display steps
const getStepsForStatus = () => {
  return [
    { key: "preparing", label: "Preparing", icon: <Clock className="w-4 h-4" /> },
    { key: "searching", label: "Searching Driver", icon: <Truck className="w-4 h-4" /> },
    { key: "arriving", label: "Driver Arriving", icon: <Truck className="w-4 h-4" /> },
    { key: "waiting", label: "Waiting at Restaurant", icon: <Clock className="w-4 h-4" /> },
    { key: "in-transit", label: "In Transit", icon: <Truck className="w-4 h-4" /> },
    { key: "delivered", label: "Delivered", icon: <CheckCircle className="w-4 h-4" /> },
  ]
}


  const getStatusIndex = (orderStatus: string) => {
    const statusLower = orderStatus?.toLowerCase().replace("_", "-") || ""
    const steps = getStepsForStatus()
    const index = steps.findIndex((s) => s.key === statusLower)
    return index >= 0 ? index : 0 // Return 0 if not found instead of -1
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
    return <div className="p-6">Order not found.</div>
  }

  const steps = getStepsForStatus()
  const currentIndex = getStatusIndex(order.order_status)

  return (
    <div className="p-6">
      <Link href="/customer/orders">
        <Button variant="ghost" className="mb-6 gap-2">
          <ArrowLeft className="w-4 h-4" /> Back to Orders
        </Button>
      </Link>

      {/* Restaurant Info */}
      {order.restaurant && (
        <Card className="p-4 mb-6 flex items-center gap-4">
          <img
            src={order.restaurant.image || "/placeholder.jpg"}
            alt={order.restaurant.name}
            className="w-20 h-20 rounded-lg object-cover"
          />
          <div>
            <p className="font-bold text-xl">{order.restaurant.name}</p>
            <p className="text-sm dark">Ordered from this restaurant</p>
          </div>
        </Card>
      )}

      {/* Order Info */}
      <Card className="p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm dark">Order ID</p>
            <p className="font-mono font-semibold">{order.id}</p>
          </div>
          <div>
            <p className="text-sm dark">Order Date</p>
            <p>{new Date(order.created_at).toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm dark">Total</p>
            <p className="text-2xl font-bold text-primary">₹{order.total?.toFixed(2)}</p>
          </div>
        </div>
      </Card>

      {/* Current Status Badge */}
      <Card className="p-6 mb-6">
        <h2 className="text-lg font-bold mb-4">Current Status</h2>
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
            {steps[currentIndex]?.icon}
          </div>
          <div>
            <p className="font-semibold text-lg">{steps[currentIndex]?.label}</p>
            <p className="text-sm dark capitalize">{order.order_status.replace("_", " ")}</p>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t">
          <p className="text-xs dark">
            Payment Status: <span className="font-semibold capitalize">{order.status}</span>
          </p>
        </div>
      </Card>

      {/* Vertical progress */}
      <Card className="p-6 mb-6">
        <h2 className="text-lg font-bold mb-4">Order Progress</h2>
        <div className="relative flex flex-col space-y-6">
          {steps.map((step, index) => {
            const isCompleted = index <= currentIndex
            const isActive = index === currentIndex

            return (
              <div key={step.key} className="flex items-center space-x-4">
                <div className="flex flex-col items-center">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-white ${
                      isCompleted ? "bg-primary" : "bg-gray-300"
                    } ${isActive ? "ring-4 ring-primary/30" : ""}`}
                  >
                    {step.icon}
                  </div>
                  {index < steps.length - 1 && (
                    <div className="h-8 w-1 bg-gray-300 relative">
                      <div
                        className={`absolute top-0 left-0 w-1 ${
                          isCompleted ? "bg-primary" : "bg-gray-300"
                        }`}
                        style={{
                          height: isCompleted ? "100%" : "0%",
                          transition: "height 0.3s ease",
                        }}
                      ></div>
                    </div>
                  )}
                </div>
                <div className="flex-1">
                  <p className={`font-semibold ${isActive ? "text-primary" : ""}`}>
                    {step.label}
                  </p>
                  {isActive && (
                    <p className="text-xs dark mt-1">
                      Current stage: {step.label.toLowerCase()}
                    </p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </Card>

      {/* Items Section */}
      <Card className="p-6 mb-6">
        <h2 className="text-lg font-bold mb-4">Ordered Items</h2>
        <div className="space-y-4">
          {order.items && order.items.length > 0 ? (
            order.items.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between border-b border-border pb-3 last:border-b-0"
              >
                <div className="flex items-center gap-4">
                  <img
                    src={item.image || "/placeholder-food.jpg"}
                    alt={item.name}
                    className="w-16 h-16 rounded-lg object-cover"
                  />
                  <div>
                    <p className="font-semibold">{item.name}</p>
                    <p className="text-sm dark">Qty: {item.quantity}</p>
                  </div>
                </div>
                <p className="font-bold">₹{(item.price * item.quantity).toFixed(2)}</p>
              </div>
            ))
          ) : (
            <p className="dark">No items found</p>
          )}
        </div>
      </Card>

      {/* Delivery Details */}
      <Card className="p-6 mb-6">
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
          <Truck className="w-5 h-5" /> Delivery Details
        </h2>
        <div className="space-y-3">
          <div>
            <p className="text-sm dark">Delivery Address</p>
            <p className="font-semibold">{order.delivery_address}</p>
          </div>
          <div>
            <p className="text-sm dark">Phone</p>
            <p className="font-semibold">{order.delivery_phone}</p>
          </div>
          {order.estimated_delivery_time && (
            <div>
              <p className="text-sm dark">Est. Delivery Time</p>
              <p className="font-semibold">{order.estimated_delivery_time} mins</p>
            </div>
          )}
        </div>
      </Card>

      {/* Price Breakdown */}
      <Card className="p-6">
        <h2 className="text-lg font-bold mb-4">Price Breakdown</h2>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span>Subtotal</span>
            <span>₹{order.subtotal?.toFixed(2) || "0.00"}</span>
          </div>
          <div className="flex justify-between">
            <span>Delivery Fee</span>
            <span>₹{order.delivery_fee?.toFixed(2) || "0.00"}</span>
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
            <p className="dark">Payment: {order.payment_method?.toUpperCase()}</p>
          </div>
        </div>
      </Card>
    </div>
  )
}