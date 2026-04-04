"""Container/CI collector — Docker, CI, WSL, cloud detection, container files."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from _imports import find_repo_root

from _env_collectors._base import BaseCollector

_tier = None


def _get_tier():  # type: ignore[no-untyped-def]
    global _tier
    if _tier is None:
        from _env_collectors import Tier

        _tier = Tier
    return _tier


class ContainerCollector(BaseCollector):
    """Detect container, CI, WSL, and cloud environments."""

    name = "container"
    timeout = 5.0

    @property
    def tier(self):  # type: ignore[override]
        return _get_tier().STANDARD

    def collect(self) -> dict[str, Any]:
        env = os.environ

        # Container detection
        in_docker = (
            Path("/.dockerenv").exists()
            or Path("/run/.containerenv").exists()
            or bool(env.get("container"))
        )

        # CI detection
        ci_system = self._detect_ci(env)

        # WSL detection
        in_wsl = "microsoft" in (
            os.uname().release.lower() if hasattr(os, "uname") else ""
        )

        # Cloud detection
        cloud = self._detect_cloud(env)

        detected = in_docker or bool(ci_system) or in_wsl or bool(cloud)

        # Container file detection in repo
        container_files = self._detect_container_files()

        return {
            "detected": detected,
            "docker": in_docker,
            "ci": ci_system,
            "wsl": in_wsl,
            "cloud": cloud,
            "container_files": container_files,
        }

    @staticmethod
    def _detect_ci(env: os._Environ[str]) -> str:
        """Detect which CI system we're running in."""
        if env.get("GITHUB_ACTIONS"):
            return "GitHub Actions"
        if env.get("GITLAB_CI"):
            return "GitLab CI"
        if env.get("JENKINS_URL"):
            return "Jenkins"
        if env.get("CIRCLECI"):
            return "CircleCI"
        if env.get("TRAVIS"):
            return "Travis CI"
        if env.get("BUILDKITE"):
            return "Buildkite"
        if env.get("TF_BUILD"):
            return "Azure Pipelines"
        if env.get("CI"):
            return "Unknown CI"
        return ""

    @staticmethod
    def _detect_cloud(env: os._Environ[str]) -> str:
        """Detect cloud provider from environment hints."""
        if env.get("AWS_REGION") or env.get("AWS_DEFAULT_REGION"):
            return "AWS"
        if env.get("GOOGLE_CLOUD_PROJECT") or env.get("GCP_PROJECT"):
            return "GCP"
        if env.get("AZURE_SUBSCRIPTION_ID"):
            return "Azure"
        return ""

    @staticmethod
    def _detect_container_files() -> list[dict[str, Any]]:
        """Detect container-related files in the repo root."""
        root = find_repo_root()
        container_file_names = [
            "Containerfile",
            "Dockerfile",
            "docker-compose.yml",
            "docker-compose.yaml",
            "compose.yml",
            "compose.yaml",
            ".dockerignore",
            "container-structure-test.yml",
        ]
        found: list[dict[str, Any]] = []
        for name in container_file_names:
            path = root / name
            found.append({"name": name, "exists": path.is_file()})
        return found
