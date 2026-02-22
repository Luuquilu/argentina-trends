"""
Topic clustering with BERTopic.
"""
import logging
logger = logging.getLogger(__name__)

def cluster_posts(posts, min_topic_size=5):
    if len(posts) < min_topic_size * 2: return posts, {}
    try:
        from bertopic import BERTopic
        from sentence_transformers import SentenceTransformer
        docs = [f"{ p.get('title','')} {p.get('body','')}"[:512] for p in posts]
        em = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
        model = BERTopic(embedding_model=em,min_topic_size=min_topic_size,language="multilingual",verbose=False)
        topics,_ = model.fit_transform(docs)
        meta = {}
        for _,row in model.get_topic_info().iterrows():
            tid=row["Topic"]
            if tid==-1: continue
            words=[x for x,_ in model.get_topic(tid)[:8]]
            meta[tid]={"label":" | ".join(words[:3]),"keywords":words,"count":int(row["Count"])}
        return [{**p,"topic_id":int(t)} for p,t in zip(posts,topics)],meta
    except Exception as e:
        logger.error(f"Topic clustering error: {e}")
        return posts,{}
