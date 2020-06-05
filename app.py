from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np

############################################
#database connection setup
engine = create_engine("sqlite:///resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

temp_mea = Base.classes.measurement
stations = Base.classes.station
session = Session(engine)

#most active station
station_records_count = session.query(temp_mea.station, func.count(temp_mea.prcp)).\
    group_by(temp_mea.station).\
    order_by(func.count(temp_mea.prcp).desc())

most_active_station = station_records_count[0][0]

############################################
app = Flask(__name__)

"localhost/"

@app.route("/")
def home():
    print("home request")
    return (
        f"<b>Welcome, surfer!</b> Looking for some good climate conditions?\
            Check out the following sections to find your perfect time!<br/> <br/>"
        f"<b>/api/v1.0/precipitation</b> >>>> Check out all the prcp records available <br/> <br/>"
        f"<b>/api/v1.0/stations</b> >>>> Stations list <br/> <br/>"
        f"<b>/api/v1.0/tobs</b> >>>> Check out all the temperature records available <br/> <br/>"
        f"#############################<br/>"
        f"Know the min, max and average temperature for any period from January 1st 2010\
             to August 18th 2017<br/>\
        <b>Note:</b> Use YYYY-MM-DD format<br/> <br/>"
        f"EXAMPLE 1: Using a starting date >>>> <b>/api/v1.0/2011-08-05</b> <br/> <br/>"
        f"EXAMPLE 2: Using a starting and ending date >>>> <b>/api/v1.0/2011-08-05/2013-04-15</b>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation_page():
    session = Session(engine)
    
    rain_log = session.query(temp_mea.date, temp_mea.prcp).\
        filter(temp_mea.station == most_active_station).\
        order_by(temp_mea.date).all()

    session.close()
    
    all_prcp = [{"station": most_active_station}]
    for date, prcp in rain_log:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")   
def station_page():
    session = Session(engine) 

    station_list = session.query(stations.station, stations.name).all()

    session.close()

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")   
def tobs_page():
    session = Session(engine) 

    last_date = session.query(temp_mea.date).order_by(temp_mea.date.desc()).first()
    one_year_ago = str(int(last_date[0][:4]) - 1)
    last_year_date = one_year_ago + last_date[0][4:]

    last_year_tobs = session.query(temp_mea.date, temp_mea.tobs).\
        filter(temp_mea.date >= last_year_date).\
        filter(temp_mea.station == most_active_station).\
        order_by(temp_mea.date).all()

    session.close()

    station_tobs = [{"Station": most_active_station}]
    for date, tobs in last_year_tobs:
        tob_list = []
        tob_list.append(date)
        tob_list.append(tobs)
        station_tobs.append(tob_list)

    return jsonify(station_tobs)

@app.route("/api/v1.0/<start_date>")  
def start_page(start_date):
    session = Session(engine) 
    
    start_temp = session.query(func.min(temp_mea.tobs), func.max(temp_mea.tobs),\
        func.avg(temp_mea.tobs)).\
        filter(temp_mea.date >= start_date).\
        filter(temp_mea.station == most_active_station)

    start_temp_sum = [f"The temperatures from {start_date} up to 2017-08-18 are..."]
    for res in start_temp:
        start_temp_sum.append(f"Min temp: {res[0]}")
        start_temp_sum.append(f"Max temp: {res[1]}")
        start_temp_sum.append(f"Ave temp: {res[2]}")
    
    session.close()

    return jsonify(start_temp_sum)

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_page(start_date, end_date):
    
    session = Session(engine)
    
    start_end_temp = session.query(func.min(temp_mea.tobs), func.max(temp_mea.tobs),\
        func.avg(temp_mea.tobs)).\
        filter(temp_mea.date >= start_date).\
        filter(temp_mea.date <= end_date).\
        filter(temp_mea.station == most_active_station)

    session.close()

    start_end_temp_sum = [f"The temperatures from {start_date} to {end_date} are..."]
    for res in start_end_temp:
        start_end_temp_sum.append(f"Min temp: {res[0]}")
        start_end_temp_sum.append(f"Max temp: {res[1]}")
        start_end_temp_sum.append(f"Ave temp: {res[2]}")
    
    return jsonify(start_end_temp_sum)



if __name__== "__main__":
    app.run(debug=True)