/*********************************************** NMSU Sources of Salary Savings **************************************************/

function addSalaryRow(){
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
        cell.innerHTML = "<div class='form-group'> <select class='form-control' id='standardSelect' name='standardSelect' style='padding: 0px'> <option value='approved amounts from sabbatical leaves'>Approved Amounts from Sabbatical Leaves</option> <option value='research buy out'>Research Buy Out (Provide Index Number)</option> <option value='other funded leave'>Other Funded Leave</option> <option value='leave without pay'>Leave Without Pay</option> </select> </div>"
    }
    //the last column is the delete checkbox
    else if (i == 3){
      cell.className = "noprint";
      cell.innerHTML = "<input type='checkbox' id='checkCFR'>";
    }
  }
};

function salarySubmit(){
    var salaryObj = [
    ];
    var aObj=document.getElementById('salaryTable').getElementsByTagName('tr');
    var i = aObj.length;
    while(i--) {
        if(aObj[i].getElementsByTagName('input')[0].checked || aObj[i].getElementsByTagName('td')[1].innerHTML == "") {
            aObj[i].parentNode.removeChild(aObj[i]);
        }
    }
    var table = document.getElementById('salaryTable');
    var row = table.getElementsByTagName('tr');
    for (i=0; i<row.length; i++){
        var cell = row[i].getElementsByTagName('td');
        salaryObj.push(
            {
            type: row[i].getElementsByTagName('select')[0].value,
            name: cell[1].innerHTML,
            savings: cell[2].innerHTML,
            confirmedAmount: "",
        });
    }
    console.log(salaryObj);
    var salaryJSON = JSON.stringify(salaryObj);

    //ADD HTTP REQUEST
};
