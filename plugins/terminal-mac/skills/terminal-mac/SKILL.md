---
name: terminal-mac
description: Operate an isolated virtual Mac (macOS guest VM) with screenshots, clicks, typing, and shortcuts for safe computer-use tasks without touching the host desktop.
keywords:
  - terminal-mac
  - mac vm
  - virtual mac
  - macos guest
  - mac desktop
  - mac automation
  - macos virtualization
  - computer use
  - screen capture
  - guest mac
---

# Terminal Mac

`terminal-mac` runs an isolated macOS guest VM on Apple silicon using Apple Virtualization. A helper inside the guest captures its screen and posts input, so actions happen entirely in the VM without touching the host desktop.

## Prefer MCP Tools

When the `terminal-mac` MCP server is enabled in AXIM, use its computer-use tools:

1. `status`: Verify the VM is running and guest permissions are granted (`screenRecording: true`, `accessibility: true`).
2. `screenshot`: Capture the guest desktop. All coordinates `(x, y)` passed to action tools are pixel coordinates from this image (top-left origin).
3. Act with:
   - `click`: Click at `(x, y)` (`clicks: 2` for double-click, `button: "right"` for right-click).
   - `move`: Move the pointer to `(x, y)`.
   - `drag`: Press at `(x, y)`, drag to `(toX, toY)`, and release.
   - `type`: Type literal text into the focused field.
   - `key`: Press key combinations (e.g., `cmd+space`, `cmd+c`, `cmd+v`, `return`, `tab`, `escape`).
   - `scroll`: Scroll at `(x, y)` (negative `dy` scrolls down).
4. Verify: Pass `screenshot: true` with actions or call `screenshot` to observe state before next steps.

Example workflow to launch an application:
- `key`: `cmd+space` (opens Spotlight)
- `type`: `"Safari"`
- `key`: `return`

## CLI Fallback

If MCP is unavailable, use the `terminal-mac` CLI directly. Commands emit JSON and return non-zero exit codes on failure:

```bash
terminal-mac status default                     # Verify VM status
terminal-mac action default status              # Check guest helper permissions
terminal-mac action default screenshot --output /tmp/guest.png
terminal-mac action default click 500 300
terminal-mac action default type "Hello"
terminal-mac action default key cmd+space
terminal-mac action default scroll --dy -300 --x 500 --y 300
```

## User Escalation & Safety

- **Guest Login / Authentication**: If the guest helper reports "no logged-in session", pause and ask the user to log in (`terminal-mac view default`).
- **Permission Prompts**: If macOS dialogs, passwords, or keychain prompts appear inside the guest, request user intervention.
- **Isolation Boundary**: Never run `terminal-mac guest` on the host, and never substitute host automation tools for guest tools. All VM resources remain strictly isolated from host files and accounts.
