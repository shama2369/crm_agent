# CRM Agent - AI-Powered Voice Capture System

An intelligent CRM system that uses AI to extract structured customer feedback from salesperson audio recordings. Built with FastAPI, LangChain, and OpenAI Whisper for audio transcription and data extraction.

## 🎯 Features

- **Audio Recording & Transcription**: Record customer interactions via microphone and automatically transcribe using OpenAI Whisper
- **Image Upload**: Upload customer photos with unique timestamped filenames
- **AI-Powered Data Extraction**: Extract 30+ structured fields from audio using LangChain and GPT-4
- **Dual Dashboard Views**: 
  - **Purchase Mode**: View customers who made purchases
  - **Sales Mode**: View all customer interactions (purchases and non-purchases)
- **Advanced Filtering**: Filter by salesperson, customer intent, item type, design, and more
- **MongoDB Integration**: Store feedback data with automatic fallback to local JSON files
- **Image Management**: Automatic image storage and deletion with records

## 📋 Prerequisites

- Python 3.8+
- MongoDB (optional, falls back to local JSON files if not available)
- OpenAI API key

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/shama2369/crm_agent.git
   cd crm_agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   MONGODB_URI=mongodb://localhost:27017
   DATABASE_NAME=crm_agent
   COLLECTION_NAME=feedback
   ```

4. **Configure image storage directory**
   Update `IMAGES_DIR` in `app.py` (line 18) to your desired path:
   ```python
   IMAGES_DIR = Path("C:\\Users\\shama\\Projects\\crm_agent_images").resolve()
   ```

## 🏃 Running the Application

### Option 1: Using the batch file (Windows)
```bash
run_server.bat
```

### Option 2: Manual start
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:
- **Frontend**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

## 📁 Project Structure

```
crm_agent/
├── app.py                 # FastAPI application and API endpoints
├── agent.py              # LangChain agent for audio processing
├── db.py                 # Database operations (MongoDB/JSON fallback)
├── dashboard.html        # Frontend dashboard UI
├── frontend.html         # Main frontend page
├── requirements.txt      # Python dependencies
├── setup.py             # Setup script
├── run_server.bat       # Windows server startup script
├── FIELD_DOCUMENTATION.md    # Complete field reference (30 fields)
├── RECORDING_GUIDE.md        # Guide for salespersons
├── IMAGE_FLOW_LOGIC.md       # Image upload/storage documentation
└── flow_diagram.md           # System architecture diagram
```

## 🔌 API Endpoints

### `POST /process_audio`
Process audio recording and extract customer feedback.

**Request:**
- `file`: Audio file (multipart/form-data)
- `image`: Image file (optional, multipart/form-data)

**Response:**
```json
{
  "status": "success",
  "feedback_id": "uuid",
  "image_url": "/images/timestamp_filename.jpg",
  "image_debug": {
    "image_url": "/images/timestamp_filename.jpg",
    "unique_filename": "timestamp_filename.jpg",
    "original_filename": "original.jpg",
    "image_saved": true
  }
}
```

### `GET /api/feedback/purchase`
Get all purchase records.

### `GET /api/feedback/sales`
Get all sales records (purchases and non-purchases).

### `GET /images/{filename}`
Serve image files.

### `DELETE /api/feedback/{feedback_id}`
Delete a feedback record and associated image.

### `GET /health`
Health check endpoint.

## 📊 Data Fields (30 Fields)

The system extracts 30 structured fields from audio recordings:

### Core Customer Information
- `purchased`: Did customer make a purchase?
- `salesperson_name`: Salesperson handling the customer
- `contact_number`: Customer's phone number

### Customer Classification
- `customer_intent`: "Just Looking", "Serious Buyer", "Price Checking", "Return Customer"
- `is_previous_cust`: Is customer existing POS customer?
- `type_of_customer`: "tourist", "resident", "none"
- `M_Source`: Marketing source/channel (walkin, Social Media, Hotels, etc.)
- `M_source_Tag`: Additional marketing source tag

### Product Details
- `item_type`: Bangle, Chain, Bracelet, Necklace, Earring, Ring, etc.
- `metal_type`: 22K, 18K, 24K, Diamond, Other
- `design_type`: Coins/Bars, Daily Wear, Custom Order, Bridal jewellery, etc.
- `item_category`: Wedding, Casual, Formal

### Size & Weight
- `required_size`: Size customer needed
- `required_weight`: Weight customer wanted (grams)
- `available_size`: Size available in store
- `available_weight`: Weight available

### Pricing
- `asked_price`: Price customer asked for
- `given_price`: Price offered by store

### Non-Purchase Reasons
- `reason_price`: Was price the reason?
- `reason_size`: Was size the reason?
- `reason_weight`: Was weight the reason?
- `reason_zeromaking`: Was zero making charge the reason?
- `reason_design_outofstock`: Was design out of stock?
- `reason_design_new`: Did customer request new design?

### Customer Experience
- `design_preference`: Liked, Disliked, Neutral
- `customer_mood`: Positive, Neutral, Negative
- `store_impression`: Positive, Neutral, Negative

### Metadata
- `timestamp`: Record creation timestamp
- `image_url`: Path to uploaded customer image

For complete field documentation, see [FIELD_DOCUMENTATION.md](FIELD_DOCUMENTATION.md).

## 📝 Usage Guide

### For Salespersons

1. **Open the dashboard** at http://127.0.0.1:8000
2. **Record audio** by clicking the microphone button
3. **Speak clearly** about the customer interaction (see [RECORDING_GUIDE.md](RECORDING_GUIDE.md))
4. **Upload customer photo** (optional)
5. **Submit** - AI will extract all relevant information automatically

### Recording Tips

- Clearly state customer name, contact number, and salesperson name
- Mention item type, design, size, and weight preferences
- Note pricing discussions (asked price vs. given price)
- Explain reasons for purchase/non-purchase
- Describe customer mood and preferences

See [RECORDING_GUIDE.md](RECORDING_GUIDE.md) for detailed recording guidelines.

## 🔧 Configuration

### MongoDB Setup (Optional)

If MongoDB is not available, the system automatically falls back to storing data in `feedback_data/` directory as JSON files.

### Image Storage

Images are stored in the directory specified by `IMAGES_DIR` in `app.py`. Images are automatically:
- Renamed with timestamps: `{timestamp}_{original_filename}`
- Stored with unique filenames
- Deleted when associated records are deleted

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **AI/ML**: LangChain, OpenAI GPT-4, Whisper API
- **Database**: MongoDB (with JSON fallback)
- **Frontend**: HTML, CSS, JavaScript
- **Audio Processing**: pydub
- **Server**: Uvicorn

## 📚 Documentation

- [FIELD_DOCUMENTATION.md](FIELD_DOCUMENTATION.md) - Complete field reference
- [RECORDING_GUIDE.md](RECORDING_GUIDE.md) - Audio recording guide for salespersons
- [IMAGE_FLOW_LOGIC.md](IMAGE_FLOW_LOGIC.md) - Image upload and storage flow
- [flow_diagram.md](flow_diagram.md) - System architecture diagram

## 🐛 Troubleshooting

### Images not displaying
- Check that `IMAGES_DIR` path exists and is writable
- Verify image URLs in MongoDB are in format `/images/{filename}`
- Check browser console for 404 errors

### Audio transcription fails
- Verify `OPENAI_API_KEY` is set correctly
- Check audio file format (supports WAV, MP3, M4A, etc.)
- Ensure audio file is not corrupted

### MongoDB connection issues
- System will automatically fall back to JSON file storage
- Check `MONGODB_URI` in `.env` file
- Verify MongoDB is running (if using local instance)

## 📄 License

This project is private and proprietary.

## 👤 Author

**shama2369**

## 🔗 Repository

https://github.com/shama2369/crm_agent

---

**Note**: Remember to keep your `.env` file secure and never commit it to version control. The `.gitignore` file is configured to exclude sensitive files.

