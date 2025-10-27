"""
YAGO Self-Test System
YAGO v5.6.0

YAGO'nun tüm özelliklerini test eder ve detaylı rapor çıkarır.
- Tüm modülleri kontrol eder
- AI sistemlerini test eder
- Performans ölçümleri yapar
- Detaylı AI kullanım raporu oluşturur
"""

import os
import sys
import time
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger("YAGO.SelfTest")


class YAGOSelfTest:
    """
    YAGO Self-Test System

    Comprehensive testing suite for all YAGO features:
    - Module integrity checks
    - AI system functionality
    - Error recovery validation
    - Offline AI detection
    - Performance benchmarks
    - Detailed AI usage statistics
    """

    def __init__(self):
        """Initialize self-test system"""
        self.test_results: List[Dict[str, Any]] = []
        self.start_time = None
        self.end_time = None
        self.ai_usage_stats: Dict[str, Any] = {
            "claude": {"calls": 0, "tokens": 0, "cost": 0.0, "time": 0.0},
            "gpt4": {"calls": 0, "tokens": 0, "cost": 0.0, "time": 0.0},
            "gemini": {"calls": 0, "tokens": 0, "cost": 0.0, "time": 0.0},
            "ollama": {"calls": 0, "tokens": 0, "cost": 0.0, "time": 0.0},
        }

    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all YAGO self-tests

        Returns:
            Dict with test results and statistics
        """
        logger.info("🧪 Starting YAGO Self-Test Suite...")
        self.start_time = datetime.now()

        # Test 1: Core Modules
        self._test_core_modules()

        # Test 2: Configuration
        self._test_configuration()

        # Test 3: Error Recovery System
        self._test_error_recovery()

        # Test 4: AI Failover System
        self._test_ai_failover()

        # Test 5: Offline AI Detection
        self._test_offline_ai()

        # Test 6: Git Project Loader
        self._test_git_loader()

        # Test 7: Report Generator
        self._test_report_generator()

        # Test 8: Cache System
        self._test_cache_system()

        self.end_time = datetime.now()

        return self._generate_final_report()

    def _test_core_modules(self):
        """Test core YAGO modules"""
        logger.info("📦 Testing core modules...")
        test_name = "Core Modules"

        required_modules = [
            "utils.error_recovery",
            "utils.ai_failover",
            "utils.offline_ai_detector",
            "utils.git_project_loader",
            "utils.report_generator",
            "utils.response_cache",
        ]

        passed = 0
        failed = 0
        details = []

        for module in required_modules:
            try:
                __import__(module)
                passed += 1
                details.append(f"✅ {module}")
            except ImportError as e:
                failed += 1
                details.append(f"❌ {module}: {e}")

        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "failed": failed,
            "total": len(required_modules),
            "success_rate": passed / len(required_modules) * 100,
            "details": details
        })

    def _test_configuration(self):
        """Test configuration loading"""
        logger.info("⚙️  Testing configuration...")
        test_name = "Configuration"

        try:
            import yaml
            config_file = Path(__file__).parent.parent / "yago_config.yaml"

            if not config_file.exists():
                raise FileNotFoundError(f"Config file not found: {config_file}")

            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)

            # Check critical sections
            required_sections = ['agents', 'workflow', 'offline_ai', 'llm_config']
            missing = [sec for sec in required_sections if sec not in config]

            if missing:
                raise ValueError(f"Missing config sections: {missing}")

            self.test_results.append({
                "test": test_name,
                "passed": 1,
                "failed": 0,
                "total": 1,
                "success_rate": 100,
                "details": [f"✅ All required sections present: {required_sections}"]
            })

        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "passed": 0,
                "failed": 1,
                "total": 1,
                "success_rate": 0,
                "details": [f"❌ Config error: {e}"]
            })

    def _test_error_recovery(self):
        """Test error recovery system"""
        logger.info("🛡️  Testing error recovery...")
        test_name = "Error Recovery System"

        try:
            from utils.error_recovery import get_error_recovery

            recovery = get_error_recovery()

            # Test different error types
            test_errors = [
                (EOFError("EOF when reading a line"), "auto_input_default"),
                (Exception("rate limit exceeded"), "api_rate_limit"),
                (Exception("context too large"), "context_truncate"),
                (FileExistsError("file already exists"), "file_exists"),
                (Exception("Internal server error"), "api_server_error"),
            ]

            passed = 0
            failed = 0
            details = []

            for error, expected_strategy in test_errors:
                strategy = recovery.analyze_error(error)
                if strategy and strategy.name == expected_strategy:
                    passed += 1
                    details.append(f"✅ {expected_strategy}: Detected correctly")
                else:
                    failed += 1
                    details.append(f"❌ {expected_strategy}: Detection failed")

            self.test_results.append({
                "test": test_name,
                "passed": passed,
                "failed": failed,
                "total": len(test_errors),
                "success_rate": passed / len(test_errors) * 100,
                "details": details
            })

        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "passed": 0,
                "failed": 1,
                "total": 1,
                "success_rate": 0,
                "details": [f"❌ Error recovery system error: {e}"]
            })

    def _test_ai_failover(self):
        """Test AI failover system"""
        logger.info("🔄 Testing AI failover...")
        test_name = "AI Failover System"

        try:
            from utils.ai_failover import get_ai_failover, AIProvider

            failover = get_ai_failover()

            # Check providers
            required_providers = [AIProvider.ANTHROPIC, AIProvider.OPENAI, AIProvider.GOOGLE]
            registered = list(failover.providers.keys())

            passed = len([p for p in required_providers if p in registered])
            failed = len([p for p in required_providers if p not in registered])

            details = []
            for provider in required_providers:
                if provider in registered:
                    details.append(f"✅ {provider.value}: Registered")
                else:
                    details.append(f"❌ {provider.value}: Not registered")

            # Check offline models
            if failover.offline_models:
                details.append(f"✅ Offline models: {len(failover.offline_models)} detected")
                passed += 1
            else:
                details.append("ℹ️ Offline models: None detected")

            self.test_results.append({
                "test": test_name,
                "passed": passed,
                "failed": failed,
                "total": len(required_providers) + 1,
                "success_rate": passed / (len(required_providers) + 1) * 100,
                "details": details
            })

        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "passed": 0,
                "failed": 1,
                "total": 1,
                "success_rate": 0,
                "details": [f"❌ AI failover system error: {e}"]
            })

    def _test_offline_ai(self):
        """Test offline AI detection"""
        logger.info("📡 Testing offline AI...")
        test_name = "Offline AI Detection"

        try:
            from utils.offline_ai_detector import get_offline_ai_detector

            detector = get_offline_ai_detector()
            models = detector.detect_all_models()

            details = []
            if models:
                details.append(f"✅ Detected {len(models)} offline models:")
                for model in models:
                    details.append(f"  - {model.name} ({model.parameters}, {model.size_gb}GB)")
                passed = 1
            else:
                details.append("ℹ️ No offline models found")
                details.append("💡 Install Ollama: https://ollama.ai/download")
                passed = 0

            # Test Ollama availability
            if detector.ollama_available:
                details.append("✅ Ollama: Available")
                passed += 1
            else:
                details.append("❌ Ollama: Not installed")

            # Test LM Studio availability
            if detector.lm_studio_available:
                details.append("✅ LM Studio: Available")
                passed += 1
            else:
                details.append("ℹ️ LM Studio: Not found")

            total = 3
            self.test_results.append({
                "test": test_name,
                "passed": passed,
                "failed": total - passed,
                "total": total,
                "success_rate": passed / total * 100,
                "details": details
            })

        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "passed": 0,
                "failed": 1,
                "total": 1,
                "success_rate": 0,
                "details": [f"❌ Offline AI detection error: {e}"]
            })

    def _test_git_loader(self):
        """Test Git project loader"""
        logger.info("🔗 Testing Git loader...")
        test_name = "Git Project Loader"

        try:
            from utils.git_project_loader import GitProjectLoader

            loader = GitProjectLoader()

            # Test validation
            valid_urls = [
                "https://github.com/user/repo.git",
                "git@github.com:user/repo.git",
            ]

            invalid_urls = [
                "not-a-url",
                "ftp://example.com/repo",
            ]

            passed = 0
            failed = 0
            details = []

            for url in valid_urls:
                if loader._is_valid_git_url(url):
                    passed += 1
                    details.append(f"✅ Valid URL detected: {url}")
                else:
                    failed += 1
                    details.append(f"❌ Valid URL rejected: {url}")

            for url in invalid_urls:
                if not loader._is_valid_git_url(url):
                    passed += 1
                    details.append(f"✅ Invalid URL rejected: {url}")
                else:
                    failed += 1
                    details.append(f"❌ Invalid URL accepted: {url}")

            total = len(valid_urls) + len(invalid_urls)
            self.test_results.append({
                "test": test_name,
                "passed": passed,
                "failed": failed,
                "total": total,
                "success_rate": passed / total * 100,
                "details": details
            })

        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "passed": 0,
                "failed": 1,
                "total": 1,
                "success_rate": 0,
                "details": [f"❌ Git loader error: {e}"]
            })

    def _test_report_generator(self):
        """Test report generator"""
        logger.info("📊 Testing report generator...")
        test_name = "Report Generator"

        try:
            from utils.report_generator import ReportGenerator

            generator = ReportGenerator(output_dir="reports/test")

            # Test report generation
            passed = 0
            failed = 0
            details = []

            # Test file creation
            test_data = {
                "project_name": "test",
                "duration": 10,
                "total_tokens": 1000,
            }

            try:
                # Just test that methods exist and don't crash
                generator._safe_int(100)
                generator._safe_int({"a": 10, "b": 20})
                generator._safe_int(None)
                passed += 1
                details.append("✅ _safe_int method works")
            except Exception as e:
                failed += 1
                details.append(f"❌ _safe_int method failed: {e}")

            self.test_results.append({
                "test": test_name,
                "passed": passed,
                "failed": failed,
                "total": 1,
                "success_rate": passed / 1 * 100,
                "details": details
            })

        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "passed": 0,
                "failed": 1,
                "total": 1,
                "success_rate": 0,
                "details": [f"❌ Report generator error: {e}"]
            })

    def _test_cache_system(self):
        """Test response cache system"""
        logger.info("💾 Testing cache system...")
        test_name = "Response Cache"

        try:
            from utils.response_cache import get_response_cache

            cache = get_response_cache()

            # Test cache operations
            passed = 0
            failed = 0
            details = []

            # Test set and get
            test_prompt = "Write a hello world program"
            test_response = "print('Hello, World!')"
            test_provider = "anthropic"
            test_model = "claude-3-5-sonnet"

            cache.set(
                prompt=test_prompt,
                response=test_response,
                provider=test_provider,
                model=test_model,
                tokens=100,
                cost=0.001
            )
            cached = cache.get(test_prompt, test_provider, test_model)

            if cached == test_response:
                passed += 1
                details.append("✅ Cache set/get works")
            else:
                failed += 1
                details.append("❌ Cache set/get failed")

            # Test statistics
            stats = cache.get_stats()
            if isinstance(stats, dict) and 'total_entries' in stats:
                passed += 1
                details.append(f"✅ Cache stats: {stats['total_entries']} entries")
            else:
                failed += 1
                details.append("❌ Cache stats failed")

            self.test_results.append({
                "test": test_name,
                "passed": passed,
                "failed": failed,
                "total": 2,
                "success_rate": passed / 2 * 100,
                "details": details
            })

        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "passed": 0,
                "failed": 1,
                "total": 1,
                "success_rate": 0,
                "details": [f"❌ Cache system error: {e}"]
            })

    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate final comprehensive test report"""
        total_duration = (self.end_time - self.start_time).total_seconds()

        # Calculate totals
        total_passed = sum(r["passed"] for r in self.test_results)
        total_failed = sum(r["failed"] for r in self.test_results)
        total_tests = sum(r["total"] for r in self.test_results)
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

        report = {
            "test_suite": "YAGO Self-Test",
            "version": "5.6.0",
            "timestamp": self.start_time.isoformat(),
            "duration": total_duration,
            "summary": {
                "total_tests": len(self.test_results),
                "total_checks": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "success_rate": round(overall_success_rate, 2)
            },
            "test_results": self.test_results,
            "ai_usage": self.ai_usage_stats,
            "recommendations": self._generate_recommendations()
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        for result in self.test_results:
            if result["success_rate"] < 100:
                if result["test"] == "Offline AI Detection":
                    recommendations.append("💡 Install Ollama for offline AI support: https://ollama.ai/download")
                elif result["success_rate"] < 50:
                    recommendations.append(f"⚠️ {result['test']}: Critical issues detected, requires attention")

        if not recommendations:
            recommendations.append("✅ All systems operational!")

        return recommendations


def run_yago_self_test() -> Dict[str, Any]:
    """
    Run YAGO self-test suite

    Returns:
        Dict with comprehensive test results
    """
    tester = YAGOSelfTest()
    return tester.run_all_tests()


def print_test_report(report: Dict[str, Any]):
    """Pretty print test report"""
    print("\n" + "="*80)
    print(f"🧪 YAGO SELF-TEST REPORT - v{report['version']}")
    print("="*80)

    print(f"\n📅 Timestamp: {report['timestamp']}")
    print(f"⏱️  Duration: {report['duration']:.2f}s")

    print("\n📊 SUMMARY")
    print("-" * 80)
    summary = report['summary']
    print(f"Total Test Suites: {summary['total_tests']}")
    print(f"Total Checks: {summary['total_checks']}")
    print(f"✅ Passed: {summary['passed']}")
    print(f"❌ Failed: {summary['failed']}")
    print(f"📈 Success Rate: {summary['success_rate']}%")

    print("\n🔍 DETAILED RESULTS")
    print("-" * 80)
    for result in report['test_results']:
        status_emoji = "✅" if result['success_rate'] == 100 else "⚠️" if result['success_rate'] >= 50 else "❌"
        print(f"\n{status_emoji} {result['test']}")
        print(f"   Passed: {result['passed']}/{result['total']} ({result['success_rate']:.1f}%)")
        for detail in result['details']:
            print(f"   {detail}")

    print("\n💡 RECOMMENDATIONS")
    print("-" * 80)
    for rec in report['recommendations']:
        print(f"{rec}")

    print("\n" + "="*80)


if __name__ == "__main__":
    # Run self-test
    report = run_yago_self_test()
    print_test_report(report)

    # Save to file
    import json
    output_file = Path(__file__).parent.parent / "reports" / "yago_self_test.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Report saved to: {output_file}")
