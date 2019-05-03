/**
* Create the schema for the database
**/

/* User Table */
CREATE TABLE user (
    username       VARCHAR(32)    NOT NULL,   /* Username/ email address*/
    usr_password   VARBINARY(64)  NOT NULL,   /* Password Hast */
    banner_id      NUMERIC(9,0)   NOT NULL,
    type           ENUM('submitter', 'approver', 'admin') NOT NULL, /* Role */
    email          VARCHAR(64),

    PRIMARY KEY (username)
);

/* 
*   Submitter Table
*   Specfies which users are submitters and for what departments
*/
CREATE TABLE submitter(
    username    VARCHAR(32) NOT NULL,
    dept_name   VARCHAR(50) NOT NULL,

    PRIMARY KEY (username),
    FOREIGN KEY (username)
         REFERENCES user(username) ON DELETE CASCADE
   );

/* Semester Table */
CREATE TABLE semester (
    semester   ENUM('Fall', 'Spring', 'Summer') NOT NULL,
    cal_year   NUMERIC(4,0)     NOT NULL,
    active     ENUM('yes','no') NOT NULL,

    PRIMARY KEY (semester, cal_year)
);

/*
* cfr_department.
*   Specfies entire course funding requests, linked with departments
*/
CREATE TABLE cfr_department(
    dept_name       VARCHAR(50) NOT NULL,
    semester        ENUM('Fall', 'Spring', 'Summer') NOT NULL,
    cal_year        NUMERIC(4,0) NOT NULL,
    date_initial    DATETIME NOT NULL,
    date_revised    DATETIME,
    revision_num    INT,
    cfr_submitter   VARCHAR(32),
    dean_committed  DECIMAL(19,2),

    PRIMARY KEY (dept_name, semester, cal_year, revision_num),
    FOREIGN KEY (cfr_submitter)
        REFERENCES user(username) ON DELETE SET NULL,
    FOREIGN KEY (semester, cal_year)
        REFERENCES semester(semester, cal_year)
);

/* request/course table */
CREATE TABLE request(
    id              mediumint NOT NULL auto_increment,
    commitment_code ENUM('EM', 'SS', 'CO', 'DE'),
    priority        INT,
    course          VARCHAR(15),
    sec             VARCHAR(10),
    mini_session    ENUM('Yes', 'No') NOT NULL,
    online_course   ENUM('Yes', 'No') NOT NULL,
    num_students    INT,
    instructor      VARCHAR(100),
    banner_id       NUMERIC(9,0),
    inst_rank       VARCHAR(10),
    cost            DECIMAL(19,2) NOT NULL,
    reason          TEXT,
    approver        VARCHAR(32),

    PRIMARY KEY (id),
    FOREIGN KEY (approver)
      REFERENCES user(username) ON DELETE SET NULL
);  

/* 
* cfr_request
*   Specifies which courses belong to which cfrs
*/
CREATE TABLE cfr_request(
    course_id       mediumint   NOT NULL, 
    dept_name       VARCHAR(50) NOT NULL,
    semester        ENUM('Fall', 'Spring', 'Summer')    NOT NULL,
    cal_year        NUMERIC(4,0)    NOT NULL,
    revision_num    INT             NOT NULL,

    PRIMARY KEY (course_id, dept_name, semester, cal_year, revision_num),
    FOREIGN KEY (course_id) 
        REFERENCES request(id),
    FOREIGN KEY (dept_name, semester, cal_year, revision_num)
        REFERENCES cfr_department(dept_name, semester, cal_year, revision_num)
   );

/* Salary savings table */
CREATE TABLE sal_savings(
    id              mediumint NOT NULL AUTO_INCREMENT,
    leave_type      ENUM('Sabbatical', 'RBO', 'LWOP', 'Other') NOT NULL,
    inst_name       VARCHAR(100),
    savings         DECIMAL(19,2) NOT NULL,
    confirmed_amt   DECIMAL(19,2),
    notes           TEXT,
    approver        VARCHAR(32),

    PRIMARY KEY (id),
    FOREIGN KEY (approver)
      REFERENCES user(username) ON DELETE SET NULL
);

/* 
* cfr_savings
*   Specifies which savings belong to which cfrs
*/
CREATE TABLE cfr_savings(
    savings_id      mediumint NOT NULL, 
    dept_name       VARCHAR(50) NOT NULL,
    semester        ENUM('Fall', 'Spring', 'Summer') NOT NULL,
    cal_year        NUMERIC(4,0) NOT NULL,
    revision_num    INT NOT NULL,

    PRIMARY KEY (savings_id, dept_name, semester, cal_year, revision_num),
    FOREIGN KEY (savings_id) 
        REFERENCES sal_savings(id),
    FOREIGN KEY (dept_name, semester, cal_year, revision_num)
        REFERENCES cfr_department(dept_name, semester, cal_year, revision_num)
);
