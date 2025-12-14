"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { FaceScanAvatar } from "@/components/ui/face-scan-avatar"
import { Camera, Sparkles, AlertCircle, ArrowRight, Video, VideoOff, Loader2, CheckCircle2 } from "lucide-react"
import { useRouter } from "next/navigation"

type ScanStep = 'ready' | 'center' | 'left' | 'right' | 'analyzing' | 'complete'

interface AnalysisResult {
  conditions: Array<{
    condition: string
    confidence: number
    severity: string
    location: string
    coordinates: {
      x: number
      y: number
      radius: number
    }
  }>
}

export default function EnhancedScanPage() {
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
  }>({
    center: [],
    left: [],
    right: []
  })
  const [progress, setProgress] = useState(0)
  const [cameraMounted, setCameraMounted] = useState(false)
  const [isScanning, setIsScanning] = useState(false)
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult | null>(null)
  const [currentImage, setCurrentImage] = useState<string | null>(null)
  const captureIntervalRef = useRef<NodeJS.Timeout | null>(null)

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

  // Start camera
  const startCamera = async () => {
    console.log('🎥 [CAMERA] Starting camera initialization...')
    try {
      console.log('🎥 [CAMERA] Checking mediaDevices support...')
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('MediaDevices API not supported')
      }
      
      console.log('🎥 [CAMERA] Requesting camera permissions...')
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'user',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      })
      
      console.log('🎥 [CAMERA] Stream obtained successfully:', {
        id: mediaStream.id,
        active: mediaStream.active,
        tracks: mediaStream.getTracks().length,
        videoTracks: mediaStream.getVideoTracks().length
      })
      
      setStream(mediaStream)
      setIsCameraActive(true)
      
      // Force a small delay to ensure video element is ready
      setTimeout(() => {
        if (videoRef.current && videoRef.current.srcObject) {
          console.log('🎥 [CAMERA] Forcing video refresh...')
          videoRef.current.load()
          videoRef.current.play().catch(e => console.error('🎥 [CAMERA] Refresh play failed:', e))
        }
      }, 200)
      
      // Wait for video element to be available
      const waitForVideoElement = () => {
        return new Promise<void>((resolve) => {
          const checkVideo = () => {
            if (videoRef.current) {
              console.log('🎥 [CAMERA] Video element found, setting up...')
              resolve()
            } else {
              console.log('🎥 [CAMERA] Video element not ready, waiting...')
              setTimeout(checkVideo, 50)
            }
          }
          checkVideo()
        })
      }
      
      // Wait for video element and then set up
      waitForVideoElement().then(() => {
        if (videoRef.current) {
          console.log('🎥 [CAMERA] Setting video source...')
          videoRef.current.srcObject = mediaStream
          videoRef.current.play().catch(e => console.error('🎥 [CAMERA] Play failed:', e))
        }
      })
      
    } catch (error) {
      console.error('🎥 [CAMERA] Error starting camera:', error)
      alert('Failed to start camera. Please check permissions and try again.')
    }
  }

  // Stop camera
  const stopCamera = () => {
    console.log('🎥 [CAMERA] Stopping camera...')
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
    setIsCameraActive(false)
    setCurrentStep('ready')
    setProgress(0)
    if (captureIntervalRef.current) {
      clearInterval(captureIntervalRef.current)
    }
  }

  // Start scan process
  const startScan = async () => {
    console.log('🔍 [SCAN] Starting multi-angle scan...')
    setCurrentStep('center')
    
    try {
      // Step 1: Center scan
      console.log('🔍 [SCAN] Step 1: Center scan')
      await scanPosition('center')
      
      // Step 2: Left scan
      console.log('🔍 [SCAN] Step 2: Left scan')
      setCurrentStep('left')
      await scanPosition('left')
      
      // Step 3: Right scan
      console.log('🔍 [SCAN] Step 3: Right scan')
      setCurrentStep('right')
      await scanPosition('right')
      
      // Step 4: Analysis
      console.log('🔍 [SCAN] Step 4: Analysis')
      setCurrentStep('analyzing')
      await performAnalysis()
      
    } catch (error) {
      console.error('🔍 [SCAN] Error during scan:', error)
      alert('Scan failed. Please try again.')
      setCurrentStep('ready')
    }
  }

  // Scan position
  const scanPosition = async (position: 'center' | 'left' | 'right'): Promise<void> => {
    console.log(`🔍 [SCAN] Starting scan for position: ${position}`)
    return new Promise<void>((resolve) => {
      let captureCount = 0
      const maxCaptures = 6
      const captures: string[] = []
      
      console.log(`🔍 [SCAN] ${position} - Starting countdown...`)
      
      // Countdown
      let countdownValue = 3
      setCountdown(countdownValue)
      
      const countdownInterval = setInterval(() => {
        countdownValue--
        console.log(`🔍 [SCAN] ${position} - Countdown: ${countdownValue}`)
        if (countdownValue > 0) {
          setCountdown(countdownValue)
        } else {
          clearInterval(countdownInterval)
          setCountdown(null)
          console.log(`🔍 [SCAN] ${position} - Countdown finished, starting capture...`)
          
          // Start scanning animation
          setIsScanning(true)
          
          // Capture frames
          captureIntervalRef.current = setInterval(async () => {
            console.log(`🔍 [SCAN] ${position} - Capture attempt ${captureCount + 1}/${maxCaptures}`)
            const frame = await captureFrame()
            if (frame) {
              captures.push(frame)
              captureCount++
              console.log(`🔍 [SCAN] ${position} - Captured frame ${captureCount}, data length: ${frame.length}`)
              setProgress((captureCount / maxCaptures) * 100)
              
              // Update current image for avatar display
              setCurrentImage(frame)
              
              if (captureCount >= maxCaptures) {
                console.log(`🔍 [SCAN] ${position} - Capture complete! Total frames: ${captures.length}`)
                if (captureIntervalRef.current) {
                  clearInterval(captureIntervalRef.current)
                }
                setCapturedImages(prev => ({
                  ...prev,
                  [position]: captures
                }))
                setProgress(0)
                setIsScanning(false)
                resolve()
              }
            } else {
              console.warn(`🔍 [SCAN] ${position} - Failed to capture frame ${captureCount + 1}`)
            }
          }, 500)
        }
      }, 1000)
    })
  }

  // Capture frame
  const captureFrame = async (): Promise<string | null> => {
    console.log('📸 [CAPTURE] Attempting to capture frame...')
    
    if (!videoRef.current) {
      console.error('📸 [CAPTURE] Video ref is null!')
      return null
    }
    
    if (!canvasRef.current) {
      console.error('📸 [CAPTURE] Canvas ref is null!')
      return null
    }
    
    const canvas = canvasRef.current
    const video = videoRef.current
    const context = canvas.getContext('2d')
    
    if (!context) {
      console.error('📸 [CAPTURE] Could not get canvas context!')
      return null
    }
    
    if (video.readyState !== video.HAVE_ENOUGH_DATA) {
      console.warn('📸 [CAPTURE] Video not ready, readyState:', video.readyState)
      return null
    }
    
    if (video.videoWidth === 0 || video.videoHeight === 0) {
      console.warn('📸 [CAPTURE] Video dimensions are 0!')
      return null
    }
    
    try {
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      console.log('📸 [CAPTURE] Canvas dimensions set:', { width: canvas.width, height: canvas.height })
      
      context.drawImage(video, 0, 0)
      console.log('📸 [CAPTURE] Image drawn to canvas')
      
      const dataURL = canvas.toDataURL('image/jpeg', 0.85)
      console.log('📸 [CAPTURE] Data URL generated, length:', dataURL.length)
      
      return dataURL
    } catch (error) {
      console.error('📸 [CAPTURE] Error capturing frame:', error)
      return null
    }
  }

  // Perform analysis
  const performAnalysis = async () => {
    console.log('🔬 [ANALYSIS] Starting enhanced analysis...')
    
    try {
      // Simulate analysis with mock results
      const mockAnalysisResults: AnalysisResult = {
        conditions: [
          {
            condition: "acne",
            confidence: 0.75,
            severity: "moderate",
            location: "forehead",
            coordinates: { x: 0.3, y: 0.2, radius: 0.05 }
          },
          {
            condition: "dry_skin",
            confidence: 0.65,
            severity: "mild",
            location: "cheeks",
            coordinates: { x: 0.2, y: 0.4, radius: 0.08 }
          },
          {
            condition: "dark_circles",
            confidence: 0.60,
            severity: "mild",
            location: "under_eyes",
            coordinates: { x: 0.5, y: 0.3, radius: 0.06 }
          }
        ]
      }
      
      // Set analysis results
      setAnalysisResults(mockAnalysisResults)
      setCurrentStep('complete')
      
      // Simulate processing delay
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Redirect to dashboard
      router.push('/dashboard')
      
    } catch (error) {
      console.error('🔬 [ANALYSIS] Error during analysis:', error)
      alert('Analysis failed. Please try again.')
      setCurrentStep('ready')
    }
  }

  // Handle scan completion
  const handleScanComplete = () => {
    console.log('✅ [SCAN] Scan animation completed')
    // Analysis results will be shown via the overlay
  }

  // Skip scan
  const handleSkip = () => {
    console.log('⏭️ [SKIP] Skipping scan, redirecting to dashboard...')
    router.push('/dashboard')
  }

  // Get instruction
  const getInstructionText = () => {
    switch (currentStep) {
      case 'center':
        return '👀 Look straight at the camera'
      case 'left':
        return '👈 Turn your head to the LEFT'
      case 'right':
        return '👉 Turn your head to the RIGHT'
      case 'analyzing':
        return '🔍 Analyzing your skin...'
      case 'complete':
        return '✅ Analysis complete!'
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
            {currentStep === 'ready' ? 'Enhanced Face Scan' : 'Scanning Your Face'}
          </h1>
          
          <p className="text-xl font-semibold text-green-700 mb-2">
            {getInstructionText()}
          </p>
          
          <p className="text-lg text-muted-foreground">
            {currentStep === 'ready' && 'Get comprehensive skin analysis with visual feedback'}
            {currentStep === 'center' && 'Step 1 of 3: Front view'}
            {currentStep === 'left' && 'Step 2 of 3: Left profile'}
            {currentStep === 'right' && 'Step 3 of 3: Right profile'}
            {currentStep === 'analyzing' && 'Processing your scan...'}
            {currentStep === 'complete' && 'Preparing your results...'}
          </p>
        </div>

        {/* Progress Indicator */}
        {isCameraActive && (
          <div className="mb-6 bg-white/80 backdrop-blur-sm rounded-xl p-4 border-2 border-green-100">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-green-700">Capture Progress</span>
              <span className="text-sm font-bold text-green-600">{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-green-100 rounded-full h-3 overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-green-500 to-green-600 transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Countdown Display */}
        {countdown !== null && isCameraActive && (
          <div className="mb-6 text-center">
            <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-gradient-to-br from-green-500 to-green-600 shadow-2xl">
              <div className="text-7xl font-bold text-white animate-pulse">
                {countdown}
              </div>
            </div>
          </div>
        )}

        {/* Main Card */}
        <Card className="bg-white/90 backdrop-blur-sm border-2 border-green-100 shadow-2xl">
          <CardContent className="pt-6">
            <div className="space-y-6">
              {/* Camera/Preview Area with Enhanced Avatar */}
              <div className="relative rounded-2xl overflow-hidden border-4 border-green-300 bg-black shadow-2xl w-full aspect-video flex items-center justify-center">
                {isCameraActive ? (
                  <>
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      muted
                      className="w-full h-full object-cover"
                      style={{ transform: 'scaleX(-1)' }}
                      onLoadStart={() => console.log('🎥 [VIDEO] Load start')}
                      onLoadedData={() => console.log('🎥 [VIDEO] Loaded data')}
                      onCanPlay={() => console.log('🎥 [VIDEO] Can play')}
                      onPlay={() => console.log('🎥 [VIDEO] Playing')}
                      onError={(e) => console.error('🎥 [VIDEO] Error:', e)}
                    />
                    
                    {/* Enhanced Face Avatar Overlay */}
                    {currentImage && (
                      <div className="absolute inset-0 flex items-center justify-center">
                        <FaceScanAvatar
                          src={currentImage}
                          alt="Face scan preview"
                          className="w-64 h-64"
                          isScanning={isScanning}
                          scanProgress={progress}
                          analysisResults={analysisResults}
                          onScanComplete={handleScanComplete}
                        />
                      </div>
                    )}
                    
                    {/* Debug info */}
                    <div className="absolute top-2 left-2 bg-black/70 text-white text-xs p-2 rounded">
                      <div>Camera: {isCameraActive ? 'Active' : 'Inactive'}</div>
                      <div>Stream: {stream ? 'Connected' : 'None'}</div>
                      <div>Scanning: {isScanning ? 'Yes' : 'No'}</div>
                      <div>Results: {analysisResults ? 'Available' : 'None'}</div>
                    </div>
                    
                    {/* Face Guide Overlay */}
                    {currentStep === 'center' && (
                      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <div className="w-64 h-80 border-4 border-green-400 rounded-full opacity-60"></div>
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

              {/* Hidden canvas for frame capture */}
              <canvas ref={canvasRef} className="hidden" />

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3">
                {!isCameraActive && currentStep === 'ready' && (
                  <>
                    <Button 
                      onClick={async () => {
                        await startCamera()
                        setTimeout(() => startScan(), 500)
                      }}
                      className="flex-1 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white font-bold border-2 border-green-700 shadow-lg h-14 text-base"
                    >
                      <Video className="w-5 h-5 mr-2" />
                      Start Enhanced Scan
                    </Button>
                    
                    <Button 
                      onClick={handleSkip}
                      variant="outline"
                      className="flex-1 border-2 border-green-600 text-green-600 hover:bg-green-50 font-semibold h-14 text-base"
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
                    className="w-full border-2 border-red-500 text-red-500 hover:bg-red-50 font-semibold h-14 text-base"
                  >
                    <VideoOff className="w-5 h-5 mr-2" />
                    Stop Scan
                  </Button>
                )}
                
                {currentStep === 'complete' && (
                  <Button 
                    disabled
                    className="w-full bg-gradient-to-r from-yellow-500 to-yellow-400 text-white font-bold h-14 text-base"
                  >
                    <CheckCircle2 className="w-5 h-5 mr-2" />
                    Redirecting to Dashboard...
                  </Button>
                )}
              </div>

              {/* Analysis Results Preview */}
              {analysisResults && (
                <div className="bg-green-50 border-2 border-green-200 rounded-xl p-4">
                  <h3 className="font-bold text-green-800 mb-2">Analysis Results Preview</h3>
                  <div className="space-y-2">
                    {analysisResults.conditions.map((condition, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <div className="w-3 h-3 rounded-full bg-red-500"></div>
                        <span className="text-sm font-medium text-green-700">
                          {condition.condition.replace('_', ' ')} ({Math.round(condition.confidence * 100)}% confidence)
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
