import sqlalchemy
import numpy as np
import datetime as dt
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker

####################################################################################################################################################################################################
######################I grabbed a lot of this setup content from 01-Lesson-Plans/10-Advanced-Data-Storage-and-Retrieval/3/Activities/10-Ins_Flask_with_ORM/Solved/app.py############################
####################################################################################################################################################################################################

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# scoped_session prevents the need of having an open and close session on each route.
session = scoped_session(sessionmaker(bind=engine))

last_day = session.query(
    Measurement.date
    ).order_by(
    Measurement.date.desc()
    ).first()[0]

last_day = dt.datetime.strptime(last_day, "%Y-%m-%d")
first_day = last_day - dt.timedelta(days=365)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        '<a href="/api/v1.0/precipitation"> Click here to see precipitation info.</a> <br />'
        '<a href="/api/v1.0/stations"> Click here to see the list of stations that provided data.</a> <br />'
        '<a href="/api/v1.0/tobs"> Click here to see a years worth of observation data.</a> <br />'
        '<a href="/api/v1.0/<start>"> Click here and enter a day (before 2017-08-24) to see data from the selected day.</a> <br />'
        '<a href="/api/v1.0/<start>/<end>"> Click here to see data from a range of days (starting after 2010-01-01 and ending before 2017-08-24).</a> <br />'
        )


@app.route("/api/v1.0/precipitation")
def precipitation():  
    # Calculation from climate_starter.ipynb
    year_review = session.query(
        Measurement.date,
        Measurement.prcp
    ).filter(
        Measurement.date > first_day
        ).order_by(
            Measurement.date
            ).all()

    # Convert list of tuples into normal list
    precipitation_data = dict(year_review)

    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station).all()
    stations_list = list()
    for station in stations:
        stations_dict = dict()
        stations_dict['Station'] = station.station
        stations_dict['Name'] = station.name
        stations_dict['Latitude'] = station.latitude
        stations_dict['Longitude'] = station.longitude
        stations_dict['Elevation'] = station.elevation
        stations_list.append(stations_dict)

    return jsonify(stations_list)
    
@app.route("/api/v1.0/tobs")
def tobs():
    tobs_list = list()
    year_tobs = session.query(
        Measurement.tobs,
        Measurement.date,
        Measurement.station,
        ).filter(
            Measurement.date > first_day
            ).all()

    for tob in year_tobs:
        tobs_dict = dict()
        tobs_dict['Temp'] = tob.tobs
        tobs_dict['Data'] = tob.date
        tobs_dict['Station'] = tob.station
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start_temp(start = None):
    start_list = list()
    start_temp = session.query(
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ).filter(Measurement.date >= start
    ).all()

    for tmax, tmin, tavg in start_temp:
        start_dict = dict()
        start_dict['Min Temp'] = tmin
        start_dict['Max Temp'] = tmax
        start_dict['Avg Temp'] = tavg
        start_list.append(start_dict)

    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def range_temp(start=None, end=None):
    start_list = list()
    range_temp = session.query(
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ).filter(Measurement.date >= start,
             Measurement.date <= end
             ).all()

    for tmax, tmin, tavg in range_temp:
        start_dict = dict()
        start_dict['Min Temp'] = tmin
        start_dict['Max Temp'] = tmax
        start_dict['Avg Temp'] = tavg
        start_list.append(start_dict)

    return jsonify(start_list)

if __name__ == '__main__':
    app.run(debug=True)
