#!/usr/bin/env python
"""Check that all plugins have help_url pointing to gixy.getpagespeed.com.

This script ensures consistency in plugin documentation URLs.
All plugins must have a help_url that points to the official documentation site.

Usage:
    python scripts/check_plugin_help_urls.py

Exit codes:
    0 - All plugins have valid help_url
    1 - One or more plugins have invalid or missing help_url
"""

import ast
import sys
from pathlib import Path

# Required URL prefix for all plugin help_urls
REQUIRED_URL_PREFIX = "https://gixy.getpagespeed.com/plugins/"

# Plugins that are allowed to have external URLs (special cases)
ALLOWED_EXTERNAL_URLS = {
    # try_files_is_evil_too links to a blog post explaining the issue
    "try_files_is_evil_too": "https://www.getpagespeed.com/",
}


def get_plugin_classes(file_path):
    """
    Parse a Python file and extract plugin class names and their help_url values.

    Args:
        file_path: Path to the plugin Python file.

    Returns:
        List of tuples (class_name, help_url or None if not found).
    """
    results = []

    try:
        with open(file_path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))
    except SyntaxError as e:
        print(f"  ❌ Syntax error in {file_path}: {e}")
        return []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        # Check if this class inherits from Plugin
        is_plugin = False
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Plugin":
                is_plugin = True
                break

        if not is_plugin:
            continue

        # Look for help_url class attribute
        help_url = None
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == "help_url":
                        # Get the value
                        if isinstance(item.value, ast.Constant):
                            help_url = item.value.value
                        elif isinstance(item.value, ast.JoinedStr):
                            # f-string - try to extract literal parts
                            help_url = "<f-string>"

        results.append((node.name, help_url))

    return results


def check_help_url(plugin_name, help_url):
    """
    Check if a plugin's help_url is valid.

    Args:
        plugin_name: Name of the plugin class.
        help_url: The help_url value or None.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if help_url is None:
        return False, "missing help_url attribute"

    if help_url == "<f-string>":
        return False, "help_url should be a literal string, not an f-string"

    # Check for allowed external URLs
    if plugin_name in ALLOWED_EXTERNAL_URLS:
        allowed_prefix = ALLOWED_EXTERNAL_URLS[plugin_name]
        if help_url.startswith(allowed_prefix):
            return True, ""
        else:
            return False, f"should start with {allowed_prefix} or {REQUIRED_URL_PREFIX}"

    # Standard check: must start with the required prefix
    if not help_url.startswith(REQUIRED_URL_PREFIX):
        return False, f"should start with {REQUIRED_URL_PREFIX}"

    # Check URL ends with trailing slash
    if not help_url.endswith("/"):
        return False, "should end with a trailing slash"

    return True, ""


def main():
    """
    Main function to check all plugin help_urls.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    plugins_dir = Path(__file__).parent.parent / "gixy" / "plugins"

    if not plugins_dir.exists():
        print(f"❌ Plugins directory not found: {plugins_dir}")
        return 1

    errors = []
    checked = 0

    print("🔍 Checking plugin help_url values...\n")

    for plugin_file in sorted(plugins_dir.glob("*.py")):
        # Skip __init__.py and base plugin.py
        if plugin_file.name in ("__init__.py", "plugin.py"):
            continue

        plugin_classes = get_plugin_classes(plugin_file)

        for class_name, help_url in plugin_classes:
            checked += 1
            is_valid, error_msg = check_help_url(class_name, help_url)

            if is_valid:
                print(f"  ✅ {class_name}: {help_url}")
            else:
                errors.append((plugin_file.name, class_name, help_url, error_msg))
                print(f"  ❌ {class_name}: {help_url or '(missing)'}")
                print(f"     Error: {error_msg}")

    print(f"\n{'=' * 60}")
    print(f"Checked {checked} plugin(s)")

    if errors:
        print(f"\n❌ Found {len(errors)} error(s):\n")
        for filename, class_name, help_url, error_msg in errors:
            print(f"  - {filename}:{class_name}")
            print(f"    Current: {help_url or '(missing)'}")
            print(f"    Error: {error_msg}")
            print(f"    Expected: {REQUIRED_URL_PREFIX}<slug>/")
            print()

        print("To fix, update the help_url in each plugin class to:")
        print(f'    help_url = "{REQUIRED_URL_PREFIX}<plugin_slug>/"')
        return 1

    print(f"\n✅ All {checked} plugin(s) have valid help_url values!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
