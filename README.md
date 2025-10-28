# LITRevu — Django Web Application

![Flake8 Lint](https://github.com/SiRipo92/LITRevu/actions/workflows/lint.yml/badge.svg)


* **Author:** Sierra Ripoche
* **Project:** Développez une application Web en utilisant Django — OpenClassrooms
* **Framework:** Django 5.x
* **Database:** SQLite (local development)

## Overview
**LITRevu** is a Django-based web application that allows a community of users to:

- Request reviews for books or articles.
- Publish their own reviews.
- Follow other users and view their activity feed.

This project is built as part of the OpenClassrooms Python Developer program.
It represents the **Minimum Viable Product (MVP)** of a platform where users can exchange literary and article critiques.

## Project Structure
```bash
LITRevu/
├── manage.py
├── LITRevu/                 # Django configuration package
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── reviews/                 # Main application package
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── .venv/                   # Virtual environment (excluded from Git)
├── .idea/                   # PyCharm project files (excluded from Git)
└── README.md

```

## Installation & Setup
1. Clone the repo
2. Create and activate the virtual environment
3. Install dependencies
4. Run the development server

## User Stories
+ User Story 1 – Authentication 

As a visitor, I can create an account and log in so that I can access the application’s features.

+ User Story 2 – Ticket Creation

As a logged-in user, I can create a ticket requesting a review for a book or article.

+ User Story 3 – Review Creation

As a logged-in user, I can post a review either in response to a ticket or independently.

+ User Story 4 – Feed Display

As a logged-in user, I can view a feed showing all tickets and reviews from users I follow, ordered by date.

+ User Story 5 – Following System

As a logged-in user, I can follow or unfollow other users to customize my feed.

+ User Story 6 – CRUD Operations

As a logged-in user, I can edit or delete my own tickets and reviews.

+ User Story 7 – Accessibility & Design

As a user with accessibility needs, I can navigate the application easily following WCAG 2.1 guidelines.

## 🧑‍💻 Development Notes

Framework: Django 5.x

Linter: flake8 (PEP8 compliance)

Database: SQLite (default local)

IDE: PyCharm

No external deployment configuration yet.

## License
This project is licensed under the 
[Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](https://creativecommons.org/licenses/by-nc-nd/4.0/).

© 2025 Sierra Ripoche — All rights reserved for educational use.