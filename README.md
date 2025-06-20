# 🧠 SmartLab – Smart Attendance Management System

**SmartLab** is an innovative solution for efficient and accurate **student attendance management**. It combines a user-friendly **Tkinter desktop interface** with a lightweight **Flask web backend** and stores data securely in **MariaDB/MySQL**.

SmartLab is an innovative solution designed to streamline and enhance student attendance management in educational institutions. Leveraging advanced technologies, SmartLab enables efficient, accurate, and automated tracking of student attendance, reducing manual workload and minimizing errors. The platform provides a user-friendly interface, robust reporting features, and seamless integration with existing systems, making it an ideal tool for educators and administrators seeking to modernize their attendance processes.

---

## 🚀 Key Features

- 📌 **Session ID-Based Attendance:** Track sessions using unique IDs  
- 🖥️ GUI Desktop Interface (Tkinter) for faculty-side operations  
- 🌐 Flask web backend to manage attendance endpoints  
- 🗃️ MariaDB/MySQL for fast and reliable data storage  
- 📊 View attendance logs in real-time  
- ✅ Includes EXE build option for Windows deployment  

---

## 🗂️ Project Structure

```
smartlab/
│
├── Desktop/           # Tkinter-based GUI logic
├── web/               # Flask backend files and routes
├── db/                # SQL dump or scripts for MariaDB/MySQL setup
├── dfd/               # Data Flow Diagrams (DFD)
├── myenv/             # Python virtual environment (optional)
├── requirements.txt   # Python dependencies
├── usefull.txt        # Notes (e.g., PyInstaller, setup)
└── README.md          # Project documentation
```

---

## ⚙️ How to Set Up and Run

### 1. Clone the Repository

```bash
git clone https://github.com/vishalvnair124/smartlab.git
cd smartlab
```

### 2. Set Up Virtual Environment (Optional but Recommended)

```bash
python -m venv myenv
source myenv/bin/activate            # Windows: myenv\Scripts\activate
```

### 3. Install Python Requirements

```bash
pip install -r requirements.txt
```

### 4. Set Up the Database

- Create a new database in **MariaDB/MySQL**
- Run the SQL script located in the `db/` folder to create required tables and seed data
- Update DB credentials in both desktop and Flask app (`conn.py`, `config.py`, etc.)

### 5. Run the Flask Web Server

```bash
cd web
python app.py
```

It will start the Flask app (usually at `http://127.0.0.1:5000`).

### 6. Run the Tkinter Desktop App

```bash
cd ../Desktop
python main.py
```

*(Replace `main.py` with the actual filename if different)*

---

## 🧑‍💻 Tech Stack

| Component   | Technology         |
|------------|--------------------|
| GUI        | Python (Tkinter)   |
| Backend    | Python (Flask)     |
| Database   | MariaDB / MySQL    |
| Packaging  | PyInstaller        |
| Diagrams   | DFDs (PDF/Image)   |

---

## 📌 Useful Notes

- ✅ `usefull.txt` contains PyInstaller `.exe` creation steps  
- 🗃️ `requirements.txt` ensures smooth setup in any environment  
- 🖼️ `dfd/` folder includes system-level flow understanding  

---

## 🧠 Future Enhancements

- 🔐 Login system with user roles (Admin, Faculty)  
- 📤 Attendance export to Excel or PDF  
- 🔍 Search/filter by student or session  
- 🌐 Full web dashboard with analytics and remote access  
- 📲 Integration with mobile attendance app (future)

---

## 👨‍💻 Developed By

**Vishal V Nair**  
🚀 MCA @ TKM | Tech Enthusiast  
🔧 Skilled in Python | Flask | Tkinter | MySQL  
📫 GitHub: [@vishalvnair124](https://github.com/vishalvnair124)

---


