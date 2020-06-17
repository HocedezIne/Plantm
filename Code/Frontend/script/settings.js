'use strict';

const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

//#region ***  DOM references ***
//#endregion

//#region ***  Callback-Visualisation - show___ ***
const showMinMax = function(jsonObject){
    console.log(jsonObject)
    for (const row of jsonObject.data){
        document.querySelector(`.js-${row.id}-min`).value = row.minimumvalue;
        document.querySelector(`.js-${row.id}-max`).value = row.maximumvalue;
    }
}
//#endregion

//#region ***  Callback-No Visualisation - callback___  ***
//#endregion

//#region ***  Data Access - get___ ***
const getMinMax = function(){
    socket.emit("F2B_get_all_min_max");
}
//#endregion

//#region ***  Event Listeners - listenTo___ ***
const listenToSocket = function () {
  socket.on('connected', function () {
    console.log('verbonden met socket webserver');
  });

  socket.on("B2F_all_min_max", function(jsonObject){
    showMinMax(jsonObject);
  });
};

const listenToUI = function(){
    const btn = document.querySelector(".js-confirm");

    btn.addEventListener("click", function(){
        const jsonObject = {
            ldrMin: document.querySelector(`.js-LDR-min`).value,
            ldrMax: document.querySelector(`.js-LDR-max`).value,
            smoistMin: document.querySelector(`.js-BV-min`).value,
            smoistMax: document.querySelector(`.js-BV-max`).value,
            tempMin: document.querySelector(`.js-TEMP-min`).value,
            tempMax: document.querySelector(`.js-TEMP-max`).value,
            lvlMin: document.querySelector(`.js-LEVEL-min`).value,
            lvlMax: document.querySelector(`.js-LEVEL-max`).value
        };
        socket.emit("F2B_update_min_max", {data: jsonObject});
        getMinMax();
    });

    const shutdown_btn = document.querySelector(".js-shutdown");
    shutdown_btn.addEventListener("click", function(){
      socket.emit("F2B_shutdown")
    })
};
//#endregion

//#region ***  INIT / DOMContentLoaded  ***
const init = function () {
  console.log('settings init geladen');
  listenToSocket();
  listenToUI();
  getMinMax();
};

document.addEventListener('DOMContentLoaded', init);
//#endregion
