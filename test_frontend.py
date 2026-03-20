import asyncio
from playwright.async_api import async_playwright
import os

async def verify_ui():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        file_path = f"file://{os.path.abspath('index.html')}"
        await page.goto(file_path)

        # Basic Checks
        assert await page.locator('#loadFromGithub').is_visible(), "GitHub button not found"

        await browser.close()
        print("UI Test passed.")

asyncio.run(verify_ui())
