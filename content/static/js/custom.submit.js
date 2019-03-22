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
  insertNewRow();

    if (testing == true){
      dummyArray2 = JSON.parse(dummyArrayJSON);
      for (i in dummyArray2) {
        dummy2 = JSON.parse(dummyArray2[i]);
        txt = "<i>added " + dummy.name1 + " " + dummy.num1 + " " + dummy.num2 + " " + dummy.num3 + " to CFR</i>";
        x = document.createElement("P");
        x.innerHTML = txt;
        document.getElementById("cfrOutput").appendChild(x);
      }
    }
    if (simData == true){
      dummyArray2 = JSON.parse(dummyArrayJSON);
      for (i in dummyArray2) {
        dummy2 = JSON.parse(dummyArray2[i]);
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
    
    xmlhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      
    }
  };

  xmlhttp.open("POST", "/add_dummy", true);
  xmlhttp.setRequestHeader("Content-Type", "text/json; charset=utf-8");
  xmlhttp.send(dummyJSON);
};

/* Function: insertNewRow() */
/* Purpose: Insert a new table row with data input by a submitter role */
function insertNewRow() {
  
  // Copy of dummy data
  dummy2 = JSON.parse(dummyJSON);
  
  // Select the table
  var table = document.getElementById("cfrTable");
  
  // Insert row and corresponding cells
  var row = table.insertRow(-1);
  var cell1 = row.insertCell(0);
  var cell2 = row.insertCell(1);
  var cell3 = row.insertCell(2);
  var cell4 = row.insertCell(3);
  
  // Make each of the cells editable
  cell1.contentEditable = "true";
  cell2.contentEditable = "true";
  cell3.contentEditable = "true";
  cell4.contentEditable = "true";
  
  // Input the data from the user
  cell1.innerHTML = dummy2[0].name1;
  cell2.innerHTML = dummy2[0].num1;
  cell3.innerHTML = dummy2[0].num2;
  cell4.innerHTML = dummy2[0].num3;
};

function insertSuccessMessage() {
  dummy2 = JSON.parse(dummyJSON);
  txt = "<i>added " + dummy[0].name1 + " " + dummy[0].num1 + " " + dummy[0].num2 + " " + dummy[0].num3 + " to CFR</i>";
  x = document.createElement("P");
  x.innerHTML = txt;
  document.getElementById("cfrOutput").appendChild(x);
}