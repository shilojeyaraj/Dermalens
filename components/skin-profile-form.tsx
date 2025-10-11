"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Separator } from "@/components/ui/separator"
import { useUser } from "@/contexts/user-context"
import { SkinProfile } from "@/lib/api"
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

  // Load existing skin profile data
  useEffect(() => {
    if (skinProfile) {
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

    try {
      if (skinProfile) {
        console.log('📝 [SKIN PROFILE] Updating existing profile...')
        await updateSkinProfile(formData)
        console.log('✅ [SKIN PROFILE] Profile updated successfully')
      } else {
        console.log('🆕 [SKIN PROFILE] Creating new profile...')
        await createSkinProfile(formData)
        console.log('✅ [SKIN PROFILE] Profile created successfully')
      }
      console.log('🎯 [SKIN PROFILE] Calling onComplete callback...')
      onComplete?.()
      console.log('🏁 [SKIN PROFILE] Profile submission completed')
    } catch (error) {
      console.error('❌ [SKIN PROFILE] Failed to save skin profile:', error)
      console.error('❌ [SKIN PROFILE] Error details:', error)
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
    { value: "none", label: "None - No acne or breakouts" },
    { value: "mild", label: "Mild - Occasional small pimples" },
    { value: "moderate", label: "Moderate - Regular breakouts, some inflammation" },
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

  // Note: medical_conditions column doesn't exist in current schema
  // const medicalConditions = [
  //   { value: "acne", label: "Acne Vulgaris" },
  //   { value: "rosacea", label: "Rosacea" },
  //   { value: "eczema", label: "Eczema (Atopic Dermatitis)" },
  //   { value: "psoriasis", label: "Psoriasis" },
  //   { value: "dermatitis", label: "Contact Dermatitis" },
  //   { value: "melasma", label: "Melasma" },
  //   { value: "vitiligo", label: "Vitiligo" },
  //   { value: "seborrheic_dermatitis", label: "Seborrheic Dermatitis" }
  // ]

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
                  <Select value={formData.skin_type} onValueChange={(value) => handleInputChange("skin_type", value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select your skin type" />
                    </SelectTrigger>
                    <SelectContent>
                      {skinTypes.map(type => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="skin_tone">Skin Tone</Label>
                  <Select value={formData.skin_tone} onValueChange={(value) => handleInputChange("skin_tone", value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select your skin tone" />
                    </SelectTrigger>
                    <SelectContent>
                      {skinTones.map(tone => (
                        <SelectItem key={tone.value} value={tone.value}>
                          {tone.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="acne_severity">Acne Severity</Label>
                  <Select value={formData.acne_severity} onValueChange={(value) => handleInputChange("acne_severity", value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select acne severity" />
                    </SelectTrigger>
                    <SelectContent>
                      {acneSeverity.map(severity => (
                        <SelectItem key={severity.value} value={severity.value}>
                          {severity.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="pore_size">Pore Size</Label>
                  <Select value={formData.pore_size} onValueChange={(value) => handleInputChange("pore_size", value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select pore size" />
                    </SelectTrigger>
                    <SelectContent>
                      {poreSize.map(size => (
                        <SelectItem key={size.value} value={size.value}>
                          {size.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="sensitivity_level">Sensitivity Level</Label>
                  <Select value={formData.sensitivity_level} onValueChange={(value) => handleInputChange("sensitivity_level", value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select sensitivity level" />
                    </SelectTrigger>
                    <SelectContent>
                      {sensitivityLevel.map(level => (
                        <SelectItem key={level.value} value={level.value}>
                          {level.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
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
                  <Select value={formData.diet_type} onValueChange={(value) => handleInputChange("diet_type", value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select diet type" />
                    </SelectTrigger>
                    <SelectContent>
                      {dietTypes.map(diet => (
                        <SelectItem key={diet} value={diet}>
                          {diet.charAt(0).toUpperCase() + diet.slice(1)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="water_intake">Water Intake</Label>
                  <Select value={formData.water_intake} onValueChange={(value) => handleInputChange("water_intake", value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select water intake" />
                    </SelectTrigger>
                    <SelectContent>
                      {waterIntake.map(intake => (
                        <SelectItem key={intake} value={intake}>
                          {intake.charAt(0).toUpperCase() + intake.slice(1)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="sleep_hours">Sleep Hours</Label>
                  <Select value={formData.sleep_hours} onValueChange={(value) => handleInputChange("sleep_hours", value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select sleep hours" />
                    </SelectTrigger>
                    <SelectContent>
                      {sleepHours.map(hours => (
                        <SelectItem key={hours} value={hours}>
                          {hours} hours
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="sun_exposure">Sun Exposure</Label>
                  <Select value={formData.sun_exposure} onValueChange={(value) => handleInputChange("sun_exposure", value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select sun exposure" />
                    </SelectTrigger>
                    <SelectContent>
                      {sunExposure.map(exposure => (
                        <SelectItem key={exposure} value={exposure}>
                          {exposure.charAt(0).toUpperCase() + exposure.slice(1)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
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
                  <Select value={formData.routine_frequency} onValueChange={(value) => handleInputChange("routine_frequency", value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select routine frequency" />
                    </SelectTrigger>
                    <SelectContent>
                      {routineFrequency.map(frequency => (
                        <SelectItem key={frequency} value={frequency}>
                          {frequency.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="routine_type">Routine Type</Label>
                  <Select value={formData.routine_type} onValueChange={(value) => handleInputChange("routine_type", value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select routine type" />
                    </SelectTrigger>
                    <SelectContent>
                      {routineType.map(type => (
                        <SelectItem key={type} value={type}>
                          {type.charAt(0).toUpperCase() + type.slice(1)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
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
                className="flex-1"
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
