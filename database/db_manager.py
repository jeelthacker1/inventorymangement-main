import sqlite3
import os
import datetime
import uuid
import hashlib

class DatabaseManager:
    def __init__(self, db_path='database/inventory.db'):
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish a connection to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # This enables column access by name
        self.cursor = self.conn.cursor()
        return self.conn, self.cursor
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def commit(self):
        """Commit changes to the database"""
        if self.conn:
            self.conn.commit()
    
    def setup_database(self):
        """Create all necessary tables if they don't exist"""
        self.connect()
        
        # Create Users table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create Products table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            cost_price REAL NOT NULL,
            selling_price REAL NOT NULL,
            max_discount REAL DEFAULT 0,
            store_quantity INTEGER DEFAULT 0,
            warehouse_quantity INTEGER DEFAULT 0,
            min_stock_level INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create Product Items table (for individual items with QR codes)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            unique_id TEXT UNIQUE NOT NULL,
            qr_code_path TEXT,
            status TEXT DEFAULT 'in_store', -- in_store, sold, in_warehouse
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
        )
        ''')
        
        # Create Customers table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            gst_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create Sales table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            total_amount REAL NOT NULL,
            discount_amount REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            final_amount REAL NOT NULL,
            payment_method TEXT,
            invoice_number TEXT UNIQUE,
            include_gst BOOLEAN DEFAULT 0,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
        ''')
        
        # Create Sale Items table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_item_id INTEGER,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            discount_percentage REAL DEFAULT 0,
            total_price REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (product_item_id) REFERENCES product_items (id)
        )
        ''')
        
        # Create Repair Jobs table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS repair_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            product_description TEXT NOT NULL,
            issue_description TEXT NOT NULL,
            status TEXT DEFAULT 'pending', -- pending, in_progress, completed, delivered
            estimated_cost REAL,
            service_charge REAL DEFAULT 0,
            total_parts_cost REAL DEFAULT 0,
            final_cost REAL,
            assigned_to INTEGER,
            serial_number TEXT,
            received_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estimated_completion_date TIMESTAMP,
            notes TEXT,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (assigned_to) REFERENCES users (id)
        )
        ''')
        
        # Create Repair Parts table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS repair_parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repair_job_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            FOREIGN KEY (repair_job_id) REFERENCES repair_jobs (id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        # Create Expenses table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            date DATE NOT NULL,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
        ''')
        
        # Insert default admin user if not exists
        self.cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not self.cursor.fetchone():
            # Hash the password 'sam3804'
            hashed_password = hashlib.sha256('sam3804'.encode()).hexdigest()
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                               ('admin', hashed_password, 'admin'))
        
        # Insert default employee user if not exists
        self.cursor.execute("SELECT * FROM users WHERE username = 'employee'")
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                               ('employee', None, 'employee'))
        
        self.commit()
        self.close()
    
    # User related methods
    def authenticate_user(self, username, password=None):
        """Authenticate a user based on username and optional password"""
        self.connect()
        
        if username == 'employee' and password is None:
            # Employee login without password
            self.cursor.execute("SELECT * FROM users WHERE username = ? AND role = 'employee'", (username,))
            user = self.cursor.fetchone()
            self.close()
            return dict(user) if user else None
        
        elif password:
            # Admin login with password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
            user = self.cursor.fetchone()
            self.close()
            return dict(user) if user else None
        
        self.close()
        return None
    
    # Product related methods
    def add_product(self, product_data):
        """Add a new product to the database"""
        self.connect()
        
        self.cursor.execute('''
        INSERT INTO products (name, description, category, cost_price, selling_price, 
                            max_discount, store_quantity, warehouse_quantity, min_stock_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product_data['name'],
            product_data['description'],
            product_data['category'],
            product_data['cost_price'],
            product_data['selling_price'],
            product_data['max_discount'],
            0,  # Initial store quantity is 0
            product_data['warehouse_quantity'],
            product_data['min_stock_level']
        ))
        
        product_id = self.cursor.lastrowid
        self.commit()
        self.close()
        return product_id
    
    def update_product(self, product_id, product_data):
        """Update an existing product"""
        self.connect()
        
        self.cursor.execute('''
        UPDATE products SET 
            name = ?,
            description = ?,
            category = ?,
            cost_price = ?,
            selling_price = ?,
            max_discount = ?,
            min_stock_level = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (
            product_data['name'],
            product_data['description'],
            product_data['category'],
            product_data['cost_price'],
            product_data['selling_price'],
            product_data['max_discount'],
            product_data['min_stock_level'],
            product_id
        ))
        
        self.commit()
        self.close()
        return True
    
    def update_product_quantities(self, product_id, store_qty, warehouse_qty):
        """Update product quantities for store and warehouse"""
        self.connect()
        
        self.cursor.execute('''
        UPDATE products SET 
            store_quantity = ?,
            warehouse_quantity = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (store_qty, warehouse_qty, product_id))
        
        self.commit()
        self.close()
        return True
    
    def get_product(self, product_id):
        """Get a product by ID"""
        self.connect()
        
        self.cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = self.cursor.fetchone()
        
        self.close()
        return dict(product) if product else None
    
    def get_all_products(self):
        """Get all products"""
        self.connect()
        
        self.cursor.execute("SELECT * FROM products ORDER BY name")
        products = [dict(row) for row in self.cursor.fetchall()]
        
        self.close()
        return products
    
    def get_low_stock_products(self):
        """Get products with low stock (below min_stock_level)"""
        self.connect()
        
        self.cursor.execute('''
        SELECT * FROM products 
        WHERE store_quantity < min_stock_level OR warehouse_quantity < min_stock_level
        ORDER BY (store_quantity + warehouse_quantity) ASC
        ''')
        products = [dict(row) for row in self.cursor.fetchall()]
        
        self.close()
        return products
        
    def get_products_needing_assembly(self, threshold=5):
        """Get products that need assembly from warehouse to store
        (store quantity below threshold but warehouse has stock)"""
        self.connect()
        
        self.cursor.execute('''
        SELECT * FROM products 
        WHERE store_quantity < ? AND warehouse_quantity > 0
        ORDER BY store_quantity ASC
        ''', (threshold,))
        products = [dict(row) for row in self.cursor.fetchall()]
        
        self.close()
        return products
        
    def get_critical_stock_products(self):
        """Get products with critically low stock in both store and warehouse"""
        self.connect()
        
        self.cursor.execute('''
        SELECT * FROM products 
        WHERE store_quantity <= 2 AND warehouse_quantity <= 3
        ORDER BY (store_quantity + warehouse_quantity) ASC
        ''')
        products = [dict(row) for row in self.cursor.fetchall()]
        
        self.close()
        return products
    
    # Product Items (with QR codes) methods
    def add_product_items(self, product_id, quantity, qr_code_paths):
        """Add individual product items with QR codes"""
        self.connect()
        
        for i in range(quantity):
            # Generate a unique 12-character ID for the item
            unique_id = f"P{product_id}I{i+1}-{uuid.uuid4().hex[:8]}"
            
            self.cursor.execute('''
            INSERT INTO product_items (product_id, unique_id, qr_code_path, status)
            VALUES (?, ?, ?, ?)
            ''', (product_id, unique_id, qr_code_paths[i], 'in_store'))
        
        self.commit()
        self.close()
        return True
    
    def get_product_items(self, product_id, status='in_store'):
        """Get all items for a specific product with a given status"""
        self.connect()
        
        self.cursor.execute('''
        SELECT * FROM product_items 
        WHERE product_id = ? AND status = ?
        ORDER BY created_at
        ''', (product_id, status))
        items = [dict(row) for row in self.cursor.fetchall()]
        
        self.close()
        return items
    
    def get_product_item_by_unique_id(self, unique_id):
        """Get a product item by its unique ID (from QR code)"""
        self.connect()
        
        self.cursor.execute('''
        SELECT pi.*, p.name as product_name, p.selling_price 
        FROM product_items pi
        JOIN products p ON pi.product_id = p.id
        WHERE pi.unique_id = ?
        ''', (unique_id,))
        item = self.cursor.fetchone()
        
        self.close()
        return dict(item) if item else None
    
    def update_product_item_status(self, item_id, new_status):
        """Update the status of a product item"""
        self.connect()
        
        self.cursor.execute('''
        UPDATE product_items SET 
            status = ?
        WHERE id = ?
        ''', (new_status, item_id))
        
        self.commit()
        self.close()
        return True
    
    # Customer related methods
    def add_customer(self, customer_data):
        """Add a new customer"""
        self.connect()
        
        self.cursor.execute('''
        INSERT INTO customers (name, phone, email, address, gst_number)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            customer_data['name'],
            customer_data.get('phone', ''),
            customer_data.get('email', ''),
            customer_data.get('address', ''),
            customer_data.get('gst_number', '')
        ))
        
        customer_id = self.cursor.lastrowid
        self.commit()
        self.close()
        return customer_id
    
    def get_customer(self, customer_id):
        """Get a customer by ID"""
        self.connect()
        
        self.cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        customer = self.cursor.fetchone()
        
        self.close()
        return dict(customer) if customer else None
    
    def search_customers(self, search_term):
        """Search for customers by name or phone"""
        self.connect()
        
        search_pattern = f"%{search_term}%"
        self.cursor.execute('''
        SELECT * FROM customers 
        WHERE name LIKE ? OR phone LIKE ?
        ORDER BY name
        ''', (search_pattern, search_pattern))
        customers = [dict(row) for row in self.cursor.fetchall()]
        
        self.close()
        return customers
    
    # Sales related methods
    def create_sale(self, sale_data, sale_items):
        """Create a new sale with items"""
        self.connect()
        
        try:
            # Generate invoice number
            today = datetime.datetime.now()
            invoice_prefix = f"INV-{today.strftime('%Y%m%d')}"
            
            # Get the last invoice number for today
            self.cursor.execute('''
            SELECT MAX(invoice_number) FROM sales 
            WHERE invoice_number LIKE ?
            ''', (f"{invoice_prefix}%",))
            
            last_invoice = self.cursor.fetchone()[0]
            if last_invoice:
                invoice_num = int(last_invoice.split('-')[-1]) + 1
            else:
                invoice_num = 1
                
            invoice_number = f"{invoice_prefix}-{invoice_num:04d}"
            
            # Insert sale record
            self.cursor.execute('''
            INSERT INTO sales (
                customer_id, total_amount, discount_amount, tax_amount, 
                final_amount, payment_method, invoice_number, include_gst, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                sale_data['customer_id'],
                sale_data['total_amount'],
                sale_data['discount_amount'],
                sale_data['tax_amount'],
                sale_data['final_amount'],
                sale_data['payment_method'],
                invoice_number,
                sale_data['include_gst'],
                sale_data['created_by']
            ))
            
            sale_id = self.cursor.lastrowid
            
            # Insert sale items
            for item in sale_items:
                self.cursor.execute('''
                INSERT INTO sale_items (
                    sale_id, product_id, product_item_id, quantity, 
                    unit_price, discount_percentage, total_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    sale_id,
                    item['product_id'],
                    item.get('product_item_id'),
                    item['quantity'],
                    item['unit_price'],
                    item['discount_percentage'],
                    item['total_price']
                ))
                
                # Update product item status if applicable
                if item.get('product_item_id'):
                    self.cursor.execute('''
                    UPDATE product_items SET status = 'sold' 
                    WHERE id = ?
                    ''', (item['product_item_id'],))
                
                # Update product quantity
                self.cursor.execute('''
                UPDATE products SET 
                    store_quantity = store_quantity - ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''', (item['quantity'], item['product_id']))
            
            self.commit()
            return sale_id, invoice_number
            
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            self.close()
    
    def get_sale(self, sale_id):
        """Get a sale by ID with all its items"""
        self.connect()
        
        # Get sale details
        self.cursor.execute('''
        SELECT s.*, c.name as customer_name, c.phone as customer_phone, 
               c.address as customer_address, c.gst_number as customer_gst
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        WHERE s.id = ?
        ''', (sale_id,))
        sale = self.cursor.fetchone()
        
        if not sale:
            self.close()
            return None
        
        sale_dict = dict(sale)
        
        # Get sale items
        self.cursor.execute('''
        SELECT si.*, p.name as product_name 
        FROM sale_items si
        JOIN products p ON si.product_id = p.id
        WHERE si.sale_id = ?
        ''', (sale_id,))
        sale_dict['items'] = [dict(row) for row in self.cursor.fetchall()]
        
        self.close()
        return sale_dict
    
    def get_recent_sales(self, limit=50):
        """Get recent sales with basic information"""
        self.connect()
        
        self.cursor.execute('''
        SELECT s.*, c.name as customer_name 
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        ORDER BY s.created_at DESC
        LIMIT ?
        ''', (limit,))
        sales = [dict(row) for row in self.cursor.fetchall()]
        
        self.close()
        return sales
    
    def get_sale_items(self, sale_id):
        """Get all items for a specific sale with product details"""
        self.connect()
        
        self.cursor.execute('''
        SELECT si.*, p.name as product_name, p.category as product_category,
               si.unit_price as price, si.discount_percentage as discount,
               si.total_price as total
        FROM sale_items si
        JOIN products p ON si.product_id = p.id
        WHERE si.sale_id = ?
        ORDER BY si.id
        ''', (sale_id,))
        items = [dict(row) for row in self.cursor.fetchall()]
        
        self.close()
        return items
    
    # Repair related methods
    def create_repair_job(self, repair_data):
        """Create a new repair job"""
        self.connect()
        
        self.cursor.execute('''
        INSERT INTO repair_jobs (
            customer_id, product_description, issue_description, 
            status, estimated_cost, assigned_to, serial_number,
            received_date, estimated_completion_date, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            repair_data['customer_id'],
            repair_data['product_description'],
            repair_data['issue_description'],
            repair_data.get('status', 'pending'),
            repair_data.get('estimated_cost', 0),
            repair_data.get('assigned_to'),
            repair_data.get('serial_number', ''),
            repair_data.get('received_date', datetime.datetime.now().strftime('%Y-%m-%d')),
            repair_data.get('estimated_completion_date'),
            repair_data.get('notes', '')
        ))
        
        repair_id = self.cursor.lastrowid
        
        # Add required parts if provided
        if 'parts' in repair_data and repair_data['parts']:
            for part in repair_data['parts']:
                self.cursor.execute('''
                INSERT INTO repair_parts (
                    repair_job_id, product_id, quantity, unit_price, total_price
                ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    repair_id,
                    part['product_id'],
                    part['quantity'],
                    part['unit_price'],
                    part['quantity'] * part['unit_price']
                ))
        
        self.commit()
        self.close()
        return repair_id
    
    def add_repair(self, repair_data):
        """Add a new repair job - wrapper for create_repair_job"""
        try:
            repair_id = self.create_repair_job(repair_data)
            return repair_id is not None
        except Exception as e:
            print(f"Error adding repair: {e}")
            return False
    
    def update_repair(self, repair_id, repair_data):
        """Update an existing repair job"""
        self.connect()
        
        try:
            # Update the repair job details
            self.cursor.execute('''
            UPDATE repair_jobs SET 
                product_description = ?,
                issue_description = ?,
                estimated_cost = ?,
                assigned_to = ?,
                serial_number = ?,
                status = ?,
                received_date = ?,
                estimated_completion_date = ?,
                notes = ?
            WHERE id = ?
            ''', (
                repair_data['product_description'],
                repair_data['issue_description'],
                repair_data.get('estimated_cost', 0),
                repair_data.get('assigned_to'),
                repair_data.get('serial_number', ''),
                repair_data.get('status', 'pending'),
                repair_data.get('received_date', datetime.datetime.now().strftime('%Y-%m-%d')),
                repair_data.get('estimated_completion_date'),
                repair_data.get('notes', ''),
                repair_id
            ))
            
            # Delete existing parts for this repair
            self.cursor.execute('DELETE FROM repair_parts WHERE repair_job_id = ?', (repair_id,))
            
            # Add updated parts
            if 'parts' in repair_data and repair_data['parts']:
                for part in repair_data['parts']:
                    self.cursor.execute('''
                    INSERT INTO repair_parts (
                        repair_job_id, product_id, quantity, unit_price, total_price
                    ) VALUES (?, ?, ?, ?, ?)
                    ''', (
                        repair_id,
                        part['product_id'],
                        part['quantity'],
                        part['unit_price'],
                        part['quantity'] * part['unit_price']
                    ))
            
            self.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating repair: {e}")
            return False
        finally:
            self.close()
    
    def update_repair_status(self, repair_id, status, service_charge=None):
        """Update the status of a repair job"""
        self.connect()
        
        try:
            if status == 'completed':
                # Calculate total parts cost
                self.cursor.execute('''
                SELECT SUM(total_price) as total_parts_cost FROM repair_parts
                WHERE repair_job_id = ?
                ''', (repair_id,))
                result = self.cursor.fetchone()
                total_parts_cost = result['total_parts_cost'] if result['total_parts_cost'] else 0
                
                # Update with completion details
                self.cursor.execute('''
                UPDATE repair_jobs SET 
                    status = ?,
                    service_charge = ?,
                    total_parts_cost = ?,
                    final_cost = ?,
                    completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''', (
                    status,
                    service_charge,
                    total_parts_cost,
                    service_charge + total_parts_cost,
                    repair_id
                ))
            else:
                # Simple status update
                self.cursor.execute('''
                UPDATE repair_jobs SET status = ? WHERE id = ?
                ''', (status, repair_id))
            
            self.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating repair status: {e}")
            return False
        finally:
            self.close()
    
    def complete_repair(self, repair_id, completion_data):
        """Complete a repair job with additional completion data"""
        try:
            # Extract data from the completion_data dictionary
            status = completion_data.get('status', 'completed')
            service_charge = completion_data.get('service_charge', 0)
            
            # Update the repair status first
            success = self.update_repair_status(repair_id, status, service_charge)
            if not success:
                return False
                
            # Update notes if provided
            completion_notes = completion_data.get('completion_notes', '')
            if completion_notes:
                self.connect()
                try:
                    self.cursor.execute('''
                    UPDATE repair_jobs SET notes = ? WHERE id = ?
                    ''', (completion_notes, repair_id))
                    self.commit()
                except Exception as e:
                    self.conn.rollback()
                    print(f"Error updating repair notes: {e}")
                    return False
                finally:
                    self.close()
            
            return True
        except Exception as e:
            print(f"Error in complete_repair: {e}")
            return False
    
    def get_repair(self, repair_id):
        """Get a repair job by ID with customer details"""
        print(f"DB: Getting repair data for repair_id: {repair_id}")
        self.connect()
        
        self.cursor.execute('''
        SELECT r.*, c.name as customer_name, c.phone as customer_phone, 
               c.email as customer_email, c.address as customer_address
        FROM repair_jobs r
        LEFT JOIN customers c ON r.customer_id = c.id
        WHERE r.id = ?
        ''', (repair_id,))
        repair = self.cursor.fetchone()
        
        if repair:
            repair_dict = dict(repair)
            # Map fields for UI compatibility
            repair_dict['device'] = repair_dict['product_description']
            repair_dict['issue'] = repair_dict['issue_description']
            self.close()
            print(f"DB: Repair data found: {repair_dict}")
            return repair_dict
        
        print(f"DB: No repair data found for repair_id: {repair_id}")
        self.close()
        return None
    
    def get_repair_parts(self, repair_id):
        """Get all parts for a specific repair job"""
        print(f"DB: Getting repair parts for repair_id: {repair_id}")
        self.connect()
        
        self.cursor.execute('''
        SELECT rp.*, p.name as product_name, p.category as product_category
        FROM repair_parts rp
        JOIN products p ON rp.product_id = p.id
        WHERE rp.repair_job_id = ?
        ORDER BY rp.id
        ''', (repair_id,))
        parts = [dict(row) for row in self.cursor.fetchall()]
        
        # Add 'name' field to each part for compatibility with UI
        for part in parts:
            part['name'] = part['product_name']
            # Also add 'cost' field if it's needed but not present
            if 'cost' not in part and 'unit_price' in part:
                part['cost'] = part['unit_price']
        
        print(f"DB: Found {len(parts)} repair parts for repair_id: {repair_id}")
        if parts:
            print(f"DB: First part: {parts[0]}")
        else:
            print(f"DB: No parts found for repair_id: {repair_id}")
            # Return empty list instead of None to avoid errors in invoice generation
            parts = []
        
        self.close()
        return parts
        
    def get_all_repairs(self):
        """Get all repair jobs with customer details"""
        self.connect()
        
        self.cursor.execute('''
        SELECT r.*, c.name as customer_name, c.phone as customer_phone
        FROM repair_jobs r
        LEFT JOIN customers c ON r.customer_id = c.id
        ORDER BY r.created_at DESC
        ''')
        repairs = [dict(row) for row in self.cursor.fetchall()]
        
        # Map fields for UI compatibility
        for repair in repairs:
            repair['device'] = repair['product_description']
            repair['issue'] = repair['issue_description']
        
        self.close()
        return repairs
    
    def get_repairs_by_status(self, status):
        """Get repair jobs filtered by status"""
        self.connect()
        
        self.cursor.execute('''
        SELECT r.*, c.name as customer_name, c.phone as customer_phone
        FROM repair_jobs r
        LEFT JOIN customers c ON r.customer_id = c.id
        WHERE r.status = ?
        ORDER BY r.created_at DESC
        ''', (status,))
        repairs = [dict(row) for row in self.cursor.fetchall()]
        
        # Map fields for UI compatibility
        for repair in repairs:
            repair['device'] = repair['product_description']
            repair['issue'] = repair['issue_description']
        
        self.close()
        return repairs
    
    def get_repair_job(self, repair_id):
        """Get a repair job by ID with all its parts"""
        self.connect()
        
        # Get repair details
        self.cursor.execute('''
        SELECT r.*, c.name as customer_name, c.phone as customer_phone 
        FROM repair_jobs r
        JOIN customers c ON r.customer_id = c.id
        WHERE r.id = ?
        ''', (repair_id,))
        repair = self.cursor.fetchone()
        
        if not repair:
            self.close()
            return None
        
        repair_dict = dict(repair)
        
        # Map fields for UI compatibility
        repair_dict['device'] = repair_dict['product_description']
        repair_dict['issue'] = repair_dict['issue_description']
        
        # Get repair parts
        self.cursor.execute('''
        SELECT rp.*, p.name as product_name 
        FROM repair_parts rp
        JOIN products p ON rp.product_id = p.id
        WHERE rp.repair_job_id = ?
        ''', (repair_id,))
        parts = [dict(row) for row in self.cursor.fetchall()]
        
        # Add 'name' field to each part for compatibility with UI
        for part in parts:
            part['name'] = part['product_name']
            # Also add 'cost' field if it's needed but not present
            if 'cost' not in part and 'unit_price' in part:
                part['cost'] = part['unit_price']
                
        repair_dict['parts'] = parts
        
        self.close()
        return repair_dict
    
    def get_pending_repairs(self):
        """Get all pending and in-progress repair jobs"""
        self.connect()
        
        self.cursor.execute('''
        SELECT r.*, c.name as customer_name, c.phone as customer_phone 
        FROM repair_jobs r
        JOIN customers c ON r.customer_id = c.id
        WHERE r.status IN ('pending', 'in_progress')
        ORDER BY r.created_at
        ''')
        repairs = [dict(row) for row in self.cursor.fetchall()]
        
        # Map fields for UI compatibility
        for repair in repairs:
            repair['device'] = repair['product_description']
            repair['issue'] = repair['issue_description']
        
        self.close()
        return repairs
    
    # Expense related methods
    def add_expense(self, expense_data):
        """Add a new expense"""
        self.connect()
        
        self.cursor.execute('''
        INSERT INTO expenses (category, description, amount, date, created_by)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            expense_data['category'],
            expense_data['description'],
            expense_data['amount'],
            expense_data['date'],
            expense_data.get('created_by')
        ))
        
        expense_id = self.cursor.lastrowid
        self.commit()
        self.close()
        return expense_id
    
    def get_expenses(self, start_date=None, end_date=None, category=None):
        """Get expenses with optional filters"""
        self.connect()
        
        query = "SELECT * FROM expenses WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY date DESC"
        
        self.cursor.execute(query, params)
        expenses = [dict(row) for row in self.cursor.fetchall()]
        
        self.close()
        return expenses
    
    # Analytics methods
    def get_sales_by_period(self, period_type, start_date, end_date):
        """Get sales aggregated by day, week, or month"""
        self.connect()
        
        if period_type == 'day':
            date_format = '%Y-%m-%d'
        elif period_type == 'week':
            date_format = '%Y-%W'  # Year and week number
        elif period_type == 'month':
            date_format = '%Y-%m'
        else:
            date_format = '%Y-%m-%d'
        
        self.cursor.execute(f'''
        SELECT 
            strftime('{date_format}', created_at) as period,
            COUNT(*) as num_sales,
            SUM(total_amount) as total_sales,
            SUM(final_amount) as final_sales,
            AVG(final_amount) as avg_sale_value
        FROM sales
        WHERE created_at BETWEEN ? AND ?
        GROUP BY period
        ORDER BY period
        ''', (start_date, end_date))
        
        results = [dict(row) for row in self.cursor.fetchall()]
        self.close()
        return results
    
    def get_top_selling_products(self, start_date=None, end_date=None, limit=10):
        """Get top selling products by quantity"""
        self.connect()
        
        query = '''
        SELECT 
            p.id, p.name, p.category,
            SUM(si.quantity) as total_quantity,
            SUM(si.total_price) as total_revenue,
            COUNT(DISTINCT s.id) as num_sales
        FROM sale_items si
        JOIN products p ON si.product_id = p.id
        JOIN sales s ON si.sale_id = s.id
        '''
        
        params = []
        if start_date and end_date:
            query += "WHERE s.created_at BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        query += '''
        GROUP BY p.id
        ORDER BY total_quantity DESC
        LIMIT ?
        '''
        params.append(limit)
        
        self.cursor.execute(query, params)
        products = [dict(row) for row in self.cursor.fetchall()]
        
        self.close()
        return products
    
    def get_sales_by_category(self, start_date=None, end_date=None):
        """Get sales data grouped by product category"""
        self.connect()
        
        query = '''
        SELECT 
            p.category,
            SUM(si.total_price) as revenue,
            SUM(si.quantity * p.cost_price) as cost,
            SUM(si.quantity) as quantity_sold,
            COUNT(DISTINCT s.id) as num_sales
        FROM sale_items si
        JOIN products p ON si.product_id = p.id
        JOIN sales s ON si.sale_id = s.id
        '''
        
        params = []
        if start_date and end_date:
            query += "WHERE s.created_at BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        query += '''
        GROUP BY p.category
        ORDER BY revenue DESC
        '''
        
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        
        # Convert to dictionary with category as key
        category_data = {}
        
        # Calculate total revenue for percentage calculation
        total_revenue = sum(dict(row)['revenue'] for row in results) if results else 0
        
        for row in results:
            row_dict = dict(row)
            category = row_dict['category'] or 'Uncategorized'
            revenue = row_dict['revenue'] or 0
            cost = row_dict['cost'] or 0
            margin = revenue - cost
            
            category_data[category] = {
                'revenue': revenue,
                'cost': cost,
                'margin': margin,
                'quantity_sold': row_dict['quantity_sold'],
                'num_sales': row_dict['num_sales'],
                'percentage': (revenue / total_revenue * 100) if total_revenue > 0 else 0
            }
        
        self.close()
        return category_data
    def get_total_expenses(self, start_date=None, end_date=None):
        """Get total expenses for a given period"""
        self.connect()
        
        query = "SELECT SUM(amount) as total FROM expenses"
        params = []
        
        if start_date and end_date:
            query += " WHERE date BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        self.cursor.execute(query, params)
        result = self.cursor.fetchone()
        total = result['total'] if result and result['total'] else 0
        
        self.close()
        return total
    
    def get_non_selling_products(self, days=30, limit=10):
        """Get products that haven't sold in the specified number of days"""
        self.connect()
        
        date_threshold = datetime.datetime.now() - datetime.timedelta(days=days)
        date_str = date_threshold.strftime('%Y-%m-%d %H:%M:%S')
        
        self.cursor.execute('''
        SELECT p.* FROM products p
        WHERE p.id NOT IN (
            SELECT DISTINCT product_id FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            WHERE s.created_at >= ?
        )
        AND p.store_quantity > 0
        ORDER BY p.updated_at ASC
        LIMIT ?
        ''', (date_str, limit))
        
        products = [dict(row) for row in self.cursor.fetchall()]
        self.close()
        return products
    
    def get_profit_analysis(self, start_date=None, end_date=None):
        """Calculate profit metrics for a given period"""
        self.connect()
        
        query_params = []
        date_condition = ""
        
        if start_date and end_date:
            date_condition = "WHERE s.created_at BETWEEN ? AND ?"
            query_params.extend([start_date, end_date])
        
        # Get sales revenue and cost
        self.cursor.execute(f'''
        SELECT 
            SUM(s.final_amount) as total_revenue,
            SUM(si.quantity * p.cost_price) as total_cost,
            COUNT(DISTINCT s.id) as num_sales,
            COUNT(si.id) as num_items_sold
        FROM sales s
        JOIN sale_items si ON s.id = si.sale_id
        JOIN products p ON si.product_id = p.id
        {date_condition}
        ''', query_params)
        
        sales_data = dict(self.cursor.fetchone())
        
        # Get expenses for the same period
        expense_params = []
        expense_condition = ""
        
        if start_date and end_date:
            expense_condition = "WHERE date BETWEEN ? AND ?"
            expense_params.extend([start_date, end_date])
        
        self.cursor.execute(f'''
        SELECT 
            SUM(amount) as total_expenses,
            COUNT(*) as num_expenses
        FROM expenses
        {expense_condition}
        ''', expense_params)
        
        expense_data = dict(self.cursor.fetchone())
        
        # Combine the results
        result = {**sales_data, **expense_data}
        
        # Calculate gross and net profit
        total_revenue = result['total_revenue'] or 0
        total_cost = result['total_cost'] or 0
        total_expenses = result['total_expenses'] or 0
        
        result['gross_profit'] = total_revenue - total_cost
        result['net_profit'] = result['gross_profit'] - total_expenses
        
        if total_revenue > 0:
            result['gross_margin'] = (result['gross_profit'] / total_revenue) * 100
            result['net_margin'] = (result['net_profit'] / total_revenue) * 100
        else:
            result['gross_margin'] = 0
            result['net_margin'] = 0
        
        self.close()
        return result
        
    def get_sales_by_payment_method(self, start_date=None, end_date=None):
        """Get sales data grouped by payment method"""
        self.connect()
        
        query = '''
        SELECT 
            payment_method,
            COUNT(*) as num_sales,
            SUM(final_amount) as total_amount
        FROM sales
        '''
        
        params = []
        if start_date and end_date:
            query += "WHERE created_at BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        query += '''
        GROUP BY payment_method
        ORDER BY total_amount DESC
        '''
        
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        
        # Convert to dictionary with payment method as key
        payment_data = {}
        total_amount = 0
        
        # First calculate total amount for percentage calculation
        for row in results:
            if row['payment_method']:
                total_amount += row['total_amount'] or 0
        
        # Then process each payment method
        for row in results:
            if row['payment_method']:
                method = row['payment_method']
            else:
                method = 'Other'
                
            payment_data[method] = dict(row)
            # Calculate percentage
            if total_amount > 0:
                payment_data[method]['percentage'] = (row['total_amount'] / total_amount) * 100
            else:
                payment_data[method]['percentage'] = 0
        
        self.close()
        return payment_data
        
    def get_expenses_by_category(self, start_date=None, end_date=None):
        """Get expenses grouped by category"""
        self.connect()
        
        query = '''
        SELECT 
            category,
            COUNT(*) as num_expenses,
            SUM(amount) as total_amount
        FROM expenses
        '''
        
        params = []
        if start_date and end_date:
            query += "WHERE date BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        query += '''
        GROUP BY category
        ORDER BY total_amount DESC
        '''
        
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        
        # Convert to dictionary with category as key
        category_data = {}
        
        # Calculate total expenses for percentage calculation
        total_expenses = sum(dict(row)['total_amount'] for row in results)
        
        for row in results:
            row_dict = dict(row)
            category = row_dict['category'] or 'Uncategorized'
            category_data[category] = {
                'num_expenses': row_dict['num_expenses'],
                'total_amount': row_dict['total_amount'],
                'percentage': (row_dict['total_amount'] / total_expenses * 100) if total_expenses > 0 else 0
            }
        
        self.close()
        return category_data
        
    def get_inventory_value_by_category(self):
        """Get inventory value grouped by product category"""
        self.connect()
        
        query = '''
        SELECT 
            category,
            SUM(store_quantity * cost_price) as store_value,
            SUM(warehouse_quantity * cost_price) as warehouse_value,
            SUM((store_quantity + warehouse_quantity) * cost_price) as total_value,
            COUNT(*) as num_products
        FROM products
        GROUP BY category
        ORDER BY total_value DESC
        '''
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        # Convert to dictionary with category as key
        category_data = {}
        
        # Calculate total inventory value for percentage calculation
        total_inventory_value = sum(dict(row)['total_value'] for row in results)
        
        for row in results:
            row_dict = dict(row)
            category = row_dict['category'] or 'Uncategorized'
            category_data[category] = {
                'store_value': row_dict['store_value'],
                'warehouse_value': row_dict['warehouse_value'],
                'total_value': row_dict['total_value'],
                'num_products': row_dict['num_products'],
                'percentage': (row_dict['total_value'] / total_inventory_value * 100) if total_inventory_value > 0 else 0
            }
        
        self.close()
        return category_data
        total_amount = 0
        
        # First calculate total amount for percentage calculation
        for row in results:
            if row['category']:
                total_amount += row['total_amount'] or 0
        
        # Then process each category
        for row in results:
            if row['category']:
                category = row['category']
            else:
                category = 'Other'
                
            category_data[category] = dict(row)
            # Calculate percentage
            if total_amount > 0:
                category_data[category]['percentage'] = (row['total_amount'] / total_amount) * 100
            else:
                category_data[category]['percentage'] = 0
        
        self.close()
        return category_data
        
    # Customer related methods
    def get_all_customers(self):
        """Get all customers from the database"""
        self.connect()
        
        self.cursor.execute('''
        SELECT c.*, 
               (SELECT MAX(s.created_at) FROM sales s WHERE s.customer_id = c.id) as last_purchase_date
        FROM customers c
        ORDER BY c.name
        ''')
        
        customers = [dict(row) for row in self.cursor.fetchall()]
        self.close()
        return customers
        
    def get_recent_customers(self, days=30):
        """Get customers who made purchases in the last X days"""
        self.connect()
        
        date_threshold = datetime.datetime.now() - datetime.timedelta(days=days)
        date_str = date_threshold.strftime('%Y-%m-%d %H:%M:%S')
        
        self.cursor.execute('''
        SELECT c.*, MAX(s.created_at) as last_purchase_date
        FROM customers c
        JOIN sales s ON c.id = s.customer_id
        WHERE s.created_at >= ?
        GROUP BY c.id
        ORDER BY last_purchase_date DESC
        ''', (date_str,))
        
        customers = [dict(row) for row in self.cursor.fetchall()]
        self.close()
        return customers
        
    def get_top_customers(self, limit=20):
        """Get top customers by purchase amount"""
        self.connect()
        
        self.cursor.execute('''
        SELECT c.*, 
               SUM(s.final_amount) as total_spent,
               COUNT(s.id) as purchase_count,
               MAX(s.created_at) as last_purchase_date
        FROM customers c
        JOIN sales s ON c.id = s.customer_id
        GROUP BY c.id
        ORDER BY total_spent DESC
        LIMIT ?
        ''', (limit,))
        
        customers = [dict(row) for row in self.cursor.fetchall()]
        self.close()
        return customers
        
    def get_inactive_customers(self, days=90):
        """Get customers who haven't made purchases in X days"""
        self.connect()
        
        date_threshold = datetime.datetime.now() - datetime.timedelta(days=days)
        date_str = date_threshold.strftime('%Y-%m-%d %H:%M:%S')
        
        self.cursor.execute('''
        SELECT c.*, MAX(s.created_at) as last_purchase_date
        FROM customers c
        LEFT JOIN sales s ON c.id = s.customer_id
        GROUP BY c.id
        HAVING MAX(s.created_at) < ? OR MAX(s.created_at) IS NULL
        ORDER BY last_purchase_date
        ''', (date_str,))
        
        customers = [dict(row) for row in self.cursor.fetchall()]
        self.close()
        return customers
        
    def get_customer_by_id(self, customer_id):
        """Get a customer by ID"""
        self.connect()
        
        self.cursor.execute('''
        SELECT c.*,
               (SELECT MAX(s.created_at) FROM sales s WHERE s.customer_id = c.id) as last_purchase_date,
               (SELECT COUNT(s.id) FROM sales s WHERE s.customer_id = c.id) as purchase_count,
               (SELECT SUM(s.final_amount) FROM sales s WHERE s.customer_id = c.id) as total_spent
        FROM customers c
        WHERE c.id = ?
        ''', (customer_id,))
        
        customer = self.cursor.fetchone()
        result = dict(customer) if customer else None
        
        self.close()
        return result
        
    def search_products(self, search_text):
        """Search for products by name, description, or category"""
        self.connect()
        
        search_pattern = f"%{search_text}%"
        self.cursor.execute('''
        SELECT * FROM products 
        WHERE name LIKE ? OR description LIKE ? OR category LIKE ?
        ORDER BY name
        ''', (search_pattern, search_pattern, search_pattern))
        
        products = [dict(row) for row in self.cursor.fetchall()]
        
        self.close()
        return products
        
    # Repair job related methods
    def get_all_repairs(self):
        """Get all repair jobs"""
        self.connect()
        
        self.cursor.execute('''
        SELECT r.*, c.name as customer_name, c.phone as customer_phone
        FROM repair_jobs r
        LEFT JOIN customers c ON r.customer_id = c.id
        ORDER BY r.created_at DESC
        ''')
        
        repairs = [dict(row) for row in self.cursor.fetchall()]
        self.close()
        return repairs
        
    def get_repairs_by_status(self, status):
        """Get repair jobs by status"""
        self.connect()
        
        self.cursor.execute('''
        SELECT r.*, c.name as customer_name, c.phone as customer_phone
        FROM repair_jobs r
        LEFT JOIN customers c ON r.customer_id = c.id
        WHERE r.status = ?
        ORDER BY r.created_at DESC
        ''', (status,))
        
        repairs = [dict(row) for row in self.cursor.fetchall()]
        self.close()
        return repairs
        
    # Invoice related methods
    def get_invoice_count_for_date(self, date_str):
        """Get the count of invoices created on a specific date"""
        self.connect()
        
        # Extract the date part from created_at and compare with the given date
        self.cursor.execute('''
        SELECT COUNT(*) as count
        FROM sales
        WHERE DATE(created_at) = ?
        ''', (date_str,))
        
        result = self.cursor.fetchone()
        count = result['count'] if result else 0
        
        self.close()
        return count