import './EventTable.css'

export default function EventTable({ events }) {
  if (!events?.length) {
    return <p className="event-table-empty">No events yet. Start the dummy sender or connect ESP32.</p>
  }

  return (
    <div className="event-table-wrap">
      <table className="event-table">
        <thead>
          <tr>
            <th>Status</th>
            <th>Confidence</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {events.map((e) => (
            <tr key={e.event_id}>
              <td>
                <span className={`status-badge ${e.leak_status === 'Leak' ? 'leak' : 'no-leak'}`}>
                  {e.leak_status === 'Leak' ? 'LEAK DETECTED' : 'NO LEAK'}
                </span>
              </td>
              <td>{Math.round(e.confidence * 100)}%</td>
              <td>{e.timestamp}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
