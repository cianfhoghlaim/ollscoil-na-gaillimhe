# Change: kcg-university-of-galway-doc-processing-v1

## Why

The `kings_college_galway` monorepo (University of Galway / Ollscoil
na Gaillimhe / NUI Galway / Kings College Galway public-document
processing) currently has only `bonneagar/`, `notebooks/`, and
`stedding/` — no actual pipeline code. The user's lost session was
the bootstrap of this repo: DLT + BAML + CocoIndex layers for the
5 canonical UoG public surfaces.

This change ships:

  - 5 DLT sources (academic_calendar + course_catalog +
    university_council_minutes + press_releases + research_outputs)
  - 4 BAML extraction schemas (CourseOutline + AcademicCalendarEvent
    + GovernanceMinute + PressRelease)
  - 2 CocoIndex embedding flows (courses_flow + governance_flow)
  - 1 OSINT allowlist + lint gate (9 allowlisted URLs, 0 violations)
  - 1 end-to-end smoke test (`scripts/smoke_test.py`)
  - 1 marimo notebook showcasing the pipeline end-to-end
  - 1 openspec capability spec (`kcg-pipeline`)

## What changes

### Code

- **NEW dir** `dlt_sources/uog/` with 6 files:
  - `__init__.py` — exports the 5 pipelines + the base class
  - `_base.py` — `UogPipelineBase` contract + `UOG_SURFACE_CONFIGS`
  - `academic_calendar.py` — `AcademicCalendarPipeline` (10 events)
  - `course_catalog.py` — `CourseCatalogPipeline` (4 sample courses)
  - `university_council_minutes.py` — `UniversityCouncilMinutesPipeline` (3 meetings)
  - `press_releases.py` — `PressReleasesPipeline` (3 stories)
  - `research_outputs.py` — `ResearchOutputsPipeline` (2 publications)

- **NEW dir** `baml_src/uog/processing/` with 4 BAML files:
  - `course_outline.baml` — CourseOutline class + ExtractCourseOutline[Bulk]
  - `academic_calendar.baml` — AcademicCalendarEvent + ExtractAcademicCalendar[Event|Bulk]
  - `governance_minute.baml` — GovernanceMinute + ExtractGovernanceMinute[|Bulk]
  - `press_release.baml` — PressRelease + ExtractPressRelease[|Bulk]

- **NEW dir** `cocoindex_flows/uog/` with 2 flows:
  - `courses_flow.py` — `uog_courses_flow` (CourseRecord → LanceDB)
  - `governance_flow.py` — `uog_governance_flow` (GovernanceMinuteRecord → LanceDB)

- **NEW dir** `scripts/` with 3 files:
  - `osint_allowlist.yaml` — the canonical 9-entry allowlist
  - `lint_osint_allowlist.py` — the OSINT allowlist lint gate
  - `smoke_test.py` — the end-to-end smoke test (4 sections, all pass)

- **NEW marimo notebook** `notebooks/uog_doc_processing_pipeline.py` — 8 tabs showcasing the pipeline

### Top-level scaffold

- **NEW** `README.md` — repo overview + routing table + cross-repo convention
- **NEW** `LICENSE.md` — BUSL-1.1 (KCG edition) licence
- **NEW** `AGENTS.md` — agent routing doc
- **NEW** `pyproject.toml` — Python deps (dlt + baml-py + cocoindex + marimo)
- **NEW** `mise.toml` — 6 domain namespaces (`core`, `core:ci`, `kcg:dlt:*`, `kcg:baml:*`, `kcg:cocoindex:*`, `kcg:lint:*`, `openspec:validate`, `kcg:smoke-test`)

## Impact

- Affected specs: **1 NEW spec** `openspec/specs/kcg-pipeline/spec.md`
- Affected code: **19 NEW Python files** + **4 NEW BAML files** + **1 NEW YAML** + **1 NEW marimo notebook** + **4 NEW top-level files**

## Out of scope (follow-up changes)

- Live HTTP scrapers (the DLT sources ship with `_yield_live_scrape_rows` stubs that yield the canonical sample data; the production httpx + BS4 wiring is the `kcg-uog-live-scrapers-v1` follow-up)
- The Dagster orchestration for nightly UoG doc syncs (`kcg-dagster-uog-pipeline-v1`)
- The MotherDuck destination wiring (`kcg-motherduck-destination-v1`)
- The Convex schema for the UoG tables (`kcg-convex-uog-v1`)
- The TanStack Start + CopilotKit per-persona surfaces (`kcg-web-uog-v1`)

## Dependencies

`Blocked by: none` (this is the foundational bootstrap).
`Affected repos: kings_college_galway.`

## Cross-repo sync

This change touches ONLY the `kings_college_galway` repo. However, the
new pipeline is the **data source** for the Students' Union agents in
`~/dev/ciandlithe/agents/adk/students_union/` (the Class Rep Aggregator
Agent consumes real UoG course_catalog + class_rep data; the Grants
Funding Agent consumes the governance minutes to check for any new
funding policies; etc.).

## Verification

```bash
cd ~/dev/kings_college_galway

# 1. Smoke test (every DLT source imports + every BAML class loads
#    + every CocoIndex flow constructs + OSINT allowlist passes)
python3 scripts/smoke_test.py
# Expected: "KCG smoke test PASS"

# 2. Openspec strict validation
openspec validate kcg-university-of-galway-doc-processing-v1 --strict
# Expected: pass

# 3. OSINT allowlist lint
python3 scripts/lint_osint_allowlist.py
# Expected: "0 violations"

# 4. Marimo notebook parse
python3 -c "import ast; ast.parse(open('notebooks/uog_doc_processing_pipeline.py').read())"
# Expected: exit 0
```
