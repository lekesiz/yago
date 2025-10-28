## Auto-Healing System

**YAGO v8.0** - Automatic error recovery and self-diagnosis

---

## Overview

YAGO's Auto-Healing System provides intelligent, automatic recovery from errors and failures. The system detects errors, classifies them, and applies appropriate recovery strategies to maintain system reliability.

### Key Features

- **Intelligent Error Detection**: Automatic error classification by severity and category
- **Multiple Recovery Strategies**: Retry, circuit breaker, fallback, rollback
- **Health Monitoring**: Continuous component health tracking
- **Self-Diagnosis**: Automatic problem detection and resolution
- **Circuit Breakers**: Prevent cascading failures
- **Recovery Statistics**: Track recovery success rates and patterns

---

## Quick Start

### 1. Initialize Auto-Healing

```python
from yago.healing import HealthMonitor, ErrorDetector, RecoveryEngine

# Create components
health_monitor = HealthMonitor(
    check_interval_seconds=30.0,
    alert_threshold=HealthStatus.UNHEALTHY
)
error_detector = ErrorDetector()
recovery_engine = RecoveryEngine(health_monitor, error_detector)

# Start monitoring
await health_monitor.start_monitoring()
```

### 2. Register Components

```python
# Register component for monitoring
health_monitor.register_component("openai_adapter")

# Enable circuit breaker
recovery_engine.register_circuit_breaker(
    "openai_adapter",
    CircuitBreakerConfig(
        failure_threshold=5,
        success_threshold=2,
        timeout_seconds=60.0
    )
)
```

### 3. Execute with Auto-Recovery

```python
# Execute operation with automatic recovery
result = await recovery_engine.execute_with_recovery(
    operation=my_api_call,
    component="openai_adapter",
    operation_name="generate",
    prompt="Hello, world!"
)
```

---

## Recovery Strategies

### 1. Retry with Exponential Backoff

Automatically retry failed operations with increasing delays.

```python
from yago.healing import RetryStrategy, RetryConfig

strategy = RetryStrategy(
    config=RetryConfig(
        max_attempts=3,
        initial_delay_ms=1000.0,
        max_delay_ms=60000.0,
        exponential_base=2.0,
        jitter=True
    )
)

result = await strategy.execute(
    operation=my_function,
    error_context=error_context,
    arg1="value1"
)
```

**Use Cases**:
- Network timeouts
- API rate limits
- Temporary service unavailability

**Configuration**:
- `max_attempts`: Maximum retry attempts (1-10)
- `initial_delay_ms`: Initial delay in milliseconds
- `max_delay_ms`: Maximum delay cap
- `exponential_base`: Backoff multiplier (typically 2.0)
- `jitter`: Add randomness to prevent thundering herd

### 2. Circuit Breaker

Prevent cascading failures by temporarily blocking requests to failing services.

```python
from yago.healing import CircuitBreakerStrategy, CircuitBreakerConfig

strategy = CircuitBreakerStrategy(
    config=CircuitBreakerConfig(
        failure_threshold=5,      # Open after 5 failures
        success_threshold=2,      # Close after 2 successes
        timeout_seconds=60.0,     # Wait 60s before retry
        half_open_max_calls=1     # Allow 1 test call
    )
)

result = await strategy.execute(
    operation=my_function,
    error_context=error_context
)
```

**States**:
- **CLOSED**: Normal operation, requests pass through
- **OPEN**: Circuit open, requests blocked immediately
- **HALF_OPEN**: Testing if service recovered

**Use Cases**:
- Protect against cascading failures
- Give failing services time to recover
- Prevent resource exhaustion

### 3. Fallback

Switch to alternative operations when primary fails.

```python
from yago.healing import FallbackStrategy

# Define fallback operations
async def primary_api():
    return await openai_api.generate()

async def fallback_api_1():
    return await anthropic_api.generate()

async def fallback_api_2():
    return await local_model.generate()

strategy = FallbackStrategy(
    fallback_operations=[fallback_api_1, fallback_api_2]
)

result = await strategy.execute(
    operation=primary_api,
    error_context=error_context
)
```

**Use Cases**:
- Multiple API providers
- Primary/secondary service architecture
- Graceful degradation

### 4. Rollback

Restore previous state after failed operations.

```python
from yago.healing import RollbackStrategy

strategy = RollbackStrategy()

result = await strategy.execute(
    operation=my_stateful_operation,
    error_context=error_context,
    state=current_state
)
```

**Use Cases**:
- Database transactions
- Multi-step operations
- State management

---

## Health Monitoring

### Component Health Tracking

```python
# Record successful operation
health_monitor.record_success("openai_adapter", response_time_ms=250.5)

# Record failed operation
health_monitor.record_failure("openai_adapter", error_context)

# Check component health
result = await health_monitor.check_component_health("openai_adapter")
print(f"Status: {result.status}")
print(f"Error rate: {result.error_rate*100:.1f}%")
print(f"Avg response time: {result.response_time_ms:.0f}ms")
```

### Health Status Levels

- **HEALTHY**: All systems operational (error rate < 5%)
- **DEGRADED**: Some issues detected (error rate 5-20%)
- **UNHEALTHY**: Significant issues (error rate 20-50%)
- **CRITICAL**: System failure (error rate > 50% or critical errors)

### System-Wide Health Check

```python
# Check overall system health
system_health = await health_monitor.get_system_health()

print(f"System status: {system_health.status}")
print(f"Issues: {system_health.issues}")
print(f"Healthy components: {system_health.details['healthy']}")
print(f"Unhealthy components: {system_health.details['unhealthy']}")
```

### Continuous Monitoring

```python
# Define alert callback
async def alert_callback(health_result):
    if health_result.status == HealthStatus.CRITICAL:
        await send_alert(f"CRITICAL: {health_result.message}")

# Register callback
health_monitor.register_alert_callback(alert_callback)

# Start monitoring (checks every 30 seconds)
await health_monitor.start_monitoring()

# Stop when done
await health_monitor.stop_monitoring()
```

---

## Error Detection & Classification

### Automatic Classification

```python
from yago.healing import ErrorDetector

detector = ErrorDetector()

try:
    result = await risky_operation()
except Exception as e:
    # Detect and classify error
    error_context = detector.detect(
        exception=e,
        component="my_component",
        operation="my_operation",
        request_id="req_123",
        user_id="user_456"
    )

    print(f"Error ID: {error_context.error_id}")
    print(f"Severity: {error_context.severity}")
    print(f"Category: {error_context.category}")
```

### Error Categories

- **NETWORK**: Connection, DNS, socket errors
- **API**: HTTP errors, API failures
- **RATE_LIMIT**: Quota exceeded, throttling
- **AUTHENTICATION**: Auth failures, permissions
- **RESOURCE**: Memory, CPU, disk exhaustion
- **DATABASE**: SQL errors, connection pools
- **VALIDATION**: Data validation errors
- **TIMEOUT**: Operation timeouts
- **CONFIGURATION**: Config errors, missing settings
- **UNKNOWN**: Unclassified errors

### Error Severity

- **LOW**: Minor issues, can be ignored
- **MEDIUM**: Needs attention but not critical
- **HIGH**: Requires immediate action
- **CRITICAL**: System-threatening, urgent recovery

### Recovery Decision Logic

```python
# Should retry?
should_retry = detector.should_retry(error_context)

# Should use fallback?
should_fallback = detector.should_fallback(error_context)

# Should open circuit breaker?
should_break = detector.should_circuit_break(error_context)

# Get recommended retry delay
delay_ms = detector.get_retry_delay(error_context)
```

---

## REST API

### Health Check

```bash
# Check system health
GET /api/v1/healing/health

# Check component health
GET /api/v1/healing/health?component=openai_adapter

# Check all components
GET /api/v1/healing/health/components
```

**Response**:
```json
{
  "system_status": "healthy",
  "error_rate": 0.02,
  "success_rate": 0.98,
  "message": "All systems operational",
  "issues": [],
  "details": {
    "components": 5,
    "healthy": 4,
    "degraded": 1,
    "unhealthy": 0,
    "critical": 0
  }
}
```

### Component Management

```bash
# Register component
POST /api/v1/healing/components/register
Content-Type: application/json

{
  "component": "openai_adapter",
  "enable_circuit_breaker": true,
  "circuit_breaker_config": {
    "failure_threshold": 5,
    "success_threshold": 2,
    "timeout_seconds": 60.0
  }
}

# List components
GET /api/v1/healing/components

# Get component stats
GET /api/v1/healing/component/openai_adapter/stats

# Reset component metrics
POST /api/v1/healing/component/openai_adapter/reset
```

### Recovery Statistics

```bash
# Get recovery stats
GET /api/v1/healing/recovery/stats

# Get component-specific stats
GET /api/v1/healing/recovery/stats?component=openai_adapter

# Get recent recoveries
GET /api/v1/healing/recovery/recent?count=10
```

**Response**:
```json
{
  "overall": {
    "total_recoveries": 150,
    "successful_recoveries": 142,
    "failed_recoveries": 8,
    "success_rate": 0.947,
    "avg_duration_ms": 2345.6
  },
  "by_action": {
    "retry_backoff": {
      "total": 100,
      "successful": 95
    },
    "fallback": {
      "total": 30,
      "successful": 28
    },
    "circuit_break": {
      "total": 20,
      "successful": 19
    }
  }
}
```

### Circuit Breaker Management

```bash
# Get circuit breaker status
GET /api/v1/healing/circuit-breakers

# Reset circuit breaker
POST /api/v1/healing/circuit-breakers/reset
Content-Type: application/json

{
  "component": "openai_adapter"
}
```

### Monitoring Control

```bash
# Start monitoring
POST /api/v1/healing/monitoring/start

# Stop monitoring
POST /api/v1/healing/monitoring/stop

# Get monitoring status
GET /api/v1/healing/monitoring/status
```

---

## Advanced Usage

### Custom Recovery Strategy

```python
from yago.healing.strategies import RecoveryStrategy
from yago.healing.base import RecoveryResult

class CustomRecoveryStrategy(RecoveryStrategy):
    async def execute(self, operation, error_context, *args, **kwargs):
        start_time = datetime.utcnow()

        # Custom recovery logic
        try:
            result = await my_custom_recovery(operation, *args, **kwargs)

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            return RecoveryResult(
                success=True,
                action=RecoveryAction.CUSTOM,
                error_context=error_context,
                attempts=1,
                duration_ms=duration,
                resolved_at=datetime.utcnow(),
                message="Custom recovery succeeded",
                metadata={"result": result}
            )

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            return RecoveryResult(
                success=False,
                action=RecoveryAction.CUSTOM,
                error_context=error_context,
                attempts=1,
                duration_ms=duration,
                message=f"Custom recovery failed: {str(e)}"
            )
```

### Custom Health Check

```python
async def custom_health_check():
    """Custom health check function"""
    try:
        # Perform custom checks
        response_time = await measure_response_time()
        error_rate = await calculate_error_rate()

        if error_rate > 0.1:
            status = HealthStatus.UNHEALTHY
        elif response_time > 1000:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY

        return HealthCheckResult(
            component="my_component",
            status=status,
            response_time_ms=response_time,
            error_rate=error_rate,
            success_rate=1.0 - error_rate,
            message="Custom health check complete"
        )

    except Exception as e:
        return HealthCheckResult(
            component="my_component",
            status=HealthStatus.CRITICAL,
            message=f"Health check failed: {str(e)}"
        )

# Register custom health check
health_monitor.register_health_check("my_component", custom_health_check)
```

### Multiple Fallback Strategies

```python
# Register multiple fallback options
recovery_engine.register_fallback(
    component="llm_service",
    fallback_operations=[
        lambda *args, **kwargs: openai_api.generate(*args, **kwargs),
        lambda *args, **kwargs: anthropic_api.generate(*args, **kwargs),
        lambda *args, **kwargs: google_api.generate(*args, **kwargs),
        lambda *args, **kwargs: local_model.generate(*args, **kwargs),
    ]
)
```

---

## Best Practices

### 1. Choose Appropriate Strategies

- **Transient Errors**: Use retry with backoff
- **Service Failures**: Use circuit breaker
- **Multiple Providers**: Use fallback
- **Stateful Operations**: Use rollback

### 2. Set Realistic Thresholds

```python
# Don't be too aggressive
CircuitBreakerConfig(
    failure_threshold=5,    # Not too low
    timeout_seconds=60.0    # Give enough time to recover
)

# Don't retry forever
RetryConfig(
    max_attempts=3,         # Reasonable limit
    max_delay_ms=60000.0    # Cap delays
)
```

### 3. Monitor Health Continuously

```python
# Start monitoring early
await health_monitor.start_monitoring()

# Register alert callbacks
health_monitor.register_alert_callback(send_to_slack)
health_monitor.register_alert_callback(log_to_file)
health_monitor.register_alert_callback(send_email)
```

### 4. Track Recovery Metrics

```python
# Regularly check recovery stats
stats = recovery_engine.get_recovery_stats()

# Identify problematic components
for component, data in stats["by_component"].items():
    if data["total"] > 100 and data["successful"] / data["total"] < 0.9:
        logger.warning(f"Component {component} has low recovery rate")
```

### 5. Use Appropriate Severity

```python
# Don't treat everything as critical
if error_rate < 0.1:
    severity = ErrorSeverity.MEDIUM
elif error_rate < 0.3:
    severity = ErrorSeverity.HIGH
else:
    severity = ErrorSeverity.CRITICAL
```

---

## Troubleshooting

### Circuit Breaker Stuck Open

```bash
# Check circuit breaker status
GET /api/v1/healing/circuit-breakers

# Reset if needed
POST /api/v1/healing/circuit-breakers/reset
{"component": "my_component"}
```

### High Error Rates

```bash
# Check component health
GET /api/v1/healing/health?component=my_component

# Check recent errors
GET /api/v1/healing/component/my_component/stats

# Reset metrics if needed
POST /api/v1/healing/component/my_component/reset
```

### Recovery Not Working

1. Check if component is registered
2. Verify recovery strategy is appropriate
3. Check circuit breaker state
4. Review recovery statistics

```python
# Debug recovery
stats = recovery_engine.get_recovery_stats()
print(stats)

# Check recent attempts
recent = recovery_engine.get_recent_recoveries(10)
for r in recent:
    print(f"{r['component']}.{r['operation']}: {r['action']} -> {r['success']}")
```

---

## Performance Impact

### Monitoring Overhead

- Health checks: ~1-5ms per check
- Error detection: ~0.1-0.5ms per error
- Recovery execution: Varies by strategy

### Resource Usage

- Memory: ~10-50MB for tracking
- CPU: < 1% for monitoring
- Network: None (unless sending alerts)

### Optimization Tips

1. Adjust monitoring interval based on needs
2. Limit history size for large systems
3. Use async operations to avoid blocking
4. Cache health check results when appropriate

---

## Examples

### Example 1: API with Auto-Recovery

```python
from yago.healing import RecoveryEngine, HealthMonitor, ErrorDetector

# Initialize
health_monitor = HealthMonitor()
recovery_engine = RecoveryEngine(health_monitor)

# Register component with circuit breaker
recovery_engine.register_circuit_breaker("api_service")

# Execute with auto-recovery
async def call_api(prompt):
    return await recovery_engine.execute_with_recovery(
        operation=api_client.generate,
        component="api_service",
        operation_name="generate",
        prompt=prompt
    )

# Use it
try:
    result = await call_api("Hello, world!")
except Exception as e:
    # Only raises if recovery fails
    logger.error(f"API call failed after recovery: {e}")
```

### Example 2: Multi-Provider Fallback

```python
# Register fallback providers
recovery_engine.register_fallback(
    component="llm",
    fallback_operations=[
        lambda **kw: openai.generate(**kw),
        lambda **kw: anthropic.generate(**kw),
        lambda **kw: local_model.generate(**kw),
    ]
)

# Execute - automatically tries fallbacks
result = await recovery_engine.execute_with_recovery(
    operation=primary_llm.generate,
    component="llm",
    operation_name="generate",
    prompt="Write a poem"
)
```

### Example 3: Health-Based Alerting

```python
# Define alert function
async def send_alert(health_result):
    if health_result.status == HealthStatus.CRITICAL:
        await slack.send(f"🚨 CRITICAL: {health_result.message}")
        await pagerduty.trigger_incident()
    elif health_result.status == HealthStatus.UNHEALTHY:
        await slack.send(f"⚠️  WARNING: {health_result.message}")

# Register and start
health_monitor.register_alert_callback(send_alert)
await health_monitor.start_monitoring()
```

---

## License

Apache-2.0
