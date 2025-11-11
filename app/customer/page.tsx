"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

interface Restaurant {
  id: string
  name: string
  description: string
  city: string
  address: string
  cuisine_types: string[]
  rating: number
  total_ratings: number
  image_url?: string
}

export default function CustomerPage() {
  const router = useRouter()
  const [restaurants, setRestaurants] = useState<Restaurant[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchRestaurants = async () => {
      try {
        console.log("[v0] Fetching restaurants...")

        const res = await fetch("http://localhost:8000/api/customers/restaurants", {
          headers: {
            "Content-Type": "application/json",
          },
        })

        if (!res.ok) {
          throw new Error(`Failed to fetch restaurants (${res.status})`)
        }

        const data = await res.json()

        // ✅ Ensure id is properly mapped from _id
        const mappedData = data.map((r: any) => ({
          id: r.id || r._id, // use either id or _id
          name: r.name,
          description: r.description,
          city: r.city,
          address: r.address,
          cuisine_types: r.cuisine_types || [],
          rating: r.rating || 0,
          total_ratings: r.total_ratings || 0,
          image_url: r.image_url || "",
        }))

        console.log("[v0] Restaurants fetched:", mappedData)
        setRestaurants(mappedData)
      } catch (err: any) {
        console.error("[v0] Error fetching restaurants:", err)
        setError(err.message || "Something went wrong")
      } finally {
        setLoading(false)
      }
    }

    fetchRestaurants()
  }, [])

  const handleClick = (id: string) => {
    console.log(`[v0] Navigating to /customer/restaurant/${id}`)
    if (id) router.push(`/customer/restaurant/${id}`)
    else console.error("[v0] Missing restaurant id!")
    console.log("[v0] Navigation complete.")
  }

  if (loading) return <p className="text-center mt-10">Loading restaurants...</p>
  if (error) return <p className="text-center text-red-500 mt-10">{error}</p>

  return (
    <main className="p-8">
      <h1 className="text-3xl font-bold mb-6 text-center">Available Restaurants</h1>

      {restaurants.length === 0 ? (
        <p className="text-center text-gray-500">No restaurants found.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {restaurants.map((r) => (
            <div
              key={r.id}
              onClick={() => handleClick(r.id)}
              className="border rounded-xl p-4 shadow hover:shadow-xl hover:scale-[1.02] transition-all duration-200 bg-white cursor-pointer"
            >
              <img
                src={
                  r.image_url
                    ? r.image_url.startsWith("data:image")
                      ? r.image_url
                      : r.image_url.startsWith("http")
                      ? r.image_url
                      : `data:image/jpeg;base64,${r.image_url}`
                    : "https://via.placeholder.com/300x200?text=Restaurant"
                }
                alt={r.name}
                className="w-full h-48 object-cover rounded-md mb-4"
              />
              <h2 className="text-xl font-semibold">{r.name}</h2>
              <p className="text-gray-600 mb-2">{r.description}</p>
              <p className="text-sm text-gray-500">📍 {r.address}, {r.city}</p>
              <p className="mt-2 text-yellow-500 font-medium">
                ⭐ {r.rating.toFixed(1)} ({r.total_ratings} reviews)
              </p>
              <p className="mt-1 text-sm text-gray-700">
                🍽️ {r.cuisine_types.join(", ")}
              </p>
            </div>
          ))}
        </div>
      )}
    </main>
  )
}
