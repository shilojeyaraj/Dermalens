"use client"

import { useState, useCallback } from "react"
import { ProductGrid } from "@/components/product-grid"
import { ProductFilters } from "@/components/product-filters"
import { Header } from "@/components/header"

export type Product = {
  id: string
  name: string
  brand: string
  price: number
  type: string
  image: string
  rating: number
  description: string
}

// Sample product data
const sampleProducts: Product[] = [
  {
    id: "1",
    name: "Hydrating Cleanser",
    brand: "CeraVe",
    price: 14.99,
    type: "Cleanser",
    image: "/hydrating-facial-cleanser-bottle.jpg",
    rating: 4.5,
    description: "Gentle hydrating cleanser for all skin types",
  },
  {
    id: "2",
    name: "Vitamin C Serum",
    brand: "The Ordinary",
    price: 25.99,
    type: "Serum",
    image: "/vitamin-c-serum-dropper-bottle.jpg",
    rating: 4.8,
    description: "Brightening serum with pure vitamin C",
  },
  {
    id: "3",
    name: "Niacinamide Treatment",
    brand: "Paula's Choice",
    price: 32.0,
    type: "Treatment",
    image: "/niacinamide-treatment-bottle.jpg",
    rating: 4.6,
    description: "Reduces pores and evens skin tone",
  },
  {
    id: "4",
    name: "Retinol Night Cream",
    brand: "Neutrogena",
    price: 19.99,
    type: "Moisturizer",
    image: "/retinol-night-cream-jar.jpg",
    rating: 4.3,
    description: "Anti-aging night cream with retinol",
  },
  {
    id: "5",
    name: "Hyaluronic Acid Serum",
    brand: "La Roche-Posay",
    price: 39.99,
    type: "Serum",
    image: "/hyaluronic-acid-serum-bottle.jpg",
    rating: 4.7,
    description: "Intense hydration with hyaluronic acid",
  },
  {
    id: "6",
    name: "SPF 50 Sunscreen",
    brand: "EltaMD",
    price: 37.0,
    type: "Sunscreen",
    image: "/facial-sunscreen-spf-50-tube.jpg",
    rating: 4.9,
    description: "Broad spectrum UV protection",
  },
  {
    id: "7",
    name: "Salicylic Acid Toner",
    brand: "Paula's Choice",
    price: 29.5,
    type: "Toner",
    image: "/salicylic-acid-toner-bottle.jpg",
    rating: 4.4,
    description: "Exfoliating toner for acne-prone skin",
  },
  {
    id: "8",
    name: "Gentle Moisturizer",
    brand: "CeraVe",
    price: 16.99,
    type: "Moisturizer",
    image: "/facial-moisturizer-pump-bottle.jpg",
    rating: 4.6,
    description: "Daily moisturizer with ceramides",
  },
]

export function ProductsPage() {
  const [products] = useState<Product[]>(sampleProducts)
  const [filteredProducts, setFilteredProducts] = useState<Product[]>(sampleProducts)

  const handleFilterChange = useCallback(
    (filters: {
      brands: string[]
      priceRange: [number, number]
      types: string[]
      searchQuery: string
    }) => {
      let filtered = products

      // Filter by brands
      if (filters.brands.length > 0) {
        filtered = filtered.filter((product) => filters.brands.includes(product.brand))
      }

      // Filter by price range
      filtered = filtered.filter(
        (product) => product.price >= filters.priceRange[0] && product.price <= filters.priceRange[1],
      )

      // Filter by product types
      if (filters.types.length > 0) {
        filtered = filtered.filter((product) => filters.types.includes(product.type))
      }

      // Filter by search query
      if (filters.searchQuery) {
        filtered = filtered.filter(
          (product) =>
            product.name.toLowerCase().includes(filters.searchQuery.toLowerCase()) ||
            product.brand.toLowerCase().includes(filters.searchQuery.toLowerCase()) ||
            product.description.toLowerCase().includes(filters.searchQuery.toLowerCase()),
        )
      }

      setFilteredProducts(filtered)
    },
    [products],
  )

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">Skincare Products</h1>
          <p className="text-muted-foreground">Discover personalized skincare products tailored to your skin's needs</p>
        </div>
        <div className="flex flex-col lg:flex-row gap-8">
          <aside className="lg:w-80 flex-shrink-0">
            <ProductFilters products={products} onFilterChange={handleFilterChange} />
          </aside>
          <main className="flex-1">
            <ProductGrid products={filteredProducts} />
          </main>
        </div>
      </div>
    </div>
  )
}
