# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.23] - 2024-12-19

### Added
- **New plugin: `weak_ssl_tls`**: Detects weak SSL/TLS configurations including:
  - Insecure protocols (SSLv2, SSLv3, TLSv1, TLSv1.1)
  - Weak cipher suites (NULL, DES, RC4, EXPORT, etc.)
  - Missing or weak HSTS headers
  - `ssl_prefer_server_ciphers off` configuration
- **Auto-fix mode**: New `--fix` and `--fix-dry-run` CLI options to automatically apply fixes for detected issues. Creates `.bak` backup files by default (disable with `--no-backup`).
- **Python 3.6 pre-commit check**: Full test suite now runs with Python 3.6 on every commit to ensure compatibility with minimum supported version.
- **README overhaul**: Reorganized plugin documentation into categorized table format with links to official docs.

### Changed
- `scripts/test_py36.sh` now runs the full test suite instead of a subset of tests.

### Fixed
- Added missing HSTS header to staging server in `wordpress_production.conf` integration test.

## [0.2.22] - 2024-12-16

### Added
- **Checkstyle XML output format**: New `-f checkstyle` formatter for CI/CD integration. Works natively with Jenkins, GitLab CI, GitHub Actions (reviewdog), Bitbucket Pipelines, and SonarQube. Maps severities: HIGH→error, MEDIUM→warning, LOW→info.
- **Bandit security scanner**: Added to pre-commit for local security scanning before push.
- **Hardcoded IP address check**: Custom pre-commit hook (`check_hardcoded_ips.py`) mirrors SonarCloud rule S1313 for local detection of hardcoded IPs.
- **Path filters for CI**: GitHub Actions workflow now skips tests when only docs/configs change.

### Changed
- Documentation updated (en/ru/zh) to list `checkstyle` as available output format.

### Fixed
- Added `# NOSONAR` and `# nosec` comments to suppress false positives from security scanners (SonarCloud, Bandit) for intentional patterns like test URLs, Jinja2 autoescape for CLI output, and test IP addresses.

## [0.2.21] - 2024-12-12

### Fixed
- Python 3.6 compatibility: Fixed AST parsing in `check_plugin_help_urls.py` to use `ast.Str` (Python 3.6/3.7) instead of `ast.Constant` (Python 3.8+).

## [0.2.20] - 2024-12-12

### Fixed
- Python 3.6 compatibility: Removed type comments that referenced undefined names (`List`, `Tuple`, `Optional`).

### Added
- Pre-commit configuration with Python 3.6 syntax checking using pyenv.
- CI job `py36-compat` to verify scripts work on Python 3.6 minimum version.

## [0.2.19] - 2024-12-12

### Added
- **Quick Fix Support**: Plugins now return machine-readable fix suggestions in JSON output for IDE integration.
  - `Fix` class in `gixy.core.issue` with `title`, `search`, `replace`, and optional `description` fields.
  - Plugins can use `self.make_fix()` helper to create fixes.
  - JSON formatter includes `fixes` array for each issue.
- **Plugin fixes implemented**:
  - `version_disclosure`: Set `server_tokens off`
  - `host_spoofing`: Replace `$http_host` with `$host`
  - `add_header_content_type`: Use `default_type` instead of `add_header Content-Type`
  - `allow_without_deny`: Add `deny all;` after allow directives
  - `valid_referers`: Remove `none` from referers
  - `error_log_off`: Set proper error_log path
  - `resolver_external`: Use internal DNS resolver
  - `low_keepalive_requests`: Increase keepalive_requests to 10000
- **Pre-commit hooks**: Added `.pre-commit-config.yaml` with plugin help_url validation.
- **CI checks**: Enhanced GitHub Actions workflow with plugin validation checks.

### Fixed
- `version_disclosure` plugin no longer double-reports when `server_tokens on` is at http level.
- Plugin help_url validation script now correctly handles edge cases.

### Changed
- All plugin `help_url` attributes now consistently point to `https://gixy.getpagespeed.com/plugins/`.

## [0.2.14] - 2025-12-06

### Added
- **ReDoS detection rewrite**: Complete rewrite of `regex_redos` plugin using Python's built-in `sre_parse` module - no external dependencies required. Detects nested quantifiers (exponential O(2^n)), overlapping alternatives (polynomial O(n²)), and adjacent greedy quantifiers.
- **nginx 1.29.3 support**: `add_header_redefinition` plugin now respects `add_header_inherit on;` directive.
- **Integration testing**: Added comprehensive WordPress production config (~380 lines) as integration test to catch false positives.
- **Documentation**: Added missing `try_files_is_evil_too.md`, updated plugin list in index.md (now 25 plugins).
- **`if` block variable capture**: `if` blocks with regex conditions (`~`, `~*`) now properly expose capture groups as variables with correct boundary inheritance.

### Changed
- ReDoS plugin now covers `location`, `if`, `rewrite`, `server_name`, and `map` directives.
- Documentation updated for `add_header_redefinition` with nginx 1.29.3+ solution.
- Expanded regex_redos.md with detailed vulnerability patterns and examples.

### Fixed
- Code quality improvements: explicit `autoescape=False` for Jinja2 (plain text output), noqa comments for intentional test patterns and random module usage.
- Legacy code cleanup in regexp.py: replaced alternation with character class, merged string concatenation, improved comments.

## [0.2.13] - 2025-12-06

### Added
- **Rich console formatter**: New beautiful terminal output with colors, panels, and progress indicators using the [Rich](https://github.com/Textualize/rich) library. Automatically enabled in TTY when `rich` is installed. Install with `pip install gixy-ng[rich]`.
- **Line numbers in output**: Issues now display the line number and file path where they were detected.
- **Security score**: The rich console formatter shows a security score (0-100) based on issue severity.
- Directives now track `line` and `file` attributes for better error reporting.
- New CLI tests for plugin options, boolean flag parsing, and module invocation.
- Formatter tests for the new rich console output.

### Changed
- Parser refactored: `parse()` method is now an alias for `parse_string()` for backward compatibility.
- Parser internals cleaned up with new `_build_tree_from_parsed()` method that handles both file and dump parsing uniformly.
- Line number propagation through the parser pipeline for accurate issue location reporting.

### Fixed
- README.md now lists all available plugins including `default_server_flag`, `hash_without_default`, and `return_bypasses_allow_deny`.
- Rich console formatter tests now skip gracefully when `rich` library is not installed.
- CLI default formatter selection now correctly checks if `rich_console` is actually registered (all rich submodules available), preventing argparse failures with partial rich installations.
- Lua blocks (`content_by_lua_block`, etc.) now include line number information for accurate issue location reporting.
- Fixed `TypeError: argument of type 'NoneType' is not iterable` in `add_header_multiline` plugin when header value is None ([#35](https://github.com/dvershinin/gixy/issues/35)).

### Dependencies
- Added optional `rich>=13.0.0` dependency for enhanced terminal output.

## [0.2.12] and earlier

See [GitHub Releases](https://github.com/dvershinin/gixy/releases) for previous changelog entries.
