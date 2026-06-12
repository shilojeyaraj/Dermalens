"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Separator } from "@/components/ui/separator"
import { 
  User, 
  LogOut, 
  Home, 
  Settings, 
  Camera, 
  Save, 
  Edit3, 
  Shield, 
  Bell,
  Palette,
  Database,
  AlertTriangle
} from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useUser } from "@/contexts/user-context-simple"

export default function SettingsPage() {
  const router = useRouter()
  const userContext = useUser()
  const { user } = userContext || {}
  const signOut = (userContext as any)?.signOut
  const updateProfile = (userContext as any)?.updateProfile
  const [isEditing, setIsEditing] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [profileData, setProfileData] = useState({
    username: "",
    email: "",
    firstName: "",
    lastName: "",
    bio: "",
    skinType: "",
    skinConcerns: "",
    allergies: "",
    routinePreference: ""
  })

  // Load user data and skin profile on mount
  useEffect(() => {
    const loadProfileData = async () => {
      if (user) {
        // Load basic user data
        setProfileData(prev => ({
          ...prev,
          username: (user as any).username || "",
          email: user.email || "",
          firstName: (user as any).first_name || "",
          lastName: (user as any).last_name || "",
          bio: (user as any).bio || "",
        }))

        // Load skin profile from API
        try {
          const token = localStorage.getItem('token')
          if (!token) return

          const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://dermalens-backend-941238576063.us-central1.run.app'
          const response = await fetch(`${apiUrl}/skin-profile`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          })

          if (response.ok) {
            const responseData = await response.json()
            console.log('✅ [SETTINGS] Loaded skin profile response:', responseData)
            
            // Handle both formats: direct data or {success, data} wrapper
            const skinProfile = responseData.data || responseData
            
            if (skinProfile) {
              console.log('✅ [SETTINGS] Parsed skin profile:', skinProfile)
              
              // Map skin profile data to form fields
              setProfileData(prev => ({
                ...prev,
                skinType: skinProfile.skin_type || "",
                skinConcerns: Array.isArray(skinProfile.primary_concerns) 
                  ? skinProfile.primary_concerns.join(", ") 
                  : (skinProfile.skin_concerns || ""),
                allergies: Array.isArray(skinProfile.allergies)
                  ? skinProfile.allergies.join(", ")
                  : (typeof skinProfile.allergies === 'string' ? skinProfile.allergies : ""),
                routinePreference: skinProfile.routine_frequency || skinProfile.routine_type || ""
              }))
            } else {
              console.log('ℹ️ [SETTINGS] No skin profile data in response')
            }
          } else if (response.status === 404) {
            console.log('ℹ️ [SETTINGS] No skin profile found yet')
          } else {
            console.error('❌ [SETTINGS] Failed to load skin profile:', response.statusText)
          }
        } catch (error) {
          console.error('❌ [SETTINGS] Error loading skin profile:', error)
        }
      }
    }

    loadProfileData()
  }, [user])

  const handleSave = async () => {
    setIsLoading(true)
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error("No authentication token found")
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://dermalens-backend-941238576063.us-central1.run.app'
      
      // Update user profile
      if (updateProfile) {
        await updateProfile(profileData)
      }

      // Update skin profile separately
      const skinProfileData = {
        skin_type: profileData.skinType,
        primary_concerns: profileData.skinConcerns.split(',').map(s => s.trim()).filter(Boolean),
        allergies: profileData.allergies.split(',').map(s => s.trim()).filter(Boolean),
        routine_frequency: profileData.routinePreference || undefined,
      }

      const skinProfileResponse = await fetch(`${apiUrl}/skin-profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(skinProfileData)
      })

      if (!skinProfileResponse.ok) {
        // Try creating if it doesn't exist
        if (skinProfileResponse.status === 404) {
          const createResponse = await fetch(`${apiUrl}/skin-profile`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(skinProfileData)
          })
          
          if (!createResponse.ok) {
            throw new Error("Failed to create skin profile")
          }
        } else {
          throw new Error("Failed to update skin profile")
        }
      }

      setIsEditing(false)
      setSuccessMessage("Profile updated successfully!")
      setError(null)
      
      // Reload data without full page reload
      setTimeout(() => {
        window.location.reload()
      }, 1500)
    } catch (error: any) {
      console.error("Error updating profile:", error)
      setError(error.message || "Failed to update profile. Please try again.")
      setSuccessMessage(null)
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = async () => {
    try {
      await signOut()
      router.push("/")
    } catch (error) {
      console.error("Error signing out:", error)
    }
  }

  const handleGoHome = () => {
    router.push("/dashboard")
  }

  // Guard: user context not yet available.
  // Must come AFTER all hooks so hooks are called unconditionally on every render
  // (React rules-of-hooks). The useEffect above already no-ops when `user` is falsy.
  if (!userContext) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Loading...</h1>
          <p className="text-gray-600">Please wait while we load your profile.</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-white via-green-50 to-green-100 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Access Denied</CardTitle>
            <CardDescription>Please sign in to access your settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button onClick={() => router.push("/login")} className="w-full">
              Sign In
            </Button>
            <Button onClick={() => router.push("/")} variant="outline" className="w-full">
              Go Home
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-green-50 to-green-100">
      <div className="max-w-4xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center">
              <Settings className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
              <p className="text-gray-600">Manage your account and preferences</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Navigation Sidebar */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button 
                  onClick={handleGoHome}
                  variant="outline" 
                  className="w-full justify-start"
                >
                  <Home className="w-4 h-4 mr-2" />
                  Go to Home
                </Button>
                <Button 
                  onClick={() => router.push("/dashboard")}
                  variant="outline" 
                  className="w-full justify-start"
                >
                  <User className="w-4 h-4 mr-2" />
                  Dashboard
                </Button>
                <Button 
                  onClick={() => router.push("/scan")}
                  variant="outline" 
                  className="w-full justify-start"
                >
                  <Camera className="w-4 h-4 mr-2" />
                  Face Scan
                </Button>
                <Separator className="my-4" />
                <Button 
                  onClick={handleLogout}
                  variant="destructive" 
                  className="w-full justify-start"
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  Sign Out
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Profile Information */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-xl">Profile Information</CardTitle>
                    <CardDescription>Update your personal details and skin profile</CardDescription>
                  </div>
                  <Button 
                    onClick={() => setIsEditing(!isEditing)}
                    variant={isEditing ? "outline" : "default"}
                  >
                    {isEditing ? <Edit3 className="w-4 h-4 mr-2" /> : <Edit3 className="w-4 h-4 mr-2" />}
                    {isEditing ? "Cancel" : "Edit Profile"}
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
                {successMessage && (
                  <Alert className="bg-green-50 border-green-200">
                    <AlertDescription className="text-green-800">{successMessage}</AlertDescription>
                  </Alert>
                )}
                {/* Avatar Section */}
                <div className="flex items-center gap-4">
                  <Avatar className="w-20 h-20">
                    <AvatarImage src="/user-profile-photo.png" />
                    <AvatarFallback className="bg-primary text-primary-foreground text-xl">
                      {(user as any).username?.charAt(0).toUpperCase() || user.email?.charAt(0).toUpperCase() || 'U'}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h3 className="text-lg font-semibold">{(user as any).username || user.email || "User"}</h3>
                    <p className="text-sm text-gray-600">{user.email}</p>
                    {isEditing && (
                      <Button size="sm" variant="outline" className="mt-2">
                        <Camera className="w-4 h-4 mr-2" />
                        Change Photo
                      </Button>
                    )}
                  </div>
                </div>

                <Separator />

                {/* Profile Form */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="username">Username</Label>
                    <Input
                      id="username"
                      value={profileData.username}
                      onChange={(e) => setProfileData({...profileData, username: e.target.value})}
                      disabled={!isEditing}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={profileData.email}
                      onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                      disabled={!isEditing}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="firstName">First Name</Label>
                    <Input
                      id="firstName"
                      value={profileData.firstName}
                      onChange={(e) => setProfileData({...profileData, firstName: e.target.value})}
                      disabled={!isEditing}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastName">Last Name</Label>
                    <Input
                      id="lastName"
                      value={profileData.lastName}
                      onChange={(e) => setProfileData({...profileData, lastName: e.target.value})}
                      disabled={!isEditing}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="bio">Bio</Label>
                  <Textarea
                    id="bio"
                    value={profileData.bio}
                    onChange={(e) => setProfileData({...profileData, bio: e.target.value})}
                    disabled={!isEditing}
                    placeholder="Tell us about yourself..."
                    rows={3}
                  />
                </div>

                {/* Skin Profile Section */}
                <div className="space-y-4">
                  <h4 className="text-lg font-semibold flex items-center gap-2">
                    <Palette className="w-5 h-5" />
                    Skin Profile
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="skinType">Skin Type</Label>
                      <Input
                        id="skinType"
                        value={profileData.skinType}
                        onChange={(e) => setProfileData({...profileData, skinType: e.target.value})}
                        disabled={!isEditing}
                        placeholder="e.g., Combination, Oily, Dry"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="skinConcerns">Skin Concerns</Label>
                      <Input
                        id="skinConcerns"
                        value={profileData.skinConcerns}
                        onChange={(e) => setProfileData({...profileData, skinConcerns: e.target.value})}
                        disabled={!isEditing}
                        placeholder="e.g., Acne, Dark spots, Wrinkles"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="allergies">Allergies</Label>
                    <Input
                      id="allergies"
                      value={profileData.allergies}
                      onChange={(e) => setProfileData({...profileData, allergies: e.target.value})}
                      disabled={!isEditing}
                      placeholder="List any known allergies"
                    />
                  </div>
                  
                  {/* Routine Preference */}
                  <div className="space-y-2">
                    <Label htmlFor="routinePreference">Current Skincare Routine</Label>
                    <select
                      id="routinePreference"
                      value={profileData.routinePreference || ""}
                      onChange={(e) => setProfileData({...profileData, routinePreference: e.target.value})}
                      disabled={!isEditing}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                    >
                      <option value="">Select your current routine</option>
                      <option value="no_routine">No routine - I don't have a skincare routine</option>
                      <option value="basic">Basic - Just cleanser and moisturizer</option>
                      <option value="moderate">Moderate - 3-5 products daily</option>
                      <option value="extensive">Extensive - 6+ products daily</option>
                      <option value="minimal">Minimal - Very simple routine</option>
                      <option value="professional">Professional - Dermatologist recommended</option>
                    </select>
                    <p className="text-sm text-gray-600">
                      Help us understand your current skincare habits to provide better recommendations.
                    </p>
                  </div>
                </div>

                {/* Save Button */}
                {isEditing && (
                  <div className="flex gap-2 pt-4">
                    <Button 
                      onClick={handleSave}
                      disabled={isLoading}
                      className="flex-1"
                    >
                      <Save className="w-4 h-4 mr-2" />
                      {isLoading ? "Saving..." : "Save Changes"}
                    </Button>
                    <Button 
                      onClick={() => setIsEditing(false)}
                      variant="outline"
                    >
                      Cancel
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Account Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="text-xl flex items-center gap-2">
                  <Shield className="w-5 h-5" />
                  Account Settings
                </CardTitle>
                <CardDescription>Manage your account security and preferences</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h4 className="font-semibold">Change Password</h4>
                    <p className="text-sm text-gray-600">Update your account password</p>
                  </div>
                  <Button variant="outline">Change</Button>
                </div>
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h4 className="font-semibold">Notifications</h4>
                    <p className="text-sm text-gray-600">Manage your notification preferences</p>
                  </div>
                  <Button variant="outline">
                    <Bell className="w-4 h-4 mr-2" />
                    Settings
                  </Button>
                </div>
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h4 className="font-semibold">Data & Privacy</h4>
                    <p className="text-sm text-gray-600">Manage your data and privacy settings</p>
                  </div>
                  <Button variant="outline">
                    <Database className="w-4 h-4 mr-2" />
                    Manage
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Danger Zone */}
            <Card className="border-red-200">
              <CardHeader>
                <CardTitle className="text-xl flex items-center gap-2 text-red-600">
                  <AlertTriangle className="w-5 h-5" />
                  Danger Zone
                </CardTitle>
                <CardDescription>Irreversible and destructive actions</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 border border-red-200 rounded-lg bg-red-50">
                  <div>
                    <h4 className="font-semibold text-red-800">Delete Account</h4>
                    <p className="text-sm text-red-600">Permanently delete your account and all data</p>
                  </div>
                  <Button variant="destructive">Delete Account</Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
