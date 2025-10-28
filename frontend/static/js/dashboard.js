const bpmCtx = document.getElementById('bpmChart').getContext('2d');
const tempCtx = document.getElementById('tempChart').getContext('2d');

const alertPanel = document.getElementById('alert-panel');
const alertMessage = document.getElementById('alert-message');

// Sonido de alerta
const alertSound = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg');

let bpmChart = new Chart(bpmCtx, {
  type: 'line',
  data: { labels: [], datasets: [{ label: 'BPM', data: [], borderColor: 'red' }] },
  options: { scales: { y: { beginAtZero: true } } }
});

let tempChart = new Chart(tempCtx, {
  type: 'line',
  data: { labels: [], datasets: [{ label: 'Temperatura °C', data: [], borderColor: 'orange' }] },
  options: { scales: { y: { beginAtZero: true } } }
});

async function updateCharts() {
  try {
    const res = await fetch('http://127.0.0.1:8001/health-data');
    const data = await res.json();

    if (Array.isArray(data) && data.length > 0) {
      const timestamps = data.map(d => d.timestamp);
      const bpm = data.map(d => d.datos.ritmo_cardiaco);
      const temp = data.map(d => d.datos.temperatura);

      bpmChart.data.labels = timestamps;
      bpmChart.data.datasets[0].data = bpm;
      tempChart.data.labels = timestamps;
      tempChart.data.datasets[0].data = temp;

      bpmChart.update();
      tempChart.update();

      // 🔍 Detección de alertas
      const lastBpm = bpm[bpm.length - 1];
      const lastTemp = temp[temp.length - 1];
      checkAlerts(lastBpm, lastTemp);
    }
  } catch (error) {
    console.error("Error al obtener datos:", error);
  }
}

function checkAlerts(bpm, temp) {
  let messages = [];

  if (bpm > 100) messages.push(`Ritmo cardíaco alto (${bpm} BPM)`);
  if (bpm < 50) messages.push(`Ritmo cardíaco bajo (${bpm} BPM)`);
  if (temp > 37.8) messages.push(`Temperatura elevada (${temp}°C)`);
  if (temp < 35.5) messages.push(`Temperatura baja (${temp}°C)`);

  if (messages.length > 0) {
    alertMessage.textContent = messages.join(' | ');
    alertPanel.classList.remove('hidden');
    alertSound.play();
  } else {
    alertPanel.classList.add('hidden');
  }
}

setInterval(updateCharts, 5000); // cada 5s
updateCharts();
