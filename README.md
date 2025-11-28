# LITRevu — Django Web Application

![Flake8](./flake8_report/badge.svg)

* **Author:** Sierra Ripoche
* **Project:** Développez une application Web en utilisant Django — OpenClassrooms
* **Framework:** Django 4.2.16
* **Database:** SQLite (local development)

## Overview
**LITRevu** is a Django-based web application that allows a community of users to:

- Request reviews for books or articles.
- Publish their own reviews.
- Follow other users and view their activity feed.

This project is built as part of the OpenClassrooms Python Developer program.
It represents the **Minimum Viable Product (MVP)** of a platform where users can exchange literary and article critiques.

### Compte superutilisateur (administration Django)

- URL admin : http://localhost:8000/admin/
- Nom d’utilisateur : oc_admin
- Mot de passe : OpenClassrooms_Evaluator!*

## Project Structure
```bash
LITRevu/
├── LICENSE.md
├── LITRevu/                         # Django project package (settings + root config)
│   ├── __init__.py
│   ├── asgi.py                     # ASGI config
│   ├── settings.py                 # Django settings
│   ├── urls.py                     # URL router for the whole project
│   ├── utils/
│   │   └── toast.py                # Helper for toast redirect/messaging utilities
│   ├── views.py                    # Home view
│   └── wsgi.py                     # WSGI config
│
├── README.md
├── flake8_report/                  # Flake8 linting results + badge
│   ├── index.html
│   ├── badge.svg
│   └── styles.css
│
├── manage.py                       # Django management entry point
│
├── package.json                    # Node + Tailwind dependencies
├── package-lock.json
├── postcss.config.js               # PostCSS pipeline for Tailwind
├── tailwind.config.js              # Tailwind configuration
├── styles.css                      # Source file imported by Tailwind (input)
│
├── requirements.txt                # Python dependencies
│
├── reviews/                        # App: Tickets, Reviews, Feed
│   ├── __init__.py
│   ├── admin.py                    # Admin registrations
│   ├── apps.py
│   ├── forms.py                    # Django forms for Tickets & Reviews
│   ├── migrations/
│   ├── models.py                   # Ticket, Review, UserFollows models
│   ├── templatetags/
│   │   └── card_tags.py            # Custom template tags for displaying cards
│   ├── tests/
│   │   ├── test_forms.py
│   │   ├── test_models.py
│   │   └── test_views.py
│   ├── urls.py                     # All /flux/ URLs
│   └── views.py                    # Ticket creation, review creation, feed view
│
├── users/                          # App: Authentication and follows
│   ├── __init__.py
│   ├── admin.py                    # Custom User admin
│   ├── apps.py
│   ├── forms.py                    # RegistrationForm, LoginForm
│   ├── migrations/
│   ├── models.py                   # Custom User model
│   ├── tests/
│   │   ├── test_forms.py
│   │   └── test_views.py
│   ├── urls.py                     # /users/... URLs
│   └── views.py                    # register, login, logout, follows, posts
│
├── static/                         # Static files served by Django
│   ├── admin/                      # Django admin assets
│   ├── css/
│   │   └── tailwind.css            # Tailwind output (generated)
│   └── js/
│       ├── auth_forms.js
│       ├── header_menu.js
│       ├── ticket_form.js
│       └── toast.js
│
└── templates/                      # HTML templates
    ├── base.html                   # Root layout
    ├── home.html                   # Homepage
    ├── registration/
    │   └── register.html           # Signup page
    ├── reviews/
    │   ├── components/             # Reusable partials (ticket cards, stars, ...)
    │   ├── forms/                  # Form field partials
    │   └── pages/                  # Full pages (feed, create_ticket, create_review)
    └── users/
        └── pages/                  # User-related pages (posts, follows)

```

## Installation & Setup

#### 1. Clone the repository
1. Clone the repo
```bash
git clone https://github.com/SiRipo92/LITRevu
cd LITRevu
```
#### 2. Create and activate the virtual environment
To create:
```bash
python3 -m venv .venv
```

To activate:
- If using MacOS/Linux
```bash
source venv/bin/activate
```
- If using Windows
```bash
venv\Scripts\activate
```
#### 3. Install backend dependencies
```bash
pip install -r requirements.txt
```

### Backend setup
#### 4. Apply database migrations
```bash
python manage.py migrate
```

#### 5. Run the Django development server
```bash
python manage.py runserver
```

### Frontend (Tailwind CSS) Setup (Terminal 2)
#### 6. Install Node.js dependencies
*(Only needed the first time on a new machine)*

Since package.json is at the project root:
```bash
npm install
```

#### 7. Run Tailwind CSS in development mode
This watches your files and rebuilds static/css/tailwind.css:
```bash
npx tailwindcss -i ./styles.css -o ./static/css/tailwind.css --watch
```

The generated CSS goes here:
```
static/css/tailwind.css   ← compiled output (never edited manually)
```

## Production Notes
+ In production, you do NOT need Tailwind running in watch mode. 
+ You can run a one-time build before deploying:
    ```bash
    npx tailwindcss -i ./styles.css -o ./static/css/tailwind.css --minify
    ```
  After that:
  + Django will serve the compiled CSS from /static/css/ 
  + Node.js is not required on the production server.

## 🧑‍💻 Development Notes

+ **Linting (backend)**
  ```bash
  flake8 .
  ```
+ **Tailwind/CSS**
  + All custom styling is in `styles.css` 
  + Tailwind builds → `static/css/tailwind.css` 
  + Never modify `tailwind.css directly.


+ **HTML & CSS validated**
  + W3C HTML validator 
  + W3C CSS validator


+ **Lighthouse testing**
    + Pages audited for:
      + Accessibility 
      + Best practices 
      + SEO 
      + Performance
      

+ **Tests & Coverage**
  + Run the Django test suite (locally)
  ```bash
  python manage.py test users reviews
  ```
  + Run tests with coverage
  ```bash
  python -m coverage run --branch manage.py test users reviews
  python -m coverage report
  ```

_Last updated: 2025-11-28 (local run)_
```text
Name                                Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------------------
reviews/admin.py                       10      0      0      0   100%
reviews/apps.py                         4      0      0      0   100%
reviews/forms.py                       33      2      6      1    87%   129-130
reviews/models.py                      41      3      0      0    93%   47, 99, 114
reviews/templatetags/card_tags.py      18      1      4      1    91%   59
reviews/urls.py                         4      0      0      0   100%
reviews/views.py                      119     18     32      8    80%   57-60, 70, 111->120, 113->115, 120->127, 166, 173-179, 195->210, 232-241
users/admin.py                         10      0      0      0   100%
users/apps.py                           4      0      0      0   100%
users/forms.py                         21      0      0      0   100%
users/models.py                        14      1      0      0    93%   42
users/urls.py                           4      0      0      0   100%
users/views.py                         75      5     20      1    94%   130-133, 143
-------------------------------------------------------------------------------
TOTAL                                 357     30     62     11    89%

3 empty files skipped.
```

## License
This project is licensed under the 
[Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](https://creativecommons.org/licenses/by-nc-nd/4.0/).

© 2025 Sierra Ripoche — All rights reserved for educational use.