"use client"

import { SkinProfileForm } from "@/components/skin-profile-form"
import { User, Sparkles } from "lucide-react"

export default function ProfilePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-green-50 to-green-100 p-4">
      {/* Header Section with Green Accent */}
      <div className="max-w-3xl mx-auto py-8">
        <div className="mb-8 text-center">
          {/* Icon with Green Background */}
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-green-500 to-green-600 shadow-lg mb-4">
            <User className="w-8 h-8 text-white" />
          </div>
          
          {/* Title with Gradient Text */}
          <h1 className="text-4xl md:text-5xl font-bold mb-3 bg-gradient-to-r from-green-600 to-green-800 bg-clip-text text-transparent">
            Complete Your Profile
          </h1>
          
          {/* Subtitle with Green Accent */}
          <p className="text-lg text-muted-foreground flex items-center justify-center gap-2 flex-wrap">
            <Sparkles className="w-5 h-5 text-green-500" />
            Tell us about your skin so we can provide personalized recommendations
            <Sparkles className="w-5 h-5 text-green-500" />
          </p>
        </div>

        {/* Form Container with White Background and Green Border */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border-2 border-green-100 p-6 md:p-8">
          <SkinProfileForm />
        </div>

        {/* Decorative Bottom Accent */}
        <div className="mt-8 text-center">
          <div className="inline-flex items-center gap-2 text-sm text-muted-foreground">
            <div className="w-12 h-0.5 bg-gradient-to-r from-transparent to-green-300"></div>
            <span>Powered by AI</span>
            <div className="w-12 h-0.5 bg-gradient-to-l from-transparent to-green-300"></div>
          </div>
        </div>
      </div>
    </div>
  )
}

