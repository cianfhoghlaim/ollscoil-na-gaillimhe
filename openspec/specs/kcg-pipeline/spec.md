# kcg-pipeline Specification

## Purpose

Codify the canonical University of Galway (Ollscoil na Gaillimhe /
NUI Galway / Kings College Galway) public-document processing
pipeline. The pipeline ingests public UoG documents via 5 DLT
sources, BAML-extracts them into structured rows, embeds the rows
into LanceDB tables via 2 CocoIndex flows, and surfaces the data via
the Students' Union agents in `~/dev/ciandlithe/agents/adk/students_union/`.

The 5 DLT surfaces are: academic calendar, public course catalog,
University Council + Academic Council + Údarás na hOllscoile minutes,
press releases + news archive, and research publications + theses.
The 4 BAML schemas (CourseOutline + AcademicCalendarEvent +
GovernanceMinute + PressRelease) are the canonical structured forms.
The 2 CocoIndex flows embed the courses and the governance minutes
into LanceDB for semantic search.

## Requirements

### Requirement: 5 DLT sources for UoG public surfaces

The system SHALL provide 5 DLT source modules under `dlt_sources/uog/`,
each scraping one public UoG surface and yielding structured rows:

  1. `academic_calendar` — `https://www.universityofgalway.ie/academic-calendar/`
  2. `course_catalog` — `https://www.universityofgalway.ie/courses/`
  3. `university_council_minutes` — `https://www.universityofgalway.ie/governance/`
  4. `press_releases` — `https://www.universityofgalway.ie/news/`
  5. `research_outputs` — `https://www.universityofgalway.ie/research/`

Each module MUST subclass `UogPipelineBase` (defined in
`dlt_sources/uog/_base.py`) and MUST set `SURFACE_CONFIG` to the
matching `UogSurfaceConfig` from `UOG_SURFACE_CONFIGS`.

#### Scenario: All 5 DLT sources import + yield rows

- **WHEN** the operator runs `python3 scripts/smoke_test.py`
- **THEN** each of the 5 DLT sources MUST yield ≥1 row from its
  `_yield_live_scrape_rows` stub method (the production httpx + BS4
  wiring is the `kcg-uog-live-scrapers-v1` follow-up)
- **AND** the row count for each surface MUST be logged via structlog

### Requirement: 4 BAML extraction schemas

The system SHALL provide 4 BAML extraction schemas under
`baml_src/uog/processing/`, each declaring one Pydantic class +
2 extraction functions (single + bulk):

  1. `course_outline.baml` — `CourseOutline` + `ExtractCourseOutline[Bulk]`
  2. `academic_calendar.baml` — `AcademicCalendarEvent` + `ExtractAcademicCalendar[Bulk]`
  3. `governance_minute.baml` — `GovernanceMinute` + `ExtractGovernanceMinute[Bulk]`
  4. `press_release.baml` — `PressRelease` + `ExtractPressRelease[Bulk]`

#### Scenario: All 4 BAML files declare class + 2 functions

- **WHEN** the smoke test scans `baml_src/uog/processing/*.baml`
- **THEN** each .baml file MUST contain `class <Name>` + `function <Name>` + `function <Name>Bulk`
- **AND** the smoke test MUST log a ✓ for each .baml file with the
  expected class + function names

### Requirement: 2 CocoIndex embedding flows

The system SHALL provide 2 CocoIndex v1 flows under
`cocoindex_flows/uog/`:

  1. `courses_flow.py` — embeds CourseOutline rows into LanceDB
     table `uog_courses` (384-d `sentence-transformers/all-MiniLM-L6-v2`)
  2. `governance_flow.py` — embeds GovernanceMinute rows into LanceDB
     table `uog_governance_minutes` (same embedder)

Each flow MUST expose:
  - The `@coco.function` decorator
  - An `EMBEDDING_MODEL` constant
  - A `LANCEDB_TABLE` + `LANCEDB_URI` constant
  - A `Record` subclass with an `embedding: coco.Vector[384]` field

#### Scenario: Both flows construct without cocoindex installed

- **WHEN** the smoke test stubs the `cocoindex` module
- **THEN** both flows MUST import + construct without errors
- **AND** the smoke test MUST log a ✓ for each flow with the EMBEDDING_MODEL + LANCEDB_TABLE

### Requirement: OSINT allowlist lint gate

The system SHALL provide `scripts/osint_allowlist.yaml` + the
`scripts/lint_osint_allowlist.py` AST-based lint that verifies every
DLT source URL is on the British Isles + Republic of Ireland
public-sector domain list AND/OR in the explicit allowlist.

#### Scenario: Lint passes with 0 violations

- **WHEN** the operator runs `python3 scripts/lint_osint_allowlist.py`
- **THEN** the script MUST exit 0 with the message
  `OK: <N> file(s) scanned; <M> allowlist entries; 0 violations`
- **AND** every UoG DLT source URL MUST be on either
  `universityofgalway.ie` / `nuigalway.ie` / `aran.library.universityofgalway.ie`
  OR in the explicit allowlist

### Requirement: End-to-end smoke test

The system SHALL provide `scripts/smoke_test.py` that exercises all 4
pipeline stages (DLT + BAML + CocoIndex + OSINT lint) in a single run.
The smoke test MUST exit 0 iff every stage passes.

#### Scenario: Smoke test passes on first run

- **WHEN** the operator runs `python3 scripts/smoke_test.py`
- **THEN** the script MUST exit 0 with the message
  `KCG smoke test PASS — UoG doc processing pipeline ready.`
- **AND** every stage log line MUST show ✓ for each surface/file

### Requirement: Public-document scope (no student-private data)

The system MUST NOT ingest student-private documents (coursework,
grades, fees, library borrowing history, accommodation records,
disciplinary records). The DLT source layer MUST refuse to add any
non-public URL — enforced by `scripts/lint_osint_allowlist.py`.

#### Scenario: Adding a non-public URL fails the lint

- **WHEN** the operator adds a DLT source that scrapes a non-public URL
  (e.g. `https://sis.universityofgalway.ie/...` — the Student
  Information System)
- **THEN** `python3 scripts/lint_osint_allowlist.py` MUST exit 1 with
  the violation `URL not in OSINT allowlist`
- **AND** the operator MUST either remove the DLT source OR add the
  URL to `scripts/osint_allowlist.yaml` with a documented justification
  (which itself requires a licence amendment per LICENSE.md)
