from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.meetings.models import meeting_participants


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    role = Column(String, nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=True)
    team = relationship("TeamModel")
    hash_password = Column(String)
    meetings = relationship(
        "MeetingModel", secondary=meeting_participants, back_populates="participants"
    )
    tasks = relationship("TaskModel")
