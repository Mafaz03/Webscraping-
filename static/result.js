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
