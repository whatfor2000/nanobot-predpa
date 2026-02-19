---
name: browser
description: "A real web browser (Playwright) for advanced web interaction. Use when you need to interact with dynamic websites, take screenshots, handle JavaScript, or when `web_fetch` is insufficient. Supports clicking, typing, and navigation."
---

# Browser Skill

This skill provides a full browser environment using Playwright. It allows you to navigate to pages, interact with elements, type text, and extract content from modern, JavaScript-heavy websites.

## Setup

To use this skill, the **Browser MCP Server** must be running.

### 1. Installation

If not already installed, install the dependencies:

```bash
pip install playwright mcp
playwright install chromium
```

### 2. Configuration

Add the folowing to your `~/.nanobot/config.json` (adjust path as needed):

```json
{
  "tools": {
    "mcpServers": {
      "browser": {
        "command": "python",
        "args": ["/path/to/nanobot/skills/browser/scripts/browser_mcp.py"]
      }
    }
  }
}
```

_Note: The agent can automate this setup if needed._

## Tools

Once configured, the following tools are available:

- `browser_navigate(url)`: Go to a URL.
- `browser_click(selector)`: Click an element matching the selector.
- `browser_type(selector, text)`: Type text into an element.
- `browser_screenshot(path)`: Save a screenshot to a file.
- `browser_get_content(selector)`: Get the text content of an element (or the whole page if selector is empty).
- `browser_eval(script)`: Execute arbitrary JavaScript in the page context.

## Usage Examples

### Search and extract

1. **Navigate**: `browser_navigate("https://google.com")`
2. **Type**: `browser_type("textarea[name='q']", "hello world")`
3. **Click**: `browser_click("input[name='btnK']")`
4. **Read**: `browser_get_content("#search")`

### Troubleshooting

- If elements are not found, use `browser_screenshot` to see what the browser sees.
- Ensure selectors are specific enough.
