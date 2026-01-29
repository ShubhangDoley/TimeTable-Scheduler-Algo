# TimeTable Scheduler Algorithm

A powerful, constraint-based timetable scheduling system built with Python and Google OR-Tools. This system generates conflict-free schedules for colleges/universities, handling complex requirements like division-level lectures, batch-level labs, and parallel sessions.

## 🚀 Features

*   **Hierarchical Scheduling**:
    *   **Lectures**: Scheduled for the entire division (e.g., DivA).
    *   **Labs**: Scheduled for individual batches (e.g., A1, A2, A3, A4).
*   **Parallel Lab Sessions**: Different batches can attend different labs simultaneously (e.g., A1 in DSL, A2 in DEVL) to maximize resource utilization.
*   **Single Teacher Allocation**: Automatically assigns one specific teacher to cover all lectures of a subject for a division (or all labs for a batch) to ensure consistency.
*   **Conflict-Free**: Guarantees no double-booking of Teachers, Rooms, or Students.
*   **Resource Management**: Assigns specific rooms and teachers based on availability and capability.
*   **Smart Constraints**:
    *   **Lectures block Labs**: If a division has a lecture, no batch in that division can have a lab.
    *   **Contiguous Sessions**: Lab sessions are strictly scheduled as 2-hour blocks.
    *   **Frequency Enforcement**: Ensures every subject gets the exact number of hours defined in the configuration.
    *   **Daily Limits**: Prevents multiple sessions of the same lab on the same day.

## 🛠️ Prerequisites

*   Python 3.8+
*   Google OR-Tools
*   Pandas
*   Tabulate
*   FPDF (for PDF generation)

## 📦 Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/ShubhangDoley/TimeTable-Scheduler-Algo.git
    cd TimeTable-Scheduler-Algo
    ```

2.  Install dependencies:
    ```bash
    pip install ortools pandas tabulate fpdf
    ```

## ⚙️ Configuration

The system is driven by JSON configuration files. You can customize the schedule by modifying these files:

### 1. `config.json`
Defines the structure of the timetable.
```json
{
    "divisions": ["DivA", "DivB", "DivC", "DivD"],
    "batches_per_division": 4,
    "lectures": ["DSA", "MA", "GenAI", ...],
    "labs": ["DSL", "DEVL", "MAL"],
    "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
    "start_hour": 9,
    "end_hour": 17,
    "lunch_start_hour": 13
}
```

### 2. `frequencies.json`
Defines how many sessions per week each subject requires.
*   **Lectures**: Number of 1-hour slots.
*   **Labs**: Number of **2-hour sessions**.
```json
{
    "DSA": 3,
    "DSL": 2  // Means 2 sessions of 2 hours each (Total 4 hours)
}
```

### 3. `teachers.json`
Maps teachers to the subjects they are qualified to teach.
```json
{
    "TeacherName": ["Subject1", "Subject2"]
}
```

### 4. `rooms.json`
Maps rooms to the subjects that can be conducted there (e.g., Computer Labs vs Lecture Halls).
```json
{
    "RoomNumber": ["Subject1", "Subject2"]
}
```

## 🏃 Usage

### 1. Generate Timetable
Run the solver script to generate the raw schedule:
```bash
python timetable_solver.py
```
This saves the schedule to `timetable_full.json`.

### 2. Generate PDF Reports
The system includes multiple scripts to generate professional PDF reports:

*   **Student Timetable**:
    ```bash
    python generate_pdf.py
    ```
    Generates `timetable.pdf` with the master timetable for all divisions and batches.

*   **Faculty Timetable**:
    ```bash
    python generate_faculty_timetable.py  # Generates JSON data
    python generate_faculty_pdf.py        # Generates PDF
    ```
    Generates `faculty_timetable.pdf` showing individual schedules for every teacher.

*   **Free Slots Report**:
    ```bash
    python generate_free_slots.py      # Calculates free slots
    python generate_free_slots_pdf.py  # Generates PDF
    ```
    Generates `free_slots.pdf` listing available teachers for every slot.

## ✅ Verification

To ensure the generated schedule is correct and meets all requirements, use the provided verification tools:

### Verify Lab Frequencies
Checks if every batch has the correct number of lab sessions.
```bash
python verify_labs.py
```
*Output: `verify_labs_output.txt`*

### Verify Lecture Frequencies & Teacher Mapping
Checks if every division has the correct number of lectures and verifies that a single teacher is consistently assigned to each subject.
```bash
python verify_lectures.py
```
*Output: `verify_lectures_output.txt` (Includes Teacher Allocation Table)*

## 📄 Output Format

The system generates a `timetable_full.json` file containing the detailed schedule:
```json
{
    "DivA": {
        "A1": {
            "Mon": [
                {"type": "LECTURE", "class": "DSA", "teacher": "SC", "room": "6102"},
                ...
                {"type": "LAB", "class": "DSL", "teacher": "AM", "room": "6222"}
            ]
        }
    }
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
