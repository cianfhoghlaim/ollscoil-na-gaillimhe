"""KCG — CocoIndex v1 embedding flow for the UoG course catalog.

Per openspec/changes/kcg-university-of-galway-doc-processing-v1/.

Embeds every CourseOutline row into a LanceDB table for semantic
search ("find UoG courses about climate science", etc.). Mirrors the
`cocoindex_flows/cianchosaint/ireland/legal_embedding.py` pattern.

Usage:

    python3 -m cocoindex_flows.uog.courses_flow

Licence: BUSL-1.1 (KCG edition, per LICENSE.md).
"""
from __future__ import annotations

from pathlib import Path

import cocoindex as coco

from dlt_sources.uog.course_catalog import course_catalog_pipeline

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # 384-d, fast
LANCEDB_TABLE = "uog_courses"
LANCEDB_URI = "stedding/lancedb/uog.lance"


@coco.function(
    name="uog_courses_flow",
    data_sources={"course_catalog": course_catalog_pipeline.courses},
)
def uog_courses_flow(
    flow_builder: coco.FlowBuilder,
    course_catalog: coco.DataSource,
) -> None:
    """Embed UoG course outlines into a LanceDB table.

    Output table schema:
        - course_code (primary key)
        - course_title_english + course_title_irish (text)
        - description_short (text)
        - ects_credits (int)
        - faculty + school (text)
        - embedding (vector[384])
    """
    # 1. Read + transform
    with flow_builder.read_data("course_catalog"):
        courses = flow_builder.add_classes(
            CourseRecord,
        )

    # 2. Collect + embed
    with courses.row() as course:
        flow_builder.embed(
            course["embedding"],
            coco.structured_data(
                course["course_title_english"],
                course["course_title_irish"],
                course["description_short"],
            ),
        )
        flow_builder.export(
            course["course_code"],
            course["course_title_english"],
            course["course_title_irish"],
            course["level"],
            course["year_of_study"],
            course["semester"],
            course["ects_credits"],
            course["faculty"],
            course["school"],
            course["campus"],
            course["mode"],
            course["delivery_language"],
            course["academic_year"],
            course["lecturer_lead"],
            course["description_short"],
            course["learning_outcomes_count"],
            course["assessment_methods"],
            course["prerequisite_course_codes"],
            course["syllabus_url"],
            course["source_url"],
            course["embedding"],
        )


class CourseRecord(coco.Record):
    """The canonical CourseOutline record schema for embedding."""

    course_code: str
    course_title_english: str
    course_title_irish: str | None
    level: str
    year_of_study: int | None
    semester: str | None
    ects_credits: int
    faculty: str
    school: str
    campus: str
    mode: str
    delivery_language: str
    academic_year: str
    lecturer_lead: str
    description_short: str
    learning_outcomes_count: int
    assessment_methods: list[str]
    prerequisite_course_codes: list[str]
    syllabus_url: str
    source_url: str
    embedding: coco.Vector[384]


def main() -> None:
    """CLI entrypoint — runs the flow."""
    print("uog_courses_flow: starting")
    flow = uog_courses_flow.setup()
    flow.update()
    print(f"uog_courses_flow: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
