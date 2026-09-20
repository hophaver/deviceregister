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

## Installation and Running

1. **Clone the repository and enter the directory**:

```bash
git clone https://github.com/hophaver/deviceregister.git
cd deviceregister
```

2. **Create and activate a virtual environment**:

```bash
python3 -m venv venv
source venv/bin/activate
```

*(On Windows, activate with `venv\Scripts\activate`)*

3. **Install the dependencies**:

```bash
pip install -r requirements.txt
```

4. **Initialize the database**:

```bash
python3 init_db.py
```

5. **Start the application**:

```bash
flask run
```

6. **Open in browser**:

Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.
