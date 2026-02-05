import { useState, useEffect } from 'react'
import { api } from '../services/api'
import LeakEventsChart from '../components/LeakEventsChart'
import SummaryChart from '../components/SummaryChart'
import ConfidenceChart from '../components/ConfidenceChart'
import './Analytics.css'

export default function Analytics() {
  const [history, setHistory] = useState([])
  const [summary, setSummary] = useState({ Leak: 0, 'No Leak': 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = async () => {
    try {
      setError(null)
      const [historyRes, summaryRes] = await Promise.all([
        api.getEventHistory(),
        api.getSummary(),
      ])
      setHistory(historyRes)
      setSummary(summaryRes)
    } catch (err) {
      setError(err.message || 'Failed to load analytics')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  if (loading) {
    return <div className="analytics-loading">Loading analytics...</div>
  }

  if (error) {
    return (
      <div className="analytics-error">
        <p>{error}</p>
        <button onClick={fetchData}>Retry</button>
      </div>
    )
  }

  return (
    <div className="analytics">
      <h1 className="page-title">Analytics</h1>
      <div className="analytics-grid">
        <section className="analytics-section chart-section">
          <h2>Number of Leak Events (Time-based)</h2>
          <LeakEventsChart data={history} />
        </section>
        <section className="analytics-section metrics-section">
          <h2>Leak vs No Leak</h2>
          <SummaryChart summary={summary} />
        </section>
        <section className="analytics-section chart-section full-width">
          <h2>Confidence Trend</h2>
          <ConfidenceChart data={history} />
        </section>
      </div>
    </div>
  )
}
