import { useEffect, useState } from 'react'
import axios from 'axios'
import { format } from 'date-fns'

function App() {
  const [actions, setActions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchActions = async () => {
    try {
      setLoading(true)
      const response = await axios.get('http://0222-2409-40e4-108a-f119-4cbd-96d-1980-abf3.ngrok-free.app/api/actions')
      // Ensure we always have an array, even if response.data is null/undefined
      setActions(Array.isArray(response.data) ? response.data : [])
      setError(null)
    } catch (err) {
      console.error('Error fetching actions:', err)
      setError('Failed to load actions')
      setActions([]) // Reset to empty array on error
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchActions()
    const interval = setInterval(fetchActions, 15000)
    return () => clearInterval(interval)
  }, [])

  const formatActionMessage = (action) => {
    const date = new Date(action.timestamp)
    const formattedDate = format(date, "do MMMM yyyy - h:mm a 'UTC'")

    switch(action.action) {
      case 'PUSH':
        return `${action.author} pushed to ${action.to_branch} on ${formattedDate}`
      case 'PULL_REQUEST':
        return `${action.author} submitted a pull request from ${action.from_branch} to ${action.to_branch} on ${formattedDate}`
      case 'MERGE':
        return `${action.author} merged branch ${action.from_branch} to ${action.to_branch} on ${formattedDate}`
      default:
        return ''
    }
  }

  return (
    <div className="container">
      <h1>GitHub Actions Monitor</h1>
      {error && <p className="error">{error}</p>}
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="actions-list">
          {actions.length === 0 ? (
            <p>No actions recorded yet</p>
          ) : (
            actions.map((action) => (
              <div key={action._id} className="action-item">
                <p>{formatActionMessage(action)}</p>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}

export default App