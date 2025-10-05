#!/usr/bin/env python3
"""
Test runner for pension scenarios tests. Supports running individual test files.
Usage: python run_tests.py [test_file]
If no test_file is provided, runs all tests from all test files.
"""

import glob
import importlib.util
import os
import sys
import unittest

# Add the parent directory to the path to allow imports
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
)


def discover_test_files():
    """Discover all test files in the tests directory."""
    test_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests")
    pattern = os.path.join(test_dir, "test_*.py")
    return glob.glob(pattern)


def load_test_from_file(test_file):
    """Load a test suite from a test file."""
    spec = importlib.util.spec_from_file_location("test_module", test_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(module)
    return suite


def run_all_tests():
    """Run all tests from all test files and return results."""
    test_files = discover_test_files()
    combined_suite = unittest.TestSuite()

    for test_file in test_files:
        suite = load_test_from_file(test_file)
        combined_suite.addTest(suite)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(combined_suite)
    return result


def run_single_test_file(test_file):
    """Run tests from a specific test file."""
    try:
        if not os.path.exists(test_file):
            print(f"Test file '{test_file}' not found.")
            return None

        suite = load_test_from_file(test_file)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result
    except Exception as e:
        print(f"Error running test file {test_file}: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test file
        test_file = sys.argv[1]
        result = run_single_test_file(test_file)
        if result and not result.wasSuccessful():
            exit(1)
        elif result is None:
            # Test file not found, show available test files
            print("Available test files:")
            test_files = discover_test_files()
            for test_file in test_files:
                print(f"  {test_file}")
            exit(1)
    else:
        # Run all tests
        result = run_all_tests()
        if not result.wasSuccessful():
            exit(1)
