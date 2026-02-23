import asyncio
import argparse
import sys
import json
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright, Page, BrowserContext, Browser

# Initialize FastMCP server
print("Initializing FastMCP server...", file=sys.stderr)
mcp = FastMCP("browser")
print("FastMCP server initialized.", file=sys.stderr)

# Global state
browser: Optional[Browser] = None
context: Optional[BrowserContext] = None
page: Optional[Page] = None

async def ensure_browser():
    global browser, context, page
    if browser is None:
        p = await async_playwright().start()
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

@mcp.tool()
async def browser_navigate(url: str) -> str:
    """Navigate/Go to a URL."""
    await ensure_browser()
    if page:
        await page.goto(url)
        title = await page.title()
        return f"Navigated to {url}. Page title: {title}"
    return "Error: Browser not initialized."

@mcp.tool()
async def browser_click(selector: str) -> str:
    """Click an element matching the selector."""
    await ensure_browser()
    if page:
        try:
            await page.click(selector, timeout=5000)
            return f"Clicked element: {selector}"
        except Exception as e:
            return f"Error clicking {selector}: {str(e)}"
    return "Error: Browser not initialized."

@mcp.tool()
async def browser_type(selector: str, text: str) -> str:
    """Type text into an element matching the selector."""
    await ensure_browser()
    if page:
        try:
            await page.fill(selector, text, timeout=5000)
            return f"Typed '{text}' into {selector}"
        except Exception as e:
            return f"Error typing into {selector}: {str(e)}"
    return "Error: Browser not initialized."

@mcp.tool()
async def browser_screenshot(path: Optional[str] = None) -> str:
    """Take a screenshot of the current page. If path is not provided, returns a base64 string (not implemented yet).
    Please provide a path to save the screenshot."""
    await ensure_browser()
    if page:
        target_path = path or "screenshot.png"
        await page.screenshot(path=target_path)
        return f"Screenshot saved to {target_path}"
    return "Error: Browser not initialized."

@mcp.tool()
async def browser_get_content(selector: Optional[str] = None) -> str:
    """Get the text content of an element or the whole page."""
    await ensure_browser()
    if page:
        try:
            if selector:
                content = await page.text_content(selector, timeout=5000)
                return content or "[Empty content]"
            else:
                # Return markdown-like structure or just text
                content = await page.content()
                # Simple html to text conversion could be done here, but for now returning a simplified version
                body_text = await page.inner_text("body")
                return body_text[:10000] # Limit output
        except Exception as e:
            return f"Error getting content: {str(e)}"
    return "Error: Browser not initialized."

@mcp.tool()
async def browser_eval(script: str) -> str:
    """Execute arbitrary JavaScript in the page context."""
    await ensure_browser()
    if page:
        try:
            result = await page.evaluate(script)
            return str(result)
        except Exception as e:
            return f"Error executing script: {str(e)}"
    return "Error: Browser not initialized."

if __name__ == "__main__":
    mcp.run()
