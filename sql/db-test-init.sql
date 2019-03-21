# mySQL script that inserts basic testing data 
# creates 10 new users, 7 submitters and 3 approvers
# creates initial cfr for departements Astronomy, Biology and Physics
# inserts class funding requests into each of these departments
# inserts salary savings for one instructor into Astronomy cfr
# creates two revisions to Astronomy cfr

#create users
INSERT INTO user 
VALUES ('submitter1', 'password', 800000000, 'submitter'),
		('submitter2', 'password', 800000001, 'submitter'),
       ('submitter3', 'password', 800000002, 'submitter'),
       ('submitter4', 'password', 800000003, 'submitter'),
       ('submitter5', 'password', 800000004, 'submitter'),
       ('submitter6', 'password', 800000005, 'submitter'),
       ('submitter7', 'password', 800000006, 'submitter'),
       ('approver1', 'password', 800000007, 'approver'),
       ('approver2', 'password', 800000008, 'approver'),
       ('approver3', 'password', 800000009, 'approver');       
INSERT INTO submitter
VALUES ('submitter1', 'Astronomy'),
	     ('submitter2', 'Biology'),
       ('submitter3', 'Physics'),
       ('submitter4', 'Art'),
       ('submitter5', 'History'),
       ('submitter6', 'Music'),
       ('submitter7', 'Theatre');


#create initial cfrs
INSERT INTO cfr_department
VALUES ('Astronomy', 'Spring', 2019, NOW(), NULL, 0, 'submitter1'),
       ('Biology', 'Spring', 2019, NOW(), NULL, 0, 'submitter2'),
       ('Physics', 'Spring', 2019, NOW(), NULL, 0, 'submitter3');

#insert class requests into into initial cfrs
INSERT INTO request 
VALUES ( NULL, NULL, 'AST101', 'M02', 'NO', 'NO', 45, 'Smith', 800111111, NULL, 1024.00, NULL, 'Astronomy', 'Spring', 2019, 0), 
       ( NULL, NULL, 'AST339', 'M02', 'NO', 'NO', 45, 'Smith', 800111111, NULL, 1024.00, NULL, 'Astronomy', 'Spring', 2019, 0),
       ( NULL, NULL, 'AST449', 'M01', 'NO', 'NO', 45, 'Smith', 800111111, NULL, 10000.56, NULL, 'Astronomy', 'Spring', 2019, 0),
       ( NULL, NULL, 'BIO101', 'M01', 'NO', 'NO', 60, 'Johnson', 800111110, NULL, 1024.00, NULL, 'Biology', 'Spring', 2019, 0),
       ( NULL, NULL, 'BIO101', 'M02', 'NO', 'NO', 54, 'Johnson', 800111110, NULL, 1024.00, NULL, 'Biology', 'Spring', 2019, 0),
       ( NULL, NULL, 'PHY101', 'M01', 'NO', 'NO', 45, 'Miller', 800111112, NULL, 1024.00, NULL, 'Physics', 'Spring', 2019, 0);


#insert sal_savings into Astronomy cfr 
INSERT INTO  sal_savings
VALUES ('Sabbatical', 'Mendez', 40254.22, NULL, NULL, 'Astronomy', 'Spring', 2019, 0);


#revision to cfr for Astronomy
#create new revision of cfr
insert into cfr_department values('Astronomy', 'Spring', 2019, (select c.date_initial from cfr_department c where c.dept_name = 'Astronomy' AND c.semester = 'Spring' AND c.cal_year = 2019 AND c.revision_num = 0), NOW(), 1, 'submitter1'); 

#duplicate initial cfr with new revision number
CREATE TABLE temp1 AS SELECT * 
				     FROM request 
					 WHERE dept_name = 'Astronomy' AND semester = 'Spring' AND cal_year = 2019 AND revision_num = 0; 
CREATE TABLE temp2 AS SELECT *
                      FROM sal_savings
                      WHERE dept_name = 'Astronomy' AND semester = 'Spring' AND cal_year = 2019 AND revision_num = 0;                      
SET SQL_SAFE_UPDATES=0;                     
UPDATE temp1 SET revision_num= 1;
UPDATE temp2 SET revision_num= 1;
SET SQL_SAFE_UPDATES=1;
INSERT INTO request SELECT * FROM temp1 ;
INSERT INTO sal_savings SELECT * FROM temp2;
DROP TABLE temp1;
DROP TABLE temp2; 
      
#add or remove requests and salary savings
#example: remove AST101 M02 and add AST101 M01
DELETE FROM request WHERE dept_name = 'Astronomy' AND semester = 'Spring' AND cal_year = 2019 AND revision_num = 1 AND  course = 'AST101' AND sec = 'M02';
INSERT INTO request 
VALUES ( NULL, NULL, 'AST101', 'M01', 'NO', 'NO', 45, 'Smith', 800111111, NULL, 1024.00, NULL, 'Astronomy', 'Spring', 2019, 1);


#second revision of cfr for Astronomy
insert into cfr_department values('Astronomy', 'Spring', 2019, (select c.date_initial from cfr_department c where c.dept_name = 'Astronomy' AND c.semester = 'Spring' AND c.cal_year = 2019 AND c.revision_num = 0), NOW(), 2, 'submitter1'); 

CREATE TABLE temp1 AS SELECT * 
				     FROM request 
					 WHERE dept_name = 'Astronomy' AND semester = 'Spring' AND cal_year = 2019 AND revision_num = 1; 
CREATE TABLE temp2 AS SELECT *
                      FROM sal_savings
                      WHERE dept_name = 'Astronomy' AND semester = 'Spring' AND cal_year = 2019 AND revision_num = 1;                      
SET SQL_SAFE_UPDATES=0;                     
UPDATE temp1 SET revision_num= 2;
UPDATE temp2 SET revision_num= 2;
SET SQL_SAFE_UPDATES=1;
INSERT INTO request SELECT * FROM temp1 ;
INSERT INTO sal_savings SELECT * FROM temp2;
DROP TABLE temp1;
DROP TABLE temp2; 
       
INSERT INTO request 
VALUES ( NULL, NULL, 'AST205', 'M01', 'NO', 'NO', 45, 'Smith', 800111111, NULL, 1024.00, NULL, 'Astronomy', 'Spring', 2019, 2);
       
