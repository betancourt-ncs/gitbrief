from db.crud import get_tenant
from db.models import Tenant


# known sender: the matching tenant row is returned
def test_get_tenant_known_sender(db_session):
    db_session.add(Tenant(sender_id=12345, signing_secret="test-secret"))
    db_session.commit()

    result = get_tenant(db_session, 12345)

    assert result is not None
    assert result.sender_id == 12345
    assert result.signing_secret == "test-secret"


# unknown sender: return None, so server.py can return 404
def test_get_tenant_unknown_sender(db_session):
    db_session.add(Tenant(sender_id=12345, signing_secret="test-secret"))   # table is NOT empty
    db_session.commit()

    result = get_tenant(db_session, 99999)

    assert result is None
