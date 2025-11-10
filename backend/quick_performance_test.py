#!/usr/bin/env python3
"""
Quick performance validation script.

Tests key performance metrics without full suite.
"""
import asyncio
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.risk_engine import RiskEngine, GeographicPoint, HazardSource, HistoricalEvent
from app.models import HazardType


def print_section(title):
    """Print formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_risk_engine_performance():
    """Test risk engine performance."""
    print_section("RISK ENGINE PERFORMANCE TEST")
    
    engine = RiskEngine()
    location = GeographicPoint(37.7749, -122.4194)
    
    fault_lines = [
        HazardSource(
            location=GeographicPoint(37.7, -122.5),
            intensity=8.0,
            influence_radius_km=100
        )
    ]
    
    historical_events = [
        HistoricalEvent(severity=6.9, days_ago=365*30, impact_radius_km=50),
        HistoricalEvent(severity=5.5, days_ago=365*5, impact_radius_km=30)
    ]
    
    # Single assessment test
    start_time = time.time()
    risk_score, breakdown = engine.calculate_seismic_risk(
        location, fault_lines, historical_events
    )
    single_time_ms = (time.time() - start_time) * 1000
    
    print(f"Single Assessment:")
    print(f"  Risk Score: {risk_score}")
    print(f"  Time: {single_time_ms:.2f}ms")
    print(f"  Target: <100ms")
    print(f"  Status: {'✓ PASS' if single_time_ms < 100 else '✗ FAIL'}")
    
    # Batch assessment test
    print(f"\nBatch Assessment (100 locations):")
    start_time = time.time()
    
    for i in range(100):
        loc = GeographicPoint(37.7749 + i * 0.01, -122.4194 + i * 0.01)
        engine.calculate_seismic_risk(loc, fault_lines, historical_events)
    
    batch_time = time.time() - start_time
    throughput = 100 / batch_time
    
    print(f"  Total Time: {batch_time:.2f}s")
    print(f"  Throughput: {throughput:.2f} assessments/sec")
    print(f"  Target: >10/sec")
    print(f"  Status: {'✓ PASS' if throughput > 10 else '✗ FAIL'}")
    
    # Cache effectiveness
    cache_stats = engine.get_performance_stats()
    print(f"\nCache Statistics:")
    print(f"  Cache Size: {cache_stats['cache_size']}")
    print(f"  Utilization: {cache_stats['cache_utilization']*100:.1f}%")
    
    return single_time_ms < 100 and throughput > 10


def test_distance_cache():
    """Test distance calculation caching."""
    print_section("DISTANCE CALCULATION CACHE TEST")
    
    engine = RiskEngine()
    
    p1 = GeographicPoint(37.7749, -122.4194)
    p2 = GeographicPoint(34.0522, -118.2437)
    
    # First calculation
    start_time = time.time()
    dist1 = engine.calculate_distance_km(p1, p2)
    first_time = (time.time() - start_time) * 1000000  # microseconds
    
    # Second calculation (should be cached)
    start_time = time.time()
    dist2 = engine.calculate_distance_km(p1, p2)
    second_time = (time.time() - start_time) * 1000000
    
    speedup = first_time / second_time if second_time > 0 else float('inf')
    
    print(f"First calculation: {first_time:.2f}μs")
    print(f"Cached calculation: {second_time:.2f}μs")
    print(f"Speedup: {speedup:.1f}x")
    print(f"Distance: {dist1:.2f}km")
    print(f"Cache working: {'✓ YES' if speedup > 2 else '✗ NO'}")
    
    return speedup > 2


def test_composite_risk_performance():
    """Test composite risk aggregation."""
    print_section("COMPOSITE RISK AGGREGATION TEST")
    
    engine = RiskEngine()
    
    hazard_scores = {
        HazardType.EARTHQUAKE: 65.0,
        HazardType.FLOOD: 45.0,
        HazardType.FIRE: 30.0,
        HazardType.STORM: 55.0
    }
    
    # Test aggregation performance
    start_time = time.time()
    
    for _ in range(1000):
        composite, level, breakdown = engine.calculate_composite_risk(hazard_scores)
    
    total_time = time.time() - start_time
    avg_time_ms = (total_time / 1000) * 1000
    
    print(f"1000 aggregations: {total_time:.3f}s")
    print(f"Average time: {avg_time_ms:.4f}ms")
    print(f"Target: <10ms")
    print(f"Status: {'✓ PASS' if avg_time_ms < 10 else '✗ FAIL'}")
    
    return avg_time_ms < 10


def test_memory_stability():
    """Test memory usage stability."""
    print_section("MEMORY STABILITY TEST")
    
    import tracemalloc
    
    engine = RiskEngine()
    location = GeographicPoint(37.7749, -122.4194)
    fault_lines = [
        HazardSource(
            location=GeographicPoint(37.7, -122.5),
            intensity=8.0,
            influence_radius_km=100
        )
    ]
    
    tracemalloc.start()
    
    # Baseline
    for _ in range(100):
        engine.calculate_seismic_risk(location, fault_lines, [])
    
    baseline_current, baseline_peak = tracemalloc.get_traced_memory()
    
    # Extended run
    for _ in range(1000):
        engine.calculate_seismic_risk(location, fault_lines, [])
    
    final_current, final_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    baseline_mb = baseline_current / 1024 / 1024
    final_mb = final_current / 1024 / 1024
    growth_mb = final_mb - baseline_mb
    
    # Only calculate growth percent if baseline is meaningful
    if baseline_mb > 0.01:  # More than 10KB
        growth_percent = (growth_mb / baseline_mb) * 100
    else:
        # If baseline is tiny, just check absolute growth
        growth_percent = 0 if growth_mb < 1.0 else 100  # Pass if <1MB growth
    
    print(f"Baseline memory: {baseline_mb:.2f}MB")
    print(f"After 1000 iterations: {final_mb:.2f}MB")
    print(f"Growth: {growth_mb:.2f}MB ({growth_percent:.2f}%)")
    print(f"Target: <10% growth (or <1MB absolute)")
    print(f"Status: {'✓ PASS' if (growth_percent < 10 or growth_mb < 1.0) else '✗ FAIL'}")
    
    return growth_percent < 10 or growth_mb < 1.0


def main():
    """Run all performance tests."""
    print("\n" + "="*70)
    print("  GEO RISK APP - QUICK PERFORMANCE VALIDATION")
    print("="*70)
    
    results = {}
    
    # Run tests
    results['risk_engine'] = test_risk_engine_performance()
    results['distance_cache'] = test_distance_cache()
    results['composite_risk'] = test_composite_risk_performance()
    results['memory_stability'] = test_memory_stability()
    
    # Summary
    print_section("PERFORMANCE TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"\nSuccess Rate: {(passed/total)*100:.1f}%\n")
    
    for test_name, passed_flag in results.items():
        status = "✓ PASS" if passed_flag else "✗ FAIL"
        print(f"  {status:10s} {test_name}")
    
    print("\n" + "="*70)
    
    if all(results.values()):
        print("\n✓ ALL PERFORMANCE TESTS PASSED\n")
        print("Key Metrics:")
        print("  • Single assessment <100ms")
        print("  • Batch throughput >10/sec")
        print("  • Distance caching active")
        print("  • Composite aggregation <10ms")
        print("  • Memory stable (<10% growth)")
        print()
        return 0
    else:
        print("\n✗ SOME PERFORMANCE TESTS FAILED\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
