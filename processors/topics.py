"""
Topic clustering with BERTopic — with Spanish stop-word filtering.
"""
import logging
logger = logging.getLogger(__name__)

# Spanish stop words (most frequent function words that add no topic signal)
SPANISH_STOPWORDS = {
    "de","la","el","en","y","a","los","del","se","las","un","por","con","una",
    "su","para","es","al","lo","como","más","o","pero","sus","le","ya","o",
    "fue","hay","han","ha","he","no","que","este","esta","esto","son","ser",
    "si","también","sobre","entre","cuando","muy","sin","todo","esta","https",
    "com","www","via","co","rt","pic","twitter","youtube","instagram","facebook",
    "argentina","argentino","argentinos","argentina's","arg","arg.",
}

def cluster_posts(posts, min_topic_size=5):
    if len(posts) < min_topic_size * 2:
        return posts, {}
    try:
        from bertopic import BERTopic
        from sentence_transformers import SentenceTransformer
        from sklearn.feature_extraction.text import CountVectorizer

        docs = [f"{p.get('title', '')} {p.get('body', '')}"[:512] for p in posts]

        em = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")

        # CountVectorizer with stop-word list for cleaner topics
        vectorizer = CountVectorizer(
            stop_words=list(SPANISH_STOPWORDS),
            ngram_range=(1, 2),
            min_df=2,
        )

        model = BERTopic(
            embedding_model=em,
            vectorizer_model=vectorizer,
            min_topic_size=min_topic_size,
            language="multilingual",
            verbose=False,
        )

        topics, _ = model.fit_transform(docs)

        meta = {}
        for _, row in model.get_topic_info().iterrows():
            tid = row["Topic"]
            if tid == -1:
                continue
            # Filter stop words from labels one more time
            words = [
                w for w, _ in model.get_topic(tid)[:10]
                if w.lower() not in SPANISH_STOPWORDS and len(w) > 2
            ]
            if not words:
                words = [str(tid)]
            meta[tid] = {
                "label": " | ".join(words[:3]),
                "keywords": words[:8],
                "count": int(row["Count"]),
            }

        return [{**p, "topic_id": int(t)} for p, t in zip(posts, topics)], meta

    except Exception as e:
        logger.error(f"Topic clustering error: {e}")
        return posts, {}
