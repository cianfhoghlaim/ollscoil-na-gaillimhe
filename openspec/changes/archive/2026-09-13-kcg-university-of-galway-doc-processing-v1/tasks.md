# Tasks: kcg-university-of-galway-doc-processing-v1

## 1. OpenSpec artifacts

- [x] Write `openspec/changes/kcg-university-of-galway-doc-processing-v1/proposal.md`
- [x] Write `openspec/changes/kcg-university-of-galway-doc-processing-v1/tasks.md` (this file)
- [x] Write `openspec/changes/kcg-university-of-galway-doc-processing-v1/cross-repo-sync.md`
- [x] Write `openspec/changes/kcg-university-of-galway-doc-processing-v1/specs/kcg-pipeline/spec.md`

## 2. Top-level scaffold

- [x] Write `README.md`
- [x] Write `LICENSE.md` (BUSL-1.1 KCG edition)
- [x] Write `AGENTS.md` (agent routing doc)
- [x] Write `pyproject.toml` (Python deps)
- [x] Write `mise.toml` (6 domain namespaces)

## 3. DLT sources (`dlt_sources/uog/`)

- [x] Write `dlt_sources/uog/__init__.py`
- [x] Write `dlt_sources/uog/_base.py` (`UogPipelineBase` contract + 5 surface configs)
- [x] Write `dlt_sources/uog/academic_calendar.py` (10 canonical events)
- [x] Write `dlt_sources/uog/course_catalog.py` (4 sample courses)
- [x] Write `dlt_sources/uog/university_council_minutes.py` (3 council meetings)
- [x] Write `dlt_sources/uog/press_releases.py` (3 news stories)
- [x] Write `dlt_sources/uog/research_outputs.py` (2 publications)

## 4. BAML extraction schemas (`baml_src/uog/processing/`)

- [x] Write `course_outline.baml` (CourseOutline + 2 extraction functions)
- [x] Write `academic_calendar.baml` (AcademicCalendarEvent + 2 extraction functions)
- [x] Write `governance_minute.baml` (GovernanceMinute + 2 extraction functions)
- [x] Write `press_release.baml` (PressRelease + 2 extraction functions)

## 5. CocoIndex embedding flows (`cocoindex_flows/uog/`)

- [x] Write `cocoindex_flows/uog/courses_flow.py` (CourseRecord → LanceDB)
- [x] Write `cocoindex_flows/uog/governance_flow.py` (GovernanceMinuteRecord → LanceDB)

## 6. Scripts

- [x] Write `scripts/osint_allowlist.yaml` (9 entries, 5 surfaces)
- [x] Write `scripts/lint_osint_allowlist.py` (OSINT allowlist lint gate)
- [x] Write `scripts/smoke_test.py` (4 sections: DLT + BAML + CocoIndex + lint)

## 7. Notebook

- [x] Write `notebooks/uog_doc_processing_pipeline.py` (marimo notebook, 8 tabs)

## 8. Validation

- [x] Run `python3 scripts/smoke_test.py` — pass
- [x] Run `openspec validate kcg-university-of-galway-doc-processing-v1 --strict` — verified 2026-09-13
- [x] Run `python3 -c "import ast; ast.parse(open('notebooks/uog_doc_processing_pipeline.py').read())"` — verified 2026-09-13

## Verification

```bash
cd ~/dev/kings_college_galway
python3 scripts/smoke_test.py
openspec validate kcg-university-of-galway-doc-processing-v1 --strict
```
