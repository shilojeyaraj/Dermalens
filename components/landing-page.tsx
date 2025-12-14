"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Sparkles, Scan, Package, GraduationCap } from "lucide-react"
import { ProductsPage } from "@/components/products-page"
import { useUser } from "@/contexts/user-context-simple"

export function LandingPage() {
  const { user } = useUser()

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-100 via-green-50 to-white relative overflow-hidden">
      <section className="relative overflow-hidden">
        {/* Single Column Layout */}
        <div className="min-h-[500px]">
          {/* Center Content - Clean Background */}
          <div className="flex items-center justify-center px-4 py-16 bg-gradient-to-b from-green-50/80 via-white/50 to-green-50/80 backdrop-blur-sm">
            <div className="max-w-2xl mx-auto text-center space-y-8">
              {/* Logo/Brand */}
              <div className="flex justify-center mb-6">
                <div className="w-16 h-16 rounded-full bg-primary flex items-center justify-center shadow-lg">
                  <Sparkles className="w-8 h-8 text-primary-foreground" />
                </div>
              </div>

              {/* Heading */}
              <div className="space-y-4">
                <h1 className="text-5xl md:text-6xl font-bold text-foreground text-balance leading-tight">
                  Welcome to Dermalens
                </h1>
                <p className="text-xl md:text-2xl text-muted-foreground text-balance">
                  AI-Powered Personalized Skincare Recommendations
                </p>
              </div>

              {/* CTA Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
        <Button
          size="lg"
          className="w-full sm:w-auto min-w-[140px] text-base font-semibold shadow-lg hover:shadow-xl transition-all duration-300 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600"
          onClick={() => window.location.href = '/signup'}
        >
          Sign Up
        </Button>
        <Button
          size="lg"
          variant="outline"
          className="w-full sm:w-auto min-w-[140px] text-base font-semibold bg-white/80 backdrop-blur-sm border-2 border-green-600 text-green-600 hover:bg-green-50 transition-all duration-300"
          onClick={() => window.location.href = '/login'}
        >
          Log In
        </Button>
      </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-8 md:py-12">
        <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {/* AI Analysis Card */}
          <div className="bg-gradient-to-br from-green-100 to-white rounded-xl p-8 space-y-4 border border-green-200 hover:border-green-400 hover:shadow-lg transition-all duration-300">
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
              <Scan className="w-6 h-6 text-primary" />
            </div>
            <div className="space-y-2">
              <h3 className="text-xl font-semibold text-foreground">AI Analysis</h3>
              <p className="text-sm text-muted-foreground font-medium">
                Upload your skin photo for AI-powered analysis
              </p>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Our advanced AI technology analyzes your skin condition and provides personalized recommendations.
            </p>
          </div>

          {/* Personalized Products Card */}
          <div className="bg-gradient-to-br from-white to-green-100 rounded-xl p-8 space-y-4 border border-green-200 hover:border-green-400 hover:shadow-lg transition-all duration-300">
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
              <Package className="w-6 h-6 text-primary" />
            </div>
            <div className="space-y-2">
              <h3 className="text-xl font-semibold text-foreground">Personalized Products</h3>
              <p className="text-sm text-muted-foreground font-medium">
                Get product recommendations tailored to your skin
              </p>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Discover skincare products that are perfect for your specific skin type and concerns.
            </p>
          </div>

          {/* Expert Guidance Card */}
          <div className="bg-gradient-to-br from-green-100 via-white to-green-100 rounded-xl p-8 space-y-4 border border-green-200 hover:border-green-400 hover:shadow-lg transition-all duration-300">
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-primary" />
            </div>
            <div className="space-y-2">
              <h3 className="text-xl font-semibold text-foreground">Expert Guidance</h3>
              <p className="text-sm text-muted-foreground font-medium">
                Professional skincare advice at your fingertips
              </p>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Access expert skincare tips and routines designed for your unique skin needs.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
