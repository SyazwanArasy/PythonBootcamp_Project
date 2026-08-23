import sqlite3
import calendar
from datetime import date, datetime

DB_PATH = "database/kirahutang.db"


class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.create_tables()
        self.refresh_recurring_bills()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _add_column_if_missing(self, cursor, table, column, coltype):
        cursor.execute(f"PRAGMA table_info({table})")
        existing_columns = [row[1] for row in cursor.fetchall()]
        if column not in existing_columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")
            
    def _add_one_month(self, date_str):
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
        month = dt.month + 1
        year = dt.year
        if month > 12:
            month = 1
            year += 1
        # Handle months with fewer days (e.g. Jan 31 -> Feb 28/29, not Mar 3)
        last_day_of_month = calendar.monthrange(year, month)[1]
        day = min(dt.day, last_day_of_month)
        return date(year, month, day).isoformat()
    
    def refresh_recurring_bills(self):
        # Runs on every page load. Finds recurring bills that are marked
        # "Selesai" but whose due date has now passed - meaning it's time
        # for the next cycle - and resets them in place: due date pushed
        # forward, status back to unpaid. No new row created.
        today = date.today().isoformat()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, due_date FROM komitmen
            WHERE is_recurring = 1 AND status = 'Selesai' AND due_date < ?
        """, (today,))
        rows = cursor.fetchall()

        for row in rows:
            new_due = row["due_date"]
            # Keep pushing forward in case multiple months passed
            # since you last opened the app
            while new_due < today:
                new_due = self._add_one_month(new_due)
            cursor.execute("""
                UPDATE komitmen SET due_date = ?, status = 'Belum bayar' WHERE id = ?
            """, (new_due, row["id"]))

        conn.commit()
        conn.close()

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pendapatan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS komitmen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Belum bayar'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hutang (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                direction TEXT NOT NULL,
                amount REAL NOT NULL,
                date_recorded TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Belum bayar'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS belanja (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                date_spent TEXT NOT NULL
            )
        """)
        
        self._add_column_if_missing(cursor, "komitmen", "is_recurring", "INTEGER NOT NULL DEFAULT 0")

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
    # NOTE: all "current" Komitmen queries only include due_date >= today.
    # Once a bill's due date passes and it's still unpaid, it "transfers" to
    # Tunggakan automatically (pure date math, no manual action needed).
    # Once paid FROM Tunggakan, it disappears from both pages entirely and
    # only remains visible in History.
    def get_total_komitmen(self):
        today = date.today().isoformat()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(amount) as total FROM komitmen
            WHERE due_date >= ?
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
        today = date.today().isoformat()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, category, amount, due_date, status, is_recurring FROM komitmen
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
            SELECT id, name, amount, due_date, status, is_recurring FROM komitmen
            WHERE category = ? AND due_date >= ?
            ORDER BY due_date ASC
        """, (category, today))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_komitmen(self, name, category, amount, due_date, is_recurring=False):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO komitmen (name, category, amount, due_date, status, is_recurring)
            VALUES (?, ?, ?, ?, 'Belum bayar', ?)
        """, (name, category, amount, due_date, int(is_recurring)))
        conn.commit()
        conn.close()

    def update_komitmen(self, komitmen_id, name, amount, due_date, category=None, is_recurring=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if category is not None and is_recurring is not None:
            cursor.execute("""
                UPDATE komitmen SET name = ?, amount = ?, due_date = ?, category = ?, is_recurring = ? WHERE id = ?
            """, (name, amount, due_date, category, int(is_recurring), komitmen_id))
        elif is_recurring is not None:
            cursor.execute("""
                UPDATE komitmen SET name = ?, amount = ?, due_date = ?, is_recurring = ? WHERE id = ?
            """, (name, amount, due_date, int(is_recurring), komitmen_id))
        elif category is not None:
            cursor.execute("""
                UPDATE komitmen SET name = ?, amount = ?, due_date = ?, category = ? WHERE id = ?
            """, (name, amount, due_date, category, komitmen_id))
        else:
            cursor.execute("""
                UPDATE komitmen SET name = ?, amount = ?, due_date = ? WHERE id = ?
            """, (name, amount, due_date, komitmen_id))
        conn.commit()
        conn.close()

    def update_komitmen_status(self, komitmen_id, new_status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE komitmen SET status = ? WHERE id = ?", (new_status, komitmen_id))
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

    # ---------- BELANJA ----------
    def get_total_belanja(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) as total FROM belanja")
        result = cursor.fetchone()["total"]
        conn.close()
        return result or 0.0
    
    def get_total_belanja_this_month(self):
        today = date.today()
        month_start = today.replace(day=1).isoformat()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(amount) as total FROM belanja
            WHERE date_spent >= ?
        """, (month_start,))
        result = cursor.fetchone()["total"]
        conn.close()
        return result or 0.0

    def get_belanja_by_category(self, category):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, category, amount, date_spent FROM belanja
            WHERE category = ?
            ORDER BY date_spent DESC
        """, (category,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_all_belanja(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, category, amount, date_spent FROM belanja
            ORDER BY date_spent DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_distinct_belanja_months(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT substr(date_spent, 1, 7) as month FROM belanja
            ORDER BY month DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [row["month"] for row in rows]

    def get_belanja_filtered(self, category=None, month=None, start_date=None, end_date=None):
        # Builds a query dynamically based on which filters are active.
        # Any filter left as None is simply skipped.
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT id, name, category, amount, date_spent FROM belanja WHERE 1=1"
        params = []

        if category and category != "All":
            query += " AND category = ?"
            params.append(category)

        if month and month != "All":
            query += " AND substr(date_spent, 1, 7) = ?"
            params.append(month)

        if start_date:
            query += " AND date_spent >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date_spent <= ?"
            params.append(end_date)

        query += " ORDER BY date_spent DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_belanja(self, name, category, amount, date_spent):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO belanja (name, category, amount, date_spent)
            VALUES (?, ?, ?, ?)
        """, (name, category, amount, date_spent))
        conn.commit()
        conn.close()

    def update_belanja(self, belanja_id, name, category, amount, date_spent):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE belanja SET name = ?, category = ?, amount = ?, date_spent = ? WHERE id = ?
        """, (name, category, amount, date_spent, belanja_id))
        conn.commit()
        conn.close()

    def delete_belanja(self, belanja_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM belanja WHERE id = ?", (belanja_id,))
        conn.commit()
        conn.close()

    def get_distinct_belanja_categories(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM belanja ORDER BY category ASC")
        rows = cursor.fetchall()
        conn.close()
        return [row["category"] for row in rows]

    def get_belanja_category_totals(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, SUM(amount) as total FROM belanja
            GROUP BY category
            ORDER BY total DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_belanja_daily_totals(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date_spent, SUM(amount) as total FROM belanja
            GROUP BY date_spent
            ORDER BY date_spent ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_top_belanja(self, limit=5):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, category, amount, date_spent FROM belanja
            ORDER BY amount DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_belanja_category_totals(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, SUM(amount) as total FROM belanja
            GROUP BY category
            ORDER BY total DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_belanja_daily_totals(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date_spent, SUM(amount) as total FROM belanja
            GROUP BY date_spent
            ORDER BY date_spent ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_top_belanja(self, limit=5):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, category, amount, date_spent FROM belanja
            ORDER BY amount DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    # ---------- HISTORY ----------
    def get_history(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT name, amount, due_date as date, status FROM komitmen")
        komitmen_rows = [dict(row, source="Komitmen") for row in cursor.fetchall()]

        cursor.execute("SELECT name, amount, date_recorded as date, status FROM hutang")
        hutang_rows = [dict(row, source="Hutang") for row in cursor.fetchall()]

        conn.close()

        combined = komitmen_rows + hutang_rows
        combined.sort(key=lambda x: x["date"], reverse=True)
        return combined