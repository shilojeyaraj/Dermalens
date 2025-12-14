"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from "react"

export interface User {
  id: string
  email: string
  created_at?: string
}

interface UserContextType {
  user: User | null
  setUser: (user: User | null) => void
  isLoading: boolean
  error: string | null
  clearError: () => void
  skinProfile: any
  analysisResult: any
  fetchUserProfile: () => Promise<void>
  updateUserProfile: (data: any) => Promise<void>
  createSkinProfile: (data: any) => Promise<void>
  updateSkinProfile: (data: any) => Promise<void>
  uploadImage: (file: File) => Promise<void>
  analyzeImage: (imageId: string) => Promise<void>
}

const UserContext = createContext<UserContextType | undefined>(undefined)

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [skinProfile, setSkinProfile] = useState<any>(null)
  const [analysisResult, setAnalysisResult] = useState<any>(null)

  useEffect(() => {
    // Check for stored user on mount
    const storedUser = localStorage.getItem("user")
    const storedToken = localStorage.getItem("token")
    const storedSkinProfile = localStorage.getItem("skinProfile")
    
    if (storedUser && storedToken) {
      try {
        setUser(JSON.parse(storedUser))
        console.log("✅ [USER CONTEXT] User loaded from localStorage")
      } catch (e) {
        console.error("Failed to parse stored user:", e)
      }
    }
    
    if (storedSkinProfile) {
      try {
        setSkinProfile(JSON.parse(storedSkinProfile))
        console.log("✅ [USER CONTEXT] Skin profile loaded from localStorage")
      } catch (e) {
        console.error("Failed to parse stored skin profile:", e)
      }
    }
  }, [])

  const clearError = () => {
    console.log("✅ [USER CONTEXT] clearError called")
    setError(null)
  }

  const fetchUserProfile = async () => {
    console.log("📥 [USER CONTEXT] fetchUserProfile called")
    // Placeholder - implement if needed
  }

  const updateUserProfile = async (data: any) => {
    console.log("📝 [USER CONTEXT] updateUserProfile called", data)
    // Placeholder - implement if needed
  }

  const createSkinProfile = async (data: any) => {
    console.log("➕ [USER CONTEXT] createSkinProfile called", data)
    setIsLoading(true)
    setError(null)
    try {
      // Save to localStorage for now (replace with API call later)
      localStorage.setItem("skinProfile", JSON.stringify(data))
      setSkinProfile(data)
      console.log("✅ [USER CONTEXT] Skin profile created successfully")
    } catch (err: any) {
      const errorMsg = err.message || "Failed to create skin profile"
      console.error("❌ [USER CONTEXT] Error:", errorMsg)
      setError(errorMsg)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const updateSkinProfile = async (data: any) => {
    console.log("🔄 [USER CONTEXT] updateSkinProfile called", data)
    setIsLoading(true)
    setError(null)
    try {
      // Save to localStorage for now (replace with API call later)
      localStorage.setItem("skinProfile", JSON.stringify(data))
      setSkinProfile(data)
      console.log("✅ [USER CONTEXT] Skin profile updated successfully")
    } catch (err: any) {
      const errorMsg = err.message || "Failed to update skin profile"
      console.error("❌ [USER CONTEXT] Error:", errorMsg)
      setError(errorMsg)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const uploadImage = async (file: File) => {
    console.log("📤 [USER CONTEXT] uploadImage called", file.name)
    setIsLoading(true)
    setError(null)
    try {
      // Placeholder - implement API call
      console.log("✅ [USER CONTEXT] Image uploaded successfully")
    } catch (err: any) {
      const errorMsg = err.message || "Failed to upload image"
      console.error("❌ [USER CONTEXT] Error:", errorMsg)
      setError(errorMsg)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const analyzeImage = async (imageId: string) => {
    console.log("🔍 [USER CONTEXT] analyzeImage called", imageId)
    setIsLoading(true)
    setError(null)
    try {
      // Placeholder - implement API call
      console.log("✅ [USER CONTEXT] Image analyzed successfully")
    } catch (err: any) {
      const errorMsg = err.message || "Failed to analyze image"
      console.error("❌ [USER CONTEXT] Error:", errorMsg)
      setError(errorMsg)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const value = {
    user, 
    setUser, 
    isLoading, 
    error, 
    clearError,
    skinProfile,
    analysisResult,
    fetchUserProfile,
    updateUserProfile,
    createSkinProfile,
    updateSkinProfile,
    uploadImage,
    analyzeImage
  }

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  const context = useContext(UserContext)
  if (context === undefined) {
    throw new Error("useUser must be used within a UserProvider")
  }
  return context
}
