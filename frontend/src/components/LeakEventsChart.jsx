import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

export default function LeakEventsChart({ data }) {
  if (!data?.length) {
    return <p className="chart-empty">No event history yet.</p>
  }

  // Group by timestamp and count leak events
  const byTime = {}
  data.forEach((e) => {
    const t = e.timestamp
    if (!byTime[t]) byTime[t] = { time: t, leak: 0, noLeak: 0, total: 0 }
    if (e.leak_status === 'Leak') byTime[t].leak += 1
    else byTime[t].noLeak += 1
    byTime[t].total += 1
  })

  const chartData = Object.values(byTime).sort(
    (a, b) => new Date(a.time) - new Date(b.time)
  )

  // Shorten labels for X axis
  const formatTime = (t) => {
    if (!t) return ''
    const d = new Date(t)
    return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis
            dataKey="time"
            tickFormatter={formatTime}
            stroke="var(--text-muted)"
            fontSize={11}
          />
          <YAxis stroke="var(--text-muted)" fontSize={11} allowDecimals={false} />
          <Tooltip
            contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
            labelFormatter={formatTime}
          />
          <Line
            type="monotone"
            dataKey="total"
            name="Events"
            stroke="var(--accent)"
            strokeWidth={2}
            dot={{ fill: 'var(--accent)' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
