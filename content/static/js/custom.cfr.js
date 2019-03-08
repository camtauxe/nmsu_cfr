/************************************************** NMSU CFR ADDITIONAL SCRIPTS **************************************************/
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