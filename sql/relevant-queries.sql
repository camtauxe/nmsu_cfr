#revision history
select r.*, c.date_initial, c.date_revised 
from request r, cfr_department c
where r.dept_name = 'Astronomy' and r.semester = 'Spring' and r.cal_year = 2019 and r.revision_num = 2 
	  and r.revision_num = c.revision_num and r.dept_name = c.dept_name and r.semester = c.semester and r.cal_year = c.cal_year;

select r.*, c.date_initial, c.date_revised 
from request r, cfr_department c
where r.dept_name = 'Astronomy' and r.semester = 'Spring' and r.cal_year = 2019 and r.revision_num = 1 
	  and r.revision_num = c.revision_num and r.dept_name = c.dept_name and r.semester = c.semester and r.cal_year = c.cal_year;
      
select r.*, c.date_initial, c.date_revised 
from request r, cfr_department c
where r.dept_name = 'Astronomy' and r.semester = 'Spring' and r.cal_year = 2019 and r.revision_num = 0 
	  and r.revision_num = c.revision_num and r.dept_name = c.dept_name and r.semester = c.semester and r.cal_year = c.cal_year;
      
#total cost of each revision
select sum(r.cost), c.date_initial, c.date_revised
from request r, cfr_department c
where r.dept_name = c.dept_name and r.semester = c.semester and r.cal_year = c.cal_year and r.revision_num = c.revision_num
	  and r.dept_name = 'Astronomy' and r.semester = 'Spring' and r.cal_year = 2019
group by r.revision_num;











