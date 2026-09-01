# Touch and Solve - Micro Finance Co-operative System

A clean, minimalist, and modern Microfinance & Co-operative Management Web Application built with **Django** for **Touch and Solve**.

---

## 👥 3 Core Actors & Capabilities

### 1. 👤 Members (Cooperative Members)
- **Personal Dashboard**: View real-time savings balance, active loan status, next installment due date.
- **Savings Account**: Submit deposit requests (Cash, bKash, Nagad, Bank Transfer), request withdrawals, download full transaction history.
- **Loans**: Apply for loans with dynamic monthly installment calculator, view loan status, repayment progress bar, and comprehensive installment schedules.
- **In-App Notifications**: Real-time alerts on deposit approvals, loan approvals/rejections, disbursements, and installment receipts.

### 2. 👔 Officers (Field / Loan Staff)
- **Member Directory**: Enroll new members with automated Member ID generation (`TNS-MEM-xxxx`) and KYC/Nominee tracking.
- **Savings Management**: Record immediate cash deposits, process member deposit/withdrawal requests, approve/reject transactions.
- **Loan Portfolio**: Review loan applications, recommend/approve loans, disburse loans (which automatically generates the full amortization installment schedule), collect and record installment payments.
- **Daily Collection Sheet**: Clean bulk sheet for quick field collections.

### 3. 👑 Admin (System Owner)
- **Executive Portal**: Real-time financial monitoring (Total Liquidity, Total Disbursed Capital, Total Repayments Collected, Total Outstanding Balance, Interest Earned).
- **Officer Management**: Create and manage staff/officer accounts and permissions.
- **Loan Products**: Create and configure standard loan products, interest rates, and loan tenors.
- **Cashflow & Audit Reports**: Comprehensive cash inflow vs outflow audit trails with print-ready statements.

---

## 🚀 Getting Started

### 1. Run Migrations & Seed Database
```bash
python manage.py migrate
python seed_data.py
```

### 2. Start the Development Server
```bash
python manage.py runserver 8000
```
Then visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🔑 Demo Login Credentials

| Role | Username | Password | Dashboard URL |
| :--- | :--- | :--- | :--- |
| **Admin (Owner)** | `admin` | `admin123` | `/portal/admin/` |
| **Field Officer 1** | `officer1` | `123456` | `/portal/officer/` |
| **Field Officer 2** | `officer2` | `123456` | `/portal/officer/` |
| **Member (Rahim)** | `rahim` | `123456` | `/portal/member/` |
| **Member (Fatema)** | `fatema` | `123456` | `/portal/member/` |
| **Member (Kamal)** | `kamal` | `123456` | `/portal/member/` |

---

## 🧪 Running Automated Tests
```bash
python manage.py test
```

---

## 🛠️ Technology Stack
- **Framework**: Django 5.2 (Python 3.11)
- **Database**: SQLite (Production-ready for PostgreSQL / MySQL)
- **Styling**: Modern, responsive Custom Vanilla CSS (Design system with Plus Jakarta Sans)
- **Notifications**: Trigger-based in-app notification engine with context processor header integration
