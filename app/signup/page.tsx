"use client"

import React, { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Eye, EyeOff } from "lucide-react"

// Use environment variable with production fallback
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://dermalens-backend-941238576063.us-central1.run.app'

export default function SignUpPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [error, setError] = useState("")

  // Clear any existing user data when component mounts
  React.useEffect(() => {
    console.log('🧹 Clearing any existing user data on signup page load')
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    localStorage.removeItem("skinProfile")
    localStorage.removeItem("currentUser")
    localStorage.removeItem("dermalens_user")
    localStorage.removeItem("dermalens_scan_data")
    localStorage.removeItem("dermalens_skin_profile")
  }, [])

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("") // Clear any previous errors
    console.log('🚀 Sign up button clicked!')
    console.log('📧 Email:', email)
    console.log('🔒 Password length:', password.length)
    
    if (password !== confirmPassword) {
      setError("Passwords don't match!")
      return
    }
    
    setLoading(true)
    console.log('⏳ Loading state set to true')
    
    try {
      console.log('🌐 Making API request to signup endpoint...')
      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })
      
      console.log('📡 Response status:', response.status)
      const data = await response.json()
      console.log('📦 Response data:', data)
      
      if (data.success) {
        console.log('✅ Signup successful!')
        // Clear any existing user data first
        localStorage.removeItem("token")
        localStorage.removeItem("user")
        localStorage.removeItem("skinProfile")
        localStorage.removeItem("currentUser")
        localStorage.removeItem("dermalens_user")
        localStorage.removeItem("dermalens_scan_data")
        localStorage.removeItem("dermalens_skin_profile")
        console.log('🧹 Cleared previous user data from localStorage')
        
        // Store new user data
        localStorage.setItem("token", data.access_token)
        localStorage.setItem("user", JSON.stringify(data.user))
        localStorage.setItem("dermalens_user", JSON.stringify(data.user))
        console.log('💾 New user data stored in localStorage')
        // Redirect to profile setup
        console.log('🔄 Redirecting to profile page...')
        window.location.href = "/profile"
      } else {
        console.error('❌ Signup failed:', data.error)
        setError(data.error || "Sign up failed")
      }
    } catch (error: any) {
      console.error('💥 Signup error:', error)
      setError("Sign up error: " + (error.message || "Unable to connect to server. Please try again."))
    } finally {
      setLoading(false)
      console.log('🏁 Loading state set to false')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-white to-green-100 p-4">
      <Card className="w-full max-w-md bg-white/90 backdrop-blur-sm border-2 border-green-200 shadow-2xl">
        <CardHeader className="space-y-1 text-center pb-6">
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-full flex items-center justify-center mb-4 shadow-lg">
            <span className="text-2xl">🌿</span>
          </div>
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-green-600 to-green-800 bg-clip-text text-transparent">
            Create Your Account
          </CardTitle>
          <CardDescription className="text-green-700 text-base">
            Sign up to start your personalized skincare journey
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          <form onSubmit={handleSignUp} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-green-700 font-semibold">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value)
                  if (error) setError("") // Clear error when user starts typing
                }}
                required
                className="border-green-300 focus:border-green-500 focus:ring-green-500 transition-colors"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="text-green-700 font-semibold">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder=""
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value)
                    if (error) setError("") // Clear error when user starts typing
                  }}
                  required
                  minLength={6}
                  className="pr-10 border-green-300 focus:border-green-500 focus:ring-green-500 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-green-600 hover:text-green-800 transition-colors"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="text-green-700 font-semibold">Confirm Password</Label>
              <div className="relative">
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  placeholder=""
                  value={confirmPassword}
                  onChange={(e) => {
                    setConfirmPassword(e.target.value)
                    if (error) setError("") // Clear error when user starts typing
                  }}
                  required
                  minLength={6}
                  className="pr-10 border-green-300 focus:border-green-500 focus:ring-green-500 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-green-600 hover:text-green-800 transition-colors"
                  aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                >
                  {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <Button 
              type="submit" 
              className="w-full bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white font-bold border-2 border-green-700 shadow-lg h-12 text-base transition-all duration-200 transform hover:scale-105" 
              disabled={loading}
            >
              {loading ? "Creating Account..." : "Sign Up"}
            </Button>
            <div className="text-center text-sm text-green-700">
              Already have an account?{" "}
              <a href="/login" className="text-green-600 hover:text-green-800 font-semibold hover:underline transition-colors">
                Log In
              </a>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

