"""KCG — CocoIndex v1 embedding flow for UoG governance minutes.

Per openspec/changes/kcg-university-of-galway-doc-processing-v1/.

Embeds every GovernanceMinute row into a LanceDB table for semantic
search across UoG University Council + Academic Council + Údarás
na hOllscoile minutes.

Usage:

    python3 -m cocoindex_flows.uog.governance_flow

Licence: BUSL-1.1 (KCG edition, per LICENSE.md).
"""
from __future__ import annotations

import cocoindex as coco

from dlt_sources.uog.university_council_minutes import (
    university_council_minutes_pipeline,
)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LANCEDB_TABLE = "uog_governance_minutes"
LANCEDB_URI = "stedding/lancedb/uog.lance"


@coco.function(
    name="uog_governance_flow",
    data_sources={"minutes": university_council_minutes_pipeline.minutes},
)
def uog_governance_flow(
    flow_builder: coco.FlowBuilder,
    minutes: coco.DataSource,
) -> None:
    """Embed UoG governance minutes into a LanceDB table."""
    with flow_builder.read_data("minutes"):
        records = flow_builder.add_classes(GovernanceMinuteRecord)

    with records.row() as minute:
        flow_builder.embed(
            minute["embedding"],
            coco.structured_data(
                minute["committee_name"],
                minute["committee_name_irish"],
                minute["decisions_summary"],
            ),
        )
        flow_builder.export(
            minute["meeting_date_iso"],
            minute["committee_name"],
            minute["committee_name_irish"],
            minute["session_number"],
            minute["chair_name"],
            minute["attendees_count"],
            minute["quorum_met"],
            minute["decisions_count"],
            minute["decisions_summary"],
            minute["action_items_count"],
            minute["source_url"],
            minute["embedding"],
        )


class GovernanceMinuteRecord(coco.Record):
    """The canonical GovernanceMinute record schema for embedding."""

    meeting_date_iso: str
    committee_name: str
    committee_name_irish: str | None
    session_number: str
    chair_name: str | None
    attendees_count: int | None
    quorum_met: bool | None
    decisions_count: int
    decisions_summary: str
    action_items_count: int | None
    source_url: str
    embedding: coco.Vector[384]


def main() -> None:
    """CLI entrypoint — runs the flow."""
    print("uog_governance_flow: starting")
    flow = uog_governance_flow.setup()
    flow.update()
    print(f"uog_governance_flow: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
