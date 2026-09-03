# student_success

Python package for student retention analytics and visualization.

## Documentation
Code is documented with **Sphinx**. To view documentation locally:
1. Clone this repository.
2. Build the docs with `sphinx-build -b html docs/source docs/_build/html`.
3. Open `docs/_build/html/index.html` in your browser.

## Licensing

- **Code**: BSD-3-Clause. See [`LICENSE`](./LICENSE).
- **Documentation and example text**: CC BY 4.0. See [`docs/LICENSE`](./docs/LICENSE).
- **Sample data/images**: CC BY 4.0 unless noted otherwise.
 
Copyright (c) 2025 Paul Ulrich and John Stewart. All rights reserved.

Attribution and citation:
- Keep copyright and license notices in redistributions.
- Do not use the author’s or institution’s name to endorse derived products without prior written permission.
- Please cite this project as specified in [`CITATION.cff`](./CITATION.cff).  
- Funding acknowledgment: developed with grant support from the HHMI Inclusive Excellence 3 program.

## Installation

### Clone the repository
```bash
git clone https://github.com/gsu-student-success/student_success.git
cd student_success
```

### Install Miniconda
Download from https://docs.conda.io/en/latest/miniconda.html and follow the platform-specific installer instructions.

### Create the conda environment
```bash
conda env create -f environment_essential.yml
conda env create -f environment_dev.yml # recommended developer scripts
```

### Activate the environment
```bash
conda activate student_success
```

### Verify installation
```bash
python -c "import student_success as ss; print(ss.__version__)"
```