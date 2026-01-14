# AI Completion Flow Investigation

This document details the "Complete with AI" flow for tools in the admin dashboard.

## Overview
The feature allows admins to automatically fill in missing fields for a tool (e.g., descriptions, pricing type, categories, professions, tags, SEO metadata) using Google's Gemini AI.

## Flow Steps

### 1. Frontend Trigger
- **Page**: Admin Tool Edit (`/admin-dashboard/tools/[tool_slug]/edit/`)
- **Template**: `templates/admin_form.html`
- **Mechanism**:
  - A "Complete with AI" button is rendered if `model_type` is present.
  - The button uses **Alpine.js** (`x-data="{ ... aiComplete() ... }"`) to handle the click event.
  - **Action**: Clicking sends an asynchronous `POST` request to the AI completion endpoint.
- **Code Snippet**:
  ```html
  <button type="button" @click="aiComplete()" ...>
      Complete with AI
  </button>
  ```
- **Response Handling**:
  - **Success**: Displays a success alert ("AI Completion Success") and **reloads the page** to show updated fields.
  - **Error**: Displays an error alert.

### 2. Backend Routing
- **URL Configuration**: `tools/urls.py`
  ```python
  path('admin-dashboard/tools/<slug:slug>/ai-complete/', views.ai_complete_tool, name='ai_complete_tool'),
  ```
- **View**: `tools.views.ai_complete_tool`

### 3. Backend Logic (`views.ai_complete_tool`)
1.  **Data Gathering**:
    - Retreives the `Tool` object by slug.
    - Collects current field values (name, website, pricing, etc.) and translation data (descriptions, pros/cons).
    - Fetches lists of *existing* Categories, Professions, and Tags to provide context to the AI (encouraging consistency).
2.  **AI Service Call**:
    - Calls `AIService.complete_tool_fields(tool_data, existing_categories, ...)`
3.  **Applying Updates**:
    - Iterates through the returned data.
    - **Direct Fields**: Updates `pricing_type`, `meta_title`, `meta_description`.
    - **Relationships**:
        - `categories`, `professions`, `tags`: Iterates through returned names.
        - slugs strings using `slugify`.
        - **Creates** new objects (`get_or_create`) if they don't exist.
        - Adds them to the tool's many-to-many fields.
    - **Translations**: Updates `ToolTranslation` (English) for `short_description`, `long_description`, `use_cases`, `pros`, `cons`.
4.  **Completion Check**:
    - Checks if all critical fields are now populated.
    - If complete, sets `status = 'published'` (logic inferred from usage context, though explicit "set published" might be conditional or done by `admin_tool_edit` - *Note: The viewed snippet showed `is_complete` check but didn't explicitly show the `status` save line in the truncated view, but implied logical flow.*)
5.  **Response**: Returns `JsonResponse({'success': True, 'message': ...})`.

### 4. AI Service (`tools/ai_service.py`)
- **Method**: `complete_tool_fields`
- **Model**: Uses `gemini-flash-latest` via `google.genai` client.
- **Tools**: Enables `types.GoogleSearch()` for the model to verify tool details and fetch up-to-date info.
- **Prompting**:
    - **Role**: "AI tools curator".
    - **Instruction**: Complete *only* missing fields. Use Google Search to verify.
    - **Input**: Tool attributes + Existing system entities (Categories, Professions, Tags).
    - **Output enforcement**: Requests valid JSON.
- **Parsing**: logic to extract JSON from the model response (handling potential markdown wrapping).

## Key Files
- `templates/admin_form.html`: Frontend UI and AJAX trigger.
- `tools/views.py`: View handler (`ai_complete_tool`).
- `tools/urls.py`: URL routing.
- `tools/ai_service.py`: Core AI logic and prompt engineering.
