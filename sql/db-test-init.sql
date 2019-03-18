# mySQL script that inserts basic testing data 
# creates 10 new users, 7 submitters and 3 approvers
# creates initial cfr for departements Astronomy, Biology and Physics
# inserts class funding requests into each of these departments
# inserts salary savings for one instructor into Astronomy cfr
# creates two revisions to Astronomy cfr

#create users
INSERT INTO user 
VALUES ('submitter1', 0xba75e5b5235c647fe1fc9474727032ebaceab0f1260b811aaae21c6348de3fc1dc14530070d8015093db150dba8bfa26bf03a0bf33963e488e25a67722531b87, 800000000, 'submitter'),
       ('submitter2', 0xbc665b8b99ea44c5db210086625243c994b5e918d16da3d133467dcb657329b623473500463cd64b14b0f6240f2a6295b43ecaeeda34f39877d386b4134be3b5, 800000001, 'submitter'),
       ('submitter3', 0x1f020d24c094c5afe6528375021f22a3111a6bdf5342c949c3f50d5eb9c2e1a508f717333d4c3df55352e38b6f71436a75caa05b64d558858d0d235cb639f32a, 800000002, 'submitter'),
       ('submitter4', 0x5bcf92b6cd4e281b8fec52fda958457ed1ad4510a6df123c3262edff2f0a9a682be6bc618921f8e79abd23e17d81a92be10e11bf5798c9401c75647ee3c8d7bc, 800000003, 'submitter'),
       ('submitter5', 0x24d46e6fae8667fc1d8e3d03aa2425cdc1df5fb24d9949585e5b3ab9fcb96b8d917649660fc36b7a86525ffd1a94a7e2e4431123a373bfbc6df70cb4c5ba750e, 800000004, 'submitter'),
       ('submitter6', 0x31f62b7f320bdecae23491b61c64f4c6120189acce3310571d99c182aa55010ea76066ff186c463dd73632f7f97e1d926fefc502e89993665666e5f115a1f068, 800000005, 'submitter'),
       ('submitter7', 0xf9f4d11fd4f84147cdb685c38153ad9c7368c6e954332c3d03be7ea9d5d31a25f052eadc2e667bfe4c28e988298e0491e5160e29ec3a81481b7d7e7baa17794f, 800000006, 'submitter'),
       ('approver1', 0x86711de86de1fc5683c170414e2402e8fa87957027299a2c11d2e5e5253c6de8417849a150e20a7b026fd44c9b056b7daf96ce04cce161674a7772b1ed78e070, 800000007, 'approver'),
       ('approver2', 0x42d09c93ca9b6d6bd11c814a2b4f09b7650f8234887a48d2c031b77f2fa06c71dbdb9e4965aad990f3fe6ed91f71fbac56a7e2c57bc80d068b3977b9d56b10ce, 800000008, 'approver'),
       ('approver3', 0x475700a5b9f9c1798abc11c5a1d87e3a9a18b0791ff992b4ac61c271982f6a7e0997c096f9151eb255b6b58ee13f5433673c78c8290e8201ffb0e832cad35e98, 800000009, 'approver');       
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
       
