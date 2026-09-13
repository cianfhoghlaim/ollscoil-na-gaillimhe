# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.10.0",
#     "pandas>=2.0.0",
#     "dlt[duckdb]>=1.0.0",
#     "pyyaml>=6.0",
# ]
# ///

"""KCG — University of Galway doc processing pipeline (marimo notebook).

Showcases the end-to-end pipeline:

  DLT source → BAML extraction → CocoIndex embedding → semantic search

5 DLT sources (academic_calendar, course_catalog,
university_council_minutes, press_releases, research_outputs) feed
4 BAML extraction schemas (CourseOutline, AcademicCalendarEvent,
GovernanceMinute, PressRelease) which feed 2 CocoIndex flows
(courses_flow, governance_flow).

Run with:

    marimo edit notebooks/uog_doc_processing_pipeline.py

Licence: BUSL-1.1 (KCG edition, per LICENSE.md).
"""
import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def _intro():
    import marimo as mo
    mo.md(
        """
        # University of Galway — Document Processing Pipeline

        **5 DLT sources → 4 BAML extraction schemas → 2 CocoIndex embedding flows**

        The pipeline ingests public UoG documents (academic calendar +
        course catalog + governance minutes + news + research outputs),
        BAML-extracts them into structured rows, then embeds the rows
        into LanceDB tables for semantic search + per-persona dashboards.

        ## Pipeline stages

        | Stage | Module | Output |
        |:--|:--|:--|
        | 1. DLT scrape | `dlt_sources/uog/academic_calendar.py` | 1 row per UoG calendar event |
        | 1. DLT scrape | `dlt_sources/uog/course_catalog.py` | 1 row per (course_code, academic_year) |
        | 1. DLT scrape | `dlt_sources/uog/university_council_minutes.py` | 1 row per council meeting |
        | 1. DLT scrape | `dlt_sources/uog/press_releases.py` | 1 row per news story |
        | 1. DLT scrape | `dlt_sources/uog/research_outputs.py` | 1 row per publication |
        | 2. BAML extract | `baml_src/uog/processing/*.baml` | Structured Pydantic rows |
        | 3. CocoIndex | `cocoindex_flows/uog/courses_flow.py` | Embed courses into LanceDB |
        | 3. CocoIndex | `cocoindex_flows/uog/governance_flow.py` | Embed governance into LanceDB |
        | 4. Consumers | `~/dev/ciandlithe/agents/adk/students_union/` (cross-repo) | SU agents consume the data |
        """
    )
    return (mo,)


@app.cell
def _imports():
    import sys
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return Path, repo_root, sys


@app.cell
def _load_pipelines(Path, repo_root, sys):
    # Stub the missing optional dependencies so the notebook runs in
    # any environment (matches the smoke_test.py strategy).
    import importlib.util
    import types

    # Stub dlt @dlt.resource decorator so the DLT source modules import
    if "dlt" not in sys.modules:
        dlt_stub = types.ModuleType("dlt")

        def _stub_resource(*_args, **_kwargs):
            def _decorator(fn):
                return fn

            return _decorator

        def _stub_source(*_args, **_kwargs):
            def _decorator(fn):
                return fn

            return _decorator

        dlt_stub.resource = _stub_resource
        dlt_stub.source = _stub_source
        sys.modules["dlt"] = dlt_stub

    # Stub cocoindex
    if "cocoindex" not in sys.modules:
        coco_stub = types.ModuleType("cocoindex")

        class _StubRecord:
            pass

        class _StubFlowBuilder:
            def read_data(self, *_args, **_kwargs):
                return self

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def add_classes(self, *_args, **_kwargs):
                return self

        class _StubVector:
            def __class_getitem__(cls, _size):
                return cls

        def _stub_structured_data(*_args, **_kwargs):
            return "structured_data_stub"

        def _stub_function(*_args, **_kwargs):
            def _decorator(fn):
                class _StubFlow:
                    def setup(self_inner):
                        return self_inner

                    def update(self_inner):
                        return None

                fn.setup = _StubFlow().setup
                fn.update = _StubFlow().update
                return fn

            return _decorator

        coco_stub.Record = _StubRecord
        coco_stub.FlowBuilder = _StubFlowBuilder
        coco_stub.Vector = _StubVector
        coco_stub.structured_data = _stub_structured_data
        coco_stub.function = _stub_function
        coco_stub.DataSource = type("DataSource", (), {})
        sys.modules["cocoindex"] = coco_stub

    # Now import the DLT pipelines + BAML classes + CocoIndex flows
    from dlt_sources.uog import (
        academic_calendar_pipeline,
        course_catalog_pipeline,
        university_council_minutes_pipeline,
        press_releases_pipeline,
        research_outputs_pipeline,
    )
    return (
        academic_calendar_pipeline,
        course_catalog_pipeline,
        press_releases_pipeline,
        research_outputs_pipeline,
        university_council_minutes_pipeline,
    )


@app.cell
def _dlt_summary(
    mo,
    academic_calendar_pipeline,
    course_catalog_pipeline,
    university_council_minutes_pipeline,
    press_releases_pipeline,
    research_outputs_pipeline,
):
    pipelines = {
        "academic_calendar": academic_calendar_pipeline,
        "course_catalog": course_catalog_pipeline,
        "university_council_minutes": university_council_minutes_pipeline,
        "press_releases": press_releases_pipeline,
        "research_outputs": research_outputs_pipeline,
    }
    summary_rows = []
    for surface_id, pipeline in pipelines.items():
        rows = list(pipeline.build_pipeline_resource())
        summary_rows.append({
            "surface_id": surface_id,
            "source_url": pipeline.source_url,
            "row_count": len(rows),
            "first_row_pk": rows[0].get(pipeline.SURFACE_CONFIG.row_primary_key, "?") if rows else "?",
        })
    mo.md(
        "## DLT sources — pipeline summary\n\n"
        + "\n".join(
            f"| `{r['surface_id']:30}` | {r['row_count']:3} rows | `{r['first_row_pk']}` |"
            for r in summary_rows
        )
    )
    return pipelines, summary_rows


@app.cell
def _course_catalog_view(mo, course_catalog_pipeline):
    rows = list(course_catalog_pipeline.build_pipeline_resource())
    mo.md(
        "## Course catalog (raw DLT rows)\n\n"
        + "```\n"
        + "\n".join(
            f"  {r['course_code']:8}  {r['course_title_english'][:40]:40}  "
            f"({r['ects_credits']} ECTS, {r['delivery_language']}, {r['semester']})"
            for r in rows
        )
        + "\n```"
    )
    return rows


@app.cell
def _governance_view(mo, university_council_minutes_pipeline):
    rows = list(university_council_minutes_pipeline.build_pipeline_resource())
    mo.md(
        "## Governance minutes (raw DLT rows)\n\n"
        + "```\n"
        + "\n".join(
            f"  {r['meeting_date_iso']}  {r['committee_name']:30}  "
            f"({r['decisions_count']} decisions, {r['action_items_count']} actions)"
            for r in rows
        )
        + "\n```"
    )
    return rows


@app.cell
def _calendar_view(mo, academic_calendar_pipeline):
    rows = list(academic_calendar_pipeline.build_pipeline_resource())
    mo.md(
        "## Academic calendar (raw DLT rows)\n\n"
        + "```\n"
        + "\n".join(
            f"  {r['date_iso']}  {r['event_name_english'][:50]:50}  "
            f"({r['category']}, {'mandatory' if r['is_mandatory'] else 'optional'})"
            for r in rows
        )
        + "\n```"
    )
    return rows


@app.cell
def _press_releases_view(mo, press_releases_pipeline):
    rows = list(press_releases_pipeline.build_pipeline_resource())
    mo.md(
        "## Press releases (raw DLT rows)\n\n"
        + "```\n"
        + "\n".join(
            f"  {r['published_date_iso']}  [{r['category']}]  {r['headline_english'][:60]}"
            + ("  🇬🇪" if r["is_irish_language"] else "")
            for r in rows
        )
        + "\n```"
    )
    return rows


@app.cell
def _research_view(mo, research_outputs_pipeline):
    rows = list(research_outputs_pipeline.build_pipeline_resource())
    mo.md(
        "## Research outputs (raw DLT rows)\n\n"
        + "```\n"
        + "\n".join(
            f"  {r['year_published']}  [{r['thesis_or_publication']}]  "
            f"{r['title'][:80]}  ({r['language']}{', Irish-language' if r['is_irish_language'] else ''})"
            for r in rows
        )
        + "\n```"
    )
    return rows


@app.cell
def _osint_allowlist(mo):
    mo.md(
        """
        ## OSINT allowlist status

        Every DLT source URL is verified against
        `scripts/osint_allowlist.yaml` by `scripts/lint_osint_allowlist.py`
        (the canonical licence-enforcement surface, per LICENSE.md).

        **Current allowlist:** 9 entries across 5 surfaces, all on the
        University of Galway / Ollscoil na Gaillimhe / NUI Galway /
        Kings College Galway public-domain namespace.

        Run the lint via:

            mise run kcg:lint:osint-allowlist
        """
    )
    return


@app.cell
def _cross_repo(mo):
    mo.md(
        """
        ## Cross-repo consumer

        The Students' Union (USG) agents in `~/dev/ciandlithe/agents/adk/students_union/`
        consume the KCG data via cross-repo imports. Example wiring:

            from dlt_sources.uog import course_catalog_pipeline
            from agents.adk.students_union.tools.class_rep_themer import (
                aggregate_class_rep_themes,
            )

            # Real UoG module codes from the course_catalog_pipeline
            modules = [r["course_code"] for r in course_catalog_pipeline.courses()]

            # Real UoG Class Rep reports (from public Class Rep feedback)
            reports = [
                # ... populated from a real scrape ...
            ]

            agg = aggregate_class_rep_themes(reports)
            # → Class Rep Aggregator Agent briefing for the SU Education Officer
        """
    )
    return


if __name__ == "__main__":
    app.run()
