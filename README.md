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
LITRevu/                ← project root
├── .venv/
├── .gitignore
├── db.sqlite3
├── LICENSE.md
├── manage.py
├── README.md
├── requirements.txt
├── staticfiles/
│   ├── admin/
│   └── css/
│
├── templates/
│   ├── registration/
│   │   └── register.html
│   ├── reviews/
│   │   └── feed.html
│   ├── users/
│   │   └── index.html  ← Site UI Entry Point
│   └── base.html       ← Base/root template
│
├── theme/
│   ├── static/
│   ├── static_src/     ← package.json, postcss.config.js, tailwind.config.js, src/styles.css
│   ├── __init__.py
│   └── apps.py
│
├── LITRevu/            ← Project folder = settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── users/           ← Users
│   ├── __init__.py
│   ├── apps.py
│   ├── migrations/
│   ├── admin.py     ← Super User (Admin)
│   ├── forms.py     ← Registration & Login Forms
│   ├── migrations/
│   ├── tests/
│   │     ├── __init.py
│   │     ├── test_forms.py
│   │     └── test_views.py
│   ├── models.py
│   ├── tests/
│   └── views.py
│   └── urls.py
│
└── reviews/            ← Tickets and Feed
    ├── __init__.py
    ├── apps.py
    ├── migrations/
    ├── models.py
    ├── tests/
    └── views.py

```

## Installation & Setup
1. Clone the repo
```bash
git clone https://github.com/SiRipo92/LITRevu
```
2. Create and activate the virtual environment

    To activate: 
    
    - If using MACOS
       ```bash
       source venv/bin/activate
       ```
    - If using Windows
      ```bash
      venv\Scripts\activate
      ```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Split terminals (have two terminals open): one for backend, one for frontend
   + For Terminal 1 (Backend):
     + For the database:
     ```bash
     python manage.py migrate
     ```
     + Run backend server:
     ```bash
     python manage.py runserver
     ```
   + For Terminal 2 (Frontend):
     + **First time setup:**
       - Navigate to frontend folder to install Node.js and dependencies
       ```bash
       cd cd theme/static_src
       npm install
       cd ../../
       ```
       - To run frontend, once you've returned to project root:
       ```bash
       python manage.py tailwind start
       ```

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

Framework: Django 5.2.7

Linter: flake8 (PEP8 compliance)

Database: SQLite (default local)

IDE: PyCharm

No external deployment configuration yet.

## License
This project is licensed under the 
[Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](https://creativecommons.org/licenses/by-nc-nd/4.0/).

© 2025 Sierra Ripoche — All rights reserved for educational use.