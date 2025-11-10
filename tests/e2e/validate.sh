#!/bin/bash

echo "=== E2E Test Suite Validation ==="
echo ""

cd "$(dirname "$0")"

errors=0

echo "Checking test structure..."

# Check required files
required_files=(
    "package.json"
    "playwright.config.ts"
    "tsconfig.json"
    "setup.sh"
    "run-tests.sh"
    "README.md"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ Missing: $file"
        errors=$((errors + 1))
    fi
done

# Check required directories
required_dirs=(
    "specs"
    "fixtures"
    "utils"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "✓ $dir/"
    else
        echo "✗ Missing directory: $dir"
        errors=$((errors + 1))
    fi
done

echo ""
echo "Checking test specs..."

specs=(
    "specs/01-user-journey.spec.ts"
    "specs/02-multi-hazard.spec.ts"
    "specs/03-error-handling.spec.ts"
    "specs/04-cross-browser.spec.ts"
    "specs/05-performance.spec.ts"
)

for spec in "${specs[@]}"; do
    if [ -f "$spec" ]; then
        lines=$(wc -l < "$spec")
        echo "✓ $spec ($lines lines)"
    else
        echo "✗ Missing spec: $spec"
        errors=$((errors + 1))
    fi
done

echo ""
echo "Checking utilities and fixtures..."

utils=(
    "utils/api-helpers.ts"
    "utils/page-objects.ts"
)

for util in "${utils[@]}"; do
    if [ -f "$util" ]; then
        echo "✓ $util"
    else
        echo "✗ Missing: $util"
        errors=$((errors + 1))
    fi
done

fixtures=(
    "fixtures/locations.json"
    "fixtures/test-scenarios.json"
)

for fixture in "${fixtures[@]}"; do
    if [ -f "$fixture" ]; then
        echo "✓ $fixture"
    else
        echo "✗ Missing: $fixture"
        errors=$((errors + 1))
    fi
done

echo ""
echo "Checking TypeScript syntax..."

if command -v npx &> /dev/null; then
    if npx tsc --noEmit 2>&1 | grep -q "error TS"; then
        echo "✗ TypeScript errors found"
        errors=$((errors + 1))
    else
        echo "✓ TypeScript syntax OK"
    fi
else
    echo "⚠ npx not found, skipping TypeScript check"
fi

echo ""
echo "=== Validation Results ==="

if [ $errors -eq 0 ]; then
    echo "✅ All checks passed!"
    echo ""
    echo "To run tests:"
    echo "  1. ./setup.sh       # Install dependencies"
    echo "  2. ./run-tests.sh   # Run E2E tests"
    exit 0
else
    echo "❌ Found $errors error(s)"
    exit 1
fi
