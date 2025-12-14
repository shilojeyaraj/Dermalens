"use client"

import { useState } from "react"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Heart, Star } from "lucide-react"
import type { Product } from "@/components/products-page"
// Simple cn function without external dependencies
function cn(...classes: (string | undefined | null | boolean)[]): string {
  return classes.filter(Boolean).join(' ')
}

type ProductCardProps = {
  product: Product
}

export function ProductCard({ product }: ProductCardProps) {
  const [isFavorite, setIsFavorite] = useState(false)

  return (
    <Card className="group overflow-hidden hover:shadow-lg transition-shadow duration-300">
      <div className="relative aspect-square overflow-hidden bg-muted">
        <img
          src={product.image || "/placeholder.svg"}
          alt={product.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
      </div>
      <CardContent className="p-4">
        <div className="mb-1">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">{product.brand}</p>
        </div>
        <h3 className="font-semibold text-base mb-2 line-clamp-2 text-balance">{product.name}</h3>
        <p className="text-sm text-muted-foreground mb-3 line-clamp-2">{product.description}</p>
        <div className="flex items-center gap-1 mb-3">
          <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
          <span className="text-sm font-medium">{product.rating}</span>
          <span className="text-xs text-muted-foreground ml-1">({Math.floor(Math.random() * 500) + 100} reviews)</span>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-primary">${(product.price || 0).toFixed(2)}</span>
          <span className="text-xs text-muted-foreground">{product.type}</span>
        </div>
      </CardContent>
      <CardFooter className="p-4 pt-0">
        <Button 
          onClick={() => window.location.href = '/products'}
          className="w-full bg-primary hover:bg-primary/90 text-primary-foreground"
        >
          Browse Products
        </Button>
      </CardFooter>
    </Card>
  )
}
