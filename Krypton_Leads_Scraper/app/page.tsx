'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Target, 
  Zap, 
  Users, 
  ArrowRight, 
  Check, 
  Star,
  MapPin,
  Phone,
  Globe,
  TrendingUp,
  Shield,
  Clock
} from 'lucide-react'
import Link from 'next/link'
import { useSession } from 'next-auth/react'

export default function HomePage() {
  const { data: session } = useSession()
  const [activePlan, setActivePlan] = useState('pro')

  const plans = [
    {
      id: 'starter',
      name: 'Starter',
      price: 19,
      leads: '500',
      features: [
        '500 leads per month',
        'Basic export (CSV)',
        'Email support',
        'Standard speed'
      ]
    },
    {
      id: 'pro',
      name: 'Pro',
      price: 49,
      leads: '2,000',
      popular: true,
      features: [
        '2,000 leads per month',
        'Advanced export (CSV, Excel)',
        'Priority support',
        'High-speed scraping',
        'API access'
      ]
    },
    {
      id: 'business',
      name: 'Business',
      price: 99,
      leads: '5,000',
      features: [
        '5,000 leads per month',
        'Premium export options',
        'Phone + email support',
        'Ultra-fast scraping',
        'Full API access',
        'Custom integrations'
      ]
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 199,
      leads: 'Unlimited',
      features: [
        'Unlimited leads',
        'White-label options',
        'Dedicated account manager',
        'Custom scraping rules',
        'SLA guarantee',
        'On-premise deployment'
      ]
    }
  ]

  return (
    <div className=\"min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900\">
      {/* Navigation */}
      <nav className=\"fixed top-0 w-full z-50 glass border-b border-gray-800\">
        <div className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8\">
          <div className=\"flex justify-between items-center h-16\">
            <div className=\"flex items-center space-x-2\">
              <Target className=\"h-8 w-8 text-primary-500\" />
              <span className=\"text-2xl font-bold text-white\">Krypton</span>
            </div>
            <div className=\"hidden md:flex items-center space-x-8\">
              <a href=\"#features\" className=\"text-gray-300 hover:text-primary-500 transition-colors\">Features</a>
              <a href=\"#pricing\" className=\"text-gray-300 hover:text-primary-500 transition-colors\">Pricing</a>
              <a href=\"#testimonials\" className=\"text-gray-300 hover:text-primary-500 transition-colors\">Reviews</a>
            </div>
            <div className=\"flex items-center space-x-4\">
              {session ? (
                <Link href=\"/dashboard\" className=\"gradient-primary text-black px-4 py-2 rounded-lg font-semibold hover:opacity-90 transition-opacity\">
                  Dashboard
                </Link>
              ) : (
                <>
                  <Link href=\"/auth/signin\" className=\"text-gray-300 hover:text-white transition-colors\">
                    Sign In
                  </Link>
                  <Link href=\"/auth/signup\" className=\"gradient-primary text-black px-4 py-2 rounded-lg font-semibold hover:opacity-90 transition-opacity\">
                    Get Started
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className=\"pt-32 pb-20 px-4\">
        <div className=\"max-w-7xl mx-auto text-center\">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className=\"text-5xl md:text-7xl font-bold text-white mb-6\">
              Generate <span className=\"text-gradient\">Local Leads</span><br />
              in Seconds
            </h1>
            <p className=\"text-xl text-gray-400 mb-8 max-w-3xl mx-auto\">
              AI-powered lead generation that finds high-quality local businesses from Google Maps. 
              Target restaurants, gyms, salons, and more with precision.
            </p>
            <div className=\"flex flex-col sm:flex-row gap-4 justify-center items-center\">
              <Link href=\"/auth/signup\" className=\"gradient-primary text-black px-8 py-4 rounded-lg font-bold text-lg hover:opacity-90 transition-opacity flex items-center gap-2\">
                Start Free Trial <ArrowRight className=\"h-5 w-5\" />
              </Link>
              <Link href=\"#demo\" className=\"border border-gray-600 text-white px-8 py-4 rounded-lg font-semibold hover:border-primary-500 transition-colors\">
                Watch Demo
              </Link>
            </div>
            <p className=\"text-sm text-gray-500 mt-4\">✨ No credit card required • 7-day free trial</p>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className=\"py-20 px-4\">
        <div className=\"max-w-7xl mx-auto\">
          <div className=\"grid grid-cols-1 md:grid-cols-4 gap-8\">
            {[
              { number: '50K+', label: 'Businesses Scraped' },
              { number: '2.5K+', label: 'Happy Customers' },
              { number: '99.9%', label: 'Uptime' },
              { number: '< 30s', label: 'Average Speed' }
            ].map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className=\"text-center glass rounded-xl p-6\"
              >
                <div className=\"text-3xl font-bold text-gradient mb-2\">{stat.number}</div>
                <div className=\"text-gray-400\">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id=\"features\" className=\"py-20 px-4\">
        <div className=\"max-w-7xl mx-auto\">
          <div className=\"text-center mb-16\">
            <h2 className=\"text-4xl font-bold text-white mb-4\">
              Why Choose <span className=\"text-gradient\">Krypton</span>?
            </h2>
            <p className=\"text-gray-400 text-lg max-w-2xl mx-auto\">
              Advanced AI technology meets enterprise-grade infrastructure
            </p>
          </div>
          
          <div className=\"grid grid-cols-1 md:grid-cols-3 gap-8\">
            {[
              {
                icon: <Zap className=\"h-8 w-8\" />,
                title: 'Lightning Fast',
                description: 'Generate thousands of leads in under 30 seconds with our optimized scraping engine.'
              },
              {
                icon: <Shield className=\"h-8 w-8\" />,
                title: 'Always Reliable',
                description: 'Enterprise-grade infrastructure with 99.9% uptime and automatic failover.'
              },
              {
                icon: <Target className=\"h-8 w-8\" />,
                title: 'Laser Precision',
                description: 'Advanced filtering and targeting to find exactly the businesses you need.'
              },
              {
                icon: <Globe className=\"h-8 w-8\" />,
                title: 'Global Coverage',
                description: 'Scrape businesses from any location worldwide with local market insights.'
              },
              {
                icon: <TrendingUp className=\"h-8 w-8\" />,
                title: 'Smart Analytics',
                description: 'Track performance, conversion rates, and ROI with built-in analytics.'
              },
              {
                icon: <Clock className=\"h-8 w-8\" />,
                title: 'Real-time Updates',
                description: 'Get fresh, up-to-date business information with real-time verification.'
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className=\"glass rounded-xl p-6 hover:bg-gray-800/50 transition-colors\"
              >
                <div className=\"text-primary-500 mb-4\">{feature.icon}</div>
                <h3 className=\"text-xl font-semibold text-white mb-2\">{feature.title}</h3>
                <p className=\"text-gray-400\">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id=\"pricing\" className=\"py-20 px-4\">
        <div className=\"max-w-7xl mx-auto\">
          <div className=\"text-center mb-16\">
            <h2 className=\"text-4xl font-bold text-white mb-4\">
              Simple, <span className=\"text-gradient\">Transparent</span> Pricing
            </h2>
            <p className=\"text-gray-400 text-lg\">
              Choose the perfect plan for your business needs
            </p>
          </div>
          
          <div className=\"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6\">
            {plans.map((plan) => (
              <motion.div
                key={plan.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className={`glass rounded-xl p-6 relative ${
                  plan.popular ? 'ring-2 ring-primary-500' : ''
                }`}
              >
                {plan.popular && (
                  <div className=\"absolute -top-3 left-1/2 transform -translate-x-1/2\">
                    <span className=\"gradient-primary text-black px-3 py-1 rounded-full text-sm font-semibold\">
                      Most Popular
                    </span>
                  </div>
                )}
                
                <div className=\"text-center mb-6\">
                  <h3 className=\"text-xl font-semibold text-white mb-2\">{plan.name}</h3>
                  <div className=\"text-3xl font-bold text-white mb-1\">
                    ${plan.price}
                    <span className=\"text-gray-400 text-lg font-normal\">/mo</span>
                  </div>
                  <p className=\"text-primary-500 font-semibold\">{plan.leads} leads</p>
                </div>
                
                <ul className=\"space-y-3 mb-6\">
                  {plan.features.map((feature, index) => (
                    <li key={index} className=\"flex items-center text-gray-300\">
                      <Check className=\"h-4 w-4 text-primary-500 mr-2 flex-shrink-0\" />
                      {feature}
                    </li>
                  ))}
                </ul>
                
                <Link 
                  href={`/checkout?plan=${plan.id}`}
                  className={`block w-full text-center py-3 rounded-lg font-semibold transition-colors ${
                    plan.popular 
                      ? 'gradient-primary text-black hover:opacity-90' 
                      : 'border border-gray-600 text-white hover:border-primary-500'
                  }`}
                >
                  Get Started
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id=\"testimonials\" className=\"py-20 px-4\">
        <div className=\"max-w-7xl mx-auto\">
          <div className=\"text-center mb-16\">
            <h2 className=\"text-4xl font-bold text-white mb-4\">
              What Our <span className=\"text-gradient\">Customers</span> Say
            </h2>
          </div>
          
          <div className=\"grid grid-cols-1 md:grid-cols-3 gap-8\">
            {[
              {
                name: 'Sarah Johnson',
                role: 'Marketing Director',
                company: 'FitLife Gyms',
                content: 'Krypton helped us generate 500+ qualified leads in our first month. The ROI is incredible!',
                rating: 5
              },
              {
                name: 'Mike Chen',
                role: 'Restaurant Owner',
                company: 'Chen\'s Kitchen',
                content: 'Perfect for local restaurant marketing. Found competitors and potential partnerships easily.',
                rating: 5
              },
              {
                name: 'Lisa Rodriguez',
                role: 'Salon Owner',
                company: 'Beauty Bliss',
                content: 'The lead quality is outstanding. Converted 15% of leads to customers immediately.',
                rating: 5
              }
            ].map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className=\"glass rounded-xl p-6\"
              >
                <div className=\"flex mb-4\">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className=\"h-5 w-5 text-yellow-500 fill-current\" />
                  ))}
                </div>
                <p className=\"text-gray-300 mb-4\">"{testimonial.content}"</p>
                <div className=\"border-t border-gray-700 pt-4\">
                  <div className=\"font-semibold text-white\">{testimonial.name}</div>
                  <div className=\"text-gray-400 text-sm\">{testimonial.role} at {testimonial.company}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className=\"py-20 px-4\">
        <div className=\"max-w-4xl mx-auto text-center glass rounded-2xl p-12\">
          <h2 className=\"text-4xl font-bold text-white mb-4\">
            Ready to <span className=\"text-gradient\">Supercharge</span> Your Lead Generation?
          </h2>
          <p className=\"text-gray-400 text-lg mb-8\">
            Join thousands of businesses already using Krypton to grow faster
          </p>
          <Link href=\"/auth/signup\" className=\"gradient-primary text-black px-8 py-4 rounded-lg font-bold text-lg hover:opacity-90 transition-opacity inline-flex items-center gap-2\">
            Start Your Free Trial <ArrowRight className=\"h-5 w-5\" />
          </Link>
          <p className=\"text-sm text-gray-500 mt-4\">🚀 Setup takes less than 2 minutes</p>
        </div>
      </section>

      {/* Footer */}
      <footer className=\"py-12 px-4 border-t border-gray-800\">
        <div className=\"max-w-7xl mx-auto\">
          <div className=\"grid grid-cols-1 md:grid-cols-4 gap-8\">
            <div>
              <div className=\"flex items-center space-x-2 mb-4\">
                <Target className=\"h-6 w-6 text-primary-500\" />
                <span className=\"text-xl font-bold text-white\">Krypton</span>
              </div>
              <p className=\"text-gray-400 text-sm\">
                AI-powered lead generation for modern businesses.
              </p>
            </div>
            
            <div>
              <h4 className=\"text-white font-semibold mb-4\">Product</h4>
              <ul className=\"space-y-2 text-gray-400 text-sm\">
                <li><a href=\"#features\" className=\"hover:text-primary-500 transition-colors\">Features</a></li>
                <li><a href=\"#pricing\" className=\"hover:text-primary-500 transition-colors\">Pricing</a></li>
                <li><a href=\"/api-docs\" className=\"hover:text-primary-500 transition-colors\">API Docs</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className=\"text-white font-semibold mb-4\">Company</h4>
              <ul className=\"space-y-2 text-gray-400 text-sm\">
                <li><a href=\"/about\" className=\"hover:text-primary-500 transition-colors\">About</a></li>
                <li><a href=\"/contact\" className=\"hover:text-primary-500 transition-colors\">Contact</a></li>
                <li><a href=\"/careers\" className=\"hover:text-primary-500 transition-colors\">Careers</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className=\"text-white font-semibold mb-4\">Legal</h4>
              <ul className=\"space-y-2 text-gray-400 text-sm\">
                <li><a href=\"/privacy\" className=\"hover:text-primary-500 transition-colors\">Privacy Policy</a></li>
                <li><a href=\"/terms\" className=\"hover:text-primary-500 transition-colors\">Terms of Service</a></li>
                <li><a href=\"/security\" className=\"hover:text-primary-500 transition-colors\">Security</a></li>
              </ul>
            </div>
          </div>
          
          <div className=\"border-t border-gray-800 mt-8 pt-8 text-center\">
            <p className=\"text-gray-400 text-sm\">
              © 2024 Krypton Leads. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}