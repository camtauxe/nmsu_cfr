create table user
   (username      varchar(32),
    usr_password      varbinary(64) not null,
    banner_id      numeric(9,0) not null,
    type      enum('submitter', 'approver', 'admin') NOT NULL,
    primary key (username)
   );

create table submitter
   (username      varchar(32),
    dept_name      varchar(50) not null,
    primary key (username),
    foreign key (username)
       references user(username) on delete cascade
   );

create table semester
   (semester   enum('Fall', 'Spring', 'Summer') not null,
    cal_year   numeric(4,0) not null,
    active     enum('yes','no') not null,
    primary key (semester, cal_year)
   );

create table cfr_department
   (dept_name      varchar(50),
    semester      enum('Fall', 'Spring', 'Summer'),
    cal_year      numeric(4,0) not null,
    date_initial      datetime not null,
    date_revised      datetime,
    revision_num      int,
    cfr_submitter      varchar(32),
    dean_committed      decimal(19,2),
    primary key (dept_name, semester, cal_year, revision_num),
    foreign key (cfr_submitter)
      references user(username) on delete set null,
    foreign key (semester, cal_year)
      references semester(semester, cal_year)
   );

create table request
   (id      mediumint NOT NULL auto_increment,
    commitment_code      enum('EM', 'SS', 'CO', 'DE'),
    priority      int,
    course      varchar(15),
    sec      varchar(10),
    mini_session      enum('Yes', 'No') not null,
    online_course      enum('Yes', 'No') not null,
    num_students      int,
    instructor      varchar(100),
    banner_id      numeric(9,0),
    inst_rank      varchar(10),
    cost      decimal(19,2) not null,
    reason      text,
    approver      varchar(32),
    primary key (id),
    foreign key (approver)
	   references user(username) on delete set null
   );  

create table cfr_request
	(course_id      mediumint NOT NULL, 
     dept_name      varchar(50) NOT NULL,
     semester      enum('Fall', 'Spring', 'Summer') NOT NULL,
     cal_year      numeric(4,0) NOT NULL,
     revision_num      int NOT NULL,
     primary key (course_id, dept_name, semester, cal_year, revision_num),
     foreign key (course_id) 
           references request(id),
     foreign key (dept_name, semester, cal_year, revision_num)
           references cfr_department(dept_name, semester, cal_year, revision_num)
	);

create table sal_savings
   (id      mediumint NOT NULL AUTO_INCREMENT,
    leave_type      enum('Sabbatical', 'RBO', 'LWOP', 'Other') not null,
    inst_name      varchar(100),
    savings      decimal(19,2) not null,
    confirmed_amt      decimal(19,2),
    notes      text,
    approver       varchar(32),
    primary key (id),
    foreign key (approver)
	   references user(username) on delete set null
   );
   
create table cfr_savings
	(savings_id      mediumint NOT NULL, 
     dept_name      varchar(50) NOT NULL,
     semester      enum('Fall', 'Spring', 'Summer') NOT NULL,
     cal_year      numeric(4,0) NOT NULL,
     revision_num      int NOT NULL,
     primary key (savings_id, dept_name, semester, cal_year, revision_num),
     foreign key (savings_id) 
           references sal_savings(id),
     foreign key (dept_name, semester, cal_year, revision_num)
           references cfr_department(dept_name, semester, cal_year, revision_num)
   );

create table dummy_data 
   (
      name     varchar(24),
      value1   int,
      value2   int,
      value3   int,

      primary key (name)
   );
