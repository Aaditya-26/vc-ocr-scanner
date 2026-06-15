# VC OCR Scanner

A web application that scans visiting card images and extracts contact information automatically using OCR.
Built with Django, Django REST Framework, EasyOCR, MySQL, and HTML/CSS/JavaScript.

---

## Features

- Upload visiting card images (JPG, PNG, PDF)
- Auto-extract Name, Mobile, Email, Company, Designation, Website, Address
- Duplicate detection by email or mobile number
- Manual correction of extracted fields
- Contact dashboard with search
- REST API built with DRF

---

## Tech Stack

- Backend: Python, Django, Django REST Framework
- OCR: EasyOCR
- Database: MySQL
- Frontend: HTML, CSS, JavaScript

---

## Setup

**1. Clone the repo**
```
git clone https://github.com/Aaditya-26/vc-ocr-scanner.git
cd vc-ocr-scanner
```

**2. Create virtual environment**
```
python -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```
pip install -r requirements.txt
```

**4. Create MySQL database**
```
CREATE DATABASE vc_ocr_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**5. Update settings**

Open `config/settings.py` and set your MySQL username and password.

**6. Run migrations**
```
python manage.py makemigrations
python manage.py migrate
```

**7. Start the server**
```
python manage.py runserver
```

Open `http://127.0.0.1:8000` in your browser.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/visiting-card/upload/ | Upload card and run OCR |
| GET | /api/v1/contacts/ | List all contacts |
| GET | /api/v1/contact/id/ | Get single contact |
| PUT | /api/v1/contact/id/ | Update contact fields |
| DELETE | /api/v1/contact/id/delete/ | Delete a contact |

---

## Project Structure

```
vc_ocr/
├── config/
│   ├── settings.py
│   └── urls.py
├── vc_app/
│   ├── templates/
│   ├── static/
│   ├── utils/
│   │   └── extractor.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── ocr_service.py
│   └── urls.py
├── manage.py
└── requirements.txt
```

---

## Notes

- First upload will be slow — EasyOCR downloads its model (~100 MB) on first use. This only happens once.
- Do not use the development server in production.