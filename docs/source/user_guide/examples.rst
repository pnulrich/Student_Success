Examples
========

Here are practical examples of using the package.

.. code-block:: python

   import pandas as pd
   from student_success.hazard_analysis import prepare_hazard_data

   df = pd.read_csv("my_data.csv")
   prepared = prepare_hazard_data(df, target_major="BIO")
