"use client"

import { useRef, useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Camera, Upload, AlertCircle, CheckCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface FaceCaptureProps {
  onImageCapture: (imageBlob: Blob) => void
  onImageUpload: (file: File) => void
  isProcessing?: boolean
}

export function FaceCapture({ onImageCapture, onImageUpload, isProcessing = false }: FaceCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [isCapturing, setIsCapturing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Initialize camera
  useEffect(() => {
    const initializeCamera = async () => {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'user'
          }
        })
        setStream(mediaStream)
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream
        }
      } catch (err) {
        setError("Camera access denied. Please allow camera access and try again.")
        console.error("Camera error:", err)
      }
    }

    initializeCamera()

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return

    const video = videoRef.current
    const canvas = canvasRef.current
    const context = canvas.getContext('2d')

    if (!context) return

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    // Draw current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height)

    // Convert to blob
    canvas.toBlob((blob) => {
      if (blob) {
        setIsCapturing(true)
        onImageCapture(blob)
        // Reset after a brief delay
        setTimeout(() => setIsCapturing(false), 1000)
      }
    }, 'image/jpeg', 0.9)
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file')
        return
      }

      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB')
        return
      }

      setError(null)
      onImageUpload(file)
    }
  }

  return (
    <div className="space-y-4">
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Camera Preview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Camera className="w-5 h-5" />
            Face Capture
          </CardTitle>
          <CardDescription>
            Position your face in the frame and click capture
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-64 object-cover rounded-lg border"
            />
            <canvas ref={canvasRef} className="hidden" />
            
            {/* Capture Overlay */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-48 h-48 border-2 border-white border-dashed rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">Position face here</span>
              </div>
            </div>
          </div>

          <div className="flex gap-2 mt-4">
            <Button
              onClick={capturePhoto}
              disabled={!stream || isProcessing || isCapturing}
              className="flex-1"
            >
              {isCapturing ? (
                <>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Captured!
                </>
              ) : (
                <>
                  <Camera className="w-4 h-4 mr-2" />
                  Capture Photo
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* File Upload Alternative */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Or Upload Image
          </CardTitle>
          <CardDescription>
            Upload a clear photo of your face instead
          </CardDescription>
        </CardHeader>
        <CardContent>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileUpload}
            className="hidden"
          />
          
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={isProcessing}
            variant="outline"
            className="w-full"
          >
            <Upload className="w-4 h-4 mr-2" />
            Choose Image File
          </Button>
          
          <p className="text-xs text-muted-foreground text-center mt-2">
            Supported: JPG, PNG, JPEG (max 10MB)
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
