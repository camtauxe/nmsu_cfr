/************************************************** SUBMIT CFR ADDITIONAL SCRIPTS **************************************************/

var dummy, dummy2, dummyJSON, txt, x, xmlhttp;

/* Function: submitCFR()
   Purpose: executes when the submit button on the cfr.html is clicked*/
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

  logSuccessMessage();
  insertIntoTable();

  xmlhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      
    }
  };

  xmlhttp.open("POST", "/add_dummy", true);
  xmlhttp.setRequestHeader("Content-Type", "text/json; charset=utf-8");
  xmlhttp.send(dummyJSON);
};

/* Function: addRow()
    Purpose: Adds row to CFR table when the add row button is clicked*/
function addRow() {
  //selects the cfr table eleemnt from cfr.html
  var table = document.getElementById("cfrTable");

  //creates a new row and adds it to the end of the table
  var row = table.insertRow(-1);
  
  //creates proper number of cells for each row
  var i;
  for (i=0; i<13; i++) {
    var cell = row.insertCell(i);
    if (i != 0 && i!=12){
      cell.contentEditable = "true";
    }
    cell.innerHTML = "";
    //the last column is the delete checkbox
    if (i == 12){
      cell.innerHTML = "<input type='checkbox' id='checkCFR'>";
    }
  }
};


function deleteRows() {
var aObj=document.getElementById('cfrTable').getElementsByTagName('tr');
var i=aObj.length; 
while(i--) { 
    if(aObj[i].getElementsByTagName('input')[0].checked) {
        aObj[i].parentNode.removeChild(aObj[i]);
        }
}
};





/* Function: insertIntoTable()
   Purpose: Inserts data from JSON object into the end of the table */
function insertIntoTable() {
  //creates a regular javascript object from the JSON object
  dummy2 = JSON.parse(dummyJSON);

  //interates through each entry in the array
  for (i in dummy2) {

    //selects the cfr table element from cfr.html
    var table = document.getElementById("cfrTable2");

    //creates a new row and adds it to the end of the table
    var row = table.insertRow(-1);

    //creates new cells and inserts them into the row
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    var cell3 = row.insertCell(2);
    var cell4 = row.insertCell(3);

    //makes cell contents editable
    cell1.contentEditable = "true";
    cell2.contentEditable = "true";
    cell3.contentEditable = "true";
    cell4.contentEditable = "true";

    //populates calls with data orginally in JSON object
    cell1.innerHTML = dummy2[i].name1;
    cell2.innerHTML = dummy2[i].num1;
    cell3.innerHTML = dummy2[i].num2;
    cell4.innerHTML = dummy2[i].num3;
    }
};

/* Function: logSuccessMessage()
   Purpose: logs new table additions to the console*/
function logSuccessMessage() {
  dummy2 = JSON.parse(dummyJSON);
  for (i in dummy2) {
    txt = "added " + dummy2[i].name1 + " " + dummy2[i].num1 + " " + dummy2[i].num2 + " " + dummy2[i].num3 + " to CFR";
    console.log(txt);
  }
}
