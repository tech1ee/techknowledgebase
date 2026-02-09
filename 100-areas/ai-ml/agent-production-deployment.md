---
title: "AI Agent Production Deployment"
tags:
  - topic/ai-ml
  - agents
  - deployment
  - production
  - kubernetes
  - scaling
  - reliability
  - type/concept
  - level/intermediate
category: ai-ml
level: advanced
created: 2026-01-11
updated: 2026-01-11
sources:
  - langchain.com
  - anthropic.com
  - openai.com
  - kubernetes.io
status: published
---

# AI Agent Production Deployment: Полное руководство

---

## TL;DR

> Деплой AI-агентов в production — это не просто "запустить на сервере". Агенты имеют уникальные требования: длительные сессии, stateful execution, непредсказуемый resource usage, зависимость от внешних API. Этот гайд покрывает всё: от архитектуры deployment до high availability, scaling, security и disaster recovery.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **AI Agents** | Понимание архитектуры | [[ai-agents-advanced]] |
| **Docker/Kubernetes** | Container orchestration | [[devops-overview]] |
| **API design** | REST, async patterns | [[api-design]] |
| **Observability** | Logging, metrics, tracing | [[ai-observability-monitoring]] |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **AI Engineer** | ✅ Да | Production patterns |
| **DevOps/SRE** | ✅ Да | Infrastructure design |
| **Tech Lead** | ✅ Да | Architecture decisions |
| **Platform Engineer** | ✅ Да | Platform capabilities |

---

## Архитектура Production Agent System

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                         PRODUCTION ARCHITECTURE                         │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────────────────┐   │
│  │   Clients   │────►│   Gateway   │────►│   Agent Orchestrator    │   │
│  │ (Web, API)  │     │ (API + WS)  │     │  (Task Queue + Router)  │   │
│  └─────────────┘     └─────────────┘     └───────────┬─────────────┘   │
│                                                       │                  │
│         ┌─────────────────────────────────────────────┼─────────────┐   │
│         │                                             │             │   │
│         ▼                                             ▼             ▼   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────────┐ │
│  │   Agent     │    │   Agent     │    │         Agent               │ │
│  │  Worker 1   │    │  Worker 2   │    │        Worker N             │ │
│  │             │    │             │    │                             │ │
│  │ ┌─────────┐ │    │ ┌─────────┐ │    │  ┌─────────┐ ┌─────────┐   │ │
│  │ │ LLM API │ │    │ │ LLM API │ │    │  │ LLM API │ │  Tools  │   │ │
│  │ └─────────┘ │    │ └─────────┘ │    │  └─────────┘ └─────────┘   │ │
│  └─────────────┘    └─────────────┘    └─────────────────────────────┘ │
│         │                 │                        │                    │
│         └─────────────────┼────────────────────────┘                    │
│                           │                                             │
│                           ▼                                             │
│  ┌────────────────────────────────────────────────────────────────────┐│
│  │                        PERSISTENCE LAYER                            ││
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   ││
│  │  │  State   │  │  Cache   │  │  Vector  │  │   Object Store   │   ││
│  │  │   DB     │  │ (Redis)  │  │    DB    │  │   (S3/GCS)       │   ││
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘   ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

### Компоненты системы

| Компонент | Роль | Технологии |
|-----------|------|------------|
| **Gateway** | Auth, rate limiting, routing | Nginx, Kong, Envoy |
| **Orchestrator** | Task scheduling, load balancing | Celery, Temporal, Redis Queue |
| **Agent Workers** | Execution runtime | Docker, K8s pods |
| **State DB** | Conversation history, agent state | PostgreSQL, MongoDB |
| **Cache** | Session cache, prompt cache | Redis, Memcached |
| **Vector DB** | RAG, semantic search | Pinecone, Weaviate, Qdrant |
| **Object Store** | Files, artifacts | S3, GCS, MinIO |

---

## Deployment Patterns

### Pattern 1: Stateless Agent (Simple)

```python
# Простой stateless деплой
# Подходит для: simple Q&A, single-turn interactions

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AgentRequest(BaseModel):
    message: str
    context: dict = {}

class AgentResponse(BaseModel):
    response: str
    metadata: dict = {}

@app.post("/agent/run")
async def run_agent(request: AgentRequest) -> AgentResponse:
    """Stateless agent endpoint"""

    # Каждый запрос независим
    agent = create_agent()

    result = await agent.run(
        message=request.message,
        context=request.context
    )

    return AgentResponse(
        response=result.output,
        metadata={"tokens_used": result.tokens}
    )

# Dockerfile
"""
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

# Kubernetes deployment
"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent
  template:
    metadata:
      labels:
        app: agent
    spec:
      containers:
      - name: agent
        image: agent-service:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai
"""
```

### Pattern 2: Stateful Agent with Sessions

```python
# Stateful agent с сессиями
# Подходит для: multi-turn conversations, complex workflows

from fastapi import FastAPI, WebSocket
from redis import Redis
import json

app = FastAPI()
redis = Redis.from_url("redis://redis:6379")

class SessionManager:
    """Управление сессиями агента"""

    def __init__(self, redis_client: Redis, ttl: int = 3600):
        self.redis = redis_client
        self.ttl = ttl

    async def get_session(self, session_id: str) -> dict | None:
        data = self.redis.get(f"session:{session_id}")
        if data:
            return json.loads(data)
        return None

    async def save_session(self, session_id: str, state: dict):
        self.redis.setex(
            f"session:{session_id}",
            self.ttl,
            json.dumps(state)
        )

    async def delete_session(self, session_id: str):
        self.redis.delete(f"session:{session_id}")


sessions = SessionManager(redis)

@app.websocket("/agent/ws/{session_id}")
async def agent_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint для real-time interactions"""

    await websocket.accept()

    # Восстанавливаем или создаём сессию
    state = await sessions.get_session(session_id)
    if not state:
        state = {"messages": [], "context": {}}

    agent = create_agent_with_state(state)

    try:
        while True:
            # Получаем сообщение
            data = await websocket.receive_json()

            # Стримим ответ
            async for chunk in agent.stream(data["message"]):
                await websocket.send_json({
                    "type": "chunk",
                    "content": chunk
                })

            # Сохраняем состояние
            await sessions.save_session(session_id, agent.get_state())

            # Финальный ответ
            await websocket.send_json({
                "type": "complete",
                "metadata": agent.get_metadata()
            })

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()
```

### Pattern 3: Background Agent with Task Queue

```python
# Background agent с очередью задач
# Подходит для: long-running tasks, async processing

from celery import Celery
from celery.result import AsyncResult

app = Celery('agent_tasks', broker='redis://redis:6379')

@app.task(bind=True, max_retries=3, soft_time_limit=300)
def run_agent_task(self, task_id: str, task_config: dict):
    """Background agent task"""

    try:
        agent = create_agent(task_config)

        # Выполняем с progress updates
        for step, result in agent.run_with_progress(task_config["input"]):
            # Обновляем статус
            self.update_state(
                state='PROGRESS',
                meta={
                    'step': step,
                    'result': result,
                    'progress': step / task_config.get('max_steps', 10)
                }
            )

        return {
            'status': 'completed',
            'result': result,
            'steps': step
        }

    except Exception as e:
        # Retry с exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


# FastAPI endpoints для task management
@app.post("/agent/task")
async def create_task(config: dict) -> dict:
    """Создаём async task"""
    task = run_agent_task.delay(str(uuid4()), config)
    return {"task_id": task.id}

@app.get("/agent/task/{task_id}")
async def get_task_status(task_id: str) -> dict:
    """Получаем статус task"""
    result = AsyncResult(task_id)

    if result.ready():
        return {
            "status": "completed",
            "result": result.get()
        }
    elif result.state == 'PROGRESS':
        return {
            "status": "in_progress",
            "progress": result.info
        }
    else:
        return {"status": result.state}
```

### Pattern 4: LangGraph Cloud Deployment

```python
# LangGraph Cloud / LangGraph Platform
# Production-ready managed service

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

# Определяем граф агента
def create_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "end": END
        }
    )
    workflow.add_edge("tools", "agent")

    workflow.set_entry_point("agent")

    # Checkpointing для persistence
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)


# langgraph.json для deployment
"""
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./agent.py:create_agent_graph"
  },
  "env": ".env"
}
"""

# Deploy command:
# langgraph up

# API usage после deploy:
"""
POST /threads
POST /threads/{thread_id}/runs
GET /threads/{thread_id}/runs/{run_id}
POST /threads/{thread_id}/runs/{run_id}/cancel
"""
```

---

## Kubernetes Deployment

### Production Kubernetes Config

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-agents
  labels:
    name: ai-agents

---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-config
  namespace: ai-agents
data:
  LOG_LEVEL: "INFO"
  MAX_TOKENS: "4096"
  TIMEOUT_SECONDS: "300"
  MAX_RETRIES: "3"

---
# secrets.yaml (use external secrets in production!)
apiVersion: v1
kind: Secret
metadata:
  name: api-keys
  namespace: ai-agents
type: Opaque
stringData:
  openai: "${OPENAI_API_KEY}"
  anthropic: "${ANTHROPIC_API_KEY}"

---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-service
  namespace: ai-agents
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: agent-service
  template:
    metadata:
      labels:
        app: agent-service
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
    spec:
      serviceAccountName: agent-service
      containers:
      - name: agent
        image: myregistry/agent-service:v1.2.3
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 9090
          name: metrics
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai
        envFrom:
        - configMapRef:
            name: agent-config
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: cache
          mountPath: /app/cache
      volumes:
      - name: cache
        emptyDir:
          sizeLimit: 1Gi

---
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: agent-service-hpa
  namespace: ai-agents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: agent-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: agent_active_tasks
      target:
        type: AverageValue
        averageValue: "10"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: agent-service
  namespace: ai-agents
spec:
  selector:
    app: agent-service
  ports:
  - name: http
    port: 80
    targetPort: 8000
  - name: metrics
    port: 9090
    targetPort: 9090
  type: ClusterIP

---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: agent-ingress
  namespace: ai-agents
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - agents.example.com
    secretName: agent-tls
  rules:
  - host: agents.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: agent-service
            port:
              number: 80
```

### Health Checks Implementation

```python
from fastapi import FastAPI, Response
from datetime import datetime

app = FastAPI()

# State tracking
startup_time = None
last_successful_llm_call = None

@app.on_event("startup")
async def startup():
    global startup_time
    startup_time = datetime.now()
    # Warm-up LLM connection
    await warm_up_llm()

@app.get("/health")
async def health():
    """Liveness probe - is the service alive?"""
    return {"status": "ok", "uptime": str(datetime.now() - startup_time)}

@app.get("/ready")
async def ready():
    """Readiness probe - is the service ready to handle requests?"""

    checks = {
        "llm_connection": await check_llm_connection(),
        "redis_connection": await check_redis(),
        "database_connection": await check_database()
    }

    all_healthy = all(checks.values())

    if all_healthy:
        return {"status": "ready", "checks": checks}
    else:
        return Response(
            content=json.dumps({"status": "not_ready", "checks": checks}),
            status_code=503
        )

async def check_llm_connection() -> bool:
    """Проверяем LLM API"""
    try:
        # Минимальный запрос
        response = await llm.complete(
            model="gpt-4o-mini",
            prompt="Say 'ok'",
            max_tokens=5
        )
        global last_successful_llm_call
        last_successful_llm_call = datetime.now()
        return True
    except:
        return False

async def check_redis() -> bool:
    """Проверяем Redis"""
    try:
        redis.ping()
        return True
    except:
        return False
```

---

## High Availability

### Multi-Region Deployment

```
┌────────────────────────────────────────────────────────────┐
│                    MULTI-REGION SETUP                       │
├────────────────────────────────────────────────────────────┤
│                                                             │
│                    ┌─────────────┐                          │
│                    │   Global    │                          │
│                    │   LB/DNS    │                          │
│                    └──────┬──────┘                          │
│                           │                                  │
│           ┌───────────────┼───────────────┐                 │
│           │               │               │                 │
│           ▼               ▼               ▼                 │
│    ┌───────────┐   ┌───────────┐   ┌───────────┐           │
│    │  US-EAST  │   │  EU-WEST  │   │ ASIA-PAC  │           │
│    │           │   │           │   │           │           │
│    │ ┌───────┐ │   │ ┌───────┐ │   │ ┌───────┐ │           │
│    │ │Agents │ │   │ │Agents │ │   │ │Agents │ │           │
│    │ └───────┘ │   │ └───────┘ │   │ └───────┘ │           │
│    │ ┌───────┐ │   │ ┌───────┐ │   │ ┌───────┐ │           │
│    │ │ Redis │ │   │ │ Redis │ │   │ │ Redis │ │           │
│    │ └───────┘ │   │ └───────┘ │   │ └───────┘ │           │
│    └─────┬─────┘   └─────┬─────┘   └─────┬─────┘           │
│          │               │               │                  │
│          └───────────────┼───────────────┘                  │
│                          │                                  │
│                   ┌──────┴──────┐                           │
│                   │   Global    │                           │
│                   │  Database   │                           │
│                   │ (CockroachDB│                           │
│                   │  /Spanner)  │                           │
│                   └─────────────┘                           │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### Failover Strategy

```python
class FailoverManager:
    """Управление failover между регионами и LLM providers"""

    def __init__(self):
        self.regions = ["us-east", "eu-west", "asia-pac"]
        self.providers = ["openai", "anthropic", "azure-openai"]
        self.circuit_breakers = {}

    async def execute_with_failover(
        self,
        task,
        preferred_region: str = None,
        preferred_provider: str = None
    ):
        """Выполняем с failover"""

        regions = self._order_regions(preferred_region)
        providers = self._order_providers(preferred_provider)

        for region in regions:
            for provider in providers:
                breaker = self._get_breaker(region, provider)

                if breaker.is_open:
                    continue

                try:
                    result = await self._execute(task, region, provider)
                    breaker.record_success()
                    return result
                except Exception as e:
                    breaker.record_failure()
                    if breaker.is_open:
                        await self._notify_circuit_open(region, provider)
                    continue

        raise AllFailoversFailed("All regions and providers failed")

    def _get_breaker(self, region: str, provider: str) -> CircuitBreaker:
        key = f"{region}:{provider}"
        if key not in self.circuit_breakers:
            self.circuit_breakers[key] = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=60
            )
        return self.circuit_breakers[key]


class CircuitBreaker:
    """Circuit breaker для защиты от каскадных failures"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure = None
        self.state = "closed"

    @property
    def is_open(self) -> bool:
        if self.state == "closed":
            return False

        if self.state == "open":
            # Проверяем можно ли попробовать recovery
            if time.time() - self.last_failure > self.recovery_timeout:
                self.state = "half-open"
                return False
            return True

        return False  # half-open

    def record_success(self):
        self.failures = 0
        self.state = "closed"

    def record_failure(self):
        self.failures += 1
        self.last_failure = time.time()

        if self.failures >= self.failure_threshold:
            self.state = "open"
```

### Graceful Degradation

```python
class GracefulDegradation:
    """Graceful degradation при проблемах"""

    def __init__(self):
        self.degradation_levels = {
            0: "full_service",
            1: "reduced_features",
            2: "minimal_service",
            3: "maintenance_mode"
        }
        self.current_level = 0

    async def execute_with_degradation(self, task):
        """Выполняем с учётом degradation level"""

        if self.current_level == 0:
            return await self._full_service(task)
        elif self.current_level == 1:
            return await self._reduced_features(task)
        elif self.current_level == 2:
            return await self._minimal_service(task)
        else:
            return await self._maintenance_response()

    async def _full_service(self, task):
        """Полный сервис"""
        return await agent.run(task)

    async def _reduced_features(self, task):
        """Отключаем дорогие features"""
        # Отключаем: multi-agent, advanced reasoning
        return await simple_agent.run(task)

    async def _minimal_service(self, task):
        """Только базовый functionality"""
        # Используем cached responses где возможно
        cached = await cache.get_similar(task)
        if cached:
            return cached

        # Fallback на FAQ
        return await faq_lookup(task)

    async def _maintenance_response(self):
        """Maintenance mode"""
        return {
            "status": "maintenance",
            "message": "Service is temporarily unavailable"
        }

    def increase_degradation(self):
        """Увеличиваем уровень degradation"""
        if self.current_level < 3:
            self.current_level += 1
            logger.warning(f"Degradation level increased to {self.current_level}")

    def decrease_degradation(self):
        """Уменьшаем уровень degradation"""
        if self.current_level > 0:
            self.current_level -= 1
            logger.info(f"Degradation level decreased to {self.current_level}")
```

---

## Scaling Strategies

### Horizontal Scaling

```python
# Метрики для auto-scaling

from prometheus_client import Gauge, Counter, Histogram

# Custom metrics
ACTIVE_TASKS = Gauge(
    'agent_active_tasks',
    'Number of currently running agent tasks',
    ['agent_type']
)

QUEUE_SIZE = Gauge(
    'agent_queue_size',
    'Number of tasks waiting in queue',
    ['priority']
)

TASK_DURATION = Histogram(
    'agent_task_duration_seconds',
    'Time spent processing agent tasks',
    ['agent_type', 'task_type'],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600]
)

# HPA will scale based on these metrics:
# - CPU > 70%
# - agent_active_tasks > 10 per pod
# - agent_queue_size > 100
```

### Vertical Scaling Considerations

```yaml
# Resource profiles для разных agent types

# Light agent (simple Q&A)
light_agent:
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "250m"

# Standard agent (multi-step reasoning)
standard_agent:
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "500m"

# Heavy agent (multi-agent, long context)
heavy_agent:
  resources:
    requests:
      memory: "2Gi"
      cpu: "1000m"
    limits:
      memory: "4Gi"
      cpu: "2000m"
```

### Queue-based Scaling

```python
class QueueBasedScaler:
    """Scaling на основе очереди"""

    def __init__(
        self,
        queue_client,
        k8s_client,
        deployment_name: str
    ):
        self.queue = queue_client
        self.k8s = k8s_client
        self.deployment = deployment_name

        self.config = {
            "min_replicas": 3,
            "max_replicas": 50,
            "tasks_per_replica": 5,
            "scale_up_threshold": 0.8,
            "scale_down_threshold": 0.3
        }

    async def evaluate_and_scale(self):
        """Оцениваем и масштабируем"""

        queue_size = await self.queue.get_size()
        current_replicas = await self.get_current_replicas()

        capacity = current_replicas * self.config["tasks_per_replica"]
        utilization = queue_size / capacity if capacity > 0 else 1

        if utilization > self.config["scale_up_threshold"]:
            # Scale up
            target = min(
                int(current_replicas * 1.5),
                self.config["max_replicas"]
            )
            await self.scale_to(target)

        elif utilization < self.config["scale_down_threshold"]:
            # Scale down
            target = max(
                int(current_replicas * 0.7),
                self.config["min_replicas"]
            )
            await self.scale_to(target)

    async def scale_to(self, replicas: int):
        """Масштабируем до N реплик"""
        await self.k8s.patch_namespaced_deployment_scale(
            name=self.deployment,
            namespace="ai-agents",
            body={"spec": {"replicas": replicas}}
        )
        logger.info(f"Scaled to {replicas} replicas")
```

---

## Security Best Practices

### Secrets Management

```python
# НЕ ДЕЛАТЬ:
OPENAI_API_KEY = "sk-..."  # Hardcoded secret

# ДЕЛАТЬ:
import os
from google.cloud import secretmanager

def get_secret(secret_id: str) -> str:
    """Получаем secret из Secret Manager"""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

OPENAI_API_KEY = get_secret("openai-api-key")
```

### Input Validation

```python
from pydantic import BaseModel, validator, Field
import re

class AgentInput(BaseModel):
    """Validated input for agent"""

    message: str = Field(..., max_length=10000)
    context: dict = Field(default_factory=dict)
    session_id: str = Field(..., regex=r'^[a-zA-Z0-9-]{36}$')

    @validator('message')
    def sanitize_message(cls, v):
        # Удаляем потенциально опасные паттерны
        v = re.sub(r'<script.*?>.*?</script>', '', v, flags=re.DOTALL)
        v = re.sub(r'javascript:', '', v, flags=re.IGNORECASE)
        return v

    @validator('context')
    def validate_context(cls, v):
        # Ограничиваем размер context
        if len(str(v)) > 50000:
            raise ValueError("Context too large")
        return v
```

### Rate Limiting

```python
from fastapi import Request, HTTPException
from redis import Redis
import time

class RateLimiter:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> bool:
        """Проверяем rate limit"""
        current = time.time()
        window_start = current - window

        # Используем sorted set для sliding window
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {str(current): current})
        pipe.zcard(key)
        pipe.expire(key, window)
        results = pipe.execute()

        count = results[2]
        return count <= limit

async def rate_limit_middleware(request: Request, call_next):
    """Rate limit middleware"""
    limiter = RateLimiter(redis)

    # По API key
    api_key = request.headers.get("X-API-Key", "anonymous")

    if not await limiter.check_rate_limit(
        f"rate:{api_key}",
        limit=100,  # 100 requests
        window=60   # per minute
    ):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )

    return await call_next(request)
```

---

## Disaster Recovery

### Backup Strategy

```python
class BackupManager:
    """Backup критических данных агента"""

    async def backup_state(self):
        """Backup состояния сессий"""
        sessions = await redis.keys("session:*")

        backup_data = {}
        for key in sessions:
            data = await redis.get(key)
            backup_data[key] = data

        # Upload to S3
        await s3.put_object(
            Bucket="agent-backups",
            Key=f"sessions/{datetime.now().isoformat()}.json",
            Body=json.dumps(backup_data)
        )

    async def backup_conversations(self):
        """Backup истории разговоров"""
        # PostgreSQL backup
        await run_command(
            f"pg_dump -h {DB_HOST} -U {DB_USER} -d agents "
            f"-f /backups/conversations_{datetime.now().date()}.sql"
        )

        # Upload to S3
        await upload_to_s3(
            f"/backups/conversations_{datetime.now().date()}.sql",
            "agent-backups"
        )

    async def restore_state(self, backup_key: str):
        """Восстановление из backup"""
        data = await s3.get_object(
            Bucket="agent-backups",
            Key=backup_key
        )

        sessions = json.loads(data['Body'].read())
        for key, value in sessions.items():
            await redis.set(key, value)
```

### Recovery Procedures

```
DISASTER RECOVERY RUNBOOK

1. DETECT
   □ Monitor alerts: Latency > 5s, Error rate > 5%
   □ Check dashboards
   □ Verify scope (single pod, region, global)

2. ASSESS
   □ Identify root cause
   □ Estimate impact (users affected, data loss)
   □ Determine recovery strategy

3. RESPOND
   □ If single pod: let K8s handle restart
   □ If region failure: failover to backup region
   □ If data corruption: restore from backup
   □ If provider outage: switch LLM provider

4. RESTORE
   □ Apply fix/restore
   □ Verify functionality
   □ Monitor for stability

5. POST-INCIDENT
   □ Document timeline
   □ Root cause analysis
   □ Update runbooks
   □ Implement preventive measures
```

---

## Deployment Checklist

### Pre-deployment

```
□ CODE QUALITY
  □ All tests passing
  □ Code review approved
  □ Security scan passed
  □ No hardcoded secrets

□ INFRASTRUCTURE
  □ K8s manifests validated
  □ Resource limits set
  □ Health checks configured
  □ Secrets in secret manager

□ MONITORING
  □ Metrics exposed
  □ Dashboards ready
  □ Alerts configured
  □ Logging structured

□ SECURITY
  □ Input validation
  □ Rate limiting
  □ Authentication
  □ TLS configured
```

### Deployment

```
□ ROLLOUT
  □ Canary deployment (10% traffic)
  □ Monitor error rate
  □ Monitor latency
  □ Check logs for anomalies

□ VERIFICATION
  □ Health endpoints responding
  □ Smoke tests passing
  □ Key flows working
  □ Metrics collecting

□ FULL ROLLOUT
  □ Increase to 50%
  □ Monitor for 15 minutes
  □ Increase to 100%
  □ Confirm stable
```

### Post-deployment

```
□ MONITORING
  □ Error rate normal
  □ Latency within SLA
  □ Resource usage expected
  □ No regression in quality

□ DOCUMENTATION
  □ Deployment documented
  □ Changelog updated
  □ Runbooks updated if needed
```

---

## Связанные материалы

- [[ai-agents-advanced]] — архитектура агентов
- [[agent-debugging-troubleshooting]] — debugging
- [[agent-cost-optimization]] — оптимизация costs
- [[ai-devops-deployment]] — общий AI DevOps
- [[ai-observability-monitoring]] — мониторинг

---

*Создано: 2026-01-11*
