/**
 * Common functions and definitions needed on most pages of the site
 */

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

    // @TODO: Fix this!!!!
    if (url === "http://localhost/")
        hideNavbar();
    else 
        showNavbar();
};