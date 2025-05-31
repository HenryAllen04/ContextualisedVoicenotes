/**
 * Purpose: Main component for processing podcast URLs and generating voicenotes
 * Handles form submission, API communication, and file download functionality
 */

import React, { useState } from 'react'
import { Upload, Download, Loader2, PlayCircle, ExternalLink, CheckCircle, AlertCircle } from 'lucide-react'
import axios from 'axios'

interface ProcessingResponse {
  message: string
  filename?: string
  download_url?: string
  processing_id?: string
}

interface ProcessingStatus {
  status: 'idle' | 'processing' | 'completed' | 'error'
  message: string
  progress?: number
}

const PodcastProcessor: React.FC = () => {
  const [podcastUrl, setPodcastUrl] = useState('')
  const [recipientName, setRecipientName] = useState('')
  const [podcastName, setPodcastName] = useState('')
  const [processingStatus, setProcessingStatus] = useState<ProcessingStatus>({
    status: 'idle',
    message: ''
  })
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null)
  const [isValidUrl, setIsValidUrl] = useState(true)

  // Backend API base URL - adjust this to match your backend
  const API_BASE_URL = 'http://localhost:8000'

  const validateUrl = (url: string): boolean => {
    try {
      new URL(url)
      return url.includes('youtube.com') || url.includes('youtu.be') || url.includes('spotify.com') || url.includes('podcasts.apple.com')
    } catch {
      return false
    }
  }

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value
    setPodcastUrl(url)
    if (url) {
      setIsValidUrl(validateUrl(url))
    } else {
      setIsValidUrl(true)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!podcastUrl || !recipientName || !isValidUrl) {
      setProcessingStatus({
        status: 'error',
        message: 'Please fill in all required fields with valid information.'
      })
      return
    }

    setProcessingStatus({
      status: 'processing',
      message: 'Analyzing podcast content and extracting key moments...',
      progress: 20
    })

    try {
      // Make actual API call to FastAPI backend
      setProcessingStatus({
        status: 'processing',
        message: 'Sending request to PODVOX backend...',
        progress: 10
      })

      const response = await axios.post<any>(`${API_BASE_URL}/generate-complete-voicenote`, {
        podcast_url: podcastUrl,
        prospect_name: recipientName,
        tone: "casual",
        script_length: "medium"
      })

      // Update progress through the pipeline stages
      setProcessingStatus({
        status: 'processing',
        message: 'Extracting hardship moments from podcast...',
        progress: 30
      })

      // Wait a bit for user to see progress
      await new Promise(resolve => setTimeout(resolve, 1000))

      setProcessingStatus({
        status: 'processing',
        message: 'Generating personalized AI script...',
        progress: 60
      })

      await new Promise(resolve => setTimeout(resolve, 1000))

      setProcessingStatus({
        status: 'processing',
        message: 'Creating voicenote with ElevenLabs AI voice...',
        progress: 90
      })

      await new Promise(resolve => setTimeout(resolve, 1000))

      // Check if we got a successful response
      if (response.data && response.data.status === 'success') {
        setProcessingStatus({
          status: 'completed',
          message: `Voicenote generated successfully for ${response.data.prospect_name}!`,
          progress: 100
        })
        
        // Set download URL from the response
        if (response.data.results && response.data.results.audio_file_url) {
          setDownloadUrl(response.data.results.audio_file_url)
        } else {
          // Fallback to a download endpoint
          setDownloadUrl(`${API_BASE_URL}/download-audio/${response.data.results?.filename || 'voicenote.mp3'}`)
        }
      } else {
        throw new Error(response.data?.message || 'Unknown error occurred')
      }

    } catch (error: any) {
      console.error('Processing error:', error)
      
      let errorMessage = 'Failed to process podcast. Please try again.'
      
      if (error.response) {
        // API responded with an error status
        errorMessage = error.response.data?.detail || error.response.data?.message || 'Backend error occurred'
      } else if (error.request) {
        // Request was made but no response received
        errorMessage = 'Cannot connect to backend. Make sure the API server is running on port 8000.'
      } else {
        // Something else happened
        errorMessage = error.message || 'Unexpected error occurred'
      }
      
      setProcessingStatus({
        status: 'error',
        message: errorMessage
      })
    }
  }

  const handleDownload = async () => {
    if (downloadUrl) {
      try {
        // If it's a relative URL, make it absolute
        const fullUrl = downloadUrl.startsWith('http') ? downloadUrl : `${API_BASE_URL}${downloadUrl}`
        
        // Use fetch to download the file
        const response = await fetch(fullUrl)
        if (!response.ok) {
          throw new Error('Download failed')
        }
        
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        
        // Create a temporary link to trigger download
        const link = document.createElement('a')
        link.href = url
        link.download = `${recipientName.replace(/\s+/g, '-').toLowerCase()}-personalized-voicenote.mp3`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        // Clean up the blob URL
        window.URL.revokeObjectURL(url)
      } catch (error) {
        console.error('Download error:', error)
        setProcessingStatus({
          status: 'error',
          message: 'Failed to download file. Please try again.'
        })
      }
    }
  }

  const resetForm = () => {
    setPodcastUrl('')
    setRecipientName('')
    setPodcastName('')
    setProcessingStatus({ status: 'idle', message: '' })
    setDownloadUrl(null)
    setIsValidUrl(true)
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-gray-900 mb-4">
          Transform Podcast Moments into 
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600"> Personal Outreach</span>
        </h2>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Enter a podcast URL and recipient details to generate a personalized voicenote that references specific moments from the episode.
        </p>
      </div>

      {/* Main Processing Card */}
      <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
        {/* Form Section */}
        <div className="p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Podcast URL Input */}
            <div>
              <label htmlFor="podcast-url" className="block text-sm font-medium text-gray-700 mb-2">
                Podcast URL *
              </label>
              <div className="relative">
                <input
                  type="url"
                  id="podcast-url"
                  value={podcastUrl}
                  onChange={handleUrlChange}
                  placeholder="https://www.youtube.com/watch?v=... or Spotify podcast link"
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                    !isValidUrl ? 'border-red-300 bg-red-50' : 'border-gray-300'
                  }`}
                  disabled={processingStatus.status === 'processing'}
                />
                <ExternalLink className="absolute right-3 top-3 w-5 h-5 text-gray-400" />
              </div>
              {!isValidUrl && (
                <p className="text-red-600 text-sm mt-1">Please enter a valid YouTube or podcast URL</p>
              )}
            </div>

            {/* Recipient Name Input */}
            <div>
              <label htmlFor="recipient-name" className="block text-sm font-medium text-gray-700 mb-2">
                Recipient Name *
              </label>
              <input
                type="text"
                id="recipient-name"
                value={recipientName}
                onChange={(e) => setRecipientName(e.target.value)}
                placeholder="e.g., Tim Ferriss, Joe Rogan"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                disabled={processingStatus.status === 'processing'}
              />
            </div>

            {/* Podcast Name Input (Optional) */}
            <div>
              <label htmlFor="podcast-name" className="block text-sm font-medium text-gray-700 mb-2">
                Podcast Name <span className="text-gray-500">(Optional)</span>
              </label>
              <input
                type="text"
                id="podcast-name"
                value={podcastName}
                onChange={(e) => setPodcastName(e.target.value)}
                placeholder="e.g., The Tim Ferriss Show, The Joe Rogan Experience"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                disabled={processingStatus.status === 'processing'}
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={processingStatus.status === 'processing' || !podcastUrl || !recipientName || !isValidUrl}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-lg font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed hover:from-blue-700 hover:to-purple-700 transition-all duration-200 flex items-center justify-center space-x-2"
            >
              {processingStatus.status === 'processing' ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <PlayCircle className="w-5 h-5" />
                  <span>Generate Personalized Voicenote</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Status Section */}
        {processingStatus.status !== 'idle' && (
          <div className="border-t border-gray-200 p-8 bg-gray-50">
            <div className="space-y-4">
              {/* Status Message */}
              <div className="flex items-center space-x-3">
                {processingStatus.status === 'processing' && (
                  <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                )}
                {processingStatus.status === 'completed' && (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                )}
                {processingStatus.status === 'error' && (
                  <AlertCircle className="w-5 h-5 text-red-600" />
                )}
                <p className={`font-medium ${
                  processingStatus.status === 'completed' ? 'text-green-800' :
                  processingStatus.status === 'error' ? 'text-red-800' :
                  'text-blue-800'
                }`}>
                  {processingStatus.message}
                </p>
              </div>

              {/* Progress Bar */}
              {processingStatus.status === 'processing' && processingStatus.progress && (
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${processingStatus.progress}%` }}
                  />
                </div>
              )}

              {/* Download Section */}
              {processingStatus.status === 'completed' && downloadUrl && (
                <div className="flex items-center space-x-4">
                  <button
                    onClick={handleDownload}
                    className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center space-x-2"
                  >
                    <Download className="w-5 h-5" />
                    <span>Download Voicenote</span>
                  </button>
                  <button
                    onClick={resetForm}
                    className="bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-700 transition-colors"
                  >
                    Generate Another
                  </button>
                </div>
              )}

              {/* Error Action */}
              {processingStatus.status === 'error' && (
                <button
                  onClick={resetForm}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                >
                  Try Again
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Features Section */}
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="text-center">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <Upload className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Analysis</h3>
          <p className="text-gray-600">AI extracts key moments and insights from any podcast episode</p>
        </div>
        <div className="text-center">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <PlayCircle className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Personal Touch</h3>
          <p className="text-gray-600">Generates contextual scripts that reference specific podcast moments</p>
        </div>
        <div className="text-center">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <Download className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Ready to Use</h3>
          <p className="text-gray-600">Download high-quality MP3 voicenotes ready for outreach</p>
        </div>
      </div>
    </div>
  )
}

export default PodcastProcessor 