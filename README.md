# Task Management API – Built with Django Rest Framework

This project is a simple yet powerful backend API that allows users to manage tasks effectively. It supports user authentication, task creation, updates, and custom scheduling logic.

> 💡 Built as part of my transition into Backend Engineering, showcasing hands-on skills with Django, DRF, and API design.

---

## 🚀 Features

- User registration & authentication
- Task CRUD (Create, Read, Update, Delete)
- Smart due-date calculation using start time and duration
- Swagger documentation included (localhost/docs/)
- Validation against past/future dates

---

## 📸 API Docs Preview

![Swagger Screenshot](swagger_preview.png)

---

## 📁 Folder Structure

```
task-api-showcase/
├── README.md
├── assets/
│   └── swagger_preview.png       # Screenshot of Swagger UI
├── code_samples/
│   ├── views.py                  # Core view methods (Task create, update)
│   ├── serializers.py            # Validation and serialization logic
│   └── urls.py                   # API endpoint definitions
└── LICENSE.md                    # MIT License
```
