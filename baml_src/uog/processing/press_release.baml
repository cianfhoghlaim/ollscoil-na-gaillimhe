// =============================================================================
// BAML — PressRelease schema for the UoG press releases + news archive.
//
// Per openspec/changes/kcg-university-of-galway-doc-processing-v1/.
//
// Source: UoG news archive (https://www.universityofgalway.ie/news/).
// Emitted by the `press_releases` DLT source.
//
// Licence: BUSL-1.1 (KCG edition, per LICENSE.md).
// =============================================================================

class PressRelease {
    url string  // canonical URL (primary key)
    headline_english string
    headline_irish string?
    category string  // "rankings" | "research_funding" | "partnership" | "event_announcement" | "appointment" | "obituary" | ...
    published_date_iso string  // YYYY-MM-DD
    author_name string?
    faculties_mentioned string[]
    sources_cited_count int?
    word_count int?
    summary string
    is_irish_language bool
    is_research_output bool
}

function ExtractPressRelease(input: string) -> PressRelease {
    client "openai/gpt-4o-mini"
    prompt #"
    Extract one PressRelease row from the following University of
    Galway news article. If a field is not present, leave it null.

    {{ input }}

    {{ ctx.output_format }}
    "#
}

function ExtractPressReleaseBulk(input: string) -> PressRelease[] {
    client "openai/gpt-4o-mini"
    prompt #"
    Extract every PressRelease row from the following University of
    Galway news archive page. Return one row per article.

    {{ input }}

    {{ ctx.output_format }}
    "#
}
