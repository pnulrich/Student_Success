Getting Started
===============
.. toctree::
   :maxdepth: 2
   :caption: Contents


Ready to start using the Student Success tools?
This guide will walk you through four things:

1. Downloading the project
2. Installing the software you need (using Miniconda)
3. Setting up your project “environment”
4. (optional) Opening the tools in JupyterLab


Cloning or Downloading the Repository
-------------------------------------

If you are comfortable with GitHub, you can clone the repository into your development directory:

.. code-block:: bash

   cd research/development
   git clone https://github.com/pnulrich/Student_Success.git
   cd student_success

If you are not using GitHub, you can also download the project as a ZIP
file from the GitHub page and unzip it into your development directory.

Installing Miniconda
--------------------

This project uses **Miniconda** to manage all the software you need.
Miniconda manages Python and the packages required by the project.

.. admonition:: On Windows

   1. Download Miniconda from: https://www.anaconda.com/download. You need a (free) account to access the download.
   2. Choose the 64-bit installer for *All Users* (this puts it in ``C:\ProgramData\miniconda3``).
   3. After installation, open **Anaconda Prompt** (installed with Miniconda).

.. admonition:: On macOS

   1. Download Miniconda from: https://www.anaconda.com/download. You need a (free) account to access the download.
   2. Install into your home directory (default is ``~/miniconda3``).
   3. Open **Terminal**.

Update Miniconda to the latest version:

.. code-block:: bash

   conda update -n base -c defaults conda

Creating the Environment
------------------------

The Student Success tools run inside a **Conda environment**.
An environment is a self-contained folder that holds everything this
project needs to run: Python itself plus all the add-ons the code uses.
This isolates the project's software dependencies from other Python installations on your system.
We suggest organization of file directories as follows:

Suggested directory organization::

    Research/
    ├── development/
    │   └── student_success/
    └── analyses/
        ├── institutionaldata/
        ├── jupyter_notebooks/
        └── Results/

Two Conda environment specification files are provided:

- environment_essential.yml installs the core libraries required to use the Student Success package.
- environment_dev.yml adds development tools including JupyterLab, pytest, and documentation utilities.

**Step 1: Essentials**

.. code-block:: bash

   conda env create -n student_success_dev -f environments/environment_essential.yml

**Step 2: Extended toolkit**

.. code-block:: bash

   conda env update -n student_success_dev -f environments/environment_dev.yml

The second command updates the existing ``student_success_dev`` environment
with the additional development dependencies.

Activating the Environment and Installing the Student Success Package
---------------------------------------------------------------------

To work within the virtual environment, you need to **activate** the environment.
Activating simply means "turn on the project setup" so Python uses the
correct version and the right add-ons. Activate the environment whenever you
work with the ``student_success`` package from a terminal. The JupyterLab
launcher scripts described below activate the environment automatically.

.. code-block:: bash

   conda activate student_success_dev
   python -m pip install -e .

The editable installation allows any changes made to the package source code to become immediately available without
reinstalling the package.

Activating the Environment and Installing the Student Success Package
---------------------------------------------------------------------

Activate the environment:

.. code-block:: bash

   conda activate student_success_dev

.. note::

   On some managed Windows systems, PowerShell may block Conda's initialization
   script because of the system execution policy. If ``conda`` is not recognized,
   or Conda cannot be initialized from PowerShell, use Command Prompt instead.

   For a per-user Anaconda installation, you can open an activated Command Prompt
   from PowerShell with:

   .. code-block:: powershell

      cmd /K ""%LOCALAPPDATA%\anaconda3\Scripts\activate.bat" student_success_dev"

   You should then see ``(student_success_dev)`` at the beginning of the
   Command Prompt.

Install the ``student_success`` package in editable mode:

.. code-block:: bash

   python -m pip install -e .


Verify Installation
-------------------

Run:

.. code-block:: bash

   python -c "import student_success; print(student_success.__file__)"

This confirms that the package was successfully loaded and should print the package location.
The printed path should point to your cloned repository rather than the Conda installation.


Project Configuration
---------------------

Some Student Success utilities require local configuration values, such as
the cipher used to anonymize student identifiers or the locations of
institutional datasets. These values are stored in a project-specific
``.env`` file rather than being hard-coded into notebooks or source code.

Institutional datasets should remain outside the Git repository and should never be committed to the repository!

Create a file named ``.env`` in the root directory of the repository:

.. code-block:: text

   student_success/
   ├── .env
   ├── pyproject.toml
   ├── environments/
   ├── student_success/
   └── ...

A template file named ``.env.example`` is provided. Copy it to ``.env`` and
fill in the required values.

Example:

.. code-block:: text

   STUDENT_SUCCESS_CIPHER=your_secret_cipher
   STUDENT_SUCCESS_DATA_ROOT=C:\Research Projects\Analyses\institutionaldata
   STUDENT_SUCCESS_RESULTS=C:\Research Projects\Analyses\results

These paths should point to your local analysis workspace and may differ from those used by other developers.

The ``.env`` file is ignored by Git and should never be committed to the
repository.

The Student Success package uses these values to configure local resources such as anonymization and
institutional data locations. Some notebooks may explicitly call ``load_dotenv()`` until configuration
loading is fully centralized within the package.

Optional Research and Developmental Resources
---------------------------------------------

JupyterLab
++++++++++

JupyterLab is an interactive environment that you can think of like a laboratory notebook
where you can record your process, run code, store results, view figures, and provide commentary.
JupyterLab documents are called *notebook* files (``.ipynb``).

As a convenience, we provide instructions for setting up and launching
JupyterLab. Because of the diversity in configurations and operating systems,
setup may require you to do some trouble-shooting to get started, but it's worth
it.

.. note::

   JupyterLab is included in the extended toolkit. If you want to use JupyterLab,
   apply both ``environments/environment_essential.yml`` and
   ``environments/environment_dev.yml`` as described in the Creating the
   Environment section above.

Launching JupyterLab
^^^^^^^^^^^^^^^^^^^^
JupyterLab should normally be started in your analysis notebook directory rather
than in the student success source-code repository. This keeps research notebooks,
data, and analysis outputs separate from the package source code.

You can launch JupyterLab manually or use one of the launcher scripts provided
with the repository.

Manual Launch
~~~~~~~~~~~~~

First, activate the development environment:

.. code-block:: bash

    conda activate student_success_dev

Second, navigate to your notebook directory and start JupyterLab:

.. code-block:: bash

   cd path/to/Analyses/jupyter_notebooks
   jupyter lab

Using a Launcher Script
~~~~~~~~~~~~~

If you use the launcher scripts described below, you do not need to activate
the Conda environment manually. The launcher activates ``student_success_dev``
for you.

First, configure the notebook directory. The launcher scripts use the ``STUDENT_SUCCESS_NOTEBOOK_DIR`` environment
variable to determine where your Jupyter notebooks are stored. This allows
notebooks to remain outside the Git repository and avoids storing
machine-specific paths in the launcher scripts.

Set this variable once on each computer where you use Student Success.

**Windows**

In PowerShell:

.. code-block:: powershell

   [Environment]::SetEnvironmentVariable("STUDENT_SUCCESS_NOTEBOOK_DIR","C:\path\to\Analyses\jupyter_notebooks","User")

Close and reopen PowerShell after setting the variable. You can verify it with:

.. code-block:: powershell

   $env:STUDENT_SUCCESS_NOTEBOOK_DIR

**macOS/Linux**

Add the following to your shell configuration file (for example,
``~/.zshrc`` or ``~/.bashrc``):

.. code-block:: bash

   export STUDENT_SUCCESS_NOTEBOOK_DIR="$HOME/path/to/Analyses/jupyter_notebooks"

Then reload the shell configuration or open a new terminal.


Now you are ready to use the launcher scripts. These are provided in the repository's ``scripts/``
directory. They activate the ``student_success_dev`` Conda environment,
change to ``STUDENT_SUCCESS_NOTEBOOK_DIR``, and launch JupyterLab.

Windows
"""""""

From the repository root, run:

.. code-block:: powershell

   .\scripts\start_studentsuccess.bat

You may also launch ``start_studentsuccess.bat`` directly from Windows
Explorer.

The Windows launcher searches common per-user Anaconda and Miniconda
installation locations automatically. Conda therefore does not need to be
added to the Windows ``PATH``.

The launcher will stop with an explanatory error if:

- ``STUDENT_SUCCESS_NOTEBOOK_DIR`` has not been configured,
- the configured notebook directory does not exist,
- Anaconda or Miniconda cannot be located, or
- the ``student_success_dev`` environment cannot be activated.


macOS/Linux
"""""""""""

From the repository root, make the launcher executable the first time:

.. code-block:: bash

   chmod +x scripts/start_studentsuccess.sh

Then launch JupyterLab with:

.. code-block:: bash

   ./scripts/start_studentsuccess.sh

The launcher searches common Anaconda and Miniconda installation locations
under the user's home directory, activates ``student_success_dev``, changes
to ``STUDENT_SUCCESS_NOTEBOOK_DIR``, and starts JupyterLab.

.. note::

   The macOS/Linux launcher searches several common Anaconda and Miniconda
   installation locations automatically. If the launcher reports that it
   cannot locate Conda, your installation may be in a nonstandard location.
   In that case, update the Conda discovery section of
   ``scripts/start_studentsuccess.sh`` to include the location of
   ``etc/profile.d/conda.sh`` for your installation.

.. warning::

   The macOS/Linux launcher has not yet been tested on Linux or macOS.
   Verify Conda discovery, environment activation, and JupyterLab startup
   before relying on it in these environments.


PyCharm
+++++++

PyCharm is an integrated development environment (IDE) like VSCode. IDEs are indispensable tools for development because
they provide a one-stop shop for coding, finding errors, and version control. Academic users should consider the free
licensing options available to them.

If you are using PyCharm, you can use your conda environment as follows:

1. Go to **File > Settings > Project > Python Interpreter**.
2. Select **Add Interpreter > Conda Environment > Existing**.
3. Browse to the Python program inside your new environment. Select the existing environment rather than creating a new
virtual environment. To locate the environment on any platform, run:

.. code-block:: bash

   conda env list

Then select the Python executable inside the ``student_success_dev``
environment shown by Conda.

Troubleshooting
---------------
- **Launcher cannot locate Conda**
  The launcher scripts search common Anaconda and Miniconda installation
  locations automatically. If Conda is installed in a nonstandard location,
  add that location to the Conda discovery section of the appropriate launcher
  script in ``scripts/``.

- **Conda will not activate in PowerShell**
  Some managed Windows systems block Conda's PowerShell initialization scripts.
  See **Activating the Environment and Installing the Student Success Package**
  above for the Command Prompt workaround.

- **Spaces in Windows paths** → If Miniconda is installed under a path with spaces (e.g. ``C:\Users\My User Name``), you may see warnings.
  These can usually be ignored, but for stability it is best to install Miniconda in a path without spaces (e.g. ``C:\miniconda3``).

- **Notebook extension errors** → This project supports Notebook 7 and JupyterLab 4.
  Legacy Notebook 6 extensions (e.g. jupyter_contrib_nbextensions) are not compatible and should not be installed.

- **OpenSSL certificate errors** → If JupyterLab fails during startup with an SSL or ASN.1 certificate-store error on
  Windows, update the Conda environment using the versions specified in the project environment files. If necessary,
  consult the project release notes for temporary OpenSSL compatibility workarounds.