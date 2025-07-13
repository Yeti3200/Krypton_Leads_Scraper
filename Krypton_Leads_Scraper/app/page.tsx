'use client'

import React, { useState } from 'react'

export default function HomePage() {
  const [businessType, setBusinessType] = useState('')
  const [location, setLocation] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  const handleScrape = async () => {
    if (!businessType || !location) return
    
    setLoading(true)
    try {
      const response = await fetch('/api/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          business_type: businessType,
          location: location,
          max_results: 25
        })
      })
      
      const data = await response.json()
      setResults(data.leads || [])
    } catch (error) {
      console.error('Error:', error)
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-center">
          🎯 Krypton Lead Scraper
        </h1>
        
        <div className="bg-gray-900 p-6 rounded-lg mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <input
              type="text"
              placeholder="Business type (e.g. restaurant)"
              value={businessType}
              onChange={(e) => setBusinessType(e.target.value)}
              className="p-3 bg-gray-800 rounded text-white"
            />
            <input
              type="text"
              placeholder="Location (e.g. New York, NY)"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="p-3 bg-gray-800 rounded text-white"
            />
            <button
              onClick={handleScrape}
              disabled={loading}
              className="p-3 bg-blue-600 hover:bg-blue-700 rounded font-semibold disabled:opacity-50"
            >
              {loading ? 'Scraping...' : 'Find Leads'}
            </button>
          </div>
        </div>

        {results.length > 0 && (
          <div className="bg-gray-900 p-6 rounded-lg">
            <h2 className="text-2xl font-bold mb-4">
              Found {results.length} leads
            </h2>
            <div className="space-y-4">
              {results.map((lead, index) => (
                <div key={index} className="bg-gray-800 p-4 rounded">
                  <h3 className="text-lg font-semibold text-blue-400">
                    {lead.business_name}
                  </h3>
                  {lead.phone && (
                    <p className="text-green-400">📞 {lead.phone}</p>
                  )}
                  {lead.website && (
                    <p className="text-purple-400">
                      🌐 <a href={lead.website} target="_blank" className="underline">
                        {lead.website}
                      </a>
                    </p>
                  )}
                  {lead.address && (
                    <p className="text-gray-400">📍 {lead.address}</p>
                  )}
                  <p className="text-yellow-400">
                    ⭐ Quality: {lead.quality_score}/10
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}