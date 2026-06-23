  **AI Resume Analyzer & ATS Scoring System** 

An AI-powered Resume Analyzer web application built using Flask and Python that helps users evaluate resumes based on job roles, technical skills, and ATS (Applicant Tracking System) standards.

This project analyzes uploaded resumes, calculates skill match percentage, checks ATS compatibility, and provides improvement suggestions through an interactive dashboard.

---

  **Features**

1. **Resume Analysis**
- Upload resumes in PDF or DOCX format
- Extract resume text automatically
- Analyze resumes for different technical roles

2. **🎯ATS Score Checker**
- Checks:
  - Email presence
  - Phone number
  - Skills section
  - Projects section
  - Experience section
  - Resume length
  - Generates ATS compatibility score

3. **AI-Based Skill Matching**
- Detects matching and missing skills
- Supports multiple job roles:
  - Python Developer
  - Full Stack Developer
  - Web Developer
  - Data Analyst
  - DevOps Engineer
  - Machine Learning Engineer
  - And more...

4. **Admin Analytics Dashboard**
- Total resume analysis count
- Average resume score
- Role distribution chart
- Resume history records

5. **📥Export Features**
- Download PDF analysis reports
- Export records to CSV

6.** 🔐 Authentication System**
- Secure admin login
- Password hashing
- Session management

-----------------------------------------------------------

**🛠 Tech Stack**

1. **Backend**
- Python
- Flask
- SQLite

2. **Frontend**
- HTML
- CSS
- JavaScript
- Chart.js

3. **Libraries Used**
- PyPDF2
- python-docx
- ReportLab
- Werkzeug

-------------------------------------------------------

# **📂 Project Structure**

```bash
AI-Resume-Analyzer/
│
├── app.py
├── database.db
├── requirements.txt
├── README.md
│
├── templates/
│   ├── index.html
│   ├── result.html
│   ├── admin.html
│   └── login.html
│
├── static/
│
├── uploads/
│
└── screenshots/
```

---
live: https://ai-resume-analyzer-tguj.onrender.com/

# ⚙️ Installation

## **1️⃣ Clone Repository**

```bash
git clone https://github.com/your-username/AI-Resume-Analyzer.git
```

------------------------------------------------------------------

## **2️⃣ Open Project Folder**

```bash
cd AI-Resume-Analyzer
```

-------------------------------------------------------------------

## **3️⃣ Create Virtual Environment**

```bash
python -m venv venv
```
------------------------------------------------------------------

## **4️⃣ Activate Virtual Environment**

### **Windows**
```bash
venv\Scripts\activate
```

### **Mac/Linux**
```bash
source venv/bin/activate
```

---

## **5️⃣ Install Dependencies**

```bash
pip install -r requirements.txt
```

---

## **6️⃣ Run Application**

```bash
python app.py
```

---

# **🌐 Default Admin Login**

```text
Username: admin
Password: admin123
```

---

# **📸 Screenshots**

Add your project screenshots inside the `screenshots` folder.

Suggested screenshots:
- Home Page
- Resume Result Page
- ATS Score
- Admin Dashboard

---

# 📈 Future Improvements

- AI Resume Ranking
- Real Machine Learning Integration
- Resume Recommendation Engine
- Dark/Light Mode
- Online Deployment

---

# 👨‍💻 Author

**## Vivek Badoni**

BSc Information Technology Student  
Interested in Full Stack Development, Python, AI Tools, and Web Applications.

GitHub: https://github.com/Vivek-Badoni

---

# 📄 License

This project is developed for educational and portfolio purposes.
