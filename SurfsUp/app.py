# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

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
        f"<h1>Welcome to the Hawaii Climate API!</h1>"
        f"<h2>Available Routes:</h2>"
        f"<p>/api/v1.0/precipitation</p>"
        f"<p>/api/v1.0/stations</p>"
        f"<p>/api/v1.0/tobs</p>"
        f"<p>/api/v1.0/&lt;start&gt;</p>"
        f"<p>/api/v1.0/&lt;start&gt;/&lt;end&gt;</p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return all precipitation measurements sorted by date"""
    # Query all precipitation by date
    precipitation_tuples = session.query(Measurement.date, Measurement.prcp).all()
    
    # Convert tuples to dataframe taking on column names 'date' and 'prcp' from the query
    precipitation_df = pd.DataFrame(precipitation_tuples)
    
    # Replace NaN values with zero
    precipitation_df["prcp"] = precipitation_df["prcp"].fillna(0)
    
    # Sort results by date
    precipitation_df = precipitation_df.sort_values(by=["date"])

    # Convert to a dictionary and return result 
    precipitation_dict = precipitation_df.to_dict(orient="records")
    return precipitation_dict

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all measurement station identifiers sorted alphabetically"""
    # Query for station names
    station_tuples = session.query(Station.station).order_by(Station.station).all()

    # Convert list of tuples into normal list
    stations = list(np.ravel(station_tuples))

    # Return result in JSON format
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations of the most-active station for the previous year of data"""
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

@app.route("/api/v1.0/<start>")
def min_avg_max_temperatures_from(start):
    """Calculate MIN, AVG, and MAX temperature for all dates greater than or equal to the start date."""
    try:
        # Convert the supplied start date from string to date type
        start_date = dt.date.fromisoformat(start)
    except:
        # Date conversion error: return error description to the caller; set HTTP status code 400 'Bad request'
        return {"error": f"Start date {start} is not in yyyy-mm-dd format"}, 400
    else:
        # Calculate the min/avg/max temperature statistics for observations from the given start date (inclusive)
        tobs_statistics_tuple = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                                .filter(Measurement.date >= start_date)\
                                .all()
  
        # Convert result tuple into a normal list
        tobs_statistics = list(np.ravel(tobs_statistics_tuple))
        if tobs_statistics[0] != None:
            # Round values to 2 decimal places
            tobs_statistics = list(np.around(np.array(tobs_statistics),2))

        # Return result in JSON format
        return jsonify(tobs_statistics)

@app.route("/api/v1.0/<start>/<end>")
def min_avg_max_temperatures_from_to(start, end):
    """calculate MIN, AVG, and MAX temperature for all dates from the start date to the end date, inclusive."""
    try:
        # Convert the supplied dates from string to date type
        start_date = dt.date.fromisoformat(start)
        end_date = dt.date.fromisoformat(end)
    except:
        # Date conversion error: return error description to the caller; set HTTP status code 400 'Bad request'
        return {"error": f"Start date {start} and/or End date {end} is not in yyyy-mm-dd format"}, 400
    else:
        # Calculate the min/avg/max temperature statistics for observations from the given start date to end date (inclusive)
        tobs_statistics_tuple = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                                .filter(Measurement.date >= start_date)\
                                .filter(Measurement.date <= end_date)\
                                .all()
  
        # Convert result tuple into a normal list
        tobs_statistics = list(np.ravel(tobs_statistics_tuple))
        if tobs_statistics[0] != None:
            # Round values to 2 decimal places
            tobs_statistics = list(np.around(np.array(tobs_statistics),2))

        # Return result in JSON format
        return jsonify(tobs_statistics)

#################################################
# Database Cleanup
#################################################
session.close()

#------------------------------------------------
# Support for invocation from the command line
if __name__ == "__main__":
    app.run(debug=True)