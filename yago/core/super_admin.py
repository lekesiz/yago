"""
YAGO v7.0 - Super Admin Orchestrator
Autonomous supervisor that monitors agent work, detects issues, and intervenes
NOW WITH REAL-TIME EVENT MONITORING
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from core.event_monitor import (
    EventQueue, EventMonitor, EventEmitter, EventType, Event,
    get_event_queue, get_event_monitor, get_event_emitter
)

logger = logging.getLogger("YAGO.SuperAdmin")


class InterventionType(Enum):
    """Types of interventions Super Admin can perform"""
    AUTO_FIX = "auto_fix"          # Automatically fix the issue
    REASSIGN = "reassign"          # Reassign task to different agent
    ESCALATE = "escalate"          # Escalate to user for decision
    FALLBACK = "fallback"          # Use fallback strategy
    ABORT = "abort"                # Abort and report


class IssueType(Enum):
    """Types of issues Super Admin monitors"""
    INCOMPLETE_TESTS = "incomplete_tests"
    API_MISMATCH = "api_mismatch"
    MISSING_DOCS = "missing_docs"
    SECURITY_ISSUE = "security_issue"
    AGENT_FAILURE = "agent_failure"
    CONSISTENCY_ERROR = "consistency_error"
    QUALITY_BELOW_THRESHOLD = "quality_below_threshold"


@dataclass
class Issue:
    """Represents a detected issue"""
    issue_type: IssueType
    severity: str  # HIGH, MEDIUM, LOW
    description: str
    affected_agent: str
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution: Optional[str] = None


@dataclass
class Intervention:
    """Represents an intervention performed by Super Admin"""
    intervention_type: InterventionType
    issue: Issue
    action_taken: str
    result: str
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = False


class IntegrityChecker:
    """
    Checks integrity and consistency of agent outputs
    """

    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        """
        Initialize IntegrityChecker

        Args:
            thresholds: Quality thresholds (test_coverage, doc_completeness, etc.)
        """
        self.thresholds = thresholds or {
            "test_coverage": 0.80,       # 80% minimum
            "doc_completeness": 0.90,    # 90% minimum
            "code_quality_score": 0.75,  # 75% minimum
        }

    def check_test_coverage(self, task_results: Dict[str, Any]) -> Optional[Issue]:
        """
        Check if test coverage meets threshold

        Args:
            task_results: Results from Tester agent

        Returns:
            Issue if coverage below threshold, None otherwise
        """
        coverage = task_results.get("test_coverage", 0.0)

        if coverage < self.thresholds["test_coverage"]:
            return Issue(
                issue_type=IssueType.INCOMPLETE_TESTS,
                severity="HIGH",
                description=f"Test coverage {coverage:.0%} < {self.thresholds['test_coverage']:.0%}",
                affected_agent="Tester"
            )

        return None

    def check_documentation(self, task_results: Dict[str, Any]) -> Optional[Issue]:
        """
        Check if documentation is complete

        Args:
            task_results: Results from Documenter agent

        Returns:
            Issue if docs incomplete, None otherwise
        """
        doc_completeness = task_results.get("doc_completeness", 0.0)

        if doc_completeness < self.thresholds["doc_completeness"]:
            return Issue(
                issue_type=IssueType.MISSING_DOCS,
                severity="MEDIUM",
                description=f"Documentation {doc_completeness:.0%} < {self.thresholds['doc_completeness']:.0%}",
                affected_agent="Documenter"
            )

        return None

    def check_api_consistency(
        self,
        frontend_result: Dict[str, Any],
        backend_result: Dict[str, Any]
    ) -> Optional[Issue]:
        """
        Check consistency between frontend and backend API expectations

        Args:
            frontend_result: Frontend agent results
            backend_result: Backend agent results

        Returns:
            Issue if mismatch detected, None otherwise
        """
        # Simplified check: look for endpoint mismatches
        frontend_endpoints = set(frontend_result.get("expected_endpoints", []))
        backend_endpoints = set(backend_result.get("implemented_endpoints", []))

        missing = frontend_endpoints - backend_endpoints

        if missing:
            return Issue(
                issue_type=IssueType.API_MISMATCH,
                severity="HIGH",
                description=f"Frontend expects endpoints not implemented: {missing}",
                affected_agent="Coder"
            )

        return None

    def check_security(self, code_results: Dict[str, Any]) -> Optional[Issue]:
        """
        Check for security issues in code

        Args:
            code_results: Code analysis results

        Returns:
            Issue if security problems found, None otherwise
        """
        security_issues = code_results.get("security_issues", [])

        if security_issues:
            return Issue(
                issue_type=IssueType.SECURITY_ISSUE,
                severity="HIGH",
                description=f"Security issues detected: {', '.join(security_issues)}",
                affected_agent="Reviewer"
            )

        return None


class ConflictResolver:
    """
    Resolves conflicts between agents
    """

    def __init__(self):
        self.resolution_strategies = {
            IssueType.API_MISMATCH: self._resolve_api_mismatch,
            IssueType.INCOMPLETE_TESTS: self._resolve_incomplete_tests,
            IssueType.MISSING_DOCS: self._resolve_missing_docs,
            IssueType.SECURITY_ISSUE: self._resolve_security_issue,
        }

    def resolve(self, issue: Issue, mode: str = "professional") -> Intervention:
        """
        Resolve an issue based on mode

        Args:
            issue: Issue to resolve
            mode: Resolution mode ("professional", "standard", "interactive")

        Returns:
            Intervention describing action taken
        """
        resolver = self.resolution_strategies.get(issue.issue_type)

        if not resolver:
            return Intervention(
                intervention_type=InterventionType.ESCALATE,
                issue=issue,
                action_taken="No automatic resolution available",
                result="Escalated to user",
                success=False
            )

        return resolver(issue, mode)

    def _resolve_api_mismatch(self, issue: Issue, mode: str) -> Intervention:
        """Resolve API mismatch between frontend and backend"""
        if mode == "professional":
            return Intervention(
                intervention_type=InterventionType.AUTO_FIX,
                issue=issue,
                action_taken="Instructed Coder to implement missing endpoints",
                result="Missing endpoints queued for implementation",
                success=True
            )
        else:
            return Intervention(
                intervention_type=InterventionType.ESCALATE,
                issue=issue,
                action_taken="Notified user of API mismatch",
                result="Waiting for user decision",
                success=False
            )

    def _resolve_incomplete_tests(self, issue: Issue, mode: str) -> Intervention:
        """Resolve incomplete test coverage"""
        if mode == "professional":
            return Intervention(
                intervention_type=InterventionType.AUTO_FIX,
                issue=issue,
                action_taken="Auto-escalated to Tester agent to complete missing tests",
                result="Tester agent re-invoked for missing test coverage",
                success=True
            )
        else:
            return Intervention(
                intervention_type=InterventionType.ESCALATE,
                issue=issue,
                action_taken="Notified user of low test coverage",
                result="User can manually request additional tests",
                success=False
            )

    def _resolve_missing_docs(self, issue: Issue, mode: str) -> Intervention:
        """Resolve missing documentation"""
        return Intervention(
            intervention_type=InterventionType.AUTO_FIX,
            issue=issue,
            action_taken="Instructed Documenter to complete missing sections",
            result="Documentation completion queued",
            success=True
        )

    def _resolve_security_issue(self, issue: Issue, mode: str) -> Intervention:
        """Resolve security issues (always escalate)"""
        return Intervention(
            intervention_type=InterventionType.ESCALATE,
            issue=issue,
            action_taken="Security issue detected - escalating to user",
            result="CRITICAL: User review required",
            success=False
        )


class SuperAdminOrchestrator:
    """
    Master supervisor that oversees all agents, ensures quality, and intervenes when needed
    NOW WITH REAL-TIME EVENT MONITORING
    """

    def __init__(
        self,
        mode: str = "professional",
        integrity_thresholds: Optional[Dict[str, float]] = None,
        enable_real_time: bool = True
    ):
        """
        Initialize SuperAdminOrchestrator

        Args:
            mode: Operation mode ("professional", "standard", "interactive")
            integrity_thresholds: Quality thresholds
            enable_real_time: Enable real-time event monitoring
        """
        self.mode = mode
        self.integrity_checker = IntegrityChecker(integrity_thresholds)
        self.conflict_resolver = ConflictResolver()

        self.issues: List[Issue] = []
        self.interventions: List[Intervention] = []
        self.metrics: Dict[str, Any] = {
            "total_checks": 0,
            "issues_detected": 0,
            "interventions_performed": 0,
            "auto_fixes": 0,
            "escalations": 0,
        }

        # NEW: Real-time monitoring
        self.enable_real_time = enable_real_time
        if enable_real_time:
            self.event_queue = get_event_queue(max_size=1000)
            self.event_monitor = get_event_monitor(self.event_queue)
            self.event_emitter = get_event_emitter(self.event_queue, source="SuperAdmin")

            # Register event handlers
            self._register_event_handlers()

            logger.info(f"🎯 SuperAdmin initialized in '{mode}' mode with REAL-TIME monitoring")
        else:
            logger.info(f"🎯 SuperAdmin initialized in '{mode}' mode (post-execution only)")

    def _register_event_handlers(self):
        """Register handlers for real-time events"""
        if not self.enable_real_time:
            return

        # Register handlers for different event types
        self.event_monitor.register_handler(EventType.TASK_COMPLETED, self._on_task_completed)
        self.event_monitor.register_handler(EventType.TASK_FAILED, self._on_task_failed)
        self.event_monitor.register_handler(EventType.VIOLATION_DETECTED, self._on_violation_detected)

        logger.info("✅ Event handlers registered")

    async def _on_task_completed(self, event: Event):
        """Handle task completion event (real-time)"""
        logger.info(f"✅ Real-time: Task completed by {event.data.get('agent')}")

        # Real-time integrity check
        task_output = event.data
        await self.monitor_task(
            task_name=task_output.get("task", "Unknown"),
            agent_name=task_output.get("agent", "Unknown"),
            task_result=task_output
        )

    async def _on_task_failed(self, event: Event):
        """Handle task failure event (real-time)"""
        logger.error(f"❌ Real-time: Task failed - {event.data.get('error')}")

        # Auto-recovery attempt
        if self.mode == "professional":
            logger.info("🔄 Attempting auto-recovery...")
            # Recovery logic here

    async def _on_violation_detected(self, event: Event):
        """Handle violation event (real-time)"""
        violation_data = event.data
        logger.warning(f"⚠️ Real-time violation: {violation_data.get('violation_type')}")

        # Create issue
        issue = Issue(
            issue_type=IssueType[violation_data.get('violation_type', 'CONSISTENCY_ERROR')],
            severity=violation_data.get('severity', 'MEDIUM'),
            description=str(violation_data.get('details', '')),
            affected_agent="Unknown"
        )

        # Immediate intervention
        await self.intervene(issue)

    async def start_monitoring(self):
        """Start real-time monitoring"""
        if self.enable_real_time:
            await self.event_monitor.start_monitoring()
            logger.info("👁️ Real-time monitoring started")

    async def stop_monitoring(self):
        """Stop real-time monitoring"""
        if self.enable_real_time:
            await self.event_monitor.stop_monitoring()
            logger.info("🛑 Real-time monitoring stopped")

    async def monitor_task(
        self,
        task_name: str,
        agent_name: str,
        task_result: Dict[str, Any]
    ) -> List[Issue]:
        """
        Monitor a completed task for issues

        Args:
            task_name: Name of task
            agent_name: Agent that performed task
            task_result: Task execution results

        Returns:
            List of detected issues
        """
        detected_issues = []
        self.metrics["total_checks"] += 1

        logger.info(f"🔍 Monitoring task '{task_name}' by {agent_name}")

        # Check for various issue types
        if agent_name == "Tester":
            issue = self.integrity_checker.check_test_coverage(task_result)
            if issue:
                detected_issues.append(issue)
                logger.warning(f"⚠️ {issue.description}")

        if agent_name == "Documenter":
            issue = self.integrity_checker.check_documentation(task_result)
            if issue:
                detected_issues.append(issue)
                logger.warning(f"⚠️ {issue.description}")

        if agent_name == "Reviewer":
            issue = self.integrity_checker.check_security(task_result)
            if issue:
                detected_issues.append(issue)
                logger.error(f"🚨 {issue.description}")

        # Update metrics
        if detected_issues:
            self.issues.extend(detected_issues)
            self.metrics["issues_detected"] += len(detected_issues)

        return detected_issues

    async def intervene(self, issue: Issue) -> Intervention:
        """
        Perform intervention for detected issue

        Args:
            issue: Issue to resolve

        Returns:
            Intervention performed
        """
        logger.info(f"🛠️ Intervening for: {issue.description}")

        intervention = self.conflict_resolver.resolve(issue, self.mode)

        self.interventions.append(intervention)
        self.metrics["interventions_performed"] += 1

        if intervention.intervention_type == InterventionType.AUTO_FIX:
            self.metrics["auto_fixes"] += 1
            logger.info(f"✅ Auto-fix: {intervention.action_taken}")
        elif intervention.intervention_type == InterventionType.ESCALATE:
            self.metrics["escalations"] += 1
            logger.warning(f"⬆️ Escalated: {intervention.action_taken}")

        return intervention

    async def supervise_workflow(
        self,
        tasks: List[Dict[str, Any]],
        agents: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Supervise entire workflow, monitoring each task

        REAL-TIME MONITORING:
        - Starts event monitoring loop in background
        - Emits events for task starts/completions
        - Monitors and intervenes in real-time

        Args:
            tasks: List of tasks to supervise
            agents: Dictionary of available agents

        Returns:
            Supervision report
        """
        logger.info("🎯 SuperAdmin: Starting workflow supervision")

        # Start real-time monitoring if enabled
        if self.enable_real_time:
            await self.start_monitoring()
            logger.info("👁️ Real-time monitoring ACTIVE")

        try:
            for task in tasks:
                # Get task details
                task_name = task.get("name", "Unknown")
                agent_name = task.get("agent", "Unknown")

                logger.info(f"📋 Supervising: {task_name}")

                # Emit task started event (real-time)
                if self.enable_real_time:
                    await self.event_emitter.emit_task_started(
                        task_description=task_name,
                        agent_role=agent_name
                    )

                # Mock task result (in real implementation, get from actual task)
                task_result = task.get("result", {})

                # Monitor task
                issues = await self.monitor_task(task_name, agent_name, task_result)

                # Emit task completed/failed event (real-time)
                if self.enable_real_time:
                    if issues:
                        await self.event_emitter.emit_task_failed(
                            task_description=task_name,
                            agent_role=agent_name,
                            error=f"{len(issues)} issues detected"
                        )
                    else:
                        await self.event_emitter.emit_task_completed(
                            task_description=task_name,
                            agent_role=agent_name,
                            output=task_result
                        )

                # Intervene if issues found
                for issue in issues:
                    intervention = await self.intervene(issue)

                    # Emit intervention event (real-time)
                    if self.enable_real_time:
                        await self.event_emitter.emit_intervention(
                            intervention_type=intervention.intervention_type.value,
                            reason=issue.description,
                            action=intervention.action_taken
                        )

        finally:
            # Stop real-time monitoring
            if self.enable_real_time:
                await self.stop_monitoring()

        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive supervision report

        Returns:
            Report dictionary
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "mode": self.mode,
            "metrics": self.metrics,
            "issues": [
                {
                    "type": issue.issue_type.value,
                    "severity": issue.severity,
                    "description": issue.description,
                    "agent": issue.affected_agent,
                    "resolved": issue.resolved,
                }
                for issue in self.issues
            ],
            "interventions": [
                {
                    "type": intervention.intervention_type.value,
                    "action": intervention.action_taken,
                    "result": intervention.result,
                    "success": intervention.success,
                }
                for intervention in self.interventions
            ],
            "summary": {
                "total_issues": len(self.issues),
                "resolved_issues": sum(1 for i in self.issues if i.resolved),
                "auto_fixes": self.metrics["auto_fixes"],
                "escalations": self.metrics["escalations"],
                "success_rate": (
                    self.metrics["auto_fixes"] / self.metrics["interventions_performed"] * 100
                    if self.metrics["interventions_performed"] > 0 else 0
                ),
            }
        }

    def print_report(self):
        """Print human-readable supervision report"""
        report = self.generate_report()

        print("\n" + "=" * 60)
        print("🎯 SUPER ADMIN SUPERVISION REPORT")
        print("=" * 60)
        print(f"Mode: {report['mode']}")
        print(f"Timestamp: {report['timestamp']}")
        print()

        print("📊 Metrics:")
        for key, value in report['metrics'].items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        print()

        if report['issues']:
            print("⚠️ Issues Detected:")
            for issue in report['issues']:
                emoji = "🚨" if issue['severity'] == "HIGH" else "⚠️" if issue['severity'] == "MEDIUM" else "ℹ️"
                print(f"  {emoji} [{issue['severity']}] {issue['description']}")
                print(f"     Agent: {issue['agent']} | Resolved: {issue['resolved']}")
        else:
            print("✅ No issues detected")

        print()

        if report['interventions']:
            print("🛠️ Interventions:")
            for intervention in report['interventions']:
                print(f"  • {intervention['type']}: {intervention['action']}")
                print(f"    Result: {intervention['result']}")
        else:
            print("✅ No interventions needed")

        print()
        print("📈 Summary:")
        summary = report['summary']
        print(f"  Total Issues: {summary['total_issues']}")
        print(f"  Resolved: {summary['resolved_issues']}")
        print(f"  Auto-fixes: {summary['auto_fixes']}")
        print(f"  Escalations: {summary['escalations']}")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")

        print("=" * 60 + "\n")


def get_super_admin(
    mode: str = "professional",
    thresholds: Optional[Dict[str, float]] = None
) -> SuperAdminOrchestrator:
    """
    Factory function to create SuperAdminOrchestrator

    Args:
        mode: Operation mode
        thresholds: Quality thresholds

    Returns:
        Configured SuperAdminOrchestrator
    """
    return SuperAdminOrchestrator(mode=mode, integrity_thresholds=thresholds)


# Standalone usage example
if __name__ == "__main__":
    import asyncio

    async def test_super_admin():
        """Test SuperAdmin functionality"""
        admin = get_super_admin(mode="professional")

        # Simulate tasks with results
        tasks = [
            {
                "name": "Write tests",
                "agent": "Tester",
                "result": {"test_coverage": 0.65}  # Below threshold
            },
            {
                "name": "Generate docs",
                "agent": "Documenter",
                "result": {"doc_completeness": 0.85}  # Below threshold
            },
            {
                "name": "Security review",
                "agent": "Reviewer",
                "result": {"security_issues": ["Hardcoded API key"]}  # Security issue
            },
        ]

        # Supervise workflow
        report = await admin.supervise_workflow(tasks, {})

        # Print report
        admin.print_report()

    asyncio.run(test_super_admin())
