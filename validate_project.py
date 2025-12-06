"""
Test runner script for RiskOptimizer

This script runs all tests for the RiskOptimizer project to validate functionality
before packaging and delivery.
"""

import argparse
import os
import subprocess
import sys


def run_command(command: Any, cwd: Any = None) -> Any:
    """Run a shell command and return the result"""
    logger.info(f"Running: {command}")
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
        logger.info(f"Success: {result.stdout}")
        return (True, result.stdout)
    except subprocess.CalledProcessError as e:
        logger.info(f"Error: {e.stderr}")
        return (False, e.stderr)


def run_backend_tests(project_root: Any) -> Any:
    """Run backend tests"""
    logger.info("\n=== Running Backend Tests ===\n")
    backend_dir = os.path.join(project_root, "code", "backend")
    success, _ = run_command("pip install pytest pytest-cov", cwd=backend_dir)
    if not success:
        return False
    success, _ = run_command("pip install -r requirements.txt", cwd=backend_dir)
    if not success:
        return False
    success, output = run_command("python -m pytest -v", cwd=backend_dir)
    return success


def run_ai_model_tests(project_root: Any) -> Any:
    """Run AI model tests"""
    logger.info("\n=== Running AI Model Tests ===\n")
    ai_models_dir = os.path.join(project_root, "code", "ai_models")
    success, _ = run_command(
        "pip install numpy pandas scikit-learn scipy matplotlib joblib pytest",
        cwd=ai_models_dir,
    )
    if not success:
        return False
    training_script = os.path.join(
        ai_models_dir, "training_scripts", "advanced_model_training.py"
    )
    if os.path.exists(training_script):
        success, _ = run_command(f"python {training_script}", cwd=ai_models_dir)
        if not success:
            return False
    return True


def run_blockchain_tests(project_root: Any) -> Any:
    """Run blockchain tests"""
    logger.info("\n=== Running Blockchain Tests ===\n")
    blockchain_dir = os.path.join(project_root, "code", "blockchain")
    success, _ = run_command("npm install -g truffle", cwd=blockchain_dir)
    if not success:
        return False
    success, _ = run_command("truffle compile", cwd=blockchain_dir)
    return success


def validate_integration(project_root: Any) -> Any:
    """Validate integration between components"""
    logger.info("\n=== Validating Integration ===\n")
    backend_dir = os.path.join(project_root, "code", "backend")
    test_script = '\nimport sys\nimport os\n\nfrom core.logging import get_logger\nlogger = get_logger(__name__)\nsys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\ntry:\n    from ai_models.optimization_model import AdvancedPortfolioOptimizer\n    logger.info("Successfully imported AI models")\n    optimizer = AdvancedPortfolioOptimizer()\n    logger.info("Successfully created optimizer instance")\n    exit(0)\nexcept Exception as e:\n    logger.info(f"Error: {e}")\n    exit(1)\n'
    test_script_path = os.path.join(backend_dir, "test_integration.py")
    with open(test_script_path, "w") as f:
        f.write(test_script)
    success, _ = run_command(f"python test_integration.py", cwd=backend_dir)
    os.remove(test_script_path)
    return success


def main() -> Any:
    parser = argparse.ArgumentParser(description="Run tests for RiskOptimizer")
    parser.add_argument(
        "--project-root",
        default="/home/ubuntu/RiskOptimizer",
        help="Path to RiskOptimizer project root",
    )
    args = parser.parse_args()
    project_root = args.project_root
    logger.info(f"Validating RiskOptimizer project at: {project_root}")
    backend_success = run_backend_tests(project_root)
    ai_success = run_ai_model_tests(project_root)
    blockchain_success = run_blockchain_tests(project_root)
    integration_success = validate_integration(project_root)
    logger.info("\n=== Test Summary ===\n")
    logger.info(f"Backend Tests: {('PASSED' if backend_success else 'FAILED')}")
    logger.info(f"AI Model Tests: {('PASSED' if ai_success else 'FAILED')}")
    logger.info(f"Blockchain Tests: {('PASSED' if blockchain_success else 'FAILED')}")
    logger.info(f"Integration Tests: {('PASSED' if integration_success else 'FAILED')}")
    if backend_success and ai_success and blockchain_success and integration_success:
        logger.info("\nAll tests PASSED! Project is ready for packaging.")
        return 0
    else:
        logger.info("\nSome tests FAILED. Please fix issues before packaging.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
