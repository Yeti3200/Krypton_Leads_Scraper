import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { business_type, location, max_results = 25 } = body

    // Mock data since Railway backend is down
    const mockLeads = Array.from({ length: Math.min(max_results, 10) }, (_, i) => ({
      business_name: `${business_type} Business ${i + 1}`,
      phone: `(555) ${String(Math.floor(Math.random() * 900) + 100)}-${String(Math.floor(Math.random() * 9000) + 1000)}`,
      website: `https://${business_type.toLowerCase().replace(' ', '')}-${i + 1}.com`,
      address: `${100 + i * 10} Main St, ${location}`,
      quality_score: Math.floor(Math.random() * 6) + 5
    }))

    return NextResponse.json({
      success: true,
      leads: mockLeads,
      total: mockLeads.length
    })
  } catch (error) {
    console.error('Scraping error:', error)
    return NextResponse.json(
      { error: 'Failed to scrape leads' },
      { status: 500 }
    )
  }
}