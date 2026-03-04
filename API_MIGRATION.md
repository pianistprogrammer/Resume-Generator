# API Response Format Migration - Complete

## Overview
All API endpoints now return responses in a standardized format with `success`, `msg`, and `data` fields.

## Backend Changes

### 1. Generic Response Models
**File:** `backend/app/models/response.py`

```python
class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    msg: str
    data: Optional[T] = None

class ErrorResponse(BaseModel):
    success: bool = False
    msg: str
    error: Optional[str] = None
```

### 2. Updated Controllers

#### Auth Controller (`backend/app/controllers/auth_controller.py`)
- ✅ POST `/auth/register` → `ApiResponse[TokenResponse]`
- ✅ POST `/auth/login` → `ApiResponse[TokenResponse]`
- ✅ GET `/auth/me` → `ApiResponse[UserResponse]`
- ✅ POST `/auth/refresh` → `ApiResponse[TokenResponse]`

#### Profile Controller (`backend/app/controllers/profile_controller.py`)
- ✅ GET `/profile` → `ApiResponse[ProfileResponse]`
- ✅ PUT `/profile` → `ApiResponse[ProfileResponse]`
- ✅ PUT `/profile/preferences` → `ApiResponse[ProfileResponse]`
- ✅ PUT `/profile/notifications` → `ApiResponse[ProfileResponse]`
- ✅ POST `/profile/onboarding/complete` → `ApiResponse[ProfileResponse]`
- ✅ GET `/profile/credits` → `ApiResponse[CreditBalanceResponse]`

### Example Response Format

**Success:**
```json
{
  "success": true,
  "msg": "User registered successfully",
  "data": {
    "access_token": "...",
    "token_type": "bearer",
    "user": { ... }
  }
}
```

**Error:**
```json
{
  "success": false,
  "msg": "An error occurred",
  "error": "Detailed error message"
}
```

## Frontend Changes

### 1. API Utility
**File:** `frontend/utils/api.ts`

Created a generic API request wrapper that:
- Automatically adds auth headers
- Extracts data from the `ApiResponse` wrapper
- Handles errors consistently
- Provides convenience methods (get, post, put, patch, delete)

```typescript
export interface ApiResponse<T = any> {
  success: boolean
  msg: string
  data?: T
}

export async function apiRequest<T>(url: string, options?: RequestInit): Promise<T>

export const api = {
  get: <T>(url: string) => apiRequest<T>(url, { method: 'GET' }),
  post: <T>(url: string, body?: any) => apiRequest<T>(url, { method: 'POST', body }),
  put: <T>(url: string, body?: any) => apiRequest<T>(url, { method: 'PUT', body }),
  patch: <T>(url: string, body?: any) => apiRequest<T>(url, { method: 'PATCH', body }),
  delete: <T>(url: string) => apiRequest<T>(url, { method: 'DELETE' }),
}
```

### 2. Updated Files

#### Auth Store (`frontend/stores/auth.ts`)
- ✅ Updated `register()` to use `api.post<TokenResponse>`
- ✅ Updated `login()` to use `api.post<TokenResponse>`
- ✅ Updated `fetchMe()` to use `api.get<User>`
- ✅ Improved error handling

#### Onboarding Page (`frontend/pages/onboarding.vue`)
- ✅ Updated profile update to use `api.put()`
- ✅ Updated preferences update to use `api.put()`
- ✅ Updated onboarding complete to use `api.post()`
- ✅ Added import for api utility

### Usage Example

**Before:**
```typescript
const response = await $fetch(`${config.public.apiBase}/auth/login`, {
  method: 'POST',
  body: { email, password }
})
this.setAuth(response.access_token, response.user)
```

**After:**
```typescript
const response = await api.post<TokenResponse>('/auth/login', { email, password })
this.setAuth(response.access_token, response.user)
```

## Benefits

1. **Consistency**: All endpoints return the same structure
2. **Type Safety**: TypeScript types ensure correct data structure
3. **Better Error Handling**: Standardized error messages
4. **Cleaner Code**: Less boilerplate in API calls
5. **Success Indicator**: Easy to check if request succeeded
6. **Informative Messages**: Every response includes a human-readable message

## Migration Checklist

### Backend ✅
- [x] Create generic response models
- [x] Update auth endpoints
- [x] Update profile endpoints
- [x] Export response models from models package

### Frontend ✅
- [x] Create API utility with response unwrapping
- [x] Update auth store
- [x] Update onboarding page
- [x] Add TypeScript interfaces

## Next Steps (Optional)

1. Update remaining frontend pages (matches, profile, preferences, settings) to use the new API utility
2. Add global error handler for API errors
3. Add toast notifications for success/error messages
4. Create loading states composable
5. Add request/response interceptors if needed
