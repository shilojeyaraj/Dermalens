"use client"

import * as React from "react"
import { cn } from "../../lib/utils"

interface FaceScanAvatarProps {
  src?: string
  alt?: string
  className?: string
  isScanning?: boolean
  scanProgress?: number
  analysisResults?: {
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
  onScanComplete?: () => void
}

const FaceScanAvatar = React.forwardRef<HTMLDivElement, FaceScanAvatarProps>(
  ({ 
    src, 
    alt = "Face scan", 
    className, 
    isScanning = false,
    scanProgress = 0,
    analysisResults,
    onScanComplete,
    ...props 
  }, ref) => {
    const [showOverlay, setShowOverlay] = React.useState(false)
    const [scanLinePosition, setScanLinePosition] = React.useState(0)
    const scanLineRef = React.useRef<HTMLDivElement>(null)

    // Scan line animation
    React.useEffect(() => {
      if (isScanning) {
        setScanLinePosition(0)
        const interval = setInterval(() => {
          setScanLinePosition(prev => {
            if (prev >= 100) {
              clearInterval(interval)
              if (onScanComplete) {
                setTimeout(() => {
                  onScanComplete()
                  setShowOverlay(true)
                }, 500)
              }
              return 100
            }
            return prev + 2
          })
        }, 50)
        return () => clearInterval(interval)
      }
    }, [isScanning, onScanComplete])

    // Show overlay after scan completion
    React.useEffect(() => {
      if (analysisResults && analysisResults.conditions.length > 0) {
        const timer = setTimeout(() => setShowOverlay(true), 1000)
        return () => clearTimeout(timer)
      }
    }, [analysisResults])

    const getSeverityColor = (severity: string, confidence: number) => {
      const opacity = Math.min(confidence * 0.8 + 0.2, 1)
      
      switch (severity) {
        case "severe":
          return `rgba(220, 38, 38, ${opacity})` // Red
        case "moderate":
          return `rgba(245, 158, 11, ${opacity})` // Orange
        case "mild":
          return `rgba(34, 197, 94, ${opacity})` // Green
        default:
          return `rgba(156, 163, 175, ${opacity})` // Gray
      }
    }

    const getConditionIcon = (condition: string) => {
      switch (condition) {
        case "acne":
          return "🔴"
        case "dry_skin":
          return "💧"
        case "dark_circles":
          return "👁️"
        case "wrinkles":
          return "〰️"
        case "redness":
          return "🔴"
        default:
          return "📍"
      }
    }

    return (
      <div
        ref={ref}
        className={cn(
          "relative flex h-64 w-64 shrink-0 overflow-hidden rounded-full border-4 border-gray-200",
          "bg-gradient-to-br from-blue-50 to-purple-50",
          className
        )}
        {...props}
      >
        {/* Face Image */}
        {src && (
          <img
            src={src}
            alt={alt}
            className="h-full w-full object-cover rounded-full"
          />
        )}

        {/* Scan Line Animation */}
        {isScanning && (
          <div
            ref={scanLineRef}
            className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-blue-500 to-transparent shadow-lg"
            style={{
              top: `${scanLinePosition}%`,
              transform: 'translateY(-50%)',
              boxShadow: '0 0 20px rgba(59, 130, 246, 0.8)',
            }}
          >
            <div className="h-full w-full bg-gradient-to-r from-transparent via-white to-transparent animate-pulse" />
          </div>
        )}

        {/* Scan Progress Indicator */}
        {isScanning && (
          <div className="absolute top-4 left-4 right-4">
            <div className="bg-black/50 backdrop-blur-sm rounded-full px-3 py-1">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                <span className="text-white text-xs font-medium">
                  Scanning... {Math.round(scanLinePosition)}%
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Face Overlay with Issue Points */}
        {showOverlay && analysisResults && (
          <div className="absolute inset-0 pointer-events-none">
            {analysisResults.conditions.map((condition, index) => {
              const { x, y, radius } = condition.coordinates
              const severityColor = getSeverityColor(condition.severity, condition.confidence)
              const icon = getConditionIcon(condition.condition)
              
              return (
                <div
                  key={index}
                  className="absolute animate-fade-in"
                  style={{
                    left: `${x * 100}%`,
                    top: `${y * 100}%`,
                    transform: 'translate(-50%, -50%)',
                    animationDelay: `${index * 0.2}s`,
                  }}
                >
                  {/* Issue Point */}
                  <div
                    className="relative flex items-center justify-center"
                    style={{
                      width: `${radius * 200}px`,
                      height: `${radius * 200}px`,
                    }}
                  >
                    {/* Pulsing Background */}
                    <div
                      className="absolute inset-0 rounded-full animate-ping"
                      style={{
                        backgroundColor: severityColor,
                        opacity: 0.3,
                      }}
                    />
                    
                    {/* Main Point */}
                    <div
                      className="relative flex items-center justify-center rounded-full border-2 border-white shadow-lg"
                      style={{
                        width: `${Math.max(radius * 100, 20)}px`,
                        height: `${Math.max(radius * 100, 20)}px`,
                        backgroundColor: severityColor,
                      }}
                    >
                      <span className="text-white text-xs font-bold">
                        {icon}
                      </span>
                    </div>
                  </div>

                  {/* Condition Label */}
                  <div
                    className="absolute top-full left-1/2 transform -translate-x-1/2 mt-1"
                    style={{
                      animationDelay: `${index * 0.2 + 0.5}s`,
                    }}
                  >
                    <div className="bg-black/80 backdrop-blur-sm text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                      {condition.condition.replace('_', ' ')}
                      <div className="text-xs opacity-75">
                        {Math.round(condition.confidence * 100)}% confidence
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Scan Complete Indicator */}
        {!isScanning && showOverlay && (
          <div className="absolute inset-0 bg-black/20 backdrop-blur-sm rounded-full flex items-center justify-center">
            <div className="bg-green-500 text-white px-4 py-2 rounded-full text-sm font-medium animate-bounce">
              ✓ Analysis Complete
            </div>
          </div>
        )}
      </div>
    )
  }
)

FaceScanAvatar.displayName = "FaceScanAvatar"

export { FaceScanAvatar }
