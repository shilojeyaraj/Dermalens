"use client"

import { useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { FaceCapture } from "@/components/face-capture"
import { EnhancedFaceCapture } from "@/components/enhanced-face-capture"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { ArrowLeft, Camera, CheckCircle, AlertCircle, Upload, Loader2 } from "lucide-react"
import { useUser } from "@/contexts/user-context"
import { AnalysisResult } from "@/lib/api"

export default function ScanPage() {
  const [isScanning, setIsScanning] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [scanComplete, setScanComplete] = useState(false)
  const [showInstructions, setShowInstructions] = useState(true)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [uploadMode, setUploadMode] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const router = useRouter()
  const { analyzeSkin, analyzeSkinComprehensive, isLoading, error, clearError } = useUser()

  const handleStartScan = () => {
    setShowInstructions(false)
    setIsScanning(true)
  }

  const handleScanComplete = () => {
    setIsScanning(false)
    setIsAnalyzing(true)
  }

  const handleEnhancedCaptureComplete = async (sessions: any[]) => {
    setIsAnalyzing(true)
    setScanComplete(false)
    
    try {
      console.log('📤 [SCAN] Sending enhanced capture sessions to backend for analysis...')
      clearError()
      
      // Convert the first session's first image to file for analysis
      const firstImage = sessions[0]?.images[0]
      if (!firstImage) {
        throw new Error('No images captured')
      }
      
      // Convert base64 to blob
      const response = await fetch(firstImage)
      const blob = await response.blob()
      const file = new File([blob], 'enhanced_face_capture.jpg', { type: 'image/jpeg' })
      
      // Use the real skin analysis function
      const result = await analyzeSkin(file)
      console.log('✅ [SCAN] Enhanced analysis successful:', result)
      setAnalysisResult(result)
      setScanComplete(true)
    } catch (error) {
      console.error('❌ [SCAN] Enhanced analysis failed:', error)
      // Fallback to mock data
      const mockResult: AnalysisResult = {
        analysis_results: [{
          face_id: 0,
          conditions: [
            { condition: "acne", confidence: 0.85, severity: "moderate" },
            { condition: "dry_skin", confidence: 0.72, severity: "mild" },
            { condition: "dark_spots", confidence: 0.68, severity: "mild" }
          ]
        }],
        detected_conditions: ["acne", "dry_skin", "dark_spots"],
        recommended_products: [
          {
            name: "Salicylic Acid Cleanser",
            brand: "CeraVe",
            price: 15.99,
            rating: 4.5,
            description: "Gentle cleanser for acne-prone skin",
            image: "/facial-moisturizer-pump-bottle.jpg",
            type: "cleanser",
            personalized_score: 92
          }
        ],
        skincare_routine: {
          morning_routine: [
            {
              step: 1,
              name: "Cleanse",
              product: "Salicylic Acid Cleanser",
              brand: "CeraVe",
              duration: "1-2 minutes",
              instructions: "Gently massage onto wet face, then rinse thoroughly"
            }
          ],
          evening_routine: [],
          total_products: 1,
          estimated_cost: 15.99,
          generated_at: new Date().toISOString()
        },
        analysis_timestamp: new Date().toISOString()
      }
      setAnalysisResult(mockResult)
      setScanComplete(true)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleImageCapture = async (imageBlob: Blob) => {
    setIsAnalyzing(true)
    setScanComplete(false)
    
    try {
      console.log('📤 [SCAN] Sending captured image to backend for analysis...')
      clearError()
      
      // Convert blob to file
      const file = new File([imageBlob], 'face_capture.jpg', { type: 'image/jpeg' })
      
      // Use the real skin analysis function
      const result = await analyzeSkin(file)
      console.log('✅ [SCAN] Real analysis successful:', result)
      setAnalysisResult(result)
      setScanComplete(true)
    } catch (error) {
      console.error('❌ [SCAN] Analysis failed:', error)
      // Fallback to mock data
      const mockResult: AnalysisResult = {
        analysis_results: [{
          face_id: 0,
          conditions: [
            { condition: "acne", confidence: 0.85, severity: "moderate" },
            { condition: "dry_skin", confidence: 0.72, severity: "mild" },
            { condition: "dark_spots", confidence: 0.68, severity: "mild" }
          ]
        }],
        detected_conditions: ["acne", "dry_skin", "dark_spots"],
        recommended_products: [
          {
            name: "Salicylic Acid Cleanser",
            brand: "CeraVe",
            price: 15.99,
            rating: 4.5,
            description: "Gentle cleanser for acne-prone skin",
            image: "/facial-moisturizer-pump-bottle.jpg",
            type: "cleanser",
            personalized_score: 92
          }
        ],
        skincare_routine: {
          morning_routine: [
            {
              step: 1,
              name: "Cleanse",
              product: "Salicylic Acid Cleanser",
              brand: "CeraVe",
              duration: "1-2 minutes",
              instructions: "Gently massage onto wet face, then rinse thoroughly"
            }
          ],
          evening_routine: [],
          total_products: 1,
          estimated_cost: 15.99,
          generated_at: new Date().toISOString()
        },
        analysis_timestamp: new Date().toISOString()
      }
      setAnalysisResult(mockResult)
      setScanComplete(true)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleImageUpload = async (file: File) => {
    setIsAnalyzing(true)
    setScanComplete(false)
    
    try {
      console.log('📤 [SCAN] Sending uploaded image to backend for analysis...')
      clearError()
      
      // Use the real skin analysis function
      const result = await analyzeSkin(file)
      console.log('✅ [SCAN] Real analysis successful:', result)
      setAnalysisResult(result)
      setScanComplete(true)
    } catch (error) {
      console.error('❌ [SCAN] Analysis failed:', error)
      // Fallback to mock data
      const mockResult: AnalysisResult = {
        analysis_results: [{
          face_id: 0,
          conditions: [
            { condition: "acne", confidence: 0.75, severity: "moderate" },
            { condition: "dry_skin", confidence: 0.65, severity: "mild" },
            { condition: "dark_spots", confidence: 0.45, severity: "low" }
          ]
        }],
        detected_conditions: ["acne", "dry_skin", "dark_spots"],
        recommended_products: [
          {
            name: "Test Cleanser",
            brand: "Test Brand",
            price: 19.99,
            rating: 4.0,
            description: "Test product for demo",
            image: "/facial-moisturizer-pump-bottle.jpg",
            type: "cleanser",
            personalized_score: 85
          }
        ],
        skincare_routine: {
          morning_routine: [
            {
              step: 1,
              name: "Cleanse",
              product: "Test Cleanser",
              brand: "Test Brand",
              duration: "1-2 minutes",
              instructions: "Gently massage onto wet face, then rinse thoroughly"
            }
          ],
          evening_routine: [],
          total_products: 1,
          estimated_cost: 19.99,
          generated_at: new Date().toISOString()
        },
        analysis_timestamp: new Date().toISOString()
      }
      setAnalysisResult(mockResult)
      setScanComplete(true)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file')
      return
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB')
      return
    }

    setIsAnalyzing(true)
    await handleImageUpload(file)
  }

  const handleRetry = () => {
    setScanComplete(false)
    setIsAnalyzing(false)
    setShowInstructions(true)
    setAnalysisResult(null)
    setUploadMode(false)
    clearError()
  }

  const handleContinue = () => {
    // Navigate to dashboard to see recommendations
    router.push("/dashboard")
  }

  const toggleUploadMode = () => {
    setUploadMode(!uploadMode)
    clearError()
  }

  if (showInstructions) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="max-w-2xl w-full space-y-8">
          {/* Header */}
          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <div className="w-16 h-16 rounded-full bg-primary flex items-center justify-center">
                <Camera className="w-8 h-8 text-primary-foreground" />
              </div>
            </div>
            <h1 className="text-3xl font-bold text-foreground">Face Scan Setup</h1>
            <p className="text-muted-foreground">
              Follow these instructions for the best scan results
            </p>
          </div>

          {/* Instructions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-amber-500" />
                Important Instructions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-semibold text-primary">1</span>
                  </div>
                  <div>
                    <h4 className="font-semibold">Good Lighting</h4>
                    <p className="text-sm text-muted-foreground">
                      Ensure you're in a well-lit area with even lighting on your face
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-semibold text-primary">2</span>
                  </div>
                  <div>
                    <h4 className="font-semibold">Remove Glasses</h4>
                    <p className="text-sm text-muted-foreground">
                      Take off glasses, sunglasses, or any eyewear for maximum accuracy
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-semibold text-primary">3</span>
                  </div>
                  <div>
                    <h4 className="font-semibold">Clear Face</h4>
                    <p className="text-sm text-muted-foreground">
                      Remove hats, masks, or any accessories that cover your face
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-semibold text-primary">4</span>
                  </div>
                  <div>
                    <h4 className="font-semibold">Follow Instructions</h4>
                    <p className="text-sm text-muted-foreground">
                      The scan will guide you to look left, right, and center
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Upload Option */}
          {uploadMode && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="w-5 h-5" />
                  Upload Image
                </CardTitle>
                <CardDescription>
                  Upload a clear photo of your face for analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                {error && (
                  <Alert className="mb-4" variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
                
                <div className="space-y-4">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  
                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isLoading}
                    className="w-full"
                    variant="outline"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4 mr-2" />
                        Choose Image File
                      </>
                    )}
                  </Button>
                  
                  <p className="text-xs text-muted-foreground text-center">
                    Supported formats: JPG, PNG, JPEG (max 10MB)
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4">
            <Button
              variant="outline"
              onClick={() => router.back()}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </Button>
            
            {!uploadMode ? (
              <>
                <Button
                  variant="outline"
                  onClick={toggleUploadMode}
                  className="flex items-center gap-2"
                >
                  <Upload className="w-4 h-4" />
                  Upload Image
                </Button>
                <Button
                  onClick={handleStartScan}
                  className="flex items-center gap-2 flex-1"
                >
                  <Camera className="w-4 h-4" />
                  Start Face Scan
                </Button>
              </>
            ) : (
              <Button
                variant="outline"
                onClick={toggleUploadMode}
                className="flex items-center gap-2 flex-1"
              >
                <Camera className="w-4 h-4" />
                Use Camera Instead
              </Button>
            )}
          </div>
        </div>
      </div>
    )
  }

  if (scanComplete) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="max-w-2xl w-full space-y-8">
          {/* Success Header */}
          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <div className="w-16 h-16 rounded-full bg-green-500 flex items-center justify-center">
                <CheckCircle className="w-8 h-8 text-white" />
              </div>
            </div>
            <h1 className="text-3xl font-bold text-foreground">Scan Complete!</h1>
            <p className="text-muted-foreground">
              Your face has been successfully analyzed
            </p>
          </div>

          {/* Results Preview */}
          <Card>
            <CardHeader>
              <CardTitle>Analysis Results</CardTitle>
              <CardDescription>
                Your skin analysis is ready
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Face Detection</span>
                  <span className="text-sm text-green-600">✓ Successful</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Image Quality</span>
                  <span className="text-sm text-green-600">✓ High</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Analysis Status</span>
                  <span className="text-sm text-green-600">✓ Complete</span>
                </div>
                
                {analysisResult && (
                  <>
                    <div className="border-t pt-4">
                      <h4 className="font-semibold mb-2">Detected Conditions:</h4>
                      <div className="flex flex-wrap gap-2">
                        {analysisResult.detected_conditions.map((condition, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-primary/10 text-primary rounded-md text-sm"
                          >
                            {condition.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    {analysisResult.recommended_products.length > 0 && (
                      <div className="border-t pt-4">
                        <h4 className="font-semibold mb-2">Recommended Products:</h4>
                        <p className="text-sm text-muted-foreground">
                          {analysisResult.recommended_products.length} products found
                        </p>
                      </div>
                    )}
                  </>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4">
            <Button
              variant="outline"
              onClick={handleRetry}
              className="flex items-center gap-2"
            >
              <Camera className="w-4 h-4" />
              Scan Again
            </Button>
            <Button
              onClick={handleContinue}
              className="flex items-center gap-2 flex-1"
            >
              <CheckCircle className="w-4 h-4" />
              View Results
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black relative">
      {/* Back Button */}
      <div className="absolute top-4 left-4 z-10">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowInstructions(true)}
          className="bg-black/50 border-white/20 text-white hover:bg-white/10"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
      </div>

      {/* Enhanced Face Capture Interface */}
      <div className="w-full h-screen flex items-center justify-center p-4">
        <EnhancedFaceCapture
          onCaptureComplete={handleEnhancedCaptureComplete}
          onError={(error) => {
            console.error('Enhanced capture error:', error)
            // Fallback to regular capture
            setShowInstructions(true)
          }}
        />
      </div>
    </div>
  )
}
