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
import { Sparkles, Plus, Calendar, User, LogIn, LogOut, Settings } from "lucide-react"

export function Header() {
  const router = useRouter()
  const [isProfileOpen, setIsProfileOpen] = useState(false)
  const [isUploadOpen, setIsUploadOpen] = useState(false)
  const [isRoutineOpen, setIsRoutineOpen] = useState(false)

  // Get user data from localStorage
  const user = typeof window !== 'undefined' ? JSON.parse(localStorage.getItem('user') || 'null') : null

  const handleSignOut = () => {
    // Show confirmation
    if (confirm('Are you sure you want to sign out?')) {
      // Clear all user data
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('skinProfile')
      localStorage.removeItem('currentUser')
      localStorage.removeItem('dermalens_user')
      localStorage.removeItem('dermalens_scan_data')
      localStorage.removeItem('dermalens_skin_profile')
      localStorage.removeItem('skinAnalysis')
      
      // Show success message
      alert('You have been signed out successfully!')
      
      // Redirect to home
      router.push('/')
    }
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
                variant="ghost"
                className="hidden sm:flex items-center gap-2"
                onClick={() => router.push('/')}
              >
                <Sparkles className="w-4 h-4" />
                <span className="text-sm font-medium">Home</span>
              </Button>
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
                  <Button 
                    variant="ghost" 
                    className="w-10 h-10 rounded-full bg-green-600 hover:bg-green-700 p-0"
                    onClick={() => console.log('Profile trigger clicked')}
                  >
                    <span className="text-white text-lg">👤</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel>
                    {user ? user.email : 'Guest User'}
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  {user ? (
                    <>
                      <DropdownMenuItem onClick={() => router.push('/')}>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Home
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => router.push('/dashboard')}>
                        <User className="mr-2 h-4 w-4" />
                        Dashboard
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => router.push('/settings')}>
                        <Settings className="mr-2 h-4 w-4" />
                        Edit Profile
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
