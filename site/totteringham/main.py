from email.mime import image
import logging
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort
from . import db
from totteringham.models import *
from sqlalchemy.sql import select, or_
import datetime
import re
import json

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def index():
    if request.method == "GET":
        afc_past_fix = db.session.query(Fixture).filter(Fixture.event_date<datetime.datetime.now(), Fixture.event_date>'08-05-2022', Fixture.league_id==39).filter(or_(Fixture.home=='42', Fixture.away=='42')).order_by(text("event_date desc")).all()
        afc_future_fix = db.session.query(Fixture).filter(Fixture.event_date>datetime.datetime.now(), Fixture.league_id==39).filter(or_(Fixture.home=='42', Fixture.away=='42')).order_by(text("event_date desc")).all()

        spuds_past_fix = db.session.query(Fixture).filter(Fixture.event_date<datetime.datetime.now(), Fixture.event_date>'08-05-2022', Fixture.league_id==39).filter(or_(Fixture.home=='47', Fixture.away=='47')).order_by(text("event_date desc")).all()
        spuds_future_fix = db.session.query(Fixture).filter(Fixture.event_date>datetime.datetime.now(), Fixture.league_id==39).filter(or_(Fixture.home=='47', Fixture.away=='47')).order_by(text("event_date desc")).all()


        


        return render_template('index.html', afc_past=json.dumps(afc_past_fix), afc_future=afc_future_fix, spuds_past=spuds_past_fix, spuds_future=spuds_future_fix)


# @bp.route('/api/fixtures', methods=['GET', 'POST'])
# def api_fixtures():
#     if request.method == "POST":
#         post_data = request.json
#         # print(post_data)
#         main_team = post_data.get("team", 0)
#     else:
#         get_data = request.args.get("team", 0)
#         main_team = get_data
#         # print(get_data)

#     main_fixtures_query = db.session.query(Fixture).filter(Fixture.event_date<datetime.datetime.now(), Fixture.event_date>'08-05-2022').filter(or_(Fixture.home==main_team, Fixture.away==main_team)).order_by(text("event_date asc")).all()
#     return jsonify([{"home": f.home_team.name, "away": f.away_team.name, "date": str(f.event_date)[:10]} for f in main_fixtures_query])
