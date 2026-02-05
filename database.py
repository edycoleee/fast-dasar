"""
Database Helper untuk SQLite
Menggunakan raw SQL queries (bukan ORM)
"""

import sqlite3
from typing import List, Optional, Dict, Any
import os

# Path database
DB_PATH = "siswa.db"


def get_db_connection():
    """
    Membuat koneksi ke SQLite database.
    Row factory untuk mendapatkan hasil sebagai dictionary.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Agar hasil query bisa diakses seperti dict
    return conn


def init_db():
    """
    Inisialisasi database dan buat tabel siswa jika belum ada.
    Tabel siswa:
    - id: INTEGER PRIMARY KEY AUTOINCREMENT
    - nama: TEXT NOT NULL
    - email: TEXT NOT NULL UNIQUE
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create table siswa
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS siswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized at {DB_PATH}")


def insert_siswa(nama: str, email: str) -> int:
    """
    Insert siswa baru ke database.
    
    Args:
        nama: Nama siswa
        email: Email siswa (harus unique)
    
    Returns:
        ID siswa yang baru dibuat
    
    Raises:
        sqlite3.IntegrityError: Jika email sudah ada
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO siswa (nama, email) VALUES (?, ?)",
        (nama, email)
    )
    
    siswa_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return siswa_id


def get_all_siswa() -> List[Dict[str, Any]]:
    """
    Ambil semua data siswa dari database.
    
    Returns:
        List of siswa dictionaries
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nama, email FROM siswa ORDER BY id")
    rows = cursor.fetchall()
    
    conn.close()
    
    # Convert Row objects to dictionaries
    siswa_list = [dict(row) for row in rows]
    return siswa_list


def get_siswa_by_id(siswa_id: int) -> Optional[Dict[str, Any]]:
    """
    Ambil data siswa berdasarkan ID.
    
    Args:
        siswa_id: ID siswa
    
    Returns:
        Siswa dictionary atau None jika tidak ditemukan
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, nama, email FROM siswa WHERE id = ?",
        (siswa_id,)
    )
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return dict(row)
    return None


def update_siswa(siswa_id: int, nama: str, email: str) -> bool:
    """
    Update data siswa.
    
    Args:
        siswa_id: ID siswa
        nama: Nama baru
        email: Email baru
    
    Returns:
        True jika berhasil, False jika siswa tidak ditemukan
    
    Raises:
        sqlite3.IntegrityError: Jika email sudah digunakan siswa lain
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE siswa SET nama = ?, email = ? WHERE id = ?",
        (nama, email, siswa_id)
    )
    
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return rows_affected > 0


def delete_siswa(siswa_id: int) -> bool:
    """
    Hapus siswa dari database.
    
    Args:
        siswa_id: ID siswa
    
    Returns:
        True jika berhasil, False jika siswa tidak ditemukan
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM siswa WHERE id = ?", (siswa_id,))
    
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return rows_affected > 0


def count_siswa() -> int:
    """
    Hitung jumlah siswa di database.
    
    Returns:
        Jumlah siswa
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM siswa")
    result = cursor.fetchone()
    
    conn.close()
    
    return result['count'] if result else 0


# Initialize database saat module di-import
if not os.path.exists(DB_PATH):
    init_db()
