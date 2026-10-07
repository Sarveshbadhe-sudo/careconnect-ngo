# AshraySeva NGO Donation Website

## Project Overview

AshraySeva NGO is a web-based NGO donation management system designed to make donating simple, organized, and transparent.

The website allows users to register, log in, choose the type of donation they want to make, select a donation date, and view their donation history. A separate administrator login provides access to a dashboard containing the complete donation history.

The project is built with HTML, CSS, JavaScript, Python Flask, and SQLite.

---

## Main Objectives

- Provide an easy online platform for making donations.
- Allow users to donate food, clothes, books, and other items.
- Allow users to record monetary donation amounts.
- Maintain donation records in a database.
- Allow users to view their own donation history.
- Allow an administrator to monitor all donations.
- Improve organization and transparency of NGO donation activities.

---

## Features

### 1. Home Page

The home page contains:

- NGO name and branding
- Donation banner
- NGO background image
- Food donation section
- Clothes donation section
- Books donation section
- Money donation section
- Login button
- Registration button
- Admin button

### 2. User Registration

New users can register using:

- Full Name
- Email Address
- Password
- Confirm Password

Passwords are hashed before being stored in the database.

### 3. User Login

Registered users can log in using:

- Email
- Password

After successful login, the user can access the donation system.

### 4. Donation System

Users can choose:

- Items
- Money
- Items + Money

For item donations, users can select:

- Food
- Clothes
- Books
- Other

Users can also enter the item quantity.

For monetary donations, the available preset amounts are:

- ₹500
- ₹1,000
- ₹2,500
- ₹5,000
- ₹10,000

The user can also:

- Select a donation date
- Add an optional message
- Submit the donation

### 5. Donation History

Users can view their previous donation records, including:

- Donation ID
- Donation type
- Item type
- Quantity
- Money amount
- Donation date
- Message

### 6. Admin Login

The website provides a separate admin login.

Demo admin credentials:

```text
Email: admin@ngo.com
Password: Admin@123
```

These credentials should be changed before real deployment.

### 7. Admin Dashboard

The administrator can view:

- Donation ID
- Donor name
- Donor email
- Donation type
- Item category
- Quantity
- Money amount
- Donation date
- Donor message

The dashboard also provides summary information such as:

- Total donations
- Total money donated
- Total item quantity

---

## Technologies Used

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- Flask

### Database

- SQLite

### Security

- Werkzeug password hashing
- Flask sessions

---

## Project Structure

For the simple three-code-file version:

```text
NGO_Project/
│
├── app.py
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── img.png
```

### `app.py`

Contains:

- Flask application
- Routes
- User registration
- User login
- Donation processing
- Database operations
- Admin login
- Admin dashboard
- Logout functionality

### `templates/index.html`

Contains the main user interface:

- Home page
- Login page
- Registration page
- Donation page
- Admin login page

### `static/style.css`

Contains the website design and styling:

- Layout
- Forms
- Buttons
- Cards
- Responsive design
- Background image
- Colors and typography

### `static/img.png`

Contains the NGO image used as the website background and donation-page image.

---

## Database

The application uses SQLite.

### Users Table

```text
id
name
email
password
```

### Donations Table

```text
id
user_id
donation_type
item_type
quantity
money
donation_date
message
```

The database is created automatically when the Flask application starts.

---

## Installation

### Step 1: Install Python

Install Python 3.10 or newer.

Check your Python version:

```bash
python --version
```

### Step 2: Install Flask

Open Command Prompt or Terminal in the project directory:

```bash
pip install flask werkzeug
```

### Step 3: Check the Project Structure

Make sure your folders are:

```text
NGO_Project/
│
├── app.py
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── img.png
```

### Step 4: Run the Application

```bash
python app.py
```

The Flask server should start at:

```text
http://127.0.0.1:5000
```

### Step 5: Open the Website

Open a web browser and go to:

```text
http://127.0.0.1:5000
```

---

## User Workflow

```text
Open Website
     |
     v
Register Account
     |
     v
Login
     |
     v
Donation Page
     |
     +------------------------+
     |          |             |
     v          v             v
   Food      Clothes       Books
     |          |             |
     +----------+-------------+
                |
                v
          Select Quantity
                |
                v
        Select Donation Date
                |
                v
          Submit Donation
                |
                v
         Donation Database
                |
                v
         User Donation History
```

Money donations can also be selected, either alone or together with item donations.

---

## Admin Workflow

```text
Admin Login
     |
     v
Admin Dashboard
     |
     +--------------------------+
     |                          |
     v                          v
Donation Summary        Donation History
     |                          |
     +-------------+------------+
                   |
                   v
             Donor Details
             Item Details
             Money Details
             Donation Date
             Message
```

---

## Security Notes

The project contains basic security features suitable for an academic or demonstration project:

- Password hashing
- Session-based login
- User authentication
- Separate admin authentication
- Database-backed donation records

For production deployment, additional security should be added, including:

- Environment variables for secret keys and credentials
- Strong admin credentials
- CSRF protection
- Secure cookies
- HTTPS
- Input validation and sanitization
- Proper role-based access control
- Database backup
- Server-side payment verification

---

## Payment Information

The current money-donation feature records the selected amount in the database.

It does not perform an actual online payment or transfer money.

For real online donations, a secure payment gateway such as Razorpay, Stripe, or another suitable provider should be integrated and verified on the server.

---

## Future Improvements

The following features can be added later:

- Real payment gateway integration
- UPI payment support
- Automatic donation receipts
- PDF receipt generation
- Email confirmation
- Admin search and filtering
- Charts and donation analytics
- Export to Excel/CSV
- User profile page
- Password reset
- Email verification
- Donation status tracking
- Production deployment

---

## Purpose of the Project

This project can be used for:

- College mini-projects
- Web development projects
- Flask learning
- Database management projects
- NGO management demonstrations
- Social-impact website prototypes

---

## Acknowledgement

The project is based on the idea that even a small contribution can create a meaningful social impact.

**Together, we can make a difference.**
