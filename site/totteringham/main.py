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
        afc_fix = db.session.query(Fixture).filter(Fixture.event_date>'08-05-2022', Fixture.league_id==39).filter(or_(Fixture.home=='42', Fixture.away=='42')).order_by(text("event_date desc")).all()
        spuds_fix = db.session.query(Fixture).filter(Fixture.event_date>'08-05-2022', Fixture.league_id==39).filter(or_(Fixture.home=='47', Fixture.away=='47')).order_by(text("event_date desc")).all()

        afc_future_fix, afc_past_fix = splitFixturesOnToday(afc_fix)
        spuds_future_fix, spuds_past_fix = splitFixturesOnToday(spuds_fix)

        afc_past_fix_complete = addFixtureWinner(afc_past_fix)
        spuds_past_fix_complete = addFixtureWinner(spuds_past_fix)

        afc_remaining_points = remainingPoints(afc_future_fix)
        spuds_remaining_points = remainingPoints(spuds_future_fix)
        # afc_past_fix = db.session.query(Fixture).filter(Fixture.event_date<datetime.datetime.now(), Fixture.event_date>'08-05-2022', Fixture.league_id==39).filter(or_(Fixture.home=='42', Fixture.away=='42')).order_by(text("event_date desc")).all()
        # afc_future_fix = db.session.query(Fixture).filter(Fixture.event_date>datetime.datetime.now(), Fixture.league_id==39).filter(or_(Fixture.home=='42', Fixture.away=='42')).order_by(text("event_date desc")).all()

        # spuds_past_fix = db.session.query(Fixture).filter(Fixture.event_date<datetime.datetime.now(), Fixture.event_date>'08-05-2022', Fixture.league_id==39).filter(or_(Fixture.home=='47', Fixture.away=='47')).order_by(text("event_date desc")).all()
        # spuds_future_fix = db.session.query(Fixture).filter(Fixture.event_date>datetime.datetime.now(), Fixture.league_id==39).filter(or_(Fixture.home=='47', Fixture.away=='47')).order_by(text("event_date desc")).all()

        return render_template('index.html', afc_past=[a.toJson() for a in afc_past_fix_complete], afc_future=[a.toJson() for a in afc_future_fix], 
            spuds_past=[a.toJson() for a in spuds_past_fix_complete], spuds_future=[a.toJson() for a in spuds_future_fix], 
            nlds=playedNLD(afc_fix),
            afc_points=afc_remaining_points, spuds_points=spuds_remaining_points)


def remainingPoints(fixtures):
    return (len(fixtures) * 3)


# split fixture lists on today's date
def splitFixturesOnToday(fixtures):
    future_fix = []
    past_fix = []

    for f in fixtures:
        if f.event_date < datetime.datetime.now():
            past_fix.append(f)
        else:
            future_fix.append(f)
    return (future_fix, past_fix)

# adds winner key to fixture dicts
def addFixtureWinner(fixtures):
    for f in fixtures:
        if f.status_short not in ['PST', 'CANC']:
            if int(f.goals_home) > int(f.goals_away):
                f.winner = f.home_team.name
            elif int(f.goals_home) < int(f.goals_away):
                f.winner = f.away_team.name
            else:
                f.winner = "draw"
    return fixtures

# how many NLDs played so far?
def playedNLD(fixtures):
    nlds = 0
    for f in fixtures:
        if f.status_short in "FT, AET, PEN":
            # if (f.home_team.name in "Arsenal, Tottenham" and f.away_team.name in "Arsenal, Tottenham"): # good
            # if f.home in [42, 47] and f.away in [42, 47]: # better
            if sorted([f.home, f.away]) == [42, 47]: # best :D
                nlds = nlds + 1
    return nlds
            
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
