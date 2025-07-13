import React from 'react'
import './globals.css'

export const metadata = {
  title: 'Krypton Lead Scraper',
  description: 'Simple lead generation tool',
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