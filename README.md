# Entity & Program Management System

## 📌 Overview
This is a robust web application developed to streamline the management of entities (like NGOs) and their administrative registrations. Built with Python and Flask, the system provides an efficient workflow for tracking document validity, managing physical processes, and preventing data redundancy through smart validations and automated data filling.

## 🚀 Key Features

* **Smart Record Management:** Create, read, update, and delete (CRUD) operations for Entities and their respective Registrations.
* **Expiration Tracking:** Built-in intelligent filtering system to monitor document validity, including a custom dashboard filter to alert users about registrations expiring within the next 30 days.
* **Backend Validation & Security:** Strict SQLAlchemy queries prevent the creation of duplicate records or registrations for non-existent entities, ensuring database integrity.
* **Automated Data Entry:** Integration with internal APIs (`fetch`) to auto-fill recurring data across different tables, minimizing manual input errors.
* **Custom Jinja2 Filters:** Server-side formatting to seamlessly display dates in the local format (DD/MM/YYYY) and clean raw database strings while maintaining standard formats (YYYY-MM-DD) in the backend.
* **Real-time Input Masks:** Pure JavaScript frontend masks for standard Brazilian formats (CEP/Zip Code, Landline, and Mobile Phones) to enhance User Experience (UX) and data standardization.

## 🛠️ Technologies & Tools

* **Backend:** Python, Flask
* **Database:** SQLite / SQLAlchemy (ORM)
* **Frontend:** HTML5, Bootstrap 5, Vanilla JavaScript
* **Template Engine:** Jinja2

## ⚙️ How to Run the Project

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/VictorMartins1585/DataBase-Entity-Registered-Programs.git](https://github.com/VictorMartins1585/DataBase-Entity-Registered-Programs.git)
