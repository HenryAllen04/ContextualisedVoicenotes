/**
 * Purpose: Footer component for PODVOX application
 * Displays copyright information and links
 */

import React from 'react'

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-50 border-t border-gray-200 mt-16">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-gray-600 text-sm">
            © 2024 PODVOX. Built with ❤️ for personalized podcast outreach.
          </p>
          <p className="text-gray-500 text-xs mt-2">
            Powered by Sieve API and ElevenLabs
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer 