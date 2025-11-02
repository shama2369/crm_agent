import os
from langchain.agents import initialize_agent, Tool
from langchain_openai import ChatOpenAI
from openai import OpenAI
from db import save_feedback as db_save_feedback

# Set Unicode encoding environment variable
os.environ['PYTHONIOENCODING'] = 'utf-8'

def save_feedback(data):
    """Wrapper function to ensure data is passed as dictionary to db_save_feedback."""
    print(f"AGENT save_feedback wrapper - Data type: {type(data)}")
    print(f"AGENT save_feedback wrapper - Data preview: {str(data)[:100]}...")
    
    # If data is a string representation of a dict, convert it
    if isinstance(data, str):
        try:
            # Try to parse as JSON first
            data = json.loads(data)
            print("AGENT: JSON parsing succeeded")
        except json.JSONDecodeError:
            try:
                # Handle string representations like "{'key': 'value'}"
                if data.startswith('{') and data.endswith('}'):
                    # Replace None with null for JSON parsing
                    json_str = data.replace('None', 'null').replace("'", '"')
                    data = json.loads(json_str)
                    print("AGENT: String-to-dict conversion succeeded")
                else:
                    print("AGENT: Not a string dictionary format")
            except Exception as e:
                print(f"AGENT: Conversion failed: {e}")
    
    print(f"AGENT: Final data type: {type(data)}")
    print(f"AGENT: Final data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
    
    # Log image_url before saving
    if isinstance(data, dict):
        image_url_value = data.get('image_url')
        print(f"[AGENT_SAVE] Image URL in data being saved: {image_url_value}")
        print(f"[AGENT_SAVE] Image URL type: {type(image_url_value)}")
        if image_url_value:
            print(f"[AGENT_SAVE] ✓ Image URL will be saved to MongoDB: {image_url_value}")
        else:
            print(f"[AGENT_SAVE] ✗ WARNING: Image URL is None or missing!")
    
    # Call the actual db function
    result = db_save_feedback(data)
    print(f"[AGENT_SAVE] Database save result: {result}")
    return result
import os
from dotenv import load_dotenv
import json
import io
from pydub import AudioSegment

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY missing in environment")

openai_client = OpenAI(api_key=openai_api_key)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ---- TOOLS ----
def transcribe_audio(input_param=None):
    """Transcribe customer feedback audio."""
    global current_audio_file
    audio_file = current_audio_file or input_param
    if not audio_file:
        return "Error: No audio file found"
    
    print(f"Transcribing audio file: {getattr(audio_file, 'name', 'unknown')}")
    
    if hasattr(audio_file, 'read'):
        audio_file.seek(0)
        file_obj = audio_file
    else:
        file_obj = io.BytesIO(audio_file)
        file_obj.name = "audio.wav"
    
    try:
        transcript = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=file_obj
        )
        print(f"Transcription successful: {len(transcript.text)} characters")
        return transcript.text
    except Exception as e:
        print(f"Transcription error: {e}")
        return f"Error transcribing audio: {e}"

def convert_audio_format(input_param=None):
    """Convert audio to WAV if needed."""
    global current_audio_file
    audio_file = current_audio_file or input_param
    if not audio_file:
        return "Error: No audio file found"
    
    print(f"Converting audio file: {getattr(audio_file, 'name', 'unknown')}")
    
    try:
        if hasattr(audio_file, 'read'):
            audio_file.seek(0)
            file_obj = audio_file
        else:
            file_obj = io.BytesIO(audio_file)
            file_obj.name = "audio.wav"
        
        audio = AudioSegment.from_file(file_obj)
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0)
        wav_buffer.name = "converted_audio.wav"
        print(f"Audio conversion successful")
        return wav_buffer
    except Exception as e:
        print(f"Audio conversion failed: {e}")
        # Return original file if conversion fails
        if hasattr(audio_file, 'seek'):
            audio_file.seek(0)
        return audio_file

def extract_feedback(feedback_text: str):
    """Extract structured feedback fields from the transcript or image context."""
    global current_image_data
    
    try:
        image_context = ""
        if current_image_data:
            image_context = f"\n\nAn image file '{current_image_data['filename']}' is also provided for additional context. Include any relevant image information in the feedback."
            # Use image URL from image_data if provided (handled separately in app.py), otherwise generate it
            if 'image_url' in current_image_data and current_image_data['image_url']:
                image_url = current_image_data['image_url']
                print(f"[AGENT] Using provided image URL: {image_url}")
            else:
                # Fallback: Generate image URL if not provided
                image_url = f"/images/{current_image_data['unique_filename']}"
                print(f"[AGENT] Generated image URL: {image_url}")
            print(f"[AGENT] Image unique filename: {current_image_data['unique_filename']}")
        else:
            image_url = None
            print(f"[AGENT] No image data available")
        
        # Check if this is an image-only upload
        is_image_only = feedback_text.startswith("Image-only upload:")
        
        if is_image_only:
            prompt = f"""
            You are an assistant that extracts structured feedback data from jewellery store customer images.
            
            An image file '{current_image_data['filename']}' has been uploaded for customer feedback analysis.{image_context}
            
            Extract as JSON with the following fields:
            {{
                "purchased": "Yes" | "No" | null,
                "salesperson_name": string or null,
                "item_type": "Bangle" | "Chain" | "Bracelet" | "Necklace" | "Earring" | "Ring" | "Pendant Set" | "Stud" | "Locket" | "Hand Chain" | "Nose Pin" | "Mangal Sutra" | "Thali" | "Band Ring" | null,
                "metal_type": "22K" | "18K" | "24K" | "Diamond" | "Other" | null,
                "reason_price": "Yes" | "No" | null,
                "reason_size": "Yes" | "No" | null,
                "reason_weight": "Yes" | "No" | null,
                "reason_zeromaking": "Yes" | "No" | null,
                "reason_design_outofstock": "Yes" | "No" | null,
                "reason_design_new": "Yes" | "No" | null,
                "required_size": number or null,
                "required_weight": number or null,
                "available_size": number or null,
                "available_weight": number or null,
                "asked_price": number or null,
                "given_price": number or null,
                "design_type": "Coins / Bars" | "Daily Wear" | "Custom Order" | "Bridal jewellery" | "Kids Jewellery" | "Men's Jewellery" | "Temple" | "Antique" | "Turkish" | "Calcutta" | "Delhi" | "Rajkot" | "Local" | "Singapore" | "Bombay" | "Italian" | null,
                "item_category": string or null,
                "customer_intent": "Just Looking" | "Serious Buyer" | "Price Checking" | "Return Customer" | null,
                "is_previous_cust": "Yes" | "No" | null,
                "type_of_customer": "tourist" | "resident" | "none" | null,
                "M_Source": "walkin" | "Social Media" | "Social Groups" | "Whatsup Groups" | "Corporates" | "Residential Cmty" | "Local Cmty" | "HNTW" | "Hotels" | "Tourism Companies" | "Tour Drivers" | "Other Tours Assctd cmpy" | "DGJG" | "Product Launch" | "Other" | "none" | null,
                "M_source_Tag": string or null,
                "design_preference": "Liked" | "Disliked" | "Neutral" | null,
                "store_impression": "Good" | "Poor" | "Neutral" | null,
                "customer_mood": "Happy" | "Frustrated" | "Neutral" | "Disappointed" | null,
                "customer_support": "Excellent" | "Good" | "Average" | "Poor" | null,
                "purchase_satisfaction": "Very Satisfied" | "Satisfied" | "Neutral" | "Dissatisfied" | null,
                "waiting_time": "Very Fast" | "Fast" | "Average" | "Slow" | "Very Slow" | null,
                "original_text": "Image-only upload: {current_image_data['filename']}",
                "contact_number": string or null
            }}
            
            Since this is an image-only upload, analyze the image context and extract any visible information about:
            - Jewelry items shown
            - Customer interactions
            - Store environment
            - Any text or labels visible in the image
            
            If a field cannot be determined from the image, set it to null.
            Return ONLY valid JSON without any markdown formatting or code blocks.
            """
        else:
            prompt = f"""
            You are an assistant that extracts structured feedback data from jewellery store customer conversations.
            
            Analyze this text:
            "{feedback_text}"{image_context}
            
            Extract as JSON with the following fields:
            {{
                "purchased": "Yes" | "No" | null,
                "salesperson_name": string or null,
                "item_type": "Bangle" | "Chain" | "Bracelet" | "Necklace" | "Earring" | "Ring" | "Pendant Set" | "Stud" | "Locket" | "Hand Chain" | "Nose Pin" | "Mangal Sutra" | "Thali" | "Band Ring" | null,
                "metal_type": "22K" | "18K" | "24K" | "Diamond" | "Other" | null,
                "reason_price": "Yes" | "No" | null,
                "reason_size": "Yes" | "No" | null,
                "reason_weight": "Yes" | "No" | null,
                "reason_zeromaking": "Yes" | "No" | null,
                "reason_design_outofstock": "Yes" | "No" | null,
                "reason_design_new": "Yes" | "No" | null,
                "required_size": number or null,
                "required_weight": number or null,
                "available_size": number or null,
                "available_weight": number or null,
                "asked_price": number or null,
                "given_price": number or null,
                "design_type": "Coins / Bars" | "Daily Wear" | "Custom Order" | "Bridal jewellery" | "Kids Jewellery" | "Men's Jewellery" | "Temple" | "Antique" | "Turkish" | "Calcutta" | "Delhi" | "Rajkot" | "Local" | "Singapore" | "Bombay" | "Italian" | null,
                "item_category": string or null,
                "customer_intent": "Just Looking" | "Serious Buyer" | "Price Checking" | "Return Customer" | null,
                "is_previous_cust": "Yes" | "No" | null,
                "type_of_customer": "tourist" | "resident" | "none" | null,
                "M_Source": "walkin" | "Social Media" | "Social Groups" | "Whatsup Groups" | "Corporates" | "Residential Cmty" | "Local Cmty" | "HNTW" | "Hotels" | "Tourism Companies" | "Tour Drivers" | "Other Tours Assctd cmpy" | "DGJG" | "Product Launch" | "Other" | "none" | null,
                "M_source_Tag": string or null,
                "design_preference": "Liked" | "Disliked" | "Neutral" | null,
                "store_impression": "Good" | "Poor" | "Neutral" | null,
                "customer_mood": "Happy" | "Frustrated" | "Neutral" | "Disappointed" | null,
                "customer_support": "Excellent" | "Good" | "Average" | "Poor" | null,
                "purchase_satisfaction": "Very Satisfied" | "Satisfied" | "Neutral" | "Dissatisfied" | null,
                "waiting_time": "Very Fast" | "Fast" | "Average" | "Slow" | "Very Slow" | null,
                "original_text": string,
                "contact_number": string or null
            }}
            
            Important distinction for design fields:
            - "reason_design_outofstock": Customer wanted a design that exists in catalog but is currently out of stock
            - "reason_design_new": Customer requested a new/custom design that does not exist in the catalog
            
            Valid item_type values: "Bangle", "Chain", "Bracelet", "Necklace", "Earring", "Ring", "Pendant Set", "Stud", "Locket", "Hand Chain", "Nose Pin", "Mangal Sutra", "Thali", "Band Ring"
            Valid design_type values: "Coins / Bars", "Daily Wear", "Custom Order", "Bridal jewellery", "Kids Jewellery", "Men's Jewellery", "Temple", "Antique", "Turkish", "Calcutta", "Delhi", "Rajkot", "Local", "Singapore", "Bombay", "Italian"
            
            If a field is not mentioned, set it to null.
            Return ONLY valid JSON without any markdown formatting or code blocks.
            """
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.choices[0].message.content.strip()
        
        # Clean the response - remove markdown formatting
        if text.startswith("```json"):
            text = text[7:]  # Remove ```json
        if text.startswith("```"):
            text = text[3:]   # Remove ```
        if text.endswith("```"):
            text = text[:-3]  # Remove trailing ```
        
        text = text.strip()
        
        # Parse JSON to ensure it's valid
        try:
            parsed_data = json.loads(text)
            print(f"Feedback extraction successful: {len(parsed_data)} fields extracted")
            
            # FORCE image_url after AI extraction (override any AI-generated values)
            # This is handled separately in app.py and should NOT be modified by AI
            if image_url:
                parsed_data["image_url"] = image_url
                print(f"[AGENT] FORCED image_url to: {image_url} (overriding AI value if any)")
            
            print(f"[AGENT] Final image_url in parsed_data: {parsed_data.get('image_url')}")
            
            return parsed_data  # Return dictionary, not string
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            print(f"Raw response: {text}")
            # Return a fallback structure
            return {
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
                "original_text": feedback_text,  # Store original text
                "contact_number": None,
                "image_url": image_url
            }
        
    except Exception as e:
        print(f"Feedback extraction error: {e}")
        return {
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
            "design_preference": None,
            "store_impression": None,
            "customer_mood": None,
            "customer_support": None,
            "purchase_satisfaction": None,
            "waiting_time": None,
            "original_text": f"Error extracting feedback: {e}",
            "contact_number": None,
            "image_url": image_url
        }

# Register tools
tools = [
    Tool(name="convert_audio_format", func=convert_audio_format, description="Convert uploaded audio to WAV."),
    Tool(name="transcribe_audio", func=transcribe_audio, description="Transcribe audio to text."),
    Tool(name="extract_feedback", func=extract_feedback, description="Extract structured data from transcribed text."),
    Tool(name="save_feedback", func=save_feedback, description="Save structured feedback data into CRM MongoDB database.")
]

current_audio_file = None
current_image_data = None
agent = initialize_agent(
    tools,
    llm,
    agent_type="zero-shot-react-description",
    verbose=False,  # Disable verbose output to prevent Unicode issues
    handle_parsing_errors=True,
)

def process_audio_with_agent(audio_file, filename="audio_file", image_data=None):
    global current_audio_file
    
    # Set the global audio file and ensure it has proper attributes
    current_audio_file = audio_file
    if hasattr(audio_file, 'name'):
        audio_file.name = filename
    else:
        audio_file.name = filename
    
    print(f"Audio file set globally: {filename}, size: {len(audio_file.getvalue()) if hasattr(audio_file, 'getvalue') else 'unknown'}")
    
    # Store image data globally for tools to access
    global current_image_data
    current_image_data = image_data
    if image_data:
        print(f"[AGENT] Image data received: filename={image_data.get('filename')}, size={image_data.get('size')} bytes")
        print(f"[AGENT] Image URL in image_data: {image_data.get('image_url')}")
        print(f"[AGENT] Unique filename in image_data: {image_data.get('unique_filename')}")
    else:
        print(f"[AGENT] No image data received")

    prompt = f"""
    The file '{filename}' contains a salesperson-customer conversation.
    {"An image file is also provided for additional context." if image_data else ""}

    You MUST use the provided tools in this exact order:
    1) convert_audio_format  - convert current audio to WAV if needed
    2) transcribe_audio      - get transcript text
    3) extract_feedback      - produce STRICT JSON with required CRM fields from the transcript
    4) save_feedback         - PERSIST the extracted JSON in the database

    Rules:
    - Do not claim any step is done unless you actually called the tool.
    - Finalize ONLY after save_feedback returns a result. Your final answer must reflect the save_feedback response.
    - If any step fails, try alternatives (e.g., skip conversion if already WAV) and then continue.
    - Never make up data; only extract what is present.
    - Include image information in the feedback if an image was provided.

    The audio file is already loaded and available to all tools; start with convert_audio_format.
    """

    try:
        # Use invoke instead of deprecated run method
        result = agent.invoke({"input": prompt})
        return {"status": "success", "message": "Processed successfully", "agent_result": result}
    except UnicodeEncodeError as unicode_error:
        print(f"Unicode encoding error caught: {unicode_error}")
        return {"status": "error", "error": f"Unicode encoding error: {unicode_error}"}
    except Exception as e:
        print(f"Agent error: {e}")
        return {"status": "error", "error": str(e)}
