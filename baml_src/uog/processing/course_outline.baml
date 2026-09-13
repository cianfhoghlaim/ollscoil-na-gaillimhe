// =============================================================================
// BAML — CourseOutline schema for the UoG public course catalog.
//
// Per openspec/changes/kcg-university-of-galway-doc-processing-v1/.
//
// Source: UoG public course catalog (https://www.universityofgalway.ie/courses/).
// Emitted by the `course_catalog` DLT source (.dlt_sources/uog/course_catalog.py)
// + BAML-extracted into structured rows via the ExtractCourseOutline function.
//
// Licence: BUSL-1.1 (KCG edition, per LICENSE.md).
// =============================================================================

class CourseOutline {
    course_code string
    course_title_english string
    course_title_irish string?
    level string  // "undergraduate" | "postgraduate" | "microcredential"
    year_of_study int?
    semester string?  // "S1" | "S2" | "S1 + S2" | "Summer"
    ects_credits int
    faculty string
    school string
    campus string
    mode string  // "full_time" | "part_time" | "blended" | "online"
    delivery_language string  // "en" | "ga" | "bi" (bilingual)
    academic_year string  // e.g. "2025/26"
    lecturer_lead string
    description_short string
    learning_outcomes_count int
    assessment_methods string[]
    prerequisite_course_codes string[]
    syllabus_url string
    source_url string
}

function ExtractCourseOutline(input: string) -> CourseOutline {
    client "openai/gpt-4o-mini"
    prompt #"
    Extract the University of Galway course outline from the following
    page or PDF content. If a field is not present, leave it null
    (use empty string for required string fields).

    {{ input }}

    {{ ctx.output_format }}
    "#
}

function ExtractCourseOutlineBulk(input: string) -> CourseOutline[] {
    client "openai/gpt-4o-mini"
    prompt #"
    Extract every University of Galway course outline from the
    following catalog page or PDF. Return one CourseOutline per
    (course_code, academic_year) tuple.

    {{ input }}

    {{ ctx.output_format }}
    "#
}
