# Topic Classification System Implementation Tasks

## Phase 1: Core Classifier

### Task 1: Create Classifier Module
- [ ] Create `app/classifier.py` with TOPIC_KEYWORDS dictionary
- [ ] Include keywords for all 10 topics (technology, politics, business, sports, entertainment, science, health, social, crypto, other)
- [ ] Implement `classify_tweet(content: str) -> tuple[str, float]` function
- [ ] Test function with sample tweets:
  - `"Just deployed a new ML model to production"` → technology
  - `"Congress votes on new healthcare law"` → politics
  - `"Stock market hits all-time high"` → business
- [ ] Manual verification: Run classifier on 10 diverse tweets, verify reasonable classifications

### Task 2: Update Tweet Model
- [ ] Add `topic: Mapped[str]` field to Tweet class in `app/models.py`
  - String, default="other", indexed for filtering performance
- [ ] Add `topic_confidence: Mapped[float]` field
  - Float between 0.0 and 1.0, default=0.0
- [ ] Manual verification: 
  - Check schema is correct: `sqlite3 data/tracker.db ".schema tweets"`
  - Verify both new columns exist with correct types

## Phase 2: Integration

### Task 3: Integrate Classification into Polling
- [ ] Modify `app/tracker_service.py` in `poll_account()` function
- [ ] Import classifier: `from app.classifier import classify_tweet`
- [ ] When creating a new tweet, call classifier:
  ```python
  topic, confidence = classify_tweet(item["content"])
  tweet = Tweet(
      # ... existing fields ...
      topic=topic,
      topic_confidence=confidence,
  )
  ```
- [ ] Manual verification:
  - Start app (uvicorn or docker)
  - Poll a test account
  - Check database: `sqlite3 data/tracker.db "SELECT content, topic, topic_confidence FROM tweets LIMIT 5;"`
  - Verify all tweets have topic assigned and confidence > 0

### Task 4: Update Dashboard Template
- [ ] Modify `app/templates/index.html` to show topics
- [ ] Add topic filter controls above tweet list:
  - [ ] Dropdown or button group with all 10 topic options
  - [ ] "All topics" default selection
  - [ ] Display selected topic filter state
- [ ] Show topic on each tweet:
  - [ ] Add topic badge/label next to each tweet
  - [ ] Show confidence as visual indicator (color/opacity) or tooltip
- [ ] Implement filter logic:
  - [ ] JavaScript to filter tweet display by topic on client-side, OR
  - [ ] Add `?topic=technology` query param and filter server-side
- [ ] Manual verification:
  - Open dashboard
  - Verify topic badges appear on all tweets
  - Test filter: select "Technology" → only tech tweets show
  - Test filter: select "Other" → only other tweets show
  - Test filter: select "All" → all tweets show
  - Check that tweet count updates correctly when filtering

## Phase 3: Refinement

### Task 5: Optimize Keyword Dictionary
- [ ] Review classifications from Task 3 verification
- [ ] Identify any obvious misclassifications
- [ ] Add missing keywords or remove overly broad keywords
- [ ] Test edge cases:
  - [ ] Very short tweets (< 5 words)
  - [ ] Tweets with only URLs/links
  - [ ] All-caps text
  - [ ] Hashtag-heavy tweets
- [ ] Rerun polling with updated keywords
- [ ] Manual verification:
  - Poll 20+ tweets
  - Review dashboard
  - Verify classifications improved

### Task 6: Add Manual Override (Optional)
- [ ] Option A: Add web UI to edit topic manually
  - [ ] Add "edit topic" button on each tweet in dashboard
  - [ ] Pop-up or inline select to choose new topic
  - [ ] Save to database via new endpoint
- [ ] Option B: Skip for v1, document as future enhancement
- [ ] If implementing, manual verification:
  - Click edit on a tweet
  - Change topic
  - Verify change persists after page reload

## Phase 4: Testing & Validation

### Task 7: Comprehensive Dashboard Testing
- [ ] Start app with sample data (poll 2-3 real accounts)
- [ ] Test complete user flow:
  - [ ] Open dashboard → see topics on tweets
  - [ ] Click topic filter → tweets update correctly
  - [ ] Add new account during session → new tweets classified
  - [ ] Run "Check now" → new tweets appear with topics
  - [ ] Switch topics → counts and display correct
- [ ] Test data integrity:
  - [ ] Check no tweets missing topic: `sqlite3 data/tracker.db "SELECT COUNT(*) FROM tweets WHERE topic IS NULL;"`
  - [ ] Should return 0
- [ ] Test performance:
  - [ ] Dashboard loads within 1-2 seconds with 100+ tweets
  - [ ] Filter switching is instant

### Task 8: Error Handling & Edge Cases
- [ ] Test very short/empty tweet content
  - [ ] Verify classified as "other" gracefully
- [ ] Test non-English content
  - [ ] Verify classified reasonably (may fall to "other")
- [ ] Test special characters/Unicode
  - [ ] Verify classifier doesn't crash
- [ ] Test all 10 topics represented
  - [ ] Add test tweets that should match each topic
  - [ ] Verify at least one tweet per topic shows in dashboard
- [ ] Manual verification: No errors in logs, dashboard displays all variations

## Final Verification

### Step 1: Clean State Test
```bash
# Backup and clear database
cp data/tracker.db data/tracker.db.backup
# Clear tweets table: sqlite3 data/tracker.db "DELETE FROM tweets;"
```

### Step 2: Fresh Poll & Classify
```bash
# Start app
docker-compose up  # or: uvicorn app.main:app --reload

# Poll real accounts to generate fresh classifications
# (via dashboard "Check now" button)
```

### Step 3: Dashboard Validation
1. Open http://localhost:8000
2. Verify all tweets have topic badges
3. Test each topic filter:
   - Technology → see tech tweets
   - Politics → see political tweets
   - Sports → see sports tweets
   - etc.
4. Verify counts change correctly
5. Verify can switch between topics smoothly

### Step 4: Data Validation
```bash
# Check all tweets classified
sqlite3 data/tracker.db "SELECT topic, COUNT(*) as count FROM tweets GROUP BY topic;"

# Check confidence scores reasonable (should be 0-1)
sqlite3 data/tracker.db "SELECT MIN(topic_confidence), MAX(topic_confidence), AVG(topic_confidence) FROM tweets;"

# Check no NULL topics
sqlite3 data/tracker.db "SELECT COUNT(*) FROM tweets WHERE topic IS NULL;"  # Should be 0
```

## Definition of Done

- [x] Classifier module created with keyword dictionaries
- [ ] Tweet model updated with topic fields
- [ ] Classification integrated into polling
- [ ] Dashboard displays topics with filtering
- [ ] Keyword dictionary optimized for accuracy
- [ ] Manual override implemented (if v1 scope)
- [ ] Comprehensive testing passed
- [ ] Error handling for edge cases
- [ ] No regressions in existing features
- [ ] Performance acceptable (< 100ms added per poll)

## Success Metrics

- ✓ 100% of tweets assigned a topic (no NULLs)
- ✓ Topic distribution reasonable (not all "other")
- ✓ Dashboard filter works reliably
- ✓ Accuracy appears ≥70% on manual review
- ✓ No performance regression on polling or UI
