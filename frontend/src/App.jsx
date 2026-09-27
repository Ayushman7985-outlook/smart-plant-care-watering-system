import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";
const DEVICE_ID = "PLANT-001";

function App() {
  const [latest, setLatest] = useState(null);
  const [history, setHistory] = useState([]);
  const [pumpStatus, setPumpStatus] = useState("OFF");
  const [autoWatering, setAutoWatering] = useState(true);
  const [threshold, setThreshold] = useState(30);
  const [thresholdInput, setThresholdInput] = useState(30);
  const [alerts, setAlerts] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [backendOnline, setBackendOnline] = useState(false);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  async function fetchData() {
    try {
      const [
        latestResponse,
        historyResponse,
        pumpResponse,
        autoResponse,
        thresholdResponse,
        alertsResponse,
        analyticsResponse,
      ] = await Promise.all([
        fetch(`${API}/api/devices/${DEVICE_ID}/latest`),
        fetch(`${API}/api/devices/${DEVICE_ID}/history`),
        fetch(`${API}/api/devices/${DEVICE_ID}/pump-status`),
        fetch(`${API}/api/devices/${DEVICE_ID}/auto-status`),
        fetch(`${API}/api/devices/${DEVICE_ID}/threshold`),
        fetch(`${API}/api/devices/${DEVICE_ID}/alerts`),
        fetch(`${API}/api/devices/${DEVICE_ID}/analytics`),
      ]);

      if (!latestResponse.ok) {
        throw new Error("Backend request failed");
      }

      const latestData = await latestResponse.json();
      const historyData = await historyResponse.json();
      const pumpData = await pumpResponse.json();
      const autoData = await autoResponse.json();
      const thresholdData = await thresholdResponse.json();
      const alertsData = await alertsResponse.json();
      const analyticsData = await analyticsResponse.json();

      setLatest(latestData);
      setHistory(historyData.readings || []);
      setPumpStatus(pumpData.pump_status || "OFF");
      setAutoWatering(autoData.auto_watering_enabled ?? true);
      setThreshold(thresholdData.moisture_threshold ?? 30);
      setThresholdInput(thresholdData.moisture_threshold ?? 30);
      setAlerts(alertsData.alerts || []);
      setAnalytics(analyticsData);
      setBackendOnline(true);
    } catch (error) {
      console.error(error);
      setBackendOnline(false);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchData();

    const interval = setInterval(fetchData, 5000);

    return () => clearInterval(interval);
  }, []);

  async function manualWater() {
    try {
      const response = await fetch(
        `${API}/api/devices/${DEVICE_ID}/water`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      setMessage(data.watering?.message || data.message);

      fetchData();
    } catch (error) {
      setMessage("Unable to activate virtual pump.");
    }
  }

  async function toggleAutoWatering() {
    try {
      const newValue = !autoWatering;

      const response = await fetch(
        `${API}/api/devices/${DEVICE_ID}/auto-water?enabled=${newValue}`,
        {
          method: "PUT",
        }
      );

      const data = await response.json();

      setAutoWatering(data.auto_watering_enabled);
      setMessage(data.message);

      fetchData();
    } catch (error) {
      setMessage("Unable to change automatic watering.");
    }
  }

  async function updateThreshold() {
    try {
      const response = await fetch(
        `${API}/api/devices/${DEVICE_ID}/threshold`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            threshold: Number(thresholdInput),
          }),
        }
      );

      const data = await response.json();

      setThreshold(data.moisture_threshold);
      setMessage(data.message);

      fetchData();
    } catch (error) {
      setMessage("Unable to update threshold.");
    }
  }

  const moisture = latest?.soil_moisture ?? 0;
  const temperature = latest?.temperature ?? 0;
  const humidity = latest?.humidity ?? 0;
  const light = latest?.light_level ?? 0;

  let plantStatus = "Healthy";

  if (moisture < threshold) {
    plantStatus = "Needs Water";
  } else if (moisture < threshold + 10) {
    plantStatus = "Monitor";
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>🌱 Smart Plant Care</h1>
          <p>Cloud-Connected IoT Plant Monitoring System</p>
        </div>

        <div className="device-status">
          <span
            className={`status-dot ${
              backendOnline ? "online" : "offline"
            }`}
          ></span>

          {backendOnline ? "Backend Online" : "Backend Offline"}
        </div>
      </header>

      <main className="container">
        {message && (
          <div className="message">
            {message}
            <button onClick={() => setMessage("")}>×</button>
          </div>
        )}

        {loading ? (
          <div className="loading">
            Loading plant data...
          </div>
        ) : (
          <>
            <section className="overview-grid">
              <div className="card">
                <span className="card-icon">💧</span>
                <h3>Soil Moisture</h3>
                <div className="big-value">{moisture}%</div>
                <p>Threshold: {threshold}%</p>
              </div>

              <div className="card">
                <span className="card-icon">🌡️</span>
                <h3>Temperature</h3>
                <div className="big-value">{temperature}°C</div>
                <p>Air temperature</p>
              </div>

              <div className="card">
                <span className="card-icon">💨</span>
                <h3>Humidity</h3>
                <div className="big-value">{humidity}%</div>
                <p>Air humidity</p>
              </div>

              <div className="card">
                <span className="card-icon">☀️</span>
                <h3>Light Level</h3>
                <div className="big-value">{light}%</div>
                <p>Ambient light</p>
              </div>
            </section>

            <section className="main-grid">
              <div className="panel">
                <div className="panel-header">
                  <h2>Plant Status</h2>
                  <span
                    className={`plant-badge ${
                      plantStatus === "Healthy"
                        ? "healthy"
                        : plantStatus === "Monitor"
                        ? "monitor"
                        : "needs-water"
                    }`}
                  >
                    {plantStatus}
                  </span>
                </div>

                <div className="plant-info">
                  <div>
                    <strong>Device</strong>
                    <span>{DEVICE_ID}</span>
                  </div>

                  <div>
                    <strong>Virtual Pump</strong>
                    <span
                      className={
                        pumpStatus === "ON"
                          ? "pump-on"
                          : "pump-off"
                      }
                    >
                      {pumpStatus}
                    </span>
                  </div>

                  <div>
                    <strong>Automatic Watering</strong>
                    <span>
                      {autoWatering ? "Enabled" : "Disabled"}
                    </span>
                  </div>
                </div>

                <div className="controls">
                  <button
                    className="primary-button"
                    onClick={manualWater}
                  >
                    💧 Water Plant
                  </button>

                  <button
                    className={`secondary-button ${
                      autoWatering ? "enabled-button" : ""
                    }`}
                    onClick={toggleAutoWatering}
                  >
                    {autoWatering
                      ? "Disable Auto Watering"
                      : "Enable Auto Watering"}
                  </button>
                </div>
              </div>

              <div className="panel">
                <h2>Moisture Threshold</h2>

                <div className="threshold-control">
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={thresholdInput}
                    onChange={(event) =>
                      setThresholdInput(event.target.value)
                    }
                  />

                  <span>%</span>

                  <button
                    className="primary-button"
                    onClick={updateThreshold}
                  >
                    Save
                  </button>
                </div>

                <p className="helper-text">
                  Automatic watering starts when soil moisture
                  drops below this value.
                </p>
              </div>
            </section>

            <section className="panel">
              <div className="panel-header">
                <h2>Moisture History</h2>
                <span>{history.length} readings</span>
              </div>

              <div className="chart">
                {history.length === 0 ? (
                  <p>No sensor readings available yet.</p>
                ) : (
                  history.slice(-20).map((reading, index) => (
                    <div
                      className="bar-wrapper"
                      key={`${reading.timestamp}-${index}`}
                    >
                      <div
                        className="bar"
                        style={{
                          height: `${Math.max(
                            8,
                            reading.soil_moisture
                          )}%`,
                        }}
                        title={`Moisture: ${reading.soil_moisture}%`}
                      ></div>

                      <span>
                        {Math.round(reading.soil_moisture)}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </section>

            <section className="main-grid">
              <div className="panel">
                <div className="panel-header">
                  <h2>Alerts</h2>
                  <span>{alerts.length}</span>
                </div>

                {alerts.length === 0 ? (
                  <div className="no-alert">
                    ✅ No active alerts
                  </div>
                ) : (
                  <div className="alerts">
                    {alerts.map((alert, index) => (
                      <div
                        className={`alert ${alert.severity}`}
                        key={index}
                      >
                        <strong>{alert.type}</strong>
                        <p>{alert.message}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="panel">
                <h2>Analytics</h2>

                {analytics ? (
                  <div className="analytics-grid">
                    <div>
                      <strong>
                        {analytics.reading_count}
                      </strong>
                      <span>Readings</span>
                    </div>

                    <div>
                      <strong>
                        {analytics.average_soil_moisture}%
                      </strong>
                      <span>Avg Moisture</span>
                    </div>

                    <div>
                      <strong>
                        {analytics.average_temperature}°C
                      </strong>
                      <span>Avg Temperature</span>
                    </div>

                    <div>
                      <strong>
                        {analytics.watering_events}
                      </strong>
                      <span>Watering Events</span>
                    </div>
                  </div>
                ) : (
                  <p>No analytics available.</p>
                )}
              </div>
            </section>

            <section className="panel system-panel">
              <h2>System Information</h2>

              <div className="system-grid">
                <div>
                  <strong>Device ID</strong>
                  <span>{DEVICE_ID}</span>
                </div>

                <div>
                  <strong>Backend</strong>
                  <span>FastAPI</span>
                </div>

                <div>
                  <strong>Database</strong>
                  <span>Firebase Firestore</span>
                </div>

                <div>
                  <strong>Frontend</strong>
                  <span>React + Vite</span>
                </div>

                <div>
                  <strong>Sensor</strong>
                  <span>Virtual IoT Simulator</span>
                </div>

                <div>
                  <strong>Pump</strong>
                  <span>Virtual Pump</span>
                </div>
              </div>
            </section>
          </>
        )}
      </main>

      <footer>
        Smart Plant Care & Watering System • EDC IIT Delhi
      </footer>
    </div>
  );
}

export default App;