// Functions for the approver's side of the course funding request page

/**
 * Display the modal with the given id
 * @param {string} modal_id 
 */
function summonModal(modal_id) {
    document.getElementById(modal_id).style.display = 'block';
}

/**
 * Hide the modal with the given id
 * @param {string} modal_id 
 */
function dismissModal(modal_id) {
    document.getElementById(modal_id).style.display = 'none';
}

/**
 * Submit a POST request to /approve_courses to approve coures.
 * If successful, the page will be refreshed
 * @param {string} modal_id The id of the modal containing the course table
 * @param {string} dept_name The name of the department the courses belong to 
 */
function approveCFR(modal_id, dept_name) {

    requestJSON = {
        dept_name: dept_name,
        courses: []
    };

    // Iterate through rows of the table
    body = document.querySelector("#"+modal_id+" tbody");
    rows = body.getElementsByTagName('tr')
    for (i = 0; i < rows.length; i++) {
        row = rows[i]
        cells = row.getElementsByTagName('td');

        // If the checkbox in the last column isn't checked,
        // ignore this row
        approveCheckbox = cells[12].getElementsByTagName('input')[0];
        if (!approveCheckbox.checked)
            continue;

        // Ensure that the entered cost is a number
        if (isNaN(cells[9].innerText.trim())) {
            window.alert("Cost must be a number!");
            return;
        }
        cost = Number(cells[9].innerText.trim())

        // Assemble the object for this course and add it to the requestJSON
        courseJSON = {
            commitment_code: cells[11].getElementsByTagName('select')[0].value,
            course: cells[1].innerText.trim(),
            sec: cells[2].innerText.trim(),
            cost: cost
        };
        requestJSON.courses.push(courseJSON)
    }

    // Create and send request
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

/**
 * Submit a POST request to /add_commitments to update the dean committed amounts.
 * If successful, the page will refresh
 */
function submitCommitments() {

    requestJSON = [];

    // Iterate through rows of the main table
    rows = document.getElementById('approveTable').getElementsByTagName('tbody')[0].getElementsByTagName('tr');
    for (i = 0; i < rows.length; i++) {
        row = rows[i];
        cells = row.getElementsByTagName('td');

        requestJSON.push({
            dept_name: cells[0].innerText.trim(),
            amount: cells[3].innerText.trim()
        });
    }

    // Create and send request
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