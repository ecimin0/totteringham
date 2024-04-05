``from __future__ import annotations
``import datetime
import json
import logging
import math
import re
from email.mime import image
from typing import Optional, Tuple

from flask import (Blueprint, flash, g, jsonify, redirect, render_template,
                   request, url_for, Response)
from sqlalchemy.sql import or_, select
from totteringham.models import *
from typeguard import typechecked
from werkzeug.exceptions import abort

from . import db

bp = Blueprint('main', __name__)
# bp.wsgi_app = ProfilerMiddleware(bp)
# print(bp.wsgi_app)

@typechecked
@bp.route('/health', methods=['GET'])
def health() -> Tuple[str, int]:
    return "OK", 200

# @typechecked
@bp.route('/', methods=['GET'])
def index():
    if request.method == "GET":
        fix = db.session.query(Fixture).filter(Fixture.event_date>'08-11-2023', Fixture.league_id==39).filter(or_(Fixture.home=='42', Fixture.away=='42', Fixture.home=='47', Fixture.away=='47')).order_by(text("event_date desc")).all()

        afc_fix, spuds_fix = splitFixturesByTeam(fix)

        afc_future_fix, afc_past_fix = splitFixturesOnToday(afc_fix)
        spuds_future_fix, spuds_past_fix = splitFixturesOnToday(spuds_fix)

        afc_past_fix_complete = addFixtureWinner(afc_past_fix)
        spuds_past_fix_complete = addFixtureWinner(spuds_past_fix)

        @typechecked
        def currentPoints(fixtures: list) -> int:
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

        # # dates
        # afc_max_points = afc_points + afc_remaining_points
        # num_afc_matches_remaining = len(afc_future_fix)
        # spuds_max_points = spuds_points + spuds_remaining_points
        # num_spuds_matches_remaining = len(spuds_future_fix)

        print("------")
        earliest(50, 36, afc_future_fix)
        print("------")
        predicted(50, 36, afc_future_fix)
        print("------")
        latestAllWins(50, 36, afc_future_fix)
        print("------")
        afcStopWinning(50, 36, afc_future_fix)

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


# 7 (afc win all, tot lose all)
@typechecked
def earliest(main: int, opponent: int, fixtures: list) -> Optional[int]:
    remaining = len(fixtures)
    for i in range(remaining):
        print(f"Iteration: {i} Main: {main} Opponent: {opponent} Max Points Still Attainable: {(remaining - i) * 3} Perfect: {remaining * 3}")
        if isTotts(main, opponent, remaining - i):
            return i
        main += 3
        opponent += 0
    return None


# best effort prediction using accurate ppg
@typechecked
def predicted(main: int, opponent: int, fixtures: list) -> Optional[float]:
    remaining = len(fixtures)
    for i in range(remaining):
        main_ppg = 0.00
        opponent_ppg = 0.00
        print(f"Iteration: {i} Main: {main} Opponent: {opponent} Max Points Still Attainable: {(remaining - i) * 3} Perfect: {remaining * 3}")
        if isTotts(main_ppg, opponent_ppg, remaining - i):
            return i
        main_ppg += (main / (38 - remaining))
        opponent_ppg += (opponent / (38 - remaining))
    return None


# 14 (both win all from x point forward)
# does not account for nld x2
@typechecked
def latestAllWins(main: int, opponent: int, fixtures: list) -> Optional[int]:
    remaining = len(fixtures)
    for i in range(remaining):
        print(f"Iteration: {i} Main: {main} Opponent: {opponent} Max Points Still Attainable: {(remaining - i) * 3} Perfect: {remaining * 3}")
        if isTotts(main, opponent, remaining - i):
            return i
        main += 3
        opponent += 3
    return None


# None (no st totts) (afc lose all, tot win all)
@typechecked
def afcStopWinning(main: int, opponent: int, fixtures: list) -> Optional[int]:
    remaining = len(fixtures)
    for i in range(remaining):
        print(f"Iteration: {i} Main: {main} Opponent: {opponent} Max Points Still Attainable: {(remaining - i) * 3} Perfect: {remaining * 3}")
        if isTotts(main, opponent, remaining - i):
            return i
        main += 0
        opponent += 3
    return None

# [Latest Actual] = last game
# [Assuming we don't suck and they don't suck] = 14 (everybody wins everything no crossplay)
# [assuming we don't suck, assuming they suck] = 7 (we win everything, they lose everything)
# [assuming we suck, assuming they don't suck] = None

@typechecked
def isTotts(main: int | float, opponent: int | float, remaining: int) -> Optional[int]:
    return main - opponent > remaining * 3


# print("------")
# earliest(50, 36, 18)
# print("------")
# predicted(50, 36, 18)
# print("------")
# latestAllWins(50, 36, 18)
# print("------")
# afcStopWinning(50, 36, 18)


# def possibleDates(points, remain_points, future_matches):
#     highest_possible_points = points + remain_points
#     num_matches_remaining = len(future_matches)


@typechecked
def splitFixturesByTeam(fixtures: list) -> Tuple[list, list]:
    afc = []
    spuds = []
    for f in fixtures:
        if f.home == 42 or f.away == 42:
            afc.append(f)
        if f.home == 47 or f.away == 47:
            spuds.append(f)
    return (afc, spuds)


@typechecked
def remainingPoints(fixtures: list) -> int:
    return (len(fixtures) * 3)


# split fixture lists on today's date
@typechecked
def splitFixturesOnToday(fixtures: list) -> Tuple[list, list]:
    future_fix = []
    past_fix = []
    for f in fixtures:
        if f.event_date < datetime.datetime.utcnow():
            past_fix.append(f)
        else:
            future_fix.append(f)
    return (future_fix, past_fix)


# adds winner key to fixture dicts
@typechecked
def addFixtureWinner(fixtures: list) -> list:
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
@typechecked
def playedNLD(fixtures: list) -> int:
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
