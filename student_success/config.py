"""
Centralized configuration for the Student Success package.

This module loads project configuration from environment variables and,
when available, from the project's ``.env`` file using ``python-dotenv``.
The ``.env`` file is located relative to the package source rather than
the current working directory, allowing configuration to work consistently
from notebooks, scripts, and development tools.

Configuration values currently supported are:

``STUDENT_SUCCESS_DATA_ROOT``
    Root directory containing institutional data files.

``STUDENT_SUCCESS_RESULTS``
    Directory used for analysis outputs and generated results.

``STUDENT_SUCCESS_CIPHER``
    Secret value used for reproducible scrambling or de-identification
    of student identifiers.

Path-based settings are exposed as :class:`pathlib.Path` objects when
configured. The cipher is retrieved through :func:`get_cipher` so that
importing this module does not fail in workflows that do not require it.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


def _get_optional_path(name: str) -> Path | None:
    """
    Return an environment variable as a :class:`~pathlib.Path`.

    Parameters
    ----------
    name : str
        Name of the environment variable.

    Returns
    -------
    pathlib.Path or None
        Expanded path if the variable is defined, otherwise ``None``.
    """
    value = os.getenv(name)
    return Path(value).expanduser() if value else None


def _get_required(name: str) -> str:
    """
    Return a required environment variable.

    Parameters
    ----------
    name : str
        Name of the environment variable.

    Returns
    -------
    str
        Configured environment-variable value.

    Raises
    ------
    RuntimeError
        If the environment variable is not configured or is empty.
    """
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Required environment variable {name!r} is not configured."
        )
    return value


DATA_ROOT = _get_optional_path("STUDENT_SUCCESS_DATA_ROOT")
"""pathlib.Path or None: Root directory containing institutional data."""

RESULTS_ROOT = _get_optional_path("STUDENT_SUCCESS_RESULTS")
"""pathlib.Path or None: Directory used for generated analysis results."""


def get_cipher() -> str:
    """
    Return the configured Student Success cipher.

    Returns
    -------
    str
        Value of ``STUDENT_SUCCESS_CIPHER``.

    Raises
    ------
    RuntimeError
        If ``STUDENT_SUCCESS_CIPHER`` is not configured.
    """
    return _get_required("STUDENT_SUCCESS_CIPHER")