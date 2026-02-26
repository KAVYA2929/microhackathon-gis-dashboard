// MAP
var map = L.map('map', { zoomControl: false }).setView([13.0, 80.25], 12);

L.tileLayer(
  'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
).addTo(map);

// STORAGE
var cables = {};

// FETCH MULTI-NODE DATA
setInterval(() => {
  fetch("http://localhost:5000/data")
    .then(res => res.json())
    .then(nodes => {

      let readingsBody = document.getElementById("readingsBody");
      let bendingAlerts = document.getElementById("bendingAlerts");
      let predictiveAnalysis = document.getElementById("predictiveAnalysis");

      if (readingsBody) readingsBody.innerHTML = "";
      if (bendingAlerts) bendingAlerts.innerHTML = "";
      if (predictiveAnalysis) predictiveAnalysis.innerHTML = "";

      let hasBending = false;

      nodes.forEach(n => {

        // CREATE CABLE IF NOT EXISTS
        if (!cables[n.node_id]) {
          cables[n.node_id] = L.polyline(n.path, { color: 'cyan', weight: 6 }).addTo(map);
        }

        // STATUS COLOR
        let statusClass = "safe";
        let lineColor = "cyan";

        if (n.status === "DANGER") {
          statusClass = "danger";
          lineColor = "red";
          if (cables[n.node_id].getElement()) cables[n.node_id].getElement().classList.add("blink");
        } else if (n.status === "WARNING") {
          statusClass = "warning";
          lineColor = "orange";
          if (cables[n.node_id].getElement()) cables[n.node_id].getElement().classList.remove("blink");
        } else {
          lineColor = "cyan";
          if (cables[n.node_id].getElement()) cables[n.node_id].getElement().classList.remove("blink");
        }

        cables[n.node_id].setStyle({ color: lineColor });

        cables[n.node_id].bindPopup(
          `<b>${n.node_id}</b><br>Status: ${n.status}<br>Vib: ${n.vibration}<br>Gyro: ${n.gyroscope}<br>Photo: ${n.photodiode}`
        );

        // 1. Live Readings
        if (readingsBody) {
          let tr = document.createElement("tr");
          tr.innerHTML = `
            <td>${n.node_id}</td>
            <td>${n.vibration}</td>
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

        // 3. Predictive Analysis
        if (predictiveAnalysis) {
          let predColor = n.is_bending ? "danger" : (n.status === "WARNING" ? "warning" : "safe");
          let predDiv = document.createElement("div");
          predDiv.className = `predictive-box ${predColor}`;
          predDiv.innerHTML = `
            <div class="predictive-node">${n.node_id}</div>
            <div>${n.predictive_status}</div>
          `;
          predictiveAnalysis.appendChild(predDiv);
        }
      });

      if (!hasBending && bendingAlerts) {
        bendingAlerts.innerHTML = `<div style="color: #aaa; padding: 10px;">No physical stress or bending detected currently.</div>`;
      }
    })
    .catch(err => console.error("Error fetching data:", err));
}, 2000);