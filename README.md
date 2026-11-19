# Academic-Performance-Tracker

> A minimalist, production-styled web portal for college internal assessment evaluation, batch-wise analytics, and dynamic student ranking.

Built with **Python (Flask)** on the backend and pure **HTML5 / Vanilla CSS / JavaScript (Fetch API)** on the frontend — **no databases (SQLite/MongoDB), no React, and no external CSS frameworks (Bootstrap/Tailwind)**.

---

## ⚡ 2-Step Quickstart Guide

### Step 1: Install Dependencies
Open your terminal in the project directory and run:
```bash
pip install -r requirements.txt
```

### Step 2: Launch Application
Run the Flask server:
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📁 5-File Architecture

```text
Academic Performance Tracker/
│
├── logic.py               # Data models, 32 subjects, 60 students, seeded generator & analytics
├── app.py                 # Flask server, route controllers & REST API endpoints
├── templates/
│   └── index.html         # Clean portal UI, modal dialog, 4 stats cards & leaderboard table
├── static/
│   ├── style.css          # Pure custom CSS, modal overlays, badges & responsive grid
│   └── script.js          # Modal controls, strict dropdown coupling & Fetch API integration
├── requirements.txt       # Dependencies (Flask)
└── README.md              # Documentation, API contracts & Viva defense guide
```

---

## 🏛️ Academic Hierarchy & Subject Mapping

The portal implements strict **Year $\rightarrow$ Semester $\rightarrow$ Subject** coupling. Impossible combinations (e.g., Year 1 + Semester 3) are physically prevented in the UI and strictly rejected with HTTP 400 on the backend.

### 32 B.Tech Subjects (4 Subjects per Semester across 8 Semesters):

| Year | Semester | Subject Code & Title |
| :---: | :---: | :--- |
| **Year 1** | **Sem 1** | 1. Problem Solving using Python <br>2. Engineering Mathematics I <br>3. Physics for Engineers <br>4. Basic Electrical Engineering |
| **Year 1** | **Sem 2** | 1. Programming in C <br>2. Engineering Mathematics II <br>3. Engineering Chemistry <br>4. Basic Electronics |
| **Year 2** | **Sem 3** | 1. Data Structures and Algorithms <br>2. Discrete Mathematics <br>3. Digital Logic and Design <br>4. Object Oriented Programming in Java |
| **Year 2** | **Sem 4** | 1. Operating Systems <br>2. Computer Organization & Architecture <br>3. Database Management Systems <br>4. Theory of Computation |
| **Year 3** | **Sem 5** | 1. Design and Analysis of Algorithms <br>2. Computer Networks <br>3. Software Engineering <br>4. Microprocessors & Microcontrollers |
| **Year 3** | **Sem 6** | 1. Artificial Intelligence <br>2. Web Technologies & Frameworks <br>3. Compiler Design <br>4. Information Security |
| **Year 4** | **Sem 7** | 1. Machine Learning <br>2. Cloud Computing & DevOps <br>3. Distributed Systems <br>4. Internet of Things (IoT) |
| **Year 4** | **Sem 8** | 1. Deep Learning & NLP <br>2. Big Data Analytics <br>3. Cyber Security & Forensics <br>4. Blockchain Technology |

---

## 👥 Roll Numbers, Passing Years & Preloaded Dataset

A B.Tech degree is 4 years. Therefore, the 4-digit prefix of a roll number represents the **Admission Year**, and **Passing Year = Admission Year + 4**:

- **Batch 2027 (Admission 2023 | Year 4 Seniors):** `2023UCS1001` to `2023UCS1015` (Completed Semesters 1 through 8)
- **Batch 2028 (Admission 2024 | Year 3 Pre-Finals):** `2024UCS1001` to `2024UCS1015` (Completed Semesters 1 through 6)
- **Batch 2029 (Admission 2025 | Year 2 Sophomores):** `2025UCS1001` to `2025UCS1015` (Completed Semesters 1 through 4)
- **Batch 2030 (Admission 2026 | Year 1 Freshmen):** `2026UCS1001` to `2026UCS1015` (Completed Semesters 1 & 2)

> 💡 **Deterministic Seed:** Marks (`mid_sem`, `ct_viva`, `end_sem`) are populated via a clean generator in `logic.py` using `random.seed(42)`. This provides realistic evaluation records without manual clutter and remains identical every time the server boots.

### 🔒 Enforcing One Name Per Roll Number
1. **Auto-Fill & UI Locking:** Typing an existing student's roll number in the Add Student modal automatically queries `/api/student/<roll_number>`, auto-fills their registered Name and Passing Year, and locks the fields (`readOnly`/`disabled`) to prevent conflicting inputs.
2. **Backend Validation:** In `POST /api/students`, the server ensures that if a roll number exists, the submitted name and passing year match the existing student record (rejecting mismatches with HTTP `400`).

---

## 📊 Evaluation Scheme & Analytics

Each assessment is graded out of **100 Marks**:
- **Mid-Sem:** Maximum 20 Marks
- **CT & Lab Viva:** Maximum 30 Marks
- **End-Sem:** Maximum 50 Marks
- **Total:** $\text{mid\_sem} + \text{ct\_viva} + \text{end\_sem}$

### 4 Top Analytics Cards:
1. **Unique Students:** Distinct students matching the active filter vs. all 60 college students (counted by unique `roll_number`).
2. **Average Score:** Mean total score across the currently filtered view.
3. **Highest Score:** Top score achieved in the filtered view.
4. **Class Topper:** Roll Number, Name, and Score of the Rank 1 student.

---

## 🔌 REST API Endpoints (`app.py`)

| Method | Endpoint | Query Parameters | Description | Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | None | Serves portal single-page interface | `200 OK` (HTML) |
| `GET` | `/api/academic-structure` | None | Returns Year $\rightarrow$ Sem $\rightarrow$ Subject mappings | `200 OK` (JSON) |
| `GET` | `/api/student/<roll>` | None | Looks up student by roll number for auto-fill & locking | `200 OK` (JSON) |
| `GET` | `/api/students` | `passing_year`, `year`, `semester`, `subject` | Returns filtered student records & computed `stats` | `200 OK` (JSON) |
| `POST` | `/api/students` | None | Validates marks, hierarchy, 1-name rule & prevents duplicate subject assessments | `201 Created` or `400 Bad Request` |
| `DELETE` | `/api/students/<id>` | None | Deletes specific record by unique database ID | `200 OK` or `404 Not Found` |
