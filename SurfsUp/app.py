# Import the dependencies.
import numpy as np

import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify 



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station


# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################

app = Flask(__name__)



#################################################
# Flask Routes
#################################################

########################################
#STATIC ROUTES
#########################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"

    )


#Convert the query results from your precipitation analysis 
#(i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.

#Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
        session = Session(engine)

        #getting last one year(12 months)
        most_rescent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
        latest_date = dt.datetime.strptime(most_rescent_date[0], '%Y-%m-%d')
        last_12_months = latest_date - dt.timedelta(days=365)
        
        results = session.query(measurement.date,measurement.prcp).\
            filter(measurement.date >= last_12_months).all()
        # dictionory  to hold date as key and precipitation as value
        precip = {date: prcp for date, prcp in results}
        session.close()
        # return JSON representation of your dictionary.
        return jsonify(precip)


#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
        session = Session(engine)

        results = session.query(station.station).all()
        session.close()

        all_station =list(np.ravel(results))
        return jsonify(all_station)

@app.route("/api/v1.0/tobs")
def tobs():
        session = Session(engine)

        active_station_count = session.query(measurement.station,func.count(measurement.station)).\
        order_by(func.count(measurement.station).desc()).\
        group_by(measurement.station).all()
        most_active_station = active_station_count[0][0]
        most_rescent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
        latest_date = dt.datetime.strptime(most_rescent_date[0], '%Y-%m-%d')
        last_12_months = latest_date - dt.timedelta(days=365)
        
        results = session.query(measurement.date,measurement.tobs).\
            filter(measurement.date.between (last_12_months,latest_date) ).\
            filter(measurement.station==most_active_station). all()
        tobs =list(np.ravel(results))
        session.close()
        return jsonify(tobs)

################################
#API Dynamic Route
################################
@app.route("/api/v1.0/<start>") 
@app.route("/api/v1.0/<start>/<end>") 
def start(start,end = None):
    session = Session(engine)
    if  end == None:
        enddate = session.query(func.max(measurement.date)).\
                    scalar()
    else:
        enddate = str(end)
    startdate = str(start)
    results = session.query(func.min(measurement.tobs).label('min_temp'),
                            func.avg(measurement.tobs).label('avg_temp'),
                            func.max(measurement.tobs).label('max_temp')).\
                filter(measurement.date.between(startdate,enddate)).\
                first()
    session.close()
    datapoints = list(np.ravel(results))
    return jsonify(datapoints)


if __name__ == "__main__":
    app.run(debug=True)


