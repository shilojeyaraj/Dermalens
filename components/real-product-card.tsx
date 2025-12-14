"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { 
  Heart, 
  ExternalLink, 
  Star, 
  ShoppingCart, 
  AlertCircle,
  CheckCircle2,
  Sparkles
} from "lucide-react"

interface RealProduct {
  name: string
  brand: string
  price: string
  originalPrice?: string
  category: string
  description: string
  rating: number
  reviewCount: number
  imageUrl: string
  productUrl: string
  source: string
  inStock: boolean
  size: string
  ingredients: string[]
  skinType: string
  keyBenefits: string[]
  discount?: string
  isNew?: boolean
  isBestSeller?: boolean
}

interface RealProductCardProps {
  product: RealProduct
  onAddToRoutine?: (product: RealProduct) => void
  onViewDetails?: (product: RealProduct) => void
}

export function RealProductCard({ product, onAddToRoutine, onViewDetails }: RealProductCardProps) {
  const [isWishlisted, setIsWishlisted] = useState(false)
  const [imageError, setImageError] = useState(false)

  const handleWishlistToggle = () => {
    setIsWishlisted(!isWishlisted)
  }

  const handleVisitProductPage = () => {
    // Open the company's product page in a new tab
    if (product.productUrl) {
      window.open(product.productUrl, '_blank', 'noopener,noreferrer')
    } else {
      // Fallback to products page if no URL available
      window.location.href = '/products'
    }
  }

  const handleViewDetails = () => {
    if (onViewDetails) {
      onViewDetails(product)
    }
  }

  const handleViewOnSite = () => {
    if (product.productUrl) {
      window.open(product.productUrl, '_blank', 'noopener,noreferrer')
    }
  }

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${
          i < Math.floor(rating)
            ? 'text-yellow-400 fill-current'
            : 'text-gray-300'
        }`}
      />
    ))
  }

  return (
    <Card className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-all duration-300 group">
      {/* Product Header - No Image */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-semibold text-lg text-gray-900 mb-1 line-clamp-2">
              {product.name}
            </h3>
            <p className="text-sm text-gray-600 mb-2">{product.brand}</p>
          </div>
          
          {/* Status Badges */}
          <div className="flex flex-col gap-1 ml-2">
            {product.isNew && (
              <Badge className="bg-green-500 text-white text-xs px-2 py-1">
                New
              </Badge>
            )}
            {product.isBestSeller && (
              <Badge className="bg-orange-500 text-white text-xs px-2 py-1">
                Best Seller
              </Badge>
            )}
            {product.discount && (
              <Badge className="bg-red-500 text-white text-xs px-2 py-1">
                {product.discount}
              </Badge>
            )}
            {!product.inStock && (
              <Badge className="bg-red-600 text-white text-xs px-2 py-1">
                Out of Stock
              </Badge>
            )}
          </div>
        </div>
      </div>

      {/* Product Details */}
      <CardContent className="p-4">

        {/* Description */}
        <p className="text-xs text-gray-600 mb-3 line-clamp-2 leading-relaxed">
          {product.description}
        </p>

        {/* Rating */}
        <div className="flex items-center mb-3">
          <div className="flex items-center mr-2">
            {renderStars(product.rating)}
          </div>
          <span className="text-xs text-gray-600">
            {(product.rating || 0).toFixed(1)} ({product.reviewCount || 0} reviews)
          </span>
        </div>

        {/* Price and Category */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-green-600">
              {product.price}
            </span>
            {product.originalPrice && (
              <span className="text-sm text-gray-500 line-through">
                {product.originalPrice}
              </span>
            )}
          </div>
          <Badge variant="outline" className="text-xs">
            {product.category}
          </Badge>
        </div>

        {/* Size */}
        <div className="text-xs text-gray-500 mb-3">
          Size: {product.size}
        </div>

        {/* Key Benefits */}
        {product.keyBenefits && product.keyBenefits.length > 0 && (
          <div className="mb-3">
            <div className="text-xs font-semibold text-gray-700 mb-1">Key Benefits:</div>
            <div className="flex flex-wrap gap-1">
              {product.keyBenefits.slice(0, 2).map((benefit, idx) => (
                <Badge key={idx} variant="secondary" className="text-xs bg-blue-100 text-blue-800">
                  {benefit}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Ingredients */}
        {product.ingredients && product.ingredients.length > 0 && (
          <div className="mb-4">
            <div className="text-xs font-semibold text-gray-700 mb-1">Key Ingredients:</div>
            <div className="flex flex-wrap gap-1">
              {product.ingredients.slice(0, 3).map((ingredient, idx) => (
                <Badge key={idx} variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">
                  {ingredient}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Skin Type */}
        <div className="mb-4">
          <div className="text-xs font-semibold text-gray-700 mb-1">Skin Type:</div>
          <Badge variant="outline" className="text-xs bg-purple-50 text-purple-700 border-purple-200">
            {product.skinType}
          </Badge>
        </div>

        {/* Source removed (redundant). We keep a single explicit "View on <source>" button below */}

        {/* Action Buttons */}
        <div className="space-y-2">
          <div className="flex gap-2">
            <Button
              onClick={handleVisitProductPage}
              className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 text-sm"
            >
              <ExternalLink className="w-4 h-4 mr-1" />
              Visit Product Page
            </Button>
          </div>
          
        </div>

        {/* Stock Status Indicator */}
        <div className="mt-2 flex items-center justify-center">
          {product.inStock ? (
            <div className="flex items-center text-green-600 text-xs">
              <CheckCircle2 className="w-3 h-3 mr-1" />
              In Stock
            </div>
          ) : (
            <div className="flex items-center text-red-600 text-xs">
              <AlertCircle className="w-3 h-3 mr-1" />
              Out of Stock
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

