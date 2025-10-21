"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from "react"
import { registerUser, authenticateUser, getCurrentUser, logoutUser, isAuthenticated, setUserContext, clearUserContext, User as AuthUser } from "@/lib/custom-auth"
import { apiClient, SkinProfile, AnalysisResult } from "@/lib/api"
import { supabase } from "@/lib/supabase"

// Use the User type from custom-auth
export type User = AuthUser

interface FaceScanData {
  id: string
  userId: string
  timestamp: string
  conditions: Array<{
    condition: string
    confidence: number
    severity: string
  }>
  imageData?: string
  analysisResults?: AnalysisResult
}

interface UserContextType {
  user: User | null
  skinProfile: SkinProfile | null
  faceScanData: FaceScanData[]
  isLoading: boolean
  error: string | null
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string, username: string) => Promise<void>
  signOut: () => Promise<void>
  updateProfile: (updates: Partial<User>) => Promise<void>
  getSkinProfile: () => Promise<void>
  createSkinProfile: (data: Partial<SkinProfile>) => Promise<void>
  updateSkinProfile: (data: Partial<SkinProfile>) => Promise<void>
  analyzeSkin: (file: File) => Promise<AnalysisResult>
  analyzeSkinComprehensive: (imageId?: string) => Promise<any>
  saveFaceScanData: (scanData: Omit<FaceScanData, 'id' | 'userId' | 'timestamp'>) => void
  getLatestScanData: () => FaceScanData | null
  clearError: () => void
}

const UserContext = createContext<UserContextType | undefined>(undefined)

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [skinProfile, setSkinProfile] = useState<SkinProfile | null>(null)
  const [faceScanData, setFaceScanData] = useState<FaceScanData[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingProfile, setIsLoadingProfile] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load user data from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('dermalens_user')
    const savedScanData = localStorage.getItem('dermalens_scan_data')
    
    if (savedUser) {
      const user = JSON.parse(savedUser)
      setUser(user)
      // Set user context for RLS
      try {
        console.log('🔧 [FRONTEND] Setting user context on page load...')
        setUserContext(user.id).then(() => {
          console.log('✅ [FRONTEND] User context set on page load')
        }).catch((contextError) => {
          console.error('❌ [FRONTEND] Failed to set user context on page load:', contextError)
        })
      } catch (error) {
        console.error('❌ [FRONTEND] Error setting user context on page load:', error)
      }
    }
    
    if (savedScanData) {
      setFaceScanData(JSON.parse(savedScanData))
    }

    // Check if user is authenticated and load profile
    if (isAuthenticated()) {
      loadUserProfile()
    }
  }, [])

  // Save user data to localStorage whenever it changes
  useEffect(() => {
    if (user) {
      localStorage.setItem('dermalens_user', JSON.stringify(user))
    } else {
      localStorage.removeItem('dermalens_user')
    }
  }, [user])

  // Save scan data to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('dermalens_scan_data', JSON.stringify(faceScanData))
  }, [faceScanData])

  const loadUserProfile = async () => {
    // Prevent multiple simultaneous calls
    if (isLoadingProfile) {
      console.log('⏳ [LOAD PROFILE] Already loading profile, skipping...')
      return
    }

    try {
      setIsLoadingProfile(true)
      const user = getCurrentUser()
      if (user) {
        setUser(user)
        
        // Try to load skin profile directly without setting loading state
        try {
          // Ensure user context is set for RLS
          console.log('🔧 [LOAD PROFILE] Setting user context for RLS...')
          try {
            await setUserContext(user.id)
            console.log('✅ [LOAD PROFILE] User context set successfully')
            
            // Add a small delay to ensure context is set
            await new Promise(resolve => setTimeout(resolve, 100))
            console.log('⏳ [LOAD PROFILE] Context setting delay completed')
          } catch (contextError) {
            console.error('❌ [LOAD PROFILE] Failed to set user context:', contextError)
            // Don't continue if context setting fails
            setSkinProfile(null)
            return
          }

          console.log('📊 [LOAD PROFILE] Querying user_skin_profiles...')
          const { data, error } = await supabase
            .from('user_skin_profiles')
            .select('*')
            .eq('user_id', user.id)
            .single()

          if (error) {
            if (error.code === 'PGRST116') {
              // No profile found, that's okay
              console.log('📝 [LOAD PROFILE] No skin profile found (PGRST116)')
              setSkinProfile(null)
            } else {
              console.error('❌ [LOAD PROFILE] Database query error:', error)
              throw error
            }
          } else {
            console.log('✅ [LOAD PROFILE] Skin profile loaded successfully:', data)
            setSkinProfile(data)
          }
        } catch (error) {
          // Skin profile doesn't exist yet, that's okay
          console.log('📝 [LOAD PROFILE] No skin profile found or error:', error)
          setSkinProfile(null)
        }
      }
    } catch (error) {
      console.error('❌ [LOAD PROFILE] Failed to load user profile:', error)
      setUser(null)
    } finally {
      setIsLoadingProfile(false)
    }
  }

  const signIn = async (email: string, password: string) => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await authenticateUser(email, password)
      
      if (response.success && response.user) {
        setUser(response.user)
        // Set user context for RLS
        try {
          console.log('🔧 [FRONTEND] Setting user context for RLS...')
          await setUserContext(response.user.id)
          console.log('✅ [FRONTEND] User context set successfully')
        } catch (contextError) {
          console.error('❌ [FRONTEND] Failed to set user context:', contextError)
          // Don't throw error, just log it
        }
      } else {
        throw new Error(response.error || 'Sign in failed')
      }
    } catch (error: any) {
      setError(error.message || 'Sign in failed')
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const signUp = async (email: string, password: string, username: string) => {
    console.log('🚀 [FRONTEND] Starting signup process...')
    console.log('📧 [FRONTEND] Email:', email)
    console.log('👤 [FRONTEND] Username:', username)
    
    try {
      setIsLoading(true)
      setError(null)
      
      console.log('🌐 [FRONTEND] Calling custom auth registerUser...')
      const response = await registerUser(email, password, username)
      
      console.log('✅ [FRONTEND] Registration successful')
      console.log('👤 [FRONTEND] User received:', response.user)
      
      if (response.success && response.user) {
        setUser(response.user)
        // Set user context for RLS
        try {
          console.log('🔧 [FRONTEND] Setting user context for RLS...')
          await setUserContext(response.user.id)
          console.log('✅ [FRONTEND] User context set successfully')
          
          // Add a small delay to ensure context is set before any queries
          await new Promise(resolve => setTimeout(resolve, 100))
          console.log('⏳ [FRONTEND] Context setting delay completed')
        } catch (contextError) {
          console.error('❌ [FRONTEND] Failed to set user context:', contextError)
          // Don't throw error, just log it
        }
        console.log('💾 [FRONTEND] User state updated successfully')
      } else {
        throw new Error(response.error || 'Registration failed')
      }
      
    } catch (error: any) {
      console.error('❌ [FRONTEND] Signup failed:', error)
      console.error('❌ [FRONTEND] Error message:', error.message)
      setError(error.message || 'Sign up failed')
      throw error
    } finally {
      setIsLoading(false)
      console.log('🏁 [FRONTEND] Signup process completed')
    }
  }

  const signOut = async () => {
    try {
      setIsLoading(true)
      // Clear user context for RLS
      await clearUserContext()
      logoutUser()
    } catch (error) {
      console.error('Sign out error:', error)
    } finally {
    setUser(null)
      setSkinProfile(null)
      setIsLoading(false)
    }
  }

  const updateProfile = async (updates: Partial<User>) => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await apiClient.updateProfile(updates)
      setUser({
        ...response.profile,
        username: response.profile.username || ''
      })
    } catch (error: any) {
      setError(error.message || 'Profile update failed')
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const getSkinProfile = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      if (!user) {
        throw new Error('User not authenticated')
      }

      // Ensure user context is set for RLS
      try {
        console.log('🔧 [USER CONTEXT] Setting user context for RLS...')
        await setUserContext(user.id)
        console.log('✅ [USER CONTEXT] User context set successfully')
        
        // Add a small delay to ensure context is set
        await new Promise(resolve => setTimeout(resolve, 100))
        console.log('⏳ [USER CONTEXT] Context setting delay completed')
      } catch (contextError) {
        console.error('❌ [USER CONTEXT] Failed to set user context:', contextError)
        // Don't continue if context setting fails
        throw new Error('Failed to set user context for database access')
      }

      const { data, error } = await supabase
        .from('user_skin_profiles')
        .select('*')
        .eq('user_id', user.id)
        .single()

      if (error) {
        if (error.code === 'PGRST116') {
          // No profile found, that's okay
          setSkinProfile(null)
          return
        }
        throw error
      }

      setSkinProfile(data)
    } catch (error: any) {
      setError(error.message || 'Failed to load skin profile')
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const createSkinProfile = async (data: Partial<SkinProfile>) => {
    try {
      console.log('🔄 [USER CONTEXT] Starting createSkinProfile...')
      console.log('👤 [USER CONTEXT] User ID:', user?.id)
      console.log('📊 [USER CONTEXT] Profile data:', data)
      
      setIsLoading(true)
      setError(null)
      
      if (!user) {
        throw new Error('User not authenticated')
      }

      // Ensure user context is set for RLS
      try {
        console.log('🔧 [USER CONTEXT] Setting user context for RLS...')
        await setUserContext(user.id)
        console.log('✅ [USER CONTEXT] User context set successfully')
        
        // Add a small delay to ensure context is set
        await new Promise(resolve => setTimeout(resolve, 100))
        console.log('⏳ [USER CONTEXT] Context setting delay completed')
      } catch (contextError) {
        console.error('❌ [USER CONTEXT] Failed to set user context:', contextError)
        // Don't continue if context setting fails
        throw new Error('Failed to set user context for database access')
      }

      const profileData = {
        ...data,
        user_id: user.id
      }

      console.log('📤 [USER CONTEXT] Inserting profile data:', profileData)
      const { data: newProfile, error } = await supabase
        .from('user_skin_profiles')
        .insert(profileData)
        .select()
        .single()

      if (error) {
        console.error('❌ [USER CONTEXT] Database insert error:', error)
        throw error
      }

      console.log('✅ [USER CONTEXT] Profile created successfully:', newProfile)
      setSkinProfile(newProfile)
    } catch (error: any) {
      console.error('❌ [USER CONTEXT] createSkinProfile failed:', error)
      setError(error.message || 'Failed to create skin profile')
      throw error
    } finally {
      console.log('🏁 [USER CONTEXT] createSkinProfile completed, setting loading to false')
      setIsLoading(false)
    }
  }

  const updateSkinProfile = async (data: Partial<SkinProfile>) => {
    try {
      setIsLoading(true)
      setError(null)
      
      if (!user) {
        throw new Error('User not authenticated')
      }

      // Ensure user context is set for RLS
      try {
        console.log('🔧 [USER CONTEXT] Setting user context for RLS...')
        await setUserContext(user.id)
        console.log('✅ [USER CONTEXT] User context set successfully')
        
        // Add a small delay to ensure context is set
        await new Promise(resolve => setTimeout(resolve, 100))
        console.log('⏳ [USER CONTEXT] Context setting delay completed')
      } catch (contextError) {
        console.error('❌ [USER CONTEXT] Failed to set user context:', contextError)
        // Don't continue if context setting fails
        throw new Error('Failed to set user context for database access')
      }

      const { data: updatedProfile, error } = await supabase
        .from('user_skin_profiles')
        .update(data)
        .eq('user_id', user.id)
        .select()
        .single()

      if (error) {
        throw error
      }

      setSkinProfile(updatedProfile)
    } catch (error: any) {
      setError(error.message || 'Failed to update skin profile')
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const analyzeSkin = async (file: File): Promise<AnalysisResult> => {
    try {
      setIsLoading(true)
      setError(null)
      const result = await apiClient.analyzeSkin(file)
      
      // Save scan data locally
      if (user) {
        const scanData: Omit<FaceScanData, 'id' | 'userId' | 'timestamp'> = {
          conditions: result.analysis_results.flatMap(r => r.conditions),
          analysisResults: result
        }
        saveFaceScanData(scanData)
      }
      
      return result
    } catch (error: any) {
      setError(error.message || 'Skin analysis failed')
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const analyzeSkinComprehensive = async (imageId?: string): Promise<any> => {
    try {
      setIsLoading(true)
      setError(null)
      
      if (!user) {
        throw new Error('User not authenticated')
      }

      console.log('🔬 [COMPREHENSIVE] Starting comprehensive analysis with Gemini 1.5 Pro...')
      console.log('👤 [COMPREHENSIVE] User ID:', user.id)
      console.log('🖼️ [COMPREHENSIVE] Image ID:', imageId)

      // For now, let's use a simple approach without authentication
      // since our custom auth doesn't use JWT tokens
      const response = await fetch('http://localhost:8000/api/analyze-user-comprehensive', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: user.id,
          image_id: imageId
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Comprehensive analysis failed')
      }

      const result = await response.json()
      console.log('✅ [COMPREHENSIVE] Analysis successful:', result)

      // Save scan data locally
      if (result.analysis_results) {
        const scanData: Omit<FaceScanData, 'id' | 'userId' | 'timestamp'> = {
          conditions: result.analysis_results.flatMap((r: any) => r.conditions || []),
          analysisResults: result
        }
        saveFaceScanData(scanData)
      }

      return result
    } catch (error: any) {
      console.error('❌ [COMPREHENSIVE] Analysis failed:', error)
      setError(error.message || 'Comprehensive analysis failed')
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const saveFaceScanData = (scanData: Omit<FaceScanData, 'id' | 'userId' | 'timestamp'>) => {
    if (!user) return

    const newScanData: FaceScanData = {
      ...scanData,
      id: Date.now().toString(),
      userId: user.id,
      timestamp: new Date().toISOString()
    }

    setFaceScanData(prev => [newScanData, ...prev])
  }

  const getLatestScanData = () => {
    if (!user || faceScanData.length === 0) return null
    return faceScanData.find(scan => scan.userId === user.id) || null
  }

  const clearError = () => {
    setError(null)
  }

  return (
    <UserContext.Provider value={{
      user,
      skinProfile,
      faceScanData,
      isLoading,
      error,
      signIn,
      signUp,
      signOut,
      updateProfile,
      getSkinProfile,
      createSkinProfile,
      updateSkinProfile,
      analyzeSkin,
      analyzeSkinComprehensive,
      saveFaceScanData,
      getLatestScanData,
      clearError
    }}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  const context = useContext(UserContext)
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}
