# CRM Agent Flow Diagram

## Current Workflow Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CRM AGENT WORKFLOW                                │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   USER      │    │  FRONTEND   │    │   BACKEND   │    │   DATABASE  │
│ INTERACTION │    │   (HTML)    │    │   (FastAPI) │    │  (MongoDB)  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       │ 1. User Action    │                   │                   │
       ├──────────────────►│                   │                   │
       │                   │                   │                   │
       │                   │ 2. Audio Upload   │                   │
       │                   ├──────────────────►│                   │
       │                   │                   │                   │
       │                   │                   │ 3. Process Audio  │
       │                   │                   ├──────────────────►│
       │                   │                   │                   │
       │                   │                   │ 4. Transcribe     │
       │                   │                   │    (Whisper API)  │
       │                   │                   │◄──────────────────┤
       │                   │                   │                   │
       │                   │                   │ 5. Extract Data   │
       │                   │                   │    (GPT-4)        │
       │                   │                   │◄──────────────────┤
       │                   │                   │                   │
       │                   │                   │ 6. Save to DB     │
       │                   │                   ├──────────────────►│
       │                   │                   │                   │
       │                   │ 7. Return Results │                   │
       │                   │◄──────────────────┤                   │
       │                   │                   │                   │
       │ 8. Display Results│                   │                   │
       │◄──────────────────┤                   │                   │
       │                   │                   │                   │
```

## Detailed Step-by-Step Flow

### Phase 1: User Input
```
User Interface (frontend.html)
├── Option 1: Record Audio (5 seconds)
│   ├── Request microphone access
│   ├── Start MediaRecorder
│   ├── Record for 5 seconds
│   └── Create audio blob
└── Option 2: Upload Audio File
    ├── Drag & drop or file selection
    ├── Validate file format
    └── Prepare for upload
```

### Phase 2: Backend Processing
```
FastAPI Endpoint (/process_audio/)
├── Receive audio file
├── Convert to BytesIO object
├── Set filename attribute
└── Process through workflow
```

### Phase 3: Audio Processing Workflow
```
Step 1: Transcription
├── Call transcribe_audio(audio_bytes)
├── Use OpenAI Whisper API
├── Convert speech to text
└── Return transcript or error

Step 2: Data Extraction
├── Call extract_feedback(transcript)
├── Use GPT-4o-mini model
├── Extract structured CRM data
└── Return JSON string

Step 3: Data Validation & Parsing
├── Try to parse JSON
├── If parsing fails, create fallback structure
└── Prepare validated data

Step 4: Data Storage
├── Call save_feedback(parsed_data)
├── Try MongoDB connection
├── If MongoDB fails, save to local JSON file
└── Return save confirmation
```

### Phase 4: Response Generation
```
Final Response
├── Include transcript
├── Include structured data
├── Include save result
└── Return to frontend
```

## Error Handling Flow

```
Error Detection Points:
├── Audio Input Errors
│   ├── Microphone access denied
│   ├── Invalid file format
│   └── File upload failure
├── Processing Errors
│   ├── Transcription API failure
│   ├── Data extraction failure
│   └── JSON parsing errors
├── Storage Errors
│   ├── MongoDB connection failure
│   ├── Database write failure
│   └── Fallback storage failure
└── System Errors
    ├── Network timeouts
    ├── API rate limits
    └── Unexpected exceptions
```

## Data Flow

```
Audio Input → BytesIO → Whisper API → Text → GPT-4 → JSON → MongoDB/JSON → Response
```

## Key Components

1. **Frontend (frontend.html)**
   - User interface
   - Audio recording/upload
   - Result display
   - Error handling

2. **Backend (app.py)**
   - FastAPI server
   - Audio processing endpoint
   - Error handling
   - Response generation

3. **Agent (agent.py)**
   - Audio transcription
   - Data extraction
   - Tool definitions

4. **Database (db.py)**
   - MongoDB connection
   - Fallback JSON storage
   - Data persistence

## Current Workflow Characteristics

- **Simple & Direct**: Linear processing without complex orchestration
- **Error Handling**: Basic error handling with fallback mechanisms
- **Storage**: MongoDB with JSON file fallback
- **API Integration**: OpenAI Whisper + GPT-4
- **User Interface**: Web-based with audio recording capabilities

