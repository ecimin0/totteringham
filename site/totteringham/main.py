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
import math
from typing import Optional

bp = Blueprint('main', __name__)
# bp.wsgi_app = ProfilerMiddleware(bp)
# print(bp.wsgi_app)

@bp.route('/health', methods=['GET'])
def health():
    return "OK", 200


@bp.route('/', methods=['GET'])
def index():
    if request.method == "GET":
        fix = db.session.query(Fixture).filter(Fixture.event_date>'08-05-2022', Fixture.league_id==39).filter(or_(Fixture.home=='42', Fixture.away=='42', Fixture.home=='47', Fixture.away=='47')).order_by(text("event_date desc")).all()

        afc_fix, spuds_fix = splitFixturesByTeam(fix)

        afc_future_fix, afc_past_fix = splitFixturesOnToday(afc_fix)
        spuds_future_fix, spuds_past_fix = splitFixturesOnToday(spuds_fix)

        afc_past_fix_complete = addFixtureWinner(afc_past_fix)
        spuds_past_fix_complete = addFixtureWinner(spuds_past_fix)

        def currentPoints(fixtures):
            points = 0
            for f in fixtures:
                if f.winner == "Arsenal" or f.winner == "Tottenham":
                    points += 3
                elif f.winner == "draw":
                    points += 1
                else:
                    pass
            return points

        afc_points = currentPoints(afc_past_fix_complete)
        spuds_points = currentPoints(spuds_past_fix_complete)

        afc_remaining_points = remainingPoints(afc_future_fix)
        spuds_remaining_points = remainingPoints(spuds_future_fix)

        # dates
        afc_max_points = afc_points + afc_remaining_points
        num_afc_matches_remaining = len(afc_future_fix)
        spuds_max_points = spuds_points + spuds_remaining_points
        num_spuds_matches_remaining = len(spuds_future_fix)
        # print(f"afc pts: {afc_points}, afc max: {afc_max_points}, afc remain: {num_afc_matches_remaining} | tot pts: {spuds_points}, tot max: {spuds_max_points}, tot remain: {num_spuds_matches_remaining}")
        # print(f"weeks: {(spuds_max_points - afc_points) / 3}, rounded: {math.ceil((spuds_max_points - afc_points) / 3)}")
        # print(afc_future_fix[math.ceil(num_afc_matches_remaining - (spuds_max_points - afc_points) / 3)].event_date)


        test_earliest()
        # test_latest()
        print(latest(50,36,18))
        # print(earliest(50,36,18))

        return render_template('index.html',
            afc_past=[a.toJson() for a in afc_past_fix_complete],
            afc_future=[a.toJson() for a in afc_future_fix],
            spuds_past=[a.toJson() for a in spuds_past_fix_complete],
            spuds_future=[a.toJson() for a in spuds_future_fix],
            nlds=playedNLD(afc_fix),
            afc_points=afc_points,
            spuds_points=spuds_points,
            afc_remaining_points=afc_remaining_points,
            spuds_remaining_points=spuds_remaining_points)


def earliest(main, opponent, remaining) -> Optional[int]:
    for i in range(remaining):
        print(f"Iteration: {i} Main: {main} Opponent: {opponent} Max Points Still Attainable: {(remaining - i) * 3} Perfect: {remaining * 3}")
        if isTotts(main, opponent, remaining - i):
            return i
        main += 3
        opponent += 0
    return None

def averagest(main, opponent, remaining) -> Optional[int]:
    ...

def latest(main, opponent, remaining) -> Optional[int]:
    for i in range(remaining):
        print(f"Iteration: {i} Main: {main} Opponent: {opponent} Max Points Still Attainable: {(remaining - i) * 3} Perfect: {remaining * 3}")
        if isTottsLatest(main, opponent):
            return i
        main += 0
        opponent += 3
    return None

def isTotts(main, opponent, remaining):
    return main - opponent > remaining * 3

def isTottsLatest(main, opponent):
    return main > opponent

def test_earliest():
    assert(earliest(50, 36, 18) == 7)
    print("")
    # assert(earliest(50, 36, 1) == 0)
    # print("")
    # assert(earliest(0, 0, 3) == 2)
    # print("")
    # assert(earliest(0, 0, 18) == 10)

def test_latest():
    assert(latest(50, 36, 18) == 7)
    print("")
    # assert(earliest(50, 36, 1) == 0)
    # print("")
    # assert(earliest(0, 0, 3) == 2)
    # print("")
    # assert(earliest(0, 0, 18) == 10)


# def possibleDates(points, remain_points, future_matches):
#     highest_possible_points = points + remain_points
#     num_matches_remaining = len(future_matches)


def splitFixturesByTeam(fixtures):
    afc = []
    spuds = []
    for f in fixtures:
        if f.home == 42 or f.away == 42:
            afc.append(f)
        else:
            spuds.append(f)
    return (afc, spuds)

def remainingPoints(fixtures):
    return (len(fixtures) * 3)


# split fixture lists on today's date
def splitFixturesOnToday(fixtures):
    future_fix = []
    past_fix = []

    for f in fixtures:
        if f.event_date < datetime.datetime.utcnow():
            past_fix.append(f)
        else:
            future_fix.append(f)
    return (future_fix, past_fix)

# adds winner key to fixture dicts
def addFixtureWinner(fixtures):
    for f in fixtures:
        if f.status_short not in ['PST', 'CANC']:
            # print(f"{f.status_short} {f.goals_home} {f.goals_away}")
            if f.goals_home > f.goals_away:
                f.winner = f.home_team.name
            elif f.goals_home < f.goals_away:
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
