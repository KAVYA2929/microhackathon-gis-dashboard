// MAP
var map = L.map('map', { zoomControl: false }).setView([12.8231, 80.0444], 16);

var tileLayer = L.tileLayer(
  'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
).addTo(map);

window.updateMapTheme = function (theme) {
  if (theme === 'dark') {
    tileLayer.setUrl('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png');
  } else {
    tileLayer.setUrl('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png');
  }

  // Update safe cable colors
  let safeColor = (theme === 'dark') ? 'cyan' : '#1976D2';
  for (let id in cables) {
    if (cables[id].options.color === 'cyan' || cables[id].options.color === '#1976D2') {
      cables[id].setStyle({ color: safeColor });
    }
  }
};

// STORAGE
var cables = {};

// FETCH MULTI-NODE DATA
var lastUpdateSeconds = 0;
var updateInterval = setInterval(() => {
  lastUpdateSeconds++;
  document.getElementById("lastUpdated").innerText = `Last update: ${lastUpdateSeconds} second(s) ago...`;
}, 1000);

let dataPollTimer = setInterval(() => {
  fetch("http://localhost:5000/data")
    .then(res => res.json())
    .then(nodes => {

      let readingsBody = document.getElementById("readingsBody");
      let bendingAlerts = document.getElementById("bendingAlerts");
      let predictiveAnalysis = document.getElementById("predictiveAnalysis");

      if (readingsBody) readingsBody.innerHTML = "";
      if (bendingAlerts) bendingAlerts.innerHTML = "";
      if (predictiveAnalysis) predictiveAnalysis.innerHTML = "";

      // Reset last update counter whenever data successfully loads
      lastUpdateSeconds = 0;
      document.getElementById("lastUpdated").innerText = `Last update: just now`;

      let hasBending = false;

      nodes.forEach(n => {

        let safeColor = (window.currentTheme === 'dark') ? 'cyan' : '#1976D2';

        // CREATE CABLE IF NOT EXISTS
        if (!cables[n.node_id]) {
          cables[n.node_id] = L.polyline(n.path, { color: safeColor, weight: 6 }).addTo(map);
        }

        // STATUS COLOR
        let statusClass = "safe";
        let lineColor = safeColor;

        if (n.status === "DANGER") {
          statusClass = "danger";
          lineColor = "red";
          if (cables[n.node_id].getElement()) cables[n.node_id].getElement().classList.add("blink");
        } else if (n.status === "WARNING") {
          statusClass = "warning";
          lineColor = "orange";
          if (cables[n.node_id].getElement()) cables[n.node_id].getElement().classList.remove("blink");
        } else {
          lineColor = safeColor;
          if (cables[n.node_id].getElement()) cables[n.node_id].getElement().classList.remove("blink");
        }

        cables[n.node_id].setStyle({ color: lineColor });

        cables[n.node_id].bindPopup(
          `<b>${n.node_id}</b><br>Status: ${n.status}<br>Vib 1: ${n.vibration_1}<br>Vib 2: ${n.vibration_2}<br>Gyro: ${n.gyroscope}<br>Photo: ${n.photodiode}<br><button onclick="showHistory('${n.node_id}')" style="margin-top:8px; padding:4px 8px; cursor:pointer;">View History</button>`
        );

        // 1. Live Readings
        if (readingsBody) {
          let tr = document.createElement("tr");
          tr.innerHTML = `
            <td>${n.node_id}</td>
            <td>${n.vibration_1}</td>
            <td>${n.vibration_2}</td>
            <td>${n.gyroscope}°/s</td>
            <td>${n.photodiode}%</td>
            <td class="${statusClass}">${n.status}</td>
          `;
          readingsBody.appendChild(tr);
        }

        // 2. Bending Alerts
        if (n.is_bending && bendingAlerts) {
          hasBending = true;
          let bendDiv = document.createElement("div");
          bendDiv.className = "predictive-box danger blink";
          bendDiv.innerHTML = `⚠️ <span class="predictive-node">${n.node_id}</span> : Critical bending detected! Gyro: ${n.gyroscope}°/s, Light: ${n.photodiode}%`;
          bendingAlerts.appendChild(bendDiv);
        }

        // 3. Predictive Analysis (Machine Learning)
        if (predictiveAnalysis) {
          let predColor = (n.xgb_prediction === "Critical") ? "danger" : ((n.xgb_prediction === "Warning") ? "warning" : "safe");

          let lrColor = "safe";
          if (n.lr_prediction >= 1.5) lrColor = "danger";
          else if (n.lr_prediction >= 0.5) lrColor = "warning";

          let predDiv = document.createElement("div");
          predDiv.className = `predictive-box ${predColor}`;
          predDiv.innerHTML = `
            <div class="predictive-node" style="font-size: 1.1em; border-bottom: 1px solid #ccc; margin-bottom: 5px; padding-bottom: 3px;">
              ${n.node_id}
            </div>
            <div style="margin-bottom: 4px;"><strong>Predictive Analysis:</strong> <span class="${predColor}">${n.xgb_prediction}</span></div>
          `;
          predictiveAnalysis.appendChild(predDiv);
        }
      });

      if (!hasBending && bendingAlerts) {
        bendingAlerts.innerHTML = `<div style="color: #aaa; padding: 10px;">No physical stress or bending detected currently.</div>`;
      }
    })
    .catch(err => console.error("Error fetching data:", err));
}, 200);

// HISTORY MODAL LOGIC
function showHistory(nodeId) {
  let modal = document.getElementById("historyModal");
  let historyTitle = document.getElementById("historyTitle");
  let historyBody = document.getElementById("historyBody");

  historyTitle.innerText = "History: " + nodeId;
  historyBody.innerHTML = "<tr><td colspan='6'>Loading...</td></tr>";
  modal.style.display = "block";

  fetch("http://localhost:5000/history/" + nodeId)
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        historyBody.innerHTML = `<tr><td colspan='6' class='danger'>${data.error}</td></tr>`;
        return;
      }

      historyBody.innerHTML = "";
      if (data.length === 0) {
        historyBody.innerHTML = "<tr><td colspan='6'>No history available.</td></tr>";
        return;
      }

      // Reverse so newest is on top
      const tableData = data.slice().reverse();

      tableData.forEach(row => {
        let statusClass = "safe";
        if (row.status === "DANGER") statusClass = "danger";
        else if (row.status === "WARNING") statusClass = "warning";

        let tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${row.time.split(" ")[1]}</td>
          <td>${row.vibration_1}</td>
          <td>${row.vibration_2}</td>
          <td>${row.gyroscope}°/s</td>
          <td>${row.photodiode}%</td>
          <td class="${statusClass}">${row.status}</td>
        `;
        historyBody.appendChild(tr);
      });

      // Update Chart
      updateChart(data);
    })
    .catch(err => {
      console.error("Error fetching history:", err);
      historyBody.innerHTML = `<tr><td colspan='6' class='danger'>Failed to load history</td></tr>`;
    });
}

let historyChartInstance = null;

function updateChart(data) {
  const ctx = document.getElementById('historyChart').getContext('2d');

  // Extract data for chart (chronological order)
  const labels = data.map(d => d.time.split(" ")[1]);
  const vib1Data = data.map(d => d.vibration_1);
  const vib2Data = data.map(d => d.vibration_2);

  if (historyChartInstance) {
    historyChartInstance.destroy();
  }

  // Determine label colors based on theme
  const textColor = window.currentTheme === 'dark' ? '#eee' : '#333';
  const gridColor = window.currentTheme === 'dark' ? '#444' : '#eee';

  historyChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Vibration 1',
          data: vib1Data,
          borderColor: '#1976D2',
          backgroundColor: 'rgba(25, 118, 210, 0.1)',
          tension: 0.3,
          fill: true
        },
        {
          label: 'Vibration 2',
          data: vib2Data,
          borderColor: '#ff9800',
          backgroundColor: 'rgba(255, 152, 0, 0.1)',
          tension: 0.3,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: textColor }
        }
      },
      scales: {
        x: {
          ticks: { color: textColor, maxTicksLimit: 10 },
          grid: { color: gridColor }
        },
        y: {
          ticks: { color: textColor },
          grid: { color: gridColor },
          beginAtZero: true,
          title: {
            display: true,
            text: 'Vibration Force',
            color: textColor
          }
        }
      }
    }
  });
}

function closeHistoryModal() {
  document.getElementById("historyModal").style.display = "none";
}

// Close modal if clicked outside of it
window.onclick = function (event) {
  let modal = document.getElementById("historyModal");
  if (event.target == modal) {
    modal.style.display = "none";
  }
}