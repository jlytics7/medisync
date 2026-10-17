# 💊 MediSync — Pharmacy Management System

A web-based pharmacy management system built with **Flask** and **MySQL**. It helps pharmacy staff track medicine inventory, watch stock levels and expiry dates, and record purchases.

## ✨ Features

- 🔐 Staff login & registration (Pharmacist / Pharmacist Assistant)
- 📊 Dashboard overview — total medicines, in stock, low stock, out of stock, expired
- 📦 Inventory with live search by name or category
- ➕ Add, edit, and delete medicines — with a safeguard that blocks deleting items that already have purchase records
- 🛒 Record purchases with automatic stock deduction
- 🕓 Purchase history with search
- ⚠️ Automatic low-stock (< 10 units) and expiry alerts

## 🛠 Tech Stack

- **Backend:** Python, Flask
- **Database:** MySQL (`mysql-connector-python`)
- **Frontend:** HTML & CSS via Jinja2 templates, Boxicons icons

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- MySQL Server 8+

### Setup

1. Clone the repository

   ```bash
   git clone https://github.com/jlytics7/medisync.git
   cd medisync
   ```

2. Create and activate a virtual environment

   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   # source venv/bin/activate # macOS / Linux
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Create the database (schema + demo data)

   ```bash
   mysql -u root -p < schema.sql
   ```

5. Configure your environment — copy `.env.example` to `.env` and fill in your values

   ```
   SECRET_KEY=your-long-random-secret
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your-mysql-password
   DB_NAME=pharmacy_db
   ```

6. Run the app

   ```bash
   python app.py
   ```

   Then open <http://127.0.0.1:5000>

### Demo login

| Category   | ID Number  |
| ---------- | ---------- |
| Pharmacist | PH-2025-001 |

## 📁 Project Structure

```
medisync/
├── app.py             # Flask routes and application logic
├── schema.sql         # Database schema + demo data
├── requirements.txt   # Python dependencies
├── .env.example       # Template for environment variables
├── templates/         # Jinja2 HTML templates
└── static/            # Stylesheets
```

## 🔒 Security Notes

- Database credentials and the Flask secret key are loaded from environment
  variables (`.env`), which is git-ignored — no secrets in the source code.
- Built for learning purposes; login is a simple category + ID number check.

---

© 2025 Medisync Pharmacy
