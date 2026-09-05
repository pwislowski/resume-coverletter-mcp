import pytest
import yaml

from scripts.build import ROOT, validate


@pytest.fixture
def profile():
    return yaml.safe_load((ROOT / "profile/career.yaml.stub").read_text())


@pytest.fixture
def application():
    return yaml.safe_load(
        (ROOT / "applications/baseline/application.yaml.stub").read_text()
    )


def test_baseline(profile, application):
    validate(profile, application)


def test_unknown_evidence_rejected(profile, application):
    application["overrides"]["invented-achievement"] = "Something unsupported"
    with pytest.raises(ValueError, match="Overrides must reference existing evidence IDs"):
        validate(profile, application)


def test_sample_cannot_be_presented_as_complete(profile, application):
    application["letter"]["is_sample"] = False
    with pytest.raises(ValueError, match="Complete all letter fields"):
        validate(profile, application)


@pytest.mark.parametrize("field", ["achievement_ids", "project_ids"])
@pytest.mark.parametrize("invalid_selection", ["unknown", "duplicate"])
def test_unknown_selection_and_duplicate_rejected(
    profile, application, field, invalid_selection
):
    application[field] = (
        ["nonexistent"] if invalid_selection == "unknown" else application[field][:1] * 2
    )
    with pytest.raises(ValueError, match=f"Invalid or duplicate {field}"):
        validate(profile, application)
