# Topic Classification System Proposal

## What We're Building

Implement an intelligent topic classification system that automatically analyzes tweets and categorizes them into predefined topics (e.g., technology, politics, sports, finance, entertainment, etc.), enabling operators to browse and filter tweets by topic.

## Why It Matters

As the Twitter Tracker accumulates tweets from multiple accounts, finding tweets of interest becomes difficult without organization. A topic classification system adds a powerful dimension to discover and focus on relevant content:

- **Content Discovery:** Find tweets about specific topics without manual reading
- **Trend Analysis:** Identify which topics are most active across tracked accounts
- **Filtering:** Show only tweets matching operator interests
- **Insights:** Understand what topics the tracked accounts focus on

## Scope

### In Scope

- **Automatic tweet classification** using lightweight NLP/keyword matching on tweet content
- **Predefined topic categories** (e.g., Tech, Politics, Business, Sports, Entertainment, Health, Science, Other)
- **Topic storage** - persist classification with each tweet
- **Dashboard filtering** - allow operators to view tweets by topic
- **Confidence scoring** - optionally mark uncertain classifications
- **Reclassification** - allow manual override of automatic classification

### Out of Scope

- Dynamic topic discovery/clustering (use fixed categories)
- Complex machine learning models (start with keyword matching/TF-IDF)
- Real-time topic trending charts
- Multi-language support (assume English for v1)
- Fine-grained sub-topics

## Risk Assessment

**No X Terms of Service concerns**: Classifying public tweets locally violates no policies.

**No performance concerns**: Lightweight keyword-based classification is fast enough to run during polling.

**Data considerations**: Adds one text column (topic) and optional float (confidence) to tweets table.

## Success Criteria

- Every tweet is assigned a topic category automatically on storage
- Dashboard shows topic filter controls
- Operators can filter by topic
- Classification is reasonably accurate (≥70% for obvious topics)
- Manual override capability for misclassified tweets
- System gracefully handles edge cases (very short tweets, non-English content)
