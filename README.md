# Resume and Cover Letter Generator

Reproducible, evidence-based CV and cover-letter builds from private local career inputs. The repository includes a command-line builder and an MCP server for drafting, validating and reviewing applications.

## Setup

Install [uv](https://docs.astral.sh/uv/), then create local inputs from the fictional examples:

```sh
mkdir -p profile applications/baseline
cp -n stubs/career.yaml profile/career.yaml
cp -n stubs/application.yaml applications/baseline/application.yaml
```

Replace the fictional evidence before building an application:

```sh
uv run cv-mcp build baseline
# or
just build
just check
```

The first build downloads Python and Typst dependencies. The included Typst binding supplies the compiler; no separate Typst or LaTeX installation is required. Outputs are written to `build/<slug>/<timestamp>_<version>/` with PDFs, previews, extracted text, an input snapshot and a report.

## Configure an application

1. Copy `applications/baseline/` to a lowercase slug containing only letters, numbers and hyphens, for example `company-role`.
2. Add the vacancy URL and any tracking ID to `application.yaml`.
3. Select evidence with `achievement_ids` and `project_ids`, and add truthful tailored wording under `overrides`.
4. Complete the cover letter, then set `letter.is_sample` to `false`.
5. Build and review both the extracted text and every PDF page.

Dates use British English. Set `letter.date` to a quoted ISO date such as `"2026-09-05"`, or leave it empty to use the current date in `Europe/London`. Use folded YAML blocks (`>-`) for long paragraphs, and quote dates and phone numbers.

## Environment variables

Local defaults are suitable for the checked-out layout. Override them with a `.env` file or the shell when needed:

| Variable | Purpose |
| --- | --- |
| `CV_MCP_ROOT` | Project root. |
| `CV_MCP_PROFILE` | Career profile YAML path. |
| `CV_MCP_APPLICATIONS` | Applications directory. |
| `CV_MCP_OUTPUT` | Build output directory. |
| `CV_MCP_FONTS` | Optional directory containing the Suisse fonts. |
| `CV_MCP_BUILD_TIMEOUT_SECONDS` | Build timeout; defaults to `120`. |
| `CV_MCP_LOG_LEVEL` | Log level; defaults to `INFO`. |
| `CV_MCP_DOWNLOAD_BASE_URL` / `CV_MCP_DOWNLOAD_SIGNING_SECRET` | Required when serving signed artifact download links. Keep the secret private. |

For Compose, `CV_MCP_DATA_DIR` selects the mounted private data directory. The tunnel container uses these variables:

| Variable | Purpose |
| --- | --- |
| `CONTROL_PLANE_ORGANIZATION_ID` | OpenAI organization identifier. |
| `CONTROL_PLANE_TUNNEL_ID` | Tunnel identifier. |
| `CONTROL_PLANE_API_KEY` | Tunnel runtime key; keep it private. |
| `MCP_SERVER_URL` | Internal MCP endpoint: `http://cv-mcp:8000/mcp`. |
| `TUNNEL_CLIENT_IMAGE` | Optional replacement for the default tunnel-client image. |

See the official [OpenAI Secure MCP Tunnel documentation](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels) for tunnel setup and configuration details.

## Example workflow

A typical workflow is to track roles, stages and next actions in Notion, keep verified career evidence and application drafts in this repository, use the MCP server to tailor and build documents, then review the generated PDFs before saving an approved release. Notion or another tracker can link to the resulting files; the repository remains the source for document inputs and builds.

The public repository contains only code, templates, tests, lockfiles and fictional stubs. Personal files under `profile/` and `applications/`, generated `build/` output, and research material are ignored. Keep private career data and submitted releases in a separate private deployment or storage location.

Typography uses Suisse Works and Suisse Intl Mono; install both locally for the intended rendering. The public baseline is a fictional layout sample.

Licensed under the [MIT License](LICENSE).
