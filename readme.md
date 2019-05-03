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
docker-compose -f "docker-compose-hostmode.yml" up -d --build
```
This will rebuild the image and start the docker container in the background. It will be bound to Port 80 on the host machine. Simply open a
web browser and navigate to *localhost*

Depending on your setup, you may want to use *docker-compose-bridgemode.yml* as the the docker-compose file instead. Host mode doesn't work on Windows and MacOS, but you won't be able to connect to a local database through 'localhost.' If you need to customize
the build further, you can create your own docker-compose file and call
it *docker-compose-local.yml* which will be ignored by git.

If you get the following error:
```
ERROR: Couldn't find env file: /path/to/nmsu_cfr/cfr.env
```
Read **Configuring the Environnment** below for how to configure a set of environment variables to pass to docker-compose.

### Configuring the Environnment
When the Docker container is built, it looks for the file *cfr.env* which will contain environment variables giving credintials to connect to
a MySQL database for data and to an SMTP server for email notifications. Copy *cfr.env.example* to a new file *cfr.env* and edit the variables provided.
```env
DB_HOST=example.com
DB_USER=myuser
DB_PASS=password
DB_DATABASE=mydatabase

SMTP_SERVER=smtp.example.com
SMTP_ADDRESS=noreply@example.com
SMTP_PASSWORD=password
SMTP_PORT=587

DEBUG=yes
```
If any of the Database environment variables are not specified, the system will not work and a "The environment has not been configured" message
will be displayed when accessing it in a browser. If any of the SMTP variables are missing, the system will still work, but email notifications
will not be sent.

Because the *cfr.env* file is specific to you and because it may contain private information (such as a database password), it is ignored by git.

### First-time setup
Log on to the database you have connected to and run the following scripts in order
- *sql/clear_db.sql*
- *create_schema.sql*
- *init_db.sql*

This will initialize the database with a single user, 'admin' with the
password 'admin'. With this, you can log in **CHANGE THE DEFAULT ADMIN PASSWORD** and then add users as well as select the active semester.

### Debug Mode
If the environment variable **DEBUG** is set to **yes** in *cfr.env*, then the system will be started in debug mode. This will display extra information to the user in the event of a 500 Internal Server Error.