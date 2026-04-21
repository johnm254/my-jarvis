# Implementation Plan: JARVIS Personal AI Assistant

## Overview

This implementation plan breaks down the JARVIS personal AI assistant into discrete coding tasks. The system will be built in Python with a phased approach: core infrastructure first, then skills, voice interface, automation, and finally the web dashboard. Each task builds incrementally, with checkpoints to ensure stability before moving forward.

## Tasks

- [x] 1. Set up project structure and core infrastructure
  - Create Python project with poetry/pip requirements
  - Set up Docker Compose configuration for all services (Brain, Memory, Voice, Dashboard, Supabase)
  - Create .env.example file with all required environment variables
  - Set up logging configuration (structured JSON logs, rotation)
  - Create base directory structure: `jarvis/brain/`, `jarvis/memory/`, `jarvis/skills/`, `jarvis/voice/`, `jarvis/hooks/`, `jarvis/dashboard/`
  - _Requirements: 19.1, 19.2, 19.5, 19.6_

- [ ]* 1.1 Write unit tests for project initialization
  - Test environment variable loading
  - Test logging configuration
  - _Requirements: 22.1_

- [ ] 2. Implement Configuration parser and formatter
  - [x] 2.1 Create Configuration dataclass with all required fields
    - Define Configuration dataclass with LLM settings, voice settings, memory settings, API keys, system settings
    - Implement field validation for required vs optional fields
    - _Requirements: 23.1, 23.6_
  
  - [x] 2.2 Implement Config_Parser for .env and YAML files
    - Write parser that reads .env files and YAML configuration files
    - Parse into Configuration object with type conversion
    - Validate required fields (llm_api_key, supabase_url, jwt_secret)
    - Return descriptive error messages for invalid configurations
    - _Requirements: 23.2, 23.3, 23.6_
  
  - [ ]* 2.3 Write property test for Configuration validation rejection
    - **Property 4: Configuration Validation Rejection**
    - **Validates: Requirements 23.3, 23.6**
    - Generate configs with missing required fields and invalid types
    - Verify all are rejected with descriptive error messages
    - Tag: `# Feature: jarvis-personal-ai-assistant, Property 4: Configuration Validation Rejection`
  
  - [x] 2.4 Implement Config_Formatter for Configuration objects
    - Write formatter that converts Configuration objects to .env format
    - Write formatter that converts Configuration objects to YAML format
    - Ensure output is valid and parseable
    - _Requirements: 23.4_
  
  - [ ]* 2.5 Write property test for Configuration round-trip preservation
    - **Property 3: Configuration Round-Trip Preservation**
    - **Validates: Requirements 23.5**
    - Generate random valid Configuration objects
    - Verify format(parse(format(config))) produces equivalent config
    - Test all field types: strings, integers, booleans, optional fields
    - Tag: `# Feature: jarvis-personal-ai-assistant, Property 3: Configuration Round-Trip Preservation`
  
  - [ ]* 2.6 Write unit tests for Config_Parser edge cases
    - Test missing files, malformed YAML, empty configs
    - Test partial configs with only some optional fields
    - _Requirements: 22.1_

- [x] 3. Checkpoint - Ensure configuration tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Set up Supabase database schema and Memory System
  - [x] 4.1 Create database schema initialization script
    - Write SQL script for conversations table with pgvector extension
    - Write SQL script for personal_profile table with JSONB fields
    - Write SQL script for episodic_memory table with timestamp index
    - Write SQL script for reminders table
    - Write SQL script for audit_log table
    - Create ivfflat index on conversations.embedding for vector search
    - _Requirements: 2.2, 2.3, 2.4, 2.8, 19.3_
  
  - [x] 4.2 Implement Memory System data models
    - Create ConversationExchange dataclass with session_id, timestamp, user_input, brain_response, tool_calls, confidence_score, embedding
    - Create PersonalProfile dataclass with user_id, first_name, timezone, preferences, habits, interests, communication_style, work_hours
    - Create EpisodicMemory dataclass with id, timestamp, interaction_type, context, action_taken, outcome, success
    - Create ToolCall dataclass with tool_name, parameters, result, execution_time_ms, success, error_message
    - _Requirements: 2.3, 2.4_
  
  - [x] 4.3 Implement MemorySystem class with Supabase integration
    - Implement store_conversation() method to insert into conversations table with vector embedding
    - Implement semantic_search() method using pgvector cosine similarity
    - Implement get_personal_profile() method to retrieve user preferences
    - Implement update_preference() method to update Personal_Profile
    - Implement log_episodic_memory() method to insert into episodic_memory table
    - Implement inject_context() method to generate context string from relevant memories
    - Add connection pooling and error handling
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.8_
  
  - [ ]* 4.4 Write unit tests for Memory System
    - Test store_conversation with valid data
    - Test semantic_search returns results within 500ms
    - Test get_personal_profile retrieves correct data
    - Test update_preference modifies profile correctly
    - Test inject_context formats memories correctly
    - _Requirements: 2.7, 22.1, 22.2_

- [ ] 5. Implement Brain (LLM reasoning engine)
  - [x] 5.1 Create Brain class with Claude API integration
    - Initialize Claude API client with API key from configuration
    - Implement conversation context management (last 20 exchanges)
    - Create system prompt template with memory injection placeholder
    - _Requirements: 1.1, 1.2_
  
  - [x] 5.2 Implement process_input() method
    - Accept user_input and session_id parameters
    - Call inject_memory_context() to load relevant memories
    - Build messages array with system prompt and conversation history
    - Call Claude API with tool definitions
    - Parse response and extract tool calls
    - Return BrainResponse with text, tool_calls, and confidence_score
    - _Requirements: 1.2, 1.5, 2.5_
  
  - [x] 5.3 Implement calculate_confidence() method
    - Analyze response text for uncertainty markers ("maybe", "possibly", "not sure")
    - Check if multiple alternatives were offered
    - Return confidence score between 0-100
    - _Requirements: 1.3_
  
  - [x] 5.4 Implement confidence-based uncertainty handling
    - If confidence_score < 70, prepend response with explicit uncertainty statement
    - Offer alternatives when confidence is low
    - _Requirements: 1.4_
  
  - [x] 5.5 Implement execute_tool_call() method with validation
    - Accept tool_name and parameters
    - Validate parameters against tool schema before invocation
    - Call skill from registry
    - Return ToolResult with success, result, error_message, execution_time_ms
    - _Requirements: 1.6, 1.7_
  
  - [ ]* 5.6 Write property test for tool call parameter validation
    - **Property 1: Tool Call Parameter Validation**
    - **Validates: Requirements 1.7**
    - Generate random tool calls with invalid/missing parameters
    - Verify all are rejected with appropriate error messages
    - Tag: `# Feature: jarvis-personal-ai-assistant, Property 1: Tool Call Parameter Validation`
  
  - [ ]* 5.7 Write unit tests for Brain
    - Test process_input with valid input
    - Test calculate_confidence returns 0-100
    - Test uncertainty handling when confidence < 70
    - Test tool validation rejects invalid parameters
    - Mock Claude API responses
    - _Requirements: 22.1, 22.2_

- [x] 6. Checkpoint - Ensure Brain and Memory tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement Skill registry and base Skill interface
  - [x] 7.1 Create Skill base class with MCP tool protocol
    - Define Skill abstract class with name, description, parameters (JSON schema)
    - Implement execute() abstract method
    - Implement validate_parameters() method using JSON schema validation
    - _Requirements: 1.6, 1.7_
  
  - [x] 7.2 Implement SkillRegistry class
    - Implement register_skill() method to add skills to registry
    - Implement get_skill() method to retrieve skill by name
    - Implement list_skills() method to return all registered skills
    - Implement get_tool_definitions() method for Claude API tool format
    - _Requirements: 1.5, 1.6_
  
  - [ ]* 7.3 Write unit tests for Skill registry
    - Test skill registration and retrieval
    - Test parameter validation with valid and invalid inputs
    - Test list_skills returns all registered skills
    - _Requirements: 22.1_

- [ ] 8. Implement core Skills (web search, weather, system status)
  - [x] 8.1 Implement web_search Skill
    - Create WebSearchSkill class extending Skill
    - Define parameters: query (required string)
    - Integrate with Brave API or Serper API
    - Return top 3-5 search results
    - Add timeout handling (3 seconds)
    - Return error message on failure
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 8.2 Implement get_weather Skill
    - Create GetWeatherSkill class extending Skill
    - Define parameters: location (optional string)
    - Integrate with Weather API
    - Return current conditions and 7-day forecast
    - Infer location from Personal_Profile if not specified
    - Add timeout handling (2 seconds)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x] 8.3 Implement system_status Skill
    - Create SystemStatusSkill class extending Skill
    - Use psutil to get CPU usage percentage
    - Get RAM usage in GB and percentage
    - Get disk usage in GB and percentage
    - List top 5 processes by resource consumption
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6_
  
  - [ ]* 8.4 Write unit tests for core Skills
    - Test web_search with mocked API responses
    - Test get_weather with mocked API responses
    - Test system_status returns valid data
    - Test timeout handling and error cases
    - _Requirements: 22.1_

- [ ] 9. Implement run_code Skill with sandboxing
  - [x] 9.1 Create RunCodeSkill class with sandbox environment
    - Define parameters: language (Python/JavaScript/Bash), code (string)
    - Implement Docker-based sandbox for code execution
    - Execute code with 30-second timeout
    - Capture stdout, stderr, and exit code
    - Return raw output and Brain-generated explanation
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_
  
  - [ ]* 9.2 Write unit tests for run_code Skill
    - Test Python code execution
    - Test JavaScript code execution
    - Test Bash code execution
    - Test timeout enforcement
    - Test error handling and stack traces
    - _Requirements: 22.1_

- [ ] 10. Implement calendar and email Skills with Google APIs
  - [x] 10.1 Implement manage_calendar Skill
    - Create ManageCalendarSkill class extending Skill
    - Define parameters: action (read/create/update), details (dict)
    - Integrate with Google Calendar API using MCP tool
    - Implement read action to retrieve events
    - Implement create action to create new events
    - Implement update action to modify existing events
    - Add confirmation prompt before creating/updating events
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_
  
  - [x] 10.2 Implement manage_email Skill
    - Create ManageEmailSkill class extending Skill
    - Define parameters: action (read/summarize/draft), filters (dict)
    - Integrate with Gmail API using MCP tool
    - Implement read action to retrieve messages
    - Implement summarize action with Brain-generated summary
    - Implement draft action to create draft messages
    - Require explicit confirmation before sending emails
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_
  
  - [ ]* 10.3 Write integration tests for calendar and email Skills
    - Test manage_calendar with mocked Google Calendar API
    - Test manage_email with mocked Gmail API
    - Test confirmation prompts
    - _Requirements: 22.3_

- [ ] 11. Implement smart home and GitHub Skills
  - [x] 11.1 Implement smart_home Skill
    - Create SmartHomeSkill class extending Skill
    - Define parameters: device (string), action (string)
    - Integrate with Home Assistant REST API
    - Send command to specified device
    - Return current device state after action
    - Return error message if device unavailable
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x] 11.2 Implement github_summary Skill
    - Create GitHubSummarySkill class extending Skill
    - Define parameters: repo (string)
    - Integrate with GitHub API
    - Retrieve open pull requests
    - Retrieve open issues
    - Retrieve last 10 commits
    - Generate Brain summary of repository activity
    - Add timeout handling (5 seconds)
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_
  
  - [ ]* 11.3 Write unit tests for smart home and GitHub Skills
    - Test smart_home with mocked Home Assistant API
    - Test github_summary with mocked GitHub API
    - Test error handling for unavailable devices
    - _Requirements: 22.1_

- [x] 12. Checkpoint - Ensure all Skills tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Implement daily_brief and reminder Skills
  - [x] 13.1 Implement daily_brief Skill
    - Create DailyBriefSkill class extending Skill
    - Orchestrate calls to get_weather, manage_calendar, manage_email, web_search
    - Aggregate weather, calendar events, email summary, news headlines
    - Generate cohesive spoken summary optimized for TTS
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [x] 13.2 Implement set_reminder Skill with time parsing
    - Create SetReminderSkill class extending Skill
    - Define parameters: task (string), time (string)
    - Implement natural language time parser for expressions like "in 30 minutes", "tomorrow at 9am", "next Monday"
    - Create cron-based scheduled task in reminders table
    - Store reminder in Memory System for persistence
    - _Requirements: 12.1, 12.2, 12.4, 12.5_
  
  - [ ]* 13.3 Write property test for time expression parsing
    - **Property 2: Time Expression Parsing**
    - **Validates: Requirements 12.4**
    - Generate various natural language time expressions
    - Verify all parse to valid future datetimes
    - Test expressions: "in X minutes/hours/days", "tomorrow at HH:MM", "next Monday"
    - Tag: `# Feature: jarvis-personal-ai-assistant, Property 2: Time Expression Parsing`
  
  - [ ]* 13.4 Write unit tests for daily_brief and set_reminder
    - Test daily_brief aggregates all data sources
    - Test time parser with various expressions
    - Test reminder creation and storage
    - _Requirements: 22.1_

- [ ] 14. Implement Voice Interface with wake word detection
  - [x] 14.1 Set up Whisper for local STT
    - Install and configure OpenAI Whisper model
    - Implement speech_to_text() method to convert audio bytes to text
    - Process audio locally without external API calls
    - Add error handling and fallback to text input
    - _Requirements: 3.1, 3.5, 3.7, 3.8_
  
  - [x] 14.2 Set up Porcupine for wake word detection
    - Install and configure Porcupine/Picovoice
    - Implement start_wake_word_detection() to listen for "Hey Jarvis"
    - Implement on_wake_word_detected() callback registration
    - Run wake word detection continuously in background thread
    - _Requirements: 3.3, 3.4_
  
  - [x] 14.3 Set up ElevenLabs for TTS
    - Integrate ElevenLabs API
    - Implement text_to_speech() method to convert text to audio bytes
    - Implement play_audio() method to output to speakers
    - _Requirements: 3.2, 3.6_
  
  - [x] 14.4 Wire Voice Interface to Brain
    - Connect wake word detection → STT → Brain → TTS pipeline
    - Implement voice interaction loop
    - Add fallback to CLI/Dashboard on voice failure
    - _Requirements: 3.7_
  
  - [ ]* 14.5 Write integration tests for Voice Interface
    - Test STT with sample audio files
    - Test TTS generates valid audio
    - Test wake word detection triggers listening mode
    - Test voice pipeline end-to-end
    - _Requirements: 22.4_

- [ ] 15. Implement Hooks Engine with scheduling
  - [x] 15.1 Create Hook base class and HooksEngine
    - Define Hook dataclass with id, name, schedule, callback
    - Implement HooksEngine class using APScheduler
    - Implement register_hook() method for time-based, event-based, and interval-based hooks
    - Implement execute_hook() method for manual execution
    - Implement list_active_hooks() method
    - Add hook persistence to database
    - _Requirements: 19.4_
  
  - [x] 15.2 Implement Morning Brief Hook
    - Create morning_brief_hook that executes daily_brief at 7:00 AM
    - Deliver output via TTS
    - Make time configurable via Dashboard settings
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_
  
  - [x] 15.3 Implement Preference Learning Hook
    - Create preference_learning_hook that executes after every conversation turn
    - Extract preferences, corrections, and new facts from interactions
    - Update Personal_Profile with extracted information
    - Store corrections to prevent repeating mistakes
    - _Requirements: 15.1, 15.2, 15.3, 15.4_
  
  - [x] 15.4 Implement Calendar Reminder Hook
    - Create calendar_reminder_hook that checks calendar every 5 minutes
    - Retrieve upcoming events within 15 minutes
    - Deliver voice reminder with event title, time, and context
    - Track delivered reminders to avoid duplicates
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_
  
  - [x] 15.5 Implement reminder delivery for set_reminder Skill
    - When reminder time arrives, deliver voice alert using TTS
    - Mark reminder as delivered in database
    - _Requirements: 12.3_
  
  - [ ]* 15.6 Write unit tests for Hooks Engine
    - Test hook registration and scheduling
    - Test time-based hook execution
    - Test event-based hook execution
    - Test hook persistence across restarts
    - _Requirements: 22.1_

- [x] 16. Checkpoint - Ensure Voice and Hooks tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 17. Implement CLI interface
  - [x] 17.1 Create CLI interface for text interaction
    - Implement command-line interface with input prompt
    - Connect CLI to Brain.process_input()
    - Display Brain responses in terminal
    - Add commands: /exit, /history, /clear, /help
    - _Requirements: 3.7_
  
  - [ ]* 17.2 Write integration tests for CLI
    - Test CLI input/output flow
    - Test CLI commands
    - _Requirements: 22.3_

- [ ] 18. Implement Web Dashboard backend API
  - [x] 18.1 Set up Flask/FastAPI backend with JWT authentication
    - Create Flask or FastAPI application
    - Implement JWT token generation and validation
    - Create authentication middleware
    - Implement POST /api/auth/login endpoint
    - _Requirements: 17.8, 18.4_
  
  - [x] 18.2 Implement conversation API endpoints
    - Implement GET /api/conversation/history endpoint
    - Implement POST /api/conversation/send endpoint with WebSocket support
    - Connect to Brain.process_input()
    - _Requirements: 17.2_
  
  - [x] 18.3 Implement memory API endpoints
    - Implement GET /api/memory/search endpoint
    - Implement PUT /api/memory/update endpoint
    - Implement DELETE /api/memory/delete endpoint
    - Connect to MemorySystem methods
    - _Requirements: 17.3_
  
  - [x] 18.4 Implement skills and settings API endpoints
    - Implement GET /api/skills/status endpoint
    - Implement GET /api/settings endpoint
    - Implement PUT /api/settings endpoint
    - _Requirements: 17.4, 17.6_
  
  - [x] 18.5 Implement audit log API endpoint
    - Implement GET /api/audit-log endpoint
    - Return audit log entries with pagination
    - _Requirements: 17.6, 18.6_
  
  - [ ]* 18.6 Write integration tests for Dashboard API
    - Test authentication flow
    - Test all API endpoints with valid JWT
    - Test unauthorized access returns 401
    - _Requirements: 22.3_

- [x] 19. Implement Web Dashboard frontend
  - [x] 19.1 Set up React project with Tailwind CSS
    - Create React application with TypeScript
    - Configure Tailwind CSS
    - Set up routing with React Router
    - Create layout components
    - _Requirements: 17.7_
  
  - [x] 19.2 Implement authentication page
    - Create login form with JWT authentication
    - Store JWT token in localStorage
    - Implement protected route wrapper
    - _Requirements: 17.8_
  
  - [x] 19.3 Implement Conversation Feed page
    - Create real-time conversation feed component
    - Display user inputs and Brain responses
    - Implement WebSocket connection for live updates
    - Add input form to send new messages
    - _Requirements: 17.2_
  
  - [x] 19.4 Implement Memory Browser page
    - Create memory search interface
    - Display stored memories with timestamps
    - Implement edit and delete functionality
    - Add pagination for large result sets
    - _Requirements: 17.3_
  
  - [x] 19.5 Implement Skills Status page
    - Display all registered skills
    - Show health status for each skill (connected/disconnected)
    - Display last execution time and success rate
    - _Requirements: 17.4_
  
  - [x] 19.6 Implement Daily Brief Card
    - Create dashboard card with weather, calendar, email summary
    - Auto-refresh every hour
    - Add manual refresh button
    - _Requirements: 17.5_
  
  - [x] 19.7 Implement Settings page
    - Create settings form for voice toggle, wake word, LLM model, API keys
    - Implement save functionality
    - Add validation for required fields
    - _Requirements: 17.6_
  
  - [ ]* 19.8 Write end-to-end tests for Dashboard
    - Test login flow
    - Test conversation interaction
    - Test memory browser operations
    - Test settings updates
    - _Requirements: 22.4_

- [ ] 20. Implement security and privacy controls
  - [x] 20.1 Implement environment variable management
    - Ensure all API keys loaded from environment variables
    - Verify no hardcoded credentials in source code
    - Create .env.example with all required variables
    - _Requirements: 18.1, 18.2_
  
  - [x] 20.2 Implement audit logging
    - Log all actions to audit_log table with timestamps, action types, outcomes
    - Include user_id, action details, and success status
    - _Requirements: 18.5, 18.6_
  
  - [x] 20.3 Implement data encryption at rest
    - Encrypt sensitive data in Memory System
    - Use encryption for stored API keys and credentials
    - _Requirements: 18.7_
  
  - [ ]* 20.4 Write security tests
    - Test no hardcoded credentials in source code
    - Test JWT authentication on all protected endpoints
    - Test audit log completeness
    - Test local STT processing (no audio sent externally)
    - _Requirements: 18.3, 18.4, 22.1_

- [ ] 21. Implement persona and interaction style
  - [x] 21.1 Configure Brain persona in system prompt
    - Address user as "Boss" or by first name from Personal_Profile
    - Provide concise responses by default
    - Fix errors without excessive apologies
    - Match user's communication style based on time of day
    - Confirm before irreversible actions
    - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5_

- [ ] 22. Implement proactive behavior and suggestions
  - [x] 22.1 Implement proactive suggestion logic
    - When confidence_score > 80, offer suggestions proactively
    - Analyze Personal_Profile for optimization opportunities
    - Generate weekly summary of learned preferences
    - Suggest new automations based on usage patterns
    - _Requirements: 20.1, 20.2, 20.3_
  
  - [x] 22.2 Implement confirmation prompts for irreversible actions
    - Require explicit confirmation before deleting data, sending emails
    - Add confirmation step in Brain before executing destructive actions
    - _Requirements: 20.4_
  
  - [x] 22.3 Implement energy level matching
    - Adjust communication style based on time of day
    - Technical and direct during work hours (9am-6pm)
    - Casual after 6pm based on Personal_Profile timezone
    - _Requirements: 20.5_

- [ ] 23. Checkpoint - Ensure Dashboard and security tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 24. Integration and system wiring
  - [x] 24.1 Wire all components together in main application
    - Initialize Configuration from environment
    - Initialize MemorySystem with Supabase connection
    - Initialize Brain with Claude API and MemorySystem
    - Initialize SkillRegistry and register all skills
    - Initialize HooksEngine and register all hooks
    - Initialize VoiceInterface with wake word detection
    - Initialize CLI interface
    - Initialize Dashboard backend and frontend
    - _Requirements: 19.1, 19.2, 19.3, 19.4_
  
  - [x] 24.2 Implement graceful error handling and fallbacks
    - Voice failures → fall back to text input
    - External API failures → return cached data when available
    - LLM failures → retry with exponential backoff (3 attempts)
    - Database failures → queue operations for retry
    - _Requirements: 3.7_
  
  - [ ]* 24.3 Write end-to-end integration tests
    - Test complete voice interaction flow: wake word → STT → Brain → TTS
    - Test complete dashboard interaction flow: login → conversation → memory browser
    - Test automated hooks: morning brief, calendar reminders
    - Test multi-turn conversations with context
    - _Requirements: 22.3, 22.4_

- [ ] 25. Performance optimization and monitoring
  - [x] 25.1 Optimize Memory System performance
    - Ensure semantic search < 500ms
    - Ensure context injection < 200ms
    - Ensure profile updates < 100ms
    - Add connection pooling for database
    - _Requirements: 2.7_
  
  - [x] 25.2 Optimize Skill execution performance
    - Ensure web_search < 3s
    - Ensure get_weather < 2s
    - Ensure github_summary < 5s
    - Add timeout handling for all external API calls
    - _Requirements: 4.4, 6.5, 10.6_
  
  - [x] 25.3 Implement monitoring and logging
    - Track conversation response time (p50, p95, p99)
    - Track skill execution time per skill
    - Track memory search latency
    - Track LLM API call success rate
    - Track voice interaction success rate
    - Track hook execution success rate
    - Set up structured JSON logging with rotation
    - _Requirements: 19.6_

- [ ] 26. Documentation and deployment preparation
  - [x] 26.1 Write comprehensive README
    - Document system architecture with diagram
    - Document setup guide with step-by-step instructions
    - Document API key requirements for all services
    - Document Docker Compose deployment
    - Document environment variables
    - _Requirements: 19.6_
  
  - [x] 26.2 Create deployment scripts
    - Finalize Docker Compose configuration
    - Create database initialization script
    - Create startup script for all services
    - Test deployment with `docker-compose up`
    - _Requirements: 19.1, 19.2_
  
  - [x] 26.3 Write API documentation
    - Document all Dashboard API endpoints
    - Document all Skill interfaces
    - Document configuration options
    - _Requirements: 19.6_

- [ ] 27. Final checkpoint - Complete test suite and deployment
  - [ ] 27.1 Run complete test suite
    - Run all unit tests
    - Run all property tests (100 iterations each)
    - Run all integration tests
    - Run all end-to-end tests
    - Verify code coverage > 80% for Brain and Memory modules
    - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.5_
  
  - [x] 27.2 Final deployment testing
    - Test complete deployment with `docker-compose up`
    - Verify all services start correctly
    - Verify database schema initialization
    - Verify all hooks load and execute
    - Test voice interaction end-to-end
    - Test dashboard access and functionality
    - _Requirements: 19.1, 19.2, 19.3, 19.4_
  
  - [x] 27.3 Final review and handoff
    - Review all code for security issues
    - Review all documentation for completeness
    - Ensure all requirements are implemented
    - Ensure all tests pass
    - Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation throughout implementation
- Property tests validate universal correctness properties from the design
- Unit tests validate specific examples and edge cases
- Integration tests validate component interactions
- End-to-end tests validate complete user workflows
- All property tests must be tagged with feature name and property number
- Python is the implementation language for all backend components
- React + TypeScript is used for the web dashboard frontend
