"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Camera, Save } from "lucide-react"

type UserProfileDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function UserProfileDialog({ open, onOpenChange }: UserProfileDialogProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [profile, setProfile] = useState({
    name: "Jane Doe",
    email: "jane.doe@example.com",
    skinType: "Combination",
    concerns: "Acne, dark spots, and uneven texture",
    allergies: "None",
  })

  const handleSave = () => {
    // Here you would typically save to a database
    setIsEditing(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Your Profile</DialogTitle>
          <DialogDescription>View and edit your personal information and skin profile</DialogDescription>
        </DialogHeader>
        <div className="space-y-6 py-4">
          {/* Avatar Section */}
          <div className="flex flex-col items-center gap-4">
            <div className="relative">
              <Avatar className="w-24 h-24">
                <AvatarImage src="/user-profile-photo.png" />
                <AvatarFallback className="bg-primary text-primary-foreground text-2xl">JD</AvatarFallback>
              </Avatar>
              {isEditing && (
                <button
                  className="absolute bottom-0 right-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center hover:bg-primary/90 transition-colors"
                  aria-label="Change profile photo"
                >
                  <Camera className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          {/* Profile Information */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                value={profile.name}
                onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                disabled={!isEditing}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={profile.email}
                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                disabled={!isEditing}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="skinType">Skin Type</Label>
              <Input
                id="skinType"
                value={profile.skinType}
                onChange={(e) => setProfile({ ...profile, skinType: e.target.value })}
                disabled={!isEditing}
                placeholder="e.g., Oily, Dry, Combination"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="concerns">Skin Concerns</Label>
              <Textarea
                id="concerns"
                value={profile.concerns}
                onChange={(e) => setProfile({ ...profile, concerns: e.target.value })}
                disabled={!isEditing}
                placeholder="Describe your main skin concerns"
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="allergies">Allergies</Label>
              <Input
                id="allergies"
                value={profile.allergies}
                onChange={(e) => setProfile({ ...profile, allergies: e.target.value })}
                disabled={!isEditing}
                placeholder="List any known allergies"
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            {isEditing ? (
              <>
                <Button onClick={handleSave} className="flex-1 bg-primary hover:bg-primary/90">
                  <Save className="w-4 h-4 mr-2" />
                  Save Changes
                </Button>
                <Button variant="outline" onClick={() => setIsEditing(false)} className="flex-1">
                  Cancel
                </Button>
              </>
            ) : (
              <Button onClick={() => setIsEditing(true)} className="w-full bg-primary hover:bg-primary/90">
                Edit Profile
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
