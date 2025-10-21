"use client"

import { useState, useEffect, useRef } from "react"

interface FaceScanHUDProps {
  name?: string
  variant?: "wire" | "solid"
  accent?: string
  className?: string
  isScanning?: boolean
  isAnalyzing?: boolean
  onScanComplete?: () => void
  onAnalysisComplete?: (imageFile?: File) => void
}

export function FaceScanHUD({ 
  name = "USER", 
  variant = "wire", 
  accent = "#36f0ff", 
  className = "w-full h-[80vh]",
  isScanning = false,
  isAnalyzing = false,
  onScanComplete,
  onAnalysisComplete
}: FaceScanHUDProps) {
  const [scanProgress, setScanProgress] = useState(0)
  const [currentInstruction, setCurrentInstruction] = useState("")
  const [showResult, setShowResult] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [cameraError, setCameraError] = useState<string | null>(null)
  const [faceDetected, setFaceDetected] = useState(false)
  const [glassesDetected, setGlassesDetected] = useState(false)
  const [mouthCovered, setMouthCovered] = useState(false)
  const [capturedImage, setCapturedImage] = useState<File | null>(null)
  
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)

  const instructions = [
    "Position your face in the center",
    "Look straight ahead",
    "Turn your head to the left",
    "Turn your head to the right", 
    "Look straight ahead again",
    "Remove glasses if wearing any",
    "Keep still for final scan"
  ]

  // Initialize camera
  const initializeCamera = async () => {
    try {
      setCameraError(null)
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        }
      })
      
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        videoRef.current.play()
      }
    } catch (error) {
      console.error('Camera access error:', error)
      setCameraError('Unable to access camera. Please check permissions.')
    }
  }

  // Stop camera
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
  }

  // Capture image from video
  const captureImage = (): File | null => {
    if (!videoRef.current || !canvasRef.current) return null
    
    const canvas = canvasRef.current
    const video = videoRef.current
    const ctx = canvas.getContext('2d')
    
    if (!ctx) return null
    
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    ctx.drawImage(video, 0, 0)
    
    return new Promise<File | null>((resolve) => {
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], 'face-scan.jpg', { type: 'image/jpeg' })
          resolve(file)
        } else {
          resolve(null)
        }
      }, 'image/jpeg', 0.9)
    })
  }

  // Simple face detection simulation (in production, use a real face detection library)
  const detectFace = () => {
    // This is a simplified simulation - in production you'd use face-api.js or similar
    const hasFace = Math.random() > 0.3 // 70% chance of detecting face
    const hasGlasses = Math.random() > 0.8 // 20% chance of detecting glasses
    const hasMouthCovered = Math.random() > 0.9 // 10% chance of mouth covered
    
    setFaceDetected(hasFace)
    setGlassesDetected(hasGlasses)
    setMouthCovered(hasMouthCovered)
    
    return { hasFace, hasGlasses, hasMouthCovered }
  }

  // Apple-style success sound effect
  const playSuccessSound = () => {
    try {
      // Create audio context if it doesn't exist
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
      }
      
      const audioContext = audioContextRef.current
      const oscillator1 = audioContext.createOscillator()
      const oscillator2 = audioContext.createOscillator()
      const gainNode = audioContext.createGain()
      
      // Connect nodes
      oscillator1.connect(gainNode)
      oscillator2.connect(gainNode)
      gainNode.connect(audioContext.destination)
      
      // Set frequencies for Apple-like success sound (ascending major third)
      oscillator1.frequency.setValueAtTime(523.25, audioContext.currentTime) // C5
      oscillator2.frequency.setValueAtTime(659.25, audioContext.currentTime) // E5
      
      // Set wave types
      oscillator1.type = 'sine'
      oscillator2.type = 'sine'
      
      // Create envelope for smooth sound
      gainNode.gain.setValueAtTime(0, audioContext.currentTime)
      gainNode.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + 0.01)
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3)
      
      // Play the sound
      oscillator1.start(audioContext.currentTime)
      oscillator2.start(audioContext.currentTime)
      oscillator1.stop(audioContext.currentTime + 0.3)
      oscillator2.stop(audioContext.currentTime + 0.3)
      
    } catch (error) {
      console.log('Audio not available:', error)
    }
  }

  useEffect(() => {
    if (isScanning) {
      setScanProgress(0)
      setShowResult(false)
      setAnalysisProgress(0)
      setFaceDetected(false)
      setGlassesDetected(false)
      setMouthCovered(false)
      
      // Initialize camera when scanning starts
      initializeCamera()
      
      const instructionInterval = setInterval(() => {
        setCurrentInstruction((prev) => {
          const currentIndex = instructions.indexOf(prev)
          const nextIndex = (currentIndex + 1) % instructions.length
          return instructions[nextIndex]
        })
      }, 2000)

      const progressInterval = setInterval(() => {
        setScanProgress((prev) => {
          if (prev >= 100) {
            clearInterval(progressInterval)
            clearInterval(instructionInterval)
            setShowResult(true)
            
            // Play success sound when scan completes
            playSuccessSound()
            
            // Capture image when scan completes
            const imageFile = captureImage()
            setCapturedImage(imageFile)
            
            setTimeout(() => {
              onScanComplete?.()
            }, 2000)
            return 100
          }
          return prev + 2
        })
      }, 100)

      // Face detection during scanning
      const detectionInterval = setInterval(() => {
        if (scanProgress > 20 && scanProgress < 80) {
          detectFace()
        }
      }, 500)

      return () => {
        clearInterval(instructionInterval)
        clearInterval(progressInterval)
        clearInterval(detectionInterval)
        stopCamera()
      }
    }
  }, [isScanning, onScanComplete])

  // Analysis effect
  useEffect(() => {
    if (isAnalyzing) {
      setAnalysisProgress(0)
      
      const analysisInterval = setInterval(() => {
        setAnalysisProgress((prev) => {
          if (prev >= 100) {
            clearInterval(analysisInterval)
            setTimeout(() => {
              onAnalysisComplete?.(capturedImage || undefined)
            }, 1000)
            return 100
          }
          return prev + 1.5
        })
      }, 50)

      return () => {
        clearInterval(analysisInterval)
      }
    }
  }, [isAnalyzing, onAnalysisComplete, capturedImage])

  return (
    <div className={`relative ${className}`} style={{ "--accent": accent } as React.CSSProperties}>
      {/* Camera Video (hidden) */}
      <video
        ref={videoRef}
        className="hidden"
        autoPlay
        playsInline
        muted
      />
      
      {/* Hidden Canvas for Image Capture */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Camera Error Alert */}
      {cameraError && (
        <div className="absolute top-8 left-0 right-0 z-30 text-center">
          <div className="bg-red-900/90 backdrop-blur-sm rounded-lg px-6 py-4 mx-4 inline-block">
            <div className="text-white text-lg font-semibold mb-2">
              Camera Error
            </div>
            <div className="text-red-300 text-sm">
              {cameraError}
            </div>
          </div>
        </div>
      )}

      {/* Detection Alerts */}
      {isScanning && glassesDetected && (
        <div className="absolute top-20 left-0 right-0 z-25 text-center">
          <div className="bg-amber-900/90 backdrop-blur-sm rounded-lg px-6 py-4 mx-4 inline-block">
            <div className="text-white text-lg font-semibold mb-2">
              ⚠️ Glasses Detected
            </div>
            <div className="text-amber-300 text-sm">
              Please remove glasses for better analysis
            </div>
          </div>
        </div>
      )}

      {isScanning && mouthCovered && (
        <div className="absolute top-20 left-0 right-0 z-25 text-center">
          <div className="bg-amber-900/90 backdrop-blur-sm rounded-lg px-6 py-4 mx-4 inline-block">
            <div className="text-white text-lg font-semibold mb-2">
              ⚠️ Mouth Covered
            </div>
            <div className="text-amber-300 text-sm">
              Please remove any face covering
            </div>
          </div>
        </div>
      )}

      {/* Face Detection Status */}
      {isScanning && faceDetected && !glassesDetected && !mouthCovered && (
        <div className="absolute top-20 left-0 right-0 z-25 text-center">
          <div className="bg-green-900/90 backdrop-blur-sm rounded-lg px-6 py-4 mx-4 inline-block">
            <div className="text-white text-lg font-semibold mb-2">
              ✅ Face Detected
            </div>
            <div className="text-green-300 text-sm">
              Good positioning, continue scanning
            </div>
          </div>
        </div>
      )}

      {/* Scanning Instructions Overlay */}
      {isScanning && !showResult && (
        <div className="absolute top-8 left-0 right-0 z-20 text-center">
          <div className="bg-black/80 backdrop-blur-sm rounded-lg px-6 py-4 mx-4 inline-block">
            <div className="text-white text-lg font-semibold mb-2">
              {currentInstruction}
            </div>
            <div className="text-green-300 text-sm mb-2">
              Progress: {scanProgress}%
            </div>
            
            {/* Scanning frequency indicator */}
            <div className="flex items-center justify-center gap-2 mb-2">
              <div className="text-xs text-green-300">SCANNING</div>
              <div className="flex gap-1">
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    className="w-1 h-3 bg-green-400 rounded-full"
                    style={{
                      animation: `pulse 0.8s ease-in-out infinite`,
                      animationDelay: `${i * 0.1}s`
                    }}
                  />
                ))}
              </div>
              <div className="text-xs text-green-300">ACTIVE</div>
            </div>
            
            <div className="w-48 h-1 bg-gray-700 rounded-full mt-2 mx-auto">
              <div 
                className="h-full bg-gradient-to-r from-green-400 to-emerald-500 rounded-full transition-all duration-200"
                style={{ width: `${scanProgress}%` }}
              />
            </div>
            
            {/* Scanning frequency display */}
            <div className="text-xs text-green-300 mt-2">
              Frequency: {Math.floor(scanProgress * 0.5 + 50)}Hz
            </div>
          </div>
        </div>
      )}

      {/* Analysis Overlay */}
      {isAnalyzing && (
        <div className="absolute top-8 left-0 right-0 z-20 text-center">
          <div className="bg-black/80 backdrop-blur-sm rounded-lg px-6 py-4 mx-4 inline-block">
            <div className="text-white text-lg font-semibold mb-2">
              Analyzing Scan...
            </div>
            <div className="text-green-300 text-sm">
              Processing facial data: {Math.round(analysisProgress)}%
            </div>
            <div className="w-48 h-1 bg-gray-700 rounded-full mt-2 mx-auto">
              <div 
                className="h-full bg-gradient-to-r from-green-400 to-emerald-500 rounded-full transition-all duration-200"
                style={{ width: `${analysisProgress}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* HUD SVG */}
      <div className="w-full h-full flex items-center justify-center">
        <svg 
          viewBox="0 0 1000 1000" 
          className="w-full h-full"
          style={{ filter: "drop-shadow(0 0 20px var(--accent))" }}
        >
          {/* Glow filter */}
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge> 
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          {/* Outer guide */}
          <g className="hud" filter="url(#glow)">
            <circle 
              cx="500" 
              cy="500" 
              r="410" 
              className="wire dim" 
              fill="none" 
              stroke="var(--accent)" 
              strokeWidth="1" 
              opacity="0.3"
            />
            <circle 
              cx="500" 
              cy="500" 
              r="420" 
              className="wire ring-dashed" 
              fill="none" 
              stroke="var(--accent)" 
              strokeWidth="2" 
              strokeDasharray="10,5"
              opacity="0.6"
            />
            <circle 
              cx="500" 
              cy="500" 
              r="330" 
              className="wire dim" 
              fill="none" 
              stroke="var(--accent)" 
              strokeWidth="1" 
              opacity="0.2"
            />
            <circle 
              cx="500" 
              cy="500" 
              r="335" 
              className="wire ticks" 
              fill="none" 
              stroke="var(--accent)" 
              strokeWidth="1" 
              strokeDasharray="2,8"
              opacity="0.4"
            />
          </g>

          {/* Scanning grid overlay */}
          {isScanning && (
            <g className="scan-grid" opacity="0.3">
              <defs>
                <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
                  <path d="M 50 0 L 0 0 0 50" fill="none" stroke="var(--accent)" strokeWidth="0.5"/>
                </pattern>
              </defs>
              <rect width="1000" height="1000" fill="url(#grid)" />
            </g>
          )}

          {/* Scanning status indicators */}
          {isScanning && (
            <g className="scan-indicators">
              {/* Top scanning indicator */}
              <rect x="450" y="200" width="100" height="4" fill="var(--accent)" opacity="0.8">
                <animate attributeName="opacity" values="0.3;1;0.3" dur="1s" repeatCount="indefinite"/>
              </rect>
              
              {/* Side scanning indicators */}
              <rect x="150" y="400" width="4" height="200" fill="var(--accent)" opacity="0.6">
                <animate attributeName="opacity" values="0.2;0.8;0.2" dur="1.5s" repeatCount="indefinite"/>
              </rect>
              <rect x="846" y="400" width="4" height="200" fill="var(--accent)" opacity="0.6">
                <animate attributeName="opacity" values="0.2;0.8;0.2" dur="1.5s" repeatCount="indefinite"/>
              </rect>
              
              {/* Bottom scanning indicator */}
              <rect x="400" y="750" width="200" height="4" fill="var(--accent)" opacity="0.7">
                <animate attributeName="opacity" values="0.4;1;0.4" dur="0.8s" repeatCount="indefinite"/>
              </rect>
            </g>
          )}

          {/* Corner brackets */}
          <g className="corner" stroke="var(--accent)" strokeWidth="3" fill="none">
            <path d="M120 350 v-60 h60" opacity="0.8"/>
            <path d="M880 350 v-60 h-60" opacity="0.8"/>
            <path d="M120 650 v60 h60" opacity="0.8"/>
            <path d="M880 650 v60 h-60" opacity="0.8"/>
          </g>

          {/* Scanning line */}
          <g className="scanner">
            <line 
              x1="140" 
              y1="620" 
              x2="860" 
              y2="620" 
              className="scan" 
              stroke="var(--accent)" 
              strokeWidth="3"
              opacity={isScanning ? "0.8" : "0.3"}
            >
              {isScanning && (
                <animate
                  attributeName="opacity"
                  values="0.3;1;0.3"
                  dur="1s"
                  repeatCount="indefinite"
                />
              )}
            </line>
          </g>

          {/* Live scanning line - moves down during scanning */}
          {isScanning && (
            <g className="live-scanner">
              <defs>
                <linearGradient id="scanGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="var(--accent)" stopOpacity="0"/>
                  <stop offset="50%" stopColor="var(--accent)" stopOpacity="1"/>
                  <stop offset="100%" stopColor="var(--accent)" stopOpacity="0"/>
                </linearGradient>
                <filter id="scanGlow" x="-50%" y="-50%" width="200%" height="200%">
                  <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                  <feMerge> 
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>
              
              {/* Main scanning line */}
              <line 
                x1="200" 
                y1={220 + (scanProgress / 100) * 540} 
                x2="800" 
                y2={220 + (scanProgress / 100) * 540} 
                stroke="url(#scanGradient)" 
                strokeWidth="6"
                opacity="0.9"
                filter="url(#scanGlow)"
              >
                <animate
                  attributeName="opacity"
                  values="0.2;1;0.2"
                  dur="1.2s"
                  repeatCount="indefinite"
                />
              </line>
              
              {/* Secondary scanning line for depth effect */}
              <line 
                x1="220" 
                y1={220 + (scanProgress / 100) * 540} 
                x2="780" 
                y2={220 + (scanProgress / 100) * 540} 
                stroke="var(--accent)" 
                strokeWidth="2"
                opacity="0.6"
              >
                <animate
                  attributeName="opacity"
                  values="0.1;0.8;0.1"
                  dur="0.8s"
                  repeatCount="indefinite"
                />
              </line>
              
              {/* Scanning particles effect */}
              <g className="scan-particles">
                {[...Array(5)].map((_, i) => (
                  <circle
                    key={i}
                    cx={200 + (i * 150)}
                    cy={220 + (scanProgress / 100) * 540}
                    r="3"
                    fill="var(--accent)"
                    opacity="0.8"
                  >
                    <animate
                      attributeName="r"
                      values="1;4;1"
                      dur="1.5s"
                      repeatCount="indefinite"
                      begin={`${i * 0.2}s`}
                    />
                    <animate
                      attributeName="opacity"
                      values="0.3;1;0.3"
                      dur="1.5s"
                      repeatCount="indefinite"
                      begin={`${i * 0.2}s`}
                    />
                  </circle>
                ))}
              </g>
            </g>
          )}

          {/* Analysis scanning line - moves down the face */}
          {isAnalyzing && (
            <g className="analysis-scanner">
              <defs>
                <linearGradient id="analysisGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#16a34a" stopOpacity="0"/>
                  <stop offset="50%" stopColor="#16a34a" stopOpacity="1"/>
                  <stop offset="100%" stopColor="#16a34a" stopOpacity="0"/>
                </linearGradient>
              </defs>
              
              <line 
                x1="200" 
                y1={220 + (analysisProgress / 100) * 540} 
                x2="800" 
                y2={220 + (analysisProgress / 100) * 540} 
                stroke="url(#analysisGradient)" 
                strokeWidth="4"
                opacity="0.9"
                filter="url(#glow)"
              >
                <animate
                  attributeName="opacity"
                  values="0.3;1;0.3"
                  dur="0.8s"
                  repeatCount="indefinite"
                />
              </line>
            </g>
          )}

          {/* Face graphic */}
          {variant === 'wire' ? (
            <g className="bob" strokeLinejoin="round" strokeLinecap="round" fill="none">
              {/* Outline */}
              <path 
                className="wire" 
                d="M500 220 C430 220, 360 270, 340 360 C320 450, 350 590, 500 760 C650 590, 680 450, 660 360 C640 270, 570 220, 500 220 Z"
                stroke="var(--accent)" 
                strokeWidth="2"
              />

              {/* Problem Areas - Red Dots (shown during analysis) */}
              {isAnalyzing && (
                <g className="problem-areas">
                  {/* Forehead acne */}
                  <circle cx="500" cy="280" r="8" fill="#ff4444" opacity="0.8">
                    <animate attributeName="opacity" values="0.3;1;0.3" dur="1.5s" repeatCount="indefinite"/>
                  </circle>
                  <text x="500" y="265" textAnchor="middle" fill="#ff4444" fontSize="12" fontWeight="bold">Acne</text>
                  
                  {/* Left cheek dark spot */}
                  <circle cx="420" cy="450" r="6" fill="#ff4444" opacity="0.8">
                    <animate attributeName="opacity" values="0.3;1;0.3" dur="1.2s" repeatCount="indefinite"/>
                  </circle>
                  <text x="420" y="440" textAnchor="middle" fill="#ff4444" fontSize="10" fontWeight="bold">Dark Spot</text>
                  
                  {/* Right cheek dryness */}
                  <circle cx="580" cy="480" r="7" fill="#ff4444" opacity="0.8">
                    <animate attributeName="opacity" values="0.3;1;0.3" dur="1.8s" repeatCount="indefinite"/>
                  </circle>
                  <text x="580" y="470" textAnchor="middle" fill="#ff4444" fontSize="10" fontWeight="bold">Dryness</text>
                  
                  {/* Chin area */}
                  <circle cx="500" cy="620" r="5" fill="#ff4444" opacity="0.8">
                    <animate attributeName="opacity" values="0.3;1;0.3" dur="1.4s" repeatCount="indefinite"/>
                  </circle>
                  <text x="500" y="610" textAnchor="middle" fill="#ff4444" fontSize="10" fontWeight="bold">Irritation</text>
                </g>
              )}

              {/* Cheek mesh */}
              <polyline 
                className="wire dim" 
                points="380,430 420,470 500,520 580,470 620,430"
                stroke="var(--accent)" 
                strokeWidth="1" 
                opacity="0.4"
              />
              <polyline 
                className="wire dim" 
                points="360,500 420,520 500,540 580,520 640,500"
                stroke="var(--accent)" 
                strokeWidth="1" 
                opacity="0.4"
              />
              <polyline 
                className="wire dim" 
                points="350,560 420,560 500,565 580,560 650,560"
                stroke="var(--accent)" 
                strokeWidth="1" 
                opacity="0.4"
              />

              {/* Nose ridge */}
              <polyline 
                className="wire" 
                points="500,300 495,360 500,430 505,500"
                stroke="var(--accent)" 
                strokeWidth="2"
              />
              <polyline 
                className="wire dim" 
                points="470,330 500,360 530,330"
                stroke="var(--accent)" 
                strokeWidth="1" 
                opacity="0.4"
              />
              <polyline 
                className="wire dim" 
                points="470,420 500,445 530,420"
                stroke="var(--accent)" 
                strokeWidth="1" 
                opacity="0.4"
              />

              {/* Eyes */}
              <polyline 
                className="wire" 
                points="410,380 450,390 410,400"
                stroke="var(--accent)" 
                strokeWidth="2"
              />
              <polyline 
                className="wire" 
                points="590,380 550,390 590,400"
                stroke="var(--accent)" 
                strokeWidth="2"
              />
              <line 
                className="wire dim" 
                x1="430" 
                y1="410" 
                x2="470" 
                y2="410"
                stroke="var(--accent)" 
                strokeWidth="1" 
                opacity="0.4"
              />
              <line 
                className="wire dim" 
                x1="530" 
                y1="410" 
                x2="570" 
                y2="410"
                stroke="var(--accent)" 
                strokeWidth="1" 
                opacity="0.4"
              />

              {/* Mouth / chin mesh */}
              <polyline 
                className="wire" 
                points="440,590 500,600 560,590"
                stroke="var(--accent)" 
                strokeWidth="2"
              />
              <polyline 
                className="wire dim" 
                points="420,620 500,635 580,620"
                stroke="var(--accent)" 
                strokeWidth="1" 
                opacity="0.4"
              />
              <polyline 
                className="wire dim" 
                points="440,660 500,685 560,660"
                stroke="var(--accent)" 
                strokeWidth="1" 
                opacity="0.4"
              />
            </g>
          ) : (
            <g className="bob">
              {/* Solid black silhouette with a faint accent stroke */}
              <path 
                d="M500 220 C430 220, 360 270, 340 360 C320 450, 350 590, 500 760 C650 590, 680 450, 660 360 C640 270, 570 220, 500 220 Z"
                fill="#000" 
                stroke="var(--accent)" 
                strokeWidth="1.4"
              />
            </g>
          )}
        </svg>
      </div>

      {/* Result Label */}
      {showResult && (
        <div className="absolute bottom-[7vh] left-0 right-0 text-center select-none animate-fade-in">
          <div className="uppercase tracking-[0.12em] font-semibold opacity-85 drop-shadow-[0_0_8px_var(--accent)]">
            <div className="text-[clamp(14px,1.6vw,18px)] animate-pulse text-green-400">
              Face Detected
            </div>
            <div className="text-[clamp(18px,2.2vw,28px)] text-[#7af3ff]">
              "{name}"
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
