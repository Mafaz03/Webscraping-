function updatemenu() {
  if (document.getElementById("responsive-menu").checked == true) {
    document.getElementById("menu").style.borderBottomRightRadius = "0";
    document.getElementById("menu").style.borderBottomLeftRadius = "0";
  } else {
    document.getElementById("menu").style.borderRadius = "10px";
  }
}

window.onscroll = function () {
  myFunction();
};

var menu = document.getElementById("menu");
var sticky = menu.offsetTop;

function myFunction() {
  if (window.pageYOffset > sticky) {
    menu.classList.add("sticky");
  } else {
    menu.classList.remove("sticky");
  }
}
// function updatemenu() {
//   var menu = document.getElementById('menu');
//   var responsiveMenu = document.getElementById('responsive-menu');

//   if (responsiveMenu.checked) {
//     menu.style.borderBottomRightRadius = '0';
//     menu.style.borderBottomLeftRadius = '0';
//   } else {
//     menu.style.borderRadius = '10px';
//   }
// }

// document.addEventListener("DOMContentLoaded", function () {
//   const model = document.querySelector(".openmodale");
//   const ml = document.querySelector(".modale");
//   const clmodel = document.querySelector(".closemodale");
//   const modelImage = document.querySelector("#dashboardImage");

//   var imgPath = "/display_image";

//   model.addEventListener("click", function (e) {
//     console.log("Dashboard link clicked");
//     e.preventDefault();

//     if (modelImage) {
//       modelImage.src = imgPath;
//       console.log("Image path set:", imgPath);
//     }
//     console.log("Modal classList after opening:", ml.classList);
//     ml.classList.remove("hidden");
//   });

//   clmodel.addEventListener("click", function (e) {
//     console.log("Close button clicked");
//     e.preventDefault();
//     ml.classList.add("hidden");
//     if (modelImage) {
//       modelImage.src = "";
//     }
//   });
// });

document.addEventListener("DOMContentLoaded", function () {
  // Get the reference to the image element
  const dashboardImage = document.getElementById("dashboardImage");

  // Set the image source when the page loads
  dashboardImage.src = "/display_image";
});
