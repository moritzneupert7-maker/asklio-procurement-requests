# Procurement Portal Enhancements - Implementation Summary

## Overview
This PR implements comprehensive frontend and backend enhancements to the procurement portal, now rebranded as **askLio**.

## Changes Implemented

### 1. Backend API Endpoints

#### New Endpoint: `POST /requests/predict-commodity-group`
- **Purpose**: Predict commodity group based on request title
- **Input**: `{ "title": "..." }`
- **Output**: `{ "commodity_group_id": "029" }`
- **Implementation**: Uses existing LLM commodity prediction logic with OpenAI GPT-4o-mini
- **Location**: `backend/app/routers/requests.py`

#### New Endpoint: `DELETE /requests`
- **Purpose**: Delete all procurement requests from the database
- **Output**: `{ "message": "All requests deleted successfully" }`
- **Location**: `backend/app/routers/requests.py`

#### New Endpoint: `POST /chat`
- **Purpose**: Chat with AskLio virtual assistant
- **Input**: `{ "message": "user's question" }`
- **Output**: `{ "reply": "assistant's response" }`
- **Implementation**: Uses OpenAI GPT-4o-mini with context about all procurement requests
- **Location**: `backend/app/routers/chat.py` (new router)
- **Features**:
  - Provides information about user's procurement requests
  - Answers general procurement policy questions
  - Maintains context from all requests in the system

### 2. Frontend Enhancements

#### Form Improvements (New Request Tab)
- **Prefilled Fields**:
  - Requestor: "Moritz Neupert"
  - Department: "Marketing"
- **Auto-fill Commodity Group**:
  - Debounced title input (500ms delay)
  - Automatically predicts and selects commodity group
  - Uses new `/requests/predict-commodity-group` endpoint
- **Form Validation**:
  - Validates all required fields before submission
  - Checks for non-empty title, requestor, vendor, department
  - Validates total_cost > 0
  - Shows alert: "Request cannot be created, due to missing information"
  - Form reset maintains prefilled values

#### Overview Tab Enhancements
- **Clear History Button**:
  - Red button in the top-right of the requests list
  - Shows confirmation dialog before deletion
  - Calls `/DELETE /requests` endpoint
  - Refreshes the request list after deletion
  
- **Status Dropdown**:
  - Replaced static status badge with interactive dropdown
  - Options: Open, In Progress, Closed
  - Automatically updates backend via `POST /{request_id}/status`
  - Shows success message on status change
  - Maintains colored badges for visual clarity

#### AskLio Chat Widget
- **Floating Chat Button**:
  - Fixed position in bottom-right corner
  - Black circular button with crescent moon icon
  - Expands into chat panel on click
  
- **Chat Panel Features**:
  - Clean, modern interface (96rem width, 500px height)
  - Black header with AskLio branding
  - Scrollable message history
  - User messages in black bubbles (right-aligned)
  - Assistant messages in gray bubbles (left-aligned)
  - Loading spinner during response
  - Text input with Enter key support
  - Initial greeting message
  
- **Chat Functionality**:
  - Maintains conversation history within session
  - Calls `/POST /chat` endpoint
  - Context-aware responses based on all requests

#### UI/Branding Changes
- **Logo**:
  - Replaced "ProcurementPortal" with "askLio" branding
  - Added crescent moon SVG icon
  - Black text styling
  - Consistent across all tabs
  
- **Color Scheme**:
  - Removed all purple/violet colors
  - Active tab indicator: black
  - Form focus colors: blue (for better usability)
  - Buttons: blue accent (maintains consistency)
  - Text: black throughout the application
  - Interactive elements kept with appropriate accent colors

### 3. Commodity Group Classification

All 50 commodity groups are properly seeded in the database:
- General Services (001-010)
- Facility Management (011-019)
- Publishing Production (020-028)
- Information Technology (029-031)
- Logistics (032-035)
- Marketing & Advertising (036-043)
- Production (044-050)

The LLM prediction uses GPT-4o-mini with structured output to classify requests into one of these 50 groups.

## Technical Implementation Details

### Frontend Architecture
- **Framework**: React with TypeScript
- **State Management**: Zustand for global state
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **New API Functions**: 
  - `predictCommodityGroup(title: string)`
  - `deleteAllRequests()`
  - `updateRequestStatus(requestId, toStatus, changedBy)`
  - `chatWithAsklio(message: string)`

### Backend Architecture
- **Framework**: FastAPI
- **Database**: SQLAlchemy with SQLite
- **LLM Integration**: OpenAI Python SDK
- **Model**: GPT-4o-mini for both commodity prediction and chat
- **Response Format**: Pydantic models with structured output

### Dependencies Added
Backend (`requirements.txt`):
```
fastapi>=0.115.0
uvicorn[standard]>=0.34.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
openai>=1.0.0
pdfplumber>=0.11.0
pytest>=8.0.0
httpx>=0.27.0
```

## Testing

### Unit Tests
New test file: `backend/tests/test_new_endpoints.py`
- Tests for commodity group prediction endpoint
- Tests for delete all requests endpoint
- Tests for chat endpoint (with and without API key)
- All tests use mocking to avoid actual OpenAI API calls

### Manual Testing Checklist
- [ ] Form prefills with "Moritz Neupert" and "Marketing"
- [ ] Title input triggers commodity group prediction after 500ms
- [ ] Form validation prevents submission with missing fields
- [ ] Clear History button deletes all requests with confirmation
- [ ] Status dropdown updates request status
- [ ] Chat widget opens and closes properly
- [ ] Chat sends messages and receives responses
- [ ] AskLio logo displays correctly on all tabs
- [ ] All purple/violet text changed to black

## Setup Instructions

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env
# Edit .env and add your OPENAI_API_KEY
python -m app.seed_commodity_groups  # Initialize database
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Running Tests
```bash
cd backend
pytest tests/
```

## API Key Requirements
The following features require an OpenAI API key:
- Commodity group prediction from title
- AskLio chat functionality
- PDF offer extraction (existing feature)

Without an API key, these features will return appropriate error messages (503 Service Unavailable).

## Future Enhancements
Potential improvements for future versions:
- Add chat conversation history persistence
- Implement more sophisticated commodity group prediction with additional context
- Add bulk status updates
- Export requests to CSV/Excel
- Advanced filtering and search in Overview tab
- User authentication and role-based access

## Files Modified
- `backend/app/main.py` - Added chat router
- `backend/app/routers/requests.py` - Added new endpoints
- `backend/app/routers/chat.py` - New file for chat functionality
- `backend/app/schemas.py` - Added new request/response models
- `backend/requirements.txt` - New file with dependencies
- `backend/tests/test_new_endpoints.py` - New test file
- `frontend/src/App.tsx` - Major UI updates and new features
- `frontend/src/api.ts` - Added new API functions

## Notes
- The commodity groups table is automatically seeded on application startup
- The chat widget is available on all tabs
- Form validation is client-side only (server-side validation exists in Pydantic models)
- Status changes create immutable status event history
- The Clear History button requires explicit confirmation before deletion
