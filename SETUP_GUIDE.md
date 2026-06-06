# Bill Management Application - Setup Guide

## Overview

This is a comprehensive bill management system built with Flask that automatically organizes and renames bills based on extracted information like company name, bill number, and vehicle number.

## Features

✅ **Automatic Bill Extraction** - Extracts text from PDFs and images using OCR
✅ **Smart Renaming** - Auto-renames bills based on company, bill number, vehicle
✅ **Search Functionality** - Quickly find bills by any parameter
✅ **Beautiful UI** - Modern, responsive interface with Bootstrap
✅ **Database Storage** - SQLite database for persistent storage
✅ **Drag & Drop** - Easy file upload with drag and drop support

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Tesseract OCR (optional, for image text extraction)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/akshatgupta665/Akshat-Gupta.git
cd Akshat-Gupta
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Tesseract (Optional, for OCR)

**Windows:**
Download installer from: https://github.com/UB-Mannheim/tesseract/wiki

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

## Running the Application

```bash
python app.py
```

The application will be available at: **http://localhost:5000**

## Usage

### Upload Bills

1. Click on the upload area or drag and drop files
2. Supported formats: PDF, PNG, JPG, JPEG, GIF
3. The system automatically extracts information and renames the file

### Example Renaming

- **Original:** Invoice_2026.pdf
- **Renamed:** Acme_Corp_INV123_AB1234.pdf

### Search Bills

Use the search tab to find bills by:
- Company name
- Bill number
- Vehicle number
- Original filename

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── bills.db              # SQLite database (auto-created)
├── templates/
│   └── index.html        # Frontend HTML
├── uploads/              # Uploaded files storage
├── README.md             # Documentation
└── SETUP_GUIDE.md        # This file
```

## API Endpoints

### Upload Bill
```
POST /api/upload
Content-Type: multipart/form-data
Body: file (binary)
```

### Get All Bills
```
GET /api/bills
```

### Get Single Bill
```
GET /api/bills/<id>
```

### Update Bill
```
PUT /api/bills/<id>
Body: { company_name, bill_number, vehicle_number, notes }
```

### Delete Bill
```
DELETE /api/bills/<id>
```

### Search Bills
```
GET /api/search?q=<query>
```

## Database Schema

### bills table

| Column | Type | Description |
|--------|------|----------|
| id | INTEGER | Primary key |
| original_filename | TEXT | Original uploaded filename |
| renamed_filename | TEXT | Auto-generated renamed filename |
| company_name | TEXT | Extracted company name |
| bill_number | TEXT | Extracted bill number |
| vehicle_number | TEXT | Extracted vehicle number |
| file_path | TEXT | Path to uploaded file |
| uploaded_date | TIMESTAMP | Upload timestamp |
| notes | TEXT | User notes |

## Configuration

Edit the following in `app.py` to customize:

```python
# Maximum file size (default: 100MB)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Allowed file extensions
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'
```

## Naming Convention

The application generates filenames in the format:

```
{CompanyName}_{BillNumber}_{VehicleNumber}.{ext}
```

Example: `Toyota_Finance_INV789456_MH02AB1234.pdf`

## Troubleshooting

### Issue: OCR not working
- Ensure Tesseract is installed
- Check pytesseract configuration

### Issue: Files not uploading
- Check file size (max 100MB)
- Verify file format is supported
- Check `uploads/` folder permissions

### Issue: Database error
- Delete `bills.db` to reset database
- Check write permissions in project directory

## Future Enhancements

- 🔐 User authentication
- 📊 Analytics dashboard
- 📧 Email integration
- ☁️ Cloud storage support
- 🔔 Duplicate bill detection
- 📱 Mobile app
- 🔄 Batch processing

## Support

For issues or questions, please create an issue in the GitHub repository.

## License

MIT License - See LICENSE file for details