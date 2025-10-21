"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Sun, Moon, Clock, Droplets, Sparkles, Shield } from "lucide-react"
import { useState, useEffect } from "react"

interface SkincareRoutineDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

interface AnalysisResult {
  detected_conditions: string[]
  recommended_products: any[]
  skincare_routine: {
    morning_routine: any[]
    evening_routine: any[]
    total_products: number
    estimated_cost: number
    generated_at: string
  }
}

// Mock data representing backend-generated routine
const morningRoutine = [
  {
    step: 1,
    name: "Gentle Cleanser",
    product: "CeraVe Hydrating Facial Cleanser",
    duration: "1 min",
    icon: Droplets,
    instructions: "Massage onto damp skin in circular motions, then rinse with lukewarm water.",
  },
  {
    step: 2,
    name: "Vitamin C Serum",
    product: "The Ordinary Vitamin C Suspension 23%",
    duration: "30 sec",
    icon: Sparkles,
    instructions: "Apply 3-4 drops to face and neck. Wait for absorption before next step.",
  },
  {
    step: 3,
    name: "Moisturizer",
    product: "Neutrogena Hydro Boost Water Gel",
    duration: "30 sec",
    icon: Droplets,
    instructions: "Apply evenly to face and neck while skin is still slightly damp.",
  },
  {
    step: 4,
    name: "Sunscreen SPF 50",
    product: "La Roche-Posay Anthelios Melt-in Milk",
    duration: "1 min",
    icon: Shield,
    instructions: "Apply generously as the final step. Reapply every 2 hours if outdoors.",
  },
]

const eveningRoutine = [
  {
    step: 1,
    name: "Oil Cleanser",
    product: "DHC Deep Cleansing Oil",
    duration: "1 min",
    icon: Droplets,
    instructions: "Massage onto dry skin to dissolve makeup and sunscreen, then rinse.",
  },
  {
    step: 2,
    name: "Gentle Cleanser",
    product: "CeraVe Hydrating Facial Cleanser",
    duration: "1 min",
    icon: Droplets,
    instructions: "Second cleanse to remove remaining impurities. Rinse thoroughly.",
  },
  {
    step: 3,
    name: "Exfoliating Toner",
    product: "Paula's Choice 2% BHA Liquid Exfoliant",
    duration: "30 sec",
    icon: Sparkles,
    instructions: "Apply with cotton pad or hands. Use 2-3 times per week initially.",
  },
  {
    step: 4,
    name: "Retinol Serum",
    product: "The Ordinary Retinol 0.5% in Squalane",
    duration: "30 sec",
    icon: Sparkles,
    instructions: "Apply pea-sized amount. Start 2x per week, gradually increase frequency.",
  },
  {
    step: 5,
    name: "Night Cream",
    product: "CeraVe Skin Renewing Night Cream",
    duration: "1 min",
    icon: Moon,
    instructions: "Apply generously as the final step to lock in moisture overnight.",
  },
]

export function SkincareRoutineDialog({ open, onOpenChange }: SkincareRoutineDialogProps) {
  const [analysisData, setAnalysisData] = useState<AnalysisResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    // Load analysis data from localStorage
    const storedAnalysis = localStorage.getItem('skinAnalysis')
    if (storedAnalysis) {
      try {
        const parsed = JSON.parse(storedAnalysis)
        setAnalysisData(parsed)
      } catch (error) {
        console.error('Error parsing stored analysis:', error)
      }
    }

    // Listen for new analysis results
    const handleAnalysisComplete = (event: CustomEvent) => {
      setAnalysisData(event.detail)
    }

    window.addEventListener('skinAnalysisComplete', handleAnalysisComplete as EventListener)
    
    return () => {
      window.removeEventListener('skinAnalysisComplete', handleAnalysisComplete as EventListener)
    }
  }, [])

  // Use real data if available, otherwise fall back to mock data
  const routineData = analysisData?.skincare_routine || {
    morning_routine: morningRoutine,
    evening_routine: eveningRoutine,
    total_products: 8,
    estimated_cost: 150.00,
    generated_at: new Date().toISOString()
  }

  const detectedConditions = analysisData?.detected_conditions || ["Combination Skin", "Mild Acne", "Sensitive", "Dehydrated"]
  const recommendedProducts = analysisData?.recommended_products || []

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-primary" />
            Your Personalized Skincare Routine
          </DialogTitle>
          <p className="text-sm text-muted-foreground">
            Generated based on your skin analysis • Last updated: {analysisData ? new Date(routineData.generated_at).toLocaleDateString() : 'Today'}
          </p>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* Skin Analysis Summary */}
          <div className="bg-muted/50 rounded-lg p-4">
            <h3 className="font-semibold mb-2">Skin Analysis Summary</h3>
            <div className="flex flex-wrap gap-2">
              {detectedConditions.map((condition, index) => (
                <Badge key={index} variant="secondary">
                  {condition.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </Badge>
              ))}
            </div>
            <p className="text-sm text-muted-foreground mt-3">
              Your routine focuses on addressing {detectedConditions.length > 0 ? detectedConditions.join(', ') : 'your skin concerns'} 
              with {routineData.total_products} recommended products (estimated cost: ${routineData.estimated_cost.toFixed(2)}).
            </p>
          </div>

          {/* Morning Routine */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Sun className="w-5 h-5 text-amber-500" />
              <h3 className="text-xl font-semibold">Morning Routine</h3>
              <Badge variant="outline" className="ml-auto">
                <Clock className="w-3 h-3 mr-1" />
                ~5 minutes
              </Badge>
            </div>
            <div className="space-y-4">
              {routineData.morning_routine.map((item) => {
                const Icon = item.icon || Droplets
                return (
                  <div
                    key={item.step}
                    className="flex gap-4 p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <Icon className="w-5 h-5 text-primary" />
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2 mb-1">
                        <div>
                          <span className="text-xs font-semibold text-muted-foreground">STEP {item.step}</span>
                          <h4 className="font-semibold text-foreground">{item.name}</h4>
                        </div>
                        <Badge variant="secondary" className="text-xs">
                          {item.duration}
                        </Badge>
                      </div>
                      <p className="text-sm font-medium text-primary mb-1">{item.product}</p>
                      <p className="text-sm text-muted-foreground">{item.instructions}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          <Separator />

          {/* Evening Routine */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Moon className="w-5 h-5 text-indigo-500" />
              <h3 className="text-xl font-semibold">Evening Routine</h3>
              <Badge variant="outline" className="ml-auto">
                <Clock className="w-3 h-3 mr-1" />
                ~7 minutes
              </Badge>
            </div>
            <div className="space-y-4">
              {routineData.evening_routine.map((item) => {
                const Icon = item.icon || Moon
                return (
                  <div
                    key={item.step}
                    className="flex gap-4 p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <Icon className="w-5 h-5 text-primary" />
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2 mb-1">
                        <div>
                          <span className="text-xs font-semibold text-muted-foreground">STEP {item.step}</span>
                          <h4 className="font-semibold text-foreground">{item.name}</h4>
                        </div>
                        <Badge variant="secondary" className="text-xs">
                          {item.duration}
                        </Badge>
                      </div>
                      <p className="text-sm font-medium text-primary mb-1">{item.product}</p>
                      <p className="text-sm text-muted-foreground">{item.instructions}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Tips Section */}
          <div className="bg-primary/5 rounded-lg p-4 border border-primary/20">
            <h4 className="font-semibold mb-2 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-primary" />
              Pro Tips
            </h4>
            <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
              <li>Always patch test new products before full application</li>
              <li>Wait 30-60 seconds between each step for better absorption</li>
              <li>Consistency is key - follow this routine for at least 4-6 weeks to see results</li>
              <li>Adjust frequency of active ingredients based on skin tolerance</li>
            </ul>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
