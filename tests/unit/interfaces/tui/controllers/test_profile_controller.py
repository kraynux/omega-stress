from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err, Ok
from omega_stress.interfaces.tui.controllers.profile_controller import (
    create,
    freeze,
    load_profiles,
)
from tests.fixtures.fakes import FakeProfileRepository


def _create(repository: FakeProfileRepository, *, name: str = "Palier standard"):
    return create(
        profile_repository=repository,
        name=name,
        description="",
        default_target_id="target-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        duration_minutes=5,
        max_error_rate=0.05,
    )


def test_create_persists_and_returns_a_profile_dto():
    repository = FakeProfileRepository()

    result = _create(repository)

    assert isinstance(result, Ok)
    assert repository.get(result.value.id) is not None


def test_load_profiles_sorts_favorites_first():
    repository = FakeProfileRepository()
    zulu = _create(repository, name="Zulu")
    alpha = _create(repository, name="Alpha")
    assert isinstance(zulu, Ok)
    assert isinstance(alpha, Ok)

    profiles = load_profiles(profile_repository=repository)

    assert [p.name for p in profiles] == ["Alpha", "Zulu"]


def test_freeze_unknown_profile_returns_err():
    repository = FakeProfileRepository()

    result = freeze("unknown-id", profile_repository=repository)

    assert isinstance(result, Err)


def test_freeze_existing_profile_marks_it_frozen():
    repository = FakeProfileRepository()
    created = _create(repository)
    assert isinstance(created, Ok)

    result = freeze(created.value.id, profile_repository=repository)

    assert isinstance(result, Ok)
    assert result.value.frozen is True
