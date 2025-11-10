// "use client"

// import { useEffect, useState } from "react"
// import { useRouter, useParams } from "next/navigation"
// import { restaurantsAPI } from "@/lib/api"
// import { Input } from "@/components/ui/input"
// import { Button } from "@/components/ui/button"
// import { useToast } from "@/hooks/use-toast"

// export default function EditMenuItemPage() {
//   const { id } = useParams()
//   const { toast } = useToast()
//   const router = useRouter()
//   const [item, setItem] = useState<any>(null)
//   const [loading, setLoading] = useState(true)

//   useEffect(() => {
//     loadItem()
//   }, [])

//   const loadItem = async () => {
//     try {
//       const data = await restaurantsAPI.getMenuItemById(id as string)
//       setItem(data)
//     } catch (e: any) {
//       toast({ title: "Error", description: e.message, variant: "destructive" })
//     } finally {
//       setLoading(false)
//     }
//   }

//   const handleSave = async () => {
//     try {
//       await restaurantsAPI.updateMenuItem(id as string, item)
//       toast({ title: "Success", description: "Menu item updated!" })
//       router.push("/restaurant/menu")
//     } catch (e: any) {
//       toast({ title: "Error", description: e.message, variant: "destructive" })
//     }
//   }

//   if (loading) return <div className="p-8 text-center">Loading...</div>
//   if (!item) return <div className="p-8 text-center text-red-500">Item not found</div>

//   return (
//     <div className="max-w-2xl mx-auto space-y-6">
//       <h1 className="text-3xl font-bold">Edit Menu Item</h1>

//       <div className="space-y-4">
//         <Input value={item.name} onChange={(e) => setItem({ ...item, name: e.target.value })} placeholder="Name" />
//         <Input value={item.description} onChange={(e) => setItem({ ...item, description: e.target.value })} placeholder="Description" />
//         <Input value={item.price} type="number" onChange={(e) => setItem({ ...item, price: Number(e.target.value) })} placeholder="Price" />
//         <label className="block text-sm text-muted">Daily Count</label>
//         <input
//             type="number"
//             value={item.daily_count ?? 0}
//             onChange={(e) => setItem({ ...item, daily_count: Number(e.target.value) })}
//             className="mt-1 w-full rounded border px-2 py-1"
//         />
//       </div>

//       <Button className="bg-primary text-white" onClick={handleSave}>Save Changes</Button>
//     </div>
//   )
// }


"use client"

import { useEffect, useState } from "react"
import { useRouter, useParams } from "next/navigation"
import { restaurantsAPI } from "@/lib/api"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"

export default function EditMenuItemPage() {
  const { id } = useParams()
  const { toast } = useToast()
  const router = useRouter()
  const [item, setItem] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [preview, setPreview] = useState<string | null>(null)

  useEffect(() => {
    loadItem()
  }, [])

  const loadItem = async () => {
    try {
      const data = await restaurantsAPI.getMenuItemById(id as string)
      setItem(data)
      setPreview(data.image_url || null)
    } catch (e: any) {
      toast({ title: "Error", description: e.message, variant: "destructive" })
    } finally {
      setLoading(false)
    }
  }

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
        setItem({ ...item, image_url: reader.result as string })
      }
      reader.readAsDataURL(file)
    }
  }

  const handleImageUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setItem({ ...item, image_url: e.target.value })
    setPreview(e.target.value)
  }

  const handleSave = async () => {
    try {
      await restaurantsAPI.updateMenuItem(id as string, item)
      toast({ title: "Success", description: "Menu item updated!" })
      router.push("/restaurant/menu")
    } catch (e: any) {
      toast({ title: "Error", description: e.message, variant: "destructive" })
    }
  }

  if (loading) return <div className="p-8 text-center">Loading...</div>
  if (!item) return <div className="p-8 text-center text-red-500">Item not found</div>

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">Edit Menu Item</h1>

      <div className="space-y-4">
        <Input
          value={item.name}
          onChange={(e) => setItem({ ...item, name: e.target.value })}
          placeholder="Name"
        />
        <Input
          value={item.description}
          onChange={(e) => setItem({ ...item, description: e.target.value })}
          placeholder="Description"
        />
        <Input
          value={item.price}
          type="number"
          onChange={(e) => setItem({ ...item, price: Number(e.target.value) })}
          placeholder="Price"
        />

        <label className="block text-sm text-muted">Daily Count</label>
        <input
          type="number"
          value={item.daily_count ?? 0}
          onChange={(e) =>
            setItem({ ...item, daily_count: Number(e.target.value) })
          }
          className="mt-1 w-full rounded border px-2 py-1"
        />

        {/* Image Upload + Preview */}
        <div className="mt-4 space-y-2">
          <label className="block text-sm font-medium text-muted-foreground">
            Menu Item Image
          </label>

          {preview ? (
            <img
              src={preview}
              alt="Preview"
              className="w-32 h-32 rounded-lg object-cover border shadow-sm"
            />
          ) : (
            <div className="w-32 h-32 rounded-lg bg-gray-200 flex items-center justify-center text-gray-500 text-sm">
              No Image
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-2 mt-2">
            <Input
              placeholder="Paste image URL"
              value={item.image_url || ""}
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
      </div>

      <Button className="bg-primary text-white" onClick={handleSave}>
        Save Changes
      </Button>
    </div>
  )
}
