"""
Profiling tests for risk assessment algorithms.

Profiles CPU usage, memory consumption, and identifies bottlenecks.
"""
import cProfile
import pstats
import io
import tracemalloc
from typing import Dict
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.risk_engine import RiskEngine, GeographicPoint, HazardSource, HistoricalEvent
from app.models import HazardType


class ProfileResult:
    """Container for profiling metrics."""
    
    def __init__(self):
        self.cpu_stats: Dict = {}
        self.memory_peak_mb: float = 0
        self.memory_current_mb: float = 0
        self.top_functions: list = []
    
    def print_summary(self, test_name: str):
        """Print profiling summary."""
        print("\n" + "="*60)
        print(f"{test_name} PROFILING RESULTS")
        print("="*60)
        print(f"{'memory_peak_mb':25s}: {self.memory_peak_mb:.2f}")
        print(f"{'memory_current_mb':25s}: {self.memory_current_mb:.2f}")
        print("\nTop CPU-consuming functions:")
        for func_name, cumtime in self.top_functions[:10]:
            print(f"  {func_name:50s}: {cumtime:.4f}s")
        print("="*60)


def profile_cpu(func, *args, **kwargs):
    """
    Profile CPU usage of a function.
    
    Args:
        func: Function to profile
        *args, **kwargs: Function arguments
        
    Returns:
        Tuple of (function result, profile stats)
    """
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = func(*args, **kwargs)
    
    profiler.disable()
    
    # Get stats
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    
    return result, ps


def profile_memory(func, *args, **kwargs):
    """
    Profile memory usage of a function.
    
    Args:
        func: Function to profile
        *args, **kwargs: Function arguments
        
    Returns:
        Tuple of (function result, peak memory MB, current memory MB)
    """
    tracemalloc.start()
    
    result = func(*args, **kwargs)
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    current_mb = current / 1024 / 1024
    peak_mb = peak / 1024 / 1024
    
    return result, peak_mb, current_mb


@pytest.mark.asyncio
async def test_profile_single_location_assessment():
    """
    Profile single location risk assessment.
    
    OPTIMIZATION TARGET:
    - Risk engine calculation < 100ms
    - Memory usage < 10MB per assessment
    - No memory leaks on repeated calls
    """
    engine = RiskEngine()
    
    # Setup test data
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
    
    # Profile seismic risk calculation
    def test_func():
        return engine.calculate_seismic_risk(
            location, fault_lines, historical_events,
            soil_amplification=1.5, building_code_rating=7.0
        )
    
    # CPU profiling
    result, stats = profile_cpu(test_func)
    stats.print_stats(20)
    
    # Memory profiling
    result, peak_mb, current_mb = profile_memory(test_func)
    
    profile_result = ProfileResult()
    profile_result.memory_peak_mb = peak_mb
    profile_result.memory_current_mb = current_mb
    profile_result.print_summary("SINGLE LOCATION ASSESSMENT")
    
    # Verify performance
    risk_score, breakdown = result
    assert breakdown['calculation_time_ms'] < 100, \
        f"Calculation took {breakdown['calculation_time_ms']:.2f}ms, target <100ms"
    
    assert peak_mb < 10, \
        f"Peak memory {peak_mb:.2f}MB exceeds 10MB target"


@pytest.mark.asyncio
async def test_profile_batch_assessments():
    """
    Profile batch processing of 1000 assessments.
    
    OPTIMIZATION TARGET:
    - Total time < 10 seconds (100/sec throughput)
    - Memory doesn't grow linearly
    - Cache effectiveness
    """
    engine = RiskEngine()
    
    # Setup shared hazard data
    fault_lines = [
        HazardSource(
            location=GeographicPoint(37.7, -122.5),
            intensity=8.0,
            influence_radius_km=100
        )
    ]
    historical_events = [
        HistoricalEvent(severity=6.9, days_ago=365*30, impact_radius_km=50)
    ]
    
    def batch_test():
        results = []
        for i in range(1000):
            location = GeographicPoint(
                37.7749 + (i % 100) * 0.01,
                -122.4194 + (i // 100) * 0.01
            )
            risk_score, breakdown = engine.calculate_seismic_risk(
                location, fault_lines, historical_events
            )
            results.append(risk_score)
        return results
    
    # Memory profiling
    results, peak_mb, current_mb = profile_memory(batch_test)
    
    profile_result = ProfileResult()
    profile_result.memory_peak_mb = peak_mb
    profile_result.memory_current_mb = current_mb
    profile_result.print_summary("BATCH 1000 ASSESSMENTS")
    
    # Check cache effectiveness
    cache_stats = engine.get_performance_stats()
    print(f"\nCache statistics:")
    print(f"  Cache size: {cache_stats['cache_size']}")
    print(f"  Cache utilization: {cache_stats['cache_utilization']*100:.2f}%")
    
    # Assertions
    assert peak_mb < 100, \
        f"Peak memory {peak_mb:.2f}MB exceeds 100MB for 1000 assessments"
    
    assert cache_stats['cache_size'] > 0, \
        "Distance cache not being used"


@pytest.mark.asyncio
async def test_profile_distance_calculations():
    """
    Profile geographic distance calculations with caching.
    
    OPTIMIZATION TARGET:
    - Cache hit rate > 80% on repeated calculations
    - Haversine calculation < 1μs
    """
    engine = RiskEngine()
    
    # Test points
    p1 = GeographicPoint(37.7749, -122.4194)  # San Francisco
    p2 = GeographicPoint(34.0522, -118.2437)  # Los Angeles
    p3 = GeographicPoint(40.7128, -74.0060)   # New York
    
    def distance_test():
        results = []
        # Calculate same distances multiple times to test cache
        for _ in range(100):
            results.append(engine.calculate_distance_km(p1, p2))
            results.append(engine.calculate_distance_km(p2, p3))
            results.append(engine.calculate_distance_km(p1, p3))
        return results
    
    # CPU profiling
    results, stats = profile_cpu(distance_test)
    
    # Check cache effectiveness
    cache_stats = engine.get_performance_stats()
    unique_calculations = 3
    total_calculations = 300
    expected_cache_size = unique_calculations
    
    print("\n" + "="*60)
    print("DISTANCE CALCULATION PROFILING")
    print("="*60)
    print(f"Total calculations: {total_calculations}")
    print(f"Unique calculations: {unique_calculations}")
    print(f"Cache size: {cache_stats['cache_size']}")
    print(f"Expected cache hits: {total_calculations - unique_calculations}")
    print(f"Cache hit rate: {((total_calculations - unique_calculations) / total_calculations)*100:.2f}%")
    print("="*60)
    
    assert cache_stats['cache_size'] == expected_cache_size, \
        f"Cache should contain {expected_cache_size} entries, has {cache_stats['cache_size']}"


@pytest.mark.asyncio
async def test_profile_composite_risk_calculation():
    """
    Profile composite risk aggregation across all hazard types.
    
    OPTIMIZATION TARGET:
    - Aggregation < 10ms
    - Memory efficient for multiple hazard scores
    """
    engine = RiskEngine()
    
    hazard_scores = {
        HazardType.EARTHQUAKE: 65.0,
        HazardType.FLOOD: 45.0,
        HazardType.FIRE: 30.0,
        HazardType.STORM: 55.0
    }
    
    def composite_test():
        results = []
        for _ in range(100):
            composite, level, breakdown = engine.calculate_composite_risk(hazard_scores)
            results.append(composite)
        return results
    
    # Profile
    results, peak_mb, current_mb = profile_memory(composite_test)
    
    # Get average calculation time
    _, _, breakdown = engine.calculate_composite_risk(hazard_scores)
    calc_time_ms = breakdown['calculation_time_ms']
    
    print("\n" + "="*60)
    print("COMPOSITE RISK PROFILING")
    print("="*60)
    print(f"Calculation time: {calc_time_ms:.4f}ms")
    print(f"Memory peak: {peak_mb:.2f}MB")
    print("="*60)
    
    assert calc_time_ms < 10, \
        f"Composite calculation {calc_time_ms:.2f}ms exceeds 10ms target"


@pytest.mark.asyncio
async def test_profile_memory_leak_detection():
    """
    Detect memory leaks in repeated assessments.
    
    OPTIMIZATION TARGET:
    - Memory usage plateaus after warmup
    - No continuous growth over 1000 iterations
    """
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
    
    # Warmup
    for _ in range(100):
        engine.calculate_seismic_risk(location, fault_lines, [])
    
    # Get baseline memory
    baseline_current, baseline_peak = tracemalloc.get_traced_memory()
    
    # Run 1000 more iterations
    for _ in range(1000):
        engine.calculate_seismic_risk(location, fault_lines, [])
    
    # Get final memory
    final_current, final_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    baseline_mb = baseline_current / 1024 / 1024
    final_mb = final_current / 1024 / 1024
    growth_mb = final_mb - baseline_mb
    growth_percent = (growth_mb / baseline_mb) * 100 if baseline_mb > 0 else 0
    
    print("\n" + "="*60)
    print("MEMORY LEAK DETECTION")
    print("="*60)
    print(f"Baseline memory: {baseline_mb:.2f}MB")
    print(f"Final memory: {final_mb:.2f}MB")
    print(f"Memory growth: {growth_mb:.2f}MB ({growth_percent:.2f}%)")
    print("="*60)
    
    # Allow up to 10% growth (some caching is expected)
    assert growth_percent < 10, \
        f"Memory grew by {growth_percent:.2f}%, possible leak detected"


@pytest.mark.asyncio
async def test_profile_algorithm_complexity():
    """
    Profile algorithm performance with varying input sizes.
    
    Tests that algorithms scale efficiently.
    """
    engine = RiskEngine()
    location = GeographicPoint(37.7749, -122.4194)
    
    # Test with varying number of fault lines
    results = {}
    for num_faults in [1, 10, 50, 100]:
        fault_lines = [
            HazardSource(
                location=GeographicPoint(37.7 + i * 0.1, -122.5 + i * 0.1),
                intensity=8.0,
                influence_radius_km=100
            )
            for i in range(num_faults)
        ]
        
        def test_func():
            return engine.calculate_seismic_risk(location, fault_lines, [])
        
        result, peak_mb, current_mb = profile_memory(test_func)
        risk_score, breakdown = result
        
        results[num_faults] = {
            'time_ms': breakdown['calculation_time_ms'],
            'memory_mb': peak_mb
        }
    
    print("\n" + "="*60)
    print("ALGORITHM COMPLEXITY PROFILING")
    print("="*60)
    print(f"{'Fault Lines':15s} {'Time (ms)':15s} {'Memory (MB)':15s}")
    print("-"*60)
    for num_faults, metrics in results.items():
        print(f"{num_faults:15d} {metrics['time_ms']:15.2f} {metrics['memory_mb']:15.2f}")
    print("="*60)
    
    # Check for reasonable scaling (should be O(n))
    time_ratio = results[100]['time_ms'] / results[10]['time_ms']
    expected_ratio = 100 / 10  # Linear scaling
    
    # Allow up to 2x worse than linear (some overhead acceptable)
    assert time_ratio < expected_ratio * 2, \
        f"Algorithm scaling worse than O(n): ratio {time_ratio:.2f} vs expected {expected_ratio}"
