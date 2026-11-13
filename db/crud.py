from sqlalchemy import select
from sqlalchemy.orm import Session
from db.models import Tenant


# Get tenant by sender id
def get_tenant(db: Session, sender_id: int):
    query = select(Tenant).where(Tenant.sender_id == sender_id)
    result = db.execute(query).scalar_one_or_none()
    return result
