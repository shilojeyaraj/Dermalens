"use client"

import { useEffect, useState } from "react"
import { Loader2, Sparkles, CheckCircle2 } from "lucide-react"

interface LoadingTransitionProps {
  message?: string
  onComplete?: () => void
  duration?: number
}

export function LoadingTransition({ 
  message = "Preparing your experience...", 
  onComplete,
  duration = 2000 
}: LoadingTransitionProps) {
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState(0)

  const steps = [
    "Saving your profile...",
    "Analyzing your preferences...",
    "Preparing face scan...",
    "Almost ready!"
  ]

  useEffect(() => {
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval)
          if (onComplete) {
            setTimeout(onComplete, 300)
          }
          return 100
        }
        return prev + 2
      })
    }, duration / 50)

    const stepInterval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev >= steps.length - 1) {
          clearInterval(stepInterval)
          return prev
        }
        return prev + 1
      })
    }, duration / steps.length)

    return () => {
      clearInterval(progressInterval)
      clearInterval(stepInterval)
    }
  }, [duration, onComplete, steps.length])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-white via-green-50 to-green-100">
      <div className="max-w-md w-full mx-4 text-center space-y-8">
        {/* Animated Icon */}
        <div className="relative inline-flex">
          <div className="absolute inset-0 bg-green-400 rounded-full blur-2xl opacity-50 animate-pulse"></div>
          <div className="relative w-24 h-24 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center shadow-2xl">
            {progress === 100 ? (
              <CheckCircle2 className="w-12 h-12 text-white animate-bounce" />
            ) : (
              <Loader2 className="w-12 h-12 text-white animate-spin" />
            )}
          </div>
        </div>

        {/* Progress Text */}
        <div className="space-y-4">
          <h2 className="text-3xl font-bold bg-gradient-to-r from-green-600 to-green-800 bg-clip-text text-transparent">
            {progress === 100 ? "All Set!" : steps[currentStep]}
          </h2>
          
          {/* Progress Bar */}
          <div className="w-full bg-green-100 rounded-full h-3 overflow-hidden shadow-inner">
            <div 
              className="h-full bg-gradient-to-r from-green-500 to-green-600 transition-all duration-300 ease-out rounded-full shadow-lg"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Percentage */}
          <p className="text-lg font-semibold text-green-700">
            {progress}%
          </p>
        </div>

        {/* Decorative Elements */}
        <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
          <Sparkles className="w-4 h-4 text-green-500 animate-pulse" />
          <span>Optimizing your experience</span>
          <Sparkles className="w-4 h-4 text-green-500 animate-pulse" />
        </div>
      </div>
    </div>
  )
}

