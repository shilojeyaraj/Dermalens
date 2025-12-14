"use client"

import { useUser } from "@/contexts/user-context"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Camera, Star, ShoppingCart, Heart, ArrowLeft } from "lucide-react"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

export default function ProductsPage() {
  const { user, getLatestScanData } = useUser()
  const router = useRouter()
  const latestScan = getLatestScanData()

  // Redirect to login if not signed in
  useEffect(() => {
    if (!user) {
      router.push('/login')
    }
  }, [user, router])

  if (!user) {
    return null
  }

  // Mock product data based on scan results
  const getRecommendedProducts = () => {
    const conditions = latestScan?.conditions || []
    const hasAcne = conditions.some(c => c.condition === 'acne')
    const hasDrySkin = conditions.some(c => c.condition === 'dry_skin')
    const hasDarkSpots = conditions.some(c => c.condition === 'dark_spots')

    const products = [
      {
        id: 1,
        name: "CeraVe Acne Foaming Cream Cleanser",
        brand: "CeraVe",
        price: 16.99,
        rating: 4.5,
        image: "/cerave-acne-cleanser.jpg",
        category: "Cleanser",
        recommended: hasAcne,
        description: "Contains benzoyl peroxide to treat acne and prevent breakouts"
      },
      {
        id: 2,
        name: "The Ordinary Niacinamide 10% + Zinc 1%",
        brand: "The Ordinary",
        price: 12.90,
        rating: 4.6,
        image: "/ordinary-niacinamide.jpg",
        category: "Serum",
        recommended: hasAcne || hasDarkSpots,
        description: "Reduces blemishes and balances oil production"
      },
      {
        id: 3,
        name: "CeraVe Moisturizing Cream",
        brand: "CeraVe",
        price: 19.99,
        rating: 4.8,
        image: "/cerave-moisturizer.jpg",
        category: "Moisturizer",
        recommended: hasDrySkin,
        description: "Rich moisturizer with ceramides and hyaluronic acid"
      },
      {
        id: 4,
        name: "Paula's Choice 10% Azelaic Acid Booster",
        brand: "Paula's Choice",
        price: 36.00,
        rating: 4.7,
        image: "/paula-choice-azelaic.jpg",
        category: "Treatment",
        recommended: hasDarkSpots,
        description: "Reduces dark spots and evens skin tone"
      },
      {
        id: 5,
        name: "The Ordinary Vitamin C Suspension 23%",
        brand: "The Ordinary",
        price: 7.20,
        rating: 4.3,
        image: "/ordinary-vitamin-c.jpg",
        category: "Serum",
        recommended: hasDarkSpots,
        description: "Brightens skin and reduces dark spots"
      },
      {
        id: 6,
        name: "Neutrogena Ultra Sheer Dry-Touch Sunscreen SPF 50",
        brand: "Neutrogena",
        price: 11.97,
        rating: 4.4,
        image: "/neutrogena-sunscreen.jpg",
        category: "Sunscreen",
        recommended: true, // Always recommended
        description: "Broad spectrum protection with dry-touch technology"
      }
    ]

    return products.filter(product => product.recommended)
  }

  const recommendedProducts = getRecommendedProducts()

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => router.push('/')}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Home
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-foreground">
                Welcome back, {user.firstName}!
              </h1>
              <p className="text-muted-foreground">
                Personalized skincare recommendations just for you
              </p>
            </div>
          </div>
          <Button
            onClick={() => router.push('/scan')}
            className="flex items-center gap-2"
          >
            <Camera className="w-4 h-4" />
            Start Face Scan
          </Button>
        </div>

        {/* Scan Status */}
        {latestScan ? (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Camera className="w-5 h-5 text-green-500" />
                Latest Scan Results
              </CardTitle>
              <CardDescription>
                Scanned on {new Date(latestScan.timestamp).toLocaleDateString()}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {latestScan.conditions.map((condition, index) => (
                  <Badge 
                    key={index} 
                    variant={condition.severity === 'high' ? 'destructive' : 'secondary'}
                  >
                    {condition.condition.replace('_', ' ')} ({Math.round(condition.confidence * 100)}%)
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card className="mb-8 border-amber-200 bg-amber-50">
            <CardHeader>
              <CardTitle className="text-amber-800">No Scan Data Yet</CardTitle>
              <CardDescription className="text-amber-700">
                Complete a face scan to get personalized product recommendations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                onClick={() => router.push('/scan')}
                className="bg-amber-600 hover:bg-amber-700"
              >
                <Camera className="w-4 h-4 mr-2" />
                Start Your First Scan
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Product Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recommendedProducts.map((product) => (
            <Card key={product.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{product.name}</CardTitle>
                    <CardDescription className="text-sm text-muted-foreground">
                      {product.brand} • {product.category}
                    </CardDescription>
                  </div>
                  <Badge variant="secondary" className="ml-2">
                    Recommended
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Product Image Placeholder */}
                <div className="w-full h-48 bg-gray-100 rounded-lg flex items-center justify-center">
                  <div className="text-center text-gray-500">
                    <div className="w-16 h-16 bg-gray-200 rounded-lg mx-auto mb-2 flex items-center justify-center">
                      <span className="text-2xl">🧴</span>
                    </div>
                    <p className="text-sm">Product Image</p>
                  </div>
                </div>

                {/* Rating */}
                <div className="flex items-center gap-2">
                  <div className="flex items-center">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-4 h-4 ${
                          i < Math.floor(product.rating)
                            ? 'text-yellow-400 fill-current'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {product.rating} ({Math.floor(Math.random() * 1000)} reviews)
                  </span>
                </div>

                {/* Description */}
                <p className="text-sm text-muted-foreground">
                  {product.description}
                </p>

                {/* Price and Actions */}
                <div className="flex items-center justify-between">
                  <div className="text-xl font-bold text-foreground">
                    ${product.price}
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      <Heart className="w-4 h-4" />
                    </Button>
                    <Button size="sm">
                      <ShoppingCart className="w-4 h-4 mr-2" />
                      Add to Cart
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Empty State */}
        {recommendedProducts.length === 0 && (
          <div className="text-center py-12">
            <Camera className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-foreground mb-2">
              No Recommendations Yet
            </h3>
            <p className="text-muted-foreground mb-6">
              Complete a face scan to get personalized product recommendations
            </p>
            <Button onClick={() => router.push('/scan')}>
              <Camera className="w-4 h-4 mr-2" />
              Start Face Scan
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
