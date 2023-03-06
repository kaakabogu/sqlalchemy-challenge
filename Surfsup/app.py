import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine=engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return prcp from last year"""
    # Query prcp for last 12 months
    all_prcp_data = [Measurement.date, Measurement.prcp]
    year_ago_date = dt.datetime(2016, 8, 22)
    
    prcp_query = session.query(*all_prcp_data).filter(Measurement.date > year_ago_date).order_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the data and append to a list 
    
    prcp_data =[]
    
    for date, prcp in prcp_query:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_data.append(prcp_dict)


    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    stations = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(stations))

    return jsonify(all_stations)
   
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return tobs from last year"""
    # Query tobs for last 12 months
    tobs_data = [Measurement.date, Measurement.tobs]
    year_ago_date = dt.datetime(2016, 8, 22)
    temp_at_most_active_station = session.query(*tobs_data).\
        filter(Measurement.date > year_ago_date).\
        filter(Measurement.station == 'USC00519281').\
        order_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list 
    tobs_data = []
    for date, tobs in temp_at_most_active_station:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

   
@app.route("/api/v1.0/<start>")
def dynamic_route_start_only(start):
    session = Session(engine)
    
    t_min = func.min(Measurement.tobs)
    t_max = func.max(Measurement.tobs)
    t_avg = func.avg(Measurement.tobs)

    params = [t_min, t_max, t_avg]

    temps = session.query(*params).\
        filter(Measurement.date >= start).all()
        
    session.close()
    
    all_temp_aggs = []
    for t_min, t_max, t_avg in temps:
        temp_aggs_dict = {}
        temp_aggs_dict["t_min"] = t_min
        temp_aggs_dict["t_max"] = t_max
        temp_aggs_dict["t_avg"] = t_avg
        all_temp_aggs.append(temp_aggs_dict)

    return jsonify(all_temp_aggs)

@app.route("/api/v1.0/<start>/<end>")
def dynamic_route_start_and_end(start, end):
    session = Session(engine)
    
    t_min = func.min(Measurement.tobs)
    t_max = func.max(Measurement.tobs)
    t_avg = func.avg(Measurement.tobs)

    params = [t_min, t_max, t_avg]

    temps_02 = session.query(*params).\
        filter(Measurement.date >= start, Measurement.date <= end).all()    

    session.close()

    all_temp_aggs = []
    for t_min, t_max, t_avg in temps_02:
        temp_aggs_dict = {}
        temp_aggs_dict["t_min"] = t_min
        temp_aggs_dict["t_max"] = t_max
        temp_aggs_dict["t_avg"] = t_avg
        all_temp_aggs.append(temp_aggs_dict)

    return jsonify(all_temp_aggs)
    
if __name__ == '__main__':
    app.run(debug=True)