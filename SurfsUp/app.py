# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, request

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<h1>Welcome to the Hawaii Climate API</h1>"
        f"<h2>Available Routes:</h2>"

        f"<p><b>/api/v1.0/precipitation</b></br>\
        All precipitation measurements for the last year of data sorted by date</p>"

        f"<p><b>/api/v1.0/stations</b></br>\
        All measurement station identifiers sorted alphabetically</p>"

        f"<p><b>/api/v1.0/tobs</b></br>\
        Temperature observations of the most-active station for the last year of data</p>"

        f"<p><b>/api/v1.0/&lt;start&gt;</b></br>\
        MIN, AVG, and MAX temperature (as a list of values in that order) for all dates greater than or equal to the 'start' date</br>\
        Alternatively, append ?mode=dict to the above route for the values labelled in alphabetical order as TAVG, TMAX, and TMIN, respectively.</br>\
        Examples:</br>\
        /api/v1.0/2017-07-01</br>\
        /api/v1.0/2017-07-01?mode=dict</p>"

        f"<p><b>/api/v1.0/&lt;start&gt;/&lt;end&gt;</b></br>\
        MIN, AVG, and MAX temperature (as a list of values in that order) for all dates from the 'start' date to the 'end' date, inclusive</br>\
        Alternatively, append ?mode=dict to the above route for the values labelled in alphabetical order as TAVG, TMAX, and TMIN, respectively.</br>\
        Examples:</br>\
        /api/v1.0/2017-07-01/2017-07-31</br>\
        /api/v1.0/2017-07-01/2017-07-31?mode=dict</p>"
    )

#------------------------------------------------

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return all precipitation measurements for the last year of data sorted by date"""
    # Find the most recent measurement date in the data set.
    most_recent_date_str = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.date.fromisoformat(most_recent_date_str[0])

    # Calculate the date one year from the last date in data set.
    one_year_before_last_date = last_date + relativedelta(years=-1)

    # Query all precipitation for the last year of data
    precipitation_tuples = session.query(Measurement.date, Measurement.prcp)\
                            .filter(Measurement.date.between(one_year_before_last_date, last_date))\
                            .all()

    # Convert tuples to dataframe taking on column names 'date' and 'prcp' from the query
    precipitation_df = pd.DataFrame(precipitation_tuples)

    # Replace NaN values with zero
    precipitation_df["prcp"] = precipitation_df["prcp"].fillna(0)

    # Sort results by date
    precipitation_df = precipitation_df.sort_values(by=["date"])

    # Convert to a dictionary and return result
    precipitation_dict = precipitation_df.to_dict(orient="records")
    return precipitation_dict

#------------------------------------------------

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all measurement station identifiers sorted alphabetically"""
    # Query for station names
    station_tuples = session.query(Station.station).order_by(Station.station).all()

    # Convert list of tuples into normal list
    stations = list(np.ravel(station_tuples))

    # Return result in JSON format
    return jsonify(stations)

#------------------------------------------------

@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations of the most-active station for the last year of data"""
    # Determine the most active station
    most_active_station_tuple = session.query(Station.station, func.count(Measurement.station))\
        .join(Measurement, Station.station == Measurement.station)\
        .group_by(Station.station)\
        .order_by(func.count(Measurement.station).desc())\
        .first()

    most_active_station_id = most_active_station_tuple[0]

    # Find the most recent observation date for this station
    most_recent_date_str = session.query(func.max(Measurement.date))\
        .filter(Measurement.station == most_active_station_id)\
        .one()

    # Convert to a date type and calculate the date one year earlier
    last_date = dt.date.fromisoformat(most_recent_date_str[0])
    one_year_before_last_date = last_date + relativedelta(years=-1)

    # Define a query to retrieve the temperature observation data for this station
    last12months_tobs_tuples = session.query(Measurement.tobs)\
                                .filter(Measurement.date.between(one_year_before_last_date, last_date))\
                                .filter(Measurement.station == most_active_station_id)\
                                .all()

    # Convert list of tuples into normal list
    last12months_tobs = list(np.ravel(last12months_tobs_tuples))

    # Return result in JSON format
    return jsonify(last12months_tobs)

#------------------------------------------------

@app.route("/api/v1.0/<start>")
def min_avg_max_temperatures_from(start):
    """Calculate MIN, AVG, and MAX temperature for all dates greater than or equal to the specified start date."""
    try:
        # Convert the supplied start date from string to date type
        start_date = dt.date.fromisoformat(start)
    except:
        # Date conversion error: return error description to the caller; set HTTP status code 400 'Bad request'
        return {"error": f"Start date {start} is not a valid date in yyyy-mm-dd format"}, 400
    else:
        # Calculate the min/avg/max temperature statistics for observations from the given start date (inclusive)
        tobs_statistics_tuple = session.query(func.min(Measurement.tobs).label("TMIN"),\
                                              func.avg(Measurement.tobs).label("TAVG"),\
                                              func.max(Measurement.tobs).label("TMAX"))\
                                .filter(Measurement.date >= start_date)\
                                .all()

        # Convert tuple to dataframe taking on column names from the query
        tobs_statistics_df = convert_min_avg_max_query_result_to_dataframe(tobs_statistics_tuple)

        # Return result in JSON format
        return format_min_avg_max_temperatures_as_JSON(tobs_statistics_df)

#------------------------------------------------

@app.route("/api/v1.0/<start>/<end>")
def min_avg_max_temperatures_from_to(start, end):
    """Calculate MIN, AVG, and MAX temperature for all dates from the specified start date to the specified end date, inclusive."""
    try:
        # Convert the supplied dates from string to date type
        start_date = dt.date.fromisoformat(start)
        end_date = dt.date.fromisoformat(end)
    except:
        # Date conversion error: return error description to the caller; set HTTP status code 400 'Bad request'
        return {"error": f"Start date {start} and/or End date {end} is not a valid date in yyyy-mm-dd format"}, 400
    else:
        # Calculate the min/avg/max temperature statistics for observations from the given start date to end date (inclusive)
        tobs_statistics_tuple = session.query(func.min(Measurement.tobs).label("TMIN"),\
                                              func.avg(Measurement.tobs).label("TAVG"),\
                                              func.max(Measurement.tobs).label("TMAX"))\
                                .filter(Measurement.date >= start_date)\
                                .filter(Measurement.date <= end_date)\
                                .all()

        # Convert tuple to dataframe taking on column names from the query
        tobs_statistics_df = convert_min_avg_max_query_result_to_dataframe(tobs_statistics_tuple)

        # Return result in JSON format
        return format_min_avg_max_temperatures_as_JSON(tobs_statistics_df)

#################################################
# Utility functions
#################################################

def convert_min_avg_max_query_result_to_dataframe(tobs_statistics_tuple):
    # Convert tuple to dataframe taking on column names from the query
    tobs_statistics_df = pd.DataFrame(tobs_statistics_tuple)

    # If the query returned a non-null record (i.e. data was found for the given start date), then round the results to 2 decimal places
    if tobs_statistics_df["TMIN"][0] != None:
        tobs_statistics_df = tobs_statistics_df.round(2)

    return tobs_statistics_df

#------------------------------------------------

def format_min_avg_max_temperatures_as_JSON (temperatures_df):
    # Return result in JSON format:
    # - as labelled key:value pairs if the query string specified "dict"ionary mode, or
    # - as a list of three values (in MIN-AVG-MAX order) otherwise.
    if request.args.get("mode") == "dict":
        return temperatures_df.to_dict(orient="records")
    else:
        return jsonify(temperatures_df.iloc[0].to_list())

#################################################
# Database Session Cleanup
#################################################
session.close()

#################################################
# Support for invocation from the command line
#################################################
if __name__ == "__main__":
    app.run(debug=False)