"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Sparkles, Scan, Package, GraduationCap } from "lucide-react"
import { ProductsPage } from "@/components/products-page"
import { useUser } from "@/contexts/user-context"

export function LandingPage() {
  const { user } = useUser()

  return (
    <div className="min-h-screen bg-background">
      <section className="relative overflow-hidden bg-background">
        {/* Three Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_2fr_1fr] min-h-[600px]">
          {/* Left Image */}
          <div className="hidden lg:block relative overflow-hidden bg-gradient-to-br from-green-100 to-green-200">
            <div className="w-full h-full flex items-center justify-center">
              <div className="text-center text-green-600">
                <div className="w-32 h-32 rounded-full bg-green-300 mx-auto mb-4 flex items-center justify-center">
                  <span className="text-4xl">👤</span>
                </div>
                <p className="text-sm font-medium">Profile Image</p>
              </div>
            </div>
            <div className="absolute inset-0 bg-gradient-to-r from-transparent to-background" />
          </div>

          {/* Center Content - Clean Background */}
          <div className="flex items-center justify-center px-4 py-20 bg-background">
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
          className="w-full sm:w-auto min-w-[140px] text-base font-semibold shadow-lg"
          onClick={() => window.location.href = '/signup'}
        >
          Sign Up
        </Button>
        <Button
          size="lg"
          variant="outline"
          className="w-full sm:w-auto min-w-[140px] text-base font-semibold bg-transparent"
          onClick={() => window.location.href = '/login'}
        >
          Log In
        </Button>
      </div>
            </div>
          </div>

          {/* Right Image */}
          <div className="hidden lg:block relative overflow-hidden bg-gradient-to-br from-green-100 to-green-200">
            <div className="w-full h-full flex items-center justify-center">
              <div className="text-center text-green-600">
                <div className="w-32 h-32 rounded-full bg-green-300 mx-auto mb-4 flex items-center justify-center">
                  <span className="text-4xl">👤</span>
                </div>
                <p className="text-sm font-medium">Profile Image</p>
              </div>
            </div>
            <div className="absolute inset-0 bg-gradient-to-l from-transparent to-background" />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16 md:py-20">
        <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {/* AI Analysis Card */}
          <div className="bg-accent/30 rounded-xl p-8 space-y-4 border border-border/50 hover:border-primary/50 transition-colors">
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
          <div className="bg-accent/30 rounded-xl p-8 space-y-4 border border-border/50 hover:border-primary/50 transition-colors">
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
          <div className="bg-accent/30 rounded-xl p-8 space-y-4 border border-border/50 hover:border-primary/50 transition-colors">
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
