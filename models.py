from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger, Interval, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////app/data/reminders.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    telegram_id = Column(BigInteger, primary_key=True, index=True)
    is_blocked = Column(Boolean, default=False, nullable=False)
    is_whitelisted = Column(Boolean, default=False, nullable=False) # Relevant in whitelist mode

    reminders = relationship("Reminder", back_populates="user") # Optional: Link to reminders

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, blocked={self.is_blocked}, whitelisted={self.is_whitelisted})>"


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False, index=True) # Foreign Key
    user = relationship("User", back_populates="reminders") # Relationship back to User
    chat_id = Column(BigInteger, nullable=False, index=True)
    reminder_text = Column(String, nullable=False)
    schedule_time = Column(String, nullable=False)
    schedule_interval_days = Column(Integer, nullable=False, default=1)
    next_reminder_time = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    job_id = Column(String, unique=True, nullable=True)

    def __repr__(self):
        return f"<Reminder(id={self.id}, user_id={self.user_id}, text='{self.reminder_text[:20]}...', next_time='{self.next_reminder_time}')>"

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creating database tables...")
    if DATABASE_URL.startswith("sqlite"):
        db_path = DATABASE_URL.split("///")[1]
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            print(f"Created data directory: {db_dir}")
    create_db_and_tables()
    print("Database tables created (if they didn't exist).")