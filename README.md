# cv-mcp

Licensed under the [MIT License](LICENSE). Copyright © 2026 Piotr Wislowski.

Reproducible, evidence-based CV and cover-letter builds with private local career inputs. Notion remains the application dashboard. This first version runs locally; it does not connect to Notion, Gmail or ChatGPT yet.

## Build

Install [uv](https://docs.astral.sh/uv/). On a fresh checkout, create local inputs from the fictional stubs (skip this if you already have personal inputs):

```sh
cp -n profile/career.yaml.stub profile/career.yaml
cp -n applications/baseline/application.yaml.stub applications/baseline/application.yaml
```

Replace the fictional evidence with your own before tailoring applications, then run:

```sh
uv run python scripts/build.py baseline
# Or, with just installed:
just build
just check
```

The Python Typst binding includes the compiler; no separate LaTeX/Typst installation is needed. First build needs network access to download Python dependencies and Typst packages. Python dependencies are locked in `uv.lock`; the CV imports `@preview/basic-resume:0.2.9` from [stuxf/basic-typst-resume-template](https://github.com/stuxf/basic-typst-resume-template) (Unlicense).

Outputs live in `build/<application>/<datetime>_<baseline-or-overrides>_<hash>/`: PDFs, page previews, extracted text, input snapshot and a check report. The UTC timestamp uses `YYYY-MM-DD_HH-MM-SS.ffffffZ`, with microseconds to distinguish rapid builds. The label is `overrides` when the application's `overrides` mapping is nonempty, otherwise `baseline`. Each build creates a new folder; the report records its timestamp, label and content hash. This is a preview cache, not an archive of submitted applications. Before submission, copy the approved output folder into a new `applications/<id>/releases/<version>/` directory and retain those exact files. Never overwrite a submitted release. The version hash includes content, templates, build script and dependency lock; PDF hashes record the actual output.

## Tailor an application

Cover-letter dates use UK English (`5 September 2026`) and appear to the right of your name. Set `letter.date` to a quoted ISO date such as `"2026-09-05"`, or leave it empty to use the current date in `Europe/London`. The resolved date is saved in the build snapshot and included in its content hash. Only `en-GB` formatting is currently supported, independently of the machine's locale.

1. Copy `applications/baseline/` to a new lowercase slug, such as `company-role`.
2. Record the vacancy URL and Notion page ID in `application.yaml`.
3. Select achievements and projects using their IDs. Project order follows `project_ids`; employment remains in career order. Change `sections` to reorder CV sections.
4. Put tailored wording in `overrides`, keyed by the original evidence ID. These strings are rendered as plain text. The validator checks references, not factual truth: review every reworded claim.
5. Fill in the cover-letter recipient, date, company, role and paragraphs; set `is_sample` to false only once placeholders are complete.
6. Build, review extracted text, and inspect every PDF page. Adjust content rather than shrinking type to force a fit.

`profile/career.yaml` holds user-reported career evidence. Contact data and current-status statements require review before submission.

Content files use YAML, including generated `input.yaml` snapshots and `report.yaml` build reports. Use folded blocks (`>-`) for long paragraphs. Quote dates (for example, `"2026-09-05"`) and phone numbers so YAML treats them as text. Inputs are loaded with PyYAML's safe loader.

`templates/theme.typ` wraps the upstream template with A4 defaults, a centred header and shared typography. The public baseline stub contains fictional sample evidence. Its cover letter is explicitly a layout sample.

Typography uses Suisse Works for the main text and Suisse Intl Mono for CV section headings. Both families must be installed locally for the intended rendering; font files are not bundled in this repository. The pairing is configured in `templates/theme.typ`.

Existing `resources/` and `ai-job-search/` are retained as reference material. Research reports are context, not evidence of personal achievements.

## Public code and private deployment

The public repository contains the build code, templates, tests, lockfile and fictional
`profile/career.yaml.stub` and `applications/baseline/application.yaml.stub` files.
Tests load only these stubs; `just check` (or `uv run pytest`) needs no personal inputs.

Actual files under `profile/` and `applications/`, including submission releases, are
ignored, as are `build/`, `resources/` and `ai-job-search/`. Existing local files are
preserved. Stubs are the only exceptions within the private input directories.
Never put personal evidence into a stub.

Maintain a separate private deployment repository for your career inputs, application
history, releases and deployment configuration. Its ignore rules should permit those
private inputs to be versioned. Bring public code updates into that repository without
copying private data back to the public repository.

This repository starts with fresh Git history containing reviewed public files.
Keep private deployment history separate; `.gitignore` does not remove files from
earlier commits.

## Next integration

Expose the existing build function through a small MCP interface once the documents are approved. Notion owns stage, next action and deadlines; the repository owns document inputs and releases. Store private final files in durable storage and link them from Notion. Treat a document build as ready-for-review, never proof of submission. Gmail status updates and any continuous monitoring belong to a later integration.
