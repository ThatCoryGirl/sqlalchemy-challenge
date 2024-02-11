# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask
from flask import jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Start at the homepage, list all the available routes
@app.route("/")
def home():
    """List all available routes."""
    routes = [
        "/api/v1.0/precipitation",
        "/api/v1.0/stations",
        "/api/v1.0/tobs",
        "/api/v1.0/<start>",
        "/api/v1.0/<start>/<end>"
    ]
    # Close the session
    session.close()
    # Show a list
    return "Available Routes:<br/>" + "<br/>".join(routes)

# Convert the query results from your precipitation analysis (retrieve only the last 12 months of data) to a dictionary
# using date as the key and precipitation as the value
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a JSON representation of precipitation data for the last 12 months."""
    last_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_date).all()
    precipitation_data = {date: prcp for date, prcp in results}
    # Close the session
    session.close()
    # Show a list
    return jsonify(precipitation_data)

# Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    results = session.query(Station.station).all()
    station_list = list(np.ravel(results))
    # Close the session
    session.close()
    # Show a list
    return jsonify(station_list)

# Query the dates and temperature observations of the most-active station for the previous year of data
# Return a JSON list of temperature observations for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the most active station for the previous year."""
    last_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).first()[0]
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= last_date).all()
    temperature_data = [{date: tobs} for date, tobs in results]
    # Close the session
    session.close()
    # Show a list
    return jsonify(temperature_data)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for
# a specificed start or start-end range.
# For a specificed start, calculate tmin, tavg, and tmax for the dates from the start date to the end date,
# inclusive
@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return a JSON list of the minimum, average, and maximum temperatures for a given start date."""
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    temperature_stats = {
        "Min Temperature": results[0][0],
        "Avg Temperature": results[0][1],
        "Max Temperature": results[0][2]
    }
    # Close the session
    session.close()
    # Show a list
    return jsonify(temperature_stats)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return a JSON list of the minimum, average, and maximum temperatures for a given start-end range."""
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temperature_stats = {
        "Min Temperature": results[0][0],
        "Avg Temperature": results[0][1],
        "Max Temperature": results[0][2]
    }
    # Close the session
    session.close()
    # Show a list
    return jsonify(temperature_stats)
# The End
if __name__ == '__main__':
    app.run(debug=True)

