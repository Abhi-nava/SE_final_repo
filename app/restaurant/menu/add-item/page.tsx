// "use client"

// import { useState } from "react"
// import { useRouter } from "next/navigation"
// import { restaurantsAPI } from "@/lib/api"
// import { Button } from "@/components/ui/button"
// import { Input } from "@/components/ui/input"
// import { Textarea } from "@/components/ui/textarea"
// import { useToast } from "@/hooks/use-toast"

// export default function AddMenuItemPage() {
//   const router = useRouter()
//   const { toast } = useToast()

//   const [formData, setFormData] = useState({
//     name: "",
//     description: "",
//     price: "",
//     category: "",
//     image_url: "",
//     availability: "available",
//     is_vegetarian: false,
//     is_vegan: false,
//     preparation_time: 0,
//     daily_count: 0,
//   })

//   const [loading, setLoading] = useState(false)

//   const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
//     const { name, value, type, checked } = e.target
//     setFormData((prev) => ({
//       ...prev,
//       [name]: type === "checkbox" ? checked : value,
//     }))
//   }

//   const handleSubmit = async (e: React.FormEvent) => {
//     e.preventDefault()
//     try {
//       setLoading(true)
//       await restaurantsAPI.addMenuItem({
//         ...formData,
//         price: parseFloat(formData.price),
//         preparation_time: parseInt(formData.preparation_time.toString()),
//         daily_count: parseInt(formData.daily_count.toString()),
//       })
//       toast({ title: "Item added", description: "Menu item created successfully." })
//       router.push("/restaurant/menu")
//     } catch (e: any) {
//       toast({ title: "Error", description: e.message, variant: "destructive" })
//     } finally {
//       setLoading(false)
//     }
//   }

//   return (
//     <div className="max-w-3xl mx-auto p-8">
//       <h1 className="text-4xl font-bold mb-6">Add New Menu Item</h1>
//       <form onSubmit={handleSubmit} className="space-y-6">
//         <div>
//           <label className="block text-sm font-semibold mb-1">Name</label>
//           <Input name="name" value={formData.name} onChange={handleChange} required />
//         </div>

//         <div>
//           <label className="block text-sm font-semibold mb-1">Description</label>
//           <Textarea name="description" value={formData.description} onChange={handleChange} rows={3} />
//         </div>

//         <div className="grid grid-cols-2 gap-4">
//           <div>
//             <label className="block text-sm font-semibold mb-1">Category</label>
//             <Input name="category" value={formData.category} onChange={handleChange} required />
//           </div>
//           <div>
//             <label className="block text-sm font-semibold mb-1">Price (₹)</label>
//             <Input type="number" name="price" value={formData.price} onChange={handleChange} required />
//           </div>
//         </div>

//         <div className="grid grid-cols-2 gap-4">
//           <div>
//             <label className="block text-sm font-semibold mb-1">Preparation Time (mins)</label>
//             <Input type="number" name="preparation_time" value={formData.preparation_time} onChange={handleChange} />
//           </div>
//           <div>
//             <label className="block text-sm font-semibold mb-1">Daily Count</label>
//             <Input type="number" name="daily_count" value={formData.daily_count} onChange={handleChange} />
//           </div>
//         </div>

//         <div>
//           <label className="block text-sm font-semibold mb-1">Image URL</label>
//           <Input name="image_url" value={formData.image_url} onChange={handleChange} />
//         </div>

//         <div className="flex gap-4 mt-2">
//           <label className="flex items-center gap-2">
//             <input type="checkbox" name="is_vegetarian" checked={formData.is_vegetarian} onChange={handleChange} />
//             Vegetarian
//           </label>
//           <label className="flex items-center gap-2">
//             <input type="checkbox" name="is_vegan" checked={formData.is_vegan} onChange={handleChange} />
//             Vegan
//           </label>
//         </div>

//         <div className="flex justify-end gap-4 mt-6">
//           <Button type="button" variant="outline" onClick={() => router.push("/restaurant/menu")}>
//             Cancel
//           </Button>
//           <Button type="submit" disabled={loading} className="bg-primary text-white">
//             {loading ? "Adding..." : "Add Item"}
//           </Button>
//         </div>
//       </form>
//     </div>
//   )
// }


"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { restaurantsAPI } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"

export default function AddMenuItemPage() {
  const router = useRouter()
  const { toast } = useToast()

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    price: "",
    category: "",
    image_url: "",
    availability: "available",
    is_vegetarian: false,
    is_vegan: false,
    preparation_time: 0,
    daily_count: 0,
  })

  const [preview, setPreview] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }))
  }

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
        setFormData((prev) => ({ ...prev, image_url: reader.result as string }))
      }
      reader.readAsDataURL(file)
    }
  }

  const handleImageUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value
    setFormData((prev) => ({ ...prev, image_url: url }))
    setPreview(url)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setLoading(true)
      await restaurantsAPI.addMenuItem({
        ...formData,
        price: parseFloat(formData.price),
        preparation_time: parseInt(formData.preparation_time.toString()),
        daily_count: parseInt(formData.daily_count.toString()),
      })
      toast({ title: "Item added", description: "Menu item created successfully." })
      router.push("/restaurant/menu")
    } catch (e: any) {
      toast({ title: "Error", description: e.message, variant: "destructive" })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto p-8">
      <h1 className="text-4xl font-bold mb-6">Add New Menu Item</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Info */}
        <div>
          <label className="block text-sm font-semibold mb-1">Name</label>
          <Input name="name" value={formData.name} onChange={handleChange} required />
        </div>

        <div>
          <label className="block text-sm font-semibold mb-1">Description</label>
          <Textarea name="description" value={formData.description} onChange={handleChange} rows={3} />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold mb-1">Category</label>
            <Input name="category" value={formData.category} onChange={handleChange} required />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-1">Price (₹)</label>
            <Input type="number" name="price" value={formData.price} onChange={handleChange} required />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold mb-1">Preparation Time (mins)</label>
            <Input type="number" name="preparation_time" value={formData.preparation_time} onChange={handleChange} />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-1">Daily Count</label>
            <Input type="number" name="daily_count" value={formData.daily_count} onChange={handleChange} />
          </div>
        </div>

        {/* Image Upload Section */}
        <div className="space-y-2">
          <label className="block text-sm font-semibold mb-1">Menu Item Image</label>

          {preview ? (
            <img
              src={preview}
              alt="Preview"
              className="w-32 h-32 object-cover rounded-lg border shadow-sm"
            />
          ) : (
            <div className="w-32 h-32 bg-gray-200 rounded-lg flex items-center justify-center text-gray-500 text-sm">
              No Image
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-2 mt-2">
            <Input
              placeholder="Paste image URL"
              name="image_url"
              value={formData.image_url}
              onChange={handleImageUrlChange}
            />
            <div className="relative">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
              <Button type="button" variant="secondary">
                Upload
              </Button>
            </div>
          </div>
        </div>

        {/* Dietary Options */}
        <div className="flex gap-4 mt-2">
          <label className="flex items-center gap-2">
            <input type="checkbox" name="is_vegetarian" checked={formData.is_vegetarian} onChange={handleChange} />
            Vegetarian
          </label>
          <label className="flex items-center gap-2">
            <input type="checkbox" name="is_vegan" checked={formData.is_vegan} onChange={handleChange} />
            Vegan
          </label>
        </div>

        {/* Submit Buttons */}
        <div className="flex justify-end gap-4 mt-6">
          <Button type="button" variant="outline" onClick={() => router.push("/restaurant/menu")}>
            Cancel
          </Button>
          <Button type="submit" disabled={loading} className="bg-primary text-white">
            {loading ? "Adding..." : "Add Item"}
          </Button>
        </div>
      </form>
    </div>
  )
}
