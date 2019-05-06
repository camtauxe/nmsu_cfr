# First Time Setup

### Prerequisites
* Docker
* Access to a MySQL Database

Please refer to the documentation for each system to install it in your environment.
* [Docker Installation](https://docs.docker.com/install/)
* [MySQL Installation](https://dev.mysql.com/doc/refman/8.0/en/installing.html)

The MySQL server can be hosted either on the same machine as the container for the Course Funding Request System or on a remote machine. If hosted locally, please be aware of any configuration needed to be able to connect to the database from within the container.

### Setting up the Database
You will need to create a database on the MySQL server to hold the data for the CFR system (users, requests, revisions, etc.). Log in to the new database and run the following scripts **in order**:
* [*sql/clear_db.sql*](../sql/clear_db.sql)
* [*sql/create_schema.sql*](../sql/create_schema.sql)
* [*sql/init_db.sql*](../sql/init_db.sql)

It is highly reccommended that you create a new MySQL user for the system to use when interacting with the database. The user should have at least **SELECT**,**INSERT**,**UPDATE** and **DELETE** permissions to the database.

### Configuring the Environnment
When the Docker container is built, it looks for the file *cfr.env* which will contain environment variables giving credintials to connect to
a MySQL database for data and to an SMTP server for email notifications. Copy *[cfr.env.example](../cfr.env.example)* to a new file *cfr.env* and edit the variables provided.
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

If the environment variable **DEBUG** is set to "yes" in *cfr.env*, then the system will be started in debug mode. This will display extra information to the user in the event of a 500 Internal Server Error.

Because the *cfr.env* file is specific to you and because it may contain private information (such as a database password), it is ignored by git.

### Build and run
```
docker-compose -f "docker-compose-hostmode.yml" up -d --build
```
This will rebuild the image and start the docker container in the background. It will be bound to Port 80 on the host machine. Simply open a
web browser and navigate to *localhost*

Depending on your setup, you may want to use *docker-compose-bridgemode.yml* as the the docker-compose file instead. Host mode doesn't work on Windows and MacOS, but you won't be able to connect to a local database through 'localhost.' If you need to customize the build further, you can create your own docker-compose file and call
it *docker-compose-local.yml* which will be ignored by git.

If you get the following error:
```
ERROR: Couldn't find env file: /path/to/nmsu_cfr/cfr.env
```
Then make sure you followed the steps in **Configuring the Environment**

### Admin Setup

The System will be initialized with a single admin user account
with the password "admin". When you log in, **please change the 
default admin password!!!** After that, you can use the admin
controls to add new users and add/set the active semester.
