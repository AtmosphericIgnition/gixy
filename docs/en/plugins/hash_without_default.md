## hash_without_default

Detects use of hash blocks (`map`, `geo`) without a `default` entry.

- Severity: Medium
- Directives: `map`, `geo`

### Why it matters

When a `map` or `geo` block omits a `default` value, unexpected keys may result in empty variables or unintended fallbacks, potentially bypassing security logic.

### Example (will trigger)

```nginx
geo $country_code {
  127.0.0.1  ZZ;
}
```

### Example (safe)

```nginx
geo $country_code {
  default    XX;
  127.0.0.1  ZZ;
}
```


