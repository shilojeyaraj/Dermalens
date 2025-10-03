"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Camera, Upload, X, CheckCircle2 } from "lucide-react"

interface FaceUploadDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function FaceUploadDialog({ open, onOpenChange }: FaceUploadDialogProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

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
          <DialogTitle className="text-balance">Upload Face Photo or Video</DialogTitle>
          <DialogDescription className="text-pretty">
            Upload a clear photo or video of your face for personalized skincare analysis
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {!previewUrl ? (
            <div className="space-y-4">
              <div
                className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors cursor-pointer"
                onClick={() => fileInputRef.current?.click()}
              >
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                    <Camera className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">Click to upload</p>
                    <p className="text-xs text-muted-foreground">or drag and drop</p>
                  </div>
                  <p className="text-xs text-muted-foreground">PNG, JPG, MP4 or MOV (max. 10MB)</p>
                </div>
              </div>

              <input
                ref={fileInputRef}
                type="file"
                accept="image/*,video/*"
                onChange={handleFileSelect}
                className="hidden"
              />

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  className="flex-1 bg-transparent"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Choose File
                </Button>
              </div>
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
