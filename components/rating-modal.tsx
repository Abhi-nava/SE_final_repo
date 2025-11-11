"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Star } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface RatingModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  orderId: string
  restaurantId: string
  deliveryAgentId?: string
  onSubmit?: () => void
}

interface RatingFormData {
  restaurant_rating: number | null
  delivery_rating: number | null
  delivery_speed: number | null
  food_quality: number | null
  packaging_quality: number | null
}

interface StarRatingProps {
  category: keyof RatingFormData
  value: number | null
  onChange: (category: keyof RatingFormData, rating: number) => void
}

function StarRating({ category, value, onChange }: StarRatingProps) {
  return (
    <div className="flex gap-2">
      {[1, 2, 3, 4, 5].map((star) => {
        const isFilled = value !== null && star <= value
        return (
          <button
            key={`${category}-${star}`}
            onClick={() => {
              console.log(`Clicked star ${star} for ${category}`)
              onChange(category, star)
            }}
            className="transition-transform hover:scale-110 focus:outline-none p-0"
            type="button"
            aria-label={`Rate ${star} stars`}
          >
            <Star
              className={`w-6 h-6 cursor-pointer ${
                isFilled ? "fill-yellow-400 text-yellow-400" : "text-gray-300 hover:text-yellow-300"
              }`}
              strokeWidth={1.5}
            />
          </button>
        )
      })}
      {value !== null && <span className="ml-2 text-sm font-semibold text-gray-600">{value}/5</span>}
    </div>
  )
}

export function RatingModal({
  open,
  onOpenChange,
  orderId,
  restaurantId,
  deliveryAgentId,
  onSubmit,
}: RatingModalProps) {
  const { toast } = useToast()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [ratings, setRatings] = useState<RatingFormData>({
    restaurant_rating: null,
    delivery_rating: null,
    delivery_speed: null,
    food_quality: null,
    packaging_quality: null,
  })

  const categories = [
    { key: "restaurant_rating" as const, label: "Restaurant Rating", description: "Rate the restaurant overall" },
    { key: "delivery_rating" as const, label: "Delivery Rating", description: "Rate the delivery service" },
    { key: "delivery_speed" as const, label: "Delivery Speed", description: "How fast was the delivery?" },
    { key: "food_quality" as const, label: "Food Quality", description: "How was the food quality?" },
    { key: "packaging_quality" as const, label: "Packaging Quality", description: "How was the packaging?" },
  ]

  const handleStarClick = (category: keyof RatingFormData, rating: number) => {
    console.log(`Setting ${category} to rating ${rating}`)
    setRatings((prev) => {
      const updated = {
        ...prev,
        [category]: rating,
      }
      console.log("Updated ratings state:", updated)
      return updated
    })
  }

  const allRatingsSelected = Object.values(ratings).every((rating) => rating !== null)

  const handleSubmit = async () => {
    if (!allRatingsSelected) {
      toast({
        title: "Error",
        description: "Please rate all categories before submitting",
        variant: "destructive",
      })
      return
    }

    setIsSubmitting(true)
    try {
      const token = localStorage.getItem("access_token")
      if (!token) {
        throw new Error("Not authenticated")
      }

      const payloadData = {
        order_id: orderId,
        restaurant_id: restaurantId,
        delivery_agent_id: deliveryAgentId || null,
        restaurant_rating: ratings.restaurant_rating,
        delivery_rating: ratings.delivery_rating,
        delivery_speed: ratings.delivery_speed,
        food_quality: ratings.food_quality,
        packaging_quality: ratings.packaging_quality,
        created_at: new Date().toISOString(),
      }

      console.log("Submitting rating payload:", payloadData)

      const response = await fetch("http://localhost:8000/api/ratings/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payloadData),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Failed to submit rating")
      }

      const result = await response.json()
      console.log("Rating submission successful:", result)

      toast({
        title: "Success",
        description: "Your rating has been submitted successfully!",
      })

      onOpenChange(false)
      setRatings({
        restaurant_rating: null,
        delivery_rating: null,
        delivery_speed: null,
        food_quality: null,
        packaging_quality: null,
      })

      if (onSubmit) {
        onSubmit()
      }
    } catch (error: any) {
      console.error("Rating submission error:", error)
      toast({
        title: "Error",
        description: error.message || "Failed to submit rating",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Rate This Order</DialogTitle>
          <DialogDescription>Please rate your experience across these categories</DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {categories.map((category) => (
            <div key={category.key} className="space-y-2">
              <div>
                <p className="font-semibold text-sm">{category.label}</p>
                <p className="text-xs text-gray-500 dark">{category.description}</p>
              </div>
              <StarRating category={category.key} value={ratings[category.key]} onChange={handleStarClick} />
            </div>
          ))}
        </div>

        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting || !allRatingsSelected}>
            {isSubmitting ? "Submitting..." : "Submit Rating"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
