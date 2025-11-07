// "use client";

// import { useEffect, useState } from "react";
// import Image from "next/image";

// // Import the deliveryAPI from your api.ts file
// // import { deliveryAPI } from "@/lib/api";

// export default function DeliveryDashboard({ agentId }: { agentId: string }) {
//   const [stats, setStats] = useState<any>(null);
//   const [orders, setOrders] = useState<any[]>([]);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState<string | null>(null);

//   const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

//   const getAuthHeaders = () => {
//     const token = localStorage.getItem("access_token");
//     return {
//       "Content-Type": "application/json",
//       ...(token && { Authorization: `Bearer ${token}` }),
//     };
//   };

//   const fetchStats = async () => {
//     try {
//       console.log("Fetching stats for agent:", agentId);
//       const res = await fetch(`${API_BASE}/api/delivery/stats/${agentId}`, {
//         headers: getAuthHeaders(),
//       });
      
//       if (!res.ok) {
//         throw new Error(`Failed to fetch stats: ${res.status}`);
//       }
      
//       const data = await res.json();
//       console.log("Stats received:", data);
//       setStats(data);
//       setError(null);
//     } catch (error: any) {
//       console.error("Error fetching stats:", error);
//       setError(error.message);
//     }
//   };

//   const fetchOrders = async () => {
//     try {
//       console.log("Fetching orders for agent:", agentId);
//       const res = await fetch(`${API_BASE}/api/delivery/assigned_orders/${agentId}`, {
//         headers: getAuthHeaders(),
//       });
      
//       if (!res.ok) {
//         throw new Error(`Failed to fetch orders: ${res.status}`);
//       }
      
//       const data = await res.json();
//       console.log("Orders received:", data);
//       setOrders(data.orders || []);
//       setError(null);
//     } catch (error: any) {
//       console.error("Error fetching orders:", error);
//       setError(error.message);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const toggleStatus = async (newStatus: string) => {
//     try {
//       console.log("Updating status to:", newStatus);
//       const res = await fetch(`${API_BASE}/api/delivery/update_status/${agentId}?status=${newStatus}`, {
//         method: "POST",
//         headers: getAuthHeaders(),
//       });
      
//       if (!res.ok) {
//         throw new Error(`Failed to update status: ${res.status}`);
//       }
      
//       console.log("Status updated successfully");
//       await fetchStats();
//       setError(null);
//     } catch (error: any) {
//       console.error("Error updating status:", error);
//       setError(error.message);
//     }
//   };

//   useEffect(() => {
//     if (!agentId) {
//       console.error("No agentId provided");
//       setError("Agent ID is required");
//       setLoading(false);
//       return;
//     }

//     console.log("Component mounted with agentId:", agentId);
//     fetchStats();
//     fetchOrders();
    
//     const interval = setInterval(() => {
//       fetchStats();
//       fetchOrders();
//     }, 10000);
    
//     return () => clearInterval(interval);
//   }, [agentId]);

//   if (loading) {
//     return (
//       <div className="p-6 min-h-screen bg-gray-50 flex items-center justify-center">
//         <div className="text-gray-600">Loading dashboard...</div>
//       </div>
//     );
//   }

//   if (error) {
//     return (
//       <div className="p-6 min-h-screen bg-gray-50">
//         <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
//           <p className="font-semibold">Error loading dashboard</p>
//           <p className="text-sm">{error}</p>
//         </div>
//       </div>
//     );
//   }

//   return (
//     <div className="p-6 space-y-8 text-gray-900 bg-gray-50 min-h-screen">
//       <h1 className="text-3xl font-semibold text-gray-800">🚴 Delivery Agent Dashboard</h1>

//       {stats && (
//         <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
//           <div className="p-4 bg-white shadow-sm border border-gray-200 rounded-xl">
//             <span className="text-gray-600 text-sm">Total Deliveries</span>
//             <p className="text-2xl font-semibold text-gray-900 mt-1">{stats.total_deliveries}</p>
//           </div>
//           <div className="p-4 bg-white shadow-sm border border-gray-200 rounded-xl">
//             <span className="text-gray-600 text-sm">Average Rating</span>
//             <p className="text-2xl font-semibold text-gray-900 mt-1">⭐ {stats.avg_rating}</p>
//           </div>
//           <div className="p-4 bg-white shadow-sm border border-gray-200 rounded-xl">
//             <span className="text-gray-600 text-sm">Earnings</span>
//             <p className="text-2xl font-semibold text-gray-900 mt-1">₹{stats.total_earnings}</p>
//           </div>
//           <div className="p-4 bg-white shadow-sm border border-gray-200 rounded-xl">
//             <span className="text-gray-600 text-sm">Completed Orders</span>
//             <p className="text-2xl font-semibold text-gray-900 mt-1">{stats.completed_orders}</p>
//           </div>
//           <div className="p-4 bg-white shadow-sm border border-gray-200 rounded-xl">
//             <span className="text-gray-600 text-sm">Active Orders</span>
//             <p className="text-2xl font-semibold text-gray-900 mt-1">{stats.active_orders}</p>
//           </div>
//           <div className="p-4 bg-white shadow-sm border border-gray-200 rounded-xl">
//             <span className="text-gray-600 text-sm">Status</span>
//             <p className="text-lg font-semibold text-gray-900 mt-1 capitalize">{stats.status}</p>
//             <div className="mt-3 flex gap-2">
//               <button
//                 className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
//                 onClick={() => toggleStatus("online")}
//               >
//                 Go Online
//               </button>
//               <button
//                 className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
//                 onClick={() => toggleStatus("offline")}
//               >
//                 Go Offline
//               </button>
//             </div>
//           </div>
//         </div>
//       )}

//       <h2 className="text-2xl mt-8 font-semibold text-gray-800">📦 Active Orders</h2>
//       {orders.length === 0 ? (
//         <div className="p-8 bg-white shadow-sm border border-gray-200 rounded-xl text-center text-gray-500">
//           No active orders at the moment
//         </div>
//       ) : (
//         <div className="space-y-4">
//           {orders.map((o) => (
//             <div key={o.order_id} className="p-5 bg-white shadow-sm border border-gray-200 rounded-xl">
//               <h3 className="text-xl font-bold text-gray-900">{o.restaurant_name}</h3>
//               <div className="flex gap-4 mt-2 text-sm text-gray-600">
//                 <p>Status: <span className="font-medium text-gray-900">{o.order_status}</span></p>
//                 <p>Total: <span className="font-medium text-gray-900">₹{o.total}</span></p>
//               </div>
//               <div className="flex gap-4 mt-4 overflow-x-auto pb-2">
//                 {o.items.map((item: any) => (
//                   <div key={item.menu_item_id} className="text-center flex-shrink-0">
//                     <Image
//                       src={item.image_url}
//                       alt={item.name}
//                       width={80}
//                       height={80}
//                       className="rounded-lg border border-gray-200"
//                     />
//                     <p className="text-sm text-gray-700 mt-2">{item.name} × {item.quantity}</p>
//                   </div>
//                 ))}
//               </div>
//             </div>
//           ))}
//         </div>
//       )}
//     </div>
//   );
// }

"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import DeliveryDashboard from "@/components/DeliveryDashboard"; // Adjust path as needed

export default function DeliveryPage() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [agentId, setAgentId] = useState<string | null>(null);
  const [fetchingAgent, setFetchingAgent] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    const fetchAgentProfile = async () => {
      if (!isAuthenticated || !user) {
        console.log("Not authenticated, redirecting to home");
        router.push("/");
        return;
      }

      if (user.role !== "delivery_agent") {
        console.log("Not a delivery agent, redirecting");
        router.push("/");
        return;
      }

      try {
        console.log("Fetching delivery agent profile for user:", user);
        const token = localStorage.getItem("access_token");
        
        const response = await fetch(`${API_BASE}/api/delivery/profile`, {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch agent profile: ${response.status}`);
        }

        const agentData = await response.json();
        console.log("Agent profile fetched:", agentData);
        setAgentId(agentData._id);
        setError(null);
      } catch (err: any) {
        console.error("Error fetching agent profile:", err);
        setError(err.message);
      } finally {
        setFetchingAgent(false);
      }
    };

    if (!isLoading) {
      fetchAgentProfile();
    }
  }, [isAuthenticated, user, isLoading, router]);

  if (isLoading || fetchingAgent) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 rounded-full border-4 border-green-500 border-t-transparent animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
        <div className="max-w-md w-full">
          <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg">
            <h2 className="text-lg font-semibold mb-2">Error Loading Dashboard</h2>
            <p className="text-sm mb-4">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!agentId) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
        <div className="max-w-md w-full">
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-6 py-4 rounded-lg">
            <h2 className="text-lg font-semibold mb-2">Agent Profile Not Found</h2>
            <p className="text-sm mb-4">
              Your delivery agent profile hasn't been created yet. Please contact support.
            </p>
            <button
              onClick={() => router.push("/")}
              className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              Go Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  return <DeliveryDashboard agentId={agentId} />;
}