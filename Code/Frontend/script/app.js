'use strict';

const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
const today = new Date();

//#region ***  DOM references ***
//#endregion

//#region ***  Callback-Visualisation - show___ ***
const showGraphs = function (jsonObject) {
  console.log(jsonObject);
  let converted_labels = [
    `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(
      2,
      '0'
    )}-${String(today.getDate() - 5).padStart(2, '0')}`,
    `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(
      2,
      '0'
    )}-${String(today.getDate() - 4).padStart(2, '0')}`,
    `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(
      2,
      '0'
    )}-${String(today.getDate() - 3).padStart(2, '0')}`,
    `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(
      2,
      '0'
    )}-${String(today.getDate() - 2).padStart(2, '0')}`,
    `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(
      2,
      '0'
    )}-${String(today.getDate() - 1).padStart(2, '0')}`,
    `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(
      2,
      '0'
    )}-${String(today.getDate()).padStart(2, '0')}`,
  ];
  let converted_data = { ldr: [], smoist: [], temp: [], lvl: [] };
  for (const measurement of jsonObject.data) {
    if (measurement.DeviceID == 'LDR') {
      converted_data['ldr'].push(measurement.Value);
    } else if (measurement.DeviceID == 'BV') {
      converted_data['smoist'].push(measurement.Value);
    } else if (measurement.DeviceID == 'TEMP') {
      converted_data['temp'].push(measurement.Value);
    } else if (measurement.DeviceID == 'LEVEL') {
      converted_data['lvl'].push(measurement.Value);
    }
  }
  console.log(converted_data);
  drawChart(converted_labels, converted_data);
};

const drawChart = function (labels, data) {
  let ctx = document.querySelector('.js-main-chart').getContext('2d');

  let config = {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Light',
          backgroundColor: '#77D9BA',
          borderColor: '#77D9BA',
          data: data['ldr'],
          fill: false,
          yAxisID: 'y-axis-1',
        },
        {
          label: 'Soil Moisture',
          backgroundColor: '#0B4D38',
          borderColor: '#0B4D38',
          data: data['smoist'],
          fill: false,
          yAxisID: 'y-axis-1',
        },
        {
          label: 'Temperature',
          backgroundColor: '#208061',
          borderColor: '#208061',
          data: data['temp'],
          fill: false,
          yAxisID: 'y-axis-2',
        },
        {
          label: "Water level",
          backgroundColor: "#454D4A",
          borderColor: "#454D4A",
          data: data["lvl"],
          fill: false,
          yAxisID: 'y-axis-2',
      }],
    },
    options: {
      responsive: true,
      hoverMode: 'index',
      stacked: false,
      title: {
        display: true,
        text: 'Last 5 days',
      },
      scales: {
        xAxes: [
          {
            display: true,
            scaleLabel: {
              display: true,
              labelStrings: 'Date',
            },
          },
        ],
        yAxes: [{
          display: true,
          scaleLabel:{
            display: true,
            labelStrings: "Procentage"
          },
          position: "left",
          id: "y-axis-1"
        }, {
          display: true,
          scaleLabel:{
            display: true,
            labelStrings: "Value"
          },
          position: "right",
          id: "y-axis-2"
        }],
      },
    },
  };

  let myChart = new Chart(ctx, config);
};

const showPlantname = function(jsonObject){
  document.querySelector(".js-plantname").value = jsonObject.name.Name;
};
//#endregion

//#region ***  Callback-No Visualisation - callback___  ***
//#endregion

//#region ***  Data Access - get___ ***
const getPlantName = function(){
  socket.emit("F2B_get_plantname");
};
//#endregion

//#region ***  Event Listeners - listenTo___ ***
const listenToSocket = function () {
  socket.on('connected', function () {
    console.log('verbonden met socket webserver');
  });

  socket.on('B2F_data_measurements', function (jsonObject) {
    showGraphs(jsonObject);
  });

  socket.on('B2F_current_values', function (jsonObject) {
    console.log('Dit zijn de current values');
    console.log(jsonObject);
    document.querySelector('.js-ldr-value').innerHTML = jsonObject.LDR;
    document.querySelector('.js-lvl-value').innerHTML = jsonObject.lvl;
    document.querySelector('.js-smoist-value').innerHTML = jsonObject.smoist;
    document.querySelector('.js-temp-value').innerHTML = jsonObject.temp;
  });

  socket.on("B2F_plantname", function(jsonObject){
    showPlantname(jsonObject);
  })
};

const listenToUI = function(){
  const field = document.querySelector(".js-plantname");

  field.addEventListener("change", function(){
    socket.emit("F2B_update_plantname", {name: field.value})
  });
};
//#endregion

//#region ***  INIT / DOMContentLoaded  ***
const init = function () {
  console.log('main init geladen');
  listenToSocket();
  getPlantName();
  listenToUI();
};

document.addEventListener('DOMContentLoaded', init);
//#endregion
