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

Cloning the Project from GitHub
-------------------------------

First, download the project to your computer.
If you are comfortable with GitHub, you can clone the repository:

.. code-block:: bash

   git clone https://github.com/pnulrich/HHMI_Student_Success.git
   cd HHMI_Student_Success

If you are not using GitHub, you can also download the project as a ZIP
file from the GitHub page and unzip it to a folder on your computer.

Installing Miniconda
--------------------

This project uses **Miniconda** to manage all the software you need.
Think of Miniconda as a manager that installs the correct version of
Python along with all the add-ons the project requires.

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
This keeps the project separate from anything else on your computer.

We split the setup into **two steps**:

- ``environment_essential.yml``
  Installs the core parts of Python needed for analysis.
- ``environment_dev.yml``
  Adds extras like JupyterLab, testing tools, and documentation support.
  These are required if you want to open notebooks or contribute code.

**Step 1: Essentials**

.. code-block:: bash

   conda env create -n student_success_dev -f environment_essential.yml

**Step 2: Extended toolkit**

.. code-block:: bash

   conda env update -n student_success_dev -f environment_dev.yml


Activating the Environment
--------------------------

Before you run anything, you need to **activate** the environment.
Activating simply means “turn on the project setup” so Python uses the
correct version and the right add-ons.

.. code-block:: bash

   conda activate student_success_dev

You only need to do this once per session. After activation, you are
inside the project environment.

Check that everything is working:

.. code-block:: bash

   python -c "import pandas, dotenv; print('OK:', pandas.__version__)"

You should see something like: ``OK: 2.2.x``.

Troubleshooting
---------------

- **Command not found: conda**
  On macOS, ensure Miniconda is installed in ``~/miniconda3`` (default),
  or edit ``start_studentsuccess.sh`` and update ``CONDA_INIT`` to the
  location of your installation.

- **Windows can’t find activate.bat**
  Switch the ``CONDA_ACTIVATE`` setting in the batch script to the correct path:
  ``C:\ProgramData\miniconda3\Scripts\activate.bat`` (all users) or
  ``%UserProfile%\miniconda3\Scripts\activate.bat`` (per-user).

- **Spaces in Windows paths** → If Miniconda is installed under a path with spaces (e.g. ``C:\Users\My User Name``), you may see warnings.
  These can usually be ignored, but for stability it is best to install Miniconda in a path without spaces (e.g. ``C:\miniconda3``).

- **Notebook extension errors** → Notebook extension errors → This project supports Notebook 7 and JupyterLab 4.
  Legacy Notebook 6 extensions (e.g. jupyter_contrib_nbextensions) are not compatible and should not be installed.


Optional Research and Developmental Resources
---------------------------------------------

JupyterLab
++++++++++

Part of the developer setup installs **JupyterLab**, which is a great workspace for you
to begin using the Student Success toolkit. JupyterLab is an interactive
environment that you can think of like a laboratory notebook where you can
record your process, run code, store results,view figures, and provide commentary.
JupyterLab documents are called *notebook* files (``.ipynb``).

As a convenience, we provide instructions for setting up and launching
JupyterLab. Because of the diversity in configurations and operating systems,
setup may require you to do some trouble-shooting to get started, but it's worth
it!

.. note::

   JupyterLab is part of the **developer requirements**. You must
   complete both steps (essentials + dev) before this will work.



Launching JupyterLab
^^^^^^^^^^^^^^^^^^^^
To open JupyterLab in the notebooks folder:

.. code-block:: bash

   cd jupyter_notebooks
   jupyter lab

Starting JupyterLab the Easy Way
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We provide simple launch scripts that open a terminal, activate the
project environment, and start JupyterLab in the notebooks folder.

Windows
~~~~~~~

1. Double-click ``start_studentsuccess.bat`` inside the project folder.
2. A terminal window opens, the environment is activated, and JupyterLab launches.

.. note::

   If Miniconda was installed per-user (not all users), you may need to edit
   the first lines of ``start_studentsuccess.bat`` and set:

   ``set CONDA_ACTIVATE="%UserProfile%\miniconda3\Scripts\activate.bat"``

macOS
~~~~~

1. Open **Terminal** and navigate to the project folder where
   ``start_studentsuccess.sh`` is located.

2. The first time only, make the script executable:

   .. code-block:: bash

      chmod +x start_studentsuccess.sh

   This tells macOS that the file can be run as a program.

3. Launch JupyterLab by running:

   .. code-block:: bash

      ./start_studentsuccess.sh

4. JupyterLab will open in your browser and the terminal will stay active
   for this session.

.. note::

   If you see an error like ``conda: command not found``, edit the script and
   check the ``CONDA_INIT`` setting points to your Miniconda installation.
   The default is ``~/miniconda3/etc/profile.d/conda.sh``.


PyCharm
+++++++

PyCharm is an integrated development environment (IDE) like VSCode. IDEs are indispensable tools for development because
they provide a one-stop shop for coding, finding errors, and version control. Academic users should consider the free
licensing options available to them.

If you are using PyCharm, you can use your conda environment as follows:

1. Go to **File > Settings > Project > Python Interpreter**.
2. Select **Add Interpreter > Conda Environment > Existing**.
3. Browse to the Python program inside your new environment:

   - **Windows**: ``C:\Users\<your username>\.conda\envs\student_success_dev\python.exe``
   - **macOS**: ``~/miniconda3/envs/student_success_dev/bin/python``

