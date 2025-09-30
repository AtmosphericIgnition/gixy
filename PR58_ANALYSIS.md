# PR #58 Analysis: Support geo and map directives

## Summary
PR #58 adds comprehensive support for tracking variables through `map` and `geo` directives, enabling security analysis of configurations that use these blocks. However, **PR #58 is based on the old pyparsing parser**, while master has migrated to crossplane.

## PR #58 Overview
- **Title**: Support geo and map directives. Add hash_without_default.py.
- **Author**: @MegaManSec
- **Status**: Open since May 2025
- **Changes**: 26 files, 459 additions, 42 deletions
- **Closes**: Issue #24

## Master Branch Status
The master branch has **completely migrated from pyparsing to crossplane** for nginx configuration parsing. This migration makes the parser-specific changes in PR #58 obsolete.

## What PR #58 Attempts to Fix

### Core Problem
Gixy currently cannot track variables through `map` and `geo` blocks, leading to **false negatives** in security analysis:

```nginx
# This SHOULD trigger SSRF warning but doesn't currently
map $uri $backend {
    ~^/api/(.*)$ "$1";
    default "http://localhost:8080";
}
server {
    location / {
        proxy_pass http://$backend;  # No warning - gixy doesn't know $backend can contain user input
    }
}
```

```nginx
# This SHOULD trigger http_splitting warning but doesn't currently
map $host $map_host {
    ~*/(.*) $1;
    default 1;
}
add_header x-header $map_host;  # No warning - gixy doesn't know $map_host can contain \r\n
```

### Current Master Behavior
Testing confirms these issues exist:
```bash
$ gixy test_ssrf_map.conf
==================== Results ===================
No issues found.  # FALSE NEGATIVE!
```

## Analysis of PR #58 Changes

### 1. Parser Changes (OBSOLETE)
**File**: `gixy/parser/raw_parser.py`

❌ **Status**: Not applicable - file now uses crossplane, not pyparsing

PR #58 modifies pyparsing grammar to handle `hash_value` blocks. This is no longer relevant since crossplane handles parsing.

### 2. MapDirective Class (NEEDS PORTING)
**File**: `gixy/directives/directive.py`

✅ **Status**: Core concept still relevant

PR #58 creates a new `MapDirective` class to represent individual map/geo entries. Currently, these are parsed as generic `Directive` objects. The concept is valid but needs to be implemented differently for crossplane.

Key features:
- Represents map/geo key-value pairs
- Tracks whether key is a regex pattern
- Provides variables from regex capture groups
- Has `src_val` (key) and `dest_val` (value) attributes

### 3. Enhanced MapBlock and GeoBlock (NEEDS PORTING)
**File**: `gixy/directives/block.py`

✅ **Status**: Core functionality still needed

Current master has TODO placeholders:
```python
@cached_property
def variables(self):
    # TODO(buglloc): Finish him!
    return [
        Variable(
            name=self.variable,
            value="",  # Empty - doesn't track actual values!
            boundary=None,
            provider=self,
            have_script=False,
        )
    ]
```

PR #58 implements:
- Gathering map entries from children (including nested includes)
- Processing regex patterns in map keys
- Creating variables with proper values and boundaries
- Context tracking via `ctx` parameter

### 4. Variable Context Tracking (NEEDS PORTING)
**Files**: `gixy/core/variable.py`, `gixy/core/context.py`

✅ **Status**: Core functionality needed

PR #58 adds a `ctx` parameter to variables for tracking map/geo context. This enables:
- Distinguishing variables with same name in different map contexts
- Resolving variables through multiple levels of maps
- Better logging when variables can't be found

Key changes:
- `Variable.__init__` accepts `ctx` parameter
- `Context.add_var` and `Context.get_var` use `(ctx, name)` as key when ctx is present
- Enhanced logging shows which block failed to resolve a variable

### 5. Enhanced Variable Analysis (NEEDS PORTING)
**File**: `gixy/core/variable.py`

✅ **Status**: Core functionality needed

PR #58 enhances `Variable` methods to check map values:
- `can_contain(char)` - checks if any map destination can contain char
- `can_startswith(char)` - checks if any map destination can start with char
- `must_contain(char)` - checks if all map destinations must contain char
- `must_startswith(char)` - checks if all map destinations must start with char

This is essential for security plugins to detect vulnerabilities.

### 6. New hash_without_default Plugin (NEEDS PORTING)
**File**: `gixy/plugins/hash_without_default.py`

✅ **Status**: New functionality worth adding

Detects when map/geo blocks don't have a default value, which can lead to security issues:
```nginx
map $host $value {
    example.com "safe";
    # Missing default - $value will be empty string for non-matching hosts
}
```

Severity: MEDIUM

### 7. Test Cases (NEED ADAPTING)
**Files**: Multiple test files in `tests/`

✅ **Status**: Test scenarios are valuable

PR #58 includes comprehensive test cases:
- Map/geo directive parsing tests
- SSRF detection with map values
- HTTP splitting detection with map values  
- Multi-level map resolution (map → map → map)
- hash_without_default plugin tests

Test scenarios are valuable and should be adapted for the crossplane-based implementation.

### 8. Formatter Changes (NEEDS PORTING)
**File**: `gixy/formatters/base.py`

✅ **Status**: Presentation improvement needed

Expands MapBlock/GeoBlock directives in output to show actual map entries instead of just the block.

## Crossplane vs Pyparsing: Key Differences

### How Crossplane Parses Map Blocks

```json
{
  "directive": "map",
  "args": ["$host", "$hostmap"],
  "block": [
    {
      "directive": "example.com",
      "args": ["value"]
    },
    {
      "directive": "default",
      "args": ["default_val"]
    }
  ]
}
```

Map entries are represented as directives with:
- `directive` = the key (e.g., "example.com", "default", "~regex")
- `args` = array with the value

This is **already compatible** with creating MapDirective objects in the nginx_parser!

### Implementation Strategy for Crossplane

The nginx_parser.py already has a directive factory pattern:

```python
def _get_directive_class(self, parsed_type, parsed_name):
    # Returns the appropriate directive class based on type and name
    ...
```

We can add logic to detect when we're inside a MapBlock or GeoBlock and create MapDirective instances for the children.

## Recommendation

**Action**: Extract and port the core functionality from PR #58

### What to Port (Priority Order)

1. **MapDirective class** (HIGH PRIORITY)
   - Create new directive type for map/geo entries
   - Detect in nginx_parser when parent is MapBlock/GeoBlock
   - Parse regex patterns and track src_val/dest_val

2. **Enhanced MapBlock/GeoBlock.variables** (HIGH PRIORITY)
   - Implement TODO to return proper variables
   - Gather MapDirective children
   - Create variables with correct values/boundaries

3. **Variable context tracking** (HIGH PRIORITY)
   - Add `ctx` parameter to Variable
   - Update Context.add_var/get_var to use context
   - Enable multi-level map resolution

4. **Enhanced Variable analysis methods** (HIGH PRIORITY)
   - Update can_contain/can_startswith to check map values
   - Update must_contain/must_startswith to check map values
   - Critical for security plugin accuracy

5. **hash_without_default plugin** (MEDIUM PRIORITY)
   - New security check for missing defaults
   - Relatively easy to implement once MapDirective exists

6. **Formatter improvements** (LOW PRIORITY)
   - Better output formatting for map/geo blocks
   - Nice to have but not critical

### What NOT to Port

❌ **raw_parser.py pyparsing changes** - Crossplane handles parsing
❌ **Pyparsing grammar modifications** - Not applicable
❌ **nginx_parser.py path_stack tracking** - May not be needed with crossplane

## Implementation Approach

Since crossplane already parses map blocks correctly, the implementation is simpler than PR #58:

1. **Detect map/geo children in nginx_parser.py**
   ```python
   def parse_block(self, parsed_block, parent):
       for parsed in parsed_block:
           # If parent is MapBlock or GeoBlock, treat children as MapDirective
           if isinstance(parent, (MapBlock, GeoBlock)):
               directive_class = MapDirective
           else:
               directive_class = self._get_directive_class(...)
   ```

2. **Implement MapDirective** (simpler than PR #58 since crossplane handles parsing)
   ```python
   class MapDirective(Directive):
       def __init__(self, name, args):
           super().__init__(name, args)
           self.src_val = name  # Key from crossplane
           self.dest_val = args[0] if args else None  # Value from crossplane
           # Detect and parse regex patterns
   ```

3. **Implement MapBlock.variables** using MapDirective children
4. **Add context tracking** to Variable class
5. **Update security plugins** to use enhanced variable analysis

## Test Results Needed

Before porting, we need to verify:
- [ ] How crossplane handles regex patterns in map keys
- [ ] How crossplane handles special map directives (include, hostnames, etc.)
- [ ] Whether crossplane preserves case sensitivity markers (~* vs ~)
- [ ] How geo block special directives (proxy, delete, ranges) are parsed

## Suggested PR Comment for #58

See `/tmp/pr58_comment.md` for the detailed comment to post on the PR.

**Summary**: 
- Close PR as pyparsing-specific implementation cannot merge
- Port core functionality to crossplane-based parser
- Credit @MegaManSec for identifying the gap and the solution approach
- Offer collaboration on the port

## Next Steps

1. Create test cases to verify crossplane behavior
2. Implement MapDirective class
3. Implement enhanced MapBlock/GeoBlock.variables
4. Add variable context tracking
5. Update variable analysis methods
6. Add hash_without_default plugin
7. Verify all test cases pass
8. Document the changes

## Conclusion

PR #58 identifies and fixes a **critical gap** in gixy's security analysis. While the pyparsing-specific implementation cannot be directly merged, the core functionality should be ported to work with the crossplane-based parser.

Estimated effort: **Medium** (2-3 days)
Priority: **High** (fixes false negatives in security analysis)
