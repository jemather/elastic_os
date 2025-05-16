# Elastic Open Science replication package

Replication package for my analysis as part of the Elastic Open Science project

## Description

An in-depth paragraph about your project and overview of use.

## Getting Started

### Dependencies

* Python
* Stata

### Installing

* Create a virtual environment for Python and install dependencies
```
python3 -m venv venv
pip install -r requirements.txt
```

* Make sure reghdfe is available in Stata
```
ssc install reghdfe
```

### Executing program

* Run the shell script to pull the data from the USDA (Python, with Selenium to drive a Chrome browser), assemble with the other data sets (Python), and then estimate the model (Stata)
```
./calcualte_elasticities.sh
```


## Authors

[Ted Matherly](https://www.tedmatherly.com)

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

