"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
// import { ordersAPI } from "@/lib/api"
import { CreditCard, UtensilsCrossed, ArrowLeft, User, Phone, MapPin } from "lucide-react"
import Link from "next/link"

interface CartItem {
  menu_item_id: string
  menuItemId?: string
  name: string
  price: number
  quantity: number
  special_instructions?: string
}

interface CheckoutData {
  restaurant_id: string
  items: CartItem[]
  delivery_address: string
  delivery_phone: string
  payment_method: string
  coupon_code?: string
  special_instructions?: string
  subtotal: number
  delivery_fee: number
  discount: number
  total: number
  name?: string
}

export default function CheckoutPage() {
  const router = useRouter()
  const { toast } = useToast()

  const [checkoutData, setCheckoutData] = useState<CheckoutData | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)

  const [user, setUser] = useState<any>(null)

  const [selectedPayment, setSelectedPayment] = useState<string>("upi")
  const [cardDetails, setCardDetails] = useState({
    cardNumber: "",
    cardName: "",
    expiry: "",
    cvv: "",
  })

  const paymentMethods = [
    { id: "upi", name: "UPI", icon: "📱", description: "Google Pay, PhonePe, Paytm" },
    { id: "card", name: "Credit/Debit Card", icon: "💳", description: "Visa, Mastercard, RuPay" },
    { id: "wallet", name: "Digital Wallet", icon: "💰", description: "Apple Pay, Google Wallet" },
    { id: "cod", name: "Cash on Delivery", icon: "💵", description: "Pay when you receive" },
  ]

// useEffect(() => {
//   // Load checkout data
//   const stored = sessionStorage.getItem("checkoutData")
//   if (stored) {
//     setCheckoutData(JSON.parse(stored))
//     localStorage.removeItem("checkoutData")
//   }

//   // Load stored user details
//   const storedUser = sessionStorage.getItem("user")
//   if (storedUser) {
//     setUser(JSON.parse(storedUser))
//   }
// }, [])


useEffect(() => {
  console.log("=== CHECKOUT PAGE LOADED ===");

  const storedCheckout = sessionStorage.getItem("checkoutData");
  // Prefer sessionStorage for ephemeral checkout info, but fall back to localStorage
  // for user/auth data because `AuthProvider` stores tokens/user in localStorage.
  const storedUser = sessionStorage.getItem("user") ?? localStorage.getItem("user");

  let userData = null;

  if (storedUser) {
    try {
      userData = JSON.parse(storedUser);
      console.log("✅ Parsed user:", userData);
      setUser(userData);
    } catch (err) {
      console.error("❌ Failed to parse user:", err);
    }
  } else {
    console.warn("⚠ No user found in sessionStorage");
  }

  if (storedCheckout) {
    try {
      const raw = JSON.parse(storedCheckout);
      console.log("Parsed checkout data:", raw);

      const formattedItems = raw.items.map((item: any) => ({
        menuItemId: item.menu_item_id ?? item.menuItemId,
        name: item.name,
        price: item.price,
        quantity: item.quantity,
      }));

      const finalData = {
        restaurant_id: raw.restaurant_id,
        items: formattedItems,
        subtotal: raw.subtotal,
        delivery_fee: raw.delivery_fee,
        discount: raw.discount ?? 0,
        total: raw.total,

        // ✅ ALWAYS USE CHECKOUT DATA (guaranteed to exist)
        name: raw.name,
        delivery_address: raw.delivery_address,
        delivery_phone: raw.delivery_phone,

        payment_method: raw.payment_method ?? "upi",
      };

      console.log("✅ Final checkoutData object:", finalData);

      setCheckoutData(finalData);
    } catch (err) {
      console.error("❌ Error parsing checkoutData:", err);
    }
  } else {
    console.warn("⚠ No checkoutData in sessionStorage");
  }
}, []);


  useEffect(() => {
  const navigationEntry = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming | undefined;
  const navigationType = navigationEntry?.type;

  // ✅ If user navigated back, DO NOT clear the cart
  if (navigationType === "back_forward") {
    console.log("🛑 Back navigation detected — cart preserved.");
    return;
  }
}, []);



// const handlePaymentSubmit = async () => {
//   if (!checkoutData) return;

//   setIsProcessing(true);

//   try {
//       const response = await fetch("http://localhost:8000/api/orders/create", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//         // auth-context stores tokens in localStorage; use that here so backend
//         // receives the actual access token and doesn't respond 401.
//         Authorization: `Bearer ${localStorage.getItem("access_token")}`,
//       },
//       body: JSON.stringify({
//         restaurant_id: checkoutData.restaurant_id,
//         items: checkoutData.items.map(i => ({
//           menu_item_id: i.menuItemId,
//           quantity: i.quantity,
//         })),
//         delivery_address: checkoutData.delivery_address,
//         delivery_phone: checkoutData.delivery_phone,
//         payment_method: checkoutData.payment_method,
//         subtotal: checkoutData.subtotal,
//         delivery_fee: checkoutData.delivery_fee,
//         discount: checkoutData.discount,
//         total: checkoutData.total,
//       }),
//     });

//     const data = await response.json();

//     if (!response.ok) {
//       toast({
//         title: "Order Failed",
//         description: data.detail || "Something went wrong",
//         variant: "destructive",
//       });
//       return;
//     }

//     // ✅ Clear cart ONLY after a successful order
//     sessionStorage.removeItem("cart");
//     sessionStorage.removeItem("checkoutData");

//     toast({
//       title: "Order Placed ✅",
//       description: `Order ID: ${data.id}`,
//     });

//     router.push(`/customer/orders/${data.id}`);

//   } catch (err: any) {
//     toast({
//       title: "Error",
//       description: err.message,
//       variant: "destructive",
//     });
//   } finally {
//     setIsProcessing(false);
//   }
// };

const handlePaymentSubmit = async () => {
  if (!checkoutData) return;

  setIsProcessing(true);

  try {
    const response = await fetch("http://localhost:8000/api/orders/create", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
      body: JSON.stringify({
        restaurant_id: checkoutData.restaurant_id,
        items: checkoutData.items.map(i => ({
          // ✅ FIXED: ensure menu_item_id is ALWAYS sent
          menu_item_id: i.menu_item_id ?? i.menuItemId,
          quantity: i.quantity,
        })),
        delivery_address: checkoutData.delivery_address,
        delivery_phone: checkoutData.delivery_phone,
        payment_method: checkoutData.payment_method,
        subtotal: checkoutData.subtotal,
        delivery_fee: checkoutData.delivery_fee,
        discount: checkoutData.discount,
        total: checkoutData.total,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      toast({
        title: "Order Failed",
        description: data.detail || "Something went wrong",
        variant: "destructive",
      });
      return;
    }

    // ✅ Clear cart ONLY after success
    sessionStorage.removeItem("cart");
    sessionStorage.removeItem("checkoutData");

    toast({
      title: "Order Placed ✅",
      description: `Order ID: ${data.id}`,
    });

    router.push(`/customer/orders/${data.id}`);

  } catch (err: any) {
    toast({
      title: "Error",
      description: err.message,
      variant: "destructive",
    });
  } finally {
    setIsProcessing(false);
  }
};



  if (!checkoutData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <UtensilsCrossed className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
          <p className="mb-4">Your cart is empty</p>
          <Link href="/customer">
            <Button>Continue Shopping</Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <Link href="/customer">
        <Button variant="ghost" className="mb-6 gap-2">
          <ArrowLeft className="w-4 h-4" />
          Back
        </Button>
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          
          {/* ✅ USER DELIVERY DETAILS CARD (NEW) */}
          <Card className="p-6">
            <h2 className="text-xl font-bold mb-4">Delivery Details</h2>

            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-3">
                <User className="w-5 h-5 text-primary" />
                <p><strong>Name:</strong> {checkoutData.name}</p>
              </div>

              <div className="flex items-center gap-3">
                <Phone className="w-5 h-5 text-primary" />
                <p><strong>Phone:</strong> {checkoutData.delivery_phone}</p>
              </div>

              <div className="flex items-center gap-3">
                <MapPin className="w-5 h-5 text-primary" />
                <p><strong>Address:</strong> {checkoutData.delivery_address}</p>
              </div>
            </div>
          </Card>


          {/* PAYMENT METHODS */}
          <Card className="p-6">
            <h2 className="text-xl font-bold mb-4">Payment Method</h2>
            <div className="grid grid-cols-1 gap-3">
              {paymentMethods.map((method) => (
                <button
                  key={method.id}
                  onClick={() => setSelectedPayment(method.id)}
                  className={`p-4 border rounded-lg text-left transition-all ${
                    selectedPayment === method.id
                      ? "border-primary bg-primary/10"
                      : "border-border hover:border-primary/50"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">{method.icon}</span>
                    <div className="flex-1">
                      <p className="font-semibold">{method.name}</p>
                      <p className="text-sm text-gray-700 dark:text-gray-300">{method.description}</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </Card>

          {/* CARD FORM */}
          {selectedPayment === "card" && (
            <Card className="p-6 space-y-4">
              <h3 className="font-semibold flex items-center gap-2">
                <CreditCard className="w-5 h-5" /> Card Details
              </h3>

              <input
                type="text"
                placeholder="Card Number"
                className="border p-2 rounded w-full"
                value={cardDetails.cardNumber}
                onChange={(e) =>
                  setCardDetails({
                    ...cardDetails,
                    cardNumber: e.target.value.replace(/\D/g, ""),
                  })
                }
              />
              <input
                type="text"
                placeholder="Cardholder Name"
                className="border p-2 rounded w-full"
                value={cardDetails.cardName}
                onChange={(e) =>
                  setCardDetails({ ...cardDetails, cardName: e.target.value })
                }
              />

              <div className="grid grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="MM/YY"
                  className="border p-2 rounded w-full"
                  value={cardDetails.expiry}
                  onChange={(e) =>
                    setCardDetails({ ...cardDetails, expiry: e.target.value })
                  }
                />
                <input
                  type="password"
                  placeholder="CVV"
                  className="border p-2 rounded w-full"
                  value={cardDetails.cvv}
                  onChange={(e) =>
                    setCardDetails({ ...cardDetails, cvv: e.target.value })
                  }
                />
              </div>
            </Card>
          )}
        </div>

        {/* ORDER SUMMARY */}
        <div>
          <Card className="p-6 sticky top-4">
            <h3 className="text-lg font-bold mb-4">Order Summary</h3>

            <div className="space-y-3 mb-4">
              {checkoutData.items.map((item, i) => (
                <div key={i} className="flex justify-between text-sm">
                  <span>
                    {item.quantity}× {item.name}
                  </span>
                  <span>₹{(item.price * item.quantity).toFixed(2)}</span>
                </div>
              ))}
            </div>

            <div className="border-t pt-3 text-sm space-y-2">
              <div className="flex justify-between">
                <span>Subtotal</span>
                <span>₹{checkoutData.subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>Delivery Fee</span>
                <span>₹{checkoutData.delivery_fee.toFixed(2)}</span>
              </div>
              {checkoutData.discount > 0 && (
                <div className="flex justify-between text-green-600">
                  <span>Discount</span>
                  <span>-₹{checkoutData.discount.toFixed(2)}</span>
                </div>
              )}
            </div>

            <div className="border-t pt-3 mt-4">
              <div className="flex justify-between font-bold text-lg">
                <span>Total</span>
                <span className="text-primary">₹{checkoutData.total.toFixed(2)}</span>
              </div>
            </div>

            <Button
              onClick={handlePaymentSubmit}
              disabled={isProcessing}
              className="w-full mt-4"
            >
              {isProcessing ? "Processing..." : "Place Order"}
            </Button>
          </Card>
        </div>
      </div>
    </div>
  )
}
