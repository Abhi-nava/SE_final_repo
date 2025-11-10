// "use client"

// import { useState, useEffect } from "react"
// import { restaurantsAPI } from "@/lib/api"
// import { Card } from "@/components/ui/card"
// import { Button } from "@/components/ui/button"
// import { useToast } from "@/hooks/use-toast"
// import { Edit2, Trash2, Plus, Eye, EyeOff } from "lucide-react"
// import Link from "next/link"

// interface MenuItem {
//   id: string
//   name: string
//   price: number
//   category: string
//   description: string
//   availability: string
//   is_vegetarian: boolean
//   preparation_time: number
// }

// export default function MenuManagementPage() {
//   const [items, setItems] = useState<MenuItem[]>([])
//   const [isLoading, setIsLoading] = useState(true)
//   const { toast } = useToast()

//   useEffect(() => {
//     loadMenuItems()
//   }, [])

//   const loadMenuItems = async () => {
//     try {
//       setIsLoading(true)
//       const data = await restaurantsAPI.getMenuItems()
//       setItems(data)
//     } catch (error: any) {
//       toast({
//         title: "Error",
//         description: error.message,
//         variant: "destructive",
//       })
//     } finally {
//       setIsLoading(false)
//     }
//   }

//   const handleToggleAvailability = async (itemId: string, currentStatus: string) => {
//     try {
//       const newStatus = currentStatus === "available" ? "out_of_stock" : "available"
//       await restaurantsAPI.updateMenuItem(itemId, { availability: newStatus })
//       toast({
//         title: "Success",
//         description: "Item availability updated",
//       })
//       loadMenuItems()
//     } catch (error: any) {
//       toast({
//         title: "Error",
//         description: error.message,
//         variant: "destructive",
//       })
//     }
//   }

//   const handleDeleteItem = async (itemId: string) => {
//     if (!window.confirm("Are you sure you want to delete this item?")) return

//     try {
//       await restaurantsAPI.deleteMenuItem(itemId)
//       toast({
//         title: "Success",
//         description: "Menu item deleted",
//       })
//       loadMenuItems()
//     } catch (error: any) {
//       toast({
//         title: "Error",
//         description: error.message,
//         variant: "destructive",
//       })
//     }
//   }

//   if (isLoading) {
//     return (
//       <div className="flex items-center justify-center min-h-screen">
//         <div className="text-center">
//           <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin mx-auto mb-4"></div>
//           <p>Loading menu items...</p>
//         </div>
//       </div>
//     )
//   }

//   return (
//     <div>
//       <div className="flex justify-between items-center mb-8">
//         <h1 className="text-4xl font-bold">Menu Management</h1>
//         <Link href="/restaurant/menu/add-item">
//           <Button className="bg-primary text-white gap-2">
//             <Plus className="w-4 h-4" />
//             Add Item
//           </Button>
//         </Link>
//       </div>

//       {items.length === 0 ? (
//         <Card className="p-12 text-center">
//           <p className="text-lg dark mb-4">No menu items added yet.</p>
//           <Link href="/restaurant/menu/add-item">
//             <Button className="bg-primary text-white">Add Your First Item</Button>
//           </Link>
//         </Card>
//       ) : (
//         <div className="space-y-4">
//           {items.map((item) => (
//             <Card key={item.id} className="p-6">
//               <div className="flex justify-between items-start gap-4">
//                 <div className="flex-1">
//                   <div className="flex items-center gap-2 mb-2">
//                     <h3 className="text-lg font-bold">{item.name}</h3>
//                     {item.is_vegetarian && (
//                       <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Vegetarian</span>
//                     )}
//                   </div>
//                   <p className="dark text-sm mb-3">{item.description}</p>
//                   <div className="grid grid-cols-4 gap-4 text-sm">
//                     <div>
//                       <p className="dark">Category</p>
//                       <p className="font-semibold">{item.category}</p>
//                     </div>
//                     <div>
//                       <p className="dark">Price</p>
//                       <p className="font-semibold">₹{item.price}</p>
//                     </div>
//                     <div>
//                       <p className="dark">Prep Time</p>
//                       <p className="font-semibold">{item.preparation_time} min</p>
//                     </div>
//                     <div>
//                       <p className="dark">Status</p>
//                       <p
//                         className={`font-semibold ${item.availability === "available" ? "text-green-600" : "text-red-600"}`}
//                       >
//                         {item.availability === "available" ? "Available" : "Out of Stock"}
//                       </p>
//                     </div>
//                   </div>
//                 </div>

//                 <div className="flex gap-2">
//                   <Button
//                     size="sm"
//                     variant="outline"
//                     onClick={() => handleToggleAvailability(item.id, item.availability)}
//                     className="gap-2"
//                   >
//                     {item.availability === "available" ? (
//                       <>
//                         <EyeOff className="w-4 h-4" />
//                         Mark Unavailable
//                       </>
//                     ) : (
//                       <>
//                         <Eye className="w-4 h-4" />
//                         Mark Available
//                       </>
//                     )}
//                   </Button>
//                   <Link href={`/restaurant/menu/edit/${item.id}`}>
//                     <Button size="sm" variant="outline" className="gap-2 bg-transparent">
//                       <Edit2 className="w-4 h-4" />
//                       Edit
//                     </Button>
//                   </Link>
//                   <Button
//                     size="sm"
//                     variant="outline"
//                     onClick={() => handleDeleteItem(item.id)}
//                     className="gap-2 text-error hover:text-error"
//                   >
//                     <Trash2 className="w-4 h-4" />
//                     Delete
//                   </Button>
//                 </div>
//               </div>
//             </Card>
//           ))}
//         </div>
//       )}
//     </div>
//   )
// }


"use client"

import { useState, useEffect } from "react"
import { restaurantsAPI } from "@/lib/api"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import Link from "next/link"
import { Edit2, Trash2, Eye, EyeOff } from "lucide-react"

import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"



export default function MenuManagementPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()
  const [showDeleteModal, setShowDeleteModal] = useState(false)
const [selectedItem, setSelectedItem] = useState<any>(null)

const confirmDelete = (item: any) => {
  setSelectedItem(item)
  setShowDeleteModal(true)
}

const handleConfirmDelete = async () => {
  try {
    await restaurantsAPI.deleteMenuItem(selectedItem.id)
    toast({ title: "Deleted", description: `${selectedItem.name} has been removed.` })
    loadMenu()
  } catch (e: any) {
    toast({ title: "Error", description: e.message, variant: "destructive" })
  } finally {
    
    setShowDeleteModal(false)
    setSelectedItem(null)
  }
}

  useEffect(() => {
    loadMenu()
  }, [])

  const loadMenu = async () => {
    try {
      const data = await restaurantsAPI.getMenuItems()
      setItems(data)
    } catch (e:any) {
      toast({ title: "Error", description: e.message, variant: "destructive" })
    } finally {
      setLoading(false)
    }
  }

  const toggleAvailability = async (id:string, status:string) => {
    const newStatus = status === "available" ? "out_of_stock" : "available"
    try {
      await restaurantsAPI.updateMenuItem(id, { availability: newStatus })
      loadMenu()
    } catch (e:any) {
      toast({ title: "Error", description: e.message, variant: "destructive" })
    }
  }

  const deleteItem = async (id:string) => {
    if (!confirm("Delete this item?")) return
    try {
      await restaurantsAPI.deleteMenuItem(id)
      loadMenu()
    } catch (e:any) {
      toast({ title: "Error", description: e.message, variant: "destructive" })
    }
  }

  if (loading) return <div className="p-8 text-center">Loading menu…</div>

  return (
    <div>
      <div className="flex justify-between mb-8">
        <h1 className="text-4xl font-bold">Menu Management</h1>
        <Link href="/restaurant/menu/add-item">
          <Button className="bg-primary text-white">Add Item</Button>
        </Link>
      </div>
      <div className="space-y-4">
  {items.map((item: any) => (
    <Card key={item.id} className="p-6">
      <div className="flex justify-between items-start gap-4">

        {/* Left section — Image + Info */}
        <div className="flex gap-4 items-start">
          {/* Menu Image */}
          {item.image_url ? (
            <img
              src={item.image_url}
              alt={item.name}
              className="w-24 h-24 object-cover rounded-lg border shadow-sm hover:scale-105 transition-transform"
            />
          ) : (
            <div className="w-24 h-24 bg-gray-200 rounded-lg flex items-center justify-center text-sm text-gray-500">
              No Image
            </div>
          )}

          {/* Menu Details */}
          <div>
            <h3 className="text-xl font-bold">{item.name}</h3>
            <p className="dark text-sm">{item.description}</p>
            <p className="mt-2 font-semibold">₹{item.price}</p>
            <p className="mt-1 text-sm dark">
              Daily count: <span className="font-semibold">{item.daily_count ?? 0}</span>
            </p>
          </div>
        </div>

        {/* Right section — Buttons */}
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => toggleAvailability(item.id, item.availability)}>
            {item.availability === "available" ? <EyeOff /> : <Eye />}
          </Button>

          <Link href={`/restaurant/menu/edit/${item.id}`}>
            <Button variant="outline"><Edit2 /></Button>
          </Link>

          <Button variant="destructive" onClick={() => confirmDelete(item)}>
            <Trash2 />
          </Button>
        </div>
      </div>
    </Card>
  ))}
</div>


    </div>
  )
}

