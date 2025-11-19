"""
Test runner script for RiskOptimizer

This script runs all tests for the RiskOptimizer project to validate functionality
before packaging and delivery.
"""

import argparse
import os
import subprocess
import sys


def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print(f"Success: {result.stdout}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False, e.stderr


def run_backend_tests(project_root):
    """Run backend tests"""
    print("\n=== Running Backend Tests ===\n")
    backend_dir = os.path.join(project_root, "code", "backend")

    # Check if pytest is installed
    success, _ = run_command("pip install pytest pytest-cov", cwd=backend_dir)
    if not success:
        return False

    # Install requirements
    success, _ = run_command("pip install -r requirements.txt", cwd=backend_dir)
    if not success:
        return False

    # Run tests
    success, output = run_command("python -m pytest -v", cwd=backend_dir)
    return success


def run_ai_model_tests(project_root):
    """Run AI model tests"""
    print("\n=== Running AI Model Tests ===\n")
    ai_models_dir = os.path.join(project_root, "code", "ai_models")

    # Install required packages
    success, _ = run_command(
        "pip install numpy pandas scikit-learn scipy matplotlib joblib pytest",
        cwd=ai_models_dir,
    )
    if not success:
        return False

    # Run training script to validate model
    training_script = os.path.join(
        ai_models_dir, "training_scripts", "advanced_model_training.py"
    )
    if os.path.exists(training_script):
        success, _ = run_command(f"python {training_script}", cwd=ai_models_dir)
        if not success:
            return False

    return True


def run_blockchain_tests(project_root):
    """Run blockchain tests"""
    print("\n=== Running Blockchain Tests ===\n")
    blockchain_dir = os.path.join(project_root, "code", "blockchain")

    # Check if contracts compile
    success, _ = run_command("npm install -g truffle", cwd=blockchain_dir)
    if not success:
        return False

    success, _ = run_command("truffle compile", cwd=blockchain_dir)
    return success


def validate_integration(project_root):
    """Validate integration between components"""
    print("\n=== Validating Integration ===\n")

    # Check if backend can import AI models
    backend_dir = os.path.join(project_root, "code", "backend")
    test_script = """
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from ai_models.optimization_model import AdvancedPortfolioOptimizer
    print("Successfully imported AI models")
    optimizer = AdvancedPortfolioOptimizer()
    print("Successfully created optimizer instance")
    exit(0)
except Exception as e:
    print(f"Error: {e}")
    exit(1)
"""

    # Write test script
    test_script_path = os.path.join(backend_dir, "test_integration.py")
    with open(test_script_path, "w") as f:
        f.write(test_script)

    # Run test script
    success, _ = run_command(f"python test_integration.py", cwd=backend_dir)

    # Clean up
    os.remove(test_script_path)

    return success


def main():
    parser = argparse.ArgumentParser(description="Run tests for RiskOptimizer")
    parser.add_argument(
        "--project-root",
        default="/home/ubuntu/RiskOptimizer",
        help="Path to RiskOptimizer project root",
    )
    args = parser.parse_args()

    project_root = args.project_root

    print(f"Validating RiskOptimizer project at: {project_root}")

    # Run tests
    backend_success = run_backend_tests(project_root)
    ai_success = run_ai_model_tests(project_root)
    blockchain_success = run_blockchain_tests(project_root)
    integration_success = validate_integration(project_root)

    # Print summary
    print("\n=== Test Summary ===\n")
    print(f"Backend Tests: {'PASSED' if backend_success else 'FAILED'}")
    print(f"AI Model Tests: {'PASSED' if ai_success else 'FAILED'}")
    print(f"Blockchain Tests: {'PASSED' if blockchain_success else 'FAILED'}")
    print(f"Integration Tests: {'PASSED' if integration_success else 'FAILED'}")

    # Overall result
    if backend_success and ai_success and blockchain_success and integration_success:
        print("\nAll tests PASSED! Project is ready for packaging.")
        return 0
    else:
        print("\nSome tests FAILED. Please fix issues before packaging.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
