"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Camera, CheckCircle, X } from "lucide-react"
import { useRouter } from "next/navigation"

interface FaceScanPromptProps {
  onAccept: () => void
  onDecline: () => void
}

export function FaceScanPrompt({ onAccept, onDecline }: FaceScanPromptProps) {
  const [isLoading, setIsLoading] = useState(false)

  const handleAccept = async () => {
    setIsLoading(true)
    // Navigate to face scan page
    onAccept()
  }

  const handleDecline = () => {
    // Navigate to dashboard without face scan
    onDecline()
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="max-w-2xl w-full space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center">
              <Camera className="w-10 h-10 text-primary" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-foreground">Face Scan Available</h1>
          <p className="text-muted-foreground text-lg">
            Get personalized recommendations based on AI analysis of your skin
          </p>
        </div>

        {/* Benefits Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              What You'll Get
            </CardTitle>
            <CardDescription>
              Our AI-powered face scan provides detailed skin analysis
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-semibold text-primary">1</span>
                </div>
                <div>
                  <h4 className="font-semibold">Detailed Skin Analysis</h4>
                  <p className="text-sm text-muted-foreground">
                    AI identifies specific skin conditions and problem areas
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-semibold text-primary">2</span>
                </div>
                <div>
                  <h4 className="font-semibold">Visual Problem Mapping</h4>
                  <p className="text-sm text-muted-foreground">
                    See exactly where issues are located on your face
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-semibold text-primary">3</span>
                </div>
                <div>
                  <h4 className="font-semibold">Personalized Report</h4>
                  <p className="text-sm text-muted-foreground">
                    Get detailed recommendations with timeframes for improvement
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-semibold text-primary">4</span>
                </div>
                <div>
                  <h4 className="font-semibold">Enhanced Product Matching</h4>
                  <p className="text-sm text-muted-foreground">
                    More accurate product recommendations based on your actual skin
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>


        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4">
          <Button
            variant="outline"
            onClick={handleDecline}
            className="flex items-center gap-2 flex-1"
            disabled={isLoading}
          >
            <X className="w-4 h-4" />
            Skip Face Scan
          </Button>
          <Button
            onClick={handleAccept}
            className="flex items-center gap-2 flex-1"
            disabled={isLoading}
          >
            <Camera className="w-4 h-4" />
            {isLoading ? "Starting..." : "Start Face Scan"}
          </Button>
        </div>

        <p className="text-center text-sm text-muted-foreground">
          You can always complete a face scan later from your dashboard
        </p>
      </div>
    </div>
  )
}
