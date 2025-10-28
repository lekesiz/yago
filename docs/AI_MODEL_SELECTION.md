# AI Model Selection System

**YAGO v8.0** - Intelligent AI model management and selection

---

## Overview

YAGO's AI Model Selection system provides dynamic, intelligent selection of AI models based on your requirements. Choose models based on cost, speed, quality, or custom criteria.

### Key Features

- **Multi-Provider Support**: OpenAI, Anthropic, Google, Local models
- **Intelligent Selection**: 5 strategies (cheapest, fastest, best quality, balanced, custom)
- **Cost Optimization**: Real-time cost calculation per 1M tokens
- **Model Comparison**: Side-by-side comparison of multiple models
- **Benchmarking**: Performance testing with custom test cases
- **Fallback System**: Automatic fallback suggestions
- **REST API**: Complete API for model management

---

## Quick Start

### 1. List Available Models

```python
from yago.models import get_registry

registry = get_registry()
models = registry.list_models()

for model in models:
    print(f"{model.name} - ${model.input_price_per_1m}/1M tokens")
```

### 2. Select Best Model

```python
from yago.models import ModelSelector, SelectionStrategy, ModelCapability

selector = ModelSelector(registry)

# Select cheapest model for code generation
model_id = selector.select(
    strategy=SelectionStrategy.CHEAPEST,
    capability=ModelCapability.CODE_GENERATION
)

print(f"Selected: {model_id}")
```

### 3. Use Selected Model

```python
from yago.models import ModelRequest

model = registry.get(model_id)
await model.initialize()

request = ModelRequest(
    messages=[
        {"role": "user", "content": "Write a Python function to sort a list"}
    ],
    temperature=0.7,
    max_tokens=1024
)

response = await model.generate(request)
print(response.content)
print(f"Cost: ${response.cost_breakdown['total']:.6f}")
```

---

## Selection Strategies

### 1. CHEAPEST
Select the most cost-effective model.

```python
model_id = selector.select(strategy=SelectionStrategy.CHEAPEST)
```

**Use Cases**:
- High-volume text processing
- Simple tasks
- Budget constraints

### 2. FASTEST
Select the model with lowest latency.

```python
model_id = selector.select(strategy=SelectionStrategy.FASTEST)
```

**Use Cases**:
- Real-time applications
- Interactive chatbots
- Time-sensitive tasks

### 3. BEST_QUALITY
Select the highest quality model.

```python
model_id = selector.select(strategy=SelectionStrategy.BEST_QUALITY)
```

**Use Cases**:
- Complex reasoning
- Critical decisions
- High-accuracy requirements

### 4. BALANCED (Default)
Balance cost, speed, and quality.

```python
model_id = selector.select(strategy=SelectionStrategy.BALANCED)
```

**Scoring**:
- Cost: 30%
- Context window: 30%
- Speed: 20%
- Capabilities: 20%

**Use Cases**:
- General-purpose tasks
- Production workloads
- Most common scenario

### 5. CUSTOM
Define custom weights for selection.

```python
model_id = selector.select(
    strategy=SelectionStrategy.CUSTOM,
    custom_weights={
        "cost": 0.5,        # 50% weight on cost
        "context": 0.3,     # 30% weight on context
        "speed": 0.1,       # 10% weight on speed
        "capabilities": 0.1 # 10% weight on capabilities
    }
)
```

---

## Model Comparison

Compare multiple models side-by-side:

```python
from yago.models import ModelComparison

comparison = ModelComparison(registry)

results = await comparison.compare(
    model_ids=["gpt-4-turbo", "claude-3-opus", "gemini-pro"],
    request=ModelRequest(
        prompt="Explain quantum computing in simple terms",
        max_tokens=500
    ),
    timeout=30.0
)

# View rankings
print(f"Cheapest: {results['rankings']['by_cost'][0]}")
print(f"Fastest: {results['rankings']['by_speed'][0]}")
```

### Generate Report

```python
# Text report
report = comparison.generate_report(results, format="text")
print(report)

# Markdown report
md_report = comparison.generate_report(results, format="markdown")

# HTML report
html_report = comparison.generate_report(results, format="html")
```

---

## Benchmarking

Benchmark a model with custom test cases:

```python
test_cases = [
    ModelRequest(prompt="Translate 'hello' to French"),
    ModelRequest(prompt="Translate 'goodbye' to Spanish"),
    ModelRequest(prompt="Translate 'thank you' to German")
]

results = await comparison.benchmark(
    model_id="gpt-3.5-turbo",
    test_cases=test_cases,
    iterations=3  # Run each test 3 times
)

print(f"Average latency: {results['statistics']['latency']['avg_ms']:.2f}ms")
print(f"Average cost: ${results['statistics']['cost']['avg']:.6f}")
print(f"Success rate: {results['statistics']['success_rate']*100:.1f}%")
```

---

## REST API

### List Models

```bash
GET /api/v1/models/list?provider=openai&capability=chat
```

**Response**:
```json
{
  "total": 3,
  "models": [
    {
      "id": "gpt-4-turbo",
      "name": "GPT-4 Turbo",
      "provider": "openai",
      "capabilities": ["text_generation", "chat", "code_generation"],
      "pricing": {
        "input_per_1m": 10.0,
        "output_per_1m": 30.0
      }
    }
  ]
}
```

### Select Model

```bash
POST /api/v1/models/select
Content-Type: application/json

{
  "strategy": "balanced",
  "capability": "code_generation",
  "max_cost": 5.0,
  "min_context_window": 8000
}
```

**Response**:
```json
{
  "selected_model": "gpt-3.5-turbo",
  "strategy": "balanced",
  "model_info": {
    "name": "GPT-3.5 Turbo",
    "provider": "openai",
    "context_window": 16385,
    "cost_per_1m": 1.5
  },
  "fallback_models": ["gpt-4", "claude-3-haiku"]
}
```

### Compare Models

```bash
POST /api/v1/models/compare
Content-Type: application/json

{
  "model_ids": ["gpt-4-turbo", "claude-3-opus"],
  "prompt": "Write a Python function",
  "temperature": 0.7,
  "max_tokens": 1024
}
```

### Get Recommendations

```bash
GET /api/v1/models/recommendations/code_generation?max_cost=5.0
```

**Response**:
```json
{
  "capability": "code_generation",
  "recommendations": {
    "cheapest": {
      "id": "gpt-3.5-turbo",
      "name": "GPT-3.5 Turbo",
      "cost_per_1m": 1.5
    },
    "fastest": {
      "id": "claude-3-haiku",
      "name": "Claude 3 Haiku",
      "cost_per_1m": 1.25
    },
    "best": {
      "id": "gpt-4-turbo",
      "name": "GPT-4 Turbo",
      "cost_per_1m": 40.0
    }
  }
}
```

---

## Supported Models

### OpenAI
- **GPT-4 Turbo**: $10 input / $30 output per 1M tokens
  - Context: 128K tokens
  - Best for: Complex reasoning, code, analysis
- **GPT-4**: $30 input / $60 output per 1M tokens
  - Context: 8K tokens
  - Best for: High-quality responses
- **GPT-3.5 Turbo**: $0.5 input / $1.5 output per 1M tokens
  - Context: 16K tokens
  - Best for: Fast, cost-effective tasks

### Anthropic
- **Claude 3 Opus**: $15 input / $75 output per 1M tokens
  - Context: 200K tokens
  - Best for: Longest context, complex tasks
- **Claude 3 Sonnet**: $3 input / $15 output per 1M tokens
  - Context: 200K tokens
  - Best for: Balanced performance
- **Claude 3 Haiku**: $0.25 input / $1.25 output per 1M tokens
  - Context: 200K tokens
  - Best for: Fast, cost-effective

### Google
- **Gemini Pro**: $0.5 input / $1.5 output per 1M tokens
  - Context: 32K tokens
  - Best for: Multimodal tasks

### Local Models
- **Ollama/LM Studio**: Free
  - Context: Varies by model
  - Best for: Privacy, no API costs

---

## Advanced Usage

### Filtering Models

```python
# Filter by provider
openai_models = registry.list_models(provider=ModelProvider.OPENAI)

# Filter by capability
code_models = registry.list_models(capability=ModelCapability.CODE_GENERATION)

# Exclude deprecated
current_models = registry.list_models(exclude_deprecated=True)
```

### Search Models

```python
results = registry.search("turbo")
# Returns: gpt-4-turbo, gpt-3.5-turbo
```

### Get Best Model

```python
best = registry.get_best_model(
    capability=ModelCapability.CHAT,
    max_cost=10.0  # Max $10 per 1M tokens
)
```

### Fallback Models

```python
fallbacks = selector.get_fallback_models(
    primary_model_id="gpt-4-turbo",
    max_fallbacks=3
)
# Returns similar models as fallback options
```

### Cost Calculation

```python
cost = model.calculate_cost(
    prompt_tokens=1000,
    completion_tokens=500
)
print(f"Input: ${cost['input']:.6f}")
print(f"Output: ${cost['output']:.6f}")
print(f"Total: ${cost['total']:.6f}")
```

---

## Configuration

### Environment Variables

```bash
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Local Model Server
LOCAL_MODEL_URL=http://localhost:11434  # Ollama default
```

### Custom Model Registration

```python
from yago.models import ModelMetadata, ModelProvider, ModelCapability

metadata = ModelMetadata(
    id="my-custom-model",
    name="My Custom Model",
    provider=ModelProvider.CUSTOM,
    version="1.0.0",
    capabilities=[ModelCapability.TEXT_GENERATION],
    context_window=4096,
    max_tokens=2048,
    input_price_per_1m=1.0,
    output_price_per_1m=2.0
)

registry.register(custom_model, metadata)
```

---

## Best Practices

### 1. Choose the Right Strategy

- **Development**: Use `CHEAPEST` for testing
- **Production**: Use `BALANCED` for most cases
- **Critical**: Use `BEST_QUALITY` for important tasks
- **Real-time**: Use `FASTEST` for interactive apps

### 2. Set Constraints

```python
model_id = selector.select(
    strategy=SelectionStrategy.BALANCED,
    max_cost=5.0,              # Budget constraint
    min_context_window=16000,  # Context requirement
    max_latency_ms=2000        # Speed requirement
)
```

### 3. Use Fallbacks

Always request fallback models for high availability:

```python
fallbacks = selector.get_fallback_models(primary_model_id)
for fallback in fallbacks:
    try:
        model = registry.get(fallback)
        response = await model.generate(request)
        break
    except Exception:
        continue
```

### 4. Monitor Costs

Track costs across all model usage:

```python
response = await model.generate(request)
total_cost += response.cost_breakdown['total']
```

### 5. Benchmark Before Production

Always benchmark models with your workload:

```python
results = await comparison.benchmark(
    model_id="gpt-3.5-turbo",
    test_cases=your_test_cases,
    iterations=10
)
```

---

## Examples

### Example 1: Cost-Optimized Translation Service

```python
from yago.models import get_registry, ModelSelector, SelectionStrategy

registry = get_registry()
selector = ModelSelector(registry)

# Select cheapest model for translation
model_id = selector.select(
    strategy=SelectionStrategy.CHEAPEST,
    capability=ModelCapability.TEXT_GENERATION
)

model = registry.get(model_id)
await model.initialize()

# Process 1000 translations
total_cost = 0.0
for text in translations:
    request = ModelRequest(
        prompt=f"Translate to French: {text}",
        max_tokens=200
    )
    response = await model.generate(request)
    total_cost += response.cost_breakdown['total']

print(f"Total cost for 1000 translations: ${total_cost:.2f}")
```

### Example 2: Real-Time Chat Application

```python
# Select fastest model for real-time chat
model_id = selector.select(
    strategy=SelectionStrategy.FASTEST,
    capability=ModelCapability.CHAT,
    max_latency_ms=1000  # Max 1 second response
)

model = registry.get(model_id)
await model.initialize()

# Stream responses
async for chunk in model.generate_stream(request):
    await websocket.send(chunk)
```

### Example 3: Code Generation with Quality Priority

```python
# Select best model for code generation
model_id = selector.select(
    strategy=SelectionStrategy.BEST_QUALITY,
    capability=ModelCapability.CODE_GENERATION
)

model = registry.get(model_id)
response = await model.generate(ModelRequest(
    messages=[
        {"role": "system", "content": "You are an expert programmer"},
        {"role": "user", "content": "Write a binary search tree in Python"}
    ],
    temperature=0.2,  # Low temperature for code
    max_tokens=2048
))
```

---

## Troubleshooting

### API Key Not Set

```python
# Error: openai.APIKeyError
# Solution: Set environment variable
import os
os.environ['OPENAI_API_KEY'] = 'sk-...'
```

### Model Not Found

```python
# Error: Model 'xyz' not found
# Solution: Check available models
models = registry.list_models()
print([m.id for m in models])
```

### Rate Limit Exceeded

```python
# Error: RateLimitError
# Solution: Add retry with exponential backoff
import asyncio

for attempt in range(3):
    try:
        response = await model.generate(request)
        break
    except RateLimitError:
        await asyncio.sleep(2 ** attempt)
```

### Cost Too High

```python
# Solution: Set max_cost constraint
model_id = selector.select(
    strategy=SelectionStrategy.BALANCED,
    max_cost=2.0  # Max $2 per 1M tokens
)
```

---

## Performance Tips

1. **Reuse Clients**: Initialize models once, reuse for multiple requests
2. **Batch Requests**: Process multiple requests in parallel with `asyncio.gather()`
3. **Cache Responses**: Cache common prompts to reduce API calls
4. **Use Streaming**: For long responses, use `generate_stream()` for better UX
5. **Monitor Usage**: Track token usage and costs in real-time

---

## API Reference

See [models_api.py](../yago/web/backend/models_api.py) for complete API reference.

**Endpoints**:
- `GET /api/v1/models/list` - List models
- `GET /api/v1/models/{model_id}` - Get model details
- `POST /api/v1/models/select` - Select best model
- `POST /api/v1/models/compare` - Compare models
- `POST /api/v1/models/benchmark` - Benchmark model
- `GET /api/v1/models/search` - Search models
- `GET /api/v1/models/providers` - List providers
- `GET /api/v1/models/capabilities` - List capabilities
- `GET /api/v1/models/strategies` - List strategies
- `GET /api/v1/models/stats` - Registry statistics
- `GET /api/v1/models/recommendations/{capability}` - Get recommendations

---

## License

Apache-2.0
