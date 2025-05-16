#!/bin/bash
# all python package dependencies are listed in requirements.txt

source venv/bin/activate

# download the USDA recalls data
# This requires using selenium because of bot detection on USDA recalls website
# commented out and just included the data for simplicity, but feel free to check/use code
#python3 get_usda_recalls.py

# assemble the data sets
# some large joins are done here so may be slow/demanding
python3 assemble_data.py

# run the analysis in stata
# need to install reghdfe to run
stata -b do estimate_model.do

#output is written to template_estimates.xlsx