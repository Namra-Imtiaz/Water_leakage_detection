import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'

export default function ConfidenceChart({ data }) {
  if (!data?.length) {
    return <p className="chart-empty">No event history yet.</p>
  }

  const chartData = data
    .map((e) => ({
      time: e.timestamp,
      confidence: Math.round(e.confidence * 100),
      status: e.leak_status,
    }))
    .slice(-100) // last 100 for readability

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
          <YAxis
            domain={[0, 100]}
            stroke="var(--text-muted)"
            fontSize={11}
            tickSuffix="%"
          />
          <Tooltip
            contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
            labelFormatter={formatTime}
            formatter={(value) => [`${value}%`, 'Confidence']}
          />
          <ReferenceLine y={50} stroke="var(--text-muted)" strokeDasharray="2 2" />
          <Line
            type="monotone"
            dataKey="confidence"
            name="Confidence"
            stroke="var(--accent)"
            strokeWidth={2}
            dot={{ fill: 'var(--accent)', r: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
