"use client"

import { useState } from "react"
import { Bell, X, CheckCircle, Clock, AlertCircle } from "lucide-react"
import useSWR from "swr"

interface Notification {
  _id: string
  type: string
  title: string
  message: string
  is_read: boolean
  created_at: string
}

const fetcher = (url: string) => fetch(url).then((r) => r.json())

export function NotificationsPanel() {
  const [isOpen, setIsOpen] = useState(false)
  const { data: notifications = [], mutate } = useSWR("/api/notifications", fetcher, { refreshInterval: 5000 })

  const unreadCount = notifications.filter((n: Notification) => !n.is_read).length

  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await fetch(`/api/notifications/${notificationId}/read`, { method: "POST" })
      mutate()
    } catch (error) {
      console.error("Error marking notification as read:", error)
    }
  }

  const getNotificationIcon = (type: string) => {
    if (type.includes("delivered")) return <CheckCircle className="w-5 h-5 text-green-500" />
    if (type.includes("transit")) return <Clock className="w-5 h-5 text-blue-500" />
    return <AlertCircle className="w-5 h-5 text-orange-500" />
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 hover:bg-secondary rounded-lg transition-colors"
      >
        <Bell className="w-6 h-6" />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-background border border-border rounded-lg shadow-lg z-50">
          <div className="flex justify-between items-center p-4 border-b border-border">
            <h3 className="font-bold">Notifications</h3>
            <button onClick={() => setIsOpen(false)}>
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-8 text-center dark">
                <p>No notifications yet</p>
              </div>
            ) : (
              <div className="divide-y divide-border">
                {notifications.map((notification: Notification) => (
                  <div
                    key={notification._id}
                    className={`p-4 hover:bg-secondary/50 cursor-pointer transition-colors ${
                      !notification.is_read ? "bg-primary/5" : ""
                    }`}
                    onClick={() => handleMarkAsRead(notification._id)}
                  >
                    <div className="flex gap-3">
                      <div className="mt-1">{getNotificationIcon(notification.type)}</div>
                      <div className="flex-1">
                        <p className="font-semibold text-sm">{notification.title}</p>
                        <p className="text-xs dark">{notification.message}</p>
                        <p className="text-xs dark mt-1">{new Date(notification.created_at).toLocaleString()}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
