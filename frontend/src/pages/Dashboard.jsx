import { useState, useEffect } from 'react'
import { api } from '../services/api'
import EventTable from '../components/EventTable'
import SummaryCards from '../components/SummaryCards'
import './Dashboard.css'

export default function Dashboard() {
  const [events, setEvents] = useState([])
  const [summary, setSummary] = useState({ Leak: 0, 'No Leak': 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = async () => {
    try {
      setError(null)
      const [eventsRes, summaryRes] = await Promise.all([
        api.getRecentEvents(),
        api.getSummary(),
      ])
      setEvents(eventsRes)
      setSummary(summaryRes)
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 5000) // refresh every 5s
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return <div className="dashboard-loading">Loading dashboard...</div>
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <p>{error}</p>
        <p className="hint">Ensure Flask backend is running on port 5000.</p>
        <button onClick={fetchData}>Retry</button>
      </div>
    )
  }

  const latestEvent = events[0]
  const lastStatus = latestEvent?.leak_status || 'No Leak'
  const lastConfidence = latestEvent ? Math.round(latestEvent.confidence * 100) : 0
  const lastTime = latestEvent?.timestamp || '—'
  const sensorStatus = events.length ? 'Active' : '—'

  return (
    <div className="dashboard">
      <h1 className="page-title">Dashboard</h1>
      <SummaryCards
        leakStatus={lastStatus}
        confidence={lastConfidence}
        lastEventTime={lastTime}
        sensorHealth={sensorStatus}
      />
      <section className="section events-section">
        <h2>Recent Events</h2>
        <EventTable events={events} />
      </section>
    </div>
  )
}
