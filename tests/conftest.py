"""Pytest fixtures for Selenium tests."""

from __future__ import annotations

import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        action="store",
        default=os.getenv("BASE_URL", "http://127.0.0.1:8000"),
        help="Base URL of the running F-Bank application.",
    )


@pytest.fixture
def base_url(request) -> str:
    return request.config.getoption("--base-url").rstrip("/")


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,900")

    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(0)
    try:
        yield browser
    finally:
        browser.quit()
