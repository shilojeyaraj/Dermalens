"use client"

import { useState, useCallback, useEffect } from "react"
import { useRouter } from "next/navigation"
import { EnhancedProductGrid } from "@/components/enhanced-product-grid"
import { EnhancedProductFilters } from "@/components/enhanced-product-filters"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Search, Filter } from "lucide-react"
import type { Product } from "@/components/enhanced-product-filters"

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
    reviewCount: 1250,
    skinType: "All Skin Types",
    category: "Cleanser"
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
    reviewCount: 890,
    skinType: "All Skin Types",
    category: "Serum"
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
    reviewCount: 2100,
    skinType: "Oily",
    category: "Treatment"
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
    reviewCount: 650,
    skinType: "All Skin Types",
    category: "Moisturizer"
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
    reviewCount: 1200,
    skinType: "Dry",
    category: "Serum"
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
    reviewCount: 3400,
    skinType: "All Skin Types",
    category: "Sunscreen"
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
    reviewCount: 1800,
    skinType: "Oily",
    category: "Toner"
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
    reviewCount: 950,
    skinType: "All Skin Types",
    category: "Moisturizer"
  },
]

export default function ProductsPage() {
  const router = useRouter()
  const [products, setProducts] = useState<Product[]>(sampleProducts)
  const [filteredProducts, setFilteredProducts] = useState<Product[]>(sampleProducts)
  const [hasAnalysis, setHasAnalysis] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  
  // Filter states
  const [selectedBrands, setSelectedBrands] = useState<string[]>([])
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 150])
  const [selectedTypes, setSelectedTypes] = useState<string[]>([])

  useEffect(() => {
    // Check if there's analysis data available
    const storedAnalysis = localStorage.getItem('skinAnalysis')
    if (storedAnalysis) {
      try {
        const analysisData = JSON.parse(storedAnalysis)
        const recommendedProducts = analysisData.recommended_products || analysisData.recommendations || []
        if (recommendedProducts.length > 0) {
          // Convert recommended products to Product format
          const convertedProducts: Product[] = recommendedProducts.map((product: any, index: number) => ({
            id: product.id || `rec-${index}`,
            name: product.name || product.product_name || 'Unknown Product',
            brand: product.brand || 'Unknown Brand',
            price: typeof product.price === 'number' ? product.price : parseFloat(product.price?.replace('$', '') || '0'),
            type: product.product_type || product.category || 'Treatment',
            image: product.image || product.image_url || "https://picsum.photos/400/300?random=" + Math.random(),
            rating: product.rating || 4.0,
            description: product.recommendation_reason || product.description || 'Recommended for your skin type',
            reviewCount: product.review_count || Math.floor(Math.random() * 1000) + 100,
            skinType: product.skin_types?.[0] || 'All Skin Types',
            category: product.category || product.product_type || 'General'
          }))
          
          // Use only the converted products (no need to combine with samples)
          setProducts(convertedProducts)
          setFilteredProducts(convertedProducts)
          setHasAnalysis(true)
        }
      } catch (error) {
        console.error('Error parsing stored analysis:', error)
      }
    }

    // Listen for new analysis results
    const handleAnalysisComplete = (event: CustomEvent) => {
      const analysisData = event.detail
      if (analysisData.recommended_products && analysisData.recommended_products.length > 0) {
        const recommendedProducts: Product[] = analysisData.recommended_products.map((product: any, index: number) => ({
          id: `rec-${index}`,
          name: product.name,
          brand: product.brand,
          price: parseFloat(product.price?.replace('$', '') || '0'),
          type: product.category || 'Treatment',
          image: product.image || "https://picsum.photos/400/300?random=" + Math.random(),
          rating: product.rating || 4.0,
          description: product.reason || product.description || 'Recommended for your skin type'
        }))
        
        const combinedProducts = [...recommendedProducts, ...sampleProducts.filter(sp => 
          !recommendedProducts.some(rp => rp.name === sp.name)
        )]
        
        setProducts(combinedProducts)
        setFilteredProducts(combinedProducts)
        setHasAnalysis(true)
      }
    }

    window.addEventListener('skinAnalysisComplete', handleAnalysisComplete as EventListener)
    
    return () => {
      window.removeEventListener('skinAnalysisComplete', handleAnalysisComplete as EventListener)
    }
  }, [])

  // Apply filters to products
  useEffect(() => {
    let filtered = [...products]
    
    // Apply brand filter
    if (selectedBrands.length > 0) {
      filtered = filtered.filter(product => 
        selectedBrands.includes(product.brand)
      )
    }
    
    // Apply price filter
    filtered = filtered.filter(product => {
      const price = parseFloat(product.price.toString())
      return price >= priceRange[0] && price <= priceRange[1]
    })
    
    // Apply type filter
    if (selectedTypes.length > 0) {
      filtered = filtered.filter(product => 
        selectedTypes.includes(product.type)
      )
    }
    
    setFilteredProducts(filtered)
  }, [selectedBrands, priceRange, selectedTypes, products])

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

  const handleProductSelect = (product: Product) => {
    console.log('Selected product:', product)
    // Handle product selection - could open a modal, add to cart, etc.
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-green-50 to-green-100">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => router.back()}
              className="hover:bg-gray-100"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Skincare Products</h1>
              <p className="text-sm text-gray-600">Discover personalized skincare products</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
              className="lg:hidden"
            >
              <Filter className="w-4 h-4 mr-2" />
              Filters
            </Button>
            {hasAnalysis && (
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                <Search className="w-3 h-3 mr-1" />
                Personalized
              </Badge>
            )}
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          <aside className={`lg:w-80 flex-shrink-0 ${showFilters ? 'block' : 'hidden lg:block'}`}>
            <EnhancedProductFilters 
              selectedBrands={selectedBrands}
              onBrandsChange={setSelectedBrands}
              priceRange={priceRange}
              onPriceRangeChange={setPriceRange}
              selectedTypes={selectedTypes}
              onTypesChange={setSelectedTypes}
            />
          </aside>

          {/* Main Content */}
          <main className="flex-1">
            <div className="mb-6">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">
                  {filteredProducts.length} products found
                </h2>
                {hasAnalysis && (
                  <Badge variant="outline" className="text-green-700 border-green-200">
                    Personalized recommendations included
                  </Badge>
                )}
              </div>
            </div>
            
            <EnhancedProductGrid products={filteredProducts} onProductSelect={handleProductSelect} />
          </main>
        </div>
      </div>
    </div>
  )
}
