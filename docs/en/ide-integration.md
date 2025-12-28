---
title: "IDE Integration"
description: "Use Gixy directly in your IDE with the Visual Studio Code extension for real-time NGINX security analysis."
---

# IDE Integration

Get real-time NGINX security feedback directly in your editor.

## Visual Studio Code

The [vscode-gixy](https://github.com/dvershinin/vscode-gixy) extension brings Gixy's security analysis directly into VS Code.

### Features

- **Real-time scanning** - Automatic analysis as you edit NGINX config files
- **Inline diagnostics** - Security issues highlighted directly in the editor
- **Quick fixes** - Suggested remediation for common issues
- **Hover information** - Detailed explanations when hovering over issues
- **Problem panel integration** - All issues listed in VS Code's Problems panel

### Installation

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "gixy"
4. Click Install

Or install from the command line:

```bash
code --install-extension dvershinin.vscode-gixy
```

### Requirements

The extension requires Gixy to be installed:

```bash
pip install gixy-ng
```

### Configuration

Configure the extension in VS Code settings:

```json
{
  "gixy.executable": "gixy",
  "gixy.runOnSave": true,
  "gixy.runOnOpen": true
}
```

### Screenshots

Issues are displayed inline with severity indicators:

- 🔴 **Error** - High severity security issues
- 🟡 **Warning** - Medium severity issues
- 🔵 **Info** - Low severity recommendations

Click on any issue to see detailed information and documentation links.

## Other Editors

### JetBrains IDEs (IntelliJ, PyCharm, WebStorm)

Use the [Checkstyle-IDEA plugin](https://plugins.jetbrains.com/plugin/1065-checkstyle-idea) with Gixy's checkstyle output:

1. Run `gixy --format checkstyle nginx.conf > gixy-report.xml`
2. Import the report in the Checkstyle plugin

### Vim/Neovim

Use [ALE](https://github.com/dense-analysis/ale) or [nvim-lint](https://github.com/mfussenegger/nvim-lint) with a custom linter configuration:

```vim
" ALE configuration for Gixy
let g:ale_linters = {
\   'nginx': ['gixy'],
\}
```

### Sublime Text

Use [SublimeLinter](https://github.com/SublimeLinter/SublimeLinter) with a custom linter plugin, or run Gixy from the build system:

```json
{
    "cmd": ["gixy", "$file"],
    "selector": "source.nginx"
}
```

## Terminal Integration

### Click-to-Jump

Gixy's rich console output formats file locations in a terminal-compatible format:

```
📍 /etc/nginx/nginx.conf:42
```

Most modern terminals (iTerm2, Windows Terminal, VS Code integrated terminal) support clicking these paths to jump directly to the file and line.

--8<-- "en/snippets/nginx-extras-cta.md"
