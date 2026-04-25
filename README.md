

# 💊 Smart Medicine Inventory & Order Management System

A full-stack web application built with **Python Flask** that supports both **online** and **offline (phone-based)** medicine ordering. Features dual-role authentication, real-time stock tracking, PDF bill generation, and a modern responsive UI with dark mode.

---

## 🚀 Features

### 🔐 Authentication
- **Dual Role System:** User & Admin with separate dashboards
- **Secure Login/Signup** with session management
- **Show/Hide Password Toggle** on all password fields
- **Profile Management:** Edit personal details, change password

### 🛒 Ordering System
- **Online Ordering:** Browse medicines, place orders with quantity & address
- **Offline Order Entry:** Admin manually records phone orders for non-internet users
- **Order Tracking:** Real-time status updates (Pending → Processing → Completed)
- **Order History:** Users view all past orders with details

### 📦 Inventory Management
- **Add/Update Stock:** Admin manages medicine inventory
- **Low Stock Alerts:** Automatic warnings when stock drops below minimum
- **Stock Status Indicators:** Visual badges (In Stock, Low Stock, Out of Stock)

### 📄 PDF Bill Generation
- **Professional Invoices:** Company branding, customer details, itemized billing
- **Auto-generation:** Admin generates bills with one click
- **Download & Preview:** Both admin and users can download/view bills
- **Invoice Numbering:** Sequential invoice numbers (INV-0001 format)

### ⭐ Rating & Reviews
- **5-Star Rating System:** Users rate medicines after order completion
- **Written Reviews:** Optional comments with ratings
- **Admin Review Panel:** View all user feedback in admin dashboard

### 🎨 UI/UX Features
- **Dark/Light Theme Toggle** with persistent local storage
- **Responsive Design:** Works on mobile, tablet, and desktop
- **Card-based Layout:** Modern, clean interface
- **Interactive Elements:** Hover effects, animations, transitions
- **Flash Messages:** Auto-dismiss notifications with color coding
- **Settings Dropdown:** Clean navigation with profile access

### 👤 User Profile
- **Dashboard Stats:** Total orders, spending, pending/completed counts
- **Order History Table:** Complete order list with status badges
- **Rating Section:** View submitted ratings and reviews
- **Bill Downloads:** Access all generated bills

### 🛡️ Admin Profile
- **System Overview:** Total users, medicines, orders, revenue
- **Low Stock Warnings:** Quick access to inventory issues
- **Recent Orders:** Latest 5 orders for quick monitoring
- **User Ratings Feed:** Latest customer reviews
- **Quick Actions:** Direct links to stock management

### 🔔 Notification System
- **Real-time Updates:** Order status changes trigger notifications
- **Bill Ready Alerts:** Users notified when bills are generated
- **Unread/Read Status:** Visual indicators for new notifications

---

## 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| **Backend** | Python 3.12, Flask 3.1 |
| **Frontend** | HTML5, CSS3 (Custom properties), JavaScript (ES6+) |
| **Database** | SQLite (with foreign keys & constraints) |
| **PDF Library** | ReportLab 4.2 |
| **Icons** | Unicode Emoji (no external dependencies) |
| **Fonts** | Google Fonts - Poppins |

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.x installed
- pip (Python package manager)
- Git (optional, for cloning)

### Option 1: GitHub Codespaces (Recommended - No Installation)
```bash
# 1. Create a GitHub repo and open in Codespaces
# 2. In terminal, install dependencies:
pip install flask reportlab

# 3. Run the application:
python app.py

# 4. Click the PORTS tab, find port 5000, click globe icon 🌐
```

### Option 2: Local Windows/Mac/Linux
```bash
# 1. Clone the repository (or download ZIP)
git clone <your-repo-url>
cd smart-medicine-system

# 2. Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install flask reportlab

# 4. Run the application
python app.py

# 5. Open browser: http://127.0.0.1:5000
```

---

## 🔑 Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin` | `admin123` |
| **User** | Sign up to create your own account | |

---

## 📁 Project Structure

```
smart-medicine-system/
│
├── app.py                       # Main Flask application (all routes & logic)
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
├── medicine.db                  # SQLite database (auto-created)
│
├── templates/                   # HTML templates (Jinja2)
│   ├── base.html                # Master template (navbar, footer, theme)
│   ├── index.html               # Landing page
│   ├── about.html               # About us page
│   ├── how_to_order.html        # Ordering guide (online + offline)
│   ├── login.html               # Login with password toggle
│   ├── signup.html              # Registration form
│   ├── medicines.html           # Browse & order medicines
│   ├── user_dashboard.html      # User order tracking
│   ├── user_profile.html        # User profile & ratings
│   ├── admin_dashboard.html     # Admin panel with offline orders
│   ├── admin_profile.html       # Admin system overview
│   ├── admin_stock.html         # Stock management
│   ├── admin_notifications.html # Notification center
│   ├── edit_profile.html        # Edit user details
│   ├── change_password.html     # Password change form
│   └── rate_medicine.html       # Star rating form
│
├── static/                      # Static assets
│   ├── css/
│   │   └── style.css            # All styles + dark mode + animations
│   └── js/
│       └── script.js            # Theme toggle, password visibility, stars
│
└── bills/                       # Generated PDF bills (auto-created)
    └── order_*.pdf
```

---

## 🗄️ Database Schema

### Tables:
1. **users** - User accounts with roles (user/admin)
2. **medicines** - Medicine inventory with stock tracking
3. **orders** - All orders (online + offline) with status
4. **notifications** - User notification system
5. **ratings** - Medicine ratings and reviews

---

## 🎯 Key Learning Outcomes

This project demonstrates:

| Skill | Implementation |
|-------|---------------|
| **Authentication** | Session-based login with role-based access control |
| **CRUD Operations** | Create, Read, Update, Delete across 5 database tables |
| **PDF Generation** | Professional invoice creation with ReportLab |
| **Responsive Design** | Custom CSS with CSS variables, flexbox, grid |
| **Dark Mode** | Theme persistence using localStorage |
| **Form Validation** | Client-side + server-side validation |
| **Relational Database** | Foreign keys, constraints, JOIN queries |
| **UI/UX Design** | Card layouts, badges, animations, hover effects |
| **Real-world Features** | Offline ordering, ratings, notifications |

---
##screenshots:
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/7cd8ce4a-5387-4f12-92ed-7295f383d480" />
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/249ce13e-e0cc-47b5-88e1-6146d7b14e6b" />
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/f78886e0-01e4-4aed-9d6f-40f6c16780c9" />
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/e5a231e4-cd42-44ca-bf07-3f6e70c6460c" />
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/cc840fef-d5f6-4ea1-8e9f-ef634c053061" />
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/eb889957-b1e3-4e64-acd8-8b50ca31a8b2" />


## 🚀 Future Enhancements (Ideas)

- [ ] Email notifications via Flask-Mail
- [ ] Medicine search & filter functionality
- [ ] Order pagination for large datasets
- [ ] Admin analytics dashboard with charts (Chart.js)
- [ ] Print bill button (window.print)
- [ ] SMS notifications for offline orders
- [ ] Reset password via email
- [ ] Medicine categories & tags
- [ ] Export orders to Excel/CSV
- [ ] Deploy to Render.com or PythonAnywhere

---

## 📝 License

This project is created for educational and portfolio purposes. Feel free to use, modify, and learn from it!

---

## 👨‍💻 About This Project

Built as a **full-stack portfolio project** showcasing:
- Python Flask backend development
- Database design & SQL
- Frontend development (HTML, CSS, JavaScript)
- PDF document generation
- User experience design
- Real-world problem solving

**Perfect for:** Beginner developers learning full-stack development, internship applications, and understanding how real-world web applications work.

---

## 🙏 Acknowledgments

- Flask Documentation
- ReportLab User Guide
- CSS-Tricks for responsive design patterns
- SQLite Documentation

---

**⭐ If you found this project helpful, give it a star on GitHub!**
