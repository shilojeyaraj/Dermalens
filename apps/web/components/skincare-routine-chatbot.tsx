"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { MessageCircle, Send, Bot, User, Loader2, Sparkles } from "lucide-react"

interface ChatMessage {
  id: string
  type: 'user' | 'bot'
  content: string
  timestamp: Date
}

interface SkincareRoutineChatbotProps {
  onRoutineExtracted?: (routine: string) => void
  initialRoutine?: string
}

export function SkincareRoutineChatbot({ onRoutineExtracted, initialRoutine }: SkincareRoutineChatbotProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [extractedRoutine, setExtractedRoutine] = useState<string | null>(initialRoutine || null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Initialize with welcome message
  useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage: ChatMessage = {
        id: '1',
        type: 'bot',
        content: "Hi! I'm here to help you describe your current skincare routine. Tell me about the products you use, when you use them, and any specific steps you follow. I'll help organize this information for your profile!",
        timestamp: new Date()
      }
      setMessages([welcomeMessage])
    }
  }, [])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    // Simulate AI processing and response
    setTimeout(() => {
      const botResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: generateBotResponse(inputValue.trim()),
        timestamp: new Date()
      }
      setMessages(prev => [...prev, botResponse])
      setIsLoading(false)
    }, 1000)
  }

  const generateBotResponse = (userInput: string): string => {
    const lowerInput = userInput.toLowerCase()
    
    // Check if user is describing their routine
    if (lowerInput.includes('morning') || lowerInput.includes('evening') || 
        lowerInput.includes('cleanser') || lowerInput.includes('moisturizer') ||
        lowerInput.includes('serum') || lowerInput.includes('toner') ||
        lowerInput.includes('sunscreen') || lowerInput.includes('routine')) {
      
      // Extract routine information
      const routine = extractRoutineInfo(userInput)
      setExtractedRoutine(routine)
      onRoutineExtracted?.(routine)
      
      return `Great! I've captured your routine: "${routine}". Is there anything else you'd like to add or clarify about your skincare routine?`
    }
    
    // General responses
    if (lowerInput.includes('help') || lowerInput.includes('what')) {
      return "I'd love to hear about your skincare routine! You can tell me about your morning routine, evening routine, specific products you use, or any special treatments. Just describe what you do and I'll help organize it."
    }
    
    if (lowerInput.includes('thank') || lowerInput.includes('thanks')) {
      return "You're welcome! Feel free to add more details about your routine anytime. The more information you provide, the better I can help organize your skincare profile."
    }
    
    return "That's helpful! Can you tell me more about your skincare routine? For example, what products do you use in the morning vs evening, or any specific steps you follow?"
  }

  const extractRoutineInfo = (input: string): string => {
    // Simple extraction - in a real app, this would be more sophisticated
    return input.trim()
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const clearChat = () => {
    setMessages([])
    setExtractedRoutine(null)
    onRoutineExtracted?.("")
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageCircle className="w-5 h-5" />
          Describe Your Current Routine
        </CardTitle>
        <CardDescription>
          Chat with our AI assistant to describe your current skincare routine in detail
        </CardDescription>
        {extractedRoutine && (
          <div className="mt-2">
            <Badge variant="secondary" className="flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              Routine Captured
            </Badge>
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Chat Messages */}
          <ScrollArea className="h-64 w-full border rounded-md p-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`flex items-start gap-2 max-w-[80%] ${
                      message.type === 'user' ? 'flex-row-reverse' : 'flex-row'
                    }`}
                  >
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        message.type === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-muted-foreground'
                      }`}
                    >
                      {message.type === 'user' ? (
                        <User className="w-4 h-4" />
                      ) : (
                        <Bot className="w-4 h-4" />
                      )}
                    </div>
                    <div
                      className={`px-3 py-2 rounded-lg ${
                        message.type === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-muted-foreground'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-muted text-muted-foreground flex items-center justify-center">
                      <Bot className="w-4 h-4" />
                    </div>
                    <div className="bg-muted text-muted-foreground px-3 py-2 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="text-sm">Thinking...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          {/* Input Area */}
          <div className="flex gap-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Describe your skincare routine..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              size="icon"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={clearChat}
              className="text-xs"
            >
              Clear Chat
            </Button>
            {extractedRoutine && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setInputValue(`My current routine: ${extractedRoutine}`)
                }}
                className="text-xs"
              >
                Use Extracted Routine
              </Button>
            )}
          </div>

          {/* Extracted Routine Display */}
          {extractedRoutine && (
            <div className="mt-4 p-3 bg-muted/50 rounded-md">
              <h4 className="text-sm font-medium mb-2">Captured Routine:</h4>
              <p className="text-sm text-muted-foreground">{extractedRoutine}</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
