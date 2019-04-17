/*********************************************** NMSU Sources of Salary Savings **************************************************/

/* Funtion: addSalaryRow()
    Purpose: add a new row to the salary savings table*/
function addSalaryRow(){
    //gets table from salary_saving.html
    var table = document.getElementById("salaryTable");

    //creates a new row and adds it to the end of the table
    var row = table.insertRow(-1);

    //creates proper number of cells for each row
    var i;
    for (i=0; i<5; i++) {
        var cell = row.insertCell(i);
        if (i!=0 && i!=4){
          cell.contentEditable = "true";
          cell.className = "editable";
          cell.innerHTML = "";
        }
        else if (i == 0){
            cell.innerHTML = "<div class='form-group' style='margin: 0px 0px'> <select class='form-control' id='standardSelect' name='standardSelect'> <option value='Sabbatical'>Approved Amounts from Sabbatical Leaves</option> <option value='RBO'>Research Buy Out (Provide Index Number)</option> <option value='Other'>Other Funded Leave</option> <option value='LWOP'>Leave Without Pay</option> </select> </div>"
        }
        //the last column is the delete checkbox
        else if (i == 4){
          cell.className = "noprint";
          cell.innerHTML = "<input type='checkbox' id='checkCFR'>";
        }
    }
};

function salarySubmit(){
    resetSalaryTableState();
    //creates a javascript array object for the salary submissions
    var salaryObj = [
    ];
    
    //saves the rows of the salary savings table from salary_saving.html into aObj
    var aObj=document.getElementById('salaryTable').getElementsByTagName('tr');
    var i = aObj.length;
    //iterates through each row in the table
    while(i--) {
        //checks if the row is empty or checked
        if(aObj[i].getElementsByTagName('input')[0].checked) {
            //deletes row
            aObj[i].parentNode.removeChild(aObj[i]);
        }
    }
    if (testDataSalary()) {
        //gets the salary savings table
        var table = document.getElementById('salaryTable');
        //row is an array where each element corresponds to a row in the table
        var row = table.getElementsByTagName('tr');
        //iterates through each row
        for (i=0; i<row.length; i++){
            //cell is an array of cells in the row
            var cell = row[i].getElementsByTagName('td');
            //adds the data from the cells into the javascript array
            salaryObj.push(
                {
                leave_type:         row[i].getElementsByTagName('select')[0].value,
                inst_name:          cell[1].innerText.trim(),
                savings:            cell[2].innerText.trim(),
                notes:              cell[3].innerText.trim(),
                confirmedAmount:    "",
            });
        }
        //prints the cfr object to the console for testing
        console.log(salaryObj);
        //creates a JSON object from the salary object
        var salaryJSON = JSON.stringify(salaryObj);

        //ADD HTTP REQUEST TO SEND JSON OBJECT
        xmlhttp = new XMLHttpRequest();

        xmlhttp.onreadystatechange = function() {
          if (this.readyState == 4) {
            document.getElementById("submitSalaryButton").disabled = false;
            if (this.status == 200) {
              window.alert("Successfully submitted course funding requests!")
            }
            else if (this.status == 400) {
              window.alert("Something was wrong with the submitted courses!\n"+this.response)
            }
            else {
              window.alert("Something went wrong! The courses were not submitted.\n Server returned: "+this.status)
            }
          }
        };
        
        document.getElementById("submitSalaryButton").disabled = true;
        xmlhttp.open("POST", "/add_sal_savings", true);
        xmlhttp.setRequestHeader("Content-Type", "text/json; charset=utf-8");
        xmlhttp.send(salaryJSON);
    }
};

/* Function: testDataSalary() 
    Purpose: tests the data entries does not send the request if entries are not correct*/
  function testDataSalary(){
    //checks if there are any errors
    var test = 1;
    //gets the salary savings table element
    var table = document.getElementById('salaryTable');
    //gets the salary savings table footer element
    var foot = document.getElementById('salaryFooter');
    //row = an array of the rows of the table
    var row = table.getElementsByTagName('tr');
    //frow = an arrow of the rows of the footer of the table
    var frow = foot.getElementsByTagName('tr');
        //fcell = an array of the cells in the first row of the footer
    var fcell = frow[0].getElementsByTagName('td');

    //for each row in the table the elements are added to the salary object
    for (i = 0; i<row.length; i++){
      var cell = row[i].getElementsByTagName('td');

      //makes sure the second column isn't empty
      if (cell[1].innerText.trim() === ""){
        cell[1].className = "danger";
        fcell[1].style.visibility = "visible";
        test = test - 1;
      }

      //makes sure the third column entries are numbers
      if (Number.isNaN(Number(cell[2].innerText.trim()))){
        //if the data is not a number the cell will turn red and an error message will display at the bottom of the column
        cell[2].className = "danger";
        fcell[2].style.visibility = "visible";
        test = test - 1;
      }

    }

    //if anything is wrong the salary savings will not be sent
    if (test <= 0){
      foot.style.visibility = "hidden";
      return false;
    }
    return true;
  };

  /* Function: resetTableState()
    Purpose: resets the table styling if any entries were formerly incorrect*/
  function resetSalaryTableState(){
    //gets the cfr Table element
    var table = document.getElementById('salaryTable');
    //row = an array of the rows of the table
    var row = table.getElementsByTagName('tr');
    //gets the cfr table footer element
    var foot = document.getElementById('salaryFooter');
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
