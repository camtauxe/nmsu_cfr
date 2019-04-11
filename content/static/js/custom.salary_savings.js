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
    for (i=0; i<4; i++) {
        var cell = row.insertCell(i);
        if (i!=0 && i!=3){
          cell.contentEditable = "true";
          cell.className = "editable";
          cell.innerHTML = "";
        }
        else if (i == 0){
            cell.innerHTML = "<div class='form-group' style='margin: 0px 0px'> <select class='form-control' id='standardSelect' name='standardSelect'> <option value='Sabbatical'>Approved Amounts from Sabbatical Leaves</option> <option value='RBO'>Research Buy Out (Provide Index Number)</option> <option value='Other'>Other Funded Leave</option> <option value='LWOP'>Leave Without Pay</option> </select> </div>"
        }
        //the last column is the delete checkbox
        else if (i == 3){
          cell.className = "noprint";
          cell.innerHTML = "<input type='checkbox' id='checkCFR'>";
        }
    }
};

function salarySubmit(){
    //creates a javascript array object for the salary submissions
    var salaryObj = [
    ];
    
    //saves the rows of the salary savings table from salary_saving.html into aObj
    var aObj=document.getElementById('salaryTable').getElementsByTagName('tr');
    var i = aObj.length;
    //iterates through each row in the table
    while(i--) {
        //checks if the row is empty or checked
        if(aObj[i].getElementsByTagName('td')[1].innerHTML == "" || aObj[i].getElementsByTagName('input')[0].checked) {
            //deletes row
            aObj[i].parentNode.removeChild(aObj[i]);
        }
    }
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
            leave_type: row[i].getElementsByTagName('select')[0].value,
            inst_name: cell[1].innerText.trim(),
            savings: cell[2].innerText.trim(),
            notes: "",
            confirmedAmount: "",
        });
    }
    //prints the javascript object to the console
    console.log(salaryObj);
    //converts the javascript object into JSON so that it can be sent via HTTP request
    var salaryJSON = JSON.stringify(salaryObj);

    //ADD HTTP REQUEST
    xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4) {
        document.getElementById("submitSalaryButton").disabled = false;
        if (this.status == 200) {
          window.alert("Successfully submitted changes!")
        }
        else {
          window.alert("Something went wrong! The changes were not submitted.\n Server returned: "+this.status)
        }
      }
    };
    
    document.getElementById("submitSalaryButton").disabled = true;
    xmlhttp.open("POST", "/add_sal_savings", true);
    xmlhttp.setRequestHeader("Content-Type", "text/json; charset=utf-8");
    xmlhttp.send(salaryJSON);
};
