import os
from dotenv import load_dotenv
from census import Census
import pandas as pd
import aiohttp
import asyncio

#2023-08-04 based on https://pygis.io/docs/d_access_census.html
#This function yields income and poverty levels from 5 year ACS data tables. The vintage year should be set for the year
#of the ACS survey. For instance, the 5 year estimates for ACS 2017 would use vintageyear = 2017
#def tract_income_poverty(statefp, countyfp, censustract, vintageyear):
#def tract_income_poverty(statefp, vintageyear, countyfps = [], censustracts = []):
#2023-08-04 comparison against async approach used in optimzied_tract_income_poverty for 230 tracts; non optimized took 176 seconds; optimized took 172 seconds
def tract_income_poverty(input_df, vintageyear):
    # API key should be stored in .env file in root directory; Do not include any API keys in code
    load_dotenv()
    api_key = os.environ['CENSUS_API_KEY']
    c = Census(api_key)

    # Initialize a list to store results for all census tracts
    all_tract_data = []

    #GEOIDS used in Census datasets have standardized lengths used to create an aggregated FIPS (Federal Information Processing Standards) number for a site
    #see https://www.census.gov/programs-surveys/geography/guidance/geo-identifiers.html
    #The census package will not return results if these are not appropriately formatted; in cases where the
    #state, county, or census tract numbers are provided without leading zeroes, I add those in

    for index, row in input_df.iterrows():
        statefp = str(row['statefp']).zfill(2)
        countyfp = str(row['countyfp']).zfill(3)
        censustract = str(row['tract']).zfill(6)

        # Obtain Census variables for given GEOID
        # C17002_001E: count of ratio of income to poverty in the past 12 months (total)
        # C17002_002E: count of ratio of income to poverty in the past 12 months (< 0.50)
        # C17002_003E: count of ratio of income to poverty in the past 12 months (0.50 - 0.99)
        # B01003_001E: total population
        # Sources: https://api.census.gov/data/2019/acs/acs5/variables.html; https://pypi.org/project/census/
        {'for': 'state:*'}
        tractdata = c.acs5.state_county_tract(
            fields=("NAME", "C17002_001E", "C17002_002E", "C17002_003E", "B01003_001E"),
            state_fips=statefp,
            county_fips=countyfp,
            tract=censustract,
            year=vintageyear
        )

        # Check if the tractdata list is not empty before appending
        if tractdata:
            # Append the tract data to the list
            all_tract_data.append(tractdata[0])

        else:
            # If tractdata is empty, create an empty dictionary with the required keys and append it
            empty_data = {
                'state': statefp,
                'county': countyfp,
                'tract': censustract,
                'C17002_001E': None,
                'C17002_002E': None,
                'C17002_003E': None,
                'B01003_001E': None
            }
            all_tract_data.append(empty_data)

    # Convert the list of dictionaries to a DataFrame
    result_df = pd.DataFrame(all_tract_data)
    return result_df

async def fetch_tract_data(session, c, statefp, countyfp, censustract, vintageyear):
    try:
        tractdata = c.acs5.state_county_tract(
            fields=("NAME", "C17002_001E", "C17002_002E", "C17002_003E", "B01003_001E"),
            state_fips=statefp,
            county_fips=countyfp,
            tract=censustract,
            year=vintageyear
        )

        #print(tractdata)
    except Exception as e:
        print(f"Error fetching data for {statefp}-{countyfp}-{censustract}: {e}")
        return None
    else:
        return tractdata[0] if tractdata else None

async def optimized_tract_income_poverty(input_df, vintageyear):
    # API key should be stored in .env file in root directory
    load_dotenv()
    api_key = os.environ['CENSUS_API_KEY']
    c = Census(api_key)

    all_tract_data = []
    tasks = []

    async with aiohttp.ClientSession() as session:
        for _, row in input_df.iterrows():
            statefp = str(row['statefp']).zfill(2)
            countyfp = str(row['countyfp']).zfill(3)
            censustract = str(row['tract']).zfill(6)
            #print(statefp, countyfp, censustract)

            task = fetch_tract_data(session, c, statefp, countyfp, censustract, vintageyear)
            tasks.append(task)

        # Wait for all the tasks to complete asynchronously
        tractdata_list = await asyncio.gather(*tasks)

    # Filter out None results and append valid data
    all_tract_data = [data for data in tractdata_list if data is not None]

    # Convert the list of dictionaries to a DataFrame
    result_df = pd.DataFrame(all_tract_data)
    return result_df