# Requirements Document

## Introduction

JARVIS is a full-stack, always-on intelligent personal AI assistant system that provides voice and text-activated interaction, persistent memory, proactive behaviors, and extensible skill-based capabilities. The system operates locally with cloud-based LLM reasoning, maintains context across sessions, learns user preferences over time, and automates routine tasks through scheduled hooks and intelligent suggestions.

## Glossary

- **JARVIS_System**: The complete personal AI assistant application including all subsystems
- **Brain**: The LLM-based reasoning engine responsible for conversation, tool selection, and decision-making
- **Memory_System**: The persistent storage layer including vector database, relational preferences, and episodic logs
- **Skill**: A discrete callable tool or function that performs a specific action (e.g., web search, calendar management)
- **Voice_Interface**: The speech-to-text and text-to-speech subsystem for audio interaction
- **Wake_Word**: The activation phrase "Hey Jarvis" that triggers voice listening mode
- **Dashboard**: The web-based user interface for monitoring and controlling JARVIS
- **Hook**: An automated behavior triggered by time, events, or system state
- **Session**: A continuous conversation context from user initiation to explicit termination
- **Confidence_Score**: A numerical value (0-100) indicating the Brain's certainty about a response or action
- **Daily_Brief**: An automated morning summary of weather, calendar, emails, and news
- **Personal_Profile**: The learned collection of user preferences, habits, timezone, and interests
- **Tool_Call**: An invocation of a Skill by the Brain to perform an action
- **Memory_Injection**: The process of loading relevant past context into the system prompt at session start
- **Episodic_Memory**: Time-stamped logs of past interactions with outcomes
- **Vector_Database**: Supabase pgvector storage for semantic memory search
- **STT**: Speech-to-text conversion subsystem
- **TTS**: Text-to-speech conversion subsystem
- **MCP_Tool**: Model Context Protocol tool interface for skill integration

## Requirements

### Requirement 1: LLM-Based Reasoning Engine

**User Story:** As a user, I want JARVIS to understand natural language and reason about my requests, so that I can interact conversationally without rigid command syntax.

#### Acceptance Criteria

1. THE Brain SHALL use Claude API (claude-sonnet-4-20250514) as the reasoning engine
2. WHEN a user submits a request, THE Brain SHALL maintain multi-turn conversation context within the current Session
3. WHEN the Brain selects an action, THE Brain SHALL generate a Confidence_Score between 0 and 100
4. IF the Confidence_Score is below 70, THEN THE Brain SHALL explicitly state uncertainty and offer alternatives
5. WHEN multiple Skills are available for a task, THE Brain SHALL select the most appropriate Skill based on context
6. THE Brain SHALL support Tool_Call architecture where each Skill is invocable as a function
7. FOR ALL Tool_Calls, THE Brain SHALL validate required parameters before invocation

### Requirement 2: Persistent Memory System

**User Story:** As a user, I want JARVIS to remember past conversations and learn my preferences, so that interactions become more personalized over time.

#### Acceptance Criteria

1. THE Memory_System SHALL store the last 20 conversation exchanges as short-term memory within a Session
2. THE Memory_System SHALL store all conversation history in the Vector_Database for semantic search
3. THE Memory_System SHALL maintain a Personal_Profile table with user preferences, habits, timezone, and interests
4. THE Memory_System SHALL log all interactions as Episodic_Memory with timestamps and outcomes
5. WHEN a Session starts, THE Memory_System SHALL perform Memory_Injection of relevant past context into the system prompt
6. WHEN a user corrects the Brain, THE Memory_System SHALL store the correction and associate it with the original context
7. FOR ALL stored memories, semantic search and retrieval SHALL return results within 500ms
8. THE Memory_System SHALL use Supabase pgvector for vector storage and PostgreSQL for relational data

### Requirement 3: Voice Interaction Capabilities

**User Story:** As a user, I want to interact with JARVIS using voice commands, so that I can use the assistant hands-free.

#### Acceptance Criteria

1. THE Voice_Interface SHALL use OpenAI Whisper running locally for STT conversion
2. THE Voice_Interface SHALL use ElevenLabs API for TTS conversion
3. WHEN the Wake_Word "Hey Jarvis" is detected, THE Voice_Interface SHALL activate listening mode
4. THE Voice_Interface SHALL use Porcupine or Picovoice for Wake_Word detection
5. WHEN audio input is received, THE STT SHALL process it locally without sending audio to external services
6. WHEN the Brain generates a response, THE TTS SHALL convert it to natural speech output
7. IF voice input fails, THEN THE JARVIS_System SHALL fall back to text input via CLI or Dashboard
8. THE Voice_Interface SHALL operate offline for STT processing

### Requirement 4: Web Search Skill

**User Story:** As a user, I want JARVIS to search the web for current information, so that I can get real-time answers without opening a browser.

#### Acceptance Criteria

1. THE JARVIS_System SHALL provide a web_search Skill that accepts a query parameter
2. WHEN web_search is invoked, THE Skill SHALL use Brave API or Serper API for search execution
3. WHEN search results are returned, THE Brain SHALL summarize the top 3-5 results
4. THE web_search Skill SHALL return results within 3 seconds under normal network conditions
5. IF the search fails, THEN THE Skill SHALL return an error message with the failure reason

### Requirement 5: Code Execution Skill

**User Story:** As a user, I want JARVIS to execute code snippets and explain the output, so that I can quickly test ideas without switching contexts.

#### Acceptance Criteria

1. THE JARVIS_System SHALL provide a run_code Skill that accepts language and code parameters
2. THE run_code Skill SHALL support Python, JavaScript, and Bash execution
3. WHEN code is executed, THE Skill SHALL return both raw output and a Brain-generated explanation
4. THE run_code Skill SHALL execute code in an isolated sandbox environment
5. THE run_code Skill SHALL enforce a 30-second timeout for code execution
6. IF code execution fails, THEN THE Skill SHALL return the error message and stack trace

### Requirement 6: Weather Information Skill

**User Story:** As a user, I want JARVIS to provide weather information, so that I can plan my day without checking weather apps.

#### Acceptance Criteria

1. THE JARVIS_System SHALL provide a get_weather Skill that accepts a location parameter
2. WHEN get_weather is invoked, THE Skill SHALL return current weather conditions
3. WHEN get_weather is invoked, THE Skill SHALL return a 7-day forecast
4. WHERE location is not specified, THE Skill SHALL use the user's timezone and Personal_Profile to infer location
5. THE get_weather Skill SHALL return results within 2 seconds under normal network conditions

### Requirement 7: Calendar Management Skill

**User Story:** As a user, I want JARVIS to manage my calendar, so that I can create, read, and update events through conversation.

#### Acceptance Criteria

1. THE JARVIS_System SHALL provide a manage_calendar Skill that accepts action and details parameters
2. THE manage_calendar Skill SHALL support read, create, and update actions
3. WHEN manage_calendar is invoked with read action, THE Skill SHALL retrieve events from Google Calendar API
4. WHEN manage_calendar is invoked with create action, THE Skill SHALL create a new event in Google Calendar
5. WHEN manage_calendar is invoked with update action, THE Skill SHALL modify an existing event in Google Calendar
6. THE manage_calendar Skill SHALL use Google Calendar MCP tool for API integration
7. BEFORE creating or updating events, THE Brain SHALL confirm details with the user

### Requirement 8: Email Management Skill

**User Story:** As a user, I want JARVIS to manage my email, so that I can read summaries, filter messages, and draft replies without opening my email client.

#### Acceptance Criteria

1. THE JARVIS_System SHALL provide a manage_email Skill that accepts action and filters parameters
2. THE manage_email Skill SHALL support read, summarize, and draft actions
3. WHEN manage_email is invoked with read action, THE Skill SHALL retrieve messages from Gmail API
4. WHEN manage_email is invoked with summarize action, THE Brain SHALL generate a concise summary of unread emails
5. WHEN manage_email is invoked with draft action, THE Skill SHALL create a draft message in Gmail
6. THE manage_email Skill SHALL use Gmail MCP tool for API integration
7. BEFORE sending any email, THE Brain SHALL require explicit user confirmation

### Requirement 9: Smart Home Control Skill

**User Story:** As a user, I want JARVIS to control my smart home devices, so that I can manage my environment through voice or text commands.

#### Acceptance Criteria

1. THE JARVIS_System SHALL provide a smart_home Skill that accepts device and action parameters
2. THE smart_home Skill SHALL integrate with Home Assistant via REST API
3. WHEN smart_home is invoked, THE Skill SHALL send the appropriate command to the specified device
4. THE smart_home Skill SHALL return the current state of the device after action execution
5. IF the device is unavailable, THEN THE Skill SHALL return an error message indicating the device status

### Requirement 10: GitHub Summary Skill

**User Story:** As a user, I want JARVIS to summarize GitHub repository activity, so that I can stay updated on open PRs, issues, and recent commits.

#### Acceptance Criteria

1. THE JARVIS_System SHALL provide a github_summary Skill that accepts a repo parameter
2. WHEN github_summary is invoked, THE Skill SHALL retrieve open pull requests from GitHub API
3. WHEN github_summary is invoked, THE Skill SHALL retrieve open issues from GitHub API
4. WHEN github_summary is invoked, THE Skill SHALL retrieve the last 10 commits from GitHub API
5. THE Brain SHALL generate a concise summary of the repository activity
6. THE github_summary Skill SHALL return results within 5 seconds under normal network conditions

### Requirement 11: Daily Brief Skill

**User Story:** As a user, I want JARVIS to provide a morning summary of my day, so that I can start each day informed without manually checking multiple sources.

#### Acceptance Criteria

1. THE JARVIS_System SHALL provide a daily_brief Skill that requires no parameters
2. WHEN daily_brief is invoked, THE Skill SHALL aggregate weather, calendar events, email summary, and news headlines
3. THE daily_brief Skill SHALL invoke get_weather, manage_calendar, manage_email, and web_search Skills
4. THE Brain SHALL generate a cohesive spoken summary of all aggregated information
5. THE daily_brief output SHALL be optimized for TTS delivery with natural pacing

### Requirement 12: Reminder Management Skill

**User Story:** As a user, I want JARVIS to set reminders, so that I receive timely notifications for tasks and events.

#### Acceptance Criteria

1. THE JARVIS_System SHALL provide a set_reminder Skill that accepts task and time parameters
2. WHEN set_reminder is invoked, THE Skill SHALL create a cron-based scheduled task
3. WHEN the reminder time arrives, THE JARVIS_System SHALL deliver a voice alert using TTS
4. THE set_reminder Skill SHALL support natural language time expressions (e.g., "in 30 minutes", "tomorrow at 9am")
5. THE JARVIS_System SHALL store active reminders in the Memory_System for persistence across restarts

### Requirement 13: System Status Skill

**User Story:** As a user, I want JARVIS to report system health, so that I can monitor my machine's performance without opening system tools.

#### Acceptance Criteria

1. THE JARVIS_System SHALL provide a system_status Skill that requires no parameters
2. WHEN system_status is invoked, THE Skill SHALL report CPU usage percentage
3. WHEN system_status is invoked, THE Skill SHALL report RAM usage in GB and percentage
4. WHEN system_status is invoked, THE Skill SHALL report disk usage in GB and percentage
5. WHEN system_status is invoked, THE Skill SHALL list running processes with high resource consumption
6. THE system_status Skill SHALL execute on the local machine where JARVIS is running

### Requirement 14: Automated Morning Brief Hook

**User Story:** As a user, I want JARVIS to automatically deliver a morning brief, so that I start each day informed without manual requests.

#### Acceptance Criteria

1. THE JARVIS_System SHALL execute the daily_brief Skill automatically at 7:00 AM local time
2. THE Hook SHALL run daily without requiring user initiation
3. WHEN the morning brief Hook executes, THE JARVIS_System SHALL deliver the output via TTS
4. THE Hook SHALL persist across system restarts
5. THE Hook SHALL be configurable via the Dashboard for custom time settings

### Requirement 15: Preference Learning Hook

**User Story:** As a user, I want JARVIS to learn from every interaction, so that the assistant becomes more personalized over time.

#### Acceptance Criteria

1. WHEN an interaction is logged to Episodic_Memory, THE JARVIS_System SHALL extract preferences, corrections, and new facts
2. THE JARVIS_System SHALL update the Personal_Profile with extracted information
3. WHEN a user corrects the Brain, THE JARVIS_System SHALL store the correction and never repeat the same mistake
4. THE learning Hook SHALL execute after every conversation turn
5. THE JARVIS_System SHALL identify patterns in user behavior and suggest new automations weekly

### Requirement 16: Calendar Reminder Hook

**User Story:** As a user, I want JARVIS to remind me of upcoming calendar events, so that I never miss important meetings or appointments.

#### Acceptance Criteria

1. THE JARVIS_System SHALL check the calendar every 5 minutes for upcoming events
2. WHEN an event is scheduled within 15 minutes, THE JARVIS_System SHALL deliver a voice reminder
3. THE reminder SHALL include the event title, time, and any relevant context from the event description
4. THE Hook SHALL not repeat reminders for the same event
5. THE Hook SHALL persist across system restarts

### Requirement 17: Web Dashboard Interface

**User Story:** As a user, I want a web dashboard to monitor and control JARVIS, so that I can manage the assistant visually when voice interaction is not convenient.

#### Acceptance Criteria

1. THE Dashboard SHALL be accessible at localhost:3000
2. THE Dashboard SHALL display a real-time conversation feed showing all user inputs and Brain responses
3. THE Dashboard SHALL provide a memory browser for viewing, editing, and deleting stored memories
4. THE Dashboard SHALL display a skills status panel showing which Skills are connected and healthy
5. THE Dashboard SHALL display a daily brief card with weather, calendar, and email summary
6. THE Dashboard SHALL provide a settings page for configuring voice toggle, Wake_Word, LLM model, and API keys
7. THE Dashboard SHALL be built using React and Tailwind CSS
8. THE Dashboard SHALL require JWT authentication for access

### Requirement 18: Security and Privacy Controls

**User Story:** As a user, I want JARVIS to protect my sensitive data, so that my personal information and credentials remain secure.

#### Acceptance Criteria

1. THE JARVIS_System SHALL store all API keys and sensitive credentials in environment variables
2. THE JARVIS_System SHALL never hardcode credentials in source code
3. THE STT SHALL process audio locally without sending audio data to external services
4. THE Dashboard SHALL require JWT authentication before granting access
5. THE JARVIS_System SHALL maintain an audit log of all actions taken on behalf of the user
6. THE audit log SHALL include timestamps, action types, and outcomes
7. THE JARVIS_System SHALL encrypt sensitive data in the Memory_System at rest

### Requirement 19: System Deployment and Initialization

**User Story:** As a user, I want to start JARVIS with a single command, so that deployment is simple and reproducible.

#### Acceptance Criteria

1. THE JARVIS_System SHALL start with the command "docker-compose up"
2. THE Docker Compose configuration SHALL include all required services: Brain, Memory_System, Voice_Interface, Dashboard, and Skill servers
3. WHEN the system starts, THE JARVIS_System SHALL initialize the Vector_Database schema if not present
4. WHEN the system starts, THE JARVIS_System SHALL load all configured Hooks
5. THE JARVIS_System SHALL provide a .env.example file documenting all required environment variables
6. THE JARVIS_System SHALL include a README with setup guide, API key requirements, and architecture diagram

### Requirement 20: Proactive Behavior and Suggestions

**User Story:** As a user, I want JARVIS to proactively suggest actions and optimizations, so that the assistant anticipates my needs rather than only reacting to requests.

#### Acceptance Criteria

1. WHEN the Confidence_Score for a suggestion exceeds 80, THE Brain SHALL proactively offer the suggestion without being asked
2. THE JARVIS_System SHALL analyze usage patterns in the Personal_Profile to identify optimization opportunities
3. THE JARVIS_System SHALL generate a weekly summary of learned preferences and suggest new automations
4. BEFORE taking any irreversible action (deleting data, sending emails), THE Brain SHALL require explicit user confirmation
5. THE Brain SHALL match user energy levels: technical and direct during work hours (9am-6pm), casual after 6pm based on Personal_Profile timezone

### Requirement 21: Persona and Interaction Style

**User Story:** As a user, I want JARVIS to have a consistent personality, so that interactions feel natural and aligned with my preferences.

#### Acceptance Criteria

1. THE Brain SHALL address the user as "Boss" or by first name from Personal_Profile
2. THE Brain SHALL provide concise responses by default and expand only when explicitly asked
3. WHEN the Brain makes an error, THE Brain SHALL fix the issue without excessive apologies
4. THE Brain SHALL match the user's communication style: technical during work hours, casual after 6pm
5. THE Brain SHALL confirm before taking irreversible actions

### Requirement 22: Testing and Quality Assurance

**User Story:** As a developer, I want comprehensive test coverage, so that JARVIS is reliable and maintainable.

#### Acceptance Criteria

1. THE JARVIS_System SHALL include unit tests for all Skills with independent test execution
2. THE test suite SHALL achieve greater than 80% code coverage for Brain and Memory_System modules
3. THE JARVIS_System SHALL include integration tests for Tool_Call workflows
4. THE JARVIS_System SHALL include end-to-end tests for voice interaction flows
5. FOR ALL Skills that parse and format data, THE test suite SHALL include round-trip property tests verifying parse-then-format-then-parse produces equivalent output

### Requirement 23: Configuration Parser and Formatter

**User Story:** As a user, I want JARVIS to correctly parse and format configuration files, so that settings are reliably loaded and saved.

#### Acceptance Criteria

1. THE JARVIS_System SHALL provide a Config_Parser that parses .env and YAML configuration files
2. WHEN a valid configuration file is provided, THE Config_Parser SHALL parse it into a Configuration object
3. WHEN an invalid configuration file is provided, THE Config_Parser SHALL return a descriptive error message
4. THE JARVIS_System SHALL provide a Config_Formatter that formats Configuration objects back into valid configuration files
5. FOR ALL valid Configuration objects, parsing then formatting then parsing SHALL produce an equivalent object (round-trip property)
6. THE Config_Parser SHALL validate required fields and data types before accepting configuration

