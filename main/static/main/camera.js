var video = document.querySelector("#videoElement");

var play = document.getElementById("play");
var pause = document.getElementById("pause");
var stop = document.getElementById("stop");

if (navigator.mediaDevices.getUserMedia) {
	
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(function (stream) {
		
      video.srcObject = stream;
      
    })
    
    .catch(function (err0r) {
      console.log("Something went wrong!");
    });
   
}
