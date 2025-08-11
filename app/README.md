# WikiTrust Index (Swahili-first)

A lightweight, Swahili-first Wikipedia article analyzer.

Frontend: Vue 3 + Vite + Bootstrap 5. Backend: FastAPI (Python). The app fetches a page summary from Swahili Wikipedia, computes heuristic AI-content risk, extracts categories, counts internal/external links, samples and checks external links for breakage, and surfaces a transparent explanation.

---

## Features
- Swahili Wikipedia focus (`sw.wikipedia.org`)
- Centered search and analysis flow
- Article card: title, summary, external link, trust score bar
- Live analysis panel:
  - AI content risk (percentage)
  - Content type
  - Internal/External link counts
  - Full internal/external links (clickable lists)
  - Categories list
  - Living/Deceased flags and Birth/Death year (from categories)
  - Broken links: sampled external URLs checked and listed
  - AI explanation (human-readable summary of findings)

---

## Tech Stack
- Frontend: Vue 3, Vite, Bootstrap 5, Bootstrap Icons, Axios
- Backend: FastAPI, Uvicorn, HTTPX
- OS target: Works on Windows (PowerShell), macOS, Linux

---

## Repository Layout
```
WikiTrust Index/
├─ app/                    # Vue 3 + Vite frontend
│  ├─ src/
│  │  ├─ components/
│  │  │  ├─ SearchBar.vue
│  │  │  ├─ ArticleCard.vue
│  │  │  ├─ TrustScoreBar.vue
│  │  │  ├─ AnalysisPanel.vue
│  │  │  └─ LinksList.vue
│  │  ├─ App.vue
│  │  ├─ main.js
│  │  └─ style.css
│  ├─ index.html
│  ├─ package.json
│  └─ vite.config.js
└─ server/                 # FastAPI backend
   ├─ main.py
   └─ requirements.txt
```

---

## Prerequisites
- Node.js 18+ and npm
- Python 3.11+

---

## Quickstart (Local)

### 1) Backend (FastAPI)
```powershell
cd server
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\uvicorn main:app --reload --port 8000
```
- Server at `http://127.0.0.1:8000`

### 2) Frontend (Vue + Vite)
```powershell
cd app
npm install
npm run dev
```
- Open Vite URL (typically `http://localhost:5173`)

---

## Using the App
1. Enter an article title in Swahili (e.g., "Tanzania", "Julius Nyerere")
2. Click "Fetch & Analyze"
3. Results show summary, Wikipedia link, Trust Score, analysis, and link lists

---

## API (Backend)
Base: `http://127.0.0.1:8000`

### POST `/analyze`
Request
```json
{ "title": "Article Name" }
```

Response (fields)
```json
{
  "title": "...",
  "url": "...",
  "ai_content_risk": 0.12,
  "broken_links_count": 2,
  "broken_external_links": ["https://..."],
  "content_type": "article",
  "total_links_internal": 12,
  "total_links_external": 13,
  "internal_links": ["..."],
  "external_links": ["..."],
  "categories": ["Jamii:..."],
  "is_living": true,
  "is_dead": false,
  "death_year": null,
  "birth_year": 1960,
  "is_stub": false,
  "ai_explanation": "This appears to be ..."
}
```

Notes
- `ai_content_risk` is heuristic (0–1). For stronger signals, integrate an LLM.
- Broken links are a sample of external URLs (up to 15) probed via HEAD/GET.
- Birth/Death detection uses Swahili/English category patterns.

---

## Configuration
- Frontend expects backend at `http://127.0.0.1:8000` (update in `app/src/App.vue` if needed)

---

## Production
- Frontend: `npm run build` → serve `app/dist`
- Backend: `uvicorn main:app --host 0.0.0.0 --port 8000`

---

## Contact / Maintainer
- Maintainer: AlvinDulle
- Email: alvinchipmunk196@gmail.com
- Phone/WhatsApp: +255-628-030-877

Markdown examples:
- Email: `[alvinchipmunk196@gmail.com](mailto:alvinchipmunk196@gmail.com)`
- Phone: `[+255-628-030-877](tel:+255628030877)`

---

## License
Add a `MIT`open sourcing.
