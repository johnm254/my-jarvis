# JARVIS API Reference

Complete reference for the JARVIS Dashboard API, Skill interfaces, and configuration options.

## Table of Contents

- [Authentication](#authentication)
- [Dashboard API Endpoints](#dashboard-api-endpoints)
  - [Auth Endpoints](#auth-endpoints)
  - [Conversation Endpoints](#conversation-endpoints)
  - [Memory Endpoints](#memory-endpoints)
  - [Skills Endpoints](#skills-endpoints)
  - [Settings Endpoints](#settings-endpoints)
  - [Audit Log Endpoints](#audit-log-endpoints)
  - [WebSocket Events](#websocket-events)
- [Skill Interfaces](#skill-interfaces)
  - [web_search](#web_search)
  - [get_weather](#get_weather)
  - [run_code](#run_code)
  - [manage_calendar](#manage_calendar)
  - [manage_email](#manage_email)
  - [smart_home](#smart_home)
  - [github_summary](#github_summary)
  - [daily_brief](#daily_brief)
  - [set_reminder](#set_reminder)
  - [system_status](#system_status)
- [Configuration Reference](#configuration-reference)
- [Error Codes](#error-codes)

---

## Authentication

All protected endpoints require a JWT Bearer token in the `Authorization` header.

```
Authorization: Bearer <your_jwt_token>
```

Tokens are obtained via `POST /api/auth/login` and expire after 24 hours.

---

## Dashboard API Endpoints

Base URL: `http://localhost:5000`

### Auth Endpoints

#### POST /api/auth/login

Authenticate and receive a JWT token.

**Request Body**
```json
{
  "username": "admin",
  "password": "jarvis123"
}
```

**Response 200**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "admin_user",
  "expires_in": 86400
}
```

**Response 401**
```json
{ "error": "Invalid username or password" }
```

**Example**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "jarvis123"}'
```

---

#### GET /api/auth/verify

Verify if the current JWT token is valid.

**Headers**: `Authorization: Bearer <token>`

**Response 200**
```json
{
  "valid": true,
  "user_id": "admin_user"
}
```

**Response 401**
```json
{ "error": "Invalid or expired token" }
```

---

#### GET /api/health

Health check endpoint (no auth required).

**Response 200**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### Conversation Endpoints

#### GET /api/conversation/history

Retrieve conversation history for a session.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session_id` | string | user_id | Session identifier |
| `limit` | integer | 20 | Max exchanges to return |

**Response 200**
```json
{
  "session_id": "session_123",
  "exchanges": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "user_input": "What's the weather in Seattle?",
      "brain_response": "In Seattle, it's currently 52°F and partly cloudy...",
      "confidence_score": 95,
      "tool_calls": [
        {
          "id": "call_abc123",
          "name": "get_weather",
          "input": { "location": "Seattle" }
        }
      ]
    }
  ],
  "count": 1
}
```

**Example**
```bash
curl -X GET "http://localhost:5000/api/conversation/history?limit=10" \
  -H "Authorization: Bearer <token>"
```

---

#### POST /api/conversation/send

Send a message to JARVIS and receive a response.

**Headers**: `Authorization: Bearer <token>`

**Request Body**
```json
{
  "message": "What's the weather in Seattle?",
  "session_id": "optional_session_id"
}
```

**Response 200**
```json
{
  "session_id": "session_123",
  "response": "In Seattle, it's currently 52°F and partly cloudy...",
  "confidence_score": 95,
  "tool_calls": [
    {
      "id": "call_abc123",
      "name": "get_weather",
      "input": { "location": "Seattle" }
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response 400**
```json
{ "error": "Message is required" }
```

**Example**
```bash
curl -X POST http://localhost:5000/api/conversation/send \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather in Seattle?"}'
```

---

### Memory Endpoints

#### GET /api/memory/search

Search stored memories using semantic similarity.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Search query |
| `limit` | integer | 5 | Max results |
| `threshold` | float | 0.7 | Min similarity (0-1) |

**Response 200**
```json
{
  "query": "weather Seattle",
  "results": [
    {
      "id": "uuid-here",
      "session_id": "session_123",
      "timestamp": "2024-01-15T10:30:00Z",
      "user_input": "What's the weather in Seattle?",
      "brain_response": "In Seattle, it's currently 52°F...",
      "similarity": 0.92
    }
  ],
  "count": 1
}
```

**Example**
```bash
curl -X GET "http://localhost:5000/api/memory/search?query=weather+Seattle&limit=5" \
  -H "Authorization: Bearer <token>"
```

---

#### PUT /api/memory/update

Update a stored memory entry.

**Headers**: `Authorization: Bearer <token>`

**Request Body**
```json
{
  "memory_id": "uuid-here",
  "updates": {
    "brain_response": "Updated response text"
  }
}
```

**Response 200**
```json
{
  "success": true,
  "memory_id": "uuid-here",
  "message": "Memory updated successfully"
}
```

---

#### DELETE /api/memory/delete

Delete a stored memory entry.

**Headers**: `Authorization: Bearer <token>`

**Request Body**
```json
{
  "memory_id": "uuid-here"
}
```

**Response 200**
```json
{
  "success": true,
  "memory_id": "uuid-here",
  "message": "Memory deleted successfully"
}
```

---

### Skills Endpoints

#### GET /api/skills/status

Get the status of all registered skills.

**Headers**: `Authorization: Bearer <token>`

**Response 200**
```json
{
  "skills": [
    {
      "name": "web_search",
      "description": "Search the web for current information using Brave API.",
      "status": "available",
      "requires_api_key": true,
      "api_key_configured": true
    },
    {
      "name": "get_weather",
      "description": "Get current weather conditions and 7-day forecast.",
      "status": "available",
      "requires_api_key": true,
      "api_key_configured": false
    }
  ],
  "total": 10,
  "available": 8
}
```

---

### Settings Endpoints

#### GET /api/settings

Retrieve current system settings.

**Headers**: `Authorization: Bearer <token>`

**Response 200**
```json
{
  "voice": {
    "enabled": true,
    "wake_word": "Hey Jarvis",
    "stt_model": "base"
  },
  "llm": {
    "model": "claude-sonnet-4-20250514"
  },
  "system": {
    "timezone": "UTC",
    "log_level": "INFO"
  }
}
```

---

#### PUT /api/settings

Update system settings.

**Headers**: `Authorization: Bearer <token>`

**Request Body**
```json
{
  "voice": {
    "enabled": false,
    "stt_model": "small"
  }
}
```

**Response 200**
```json
{
  "success": true,
  "message": "Settings updated successfully",
  "updated_fields": ["voice.enabled", "voice.stt_model"]
}
```

---

### Audit Log Endpoints

#### GET /api/audit-log

Retrieve audit log entries with pagination.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 50 | Entries per page |
| `action_type` | string | all | Filter by action type |
| `start_date` | string | - | ISO 8601 start date |
| `end_date` | string | - | ISO 8601 end date |

**Response 200**
```json
{
  "entries": [
    {
      "id": "uuid-here",
      "timestamp": "2024-01-15T10:30:00Z",
      "action_type": "conversation",
      "user_id": "admin_user",
      "details": {
        "session_id": "session_123",
        "confidence_score": 95
      },
      "success": true
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 150,
    "pages": 3
  }
}
```

**Example**
```bash
curl -X GET "http://localhost:5000/api/audit-log?page=1&per_page=20&action_type=authentication" \
  -H "Authorization: Bearer <token>"
```

---

### WebSocket Events

Connect to the WebSocket server for real-time updates.

**Connection URL**: `ws://localhost:5000`

#### Client → Server Events

**join_session**
```json
{ "session_id": "session_123" }
```

#### Server → Client Events

**conversation_update** — Emitted after each conversation turn
```json
{
  "session_id": "session_123",
  "user_input": "What's the weather?",
  "brain_response": "It's sunny today...",
  "confidence_score": 95,
  "tool_calls": [],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example (JavaScript)**
```javascript
const socket = io('http://localhost:5000');

socket.on('connect', () => {
  socket.emit('join_session', { session_id: 'my_session' });
});

socket.on('conversation_update', (data) => {
  console.log('New message:', data.brain_response);
});
```

---

## Skill Interfaces

Skills are invoked automatically by the Brain based on user requests. They can also be called directly via the `execute_tool_call()` method on the Brain.

All skills return a `SkillResult`:
```python
@dataclass
class SkillResult:
    success: bool           # Whether execution succeeded
    result: Any             # The result data (None on failure)
    error_message: str      # Error description (None on success)
    execution_time_ms: int  # Execution time in milliseconds
```

---

### web_search

Search the web using the Brave Search API.

**Requires**: `BRAVE_API_KEY` environment variable

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | The search query |

**Result**
```python
{
    "query": "Python best practices",
    "results": [
        {
            "position": 1,
            "title": "Python Best Practices Guide",
            "url": "https://example.com/python-guide",
            "description": "A comprehensive guide to Python best practices..."
        }
    ],
    "total_results": 5
}
```

**Performance**: < 3 seconds

**Example**
```python
brain = Brain(config, skill_registry)
result = brain.execute_tool_call("web_search", {"query": "Python best practices"})
if result.success:
    for item in result.result["results"]:
        print(f"{item['position']}. {item['title']}: {item['url']}")
```

---

### get_weather

Get current weather conditions and 7-day forecast.

**Requires**: `WEATHER_API_KEY` environment variable

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `location` | string | no | City name, zip code, or coordinates |

**Result**
```python
{
    "current": {
        "location": "Seattle",
        "region": "Washington",
        "country": "USA",
        "temperature_f": 52.0,
        "temperature_c": 11.1,
        "condition": "Partly cloudy",
        "humidity": 75,
        "wind_mph": 8.0,
        "feels_like_f": 49.0,
        "last_updated": "2024-01-15 10:00"
    },
    "forecast": [
        {
            "date": "2024-01-15",
            "max_temp_f": 58.0,
            "min_temp_f": 45.0,
            "condition": "Partly cloudy",
            "chance_of_rain": 30,
            "chance_of_snow": 0
        }
        // ... 6 more days
    ]
}
```

**Performance**: < 2 seconds

---

### run_code

Execute code in an isolated sandbox environment.

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `language` | string | yes | `python`, `javascript`, or `bash` |
| `code` | string | yes | Code to execute |

**Result**
```python
{
    "language": "python",
    "output": "Hello, World!\n",
    "error": "",
    "exit_code": 0,
    "execution_time_ms": 245
}
```

**Timeout**: 30 seconds

**Example**
```python
result = brain.execute_tool_call("run_code", {
    "language": "python",
    "code": "print('Hello, World!')"
})
print(result.result["output"])  # "Hello, World!\n"
```

---

### manage_calendar

Read, create, and update Google Calendar events.

**Requires**: `GOOGLE_CALENDAR_CREDENTIALS` environment variable

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | yes | `read`, `create`, or `update` |
| `details` | object | no | Action-specific details |

**Action: read**
```python
# details (optional)
{
    "start_date": "2024-01-15",
    "end_date": "2024-01-22",
    "max_results": 10
}
# result
{
    "events": [
        {
            "id": "event_id",
            "title": "Team Meeting",
            "start": "2024-01-15T14:00:00Z",
            "end": "2024-01-15T15:00:00Z",
            "location": "Conference Room A",
            "description": "Weekly sync"
        }
    ],
    "count": 1
}
```

**Action: create**
```python
# details (required)
{
    "title": "Doctor Appointment",
    "start": "2024-01-20T10:00:00",
    "end": "2024-01-20T11:00:00",
    "location": "Medical Center",
    "description": "Annual checkup"
}
```

**Note**: Requires explicit user confirmation before creating/updating events.

---

### manage_email

Read, summarize, and draft Gmail messages.

**Requires**: `GMAIL_CREDENTIALS` environment variable

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | yes | `read`, `summarize`, or `draft` |
| `filters` | object | no | Filter criteria |

**Action: read**
```python
# filters (optional)
{
    "unread_only": true,
    "max_results": 10,
    "label": "INBOX"
}
# result
{
    "emails": [
        {
            "id": "email_id",
            "subject": "Meeting Tomorrow",
            "from": "colleague@example.com",
            "date": "2024-01-15T09:00:00Z",
            "snippet": "Just a reminder about our meeting..."
        }
    ],
    "count": 1
}
```

**Note**: Requires explicit confirmation before sending emails.

---

### smart_home

Control smart home devices via Home Assistant.

**Requires**: `HOME_ASSISTANT_URL` and `HOME_ASSISTANT_TOKEN` environment variables

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `device` | string | yes | Device entity ID (e.g., `light.living_room`) |
| `action` | string | yes | Action to perform (e.g., `turn_on`, `turn_off`, `toggle`) |
| `attributes` | object | no | Additional attributes (e.g., brightness, color) |

**Result**
```python
{
    "device": "light.living_room",
    "action": "turn_on",
    "state": "on",
    "attributes": {
        "brightness": 255,
        "color_temp": 4000
    },
    "success": true
}
```

**Example**
```python
result = brain.execute_tool_call("smart_home", {
    "device": "light.living_room",
    "action": "turn_on",
    "attributes": {"brightness": 128}
})
```

---

### github_summary

Summarize GitHub repository activity.

**Requires**: `GITHUB_TOKEN` environment variable

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo` | string | yes | Repository in `owner/repo` format |

**Result**
```python
{
    "repo": "facebook/react",
    "pull_requests": [
        {
            "number": 28000,
            "title": "Fix memory leak in useEffect",
            "author": "developer123",
            "created_at": "2024-01-14T08:00:00Z",
            "url": "https://github.com/facebook/react/pull/28000"
        }
    ],
    "pull_requests_count": 42,
    "issues": [...],
    "issues_count": 156,
    "commits": [
        {
            "sha": "abc1234",
            "message": "Fix: resolve edge case in reconciler",
            "author": "gaearon",
            "date": "2024-01-15T10:00:00Z"
        }
    ],
    "commits_count": 10,
    "summary": "GitHub Repository Summary for facebook/react:\n\nOpen Pull Requests (42):\n  - #28000: Fix memory leak...",
    "partial_failures": null
}
```

**Performance**: < 5 seconds (parallel API calls)

---

### daily_brief

Generate an aggregated morning summary.

**Parameters**: None required

**Result**
```python
{
    "brief": "Good morning! Here's your daily brief:\n\nWeather: It's 52°F and partly cloudy in Seattle...\n\nCalendar: You have 3 events today...\n\nEmails: You have 5 unread emails...",
    "sections": {
        "weather": { ... },
        "calendar": { ... },
        "email": { ... }
    },
    "generated_at": "2024-01-15T07:00:00Z"
}
```

---

### set_reminder

Schedule a reminder with natural language time parsing.

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task` | string | yes | What to remind about |
| `time` | string | yes | When to remind (natural language) |

**Supported time expressions**:
- `"in 30 minutes"`
- `"in 2 hours"`
- `"tomorrow at 9am"`
- `"next Monday at 3pm"`
- `"2024-01-20 at 10:00"`

**Result**
```python
{
    "reminder_id": "uuid-here",
    "task": "Call mom",
    "scheduled_time": "2024-01-15T15:00:00Z",
    "message": "Reminder set for 3:00 PM today: Call mom"
}
```

**Example**
```python
result = brain.execute_tool_call("set_reminder", {
    "task": "Call mom",
    "time": "tomorrow at 3pm"
})
print(result.result["message"])
```

---

### system_status

Report local machine health and performance metrics.

**Parameters**: None

**Result**
```python
{
    "cpu": {
        "usage_percent": 23.5,
        "cores": 8
    },
    "memory": {
        "total_gb": 16.0,
        "used_gb": 8.2,
        "usage_percent": 51.3
    },
    "disk": {
        "total_gb": 512.0,
        "used_gb": 234.5,
        "usage_percent": 45.8
    },
    "top_processes": [
        {
            "name": "python",
            "cpu_percent": 5.2,
            "memory_mb": 512.0
        }
    ],
    "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Configuration Reference

All configuration is loaded from environment variables. See `.env.example` for a complete template.

### Core Settings

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `LLM_API_KEY` | string | yes | - | Anthropic Claude API key |
| `LLM_MODEL` | string | no | `claude-sonnet-4-20250514` | Claude model to use |
| `SUPABASE_URL` | string | yes | - | PostgreSQL connection URL |
| `SUPABASE_KEY` | string | yes | - | Database password/key |
| `JWT_SECRET` | string | yes | - | Secret for JWT token signing |

### Voice Settings

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `VOICE_ENABLED` | boolean | no | `true` | Enable voice interface |
| `TTS_API_KEY` | string | no | - | ElevenLabs API key |
| `PORCUPINE_ACCESS_KEY` | string | no | - | Picovoice access key |
| `WAKE_WORD` | string | no | `Hey Jarvis` | Wake word phrase |
| `STT_MODEL` | string | no | `base` | Whisper model size |

**Whisper model options**: `tiny`, `base`, `small`, `medium`, `large`

### Skills API Keys

| Variable | Skill | Description |
|----------|-------|-------------|
| `BRAVE_API_KEY` | web_search | Brave Search API key |
| `WEATHER_API_KEY` | get_weather | WeatherAPI.com key |
| `GOOGLE_CALENDAR_CREDENTIALS` | manage_calendar | Path to credentials JSON |
| `GMAIL_CREDENTIALS` | manage_email | Path to credentials JSON |
| `HOME_ASSISTANT_URL` | smart_home | Home Assistant URL |
| `HOME_ASSISTANT_TOKEN` | smart_home | Long-lived access token |
| `GITHUB_TOKEN` | github_summary | Personal access token |

### System Settings

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `DASHBOARD_PORT` | integer | no | `3000` | Dashboard frontend port |
| `API_PORT` | integer | no | `5000` | Dashboard API port |
| `BRAIN_PORT` | integer | no | `8000` | Brain service port |
| `DB_PORT` | integer | no | `5432` | Database port |
| `LOG_LEVEL` | string | no | `INFO` | Logging level |
| `LOG_DIR` | string | no | `logs` | Log file directory |
| `TIMEZONE` | string | no | `UTC` | User timezone |
| `POSTGRES_PASSWORD` | string | no | - | PostgreSQL password (Docker) |

---

## Error Codes

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `400` | Bad Request — missing or invalid parameters |
| `401` | Unauthorized — missing or invalid JWT token |
| `404` | Not Found — resource does not exist |
| `500` | Internal Server Error — unexpected server error |

### Common Error Responses

**Missing Authorization**
```json
{ "error": "Missing Authorization header" }
```

**Invalid Token**
```json
{ "error": "Invalid or expired token" }
```

**Validation Error**
```json
{ "error": "Message is required" }
```

**Skill Not Configured**
```json
{
  "success": false,
  "error_message": "Brave API key not configured. Please set BRAVE_API_KEY in .env file."
}
```

**Skill Timeout**
```json
{
  "success": false,
  "error_message": "Web search timed out after 3 seconds. Please try again."
}
```

---

## Custom Skill Development

To add a new skill, extend the `Skill` base class:

```python
from jarvis.skills.base import Skill, SkillResult

class MySkill(Skill):
    def __init__(self):
        super().__init__()
        self._name = "my_skill"
        self._description = "What this skill does"
        self._parameters = {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Description of param1"
                }
            },
            "required": ["param1"]
        }

    def execute(self, **kwargs) -> SkillResult:
        import time
        start = time.time()

        is_valid, error = self.validate_parameters(**kwargs)
        if not is_valid:
            return SkillResult(
                success=False,
                result=None,
                error_message=error,
                execution_time_ms=int((time.time() - start) * 1000)
            )

        param1 = kwargs["param1"]
        # ... your logic here ...
        result = {"output": f"Processed: {param1}"}

        return SkillResult(
            success=True,
            result=result,
            execution_time_ms=int((time.time() - start) * 1000)
        )
```

Register it in `jarvis/skills/__init__.py`:

```python
from jarvis.skills.my_skill import MySkill
registry.register_skill(MySkill())
```
