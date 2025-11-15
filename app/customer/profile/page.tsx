"use client"

import type React from "react"

import { useState } from "react"
import { useAuth } from "@/lib/auth-context"
// import { customersAPI } from "@/lib/api"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/use-toast"

export default function CustomerProfilePage() {
  const { user, updateUser } = useAuth()
  const { toast } = useToast()
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [formData, setFormData] = useState({
    full_name: user?.full_name || "",
    phone: user?.phone || "",
    address: user?.address || "",
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSave = async () => {
    try {
      setIsSaving(true)
      await customersAPI.updateProfile(formData)

      if (user) {
        updateUser({
          ...user,
          full_name: formData.full_name,
          phone: formData.phone,
          address: formData.address,
        })
      }

      toast({
        title: "Success",
        description: "Profile updated successfully",
      })
      setIsEditing(false)
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div>
      <h1 className="text-4xl font-bold mb-8">My Profile</h1>

      <Card className="p-8 max-w-2xl">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">Email</label>
            <Input value={user?.email} disabled className="bg-bg-alt" />
            <p className="text-xs text-muted mt-1">Email cannot be changed</p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Full Name</label>
            <Input name="full_name" value={formData.full_name} onChange={handleInputChange} disabled={!isEditing} />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Phone</label>
            <Input name="phone" value={formData.phone} onChange={handleInputChange} disabled={!isEditing} type="tel" />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Default Delivery Address</label>
            <Input
              name="address"
              value={formData.address}
              onChange={handleInputChange}
              disabled={!isEditing}
              placeholder="Your delivery address"
            />
          </div>

          <div className="flex gap-2 pt-4">
            {!isEditing ? (
              <Button onClick={() => setIsEditing(true)} className="bg-primary text-white">
                Edit Profile
              </Button>
            ) : (
              <>
                <Button onClick={handleSave} disabled={isSaving} className="bg-primary text-white">
                  {isSaving ? "Saving..." : "Save Changes"}
                </Button>
                <Button
                  onClick={() => {
                    setIsEditing(false)
                    setFormData({
                      full_name: user?.full_name || "",
                      phone: user?.phone || "",
                      address: user?.address || "",
                    })
                  }}
                  variant="outline"
                >
                  Cancel
                </Button>
              </>
            )}
          </div>
        </div>
      </Card>
    </div>
  )
}
