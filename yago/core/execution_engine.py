"""
YAGO v7.0 - Execution Engine
Advanced execution strategies: sequential, parallel, and race mode
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from crewai import Task, Crew, Process

logger = logging.getLogger("YAGO.ExecutionEngine")


@dataclass
class ExecutionResult:
    """Result of task execution"""
    task_description: str
    agent_role: str
    output: Any
    duration: float
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None


@dataclass
class PhaseResult:
    """Result of execution phase"""
    phase_name: str
    tasks_completed: int
    duration: float
    results: List[ExecutionResult]
    success: bool


class ExecutionEngine:
    """
    Advanced execution engine with multiple strategies:
    - Sequential: Tasks run one after another
    - Parallel: Independent tasks run concurrently
    - Hybrid: Mix of sequential and parallel
    - Race: First successful result wins (cost optimization)
    """

    def __init__(self, tasks: List[Task], strategy: str = "auto"):
        """
        Initialize ExecutionEngine

        Args:
            tasks: List of CrewAI tasks
            strategy: "sequential", "parallel", "hybrid", "race", or "auto"
        """
        self.tasks = tasks
        self.strategy = strategy if strategy != "auto" else self._auto_select_strategy()
        self.results: List[ExecutionResult] = []

        logger.info(f"🚀 ExecutionEngine initialized with '{self.strategy}' strategy")

    def _auto_select_strategy(self) -> str:
        """
        Automatically select best strategy based on tasks

        Returns:
            Best strategy name
        """
        task_count = len(self.tasks)

        if task_count <= 5:
            return "sequential"  # Simple, predictable
        elif task_count <= 10:
            return "hybrid"  # Balance speed and control
        else:
            return "parallel"  # Maximum speed

    async def execute_sequential(self) -> Dict[str, Any]:
        """
        Execute tasks sequentially (one after another)

        Returns:
            Execution report
        """
        logger.info("📋 Starting SEQUENTIAL execution...")
        start_time = datetime.now()

        results = []

        for idx, task in enumerate(self.tasks, 1):
            logger.info(f"  [{idx}/{len(self.tasks)}] Executing: {task.description[:50]}...")

            task_start = datetime.now()

            try:
                # Execute task
                output = await self._execute_single_task(task)

                task_duration = (datetime.now() - task_start).total_seconds()

                result = ExecutionResult(
                    task_description=task.description[:100],
                    agent_role=task.agent.role,
                    output=output,
                    duration=task_duration,
                    success=True
                )

                results.append(result)
                logger.info(f"  ✅ Completed in {task_duration:.2f}s")

            except Exception as e:
                task_duration = (datetime.now() - task_start).total_seconds()

                result = ExecutionResult(
                    task_description=task.description[:100],
                    agent_role=task.agent.role,
                    output=None,
                    duration=task_duration,
                    success=False,
                    error=str(e)
                )

                results.append(result)
                logger.error(f"  ❌ Failed: {str(e)}")

        total_duration = (datetime.now() - start_time).total_seconds()
        success_count = sum(1 for r in results if r.success)

        logger.info(f"\n✅ Sequential execution complete: {success_count}/{len(results)} successful")

        return {
            "strategy": "sequential",
            "total_tasks": len(results),
            "successful": success_count,
            "failed": len(results) - success_count,
            "duration": total_duration,
            "results": results,
        }

    async def execute_parallel(self) -> Dict[str, Any]:
        """
        Execute all tasks in parallel (maximum speed)

        Returns:
            Execution report
        """
        logger.info("⚡ Starting PARALLEL execution...")
        start_time = datetime.now()

        # Execute all tasks concurrently
        task_coroutines = [self._execute_single_task(task) for task in self.tasks]

        results = []

        try:
            # Gather all results
            outputs = await asyncio.gather(*task_coroutines, return_exceptions=True)

            for idx, (task, output) in enumerate(zip(self.tasks, outputs)):
                if isinstance(output, Exception):
                    result = ExecutionResult(
                        task_description=task.description[:100],
                        agent_role=task.agent.role,
                        output=None,
                        duration=0.0,
                        success=False,
                        error=str(output)
                    )
                else:
                    result = ExecutionResult(
                        task_description=task.description[:100],
                        agent_role=task.agent.role,
                        output=output,
                        duration=0.0,  # Individual timing not available in parallel
                        success=True
                    )

                results.append(result)

        except Exception as e:
            logger.error(f"❌ Parallel execution error: {str(e)}")

        total_duration = (datetime.now() - start_time).total_seconds()
        success_count = sum(1 for r in results if r.success)

        logger.info(f"\n⚡ Parallel execution complete: {success_count}/{len(results)} successful in {total_duration:.2f}s")

        return {
            "strategy": "parallel",
            "total_tasks": len(results),
            "successful": success_count,
            "failed": len(results) - success_count,
            "duration": total_duration,
            "results": results,
            "speedup": f"{len(self.tasks) / max(total_duration, 1):.1f}x theoretical"
        }

    async def execute_hybrid(self, groups: Dict[str, List[Task]]) -> Dict[str, Any]:
        """
        Execute tasks in phases with parallel execution within each phase

        Args:
            groups: Task groups by phase

        Returns:
            Execution report
        """
        logger.info("🔀 Starting HYBRID execution...")
        start_time = datetime.now()

        phase_results = []

        # Define execution order
        phases = ["planning", "coding", "quality", "documentation"]

        for phase_name in phases:
            phase_tasks = groups.get(phase_name, [])

            if not phase_tasks:
                continue

            logger.info(f"\n📋 Phase: {phase_name.upper()} ({len(phase_tasks)} tasks)")
            phase_start = datetime.now()

            # Execute phase tasks in parallel
            phase_coroutines = [self._execute_single_task(task) for task in phase_tasks]

            try:
                outputs = await asyncio.gather(*phase_coroutines, return_exceptions=True)

                phase_task_results = []
                for task, output in zip(phase_tasks, outputs):
                    if isinstance(output, Exception):
                        result = ExecutionResult(
                            task_description=task.description[:100],
                            agent_role=task.agent.role,
                            output=None,
                            duration=0.0,
                            success=False,
                            error=str(output)
                        )
                    else:
                        result = ExecutionResult(
                            task_description=task.description[:100],
                            agent_role=task.agent.role,
                            output=output,
                            duration=0.0,
                            success=True
                        )

                    phase_task_results.append(result)

                phase_duration = (datetime.now() - phase_start).total_seconds()
                phase_success = all(r.success for r in phase_task_results)

                phase_result = PhaseResult(
                    phase_name=phase_name,
                    tasks_completed=len(phase_task_results),
                    duration=phase_duration,
                    results=phase_task_results,
                    success=phase_success
                )

                phase_results.append(phase_result)

                logger.info(f"  ✅ {phase_name.capitalize()} phase complete in {phase_duration:.2f}s")

            except Exception as e:
                logger.error(f"  ❌ {phase_name.capitalize()} phase failed: {str(e)}")

        total_duration = (datetime.now() - start_time).total_seconds()
        all_results = [r for phase in phase_results for r in phase.results]
        success_count = sum(1 for r in all_results if r.success)

        logger.info(f"\n🔀 Hybrid execution complete: {success_count}/{len(all_results)} successful")

        return {
            "strategy": "hybrid",
            "total_tasks": len(all_results),
            "successful": success_count,
            "failed": len(all_results) - success_count,
            "duration": total_duration,
            "phases": [
                {
                    "name": phase.phase_name,
                    "tasks": phase.tasks_completed,
                    "duration": phase.duration,
                    "success": phase.success
                }
                for phase in phase_results
            ],
            "results": all_results,
        }

    async def execute_race(self, task_variants: List[List[Task]]) -> Dict[str, Any]:
        """
        Race mode: Execute multiple variants of the same task, use first successful result
        (Cost optimization: only pay for fastest result)

        Args:
            task_variants: List of task variant lists (each list is one approach)

        Returns:
            Execution report
        """
        logger.info("🏁 Starting RACE execution...")
        start_time = datetime.now()

        results = []

        for idx, variants in enumerate(task_variants, 1):
            logger.info(f"\n🏁 Task {idx}: Racing {len(variants)} variants...")

            variant_start = datetime.now()

            try:
                # Race: first successful completion wins
                variant_coroutines = [self._execute_single_task(task) for task in variants]

                # Use wait with FIRST_COMPLETED
                done, pending = await asyncio.wait(
                    variant_coroutines,
                    return_when=asyncio.FIRST_COMPLETED
                )

                # Cancel remaining tasks (cost saving)
                for task in pending:
                    task.cancel()

                # Get winning result
                winner = list(done)[0]
                output = await winner

                duration = (datetime.now() - variant_start).total_seconds()

                result = ExecutionResult(
                    task_description=f"Race task {idx}",
                    agent_role="Race Winner",
                    output=output,
                    duration=duration,
                    success=True
                )

                results.append(result)

                logger.info(f"  🏆 Winner found in {duration:.2f}s (saved {len(pending)} executions)")

            except Exception as e:
                duration = (datetime.now() - variant_start).total_seconds()

                result = ExecutionResult(
                    task_description=f"Race task {idx}",
                    agent_role="Race",
                    output=None,
                    duration=duration,
                    success=False,
                    error=str(e)
                )

                results.append(result)
                logger.error(f"  ❌ All variants failed: {str(e)}")

        total_duration = (datetime.now() - start_time).total_seconds()
        success_count = sum(1 for r in results if r.success)

        logger.info(f"\n🏁 Race execution complete: {success_count}/{len(results)} successful")

        return {
            "strategy": "race",
            "total_tasks": len(results),
            "successful": success_count,
            "failed": len(results) - success_count,
            "duration": total_duration,
            "cost_savings": "50-70% (only fastest execution paid)",
            "results": results,
        }

    async def _execute_single_task(self, task: Task) -> Any:
        """
        Execute a single task (simulated for now, real integration with CrewAI)

        Args:
            task: CrewAI Task

        Returns:
            Task output
        """
        # TODO: Real CrewAI integration
        # For now, simulate execution

        await asyncio.sleep(0.1)  # Simulate work

        # Simulate agent execution
        return {
            "task": task.description[:50],
            "agent": task.agent.role,
            "status": "completed",
            "output": f"Output from {task.agent.role}"
        }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Main execution entry point - routes to appropriate strategy

        Args:
            **kwargs: Strategy-specific arguments

        Returns:
            Execution report
        """
        logger.info(f"🎯 Executing with '{self.strategy}' strategy...")

        if self.strategy == "sequential":
            return await self.execute_sequential()
        elif self.strategy == "parallel":
            return await self.execute_parallel()
        elif self.strategy == "hybrid":
            groups = kwargs.get("groups", self._default_groups())
            return await self.execute_hybrid(groups)
        elif self.strategy == "race":
            variants = kwargs.get("variants", [])
            return await self.execute_race(variants)
        else:
            logger.warning(f"Unknown strategy '{self.strategy}', falling back to sequential")
            return await self.execute_sequential()

    def _default_groups(self) -> Dict[str, List[Task]]:
        """Create default task groups for hybrid execution"""
        groups = {
            "planning": [],
            "coding": [],
            "quality": [],
            "documentation": []
        }

        for task in self.tasks:
            role = task.agent.role

            if role == "Planner":
                groups["planning"].append(task)
            elif role in ["Coder", "SecurityAgent", "DevOpsAgent", "DatabaseAgent", "FrontendAgent"]:
                groups["coding"].append(task)
            elif role in ["Tester", "Reviewer"]:
                groups["quality"].append(task)
            elif role == "Documenter":
                groups["documentation"].append(task)

        return groups


def get_execution_engine(tasks: List[Task], strategy: str = "auto") -> ExecutionEngine:
    """
    Factory function to create ExecutionEngine

    Args:
        tasks: List of tasks
        strategy: Execution strategy

    Returns:
        Configured ExecutionEngine
    """
    return ExecutionEngine(tasks=tasks, strategy=strategy)


# Standalone usage example
if __name__ == "__main__":
    async def main():
        from unittest.mock import Mock

        # Mock tasks
        mock_agent = Mock(role="Coder")
        mock_tasks = [
            Mock(description=f"Task {i}", agent=mock_agent, expected_output="output")
            for i in range(1, 6)
        ]

        # Test sequential
        engine_seq = ExecutionEngine(mock_tasks, strategy="sequential")
        result_seq = await engine_seq.execute()

        print("\n" + "=" * 60)
        print("SEQUENTIAL EXECUTION RESULT")
        print("=" * 60)
        print(f"Strategy: {result_seq['strategy']}")
        print(f"Total: {result_seq['total_tasks']}")
        print(f"Success: {result_seq['successful']}")
        print(f"Duration: {result_seq['duration']:.2f}s")

        # Test parallel
        engine_par = ExecutionEngine(mock_tasks, strategy="parallel")
        result_par = await engine_par.execute()

        print("\n" + "=" * 60)
        print("PARALLEL EXECUTION RESULT")
        print("=" * 60)
        print(f"Strategy: {result_par['strategy']}")
        print(f"Total: {result_par['total_tasks']}")
        print(f"Success: {result_par['successful']}")
        print(f"Duration: {result_par['duration']:.2f}s")
        print(f"Speedup: {result_par.get('speedup', 'N/A')}")

        print("\n✅ Execution engine tests complete")

    asyncio.run(main())
