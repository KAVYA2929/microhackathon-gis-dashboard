// MAP
var map = L.map('map').setView([13.0827, 80.2707], 15);

L.tileLayer(
  'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
).addTo(map);

// FIBER ROUTE
var fiberRoute = [
  [13.0827, 80.2707],
  [13.0835, 80.2715],
  [13.0842, 80.2728],
  [13.0850, 80.2740]
];

L.polyline(fiberRoute, {
  color:'cyan',
  weight:5
}).addTo(map);

// STORAGE
var markers = {};
var heatData = [];
var heatLayer = L.heatLayer(heatData, { radius:25, blur:15 }).addTo(map);

// FETCH MULTI-NODE DATA
setInterval(() => {
  fetch("http://localhost:5000/data")
    .then(res => res.json())
    .then(nodes => {

      nodes.forEach(n => {

        // CREATE MARKER IF NOT EXISTS
        if (!markers[n.node_id]) {
          markers[n.node_id] = L.circleMarker(
            [n.lat, n.lng],
            { radius:10, color:'green', fillColor:'green', fillOpacity:1 }
          ).addTo(map);
        }

        // STATUS COLOR
        if (n.status === "DANGER") {
          markers[n.node_id].setStyle({ color:'red', fillColor:'red' });
          markers[n.node_id].getElement().classList.add("blink");

          heatData.push([n.lat, n.lng, 1]);
          heatLayer.setLatLngs(heatData);

          let table = document.getElementById("alertTable");
          let row = table.insertRow(1);
          row.insertCell(0).innerText = n.time;
          row.insertCell(1).innerText = n.node_id;
          row.insertCell(2).innerText = n.status;
          row.insertCell(3).innerText = n.vibration;
          row.insertCell(4).innerText = n.accel;

        } else {
          markers[n.node_id].setStyle({ color:'green', fillColor:'green' });
          markers[n.node_id].getElement().classList.remove("blink");
        }

        markers[n.node_id].bindPopup(
          `Node: ${n.node_id}<br>Status: ${n.status}<br>Vib: ${n.vibration}<br>Accel: ${n.accel}`
        );
      });
    });
}, 2000);