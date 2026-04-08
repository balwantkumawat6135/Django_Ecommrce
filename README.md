# Django Stripe Payment App

## 📌 Overview
This is a Django-based web application with 3 fixed products. Users can select quantities, make payment using Stripe (test mode), and view paid orders on the same page.

---

## ⚙️ Assumptions
- No user authentication (single user flow)
- Products are fixed and hardcoded
- INR currency is used
- Single page UI (home page handles everything)

---

## 💳 Payment Flow
- User selects product quantity
- Clicks "Buy"
- Redirected to Stripe Checkout (test mode)
- After successful payment, redirected back to home page
- Paid order appears in "My Orders"

---

## 🛡️ Double Charge Prevention
- Each order uses a unique `stripe_session_id`
- Order is marked as paid only once
- Refreshing success page does not duplicate payment

---

## 🚀 Setup Instructions

```bash
git clone <repo-link>
cd project
python -m venv venv
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver


## ⏱️ Time Spent
Approximately 8 hours (including development, debugging, and testing)
