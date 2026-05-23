# OptiLoc HK — Claude Project Context

> **This file is the canonical handoff. Add it to Project knowledge so every new chat in this Project starts with full context. Update it whenever a session meaningfully changes the project state.**

---

## TL;DR for new chats

OptiLoc HK is a Hong Kong facility location optimizer being built by **Kaito Ishiguro**, a 2nd-year IELM student at HKU. It applies the math from his DASE2135 course (Mathematical Optimization, Spring 2026, Dr. Y.H. Kuo) to real HK demographic data. Public GitHub repo:

**https://github.com/Kaito-ishiguro/optiloc-hk**

**Current phase:** Phase 1 active. Sessions 001–017 complete (solver pipeline, OZP zoning, k-median network, Dockerized FastAPI, Cloud Run deploy, road-network distance integration, Cloud Build CI/CD). **Session 015 shipped: container is live on Cloud Run at `https://optiloc-api-809774362984.asia-east2.run.app/docs`. Session 016 shipped: road-network Weber and k-median solvers (files 21–23), file-16 lazy-load refactor. Session 017 shipped: Cloud Build CI/CD pipeline — every push to main now auto-builds and deploys.** Next: Session 018 landing page v1. The canonical product/business plan is **`docs/ROADMAP.md`** (commit `57b630d`). Companion to CONTEXT.md (technical handoff) and MATH.md (mathematical reference). The DASE2135 final exam was on May 11, 2026 (in the past). Prof. Kuo has emailed back acknowledging the project and offering UG research collaboration. **FWD Group internship starts June 8, 2026.** Kaito plans to maintain ~1-3 sessions/day through the internship. Kaito is studying for the **Google Cloud Associate Cloud Engineer (ACE) certification** and has ~HKD 2,000 (~USD 255) in free GCP trial credit (project `ace-prep-496408`).

**The immediate pending task at the start of this new chat: Session 018 — landing page v1.**

---

## End-of-session protocol (MANDATORY — follow exactly)

When Kaito says **"wrap up this session"** or **"log this"**, do these four things in order:

**1. Generate the JOURNAL.md entry** following the standard template (see "Journaling workflow" below). Always output it in a single copy-pasteable code block.

**2. Tell him to paste it into JOURNAL.md and commit:**
> Paste the entry above at the bottom of your `JOURNAL.md`, save it, then commit:
> ```
> git add <files-from-this-session> JOURNAL.md
> git commit -m "Session NNN: <short description>"
> git push
> ```

**3. Always ask the chat-switch question.** After he confirms the commit, ALWAYS ask:

> *"This chat is now [N messages / has covered X sessions / has crossed a major milestone]. Do you want to switch to a new chat in the OptiLoc HK Project? If yes, I'll generate an updated CONTEXT.md with the latest project state and walk you through re-uploading it to Project knowledge."*

Use judgment on whether to recommend switching. Recommend YES if:
- The chat has covered 2+ full sessions
- A major milestone just closed
- The chat is over ~50 messages long
- Claude has started showing signs of context strain

Recommend NO (or "your call") if:
- Only one short session has happened
- We're mid-flow on something that benefits from immediate context

**4. If he says yes to switching, generate a fresh CONTEXT.md as a downloadable file** with all updates, then walk him through:
1. `Move-Item $HOME\Downloads\CONTEXT.md . -Force`
2. `git add CONTEXT.md`, commit, push
3. Delete old CONTEXT.md from Project knowledge, upload new version
4. Start new chat with *"Where are we and what's next?"* or *"Session NNN: <direction>"*

---

## How to work with Kaito

### Step-by-step rhythm for terminal work

**Give ONE step at a time and wait for him to reply "done" (or paste any errors) before giving the next step.** He uses Windows and hits platform-specific errors. Single-step rhythm only.

### Teaching style

- Learns through visual and interactive examples connecting math to real applications.
- Likes full hand-derivations when learning new math.
- Treat failures as pedagogical — he values seeing real failure modes.
- Honest engineering feedback over hype. Tell him when an idea is harder than it looks.
- **The math-concept-tutor skill** at `/mnt/skills/user/math-concept-tutor/SKILL.md` is canonical for any new math concept.
- Real-world interpretation matters as much as math.

### Journaling workflow

```
## Session NNN — YYYY-MM-DD — [3-word title]

**What I built / learned**
- 2-4 concrete bullets

**Key insight or aha moment**
One paragraph.

**What I got stuck on**
Honest.

**Next session's first move**
One concrete specific action.

**Time spent / mood**
Optional.
```

Optional bonus: **Real-world meaning of the output** when deployment-relevant result shipped.

Journal lives in `JOURNAL.md`. Commit messages: `Session NNN: <short description>`.

**Journal entries always output in a single copy-pasteable code block.**

### Formatting preferences

- Prose by default in conversation. Bullets/tables for structured content.
- Math: LaTeX inline (`$...$`) or display (`$$...$$`).
- Be concise by default. Token efficiency matters.
- He uses VS Code as his editor.

### Security posture

Proportional security, not maximal. Phase 1 is a public portfolio asset. Skip items wrong for this stage.

---

## About Kaito

- 2nd-year BEng IELM, HKU, Class of 2028. Concentration: Intelligent Systems and Automation.
- Languages: native English and Japanese; conversational Mandarin; basic functional Thai. **Do NOT claim Cantonese in any documents.**
- Based between Hong Kong and Kochi, Japan.
- Top-30 nationally ranked tennis player (Thailand U18).
- Short-term goal: Hong Kong PR after graduation.
- Long-term goals: support two future children's NYU tuition; own apartments in HK and Japan; retire to renovated grandparents' house in Kochi.
- Has Claude Pro and Gemini Pro.
- **FWD Group internship** starts June 8, 2026.
- DASE2135 final exam done (May 11, 2026).
- **Studying for Google Cloud ACE certification.** GCP project: `ace-prep-496408`, region: `asia-east2`.
- **Primary goal:** gain repeatable experience pitching and connecting with operational decision-makers. **Enjoys cold outreach** — Claude should tell him when to send DMs.

---

## The project at a glance

OptiLoc's pipeline ingests WorldPop raster → 41,288 weighted demand points (population 7,496,988) → solves Weber and k-median facility-location variants → visualizes as Folium maps or matplotlib galleries. Solvers exposed over HTTP via containerized FastAPI, live on Cloud Run. Every push to main auto-deploys via Cloud Build.

---

## Codebase reference — file by file

### CI/CD layer (Session 017)

#### `cloudbuild.yaml`
3-step pipeline: docker build → push to Artifact Registry → gcloud run deploy. Flags: `--max-instances=3`, `--port=8000`, `--allow-unauthenticated`, region `asia-east2`. Image tagged with `$COMMIT_SHA`.

#### Cloud Build trigger `deploy-on-push`
Region: asia-east2. Event: push to `^main$`. Ignored files: `README.md,JOURNAL.md,CONTEXT.md,docs/**`. Config: `cloudbuild.yaml`. SA: `cloudbuild-deployer@ace-prep-496408.iam.gserviceaccount.com`.

#### Service account `cloudbuild-deployer`
Roles: Artifact Registry Writer, Cloud Run Developer, Service Account User, Logs Writer, Storage Admin.

### API + container layer (Sessions 014–015)

#### `api/__init__.py`
`__version__ = "0.1.0"`.

#### `api/config.py`
Paths, security limits, solver defaults. `MAX_K=25`, `MAX_RESTARTS=20`. Rate limit: `5/minute`. Timeouts: Weber 30s, k-median 180s.

#### `api/models.py`
Pydantic v2 request/response schemas with bounded inputs.

#### `api/solvers.py`
Loads files 08 and 16 via importlib. Caches graph + demand data at startup. File 16 geopandas import is lazy.

#### `api/main.py`
FastAPI app. Endpoints: `GET /healthz`, `POST /solve_weber`, `POST /solve_kmedian_ozp`, `GET /docs`, `GET /redoc`. CORS open, slowapi rate limiter, asyncio timeouts, sanitized 500s.

#### `api/requirements.txt`
fastapi, uvicorn, slowapi, numpy, scipy, pandas, shapely, geopandas, pyogrio, pyproj.

#### `Dockerfile`
Single-stage, `python:3.14-slim`. Non-root `appuser`, HEALTHCHECK, exposes 8000.

#### `.dockerignore`
Allow-list pattern. Build context 3.69 MB.

### Notebooks (01–23)

- **01** — WorldPop ingest → `demand_points.csv` (41,288 points)
- **02** — HK population heatmap
- **03** — Unconstrained Weber. GD + Newton + BFGS. Optimum: Sham Shui Po (114.17071, 22.33729)
- **03_multi** — 4 starting points, backtracking line search
- **04** — 8 convergence trails visualization
- **05** — KKT-constrained Weber (OSM Kowloon + MTR + competitor exclusion). SLSQP. Optimum: (114.17323, 22.34038)
- **06** — Constrained map visualization
- **07** — Hessian condition number across HK. κ: 1.24–3.25
- **08** — Weiszfeld + 4-solver comparison. All converge to 10⁻⁹ degrees. **Imported by API.**
- **09** — Four-solver convergence map
- **10** — ArcGIS OZP fetch. 11,963 polygons
- **11** — Filter to 590 C+CDA, union → 499-piece MultiPolygon (10.30 km²)
- **12** — Weber constrained to OZP commercial. Optimum: (114.16944, 22.33321)
- **13** — OZP-constrained map
- **14** — k-median (k=5, 10 restarts). Best obj 274,830 = 59.1% reduction
- **15** — k=5 k-median map with Voronoi
- **16** — OZP-constrained k-median. Best obj 277,595 = +1.0% penalty. Lazy geopandas import. **Imported by API.**
- **17** — OZP k-median map
- **18** — k-sweep k∈{3,5,8,10,15,20}. Elbow at k≈8–10
- **19** — Diminishing-returns chart
- **20** — 2×3 hub-location gallery
- **21** *(Session 016)* — Road network prep. HK driving network (18,820 nodes, 35,848 edges). Snaps 41,288 demand points → 12,513 unique nodes
- **22** *(Session 016)* — Road-network Weber. Optimum: (22.32462, 114.18873), 2.33 km SE of Euclidean. Avg 12,831 m/resident
- **23** *(Session 016)* — Road k-median (k=5). Best: 5,852 m/resident, 54.4% reduction. 24% obj gap across 3 restarts

---

## Tech stack

- **Language:** Python 3.14
- **Env:** `.venv/`, activate via `.venv\Scripts\Activate.ps1`
- **Numerical:** NumPy, SciPy (BFGS, SLSQP)
- **Geographic:** rasterio, osmnx 2.1.0, shapely, GeoPandas, pyogrio, pyproj, scikit-learn 1.8.0
- **Visualization:** Folium, matplotlib
- **API:** FastAPI 0.136.1 + Uvicorn 0.47.0 + Pydantic 2.13.4 + slowapi 0.1.9
- **Container:** Docker Desktop 4.67.0, `python:3.14-slim`, linux/amd64
- **Cloud:** GCP `ace-prep-496408`, `asia-east2`. Artifact Registry `optiloc`. Cloud Run `optiloc-api`. URL: `https://optiloc-api-809774362984.asia-east2.run.app`
- **CI/CD:** Cloud Build trigger `deploy-on-push`, SA `cloudbuild-deployer`
- **VCS:** Git, GitHub `github.com/Kaito-ishiguro/optiloc-hk`

---

## Environment specifics (Windows quirks)

- Smart App Control disabled (Session 002)
- `mkdir -p` doesn't work → use `New-Item -ItemType Directory -Force`
- Always use `python -m pip install ...`
- `Move-Item` with `-Force` if destination exists
- `&&` invalid in PowerShell → use `;`
- Multi-line string edits → use Python helper script
- Activate venv first: `cd "C:\Users\Kaito Ishiguro\Documents\optiloc-hk"` then `.venv\Scripts\Activate.ps1`
- Use `Invoke-RestMethod` not `curl`
- Docker Desktop must be running for docker commands
- LF→CRLF warnings from Git are harmless
- VS Code is his editor — he creates files there rather than via PowerShell when possible

---

## Where we are right now

**Session 017 is shipped.** CI/CD pipeline complete and verified:

- `cloudbuild.yaml` with `--max-instances=3`, `--port=8000`
- `deploy-on-push` trigger firing on push to main
- `cloudbuild-deployer` SA with least-privilege roles
- All Dockerfile dependencies committed to git
- Live API confirmed: `https://optiloc-api-809774362984.asia-east2.run.app/docs`

**Key lesson from Session 017:** Cloud Build clones the repo fresh every time. Every file the Dockerfile COPYs must be committed to git. Local Docker builds hide this gap because local files exist regardless of git status.

**Next up: Session 018 — landing page v1.** Fetch ROADMAP.md first to confirm spec.

---

## Session history (compressed)

- **001** — Project genesis. Weber facility location scoped.
- **002** — WorldPop ingestion. 41k demand points.
- **003** — GD + Newton + BFGS solvers. Optimum: Sham Shui Po.
- **004** — Multi-start visualization. Backtracking line search.
- **005** — KKT-constrained SLSQP. Constrained optimum: Beacon Hill.
- **006** — README + Phase 1 shipped. LinkedIn post.
- **007** — Condition number analysis. κ: 1.24–3.25.
- **Email from Prof. Kuo** — UG research collaboration offered.
- **008+009** — Weiszfeld + four-solver comparison. 10⁻⁹ degree convergence.
- **010** — OZP commercial zoning. 590 C+CDA, 499-piece MultiPolygon.
- **010b** — SLSQP buffer-smoothness fix.
- **011** — k-median + Voronoi. k=5. 59.1% reduction.
- **012** — OZP-constrained k-median. +1.0% penalty. MATH.md extracted.
- **Inter-session 2026-05-22** — Strategic pivot. ROADMAP.md shipped.
- **013** — k-sweep k∈{3,5,8,10,15,20}. Elbow k≈8–10.
- **014** — FastAPI + Docker. Local validation.
- **015** — Cloud Run deploy. Live API.
- **016** — Road-network solvers (files 21–23). Road Weber: 2.33 km shift. Road k-median: 5,852 m/resident.
- **017** — Cloud Build CI/CD. `cloudbuild.yaml`, trigger, SA. Auto-deploy on push to main. Key lesson: all Dockerfile COPY targets must be in git.

---

## Files in Git (after Session 017)

README.md, JOURNAL.md, CONTEXT.md, docs/MATH.md, docs/ROADMAP.md, requirements.txt, .gitignore, LICENSE, cloudbuild.yaml, notebooks/01–23, docs/maps/*.png (13 screenshots), data/raw/.gitkeep, data/processed/.gitkeep, **data/processed/demand_points.csv**, **data/processed/ozp_commercial_union.geojson**, api/__init__.py, api/config.py, api/models.py, api/solvers.py, api/main.py, api/requirements.txt, .dockerignore, Dockerfile.

## Files NOT in Git

- `data/raw/hkg_ppp_2020_UNadj_constrained.tif`
- `data/processed/ozp_all_zones.geojson` (~120 MB)
- `data/processed/hk_road_network.graphml`
- `data/processed/demand_points_road.csv`
- `data/processed/demand_nodes_aggregated.csv`
- `docs/maps/*.html`
- `.venv/`

---

## Triggers and protocols

- **"wrap up this session"** / **"log this"** → journal entry in code block + chat-switch question
- **"let's start session NNN"** → proceed directly into work
- **"don't include this in the file but tell me..."** → thorough technical debrief outside journal
- **Terminal commands** → ONE step at a time
- **New math concept** → math-concept-tutor skill
- **Math grounding** → `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/MATH.md
- **Business grounding** → `web_fetch` https://raw.githubusercontent.com/Kaito-ishiguro/optiloc-hk/main/docs/ROADMAP.md
- **Security question** → proportional security, not maximal
- **CONTEXT.md update** → always generate as downloadable file

---

*Last updated: end of Session 017 (May 23, 2026). CI/CD pipeline shipped. Session 018 (landing page v1) is next. Update this file at the end of every session that meaningfully changes project state.*
