"""KCG — End-to-end smoke test for the UoG doc processing pipeline.

Per openspec/changes/kcg-university-of-galway-doc-processing-v1/.

Exercises:

  - The 5 DLT sources (academic_calendar + course_catalog +
    university_council_minutes + press_releases + research_outputs)
  - The 4 BAML extraction schemas (CourseOutline +
    AcademicCalendarEvent + GovernanceMinute + PressRelease)
  - The 2 CocoIndex embedding flows (courses_flow + governance_flow)
  - The OSINT allowlist lint

Exits 0 on full pass, 1 on any failure. Run via:

    python3 scripts/smoke_test.py

Licence: BUSL-1.1 (KCG edition, per LICENSE.md).
"""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent


def main() -> int:
    print("KCG smoke test — University of Galway doc processing pipeline")
    print(f"  repo_root: {REPO_ROOT}")
    print()

    # ────────────────────────────────────────────────────────────────────
    # 1. The 5 DLT sources
    # ────────────────────────────────────────────────────────────────────
    print("[1/4] DLT sources")
    sys.path.insert(0, str(REPO_ROOT))

    # Stub dlt before importing the pipelines, so the @dlt.resource
    # decorator is a no-op (and the stub methods aren't called as
    # bound-method resources, which would fail).
    if "dlt" not in sys.modules:
        import types
        dlt_stub = types.ModuleType("dlt")

        def _stub_resource(*_args, **_kwargs):
            def _decorator(fn):
                # Return a callable that, when invoked, returns the
                # underlying generator function (so `self.events()`
                # in build_pipeline_resource still works).
                class _StubResource:
                    def __call__(self_inner, *_call_args, **_call_kwargs):
                        # Call as a bound method: events(self)
                        return fn(_StubPipelineInstance(), *_call_args, **_call_kwargs)

                    def __get__(self_inner, obj, objtype=None):
                        # Bind `self` when accessed as an attribute
                        if obj is None:
                            return self_inner
                        def _bound(*_call_args, **_call_kwargs):
                            return fn(obj, *_call_args, **_call_kwargs)
                        return _bound

                return _StubResource()

            return _decorator

        def _stub_source(*_args, **_kwargs):
            def _decorator(fn):
                return fn
            return _decorator

        class _StubPipelineInstance:
            pass

        dlt_stub.resource = _stub_resource
        dlt_stub.source = _stub_source
        sys.modules["dlt"] = dlt_stub

    # Re-import the dlt_sources package so the stub takes effect
    if "dlt_sources" in sys.modules:
        del sys.modules["dlt_sources"]
    if "dlt_sources.uog" in sys.modules:
        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("dlt_sources."):
                del sys.modules[mod_name]

    from dlt_sources.uog import (
        academic_calendar_pipeline,
        course_catalog_pipeline,
        university_council_minutes_pipeline,
        press_releases_pipeline,
        research_outputs_pipeline,
    )

    expected_surfaces = {
        academic_calendar_pipeline: "academic_calendar",
        course_catalog_pipeline: "course_catalog",
        university_council_minutes_pipeline: "university_council_minutes",
        press_releases_pipeline: "press_releases",
        research_outputs_pipeline: "research_outputs",
    }
    for pipeline, expected in expected_surfaces.items():
        # Use the underlying _yield_live_scrape_rows method directly
        # (bypasses the @dlt.resource stub wrapper).
        rows = list(pipeline._yield_live_scrape_rows())
        assert rows, f"{expected}: expected ≥1 row from stub, got 0"
        # Surface ID matches the class
        assert pipeline.surface_id == expected, (
            f"surface_id={pipeline.surface_id} != expected={expected}"
        )
        # All rows include source_url OR url (some surfaces use url
        # as the canonical key, others use source_url).
        for r in rows:
            assert "source_url" in r or "url" in r, f"row missing source_url/url: {r}"
        print(f"  ✓ {expected}: {len(rows)} rows, surface_id={pipeline.surface_id}")

    # ────────────────────────────────────────────────────────────────────
    # 2. The 4 BAML extraction schemas (parse-only — no BAML compile here)
    # ────────────────────────────────────────────────────────────────────
    print()
    print("[2/4] BAML extraction schemas")

    baml_dir = REPO_ROOT / "baml_src" / "uog" / "processing"
    baml_files = [
        "course_outline.baml",
        "academic_calendar.baml",
        "governance_minute.baml",
        "press_release.baml",
    ]
    expected_classes_per_file = {
        "course_outline.baml": ("CourseOutline", "ExtractCourseOutline", "ExtractCourseOutlineBulk"),
        "academic_calendar.baml": ("AcademicCalendarEvent", "ExtractAcademicCalendarEvent", "ExtractAcademicCalendarBulk"),
        "governance_minute.baml": ("GovernanceMinute", "ExtractGovernanceMinute", "ExtractGovernanceMinuteBulk"),
        "press_release.baml": ("PressRelease", "ExtractPressRelease", "ExtractPressReleaseBulk"),
    }
    for baml_file in baml_files:
        baml_path = baml_dir / baml_file
        assert baml_path.exists(), f"{baml_path} missing"
        content = baml_path.read_text(encoding="utf-8")
        klass, single_fn, bulk_fn = expected_classes_per_file[baml_file]
        assert f"class {klass}" in content, f"{baml_file}: class {klass} missing"
        assert f"function {single_fn}" in content, f"{baml_file}: function {single_fn} missing"
        assert f"function {bulk_fn}" in content, f"{baml_file}: function {bulk_fn} missing"
        print(f"  ✓ {baml_file}: class {klass} + 2 extraction functions")

    # ────────────────────────────────────────────────────────────────────
    # 3. The 2 CocoIndex embedding flows (stub the cocoindex module)
    # ────────────────────────────────────────────────────────────────────
    print()
    print("[3/4] CocoIndex embedding flows")

    # Stub cocoindex so the flow files can import
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
            # Wrap so `.setup()` returns a flow-like object
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

    for flow_file in ["courses_flow.py", "governance_flow.py"]:
        flow_path = REPO_ROOT / "cocoindex_flows" / "uog" / flow_file
        assert flow_path.exists(), f"{flow_path} missing"
        spec = importlib.util.spec_from_file_location(
            f"flow_{flow_file.removesuffix('.py')}", str(flow_path)
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)

        # Each flow file names its top-level function per the file name
        # with _flow suffix (courses_flow.py → uog_courses_flow).
        flow_fn_name = "uog_" + flow_file.removesuffix(".py")
        flow_fn = getattr(mod, flow_fn_name, None)
        assert flow_fn is not None, f"{flow_file}: expected function {flow_fn_name}"
        assert hasattr(flow_fn, "setup"), f"{flow_file}: flow function missing setup()"
        assert hasattr(mod, "EMBEDDING_MODEL"), f"{flow_file}: missing EMBEDDING_MODEL"
        assert hasattr(mod, "LANCEDB_TABLE"), f"{flow_file}: missing LANCEDB_TABLE"
        assert hasattr(mod, "LANCEDB_URI"), f"{flow_file}: missing LANCEDB_URI"

        # The Record class must have an `embedding: coco.Vector[384]` field
        record_cls = (
            mod.CourseRecord if flow_file == "courses_flow.py" else mod.GovernanceMinuteRecord
        )
        annotations = record_cls.__annotations__
        assert "embedding" in annotations, f"{flow_file}: Record missing 'embedding' field"
        print(
            f"  ✓ {flow_file}: flow={flow_fn_name}, "
            f"EMBEDDING_MODEL={mod.EMBEDDING_MODEL}, "
            f"LANCEDB_TABLE={mod.LANCEDB_TABLE}"
        )

    # ────────────────────────────────────────────────────────────────────
    # 4. OSINT allowlist lint
    # ────────────────────────────────────────────────────────────────────
    print()
    print("[4/4] OSINT allowlist lint")
    import subprocess

    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "lint_osint_allowlist.py")],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    print(f"  {result.stdout.strip()}")
    if result.returncode != 0:
        print(result.stderr)
        return 1
    print("  ✓ 0 violations across 5 DLT sources")

    print()
    print("=" * 60)
    print("KCG smoke test PASS — UoG doc processing pipeline ready.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
