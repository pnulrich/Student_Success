import pandas as pd
from institutionaldata import utilityfunctions as uf
def test_set_up_demographic_flags_basic():
    # Setup: create a simple DataFrame
    df = pd.DataFrame({
        'demographics_race': ['Asian', 'White', 'Black or African American', 'Black', 'Not Reported', 'More Than One Race Reported'],
        'demographics_sex': ['Male', 'Female', 'non-binary', '', 'M', 'F'],
        'flag_first_generation': ['Y', 'N', 1, 0, 0, 0],
        'flag_PELL': ['Y', 'N', 1, 0, 0, 0]
    })

    # Call the function under test
    result_df = uf.set_up_demographic_flags(df)

    # Assert conditions to verify the correctness of the function
    # For example, checking if the flag columns exist
    assert 'flag_first_generation' in result_df.columns
    assert 'flag_PELL' in result_df.columns
    assert 'flag_PEER' in result_df.columns
    assert 'flag_sex' in result_df.columns

    # test first generation logic
    assert result_df.loc[0, 'flag_first_generation'] == 1  # Since 'Y' should map to 1
    assert result_df.loc[1, 'flag_first_generation'] == 0  # Since 'N' should map to 0
    assert result_df.loc[2, 'flag_first_generation'] == 1  # Since 'Y' should map to 1
    assert result_df.loc[3, 'flag_first_generation'] == 0  # Since 'N' should map to 0

    # test PEER logic
    assert result_df.loc[0, 'flag_PEER'] == 0  # Since 'Asian' should map to 0
    assert result_df.loc[1, 'flag_PEER'] == 0  # Since 'White' should map to 0
    assert result_df.loc[2, 'flag_PEER'] == 1  # Since 'Black or African American' should map to 1
    assert result_df.loc[3, 'flag_PEER'] == 1  # Since 'Black' should map to 1
    assert result_df.loc[4, 'flag_PEER'] == -1  # Since 'Note Reported' should map to -1
    assert result_df.loc[5, 'flag_PEER'] == 2  # Since 'More Than One Race Reported' should map to 2

    # test PELL logic
    assert result_df.loc[0, 'flag_PELL'] == 1  # Since 'Y' should map to 1
    assert result_df.loc[1, 'flag_PELL'] == 0  # Since 'N' should map to 0
    assert result_df.loc[2, 'flag_PELL'] == 1  # Since 1 should remain 1
    assert result_df.loc[3, 'flag_PELL'] == 0  # Since 0 should remain 0

    # test sex logic
    assert result_df.loc[0, 'flag_sex'] == 0  # Since 'Male' should map to 0
    assert result_df.loc[1, 'flag_sex'] == 1  # Since 'Female' should map to
    assert result_df.loc[2, 'flag_sex'] == -1  # Since non-dictionary string should map to -1
    assert result_df.loc[3, 'flag_sex'] == -1  # Since empty string should map to -1
    assert result_df.loc[4, 'flag_sex'] == 0  # Since 'M' should map to 0
    assert result_df.loc[5, 'flag_sex'] == 1  # Since 'F' should map to 1
