# terminal-mac

An isolated macOS guest desktop for computer-use agents, viewed and controlled from a terminal or through AXIM agent tools.

`terminal-mac` runs a genuine macOS guest on Apple silicon using Apple Virtualization. A bundled helper **inside that guest** captures its screen and posts input events. A terminal viewer streams that screen using Kitty or iTerm2 graphics, while agent commands drive the guest without touching the physical Mac's display, pointer, or clipboard.

The guest is a separate Mac: it has its own apps, files, accounts, and permissions. It does not inherit running host applications or signed-in sessions.

## Requirements

- Apple silicon Mac (M1/M2/M3/M4), macOS 14 or later.
- Internet on first run to download a compatible macOS IPSW restore image from Apple.
- Sufficient disk space for restore image and growing VM disk (64 GiB default sparse allocation).
- Terminal with graphics support (Ghostty, Kitty, iTerm2) for the inline viewer, or native VM window.

## Installation

```sh
# Build from source inside the plugin directory
bash scripts/build.sh

# Check host support
./dist/terminal-mac doctor
```

Install the compiled binary to your PATH:
```sh
bash scripts/install.sh --prefix ~/.local
```

## Use with AXIM Agents

`terminal-mac` integrates with AXIM as a native plugin with both an Agent Skill and an MCP server (`screenshot`, `click`, `drag`, `scroll`, `type`, `key`, `status`):

### Register MCP in AXIM

Add the server to AXIM (`~/.axim/plugins/installed/terminal-mac/mcp.json` or CLI):

```sh
axim mcp add terminal-mac -- terminal-mac mcp default
```

Tools provided:
- `status`: Check if the VM is running and guest permissions are granted.
- `screenshot`: Capture the guest desktop (returns PNG).
- `click`: Click at `(x, y)` (`button: "left" | "right"`, `clicks: 1..3`).
- `move`: Move cursor to `(x, y)`.
- `drag`: Click and drag between points.
- `type`: Type literal text into focused controls.
- `key`: Send keyboard shortcuts (`cmd+space`, `return`, `cmd+c`...).
- `scroll`: Scroll at coordinate.

### CLI Usage

```bash
# Verify status
terminal-mac status default

# Take a screenshot
terminal-mac action default screenshot --output /tmp/guest.png

# Automate input
terminal-mac action default click 640 400
terminal-mac action default type "Hello AXIM"
terminal-mac action default key cmd+space
terminal-mac action default scroll --dy -300 --x 640 --y 400
```

## First-Time Guest Setup

1. Start setup:
   ```sh
   terminal-mac up default
   ```
2. Complete Apple Setup Assistant in the VM window and create a user account.
3. Inside the guest, open Finder → `/Volumes/My Shared Files/tools` → `TerminalMacGuest.app`.
4. Grant **Screen Recording** and **Accessibility** inside the guest System Settings.
5. Close setup. The guest helper will run in the background for agent interactions.

## Lifecycle Management

```sh
terminal-mac ls                          # List VMs
terminal-mac status default              # Check state
terminal-mac pause default               # Pause execution
terminal-mac resume default              # Resume execution
terminal-mac show default                # Show VM window
terminal-mac hide default                # Hide VM window
terminal-mac stop default                # Graceful shutdown
terminal-mac stop default --force        # Immediate power off
```

## Testing & Validation

```sh
swift test
```
