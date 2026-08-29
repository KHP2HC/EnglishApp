import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from data.database import get_session as db_session
from data.models import ContentCache
import json

class ContentFetcher:
    SOURCES = {
        "british_council": [
            "https://learnenglish.britishcouncil.org/feeds/learnenglish",
            "https://learnenglish.britishcouncil.org/feeds/skill/listening",
        ],
        "bbc": [
            "https://www.bbc.co.uk/learningenglish/feeds/rss.xml",
        ],
        "voa": [
            "https://learningenglish.voanews.com/api/zy?format=xml",
        ],
    }

    def fetch_articles(self, difficulty="B1", max_age_days=7):
        db = db_session()
        cache = None
        try:
            cache = db.query(ContentCache).filter(
                ContentCache.content_type == "reading",
                ContentCache.difficulty_level == difficulty,
                ContentCache.fetched_at > datetime.utcnow() - timedelta(days=max_age_days)
            ).first()
        except Exception:
            cache = None
        if cache:
            return json.loads(cache.body) if hasattr(cache, 'body') else cache

        articles = []
        seen_urls = set()
        for source_name, urls in self.SOURCES.items():
            for url in urls:
                try:
                    resp = requests.get(url, timeout=20)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, "xml") if "xml" in resp.headers.get("Content-Type", "") else BeautifulSoup(resp.text, "html.parser")
                    items = soup.select("item, entry") or soup.select(".item")[:10]
                    for item in items[:5]:
                        title = (item.find("title") or item.find("h2") or item.find("a")).get_text(strip=True)
                        link = item.find("link")
                        link_url = link.get_text(strip=True) if link else (item.find("guid") or item.find("a")).get_text(strip=True)
                        if not link_url:
                            continue
                        if link_url in seen_urls:
                            continue
                        seen_urls.add(link_url)
                        body = self._extract_body(link_url)
                        if not body:
                            body = (item.find("description") or item.find("summary") or item.find("content") or item).get_text(" ", strip=True)
                        level = self._estimate_difficulty(body)
                        articles.append({"title": title, "body": body, "level": level, "source": source_name, "url": link_url})
                except Exception:
                    continue

        if not articles:
            articles = [{
                "title": "Official IELTS reading sample",
                "body": "The British Council and IELTS task sources provide a practical reading passage to build accuracy and time management. Read the passage carefully and answer the questions in one sitting.",
                "level": "B1",
                "source": "curated",
                "url": "https://www.ielts.org/"
            }]

        cache_entry = ContentCache(
            content_type="reading",
            source_url=", ".join(self.SOURCES.keys()),
            title="Latest Articles",
            body=json.dumps(articles),
            difficulty_level=difficulty,
            fetched_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        try:
            db.add(cache_entry)
            db.commit()
        except Exception:
            pass
        finally:
            try:
                db.close()
            except Exception:
                pass
        return articles

    def _extract_body(self, url):
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for selector in [".article-content", ".content", "article", "main"]:
                node = soup.select_one(selector)
                if node:
                    return " ".join(node.get_text(" ", strip=True).split())
        except Exception:
            return ""
        return ""

    def _estimate_difficulty(self, text: str):
        words = len(text.split())
        if words < 200:
            return "A2"
        if words < 400:
            return "B1"
        if words < 800:
            return "B2"
        return "C1"