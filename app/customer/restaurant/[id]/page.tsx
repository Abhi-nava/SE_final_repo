"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import Link from "next/link"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { ArrowLeft, ShoppingCart, Plus, Minus } from "lucide-react"
import { useAuth } from "@/lib/auth-context"

interface MenuItem {
  id: string
  name: string
  description: string
  price: number
  category: string
  image_url: string
  daily_count: number      
}


interface Restaurant {
  id: string
  name: string
  description: string
  address: string
  opening_time: string
  closing_time: string
  rating: number
  total_ratings: number
  cuisine_types: string[]
}

interface CartItem {
  menuItemId: string
  name: string
  price: number
  quantity: number
}

export default function RestaurantPage() {
  const params = useParams()
  const { user } = useAuth()
  const router = useRouter()
  const restaurantId = params.id as string

  const [restaurant, setRestaurant] = useState<Restaurant | null>(null)
  const [menuItems, setMenuItems] = useState<MenuItem[]>([])
  const [cart, setCart] = useState<CartItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

  // ✅ Load cart on page load
  useEffect(() => {
    const stored = localStorage.getItem("cartData")
    if (stored) {
      const parsed = JSON.parse(stored)
      if (parsed.restaurant_id === restaurantId) {
        setCart(parsed.items)
      } else {
        setCart([]) // switching restaurant clears cart
      }
    }
    loadRestaurantData()
  }, [restaurantId])

  // ✅ Save cart on every update
  useEffect(() => {
    localStorage.setItem(
      "cartData",
      JSON.stringify({
        restaurant_id: restaurantId,
        items: cart,
      })
    )
  }, [cart])




  const loadRestaurantData = async () => {
    try {
      setIsLoading(true)

      const restaurantRes = await fetch(
        `http://localhost:8000/api/customers/restaurants/${restaurantId}`
      )
      if (!restaurantRes.ok) throw new Error("Failed to load restaurant")
      setRestaurant(await restaurantRes.json())

      const menuRes = await fetch(
        `http://localhost:8000/api/restaurants/${restaurantId}/menu`
      )
      if (!menuRes.ok) throw new Error("Failed to load menu")
      const menuData = await menuRes.json()
    console.log("Menu Data:", menuData) // ✅ Debug log

        setMenuItems(
          menuData.map((item: any) => ({
            ...item,
            id: item.id || item._id,
            daily_count: Number(item.daily_count) || 0,   // ✅ Ensure numeric
          }))

)
    } catch (err: any) {
      toast({ title: "Error", description: err.message, variant: "destructive" })
      router.push("/customer")
    } finally {
      setIsLoading(false)
    }
  }

//   // ✅ Prevent adding items from different restaurants
//   const handleAddToCart = (item: MenuItem) => {
//     const stored = localStorage.getItem("cartData")

//       const menuItem = menuItems.find((m) => m.id === item.id)

//       if (!menuItem) return

//       // ✅ If sold out
//       if (menuItem.daily_count <= 0) {
//         toast({
//           title: "Item unavailable",
//           description: `${item.name} is sold out for today.`,
//           variant: "destructive",
//         })
//         return
// }

//     if (stored) {
//       const parsed = JSON.parse(stored)
//       if (parsed.restaurant_id !== restaurantId && parsed.items.length > 0) {
//         toast({
//           title: "Cannot add item",
//           description: "You already have items from another restaurant.",
//           variant: "destructive",
//         })
//         return
//       }
//     }

//     const existing = cart.find((i) => i.menuItemId === item.id)

//     if (existing) {
//       setCart(
//         cart.map((i) =>
//           i.menuItemId === item.id ? { ...i, quantity: i.quantity + 1 } : i
//         )
//       )
//     } else {
//       setCart([...cart, { menuItemId: item.id, name: item.name, price: item.price, quantity: 1 }])
//     }

//     toast({ title: "Added to cart", description: `${item.name} added.` })
//   }

const handleAddToCart = (item: MenuItem) => {
  console.log("[CART] Adding item:", item)

  // ✅ Find menu item (contains daily_count)
  const menuItem = menuItems.find((m) => m.id === item.id)
  if (!menuItem) {
    console.warn("[CART] Menu item not found")
    return
  }

  // ✅ Out of stock
  if (menuItem.daily_count <= 0) {
    toast({
      title: "Item Unavailable",
      description: `${item.name} is sold out today.`,
      variant: "destructive",
    })
    return
  }

  // ✅ Check if already in cart
  const existing = cart.find((i) => i.menuItemId === item.id)

  // ✅ If adding more than available stock
  if (existing && existing.quantity >= menuItem.daily_count) {
    toast({
      title: "Limit Reached",
      description: `Only ${menuItem.daily_count} available today.`,
      variant: "destructive",
    })
    return
  }

  // ✅ Add or increase cart item
  let newCart
  if (existing) {
    newCart = cart.map((i) =>
      i.menuItemId === item.id ? { ...i, quantity: i.quantity + 1 } : i
    )
  } else {
    newCart = [
      ...cart,
      {
        menuItemId: item.id,
        name: item.name,
        price: item.price,
        quantity: 1,
      },
    ]
  }

  // ✅ Update cart state & persist to sessionStorage
  setCart(newCart)
  sessionStorage.setItem("cart", JSON.stringify(newCart))

  // ✅ Decrease daily_count locally so UI updates instantly
  const updatedMenu = menuItems.map((m) =>
    m.id === item.id ? { ...m, daily_count: m.daily_count - 1 } : m
  )
  setMenuItems(updatedMenu)

  console.log("[CART] Updated cart:", newCart)
  console.log("[CART] Updated menuItems:", updatedMenu)
}


const updateQuantity = (id: string, qty: number) => {
  const menuItem = menuItems.find((m) => m.id === id)
  const existing = cart.find((i) => i.menuItemId === id)

  if (!menuItem || !existing) return

  // ✅ Increasing quantity
  if (qty > existing.quantity) {
    if (menuItem.daily_count <= 0) {
      toast({
        title: "Stock limit reached",
        description: `No more stock available for ${menuItem.name}.`,
        variant: "destructive",
      })
      return
    }

    // ✅ Deduct stock
    setMenuItems(
      menuItems.map((m) =>
        m.id === id ? { ...m, daily_count: m.daily_count - 1 } : m
      )
    )
  }

  // ✅ Decreasing quantity → restore stock
  if (qty < existing.quantity) {
    setMenuItems(
      menuItems.map((m) =>
        m.id === id ? { ...m, daily_count: m.daily_count + 1 } : m
      )
    )
  }

  // ✅ Remove if zero
  if (qty <= 0) {
    setCart(cart.filter((i) => i.menuItemId !== id))
  } else {
    setCart(cart.map((i) => (i.menuItemId === id ? { ...i, quantity: qty } : i)))
  }
}


  const subtotal = cart.reduce((acc, item) => acc + item.price * item.quantity, 0)
  const deliveryFee = 50
  const total = subtotal + deliveryFee

  const goToCheckout = () => {
    if (!user) {
      toast({ title: "Login required", description: "Please login to continue", variant: "destructive" })
      return
    }

    const checkoutData = {
      restaurant_id: restaurantId,
      items: cart,
      subtotal,
      delivery_fee: deliveryFee,
      discount: 0,
      total,
      name: user.full_name,
      delivery_address: user.address,
      delivery_phone: user.phone,
      payment_method: "upi",
    }

    sessionStorage.setItem("checkoutData", JSON.stringify(checkoutData))
    router.push("/customer/checkout")
  }

  if (isLoading)
    return (
      <div className="flex justify-center items-center min-h-screen">
        <p>Loading...</p>
      </div>
    )

  return (
    <div className="p-6 relative">
      <Link href="/customer">
        <Button variant="ghost" className="mb-6 gap-2">
          <ArrowLeft className="w-4 h-4" /> Back
        </Button>
      </Link>

      {/* ✅ Restaurant Header */}
      <Card className="p-6 mb-6">
        <h1 className="text-3xl font-bold">{restaurant?.name}</h1>
        <p className="text-gray-600 mt-2">{restaurant?.description}</p>
      </Card>

      <h2 className="text-2xl font-semibold mb-4">Menu</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {menuItems.map((item) => (
          <Card key={item.id} className="p-4">
            <img
              src={
                item.image_url.startsWith("data:image")
                  ? item.image_url
                  : item.image_url.startsWith("http")
                  ? item.image_url
                  : `data:image/jpeg;base64,${item.image_url}`
              }
              className="w-full h-40 object-cover rounded-md"
            />

            <h3 className="font-semibold mt-2">{item.name}</h3>
            <p className="text-sm text-gray-600">{item.description}</p>

            <p className="font-bold mt-2">₹{item.price}</p>
            {item.daily_count <= 0 ? (
              <Button disabled className="mt-2 w-full opacity-50">
                Sold Out
              </Button>
            ) : (
              <Button className="mt-2 w-full" onClick={() => handleAddToCart(item)}>
                Add to Cart ({item.daily_count} left)
              </Button>
            )}

          </Card>
        ))}
      </div>

      {/* ✅ Floating Cart */}
      {cart.length > 0 && (
        <div className="fixed right-6 top-20 w-80 bg-white shadow-xl rounded-xl p-4 border z-50">
          <h3 className="text-lg font-bold flex items-center gap-2 mb-3">
            <ShoppingCart className="w-5 h-5" /> Cart
          </h3>

          <div className="max-h-80 overflow-y-auto space-y-3">
            {cart.map((item) => (
              <div key={item.menuItemId} className="border rounded-lg p-3">
                <p className="font-semibold">{item.name}</p>
                <p className="text-sm text-gray-500">₹{item.price}</p>

                <div className="flex items-center gap-3 mt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => updateQuantity(item.menuItemId, item.quantity - 1)}
                  >
                    <Minus className="w-4 h-4" />
                  </Button>

                  <span className="font-semibold">{item.quantity}</span>

                  <Button
                    size="sm"
                    onClick={() => updateQuantity(item.menuItemId, item.quantity + 1)}
                  >
                    <Plus className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 border-t pt-3">
            <p className="flex justify-between text-sm">
              <span>Subtotal:</span> <span>₹{subtotal}</span>
            </p>
            <p className="flex justify-between text-sm">
              <span>Delivery Fee:</span> <span>₹{deliveryFee}</span>
            </p>

            <p className="flex justify-between font-bold mt-2">
              <span>Total:</span> <span>₹{total}</span>
            </p>

            <Button className="mt-4 w-full" onClick={goToCheckout}>
              Checkout
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
