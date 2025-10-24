"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ProductSearch } from "@/components/product-search"
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

  useEffect(() => {
    // Load analysis from localStorage
    const storedAnalysis = localStorage.getItem('skinAnalysis')
    console.log('🔍 [DASHBOARD] Loading analysis from localStorage:', storedAnalysis)
    
    if (storedAnalysis) {
      try {
        const parsedAnalysis = JSON.parse(storedAnalysis)
        console.log('🔍 [DASHBOARD] Parsed analysis data:', parsedAnalysis)
        console.log('🔍 [DASHBOARD] Detected conditions:', parsedAnalysis.detected_conditions)
        console.log('🔍 [DASHBOARD] Skin health score:', parsedAnalysis.skin_health_score)
        console.log('🔍 [DASHBOARD] AI report:', parsedAnalysis.ai_report)
        setAnalysis(parsedAnalysis)
        setError(null)
      } catch (err) {
        console.error('🔍 [DASHBOARD] Failed to parse analysis:', err)
        setError("Failed to load analysis results")
      }
    } else {
      console.log('🔍 [DASHBOARD] No analysis found in localStorage')
      setError("No analysis results found. Please run a scan first.")
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
                  <Button onClick={() => router.push('/scan')} className="mt-4">
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
            <Button onClick={() => router.push('/scan')} className="bg-blue-600 hover:bg-blue-700 text-white">
              Face Scan
            </Button>
            <Dialog>
              <DialogTrigger asChild>
                <Button variant="outline" className="flex items-center gap-2">
                  <Repeat2 className="w-4 h-4" />
                  Your Skincare Routine
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle className="flex items-center gap-3 text-2xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                    <Sparkles className="w-6 h-6 text-green-500" />
                    Your AI-Powered Skincare Routine
                  </DialogTitle>
                  <p className="text-gray-600 mt-2">Personalized for your skin type and concerns</p>
                </DialogHeader>
                <div className="space-y-8">
                  {/* Morning Routine */}
                  <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl p-6 border-2 border-yellow-200">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center">
                        <span className="text-white text-lg">🌅</span>
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900">Morning Routine</h3>
                        <p className="text-sm text-gray-600">Start your day with healthy skin</p>
                      </div>
                    </div>
                    <div className="space-y-4">
                      {(() => {
                        const routine = (analysis as any)?.skincare_routine
                        console.log('🔍 [ROUTINE] Full routine data:', routine)
                        const morning = Array.isArray(routine?.morning) ? routine.morning : []
                        console.log('🔍 [ROUTINE] Morning routine:', morning)
                        return morning.map((step: any, idx: number) => (
                          <div key={idx} className="bg-white rounded-lg p-4 border border-yellow-200 shadow-sm hover:shadow-md transition-shadow">
                            <div className="flex items-start gap-4">
                              <div className="flex-shrink-0">
                                <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                                  {step.step || idx + 1}
                                </div>
                              </div>
                              <div className="flex-1">
                                <div className="flex items-start justify-between mb-2">
                                  <h4 className="font-bold text-gray-900 text-lg">{step.action || step.name || `Step ${step.step || idx + 1}`}</h4>
                                  {step.duration ? (
                                    <span className="bg-yellow-100 text-yellow-800 text-xs font-semibold px-3 py-1 rounded-full flex items-center gap-1">
                                      <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
                                      {step.duration}
                                    </span>
                                  ) : null}
                                </div>
                                {step.instructions ? (
                                  <p className="text-gray-700 mb-3 leading-relaxed">{step.instructions}</p>
                                ) : null}
                                {step.product ? (
                                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
                                    <p className="text-sm font-semibold text-blue-900 mb-1">💄 Recommended Product:</p>
                                    <p className="text-blue-800">{step.product}</p>
                                  </div>
                                ) : null}
                                {step.tips ? (
                                  <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                    <p className="text-sm font-semibold text-green-900 mb-1">💡 Pro Tip:</p>
                                    <p className="text-green-800 text-sm italic">{step.tips}</p>
                                  </div>
                                ) : null}
                                {step.url ? (
                                  <a href={step.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800 text-sm font-medium mt-2">
                                    <span>Shop Product</span>
                                    <ArrowRight className="w-4 h-4" />
                                  </a>
                                ) : null}
                              </div>
                            </div>
                          </div>
                        ))
                      })()}
                    </div>
                  </div>
                  {/* Evening Routine */}
                  <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl p-6 border-2 border-purple-200">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-indigo-500 rounded-full flex items-center justify-center">
                        <span className="text-white text-lg">🌙</span>
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900">Evening Routine</h3>
                        <p className="text-sm text-gray-600">Repair and restore while you sleep</p>
                      </div>
                    </div>
                    <div className="space-y-4">
                      {(() => {
                        const routine = (analysis as any)?.skincare_routine
                        console.log('🔍 [ROUTINE] Evening routine:', routine?.evening)
                        const evening = Array.isArray(routine?.evening) ? routine.evening : []
                        return evening.map((step: any, idx: number) => (
                          <div key={idx} className="bg-white rounded-lg p-4 border border-purple-200 shadow-sm hover:shadow-md transition-shadow">
                            <div className="flex items-start gap-4">
                              <div className="flex-shrink-0">
                                <div className="w-8 h-8 bg-gradient-to-br from-purple-400 to-indigo-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                                  {step.step || idx + 1}
                                </div>
                              </div>
                              <div className="flex-1">
                                <div className="flex items-start justify-between mb-2">
                                  <h4 className="font-bold text-gray-900 text-lg">{step.action || step.name || `Step ${step.step || idx + 1}`}</h4>
                                  {step.duration ? (
                                    <span className="bg-purple-100 text-purple-800 text-xs font-semibold px-3 py-1 rounded-full flex items-center gap-1">
                                      <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                                      {step.duration}
                                    </span>
                                  ) : null}
                                </div>
                                {step.instructions ? (
                                  <p className="text-gray-700 mb-3 leading-relaxed">{step.instructions}</p>
                                ) : null}
                                {step.product ? (
                                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
                                    <p className="text-sm font-semibold text-blue-900 mb-1">💄 Recommended Product:</p>
                                    <p className="text-blue-800">{step.product}</p>
                                  </div>
                                ) : null}
                                {step.tips ? (
                                  <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                    <p className="text-sm font-semibold text-green-900 mb-1">💡 Pro Tip:</p>
                                    <p className="text-green-800 text-sm italic">{step.tips}</p>
                                  </div>
                                ) : null}
                                {step.url ? (
                                  <a href={step.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800 text-sm font-medium mt-2">
                                    <span>Shop Product</span>
                                    <ArrowRight className="w-4 h-4" />
                                  </a>
                                ) : null}
                              </div>
                            </div>
                          </div>
                        ))
                      })()}
                    </div>
                  </div>
                  
                  {/* Weekly Routine */}
                  {(() => {
                    const routine = (analysis as any)?.skincare_routine
                    const weekly = Array.isArray(routine?.weekly) ? routine.weekly : []
                    if (weekly.length > 0) {
                      return (
                        <div className="bg-gradient-to-br from-pink-50 to-rose-50 rounded-xl p-6 border-2 border-pink-200">
                          <div className="flex items-center gap-3 mb-6">
                            <div className="w-10 h-10 bg-gradient-to-br from-pink-400 to-rose-500 rounded-full flex items-center justify-center">
                              <span className="text-white text-lg">✨</span>
                            </div>
                            <div>
                              <h3 className="text-xl font-bold text-gray-900">Weekly Treatments</h3>
                              <p className="text-sm text-gray-600">Extra care for optimal skin health</p>
                            </div>
                          </div>
                          <div className="space-y-4">
                            {weekly.map((step: any, idx: number) => (
                              <div key={idx} className="bg-white rounded-lg p-4 border border-pink-200 shadow-sm hover:shadow-md transition-shadow">
                                <div className="flex items-start gap-4">
                                  <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-gradient-to-br from-pink-400 to-rose-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                                      {step.step || idx + 1}
                                    </div>
                                  </div>
                                  <div className="flex-1">
                                    <div className="flex items-start justify-between mb-2">
                                      <h4 className="font-bold text-gray-900 text-lg">{step.action || step.name || `Step ${step.step || idx + 1}`}</h4>
                                      {step.duration ? (
                                        <span className="bg-pink-100 text-pink-800 text-xs font-semibold px-3 py-1 rounded-full flex items-center gap-1">
                                          <span className="w-2 h-2 bg-pink-500 rounded-full"></span>
                                          {step.duration}
                                        </span>
                                      ) : null}
                                    </div>
                                    {step.instructions ? (
                                      <p className="text-gray-700 mb-3 leading-relaxed">{step.instructions}</p>
                                    ) : null}
                                    {step.product ? (
                                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
                                        <p className="text-sm font-semibold text-blue-900 mb-1">💄 Recommended Product:</p>
                                        <p className="text-blue-800">{step.product}</p>
                                      </div>
                                    ) : null}
                                    {step.tips ? (
                                      <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                        <p className="text-sm font-semibold text-green-900 mb-1">💡 Pro Tip:</p>
                                        <p className="text-green-800 text-sm italic">{step.tips}</p>
                                      </div>
                                    ) : null}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )
                    }
                    return null
                  })()}
                  
                  {/* Tips Section */}
                  {(() => {
                    const routine = (analysis as any)?.skincare_routine
                    const tips = Array.isArray(routine?.tips) ? routine.tips : []
                    if (tips.length > 0) {
                      return (
                        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border-2 border-green-200">
                          <div className="flex items-center gap-3 mb-6">
                            <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center">
                              <span className="text-white text-lg">💡</span>
                            </div>
                            <div>
                              <h3 className="text-xl font-bold text-gray-900">Pro Tips</h3>
                              <p className="text-sm text-gray-600">Expert advice for better results</p>
                            </div>
                          </div>
                          <div className="grid gap-3">
                            {tips.map((tip: string, idx: number) => (
                              <div key={idx} className="bg-white rounded-lg p-4 border border-green-200 shadow-sm">
                                <div className="flex items-start gap-3">
                                  <div className="flex-shrink-0 w-6 h-6 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center">
                                    <span className="text-white text-xs font-bold">{idx + 1}</span>
                                  </div>
                                  <p className="text-gray-700 leading-relaxed">{tip}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )
                    }
                    return null
                  })()}
                </div>
              </DialogContent>
            </Dialog>
            
            <Button className="bg-green-600 hover:bg-green-700 text-white rounded-full w-10 h-10 p-0">
              <Sparkles className="w-5 h-5" />
            </Button>
            
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
              <span className="text-sm font-medium">Profile</span>
            </div>
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
                    {analysis.ai_report}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Product Recommendations Section */}
        {analysis.recommended_products && analysis.recommended_products.length > 0 && (
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
        )}

        {/* Main Content Layout */}
        <div className="grid lg:grid-cols-4 gap-8">
          {/* Left Sidebar - Filters */}
          <div className="lg:col-span-1">
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Search</h3>
              <div className="relative mb-6">
                <input
                  type="text"
                  placeholder="Search products..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
              </div>

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
                    <input type="checkbox" className="mr-2" />
                    <span className="text-sm text-gray-700">{brand}</span>
                  </label>
                ))}
              </div>

              <h3 className="font-semibold text-gray-900 mb-4">Price Range</h3>
              <div className="mb-6">
                <input
                  type="range"
                  min="0"
                  max="100"
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>$0.00</span>
                  <span>$50.00</span>
                </div>
              </div>
            </div>
          </div>

                 {/* Right Content - Real Product Search */}
                 <div className="lg:col-span-3">
                  <ProductSearch 
                    initialQuery={(analysis.detected_conditions ?? []).join(' ')}
                    activeFilter={activeFilter}
                    recommendedProducts={analysis.recommended_products || []}
                    onProductSelect={(product) => {
                       console.log('Selected product:', product)
                       // Handle product selection
                     }}
                   />
                 </div>
        </div>

        {/* Skincare Routine Section */}
        {analysis.skincare_routine && (
          <div className="mt-12">
            <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Repeat2 className="w-5 h-5 text-green-600" />
                Your Personalized Skincare Routine
              </h3>
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <div className="prose prose-sm max-w-none">
                  <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                    {typeof analysis.skincare_routine === 'string' 
                      ? analysis.skincare_routine
                      : JSON.stringify(analysis.skincare_routine, null, 2)
                    }
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

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
                    <p className="text-blue-700">{analysis.analysis_notes.image_analysis_contribution}</p>
                  </div>
                  <div>
                    <p className="font-semibold text-blue-800 mb-1">Profile Enhancement:</p>
                    <p className="text-blue-700">{analysis.analysis_notes.profile_enhancement}</p>
                  </div>
                  <div className="md:col-span-2">
                    <p className="font-semibold text-blue-800 mb-1">Recommendation Basis:</p>
                    <p className="text-blue-700">{analysis.analysis_notes.recommendation_basis}</p>
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

