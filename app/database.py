"""
Database configuration dan ORM models menggunakan SQLAlchemy
"""

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Optional, List

# Database configuration
DATABASE_URL = "sqlite:///./siswa.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Untuk SQLite
    echo=False  # Set True untuk debug SQL queries
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ==================== ORM Models ====================

class SiswaORM(Base):
    """SQLAlchemy ORM model untuk tabel siswa"""
    __tablename__ = "siswa"
    
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    
    def __repr__(self):
        return f"<SiswaORM(id={self.id}, nama={self.nama}, email={self.email})>"


# ==================== Database Initialization ====================

def init_db():
    """
    Inisialisasi database dan create semua tables.
    Dipanggil saat app startup via lifespan.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized with SQLAlchemy")


def get_db():
    """
    Dependency untuk mendapatkan database session.
    Digunakan di FastAPI endpoints.
    
    Usage:
        @app.get("/api/siswa/")
        def get_siswa(db: Session = Depends(get_db)):
            siswa = db.query(SiswaORM).all()
            return siswa
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== CRUD Operations ====================

def get_all_siswa(db: Session) -> List[SiswaORM]:
    """
    Ambil semua siswa dari database.
    
    Args:
        db: SQLAlchemy Session
    
    Returns:
        List[SiswaORM]
    """
    return db.query(SiswaORM).all()


def get_siswa_by_id(db: Session, siswa_id: int) -> Optional[SiswaORM]:
    """
    Ambil siswa berdasarkan ID.
    
    Args:
        db: SQLAlchemy Session
        siswa_id: ID siswa
    
    Returns:
        SiswaORM atau None jika tidak ditemukan
    """
    return db.query(SiswaORM).filter(SiswaORM.id == siswa_id).first()


def get_siswa_by_email(db: Session, email: str) -> Optional[SiswaORM]:
    """
    Ambil siswa berdasarkan email.
    
    Args:
        db: SQLAlchemy Session
        email: Email siswa
    
    Returns:
        SiswaORM atau None jika tidak ditemukan
    """
    return db.query(SiswaORM).filter(SiswaORM.email == email).first()


def insert_siswa(db: Session, nama: str, email: str) -> SiswaORM:
    """
    Tambah siswa baru ke database.
    
    Args:
        db: SQLAlchemy Session
        nama: Nama siswa
        email: Email siswa
    
    Returns:
        SiswaORM yang baru dibuat
    
    Raises:
        sqlalchemy.exc.IntegrityError: Jika email sudah ada
    """
    siswa = SiswaORM(nama=nama, email=email)
    db.add(siswa)
    db.commit()
    db.refresh(siswa)
    return siswa


def update_siswa(db: Session, siswa_id: int, nama: str, email: str) -> Optional[SiswaORM]:
    """
    Update data siswa.
    
    Args:
        db: SQLAlchemy Session
        siswa_id: ID siswa
        nama: Nama baru
        email: Email baru
    
    Returns:
        SiswaORM yang diupdate atau None jika tidak ditemukan
    
    Raises:
        sqlalchemy.exc.IntegrityError: Jika email sudah digunakan siswa lain
    """
    siswa = db.query(SiswaORM).filter(SiswaORM.id == siswa_id).first()
    if siswa:
        siswa.nama = nama
        siswa.email = email
        db.commit()
        db.refresh(siswa)
    return siswa


def delete_siswa(db: Session, siswa_id: int) -> bool:
    """
    Hapus siswa dari database.
    
    Args:
        db: SQLAlchemy Session
        siswa_id: ID siswa
    
    Returns:
        True jika berhasil, False jika siswa tidak ditemukan
    """
    siswa = db.query(SiswaORM).filter(SiswaORM.id == siswa_id).first()
    if siswa:
        db.delete(siswa)
        db.commit()
        return True
    return False


def count_siswa(db: Session) -> int:
    """
    Hitung total siswa di database.
    
    Args:
        db: SQLAlchemy Session
    
    Returns:
        Jumlah siswa
    """
    return db.query(SiswaORM).count()
