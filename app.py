from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask import send_file
from functools import wraps
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey_123456'  # Change in production

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect('medicine.db')
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        name TEXT,
        email TEXT,
        phone TEXT,
        address TEXT
    )''')
    # Medicines table
    c.execute('''CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 0,
        min_stock INTEGER DEFAULT 5
    )''')
    # Orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        medicine_id INTEGER,
        customer_name TEXT,
        quantity INTEGER NOT NULL,
        phone TEXT,
        address TEXT,
        status TEXT DEFAULT 'pending',
        is_offline_order INTEGER DEFAULT 0,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        bill_path TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (medicine_id) REFERENCES medicines(id)
    )''')
    # Notifications table
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    # Insert default admin if not exists
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
                  ('admin', 'admin123', 'admin', 'System Admin'))

    
    c.execute('''CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        medicine_id INTEGER NOT NULL,
        order_id INTEGER,
        rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (medicine_id) REFERENCES medicines(id),
        FOREIGN KEY (order_id) REFERENCES orders(id)
    )''')
    

    conn.commit()
    conn.close()

def query_db(query, args=(), one=False):
    conn = sqlite3.connect('medicine.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# ---------- DECORATORS ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ---------- PUBLIC ROUTES ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/how-to-order')
def how_to_order():
    return render_template('how_to_order.html')

@app.route('/medicines')
def medicines():
    meds = query_db("SELECT * FROM medicines WHERE quantity > 0")
    return render_template('medicines.html', medicines=meds)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = query_db("SELECT * FROM users WHERE username=? AND password=?",
                        [username, password], one=True)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['name'] = user['name']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_data = {
            'username': request.form['username'],
            'password': request.form['password'],
            'name': request.form['name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'address': request.form['address']
        }
        try:
            query_db("INSERT INTO users (username, password, role, name, email, phone, address) VALUES (?, ?, ?, ?, ?, ?, ?)",
                     [user_data['username'], user_data['password'], 'user',
                      user_data['name'], user_data['email'],
                      user_data['phone'], user_data['address']])
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists', 'error')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# ---------- USER ROUTES ----------
@app.route('/dashboard')
@login_required
def dashboard():
    if session['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    # User dashboard data
    user_orders = query_db("""
        SELECT o.*, m.name as medicine_name, m.price
        FROM orders o
        JOIN medicines m ON o.medicine_id = m.id
        WHERE o.user_id=? AND o.is_offline_order=0
        ORDER BY o.order_date DESC
    """, [session['user_id']])
    notifications = query_db("""
        SELECT * FROM notifications
        WHERE user_id=? AND is_read=0
        ORDER BY created_at DESC
    """, [session['user_id']])
    return render_template('user_dashboard.html',
                           orders=user_orders,
                           notifications=notifications)

@app.route('/order', methods=['POST'])
@login_required
def place_order():
    medicine_id = request.form['medicine_id']
    quantity = int(request.form['quantity'])
    phone = request.form['phone']
    address = request.form['address']

    # Check stock
    med = query_db("SELECT * FROM medicines WHERE id=?", [medicine_id], one=True)
    if med['quantity'] < quantity:
        flash('Insufficient stock', 'error')
        return redirect(url_for('medicines'))

    # Create order
    query_db("""INSERT INTO orders (user_id, medicine_id, customer_name, quantity, phone, address)
                VALUES (?, ?, ?, ?, ?, ?)""",
             [session['user_id'], medicine_id, session['name'], quantity, phone, address])

    # Update stock
    query_db("UPDATE medicines SET quantity = quantity - ? WHERE id=?",
             [quantity, medicine_id])

    # Create notification for user
    query_db("""INSERT INTO notifications (user_id, message)
                VALUES (?, ?)""",
             [session['user_id'], f"Order placed for {med['name']} x{quantity}"])

    flash('Order placed successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/mark-notification-read/<int:notif_id>')
@login_required
def mark_notification_read(notif_id):
    query_db("UPDATE notifications SET is_read=1 WHERE id=? AND user_id=?",
             [notif_id, session['user_id']])
    return redirect(url_for('dashboard'))

# ---------- ADMIN ROUTES ----------
@app.route('/admin')
@admin_required
def admin_dashboard():
    # All orders (online + offline)
    all_orders = query_db("""
        SELECT o.*, m.name as medicine_name, m.price
        FROM orders o
        JOIN medicines m ON o.medicine_id = m.id
        ORDER BY o.order_date DESC
    """)
    # Low stock items
    low_stock = query_db("""
        SELECT * FROM medicines WHERE quantity <= min_stock
    """)
    # 👇 ADD THIS LINE - Get all medicines for the offline order dropdown
    medicines = query_db("SELECT * FROM medicines ORDER BY name")
    
    return render_template('admin_dashboard.html',
                           orders=all_orders,
                           low_stock=low_stock,
                           medicines=medicines)  # 👈 Pass medicines to template


@app.route('/admin/stock', methods=['GET', 'POST'])
@admin_required
def admin_stock():
    if request.method == 'POST':
        # Add or update medicine
        med_data = {
            'name': request.form['name'],
            'description': request.form['description'],
            'price': float(request.form['price']),
            'quantity': int(request.form['quantity']),
            'min_stock': int(request.form['min_stock'])
        }
        # Check if medicine exists
        existing = query_db("SELECT * FROM medicines WHERE name=?",
                            [med_data['name']], one=True)
        if existing:
            query_db("""UPDATE medicines
                        SET description=?, price=?, quantity=quantity+?, min_stock=?
                        WHERE name=?""",
                     [med_data['description'], med_data['price'],
                      med_data['quantity'], med_data['min_stock'],
                      med_data['name']])
            flash(f"Updated stock for {med_data['name']}", 'success')
        else:
            query_db("""INSERT INTO medicines (name, description, price, quantity, min_stock)
                        VALUES (?, ?, ?, ?, ?)""",
                     [med_data['name'], med_data['description'],
                      med_data['price'], med_data['quantity'],
                      med_data['min_stock']])
            flash(f"Added new medicine: {med_data['name']}", 'success')
        return redirect(url_for('admin_stock'))

    all_meds = query_db("SELECT * FROM medicines ORDER BY name")
    return render_template('admin_stock.html', medicines=all_meds)

@app.route('/admin/offline-order', methods=['POST'])
@admin_required
def offline_order():
    order_data = {
        'customer_name': request.form['customer_name'],
        'medicine_id': request.form['medicine_id'],
        'quantity': int(request.form['quantity']),
        'phone': request.form['phone'],
        'address': request.form['address']
    }
    # Check stock
    med = query_db("SELECT * FROM medicines WHERE id=?",
                   [order_data['medicine_id']], one=True)
    if med['quantity'] < order_data['quantity']:
        flash('Insufficient stock', 'error')
        return redirect(url_for('admin_dashboard'))

    # Create offline order (user_id = 0 for offline)
    query_db("""INSERT INTO orders (user_id, medicine_id, customer_name, quantity, phone, address, is_offline_order)
                VALUES (?, ?, ?, ?, ?, ?, 1)""",
             [0, order_data['medicine_id'], order_data['customer_name'],
              order_data['quantity'], order_data['phone'], order_data['address']])

    # Update stock
    query_db("UPDATE medicines SET quantity = quantity - ? WHERE id=?",
             [order_data['quantity'], order_data['medicine_id']])

    flash(f"Offline order recorded for {order_data['customer_name']}", 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/notifications')
@admin_required
def admin_notifications():
    # Show all notifications with user info
    all_notifs = query_db("""
        SELECT n.*, u.name as user_name
        FROM notifications n
        LEFT JOIN users u ON n.user_id = u.id
        ORDER BY n.created_at DESC
    """)
    return render_template('admin_notifications.html', notifications=all_notifs)

@app.route('/admin/update-order-status/<int:order_id>', methods=['POST'])
@admin_required
def update_order_status(order_id):
    new_status = request.form['status']
    query_db("UPDATE orders SET status=? WHERE id=?", [new_status, order_id])

    # Get order details for notification
    order = query_db("""
        SELECT o.*, m.name as medicine_name
        FROM orders o
        JOIN medicines m ON o.medicine_id = m.id
        WHERE o.id=?
    """, [order_id], one=True)

    if order and order['user_id'] != 0:
        query_db("""INSERT INTO notifications (user_id, message)
                    VALUES (?, ?)""",
                 [order['user_id'],
                  f"Order #{order_id} ({order['medicine_name']}) is now {new_status}"])

    flash(f"Order #{order_id} status updated to {new_status}", 'success')
    return redirect(url_for('admin_dashboard'))

# ---------- ENHANCED PDF BILL GENERATION ----------
@app.route('/admin/generate-bill/<int:order_id>')
@admin_required
def generate_bill(order_id):
    order = query_db("""
        SELECT o.*, m.name as medicine_name, m.price, m.description as medicine_description
        FROM orders o
        JOIN medicines m ON o.medicine_id = m.id
        WHERE o.id=?
    """, [order_id], one=True)

    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('admin_dashboard'))

    # Create PDF with professional layout
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Color scheme (dark blue header)
    header_color = (0.14, 0.27, 0.48)  # #24467A
    accent_color = (0.23, 0.51, 0.96)  # #3B82F6
    text_color = (0.12, 0.16, 0.22)    # #1E293B
    
    # ---------- HEADER BAR ----------
    c.setFillColorRGB(*header_color)
    c.rect(0, height - 100, width, 100, fill=True, stroke=False)
    
    # Company logo & name
    c.setFillColorRGB(1, 1, 1)  # White text
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 45, "SMART MEDICINE INVENTORY")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 65, "Trusted Medicine Delivery | Online & Offline Orders")
    c.drawString(50, height - 80, "📞 +91 1234567890 | 📧 support@smartmeds.com")
    
    # ---------- BILL TITLE ----------
    c.setFillColorRGB(*text_color)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(50, height - 130, f"TAX INVOICE / BILL")
    
    # Horizontal line
    c.setStrokeColorRGB(*accent_color)
    c.setLineWidth(2)
    c.line(50, height - 138, width - 50, height - 138)
    
    # ---------- BILL DETAILS (Right side) ----------
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    x_right = width - 200
    
    c.drawString(x_right, height - 130, f"Bill No: INV-{order['id']:04d}")
    c.drawString(x_right, height - 145, f"Date: {order['order_date'][:10] if order['order_date'] else 'N/A'}")
    c.drawString(x_right, height - 160, f"Order Type: {'Offline (Phone)' if order['is_offline_order'] else 'Online'}")
    
    # ---------- CUSTOMER DETAILS ----------
    y_pos = height - 180
    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(*text_color)
    c.drawString(50, y_pos, "CUSTOMER DETAILS")
    c.setFont("Helvetica", 11)
    c.drawString(50, y_pos - 25, f"Name: {order['customer_name']}")
    c.drawString(50, y_pos - 45, f"Phone: {order['phone']}")
    c.drawString(50, y_pos - 65, f"Address: {order['address']}")
    
    # ---------- ORDER TABLE ----------
    y_pos = y_pos - 110
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_pos, "ORDER DETAILS")
    
    # Table header
    y_pos -= 30
    table_header_bg = (0.95, 0.95, 0.95)
    c.setFillColorRGB(*table_header_bg)
    c.rect(50, y_pos - 5, width - 100, 20, fill=True, stroke=False)
    
    c.setFillColorRGB(*text_color)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(60, y_pos, "Medicine")
    c.drawString(250, y_pos, "Description")
    c.drawString(380, y_pos, "Qty")
    c.drawString(430, y_pos, "Unit Price")
    c.drawString(500, y_pos, "Total")
    
    # Table row
    y_pos -= 22
    c.setFont("Helvetica", 10)
    c.drawString(60, y_pos, order['medicine_name'])
    c.drawString(250, y_pos, order['medicine_description'] or 'N/A')
    c.drawString(380, y_pos, str(order['quantity']))
    
    # Format currency
    unit_price = f"₹{order['price']:.2f}"
    total_amount = order['price'] * order['quantity']
    c.drawString(430, y_pos, unit_price)
    c.drawString(500, y_pos, f"₹{total_amount:.2f}")
    
    # Table bottom line
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(50, y_pos - 5, width - 50, y_pos - 5)
    
    # ---------- TOTAL SECTION ----------
    y_pos -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y_pos, "SUB TOTAL:")
    c.drawString(500, y_pos, f"₹{total_amount:.2f}")
    
    y_pos -= 20
    c.drawString(400, y_pos, "TAX (0%):")
    c.drawString(500, y_pos, "₹0.00")
    
    y_pos -= 25
    c.setStrokeColorRGB(*accent_color)
    c.setLineWidth(1)
    c.line(400, y_pos, 550, y_pos)
    
    y_pos -= 20
    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(*accent_color)
    c.drawString(400, y_pos, "TOTAL AMOUNT:")
    c.drawString(500, y_pos, f"₹{total_amount:.2f}")
    
    # ---------- ORDER STATUS ----------
    y_pos -= 50
    c.setFillColorRGB(*text_color)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_pos, f"ORDER STATUS: {order['status'].upper()}")
    
    status_badge_bg = None
    if order['status'] == 'completed':
        status_badge_bg = (0.07, 0.65, 0.36)  # Green
    elif order['status'] == 'processing':
        status_badge_bg = (0.23, 0.51, 0.96)  # Blue
    elif order['status'] == 'pending':
        status_badge_bg = (0.96, 0.75, 0.05)  # Yellow
    else:
        status_badge_bg = (0.93, 0.25, 0.22)  # Red
        
    if status_badge_bg:
        c.setFillColorRGB(*status_badge_bg)
        c.rect(230, y_pos - 3, 80, 16, fill=True, stroke=False)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(240, y_pos, order['status'].upper())
    
    # ---------- FOOTER ----------
    y_pos = 80
    c.setStrokeColorRGB(0.9, 0.9, 0.9)
    c.line(50, y_pos + 20, width - 50, y_pos + 20)
    
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Helvetica", 8)
    c.drawString(50, y_pos, "Thank you for choosing Smart Medicine Inventory!")
    c.drawString(50, y_pos - 15, "This is a computer-generated bill and does not require a physical signature.")
    c.drawString(50, y_pos - 30, "For any queries, contact: support@smartmeds.com | 📞 +91 1234567890")
    
    # Terms
    c.setFont("Helvetica-Oblique", 7)
    c.drawString(50, y_pos - 55, "Terms: 1. Medicines once sold cannot be returned. 2. Prices are inclusive of all taxes. 3. Delivery timeline: 24-48 hours.")
    
    # ---------- SAVE PDF ----------
    c.save()
    buffer.seek(0)

    # Create bills directory if not exists
    os.makedirs("bills", exist_ok=True)
    bill_filename = f"order_{order_id}_bill.pdf"
    bill_path = os.path.join("bills", bill_filename)
    
    with open(bill_path, 'wb') as f:
        f.write(buffer.read())
    
    # Update database with bill path
    query_db("UPDATE orders SET bill_path=? WHERE id=?", [bill_path, order_id])

    # Notify user if this is an online order
    if order['user_id'] != 0:
        query_db("""INSERT INTO notifications (user_id, message)
                    VALUES (?, ?)""",
                 [order['user_id'], 
                  f"📄 Bill generated for Order #{order['id']} ({order['medicine_name']}). Total: ₹{total_amount:.2f}"])

    flash(f'✅ Bill generated successfully for Order #{order_id}!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/download-bill/<int:order_id>')
@admin_required
def download_bill(order_id):
    """Download generated bill PDF"""
    bill_path = os.path.join("bills", f"order_{order_id}_bill.pdf")
    if os.path.exists(bill_path):
        return send_file(
            bill_path, 
            as_attachment=True,
            download_name=f'SmartMeds_Invoice_Order_{order_id}.pdf',
            mimetype='application/pdf'
        )
    else:
        flash('❌ Bill not found. Please generate the bill first.', 'error')
        return redirect(url_for('admin_dashboard'))


@app.route('/user/download-bill/<int:order_id>')
@login_required
def user_download_bill(order_id):
    """Allow users to download their own bills"""
    # Verify this order belongs to the logged-in user
    order = query_db("SELECT * FROM orders WHERE id=? AND user_id=?", 
                     [order_id, session['user_id']], one=True)
    
    if not order:
        flash('❌ Unauthorized access or order not found.', 'error')
        return redirect(url_for('dashboard'))
    
    bill_path = order['bill_path']
    if bill_path and os.path.exists(bill_path):
        return send_file(
            bill_path,
            as_attachment=True,
            download_name=f'SmartMeds_Order_{order_id}_Bill.pdf',
            mimetype='application/pdf'
        )
    else:
        flash('❌ Bill not yet generated. Please wait for admin to generate it.', 'error')
        return redirect(url_for('dashboard'))


@app.route('/admin/preview-bill/<int:order_id>')
@admin_required
def preview_bill(order_id):
    """Preview bill in browser before downloading"""
    bill_path = os.path.join("bills", f"order_{order_id}_bill.pdf")
    if os.path.exists(bill_path):
        return send_file(
            bill_path,
            mimetype='application/pdf',
            as_attachment=False  # View in browser
        )
    else:
        flash('❌ Bill not found. Generate it first.', 'error')
        return redirect(url_for('admin_dashboard'))


# ==========================================
# PROFILE ROUTES (USER & ADMIN)
# ==========================================

@app.route('/profile')
@login_required
def profile():
    """Redirect to appropriate profile based on role"""
    if session['role'] == 'admin':
        return redirect(url_for('admin_profile'))
    else:
        return redirect(url_for('user_profile'))


@app.route('/user/profile')
@login_required
def user_profile():
    """User profile with order history and stats"""
    # Get user details
    user = query_db("SELECT * FROM users WHERE id=?", [session['user_id']], one=True)
    
    # Get all orders with medicine details
    orders = query_db("""
        SELECT o.*, m.name as medicine_name, m.price, m.id as medicine_id
        FROM orders o
        JOIN medicines m ON o.medicine_id = m.id
        WHERE o.user_id=? AND o.is_offline_order=0
        ORDER BY o.order_date DESC
    """, [session['user_id']])
    
    # Calculate stats
    total_orders = len(orders)
    total_spent = sum(o['price'] * o['quantity'] for o in orders)
    pending_orders = len([o for o in orders if o['status'] == 'pending'])
    completed_orders = len([o for o in orders if o['status'] == 'completed'])
    
    # Get user's ratings
    ratings = query_db("""
        SELECT r.*, m.name as medicine_name
        FROM ratings r
        JOIN medicines m ON r.medicine_id = m.id
        WHERE r.user_id=?
        ORDER BY r.created_at DESC
    """, [session['user_id']])
    
    return render_template('user_profile.html',
                           user=user,
                           orders=orders,
                           ratings=ratings,
                           total_orders=total_orders,
                           total_spent=total_spent,
                           pending_orders=pending_orders,
                           completed_orders=completed_orders)


@app.route('/admin/profile')
@admin_required
def admin_profile():
    """Admin profile with system statistics"""
    # Get admin details
    admin = query_db("SELECT * FROM users WHERE id=?", [session['user_id']], one=True)
    
    # System stats
    total_users = query_db("SELECT COUNT(*) as count FROM users WHERE role='user'", one=True)['count']
    total_medicines = query_db("SELECT COUNT(*) as count FROM medicines", one=True)['count']
    total_orders = query_db("SELECT COUNT(*) as count FROM orders", one=True)['count']
    total_revenue = query_db("""
        SELECT SUM(m.price * o.quantity) as revenue
        FROM orders o
        JOIN medicines m ON o.medicine_id = m.id
        WHERE o.status='completed'
    """, one=True)['revenue'] or 0
    
    # Recent orders
    recent_orders = query_db("""
        SELECT o.*, m.name as medicine_name, m.price
        FROM orders o
        JOIN medicines m ON o.medicine_id = m.id
        ORDER BY o.order_date DESC
        LIMIT 5
    """)
    
    # All ratings for review
    all_ratings = query_db("""
        SELECT r.*, u.name as user_name, m.name as medicine_name
        FROM ratings r
        JOIN users u ON r.user_id = u.id
        JOIN medicines m ON r.medicine_id = m.id
        ORDER BY r.created_at DESC
        LIMIT 10
    """)
    
    # Low stock alerts
    low_stock = query_db("SELECT * FROM medicines WHERE quantity <= min_stock")
    
    return render_template('admin_profile.html',
                           admin=admin,
                           total_users=total_users,
                           total_medicines=total_medicines,
                           total_orders=total_orders,
                           total_revenue=total_revenue,
                           recent_orders=recent_orders,
                           all_ratings=all_ratings,
                           low_stock=low_stock)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user/admin profile"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        
        query_db("""UPDATE users SET name=?, email=?, phone=?, address=? WHERE id=?""",
                 [name, email, phone, address, session['user_id']])
        
        session['name'] = name  # Update session
        flash('✅ Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    user = query_db("SELECT * FROM users WHERE id=?", [session['user_id']], one=True)
    return render_template('edit_profile.html', user=user)


@app.route('/rate-medicine/<int:order_id>', methods=['GET', 'POST'])
@login_required
def rate_medicine(order_id):
    """Rate a medicine from an order"""
    # Get order details
    order = query_db("""
        SELECT o.*, m.name as medicine_name
        FROM orders o
        JOIN medicines m ON o.medicine_id = m.id
        WHERE o.id=? AND o.user_id=?
    """, [order_id, session['user_id']], one=True)
    
    if not order:
        flash('❌ Order not found', 'error')
        return redirect(url_for('user_profile'))
    
    # Check if already rated
    existing = query_db("SELECT * FROM ratings WHERE order_id=?", [order_id], one=True)
    
    if request.method == 'POST':
        rating = int(request.form['rating'])
        comment = request.form['comment']
        
        if existing:
            # Update existing rating
            query_db("UPDATE ratings SET rating=?, comment=? WHERE id=?",
                     [rating, comment, existing['id']])
            flash('✅ Rating updated!', 'success')
        else:
            # Insert new rating
            query_db("""INSERT INTO ratings (user_id, medicine_id, order_id, rating, comment)
                        VALUES (?, ?, ?, ?, ?)""",
                     [session['user_id'], order['medicine_id'], order_id, rating, comment])
            flash('✅ Thank you for your rating!', 'success')
        
        return redirect(url_for('user_profile'))
    
    return render_template('rate_medicine.html', order=order, existing=existing)

    
# ============================================
# RUN APPLICATION (Production Ready)
# ============================================

if __name__ == '__main__':
    import os
    
    # Initialize database
    init_db()
    
    # Get port from Render environment variable
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 60)
    print("🏥 MediStock Pro - Medical Inventory System")
    print("=" * 60)
    print(f"🚀 Server starting on port {port}...")
    print(f"📍 Binding to 0.0.0.0:{port}")
    print("📱 Web Dashboard: Available after deployment")
    print("📡 REST API: /api/medicines")
    print("👤 Demo User: user / user123")
    print("👑 Demo Admin: admin / admin123")
    print("=" * 60)
    
    # Critical: host='0.0.0.0' for Render
    app.run(host='0.0.0.0', port=port, debug=False)
