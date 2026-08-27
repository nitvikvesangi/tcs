# Frontend-Backend Connection Details

## 1. Backend Server
- **File**: `backend/main.py`
- **Startup Command**: `cd backend && uvicorn main:app --reload --port 8000`
- **Base URL**: `http://localhost:8000`

## 2. Frontend Application
- **Startup Command**: `cd dashboard && npm run dev`
- **Frontend Service**: `frontend/src/services/api.ts` (API Client) and `chatService.ts`

## 3. Endpoints

### Endpoint: GET `/health`
- **Method**: GET
- **Query Parameters**: None
- **Request Body**: None
- **Response Schema**: `{"status": "string", "backend_version": "string"}`
- **Frontend Consuming File**: None explicitly currently.
- **Backend Function Powering It**: `health_check()`

### Endpoint: GET `/recommendations`
- **Method**: GET
- **Query Parameters**: `city` (str), `dark_store_id` (str), `category` (str), `demand_status` (str), `search_query` (str)
- **Request Body**: None
- **Response Schema**: `List[RecommendationResponse]`
- **Frontend Consuming File**: `frontend/src/services/api.ts`
- **Backend Function Powering It**: `get_recommendations_endpoint()` which calls `recommendation_service.get_recommendations()`

### Endpoint: POST `/chat`
- **Method**: POST
- **Query Parameters**: None
- **Request Body**: `ChatRequest` (contains `message` string)
- **Response Schema**: `ChatResponse`
- **Frontend Consuming File**: `frontend/src/services/chatService.ts`
- **Backend Function Powering It**: `chat_endpoint()` which calls `chat_service.process_chat_message()`

### Endpoint: GET `/inventory`
- **Method**: GET
- **Query Parameters**: None
- **Request Body**: None
- **Response Schema**: `{ "total_items": int, "items": List[RecommendationResponse] }`
- **Frontend Consuming File**: None explicitly currently (uses `/recommendations` directly).
- **Backend Function Powering It**: `get_inventory()`

### Endpoint: GET `/promotions`
- **Method**: GET
- **Query Parameters**: None
- **Request Body**: None
- **Response Schema**: `List[RecommendationResponse]` (filtered)
- **Frontend Consuming File**: None explicitly currently (uses `/recommendations` directly).
- **Backend Function Powering It**: `get_promotions()`
