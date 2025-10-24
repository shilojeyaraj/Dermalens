"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { RealProductCard } from "./real-product-card"
import { 
  Search, 
  Filter, 
  SlidersHorizontal, 
  Loader2,
  AlertCircle,
  TrendingUp,
  Star
} from "lucide-react"

interface Product {
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

interface ProductSearchProps {
  onProductSelect?: (product: Product) => void
  initialQuery?: string
  activeFilter?: 'all' | 'recommended'
  recommendedProducts?: any[]
}

export function ProductSearch({ onProductSelect, initialQuery = "", activeFilter = 'all', recommendedProducts = [] }: ProductSearchProps) {
  const [searchQuery, setSearchQuery] = useState(initialQuery)
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showFilters, setShowFilters] = useState(false)
  
  // Filter states
  const [selectedCategory, setSelectedCategory] = useState<string>("")
  const [selectedBrands, setSelectedBrands] = useState<string[]>([])
  const [minPrice, setMinPrice] = useState<string>("")
  const [maxPrice, setMaxPrice] = useState<string>("")
  const [selectedSkinType, setSelectedSkinType] = useState<string>("")
  const [minRating, setMinRating] = useState<string>("")
  const [sort, setSort] = useState<string>("rating_desc")
  const [page, setPage] = useState<number>(1)

  const categories = [
    "Cleanser", "Moisturizer", "Serum", "Sunscreen", 
    "Toner", "Exfoliant", "Eye Cream", "Face Mask", "Treatment"
  ]

  const brands = [
    "CeraVe", "The Ordinary", "Paula's Choice", "La Roche-Posay",
    "Neutrogena", "EltaMD", "Olay", "Aveeno", "Cetaphil",
    "Eucerin", "Vichy", "Bioderma", "Clinique", "Kiehl's",
    "Tatcha", "First Aid Beauty", "Drunk Elephant", "The Inkey List",
    "SkinCeuticals", "Murad", "Youth To The People", "Glossier",
    "Pixi", "COSRX", "Innisfree", "Laneige", "Curel"
  ]

  const skinTypes = [
    "Normal", "Dry", "Oily", "Combination", "Sensitive", "All Skin Types"
  ]

  const searchProducts = async () => {
    if (!searchQuery.trim()) return

    setLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams({
        q: searchQuery,
        limit: "20"
      })

      if (selectedCategory) params.append("category", selectedCategory)
      if (selectedBrands.length) params.append("brands", selectedBrands.join(","))
      if (minPrice) params.append("min_price", minPrice)
      if (maxPrice) params.append("max_price", maxPrice)
      if (selectedSkinType) params.append("skin_type", selectedSkinType)
      if (minRating) params.append("rating_min", minRating)
      if (sort) params.append("sort", sort)
      if (page) params.append("page", String(page))

      const token = localStorage.getItem('token')
      const response = await fetch(`http://localhost:8000/products/search?${params}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined
      })
      const data = await response.json()

      if (data.success) {
        setProducts(data.products)
      } else {
        setError(data.error || "Failed to search products")
      }
    } catch (err) {
      setError("Network error. Please try again.")
      console.error("Search error:", err)
    } finally {
      setLoading(false)
    }
  }

  const loadTrendingProducts = async () => {
    setLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem('token')
      const response = await fetch("http://localhost:8000/products/trending", {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined
      })
      const data = await response.json()

      if (data.success) {
        setProducts(data.trending_products)
        setSearchQuery("")
      } else {
        setError(data.error || "Failed to load trending products")
      }
    } catch (err) {
      setError("Network error. Please try again.")
      console.error("Trending products error:", err)
    } finally {
      setLoading(false)
    }
  }

  const clearFilters = () => {
    setSelectedCategory("")
    setSelectedBrands([])
    setMinPrice("")
    setMaxPrice("")
    setSelectedSkinType("")
    setMinRating("")
    setSort("rating_desc")
    setPage(1)
  }

  // Filter products based on activeFilter
  const getFilteredProducts = () => {
    if (activeFilter === 'recommended') {
      // Convert recommended products to Product format
      return recommendedProducts.map((rec: any) => ({
        name: rec.name,
        brand: rec.brand,
        price: rec.price,
        category: rec.category,
        description: rec.reason,
        rating: rec.rating || 4.0,
        reviewCount: 0,
        imageUrl: "",
        productUrl: rec.url || "",
        source: "recommended",
        inStock: true,
        size: "Standard",
        ingredients: rec.key_ingredients || [],
        skinType: rec.skin_types?.join(", ") || "All Skin Types",
        keyBenefits: [rec.reason]
      }))
    } else {
      // Show all products
      return products
    }
  }

  const filteredProducts = getFilteredProducts()

  const handleProductSelect = (product: Product) => {
    if (onProductSelect) {
      onProductSelect(product)
    }
  }

  const handleViewProductOnSite = (product: Product) => {
    if (product.productUrl) {
      window.open(product.productUrl, '_blank', 'noopener,noreferrer')
    }
  }

  useEffect(() => {
    if (initialQuery) {
      setSearchQuery(initialQuery)
      searchProducts()
    } else {
      loadTrendingProducts()
    }
  }, [initialQuery])

  return (
    <div className="space-y-6">
      {/* Search Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="w-5 h-5" />
            Search Skincare Products
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-4">
            <Input
              placeholder="Search for products, brands, or ingredients..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && searchProducts()}
              className="flex-1"
            />
            <Button onClick={searchProducts} disabled={loading || !searchQuery.trim()}>
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            </Button>
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
            >
              <SlidersHorizontal className="w-4 h-4" />
            </Button>
          </div>

          {/* Quick Actions */}
          <div className="flex gap-2 flex-wrap">
            <Button
              variant="outline"
              size="sm"
              onClick={loadTrendingProducts}
              disabled={loading}
            >
              <TrendingUp className="w-4 h-4 mr-1" />
              Trending
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSearchQuery("best skincare 2024")}
            >
              <Star className="w-4 h-4 mr-1" />
              Best of 2024
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSearchQuery("dermatologist recommended")}
            >
              <Star className="w-4 h-4 mr-1" />
              Expert Picks
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Filters */}
      {showFilters && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Filter className="w-5 h-5" />
                Filters
              </span>
              <Button variant="outline" size="sm" onClick={clearFilters}>
                Clear All
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Category Filter */}
              <div>
                <label className="text-sm font-medium mb-2 block">Category</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="">All Categories</option>
                  {categories.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </select>
              </div>

              {/* Brand Filter (multi-select) */}
              <div>
                <label className="text-sm font-medium mb-2 block">Brand</label>
                <div className="max-h-40 overflow-auto border rounded-md p-2">
                  {brands.map((brand) => (
                    <label key={brand} className="flex items-center gap-2 text-sm py-1">
                      <input
                        type="checkbox"
                        checked={selectedBrands.includes(brand)}
                        onChange={(e) => {
                          setPage(1)
                          if (e.target.checked) setSelectedBrands([...selectedBrands, brand])
                          else setSelectedBrands(selectedBrands.filter(b => b !== brand))
                        }}
                      />
                      {brand}
                    </label>
                  ))}
                </div>
              </div>

              {/* Skin Type Filter */}
              <div>
                <label className="text-sm font-medium mb-2 block">Skin Type</label>
                <select
                  value={selectedSkinType}
                  onChange={(e) => setSelectedSkinType(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="">All Skin Types</option>
                  {skinTypes.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>

              {/* Price Range */}
              <div>
                <label className="text-sm font-medium mb-2 block">Min Price ($)</label>
                <Input
                  type="number"
                  placeholder="0"
                  value={minPrice}
                  onChange={(e) => setMinPrice(e.target.value)}
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Max Price ($)</label>
                <Input
                  type="number"
                  placeholder="100"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(e.target.value)}
                />
              </div>

              {/* Rating Filter + Sorting */}
              <div>
                <label className="text-sm font-medium mb-2 block">Min Rating</label>
                <select
                  value={minRating}
                  onChange={(e) => setMinRating(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="">Any Rating</option>
                  <option value="4.5">4.5+ Stars</option>
                  <option value="4.0">4.0+ Stars</option>
                  <option value="3.5">3.5+ Stars</option>
                  <option value="3.0">3.0+ Stars</option>
                </select>
                <label className="text-sm font-medium mt-3 mb-2 block">Sort By</label>
                <select
                  value={sort}
                  onChange={(e) => { setSort(e.target.value); setPage(1) }}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="rating_desc">Rating (high → low)</option>
                  <option value="price_asc">Price (low → high)</option>
                  <option value="price_desc">Price (high → low)</option>
                  <option value="reviews_desc">Reviews (most → least)</option>
                </select>
              </div>
            </div>

            <div className="mt-4">
              <Button onClick={searchProducts} disabled={loading || !searchQuery.trim()}>
                Apply Filters
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="w-5 h-5" />
              <span>{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {loading && (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-8 h-8 animate-spin text-green-600" />
          <span className="ml-2 text-gray-600">Searching products...</span>
        </div>
      )}

      {!loading && !error && filteredProducts.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">
              {activeFilter === 'recommended' ? 'Recommended Products' :
               searchQuery ? `Results for "${searchQuery}"` : "Trending Products"}
            </h3>
            <Badge variant="outline">
              {filteredProducts.length} products found
            </Badge>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredProducts.map((product, index) => (
              <RealProductCard
                key={`${product.name}-${index}`}
                product={product}
                onAddToRoutine={handleProductSelect}
                onViewDetails={handleProductSelect}
              />
            ))}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-center gap-2 mt-6">
            <Button variant="outline" disabled={page <= 1} onClick={() => { setPage(page - 1); searchProducts() }}>Prev</Button>
            <span className="text-sm text-gray-600">Page {page}</span>
            <Button variant="outline" onClick={() => { setPage(page + 1); searchProducts() }}>Next</Button>
          </div>
        </div>
      )}

      {!loading && !error && products.length === 0 && searchQuery && (
        <Card>
          <CardContent className="pt-6 text-center">
            <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-600 mb-2">
              No products found
            </h3>
            <p className="text-gray-500 mb-4">
              Try adjusting your search terms or filters
            </p>
            <Button onClick={clearFilters} variant="outline">
              Clear Filters
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

