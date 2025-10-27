"""
YAGO v7.0 - Real-Time Event Monitoring System
Event-driven monitoring for SuperAdmin live supervision
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

logger = logging.getLogger("YAGO.EventMonitor")


class EventType(Enum):
    """Types of events in the system"""
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    AGENT_CREATED = "agent_created"
    QUALITY_CHECK = "quality_check"
    VIOLATION_DETECTED = "violation_detected"
    INTERVENTION_TRIGGERED = "intervention_triggered"
    SYSTEM_ERROR = "system_error"
    MILESTONE_REACHED = "milestone_reached"


@dataclass
class Event:
    """Represents a system event"""
    event_type: EventType
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    source: str = ""  # Agent or system component
    data: Dict[str, Any] = field(default_factory=dict)
    priority: str = "NORMAL"  # LOW, NORMAL, HIGH, CRITICAL
    processed: bool = False


class EventQueue:
    """
    Thread-safe event queue for real-time monitoring
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize EventQueue

        Args:
            max_size: Maximum queue size (older events dropped)
        """
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self.history: deque = deque(maxlen=max_size)
        self.listeners: Dict[EventType, list] = {}

    async def push(self, event: Event):
        """
        Push event to queue

        Args:
            event: Event to push
        """
        try:
            await self.queue.put(event)
            self.history.append(event)
            logger.debug(f"📨 Event pushed: {event.event_type.value} from {event.source}")

            # Notify listeners
            await self._notify_listeners(event)

        except asyncio.QueueFull:
            logger.warning(f"⚠️ Event queue full, dropping event: {event.event_type.value}")

    async def pop(self, timeout: Optional[float] = None) -> Optional[Event]:
        """
        Pop event from queue

        Args:
            timeout: Wait timeout in seconds (None = wait forever)

        Returns:
            Event or None if timeout
        """
        try:
            if timeout is not None:
                event = await asyncio.wait_for(self.queue.get(), timeout=timeout)
            else:
                event = await self.queue.get()

            return event

        except asyncio.TimeoutError:
            return None

    def register_listener(self, event_type: EventType, callback: Callable):
        """
        Register listener for specific event type

        Args:
            event_type: Type of event to listen for
            callback: Async callback function
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []

        self.listeners[event_type].append(callback)
        logger.info(f"📡 Registered listener for {event_type.value}")

    async def _notify_listeners(self, event: Event):
        """
        Notify all registered listeners for event type

        Args:
            event: Event to notify about
        """
        listeners = self.listeners.get(event.event_type, [])

        for callback in listeners:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"❌ Listener error: {str(e)}")

    def get_recent_events(self, count: int = 10, event_type: Optional[EventType] = None) -> list:
        """
        Get recent events from history

        Args:
            count: Number of events
            event_type: Filter by type (None = all)

        Returns:
            List of recent events
        """
        if event_type:
            filtered = [e for e in self.history if e.event_type == event_type]
            return list(filtered)[-count:]
        else:
            return list(self.history)[-count:]


class EventMonitor:
    """
    Real-time event monitoring system for SuperAdmin
    """

    def __init__(self, event_queue: EventQueue):
        """
        Initialize EventMonitor

        Args:
            event_queue: Event queue to monitor
        """
        self.event_queue = event_queue
        self.running = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.event_handlers: Dict[EventType, Callable] = {}

        # Metrics
        self.metrics = {
            "events_processed": 0,
            "violations_detected": 0,
            "interventions_triggered": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
        }

    def register_handler(self, event_type: EventType, handler: Callable):
        """
        Register handler for event type

        Args:
            event_type: Event type to handle
            handler: Async handler function
        """
        self.event_handlers[event_type] = handler
        logger.info(f"🔧 Registered handler for {event_type.value}")

    async def start_monitoring(self):
        """
        Start real-time monitoring loop
        """
        if self.running:
            logger.warning("⚠️ Monitoring already running")
            return

        self.running = True
        logger.info("👁️ Event monitoring started")

        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self):
        """
        Stop monitoring loop
        """
        if not self.running:
            return

        self.running = False
        logger.info("🛑 Stopping event monitoring...")

        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("✅ Event monitoring stopped")

    async def _monitoring_loop(self):
        """
        Main monitoring loop - processes events in real-time
        """
        logger.info("🔄 Monitoring loop active")

        try:
            while self.running:
                # Pop event with timeout (non-blocking check every 1 second)
                event = await self.event_queue.pop(timeout=1.0)

                if event:
                    await self._process_event(event)

        except asyncio.CancelledError:
            logger.info("🛑 Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"❌ Monitoring loop error: {str(e)}", exc_info=True)

    async def _process_event(self, event: Event):
        """
        Process a single event

        Args:
            event: Event to process
        """
        logger.debug(f"🔍 Processing event: {event.event_type.value}")

        self.metrics["events_processed"] += 1

        # Update metrics
        if event.event_type == EventType.TASK_COMPLETED:
            self.metrics["tasks_completed"] += 1
        elif event.event_type == EventType.TASK_FAILED:
            self.metrics["tasks_failed"] += 1
        elif event.event_type == EventType.VIOLATION_DETECTED:
            self.metrics["violations_detected"] += 1
        elif event.event_type == EventType.INTERVENTION_TRIGGERED:
            self.metrics["interventions_triggered"] += 1

        # Call registered handler
        handler = self.event_handlers.get(event.event_type)

        if handler:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)

                event.processed = True

            except Exception as e:
                logger.error(f"❌ Handler error for {event.event_type.value}: {str(e)}")
        else:
            logger.debug(f"ℹ️ No handler for {event.event_type.value}")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get monitoring metrics

        Returns:
            Metrics dictionary
        """
        return {
            **self.metrics,
            "recent_events": len(self.event_queue.history),
            "monitoring_active": self.running,
        }

    def print_metrics(self):
        """Print current metrics"""
        metrics = self.get_metrics()

        print("\n" + "=" * 60)
        print("👁️ EVENT MONITOR METRICS")
        print("=" * 60)
        print(f"Status: {'🟢 ACTIVE' if metrics['monitoring_active'] else '🔴 STOPPED'}")
        print(f"\nEvents Processed: {metrics['events_processed']}")
        print(f"Tasks Completed: {metrics['tasks_completed']}")
        print(f"Tasks Failed: {metrics['tasks_failed']}")
        print(f"Violations Detected: {metrics['violations_detected']}")
        print(f"Interventions Triggered: {metrics['interventions_triggered']}")
        print(f"Recent Events: {metrics['recent_events']}")
        print("=" * 60 + "\n")


class EventEmitter:
    """
    Helper class to emit events from various system components
    """

    def __init__(self, event_queue: EventQueue, source: str):
        """
        Initialize EventEmitter

        Args:
            event_queue: Event queue to emit to
            source: Source component name
        """
        self.event_queue = event_queue
        self.source = source

    async def emit_task_started(self, task_description: str, agent_role: str):
        """Emit task started event"""
        event = Event(
            event_type=EventType.TASK_STARTED,
            source=self.source,
            data={
                "task": task_description[:100],
                "agent": agent_role,
            }
        )
        await self.event_queue.push(event)

    async def emit_task_completed(self, task_description: str, agent_role: str, output: Any):
        """Emit task completed event"""
        event = Event(
            event_type=EventType.TASK_COMPLETED,
            source=self.source,
            data={
                "task": task_description[:100],
                "agent": agent_role,
                "output": str(output)[:200],
            }
        )
        await self.event_queue.push(event)

    async def emit_task_failed(self, task_description: str, agent_role: str, error: str):
        """Emit task failed event"""
        event = Event(
            event_type=EventType.TASK_FAILED,
            source=self.source,
            data={
                "task": task_description[:100],
                "agent": agent_role,
                "error": error,
            },
            priority="HIGH"
        )
        await self.event_queue.push(event)

    async def emit_violation(self, violation_type: str, severity: str, details: Dict):
        """Emit quality violation event"""
        event = Event(
            event_type=EventType.VIOLATION_DETECTED,
            source=self.source,
            data={
                "violation_type": violation_type,
                "severity": severity,
                "details": details,
            },
            priority="HIGH" if severity == "HIGH" else "NORMAL"
        )
        await self.event_queue.push(event)

    async def emit_intervention(self, intervention_type: str, reason: str, action: str):
        """Emit intervention triggered event"""
        event = Event(
            event_type=EventType.INTERVENTION_TRIGGERED,
            source=self.source,
            data={
                "intervention_type": intervention_type,
                "reason": reason,
                "action": action,
            },
            priority="HIGH"
        )
        await self.event_queue.push(event)


# Factory functions
def get_event_queue(max_size: int = 1000) -> EventQueue:
    """Create EventQueue"""
    return EventQueue(max_size=max_size)


def get_event_monitor(event_queue: EventQueue) -> EventMonitor:
    """Create EventMonitor"""
    return EventMonitor(event_queue=event_queue)


def get_event_emitter(event_queue: EventQueue, source: str) -> EventEmitter:
    """Create EventEmitter"""
    return EventEmitter(event_queue=event_queue, source=source)


# Standalone usage example
if __name__ == "__main__":
    async def main():
        # Create event system
        queue = get_event_queue()
        monitor = get_event_monitor(queue)
        emitter = get_event_emitter(queue, source="TestSystem")

        # Register handlers
        async def on_task_completed(event: Event):
            print(f"✅ Task completed: {event.data['task']}")

        async def on_violation(event: Event):
            print(f"⚠️ Violation: {event.data['violation_type']}")

        monitor.register_handler(EventType.TASK_COMPLETED, on_task_completed)
        monitor.register_handler(EventType.VIOLATION_DETECTED, on_violation)

        # Start monitoring
        await monitor.start_monitoring()

        # Emit some test events
        await emitter.emit_task_started("Test task", "Coder")
        await asyncio.sleep(0.1)

        await emitter.emit_task_completed("Test task", "Coder", "Success")
        await asyncio.sleep(0.1)

        await emitter.emit_violation("LOW_TEST_COVERAGE", "HIGH", {"coverage": 65})
        await asyncio.sleep(0.1)

        # Wait for processing
        await asyncio.sleep(1)

        # Print metrics
        monitor.print_metrics()

        # Stop monitoring
        await monitor.stop_monitoring()

        print("\n✅ Event monitoring test complete")

    asyncio.run(main())
