"""Tweet topic classifier using keyword-based matching."""

TOPIC_KEYWORDS = {
    'technology': [
        'AI', 'artificial intelligence', 'machine learning', 'software', 'hardware',
        'startup', 'programming', 'code', 'development', 'app', 'cloud', 'GPU',
        'neural', 'algorithm', 'database', 'server', 'API', 'framework', 'library',
        'python', 'javascript', 'java', 'react', 'django', 'flask', 'node', 'crypto',
        'blockchain', 'web3', 'tech', 'innovation', 'digital', 'cyber', 'data',
        'engineering', 'infrastructure', 'devops', 'docker', 'kubernetes', 'aws',
        'azure', 'gcp', 'silicon', 'chip', 'gpu', 'processing', 'computing'
    ],
    'politics': [
        'election', 'government', 'policy', 'law', 'congress', 'senate', 'representative',
        'president', 'politician', 'political', 'vote', 'voting', 'campaign', 'debate',
        'legislation', 'bill', 'parliament', 'minister', 'cabinet', 'state', 'federal',
        'democrat', 'republican', 'conservative', 'liberal', 'progressive', 'reform',
        'executive', 'judicial', 'treaty', 'diplomacy', 'foreign policy', 'alliance',
        'war', 'conflict', 'peace', 'negotiation', 'administration', 'mandate'
    ],
    'business': [
        'market', 'stock', 'company', 'business', 'investment', 'investor', 'fund',
        'financial', 'economy', 'economic', 'profit', 'revenue', 'earnings', 'quarter',
        'earnings call', 'merger', 'acquisition', 'IPO', 'valuation', 'shares', 'bond',
        'dividend', 'portfolio', 'trade', 'commerce', 'industry', 'corporate', 'enterprise',
        'startup', 'venture', 'capital', 'private equity', 'hedge fund', 'banking',
        'loan', 'credit', 'debt', 'interest', 'rate', 'retail', 'supply chain'
    ],
    'sports': [
        'game', 'team', 'player', 'coach', 'sport', 'sports', 'championship', 'tournament',
        'league', 'football', 'baseball', 'basketball', 'hockey', 'soccer', 'rugby',
        'tennis', 'golf', 'olympics', 'medal', 'athlete', 'competition', 'match',
        'winning', 'score', 'goal', 'touchdown', 'home run', 'season', 'playoff',
        'draft', 'trade', 'contract', 'performance', 'stats', 'record', 'fan'
    ],
    'entertainment': [
        'movie', 'film', 'music', 'singer', 'actor', 'actress', 'celebrity', 'show',
        'entertainment', 'premiere', 'release', 'album', 'song', 'concert', 'festival',
        'hollywood', 'broadway', 'netflix', 'streaming', 'television', 'tv', 'series',
        'episode', 'character', 'director', 'producer', 'screenplay', 'production',
        'award', 'oscar', 'grammy', 'emmy', 'golden globe', 'box office', 'blockbuster'
    ],
    'science': [
        'research', 'science', 'scientific', 'discovery', 'space', 'nasa', 'astronomy',
        'physics', 'chemistry', 'biology', 'medicine', 'study', 'experiment', 'theory',
        'scientist', 'laboratory', 'data', 'analysis', 'findings', 'journal', 'publication',
        'breakthrough', 'innovation', 'technology', 'evolution', 'universe', 'planet',
        'galaxy', 'atom', 'molecule', 'dna', 'gene', 'climate', 'environment'
    ],
    'health': [
        'health', 'healthcare', 'medical', 'medicine', 'doctor', 'hospital', 'patient',
        'disease', 'illness', 'vaccine', 'vaccination', 'treatment', 'therapy', 'wellness',
        'fitness', 'exercise', 'diet', 'nutrition', 'mental health', 'depression', 'anxiety',
        'pharmacy', 'prescription', 'drug', 'virus', 'pandemic', 'epidemic', 'symptom',
        'diagnosis', 'cure', 'prevention', 'cancer', 'heart', 'brain', 'covid'
    ],
    'social': [
        'social', 'community', 'activism', 'activist', 'protest', 'movement', 'justice',
        'rights', 'equality', 'discrimination', 'racism', 'sexism', 'lgbtq', 'feminism',
        'human rights', 'civil rights', 'immigration', 'refugee', 'poverty', 'inequality',
        'education', 'school', 'university', 'reform', 'advocacy', 'nonprofit', 'charity',
        'volunteer', 'donate', 'cause', 'awareness', 'campaign', 'solidarity'
    ],
    'crypto': [
        'cryptocurrency', 'bitcoin', 'ethereum', 'crypto', 'blockchain', 'web3', 'defi',
        'nft', 'token', 'coin', 'altcoin', 'dogecoin', 'cardano', 'solana', 'ripple',
        'wallet', 'exchange', 'trading', 'mining', 'hash', 'transaction', 'ledger',
        'smart contract', 'dapp', 'stake', 'yield', 'liquidity', 'pump', 'dump',
        'bull', 'bear', 'hodl', 'fomo', 'bullish', 'bearish', 'volatility'
    ],
    'other': []
}


def classify_tweet(content: str) -> tuple[str, float]:
    """
    Classify tweet content and return (topic, confidence).

    Args:
        content: Tweet text to classify

    Returns:
        Tuple of (topic: str, confidence: float) where confidence is 0.0-1.0
    """
    if not content or not content.strip():
        return 'other', 0.0

    content_lower = content.lower()
    scores = {}

    for topic, keywords in TOPIC_KEYWORDS.items():
        if not keywords:
            scores[topic] = 0
            continue

        matches = sum(1 for keyword in keywords if keyword.lower() in content_lower)
        scores[topic] = matches

    max_topic = max(scores, key=scores.get)
    max_score = scores[max_topic]

    if max_score == 0:
        return 'other', 0.0

    word_count = len(content_lower.split())
    confidence = min(max_score / (word_count * 0.1) if word_count > 0 else 0, 1.0)

    return max_topic, confidence
