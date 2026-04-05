from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.database import Base

meeting_participants = Table(
    "meeting_participants",
    Base.metadata,
    Column("meeting_id", Integer, ForeignKey("meetings.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
)


class MeetingModel(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    datetime_beginning = Column(DateTime)
    datetime_end = Column(DateTime)
    team_id = Column(Integer, ForeignKey("teams.id"))

    team = relationship("TeamModel")
    participants = relationship(
        "UserModel", secondary=meeting_participants, back_populates="meetings"
    )
