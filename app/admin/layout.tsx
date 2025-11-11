import type React from "react"
import type { Metadata } from "next"
import { AdminNavbar } from "@/components/admin-navbar"

export const metadata: Metadata = {
  title: "Admin Dashboard | Food Delivery",
  description: "Platform analytics and management",
}

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-background">
      <AdminNavbar />
      {children}
    </div>
  )
}
