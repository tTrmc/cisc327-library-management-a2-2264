import os
import subprocess
import time
from contextlib import suppress
from urllib.request import urlopen

import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:5000"


def _wait_for_server(url: str, timeout: float = 15.0) -> None:
    """Poll the app until it responds or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urlopen(url, timeout=1) as resp:
                if resp.status < 500:
                    return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError("Flask app did not become ready in time")


@pytest.fixture(scope="session", autouse=True)
def app_server():
    """Start the Flask app once for all E2E tests."""
    if os.path.exists("library.db"):
        os.remove("library.db")
    proc = subprocess.Popen(
        ["python", "app.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    try:
        _wait_for_server(f"{BASE_URL}/catalog")
        yield
    finally:
        proc.terminate()
        with suppress(ProcessLookupError, subprocess.TimeoutExpired):
            proc.wait(timeout=5)


def test_add_and_borrow_book(app_server):
    timestamp = int(time.time())
    title = f"E2E Book {timestamp}"
    author = "Playwright Tester"
    isbn_suffix = f"{timestamp % 10_000_000_000:010d}"
    isbn = f"978{isbn_suffix}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(f"{BASE_URL}/catalog", wait_until="networkidle")

        page.get_by_role("link", name="➕ Add Book").click()
        page.fill("input#title", title)
        page.fill("input#author", author)
        page.fill("input#isbn", isbn)
        page.fill("input#total_copies", "2")
        page.click("button:has-text('Add Book to Catalog')")

        page.wait_for_url(f"{BASE_URL}/catalog")
        page.wait_for_selector(".flash-success")
        assert "successfully added" in page.inner_text(".flash-success").lower()

        row = page.locator("table tbody tr").filter(has_text=isbn)
        assert row.count() == 1

        row.locator("input[name='patron_id']").fill("123456")
        row.locator("button:has-text('Borrow')").click()

        page.wait_for_url(f"{BASE_URL}/catalog")
        page.wait_for_selector(".flash-success")
        assert "successfully borrowed" in page.inner_text(".flash-success").lower()

        availability_text = row.locator("td:nth-child(5)").inner_text()
        assert "1/2" in availability_text

        browser.close()
