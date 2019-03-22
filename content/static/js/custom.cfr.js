/************************************************** NMSU CFR ADDITIONAL SCRIPTS **************************************************/
var testing = "true";
var simData = "true";

function hideNavbar() {
  var navbar = document.getElementById("main-navigation");
  navbar.style.display = "none";
};

function showNavbar() {
  var navbar = document.getElementById("main-navigation");
  navbar.style.display = "block";
};

function checkNavbar() {
  var url = location.href;

  if (url === "http://localhost/") {
    hideNavbar();
  } else {
    showNavbar();
  }
};

/*
window.onscroll = function() {scrollFunction()};

function scrollFunction() {
  if (document.body.scrollTop > 40|| document.documentElement.scrollTop > 40) {
    document.getElementById("logo").style.width = "213px";
    document.getElementById("headertitle").style.fontsize = "20px";
  } else {
    document.getElementById("logo").style.width = "427px";
    document.getElementById("headertitle").style.fontsize = "initial";
  }
}
*/

