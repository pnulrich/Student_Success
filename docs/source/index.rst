.. student_success documentation master file

Welcome to student_success's documentation!
===========================================

The ``student_success`` package provides tools for analyzing institutional data associated with student demographics, retention,
course performance, and degree completion. Visualization of course progression, demographics, and flows of students are
features of this tool kit.

The package also provides a suite of utilities for standardizing and cleaning data, handling
variations in term structure, and data import. Among these are hazard analysis for assessing patterns in student movements
among majors, timing of courses, and flow of students attempts of prerequisites and downstream courses.

Four subpackages constitute the core of the ``student_success`` package.

- **hazard_analysis**: hazard models and visualization.
- **markov_diagrams**: course flow diagrams.
- **metrics**: classification, retention, and graduation indicators.
- **utils**: wide range of time, grade, program, and IO utilities.

We encourage you to begin by exploring our User Guide for guidance on installation and use cases.

.. toctree::
   :maxdepth: 3
   :caption: User Guide

   user_guide/GettingStarted
   user_guide/workflows
   user_guide/examples/index

Project Information
===================

The source code, release history, and development resources for
``student_success`` are available in the `Student Success GitHub repository
<https://github.com/pnulrich/Student_Success>`_.

Citation
--------

If you use ``student_success`` in research, please cite the software using the
`citation information
<https://github.com/pnulrich/Student_Success/blob/master/CITATION.cff>`_
provided with the project.

Licensing
---------

The ``student_success`` source code is distributed under the
`BSD 3-Clause License
<https://github.com/pnulrich/Student_Success/blob/master/LICENSE>`_.

Documentation and example text are distributed under the
`Creative Commons Attribution 4.0 International License
<https://github.com/pnulrich/Student_Success/blob/master/docs/LICENSE>`_.


.. toctree::
   :maxdepth: 2
   :caption: API Reference

   modules/index

Reference
=========

* :ref:`genindex`
* :ref:`modindex`