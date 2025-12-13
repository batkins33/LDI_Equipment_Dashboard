"""
Test script to verify all SysPulse modules work correctly

Run this to test each module individually before running full scan
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.browser_scanner import BrowserScanner
from modules.startup_analyzer import StartupAnalyzer
from modules.storage_sense import StorageSense
from modules.process_explainer import ProcessExplainer


def test_browser_scanner():
    """Test browser scanner module"""
    print("=" * 60)
    print("Testing Browser Scanner")
    print("=" * 60)

    scanner = BrowserScanner()
    profiles = scanner.scan_all()

    print(f"\n✓ Found {len(profiles)} browser profiles")

    if profiles:
        summary = scanner.get_summary()
        print(f"  Total cache: {summary['total_cache_size']}")
        print(f"  Total extensions: {summary['total_extensions']}")
        print(f"  Browsers: {', '.join(summary['browsers_found'])}")

        print("\n  Sample profile:")
        sample = profiles[0].to_dict()
        print(f"    {sample['browser']} - {sample['name']}")
        print(f"    Cache: {sample['cache_size_human']}")
        print(f"    Extensions: {sample['extensions_count']}")
    else:
        print("  (No profiles found - this is OK if no browsers installed)")

    print("\n✅ Browser Scanner OK\n")


def test_startup_analyzer():
    """Test startup analyzer module"""
    print("=" * 60)
    print("Testing Startup Analyzer")
    print("=" * 60)

    analyzer = StartupAnalyzer()
    items = analyzer.scan_all()

    print(f"\n✓ Found {len(items)} startup items")

    if items:
        summary = analyzer.get_summary()
        print(f"  High impact: {summary['high_impact_count']}")
        print(f"  Safe to disable: {summary['safe_to_disable_count']}")
        print(f"  Est. boot delay: {summary['estimated_boot_delay_seconds']}s")

        if summary['top_recommendations']:
            print("\n  Sample recommendation:")
            rec = summary['top_recommendations'][0]
            print(f"    {rec['name']} [{rec['impact']}]")
            print(f"    {rec['recommendation']}")
    else:
        print("  (No startup items found - may need admin privileges)")

    print("\n✅ Startup Analyzer OK\n")


def test_storage_sense():
    """Test storage sense module"""
    print("=" * 60)
    print("Testing Storage Sense")
    print("=" * 60)

    storage = StorageSense()
    categories = storage.scan_all(quick_scan=True)

    print(f"\n✓ Scanned {len(categories)} storage categories")

    summary = storage.get_summary()
    print(f"  Total size: {summary['total_size']}")
    print(f"  Safe to clean: {summary['safe_to_clean_size']}")

    if summary['high_priority_cleanups']:
        print(f"\n  High priority cleanups: {len(summary['high_priority_cleanups'])}")
        for cleanup in summary['high_priority_cleanups'][:2]:
            print(f"    • {cleanup['name']}: {cleanup['size']}")

    print("\n✅ Storage Sense OK\n")


def test_process_explainer():
    """Test process explainer module"""
    print("=" * 60)
    print("Testing Process Explainer")
    print("=" * 60)

    explainer = ProcessExplainer()
    processes = explainer.scan_all(min_memory_mb=100)  # Only significant processes

    print(f"\n✓ Found {len(processes)} significant processes")

    summary = explainer.get_summary()
    print(f"  Total CPU: {summary['total_cpu_percent']}%")
    print(f"  Total Memory: {summary['total_memory_gb']} GB")

    if summary['top_cpu']:
        print("\n  Top CPU process:")
        top = summary['top_cpu'][0]
        print(f"    {top['name']} - {top['cpu_percent']}%")
        print(f"    {top['description']}")

    if summary['top_memory']:
        print("\n  Top Memory process:")
        top = summary['top_memory'][0]
        print(f"    {top['name']} - {top['memory_mb']:.1f} MB")
        print(f"    {top['description']}")

    print("\n✅ Process Explainer OK\n")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SysPulse Module Tests")
    print("=" * 60)
    print("\nTesting all modules individually...\n")

    try:
        test_browser_scanner()
        test_startup_analyzer()
        test_storage_sense()
        test_process_explainer()

        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nAll modules working correctly!")
        print("You can now run: python syspulse.py\n")

        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
