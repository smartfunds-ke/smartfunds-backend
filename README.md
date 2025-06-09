# SmartFunds KE – Backend

This is the backend API for the **SmartFunds KE** platform — a decentralized fund management system for handling CDF, Bursary, and Government disbursements in a transparent way using Smart Contracts, Django, and Africastalking.

---

## ⚙️ Tech Stack

- **Python 3.11+**
- **Django 4.x**
- **Django REST Framework**
- **PostgreSQL**
- **Celery + Redis**
- **Web3.py** for smart contract interaction
- **Africastalking** for SMS + USSD

---

## 🧩 Features

- JWT Authentication with role-based access
- Smart contract interaction using Web3.py
- Application lifecycle: Apply → Review → Approve → Disburse
- Transaction hash logging
- SMS Notifications (e.g., Application approved, Funds sent)
- USSD support for non-smartphone access

---

## 🧪 Local Setup

```bash
git clone https://github.com/smartfunds-ke/smartfunds-backend.git
cd smartfunds-backend

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Update database and AT credentials in .env

python manage.py migrate
python manage.py runserver
```

---

## 🐳 Docker (Optional)

```bash
docker-compose up --build
```

---

## 📂 Core Apps

| App         | Responsibility                                |
| ----------- | --------------------------------------------- |
| `accounts`  | Auth, groups, roles (citizen, officer, admin) |
| `funds`     | Fund applications, statuses, logs             |
| `contracts` | Web3 triggers, disbursement logic             |
| `api`       | Aggregated URL dispatcher                     |
| `core`      | Core utilities, settings, common logic        |
| `notifications` | SMS/USSD handlers, Africastalking integration |

---

## 🔐 Roles

| Role           | Description                           |
| -------------- | ------------------------------------- |
| `citizen`      | Applies for funds via USSD or web     |
| `fund_officer` | Reviews and approves                  |
| `fund_admin`   | Final approver, triggers disbursement |
| `superadmin`   | Org-wide full access                  |

---

## 📬 SMS/USSD

- Handled via **Africastalking Webhooks**
- USSD sessions persist using Redis (or fallback cache)

---

## 🧾 License

MIT License — For public good / civic tech use.
