import pytest
import yaml

from cv_mcp.builder import validate


@pytest.fixture
def profile():
    return yaml.safe_load(open("stubs/career.yaml"))


@pytest.fixture
def application():
    return yaml.safe_load(open("stubs/application.yaml"))


def test_baseline(profile, application):
    validate(profile, application)


def test_unknown_evidence_rejected(profile, application):
    application["overrides"]["invented-achievement"] = "Something unsupported"
    with pytest.raises(
        ValueError, match="Overrides must reference existing evidence IDs"
    ):
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
        ["nonexistent"]
        if invalid_selection == "unknown"
        else application[field][:1] * 2
    )
    with pytest.raises(ValueError, match=f"Invalid or duplicate {field}"):
        validate(profile, application)
