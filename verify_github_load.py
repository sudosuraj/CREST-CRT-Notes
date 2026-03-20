import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        file_path = f"file://{os.path.abspath('index.html')}"
        await page.goto(file_path)

        page.on("console", lambda msg: print("PAGE CONSOLE LOG:", msg.text))

        await page.evaluate("""
            window.prompt = function(msg, defaultVal) {
                if (typeof msg === 'string' && msg.includes('repository')) return 'github/gitignore';
                if (typeof msg === 'string' && msg.includes('branch')) return 'main';
                return defaultVal;
            };
        """)

        print("Clicking 'Load from GitHub' button...")
        await page.click('#loadFromGithub')

        print("Waiting for file items...")
        await page.wait_for_selector('.file-item', timeout=15000)

        await page.wait_for_timeout(2000)

        # Print all file items
        file_items = await page.locator('.file-item').all_text_contents()
        print("LOADED FILES:", [f.strip() for f in file_items])

        await browser.close()

asyncio.run(main())
