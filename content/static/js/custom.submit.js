/************************************************** SUBMIT CFR ADDITIONAL SCRIPTS **************************************************/

var dummy, dummy2, dummyJSON, txt, x, xmlhttp;


/* Function: submitCFR()
   Purpose: executes when the submit button on the cfr.html is clicked*/
function submitDummy() {
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
  for (i=0; i<12; i++) {
    var cell = row.insertCell(i);
    if (i!=11){
      cell.contentEditable = "true";
      cell.className = "editable";
      cell.innerHTML = "";
    }
    //the last column is the delete checkbox
    else if (i == 11){
      cell.className = "noprint";
      cell.innerHTML = "<input type='checkbox' id='checkCFR'>";
    }
  }
};

/* Function: CFRsubmit()
    Purpose: submits modified CFRs*/
function CFRsubmit() {
  resetTableState();
  var cfrObj = [
  ];
  //gets array of rows from the cfr table
  var aObj=document.getElementById('cfrTable').getElementsByTagName('tr');
  //i = number of rows in the table
  var i=aObj.length;
  //goes through rows from end to beginning
  while(i--) { 
      //deletes rows that are checked
      if(aObj[i].getElementsByTagName('input')[0].checked || aObj[i].getElementsByTagName('td')[1].innerHTML == "") {
        aObj[i].parentNode.removeChild(aObj[i]);
      }
  }
  if (testData()){
  //gets the cfr Table element
  var table = document.getElementById('cfrTable');
  //row = an array of the rows of the table
  var row = table.getElementsByTagName('tr');
  //for each row in the table the elements are added to the cfr object
  for (i = 0; i<row.length; i++){
    var cell = row[i].getElementsByTagName('td');
        cfrObj.push(
          {
            priority:         cell[0].innerText.trim(),
            course:           cell[1].innerText.trim(),
            sec:              cell[2].innerText.trim(),
            mini_session:     cell[3].innerText.trim(),
            online_course:    cell[4].innerText.trim(),
            num_students:     cell[5].innerText.trim(),
            instructor:       cell[6].innerText.trim(),
            banner_id:        cell[7].innerText.trim(),
            inst_rank:        cell[8].innerText.trim(),
            cost:             cell[9].innerText.trim(),
            reason:           cell[10].innerText.trim()
        });
  }
    //prints the cfr object to the console for testing
    console.log(cfrObj);
    //creates a JSON object from the cfr object
    var cfrJSON = JSON.stringify(cfrObj);

    //ADD HTTP REQUEST TO SEND JSON OBJECT
    xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function() {

      if (this.readyState == 4 && this.status == 200) {
        window.alert("Success!!")
      }
    };

    xmlhttp.open("POST", "/add_course", true);
    xmlhttp.setRequestHeader("Content-Type", "text/json; charset=utf-8");
    xmlhttp.send(cfrJSON);
  }
};
/* Function: resetTableState()
    Purpose: resets the table styling if any entries were formerly incorrect*/
  function resetTableState(){
    //gets the cfr Table element
    var table = document.getElementById('cfrTable');
    //row = an array of the rows of the table
    var row = table.getElementsByTagName('tr');
    //gets the cfr table footer element
    var foot = document.getElementById('cfrFooter');
    //resets table footer to not be displayed
    foot.style.visibility = "collapse";
    //frow = an array of the rows of the footer of the table
    var frow = foot.getElementsByTagName('tr');
    //fcell = an array of the cells in the first row of the footer
    var fcell = frow[0].getElementsByTagName('td');

    //for each row in the table the cells are set back to normal styling and the error messages are hidden
    for (i = 0; i<row.length; i++){
      var cell = row[i].getElementsByTagName('td');
      for (j = 0; j<cell.length; j++){
        if (cell[j].className == "danger"){
          cell[j].classList.remove("danger");
        }
        if (fcell[j].style.visibility == "visible"){
          fcell[j].style.visibility = "hidden";
        }
      }
    }
  };

/* Function: testData() 
    Purpose: tests the data entries does not send the request if entries are not correct*/
  function testData(){
    //checks if there are any errors
    var test = 1;
    //gets the cfr table element
    var table = document.getElementById('cfrTable');
    //gets the cfr table footer element
    var foot = document.getElementById('cfrFooter');
    //row = an array of the rows of the table
    var row = table.getElementsByTagName('tr');
    //frow = an arrow of the rows of the footer of the table
    var frow = foot.getElementsByTagName('tr');
        //fcell = an array of the cells in the first row of the footer
    var fcell = frow[0].getElementsByTagName('td');

    //for each row in the table the elements are added to the cfr object
    for (i = 0; i<row.length; i++){
      var cell = row[i].getElementsByTagName('td');

      //makes sure the first column entries are numbers
      if (Number.isNaN(Number(cell[0].innerText.trim()))){
        //if the data is not a number the cell will turn red and an error message will display at the bottom of the column
        cell[0].className = "danger";
        fcell[0].style.visibility = "visible";
        test = test - 1;
      }

      //makes sure the mini session column has proper inputs
      //capitalizes the first letter in no
      if (cell[3].innerText.trim()=="no" || cell[3].innerText.trim()=="No" || cell[3].innerText.trim()=="NO"){
        cell[3].innerText = "No";
      }
      //capitalizes the first letter in yes
      else if (cell[3].innerText.trim()=="yes" || cell[3].innerText.trim()=="Yes" || cell[3].innerText.trim()=="YES"){
        cell[3].innerText = "Yes";
      }
      //if the data is not yes or no the cell will turn red and an error message will display at the bottom of the column
      else {
        cell[3].className = "danger";
        fcell[3].style.visibility = "visible";
        test = test - 1;
      }

      //makes sure the online class column has proper inputs
      //capitalizes the first letter in no
      if (cell[4].innerText.trim()=="no" || cell[4].innerText.trim()=="No" || cell[4].innerText.trim()=="NO"){
        cell[4].innerText = "No";
      }
      //capitalizes the first letter in yes
      else if (cell[4].innerText.trim()=="yes" || cell[4].innerText.trim()=="Yes" || cell[4].innerText.trim()=="YES"){
        cell[4].innerText = "Yes";
      }
      //if the data is not yes or no the cell will turn red and an error message will display at the bottom of the column
      else {
        cell[4].className = "danger";
        fcell[4].style.visibility = "visible";
        test = test - 1;
      }

      //makes sure the number of students column has proper inputs
      //checks to make sure >0
      if (cell[5].innerText.trim()>0){
        //empty
      }
      //if the data is not yes or no the cell will turn red and an error message will display at the bottom of the column
      else {
        cell[5].className = "danger";
        fcell[5].style.visibility = "visible";
        test = test - 1;
      }

      //makes sure the instructor column has proper inputs
      //capitalizes TBD
      if (cell[6].innerText.trim()=="tbd" || cell[6].innerText.trim()=="Tbd" || cell[6].innerText.trim()=="tBd" 
        || cell[6].innerText.trim()=="tbD" || cell[6].innerText.trim()=="TBd" || cell[6].innerText.trim()=="TbD" 
        || cell[6].innerText.trim()=="tBD" || cell[6].innerText.trim()=="TBD"){
        cell[6].innerText = "TBD";
      }
      //if empty set to TBH
      else if (cell[6].innerText.trim()==""){
        cell[6].innerText = "TBD";
      }

      //makes sure the instructor banner id column has proper inputs
      //set column to N/A if empty 
      if (cell[6].innerText.trim()=="N/A" || cell[6].innerText.trim()=="NA" || cell[6].innerText.trim()=="N/a" 
        || cell[6].innerText.trim()=="Na" || cell[6].innerText.trim()=="n/a" || cell[6].innerText.trim()=="na" 
        || cell[6].innerText.trim()==""){
        cell[7].innerText = "N/A";
      }
      // if the instructor is TBD set the column to N/A
      else if (cell[6].innerText.trim()=="tbd" || cell[6].innerText.trim()=="Tbd" || cell[6].innerText.trim()=="tBd" 
        || cell[6].innerText.trim()=="tbD" || cell[6].innerText.trim()=="TBd" || cell[6].innerText.trim()=="TbD" 
        || cell[6].innerText.trim()=="tBD" || cell[6].innerText.trim()=="TBD"){
        cell[7].innerText = "N/A";
      }
      //if invalid id the cell will turn red and an error message will display at the bottom of the column
      else if (cell[7].innerText.trim()<800000000){
        cell[7].className = "danger";
        fcell[7].style.visibility = "visible";
        test = test - 1;
      }

      //makes sure the instructor rank column has proper inputs
      //set column to N/A if empty 
      if (cell[8].innerText.trim()=="N/A" || cell[8].innerText.trim()=="NA" || cell[8].innerText.trim()=="N/a" 
        || cell[8].innerText.trim()=="Na" || cell[8].innerText.trim()=="n/a" || cell[8].innerText.trim()=="na" 
        || cell[8].innerText.trim()==""){
        cell[8].innerText = "N/A";
      }
      // if the instructor is TBD set the column to N/A
      else if (cell[6].innerText.trim()=="tbd" || cell[6].innerText.trim()=="Tbd" || cell[6].innerText.trim()=="tBd" 
        || cell[6].innerText.trim()=="tbD" || cell[6].innerText.trim()=="TBd" || cell[6].innerText.trim()=="TbD" 
        || cell[6].innerText.trim()=="tBD" || cell[6].innerText.trim()=="TBD"){
        cell[8].innerText = "N/A";
      }

    }

    //if anything is wrong the cfr will not be sent
    if (test <= 0){
      foot.style.visibility = "hidden";
      return false;
    }
    return true;
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
  };