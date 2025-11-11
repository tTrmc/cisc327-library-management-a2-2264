# Library Management System - Flask Web Application with SQLite

## Overview

[![Python Tests](https://github.com/tTrmc/CISC327-CMPE327-F25/actions/workflows/python-tests.yml/badge.svg)](https://github.com/tTrmc/CISC327-CMPE327-F25/actions/workflows/python-tests.yml)
[![codecov](https://codecov.io/gh/tTrmc/cisc327-library-management-a2-2264/graph/badge.svg?token=CVV7M4024T)](https://codecov.io/gh/tTrmc/cisc327-library-management-a2-2264)

This project contains a partial implementation of a Flask-based Library Management System with SQLite database, designed for CISC 327 (Software Quality Assurance) coursework.

Students are provided with:

- [`requirements_specification.md`](requirements_specification.md): Complete requirements document with 7 functional requirements (R1-R7)
- [`app.py`](app.py): Main Flask application with application factory pattern
- [`routes/`](routes/): Modular Flask blueprints for different functionalities
  - [`catalog_routes.py`](routes/catalog_routes.py): Book catalog display and management routes
  - [`borrowing_routes.py`](routes/borrowing_routes.py): Book borrowing and return routes
  - [`api_routes.py`](routes/api_routes.py): JSON API endpoints for late fees and search
  - [`search_routes.py`](routes/search_routes.py): Book search functionality routes
- [`database.py`](database.py): Database operations and SQLite functions
- [`services/`](services/): Modular service layer containing core business logic and integrations
  - [`library_service.py`](services/library_service.py): **Business logic functions** (your main testing focus)
  - [`payment_service.py`](services/payment_service.py): Simulated external payment gateway used for mocking/stubbing exercises
- [`templates/`](templates/): HTML templates for the web interface
- [`requirements.txt`](requirements.txt): Python dependencies

## ❗ Known Issues
The implemented functions may contain intentional bugs. Students should discover these through unit testing (to be covered in later assignments).

## Database Schema
**Books Table:**
- `id` (INTEGER PRIMARY KEY)
- `title` (TEXT NOT NULL)
- `author` (TEXT NOT NULL)  
- `isbn` (TEXT UNIQUE NOT NULL)
- `total_copies` (INTEGER NOT NULL)
- `available_copies` (INTEGER NOT NULL)

**Borrow Records Table:**
- `id` (INTEGER PRIMARY KEY)
- `patron_id` (TEXT NOT NULL)
- `book_id` (INTEGER FOREIGN KEY)
- `borrow_date` (TEXT NOT NULL)
- `due_date` (TEXT NOT NULL)
- `return_date` (TEXT NULL)

## Assignment Instructions
See [`student_instructions.md`](student_instructions.md) for complete assignment details.

**Resources for students:**

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Test Driven Development](https://www.datacamp.com/tutorial/test-driven-development-in-python)
- [Pytest framework](https://realpython.com/pytest-python-testing/)
- [Python Blueprint](https://flask.palletsprojects.com/en/stable/blueprints)


