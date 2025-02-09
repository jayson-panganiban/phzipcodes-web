from typing import Literal

import pytest
from playwright.async_api import async_playwright

BrowserType = Literal["chromium", "firefox", "webkit"]

BROWSER_OPTIONS = {
    "headless": True,
    "slow_mo": 0,
    "timeout": 30000,
    "args": [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
    ],
}

BASE_URL = "http://localhost:8000"

VIEWPORTS = {
    "mobile": {"width": 375, "height": 667},
    "desktop": {"width": 1280, "height": 720},
}


@pytest.fixture(params=["chromium", "firefox", "webkit"])
async def browser(request):
    async with async_playwright() as p:
        browser = await getattr(p, request.param).launch(**BROWSER_OPTIONS)
        yield browser
        await browser.close()


@pytest.fixture(scope="function")
async def context(browser):
    context = await browser.new_context()
    yield context
    await context.close()


@pytest.fixture(scope="function")
async def page(context):
    page = await context.new_page()
    await page.goto(BASE_URL)
    yield page


@pytest.fixture(scope="function")
async def mobile_page(context):
    page = await context.new_page()
    await page.set_viewport_size(VIEWPORTS["mobile"])
    await page.goto(BASE_URL)
    yield page


@pytest.fixture(scope="function")
async def desktop_page(context):
    page = await context.new_page()
    await page.set_viewport_size(VIEWPORTS["desktop"])
    await page.goto(BASE_URL)
    yield page
