#!/usr/bin/env python3
"""Validate the frontend container contract without requiring Docker images."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class FrontendContainerContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dockerfile = (ROOT / "frontend/Dockerfile").read_text(encoding="utf-8")
        cls.nginx = (ROOT / "frontend/nginx.conf").read_text(encoding="utf-8")
        cls.root_ignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
        cls.frontend_ignore = (ROOT / "frontend/.dockerignore").read_text(encoding="utf-8")
        cls.compose = yaml.safe_load(
            (ROOT / "deploy/docker-compose.yml").read_text(encoding="utf-8")
        )

    def test_dockerfile_is_reproducible_two_stage_build(self) -> None:
        self.assertIn("FROM node:22-alpine AS build", self.dockerfile)
        self.assertIn("COPY package*.json ./", self.dockerfile)
        self.assertIn("RUN npm ci", self.dockerfile)
        self.assertIn("ARG VITE_BASE_PATH=/learn/", self.dockerfile)
        self.assertIn("RUN npm run build", self.dockerfile)
        self.assertIn("FROM nginx:1.27.5-alpine", self.dockerfile)
        self.assertIn("COPY --from=build /app/dist /usr/share/nginx/html", self.dockerfile)

    def test_build_context_ignores_local_outputs(self) -> None:
        for entry in ("frontend/node_modules", "frontend/dist", "frontend/*.tsbuildinfo"):
            self.assertIn(entry, self.root_ignore)
        for entry in ("node_modules", "dist", "test-results", "playwright-report"):
            self.assertIn(entry, self.frontend_ignore)

    def test_nginx_preserves_same_origin_and_cache_boundaries(self) -> None:
        self.assertIn("location /api/", self.nginx)
        self.assertIn("proxy_pass http://agent-adapter:8081", self.nginx)
        self.assertIn('Cache-Control "no-store"', self.nginx)
        self.assertIn("max-age=31536000, immutable", self.nginx)
        self.assertIn("try_files $uri $uri/ /index.html", self.nginx)

    def test_compose_frontend_health_and_adapter_dependency(self) -> None:
        frontend = self.compose["services"]["frontend"]
        self.assertEqual(frontend["build"]["context"], "../frontend")
        self.assertEqual(frontend["build"]["args"]["VITE_BASE_PATH"], "/learn/")
        self.assertIn("wget", frontend["healthcheck"]["test"][1])
        self.assertEqual(
            frontend["depends_on"]["agent-adapter"]["condition"], "service_healthy"
        )
        self.assertEqual(
            self.compose["services"]["caddy"]["depends_on"]["frontend"]["condition"],
            "service_healthy",
        )


if __name__ == "__main__":
    result = unittest.main(exit=False)
    if result.result.wasSuccessful():
        print("FRONTEND_CONTAINER_CONTRACT_OK")
    raise SystemExit(0 if result.result.wasSuccessful() else 1)
