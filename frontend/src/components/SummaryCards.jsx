import './SummaryCards.css'

export default function SummaryCards({ leakStatus, confidence, lastEventTime, sensorHealth }) {
  return (
    <div className="summary-cards">
      <div className={`summary-card status-card ${leakStatus === 'Leak' ? 'leak' : 'no-leak'}`}>
        <div className="card-value">{leakStatus === 'Leak' ? 'LEAK DETECTED' : 'NO LEAK DETECTED'}</div>
        <div className="card-label">Leak Detection Status</div>
      </div>
      <div className="summary-card">
        <div className="card-value">{confidence}%</div>
        <div className="card-label">Current Confidence</div>
      </div>
      <div className="summary-card">
        <div className="card-value">{lastEventTime}</div>
        <div className="card-label">Last Event Time</div>
      </div>
      <div className="summary-card">
        <div className="card-value">{sensorHealth}</div>
        <div className="card-label">Sensor Health</div>
      </div>
    </div>
  )
}
