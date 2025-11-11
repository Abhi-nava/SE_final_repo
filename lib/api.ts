// const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// export async function apiFetch(endpoint: string, options: RequestInit = {}) {
//   const token = localStorage.getItem("access_token")

//   const headers: HeadersInit = {
//     "Content-Type": "application/json",
//     ...options.headers,
//   }

//   if (token) {
//     headers.Authorization = `Bearer ${token}`
//   }

//   const response = await fetch(`${API_BASE_URL}${endpoint}`, {
//     ...options,
//     headers,
//   })

//   if (response.status === 401) {
//     localStorage.removeItem("access_token")
//     localStorage.removeItem("refresh_token")
//     window.location.href = "/"
//   }

//   if (!response.ok) {
//     const error = await response.json()
//     throw new Error(error.detail || "API request failed")
//   }

//   return response.json()
// }

// // Customers API
// export const customersAPI = {
//   listRestaurants: (city?: string, cuisine?: string) =>
//     apiFetch(`/api/customers/restaurants?${new URLSearchParams({ ...(city && { city }), ...(cuisine && { cuisine }) })}`),
//   getRestaurant: (id: string) => apiFetch(`/api/customers/restaurants/${id}`),
//   updateProfile: (data: any) => apiFetch("/api/customers/profile", { method: "PUT", body: JSON.stringify(data) }),
// }



// export const ordersAPI = {

//   // Existing restaurant orders list
//   getRestaurantOrders: () => getJSON(`/api/orders/restaurant`),

//   // NEW: Get details for a specific order (restaurant view)
//   getRestaurantOrderDetails: (orderId: string) =>
//     getJSON(`/api/orders/restaurant/${orderId}`),

//   // Status updates (already used by your UI)
//   updateOrderStatus: (orderId: string, status: string) =>
//     putJSON(`/api/orders/${orderId}/status`, { status }),

//   // NEW: List verified delivery agents
//   listAgents: () =>
//     getJSON(`/api/orders/restaurant/agents`),

//   // NEW: Assign a delivery agent to an order
//   assignAgent: (orderId: string, agentId: string) =>
//     postJSON(`/api/orders/${orderId}/assign-agent`, {
//       delivery_agent_id: agentId,
//     }),

//   // NEW: Ratings summary for dashboard
//   getRatingsSummary: () =>
//     getJSON(`/api/restaurants/stats/rating-summary`),

//   // CUSTOMER SIDE (you already use this)
//   getMyOrders: () => getJSON(`/api/orders/my-orders`),

//   // CUSTOMER order details
//   getOrderById: (orderId: string) =>
//     getJSON(`/api/orders/${orderId}`),

  
// }





// export const restaurantsAPI = {
//   getMyRestaurant: () => getJSON(`/api/restaurants/my-restaurant`),

//   getMenuItems: () => getJSON(`/api/restaurants/menu-items`),
//   addMenuItem: (data: any) => postJSON(`/api/restaurants/menu-items`, data),
//   updateMenuItem: (id: string, data: any) =>
//     putJSON(`/api/restaurants/menu-items/${id}`, data),
//   deleteMenuItem: (id: string) => del(`/api/restaurants/menu-items/${id}`),


//   getDashboardSummary: async () => {
//     const response = await fetch(`${API_BASE_URL}/restaurants/stats/dashboard-summary`, {
//       headers: getAuthHeaders(),
//     })
//     if (!response.ok) {
//       const error = await response.json()
//       throw new Error(error.detail || 'Failed to fetch dashboard summary')
//     }
//     return response.json()
//   },

//   getRatingSummary: async () => {
//     const response = await fetch(`${API_BASE_URL}/restaurants/stats/rating-summary`, {
//       headers: getAuthHeaders(),
//     })
//     if (!response.ok) {
//       const error = await response.json()
//       throw new Error(error.detail || 'Failed to fetch rating summary')
//     }
//     return response.json()
//   },
// }





// export const deliveryAPI = {
//   getAvailableOrders: () =>
//     getJSON(`/api/delivery/available-orders`),

//   acceptOrder: (orderId: string) =>
//     postJSON(`/api/delivery/${orderId}/accept`, {}),

//   updateStatus: (orderId: string, status: string) =>
//     putJSON(`/api/delivery/${orderId}/status?status=${status}`),

//   getMyDeliveries: () =>
//     getJSON(`/api/delivery/my-deliveries`),
// }

// function getToken() {
//   return localStorage.getItem("access_token")
// }


// const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// async function fetchJSON(path: string, options: RequestInit = {}) {
//   const token = getToken()

//   const res = await fetch(`${API_BASE}${path}`, {
//     ...options,
//     headers: {
//       "Content-Type": "application/json",
//       Authorization: token ? `Bearer ${token}` : "",
//       ...(options.headers || {})
//     },
//   })

//   if (!res.ok) {
//     const err = await res.json().catch(() => ({ detail: "Error" }))
//     throw new Error(err.detail || "Request failed")
//   }

//   return res.json()
// }

// function getJSON(path: string) {
//   return fetchJSON(path, { method: "GET" })
// }

// function postJSON(path: string, body: any) {
//   return fetchJSON(path, {
//     method: "POST",
//     body: JSON.stringify(body),
//   })
// }

// function putJSON(path: string, body: any) {
//   return fetchJSON(path, {
//     method: "PUT",
//     body: JSON.stringify(body),
//   })
// }


// function del(path: string) {
//   return fetchJSON(path, { method: "DELETE" })
// }

// // Ratings API
// export const ratingsAPI = {
//   create: (data: any) => apiFetch("/ratings/create", { method: "POST", body: JSON.stringify(data) }),
//   getRestaurantRatings: (restaurantId: string) => apiFetch(`/ratings/restaurant/${restaurantId}`),
//   getAgentRatings: (agentId: string) => apiFetch(`/ratings/delivery-agent/${agentId}`),
// }

// // Admin API
// export const adminAPI = {
//   getAnalytics: async () => {
//     const response = await fetch(`${API_BASE_URL}/api/admin/analytics/overview`, {
//       headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
//     })
//     return response.json()
//   },

//   getRestaurants: async (skip = 0, limit = 20) => {
//     const response = await fetch(`${API_BASE_URL}/api/admin/restaurants?skip=${skip}&limit=${limit}`, {
//       headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
//     })
//     return response.json()
//   },

//   getDeliveryAgents: async (skip = 0, limit = 20) => {
//     const response = await fetch(`${API_BASE_URL}/api/admin/delivery-agents?skip=${skip}&limit=${limit}`, {
//       headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
//     })
//     return response.json()
//   },

//   getUsers: async (skip = 0, limit = 20) => {
//     const response = await fetch(`${API_BASE_URL}/api/admin/users?skip=${skip}&limit=${limit}`, {
//       headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
//     })
//     return response.json()
//   },

//   getOrders: async (skip = 0, limit = 20) => {
//     const response = await fetch(`${API_BASE_URL}/api/admin/orders?skip=${skip}&limit=${limit}`, {
//       headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
//     })
//     return response.json()
//   },

//   getDailyRevenue: async (days = 30) => {
//     const response = await fetch(`${API_BASE_URL}/api/admin/revenue/daily?days=${days}`, {
//       headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
//     })
//     return response.json()
//   },
// }


const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// Helper function to get auth headers
function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem("access_token")
  return {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  }
}

function getToken() {
  return localStorage.getItem("access_token")
}

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem("access_token")

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  })

  if (response.status === 401) {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    window.location.href = "/"
  }

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "API request failed")
  }

  return response.json()
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function fetchJSON(path: string, options: RequestInit = {}) {
  const token = getToken()

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: token ? `Bearer ${token}` : "",
      ...(options.headers || {})
    },
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Error" }))
    throw new Error(err.detail || "Request failed")
  }

  return res.json()
}

function getJSON(path: string) {
  return fetchJSON(path, { method: "GET" })
}

function postJSON(path: string, body: any) {
  return fetchJSON(path, {
    method: "POST",
    body: JSON.stringify(body),
  })
}

function putJSON(path: string, body: any) {
  return fetchJSON(path, {
    method: "PUT",
    body: JSON.stringify(body),
  })
}

function del(path: string) {
  return fetchJSON(path, { method: "DELETE" })
}

// Customers API
export const customersAPI = {
  listRestaurants: (city?: string, cuisine?: string) =>
    apiFetch(`/api/customers/restaurants?${new URLSearchParams({ ...(city && { city }), ...(cuisine && { cuisine }) })}`),
  getRestaurant: (id: string) => apiFetch(`/api/customers/restaurants/${id}`),
  updateProfile: (data: any) => apiFetch("/api/customers/profile", { method: "PUT", body: JSON.stringify(data) }),
}

// Orders API
export const ordersAPI = {
  // Existing restaurant orders list
  // getRestaurantOrders: () => getJSON(`/api/orders/restaurant`),

    getRestaurantOrders: () => getJSON("/api/orders/restaurant/orders"),

  // Get details for a specific order (restaurant view)
  getRestaurantOrderDetails: (orderId: string) =>
    getJSON(`/api/orders/restaurant/${orderId}`),

 getOrder: async (orderId: string) => {
  const res = await fetch(`${API_BASE}/api/orders/details/${orderId}`, {  // Changed path
    credentials: "include",
  })
  if (!res.ok) {
    const error = await res.json()
    throw new Error(error.detail || "Failed to fetch order")
  }
  return res.json()
},

  // Status updates
  // updateOrderStatus: (orderId: string, status: string) =>
  //   putJSON(`/api/orders/${orderId}/status`, { status }),
    updateOrderStatus: (id: string, order_status: string) =>
    putJSON(`/api/orders/restaurant/order/${id}/status`, { order_status }),
  // List verified delivery agents
  listAgents: () => getJSON(`/api/orders/restaurant/agents`),

  // Assign a delivery agent to an order
  assignAgent: (orderId: string, agentId: string) =>
    postJSON(`/api/orders/${orderId}/assign-agent`, {
      delivery_agent_id: agentId,
    }),

  // Ratings summary for dashboard
  getRatingsSummary: () => getJSON(`/api/restaurants/stats/rating-summary`),

  // CUSTOMER SIDE
  getMyOrders: () => getJSON(`/api/orders/my-orders`),

  // CUSTOMER order details
  getOrderById: (orderId: string) => getJSON(`/api/orders/${orderId}`),
}

// Restaurants API
export const restaurantsAPI = {
  getMyRestaurant: () => getJSON(`/api/restaurants/my-restaurant`),

  getMenuItems: () => getJSON(`/api/restaurants/menu-items`),
  
  addMenuItem: (data: any) => postJSON(`/api/restaurants/menu-items`, data),
  
  updateMenuItem: (id: string, data: any) =>
    putJSON(`/api/restaurants/menu-items/${id}`, data),
  
  deleteMenuItem: (id: string) => del(`/api/restaurants/menu-items/${id}`),

  // Dashboard summary - gets restaurant info, stats, and ratings in one call
  getDashboardSummary: () => getJSON(`/api/restaurants/stats/dashboard-summary`),

  // Separate ratings summary endpoint (if needed separately)
  getRatingSummary: () => getJSON(`/api/restaurants/stats/rating-summary`),

  getMenuItemById: (id: string) => getJSON(`/api/restaurants/menu-items/${id}`),
}

// Delivery API
// export const deliveryAPI = {
//   getAvailableOrders: () => getJSON(`/api/delivery/available-orders`),

//   acceptOrder: (orderId: string) => postJSON(`/api/delivery/${orderId}/accept`, {}),

//   updateStatus: (orderId: string, status: string) =>
//     putJSON(`/api/delivery/${orderId}/status?status=${status}`),

//   getMyDeliveries: () => getJSON(`/api/delivery/my-deliveries`),
// }

export const deliveryAPI = {
  // Existing methods
  getAvailableOrders: () => getJSON(`/api/delivery/available-orders`),
  acceptOrder: (orderId: string) => postJSON(`/api/delivery/${orderId}/accept`, {}),
  updateStatus: (orderId: string, status: string) =>
    putJSON(`/api/delivery/${orderId}/status?status=${status}`),
  getMyDeliveries: () => getJSON(`/api/delivery/my-deliveries`),

  // New dashboard methods
  getStats: (agentId: string) => getJSON(`/api/delivery/stats/${agentId}`),
  
  getAssignedOrders: (agentId: string) => getJSON(`/api/delivery/assigned_orders/${agentId}`),
  
  updateAgentStatus: (agentId: string, status: string) =>
    postJSON(`/api/delivery/update_status/${agentId}?status=${status}`, {}),
  
  updateLocation: (agentId: string, lat: number, lng: number) =>
    postJSON(`/api/delivery/update_location/${agentId}?lat=${lat}&lng=${lng}`, {}),
}

// Ratings API
export const ratingsAPI = {
  create: (data: any) => apiFetch("/api/ratings/create", { method: "POST", body: JSON.stringify(data) }),
  getRestaurantRatings: (restaurantId: string) => apiFetch(`/api/ratings/restaurant/${restaurantId}`),
  getAgentRatings: (agentId: string) => apiFetch(`/api/ratings/delivery-agent/${agentId}`),
  checkOrderRating: (orderId: string) => apiFetch(`/api/ratings/check/${orderId}`),
}

// Admin API
export const adminAPI = {
  getAnalytics: async () => {
    const response = await fetch(`${API_BASE_URL}/api/admin/analytics/overview`, {
      headers: getAuthHeaders(),
    })
    if (!response.ok) throw new Error("Failed to fetch analytics")
    return response.json()
  },

  getRestaurants: async (skip = 0, limit = 20) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/restaurants?skip=${skip}&limit=${limit}`, {
      headers: getAuthHeaders(),
    })
    if (!response.ok) throw new Error("Failed to fetch restaurants")
    return response.json()
  },

  getDeliveryAgents: async (skip = 0, limit = 20) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/delivery-agents?skip=${skip}&limit=${limit}`, {
      headers: getAuthHeaders(),
    })
    if (!response.ok) throw new Error("Failed to fetch delivery agents")
    return response.json()
  },

  getUsers: async (skip = 0, limit = 20) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/users?skip=${skip}&limit=${limit}`, {
      headers: getAuthHeaders(),
    })
    if (!response.ok) throw new Error("Failed to fetch users")
    return response.json()
  },

  getOrders: async (skip = 0, limit = 20) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/orders?skip=${skip}&limit=${limit}`, {
      headers: getAuthHeaders(),
    })
    if (!response.ok) throw new Error("Failed to fetch orders")
    return response.json()
  },

  getDailyRevenue: async (days = 30) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/revenue/daily?days=${days}`, {
      headers: getAuthHeaders(),
    })
    if (!response.ok) throw new Error("Failed to fetch revenue data")
    return response.json()
  },
}

// Coupons API
export const couponsAPI = {
  validateCoupon: (code: string, orderTotal: number) =>
    postJSON("/api/coupons/validate", { code, orderTotal }),
  
  getAvailableCoupons: () =>
    getJSON("/api/coupons/available"),
}