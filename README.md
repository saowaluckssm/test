# Meter Reading Ingestion

This Django project is designed to process "D0010" flow files, which contain meter readings data, in order to communicate with the energy industry. These flow files are provided to Kraken via sFTP and need to be ingested into our database. The data can then be accessed via the Django admin interface by support staff for review.

### Author: Saowaluck Morales

---

## Purpose

The goal of this project is to create a service that can process "D0010" flow files and allow their data to be viewed in the Django admin panel. These files are pipe-delimited and contain important meter readings. The system currently supports file ingestion via the command line, and a REST interface could potentially be added in the future to allow web uploads.

---

## Assumptions

- Developed with:
    - Python version 3.11.3
    - Django version 5.2.3
- The current implementation only handles "D0010" flow files.

---


## Installation

To get this project running on your local machine, follow the steps below:

### Prerequisites

Ensure the following dependencies are installed on your machine:

- Python **3.11.x** (use `python3.11 --version` to check)
- Django **5.2.x** or higher
- PostgreSQL (or your preferred database)
- A **text editor** or IDE (e.g., VS Code, Sublime Text, PyCharm)

### Steps

1. **Create a Virtual Environment**  

   ```bash
   python3.11 -m venv venv
   source venv/bin/activate 

2. **Create a Virtual Environment**  
    With your virtual environment activated, install the dependencies specified in requirements.txt:

     ```bash
      pip install -r requirements.txt

3. **Setup the Database**  
    You will need to migrate the database to ensure the necessary tables are created:

     ```bash
      python manage.py migrate

4. **Ingest a Sample Data File**  
    You can now ingest a sample .uff flow file into the system. Place the flow file in the appropriate folder, and then run the ingestion command:

     ```bash
      python manage.py import_d0010 DTC5259515123502080915D0010.uff












   
  
