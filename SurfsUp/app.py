# Import the dependencies.
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

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
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"

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

#################################################
# Database Cleanup
#################################################
session.close()

#------------------------------------------------
# Support for invocation from the command line
if __name__ == "__main__":
    app.run(debug=True)