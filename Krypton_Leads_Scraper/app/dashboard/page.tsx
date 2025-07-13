'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { 
  Target, 
  Plus, 
  Download, 
  Clock, 
  CheckCircle, 
  XCircle,
  BarChart3,
  Users,
  Zap,
  CreditCard,
  Settings,
  LogOut
} from 'lucide-react'
import Link from 'next/link'

interface Lead {
  business_name: string
  website?: string
  phone?: string
  address?: string
  rating?: number
  reviews?: number
  quality_score: number
}

interface ScrapeJob {
  job_id: string
  business_type: string
  location: string
  status: string
  created_at: string
  total_leads: number
  leads?: Lead[]
  processing_time?: number
}

export default function DashboardPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [jobs, setJobs] = useState<ScrapeJob[]>([])
  const [loading, setLoading] = useState(true)
  const [activeJob, setActiveJob] = useState<ScrapeJob | null>(null)

  // Redirect if not authenticated
  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin')
    }
  }, [status, router])

  // Fetch user's jobs
  useEffect(() => {
    if (session?.user) {
      fetchJobs()
    }
  }, [session])

  const fetchJobs = async () => {
    try {
      const response = await fetch('/api/jobs', {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setJobs(data)
      }
    } catch (error) {
      console.error('Failed to fetch jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className=\"h-5 w-5 text-green-500\" />
      case 'failed':
        return <XCircle className=\"h-5 w-5 text-red-500\" />
      case 'processing':
        return <Clock className=\"h-5 w-5 text-yellow-500 animate-spin\" />
      default:
        return <Clock className=\"h-5 w-5 text-gray-500\" />
    }
  }

  const exportToCSV = (job: ScrapeJob) => {
    if (!job.leads) return
    
    const headers = ['Business Name', 'Website', 'Phone', 'Address', 'Rating', 'Reviews', 'Quality Score']
    const csvContent = [
      headers.join(','),
      ...job.leads.map(lead => [
        `\"${lead.business_name}\"`,
        `\"${lead.website || ''}\"`,
        `\"${lead.phone || ''}\"`,
        `\"${lead.address || ''}\"`,
        lead.rating || 0,
        lead.reviews || 0,
        lead.quality_score
      ].join(','))
    ].join('\\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${job.business_type}_${job.location}_leads.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  if (status === 'loading' || loading) {
    return (
      <div className=\"min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 flex items-center justify-center\">
        <div className=\"text-center\">
          <Target className=\"h-12 w-12 text-primary-500 animate-spin mx-auto mb-4\" />
          <p className=\"text-gray-400\">Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  const stats = {
    totalJobs: jobs.length,
    completedJobs: jobs.filter(job => job.status === 'completed').length,
    totalLeads: jobs.reduce((sum, job) => sum + job.total_leads, 0),
    avgQuality: jobs.length > 0 ? Math.round(jobs.reduce((sum, job) => sum + job.total_leads, 0) / jobs.length) : 0
  }

  return (
    <div className=\"min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900\">
      {/* Navigation */}
      <nav className=\"border-b border-gray-800 glass\">
        <div className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8\">
          <div className=\"flex justify-between items-center h-16\">
            <Link href=\"/\" className=\"flex items-center space-x-2\">
              <Target className=\"h-8 w-8 text-primary-500\" />
              <span className=\"text-2xl font-bold text-white\">Krypton</span>
            </Link>
            <div className=\"flex items-center space-x-4\">
              <div className=\"text-sm text-gray-400\">
                Welcome back, {session?.user?.name || session?.user?.email}
              </div>
              <button className=\"p-2 text-gray-400 hover:text-white transition-colors\">
                <Settings className=\"h-5 w-5\" />
              </button>
              <button className=\"p-2 text-gray-400 hover:text-white transition-colors\">
                <LogOut className=\"h-5 w-5\" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8\">
        {/* Stats Cards */}
        <div className=\"grid grid-cols-1 md:grid-cols-4 gap-6 mb-8\">
          <div className=\"glass rounded-xl p-6\">
            <div className=\"flex items-center justify-between\">
              <div>
                <p className=\"text-gray-400 text-sm\">Total Jobs</p>
                <p className=\"text-3xl font-bold text-white\">{stats.totalJobs}</p>
              </div>
              <BarChart3 className=\"h-8 w-8 text-primary-500\" />
            </div>
          </div>
          
          <div className=\"glass rounded-xl p-6\">
            <div className=\"flex items-center justify-between\">
              <div>
                <p className=\"text-gray-400 text-sm\">Completed</p>
                <p className=\"text-3xl font-bold text-white\">{stats.completedJobs}</p>
              </div>
              <CheckCircle className=\"h-8 w-8 text-green-500\" />
            </div>
          </div>
          
          <div className=\"glass rounded-xl p-6\">
            <div className=\"flex items-center justify-between\">
              <div>
                <p className=\"text-gray-400 text-sm\">Total Leads</p>
                <p className=\"text-3xl font-bold text-white\">{stats.totalLeads}</p>
              </div>
              <Users className=\"h-8 w-8 text-blue-500\" />
            </div>
          </div>
          
          <div className=\"glass rounded-xl p-6\">
            <div className=\"flex items-center justify-between\">
              <div>
                <p className=\"text-gray-400 text-sm\">Success Rate</p>
                <p className=\"text-3xl font-bold text-white\">{Math.round((stats.completedJobs / Math.max(stats.totalJobs, 1)) * 100)}%</p>
              </div>
              <Zap className=\"h-8 w-8 text-yellow-500\" />
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className=\"flex flex-col sm:flex-row gap-4 mb-8\">
          <Link 
            href=\"/scrape\"
            className=\"gradient-primary text-black px-6 py-3 rounded-lg font-semibold hover:opacity-90 transition-opacity flex items-center gap-2\"
          >
            <Plus className=\"h-5 w-5\" />
            New Scrape Job
          </Link>
          <Link 
            href=\"/billing\"
            className=\"border border-gray-600 text-white px-6 py-3 rounded-lg font-semibold hover:border-primary-500 transition-colors flex items-center gap-2\"
          >
            <CreditCard className=\"h-5 w-5\" />
            Manage Billing
          </Link>
        </div>

        {/* Jobs List */}
        <div className=\"glass rounded-xl overflow-hidden\">
          <div className=\"px-6 py-4 border-b border-gray-700\">
            <h2 className=\"text-xl font-semibold text-white\">Recent Jobs</h2>
          </div>
          
          {jobs.length === 0 ? (
            <div className=\"p-12 text-center\">
              <Target className=\"h-12 w-12 text-gray-500 mx-auto mb-4\" />
              <h3 className=\"text-lg font-medium text-white mb-2\">No jobs yet</h3>
              <p className=\"text-gray-400 mb-4\">
                Create your first scraping job to get started
              </p>
              <Link 
                href=\"/scrape\"
                className=\"gradient-primary text-black px-6 py-3 rounded-lg font-semibold hover:opacity-90 transition-opacity inline-flex items-center gap-2\"
              >
                <Plus className=\"h-5 w-5\" />
                Create Job
              </Link>
            </div>
          ) : (
            <div className=\"divide-y divide-gray-700\">
              {jobs.map((job) => (
                <div key={job.job_id} className=\"p-6 hover:bg-gray-800/50 transition-colors\">
                  <div className=\"flex items-center justify-between\">
                    <div className=\"flex-1\">
                      <div className=\"flex items-center gap-3 mb-2\">
                        {getStatusIcon(job.status)}
                        <h3 className=\"text-lg font-medium text-white\">
                          {job.business_type} in {job.location}
                        </h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${{
                          'completed': 'bg-green-500/20 text-green-400',
                          'failed': 'bg-red-500/20 text-red-400',
                          'processing': 'bg-yellow-500/20 text-yellow-400',
                          'pending': 'bg-gray-500/20 text-gray-400'
                        }[job.status] || 'bg-gray-500/20 text-gray-400'}`}>
                          {job.status}
                        </span>
                      </div>
                      <div className=\"text-sm text-gray-400 space-x-4\">
                        <span>Created: {new Date(job.created_at).toLocaleDateString()}</span>
                        <span>Leads: {job.total_leads}</span>
                        {job.processing_time && (
                          <span>Processing time: {job.processing_time.toFixed(1)}s</span>
                        )}
                      </div>
                    </div>
                    
                    <div className=\"flex items-center gap-2\">
                      {job.status === 'completed' && job.total_leads > 0 && (
                        <button
                          onClick={() => exportToCSV(job)}
                          className=\"p-2 text-gray-400 hover:text-primary-500 transition-colors\"
                          title=\"Export CSV\"
                        >
                          <Download className=\"h-5 w-5\" />
                        </button>
                      )}
                      {job.status === 'completed' && (
                        <button
                          onClick={() => setActiveJob(activeJob?.job_id === job.job_id ? null : job)}
                          className=\"text-primary-500 hover:text-primary-400 transition-colors text-sm font-medium\"
                        >
                          {activeJob?.job_id === job.job_id ? 'Hide' : 'View'} Results
                        </button>
                      )}
                    </div>
                  </div>
                  
                  {/* Job Results */}
                  {activeJob?.job_id === job.job_id && job.leads && (
                    <div className=\"mt-4 border-t border-gray-700 pt-4\">
                      <h4 className=\"text-white font-medium mb-3\">Leads ({job.leads.length})</h4>
                      <div className=\"space-y-2 max-h-64 overflow-y-auto\">
                        {job.leads.slice(0, 10).map((lead, index) => (
                          <div key={index} className=\"bg-gray-800/50 rounded-lg p-3\">
                            <div className=\"flex justify-between items-start\">
                              <div>
                                <h5 className=\"text-white font-medium\">{lead.business_name}</h5>
                                {lead.address && (
                                  <p className=\"text-gray-400 text-sm\">{lead.address}</p>
                                )}
                                {lead.phone && (
                                  <p className=\"text-primary-400 text-sm\">{lead.phone}</p>
                                )}
                              </div>
                              <div className=\"text-right\">
                                <div className=\"text-yellow-400 text-sm\">
                                  Quality: {lead.quality_score}/10
                                </div>
                                {lead.rating && (
                                  <div className=\"text-gray-400 text-sm\">
                                    ⭐ {lead.rating}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                        {job.leads.length > 10 && (
                          <div className=\"text-center py-2\">
                            <span className=\"text-gray-400 text-sm\">
                              ... and {job.leads.length - 10} more leads
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}