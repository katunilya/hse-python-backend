
# Homework 1 - Mathematical API

This folder contains the implementation of the Mathematical API using an ASGI-compatible function.

## Folder Structure

```
homework_1/
│
├── handlers.py      # Route handler functions for factorial, Fibonacci, and mean
├── main.py          # The entry point for the ASGI application
├── math_utils.py    # Mathematical functions (factorial, Fibonacci)
├── utils.py         # Utility functions for JSON responses and request body handling
└── README.md        # Documentation for this folder
```

## How to Set Up and Run

### Step 1: Clone the Repository

First, clone the repository:

```bash
git clone git@github.com:Reveur1988/hse-python-backend.git
cd hse-python-backend
```

### Step 2: Switch to the Homework 1 Branch

Make sure to switch to the branch where the homework implementation is located:

```bash
git checkout homework_1
```

### Step 3: Set Up Virtual Environment

#### Option 1: Using `venv`

Ensure you have Python 3.12 installed. If not, you can download it from the official [Python website](https://www.python.org/downloads/).

Once Python 3.12 is installed, create and activate a virtual environment using `venv`:

```bash
python3.12 -m venv venv
source venv/bin/activate
```

#### Option 2: Using `conda`

Alternatively, you can create and activate a virtual environment using Conda (no need to install Python 3.12 manually):

1. Install Conda by following the instructions on the [official Conda installation guide](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).
   
2. Create a new environment with Python 3.12:

   ```bash
   conda create -n myenv python=3.12
   ```

3. Activate the environment:

   ```bash
   conda activate myenv
   ```

### Step 4: Install Poetry

If you don't have Poetry installed, you can install it using the following command:

```bash
pip install poetry
```

### Step 5: Install Dependencies Using Poetry

Now, install the required dependencies:

```bash
poetry install --no-root
```

### Step 6: Running the Application

You can start the application in two ways:

1. **Using Makefile**: If you have `make` installed, you can simply run:

   ```bash
   make hw1
   ```

2. **Using Uvicorn Directly**: Alternatively, you can run the following command:

   ```bash
   uvicorn homework_1.main:app --reload
   ```

The application will be available at `http://127.0.0.1:8000`.
