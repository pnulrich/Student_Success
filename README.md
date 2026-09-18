# Student Success

Student Success is a Python package for analyzing student academic progression, retention, course outcomes, and related student-success measures. It provides utilities for preparing institutional academic records and tools for retention analysis, hazard analysis, Markov-style course-flow analysis, and visualization.

The project was developed for research and assessment of student success in higher education with support from the HHMI Inclusive Excellence 3 program.

## Data and privacy

Institutional and student-level datasets are **not distributed with this repository**. Users must provide their own appropriately authorized data.

Research datasets should be stored outside the Git repository. Machine-specific paths and confidential configuration values are supplied locally through environment variables or a `.env` file. An example configuration is provided in `.env.example`.

**Do not commit institutional student data, credentials, ciphers, API keys, or other confidential information to the repository.**

## Installation

Clone the repository:

```bash
git clone https://github.com/pnulrich/Student_Success.git
cd Student_Success
```

Create the development environment using the supplied Conda environment specifications:

```bash
conda env create -n student_success_dev -f environments/environment_essential.yml
conda env update -n student_success_dev -f environments/environment_dev.yml
conda activate student_success_dev
```

Install the Student Success package in editable mode:

```bash
python -m pip install -e .
```

Verify the installation:

```bash
python -c "import student_success; print(student_success.__version__)"
```

For complete installation, configuration, JupyterLab, and development instructions, see `docs/source/user_guide/GettingStarted.rst`.

## Documentation

Documentation is built with Sphinx.

From the repository root:

```bash
sphinx-build -b html docs/source docs/build/html
```

Then open:

```text
docs/build/html/index.html
```

The documentation includes setup instructions, package API documentation, example workflows, and demonstration datasets.

## Repository structure

```text
Student_Success/
├── student_success/    # Python package
├── tests/              # Current automated tests
├── tests_legacy/       # Archived legacy tests
├── docs/               # Sphinx documentation and demonstration data
├── environments/       # Conda environment specifications
├── scripts/            # JupyterLab and development utilities
└── .env.example        # Local configuration template
```

The repository intentionally does not contain institutional research datasets or generated research results.

## Project status

The core `student_success` package is under active development. Some modules retained for compatibility or historical reference are explicitly marked as deprecated. Legacy tests are preserved separately in `tests_legacy`.

The `censustools` component is currently retained but is not part of the active modernization effort.

## Licensing

- **Code:** BSD-3-Clause. See [`LICENSE`](./LICENSE).
- **Documentation and example text:** CC BY 4.0. See [`docs/LICENSE`](./docs/LICENSE).
- **Sample data/images:** CC BY 4.0 unless noted otherwise.

Copyright (c) 2026 Paul Ulrich and John Stewart.

Please retain applicable copyright and license notices in redistributions. The BSD-3-Clause license prohibits using the authors' or institution's names to endorse derived products without prior written permission.

## Citation

Please cite this project as specified in [`CITATION.cff`](./CITATION.cff).

Developed with grant support from the HHMI Inclusive Excellence 3 program.