import psycopg2
from psycopg2 import OperationalError, DatabaseError
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# ============================
# Koneksi ke database PostgreSQL / Supabase
# ============================
conn = None
c = None

# Determine if using Supabase or local PostgreSQL
USE_SUPABASE = os.getenv("DB_HOST", "").endswith("supabase.co")

try:
    if USE_SUPABASE:
        # Connection to Supabase
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "db.hbdiwdfzryzvbexbehyr.supabase.co"),
            port=os.getenv("DB_PORT", "5432"),
            user=os.getenv("DB_USER", "DeathMoonerg"),
            password=os.getenv("DB_PASSWORD", "5AY2ZV2zJXVNDJJZ"),
            dbname=os.getenv("DB_NAME", "sales_db"),
            sslmode="require"
        )
        db_type = "Supabase"
    else:
        # Connection to local PostgreSQL
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "db.hbdiwdfzryzvbexbehyr.supabase.co"),
            port=os.getenv("DB_PORT", "5432"),
            user=os.getenv("DB_USER", "DeathMoonerg"),
            password=os.getenv("DB_PASSWORD", "5AY2ZV2zJXVNDJJZ"),
            dbname=os.getenv("DB_NAME", "sales_db")
        )
        db_type = "PostgreSQL Local"

    # Membuat cursor
    c = conn.cursor()
    
    # Test koneksi dengan query sederhana
    c.execute("SELECT version();")
    db_version = c.fetchone()
    
    print("✅ Koneksi database berhasil!")
    print(f"📊 Database Type: {db_type}")
    print(f"🔗 Database Version: {db_version[0]}")
    
except OperationalError as e:
    print("⚠️  WARNING: Gagal terhubung ke database!")
    print(f"   Detail Error: {str(e)}")
    print("\n💡 Tips untuk memperbaiki:")
    if USE_SUPABASE:
        print("   1. Periksa konfigurasi Supabase di .env file")
        print("   2. Pastikan DB_HOST, DB_USER, DB_PASSWORD, dan DB_NAME sudah benar")
        print("   3. Pastikan Supabase project sudah aktif")
    else:
        print("   1. Pastikan PostgreSQL sudah berjalan")
        print("   2. Periksa host, port, user, password, dan dbname di .env atau config.py")
        print("   3. Pastikan database sudah dibuat")
    print("\n   Aplikasi akan dimulai dalam mode offline. Data tidak akan tersedia.\n")
    db_version = ("Offline Mode",)
    
except DatabaseError as e:
    print("⚠️  WARNING: Terjadi kesalahan pada database!")
    print(f"   Detail Error: {str(e)}")
    print("\n   Aplikasi akan dimulai dalam mode offline. Data tidak akan tersedia.\n")
    db_version = ("Offline Mode",)
    
except Exception as e:
    print("⚠️  WARNING: Terjadi kesalahan tidak terduga!")
    print(f"   Detail Error: {str(e)}")
    print("\n   Aplikasi akan dimulai dalam mode offline. Data tidak akan tersedia.\n")
    db_version = ("Offline Mode",)

# ============================
# Fungsi ambil data dari tabel
# ============================

def view_customers():
    try:
        query = '''
            SELECT customer_id, name, email, phone, address, birthdate
            FROM customers
            ORDER BY name ASC
        '''
        c.execute(query)
        return c.fetchall()
    except Exception as e:
        print(f"❌ ERROR saat mengambil data customers: {str(e)}")
        return []

def view_orders_with_customers():
    try:
        query = '''
            SELECT 
                o.order_id, 
                o.order_date, 
                o.total_amount, 
                c.name AS customer_name, 
                c.phone 
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            ORDER BY o.order_date DESC
        '''
        c.execute(query)
        return c.fetchall()
    except Exception as e:
        print(f"❌ ERROR saat mengambil data orders: {str(e)}")
        return []

def view_products():
    try:
        query = '''
            SELECT product_id, name, description, price, stock
            FROM products
            ORDER BY name ASC
        '''
        c.execute(query)
        return c.fetchall()
    except Exception as e:
        print(f"❌ ERROR saat mengambil data products: {str(e)}")
        return []

def view_order_details_with_info():
    try:
        query = '''
            SELECT 
                od.order_detail_id,
                o.order_id,
                o.order_date,
                c.customer_id,
                c.name AS customer_name,
                p.product_id,
                p.name AS product_name,
                p.price AS unit_price,
                od.quantity,
                od.subtotal,
                o.total_amount AS order_total,
                c.phone
            FROM order_details od
            JOIN orders o ON od.order_id = o.order_id
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN products p ON od.product_id = p.product_id
            ORDER BY o.order_date DESC
        '''
        c.execute(query)
        return c.fetchall()
    except Exception as e:
        print(f"❌ ERROR saat mengambil data order_details: {str(e)}")
        return []

# ============================
# Fungsi untuk menutup koneksi (opsional, biasanya tidak perlu dipanggil)
# ============================
def close_connection():
    """Fungsi untuk menutup koneksi database"""
    global conn, c
    try:
        if c:
            c.close()
            print("✅ Cursor ditutup")
        if conn:
            conn.close()
            print("✅ Koneksi database ditutup")
    except Exception as e:
        print(f"❌ ERROR saat menutup koneksi: {str(e)}")
