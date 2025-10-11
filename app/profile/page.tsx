"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useUser } from "@/contexts/user-context"
import { SkinProfileForm } from "@/components/skin-profile-form"
import { FaceScanPrompt } from "@/components/face-scan-prompt"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Loader2, User, Settings } from "lucide-react"

export default function ProfilePage() {
  const { user, skinProfile, isLoading } = useUser()
  const router = useRouter()
  const [showFaceScanPrompt, setShowFaceScanPrompt] = useState(false)

  useEffect(() => {
    if (!user) {
      router.push("/login")
      return
    }
    // Skin profile loading is handled by the user context automatically
  }, [user, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center gap-2">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span>Loading profile...</span>
        </div>
      </div>
    )
  }

  if (!user) {
    return null // Will redirect to login
  }

  const handleProfileComplete = () => {
    console.log('🎯 [PROFILE PAGE] Profile completed, showing face scan prompt...')
    // Show face scan prompt after profile completion
    setShowFaceScanPrompt(true)
  }

  const handleFaceScanAccept = () => {
    // Navigate to face scan page
    router.push("/scan")
  }

  const handleFaceScanDecline = () => {
    // Navigate to dashboard without face scan
    router.push("/dashboard")
  }

  // Show face scan prompt if profile is complete and user chose to see it
  if (showFaceScanPrompt) {
    return (
      <FaceScanPrompt 
        onAccept={handleFaceScanAccept}
        onDecline={handleFaceScanDecline}
      />
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">Profile Setup</h1>
            <p className="text-muted-foreground">
              Complete your skin profile to get personalized recommendations
            </p>
          </div>

          {/* User Info Card */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5" />
                Account Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Email</label>
                  <p className="text-foreground">{user.email}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Username</label>
                  <p className="text-foreground">{user.username || "Not set"}</p>
                </div>
              </div>
              <div className="mt-4">
                <Button variant="outline" size="sm">
                  <Settings className="w-4 h-4 mr-2" />
                  Edit Account Settings
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Skin Profile Form */}
          <SkinProfileForm onComplete={handleProfileComplete} />
        </div>
      </div>
    </div>
  )
}
