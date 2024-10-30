# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc, and_
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station

measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#A lot of these routes use these dates, so I'm setting them up here ahead of time
latest = session.query(measurement).order_by(desc(measurement.date)).first().date
year_ago = datetime.strptime(latest, "%Y-%m-%d") - dt.timedelta(days=365)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print('Server received request for Home page')
    return ("Available routes <br>"
    "------------------------------------------<br>"
    "To view precipitation from each date of the past year: /api/v1.0/precipitation <br>"
    "To view list of stations: /api/v1.0/stations <br>"
    "To view one year of dates and temps from our most active station: /api/v1.0/tobs <br>"
    "To view min, avg, and max temp from a chosen start date onward: /api/v1.0/start <br>"
    "To view min, avg, and max temp from chosen start date to chosen end date: /api/v1.0/start/end <br>")
    

@app.route("/api/v1.0/precipitation")
def precipitation():
    print('Server received request for Precipitation page')
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_ago.strftime("%Y-%m-%d")).all()
    data = dict(results)
    return jsonify(data)

@app.route("/api/v1.0/stations")
def stations():
    print('Server received request for Stations page')
    station_data = session.query(station.name, station.station).all()
    station_dict = dict(station_data)
    return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    print('Server received request for Tobs page')
    counts = session.query(measurement.station, 
                       func.count(measurement.station).label('count')
                       ).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()

    tobs = session.query(measurement.date, measurement.tobs).filter(
        and_(
        measurement.date >= year_ago.strftime("%Y-%m-%d"),
        measurement.station == counts[0][0])
    ).all()
    tobs_dict = dict(tobs)
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def start(start):
    print('Server received request for Start page')

    results = session.query(
    func.max(measurement.tobs).label('max'),
    func.min(measurement.tobs).label('min'),
    func.avg(measurement.tobs.label('avg'))
    ).filter(measurement.date >= start).one()

    return (f"Min Temp: {results[1]} <br>"
            f"Avg Temp: {results[2]} <br>"
            f"Max Temp: {results[0]} <br>")

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    print('Server received request for Start/End page')

    results = session.query(
    func.max(measurement.tobs).label('max'),
    func.min(measurement.tobs).label('min'),
    func.avg(measurement.tobs.label('avg'))
    ).filter(
        and_(
            measurement.date >= start,
            measurement.date <= end)
            ).one()

    return (f"Min Temp: {results[1]} <br>"
            f"Avg Temp: {results[2]} <br>"
            f"Max Temp: {results[0]} <br>")

if __name__ == "__main__":
    app.run(debug=True)
