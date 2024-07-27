# Module10-Challenge-SQLAlchemy

Data Analytics Boot Camp - Module 10 - SQLAlchemy \
SQLAlchemy Challenge

---

# Results

The ***SurfsUp*** subfolder contains the following source code files

Part 1: Analyse and Explore the Climate Data
- climate.ipynb

Part 2: Design Your Climate App
- app.py

# Implementation notes

Precipitation Analysis
 - Attempting to use Pandas' Dataframe plot() method to plot the bar chart resulted in the x-axis date values being displayed with year values of 1970. This appears to be some mis-match between Pandas' and matplotlib's datetime handling.
 - The workaround was to use matplotlib functions for both the bar plot and the associated axis ticks and labels. See the References section below for one example of a StackOverflow article on this subject.

# References

The following references were used in the development of the solution for this Challenge.

## SQLAlchemy ORM
- Class notes/sample files for 'Advanced Usage of the SQLAlchemy ORM', Monash University 'Data Analytics Boot Camp'
- Query for results between two dates
    - https://www.slingacademy.com/article/sqlalchemy-select-rows-between-two-dates/#Selection_with_ORM

## Python - date conversion & calculations
- Add 1 year to a date
    - https://stackoverflow.com/questions/54394327/using-datetime-timedelta-to-add-years

## Pandas / Matplotlib - problems with x-axis Date values
- Work-around for Date values shown with year as 1970
    - https://stackoverflow.com/questions/64919511/dateformatter-is-bringing-1970-as-year-not-the-original-year-in-the-dataset
