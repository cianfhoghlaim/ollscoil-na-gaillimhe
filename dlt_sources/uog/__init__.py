"""KCG — DLT sources for the University of Galway (Ollscoil na Gaillimhe).

Per openspec/changes/kcg-university-of-galway-doc-processing-v1/.

Five public surfaces are ingested:

  1. academic_calendar       — UoG academic calendar + key dates
  2. course_catalog          — Public course catalog (UG + PG)
  3. university_council_minutes — University Council + Academic Council minutes
  4. press_releases          — UoG news + press releases
  5. research_outputs        — Research publications + theses

Every DLT resource honours `USE_LOCAL_SCRAPES=true` falling back to
`stedding/ingest_queue/uog/<surface>/` for offline development.

Licence: BUSL-1.1 (KCG edition, per LICENSE.md).
"""
from ._base import (
    UOG_SURFACES,
    UOG_SURFACE_CONFIGS,
    UOG_PIPELINE_BASE_VERSION,
    UogPipelineBase,
    UogSurfaceConfig,
)
from .academic_calendar import (
    AcademicCalendarPipeline,
    academic_calendar_pipeline,
)
from .course_catalog import (
    CourseCatalogPipeline,
    course_catalog_pipeline,
)
from .university_council_minutes import (
    UniversityCouncilMinutesPipeline,
    university_council_minutes_pipeline,
)
from .press_releases import (
    PressReleasesPipeline,
    press_releases_pipeline,
)
from .research_outputs import (
    ResearchOutputsPipeline,
    research_outputs_pipeline,
)

__all__ = [
    # Base classes
    "UOG_SURFACES",
    "UOG_SURFACE_CONFIGS",
    "UOG_PIPELINE_BASE_VERSION",
    "UogPipelineBase",
    "UogSurfaceConfig",
    # Pipeline classes
    "AcademicCalendarPipeline",
    "CourseCatalogPipeline",
    "UniversityCouncilMinutesPipeline",
    "PressReleasesPipeline",
    "ResearchOutputsPipeline",
    # Pipeline singletons
    "academic_calendar_pipeline",
    "course_catalog_pipeline",
    "university_council_minutes_pipeline",
    "press_releases_pipeline",
    "research_outputs_pipeline",
]
