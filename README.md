# 📋 Job Card Pro

A modern, attractive Job Card Management System with a beautiful Streamlit frontend and MySQL backend. Generate professional PDF documents with ease.

![Job Card Pro](https://img.shields.io/badge/Version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)

## ✨ Features

- **🎨 Modern UI**: Beautiful, responsive design with gradients, shadows, and animations
- **💾 MySQL Backend**: Full CRUD operations with database storage
- **📄 Premium PDF**: Generate professional, print-ready PDF documents
- **📱 QR Codes**: Auto-generated QR codes for job card identification
- **🔍 Advanced Search**: Search by vendor, date range, or any field
- **📊 Analytics**: Dashboard with statistics and trends
- **📦 Multi-item Support**: Add multiple items, materials, and GRN entries
- **⚙️ Operations Checklist**: Track manufacturing operations
- **✅ Quality Control**: Quality instructions and QC tracking

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd job-card-pro
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up MySQL Database

Make sure MySQL is installed and running. Create a database:

```sql
CREATE DATABASE job_card_db;
```

### 4. Configure Environment Variables (Optional)

You can configure the database connection using environment variables:

```bash
# Linux/macOS
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=job_card_db

# Windows (Command Prompt)
set DB_HOST=localhost
set DB_PORT=3306
set DB_USER=root
set DB_PASSWORD=your_password
set DB_NAME=job_card_db

# Windows (PowerShell)
$env:DB_HOST="localhost"
$env:DB_PORT="3306"
$env:DB_USER="root"
$env:DB_PASSWORD="your_password"
$env:DB_NAME="job_card_db"
```

Or create a `.env` file:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=job_card_db
```

### 5. Run the Application

```bash
python main.py
```

The application will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
job-card-pro/
├── main.py              # Main application entry point
├── database.py          # MySQL database operations
├── pdf_generator.py     # Premium PDF generation
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── .env                 # Environment variables (create this)
```

## 🖥️ Application Screenshots

### Dashboard
- Beautiful hero section with gradient background
- Real-time statistics cards
- Quick action buttons
- Feature highlights

### Job Card Form
- Tabbed interface for easy navigation
- Company and vendor information
- Item and material management
- Operations checklist
- Quality instructions
- GRN/QC tracking

### PDF Output
- Professional header with company branding
- Color-coded sections
- QR codes for quick reference
- Signature areas
- Page numbers

## 🔧 Configuration

### Database Configuration

The application uses the following environment variables for database connection:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | localhost | MySQL server host |
| `DB_PORT` | 3306 | MySQL server port |
| `DB_USER` | root | Database username |
| `DB_PASSWORD` | (empty) | Database password |
| `DB_NAME` | job_card_db | Database name |

### Application Configuration

You can modify the following in the code:

- **Color Scheme**: Edit the CSS variables in `main.py`
- **PDF Layout**: Modify `pdf_generator.py`
- **Database Schema**: Update `database.py`

## 📝 Usage Guide

### Creating a New Job Card

1. Click "New Job Card" in the sidebar
2. Fill in the company and vendor details
3. Add items to the job card
4. Add materials issued
5. Select required operations
6. Add quality instructions
7. Save to database or generate PDF

### Searching Job Cards

1. Click "Search" in the sidebar
2. Use date range search for specific periods
3. Search by vendor ID or name
4. View and manage results

### Generating PDF

1. Create or open a job card
2. Click "Generate PDF"
3. Download the PDF file

## 🛠️ Technologies Used

- **Python 3.8+**: Programming language
- **Streamlit**: Web framework
- **MySQL**: Database
- **ReportLab**: PDF generation
- **Pillow**: Image processing
- **QRCode**: QR code generation
- **Pandas**: Data manipulation

## 📦 Dependencies

See `requirements.txt` for all dependencies:

```
streamlit>=1.28.0
mysql-connector-python>=8.2.0
pandas>=2.0.0
pillow>=10.0.0
qrcode>=7.4.0
reportlab>=4.0.0
streamlit-option-menu>=0.3.6
```

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Use strong database passwords
- Consider using secrets management for production
- The application is for demonstration; add authentication for production use

## 🐛 Troubleshooting

### Database Connection Issues

1. Make sure MySQL is running
2. Check your credentials
3. Verify the database exists
4. Check firewall settings

### PDF Generation Fails

1. Ensure ReportLab is installed
2. Check if you have write permissions
3. Verify all data is properly formatted

### UI Issues

1. Clear browser cache
2. Try a different browser
3. Ensure JavaScript is enabled

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Created with ❤️ for modern manufacturing management.

## 🆘 Support

For support, please open an issue on GitHub.

---

Made with ❤️ using Streamlit and MySQL
