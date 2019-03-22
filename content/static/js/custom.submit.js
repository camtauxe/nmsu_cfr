/************************************************** SUBMIT CFR ADDITIONAL SCRIPTS **************************************************/

var testing = "true";
var simData = "true";
var dummy, dummy2, dummyJSON, txt, x, xmlhttp;

function submitCFR() {
  dummy = {name1: document.getElementById("cfrName").value, num1: document.getElementById("cfrNum1").value,
  num2: document.getElementById("cfrNum2").value, num3: document.getElementById("cfrNum3").value};
  dummyJSON = JSON.stringify(dummy);
  xmlhttp = new XMLHttpRequest();

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

  xmlhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
    }
  };

  xmlhttp.open("POST", "/add_dummy", true);
  xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xmlhttp.send("x=" + dummyJSON);
}