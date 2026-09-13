# Cross-repo sync: kcg-university-of-galway-doc-processing-v1

This change touches ONLY the `kings_college_galway` repo. However,
the new pipeline is the **data source** for the Students' Union
agents in `~/dev/ciandlithe/agents/adk/students_union/` (cross-repo
consumers).

## Files touched (kings_college_galway)

| Path | Change |
|:--|:--|
| `README.md` | NEW |
| `LICENSE.md` | NEW |
| `AGENTS.md` | NEW |
| `pyproject.toml` | NEW |
| `mise.toml` | NEW |
| `dlt_sources/uog/__init__.py` | NEW |
| `dlt_sources/uog/_base.py` | NEW |
| `dlt_sources/uog/academic_calendar.py` | NEW |
| `dlt_sources/uog/course_catalog.py` | NEW |
| `dlt_sources/uog/university_council_minutes.py` | NEW |
| `dlt_sources/uog/press_releases.py` | NEW |
| `dlt_sources/uog/research_outputs.py` | NEW |
| `baml_src/uog/processing/course_outline.baml` | NEW |
| `baml_src/uog/processing/academic_calendar.baml` | NEW |
| `baml_src/uog/processing/governance_minute.baml` | NEW |
| `baml_src/uog/processing/press_release.baml` | NEW |
| `cocoindex_flows/uog/courses_flow.py` | NEW |
| `cocoindex_flows/uog/governance_flow.py` | NEW |
| `scripts/osint_allowlist.yaml` | NEW |
| `scripts/lint_osint_allowlist.py` | NEW |
| `scripts/smoke_test.py` | NEW |
| `notebooks/uog_doc_processing_pipeline.py` | NEW |
| `openspec/changes/kcg-university-of-galway-doc-processing-v1/{proposal,tasks,cross-repo-sync}.md` | NEW |
| `openspec/changes/kcg-university-of-galway-doc-processing-v1/specs/kcg-pipeline/spec.md` | NEW |

## Cross-repo consumers (informational, no changes here)

### `~/dev/ciandlithe/agents/adk/students_union/`

The SU agents consume the KCG data via cross-repo imports. The
canonical consumers are:

| SU Agent | KCG surface |
|:--|:--|
| `class_rep_aggregator_agent` | `course_catalog` (real module codes) + `class_reports_public` (when added) |
| `grants_funding_agent` | `university_council_minutes` (check for new funding-policy changes) |
| `elections_agent` | `governance_minutes` (check for any constitutional changes) |
| Root orchestrator | All 5 surfaces (intent classification + domain lookup) |

### `~/dev/ciandlithe/agents/adk/students_union/_smoke_test.py`

The SU smoke test in ciandlithe is unaffected by this change — it
still runs in isolation. The cross-repo wiring is via Python imports
that the marimo notebook demonstrates end-to-end.

## Soft dependencies

- **DLT** (`dlt[duckdb]>=1.0.0`) — already declared in `pyproject.toml`
- **BAML** (`baml-py>=0.50.0`) — already declared in `pyproject.toml`
- **CocoIndex** (`cocoindex>=1.0.0`) — already declared in `pyproject.toml`
- **Marimo** (`marimo>=0.10.0`) — declared in `pyproject.toml` under `[project.optional-dependencies].notebooks`

The BAML client (`baml_client/`) is NOT shipped in this change — it
must be generated locally via `baml-cli generate` (not run in this
change to avoid sandboxed-exec surprises).
