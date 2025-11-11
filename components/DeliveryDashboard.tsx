"use client";

import { useEffect, useState } from "react";
import Image from "next/image";

interface DeliveryDashboardProps {
  agentId: string;
}

interface Stats {
  total_deliveries: number;
  avg_rating: number;
  total_earnings: number;
  completed_orders: number;
  active_orders: number;
  status: string;
}

interface OrderItem {
  menu_item_id: string;
  name: string;
  quantity: number;
  image_url: string;
}

interface Order {
  order_id: string;
  restaurant_name: string;
  order_status: string;
  total: number;
  items: OrderItem[];
  delivery_address: string;
  delivery_phone: string;
}

export default function DeliveryDashboard({ agentId }: DeliveryDashboardProps) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const getAuthHeaders = () => {
    const token = localStorage.getItem("access_token");
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  };

  const fetchStats = async () => {
    try {
      console.log("Fetching stats for agent:", agentId);
      const res = await fetch(`${API_BASE}/api/delivery/stats/${agentId}`, {
        headers: getAuthHeaders(),
      });
      
      if (!res.ok) {
        throw new Error(`Failed to fetch stats: ${res.status}`);
      }
      
      const data = await res.json();
      console.log("Stats received:", data);
      setStats(data);
      setError(null);
    } catch (error: any) {
      console.error("Error fetching stats:", error);
      setError(error.message);
    }
  };

  const fetchOrders = async () => {
    try {
      console.log("Fetching orders for agent:", agentId);
      const res = await fetch(`${API_BASE}/api/delivery/assigned_orders/${agentId}`, {
        headers: getAuthHeaders(),
      });
      
      if (!res.ok) {
        throw new Error(`Failed to fetch orders: ${res.status}`);
      }
      
      const data = await res.json();
      console.log("Orders received:", data);
      setOrders(data.orders || []);
      setError(null);
    } catch (error: any) {
      console.error("Error fetching orders:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleStatus = async (newStatus: string) => {
    try {
      console.log("Updating status to:", newStatus);
      const res = await fetch(`${API_BASE}/api/delivery/update_status/${agentId}?status=${newStatus}`, {
        method: "POST",
        headers: getAuthHeaders(),
      });
      
      if (!res.ok) {
        throw new Error(`Failed to update status: ${res.status}`);
      }
      
      console.log("Status updated successfully");
      await fetchStats();
      setError(null);
    } catch (error: any) {
      console.error("Error updating status:", error);
      setError(error.message);
    }
  };

  useEffect(() => {
    if (!agentId) {
      console.error("No agentId provided");
      setError("Agent ID is required");
      setLoading(false);
      return;
    }

    console.log("Dashboard mounted with agentId:", agentId);
    fetchStats();
    fetchOrders();
    
    const interval = setInterval(() => {
      fetchStats();
      fetchOrders();
    }, 10000);
    
    return () => clearInterval(interval);
  }, [agentId]);

  if (loading) {
    return (
      <div className="p-6 min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 rounded-full border-4 border-green-500 border-t-transparent animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 min-h-screen bg-gray-50">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          <p className="font-semibold">Error loading dashboard</p>
          <p className="text-sm">{error}</p>
          <button
            onClick={() => {
              setError(null);
              setLoading(true);
              fetchStats();
              fetchOrders();
            }}
            className="mt-3 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8 text-gray-900 bg-gray-50 min-h-screen">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-semibold text-gray-800">🚴 Delivery Agent Dashboard</h1>
        <button
          onClick={() => {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            window.location.href = "/";
          }}
          className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
        >
          Logout
        </button>
      </div>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="p-4 bg-white shadow-sm border border-gray-200 rounded-xl">
            <span className="text-gray-600 text-sm">Total Deliveries</span>
            <p className="text-2xl font-semibold text-gray-900 mt-1">{stats.total_deliveries}</p>
          </div>
          <div className="p-4 bg-white shadow-sm border border-gray-200 rounded-xl">
            <span className="text-gray-600 text-sm">Average Rating</span>
            <p className="text-2xl font-semibold text-gray-900 mt-1">⭐ {stats.avg_rating.toFixed(1)}</p>
          </div>
          <div className="p-4 bg-white shadow-sm border border-gray-200 rounded-xl">
            <span className="text-gray-600 text-sm">Earnings</span>
            <p className="text-2xl font-semibold text-gray-900 mt-1">₹{stats.total_earnings}</p>
          </div>
          <div className="p-4 bg-white shadow-sm border border-gray-200 rounded-xl">
            <span className="text-gray-600 text-sm">Completed Orders</span>
            <p className="text-2xl font-semibold text-gray-900 mt-1">{stats.completed_orders}</p>
          </div>
          <div className="p-4 bg-white shadow-sm border border-gray-200 rounded-xl">
            <span className="text-gray-600 text-sm">Active Orders</span>
            <p className="text-2xl font-semibold text-gray-900 mt-1">{stats.active_orders}</p>
          </div>
          <div className="p-4 bg-white shadow-sm border border-gray-200 rounded-xl">
            <span className="text-gray-600 text-sm">Status</span>
            <p className="text-lg font-semibold text-gray-900 mt-1 capitalize">{stats.status}</p>
            <div className="mt-3 flex gap-2">
              <button
                className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                onClick={() => toggleStatus("online")}
                disabled={stats.status === "online"}
              >
                Go Online
              </button>
              <button
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                onClick={() => toggleStatus("offline")}
                disabled={stats.status === "offline"}
              >
                Go Offline
              </button>
            </div>
          </div>
        </div>
      )}

      <h2 className="text-2xl mt-8 font-semibold text-gray-800">📦 Active Orders</h2>
      {orders.length === 0 ? (
        <div className="p-8 bg-white shadow-sm border border-gray-200 rounded-xl text-center text-gray-500">
          No active orders at the moment
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((o) => (
            <div key={o.order_id} className="p-5 bg-white shadow-sm border border-gray-200 rounded-xl">
              <h3 className="text-xl font-bold text-gray-900">{o.restaurant_name}</h3>
              <div className="flex gap-4 mt-2 text-sm text-gray-600">
                <p>Status: <span className="font-medium text-gray-900 capitalize">{o.order_status}</span></p>
                <p>Total: <span className="font-medium text-gray-900">₹{o.total}</span></p>
              </div>
              <div className="mt-3 text-sm text-gray-600">
                <p><span className="font-medium text-gray-900">Address:</span> {o.delivery_address}</p>
                <p><span className="font-medium text-gray-900">Phone:</span> {o.delivery_phone}</p>
              </div>
              <div className="flex gap-4 mt-4 overflow-x-auto pb-2">
                {o.items.map((item) => (
                  <div key={item.menu_item_id} className="text-center flex-shrink-0">
                    <Image
                      src={item.image_url}
                      alt={item.name}
                      width={80}
                      height={80}
                      className="rounded-lg border border-gray-200"
                    />
                    <p className="text-sm text-gray-700 mt-2">{item.name} × {item.quantity}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}