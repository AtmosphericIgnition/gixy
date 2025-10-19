import re
import gixy
from gixy.plugins.plugin import Plugin
from gixy.core.regexp import Regexp


class invalid_regex_group(Plugin):
    """
    Detects usage of numeric backreferences in rewrite replacement that are not
    provided by the rewrite pattern (e.g., using $1 without a capturing group).
    """

    summary = "Rewrite references non-existent capture group"
    description = (
        "The rewrite replacement references a numeric capture group (e.g., $1), "
        "but the pattern does not define enough capturing groups."
    )
    help_url = (
        "https://github.com/dvershinin/gixy/blob/master/docs/en/plugins/invalid_regex_group.md"
    )
    severity = gixy.severity.LOW
    directives = ["rewrite"]

    def audit(self, directive):
        # Expecting a RewriteDirective-like object with pattern and replace attrs
        try:
            pattern = getattr(directive, "pattern", None)
            replace = getattr(directive, "replace", None)
            if not pattern or not replace:
                return

            # Count available capturing groups in the pattern
            # groups dict includes key 0 for the whole match; we want numbered groups >= 1
            regexp = Regexp(pattern, case_sensitive=True)
            available_group_ids = [
                k for k in regexp.groups.keys() if isinstance(k, int) and k >= 1
            ]
            max_available = max(available_group_ids) if available_group_ids else 0

            # Find all numeric backrefs used in the replacement, support $1, $2, ... $10
            used_group_ids = [int(m) for m in re.findall(r"\$(\d+)", str(replace))]
            if not used_group_ids:
                return

            invalid_ids = sorted({g for g in used_group_ids if g > max_available})
            if not invalid_ids:
                return

            # Build a clear reason message
            invalid_list = ", ".join(f"${g}" for g in invalid_ids)
            reason = (
                f"Replacement references {invalid_list}, but pattern defines only "
                f"{max_available} capture group(s)."
            )
            # Report at the rewrite directive location
            self.add_issue(directive=directive, reason=reason)
        except Exception:
            # Be resilient; never break the analyzer for plugin errors
            return
