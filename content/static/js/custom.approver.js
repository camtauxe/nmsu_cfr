function summonModal(modal_id) {
    document.getElementById(modal_id).style.display = 'block';
}

function dismissModal(modal_id) {
    document.getElementById(modal_id).style.display = 'none';
}

function approveCFR(modal_id, dept_name) {

    requestJSON = {
        dept_name: dept_name,
        courses: []
    };

    body = document.querySelector("#"+modal_id+" tbody");
    rows = body.getElementsByTagName('tr')
    for (i = 0; i < rows.length; i++) {
        row = rows[i]
        cells = row.getElementsByTagName('td');

        approveCheckbox = cells[12].getElementsByTagName('input')[0];
        if (!approveCheckbox.checked)
            continue;

        if (isNaN(cells[9].innerText.trim())) {
            window.alert("Cost must be a number!");
            return;
        }
        cost = Number(cells[9].innerText.trim())

        courseJSON = {
            commitment_code: cells[11].getElementsByTagName('select')[0].value,
            course: cells[1].innerText.trim(),
            sec: cells[2].innerText.trim(),
            cost: cost
        };
        requestJSON.courses.push(courseJSON)
    }

    req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                window.alert("Successfully approved courses! (The page will now refresh)");
                location.reload()
              }
              else if (this.status == 400) {
                window.alert("Something was wrong with the submitted data!\n"+this.response);
              }
              else {
                window.alert("Something went wrong! The changes were not submitted.\n Server returned: "+this.status);
              }
        }
    }
    req.open('POST', "/approve_courses", true);
    req.setRequestHeader("Content-Type","text/json; charset=utf-8");
    req.send(JSON.stringify(requestJSON))
}

function approveSS(modal_id, dept_name) {

    requestJSON = {
        dept_name: dept_name,
        savings: []
    };

    body = document.querySelector("#"+modal_id+" tbody");
    rows = body.getElementsByTagName('tr')
    for (i = 0; i < rows.length; i++) {
        row = rows[i]
        cells = row.getElementsByTagName('td');

        approveCheckbox = cells[5].getElementsByTagName('input')[0];
        if (!approveCheckbox.checked)
            continue;

        if (isNaN(cells[4].innerText.trim())) {
            window.alert("Confirmed amount must be a number!");
            return;
        }
        confirmed_amt = Number(cells[4].innerText.trim())

        savingJSON = {
            inst_name: cells[1].innerText.trim(),
            confirmed_amt: confirmed_amt
        };
        requestJSON.savings.push(savingJSON)
    }

    req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                window.alert("Successfully approved savings! (The page will now refresh)");
                location.reload()
              }
              else if (this.status == 400) {
                window.alert("Something was wrong with the submitted data!\n"+this.response);
              }
              else {
                window.alert("Something went wrong! The changes were not submitted.\n Server returned: "+this.status);
              }
        }
    }
    req.open('POST', "/approve_sal_savings", true);
    req.setRequestHeader("Content-Type","text/json; charset=utf-8");
    req.send(JSON.stringify(requestJSON))
}