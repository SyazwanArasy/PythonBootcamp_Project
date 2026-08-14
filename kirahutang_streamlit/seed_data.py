from database.db_manager import DatabaseManager

db = DatabaseManager()
conn = db.get_connection()
cursor = conn.cursor()

# Clear existing data first, so re-running this script doesn't duplicate rows
cursor.execute("DELETE FROM pendapatan")
cursor.execute("DELETE FROM komitmen")
cursor.execute("DELETE FROM hutang")

# --- Pendapatan ---
cursor.executemany(
    "INSERT INTO pendapatan (name, category, amount) VALUES (?, ?, ?)",
    [
        ("Gaji", "Tetap", 3599.62),
        ("Freelance", "Tambahan", 2500.00),
        ("Lain-lain", "Lain-lain", 500.00),
    ]
)

# --- Komitmen ---
cursor.executemany(
    "INSERT INTO komitmen (name, category, amount, due_date, status) VALUES (?, ?, ?, ?, ?)",
    [
        ("House Loan", "Tetap", 1700.00, "2026-08-31", "Belum bayar"),
        ("Maintainance Fee", "Tetap", 143.00, "2026-09-01", "Selesai"),
        ("Internet", "Tetap", 104.92, "2026-08-01", "Belum bayar"),
        ("Coway", "Tetap", 56.00, "2026-08-31", "Selesai"),
        ("Credit Card", "Berubah", 560.95, "2026-09-13", "Belum bayar"),
        ("Bil Air", "Berubah", 36.00, "2026-08-31", "Selesai"),
        ("TNB", "Berubah", 240.63, "2026-08-31", "Belum bayar"),
        ("Netflix", "Lain-lain", 49.90, "2026-08-31", "Selesai"),
        ("Spotify", "Lain-lain", 17.50, "2026-09-13", "Selesai"),
        ("Google One", "Lain-lain", 8.49, "2026-09-01", "Selesai"),
        ("Car Services", "Lain-lain", 350.00, "2026-08-31", "Belum bayar"),
        ("Road Tax & Insurances", "Lain-lain", 376.85, "2026-08-31", "Belum bayar"),
    ]
)

# --- Hutang ---
cursor.executemany(
    "INSERT INTO hutang (name, direction, amount, date_recorded, status) VALUES (?, ?, ?, ?, ?)",
    [
        ("Ayah", "saya_hutang", 350.00, "2026-08-05", "Belum bayar"),
        ("Ali", "saya_hutang", 150.00, "2026-05-16", "Belum bayar"),
        ("Abu", "saya_hutang", 150.00, "2026-06-26", "Belum bayar"),
        ("Amar", "orang_hutang", 500.00, "2026-02-20", "Belum bayar"),
        ("Atan", "orang_hutang", 200.00, "2026-01-26", "Selesai"),
        ("Amir", "orang_hutang", 50.00, "2026-07-26", "Belum bayar"),
    ]
)

conn.commit()
conn.close()

print("✅ Seed data inserted successfully!")