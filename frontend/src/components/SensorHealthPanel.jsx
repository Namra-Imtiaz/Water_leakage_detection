import './SensorHealthPanel.css'

export default function SensorHealthPanel({ sensors }) {
  if (!sensors?.length) {
    return <p className="sensor-panel-empty">No sensors registered yet.</p>
  }

  return (
    <div className="sensor-panel">
      {sensors.map((s) => (
        <div key={s.sensor_id} className="sensor-card">
          <div className="sensor-name">{s.sensor_name}</div>
          <div className={`sensor-status ${s.health_status === 'Active' ? 'active' : 'inactive'}`}>
            {s.health_status}
          </div>
          <div className="sensor-last-seen">Last seen: {s.last_seen}</div>
        </div>
      ))}
    </div>
  )
}
