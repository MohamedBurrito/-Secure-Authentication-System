# 🛡️ Secure Authentication System (Sentinel Hub)

**Course:** Data Integrity and Authentication  
**Assignment:** #2 Secure Authentication System  

A complete, real-world secure web authentication system built with Python and Flask. This project implements advanced security practices including Two-Factor Authentication (2FA), Password Hashing, Role-Based Access Control (RBAC), and Session/Token protection.

---

## ✨ Features Implemented (Based on Requirements)

1. **User Registration & Login:** Users can register with Name, Email, Password, and Role.
2. **Password Hashing:** Passwords are never stored in plain text. We use `flask-bcrypt` for strong hashing.
3. **Two-Factor Authentication (2FA):** Integrated with Google Authenticator. Generates a Secret Key and displays a QR code using `pyotp` and `PyQRCode`.
4. **Token/Session-Based Authentication:** After successful login and 2FA, a secure session token is generated to track the logged-in user and protect routes.
5. **Role-Based Access Control (RBAC):** Exactly 3 roles implemented:
   * **Admin:** Full access (View all users, update roles, delete users).
   * **Manager:** Read-only access to user reports.
   * **User:** Access to Dashboard and Personal Profile only.
6. **Protected Routes:** Unauthorized access attempts (e.g., a User trying to access `/admin`) are strictly blocked with a custom **403 Access Denied** or **404 Restricted** UI.
7. **Clean Code & Modular Design:** Professional UI/UX, organized file structure, and clean Python backend.

---

## 🛠️ Technology Stack

* **Backend:** Python, Flask
* **Database:** SQLite (Relational DB)
* **Security & Auth:** `flask-bcrypt` (Hashing), `pyotp` (TOTP/2FA)
* **QR Generation:** `PyQRCode`, `pypng`
* **Frontend:** HTML5, CSS3 (Custom Dark Mode UI)

---

## 🚀 Installation & Setup

Follow these steps to run the project locally:

**1. Clone the repository:**
```bash
git clone https://github.com/MohamedBurrito/-Secure-Authentication-System.git
cd -Secure-Authentication-System
