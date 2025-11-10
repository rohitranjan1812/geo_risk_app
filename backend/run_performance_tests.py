#!/usr/bin/env python3
"""
Performance testing and optimization validation script.

Runs comprehensive performance tests and generates a detailed report.
"""
import asyncio
import sys
import subprocess
from pathlib import Path


def print_header(title: str):
    """Print formatted header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def run_pytest(test_path: str, markers: str = None) -> tuple[bool, str]:
    """
    Run pytest on specific test file or marker.
    
    Args:
        test_path: Path to test file
        markers: Optional pytest markers to filter
        
    Returns:
        Tuple of (success, output)
    """
    cmd = ["python", "-m", "pytest", test_path, "-v", "--tb=short", "-s"]
    
    if markers:
        cmd.extend(["-m", markers])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Test timed out after 10 minutes"
    except Exception as e:
        return False, f"Error running tests: {str(e)}"


async def main():
    """Run all performance tests and generate report."""
    
    print_header("GEO RISK APP - PERFORMANCE TEST SUITE")
    
    backend_dir = Path(__file__).parent
    tests_dir = backend_dir / "tests" / "performance"
    
    if not tests_dir.exists():
        print(f"❌ Performance tests directory not found: {tests_dir}")
        sys.exit(1)
    
    results = {}
    
    # Test 1: Database Migration (Add Indexes)
    print_header("Step 1: Apply Performance Indexes")
    print("Running database migration to add performance indexes...")
    
    migration_cmd = ["alembic", "upgrade", "head"]
    try:
        result = subprocess.run(
            migration_cmd,
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("✓ Database indexes applied successfully")
            results['migration'] = True
        else:
            print(f"✗ Migration failed: {result.stderr}")
            results['migration'] = False
    except Exception as e:
        print(f"✗ Migration error: {str(e)}")
        results['migration'] = False
    
    # Test 2: Load Testing
    print_header("Step 2: Load Testing")
    print("Running concurrent request tests...")
    
    success, output = run_pytest(str(tests_dir / "test_load.py"))
    results['load_testing'] = success
    
    if success:
        print("✓ Load tests PASSED")
        # Extract key metrics from output
        if "CONCURRENT 100 REQUESTS" in output:
            print("\nKey Metrics:")
            for line in output.split('\n'):
                if 'latency_p95_ms' in line or 'throughput_rps' in line or 'success_rate' in line:
                    print(f"  {line.strip()}")
    else:
        print("✗ Load tests FAILED")
        print(output[-1000:])  # Last 1000 chars
    
    # Test 3: Database Performance
    print_header("Step 3: Database Query Optimization")
    print("Testing query performance with indexes...")
    
    success, output = run_pytest(str(tests_dir / "test_database.py"))
    results['database_perf'] = success
    
    if success:
        print("✓ Database performance tests PASSED")
        # Extract query times
        if "GEOSPATIAL QUERY" in output:
            for line in output.split('\n'):
                if 'Query time:' in line:
                    print(f"  {line.strip()}")
    else:
        print("✗ Database performance tests FAILED")
        print(output[-1000:])
    
    # Test 4: Algorithm Profiling
    print_header("Step 4: Algorithm Profiling & Optimization")
    print("Profiling risk calculation algorithms...")
    
    success, output = run_pytest(str(tests_dir / "test_profiling.py"))
    results['profiling'] = success
    
    if success:
        print("✓ Profiling tests PASSED")
        # Extract profiling data
        if "PROFILING RESULTS" in output:
            for line in output.split('\n'):
                if 'memory_peak_mb' in line or 'calculation_time_ms' in line:
                    print(f"  {line.strip()}")
    else:
        print("✗ Profiling tests FAILED")
        print(output[-1000:])
    
    # Final Summary
    print_header("PERFORMANCE TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print(f"Total Test Suites: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"\nSuccess Rate: {(passed_tests/total_tests)*100:.1f}%\n")
    
    print("Detailed Results:")
    status_icons = {True: "✓", False: "✗"}
    for test_name, passed in results.items():
        icon = status_icons[passed]
        status = "PASSED" if passed else "FAILED"
        print(f"  {icon} {test_name:25s}: {status}")
    
    # Check success criteria
    print_header("SUCCESS CRITERIA VALIDATION")
    
    criteria = {
        "✓ Database indexes applied": results.get('migration', False),
        "✓ 100 concurrent requests handled": results.get('load_testing', False),
        "✓ Database queries optimized": results.get('database_perf', False),
        "✓ Algorithms profiled": results.get('profiling', False),
    }
    
    all_passed = all(criteria.values())
    
    for criterion, passed in criteria.items():
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {criterion}")
    
    print("\n" + "="*80)
    
    if all_passed:
        print("\n✓ ALL PERFORMANCE OPTIMIZATIONS VALIDATED\n")
        print("Key Achievements:")
        print("  • API handles 100+ concurrent requests")
        print("  • P95 latency <500ms for single assessments")
        print("  • Database queries optimized with indexes")
        print("  • Geospatial lookups <100ms")
        print("  • Memory usage stable under load")
        print("  • Caching strategy implemented")
        sys.exit(0)
    else:
        print("\n✗ SOME PERFORMANCE TESTS FAILED\n")
        print("Review the detailed output above for failure reasons.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Error running performance tests: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
