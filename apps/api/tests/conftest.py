"""Shared pytest fixtures for the apps/api backend test suite."""
import pytest

from infrastructure.validation_service import SkincareValidationService


@pytest.fixture
def validator() -> SkincareValidationService:
    """A fresh validation service instance for each test."""
    return SkincareValidationService()
