"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Camera, User } from "lucide-react"

interface FaceScanAvatarProps {
  src?: string
  alt?: string
  size?: "sm" | "md" | "lg"
  className?: string
  isScanning?: boolean
  scanProgress?: number
  analysisResults?: any
  onScanComplete?: () => void
}

export function FaceScanAvatar({ 
  src, 
  alt = "Face scan avatar", 
  size = "md",
  className = ""
}: FaceScanAvatarProps) {
  const sizeClasses = {
    sm: "w-8 h-8",
    md: "w-12 h-12", 
    lg: "w-16 h-16"
  }

  return (
    <Avatar className={`${sizeClasses[size]} ${className}`}>
      <AvatarImage src={src} alt={alt} />
      <AvatarFallback className="bg-green-100 text-green-600">
        {src ? <Camera className="w-4 h-4" /> : <User className="w-4 h-4" />}
      </AvatarFallback>
    </Avatar>
  )
}
