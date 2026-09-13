# KCG — Agent Routing

> **Wordplay (canonical):** *Kings College Galway* is the historical
> English name for the institution now called *Ollscoil na
> Gaillimhe* / *University of Galway* (renamed 2022). The repo
> preserves the original English name as a backwards-compatibility
> alias — many alumni documents + governance minutes still reference
> the Kings College Galway nomenclature.
>
> **GitHub location:** https://github.com/cianfhoghlaim/ollscoil-na-gaillimhe
> (the Irish name for UoG was chosen over `kings_college_galway`
> because that GitHub repo URL is already taken by the original
> cianfhoghlaim monorepo pre-rename). The local working directory
> remains `~/dev/kings_college_galway/` for backwards compatibility.
>
> **Scope (per `LICENSE.md`):** OSINT-only public-document processing
> for the University of Galway + the Students' Union. Strictly
> restricted to public-facing documents. Ingestion of student-private
> documents (coursework, grades, fees) is explicitly out of scope.

## Priority quick reference

### What KCG IS

- A sibling repo to `~/dev/ciandlithe` (civil litigation), `~/dev/cianchosaint`
  (defence / policing / intel oversight), and `~/dev/cianfhoghlaim` (main monorepo)
- The canonical home for **University of Galway public-document
  processing**: ingest UoG academic calendars, course catalogs,
  governance minutes, press releases, research outputs → BAML
  extraction → CocoIndex embedding → semantic search + per-persona
  marimo dashboards
- The data-source layer for the **Students' Union (USG) agents** in
  `~/dev/ciandlithe/agents/adk/students_union/` — the SU agents consume
  real-world UoG data via cross-repo imports

### What KCG IS NOT

- A platform for student-private documents. The DLT source layer MUST
  refuse to add a non-public URL.
- A replacement for the actual UoG systems (SLS, Banner, library
  databases). KCG is a read-only mirror of the PUBLIC documents.
- A platform for academic research collaboration. Use `~/dev/cianfhoghlaim`
  for that.
- A platform for civil litigation. Use `~/dev/ciandlithe` for that.

## Routing table — "where do I do X in kcg?"

| I want to... | Look at... |
|:--|:--|
| Add a new DLT source for a UoG public surface | `dlt_sources/uog/<surface>.py` — mirror the `academic_calendar.py` pattern |
| Add a new BAML extraction function | `baml_src/uog/processing/<domain>.baml` |
| Add a new CocoIndex embedding flow | `cocoindex_flows/uog/<domain>_flow.py` — mirror the `courses_flow.py` pattern |
| Add a new per-persona notebook | `notebooks/<notebook_name>.py` — marimo with PEP 723 inline deps |
| Add a new openspec change | `openspec/changes/<change-id>/{proposal.md, tasks.md, cross-repo-sync.md}` |
| Add a new capability spec | `openspec/specs/<spec-name>/spec.md` |
| Run the openspec validation gate | `openspec validate <change-id> --strict` |

## Cross-repo convention

KCG is a sibling repo to `~/dev/ciandlithe`. The two repos share:

- The openspec workflow (same `openspec/` layout, same `spec-driven`
  schema, same `proposal.md` + `tasks.md` + spec delta format)
- The DLT + BAML + CocoIndex pipeline convention
- The marimo notebook convention (PEP 723 inline deps + `@app.cell` layout)
- The Infisical `dev-baile` vault (kcg lives in its own `kcg/` folder)
- The MotherDuck + LanceDB stack (kcg uses the `md:kcg` database namespace)

The two repos diverge on:

- Domain (civil litigation vs University of Galway public docs)
- Licence (Ciandlithe: court-facing procedural rules; KCG: public UoG documents)
- Persona surfaces (Ciandlithe: civil-litigation analysts; KCG: UoG staff + SU + students)

## Priority mise tasks

```bash
# P1 — UoG doc processing pipeline
mise run kcg:dlt:sync-academic-calendar    # Sync the academic calendar + key dates
mise run kcg:dlt:sync-course-catalog       # Sync the public course catalog
mise run kcg:dlt:sync-governance-minutes   # Sync the University Council + Academic Council minutes
mise run kcg:dlt:sync-press-releases       # Sync the UoG press releases + news
mise run kcg:dlt:sync-research-outputs      # Sync the research publications + theses

# P2 — BAML extraction
mise run kcg:baml:extract-courses          # BAML-extract CourseOutline from the course catalog
mise run kcg:baml:extract-calendar          # BAML-extract AcademicCalendarEvent from the academic calendar
mise run kcg:baml:extract-minutes           # BAML-extract GovernanceMinute from the minutes
mise run kcg:baml:extract-press             # BAML-extract PressRelease from the news archive

# P3 — CocoIndex embedding
mise run kcg:cocoindex:embed-courses        # Embed courses into LanceDB
mise run kcg:cocoindex:embed-governance      # Embed governance minutes into LanceDB

# Cross-cutting
mise run kcg:lint:osint-allowlist           # Verify every DLT source URL is in the OSINT allowlist
mise run kcg:openspec:validate             # Validate every openspec change + spec
```

## Skill pointers

- `dlt` — the dlt pipeline convention (see `~/dev/cianfhoghlaim/.agents/skills/dlt/SKILL.md`)
- `cocoindex` — the CocoIndex v1 embedding pattern
- `marimo` — the marimo notebook convention (PEP 723 + `@app.cell`)
- `openspec` — the openspec workflow
- `baml` — the BAML extraction schema convention

## DO NOT

- Ingest student-private documents. The DLT source layer MUST
  refuse to add a non-public URL.
- Use this repo to scrape protected/sensitive UoG systems (Banner,
  SLS, library databases). The OSINT allowlist IS the licence
  ceiling.
- Bypass the openspec validation gate. `openspec validate --strict`
  MUST pass before commit.
- Commit the marimo `__marimo__/` cache or the `stedding/`
  site_scrape_samples. Both are gitignored.
