import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'ZoneWise - AI-Powered Zoning Intelligence',
  description: 'Research zoning codes, analyze parcels, and generate reports with AI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
