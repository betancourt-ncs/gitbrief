import server


def test_app_imports():
    assert server.app is not None
