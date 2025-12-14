"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Camera, Sparkles, AlertCircle, ArrowRight, Video, VideoOff, Loader2, CheckCircle2 } from "lucide-react"
import { useRouter } from "next/navigation"

type ScanStep = 'ready' | 'center' | 'left' | 'right' | 'analyzing' | 'analysis_complete' | 'complete'

export default function ScanPage() {
  const router = useRouter()
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [isCameraActive, setIsCameraActive] = useState(false)
  const [currentStep, setCurrentStep] = useState<ScanStep>('ready')
  const [countdown, setCountdown] = useState<number | null>(null)
  const [capturedImages, setCapturedImages] = useState<{
    center: string[]
    left: string[]
    right: string[]
  }>({ center: [], left: [], right: [] })
  const [progress, setProgress] = useState(0)
  const [cameraMounted, setCameraMounted] = useState(false)
  const [analysisResults, setAnalysisResults] = useState<any>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [showAnalysisComplete, setShowAnalysisComplete] = useState(false)
  const captureIntervalRef = useRef<NodeJS.Timeout | null>(null)

  // Use ref to avoid closure issues
  const capturedImagesRef = useRef(capturedImages)
  
  useEffect(() => {
    capturedImagesRef.current = capturedImages
  }, [capturedImages])

  // Mount camera component
  useEffect(() => {
    setCameraMounted(true)
    return () => {
      // Cleanup
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }
      if (captureIntervalRef.current) {
        clearInterval(captureIntervalRef.current)
      }
    }
  }, [stream])

  // Connect stream to video element
  useEffect(() => {
    if (stream && videoRef.current) {
      console.log('🔗 Connecting stream to video element')
      videoRef.current.srcObject = stream
      
      // Add event listeners for debugging
      videoRef.current.onloadedmetadata = () => {
        console.log('📹 Video metadata loaded')
      }
      
      videoRef.current.oncanplay = () => {
        console.log('▶️ Video can play')
        // Auto-start scanning when video is ready
        if (currentStep === 'ready') {
          console.log('🚀 Auto-starting scan...')
          setTimeout(() => startScan(), 1000)
        }
      }
    }
  }, [stream, currentStep])

  // Start camera
  const startCamera = async () => {
    try {
      console.log('🎥 Starting camera...')
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'user',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      })
      
      console.log('✅ Camera stream obtained:', mediaStream)
      setStream(mediaStream)
      setIsCameraActive(true)
      
      // Stream will be connected via useEffect when video ref is available
      console.log('✅ Camera stream set, waiting for video element...')
    } catch (error) {
      console.error('❌ Camera access failed:', error)
      alert(`Camera access failed: ${error instanceof Error ? error.message : 'Unknown error'}. Please allow camera permissions and try again.`)
    }
  }

  // Stop camera
  const stopCamera = async () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
    if (captureIntervalRef.current) {
      clearInterval(captureIntervalRef.current)
    }
    setIsCameraActive(false)
  }

  // Capture frame
  const captureFrame = async (): Promise<string | null> => {
    if (!videoRef.current || !canvasRef.current) {
      return null
    }
    
    const canvas = canvasRef.current
    const video = videoRef.current
    const context = canvas.getContext('2d')
    
    if (!context || video.readyState !== video.HAVE_ENOUGH_DATA) {
      return null
    }
    
            try {
              canvas.width = video.videoWidth
              canvas.height = video.videoHeight
              context.drawImage(video, 0, 0)
      return canvas.toDataURL('image/jpeg', 0.85)
            } catch (error) {
      console.error('Error capturing frame:', error)
      return null
    }
  }

  // Scan position
  const scanPosition = async (position: 'center' | 'left' | 'right'): Promise<void> => {
    console.log(`📸 Starting scan for ${position} position`)
    return new Promise<void>((resolve) => {
      let captureCount = 0
      const maxCaptures = 6
      const captures: string[] = []
      
      // Countdown
      let countdownValue = 3
      setCountdown(countdownValue)
      console.log(`⏰ Starting countdown for ${position}: ${countdownValue}`)
      
      const countdownInterval = setInterval(() => {
        countdownValue--
        if (countdownValue > 0) {
          setCountdown(countdownValue)
        } else {
          clearInterval(countdownInterval)
          setCountdown(null)
          
          // Capture frames
          console.log(`📷 Starting frame capture for ${position}`)
          captureIntervalRef.current = setInterval(async () => {
            const frame = await captureFrame()
            if (frame) {
              captures.push(frame)
              captureCount++
              setProgress((captureCount / maxCaptures) * 100)
              console.log(`📸 Captured frame ${captureCount}/${maxCaptures} for ${position}`)
              
              if (captureCount >= maxCaptures) {
                if (captureIntervalRef.current) {
                  clearInterval(captureIntervalRef.current)
                }
                
                console.log(`✅ Completed ${position} scan with ${captures.length} frames`)
                setCapturedImages(prev => ({
                    ...prev,
                    [position]: captures
                }))
                setProgress(0)
                resolve()
              }
            } else {
              console.warn(`⚠️ Failed to capture frame for ${position}`)
            }
          }, 500)
        }
      }, 1000)
    })
  }

  // Start scan
  const startScan = async () => {
    console.log('🔍 Starting 3-angle scan...')
    setCurrentStep('center')
    console.log('📸 Scanning center position...')
    await scanPosition('center')
    
    setCurrentStep('left')
    console.log('📸 Scanning left position...')
    await scanPosition('left')
    
    setCurrentStep('right')
    console.log('📸 Scanning right position...')
    await scanPosition('right')
    
    // Brief pause before analysis
    console.log('⏳ Scan complete, preparing analysis...')
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    setCurrentStep('analyzing')
    setIsAnalyzing(true)
    setAnalysisProgress(0)
    console.log('🧠 Starting analysis...')
    
    // Simulate analysis progress
    const progressInterval = setInterval(() => {
      setAnalysisProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return prev
        }
        return prev + 10
      })
    }, 200)
    
    await analyzeAllImages()
    
    clearInterval(progressInterval)
    setAnalysisProgress(100)
    setCurrentStep('analysis_complete')
    setShowAnalysisComplete(true)
    console.log('✅ Analysis complete!')
    
    // Show completion message for 2 seconds, then redirect
    setTimeout(() => {
      setCurrentStep('complete')
      router.push('/dashboard')
    }, 2000)
  }

  // Analyze images
  const analyzeAllImages = async () => {
    console.log('🔍 [ANALYSIS] Starting image analysis...')
    const currentImages = capturedImagesRef.current
    const totalImages = currentImages.center.length + currentImages.left.length + currentImages.right.length
    
    console.log(`📊 [ANALYSIS] Total images to analyze: ${totalImages}`)
    console.log(`   - Center images: ${currentImages.center.length}`)
    console.log(`   - Left images: ${currentImages.left.length}`)
    console.log(`   - Right images: ${currentImages.right.length}`)
    
    if (totalImages === 0) {
      console.error('❌ [ANALYSIS] No images captured')
      throw new Error('No images captured - please try the scan again')
    }
    
    try {
      const token = localStorage.getItem('token')
      console.log(`🔑 [ANALYSIS] Using token: ${token ? 'Present' : 'Missing'}`)
      
      const formData = new FormData()
      
      // Add center images to form data
      console.log('📸 [ANALYSIS] Processing center images...')
      for (let i = 0; i < currentImages.center.length; i++) {
        console.log(`   - Processing center_${i}.jpg`)
        const response = await fetch(currentImages.center[i])
          const blob = await response.blob()
        console.log(`   - Blob size: ${blob.size} bytes`)
          if (blob.size > 0) {
            formData.append('files', blob, `center_${i}.jpg`)
          console.log(`   - Added center_${i}.jpg to form data`)
          } else {
          console.warn(`   - Skipped empty center_${i}.jpg`)
        }
      }
      
      // Add left images to form data
      console.log('📸 [ANALYSIS] Processing left images...')
      for (let i = 0; i < currentImages.left.length; i++) {
        console.log(`   - Processing left_${i}.jpg`)
        const response = await fetch(currentImages.left[i])
          const blob = await response.blob()
        console.log(`   - Blob size: ${blob.size} bytes`)
          if (blob.size > 0) {
            formData.append('files', blob, `left_${i}.jpg`)
          console.log(`   - Added left_${i}.jpg to form data`)
          } else {
          console.warn(`   - Skipped empty left_${i}.jpg`)
        }
      }
      
      // Add right images to form data
      console.log('📸 [ANALYSIS] Processing right images...')
      for (let i = 0; i < currentImages.right.length; i++) {
        console.log(`   - Processing right_${i}.jpg`)
        const response = await fetch(currentImages.right[i])
          const blob = await response.blob()
        console.log(`   - Blob size: ${blob.size} bytes`)
          if (blob.size > 0) {
            formData.append('files', blob, `right_${i}.jpg`)
          console.log(`   - Added right_${i}.jpg to form data`)
          } else {
          console.warn(`   - Skipped empty right_${i}.jpg`)
        }
      }
      
      console.log('🌐 [ANALYSIS] Sending request to backend...')
      console.log(`   - Endpoint: ${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/analyze-skin-multi-angle`)
      console.log(`   - Method: POST`)
      console.log(`   - Form data entries: ${Array.from(formData.entries()).length}`)
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/analyze-skin-multi-angle`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })
      
      console.log(`📡 [ANALYSIS] Response received:`)
      console.log(`   - Status: ${response.status}`)
      console.log(`   - OK: ${response.ok}`)
      console.log(`   - Headers: ${JSON.stringify(Object.fromEntries(response.headers.entries()))}`)
      
      if (response.ok) {
        console.log('✅ [ANALYSIS] Analysis successful, parsing results...')
      const result = await response.json()
        console.log('📊 [ANALYSIS] Analysis results:', result)
      
        localStorage.setItem('skinAnalysis', JSON.stringify(result))
        console.log('💾 [ANALYSIS] Results saved to localStorage')
        
        setCurrentStep('complete')
        setAnalysisResults(result)
        console.log('🎉 [ANALYSIS] Analysis complete!')
      } else {
        const errorText = await response.text()
        console.error(`❌ [ANALYSIS] Analysis failed with status ${response.status}`)
        console.error(`   - Error response: ${errorText}`)
        throw new Error(`Analysis failed: ${response.status} - ${errorText}`)
      }
    } catch (error: any) {
      console.error('💥 [ANALYSIS] Analysis error:', error)
      // Show error in console and reset - dashboard will handle display
      console.error('Analysis failed:', error.message || error)
      setCurrentStep('ready')
      setCapturedImages({ center: [], left: [], right: [] })
      setProgress(0)
      // Store error for dashboard to display
      const errorResult = {
        success: false,
        error: error.message || "Analysis failed. Please try again."
      }
      localStorage.setItem('skinAnalysis', JSON.stringify(errorResult))
    }
  }

  // Skip scan
  const handleSkip = async () => {
    stopCamera()
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/generate-profile-recommendations`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const result = await response.json()
        localStorage.setItem('skinAnalysis', JSON.stringify(result))
        router.push('/dashboard')
      } else {
        // Fallback
        const fallbackAnalysis = {
          success: true,
          analysis_type: 'profile_based',
          detected_conditions: ['general_care'],
          recommended_products: [
            {
              name: "Gentle Daily Cleanser",
              category: "Cleanser",
              price: "15.99",
              description: "Recommended for all skin types"
            }
          ],
          skincare_routine: "Morning: Gentle cleanser → Moisturizer\nEvening: Gentle cleanser",
          ai_report: "Based on your profile, here are general skincare recommendations.",
          skin_health_score: 0.7,
          analysis_timestamp: new Date().toISOString()
        }
        
        localStorage.setItem('skinAnalysis', JSON.stringify(fallbackAnalysis))
        router.push('/dashboard')
      }
    } catch (error) {
      console.error('Profile analysis error:', error)
      router.push('/dashboard')
    }
  }

  // Restart scan
  const restartScan = () => {
    setCapturedImages({ center: [], left: [], right: [] })
    setCurrentStep('ready')
    setProgress(0)
    startCamera()
  }

  // Get instruction text
  const getInstructionText = () => {
    switch (currentStep) {
      case 'center':
        return '👀 Look straight at the camera - Keep your face centered'
      case 'left':
        return '👈 Turn your head to the LEFT - Show your left profile'
      case 'right':
        return '👉 Turn your head to the RIGHT - Show your right profile'
      case 'analyzing':
        return '🔍 Analyzing your skin...'
      case 'analysis_complete':
        return '✅ Analysis complete! Redirecting to dashboard...'
      case 'complete':
        return '✅ Analysis complete! Ready to process with your profile'
      default:
        return 'Ready to start'
    }
  }

  // Get step icon
  const getStepIcon = () => {
    switch (currentStep) {
      case 'center':
      case 'left':
      case 'right':
        return <Video className="w-8 h-8 text-green-500" />
      case 'analyzing':
        return <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
      case 'analysis_complete':
        return <CheckCircle2 className="w-8 h-8 text-green-500 animate-pulse" />
      case 'complete':
        return <Sparkles className="w-8 h-8 text-yellow-500" />
      default:
        return <Camera className="w-8 h-8 text-gray-500" />
    }
  }

  if (!cameraMounted) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-green-50 to-green-100 p-4">
      <div className="max-w-4xl mx-auto py-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-green-500 to-green-600 shadow-lg mb-4">
            {getStepIcon()}
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold mb-3 bg-gradient-to-r from-green-600 to-green-800 bg-clip-text text-transparent">
            {currentStep === 'ready' ? 'Multi-Angle Face Scan' : 'Scanning Your Face'}
          </h1>
          
          <p className="text-lg text-gray-600 mb-6">
            {getInstructionText()}
          </p>
        </div>

        {/* Main Card */}
        <Card className="bg-white/90 backdrop-blur-sm border-2 border-green-100 shadow-2xl">
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Camera Area */}
              <div className="lg:col-span-2">
              <div className="relative rounded-xl overflow-hidden border-3 border-green-300 bg-black shadow-xl w-full aspect-video flex items-center justify-center">
                {isCameraActive ? (
                  <>
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      muted
                      className="w-full h-full object-cover"
                      style={{ transform: 'scaleX(-1)' }}
                      />
                      
                      {/* Face Overlay */}
                      <div className="absolute inset-0 pointer-events-none">
                        {/* Face outline overlay */}
                        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                          <div className="relative">
                            {/* Face oval */}
                            <div className="w-48 h-64 border-4 border-green-400 rounded-full opacity-80 animate-pulse"></div>
                            
                            {/* Position indicators */}
                            <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
                              <div className="w-3 h-3 bg-green-400 rounded-full animate-bounce"></div>
                            </div>
                            <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
                              <div className="w-3 h-3 bg-green-400 rounded-full animate-bounce"></div>
                            </div>
                            <div className="absolute top-1/2 -left-2 transform -translate-y-1/2">
                              <div className="w-3 h-3 bg-green-400 rounded-full animate-bounce"></div>
                            </div>
                            <div className="absolute top-1/2 -right-2 transform -translate-y-1/2">
                              <div className="w-3 h-3 bg-green-400 rounded-full animate-bounce"></div>
                            </div>
                          </div>
                        </div>
                        
                        {/* Step-specific positioning guides */}
                        {currentStep === 'center' && (
                          <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-green-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
                            Look straight at the camera
                          </div>
                        )}
                        {currentStep === 'left' && (
                          <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-green-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
                            Turn your head to the left
                          </div>
                        )}
                        {currentStep === 'right' && (
                          <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-green-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
                            Turn your head to the right
                          </div>
                        )}
                      </div>
                      
                      {/* Countdown */}
                      {countdown && (
                        <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                          <div className="text-6xl font-bold text-white">
                            {countdown}
                        </div>
                      </div>
                    )}
                    
                      {/* Progress */}
                      {progress > 0 && (
                        <div className="absolute bottom-4 left-4 right-4">
                          <div className="bg-white/90 rounded-full h-2">
                            <div 
                              className="bg-green-500 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${progress}%` }}
                            />
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="text-center p-8">
                    <Video className="w-24 h-24 text-white/50 mx-auto mb-4" />
                    <p className="text-white text-lg">Click "Start Scan" to begin</p>
                  </div>
                )}
              </div>
                  </div>

              {/* Controls */}
              <div className="lg:col-span-1 space-y-4">
                {!isCameraActive && currentStep === 'ready' && (
                  <>
                    <Button 
                      onClick={async () => {
                        console.log('🎬 Starting camera and scan...')
                        await startCamera()
                        // Scanning will auto-start when video is ready
                      }}
                      className="w-full bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white font-bold h-14 text-base"
                    >
                      <Video className="w-5 h-5 mr-2" />
                      Start 3-Angle Scan
                    </Button>
                    
                    <Button 
                      onClick={handleSkip}
                      variant="outline"
                      className="w-full border-2 border-green-600 text-green-600 hover:bg-green-50 font-semibold h-14 text-base"
                    >
                      Skip for Now
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </Button>
                  </>
                )}
                
                {isCameraActive && (currentStep === 'center' || currentStep === 'left' || currentStep === 'right') && (
                    <Button 
                      onClick={stopCamera}
                      variant="outline"
                      className="w-full border-2 border-red-500 text-red-500 hover:bg-red-50 font-semibold h-12 text-base"
                    >
                      <VideoOff className="w-5 h-5 mr-2" />
                      Stop Scan
                    </Button>
                )}
                
                {currentStep === 'analyzing' && (
                  <div className="text-center space-y-4">
                    <Loader2 className="w-12 h-12 text-purple-500 animate-spin mx-auto" />
                    <p className="text-lg font-semibold text-gray-700">Analyzing your skin...</p>
                    <p className="text-sm text-gray-500">This may take a few moments</p>
                    
                    {/* Analysis Progress Bar */}
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div 
                        className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all duration-300"
                        style={{ width: `${analysisProgress}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-500">{analysisProgress}% complete</p>
                  </div>
                )}
                
                {currentStep === 'analysis_complete' && showAnalysisComplete && (
                  <div className="text-center space-y-4">
                    <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto animate-pulse" />
                    <p className="text-xl font-bold text-green-600">Analysis Complete!</p>
                    <p className="text-sm text-gray-500">Redirecting to dashboard...</p>
                  </div>
                )}
                
                {currentStep === 'complete' && (
                    <Button 
                      onClick={() => {
                      handleSkip()
                      }}
                      className="w-full bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white font-bold h-14 text-base"
                    >
                      <Sparkles className="w-5 h-5 mr-2" />
                      Process with My Profile
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Bottom Accent */}
        <div className="mt-8 text-center">
          <div className="inline-flex items-center gap-2 text-sm text-muted-foreground">
            <div className="w-16 h-0.5 bg-gradient-to-r from-transparent to-green-300"></div>
            <span className="font-medium">Powered by AI • Professional-grade scanning</span>
            <div className="w-16 h-0.5 bg-gradient-to-l from-transparent to-green-300"></div>
          </div>
        </div>
      </div>
      
      {/* Hidden canvas for capture */}
      <canvas ref={canvasRef} className="hidden" />
    </div>
  )
}
