/************************************************** NMSU CFR ADDITIONAL SCRIPTS **************************************************/

/*
var dummy, dummy1, dummy2, dummyArray, dummyArrayJSON, dummyArray2, dummyJSON, txt, x, i;
//var xmlhttp = new XMLHttpRequest();

function submitCFR() {
  dummy = { name1: document.getElementById("cfrName").value, num1: document.getElementById("cfrNum1").value,
  num2: document.getElementById("cfrNum2").value, num3: document.getElementById("cfrNum3").value};
  dummyJSON = JSON.stringify(dummy);
  dummyArray = { dummy1: dummyJSON };
  dummyArrayJSON = JSON.stringify(dummyArray);


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
  xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xmlhttp.send("x=" + dummyJSON);
}



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

