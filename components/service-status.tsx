"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, XCircle, AlertCircle, Loader2 } from "lucide-react"

interface ServiceStatus {
  openai: {
    enabled: boolean
    model?: string
  }
  google_search: {
    enabled: boolean
    max_results?: number
  }
  database: {
    connected: boolean
    tables: string[]
  }
}

export function ServiceStatus() {
  const [status, setStatus] = useState<ServiceStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const checkStatus = async () => {
      try {
        setLoading(true)
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/services-status`)
        
        if (!response.ok) {
          throw new Error('Failed to fetch service status')
        }
        
        const data = await response.json()
        setStatus(data)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    checkStatus()
    
    // Check status every 30 seconds
    const interval = setInterval(checkStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            Service Status
          </CardTitle>
          <CardDescription>Checking service availability...</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <XCircle className="h-4 w-4 text-red-500" />
            Service Status
          </CardTitle>
          <CardDescription>Error checking services: {error}</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (!status) return null

  const getStatusIcon = (enabled: boolean) => {
    return enabled ? (
      <CheckCircle className="h-4 w-4 text-green-500" />
    ) : (
      <XCircle className="h-4 w-4 text-red-500" />
    )
  }

  const getStatusBadge = (enabled: boolean) => {
    return (
      <Badge variant={enabled ? "default" : "destructive"}>
        {enabled ? "Online" : "Offline"}
      </Badge>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          Service Status
        </CardTitle>
        <CardDescription>Current status of integrated services</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* OpenAI Status */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon(status.openai.enabled)}
            <span className="font-medium">OpenAI Vision API</span>
            {status.openai.model && (
              <Badge variant="outline">{status.openai.model}</Badge>
            )}
          </div>
          {getStatusBadge(status.openai.enabled)}
        </div>

        {/* Google Search Status */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon(status.google_search.enabled)}
            <span className="font-medium">Google Custom Search</span>
            {status.google_search.max_results && (
              <Badge variant="outline">{status.google_search.max_results} results</Badge>
            )}
          </div>
          {getStatusBadge(status.google_search.enabled)}
        </div>

        {/* Database Status */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon(status.database.connected)}
            <span className="font-medium">Supabase Database</span>
            <Badge variant="outline">{status.database.tables.length} tables</Badge>
          </div>
          {getStatusBadge(status.database.connected)}
        </div>

        {/* Overall Status */}
        <div className="pt-2 border-t">
          <div className="flex items-center justify-between">
            <span className="font-medium">Overall System</span>
            {getStatusBadge(
              status.openai.enabled && 
              status.google_search.enabled && 
              status.database.connected
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

