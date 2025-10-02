"use client"

import { useState } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { UserProfileDialog } from "@/components/user-profile-dialog"
import { FaceUploadDialog } from "@/components/face-upload-dialog"
import { SkincareRoutineDialog } from "@/components/skincare-routine-dialog"
import { Sparkles, Plus, Calendar } from "lucide-react"

export function Header() {
  const [isProfileOpen, setIsProfileOpen] = useState(false)
  const [isUploadOpen, setIsUploadOpen] = useState(false)
  const [isRoutineOpen, setIsRoutineOpen] = useState(false)

  return (
    <>
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">SkinCare AI</h1>
                <p className="text-xs text-muted-foreground">Personalized skincare recommendations</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                className="hidden sm:flex items-center gap-2 bg-transparent"
                onClick={() => setIsRoutineOpen(true)}
              >
                <Calendar className="w-4 h-4" />
                <span className="text-sm font-medium">Your Skincare Routine</span>
              </Button>
              <Button
                variant="default"
                size="icon"
                className="rounded-full w-10 h-10"
                onClick={() => setIsUploadOpen(true)}
              >
                <Plus className="w-5 h-5" />
              </Button>
              <Button variant="ghost" className="flex items-center gap-2" onClick={() => setIsProfileOpen(true)}>
                <Avatar className="w-9 h-9">
                  <AvatarImage src="/user-profile-photo.png" />
                  <AvatarFallback className="bg-primary text-primary-foreground">JD</AvatarFallback>
                </Avatar>
                <span className="hidden sm:inline text-sm font-medium">Profile</span>
              </Button>
            </div>
          </div>
        </div>
      </header>
      <UserProfileDialog open={isProfileOpen} onOpenChange={setIsProfileOpen} />
      <FaceUploadDialog open={isUploadOpen} onOpenChange={setIsUploadOpen} />
      <SkincareRoutineDialog open={isRoutineOpen} onOpenChange={setIsRoutineOpen} />
    </>
  )
}
