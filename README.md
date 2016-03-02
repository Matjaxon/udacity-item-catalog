# Item Catalog Application

## Overview

The purpose of this project is to display basic web app development skills as part of Udacity's Fullstack Web Developer Nanodegree.

## Necessary Files
1.  **Udacity's fullstack-nanodegree-vm** - Original version can be obtained
from the following
Github link:  https://github.com/udacity/fullstack-nanodegree-vm.git.  This
directory contains the necessary Vagrant and VirtualBox programs used to run the
databases.

2.  **Catalog Folder**
  1.  **item_catalog.py** - Python file containing the primary Python code needed to run the item catalog app.  URL routing and SQLAlchemy queries are found here.
  2.  **item_catalog.db** - PostgreSQL Database housing info on each vendor, item, and user.  CRUD functions in item_catalog.py interact with this database.
  3.  **static folder** - Houses css files used for styling the application.
  4.  **templates folder** - Houses html templates for each webpage of the application.

## Dependencies
- Programs must be run with Vagrant running and logged in.

## Getting Started
- Navigate to the "oauth" directory and enter "vagrant up" in the command line to boot the virtual machine.
- Enter "vagrant ssh" in the command line to login to the virtual machine.
- Type "cd /vagrant" into the command line to navigate to the project directory in the virtual machine.
- Run item_catalog.py to verify the functionality of the application.
- The application will be running on local host 5000.
- Follow the links on each webpage to add, edit, or delete restaurants and items at each respective restaurant.
- Deleting a vendor company will delete all items associated with that vendor from the database.
- All fields must be completed when creating or editing a vendor or item.
- To access the database directly, type "psql" into the command line.  Then type "\c item_catalog" to connect to the catalog database.  You should see "item_catalog=>" at the start of the command line.  This indicates that you are connected to the database.  From here you can query or write to the item_catalog database.
