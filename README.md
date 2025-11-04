# student_success

Python package for student retention analytics and visualization.

## Documentation
Code is documented with **Sphinx**.  
To view documentation locally:
1. Clone this repository.
2. Build the docs with `sphinx-build -b html docs/source docs/_build/html`.
3. Open `docs/_build/html/index.html` in your browser.

```python
import student_success as ss
print(ss.__version__)
```

## Licensing

- **Code**: BSD-3-Clause. See [`LICENSE`](./LICENSE).
- **Documentation and example text**: CC BY 4.0. See [`docs/LICENSE`](./docs/LICENSE).
- **Sample data/images**: CC BY 4.0 unless noted otherwise.

Attribution and citation:
- Keep copyright and license notices in redistributions.
- Do not use the author’s or institution’s name to endorse derived products without prior written permission (BSD-3-Clause §3).
- Please cite this project as specified in [`CITATION.cff`](./CITATION.cff).  
  Funding acknowledgment: developed with grant support from the HHMI Inclusive Excellence 3 program.

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
```

### Activate the environment
```bash
conda activate student_success
```

### (Optional) Install development tools
```bash
conda env create -f environment_dev.yml
```

### Verify installation
```bash
python -c "import student_success as ss; print(ss.__version__)"
```

```python
# Copyright (c) 2025 Paul Ulrich and John Stewart
# Licensed under the BSD 3-Clause License. See LICENSE file for details.
```