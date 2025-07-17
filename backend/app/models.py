from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, UniqueConstraint, func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    current_language = Column(String, default="Spanish", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_admin = Column(Boolean, default=False, nullable=False)

    language_progress = relationship("UserLanguageProgress", back_populates="user", cascade="all, delete-orphan")
    srs_states = relationship("SRSState", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    level = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    flashcards = relationship("Flashcard", back_populates="lesson")

class Flashcard(Base):
    __tablename__ = "flashcards"
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"))
    front_text = Column(String, nullable=False)
    back_text = Column(String, nullable=False)
    example = Column(Text)

    lesson = relationship("Lesson", back_populates="flashcards")
    srs_states = relationship("SRSState", back_populates="flashcard")

class SRSState(Base):
    __tablename__ = "srs_states"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    flashcard_id = Column(Integer, ForeignKey("flashcards.id", ondelete="CASCADE"))
    ease_factor = Column(Integer, default=250)
    interval_days = Column(Integer, default=0)
    repetition = Column(Integer, default=0)
    next_due = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="srs_states")
    flashcard = relationship("Flashcard", back_populates="srs_states")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    transcript = Column(Text)
    duration_sec = Column(Integer)

    user = relationship("User", back_populates="chat_sessions")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String, nullable=False)
    choices = Column(JSON, nullable=False)
    correct_choice = Column(String, nullable=False)
    language = Column(String, default="Spanish", nullable=False)

class UserLanguageProgress(Base):
    __tablename__ = "user_language_progress"
    __table_args__ = (UniqueConstraint("user_id", "language", name="user_language"),)
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    language = Column(String, nullable=False)
    level = Column(String, default="Beginner", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="language_progress")