import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import quote
from pydantic import BaseModel
import httpx
import re

app = FastAPI(title="WikiTrust Index Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WIKI_BASE = "https://sw.wikipedia.org/api/rest_v1/page/summary/"


class AnalyzeRequest(BaseModel):
    title: str


class AnalyzeResponse(BaseModel):
    title: str
    url: str | None
    ai_content_risk: float  # 0-1
    broken_links_count: int
    broken_external_links: list[str]
    content_type: str  # e.g., article, disambiguation, redirect
    total_links_internal: int
    total_links_external: int
    internal_links: list[str]
    external_links: list[str]
    categories: list[str]
    is_living: bool
    is_dead: bool
    death_year: int | None
    birth_year: int | None
    is_stub: bool
    ai_explanation: str


def estimate_ai_content_risk(text: str) -> float:
    if not text:
        return 0.0
    patterns = [
        r"As an AI language model",
        r"In conclusion,",
        r"This article aims to",
        r"It is important to note that",
    ]
    hits = sum(1 for p in patterns if re.search(p, text, flags=re.IGNORECASE))
    length_penalty = 0.0 if len(text) < 200 else min(0.3, len(text) / 5000)
    score = min(1.0, hits * 0.25 + length_penalty)
    return round(score, 2)


def count_broken_links(summary_json: dict) -> int:
    url = summary_json.get("content_urls", {}).get("desktop", {}).get("page")
    if not url:
        return 0
    # Heuristic: REST summary does not include references; treat missing page as broken.
    return 0


def detect_content_type(summary_json: dict) -> str:
    if summary_json.get("type"):
        t = summary_json["type"]
        if t == "standard":
            return "article"
        return t
    return "article"


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(WIKI_BASE + quote(req.title, safe=""))
        r.raise_for_status()
        data = r.json()

    ai_risk = estimate_ai_content_risk(data.get("extract", ""))
    broken = count_broken_links(data)
    content_t = detect_content_type(data)

    # MediaWiki Action API for links/categories
    page_title = data.get("title", req.title)

    async def query_with_continue(params: dict, list_key: str, subkey: str | None = None) -> list:
        """Fetch all pages with continuation and return flattened list of items under list_key/subkey."""
        base = {
            "action": "query",
            "format": "json",
            "formatversion": 2,
            "titles": page_title,
            "redirects": 1,
        }
        base.update(params)
        out: list = []
        async with httpx.AsyncClient(timeout=60) as c:
            cont: dict | None = None
            while True:
                req_params = base.copy()
                if cont:
                    req_params.update(cont)
                resp = await c.get("https://sw.wikipedia.org/w/api.php", params=req_params)
                resp.raise_for_status()
                js = resp.json()
                pages = js.get("query", {}).get("pages", [])
                if pages:
                    page = pages[0]
                    item = page.get(list_key, []) if subkey is None else page.get(list_key, {}).get(subkey, [])
                    if item:
                        out.extend(item)
                cont = js.get("continue")
                if not cont:
                    break
        return out

    # Internal links (namespace 0 only)
    links = await query_with_continue({"prop": "links", "plnamespace": 0, "pllimit": "max"}, "links")
    # External links
    extlinks = await query_with_continue({"prop": "extlinks", "ellimit": "max"}, "extlinks")
    # Categories (hide hidden)
    categories = await query_with_continue({"prop": "categories", "clshow": "!hidden", "cllimit": "max"}, "categories")

    cat_titles = [c.get("title", "") for c in categories]

    # Heuristics for living/dead/birth year/stub
    def extract_birth_year(cats: list[str]) -> int | None:
        for ct in cats:
            # Require explicit birth indicators to avoid matching death years
            m_sw = re.search(r"(?:Waliozaliwa|Kuzaliwa)\s+(\d{3,4})$", ct, flags=re.IGNORECASE)
            if m_sw:
                y = int(m_sw.group(1))
                if 1000 <= y <= 2100:
                    return y
            m_en = re.search(r"(\d{3,4})\s+births$", ct, flags=re.IGNORECASE)
            if m_en:
                y = int(m_en.group(1))
                if 1000 <= y <= 2100:
                    return y
        return None

    def has_death_year(cats: list[str]) -> tuple[bool, int | None]:
        for ct in cats:
            # Explicit death indicators only
            m_sw = re.search(r"(?:Waliofariki|Vifo vya)\s+(\d{3,4})$", ct, flags=re.IGNORECASE)
            if m_sw:
                y = int(m_sw.group(1))
                if 1000 <= y <= 2100:
                    return True, y
            m_en = re.search(r"(\d{3,4})\s+deaths$", ct, flags=re.IGNORECASE)
            if m_en:
                y = int(m_en.group(1))
                if 1000 <= y <= 2100:
                    return True, y
        return False, None

    def detect_living(cats: list[str]) -> bool:
        patterns = [r"Watu hai", r"Walio hai", r"Living people"]
        return any(re.search(p, ct, flags=re.IGNORECASE) for p in patterns for ct in cats)

    def detect_stub(cats: list[str]) -> bool:
        # Swahili stub categories: often contain 'mbegu' (seed) or 'stub'; include English fallback
        return any(re.search(r"mbegu|stub", ct, flags=re.IGNORECASE) for ct in cats)

    birth_year = extract_birth_year(cat_titles)
    dead, death_year = has_death_year(cat_titles)
    living = detect_living(cat_titles)
    is_stub = detect_stub(cat_titles)

    # Extract external link URLs (formatversion=2 returns dicts with 'url' or '*')
    ext_urls: list[str] = []
    for item in extlinks:
        if isinstance(item, str):
            ext_urls.append(item)
        elif isinstance(item, dict):
            if "url" in item:
                ext_urls.append(item["url"]) 
            elif "*" in item:
                ext_urls.append(item["*"])

    # Probe a subset of external links for broken status
    async def probe(url: str) -> bool:
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=8) as c:
                r = await c.head(url)
                if r.status_code in range(200, 400):
                    return False
                # Some sites reject HEAD; try GET with small read
                r = await c.get(url)
                return not (r.status_code in range(200, 400))
        except Exception:
            return True

    sample = ext_urls[:15]
    broken_checks = await asyncio.gather(*[probe(u) for u in sample]) if sample else []
    broken_urls = [u for u, bad in zip(sample, broken_checks) if bad]
    broken_from_ext = len(broken_urls)

    # Build a simple AI-style explanation
    parts = []
    if content_t == "article":
        parts.append("This appears to be a standard encyclopedia article.")
    else:
        parts.append(f"This page is a '{content_t}' page.")
    if birth_year:
        parts.append(f"The subject seems to have been born in {birth_year}.")
    if living:
        parts.append("Categories suggest the person is living.")
    if dead:
        parts.append("Categories indicate the subject is deceased.")
    if is_stub:
        parts.append("The article is categorized as a stub (mbegu); it may be incomplete.")
    parts.append(f"There are about {len(links)} internal links and {len(ext_urls)} external links.")
    if broken_from_ext:
        parts.append(f"At least {broken_from_ext} external link(s) appear broken.")
    if ai_risk >= 0.7:
        parts.append("Text shows a high risk of AI-generated patterns.")
    elif ai_risk >= 0.4:
        parts.append("Text shows a moderate risk of AI-generated patterns.")
    else:
        parts.append("Low indications of AI-generated phrasing in summary.")

    explanation = " ".join(parts)

    # Prepare link lists (unique, sorted, capped for payload safety)
    internal_titles = sorted({l.get("title", "") for l in links if isinstance(l, dict) and l.get("title")})
    internal_titles = [t for t in internal_titles if t][:200]
    external_list = sorted({u for u in ext_urls if isinstance(u, str) and u.startswith("http")})[:200]

    return AnalyzeResponse(
        title=data.get("title", req.title),
        url=data.get("content_urls", {}).get("desktop", {}).get("page"),
        ai_content_risk=ai_risk,
        broken_links_count=broken + broken_from_ext,
        content_type=content_t,
        total_links_internal=len(links),
        total_links_external=len(ext_urls),
        internal_links=internal_titles,
        external_links=external_list,
        broken_external_links=broken_urls,
        categories=cat_titles,
        is_living=bool(living and not dead),
        is_dead=bool(dead),
        death_year=death_year,
        birth_year=birth_year,
        is_stub=is_stub,
        ai_explanation=explanation,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


