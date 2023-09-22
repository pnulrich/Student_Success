import os
from dotenv import load_dotenv
import math
import pandas
from time import sleep
import censusgeocode as cg #2023-07-07 censusgeocode package has a dependency that requires an older version of urllib3. I was able to get it working again wtih urllib3 version 1.26.12

# Updated 2023-08-03, Paul Ulrich
# Accepts a data frame with the following columns: 'StudentID','SDSTUDEMOG_TERM', 'SDSTUDEMOG_ADDRESS_LINE_1','SDSTUDEMOG_CITY', 'SDSTUDEMOG_STATE', 'SDSTUDEMOG_ZIPCODE'
# Vintage and benchmark arguments should be passed using naming conventions used in documentation. Vintage is a required argument.
def batch_geocode(input_address_dataframe, vintage, benchmark=None):
    # API key should be stored in .env file in root directory; Do not include any API keys in code
    load_dotenv()
    api_key = os.environ['CENSUS_API_KEY']

    census_geocode = cg.CensusGeocode()

    #if benchmark provided as an argument, then set the benchmark here; otherwise it will use API default of Public_AR_Current
    #if a benchmark is specified as an argument, set it accordingly
    if benchmark is not None:
        census_geocode.set_benchmark(benchmark)

    #set the vintage for the address lookup; for isntance, ACS2017 would be set as 'ACS2017_Current'
    census_geocode.vintage = vintage

    print("Census vintage : ", census_geocode.vintage)
    print("Census benchmark : ", census_geocode.benchmark)


    batch_size = 10000
    num_batches = math.ceil(
        len(input_address_dataframe) / batch_size
    )

    output_geocode_dataFrame = pandas.DataFrame(
        columns=[
            "StudentID",
            "term",
            "vintage",
            "tigerlineid",
            "statefp",
            "countyfp",
            "tract",
            "block",
        ]
    )

    for term in input_address_dataframe['SDSTUDEMOG_TERM'].unique():
        working_address_df =input_address_dataframe[input_address_dataframe['SDSTUDEMOG_TERM'] == term]
        working_address_df = working_address_df.drop(['SDSTUDEMOG_TERM'], axis=1) #term column is not expected by API so must be dropped; we have stored term variable already as "term" so it is not lost
        print(term, len(working_address_df))

        # Census API accepts batches of addresses up to a max of 10,0000. Determine the # of batch submissions to perform
        num_batches = math.ceil(len(working_address_df) / batch_size)

        for batch_num in range(num_batches):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, len(working_address_df))
            print("batch_num = " + str(batch_num), start_index, end_index)

            #batch geocoding function takes a file path as the first argument
            temp_output_filepath = "C:\\Research\\Research Projects\\GSU\\HHMI_IE3\\Analyses\\Pilot_CalcCLS\\TempAddresses.csv"
            working_address_df[start_index:end_index].to_csv(temp_output_filepath, encoding="utf-8", index=False,
                                                             header=None)
            result = census_geocode.addressbatch(temp_output_filepath, vintage='ACS2017_CURRENT')  # store the result

            try:
                for count, row in enumerate(result):
                    StudentID = result[count]["id"]
                    tigerlineid = result[count]["tigerlineid"]
                    statefp = result[count]["statefp"]
                    countyfp = result[count]["countyfp"]
                    tract = result[count]["tract"]
                    block = result[count]["block"]

                    geocodeDict = {
                        "StudentID": StudentID,
                        "term": term,
                        "vintage": census_geocode.vintage,
                        "benchmark": census_geocode.benchmark,
                        "tigerlineid": tigerlineid,
                        "statefp": statefp,
                        "countyfp": countyfp,
                        "tract": tract,
                        "block": block,
                    }

                    #add the geocoded address to the output dataframe
                    output_geocode_dataFrame = pandas.concat([output_geocode_dataFrame, pandas.DataFrame([geocodeDict])])

                if len(input_address_dataframe) > 10000:
                    print(
                        len(result),
                        " geocoded in batch number: ",
                        batch_num,
                        "\n going to sleep for 5 minutes before running next batch",
                    )
                    sleep(300)

            except Exception as e:
                    print("Error while processing batch:", str(e))

            except KeyboardInterrupt:
                break

    #the dataframe that is returned can be merged wtih a demographics dataframe with a command such as
    #test_demographics_df.merge(result, left_on=['StudentID', 'SDSTUDEMOG_TERM'], right_on=['StudentID', 'term'])
    return output_geocode_dataFrame