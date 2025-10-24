"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { UserProfileDialog } from "@/components/user-profile-dialog"
import { FaceUploadDialog } from "@/components/face-upload-dialog"
import { SkincareRoutineDialog } from "@/components/skincare-routine-dialog"
import { useUser } from "@/contexts/user-context"
import { Sparkles, Plus, Calendar, User, LogIn, LogOut, Settings } from "lucide-react"

export function Header() {
  const [isProfileOpen, setIsProfileOpen] = useState(false)
  const [isUploadOpen, setIsUploadOpen] = useState(false)
  const [isRoutineOpen, setIsRoutineOpen] = useState(false)
  const { user, signOut } = useUser()
  const router = useRouter()

  const handleSignOut = () => {
    signOut()
    router.push('/')
  }

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
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-2">
                    <Avatar className="w-9 h-9">
                      <AvatarImage src="/user-profile-photo.png" />
                      <AvatarFallback className="bg-primary text-primary-foreground">
                        {user ? user.username.charAt(0).toUpperCase() : 'U'}
                      </AvatarFallback>
                    </Avatar>
                    <span className="hidden sm:inline text-sm font-medium">
                      {user ? user.username : 'Profile'}
                    </span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel>
                    {user ? user.email : 'Guest User'}
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  {user ? (
                    <>
                      <DropdownMenuItem onClick={() => router.push('/dashboard')}>
                        <User className="mr-2 h-4 w-4" />
                        Dashboard
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setIsProfileOpen(true)}>
                        <Settings className="mr-2 h-4 w-4" />
                        Profile Settings
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem onClick={handleSignOut}>
                        <LogOut className="mr-2 h-4 w-4" />
                        Sign Out
                      </DropdownMenuItem>
                    </>
                  ) : (
                    <DropdownMenuItem onClick={() => router.push('/login')}>
                      <LogIn className="mr-2 h-4 w-4" />
                      Sign In
                    </DropdownMenuItem>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
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
