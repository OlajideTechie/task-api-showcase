# 🗂️ Task Management API – Built with Django Rest Framework

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Django](https://img.shields.io/badge/Django-REST--Framework-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 👋 About Me

I'm **Olajide Ojo**, a QA Engineer transitioning into **Backend Development**. I specialize in building practical, testable APIs and backend systems that solve real-world problems.

---

## 📌 Project Overview

This project is a backend API for managing tasks with user-based access, custom scheduling logic, and clean time validations.

> 💡 Part of my backend engineering journey, focused on building APIs that are easy to test, extend, and scale.

---

## 🚀 Key Features

- ✅ **JWT Auth** – Login, logout, refresh with token blacklisting
- ✅ **Task Management** – CRUD + toggle completion status
- ✅ **Date Guardrails** – Prevent past scheduling
- ✅ **Auto-Calculate Due Time** – Combines start time + duration
- ✅ **Swagger Docs** – Auto-generated API explorer
- ✅ **Clean Timestamps** – Consistent `YYYY-MM-DD HH:MM:SS`

---


## Repo Structure

```
task-api-showcase/
├── README.md
├── assets/
│ └── swagger_preview.png # Swagger UI screenshot
├── code_samples/
│ ├── views.py # Core task views
│ ├── serializers.py # Validation & logic
│ └── urls.py # API routing
└── LICENSE.md
```
---

## 📸 API Docs Preview

![Swagger Screenshot](/assets/swagger_preview.png)


## Run Locally

```bash
git clone https://github.com/OlajideTechie/task-api-showcase.git
cd task-api-showcase

# Set up virtual environment
python -m venv env
source env/bin/activate  # or env\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run migration
python manage.py migrate

# Start the server
python manage.py runserver
````

# Access Swagger docs at

```http://127.0.0.1:8000/swagger/```


# 🔑 Want Full Access?
This showcase highlights only selected logic. To access the full working repository:

✉️ Email me at oolajide91@gmail.com
Let’s connect on LinkedIn (https://www.linkedin.com/in/ojo-olajide/)
