"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
// Removed Radix UI Select import - using HTML select instead
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Separator } from "@/components/ui/separator"
import { useUser } from "@/contexts/user-context-simple"
import { SkinProfile } from "../lib/api"
import { Loader2, Save, User } from "lucide-react"

interface SkinProfileFormProps {
  onComplete?: () => void
  onCancel?: () => void
}

export function SkinProfileForm({ onComplete, onCancel }: SkinProfileFormProps) {
  const { skinProfile, createSkinProfile, updateSkinProfile, isLoading, error, clearError } = useUser()
  
  const [formData, setFormData] = useState({
    skin_type: "",
    skin_tone: "",
    acne_severity: "",
    pore_size: "",
    sensitivity_level: "",
    primary_concerns: [] as string[],
    pre_existing_conditions: [] as string[],
    allergies: [] as string[],
    diet_type: "",
    water_intake: "",
    sleep_hours: "",
    sun_exposure: "",
    routine_frequency: "",
    routine_type: "",
    skin_goals: [] as string[]
  })

  const [customAllergy, setCustomAllergy] = useState("")
  const [customConcern, setCustomConcern] = useState("")
  const [customCondition, setCustomCondition] = useState("")
  const [customGoal, setCustomGoal] = useState("")
  const [additionalInfo, setAdditionalInfo] = useState("")

  // Load profile data on component mount
  useEffect(() => {
    console.log('📋 [SKIN PROFILE FORM] Component mounted, checking for stored profile...')
    const storedProfile = localStorage.getItem('skinProfile')
    if (storedProfile) {
      try {
        const parsedProfile = JSON.parse(storedProfile)
        console.log('📋 [SKIN PROFILE FORM] Found stored profile on mount:', parsedProfile)
        setFormData({
          skin_type: parsedProfile.skin_type || "",
          skin_tone: parsedProfile.skin_tone || "",
          acne_severity: parsedProfile.acne_severity || "",
          pore_size: parsedProfile.pore_size || "",
          sensitivity_level: parsedProfile.sensitivity_level || "",
          primary_concerns: parsedProfile.primary_concerns || [],
          pre_existing_conditions: parsedProfile.pre_existing_conditions || [],
          allergies: parsedProfile.allergies || [],
          diet_type: parsedProfile.diet_type || "",
          water_intake: parsedProfile.water_intake || "",
          sleep_hours: parsedProfile.sleep_hours || "",
          sun_exposure: parsedProfile.sun_exposure || "",
          routine_frequency: parsedProfile.routine_frequency || "",
          routine_type: parsedProfile.routine_type || "",
          skin_goals: parsedProfile.skin_goals || []
        })
        setAdditionalInfo(parsedProfile.additional_info || "")
        console.log('📋 [SKIN PROFILE FORM] Profile loaded on mount successfully')
      } catch (error) {
        console.error('📋 [SKIN PROFILE FORM] Error parsing profile on mount:', error)
      }
    }
  }, [])

  // Load existing skin profile data
  useEffect(() => {
    console.log('📋 [SKIN PROFILE FORM] useEffect triggered, skinProfile:', skinProfile)
    
    // Try to load from context first
    if (skinProfile) {
      console.log('📋 [SKIN PROFILE FORM] Loading existing profile data from context:', skinProfile)
      setFormData({
        skin_type: skinProfile.skin_type || "",
        skin_tone: skinProfile.skin_tone || "",
        acne_severity: skinProfile.acne_severity || "",
        pore_size: skinProfile.pore_size || "",
        sensitivity_level: skinProfile.sensitivity_level || "",
        primary_concerns: skinProfile.primary_concerns || [],
        pre_existing_conditions: skinProfile.pre_existing_conditions || [],
        allergies: skinProfile.allergies || [],
        diet_type: skinProfile.diet_type || "",
        water_intake: skinProfile.water_intake || "",
        sleep_hours: skinProfile.sleep_hours || "",
        sun_exposure: skinProfile.sun_exposure || "",
        routine_frequency: skinProfile.routine_frequency || "",
        routine_type: skinProfile.routine_type || "",
        skin_goals: skinProfile.skin_goals || []
      })
      setAdditionalInfo(skinProfile.additional_info || "")
      console.log('📋 [SKIN PROFILE FORM] Form data loaded successfully from context')
    } else {
      // Fallback: check localStorage directly
      console.log('📋 [SKIN PROFILE FORM] No context profile, checking localStorage...')
      const storedProfile = localStorage.getItem('skinProfile')
      if (storedProfile) {
        try {
          const parsedProfile = JSON.parse(storedProfile)
          console.log('📋 [SKIN PROFILE FORM] Loading profile from localStorage:', parsedProfile)
          setFormData({
            skin_type: parsedProfile.skin_type || "",
            skin_tone: parsedProfile.skin_tone || "",
            acne_severity: parsedProfile.acne_severity || "",
            pore_size: parsedProfile.pore_size || "",
            sensitivity_level: parsedProfile.sensitivity_level || "",
            primary_concerns: parsedProfile.primary_concerns || [],
            pre_existing_conditions: parsedProfile.pre_existing_conditions || [],
            allergies: parsedProfile.allergies || [],
            diet_type: parsedProfile.diet_type || "",
            water_intake: parsedProfile.water_intake || "",
            sleep_hours: parsedProfile.sleep_hours || "",
            sun_exposure: parsedProfile.sun_exposure || "",
            routine_frequency: parsedProfile.routine_frequency || "",
            routine_type: parsedProfile.routine_type || "",
            skin_goals: parsedProfile.skin_goals || []
          })
          setAdditionalInfo(parsedProfile.additional_info || "")
          console.log('📋 [SKIN PROFILE FORM] Form data loaded successfully from localStorage')
        } catch (error) {
          console.error('📋 [SKIN PROFILE FORM] Error parsing stored profile:', error)
        }
      } else {
        console.log('📋 [SKIN PROFILE FORM] No existing profile found in localStorage either')
      }
    }
  }, [skinProfile])

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
    if (error) clearError()
  }

  const handleArrayChange = (field: string, value: string, checked: boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: checked 
        ? [...prev[field as keyof typeof prev] as string[], value]
        : (prev[field as keyof typeof prev] as string[]).filter(item => item !== value)
    }))
    if (error) clearError()
  }

  const addCustomItem = (field: string, value: string, setter: (value: string) => void) => {
    if (value.trim()) {
      setFormData(prev => ({
        ...prev,
        [field]: [...prev[field as keyof typeof prev] as string[], value.trim()]
      }))
      setter("")
    }
  }

  const removeItem = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: (prev[field as keyof typeof prev] as string[]).filter(item => item !== value)
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()

    console.log('🚀 [SKIN PROFILE] Starting profile submission...')
    console.log('📊 [SKIN PROFILE] Form data:', formData)
    console.log('🔄 [SKIN PROFILE] Is update?', !!skinProfile)

    // Filter out empty string values and handle enum constraints
    const cleanedFormData = Object.fromEntries(
      Object.entries(formData).map(([key, value]) => {
        if (value === "") {
          return [key, null]
        }
        
        // Handle specific enum field mappings
        if (key === "acne_severity" && value === "moderate") {
          return [key, "moderate_acne"] // Map to valid enum value
        }
        
        return [key, value]
      })
    )

    // Add additional information to the form data
    if (additionalInfo.trim()) {
      cleanedFormData.additional_info = additionalInfo.trim()
    }

    console.log('🧹 [SKIN PROFILE] Cleaned form data:', cleanedFormData)

    try {
      if (skinProfile) {
        console.log('📝 [SKIN PROFILE] Updating existing profile...')
        await updateSkinProfile(cleanedFormData)
        console.log('✅ [SKIN PROFILE] Profile updated successfully')
        alert('Profile updated successfully!')
      } else {
        console.log('🆕 [SKIN PROFILE] Creating new profile...')
        await createSkinProfile(cleanedFormData)
        console.log('✅ [SKIN PROFILE] Profile created successfully')
      }
      
      // Handle completion or redirect with loading screen
      if (onComplete) {
        console.log('🎯 [SKIN PROFILE] Calling onComplete callback...')
        onComplete()
      } else {
        // Show loading and redirect to face scan
        console.log('📸 [SKIN PROFILE] Redirecting to face scan page...')
        // Redirect immediately - the loading will show on the scan page
        window.location.href = '/scan'
      }
      
      console.log('🏁 [SKIN PROFILE] Profile submission completed')
    } catch (error) {
      console.error('❌ [SKIN PROFILE] Failed to save skin profile:', error)
      alert('Failed to save profile. Please try again.')
    }
  }

  const skinTypes = [
    { value: "Normal", label: "Normal - Balanced, not too oily or dry" },
    { value: "Dry", label: "Dry - Feels tight, may have flaking" },
    { value: "Oily", label: "Oily - Shiny, especially in T-zone" },
    { value: "Combination", label: "Combination - Oily T-zone, dry cheeks" },
    { value: "Sensitive", label: "Sensitive - Easily irritated, reactive" }
  ]

  const skinTones = [
    { value: "fair", label: "Fair - Very light, burns easily" },
    { value: "light", label: "Light - Light with some tanning ability" },
    { value: "medium", label: "Medium - Moderate tanning ability" },
    { value: "tan", label: "Tan - Tans easily, rarely burns" },
    { value: "dark", label: "Dark - Deep tan, rarely burns" },
    { value: "deep", label: "Deep - Very dark, never burns" }
  ]

  const acneSeverity = [
    { value: "mild", label: "Mild - Occasional small pimples" },
    { value: "moderate_acne", label: "Moderate - Regular breakouts, some inflammation" },
    { value: "severe", label: "Severe - Frequent, inflamed breakouts" }
  ]

  const poreSize = [
    { value: "small", label: "Small - Barely visible pores" },
    { value: "medium", label: "Medium - Noticeable but not prominent" },
    { value: "large", label: "Large - Clearly visible, prominent pores" }
  ]

  const sensitivityLevel = [
    { value: "low", label: "Low - Rarely reacts to products" },
    { value: "moderate", label: "Moderate - Occasional mild reactions" },
    { value: "high", label: "High - Frequently reacts to new products" }
  ]

  // Note: preferred_brands column doesn't exist in current schema
  // const preferredBrands = [
  //   "CeraVe", "The Ordinary", "Paula's Choice", "Neutrogena", "Olay", 
  //   "La Roche-Posay", "Avene", "Clinique", "Estée Lauder", "L'Oreal",
  //   "Dove", "Cetaphil", "Vanicream", "Eucerin"
  // ]

  const mainConcerns = [
    { value: "acne", label: "Acne & Breakouts" },
    { value: "hyperpigmentation", label: "Dark Spots & Hyperpigmentation" },
    { value: "wrinkles", label: "Fine Lines & Wrinkles" },
    { value: "dry_skin", label: "Dryness & Dehydration" },
    { value: "oily_skin", label: "Excess Oil & Shine" },
    { value: "sensitive_skin", label: "Sensitivity & Redness" },
    { value: "blackheads", label: "Blackheads & Clogged Pores" },
    { value: "whiteheads", label: "Whiteheads" },
    { value: "rosacea", label: "Rosacea" },
    { value: "eczema", label: "Eczema & Irritation" },
    { value: "uneven_tone", label: "Uneven Skin Tone" },
    { value: "large_pores", label: "Large Pores" }
  ]

  // Medical conditions for pre_existing_conditions field
  const medicalConditions = [
    { value: "acne", label: "Acne Vulgaris" },
    { value: "rosacea", label: "Rosacea" },
    { value: "eczema", label: "Eczema (Atopic Dermatitis)" },
    { value: "psoriasis", label: "Psoriasis" },
    { value: "dermatitis", label: "Contact Dermatitis" },
    { value: "melasma", label: "Melasma" },
    { value: "vitiligo", label: "Vitiligo" },
    { value: "seborrheic_dermatitis", label: "Seborrheic Dermatitis" }
  ]

  const commonAllergies = [
    { value: "fragrance", label: "Fragrance/Parfum" },
    { value: "alcohol", label: "Alcohol (Ethanol)" },
    { value: "sulfates", label: "Sulfates (SLS/SLES)" },
    { value: "parabens", label: "Parabens" },
    { value: "retinol", label: "Retinol/Vitamin A" },
    { value: "vitamin_c", label: "Vitamin C (Ascorbic Acid)" },
    { value: "niacinamide", label: "Niacinamide" },
    { value: "salicylic_acid", label: "Salicylic Acid" },
    { value: "benzoyl_peroxide", label: "Benzoyl Peroxide" },
    { value: "glycolic_acid", label: "Glycolic Acid" },
    { value: "lactic_acid", label: "Lactic Acid" },
    { value: "hyaluronic_acid", label: "Hyaluronic Acid" }
  ]

  const skinGoals = [
    { value: "clear_skin", label: "Clear, Blemish-Free Skin" },
    { value: "even_tone", label: "Even Skin Tone" },
    { value: "reduce_wrinkles", label: "Reduce Fine Lines & Wrinkles" },
    { value: "hydrated_skin", label: "Hydrated, Plump Skin" },
    { value: "reduce_oil", label: "Control Oil Production" },
    { value: "reduce_sensitivity", label: "Reduce Sensitivity & Redness" },
    { value: "anti_aging", label: "Anti-Aging & Prevention" },
    { value: "brighten_skin", label: "Brighten Dull Skin" },
    { value: "smooth_texture", label: "Smooth Skin Texture" },
    { value: "minimize_pores", label: "Minimize Pore Appearance" }
  ]

  const dietTypes = ["omnivore", "vegetarian", "vegan", "pescatarian"]
  const waterIntake = ["low", "moderate", "high"]
  const sleepHours = ["<6", "6-8", "8-10", ">10"]
  const sunExposure = ["minimal", "moderate", "high"]
  const routineFrequency = ["daily", "alternating_days", "weekly"]
  const routineType = ["minimal", "standard", "extensive"]

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="w-5 h-5" />
            {skinProfile ? "Update Skin Profile" : "Create Skin Profile"}
          </CardTitle>
          <CardDescription>
            Help us understand your skin better to provide personalized recommendations
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert className="mb-6" variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Basic Skin Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Basic Skin Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="skin_type">Skin Type</Label>
                  <select
                    id="skin_type"
                    value={formData.skin_type}
                    onChange={(e) => handleInputChange("skin_type", e.target.value)}
                    className="w-full h-10 px-3 py-2 border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  >
                    <option value="">Select your skin type</option>
                    {skinTypes.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="skin_tone">Skin Tone</Label>
                  <select
                    id="skin_tone"
                    value={formData.skin_tone}
                    onChange={(e) => handleInputChange("skin_tone", e.target.value)}
                    className="w-full h-10 px-3 py-2 border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  >
                    <option value="">Select your skin tone</option>
                    {skinTones.map(tone => (
                      <option key={tone.value} value={tone.value}>
                        {tone.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="acne_severity">Acne Severity</Label>
                  <select
                    id="acne_severity"
                    value={formData.acne_severity}
                    onChange={(e) => handleInputChange("acne_severity", e.target.value)}
                    className="w-full h-10 px-3 py-2 border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  >
                    <option value="">Select acne severity</option>
                    {acneSeverity.map(severity => (
                      <option key={severity.value} value={severity.value}>
                        {severity.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="pore_size">Pore Size</Label>
                  <select
                    id="pore_size"
                    value={formData.pore_size}
                    onChange={(e) => handleInputChange("pore_size", e.target.value)}
                    className="w-full h-10 px-3 py-2 border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  >
                    <option value="">Select pore size</option>
                    {poreSize.map(size => (
                      <option key={size.value} value={size.value}>
                        {size.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="sensitivity_level">Sensitivity Level</Label>
                  <select
                    id="sensitivity_level"
                    value={formData.sensitivity_level}
                    onChange={(e) => handleInputChange("sensitivity_level", e.target.value)}
                    className="w-full h-10 px-3 py-2 border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  >
                    <option value="">Select sensitivity level</option>
                    {sensitivityLevel.map(level => (
                      <option key={level.value} value={level.value}>
                        {level.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <Separator />

            {/* Primary Concerns */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Primary Skin Concerns</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {mainConcerns.map(concern => (
                  <div key={concern.value} className="flex items-center space-x-2">
                    <Checkbox
                      id={`concern-${concern.value}`}
                      checked={formData.primary_concerns.includes(concern.value)}
                      onCheckedChange={(checked) => handleArrayChange("primary_concerns", concern.value, checked as boolean)}
                    />
                    <Label htmlFor={`concern-${concern.value}`} className="text-sm">
                      {concern.label}
                    </Label>
                  </div>
                ))}
              </div>
              
              <div className="flex gap-2">
                <Input
                  placeholder="Add custom concern"
                  value={customConcern}
                  onChange={(e) => setCustomConcern(e.target.value)}
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => addCustomItem("primary_concerns", customConcern, setCustomConcern)}
                >
                  Add
                </Button>
              </div>
              
              {formData.primary_concerns.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {formData.primary_concerns.map(concern => (
                    <span
                      key={concern}
                      className="inline-flex items-center gap-1 px-2 py-1 bg-primary/10 text-primary rounded-md text-sm"
                    >
                      {concern.replace('_', ' ')}
                      <button
                        type="button"
                        onClick={() => removeItem("primary_concerns", concern)}
                        className="ml-1 hover:text-destructive"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            <Separator />

            {/* Note: Preferred Brands section removed - column doesn't exist in current schema */}

            {/* Note: Medical Conditions section removed - column doesn't exist in current schema */}

            {/* Pre-existing Conditions */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Other Skin Conditions</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {medicalConditions.map(condition => (
                  <div key={condition.value} className="flex items-center space-x-2">
                    <Checkbox
                      id={`condition-${condition.value}`}
                      checked={formData.pre_existing_conditions.includes(condition.value)}
                      onCheckedChange={(checked) => handleArrayChange("pre_existing_conditions", condition.value, checked as boolean)}
                    />
                    <Label htmlFor={`condition-${condition.value}`} className="text-sm">
                      {condition.label}
                    </Label>
                  </div>
                ))}
              </div>
              
              <div className="flex gap-2">
                <Input
                  placeholder="Add custom condition"
                  value={customCondition}
                  onChange={(e) => setCustomCondition(e.target.value)}
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => addCustomItem("pre_existing_conditions", customCondition, setCustomCondition)}
                >
                  Add
                </Button>
              </div>
            </div>

            <Separator />

            {/* Allergies */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Known Allergies/Sensitivities</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {commonAllergies.map(allergy => (
                  <div key={allergy.value} className="flex items-center space-x-2">
                    <Checkbox
                      id={`allergy-${allergy.value}`}
                      checked={formData.allergies.includes(allergy.value)}
                      onCheckedChange={(checked) => handleArrayChange("allergies", allergy.value, checked as boolean)}
                    />
                    <Label htmlFor={`allergy-${allergy.value}`} className="text-sm">
                      {allergy.label}
                    </Label>
                  </div>
                ))}
              </div>
              
              <div className="flex gap-2">
                <Input
                  placeholder="Add custom allergy"
                  value={customAllergy}
                  onChange={(e) => setCustomAllergy(e.target.value)}
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => addCustomItem("allergies", customAllergy, setCustomAllergy)}
                >
                  Add
                </Button>
              </div>
            </div>

            <Separator />

            {/* Lifestyle Factors */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Lifestyle Factors</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="diet_type">Diet Type</Label>
                  <select
                    id="diet_type"
                    value={formData.diet_type}
                    onChange={(e) => handleInputChange("diet_type", e.target.value)}
                    className="w-full h-10 px-3 py-2 border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  >
                    <option value="">Select diet type</option>
                    {dietTypes.map(diet => (
                      <option key={diet} value={diet}>
                        {diet.charAt(0).toUpperCase() + diet.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="water_intake">Water Intake</Label>
                  <select
                    id="water_intake"
                    value={formData.water_intake}
                    onChange={(e) => handleInputChange("water_intake", e.target.value)}
                    className="w-full h-10 px-3 py-2 border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  >
                    <option value="">Select water intake</option>
                    {waterIntake.map(intake => (
                      <option key={intake} value={intake}>
                        {intake.charAt(0).toUpperCase() + intake.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="sleep_hours">Sleep Hours</Label>
                  <select
                    id="sleep_hours"
                    value={formData.sleep_hours}
                    onChange={(e) => handleInputChange("sleep_hours", e.target.value)}
                    className="w-full h-10 px-3 py-2 border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  >
                    <option value="">Select sleep hours</option>
                    {sleepHours.map(hours => (
                      <option key={hours} value={hours}>
                        {hours} hours
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="sun_exposure">Sun Exposure</Label>
                  <select
                    id="sun_exposure"
                    value={formData.sun_exposure}
                    onChange={(e) => handleInputChange("sun_exposure", e.target.value)}
                    className="w-full h-10 px-3 py-2 border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  >
                    <option value="">Select sun exposure</option>
                    {sunExposure.map(exposure => (
                      <option key={exposure} value={exposure}>
                        {exposure.charAt(0).toUpperCase() + exposure.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <Separator />

            {/* Current Routine */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Current Skincare Routine</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="routine_frequency">Routine Frequency</Label>
                  <select
                    id="routine_frequency"
                    value={formData.routine_frequency}
                    onChange={(e) => handleInputChange("routine_frequency", e.target.value)}
                    className="w-full h-10 px-3 py-2 border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  >
                    <option value="">Select routine frequency</option>
                    {routineFrequency.map(frequency => (
                      <option key={frequency} value={frequency}>
                        {frequency.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="routine_type">Routine Type</Label>
                  <select
                    id="routine_type"
                    value={formData.routine_type}
                    onChange={(e) => handleInputChange("routine_type", e.target.value)}
                    className="w-full h-10 px-3 py-2 border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  >
                    <option value="">Select routine type</option>
                    {routineType.map(type => (
                      <option key={type} value={type}>
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <Separator />

            {/* Additional Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Additional Information</h3>
              <p className="text-sm text-muted-foreground">
                Tell us anything else about your skin, current routine, or specific concerns that might help us provide better recommendations.
              </p>
              <Textarea
                placeholder="Describe your current skincare routine, any specific concerns, or anything else you'd like us to know about your skin..."
                value={additionalInfo}
                onChange={(e) => setAdditionalInfo(e.target.value)}
                className="min-h-[120px] resize-none"
              />
            </div>

            <Separator />

            {/* Skin Goals */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Skin Goals</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {skinGoals.map(goal => (
                  <div key={goal.value} className="flex items-center space-x-2">
                    <Checkbox
                      id={`goal-${goal.value}`}
                      checked={formData.skin_goals.includes(goal.value)}
                      onCheckedChange={(checked) => handleArrayChange("skin_goals", goal.value, checked as boolean)}
                    />
                    <Label htmlFor={`goal-${goal.value}`} className="text-sm">
                      {goal.label}
                    </Label>
                  </div>
                ))}
              </div>
              
              <div className="flex gap-2">
                <Input
                  placeholder="Add custom goal"
                  value={customGoal}
                  onChange={(e) => setCustomGoal(e.target.value)}
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => addCustomItem("skin_goals", customGoal, setCustomGoal)}
                >
                  Add
                </Button>
              </div>
            </div>

            {/* Submit Buttons */}
            <div className="flex gap-4 pt-6">
              <Button
                type="submit"
                disabled={isLoading}
                className="flex-1 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white font-semibold border-2 border-green-700 shadow-lg hover:shadow-xl transition-all duration-300"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    {skinProfile ? "Update Profile" : "Save Profile"}
                  </>
                )}
              </Button>
              
              {onCancel && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={onCancel}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
