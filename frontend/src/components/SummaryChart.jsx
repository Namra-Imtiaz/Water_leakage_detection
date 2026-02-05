import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

export default function SummaryChart({ summary }) {
  const data = [
    { name: 'Leak', count: summary?.Leak ?? 0, fill: 'var(--leak)' },
    { name: 'No Leak', count: summary?.['No Leak'] ?? 0, fill: 'var(--no-leak)' },
  ]

  if (data.every((d) => d.count === 0)) {
    return <p className="chart-empty">No events yet.</p>
  }

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} />
          <YAxis stroke="var(--text-muted)" fontSize={11} allowDecimals={false} />
          <Tooltip
            contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
          />
          <Bar dataKey="count" name="Count" radius={[6, 6, 0, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
