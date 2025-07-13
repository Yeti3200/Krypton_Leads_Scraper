import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { business_type, location, max_results = 25 } = body

    // Call Railway backend for actual scraping
    const response = await fetch('https://kryptonleadsscraper-production.up.railway.app/scrape', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        business_type,
        location,
        max_results
      })
    })

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Scraping error:', error)
    return NextResponse.json(
      { error: 'Failed to scrape leads' },
      { status: 500 }
    )
  }
}