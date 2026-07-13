from app import config


def test_env_driven_settings_reflect_environment():
    assert config.TWITTER_USERNAME == ""
    assert config.BASIC_AUTH_USER == "admin"
    assert config.BASIC_AUTH_PASSWORD == "test-password"
    assert config.POLL_INTERVAL_MINUTES == 15
    assert config.DATABASE_URL.startswith("sqlite:///")
    assert config.COOKIES_FILE.endswith("cookies.json")
