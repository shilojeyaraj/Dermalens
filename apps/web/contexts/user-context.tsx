"use client"

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface User {
  id: string
  username: string
  email: string
}

interface SkinProfile {
  id: string
  skinType: string
  concerns: string[]
  routine: string
}

interface UserContextType {
  user: User | null
  skinProfile: SkinProfile | null
  isLoading: boolean
  error: string | null
  signIn: (email: string, password: string) => Promise<void>
  signUp: (username: string, email: string, password: string) => Promise<void>
  signOut: () => void
  createSkinProfile: (profile: Omit<SkinProfile, 'id'>) => Promise<void>
  updateSkinProfile: (profile: Partial<SkinProfile>) => Promise<void>
  analyzeSkin: (imageFile: File) => Promise<any>
  analyzeSkinComprehensive: (imageFile: File) => Promise<any>
  getLatestScanData: () => any
  clearError: () => void
}

const UserContext = createContext<UserContextType | undefined>(undefined)

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [skinProfile, setSkinProfile] = useState<SkinProfile | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Check for existing user session on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('user')
    const storedSkinProfile = localStorage.getItem('skinProfile')
    
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser))
      } catch (e) {
        console.error('Error parsing stored user:', e)
        localStorage.removeItem('user')
      }
    }
    
    if (storedSkinProfile) {
      try {
        setSkinProfile(JSON.parse(storedSkinProfile))
      } catch (e) {
        console.error('Error parsing stored skin profile:', e)
        localStorage.removeItem('skinProfile')
      }
    }
  }, [])

  const signIn = async (email: string, password: string) => {
    setIsLoading(true)
    setError(null)
    
    try {
      // Mock authentication - replace with actual API call
      const mockUser = {
        id: '1',
        username: email.split('@')[0],
        email: email
      }
      
      setUser(mockUser)
      localStorage.setItem('user', JSON.stringify(mockUser))
    } catch (err) {
      setError('Failed to sign in. Please check your credentials.')
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const signUp = async (username: string, email: string, password: string) => {
    setIsLoading(true)
    setError(null)
    
    try {
      // Mock registration - replace with actual API call
      const mockUser = {
        id: '1',
        username: username,
        email: email
      }
      
      setUser(mockUser)
      localStorage.setItem('user', JSON.stringify(mockUser))
    } catch (err) {
      setError('Failed to create account. Please try again.')
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const signOut = () => {
    setUser(null)
    setSkinProfile(null)
    localStorage.removeItem('user')
    localStorage.removeItem('skinProfile')
    localStorage.removeItem('skinAnalysis')
  }

  const createSkinProfile = async (profile: Omit<SkinProfile, 'id'>) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const newProfile = {
        ...profile,
        id: Date.now().toString()
      }
      
      setSkinProfile(newProfile)
      localStorage.setItem('skinProfile', JSON.stringify(newProfile))
    } catch (err) {
      setError('Failed to create skin profile.')
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const updateSkinProfile = async (profile: Partial<SkinProfile>) => {
    if (!skinProfile) return
    
    setIsLoading(true)
    setError(null)
    
    try {
      const updatedProfile = { ...skinProfile, ...profile }
      setSkinProfile(updatedProfile)
      localStorage.setItem('skinProfile', JSON.stringify(updatedProfile))
    } catch (err) {
      setError('Failed to update skin profile.')
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const analyzeSkin = async (imageFile: File) => {
    setIsLoading(true)
    setError(null)
    
    try {
      // Mock analysis - replace with actual API call
      const mockAnalysis = {
        skinType: 'Combination',
        concerns: ['Acne', 'Dark spots'],
        recommendations: ['Use gentle cleanser', 'Apply sunscreen daily']
      }
      
      localStorage.setItem('skinAnalysis', JSON.stringify(mockAnalysis))
      return mockAnalysis
    } catch (err) {
      setError('Failed to analyze skin. Please try again.')
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const analyzeSkinComprehensive = async (imageFile: File) => {
    setIsLoading(true)
    setError(null)
    
    try {
      // Mock comprehensive analysis - replace with actual API call
      const mockAnalysis = {
        skinType: 'Combination',
        concerns: ['Acne', 'Dark spots'],
        recommended_products: [
          {
            name: 'Gentle Cleanser',
            brand: 'CeraVe',
            price: 14.99,
            type: 'Cleanser',
            image: '/gentle-cleanser.jpg',
            rating: 4.5,
            description: 'Gentle daily cleanser for combination skin'
          }
        ],
        routine: 'Morning: Cleanser, Moisturizer, Sunscreen\nEvening: Cleanser, Treatment, Moisturizer'
      }
      
      localStorage.setItem('skinAnalysis', JSON.stringify(mockAnalysis))
      return mockAnalysis
    } catch (err) {
      setError('Failed to analyze skin. Please try again.')
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const getLatestScanData = () => {
    try {
      const stored = localStorage.getItem('skinAnalysis')
      return stored ? JSON.parse(stored) : null
    } catch (e) {
      console.error('Error parsing scan data:', e)
      return null
    }
  }

  const clearError = () => {
    setError(null)
  }

  const value: UserContextType = {
    user,
    skinProfile,
    isLoading,
    error,
    signIn,
    signUp,
    signOut,
    createSkinProfile,
    updateSkinProfile,
    analyzeSkin,
    analyzeSkinComprehensive,
    getLatestScanData,
    clearError
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
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}
