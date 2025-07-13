import React from 'react'
import './globals.css'

export const metadata = {
  title: 'Krypton Lead Scraper',
  description: 'Simple lead generation tool',
}

// Global error handling
if (typeof window === 'undefined') {
  process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error)
  })
  
  process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason)
  })
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  )
}