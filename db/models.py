from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base


# Modeling tenants db table

class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(unique=True, index=True)
    signing_secret: Mapped[str] = mapped_column()
    social_webhook_url: Mapped[Optional[str]] = mapped_column()
    direct_webhook_url: Mapped[Optional[str]] = mapped_column()
