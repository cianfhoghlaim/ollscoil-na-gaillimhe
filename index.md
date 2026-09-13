# kings_college_galway — University of Galway / Ollscoil na Gaillimhe

Monorepo for the University of Galway public-document processing pipeline.

See [README.md](README.md), [AGENTS.md](AGENTS.md), [LICENSE.md](LICENSE.md),
and the openspec change [kcg-university-of-galway-doc-processing-v1](openspec/changes/kcg-university-of-galway-doc-processing-v1/).

## Quickstart

```bash
# Bootstrap dev env
uv sync --all-extras

# Run the end-to-end smoke test
python3 scripts/smoke_test.py

# Run the OSINT allowlist lint
python3 scripts/lint_osint_allowlist.py

# Sync all 5 UoG DLT sources (requires network access)
mise run kcg:dlt:sync-all

# Embed all 2 CocoIndex flows (requires local model)
mise run kcg:cocoindex:embed-all

# Launch the showcase notebook
marimo edit notebooks/uog_doc_processing_pipeline.py
```
