Getting Started
===============

Ready to start using the Student Success tools generated for Project B?
To use these tools, you will need to install Python on your computer and set up the appropriate modules.

Installing Python
-----------------

### For Windows

1. **Download and install Python**:
   - Go to the `https://www.python.org/downloads/`
   - Download the latest version for Windows.
   - Run the installer. Be sure to **check** the box labeled **"Add Python to PATH"**.

2. **Verify installation**:
   - Open Command Prompt (`Win + R`, type `cmd`, press Enter).
   - Type `python --version`. You should see the installed version.

### For Mac

1. **Install Homebrew (if not already installed)**:
   - Open Terminal.
   - Paste and run:
     ::
       /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

2. **Install Python using Homebrew**:
   ::
     brew install python

3. **Verify installation**:
   ::
     python --version

Installing Python Modules and Setting Up Environment Variables
--------------------------------------------------------------

1. **Install required modules**:
   ::
     pip install pandas numpy matplotlib tabulate statsmodels pydot pygraphviz

2. **Test module import**:
   ::
     import institutionaldata.successmetrics
     import institutionaldata.utilityfunctions

3. **Set up the `STUDENT_SUCCESS_CIPHER` environment variable**:

   **For Windows**:
   - Open Control Panel → System and Security → System
   - Click **Advanced system settings**
   - Under *System Variables*, click **New**
   - Set:
     - Name: `STUDENT_SUCCESS_CIPHER`
     - Value: (your custom cipher)

   **For macOS**:
   - Open Terminal.
   - Run:
     ::
       nano ~/.bash_profile

   - Add this line to the bottom:
     ::
       export STUDENT_SUCCESS_CIPHER="your_cipher_here"

   - Save and exit (`Ctrl+X`, then `Y`, then `Enter`)
   - Reload the profile:
     ::
       source ~/.bash_profile

Importing Your Data
-------------------

1. **Set up column mapping**:
   - Open `columnmapping.tsv`
   - Ensure the `variable_name_institution` column lists your dataset's actual column names for each standardized field.

2. **In Python, load and clean your data**:
   ::
     import os
     from dotenv import load_dotenv
     import pandas as pd
     import numpy as np
     import sys
     sys.path.append('../../')  # adjust as needed
     import institutionaldata.successmetrics
     import institutionaldata.utilityfunctions
     import statsmodels.api as sm

     load_dotenv()
     column_mapping_file_path = './institutionaldata/column_mapping.tsv'
     data_filepath = "path_to_your_data.csv"

     dataset_df = pd.read_csv(data_filepath)
     dataset_df = institutionaldata.utilityfunctions.rename_columns_in_bulk(
         dataset_df,
         column_mapping_filepath=column_mapping_file_path
     )

     dataset_df = institutionaldata.utilityfunctions.scramble_ID(
         dataset_df,
         cipher=os.environ['STUDENT_SUCCESS_CIPHER']
     )

3. **Verify renaming**:
   ::
     print(list(dataset_df))

4. **Next steps**:
   Explore the functions in `successmetrics.py` and `utilityfunctions.py`.
   Expect some early data-cleaning errors — these vary based on how your institution structures data.
   Reach out to the Project B team or use ChatGPT for troubleshooting.

