"use client"

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { SimpleSelect, SimpleSelectContent, SimpleSelectItem, SimpleSelectTrigger, SimpleSelectValue } from "@/components/simple-select"
import { useState } from "react"

export function TestSelect() {
  const [value, setValue] = useState("")
  const [htmlValue, setHtmlValue] = useState("")
  const [simpleValue, setSimpleValue] = useState("")

  console.log("TestSelect rendered, value:", value)

  return (
    <div className="p-4 space-y-6">
      <h3 className="text-lg font-semibold mb-4">Test Select Components</h3>
      
      {/* HTML Select Test */}
      <div>
        <h4 className="font-medium mb-2">HTML Select (should work):</h4>
        <p className="text-sm text-gray-600 mb-2">HTML value: {htmlValue || "None"}</p>
        <select 
          value={htmlValue} 
          onChange={(e) => {
            console.log("HTML select changed to:", e.target.value)
            setHtmlValue(e.target.value)
          }}
          className="w-[200px] p-2 border rounded"
        >
          <option value="">Select an option</option>
          <option value="html1">HTML Option 1</option>
          <option value="html2">HTML Option 2</option>
          <option value="html3">HTML Option 3</option>
        </select>
      </div>

      {/* Simple Radix UI Select Test */}
      <div>
        <h4 className="font-medium mb-2">Simple Radix UI Select (testing):</h4>
        <p className="text-sm text-gray-600 mb-2">Simple value: {simpleValue || "None"}</p>
        <SimpleSelect value={simpleValue} onValueChange={(newValue) => {
          console.log("Simple Select value changed to:", newValue)
          setSimpleValue(newValue)
        }}>
          <SimpleSelectTrigger className="w-[200px]">
            <SimpleSelectValue placeholder="Select an option" />
          </SimpleSelectTrigger>
          <SimpleSelectContent>
            <SimpleSelectItem value="simple1">Simple Option 1</SimpleSelectItem>
            <SimpleSelectItem value="simple2">Simple Option 2</SimpleSelectItem>
            <SimpleSelectItem value="simple3">Simple Option 3</SimpleSelectItem>
          </SimpleSelectContent>
        </SimpleSelect>
      </div>

      {/* Original Radix UI Select Test */}
      <div>
        <h4 className="font-medium mb-2">Original Radix UI Select (testing):</h4>
        <p className="text-sm text-gray-600 mb-2">Radix value: {value || "None"}</p>
        <Select value={value} onValueChange={(newValue) => {
          console.log("Radix Select value changed to:", newValue)
          setValue(newValue)
        }}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Select an option" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="option1">Radix Option 1</SelectItem>
            <SelectItem value="option2">Radix Option 2</SelectItem>
            <SelectItem value="option3">Radix Option 3</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  )
}
