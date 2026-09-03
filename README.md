# Device Register

## Application features

* A user can create an account and log in (the first registered user is an admin).
* Admin has full access to manage all devices, classifications, and users.
* Admin can add, edit, and remove other users.
* Admin can configure privileges for other users.
* Users can view devices (both own and added by others), with the device owner displayed in the main view.
* Users can add, edit, and remove devices according to their assigned privileges.
* Devices have multiple database-defined classifications: Type, Category, Location, and Operating System (OS).
* Users can search devices by keywords/values and filter by multiple classifications simultaneously.
* Users can add maintenance and service logs to any device (own or others).
* Users have profile pages showing user information, statistics (devices owned/added, maintenance logs created), and their device list.
* The application uses pagination for browsing device listings smoothly.
* Secure implementation: password hashing, route-level access control, input validation, parameterized SQL queries, and CSRF protection.

## Technical details

* Python with Flask (only allowed external library: Flask)
* SQLite database with direct SQL queries
* Clean, minimalist black-and-white HTML + CSS

## Installation

Install the `flask` library:

```
$ pip install flask
```

Create the database tables and insert initial data:

```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```

Start the application:

```
$ flask run
```
