"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ProductSearch } from "@/components/product-search"
import { Header } from "@/components/header"
import { Loader2, TrendingUp, AlertCircle, CheckCircle2, Sparkles, ArrowRight, Repeat2, ShoppingCart } from "lucide-react"

interface SkinAnalysisResult {
  success: boolean
  analysis_type: string
  detected_conditions: string[]
  recommended_products: any[]
  skincare_routine: any
  ai_report: string
  skin_health_score: number
  analysis_timestamp: string
  analysis_notes?: {
    image_analysis?: string
    image_analysis_contribution?: string
    profile_enhancement?: string
    recommendation_basis?: string
  }
}

export default function DashboardPage() {
  const router = useRouter()
  const [analysis, setAnalysis] = useState<SkinAnalysisResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeFilter, setActiveFilter] = useState<'all' | 'recommended'>('all')
  const [selectedBrands, setSelectedBrands] = useState<string[]>([])
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 150])
  const [searchQuery, setSearchQuery] = useState("")
  const [filtersApplied, setFiltersApplied] = useState(0)

  useEffect(() => {
    // Load analysis from localStorage
    const storedAnalysis = localStorage.getItem('skinAnalysis')
    console.log('🔍 [DASHBOARD] Loading analysis from localStorage:', storedAnalysis)
    
    if (storedAnalysis) {
      try {
        const parsedAnalysis = JSON.parse(storedAnalysis)
        console.log('🔍 [DASHBOARD] Parsed analysis data:', parsedAnalysis)
        
        // Normalize the analysis data structure - handle both face scan and profile-based data
        let normalizedAnalysis;
        
        if (parsedAnalysis.multi_angle_analysis && parsedAnalysis.results && parsedAnalysis.results.length > 0) {
          // Face scan analysis data structure
          const firstResult = parsedAnalysis.results[0];
          const analysis = firstResult.analysis;
          
          normalizedAnalysis = {
            success: parsedAnalysis.success || true,
            analysis_type: "multi_angle_scan",
            detected_conditions: analysis?.detected_conditions || ["general_care"],
            recommended_products: parsedAnalysis.recommended_products || [],
            skincare_routine: parsedAnalysis.skincare_routine || { morning_routine: [], evening_routine: [] },
            ai_report: parsedAnalysis.ai_report || "Based on your face scan analysis, here are personalized recommendations for your skin.",
            skin_health_score: typeof analysis?.skin_health_score === 'number' ? analysis.skin_health_score : 0.7,
            analysis_timestamp: parsedAnalysis.analysis_timestamp || new Date().toISOString(),
            analysis_notes: parsedAnalysis.analysis_notes || {
              image_analysis_contribution: "Multi-angle face scan analysis",
              profile_enhancement: "Recommendations based on your face scan results",
              recommendation_basis: "Personalized suggestions based on your skin analysis"
            }
          };
        } else {
          // Profile-based or other analysis data structure
          normalizedAnalysis = {
            success: parsedAnalysis.success || true,
            analysis_type: parsedAnalysis.analysis_type || "profile_based",
            detected_conditions: parsedAnalysis.detected_conditions || parsedAnalysis.needs_analysis?.detected_conditions || ["general_care"],
            recommended_products: parsedAnalysis.recommended_products || parsedAnalysis.recommendations || [],
            skincare_routine: parsedAnalysis.skincare_routine || { morning_routine: [], evening_routine: [] },
            ai_report: parsedAnalysis.ai_report || "Based on your profile, here are personalized recommendations for your skin type and concerns.",
            skin_health_score: typeof parsedAnalysis.skin_health_score === 'number' ? parsedAnalysis.skin_health_score : 
                              (typeof parsedAnalysis.needs_analysis?.skin_health_score === 'number' ? parsedAnalysis.needs_analysis.skin_health_score : 0.7),
            analysis_timestamp: parsedAnalysis.analysis_timestamp || new Date().toISOString(),
            analysis_notes: parsedAnalysis.analysis_notes || {
              image_analysis_contribution: "Profile-based analysis",
              profile_enhancement: "Recommendations based on your skin profile",
              recommendation_basis: "Personalized suggestions for your skin type and concerns"
            }
          };
        }
        
        console.log('🔍 [DASHBOARD] Normalized analysis:', normalizedAnalysis)
        console.log('🔍 [DASHBOARD] Detected conditions:', normalizedAnalysis.detected_conditions)
        console.log('🔍 [DASHBOARD] Skin health score:', normalizedAnalysis.skin_health_score)
        console.log('🔍 [DASHBOARD] AI report:', normalizedAnalysis.ai_report)
        setAnalysis(normalizedAnalysis)
        setError(null)
      } catch (err) {
        console.error('🔍 [DASHBOARD] Failed to parse analysis:', err)
        setError("Failed to load analysis results")
      }
    } else {
      console.log('🔍 [DASHBOARD] No analysis found in localStorage, generating profile-based recommendations')
      // Generate profile-based recommendations for users who skipped face scan
      const generateProfileRecommendations = async () => {
        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://dermalens-backend-941238576063.us-central1.run.app'}/generate-profile-recommendations`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          })
          
          if (response.ok) {
            const profileData = await response.json()
            console.log('🔍 [DASHBOARD] Profile recommendations received:', profileData)
            
            // Store the profile-based analysis in localStorage
            localStorage.setItem('skinAnalysis', JSON.stringify(profileData))
            
            // Normalize the profile data structure
            const normalizedAnalysis = {
              success: profileData.success || true,
              analysis_type: "profile_based",
              detected_conditions: profileData.needs_analysis?.detected_conditions || ["general_care"],
              recommended_products: profileData.recommendations || [],
              skincare_routine: profileData.skincare_routine || { morning_routine: [], evening_routine: [] },
              ai_report: "Based on your profile, here are personalized recommendations for your skin type and concerns.",
              skin_health_score: profileData.needs_analysis?.skin_health_score || 0.7,
              analysis_timestamp: profileData.timestamp || new Date().toISOString(),
              analysis_notes: {
                image_analysis_contribution: "Profile-based analysis",
                profile_enhancement: "Recommendations based on your skin profile",
                recommendation_basis: "Personalized suggestions for your skin type and concerns"
              }
            }
            
            console.log('🔍 [DASHBOARD] Normalized profile analysis:', normalizedAnalysis)
            setAnalysis(normalizedAnalysis)
            setError(null)
          } else {
            console.error('🔍 [DASHBOARD] Failed to get profile recommendations:', response.status)
            setError("Failed to generate profile-based recommendations. Please try again.")
          }
        } catch (err) {
          console.error('🔍 [DASHBOARD] Error generating profile recommendations:', err)
          setError("Failed to generate profile-based recommendations. Please try again.")
        }
      }
      generateProfileRecommendations()
    }
    setLoading(false)
  }, [])


  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-white via-green-50 to-green-100 flex items-center justify-center p-4">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-green-600 mx-auto mb-4" />
          <p className="text-lg font-semibold text-gray-700">Loading your analysis...</p>
        </div>
      </div>
    )
  }

  if (error || !analysis) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-white via-green-50 to-green-100 p-4">
        <div className="max-w-4xl mx-auto py-8">
          <Card className="bg-red-50 border-2 border-red-200">
            <CardContent className="pt-6">
              <div className="flex items-start gap-4">
                <AlertCircle className="w-8 h-8 text-red-600 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-bold text-red-900 mb-2">{error}</h3>
                  <Button onClick={() => router.push('/scan')} className="mt-4 bg-green-600 hover:bg-green-700 text-white">
                    Start New Scan
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      <Header />
      {/* Top Navigation Bar */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Dermalens AI</h1>
              <p className="text-sm text-gray-500">Personalized skincare recommendations</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <Button onClick={() => router.push('/scan')} className="bg-green-600 hover:bg-green-700 text-white">
              Face Scan
            </Button>
            <Button onClick={() => router.push('/products')} variant="outline" className="flex items-center gap-2">
              <ShoppingCart className="w-4 h-4" />
              Browse Products
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Main Heading with View Analysis Button */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Skincare Products</h1>
            <p className="text-gray-600">Discover personalized skincare products tailored to your skin's needs</p>
          </div>
          
          <Button 
            onClick={() => {
              // Toggle analysis details visibility
              const analysisDetails = document.getElementById('analysis-details');
              if (analysisDetails) {
                analysisDetails.classList.toggle('hidden');
              }
            }}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-2"
          >
            View Analysis
          </Button>
        </div>

        {/* Hidden Analysis Details */}
        <div id="analysis-details" className="hidden mb-8">
          <div className="grid md:grid-cols-3 gap-4 mb-6">
            <Card className="bg-gradient-to-br from-green-50 to-white border-2 border-green-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-green-700">Skin Health Score</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="text-4xl font-bold text-green-600">
                    {Math.round(((analysis.skin_health_score ?? 0) * 100) || 0)}
                  </div>
                  <div className="text-right">
                    <TrendingUp className="w-8 h-8 text-green-500 mb-1" />
                    <p className="text-xs text-gray-600">/100</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-blue-50 to-white border-2 border-blue-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-blue-700">Conditions Detected</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">
                  {(analysis.detected_conditions?.length ?? 0)}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-50 to-white border-2 border-purple-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-purple-700">Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-purple-600">
                  {(Array.isArray(analysis.recommended_products) ? analysis.recommended_products.length : 0)}
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid lg:grid-cols-3 gap-6 mb-6">
            {/* Detected Conditions */}
            <Card className="bg-white border-2 border-green-100 lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-orange-500" />
                  Detected Conditions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 flex flex-wrap gap-2">
                  {(analysis.detected_conditions ?? []).map((condition) => (
                    <Badge 
                      key={condition} 
                      className="bg-orange-100 text-orange-800 border border-orange-300 px-3 py-1 font-semibold"
                    >
                      {condition.replace(/_/g, ' ')}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* AI Report */}
            <Card className="bg-white border-2 border-green-100 lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-yellow-500" />
                  AI-Powered Analysis
                </CardTitle>
                <CardDescription>Generated by Gemini AI</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm max-w-none">
                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {analysis.ai_report || analysis.analysis_notes?.image_analysis_contribution || 
                     analysis.analysis_notes?.profile_enhancement || 
                     "Based on your face scan analysis, here are personalized recommendations for your skin."}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Skincare Routine Section */}
        {analysis.skincare_routine && (
          <div className="mb-8">
            <Card className="bg-gradient-to-br from-green-50 to-blue-50 border-2 border-green-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-2xl font-bold text-green-800">
                  <Repeat2 className="w-6 h-6 text-green-600" />
                  Your Personalized Skincare Routine
                </CardTitle>
                <p className="text-green-700">Daily routine tailored to your skin needs</p>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Morning Routine */}
                  <div className="bg-white rounded-lg p-4 border border-green-200">
                    <h4 className="font-bold text-green-800 mb-3 flex items-center gap-2">
                      <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                      Morning Routine
                    </h4>
                    {analysis.skincare_routine.morning_routine && analysis.skincare_routine.morning_routine.length > 0 ? (
                      <div className="space-y-3 max-h-96 overflow-y-auto">
                        {analysis.skincare_routine.morning_routine.map((step: any, index: number) => (
                          <div key={index} className="border-l-4 border-green-300 pl-4 py-2">
                            <div className="font-semibold text-gray-900">{step.name}</div>
                            {step.product && (
                              <div className="text-sm text-gray-600 mb-1">
                                <strong>Product:</strong> {step.product}
                                {step.brand && <span> by {step.brand}</span>}
                              </div>
                            )}
                            {step.instructions && (
                              <div className="text-sm text-gray-700">{step.instructions}</div>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-gray-600 mb-4">No morning routine generated yet</p>
                        <Button onClick={() => router.push('/scan')} className="bg-green-600 hover:bg-green-700 text-white">
                          Start Analysis
                        </Button>
                      </div>
                    )}
                  </div>

                  {/* Evening Routine */}
                  <div className="bg-white rounded-lg p-4 border border-green-200">
                    <h4 className="font-bold text-green-800 mb-3 flex items-center gap-2">
                      <span className="w-2 h-2 bg-indigo-400 rounded-full"></span>
                      Evening Routine
                    </h4>
                    {analysis.skincare_routine.evening_routine && analysis.skincare_routine.evening_routine.length > 0 ? (
                      <div className="space-y-3 max-h-96 overflow-y-auto">
                        {analysis.skincare_routine.evening_routine.map((step: any, index: number) => (
                          <div key={index} className="border-l-4 border-green-300 pl-4 py-2">
                            <div className="font-semibold text-gray-900">{step.name}</div>
                            {step.product && (
                              <div className="text-sm text-gray-600 mb-1">
                                <strong>Product:</strong> {step.product}
                                {step.brand && <span> by {step.brand}</span>}
                              </div>
                            )}
                            {step.instructions && (
                              <div className="text-sm text-gray-700">{step.instructions}</div>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-gray-600 mb-4">No evening routine generated yet</p>
                        <Button onClick={() => router.push('/scan')} className="bg-green-600 hover:bg-green-700 text-white">
                          Start Analysis
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Product Recommendations Section */}
        {(analysis.recommended_products && analysis.recommended_products.length > 0) ? (
          <div className="mb-8">
            <Card className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-2xl font-bold text-purple-800">
                  <Sparkles className="w-6 h-6 text-purple-600" />
                  Recommended Products for You
                </CardTitle>
                <p className="text-purple-700">Personalized recommendations based on your skin analysis</p>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {analysis.recommended_products.map((product: any, index: number) => (
                    <div key={index} className="bg-white rounded-lg p-4 border border-purple-200 shadow-sm hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h4 className="font-bold text-gray-900 text-lg mb-1">{product.name}</h4>
                          <p className="text-purple-700 font-semibold text-sm">{product.brand}</p>
                        </div>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center gap-2">
                          <span className="text-lg font-bold text-green-600">{product.price}</span>
                          {product.rating && (
                            <div className="flex items-center gap-1">
                              <span className="text-yellow-500">★</span>
                              <span className="text-sm text-gray-600">{product.rating}</span>
                            </div>
                          )}
                        </div>
                        
                        <p className="text-sm text-gray-600">{product.reason}</p>
                        
                        {product.key_ingredients && (
                          <div className="flex flex-wrap gap-1">
                            {product.key_ingredients.map((ingredient: string, idx: number) => (
                              <span key={idx} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                {ingredient}
                              </span>
                            ))}
                          </div>
                        )}
                        
                        {product.skin_types && (
                          <div className="flex flex-wrap gap-1">
                            {product.skin_types.map((type: string, idx: number) => (
                              <span key={idx} className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                                {type}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      
                      {product.url && (
                        <a 
                          href={product.url} 
                          target="_blank" 
                          rel="noreferrer"
                          className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800 text-sm font-medium"
                        >
                          <span>View Product</span>
                          <ArrowRight className="w-4 h-4" />
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          <div className="mb-8">
            <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-2xl font-bold text-blue-800">
                  <Sparkles className="w-6 h-6 text-blue-600" />
                  Get Personalized Recommendations
                </CardTitle>
                <p className="text-blue-700">Complete your profile and run a skin analysis to get personalized product recommendations</p>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <p className="text-gray-600 mb-4">No personalized recommendations yet</p>
                  <div className="flex gap-4 justify-center">
                    <Button onClick={() => router.push('/scan')} className="bg-green-600 hover:bg-green-700 text-white">
                      Start Face Scan
                    </Button>
                    <Button onClick={() => router.push('/settings')} variant="outline">
                      Complete Profile
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Content Layout */}
        <div className="grid lg:grid-cols-4 gap-8">
          {/* Left Sidebar - Filters */}
          <div className="lg:col-span-1">
            <div className="bg-white border border-gray-200 rounded-lg p-6">

              <h3 className="font-semibold text-gray-900 mb-4">Filter by</h3>
              <div className="space-y-3 mb-6">
                <label className="flex items-center p-2 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input 
                    type="radio" 
                    name="filter" 
                    value="all" 
                    className="mr-3" 
                    checked={activeFilter === 'all'}
                    onChange={() => setActiveFilter('all')}
                  />
                  <span className="text-sm text-gray-700">All Products</span>
                </label>
                <label className="flex items-center p-2 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input 
                    type="radio" 
                    name="filter" 
                    value="recommended" 
                    className="mr-3"
                    checked={activeFilter === 'recommended'}
                    onChange={() => setActiveFilter('recommended')}
                  />
                  <span className="text-sm text-gray-700 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-purple-500" />
                    Recommended
                  </span>
                </label>
              </div>

              <h3 className="font-semibold text-gray-900 mb-4">Brand</h3>
              <div className="space-y-2 mb-6">
                {['CeraVe', 'EltaMD', 'La Roche-Posay', 'Neutrogena', "Paula's Choice", 'The Ordinary'].map((brand) => (
                  <label key={brand} className="flex items-center">
                    <input 
                      type="checkbox" 
                      className="mr-2" 
                      checked={selectedBrands.includes(brand)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedBrands([...selectedBrands, brand])
                        } else {
                          setSelectedBrands(selectedBrands.filter(b => b !== brand))
                        }
                      }}
                    />
                    <span className="text-sm text-gray-700">{brand}</span>
                  </label>
                ))}
              </div>

              <h3 className="font-semibold text-gray-900 mb-4">Price Range</h3>
              <div className="mb-6">
                <input
                  type="range"
                  min="0"
                  max="150"
                  value={priceRange[1]}
                  onChange={(e) => setPriceRange([priceRange[0], parseInt(e.target.value)])}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>${priceRange[0]}</span>
                  <span>${priceRange[1]}</span>
                </div>
              </div>

              {/* Apply Filters Button */}
              <Button 
                onClick={() => {
                  // Trigger product refresh with filters by updating the timestamp
                  setFiltersApplied(Date.now())
                }}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 mt-4"
              >
                Apply Filters
              </Button>
            </div>
          </div>

                 {/* Right Content - Real Product Search */}
                 <div className="lg:col-span-3">
                  <ProductSearch 
                    initialQuery={searchQuery}
                    activeFilter={activeFilter}
                    recommendedProducts={analysis.recommended_products || []}
                    selectedBrands={selectedBrands}
                    priceRange={priceRange}
                    refreshTrigger={filtersApplied ? Date.now() : 0}
                    onProductSelect={(product) => {
                       console.log('Selected product:', product)
                       // Handle product selection
                     }}
                   />
                 </div>
        </div>


        {/* Analysis Details in Hidden Section */}
        {analysis.analysis_notes && (
          <div id="analysis-details" className="hidden mt-8">
            <Card className="bg-gradient-to-br from-blue-50 to-white border-2 border-blue-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-blue-700">
                  <Sparkles className="w-5 h-5" />
                  Analysis Details
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="font-semibold text-blue-800 mb-1">Image Analysis:</p>
                    <p className="text-blue-700">{analysis.analysis_notes?.image_analysis_contribution}</p>
                  </div>
                  <div>
                    <p className="font-semibold text-blue-800 mb-1">Profile Enhancement:</p>
                    <p className="text-blue-700">{analysis.analysis_notes?.profile_enhancement}</p>
                  </div>
                  <div className="md:col-span-2">
                    <p className="font-semibold text-blue-800 mb-1">Recommendation Basis:</p>
                    <p className="text-blue-700">{analysis.analysis_notes?.recommendation_basis}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Bottom Info */}
        <div className="mt-12 text-center">
          <p className="text-sm text-gray-600 mb-2">
            Analysis performed on: {new Date(analysis.analysis_timestamp).toLocaleDateString()}
          </p>
          <div className="inline-flex items-center gap-2 text-sm text-muted-foreground">
            <div className="w-16 h-0.5 bg-gradient-to-r from-transparent to-green-300"></div>
            <span className="font-medium">Powered by AI • Medical-grade Analysis</span>
            <div className="w-16 h-0.5 bg-gradient-to-l from-transparent to-green-300"></div>
          </div>
        </div>
      </div>
    </div>
  )
}