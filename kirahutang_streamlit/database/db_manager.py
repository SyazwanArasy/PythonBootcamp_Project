import sqlite3
from datetime import date

DB_PATH = "database/kirahutang.db"


class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.create_tables()

    def get_connection(self):
        # Each call opens a fresh connection - simplest approach for Streamlit,
        # since Streamlit reruns the whole script on every interaction.
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # lets us access columns by name, like a dict
        return conn

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pendapatan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,   -- 'Tetap', 'Tambahan', 'Lain-lain'
                amount REAL NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS komitmen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,   -- 'Tetap', 'Berubah', 'Lain-lain'
                amount REAL NOT NULL,
                due_date TEXT NOT NULL,   -- stored as 'YYYY-MM-DD'
                status TEXT NOT NULL DEFAULT 'Belum bayar'  -- or 'Selesai'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hutang (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                direction TEXT NOT NULL,  -- 'saya_hutang' or 'orang_hutang'
                amount REAL NOT NULL,
                date_recorded TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Belum bayar'
            )
        """)

        conn.commit()
        conn.close()

    # ---------- PENDAPATAN ----------
    def get_total_pendapatan(self, category=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if category:
            cursor.execute(
                "SELECT SUM(amount) as total FROM pendapatan WHERE category = ?",
                (category,)
            )
        else:
            cursor.execute("SELECT SUM(amount) as total FROM pendapatan")
        result = cursor.fetchone()["total"]
        conn.close()
        return result or 0.0
    
    def get_pendapatan_by_category(self, category):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, amount FROM pendapatan
            WHERE category = ?
            ORDER BY id DESC
        """, (category,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_pendapatan(self, name, category, amount):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pendapatan (name, category, amount)
            VALUES (?, ?, ?)
        """, (name, category, amount))
        conn.commit()
        conn.close()

    def delete_pendapatan(self, pendapatan_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pendapatan WHERE id = ?", (pendapatan_id,))
        conn.commit()
        conn.close()
        
    def update_pendapatan(self, pendapatan_id, name, amount):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pendapatan SET name = ?, amount = ? WHERE id = ?
        """, (name, amount, pendapatan_id))
        conn.commit()
        conn.close()

   # ---------- KOMITMEN ----------
    def get_total_komitmen(self):
        # Only counts CURRENT commitments - excludes anything overdue & unpaid
        # (those have "transferred" to Tunggakan)
        today = date.today().isoformat()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(amount) as total FROM komitmen
            WHERE due_date >= ? OR status = 'Selesai'
        """, (today,))
        result = cursor.fetchone()["total"]
        conn.close()
        return result or 0.0

    def get_total_komitmen_unpaid(self):
        today = date.today().isoformat()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(amount) as total FROM komitmen
            WHERE status != 'Selesai' AND due_date >= ?
        """, (today,))
        result = cursor.fetchone()["total"]
        conn.close()
        return result or 0.0

    def get_total_tunggakan(self):
        # Tunggakan = komitmen that's past due AND not yet paid
        today = date.today().isoformat()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(amount) as total FROM komitmen
            WHERE due_date < ? AND status != 'Selesai'
        """, (today,))
        result = cursor.fetchone()["total"]
        conn.close()
        return result or 0.0
    
    def get_tunggakan_items(self):
        # Same overdue+unpaid logic as get_total_tunggakan, but returns full rows
        today = date.today().isoformat()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, category, amount, due_date, status FROM komitmen
            WHERE due_date < ? AND status != 'Selesai'
            ORDER BY due_date ASC
        """, (today,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_upcoming_bills(self, limit=6):
        today = date.today().isoformat()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, due_date, amount FROM komitmen
            WHERE status != 'Selesai' AND due_date >= ?
            ORDER BY due_date ASC
            LIMIT ?
        """, (today, limit))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_komitmen_by_category(self, category):
        today = date.today().isoformat()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, amount, due_date, status FROM komitmen
            WHERE category = ? AND (due_date >= ? OR status = 'Selesai')
            ORDER BY due_date ASC
        """, (category, today))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_komitmen(self, name, category, amount, due_date):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO komitmen (name, category, amount, due_date, status)
            VALUES (?, ?, ?, ?, 'Belum bayar')
        """, (name, category, amount, due_date))
        conn.commit()
        conn.close()

    def update_komitmen_status(self, komitmen_id, new_status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE komitmen SET status = ? WHERE id = ?
        """, (new_status, komitmen_id))
        conn.commit()
        conn.close()
        
    def update_komitmen(self, komitmen_id, name, amount, due_date, category=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if category:
            cursor.execute("""
                UPDATE komitmen SET name = ?, amount = ?, due_date = ?, category = ? WHERE id = ?
            """, (name, amount, due_date, category, komitmen_id))
        else:
            cursor.execute("""
                UPDATE komitmen SET name = ?, amount = ?, due_date = ? WHERE id = ?
            """, (name, amount, due_date, komitmen_id))
        conn.commit()
        conn.close()

    def delete_komitmen(self, komitmen_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM komitmen WHERE id = ?", (komitmen_id,))
        conn.commit()
        conn.close()

    # ---------- HUTANG ----------
    def get_total_hutang(self, direction):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(amount) as total FROM hutang
            WHERE direction = ? AND status != 'Selesai'
        """, (direction,))
        result = cursor.fetchone()["total"]
        conn.close()
        return result or 0.0
    
    def get_hutang_by_direction(self, direction):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, amount, date_recorded, status FROM hutang
            WHERE direction = ?
            ORDER BY date_recorded DESC
        """, (direction,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_hutang(self, name, direction, amount, date_recorded):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO hutang (name, direction, amount, date_recorded, status)
            VALUES (?, ?, ?, ?, 'Belum bayar')
        """, (name, direction, amount, date_recorded))
        conn.commit()
        conn.close()

    def update_hutang(self, hutang_id, name, amount, date_recorded):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE hutang SET name = ?, amount = ?, date_recorded = ? WHERE id = ?
        """, (name, amount, date_recorded, hutang_id))
        conn.commit()
        conn.close()

    def update_hutang_status(self, hutang_id, new_status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE hutang SET status = ? WHERE id = ?
        """, (new_status, hutang_id))
        conn.commit()
        conn.close()

    def delete_hutang(self, hutang_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hutang WHERE id = ?", (hutang_id,))
        conn.commit()
        conn.close()