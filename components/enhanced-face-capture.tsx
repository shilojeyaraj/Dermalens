"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  Camera, 
  CheckCircle, 
  AlertCircle, 
  RotateCcw, 
  RotateCw, 
  Eye, 
  Shield,
  Clock,
  Smile,
  ArrowLeft,
  ArrowRight,
  ArrowUp
} from "lucide-react"

interface CaptureSession {
  id: string
  angle: 'front' | 'left' | 'right'
  images: string[]
  timestamp: Date
  accessories: {
    glasses: boolean
    hat: boolean
    faceCovering: boolean
    mask: boolean
  }
}

interface EnhancedFaceCaptureProps {
  onCaptureComplete: (sessions: CaptureSession[]) => void
  onError: (error: string) => void
}

export function EnhancedFaceCapture({ onCaptureComplete, onError }: EnhancedFaceCaptureProps) {
  const [isCapturing, setIsCapturing] = useState(false)
  const [currentStep, setCurrentStep] = useState<'front' | 'left' | 'right' | 'complete'>('front')
  const [captureProgress, setCaptureProgress] = useState(0)
  const [countdown, setCountdown] = useState(0)
  const [capturedSessions, setCapturedSessions] = useState<CaptureSession[]>([])
  const [currentSession, setCurrentSession] = useState<CaptureSession | null>(null)
  const [detectedAccessories, setDetectedAccessories] = useState({
    glasses: false,
    hat: false,
    faceCovering: false,
    mask: false
  })

  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const stepInstructions = {
    front: {
      title: "Front View",
      instruction: "Look directly at the camera and stay still",
      icon: <ArrowUp className="w-6 h-6" />,
      description: "We'll capture your face from the front for the main analysis"
    },
    left: {
      title: "Left Profile", 
      instruction: "Turn your head to the left (your left)",
      icon: <ArrowLeft className="w-6 h-6" />,
      description: "This helps us see your skin from different angles"
    },
    right: {
      title: "Right Profile",
      instruction: "Turn your head to the right (your right)", 
      icon: <ArrowRight className="w-6 h-6" />,
      description: "Final angle to complete the analysis"
    }
  }

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { 
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        }
      })
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        streamRef.current = stream
      }
    } catch (error) {
      onError("Failed to access camera. Please ensure camera permissions are granted.")
    }
  }, [onError])

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
  }, [])

  const detectAccessories = (imageData: string): Promise<typeof detectedAccessories> => {
    return new Promise((resolve) => {
      // Simulate AI detection - in real implementation, this would call your backend
      setTimeout(() => {
        const random = Math.random()
        resolve({
          glasses: random > 0.7,
          hat: random > 0.8,
          faceCovering: random > 0.9,
          mask: random > 0.85
        })
      }, 500)
    })
  }

  const captureImage = useCallback(async (): Promise<string> => {
    if (!videoRef.current || !canvasRef.current) return ""

    const canvas = canvasRef.current
    const video = videoRef.current
    const ctx = canvas.getContext('2d')
    
    if (!ctx) return ""

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    
    return canvas.toDataURL('image/jpeg', 0.8)
  }, [])

  const startCaptureSession = async (angle: 'front' | 'left' | 'right') => {
    setIsCapturing(true)
    setCurrentStep(angle)
    setCaptureProgress(0)
    
    const session: CaptureSession = {
      id: `${angle}-${Date.now()}`,
      angle,
      images: [],
      timestamp: new Date(),
      accessories: {
        glasses: false,
        hat: false,
        faceCovering: false,
        mask: false
      }
    }
    
    setCurrentSession(session)
    
    // Start countdown
    setCountdown(3)
    let count = 3
    const countdownInterval = setInterval(() => {
      count--
      setCountdown(count)
      if (count <= 0) {
        clearInterval(countdownInterval)
        startImageCapture(session)
      }
    }, 1000)
  }

  const startImageCapture = async (session: CaptureSession) => {
    const captureInterval = setInterval(async () => {
      const imageData = await captureImage()
      if (imageData) {
        const newImages = [...session.images, imageData]
        session.images = newImages
        
        setCurrentSession({ ...session })
        setCaptureProgress((newImages.length / 10) * 100)
        
        // Detect accessories on first image
        if (newImages.length === 1) {
          const accessories = await detectAccessories(imageData)
          session.accessories = accessories
          setDetectedAccessories(accessories)
          setCurrentSession({ ...session })
        }
        
        if (newImages.length >= 10) {
          clearInterval(captureInterval)
          completeCaptureSession(session)
        }
      }
    }, 300) // Capture every 300ms for 3 seconds (10 images)
  }

  const completeCaptureSession = (session: CaptureSession) => {
    setCapturedSessions(prev => [...prev, session])
    setIsCapturing(false)
    setCurrentSession(null)
    setCaptureProgress(0)
    
    // Move to next step or complete
    if (currentStep === 'front') {
      setTimeout(() => startCaptureSession('left'), 2000)
    } else if (currentStep === 'left') {
      setTimeout(() => startCaptureSession('right'), 2000)
    } else {
      setCurrentStep('complete')
      onCaptureComplete(capturedSessions)
    }
  }

  const retakeSession = (sessionId: string) => {
    const session = capturedSessions.find(s => s.id === sessionId)
    if (session) {
      startCaptureSession(session.angle)
    }
  }

  const startScan = () => {
    startCaptureSession('front')
  }

  useEffect(() => {
    startCamera()
    return () => stopCamera()
  }, [startCamera, stopCamera])

  const getAccessoryBadges = (accessories: typeof detectedAccessories) => {
    const badges = []
    if (accessories.glasses) badges.push({ label: "Glasses", variant: "secondary" as const })
    if (accessories.hat) badges.push({ label: "Hat", variant: "secondary" as const })
    if (accessories.faceCovering) badges.push({ label: "Face Covering", variant: "destructive" as const })
    if (accessories.mask) badges.push({ label: "Mask", variant: "destructive" as const })
    return badges
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Camera className="w-6 h-6" />
            Enhanced Face Scan
          </CardTitle>
          <CardDescription>
            We'll capture multiple angles of your face for comprehensive skin analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Camera Feed */}
          <div className="relative">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-64 object-cover rounded-lg border"
            />
            <canvas ref={canvasRef} className="hidden" />
            
            {/* Overlay for capture guidance */}
            {isCapturing && (
              <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                <div className="text-center text-white">
                  {countdown > 0 ? (
                    <div className="space-y-4">
                      <div className="text-6xl font-bold">{countdown}</div>
                      <div className="text-lg">Stay still...</div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="text-4xl">📸</div>
                      <div className="text-lg">Capturing images...</div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Current Step Instructions */}
          {!isCapturing && currentStep !== 'complete' && (
            <div className="text-center space-y-4">
              <div className="flex items-center justify-center gap-2 text-2xl">
                {stepInstructions[currentStep].icon}
                <span className="font-semibold">{stepInstructions[currentStep].title}</span>
              </div>
              <p className="text-lg">{stepInstructions[currentStep].instruction}</p>
              <p className="text-sm text-muted-foreground">
                {stepInstructions[currentStep].description}
              </p>
              <Button onClick={startScan} size="lg" className="mt-4">
                <Camera className="w-4 h-4 mr-2" />
                Start {stepInstructions[currentStep].title}
              </Button>
            </div>
          )}

          {/* Capture Progress */}
          {isCapturing && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">
                  Capturing {currentStep} view...
                </span>
                <span className="text-sm text-muted-foreground">
                  {Math.round(captureProgress)}%
                </span>
              </div>
              <Progress value={captureProgress} className="w-full" />
            </div>
          )}

          {/* Detected Accessories Alert */}
          {Object.values(detectedAccessories).some(Boolean) && (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-2">
                  <p>We detected the following accessories:</p>
                  <div className="flex flex-wrap gap-2">
                    {getAccessoryBadges(detectedAccessories).map((badge, index) => (
                      <Badge key={index} variant={badge.variant}>
                        {badge.label}
                      </Badge>
                    ))}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    For best results, please remove accessories if possible and retake the scan.
                  </p>
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* Captured Sessions */}
          {capturedSessions.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Captured Views</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {capturedSessions.map((session) => (
                  <Card key={session.id}>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm flex items-center gap-2">
                        {stepInstructions[session.angle].icon}
                        {stepInstructions[session.angle].title}
                        <Badge variant="outline">
                          {session.images.length} images
                        </Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      {session.images.length > 0 && (
                        <img
                          src={session.images[0]}
                          alt={`${session.angle} view`}
                          className="w-full h-24 object-cover rounded"
                        />
                      )}
                      {Object.values(session.accessories).some(Boolean) && (
                        <div className="flex flex-wrap gap-1">
                          {getAccessoryBadges(session.accessories).map((badge, index) => (
                            <Badge key={index} variant={badge.variant} className="text-xs">
                              {badge.label}
                            </Badge>
                          ))}
                        </div>
                      )}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => retakeSession(session.id)}
                        className="w-full"
                      >
                        <RotateCcw className="w-3 h-3 mr-1" />
                        Retake
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Completion */}
          {currentStep === 'complete' && (
            <div className="text-center space-y-4">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
              <h3 className="text-2xl font-semibold">Scan Complete!</h3>
              <p className="text-muted-foreground">
                We've captured {capturedSessions.reduce((total, session) => total + session.images.length, 0)} images 
                from {capturedSessions.length} different angles.
              </p>
              <Button size="lg" onClick={() => onCaptureComplete(capturedSessions)}>
                <Smile className="w-4 h-4 mr-2" />
                Analyze My Skin
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
