"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Camera, Upload, X, CheckCircle2, Video, CameraOff } from "lucide-react"

interface FaceUploadDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function FaceUploadDialog({ open, onOpenChange }: FaceUploadDialogProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isCameraOpen, setIsCameraOpen] = useState(false)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
    }
  }

  const handleRemoveFile = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }
    setSelectedFile(null)
    setPreviewUrl(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'user',
          width: { ideal: 640 },
          height: { ideal: 480 }
        }
      })
      setStream(mediaStream)
      setIsCameraOpen(true)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
    } catch (error) {
      console.error('Error accessing camera:', error)
      alert('Unable to access camera. Please check permissions or try uploading a file instead.')
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
    setIsCameraOpen(false)
  }

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current
      const video = videoRef.current
      const context = canvas.getContext('2d')
      
      if (context) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        context.drawImage(video, 0, 0)
        
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' })
            setSelectedFile(file)
            const url = URL.createObjectURL(blob)
            setPreviewUrl(url)
            stopCamera()
          }
        }, 'image/jpeg', 0.8)
      }
    }
  }

  // Cleanup camera stream when dialog closes
  useEffect(() => {
    if (!open) {
      stopCamera()
    }
    return () => {
      stopCamera()
    }
  }, [open])

  const handleAnalyze = async () => {
    if (!selectedFile) return

    setIsAnalyzing(true)
    
    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch('http://localhost:8000/analyze-skin', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`)
      }

      const analysisResult = await response.json()
      
      // Store analysis results in localStorage for other components to use
      localStorage.setItem('skinAnalysis', JSON.stringify(analysisResult))
      
      // Show success and close
      setTimeout(() => {
        handleRemoveFile()
        onOpenChange(false)
        // Trigger a custom event to notify other components
        window.dispatchEvent(new CustomEvent('skinAnalysisComplete', { 
          detail: analysisResult 
        }))
      }, 1000)
      
    } catch (error) {
      console.error('Analysis error:', error)
      alert('Analysis failed. Please try again or check if the backend server is running.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-balance">Face Scan & Analysis</DialogTitle>
          <DialogDescription className="text-pretty">
            Take a photo with your camera or upload an image for personalized skincare analysis
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {!previewUrl && !isCameraOpen ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <Button
                  variant="outline"
                  className="h-20 flex flex-col items-center gap-2 bg-transparent"
                  onClick={startCamera}
                >
                  <Video className="w-6 h-6 text-primary" />
                  <span className="text-sm font-medium">Take Photo</span>
                </Button>
                <Button
                  variant="outline"
                  className="h-20 flex flex-col items-center gap-2 bg-transparent"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="w-6 h-6 text-primary" />
                  <span className="text-sm font-medium">Upload File</span>
                </Button>
              </div>

              <input
                ref={fileInputRef}
                type="file"
                accept="image/*,video/*"
                onChange={handleFileSelect}
                className="hidden"
              />

              <div className="text-center">
                <p className="text-xs text-muted-foreground">PNG, JPG, MP4 or MOV (max. 10MB)</p>
              </div>
            </div>
          ) : isCameraOpen ? (
            <div className="space-y-4">
              <div className="relative rounded-lg overflow-hidden bg-black">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  className="w-full h-64 object-cover"
                />
                <Button
                  variant="destructive"
                  size="icon"
                  className="absolute top-2 right-2 rounded-full w-8 h-8"
                  onClick={stopCamera}
                >
                  <CameraOff className="w-4 h-4" />
                </Button>
              </div>
              
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={stopCamera}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1"
                  onClick={capturePhoto}
                >
                  <Camera className="w-4 h-4 mr-2" />
                  Capture Photo
                </Button>
              </div>
              
              <canvas ref={canvasRef} className="hidden" />
            </div>
          ) : (
            <div className="space-y-4">
              <div className="relative rounded-lg overflow-hidden bg-muted">
                {selectedFile?.type.startsWith("video/") ? (
                  <video src={previewUrl} controls className="w-full h-64 object-cover" />
                ) : (
                  <img src={previewUrl || "/placeholder.svg"} alt="Face preview" className="w-full h-64 object-cover" />
                )}
                <Button
                  variant="destructive"
                  size="icon"
                  className="absolute top-2 right-2 rounded-full w-8 h-8"
                  onClick={handleRemoveFile}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>

              <div className="space-y-2">
                <Label className="text-sm text-muted-foreground">{selectedFile?.name}</Label>
                <Button className="w-full" onClick={handleAnalyze} disabled={isAnalyzing}>
                  {isAnalyzing ? (
                    <>
                      <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin mr-2" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="w-4 h-4 mr-2" />
                      Analyze Face
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}

          <div className="bg-muted/50 rounded-lg p-3 space-y-1">
            <p className="text-xs font-medium text-foreground">Tips for best results:</p>
            <ul className="text-xs text-muted-foreground space-y-1 list-disc list-inside">
              <li>Use good lighting</li>
              <li>Face the camera directly</li>
              <li>Remove makeup if possible</li>
              <li>Ensure your face is clearly visible</li>
            </ul>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
