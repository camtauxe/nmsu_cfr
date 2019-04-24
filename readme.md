# Course Funding Request System for New Mexico State University College of Arts and Sciences

Spring 2019 Senior Project

**Instructor:** William Hamilton

**Contributors:**
* Angela Kearns
* Cameron Tauxe
* Elena Davidson
* Kathleen Near
* Louis Miller

This is an online system for managing the submission and approval of course funding requests in the New Mexico State University College of Arts and Sciences.

It is implemented as a docker container running Apache HTTP server using
Python for backend code via WSGI.

### Prerequisites
* Docker
* Access to a MySQL Database

### Build and run
```
docker-compose up -d --build
```
This will rebuild the image and start the docker container in the background. It will be bound to Port 80 on the host machine. Simply open a
web browser and navigate to *localhost*

If you get the following error:
```
ERROR: Couldn't find env file: /path/to/nmsu_cfr/cfr.env
```
Read **Connecting to a Database** below for how to configure a set of environment variables to pass to docker-compose.

### Connecting to a Database
In order to work, the system needs to be connected to an external MySQL database that will contain all of its data (users, requests, revisions, etc.). The credintials for this database are provided as environment variables that docker-compose passes to the container at startup. Copy *cfr.env.example* to a new file *cfr.env* and edit the variables provided for the database you wish to connect to.
```env
DB_HOST=example.com
DB_USER=myuser
DB_PASS=password
DB_DATABASE=mydatabase

DEBUG=yes
```
Because the *cfr.env* file is specific to you and because it may contain private information (such as a database password), it is ignored by git.

### First-time setup
Log on to the database, you have connected to and run the following scripts in order
- *sql/clear_db.sql*
- *create_schema.sql*
- *init_db.sql*

This will initialize the database with a single user, 'admin' with the
password 'admin'. With this, you can log in **CHANGE THE DEFAULT ADMIN PASSWORD** and then add users as well as select the active semester.

### Debug Mode
If the environment variable **DEBUG** is set to **yes** in *cfr.env*, then the system will be started in debug mode. This will display extra information to the user in the event of a 500 Internal Server Error.