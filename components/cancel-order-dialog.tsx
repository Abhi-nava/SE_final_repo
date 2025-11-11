"use client"

import { useState } from "react"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

interface CancelOrderDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  orderId: string
  orderNumber?: string
  onConfirm: () => Promise<void>
  isLoading?: boolean
}

export function CancelOrderDialog({
  open,
  onOpenChange,
  orderId,
  orderNumber,
  onConfirm,
  isLoading = false,
}: CancelOrderDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleConfirm = async () => {
    try {
      setIsSubmitting(true)
      await onConfirm()
      setIsSubmitting(false)
      onOpenChange(false)
    } catch (error) {
      setIsSubmitting(false)
      // Error is handled by the parent component
    }
  }

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Cancel Order</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to cancel this order?
          </AlertDialogDescription>
          {orderNumber && (
            <div className="mt-2 font-semibold text-foreground text-sm">
              Order ID: {orderNumber}
            </div>
          )}
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isSubmitting || isLoading}>
            Go Back
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={handleConfirm}
            disabled={isSubmitting || isLoading}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            {isSubmitting || isLoading ? "Cancelling..." : "Cancel Order"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
