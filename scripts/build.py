"""Build versioned PDF previews from plain data, never executable AI-generated markup."""

import argparse
import hashlib
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pymupdf
import typst
import yaml

ROOT = Path(__file__).resolve().parents[1]


def format_letter_date(value, locale="en-GB"):
    if locale != "en-GB":
        raise ValueError("Only en-GB letter dates are supported")
    months = (
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    )
    return f"{value.day} {months[value.month - 1]} {value.year}"


def validate(profile, application):
    ids = [x["id"] for job in profile["experience"] for x in job["achievements"]]
    project_ids = [x["id"] for x in profile["projects"]]
    known = ids + project_ids
    if len(known) != len(set(known)):
        raise ValueError("Career evidence IDs must be unique")
    for field, allowed in (("achievement_ids", ids), ("project_ids", project_ids)):
        selected = application[field]
        if len(selected) != len(set(selected)) or not set(selected) <= set(allowed):
            raise ValueError(f"Invalid or duplicate {field}")
    if not set(application["overrides"]) <= set(known):
        raise ValueError("Overrides must reference existing evidence IDs")
    if any(
        not isinstance(x, str) or not x.strip()
        for x in application["overrides"].values()
    ):
        raise ValueError("Overrides must contain nonempty plain text")
    allowed_sections = {"experience", "projects", "skills", "awards", "education"}
    sections = application["sections"]
    if (
        not sections
        or len(set(sections)) != len(sections)
        or not set(sections) <= allowed_sections
    ):
        raise ValueError("Invalid or duplicate sections")
    if application["paper"] not in ("a4", "us-letter"):
        raise ValueError("Paper must be a4 or us-letter")
    if type(application["max_cv_pages"]) is not int or application["max_cv_pages"] < 1:
        raise ValueError("max_cv_pages must be a positive integer")
    letter = application["letter"]
    if not letter["is_sample"]:
        values = [letter[k] for k in ("date", "recipient", "company", "role")] + letter[
            "paragraphs"
        ]
        if not letter["paragraphs"] or any(
            not v.strip() or re.search(r"\[[^]]+\]", v) for v in values
        ):
            raise ValueError(
                "Complete all letter fields and placeholders before disabling sample mode"
            )


def build(name):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        raise ValueError("Use a lowercase application slug")
    profile = yaml.safe_load((ROOT / "profile/career.yaml").read_text())
    application = yaml.safe_load(
        (ROOT / "applications" / name / "application.yaml").read_text()
    )
    letter = application["letter"]
    if not letter["date"]:
        letter["date"] = datetime.now(ZoneInfo("Europe/London")).date().isoformat()
    if not isinstance(letter["date"], str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", letter["date"]):
        raise ValueError("Letter date must be a quoted YYYY-MM-DD string")
    letter["formatted_date"] = format_letter_date(datetime.strptime(letter["date"], "%Y-%m-%d"))
    validate(profile, application)
    payload = yaml.safe_dump(
        {"profile": profile, "application": application},
        allow_unicode=True,
        sort_keys=False,
    )
    digest = hashlib.sha256(payload.encode())
    for path in sorted((ROOT / "templates").glob("*.typ")):
        digest.update(path.read_bytes())
    digest.update(Path(__file__).read_bytes())
    digest.update((ROOT / "uv.lock").read_bytes())
    version = digest.hexdigest()[:12]
    built_at = datetime.now(UTC)
    folder = f"{built_at:%Y-%m-%d_%H-%M-%S}_{version}"
    output = ROOT / "build" / name / folder
    output.mkdir(parents=True, exist_ok=False)
    data = output / "input.yaml"
    data.write_text(payload)
    report = {
        "version": version,
        "built_at": built_at.isoformat(),
        "variant": name,
        "review_notes": profile["review_notes"],
        "documents": {},
    }
    for document, limit in (("cv", application["max_cv_pages"]), ("cover-letter", 1)):
        pdf = output / f"{document}.pdf"
        typst.compile(
            str(ROOT / "templates" / f"{document}.typ"),
            output=str(pdf),
            root=str(ROOT),
            sys_inputs={"data": "/" + str(data.relative_to(ROOT))},
        )
        with pymupdf.open(pdf) as pages:
            text = "\n".join(page.get_text() for page in pages)
            (output / f"{document}.txt").write_text(text)
            if len(pages) > limit:
                raise ValueError(
                    f"{document}: {len(pages)} pages exceeds limit {limit}"
                )
            if (
                profile["name"].lower() not in text.lower()
                or profile["email"] not in text
            ):
                raise ValueError(
                    f"{document}: contact details missing from extracted text"
                )
            for number, page in enumerate(pages, 1):
                page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).save(
                    output / f"{document}-{number}.png"
                )
            report["documents"][document] = {
                "pages": len(pages),
                "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
            }
    (output / "report.yaml").write_text(yaml.safe_dump(report, sort_keys=False))
    print(f"Built {output.relative_to(ROOT)}")
    print(
        "CV and letter: page limits and contact text extraction passed. Inspect PNG previews before use."
    )
    if application["letter"]["is_sample"]:
        print("Cover letter is a layout sample, not ready for submission.")
    for note in profile["review_notes"]:
        print(f"Review: {note}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("application", nargs="?", default="baseline")
    args = parser.parse_args()
    try:
        build(args.application)
    except (ValueError, KeyError, OSError, yaml.YAMLError, typst.TypstError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        sys.exit(1)
