from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set
from dotenv import load_dotenv
from scopus_client import ScopusClient
from db import upsert_candidates

ROOT = Path(__file__).parent

def _first(value: Any) -> Any:
    if isinstance(value, list):
        return value[0] if value else {}
    return value or {}

def parse_author_profile(payload: Dict[str, Any], source_query: str) -> Dict[str, Any]:
    response = payload.get("author-retrieval-response", [])
    profile = _first(response)
    core = profile.get("coredata", {}) or {}
    preferred = profile.get("author-profile", {}).get("preferred-name", {}) or {}

    affiliation = _first(profile.get("author-profile", {}).get("affiliation-current", {}).get("affiliation", {}))
    aff_name = affiliation.get("ip-doc", {}).get("afdispname") or affiliation.get("affiliation-name")
    country = affiliation.get("ip-doc", {}).get("address", {}).get("country")

    subject_items = profile.get("subject-areas", {}).get("subject-area", []) or []
    if isinstance(subject_items, dict):
        subject_items = [subject_items]
    subjects = ", ".join(
        sorted({str(item.get("$", "")).strip() for item in subject_items if item.get("$")})
    )

    author_id = str(core.get("dc:identifier", "")).replace("AUTHOR_ID:", "")
    h_index = int(core.get("h-index", 0) or 0)
    cited_by = int(core.get("cited-by-count", 0) or 0)
    doc_count = int(core.get("document-count", 0) or 0)
    current_doc_count = int(core.get("current-affiliation-document-count", 0) or 0)

    relevance = min(
        100.0,
        45 + min(h_index, 70) * 0.45 + min(current_doc_count, 50) * 0.25
    )

    return {
        "author_id": author_id,
        "full_name": preferred.get("indexed-name") or core.get("dc:title"),
        "given_name": preferred.get("given-name"),
        "surname": preferred.get("surname"),
        "affiliation": aff_name,
        "country": country,
        "h_index": h_index,
        "citation_count": cited_by,
        "document_count": doc_count,
        "current_doc_count": current_doc_count,
        "orcid": core.get("orcid"),
        "subject_areas": subjects,
        "source_query": source_query,
        "relevance_score": round(relevance, 1),
        "notes": "",
    }

def collect(query: str, max_documents: int, h_index_min: int) -> List[Dict[str, Any]]:
    client = ScopusClient()
    docs = client.search_documents(query, max_records=max_documents, view="COMPLETE")
    author_ids: Set[str] = set()
    for doc in docs:
        author_ids.update(client.extract_author_ids(doc))

    candidates: List[Dict[str, Any]] = []
    for i, author_id in enumerate(sorted(author_ids), start=1):
        try:
            row = parse_author_profile(client.retrieve_author(author_id), query)
            if row["h_index"] >= h_index_min:
                candidates.append(row)
                print(f"[{i}/{len(author_ids)}] {row['full_name']} — H={row['h_index']}")
        except Exception as exc:
            print(f"[{i}/{len(author_ids)}] gagal {author_id}: {exc}")

    upsert_candidates(candidates)
    return candidates

def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--query-name", default="veterinary_anatomic_pathology")
    parser.add_argument("--max-documents", type=int, default=150)
    parser.add_argument("--h-index-min", type=int, default=35)
    args = parser.parse_args()

    queries = json.loads((ROOT / "queries.json").read_text())
    if args.query_name not in queries:
        raise SystemExit(f"Query tidak ditemukan. Pilihan: {', '.join(queries)}")
    rows = collect(queries[args.query_name], args.max_documents, args.h_index_min)
    print(f"Selesai. {len(rows)} kandidat memenuhi ambang.")

if __name__ == "__main__":
    main()
