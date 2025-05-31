/**
 * Purpose: Header component for PODVOX application
 * Displays branding, navigation, and key information about the service
 */

import React from 'react'
import { Mic, Podcast } from 'lucide-react'

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
              <Mic className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">PODVOX</h1>
              <p className="text-sm text-gray-600">Personalized Podcast Outreach Engine</p>
            </div>
          </div>
          
          <div className="hidden md:flex items-center space-x-6">
            <div className="flex items-center space-x-2 text-gray-600">
              <Podcast className="w-5 h-5" />
              <span className="text-sm">Transform any podcast into personalized outreach</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header 