"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  Camera, 
  ShoppingBag, 
  Clock, 
  ArrowLeft,
  RefreshCw
} from "lucide-react"
import { useUser } from "@/contexts/user-context"

export default function DashboardPage() {
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()
  const { user, isLoading: userLoading, error } = useUser()

  useEffect(() => {
    if (userLoading) {
      setIsLoading(true)
    } else {
      setIsLoading(false)
    }
  }, [userLoading])

  const handleSkinAnalysis = () => {
    router.push("/scan")
  }

  const handleRecommendedProducts = () => {
    router.push("/products")
  }

  const handleSkincareRoutine = () => {
    router.push("/routine")
  }

  if (userLoading || isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    router.push("/login")
    return null
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-8">
          <Link 
            href="/" 
            className="flex items-center text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Link>
        </div>
        
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-foreground mb-4">Products Dashboard</h1>
        </div>

        {error && (
          <Alert className="mb-6" variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Three Main Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {/* Skin Analysis Card */}
          <Card className="bg-green-50 border-green-200 hover:shadow-lg transition-shadow cursor-pointer" onClick={handleSkinAnalysis}>
            <CardHeader className="text-center pb-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Camera className="w-8 h-8 text-green-600" />
              </div>
              <CardTitle className="text-xl text-green-800">Skin Analysis</CardTitle>
              <CardDescription className="text-green-600 font-medium">
                Upload your photo to get started
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <p className="text-sm text-green-700">
                This is where the skin analysis feature will be implemented.
              </p>
            </CardContent>
          </Card>

          {/* Recommended Products Card */}
          <Card className="bg-green-50 border-green-200 hover:shadow-lg transition-shadow cursor-pointer" onClick={handleRecommendedProducts}>
            <CardHeader className="text-center pb-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <ShoppingBag className="w-8 h-8 text-green-600" />
              </div>
              <CardTitle className="text-xl text-green-800">Recommended Products</CardTitle>
              <CardDescription className="text-green-600 font-medium">
                Based on your skin analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <p className="text-sm text-green-700">
                This is where product recommendations will be displayed.
              </p>
            </CardContent>
          </Card>

          {/* Skincare Routine Card */}
          <Card className="bg-green-50 border-green-200 hover:shadow-lg transition-shadow cursor-pointer" onClick={handleSkincareRoutine}>
            <CardHeader className="text-center pb-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Clock className="w-8 h-8 text-green-600" />
              </div>
              <CardTitle className="text-xl text-green-800">Skincare Routine</CardTitle>
              <CardDescription className="text-green-600 font-medium">
                Personalized daily routine
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <p className="text-sm text-green-700">
                This is where the skincare routine will be shown.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}