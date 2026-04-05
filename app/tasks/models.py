from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, Table,
                        func)
from sqlalchemy.orm import relationship

from app.database import Base

chat_messages = Table(
    "chat_messages",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id")),
    Column("messages_id", Integer, ForeignKey("messages.id")),
)


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    status = Column(String, default="открыто")
    dedline = Column(DateTime)
    description = Column(String, nullable=True)
    job_evaluation = Column(Integer, nullable=True)

    executor_id = Column(Integer, ForeignKey("users.id"))
    executor = relationship("UserModel")

    team_id = Column(Integer, ForeignKey("teams.id"))
    team = relationship("TeamModel")

    chat = relationship("MessageModel", secondary=chat_messages, back_populates="task")


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    created_at = Column(DateTime, default=func.now())
    sender_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))

    sender = relationship("UserModel")
    task = relationship("TaskModel", secondary=chat_messages, back_populates="chat")
