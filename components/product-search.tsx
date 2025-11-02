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
  selectedBrands?: string[]
  priceRange?: [number, number]
  onFiltersApplied?: () => void
  refreshTrigger?: number
}

export function ProductSearch({ onProductSelect, initialQuery = "", activeFilter = 'all', recommendedProducts = [], selectedBrands = [], priceRange = [0, 150], onFiltersApplied, refreshTrigger }: ProductSearchProps) {
  const [searchQuery, setSearchQuery] = useState(initialQuery)
  const [products, setProducts] = useState<Product[]>([])
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showFilters, setShowFilters] = useState(false)
  
  // Filter states
  const [selectedCategory, setSelectedCategory] = useState<string>("")
  const [internalSelectedBrands, setInternalSelectedBrands] = useState<string[]>(selectedBrands)
  const [minPrice, setMinPrice] = useState<string>("")
  const [maxPrice, setMaxPrice] = useState<string>("")
  const [selectedSkinType, setSelectedSkinType] = useState<string>("")
  const [minRating, setMinRating] = useState<string>("")
  const [sort, setSort] = useState<string>("rating_desc")
  const [page, setPage] = useState<number>(1)

  // Sync props with internal state (for brand and price filters from dashboard)
  useEffect(() => {
    if (selectedBrands.length > 0 || selectedBrands.length === 0) {
      setInternalSelectedBrands(selectedBrands)
    }
  }, [selectedBrands, priceRange])

  // Use priceRange prop when available, otherwise use local state
  const effectivePriceRange = priceRange[0] !== 0 || priceRange[1] !== 150 ? priceRange : [
    minPrice ? parseFloat(minPrice) : 0,
    maxPrice ? parseFloat(maxPrice) : 150
  ]

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

  // Initialize filteredProducts when products change
  useEffect(() => {
    setFilteredProducts(products)
  }, [products])

  // Auto-search when filters change or when products change
  useEffect(() => {
    if (products.length > 0) {
      applyFiltersToProducts()
    }
  }, [internalSelectedBrands, priceRange, activeFilter, selectedCategory, selectedSkinType, minRating, sort, products])

  const applyFiltersToProducts = () => {
    // Determine source products based on activeFilter
    let sourceProducts: Product[] = []
    
    if (activeFilter === 'recommended' && recommendedProducts.length > 0) {
      // Use recommended products as source
      sourceProducts = recommendedProducts.map((rec: any) => ({
        name: rec.name || rec.product_name || "Unknown Product",
        brand: rec.brand || "Unknown Brand",
        price: rec.price || "$0.00",
        category: rec.category || rec.product_type || "Unknown",
        description: rec.reason || rec.description || "",
        rating: rec.rating || 4.0,
        reviewCount: rec.review_count || 0,
        imageUrl: rec.image_url || rec.imageUrl || "/skincarelogo.jpeg",
        productUrl: rec.url || rec.product_url || "",
        source: "recommended",
        inStock: true,
        size: rec.size || "Standard",
        ingredients: rec.key_ingredients || rec.ingredients || [],
        skinType: Array.isArray(rec.skin_types) ? rec.skin_types.join(", ") : (rec.skin_types || "All Skin Types"),
        keyBenefits: rec.key_benefits || [rec.reason].filter(Boolean)
      }))
    } else {
      // Use regular products from API
      sourceProducts = [...products]
    }
    
    let filtered = [...sourceProducts]
    
    // Apply brand filter
    if (internalSelectedBrands.length > 0) {
      filtered = filtered.filter(product => 
        internalSelectedBrands.some(brand => 
          product.brand.toLowerCase().includes(brand.toLowerCase())
        )
      )
    }
    
    // Apply price filter using effective price range
    const [minPriceValue, maxPriceValue] = effectivePriceRange
    filtered = filtered.filter(product => {
      const priceStr = product.price.toString().replace('$', '').trim()
      const price = parseFloat(priceStr) || 0
      return price >= minPriceValue && price <= maxPriceValue
    })
    
    // Apply category filter
    if (selectedCategory) {
      filtered = filtered.filter(product => 
        product.category === selectedCategory
      )
    }
    
    // Apply skin type filter
    if (selectedSkinType) {
      filtered = filtered.filter(product => 
        product.skinType === selectedSkinType || product.skinType === "All Skin Types"
      )
    }
    
    // Apply rating filter
    if (minRating) {
      const minRatingNum = parseFloat(minRating)
      filtered = filtered.filter(product => 
        product.rating >= minRatingNum
      )
    }
    
    // Apply sorting
    if (sort === "rating_desc") {
      filtered.sort((a, b) => b.rating - a.rating)
    } else if (sort === "price_asc") {
      filtered.sort((a, b) => {
        const priceA = parseFloat(a.price.toString().replace('$', '').trim()) || 0
        const priceB = parseFloat(b.price.toString().replace('$', '').trim()) || 0
        return priceA - priceB
      })
    } else if (sort === "price_desc") {
      filtered.sort((a, b) => {
        const priceA = parseFloat(a.price.toString().replace('$', '').trim()) || 0
        const priceB = parseFloat(b.price.toString().replace('$', '').trim()) || 0
        return priceB - priceA
      })
    } else if (sort === "reviews_desc") {
      filtered.sort((a, b) => b.reviewCount - a.reviewCount)
    }
    
    // Update filtered products state
    setFilteredProducts(filtered)
  }

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
      if (internalSelectedBrands.length) params.append("brands", internalSelectedBrands.join(","))
      // Use effective price range for API call
      const [apiMinPrice, apiMaxPrice] = effectivePriceRange
      if (apiMinPrice > 0) params.append("min_price", apiMinPrice.toString())
      if (apiMaxPrice < 150) params.append("max_price", apiMaxPrice.toString())
      if (selectedSkinType) params.append("skin_type", selectedSkinType)
      if (minRating) params.append("rating_min", minRating)
      if (sort) params.append("sort", sort)
      if (page) params.append("page", String(page))

      const token = localStorage.getItem('token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/products/search?${params}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined
      })
      const data = await response.json()

      if (data.success) {
        setProducts(data.products)
        getFilteredProducts(data.products)
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
      
      // Build query params with filters
      const params = new URLSearchParams({
        limit: "50"
      })
      
      // Add brand filters if any selected
      if (internalSelectedBrands.length > 0) {
        params.append("brands", internalSelectedBrands.join(","))
      }
      
      // Add price range filters
      const [apiMinPrice, apiMaxPrice] = effectivePriceRange
      if (apiMinPrice > 0) params.append("min_price", apiMinPrice.toString())
      if (apiMaxPrice < 150) params.append("max_price", apiMaxPrice.toString())
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/products/trending?${params}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined
      })
      const data = await response.json()

      if (data.success) {
        setProducts(data.trending_products || [])
        setSearchQuery("")
        // Apply filters after loading
        applyFiltersToProducts()
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
    setInternalSelectedBrands([])
    setMinPrice("")
    setMaxPrice("")
    setSelectedSkinType("")
    setMinRating("")
    setSort("rating_desc")
    setPage(1)
  }

  // Filter products based on activeFilter
  const getFilteredProducts = (productsList: Product[]): Product[] => {
    if (activeFilter === 'recommended' && recommendedProducts.length > 0) {
      // Convert recommended products to Product format
      const recProducts = recommendedProducts.map((rec: any) => ({
        name: rec.name || rec.product_name || "Unknown Product",
        brand: rec.brand || "Unknown Brand",
        price: rec.price || "$0.00",
        category: rec.category || rec.product_type || "Unknown",
        description: rec.reason || rec.description || "",
        rating: rec.rating || 4.0,
        reviewCount: rec.review_count || 0,
        imageUrl: rec.image_url || rec.imageUrl || "/skincarelogo.jpeg",
        productUrl: rec.url || rec.product_url || "",
        source: "recommended",
        inStock: true,
        size: rec.size || "Standard",
        ingredients: rec.key_ingredients || rec.ingredients || [],
        skinType: Array.isArray(rec.skin_types) ? rec.skin_types.join(", ") : (rec.skin_types || "All Skin Types"),
        keyBenefits: rec.key_benefits || [rec.reason].filter(Boolean)
      }))
      
      // Apply filters to recommended products too
      let filtered = [...recProducts]
      if (internalSelectedBrands.length > 0) {
        filtered = filtered.filter(product => 
          internalSelectedBrands.some(brand => 
            product.brand.toLowerCase().includes(brand.toLowerCase())
          )
        )
      }
      const [minPriceValue, maxPriceValue] = effectivePriceRange
      filtered = filtered.filter(product => {
        const priceStr = product.price.toString().replace('$', '').trim()
        const price = parseFloat(priceStr) || 0
        return price >= minPriceValue && price <= maxPriceValue
      })
      return filtered
    } else {
      // Show all products (already filtered by applyFiltersToProducts)
      return productsList
    }
  }

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
      // Always load trending products on mount if no query
      loadTrendingProducts()
    }
  }, [initialQuery])

  // Update filtered products when activeFilter or recommendedProducts change
  useEffect(() => {
    if (activeFilter === 'recommended' && recommendedProducts.length > 0) {
      applyFiltersToProducts()
    } else if (products.length > 0) {
      applyFiltersToProducts()
    }
  }, [activeFilter, recommendedProducts])

  // Refresh products when filters are applied (via refreshTrigger)
  useEffect(() => {
    if (refreshTrigger !== undefined && refreshTrigger > 0) {
      console.log('🔄 [PRODUCT SEARCH] Filters applied, refreshing products with:', {
        selectedBrands: internalSelectedBrands,
        priceRange: effectivePriceRange,
        activeFilter
      })
      // Sync internal brands with prop brands before refreshing
      if (selectedBrands.length !== internalSelectedBrands.length || 
          !selectedBrands.every(b => internalSelectedBrands.includes(b))) {
        setInternalSelectedBrands(selectedBrands)
      }
      // If activeFilter is 'all', reload trending products with filters
      if (activeFilter === 'all') {
        loadTrendingProducts()
      } else {
        // If 'recommended', just apply filters to existing recommended products
        applyFiltersToProducts()
      }
      if (onFiltersApplied) {
        onFiltersApplied()
      }
    }
  }, [refreshTrigger, selectedBrands, priceRange])

  // Debounced search effect
  useEffect(() => {
    if (searchQuery.trim()) {
      const timeoutId = setTimeout(() => {
        searchProducts()
      }, 500)
      return () => clearTimeout(timeoutId)
    }
  }, [searchQuery])

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
                        checked={internalSelectedBrands.includes(brand)}
                        onChange={(e) => {
                          setPage(1)
                          if (e.target.checked) setInternalSelectedBrands([...internalSelectedBrands, brand])
                          else setInternalSelectedBrands(internalSelectedBrands.filter(b => b !== brand))
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
            {filteredProducts.map((product: Product, index: number) => (
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

