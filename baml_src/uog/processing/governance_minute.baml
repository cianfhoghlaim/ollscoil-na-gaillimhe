// =============================================================================
// BAML — GovernanceMinute schema for UoG University Council + Academic
// Council + Údarás na hOllscoile minutes.
//
// Per openspec/changes/kcg-university-of-galway-doc-processing-v1/.
//
// Source: UoG governance pages (https://www.universityofgalway.ie/governance/).
// Emitted by the `university_council_minutes` DLT source.
//
// Licence: BUSL-1.1 (KCG edition, per LICENSE.md).
// =============================================================================

class GovernanceMinute {
    meeting_date_iso string  // ISO date YYYY-MM-DD
    committee_name string  // "University Council" | "Academic Council" | "Údarás na hOllscoile" | "Finance Committee" | "Audit + Risk Committee" | ...
    committee_name_irish string?
    session_number string  // e.g. "2025/26/01"
    chair_name string?
    attendees_count int?
    quorum_met bool?
    decisions_count int
    decisions_summary string
    action_items_count int?
    source_url string
}

function ExtractGovernanceMinute(input: string) -> GovernanceMinute {
    client "openai/gpt-4o-mini"
    prompt #"
    Extract one GovernanceMinute row from the following University
    of Galway governance minutes PDF or page. If a field is not
    present, leave it null.

    {{ input }}

    {{ ctx.output_format }}
    "#
}

function ExtractGovernanceMinuteBulk(input: string) -> GovernanceMinute[] {
    client "openai/gpt-4o-mini"
    prompt #"
    Extract every GovernanceMinute row from the following
    University of Galway governance archive. Return one row per
    meeting.

    {{ input }}

    {{ ctx.output_format }}
    "#
}
