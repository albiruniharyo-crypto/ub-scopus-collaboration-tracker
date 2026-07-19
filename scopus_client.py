from __future__ import annotations
import os
import time
from typing import Any, Dict, Iterable, List, Optional
import requests

BASE_URL = "https://api.elsevier.com/content"

class ScopusAPIError(RuntimeError):
    pass

class ScopusClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        inst_token: Optional[str] = None,
        timeout: int = 45,
        max_retries: int = 4,
    ) -> None:
        self.api_key = api_key or os.getenv("ELSEVIER_API_KEY")
        self.inst_token = inst_token or os.getenv("ELSEVIER_INST_TOKEN")
        if not self.api_key:
            raise ValueError("ELSEVIER_API_KEY belum tersedia.")
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            "X-ELS-APIKey": self.api_key,
            "Accept": "application/json",
            "User-Agent": os.getenv("APP_NAME", "UB-Veterinary-Collaboration-Tracker"),
        })
        if self.inst_token:
            self.session.headers["X-ELS-Insttoken"] = self.inst_token

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{BASE_URL}/{endpoint.lstrip('/')}"
        for attempt in range(self.max_retries):
            response = self.session.get(url, params=params, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            if response.status_code in {429, 500, 502, 503, 504}:
                wait = min(2 ** attempt, 20)
                time.sleep(wait)
                continue
            detail = response.text[:1000]
            raise ScopusAPIError(
                f"Elsevier API error {response.status_code}: {detail}"
            )
        raise ScopusAPIError("Permintaan gagal setelah beberapa percobaan.")

    def search_documents(
        self,
        query: str,
        count: int = 25,
        max_records: int = 200,
        view: str = "STANDARD",
    ) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        start = 0
        count = min(max(count, 1), 200)

        while len(records) < max_records:
            payload = self._get("search/scopus", {
                "query": query,
                "start": start,
                "count": min(count, max_records - len(records)),
                "view": view,
            })
            search = payload.get("search-results", {})
            batch = search.get("entry", []) or []
            if not batch:
                break
            records.extend(batch)
            start += len(batch)
            total = int(search.get("opensearch:totalResults", 0) or 0)
            if start >= total:
                break
        return records[:max_records]

    def retrieve_author(self, author_id: str, view: str = "ENHANCED") -> Dict[str, Any]:
        return self._get(f"author/author_id/{author_id}", {"view": view})

    @staticmethod
    def extract_author_ids(document: Dict[str, Any]) -> List[str]:
        ids: List[str] = []
        authors = document.get("author", []) or []
        if isinstance(authors, dict):
            authors = [authors]
        for author in authors:
            aid = author.get("authid") or author.get("@auid")
            if aid:
                ids.append(str(aid))
        return ids
