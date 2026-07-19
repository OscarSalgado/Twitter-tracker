# Topic Classification System Design

## Architecture Overview

```
Tweet Storage (app/models.py)
        ↓
Classifier Module (app/classifier.py - NEW)
        ↓
Classification during Poll (tracker_service.poll_account)
        ↓
Dashboard Filter (app/templates/index.html)
```

## Topic Categories

**Fixed categories** for v1:
- `technology` - AI, software, hardware, startups, programming
- `politics` - government, elections, policy, laws
- `business` - markets, companies, finance, investments
- `sports` - teams, players, games, competitions
- `entertainment` - movies, music, celebrities, entertainment industry
- `science` - research, discoveries, space, medicine
- `health` - health, wellness, fitness, medicine
- `social` - social issues, activism, community
- `crypto` - cryptocurrency, blockchain, NFTs, defi
- `other` - everything else

## Classification Algorithm

**Approach: Keyword-based matching with confidence scoring**

For each tweet, scan content against keyword dictionaries:

```python
TOPIC_KEYWORDS = {
    'technology': ['AI', 'machine learning', 'software', 'cloud', 'GPU', ...],
    'politics': ['election', 'government', 'policy', 'congress', ...],
    'business': ['market', 'company', 'investment', 'stock', ...],
    # ... etc
}

def classify_tweet(content):
    scores = {}
    words = content.lower().split()
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw.lower() in content.lower())
        scores[topic] = matches
    
    max_topic = max(scores, key=scores.get)
    max_score = scores[max_topic]
    confidence = min(max_score / len(content.split()), 1.0)  # normalize
    
    return max_topic, confidence
```

**Why keyword matching:**
- Fast (no model loading/inference)
- Transparent (operators can understand why a tweet was classified)
- Easy to maintain/update (just add/remove keywords)
- No external dependencies (no transformers, sklearn, etc)

## Data Model Changes

### Tweet Model Update

Add two fields to `Tweet` class in `app/models.py`:

```python
class Tweet(Base):
    # ... existing fields ...
    topic: Mapped[str] = mapped_column(String(32), default="other", index=True)
    topic_confidence: Mapped[float] = mapped_column(default=0.0)
```

## Implementation Strategy

### 1. Create Classifier Module

New file: `app/classifier.py`

```python
TOPIC_KEYWORDS = { ... }  # keyword dictionaries

def classify_tweet(content: str) -> tuple[str, float]:
    """Classify tweet content and return (topic, confidence)"""
    # keyword matching logic
```

### 2. Update Tweet Model

Modify `app/models.py`:
- Add `topic` field (string, default="other", indexed)
- Add `topic_confidence` field (float, default=0.0)
- Run database migration

### 3. Integrate Classification into Polling

Modify `app/tracker_service.py` in `poll_account()`:

```python
# When creating a new tweet:
topic, confidence = classify_tweet(item["content"])
tweet = Tweet(
    tweet_id=item["tweet_id"],
    account_id=account.id,
    content=item["content"],
    url=item["url"],
    tweet_created_at=item["tweet_created_at"],
    topic=topic,  # NEW
    topic_confidence=confidence,  # NEW
)
```

### 4. Update Dashboard

Modify `app/templates/index.html`:
- Add topic filter buttons/dropdown above tweets
- Show topic badge on each tweet
- Filter tweets list by selected topic
- JavaScript filter logic (client-side or server-side redirect)

### 5. Manual Override (Optional for v1)

Optionally add endpoint to manually change a tweet's topic:

```
POST /tweets/{tweet_id}/topic
- topic: new topic value
```

## Classification Accuracy Considerations

**Expected accuracy:** 70-80% for obvious topics, lower for ambiguous tweets

**Limitations:**
- Short tweets with no keyword matches → "other"
- Sarcasm/irony not detected
- Non-English tweets poorly classified
- Emerging topics/terms won't be recognized until keywords added

**Mitigations:**
- Keyword sets include variations/synonyms
- Confidence scoring shows uncertainty
- Manual override allows correction
- Easy to add new keywords

## Testing Strategy

1. **Unit tests** for classifier:
   - Test known tweets → verify correct classification
   - Test edge cases (empty, very short, gibberish)

2. **Integration tests**:
   - Poll a test account
   - Verify tweets stored with topic/confidence
   - Verify dashboard filter works

3. **Manual acceptance**:
   - Poll real accounts
   - Verify classifications look reasonable
   - Test dashboard filter UI

## Dependencies

- No new external dependencies (uses Python built-ins)
- Optional: `nltk` or `spacy` for future v2 (more sophisticated NLP)

## Performance Impact

- **Classification speed:** ~1ms per tweet (keyword matching)
- **Storage:** +36 bytes per tweet (topic string + confidence float)
- **Dashboard:** Negligible (filtering on indexed column)
- **Overall:** Minimal impact, safe to enable for all tweets
