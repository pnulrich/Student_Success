Getting Started
===============

Ready to start using the Student Success tools? This guide will walk you through installing Python, setting up required modules, configuring environment variables, and importing your first dataset.

Installing Python
-----------------

### For Windows

1. **Download and install Python**:
   - Go to the `https://www.python.org/downloads/`
   - Download the latest version for Windows.
   - Run the installer. **Ensure** the checkbox **“Add Python to PATH”** is selected.

2. **Verify installation**:
   - Open Command Prompt (`Win + R`, then type `cmd`)
   - Run:

     .. code-block:: bash

        python --version

### For Mac

1. **Install Homebrew (if not already installed)**:

   .. code-block:: bash

      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

2. **Install Python using Homebrew**:

   .. code-block:: bash

      brew install python

3. **Verify installation**:

   .. code-block:: bash

      python --version

Installing Required Python Modules
----------------------------------

The Student Success project uses a curated list of essential modules defined in a `requirements_essential.txt` file.

1. **Ensure you're in a virtual environment** (optional but recommended):

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate   # On Windows use: venv\Scripts\activate

2. **Install modules from the requirements file**:

   .. code-block:: bash

      pip install -r requirements_essential.txt

3. **Test module import**:

   .. code-block:: python

      import pandas
      import numpy
      import student_success

Setting Up the Cipher Environment Variable
------------------------------------------

1. **Define the `STUDENT_SUCCESS_CIPHER` environment variable**, which is used to anonymize student IDs.

   ### For Windows

   - Control Panel → System and Security → System
   - Click *Advanced system settings*
   - Under *System Variables*, click **New**
     - Name: `STUDENT_SUCCESS_CIPHER`
     - Value: (an alphanumeric cipher of the same length as your student IDs)

   ### For macOS / Linux

   .. code-block:: bash

      nano ~/.bash_profile

   Add this line:

   .. code-block:: bash

      export STUDENT_SUCCESS_CIPHER="your_cipher_here"

   Then:

   .. code-block:: bash

      source ~/.bash_profile

Importing and Preparing Your Data
---------------------------------

1. **Set up your column mapping**:
   - Open `columnmapping.tsv`
   - Update the `variable_name_institution` column to reflect the exact names from your dataset.

2. **Run the setup in Python**:

   .. code-block:: python

      import os
      from dotenv import load_dotenv
      import pandas as pd
      import sys

      sys.path.append("../../")  # Adjust relative path as needed

      from student_success.utils.io_utils import rename_columns_in_bulk
      from student_success.utils.scrambler import scramble_ID

      load_dotenv()
      column_mapping_file_path = "./institutionaldata/column_mapping.tsv"
      data_filepath = "path_to_your_data.csv"

      dataset_df = pd.read_csv(data_filepath)
      dataset_df = rename_columns_in_bulk(dataset_df, column_mapping_filepath=column_mapping_file_path)
      dataset_df = scramble_ID(dataset_df, cipher=os.environ['STUDENT_SUCCESS_CIPHER'])

3. **Check that column names were changed**:

   .. code-block:: python

      print(list(dataset_df))

Next Steps
----------

You are now ready to explore the modules within `student_success`, including:

- `metrics` for graduation and retention flags
- `hazard_analysis` for modeling time-based transitions
- `markov_diagrams` for visualizing course flows
- `utils` for I/O, time, and demographic utilities

Troubleshooting and Questions
-----------------------------

Errors are a normal part of setup. For help:

- Contact the Project B team via Slack (#project-b)
- Paste any error messages into ChatGPT for quick debugging help
