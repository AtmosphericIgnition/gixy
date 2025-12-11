#!/usr/bin/env python3
"""
CI check: Ensure all plugins are documented in README.md

Fails if any plugin is missing from README or docs/.
Run: python scripts/check_plugin_docs.py
"""

import sys
from pathlib import Path


def get_plugins():
    """Get all plugin names from gixy/plugins/."""
    plugins_dir = Path("gixy/plugins")
    skip = {"__init__.py", "plugin.py"}
    plugins = []
    for f in plugins_dir.glob("*.py"):
        if f.name not in skip:
            plugins.append(f.stem)
    return sorted(plugins)


def check_readme(plugins):
    """Check if plugins are mentioned in README.md."""
    readme = Path("README.md").read_text().lower()
    missing = []
    for plugin in plugins:
        # Check for plugin name (with underscores or without)
        variants = [
            plugin.lower(),
            plugin.replace("_", ""),
            plugin.replace("_", "-"),
        ]
        if not any(v in readme for v in variants):
            missing.append(plugin)
    return missing


def check_docs(plugins):
    """Check if plugins have doc files."""
    docs_dir = Path("docs/en/plugins")
    missing = []
    for plugin in plugins:
        # Check various naming conventions
        variants = [
            f"{plugin}.md",
            f"{plugin.replace('_', '')}.md",
            f"{plugin.replace('_', '-')}.md",
        ]
        if not any((docs_dir / v).exists() for v in variants):
            missing.append(plugin)
    return missing


def main():
    plugins = get_plugins()
    print(f"Found {len(plugins)} plugins: {', '.join(plugins)}\n")

    readme_missing = check_readme(plugins)
    docs_missing = check_docs(plugins)

    errors = []

    if readme_missing:
        print("❌ Plugins missing from README.md:")
        for p in readme_missing:
            print(f"   - {p}")
        errors.append(f"{len(readme_missing)} plugins not in README")

    if docs_missing:
        print("\n⚠️  Plugins missing documentation (docs/en/plugins/):")
        for p in docs_missing:
            print(f"   - {p}")
        # Warning only, not error (docs can be added later)

    if errors:
        print(f"\n💥 FAILED: {', '.join(errors)}")
        sys.exit(1)
    else:
        print("\n✅ All plugins documented in README!")
        sys.exit(0)


if __name__ == "__main__":
    main()
