'use strict';

const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
const today = new Date();
const startDay = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,"0")}-${String(today.getDate()-7).padStart(2,"0")}`;
let endDay = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,"0")}-${String(today.getDate()).padStart(2,"0")}`;
let dates = {start:  `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,"0")}-${String(today.getDate()-7).padStart(2,"0")} 00:00:00`, end: `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,"0")}-${String(today.getDate()).padStart(2,"0")} 23:59:59`}

//#region ***  DOM references ***
//#endregion

//#region ***  Callback-Visualisation - show___ ***
const showCurrentDates = function(){
    document.querySelector(".js-start-date").value = `${startDay}`;
    document.querySelector(".js-end-date").value = `${endDay}`;
};

const showMinMax = function(jsonObject){
    document.querySelector('.js-min').innerHTML = jsonObject.data.minimumvalue
    document.querySelector('.js-max').innerHTML = jsonObject.data.maximumvalue
}

const showGraphs = function(jsonObject){
  console.log(jsonObject)
  let converted_labels = [];
  let converted_data = [];
  for (const measurement of jsonObject.data){
    if (measurement.DeviceID == "LEVEL"){
      converted_labels.push(measurement.DateTime);
      converted_data.push(measurement.Value);
    };
    drawChart(converted_labels, converted_data);
  };
};

const drawChart = function(labels, data){
  let ctx = document.querySelector(".js-lvl-chart").getContext("2d");

  let config = {
      type: "line",
      data: {
          labels: labels,
          datasets: [{
              label: "Water level values",
              backgroundColor: "#4FC19D",
              borderColor: "#4FC19D",
              data: data,
              fill: false
          }]
      },
      options: {
          responsive: true,
          title: {
              display: true,
              text: "Water level"
          },
          tooltips: {
              mode: "index",
              intersect: true
          },
          hover: {
              mode: "nearest",
              intersect: true
          },
          scales: {
              xAxes: [{
                  display: true,
                  scaleLabel: {
                      display: true,
                      labelStrings: "Date"
                  }
              }],
              yAxes: [{
                  display: true,
                  scaleLabel: {
                      display: true,
                      labelStrings: "Value"
                  }
              }]
          }
      }
  }

  let myChart = new Chart(ctx, config);
};
//#endregion

//#region ***  Callback-No Visualisation - callback___  ***
//#endregion

//#region ***  Data Access - get___ ***

//#endregion

//#region ***  Event Listeners - listenTo___ ***
const listenToSocket = function () {
  socket.on("connected", function () {
    console.log("verbonden met socket webserver");
  });

  socket.on("B2F_requested_data", function(jsonObject){
    showGraphs(jsonObject);
  });

  socket.on("B2F_min_max", function(jsonObject){
    showMinMax(jsonObject);
  });
};

const listenToUI = function(){
    const startInput = document.querySelector(".js-start-date");
    const endInput = document.querySelector(".js-end-date");

    startInput.addEventListener("change", function(){
        dates["start"] = startInput.value + " 00:00:00";
        console.log(dates)
        socket.emit("F2B_send_data", {data: dates})
    })

    endInput.addEventListener("change", function(){
        dates["end"] = endInput.value + " 00:00:00";
        console.log(dates)
        socket.emit("F2B_send_data", {data: dates})
    })
};
//#endregion

//#region ***  INIT / DOMContentLoaded  ***
const init = function () {
  console.log('light init geladen');
  listenToSocket();
  listenToUI();
  showCurrentDates();
  socket.emit("F2B_send_min_max", {deviceid: "LEVEL"})
  socket.emit("F2B_send_data", {data: dates})
};

document.addEventListener('DOMContentLoaded', init);
//#endregion