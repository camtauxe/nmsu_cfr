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

function submitCommitments() {

    requestJSON = [];

    rows = document.getElementById('approveTable').getElementsByTagName('tbody')[0].getElementsByTagName('tr');
    for (i = 0; i < rows.length; i++) {
        row = rows[i];
        cells = row.getElementsByTagName('td');

        requestJSON.push({
            dept_name: cells[0].innerText.trim(),
            amount: cells[3].innerText.trim()
        });
    }

    req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                window.alert("Successfully submitted! (The page will now refresh)");
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
    req.open('POST', "/add_commitments", true);
    req.setRequestHeader("Content-Type","text/json; charset=utf-8");
    req.send(JSON.stringify(requestJSON));

}