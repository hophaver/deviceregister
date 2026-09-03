# deviceregister / inventory system

## Plan + Requirements
- user can create an account and login (first registered user is admin)
- admin has full access to manage all devices, classifications, and users
- admin can add, edit, and remove other users
- admin can configure privileges for other users
- users can view devices (both own and added by others), with the device owner displayed in the main view
- users can add, edit, and remove devices according to their assigned privileges
- devices have multiple database-defined classifications: Type, Category, Location, and Operating System (OS)
- users can search devices by keywords/values and filter by multiple classifications simultaneously
- secondary entity: users can add maintenance and service logs to any device (own or others)
- users have profile pages showing user information, statistics (devices owned/added, maintenance logs created), and their device list
- pagination for browsing device listings smoothly
- secure implementation: password hashing, route-level access control, input validation, parameterized SQL queries, and CSRF protection

## Technical Specifications
- Python with Flask
- only allowed external library: Flask
- SQLite database with direct SQL queries
- clean, minimalist black-and-white HTML + CSS
