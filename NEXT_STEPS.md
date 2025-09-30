# Next Steps for PR #58

This document outlines the immediate and follow-up actions needed based on the PR #58 review.

## Immediate Actions (Do These First)

### 1. Post Comment to PR #58
**File**: `/tmp/pr58_comment.md`

```bash
# Copy the comment
cat /tmp/pr58_comment.md

# Then post it to: https://github.com/dvershinin/gixy/pull/58
```

The comment:
- Thanks @MegaManSec for the contribution
- Explains why it can't merge (pyparsing → crossplane migration)
- Commits to porting the functionality
- Offers collaboration

### 2. Close PR #58
After posting the comment:
- Close the PR as "not mergeable"
- Reason: Implementation is pyparsing-specific
- Note: Functionality will be ported

### 3. Create Issue for Porting
Create a new issue:

**Title**: Port map/geo directive support from PR #58 to crossplane

**Body**:
```markdown
PR #58 by @MegaManSec identifies and fixes critical security false negatives in gixy when analyzing map/geo blocks.

## The Problem
Gixy currently has FALSE NEGATIVES for:
- SSRF through map variables
- HTTP splitting through map variables
- Missing defaults in map/geo blocks

See PR58_ANALYSIS.md for complete details.

## What Needs to Be Done
Port the following from PR #58 to work with crossplane:

### HIGH PRIORITY (fixes false negatives)
1. MapDirective class for map/geo entries
2. Enhanced MapBlock/GeoBlock.variables to track actual values
3. Variable context tracking (ctx parameter)
4. Enhanced variable analysis (can_contain, must_contain, etc.)

### MEDIUM PRIORITY (new security check)
5. hash_without_default plugin

## Implementation Notes
- See PR58_ANALYSIS.md for detailed implementation strategy
- Crossplane already parses map blocks correctly
- Implementation should be simpler than the pyparsing version
- Estimated effort: 2-3 days

## References
- Original PR: #58
- Analysis: PR58_ANALYSIS.md
- Demo: Run `./demonstrate_pr58_issue.sh`

## Credit
@MegaManSec for identifying the issue and solution approach.
```

**Labels**: 
- `enhancement`
- `security`
- `high-priority`

## Follow-Up Implementation

### Phase 1: MapDirective Class
**File**: `gixy/directives/directive.py`

Add MapDirective class that:
- Represents individual map/geo entries
- Has `src_val` (key) and `dest_val` (value) properties
- Detects regex patterns in keys (`~` or `~*`)
- Parses regex and extracts capture groups
- Provides variables from capture groups

### Phase 2: Parser Integration
**File**: `gixy/parser/nginx_parser.py`

Modify parser to:
- Detect when inside MapBlock or GeoBlock
- Create MapDirective instances for children
- Handle special map directives (include, hostnames, etc.)

### Phase 3: Enhanced MapBlock/GeoBlock
**File**: `gixy/directives/block.py`

Implement:
- MapBlock.variables to return list of map values
- GeoBlock.variables to return list of geo values
- Gather MapDirective children (including from includes)
- Process regex patterns and create proper variables

### Phase 4: Variable Context Tracking
**Files**: `gixy/core/variable.py`, `gixy/core/context.py`

Add:
- `ctx` parameter to Variable class
- Context-aware variable storage and retrieval
- Multi-level map resolution (map → map → map)
- Better logging for variable resolution failures

### Phase 5: Enhanced Variable Analysis
**File**: `gixy/core/variable.py`

Update methods to check map values:
- `can_contain(char)` - check if any map dest can contain char
- `can_startswith(char)` - check if any map dest can start with char
- `must_contain(char)` - check if all map dests must contain char
- `must_startswith(char)` - check if all map dests must start with char

### Phase 6: hash_without_default Plugin
**File**: `gixy/plugins/hash_without_default.py`

Create new plugin that:
- Checks map/geo blocks for default value
- Reports MEDIUM severity if missing
- Helps prevent security bypasses

### Phase 7: Testing
**Directory**: `tests/`

Port test cases from PR #58:
- Map/geo directive parsing tests
- SSRF detection with map values
- HTTP splitting detection with map values
- Multi-level map resolution
- hash_without_default plugin tests

Adapt tests for crossplane-based implementation.

## Validation Checklist

Before merging the port:
- [ ] SSRF through map variables is detected
- [ ] HTTP splitting through map variables is detected
- [ ] Multi-level map resolution works (map → map → map)
- [ ] hash_without_default plugin works
- [ ] All existing tests still pass
- [ ] New tests from PR #58 are ported and pass
- [ ] No regressions in other plugins
- [ ] Documentation is updated

## Success Criteria

The port is successful when:
1. `./demonstrate_pr58_issue.sh` shows warnings instead of "No issues found"
2. All tests pass
3. No false positives introduced
4. @MegaManSec is credited in commits and changelog

## Timeline

Estimated total: 2-3 days
- Day 1: MapDirective class + parser integration
- Day 2: Enhanced MapBlock/GeoBlock + variable tracking
- Day 3: Enhanced variable analysis + plugin + testing

## Questions?

Review the analysis documents:
- Quick overview: REVIEW_SUMMARY.md
- Full details: PR58_ANALYSIS.md
- Main doc: README_PR58_REVIEW.md
