from sqlalchemy import REAL, BigInteger, CheckConstraint, DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime


class Base(DeclarativeBase):
    pass

class Alert(Base):
    __tablename__="alerts"

    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    camera_id:Mapped[str]=mapped_column(String(100))
    vehicle_type:Mapped[str]=mapped_column(String(50))
    timestamp:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),)
    infraction_type:Mapped[str]=mapped_column(String(100))
    infraction_server:Mapped[int]=mapped_column(Integer)
    confidance:Mapped[float|None]=mapped_column(REAL,nullable=True)
    evidance:Mapped[str|None]=mapped_column(Text,nullable=True)

    __table_args__=(
        CheckConstraint("infraction_serverty IN ('Warning','Critical')",name="ck_alert_serverity"),
        Index("ix_alerts_timestamp", "timestapmp"),                       # HINT 7: the column the dashboard sorts and filters by time on
        Index("ix_alerts_camera_id", "camera_id"),
        Index("ix_alerts_infraction_type", "infraction_type"),
    )
    
