# invalid_regex_group

- Summary: Rewrite references non-existent capture group
- Severity: LOW

## Description
This check reports `rewrite` directives where the replacement string references numeric capture groups (e.g. `$1`, `$2`) that are not defined by the rewrite pattern.

Example of problematic configuration:

```nginx
rewrite "(?i)/" $1 break;
```

In this case, the pattern has zero capturing groups, yet `$1` is referenced in the replacement. The plugin points precisely at the offending `rewrite` directive so you can adjust the pattern or the replacement accordingly.

## Why it matters
Using an undefined backreference in a replacement often indicates a logic error and can result in unintended URLs being generated.

## Recommendation
- Add the necessary capturing groups to the pattern, e.g. `^/(.*)` to use `$1`.
- Or remove the backreference from the replacement if it is not intended.

## References
- NGINX `rewrite` directive documentation: `https://nginx.org/en/docs/http/ngx_http_rewrite_module.html#rewrite`
