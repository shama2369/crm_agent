from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
import io
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# CONFIGURATION
# -----------------------------
app = FastAPI(title="Trichy Gold AI Voice Capture - LangChain Agent")

# Image storage configuration
IMAGES_DIR = Path("C:\\Users\\shama\\Projects\\crm_agent_images").resolve()
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
print(f"[CONFIG] Images directory: {IMAGES_DIR}")
print(f"[CONFIG] Images directory exists: {IMAGES_DIR.exists()}")
print(f"[CONFIG] Images directory absolute: {IMAGES_DIR.absolute()}")

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# ROUTES
# -----------------------------

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the dashboard page"""
    return FileResponse("dashboard.html")

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "Trichy Gold AI Lead Capture API is running with LangChain Agent!",
        "description": "AI-powered CRM agent using LangChain for salesperson audio processing",
        "endpoints": {
            "upload_audio": "/process_audio",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "ai_components": {
            "agent_framework": "LangChain",
            "transcription": "OpenAI Whisper",
            "text_processing": "OpenAI GPT-4o-mini",
            "database": "MongoDB (Railway) with JSON fallback"
        },
        "purpose": "Capture salesperson audio about non-buying customers and extract reasons"
    }

@app.post("/test-upload")
async def test_upload(file: UploadFile = File(...), image: UploadFile = File(None)):
    """Test endpoint to debug image upload."""
    try:
        print(f"[TEST] Received file: {file.filename}")
        print(f"[TEST] Received image: {image.filename if image else 'None'}")
        
        if image:
            image_content = await image.read()
            print(f"[TEST] Image size: {len(image_content)} bytes")
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{image.filename}"
            image_path = IMAGES_DIR / unique_filename
            
            with open(image_path, "wb") as f:
                f.write(image_content)
            
            print(f"[TEST] Image saved: {image_path}")
            return {"status": "success", "image_saved": unique_filename}
        else:
            return {"status": "success", "image_saved": None}
            
    except Exception as e:
        print(f"[TEST] Error: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...), image: UploadFile = File(None)):
    """
    Process salesperson audio using LangChain agent.
    Extracts reasons why customers didn't purchase.
    Optionally accepts an image file for additional context.
    Audio recording is REQUIRED.
    """
    print(f"\n{'='*80}")
    print(f"[PROCESS_AUDIO] ========== ENDPOINT CALLED ==========")
    print(f"[PROCESS_AUDIO] File: {file.filename if file else 'None'}")
    print(f"[PROCESS_AUDIO] Image parameter: {image is not None}")
    if image:
        print(f"[PROCESS_AUDIO] Image filename: {image.filename if hasattr(image, 'filename') else 'No filename attr'}")
    print(f"{'='*80}\n")
    
    try:
        # Debug information
        print(f"[FILE] Received file: filename={file.filename}, content_type={file.content_type}, size={file.size}")
        print(f"[IMAGE] Image parameter received: {image is not None}")
        print(f"[IMAGE] Image object: {image}")
        if image:
            print(f"[IMAGE] Received image: filename={image.filename}, content_type={image.content_type}, size={image.size}")
        else:
            print(f"[IMAGE] No image provided")
        
        # Audio file validation is REQUIRED
        is_audio_file = (
            (file.content_type and file.content_type.startswith('audio/')) or
            (file.filename and any(file.filename.lower().endswith(ext) for ext in ['.wav', '.mp3', '.m4a', '.webm', '.ogg', '.flac', '.aac'])) or
            (file.filename and 'audio' in file.filename.lower())
        )
        
        if not is_audio_file:
            print(f"[ERROR] File validation failed: content_type={file.content_type}, filename={file.filename}")
            raise HTTPException(status_code=400, detail=f"Please upload an audio file. Received: content_type={file.content_type}, filename={file.filename}")
        
        # Read the file content
        file_content = await file.read()
        if len(file_content) == 0:
            print("[ERROR] Empty file uploaded")
            raise HTTPException(status_code=400, detail="Empty file uploaded")
            
        audio_bytes = io.BytesIO(file_content)
        audio_bytes.name = file.filename or "audio_file"

        # Handle image if provided
        image_data = None
        print(f"[IMAGE] ========== STARTING IMAGE PROCESSING ==========")
        print(f"[IMAGE] image parameter received: {image is not None}")
        print(f"[IMAGE] image object type: {type(image)}")
        if image:
            print(f"[IMAGE] image.filename: {image.filename}")
            print(f"[IMAGE] image.content_type: {image.content_type if hasattr(image, 'content_type') else 'N/A'}")
            print(f"[IMAGE] image.size: {image.size if hasattr(image, 'size') else 'N/A'}")
        else:
            print(f"[IMAGE] NO IMAGE OBJECT - image parameter is None")
        
        if image and image.filename:
            print(f"[IMAGE] Image condition met - proceeding with processing")
            print(f"[IMAGE] Processing image: {image.filename}")
            print(f"[IMAGE] Image object type: {type(image)}")
            print(f"[IMAGE] Image has read method: {hasattr(image, 'read')}")
            try:
                # Reset file pointer to beginning (in case it was already read)
                if hasattr(image.file, 'seek'):
                    image.file.seek(0)
                
                image_content = await image.read()
                print(f"[IMAGE] Image content size: {len(image_content)} bytes")
                print(f"[IMAGE] Image content type: {type(image_content)}")
                
                if len(image_content) > 0:
                    # Generate unique filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_extension = Path(image.filename).suffix
                    unique_filename = f"{timestamp}_{Path(image.filename).stem}{file_extension}"
                    
                    # Save image to local directory
                    image_path = IMAGES_DIR / unique_filename
                    print(f"[IMAGE] Saving to: {image_path}")
                    print(f"[IMAGE] Directory exists: {IMAGES_DIR.exists()}")
                    print(f"[IMAGE] Directory path: {IMAGES_DIR}")
                    
                    # Generate image URL for database BEFORE saving (separate from agent)
                    image_url = f"/images/{unique_filename}"
                    print(f"[IMAGE] Image URL generated: {image_url}")
                    
                    # Save image to local directory
                    image_saved = False
                    try:
                        print(f"[IMAGE] Attempting to write {len(image_content)} bytes to: {image_path}")
                        print(f"[IMAGE] Parent directory exists: {image_path.parent.exists()}")
                        print(f"[IMAGE] Parent directory: {image_path.parent}")
                        print(f"[IMAGE] Parent is writable: {os.access(image_path.parent, os.W_OK) if image_path.parent.exists() else 'N/A'}")
                        
                        # Ensure parent directory exists
                        image_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Write file
                        with open(image_path, "wb") as f:
                            bytes_written = f.write(image_content)
                            f.flush()
                            os.fsync(f.fileno())  # Force write to disk
                        
                        print(f"[IMAGE] Bytes written to file: {bytes_written}")
                        
                        # Verify file was saved
                        image_saved = image_path.exists()
                        if image_saved:
                            file_size = image_path.stat().st_size
                            print(f"[IMAGE] ✓ Image saved successfully!")
                            print(f"[IMAGE] ✓ File path: {image_path}")
                            print(f"[IMAGE] ✓ File size on disk: {file_size} bytes")
                            print(f"[IMAGE] ✓ File exists: {image_saved}")
                        else:
                            print(f"[IMAGE] ✗ WARNING: Image save reported success but file not found!")
                            print(f"[IMAGE] ✗ Expected path: {image_path}")
                            print(f"[IMAGE] ✗ Directory contents: {list(image_path.parent.iterdir()) if image_path.parent.exists() else 'Directory does not exist'}")
                    except PermissionError as pe:
                        print(f"[IMAGE] ✗ PERMISSION ERROR saving image: {pe}")
                        print(f"[IMAGE] ✗ Path: {image_path}")
                        print(f"[IMAGE] ✗ Check write permissions for: {image_path.parent}")
                    except Exception as e:
                        print(f"[IMAGE] ✗ ERROR saving image: {e}")
                        print(f"[IMAGE] ✗ Exception type: {type(e).__name__}")
                        import traceback
                        print(f"[IMAGE] ✗ Traceback:\n{traceback.format_exc()}")
                    
                    # Always create image_data with image_url, even if save failed
                    image_data = {
                        "filename": image.filename,
                        "unique_filename": unique_filename,
                        "file_path": str(image_path),
                        "content_type": image.content_type,
                        "size": len(image_content),
                        "image_url": image_url,  # Always use the generated URL
                        "image_saved": image_saved  # Flag to indicate if file was actually saved
                    }
                    print(f"[IMAGE] ========== IMAGE DATA CREATED ==========")
                    print(f"[IMAGE] image_data['image_url']: {image_data.get('image_url')}")
                    print(f"[IMAGE] image_data['unique_filename']: {image_data.get('unique_filename')}")
                    print(f"[IMAGE] image_data['filename']: {image_data.get('filename')}")
                    print(f"[IMAGE] image_data['file_path']: {image_data.get('file_path')}")
                    print(f"[IMAGE] image_saved flag: {image_data.get('image_saved')}")
                else:
                    print(f"[IMAGE] Image content is empty - skipping")
            except Exception as e:
                print(f"[IMAGE] ========== ERROR READING IMAGE ==========")
                print(f"[IMAGE] Error type: {type(e).__name__}")
                print(f"[IMAGE] Error message: {str(e)}")
                import traceback
                print(f"[IMAGE] Full traceback:\n{traceback.format_exc()}")
        else:
            print(f"[IMAGE] ========== SKIPPING IMAGE PROCESSING ==========")
            print(f"[IMAGE] Reason: image={image}, filename={image.filename if image else 'None'}")
        
        # Verify image_data before passing to agent
        if image_data:
            print(f"[APP] Image data before agent: image_url={image_data.get('image_url')}, unique_filename={image_data.get('unique_filename')}")
        else:
            print(f"[APP] No image_data to pass to agent")
        
        # Import and use the LangChain agent
        print("[AGENT] Starting LangChain agent processing...")
        from agent import process_audio_with_agent
        
        # Process audio using the AI agent with Unicode error handling
        try:
            result = process_audio_with_agent(audio_bytes, file.filename or "audio_file", image_data)
        except UnicodeEncodeError as unicode_error:
            print(f"[ERROR] Unicode encoding error: {unicode_error}")
            # Fallback: Try to save basic data even if agent fails due to Unicode
            try:
                from db import save_feedback
                fallback_data = {
                    "purchased": None,
                    "salesperson_name": None,
                    "item_type": None,
                    "metal_type": None,
                    "reason_price": None,
                    "reason_size": None,
                    "reason_weight": None,
                    "reason_zeromaking": None,
                    "reason_design_outofstock": None,
                    "reason_design_new": None,
                    "required_size": None,
                    "required_weight": None,
                    "available_size": None,
                    "available_weight": None,
                    "asked_price": None,
                    "given_price": None,
                    "design_type": None,
                    "item_category": None,
                    "customer_intent": None,
                    "is_previous_cust": None,
                    "type_of_customer": None,
                    "M_Source": None,
                    "M_source_Tag": None,
                    "design_preference": None,
                    "store_impression": None,
                    "customer_mood": None,
                    "customer_support": None,
                    "purchase_satisfaction": None,
                    "waiting_time": None,
                    "original_text": f"Unicode encoding error: {unicode_error}",
                    "contact_number": None,
                    "image_url": image_data.get('image_url') if image_data else None
                }
                save_result = save_feedback(fallback_data)
                print(f"Fallback save result: {save_result}")
                return {
                    "message": "Unicode encoding error occurred, but basic data saved",
                    "error": str(unicode_error),
                    "status": "partial_success",
                    "fallback_saved": True
                }
            except Exception as fallback_error:
                print(f"Fallback save also failed: {fallback_error}")
                raise HTTPException(status_code=500, detail=f"Unicode encoding error: {unicode_error}")
        
        print(f"Agent result: {result}")
        
        if result["status"] == "error":
            print(f"Agent processing failed: {result['error']}")
            # Fallback: Try to save basic data even if agent fails
            try:
                from db import save_feedback
                fallback_data = {
                    "purchased": None,
                    "salesperson_name": None,
                    "item_type": None,
                    "metal_type": None,
                    "reason_price": None,
                    "reason_size": None,
                    "reason_weight": None,
                    "reason_zeromaking": None,
                    "reason_design_outofstock": None,
                    "reason_design_new": None,
                    "required_size": None,
                    "required_weight": None,
                    "available_size": None,
                    "available_weight": None,
                    "asked_price": None,
                    "given_price": None,
                    "design_type": None,
                    "item_category": None,
                    "customer_intent": None,
                    "is_previous_cust": None,
                    "type_of_customer": None,
                    "M_Source": None,
                    "M_source_Tag": None,
                    "design_preference": None,
                    "store_impression": None,
                    "customer_mood": None,
                    "customer_support": None,
                    "purchase_satisfaction": None,
                    "waiting_time": None,
                    "original_text": f"Audio processing failed: {result['error']}",
                    "contact_number": None,
                    "image_url": image_data.get('image_url') if image_data else None
                }
                save_result = save_feedback(fallback_data)
                print(f"Fallback save result: {save_result}")
                return {
                    "message": "Audio processing failed, but basic data saved",
                    "error": result["error"],
                    "status": "partial_success",
                    "fallback_saved": True
                }
            except Exception as fallback_error:
                print(f"Fallback save also failed: {fallback_error}")
                raise HTTPException(status_code=500, detail=f"Processing failed: {result['error']}")
        
        print("Agent processing completed successfully")
        
        # Return debug info about image
        response_data = {
            "message": "Salesperson audio processed successfully by AI agent",
            "agent_result": result["agent_result"],
            "status": "success",
            "purpose": "Captured reasons why customer did not purchase",
            "image_included": image_data is not None
        }
        
        if image_data:
            response_data["image_debug"] = {
                "image_url": image_data.get("image_url"),
                "unique_filename": image_data.get("unique_filename"),
                "filename": image_data.get("filename"),
                "image_saved": image_data.get("image_saved")
            }
            print(f"[RESPONSE] Returning image debug info: {response_data['image_debug']}")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Trichy Gold AI Voice Capture",
        "agent": "LangChain Agent Active"
    }

@app.get("/api/feedback")
async def get_feedback(
    feedbackId: str = None,
    salesperson: str = None,
    itemType: str = None,
    metalType: str = None,
    customerIntent: str = None,
    designPreference: str = None,
    customerMood: str = None,
    storeImpression: str = None,
    customerSupport: str = None,
    priceIssue: str = None,
    sizeIssue: str = None
):
    """Get filtered feedback data for the filter table."""
    try:
        from db import get_filtered_feedback
        
        filters = {
            "feedbackId": feedbackId,
            "salesperson": salesperson,
            "itemType": itemType,
            "metalType": metalType,
            "customerIntent": customerIntent,
            "designPreference": designPreference,
            "customerMood": customerMood,
            "storeImpression": storeImpression,
            "customerSupport": customerSupport,
            "priceIssue": priceIssue,
            "sizeIssue": sizeIssue
        }
        
        feedback_data = get_filtered_feedback(filters)
        return feedback_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching filtered feedback: {str(e)}")

@app.get("/test-images")
async def test_images():
    """Test endpoint to check images directory."""
    try:
        files = list(IMAGES_DIR.iterdir())
        return {
            "directory": str(IMAGES_DIR),
            "exists": IMAGES_DIR.exists(),
            "files": [f.name for f in files]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/images/{filename}")
async def serve_image(filename: str):
    """Serve images from local directory."""
    try:
        print(f"[IMAGE_SERVE] Requested filename: {filename}")
        image_path = IMAGES_DIR / filename
        print(f"[IMAGE_SERVE] Full path: {image_path}")
        print(f"[IMAGE_SERVE] Path exists: {image_path.exists()}")
        print(f"[IMAGE_SERVE] Directory contents: {list(IMAGES_DIR.iterdir())}")
        
        if image_path.exists():
            print(f"[IMAGE_SERVE] Serving file: {image_path}")
            return FileResponse(image_path)
        else:
            print(f"[IMAGE_SERVE] File not found: {image_path}")
            raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        print(f"[IMAGE_SERVE] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error serving image: {str(e)}")

@app.delete("/api/feedback/{feedback_id}")
async def delete_feedback(feedback_id: str):
    """Delete a specific feedback record and associated image file."""
    print(f"[DELETE_API] ========== DELETE REQUEST ==========")
    print(f"[DELETE_API] Feedback ID: {feedback_id}")
    try:
        from db import delete_feedback_record
        result = delete_feedback_record(feedback_id)
        print(f"[DELETE_API] Result from delete_feedback_record: {result}")
        print(f"[DELETE_API] Result type: {type(result)}")
        
        if not result:
            print(f"[DELETE_API] ✗ Record not found or deletion failed")
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        # Check if result is a dict with image_url (new format)
        if isinstance(result, dict) and result.get("deleted"):
            image_url = result.get("image_url")
            print(f"[DELETE_API] Image URL from database: {image_url}")
            print(f"[DELETE_API] Image URL type: {type(image_url)}")
            print(f"[DELETE_API] Image URL truthy check: {bool(image_url)}")
            
            # Delete associated image file if it exists
            if image_url and image_url != "null" and str(image_url).strip():
                try:
                    # Extract filename from image_url (e.g., /images/20251029_123456_filename.jpg)
                    # Remove leading /images/ if present, handle both /images/ and images/ prefixes
                    filename = str(image_url).strip()
                    if filename.startswith("/images/"):
                        filename = filename.replace("/images/", "", 1)
                    elif filename.startswith("images/"):
                        filename = filename.replace("images/", "", 1)
                    
                    image_path = IMAGES_DIR / filename
                    print(f"[DELETE_API] Extracted filename: {filename}")
                    print(f"[DELETE_API] Full image path: {image_path}")
                    print(f"[DELETE_API] Path exists: {image_path.exists()}")
                    print(f"[DELETE_API] Images directory: {IMAGES_DIR}")
                    print(f"[DELETE_API] Images directory exists: {IMAGES_DIR.exists()}")
                    
                    if image_path.exists() and image_path.is_file():
                        try:
                            image_path.unlink()
                            # Verify deletion succeeded
                            if image_path.exists():
                                print(f"[DELETE_API] ✗ WARNING: File still exists after deletion attempt. File may be locked by another process (File Explorer, image viewer, etc.)")
                            else:
                                print(f"[DELETE_API] ✓ Successfully deleted image file: {image_path}")
                        except PermissionError as pe:
                            print(f"[DELETE_API] ✗ Permission denied - File may be open in File Explorer or another program: {pe}")
                        except Exception as delete_error:
                            print(f"[DELETE_API] ✗ Error deleting file: {delete_error}")
                    else:
                        print(f"[DELETE_API] ✗ Image file not found: {image_path}")
                        # Try to list files in directory for debugging
                        try:
                            files_in_dir = list(IMAGES_DIR.glob("*"))
                            print(f"[DELETE_API] Files in images directory: {[f.name for f in files_in_dir[:10]]}")
                            # Check if filename matches any file (case-insensitive)
                            matching_files = [f for f in files_in_dir if f.name.lower() == filename.lower()]
                            if matching_files:
                                print(f"[DELETE_API] Found case-insensitive match: {matching_files[0]}")
                                matching_files[0].unlink()
                                print(f"[DELETE_API] ✓ Deleted case-insensitive match: {matching_files[0]}")
                        except Exception as list_error:
                            print(f"[DELETE_API] Could not list directory: {list_error}")
                except Exception as image_error:
                    print(f"[DELETE_API] ✗ Error deleting image file: {image_error}")
                    import traceback
                    print(f"[DELETE_API] Traceback: {traceback.format_exc()}")
                    # Don't fail the deletion if image deletion fails
            else:
                print(f"[DELETE_API] No image_url found in record (image_url={image_url}), skipping image deletion")
        else:
            print(f"[DELETE_API] Result is not expected dict format: {result}")
        
        print(f"[DELETE_API] ========== DELETE COMPLETE ==========")
        return {"message": "Feedback deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DELETE_API] ✗ Exception: {e}")
        import traceback
        print(f"[DELETE_API] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error deleting feedback: {str(e)}")

@app.get("/dashboard")
async def dashboard():
    """Serve the dashboard page."""
    return FileResponse("dashboard.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)