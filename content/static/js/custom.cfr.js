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

var dummy, dummy2, dummyJSON, txt, x;
//var xmlhttp = new XMLHttpRequest();

function submitCFR() {
  dummy = { name1: document.getElementById("cfrName").value, num1: document.getElementById("cfrNum1").value,
  num2: document.getElementById("cfrNum2").value, num3: document.getElementById("cfrNum3").value};
  dummyJSON = JSON.stringify(dummy);


    if (testing == "true"){
      dummy2 = JSON.parse(dummyJSON);
      txt = "<i>added " + dummy.name1 + " " + dummy.num1 + " " + dummy.num2 + " " + dummy.num3 + " to CFR</i>";
      x = document.createElement("P");
      x.innerHTML = txt;
      document.getElementById("cfrOutput").appendChild(x);

    }
    if (simData == "true"){
      dummy2 = JSON.parse(dummyJSON);
      var table = document.getElementById("cfrTable");
      var row = table.insertRow(-1);
      var cell1 = row.insertCell(0);
      var cell2 = row.insertCell(1);
      var cell3 = row.insertCell(2);
      var cell4 = row.insertCell(3);
      cell1.contentEditable = "true";
      cell2.contentEditable = "true";
      cell3.contentEditable = "true";
      cell4.contentEditable = "true";
      cell1.innerHTML = dummy2.name1;
      cell2.innerHTML = dummy2.num1;
      cell3.innerHTML = dummy2.num2;
      cell4.innerHTML = dummy2.num3;
    }
}

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

