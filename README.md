# PSCASO

PSCASO is a user-friendly tool designed to assist beginner and new researchers in the classification and analysis of stellar data. It provides a straightforward interface for working with astronomical datasets, allowing users to classify stars, galaxies, and quasars, while also offering various visualizations to explore photometric data. The app simplifies complex tasks, making it accessible for those just entering the field of astronomy and data science.
## Table of Contents

- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/VikkiezDev/PSCASO.git
    ```

2. **Navigate to the project directory:**

    ```bash
    cd PSCASO
    ```

3. **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    ```


4. **Activate the virtual environment:**

    * **Linux/macOS:**
        ```bash
        source venv/bin/activate
        ```

    * **Windows:**
        ```bash
        venv\Scripts\activate
        ```

5. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Project Structure
```
└── PSCASO/
    ├── assets/
    │   └── styles.css
    ├── dash_application/
    │   └── __init__.py
    ├── data/
    │   ├── data_release.db
    │   └── DR18.csv
    ├── model/
    │   ├── final-model.pkl
    │   └── pca_scaler.pkl
    ├── static/
    │   ├── css/
    │   │   ├── styles.css
    │   │   ├── timeline.css
    │   │   └── viewer.css
    │   ├── js/
    │   │   └── script.js
    │   ├── img/
    │   │   ├── bg.jpg
    │   │   ├── .
    │   │   ├── .
    │   │   └── research.png
    │   └── docs/
    │       ├── Project_Documentation.pdf
    │       └── Research_paper.pdf
    ├── templates/
    │   ├── index.html
    │   ├── background.html
    │   ├── classifier.html
    │   ├── research.html
    │   └── documentation.html
    ├── main.py
    ├── README.md
    └── requirements.txt
```
## Usage

1. **Run the application:**
    ```bash
    python main.py
    ```
2. **Access the application:**

   Open your web browser and go to `http://localhost:8080` (or the port you configured).
