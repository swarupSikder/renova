# Renova 🎉 — Event Management Web App

Live_link: https://renova-ffyl.onrender.com/

Renova is a modern Django-powered event management web application. It allows users to create, view, and manage events along with participants. Designed with Tailwind CSS for sleek styling and PostgreSQL for reliable data storage.

## 🔧 Features

- Add, edit, and delete events
- Search & filter events by category or date
- Organizer dashboard with stats
- Participant tracking
- Responsive UI with Tailwind CSS
- PostgreSQL support (Render-hosted)
- Admin panel
- Debug toolbar for development
- Faker support for test data

---

## 🚀 Tech Stack

- **Backend**: Django 5.2+
- **Frontend**: HTML, Tailwind CSS
- **Database**: PostgreSQL (Render Cloud)
- **Admin UI**: Django Admin
- **Faker**: Generate fake test data
- **pgAdmin**: Local PostgreSQL GUI
- **Render**: Hosting (app + database)


🧩 Folder Structure

renova/
│
├── config/                # Project settings
├── events/                # Core app
│   ├── models.py
│   ├── views.py
│   └── templates/events/
│
├── static/                # Static files
├── templates/             # Base templates
├── manage.py
└── requirements.txt
