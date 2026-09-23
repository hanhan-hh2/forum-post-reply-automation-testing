# Forum Post/Reply Feature — Automation Testing

Automated test suite for the "Post/Reply in Forum" feature, built as part of a 
5-member software testing team project. Covers functional testing across two 
complexity levels and non-functional (security) testing, using a data-driven 
approach with Selenium WebDriver.

## What this covers
- **Level 1**: Data-driven functional tests using CSV test data
- **Level 2**: Data-driven tests with configurable Action URL and credentials 
  via `config.ini`, covering more complex scenarios
- **Non-functional**: Security testing (e.g. input validation, unauthorized 
  access attempts)

## Tech stack
Python, Selenium WebDriver, webdriver-manager

# Submit Assignment Automation Test

## Requirements

pip install selenium webdriver-manager

## Files

* test_submit_assignment.py - Level 1: Data-driven testing
* test_submit_assignment_level2.py - Level 2: Data-driven voi Action_URL va config.ini
* test_nonfunctional.py - Security testing (non-functional)
* test_data.csv - Test data Level 1
* test_data_level2.csv - Test data Level 2
* config.ini - Cau hinh URL, credentials, button text

## How to run

### Level 1

python test_submit_assignment.py

### Level 2

python test_submit_assignment_level2.py

### Non-functional (Security)

python test_nonfunctional.py
