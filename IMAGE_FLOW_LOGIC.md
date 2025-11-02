# Image Upload and Storage Flow Logic

## Overview
This document explains how images are uploaded, processed, stored locally, and saved to MongoDB.

## Complete Flow

### 1. Frontend (dashboard.html)
- User selects an image file via `<input type="file" id="imageUpload">`
- Image is stored in `selectedImage` variable
- When "Complete & Upload" is clicked:
  - Audio blob is created and added to FormData as `"file"`
  - Image is added to FormData as `"image"` (if selected)
  - FormData is sent via POST to `/process_audio`

### 2. Backend Endpoint (app.py - `/process_audio`)
**Location:** Lines 91-355

**Process:**
1. Receives `file` (audio) and `image` (optional) as `UploadFile` objects
2. Validates audio file
3. Reads audio into memory
4. **Image Processing (Lines 137-217):**
   - Checks if `image` exists and has `image.filename`
   - Reads image content: `image_content = await image.read()`
   - Generates unique filename: `{timestamp}_{original_stem}.{extension}`
     - Example: `20251029_123456_Artboard-1.jpg`
   - Creates full path: `IMAGES_DIR / unique_filename`
   - **SAVES TO DISK:** `with open(image_path, "wb") as f: f.write(image_content)`
   - Creates `image_data` dictionary with:
     - `image_url`: `/images/{unique_filename}`
     - `unique_filename`: The timestamped filename
     - `filename`: Original filename
     - `file_path`: Full absolute path
     - `image_saved`: Boolean flag

5. **Passes to Agent:** `process_audio_with_agent(audio_bytes, filename, image_data)`

### 3. Agent Processing (agent.py - `process_audio_with_agent`)
**Location:** Lines 353-405

**Process:**
1. Receives `image_data` parameter
2. Stores `image_data` in global variable `current_image_data`
3. Creates prompt for LangChain agent
4. Agent uses tools in order:
   - `convert_audio_format` → Convert audio to WAV
   - `transcribe_audio` → Get transcript
   - `extract_feedback` → Extract structured data
   - `save_feedback` → Save to MongoDB

### 4. Extract Feedback Tool (agent.py - `extract_feedback`)
**Location:** Lines 113-333

**Process:**
1. Accesses global `current_image_data`
2. Extracts `image_url` and `image_description` from `image_data`
3. Calls OpenAI to extract structured data from transcript
4. **FORCES image fields after AI extraction (Lines 252-262):**
   ```python
   if image_url:
       parsed_data["image_url"] = image_url  # Override any AI-generated value
   if image_description:
       parsed_data["image_description"] = image_description
   ```
5. Returns `parsed_data` dictionary with all fields including `image_url`

### 5. Save Feedback Tool (agent.py - `save_feedback`)
**Location:** Lines 10-38

**Process:**
1. Receives `parsed_data` dictionary from `extract_feedback`
2. Converts string representations to dict if needed
3. Calls `db.save_feedback(data)` to save to MongoDB

### 6. Database Save (db.py - `save_feedback`)
**Location:** Lines 10-89

**Process:**
1. Receives data dictionary
2. Connects to MongoDB (or falls back to JSON)
3. Inserts document into `crm.returned_cust` collection
4. Document includes `image_url` field (e.g., `/images/20251029_123456_Artboard-1.jpg`)

### 7. Image Serving (app.py - `/images/{filename}`)
**Location:** Lines 416-431

**Process:**
1. Receives request for `/images/{filename}`
2. Looks up file in `IMAGES_DIR`
3. Returns file using `FileResponse`

## Key Points

1. **Image URL Generation:** Happens in `app.py` BEFORE agent processing
2. **Image Saving:** Happens in `app.py` BEFORE agent processing
3. **Agent Involvement:** Agent ONLY receives `image_url` and stores it - does NOT generate it
4. **Forced Values:** Agent's `extract_feedback` FORCES `image_url` into parsed data to prevent AI override

## Potential Issues

1. **Image not saved to disk:**
   - Check if `IMAGES_DIR` exists and is writable
   - Check if `image.read()` is called before file is saved
   - Check for permission errors

2. **Wrong URL in MongoDB:**
   - Agent might be overriding the URL (should be prevented by forcing)
   - Database save might not include `image_url` field
   - Old data might have wrong format

3. **404 Errors:**
   - URL format mismatch (e.g., storing original filename instead of `/images/...`)
   - File not actually saved to disk
   - Filename encoding issues

## Debugging Checklist

- [ ] Check server terminal for `[IMAGE]` debug messages
- [ ] Verify `IMAGES_DIR` exists: `C:\Users\shama\Projects\crm_agent_images`
- [ ] Check if files appear in the directory after upload
- [ ] Check MongoDB document to see what `image_url` value is stored
- [ ] Check browser console for FormData contents
- [ ] Check server response for `image_debug` info
