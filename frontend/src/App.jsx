import React, { useEffect, useState } from 'react'
import './App.css'
import ChatPage from './components/ChatPage'
import APIClient from './services/api'

function App() {
  const [isHealthy, setIsHealthy] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Check backend health on startup
  useEffect(() => {
    const checkHealth = async () => {
      try {
        await APIClient.getHealth()
        setIsHealthy(true)
      } catch (error) {
        console.error('Backend health check failed:', error)
        setIsHealthy(false)
      } finally {
        setIsLoading(false)
      }
    }

    checkHealth()
  }, [])

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-gray-700 border-t-blue-500 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Connecting to backend...</p>
        </div>
      </div>
    )
  }

  if (!isHealthy) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <svg className="w-16 h-16 mx-auto mb-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" />
          </svg>
          <h2 className="text-2xl font-semibold text-red-400 mb-2">Connection Error</h2>
          <p className="text-gray-400 mb-4">Unable to connect to backend server</p>
          <p className="text-sm text-gray-500">Make sure the backend is running on {import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return <ChatPage />
}

export default App
