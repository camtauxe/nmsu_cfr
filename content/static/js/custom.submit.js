/************************************************** SUBMIT CFR ADDITIONAL SCRIPTS **************************************************/

var dummy, dummy2, dummyJSON, txt, x, xmlhttp;

function submitCFR() {
  dummy = [
    {
      name1: document.getElementById("cfrName").value, 
      num1: document.getElementById("cfrNum1").value,
      num2: document.getElementById("cfrNum2").value, 
      num3: document.getElementById("cfrNum3").value
    }
  ];
  
  dummyJSON = JSON.stringify(dummy);
  
  xmlhttp = new XMLHttpRequest();

  insertSuccessMessage();
  insertIntoTable();

    xmlhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      
    }
  };

  xmlhttp.open("POST", "/add_dummy", true);
  xmlhttp.setRequestHeader("Content-Type", "text/json; charset=utf-8");
  xmlhttp.send(dummyJSON);
};

function insertIntoTable() {
  dummy2 = JSON.parse(dummyJSON);
  for (i in dummy2) {
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
    cell1.innerHTML = dummy2[i].name1;
    cell2.innerHTML = dummy2[i].num1;
    cell3.innerHTML = dummy2[i].num2;
    cell4.innerHTML = dummy2[i].num3;
    }
};

function insertSuccessMessage() {
  dummy2 = JSON.parse(dummyJSON);
  for (i in dummy2) {
    txt = "<i>added " + dummy2[i].name1 + " " + dummy2[i].num1 + " " + dummy2[i].num2 + " " + dummy2[i].num3 + " to CFR</i>";
    console.log(txt);
  }
}
