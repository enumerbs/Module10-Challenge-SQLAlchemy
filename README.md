# Module10-Challenge-SQLAlchemy

Data Analytics Boot Camp - Module 10 - SQLAlchemy \
SQLAlchemy Challenge

---

# Results

The ***SurfsUp*** subfolder contains the following source code files:

**climate.ipynb** (for Part 1: Analyse and Explore the Climate Data)<br>
- Change directory into the SurfsUp folder
- Load and run the file from there as a Jupyter Notebook.

**app.py** (for Part 2: Design Your Climate App)<br>
- Change directory into the SurfsUp folder (if not already there)
- Invoke from the command-line as 'python app.py'
- Note the URL in the command line messages (e.g. http://127.0.0.1:5000)
- Enter that URL into your browser to see a description of the available API routes.

# Implementation notes

**climate.ipynb** - Precipitation Analysis
 - Attempting to use Pandas' Dataframe plot() method to plot the bar chart resulted in the x-axis date values being displayed with year values of 1970. This appears to be some mis-match between Pandas' and matplotlib's datetime handling.
 - The workaround was to use matplotlib functions for both the bar plot and the associated axis ticks and labels. See the References section below for StackOverflow articles on this subject.

  **app.py** - SQLAlchemy / database Session management
  - It was mentioned in class / sample code examples that good practice is to create the Session, use it to query the required data from the database, and then close the Session immediately once it's no longer required in each route handler method (so as to minimise blocking access to the database from other potential user sessions).
  - So, while the starter code for this Challenge exercise indicated via a comment to open the Session only once at the start of the file (and by implication close it only once at the end of the file), this implementation opens and closes a new Session instance in each route handler.

 **app.py** - Temperature observation data - Min / Avg / Max values
 - The challenge instructions ask for different orders of these values at different points, which is confusing.
 - For example, in Part 2, item 5 it specifies "Return a JSON list of minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range".
 - In contrast, the Requirement summary/marking rubric specifies the start route, and start/end route, must return the min, max, and average temperatures (in other words, the same values but in a different order).
 - To avoid confusion, the API implementation returns a simple JSON list of temperature values (in order Min, Avg, Max) by default, or a JSON dictionary (with labels TAVG, TMAX, and TMIN in alphabetical order) if the query string "?mode=dict" is appended to the API endpoint.
 - For example, for the Temperature observations 'Start' endpoint:
 ```
 /api/v1.0/2017-07-01
 ```
 returns
 ```
 [20.6, 25.89, 30.6]
 ```
 or alternatively using
 ```
 /api/v1.0/2017-07-01?mode=dict
```
returns
```
[{"TAVG":25.89,"TMAX":30.6,"TMIN":20.6}]
```

# References

The following references were used in the development of the solution for this Challenge.

## Flask
- Accessing URL query string parameters in Flask routes
    - https://stackoverflow.com/questions/11774265/how-do-you-access-the-query-string-in-flask-routes

## HTML Character Entities

- Encoding for reserved characters in HTML
    - https://www.w3schools.com/html/html_entities.asp

## HTTP Response Status Codes
- Client error responses
    - https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#client_error_responses

## Pandas / Matplotlib - problems with x-axis Date values
- Work-around for Date values shown with year as 1970
    - https://stackoverflow.com/questions/64919511/dateformatter-is-bringing-1970-as-year-not-the-original-year-in-the-dataset
- Controlling x-axis labels in general, especially for bar charts with Date values on the x-axis
    - https://stackoverflow.com/questions/30133280/pandas-bar-plot-changes-date-format

## Python - data conversion & calculations
- Add 1 year to a date
    - https://stackoverflow.com/questions/54394327/using-datetime-timedelta-to-add-years
- Rounding values in a list
    - https://stackoverflow.com/questions/5326112/how-to-round-each-item-in-a-list-of-floats-to-2-decimal-places

## SQLAlchemy ORM
- Class notes/sample files for 'Advanced Usage of the SQLAlchemy ORM', Monash University 'Data Analytics Boot Camp'
- Query for results between two dates
    - https://www.slingacademy.com/article/sqlalchemy-select-rows-between-two-dates/#Selection_with_ORM
