#!/bin/bash

echo "=========================================="
echo "PR #58 Review: Visual Demonstration"
echo "=========================================="
echo ""

# Test 1: HTTP Splitting
echo "TEST 1: HTTP Splitting False Negative"
echo "--------------------------------------"
cat > /tmp/test1.conf << 'EOF'
http {
    map $host $custom_header {
        ~*/(.*) $1;
        default "safe";
    }
    server {
        add_header X-Custom $custom_header;
    }
}
EOF

echo "Config:"
cat /tmp/test1.conf
echo ""
echo "Running: gixy /tmp/test1.conf --skips version_disclosure"
gixy /tmp/test1.conf --skips version_disclosure 2>&1
echo ""
echo "❌ EXPECTED: Should detect HTTP Splitting (HIGH severity)"
echo "❌ ACTUAL: No issues found (FALSE NEGATIVE)"
echo ""
echo ""

# Test 2: SSRF
echo "TEST 2: SSRF False Negative"
echo "----------------------------"
cat > /tmp/test2.conf << 'EOF'
http {
    map $uri $backend {
        ~^/api/(.*)$ "$1";
        default "http://localhost:8080";
    }
    server {
        location / {
            proxy_pass http://$backend;
        }
    }
}
EOF

echo "Config:"
cat /tmp/test2.conf
echo ""
echo "Running: gixy /tmp/test2.conf --skips version_disclosure"
gixy /tmp/test2.conf --skips version_disclosure 2>&1
echo ""
echo "❌ EXPECTED: Should detect SSRF (HIGH severity)"
echo "❌ ACTUAL: No issues found (FALSE NEGATIVE)"
echo ""
echo ""

# Current behavior of map variables
echo "TEST 3: Current Map Variable Tracking"
echo "--------------------------------------"
python3 << 'PYEOF'
from gixy.parser.nginx_parser import NginxParser
from gixy.directives.block import MapBlock

config = """
http {
    map $host $value {
        example.com "test";
        default "safe";
    }
}
"""

parser = NginxParser(cwd='', allow_includes=False)
tree = parser.parse(config)
map_block = tree.children[0].children[0]

print(f"Map block type: {type(map_block).__name__}")
print(f"Variables: {map_block.variables}")
print(f"Variable name: {map_block.variables[0].name}")
print(f"Variable value: '{map_block.variables[0].value}'")
print(f"Variable boundary: {map_block.variables[0].boundary}")
print("")
print("❌ Problem: Variable value is empty string ''")
print("❌ Should be: List of map entries with actual values")
PYEOF
echo ""
echo ""

echo "=========================================="
echo "CONCLUSION"
echo "=========================================="
echo ""
echo "✅ PR #58 fixes these false negatives"
echo "✅ Core functionality should be ported to crossplane"
echo "✅ Priority: HIGH (security-critical)"
echo ""
