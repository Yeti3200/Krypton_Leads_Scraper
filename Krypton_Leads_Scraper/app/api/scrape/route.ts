import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { business_type, location, max_results = 25 } = body

    // For now, return mock data
    const mockLeads = [
      {
        business_name: "Joe's Pizza",
        phone: "(555) 123-4567",
        website: "https://joespizza.com",
        address: "123 Main St, New York, NY",
        quality_score: 8
      },
      {
        business_name: "Tony's Italian",
        phone: "(555) 234-5678", 
        website: "https://tonysitalian.com",
        address: "456 Broadway, New York, NY",
        quality_score: 7
      }
    ]

    return NextResponse.json({
      success: true,
      leads: mockLeads,
      total: mockLeads.length
    })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to scrape leads' },
      { status: 500 }
    )
  }
}