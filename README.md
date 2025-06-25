# General Information

This code converts a specifically formatted table of transient candidates into a json file that is compatible with the script provided by TNS that performs a bulk AT report upload. Here is a link to the TNS script that actually performs the upload: https://www.wis-tns.org/content/tns-getting-started 

Navigate to the "API - Bulk Report" sub-section of that webpage to find their downloadable Python scripts for uploading sources via an input json file (that this script generates).

If you have any questions, refer to TNS’s bulk AT report guide: https://www.wis-tns.org/sites/default/files/api/tns2_manuals/TNS2.0_bulk_reports_manual.pdf or email me at cndecoursey@arizona.edu

# How the Code Works

Before running the code, you must download the values.json file from the TNS site (https://www.wis-tns.org/api/get/values) and save it in the same directory as the 'make_json.py' script. This dictionary maps values like the filter “F200W” to a specific key that the TNS site uses. Rather than enter the keys into your input table, I have written this conversion code so that you can simply enter the value (i.e., in your input table, you will write “F200W” rather than “185”, which is the TNS key for this filter). 

Below is a description of each table column that this script can handle. There is additional information that can be input into a TNS AT report (e.g., ‘proprietary_period’), but I have not built every possible option into the code. It would be fairly straightforward, however, to add a few lines to this code to convert new table columns into new json lines. I've also included an example input file ('input_example_catalog.txt') that contains all of the columns listed below and generates the 'output_example.json'.

In order to run the code from the command line, you must type 
`python make_json.py <your_input_catalog_name> <your_output_json_name.json>`

Below is a description of each table column that is currently enabled by the code:

### “ID” (required)

This is just so you’re required to have your own ID for each source. Purely organizational

### “RA” (required)
Right ascension of your sources. Must be in degrees

### “Dec” (required)
Declination of your sources. Must be in degrees

### “Reporting_Group” (required)
TNS Group that is writing the TNS report. Name must be included in this list of TNS group names (https://www.wis-tns.org/groups)

### “Data_Source” (required)
TNS Group whose data you discovered the transients in. Name must be included in the list of TNS group names (see above)

### “Reporter” (required)
“[your name] on behalf of [your collaboration]” or something like that

### “Discovery_Year” (required)
The year in which the transient was discovered. This is not the year you actually found it in the data; rather, this is the year in which the data was obtained

### “Discovery_Month” (required)
The month (number) in which the transient was discovered. This is not the month you actually found it in the data; rather, this is the month in which the data was obtained

### “Discovery_Day” (required)
The day on which the transient was discovered. This is not the day you actually found it in the data; rather, this is the day in which the data was obtained

### “AT_Type” (required)
The astronomical transient type. Options are: "PSN - Possible SN", "PNV - Possible Nova", "AGN - Known AGN", "NUC - Possibly nuclear", "FRB - Fast Radio Burst event", and "Other - Undefined". Note that you don’t have to write out the full word – as long as you write a word within the full option (i.e., write “PSN” instead of “PSN – Possible SN”, the code will find the correct key)

### “Host_ID” (optional)
The name you’d like to assign to the host. You don’t have to include this column in your table. However, if you do include it and only have host names for a subset of your sources, either make the “Host_ID” entry empty or ‘--’ for the sources without assigned host names.

### “Host_z” (optional)
The host redshift. You don’t have to include this column in your table. However, if you do include it and only have host redshifts for a subset of your sources, either make the “Host_z” entry empty or ‘--’ or ‘-99’ for the sources without assigned host redshifts.

### “Internal_Name” (optional)
This is where you list internal names you’d like to assign to your transients. This is optional. If you don’t want to assign internal names, don’t include this column in your input table

### “Remarks” (optional)
This is where you can make comments about host assignment quality, host redshift, quality, etc. This is optional, so if you have no remarks to make, do not include this column in your input table. If you only have remarks for a subset of your sources, make sure the entries for all other sources are ‘--’ or empty

### “Reference_Method” (required)
The only options for this column are either “Observation” or “Archive.” If you select “Observation”, then you will list out specific information regarding the reference image date, filter, instrument, etc. If you select “Archive”, then you will simply make an archival remark. More details later. You can have a mix of methods (i.e., differing source by source).

### “Reference_Year” (only required if “Reference_Method” == “Observation”)
The year in which the last observation in which your source was not detected was obtained

### “Reference_Month” (only required if “Reference_Method” == “Observation”)
The month (number) in which the last observation in which your source was not detected was obtained

### “Reference_Day” (only required if “Reference_Method” == “Observation”)
The day on which the last observation in which your source was not detected was obtained

### “Reference_Instrument” (only required if “Reference_Method” == “Observation”)
The instrument (e.g., ‘NIRCam’) that obtained the last non-detection of your source. While the full entry for NIRCam in the TNS dictionary is “JWST - NIRCam”, you’ll get the correct key by just entering “NIRCam” into your table since the string “NIRCam” is contained within the full “JWST - NIRCam” string

### “Reference_Filter” (only required if “Reference_Method” == “Observation”)
The filter (e.g., ‘F200W’) that obtained the last non-detection of your source. While the full entry for F200W in the TNS dictionary is “F200W-JWST”, you’ll get the correct key by just entering “F200W” into your table since the string “F200W” is contained within the full “F200W-JWST” string

### “Reference_Flux_Units” (only required if “Reference_Method” == “Observation”)
The flux units that are associated with the last non-detection (e.g., “ABMag”). Really only relevant if you enter a limiting flux for the reference epoch, but this is not a required field for the TNS AT reports, so I haven’t included it in this script (it would be simple to add though). The flux unit is still required though if you’re doing the “observation” reference method.

### “Archive” (only required if “Reference_Method” == “Archive”)
This refers to your archive. There are three options: “DSS”, “SDSS”, and “Other”. You will likely choose “Other”

### “Archival_Remark” (only required if “Reference_Method” == “Archive”)
A sentence or two describing your archival data. An example is “This source was not detected in Public Release IMaging for Extragalactic Research images (PRIMER; Cycle 1, GO 1837; https://primer-jwst.github.io/observations.html).”

### “XXX_Phot” (required at least once; can use multiple filters with multiple columns)
Here, “XXX” refers to your filter, so your column name may be “F200W_Phot”. Here, you would list your F200W photometry for however many sources you have F200W photometry for. If you do not have F200W photometry for a specific source, leave the cell empty or fill it with ‘--'

### “XXX_Phot_Err” (required at least once; can use multiple filters with multiple columns)
Here, “XXX” refers to your filter, so your column name may be “F200W_Phot_Err”. Here, you would list your F200W photometry uncertainty for however many sources you have F200W photometry for. If you do not have F200W photometry for a specific source, leave the cell empty or fill it with ‘--'

### “Discovery_Filter” (required)
Here, you list the filter whose photometry you want to list first for a source. If you have multiple bands of photometry and don’t care which one is listed first, just pick one. You just have to make sure your source has a measurement listed in the table for that specific filter (i.e., if F200W is your discovery filter for source2, make sure source2 has an F200W photometry measurement listed in the table). Note that if you have multiple bands of photometry listed in the table for a source, all of those photometric points will be reported (e.g., if you have “F200W_Phot” and “F150W_Phot” columns with measurements listed in both columns for a source, both photometric measurements will be reported). Your “discovery filter’s” photometry will just be listed first. If there are photometric measurements that you do not want published, do not list them in the table; leave those cells empty or as ‘--'. However, you do need at least one photometric measurement per source. While the full entry for F200W in the TNS dictionary is “F200W-JWST”, you’ll get the correct key by just entering “F200W” into your table since the string “F200W” is contained within the full “F200W-JWST” string

### “Discovery_Flux_Units” (required)
The flux units that are associated with your discovery photometry (e.g., “ABMag”)

### “Discovery_Instrument” (required)
The instrument (e.g., ‘NIRCam’) that discovered your source. While the full entry for NIRCam in the TNS dictionary is “JWST - NIRCam”, you’ll get the correct key by just entering “NIRCam” into your table since the string “NIRCam” is contained within the full “JWST - NIRCam” string

### “Discovery_Photometry_Comment” (optional)
If you have some specification to make about your photometry (e.g., “This photometric measurement may be contaminated by a subtraction residual.”), add a photometry comment. Only include this column if you intend to make photometry comments. Note that as the code currently exists, you can only add custom comments to the first photometry’s entry (i.e., the photometry associated with the “discovery filter”). However, it’d be fairly simple to add additional “photometry comment” columns to the table (and adjust the code as needed) to enable custom comments to be made for multiple filters.
