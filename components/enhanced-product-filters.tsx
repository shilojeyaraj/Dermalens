"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"

export interface Product {
  id: string
  name: string
  brand: string
  price: number
  type: string
  image: string
  rating: number
  description: string
  reviewCount: number
  skinType: string
  category: string
}

interface EnhancedProductFiltersProps {
  selectedBrands: string[]
  onBrandsChange: (brands: string[]) => void
  priceRange: [number, number]
  onPriceRangeChange: (range: [number, number]) => void
  selectedTypes: string[]
  onTypesChange: (types: string[]) => void
}

export function EnhancedProductFilters({
  selectedBrands,
  onBrandsChange,
  priceRange,
  onPriceRangeChange,
  selectedTypes,
  onTypesChange
}: EnhancedProductFiltersProps) {
  const maxPrice = 150

  const allBrands = [
    "CeraVe", "The Ordinary", "Paula's Choice", "La Roche-Posay", "Neutrogena", "EltaMD", "Olay", "Aveeno", "Cetaphil",
    "Eucerin", "Vichy", "Bioderma", "Clinique", "Kiehl's", "Tatcha", "First Aid Beauty", "Drunk Elephant", "The Inkey List",
    "SkinCeuticals", "Murad", "Youth To The People", "Glossier", "Pixi", "COSRX", "Innisfree", "Laneige", "Curel",
    "Lancôme", "Estée Lauder", "MAC", "Bobbi Brown", "NARS", "Urban Decay", "Too Faced", "Benefit", "Tarte",
    "Fenty Beauty", "Rare Beauty", "Milk Makeup", "Glow Recipe", "Drunk Elephant", "Sunday Riley", "The Ordinary",
    "Paula's Choice", "CeraVe", "La Roche-Posay", "Vichy", "Avene", "Bioderma", "Eucerin", "Neutrogena", "Olay",
    "Aveeno", "Cetaphil", "Dove", "Garnier", "L'Oréal Paris", "Maybelline", "Revlon", "CoverGirl", "Rimmel",
    "NYX", "e.l.f.", "Wet n Wild", "Physician's Formula", "Burt's Bees", "The Body Shop", "Lush", "Kiehl's",
    "Origins", "Clinique", "Estée Lauder", "Lancôme", "Dior", "Chanel", "Yves Saint Laurent", "Giorgio Armani",
    "Tom Ford", "Marc Jacobs", "Versace", "Dolce & Gabbana", "Prada", "Hermès", "Bulgari", "Cartier", "Van Cleef & Arpels"
  ]

  const types = [
    "Cleanser", "Moisturizer", "Serum", "Sunscreen", "Toner", "Exfoliant", 
    "Eye Cream", "Face Mask", "Treatment", "Oil", "Essence", "Ampoule"
  ]

  const handleBrandToggle = (brand: string) => {
    if (selectedBrands.includes(brand)) {
      onBrandsChange(selectedBrands.filter(b => b !== brand))
    } else {
      onBrandsChange([...selectedBrands, brand])
    }
  }

  const handleTypeToggle = (type: string) => {
    if (selectedTypes.includes(type)) {
      onTypesChange(selectedTypes.filter(t => t !== type))
    } else {
      onTypesChange([...selectedTypes, type])
    }
  }

  return (
    <div className="space-y-6">
      {/* Brand Filter */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Brands</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="max-h-60 overflow-y-auto space-y-2">
            {allBrands.map((brand) => (
              <div key={brand} className="flex items-center space-x-2">
                <Checkbox
                  id={`brand-${brand}`}
                  checked={selectedBrands.includes(brand)}
                  onCheckedChange={() => handleBrandToggle(brand)}
                />
                <Label htmlFor={`brand-${brand}`} className="text-sm font-normal cursor-pointer">
                  {brand}
                </Label>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Price Range Filter */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Price Range</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Slider
            min={0}
            max={maxPrice}
            step={1}
            value={priceRange}
            onValueChange={(value) => onPriceRangeChange(value as [number, number])}
            className="w-full"
          />
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>${(priceRange[0] || 0).toFixed(2)}</span>
            <span>${(priceRange[1] || 0).toFixed(2)}</span>
          </div>
        </CardContent>
      </Card>

      {/* Product Type Filter */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Product Type</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {types.map((type) => (
            <div key={type} className="flex items-center space-x-2">
              <Checkbox
                id={`type-${type}`}
                checked={selectedTypes.includes(type)}
                onCheckedChange={() => handleTypeToggle(type)}
              />
              <Label htmlFor={`type-${type}`} className="text-sm font-normal cursor-pointer">
                {type}
              </Label>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}