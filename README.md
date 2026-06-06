# Bill Management Application

A comprehensive bill management system that helps organize and rename bills based on company name, bill number, and vehicle number.

## Features

- **Bill Upload**: Upload bills/documents to the application
- **Auto-Rename**: Automatically rename bills based on company name, bill number, or vehicle number
- **Extract Metadata**: Extract key information from bills using OCR
- **Manual Override**: Allow users to manually adjust names if extraction fails
- **Search & Filter**: Easily search and filter bills by company, bill number, or vehicle
- **Organize**: Keep all bills organized and easy to find
- **Export**: Export organized bill data for accounting purposes

## Project Structure

```
bill-management-app/
├── frontend/              # Web interface
├── backend/               # API and business logic
├── database/              # Database schemas
├── docs/                  # Documentation
└── tests/                 # Test files
```

## Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Backend**: Python with Flask
- **Database**: SQLite
- **OCR**: Tesseract (optional for advanced extraction)

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. Open browser to `http://localhost:5000`

## Installation

```bash
git clone https://github.com/akshatgupta665/Akshat-Gupta.git
cd Akshat-Gupta
pip install -r requirements.txt
python app.py
```

## Usage

1. **Upload Bills**: Click "Upload" to add new bills
2. **Configure Naming**: Set naming rules (Company, Bill No, Vehicle No)
3. **Auto-Rename**: System automatically renames based on extracted data
4. **Search**: Use search bar to find bills quickly
5. **Export**: Export organized data for records

## File Naming Convention

Default format: `{CompanyName}_{BillNo}_{VehicleNo}.pdf`

Example: `Acme_Corp_INV123_AB1234.pdf`

## Contributing

Feel free to fork, modify, and submit pull requests!

## License

MIT License - See LICENSE file for details
