#!/bin/bash

# Production build script for Dermalens Frontend
echo "🚀 Building Dermalens Frontend for Production..."

# Install dependencies
echo "📦 Installing dependencies..."
npm ci

# Create lib directory if it doesn't exist
mkdir -p lib

# Create utils.ts if it doesn't exist
if [ ! -f "lib/utils.ts" ]; then
    echo "📝 Creating utils.ts..."
    cat > lib/utils.ts << 'EOF'
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: Date): string {
  return date.toLocaleDateString()
}

export function formatPrice(price: number): string {
  return `$${price.toFixed(2)}`
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + "..."
}
EOF
fi

# Build the application
echo "🔨 Building Next.js application..."
npm run build

echo "✅ Build completed successfully!"
