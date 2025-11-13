# VectorTutor - Architecture Documentation

## Overview

VectorTutor is a 5-agent AI system built with Streamlit and Groq API. It provides a comprehensive learning platform that processes PDF documents and generates study materials through specialized AI agents.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                       │
│              (Single-page Modern Interface)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent Layer                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Reader  │  │Flashcard  │  │   Quiz   │  │ Planner  │ │
│  │  Agent   │  │  Agent    │  │  Agent  │  │  Agent   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│                                                           │
│  ┌──────────┐                                            │
│  │   Chat   │                                            │
│  │  Agent   │                                            │
│  └──────────┘                                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Knowledge Memory Module (SQLite)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Documents   │  │  Flashcards   │  │    Quizzes   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │Quiz Attempts │  │Revision Plans │  │Chat History  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Utility Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Groq Client  │  │   Memory     │  │  PDF Utils   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              External Services                              │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │  Groq API    │  │  SQLite DB   │                       │
│  │ (llama-3.3)  │  │              │                       │
│  └──────────────┘  └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. UI Layer (Streamlit)

**File:** `app.py`

**Responsibilities:**
- Single-page modern interface with expandable sections
- User interaction and input handling
- Display of agent outputs
- Session state management
- Navigation and routing

**Key Features:**
- Collapsible sidebar navigation
- Modern CSS styling with gradients and cards
- Real-time updates using Streamlit's reactive framework
- Responsive layout with columns and containers

### 2. Agent Layer

All agents inherit a common pattern:
- Initialize with `GroqClient` and `KnowledgeMemory`
- Process document content using Groq API
- Store results in Knowledge Memory
- Return structured data to UI

#### 2.1 Reader Agent

**File:** `agents/reader_agent.py`

**Purpose:** Extract and structure PDF content

**Workflow:**
```
PDF Upload → Extract Text (PyMuPDF) → Structure with Groq → Store in Memory
```

**Key Methods:**
- `process_pdf(pdf_path, filename)`: Main entry point
  - Extracts raw text using PyMuPDF
  - Extracts metadata (title, author, pages, etc.)
  - Structures content using Groq API
  - Stores in `documents` table
  - Returns document ID and structured data

- `_structure_content(text)`: Uses Groq to analyze and organize content
  - Extracts main topics
  - Identifies key concepts
  - Generates summary
  - Returns structured analysis

**Data Flow:**
```
PDF → Raw Text → Groq Analysis → Structured Content → SQLite
```

#### 2.2 Flashcard Agent

**File:** `agents/flashcard_agent.py`

**Purpose:** Generate Q&A flashcards for active recall

**Workflow:**
```
Document Content → Groq Generation → Q&A Pairs → Store in Memory
```

**Key Methods:**
- `generate_flashcards(document_id, num_flashcards, topic)`: 
  - Retrieves document from memory
  - Generates flashcards using Groq with structured prompts
  - Validates and stores flashcards
  - Returns list of flashcard objects

- `_generate_with_groq(content, num_flashcards, topic)`:
  - Creates prompt for flashcard generation
  - Requests JSON response from Groq
  - Parses and validates flashcards
  - Handles fallback if JSON parsing fails

**Data Structure:**
```json
{
  "question": "What is...?",
  "answer": "It is...",
  "topic": "Topic Name",
  "difficulty": "easy|medium|hard"
}
```

#### 2.3 Quiz Agent

**File:** `agents/quiz_agent.py`

**Purpose:** Create adaptive multiple-choice questions

**Workflow:**
```
Document Content → Difficulty-based Generation → MCQs → Store in Memory
```

**Key Methods:**
- `generate_quiz(document_id, num_questions, difficulty, topic)`:
  - Retrieves document content
  - Generates questions by difficulty level
  - Creates mix of easy/medium/hard if not specified
  - Stores questions in `quizzes` table

- `_generate_by_difficulty(content, count, difficulty, topic)`:
  - Creates difficulty-specific prompts
  - Generates 4-option MCQs
  - Validates question structure
  - Returns validated questions

- `submit_answer(quiz_id, user_answer)`:
  - Records attempt in `quiz_attempts` table
  - Returns correctness boolean

**Data Structure:**
```json
{
  "question": "Question text?",
  "options": ["A", "B", "C", "D"],
  "correct_answer": 0,
  "difficulty": "easy|medium|hard",
  "topic": "Topic Name"
}
```

#### 2.4 Planner Agent

**File:** `agents/planner_agent.py`

**Purpose:** Build personalized revision schedules

**Workflow:**
```
Document + Topics + Constraints → Groq Planning → Schedule → Store in Memory
```

**Key Methods:**
- `create_revision_plan(document_id, days_until_exam, hours_per_day, focus_topics)`:
  - Extracts topics from document metadata or flashcards
  - Gets performance statistics
  - Generates plan using Groq
  - Stores plan in `revision_plans` table

- `_generate_plan_with_groq(document, topics, days, hours_per_day, performance)`:
  - Creates comprehensive planning prompt
  - Includes performance data for adaptive planning
  - Generates day-by-day schedule
  - Adds dates and activities

**Data Structure:**
```json
{
  "plan_name": "7-Day Revision Plan",
  "total_days": 7,
  "hours_per_day": 2.0,
  "schedule": [
    {
      "day": 1,
      "date": "2024-01-01",
      "topics": ["Topic 1", "Topic 2"],
      "activities": [
        {
          "type": "reading",
          "description": "Read Chapter 1",
          "duration_minutes": 60
        }
      ],
      "notes": "Day 1 notes"
    }
  ],
  "tips": ["Tip 1", "Tip 2"]
}
```

#### 2.5 Chat Agent

**File:** `agents/chat_agent.py`

**Purpose:** Answer questions and summarize notes

**Workflow:**
```
User Question + Document Context → Groq Answer → Store in History
```

**Key Methods:**
- `answer_question(document_id, question, use_history)`:
  - Retrieves document content
  - Optionally includes chat history for context
  - Generates answer using Groq
  - Stores Q&A in `chat_history` table

- `summarize_notes(document_id, focus_topic)`:
  - Retrieves document content
  - Generates comprehensive summary
  - Optionally focuses on specific topic
  - Returns formatted summary text

**Context Management:**
- Uses first 10,000 characters of document for context
- Includes last 3 Q&A pairs for conversation continuity
- Stores all interactions for future reference

### 3. Knowledge Memory Module

**File:** `utils/memory.py`

**Purpose:** Centralized data storage and retrieval

**Database Schema:**

#### Documents Table
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    uploaded_at TIMESTAMP
)
```

#### Flashcards Table
```sql
CREATE TABLE flashcards (
    id INTEGER PRIMARY KEY,
    document_id INTEGER,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    topic TEXT,
    difficulty TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id)
)
```

#### Quizzes Table
```sql
CREATE TABLE quizzes (
    id INTEGER PRIMARY KEY,
    document_id INTEGER,
    question TEXT NOT NULL,
    options TEXT NOT NULL,  -- JSON array
    correct_answer INTEGER,
    difficulty TEXT,
    topic TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id)
)
```

#### Quiz Attempts Table
```sql
CREATE TABLE quiz_attempts (
    id INTEGER PRIMARY KEY,
    quiz_id INTEGER,
    user_answer INTEGER,
    is_correct INTEGER,
    attempted_at TIMESTAMP,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
)
```

#### Revision Plans Table
```sql
CREATE TABLE revision_plans (
    id INTEGER PRIMARY KEY,
    document_id INTEGER,
    plan_data TEXT NOT NULL,  -- JSON object
    created_at TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id)
)
```

#### Chat History Table
```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY,
    document_id INTEGER,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    asked_at TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id)
)
```

**Key Methods:**
- `add_document()`: Store new PDF document
- `get_document()`: Retrieve document by ID
- `add_flashcard()`: Store flashcard
- `get_flashcards()`: Retrieve flashcards (optionally filtered)
- `add_quiz()`: Store quiz question
- `get_quizzes()`: Retrieve quizzes (optionally filtered by difficulty)
- `record_quiz_attempt()`: Track user performance
- `get_performance_stats()`: Calculate accuracy and statistics
- `add_revision_plan()`: Store revision schedule
- `get_revision_plans()`: Retrieve plans
- `add_chat_message()`: Store Q&A
- `get_chat_history()`: Retrieve conversation history

### 4. Utility Layer

#### 4.1 Groq Client

**File:** `utils/groq_client.py`

**Purpose:** Wrapper for Groq API interactions

**Features:**
- Handles API key management
- Manages proxy environment variables
- Provides text generation with temperature control
- Provides JSON generation for structured outputs
- Error handling and retry logic

**Key Methods:**
- `generate(prompt, system_prompt, temperature, max_tokens)`: Text generation
- `generate_json(prompt, system_prompt, temperature)`: Structured JSON output

**Model Configuration:**
- Model: `llama-3.3-70b-versatile`
- Default temperature: 0.7 (text), 0.3 (JSON)
- Max tokens: 4096

#### 4.2 PDF Utils

**File:** `utils/pdf_utils.py`

**Purpose:** PDF text extraction

**Key Methods:**
- `extract_text_from_pdf(pdf_path)`: Extract all text
- `extract_pdf_metadata(pdf_path)`: Get PDF metadata
- `extract_text_by_pages(pdf_path, max_chars)`: Chunked extraction

**Library:** PyMuPDF (fitz)

## Data Flow

### Document Processing Flow

```
1. User uploads PDF
   ↓
2. Reader Agent extracts text (PyMuPDF)
   ↓
3. Reader Agent structures content (Groq API)
   ↓
4. Store in documents table (SQLite)
   ↓
5. Display structured content in UI
```

### Flashcard Generation Flow

```
1. User selects document
   ↓
2. Flashcard Agent retrieves document content
   ↓
3. Generate flashcards using Groq API
   ↓
4. Store in flashcards table
   ↓
5. Display flashcards in UI
```

### Quiz Generation Flow

```
1. User selects document and difficulty
   ↓
2. Quiz Agent retrieves document content
   ↓
3. Generate MCQs by difficulty (Groq API)
   ↓
4. Store in quizzes table
   ↓
5. User takes quiz
   ↓
6. Record attempts in quiz_attempts table
   ↓
7. Calculate and display performance
```

### Chat Flow

```
1. User asks question
   ↓
2. Chat Agent retrieves document content
   ↓
3. Include chat history for context
   ↓
4. Generate answer (Groq API)
   ↓
5. Store in chat_history table
   ↓
6. Display answer in UI
```

## Agent Communication Pattern

All agents follow this communication pattern:

```
Agent → Knowledge Memory (Read)
   ↓
Agent → Groq API (Process)
   ↓
Agent → Knowledge Memory (Write)
   ↓
Agent → UI (Display)
```

**Shared Resources:**
- All agents read from same `documents` table
- All agents write to their respective tables
- Performance data shared across agents
- Chat history used for context

## Error Handling

### Groq API Errors
- Try-catch blocks in all agent methods
- Fallback to simpler generation methods
- User-friendly error messages
- Graceful degradation

### PDF Processing Errors
- Validation of PDF format
- Error messages for corrupted files
- Support for password-protected PDFs (future)

### Database Errors
- Connection error handling
- Transaction rollback on failures
- Data validation before insertion

## Performance Considerations

### Content Chunking
- Documents truncated to ~15,000 chars for processing
- PDFs split into manageable chunks
- Context windows optimized for Groq API

### Caching Strategy
- Session state caching for agents
- Document content cached after first read
- Quiz questions cached during session

### Database Optimization
- Indexed foreign keys
- Efficient queries with WHERE clauses
- Limited result sets with LIMIT

## Security Considerations

### API Key Management
- Environment variable storage
- No hardcoded credentials
- .env file in .gitignore

### Data Privacy
- Local SQLite database (no cloud storage)
- User data stored locally
- No external data transmission except Groq API

### Input Validation
- PDF file type validation
- SQL injection prevention (parameterized queries)
- Content length limits

## Extension Points

### Adding New Agents
1. Create agent class in `agents/` directory
2. Initialize with `GroqClient` and `KnowledgeMemory`
3. Add methods following existing patterns
4. Create UI section in `app.py`
5. Add database tables if needed

### Adding New Features
1. Extend Knowledge Memory with new tables
2. Add agent methods for new functionality
3. Update UI with new sections
4. Update documentation

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| UI Framework | Streamlit | >=1.28.0 |
| AI API | Groq | >=0.4.0 |
| Model | llama-3.3-70b-versatile | - |
| PDF Processing | PyMuPDF | >=1.23.0 |
| Database | SQLite | Built-in |
| HTTP Client | httpx | >=0.24.0 |
| Environment | python-dotenv | >=1.0.0 |

## Deployment Considerations

### Local Deployment
- Single-file database (SQLite)
- No external dependencies except Groq API
- Easy to run with `streamlit run app.py`

### Production Deployment
- Consider PostgreSQL for multi-user support
- Add authentication/authorization
- Implement rate limiting
- Add monitoring and logging
- Consider containerization (Docker)

## Future Enhancements

### Potential Improvements
1. **Multi-user support**: User authentication and data isolation
2. **Advanced chunking**: Better document segmentation
3. **Vector embeddings**: Semantic search capabilities
4. **Export features**: PDF/JSON export of study materials
5. **Spaced repetition**: Algorithm-based flashcard scheduling
6. **Collaboration**: Share flashcards and quizzes
7. **Mobile app**: Native mobile interface
8. **Offline mode**: Local LLM support

## Troubleshooting Guide

### Common Issues

**Issue:** Groq API initialization error
- **Solution:** Check API key in .env file
- **Solution:** Verify proxy settings

**Issue:** PDF extraction fails
- **Solution:** Ensure PDF is not password-protected
- **Solution:** Check PyMuPDF installation

**Issue:** JSON parsing errors
- **Solution:** Agent falls back to simpler generation
- **Solution:** Check Groq API response format

**Issue:** Database locked
- **Solution:** Ensure only one instance running
- **Solution:** Check file permissions

## API Reference

### GroqClient

```python
client = GroqClient(api_key="your_key")
response = client.generate(
    prompt="Your prompt",
    system_prompt="System instructions",
    temperature=0.7,
    max_tokens=4096
)
```

### KnowledgeMemory

```python
memory = KnowledgeMemory(db_path="vectortutor.db")
doc_id = memory.add_document(filename, content, metadata)
document = memory.get_document(doc_id)
```

### ReaderAgent

```python
agent = ReaderAgent(groq_client, memory)
result = agent.process_pdf(pdf_path, filename)
```

### FlashcardAgent

```python
agent = FlashcardAgent(groq_client, memory)
flashcards = agent.generate_flashcards(doc_id, num=10, topic="Physics")
```

### QuizAgent

```python
agent = QuizAgent(groq_client, memory)
quizzes = agent.generate_quiz(doc_id, num=10, difficulty="medium")
```

### PlannerAgent

```python
agent = PlannerAgent(groq_client, memory)
plan = agent.create_revision_plan(doc_id, days=7, hours_per_day=2.0)
```

### ChatAgent

```python
agent = ChatAgent(groq_client, memory)
answer = agent.answer_question(doc_id, "What is...?")
summary = agent.summarize_notes(doc_id, focus_topic="Physics")
```

---

**Last Updated:** 2024
**Version:** 1.0.0
**Maintainer:** VectorTutor Team

