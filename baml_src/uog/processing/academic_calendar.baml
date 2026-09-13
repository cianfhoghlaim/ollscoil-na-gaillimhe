// =============================================================================
// BAML — AcademicCalendarEvent schema for the UoG academic calendar.
//
// Per openspec/changes/kcg-university-of-galway-doc-processing-v1/.
//
// Source: UoG academic calendar (https://www.universityofgalway.ie/academic-calendar/).
// Emitted by the `academic_calendar` DLT source.
//
// Licence: BUSL-1.1 (KCG edition, per LICENSE.md).
// =============================================================================

class AcademicCalendarEvent {
    date_iso string  // ISO date string YYYY-MM-DD
    event_name_english string
    event_name_irish string?
    academic_year string  // e.g. "2025/26"
    semester string?  // "S1" | "S2" | "Summer" | "Year-long"
    category string  // "teaching_start" | "teaching_end" | "reading_week" | "exam_start" | "exam_end" | "public_holiday" | "university_closure"
    is_mandatory bool
    source_url string
}

function ExtractAcademicCalendarEvent(input: string) -> AcademicCalendarEvent {
    client "openai/gpt-4o-mini"
    prompt #"
    Extract one AcademicCalendarEvent row from the following
    University of Galway calendar page or PDF content. If a field
    is not present, leave it null.

    {{ input }}

    {{ ctx.output_format }}
    "#
}

function ExtractAcademicCalendarBulk(input: string) -> AcademicCalendarEvent[] {
    client "openai/gpt-4o-mini"
    prompt #"
    Extract every AcademicCalendarEvent row from the following
    University of Galway calendar page or PDF. Return one row per
    event date.

    {{ input }}

    {{ ctx.output_format }}
    "#
}
