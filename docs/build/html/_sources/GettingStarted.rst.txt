Getting Started
===============

Ready to start using the Student Success tools? This guide walks you through cloning the project, installing Python and required modules, setting environment variables, and importing your first dataset.

Cloning the Project from GitHub
-------------------------------

To begin, clone the repository to your local machine:

.. code-block:: bash

   git clone https://github.com/pnulrich/HHMI_Student_Success.git
   cd HHMI_Student_Success

Installing Python
-----------------

.. admonition:: On Windows

    1. **Download and install Python**:
       - Go to the `https://www.python.org/downloads/`
       - Download the latest version for Windows.
       - Run the installer. **Ensure** the checkbox **“Add Python to PATH”** is selected.

    2. **Verify installation**:
       - Open Command Prompt (`Win + R`, then type `cmd`)
       - Run:

    .. code-block:: bash

       python --version

.. admonition:: On Mac

   1. **Install Homebrew (if not already installed)**:

   .. code-block:: bash

      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

   2. **Install Python using Homebrew**:

   .. code-block:: bash

      brew install python

   3. **Verify installation**:

   .. code-block:: bash

      python --version

Setting up a Virtual Environment and Installing Required Python Modules
----------------------------------

I recommend that you work within a Python virtual environmnent.

1. **Ensure you're in a virtual environment** (optional but recommended):

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate   # On Windows use: venv\Scripts\activate

2. **Navigate to the student_success subfolder and install essential packages requirements_essential.txt**:

   .. code-block:: bash

      pip install -r requirements_essential.txt

3. **Test module import**:

   .. code-block:: python

      import pandas
      import numpy
      import student_success

Setting Up the Cipher Environment Variable
------------------------------------------

1. **Student ID's frequently need to be anonymized to protect identity, and a tool is provided to help you handle this.
This will rely on a cipher that *only* you know. It can be stored on your local workstation as an environmental variable
('STUDENT_SUCCESS_CIPHER`) and should *not* be hard-coded or posted anywhere.

.. admonition:: Windows Environment Variable Setup

    1. Control Panel → System and Security → System
    2. Click *Advanced system settings*
    3. Under *System Variables*, click **New**
        - Name: `STUDENT_SUCCESS_CIPHER`
        - Value: (an alphanumeric cipher the same length as your student IDs)

.. admonition:: Mac and Linus Environment Variable Setup

    1. Open .bash_profile

    .. code-block:: bash

       nano ~/.bash_profile

    2. Add this line:

    .. code-block:: bash

       export STUDENT_SUCCESS_CIPHER="your_cipher_here"

    3. Then run:

    .. code-block:: bash

       source ~/.bash_profile

Importing and Preparing Your Data
---------------------------------
Institutions use different conventions for naming of variables and codes for different categories. You will need to align
your column names and category codes to variable names used with the Student Success package. We provide tools to rapidly
rename your columns and codes.


1. **Update your variable name mappings**:
    - Open `HHMI_IE3_codebook.xlsx`
    - Update `variable_name_institution` values with the column names from your dataset.

2. **Update categorical codes in the python dictionaries in utils.constants.py**:
    - Open student_success/utils/constants.py
    - There are many different categories, lists, and maps in constants.py, not all of which may be relevant to your analyses.
These include demographics, major codes, major names, and color maps for various visualization tools. As a starting place,
I suggest working with the dictionaries for lookup of sex and PEER status to become familiar with how they are used. Adjust
used in your institution by changing the number or character associated with that variable name.

2. **Load some data and run the tools to rename your columns and anonymize student_ID's**:

   .. code-block:: python

      import os
      from dotenv import load_dotenv
      import pandas as pd
      import sys

      sys.path.append("../../")  # Adjust relative path as needed

      from student_success.utils.io_utils import rename_columns_in_bulk
      from student_success.utils.scrambler import scramble_ID

      load_dotenv()
      column_mapping_file_path = "./student_success/HHMI_IE3_codebook.xlsx"
      data_filepath = "path_to_your_data.csv" # replace this with the path for your local datafile

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

Errors are a normal part of setup. For help, reach out to us on GitHub and definitely consider using ChatGPT for debugging errors!