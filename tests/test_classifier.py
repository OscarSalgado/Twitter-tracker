from app.classifier import classify_tweet


def test_empty_content_returns_other():
    assert classify_tweet("") == ("other", 0.0)
    assert classify_tweet("   ") == ("other", 0.0)


def test_unrecognized_content_returns_other():
    topic, confidence = classify_tweet("blah blah blah")
    assert topic == "other"
    assert confidence == 0.0


def test_technology_keywords_match():
    topic, confidence = classify_tweet("Python and machine learning are transforming software development")
    assert topic == "technology"
    assert confidence > 0.0


def test_confidence_capped_at_one():
    content = " ".join(["AI"] * 100)
    _, confidence = classify_tweet(content)
    assert confidence <= 1.0
