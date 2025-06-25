#Purpose: Create Input JSON for TNS AT Report

import astropy.io.ascii as ascii
import numpy as np
import sys
import re
from astropy import units as u
from astropy.coordinates import SkyCoord
import json

# Before running this script, make sure you:
# (1) Download this 'values.json' file ( https://www.wis-tns.org/api/get/values) and save it in the same directory as this script
# (2) Review TNS's guide for bulk reports: https://www.wis-tns.org/sites/default/files/api/tns2_manuals/TNS2.0_bulk_reports_manual.pdf

# There's additional non-required information that can be built into this script (e.g., limiting flux of discovery and reference epochs)
# Here is a link to the current TNS Group IDs: https://www.wis-tns.org/groups

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

input_table_path = sys.argv[1] # file path to your input transient table
save_name = sys.argv[2]        # name to save your output file to  

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

# Open the TNS JSON file containing all of the keyword associations

json_filename = 'values.json'
try:
    with open(json_filename, 'r') as file:
        tns_dict = json.load(file)
except FileNotFoundError:
    print(f"Error: The file '{json_filename}' was not found.")
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from '{json_filename}'. Check if the file contains valid JSON.")

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

# Function for associated dictionary value with its keyword

def get_key_from_value(parent_key, target_value):
	"""
	Returns the first key in a dictionary that corresponds to the given value (should be correct key because 1:1 correspondence between key and value in TNS dict)

	Args:
	parent_key: The keyword indicating the area you're searching within the TNS dict
	target_value: The value to search for (doesn't need to be full value; i.e., can be 'PSN' instead of 'PSN - Possible SN')

	Returns:
	The key associated with the target_value, or raises a ValueError if the value is not in the dictionary
	"""

	found = False
	for key, value in tns_dict['data'][parent_key].items():
		if target_value in value:
			found = True
			return str(key)

	if(found == False):

		# Sometimes your filter isn't in TNS Dict, so you use "Other" (key = '0') and leave a comment with the filter name (built into code later)
		if(parent_key == 'filters'):
			return('0')
		else:
			raise ValueError('Value %s not in TNS dictionary' % target_value)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

# Read in the Source Table
tab = ascii.read(input_table_path)

with open('%s' % save_name, 'w') as file:
	file.write('{\n')
	file.write('  "at_report": {\n')
	for i in range(len(tab['ID'])):

		# Source Number
		file.write('    "' + str(i)+ '": {\n')

		# RA/Dec --> Needs specific formatting like ('02:23:49.531 +10:14:10.340')
		c_deg = SkyCoord(ra=tab['RA'][i]*u.degree, dec=tab['Dec'][i]*u.degree)
		ra_hms, dec_dms = c_deg.ra.hms, c_deg.dec.dms

		# Need to ensure that there's a '0' preceding any value <10 in hours, minutes, or seconds; add '+' if dec is positive and '-' if dec is negative
		ra = f"{ra_hms[0]:02.0f}" + ':' + f"{ra_hms[1]:02.0f}" + ':' + f"{ra_hms[2]:05.2f}"
		dec = f"{abs(dec_dms[0]):02.0f}" + ':' + f"{abs(dec_dms[1]):02.0f}" + ':' + f"{abs(dec_dms[2]):05.2f}"		
		if(tab['Dec'][i] > 0):
			dec = '+' + dec
		else:
			dec = '-' + dec

		file.write('      "ra": {\n')
		file.write('        "value": "' + str(ra) + '"\n')
		file.write('      },\n')
		file.write('      "dec": {\n')
		file.write('        "value": "' + str(dec) + '"\n')
		file.write('      },\n')

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

		# Reporting Group ID
		file.write('      "reporting_groupid": "' + get_key_from_value('groups', tab['Reporting_Group'][i]) + '",\n')

		# Discovery Data Source ID
		file.write('      "data_source_groupid": "' + get_key_from_value('groups', tab['Data_Source'][i]) + '",\n')

		# Reporter
		file.write('      "reporter": "' + tab['Reporter'][i] + '",\n')

		# Discovery DateTime
		discovery_obsdate = f"{tab['Discovery_Year'][i]:4.0f}" + '-' + f"{tab['Discovery_Month'][i]:02.0f}" + '-' + f"{tab['Discovery_Day'][i]:02.0f}"
		file.write('      "discovery_datetime": "' + discovery_obsdate + '",\n')

		# AT Type
		file.write('      "at_type": "' + get_key_from_value('at_types', tab['AT_Type'][i]) + '",\n')

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

		# Host Name --> not required, so only list these if column is present in table
		if 'Host_ID' in tab.colnames:
		
			# Only list out host ID if host is known --> weird behavior with empty values, so I'm trying to cover all of the bases ('--', None, '')
			if str(tab['Host_ID'][i]) != '--' and tab['Host_ID'][i] is not None and str(tab['Host_ID'][i]) != '':
				file.write('      "host_name": "' + str(tab['Host_ID'][i]) + '",\n')

		# Host Redshift --> not required, so only list these if column is present in table
		if 'Host_z' in tab.colnames:

			# Only list out host z if it is known --> weird behavior with empty values, so I'm trying to cover all of the bases ('--', None, '', -99)
			if str(tab['Host_z'][i]) != '--' and tab['Host_z'][i] is not None and str(tab['Host_z'][i]) != '' and tab['Host_z'][i] > 0:
				file.write('      "host_redshift": "' + str(tab['Host_z'][i]) + '",\n')	

		# Internal Name --> not required, so only list these if column is prseent in table
		if 'Internal_Name' in tab.colnames:

			# Only include internal name if it's included in table --> weird behavior with empty values, so I'm trying to cover all of the bases ('--', None, '', -99)
			if str(tab['Internal_Name'][i]) != '--' and tab['Internal_Name'][i] is not None and str(tab['Internal_Name'][i]) != '':
				file.write('      "internal_name": "' + str(tab['Internal_Name'][i]) + '",\n')	

		# Remarks --> not required, so only list these if present in table; remarks usually refer to special notes about host association, host redshift, etc.
		if 'Remarks' in tab.colnames:
			# Weird behavior with empty values, so I'm trying to cover all of the bases ('--', None, '')
			if str(tab['Remarks'][i]) != '--' and tab['Remarks'][i] is not None and str(tab['Remarks'][i]) != '':
				file.write('      "remarks": "' + tab['Remarks'][i] + '",\n')	

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

		# Last Non-Detection --> Use either the 'Observation' or 'Archive' method as specified by the 'Reference_Method' column in your input table
		file.write('      "non_detection": {\n')
		if tab['Reference_Method'][i] == 'Observation':
			reference_obsdate = f"{tab['Reference_Year'][i]:4.0f}" + '-' + f"{tab['Reference_Month'][i]:02.0f}" + '-' + f"{tab['Reference_Day'][i]:02.0f}"
			file.write('        "obsdate": "' + reference_obsdate + '",\n')
			file.write('        "flux_unitid": "' + get_key_from_value('units', tab['Reference_Flux_Units'][i]) + '",\n')
			file.write('        "filterid": "' + get_key_from_value('filters', tab['Reference_Filter'][i]) + '",\n') 
			file.write('        "instrumentid": "' + get_key_from_value('instruments', tab['Reference_Instrument'][i]) + '"\n')
		elif tab['Reference_Method'][i] == 'Archive':
			file.write('        "archiveid": "' + get_key_from_value('archives', tab['Archive'][i]) + '",\n')
			file.write('        "archival_remarks": "' + tab['Archival_Remark'][i] + '"\n')
		else:
			raise ValueError("Value in Reference_Method column must be either 'Archive' or 'Observation'; you have listed '%s'" % tab['Reference_Method'][i])
		file.write('      },\n')

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

		# First figure out if you want to make a photometry comment (because that affects structure in the photometry section)
		commenting = False
		comment = ''
		if 'Discovery_Photometry_Comment' in tab.colnames:

			# Only include photometry comment if it's included in table --> weird behavior with empty values, so I'm trying to cover all of the bases ('--', None, '')
			if str(tab['Discovery_Photometry_Comment'][i]) != '--' and tab['Discovery_Photometry_Comment'][i] is not None and str(tab['Discovery_Photometry_Comment'][i]) != '':
				comment = tab['Discovery_Photometry_Comment'][i] + '. '
				commenting = True

		# If your filter is not in TNS Dict, you must leave comment with filter name
		if(get_key_from_value('filters', tab['Discovery_Filter'][i]) == '0'):
			commenting = True
			comment = comment + 'Filter is ' + tab['Discovery_Instrument'][i] + '-' + tab['Discovery_Filter'][i] + '. '

		# Photometry
		file.write('      "photometry": {\n')
		file.write('        "0": {\n')
		file.write('          "obsdate": "' + discovery_obsdate + '",\n')
		file.write('          "flux": "' + str(tab['%s_Phot' % tab['Discovery_Filter'][i]].tolist()[i]) + '",\n')
		file.write('          "flux_error": "' + str(tab['%s_Phot_Err' % tab['Discovery_Filter'][i]].tolist()[i]) + '",\n')
		file.write('          "flux_unitid": "' + get_key_from_value('units', tab['Discovery_Flux_Units'][i]) + '",\n')
		file.write('          "filterid": "' + get_key_from_value('filters', tab['Discovery_Filter'][i]) + '",\n')
		if(commenting == False):
			file.write('          "instrumentid": "' + get_key_from_value('instruments', tab['Discovery_Instrument'][i]) + '"\n')
		else:
			file.write('          "instrumentid": "' + get_key_from_value('instruments', tab['Discovery_Instrument'][i]) + '",\n')
			file.write('          "comments": "' + comment + '"\n')		

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

		# Reporting multiple photometric points for one source
		# All points listed in your input table will be reported. If you don't want certain photometry published, remove it from your table
		# If you'd like to have custom 'Photometry Comments' for the additional photometry (that is different than just reporting non-TNS filter), add columns to input table and adjust this code as needed
		# Only customized 'discovery' photometry comments are supported in the code as it currently exists

		filter_list = []
		colname_list = [item for item in tab.colnames if 'W_Phot' in item] # 'W_' prevents 'Discovery_Photometry_Comment' from being included
		for col in colname_list:
			band = col.split('_', maxsplit=1)[0]

			# Only add bands that are not the discovery band (since that is already reported) and that do have photometry listed --> hitting all the bases with '--', None, ''
			# First condition ensures no duplicate filters (since there is 'Phot' and 'Phot_Err' that filters will be drawn from)
			if band not in filter_list and band != tab['Discovery_Filter'][i] and str(tab['%s_Phot'%band][i]) != '--' and tab['%s_Phot'%band][i] is not None and str(tab['%s_Phot'%band][i]) != '':
				filter_list.append(band)

		if(len(filter_list)) == 0:
			file.write('        }\n') # No comma because there is no more photometry to report
		else:
			file.write('        },\n') # Comma because there is at least one additional photometric point to report

		# Extra Photometry --> assumes same flux units + instrument (but different filter)
		for j in range(len(filter_list)):

			# Figure out if you need to leave a comment (i.e., if filter is not in TNS Dict)
			commenting2 = False
			if(get_key_from_value('filters', filter_list[j]) == '0'):
				commenting2 = True

			file.write('        "' + str(j+1) + '": {\n')
			file.write('          "obsdate": "' + discovery_obsdate + '",\n')
			file.write('          "flux": "' + str(tab['%s_Phot' % filter_list[j]].tolist()[i]) + '",\n')
			file.write('          "flux_error": "' + str(tab['%s_Phot_Err' % filter_list[j]].tolist()[i]) + '",\n')
			file.write('          "flux_unitid": "' + get_key_from_value('units', tab['Discovery_Flux_Units'][i]) + '",\n')
			file.write('          "filterid": "' + get_key_from_value('filters', filter_list[j]) + '",\n')
			if(commenting2 == False):
				file.write('          "instrumentid": "' + get_key_from_value('instruments', tab['Discovery_Instrument'][i]) + '"\n')	
			else:
				file.write('          "instrumentid": "' + get_key_from_value('instruments', tab['Discovery_Instrument'][i]) + '",\n')	
				file.write('          "comments": "Filter is ' + tab['Discovery_Instrument'][i] + '-' + filter_list[j] + '. ' + '"\n')	


			if j != (len(filter_list)-1):
				file.write('        },\n') # Comma because there is at least one additional photometric point to report
			else:
				file.write('        }\n')  # No comma because there is no more photometry to report 		

		# Ending the Photometry Section
		file.write('      }\n')

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

		# Comma if there's additional sources to report; no comma if this is the final source
		if(i != len(tab['ID'])-1):
			file.write('    },\n')
		else:
			file.write('    }\n')

	file.write('  }\n')
	file.write('}')