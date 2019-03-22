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
       references user(username)
   );

create table cfr_department
   (dept_name      varchar(50),
    semester      enum('Fall', 'Spring', 'Summer'),
    cal_year      numeric(4,0) not null,
    date_initial      datetime not null,
    date_revised      datetime,
    revision_num      int,
    cfr_submitter      varchar(32),
    primary key (dept_name, semester, cal_year, revision_num),
    foreign key (cfr_submitter)
	   references user(username)
   );

create table request
   (commitment_code      enum('EM', 'SS', 'CO', 'DE'),
    priority      int,
    course      varchar(15),
    sec      varchar(10),
    mini_session      enum('Yes', 'No') not null,
    online_course      enum('Yes', 'No') not null,
    num_students      int,
    instructor      varchar(100),
    banner_id      numeric(9,0),
    inst_rank      varchar(10),
    cost      decimal(19,4) not null,
    reason      text,
    dept_name      varchar(50) not null,
    semester      enum('Fall', 'Spring', 'Summer'),
    cal_year      numeric(4,0),
    revision_num      int,
    primary key (course, sec, dept_name, semester, cal_year, revision_num),
    foreign key (dept_name, semester, cal_year, revision_num)
       references cfr_department(dept_name, semester, cal_year, revision_num)
   );  

create table sal_savings
   (leave_type      enum('Sabbatical', 'RBO', 'LWOP', 'Other') not null,
    inst_name      varchar(100),
    savings      decimal(19,4) not null,
    confirmed_amt      decimal(19,4),
    notes      text,
    dept_name      varchar(50),
    semester      enum('Fall', 'Spring', 'Summer'),
    cal_year      numeric(4,0),
    revision_num      int,
    primary key (inst_name, dept_name, semester, cal_year, revision_num),
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







      
       			     