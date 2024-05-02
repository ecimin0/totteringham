from __future__ import annotations
import datetime
import json
import logging
import math
import re
from email.mime import image
from typing import Optional, Tuple

from flask import (
    Blueprint,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
    Response,
)
from sqlalchemy.sql import or_, select
from totteringham.models import *
from typeguard import typechecked
from werkzeug.exceptions import abort

from . import db

bp = Blueprint("main", __name__)
# bp.wsgi_app = ProfilerMiddleware(bp)
# print(bp.wsgi_app)


@typechecked
@bp.route("/health", methods=["GET"])
def health() -> Tuple[str, int]:
    return "OK", 200


# @typechecked
@bp.route("/", methods=["GET"])
def index():
    if request.method == "GET":
        fix = (
            db.session.query(Fixture)
            .filter(Fixture.event_date > "08-11-2023", Fixture.league_id == 39)
            .filter(
                or_(
                    Fixture.home == "42",
                    Fixture.away == "42",
                    Fixture.home == "47",
                    Fixture.away == "47",
                )
            )
            .order_by(text("event_date desc"))
            .all()
        )

        fix_rev = list(reversed(fix))

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

        afc_ppg = getPPG(afc_points, afc_future_fix)
        spuds_ppg = getPPG(spuds_points, spuds_future_fix)

        totts_date = whenIsStTotts(fix_rev)

        if datetime.datetime.now() > totts_date:
            is_totts: bool = True
        else:
            is_totts: bool = False

        # # dates
        # afc_max_points = afc_points + afc_remaining_points
        # num_afc_matches_remaining = len(afc_future_fix)
        # spuds_max_points = spuds_points + spuds_remaining_points
        # num_spuds_matches_remaining = len(spuds_future_fix)

        # is_totts = isTotts(afc_points, spuds_points, len(afc_future_fix))

        # earliest_date = earliestDate(afc_points, spuds_points, afc_future_fix, afc_past_fix, spuds_future_fix, spuds_past_fix)
        # earliest_date_fmt = earliest_date.strftime("%Y-%m-%d")
        # earliest_date_fmt = earliest_date
        # predicted_date = predictedDate(afc_points, spuds_points, afc_future_fix)
        # print(f"predicted {predicted_date}\n")
        # latest_date = latestAllWinsDate(afc_points, spuds_points, afc_future_fix)
        # print(f"latestAllWins {latest_date}\n")
        # afc_stop_winning_date = afcStopWinningDate(afc_points, spuds_points, afc_future_fix)
        # print(f"afcStopWinning {afc_stop_winning_date}\n")

        # for i,fix in enumerate(spuds_future_fix):
        #     print(i,fix.event_date)

        return render_template(
            "index.html",
            afc_past=[a.toJson() for a in afc_past_fix_complete],
            afc_future=[a.toJson() for a in afc_future_fix],
            spuds_past=[a.toJson() for a in spuds_past_fix_complete],
            spuds_future=[a.toJson() for a in spuds_future_fix],
            nlds=playedNLD(afc_fix),
            afc_points=afc_points,
            spuds_points=spuds_points,
            afc_remaining_points=afc_remaining_points,
            spuds_remaining_points=spuds_remaining_points,
            afc_ppg=afc_ppg,
            spuds_ppg=spuds_ppg,
            # earliest_date=earliest_date_fmt,
            # predicted_date=predicted_date,
            # latest_date=latest_date,
            # afc_stop_winning_date=afc_stop_winning_date,
            is_totts=is_totts,
        )


@typechecked
def getPPG(points: int, fixtures: list) -> Optional[int | float]:
    remaining = len(fixtures)
    num_played_matches = 38 - remaining
    ppg = points / num_played_matches
    return ppg


# @typechecked
# def isTotts(main: int | float, opponent: int | float, remaining: int) -> Optional[int]:
#     return main - opponent > remaining * 3

@typechecked
def whenIsStTotts(combined_all_fixtures: list) -> Optional[datetime.datetime]:
    afc_points: int = 0
    spuds_points: int = 0
    afc_fix_num: int = 0
    spuds_fix_num: int = 0

    for fixture in combined_all_fixtures:
        home: str = ""
        away: str = ""
        gh: int = 0
        ga: int = 0
        winner: str = ""

        if fixture.status_short != "NS":
            if fixture.home == 42 and fixture.away == 47:
                home = "arsenal"
                away = "spuds"
                afc_fix_num += 1
                spuds_fix_num += 1
            elif fixture.home == 47 and fixture.away == 42:
                home = "spuds"
                away = "arsenal"
                afc_fix_num += 1
                spuds_fix_num += 1
            elif fixture.home == 42:
                home = "arsenal"
                away = "other"
                afc_fix_num += 1
            elif fixture.away == 42:
                home = "other"
                away = "arsenal"
                afc_fix_num += 1
            elif fixture.home == 47:
                home = "spuds"
                away = "other"
                spuds_fix_num += 1
            elif fixture.away == 47:
                home = "other"
                away = "spuds"
                spuds_fix_num += 1

            gh = int(fixture.goals_home)
            ga = int(fixture.goals_away)

            if gh > ga:
                winner = home
            elif gh < ga:
                winner = away
            elif gh == ga:
                winner = "draw"

            if winner == "arsenal":
                afc_points += 3
            if winner == "spuds":
                spuds_points += 3
            if winner == "draw":
                if fixture.home == 42 or fixture.away == 42:
                    afc_points += 1
                if fixture.home == 47 or fixture.away == 47:
                    spuds_points += 1

            # print(f"afc fix num: {afc_fix_num}, afc pts: {afc_points}, rem. fix: {(38 - afc_fix_num)}, fix date: {fixture.event_date}, home: {fixture.home}, away: {fixture.away}")
            # print(f"spuds fix num: {spuds_fix_num}, spuds pts: {spuds_points}, rem. fix: {(38 - spuds_fix_num)}, fix date: {fixture.event_date}, home: {fixture.home}, away: {fixture.away}")

            # want min() here because we want the greatest amount *left* after subtracting from 38
            totts_day: bool = afc_points - spuds_points > ((38 - min(afc_fix_num, spuds_fix_num)) * 3)
            # print(totts_day)
            # print("")
            if totts_day:
                return fixture.event_date
                # print("skip")
        # else:
        #     print(fixture.event_date)

    return None



# @typechecked
# # def earliestDate(afc_points: int, spuds_points: int, afc_fixtures: list, spuds_fixtures: list) -> Optional[int]:
# # def earliestDate(afc_points: int, spuds_points: int, afc_future_fixtures: list, afc_past_fixtures: list, spuds_future_fixtures: list, spuds_past_fixtures: list,) -> Optional[datetime.datetime]:
# def earliestDate(afc_points: int, spuds_points: int, afc_future_fixtures: list, afc_past_fixtures: list, spuds_future_fixtures: list, spuds_past_fixtures: list,) -> Optional[int]:
#     last_played_afc_fix = afc_past_fixtures[0]
#     last_played_spuds_fix = spuds_past_fixtures[0]

#     # these get reversed because the orignal lists are sorted where 0 is the "current" fixture, and we need the last element instead
#     afc_fixtures = list(reversed(afc_future_fixtures))
#     # print([f.event_date for f in afc_fixtures])
#     spuds_fixtures = list(reversed(spuds_future_fixtures))

#     # note to self. list.insert() is an in-place operation
#     afc_fixtures.insert(0, last_played_afc_fix)
#     spuds_fixtures.insert(0, last_played_spuds_fix)

#     afc_remaining = len(afc_fixtures)
#     spuds_remaining = len(spuds_fixtures)
#     remaining = max(afc_remaining, spuds_remaining)

#     for i in range(remaining):
#         afc_points += 3 # possible bug, will overflow past the actual possible number of points right now since remaining = 6 but arsenal only have 4 left
#         spuds_points += 0
#         print(f"Iteration: {i} Main: {afc_points} Opponent: {spuds_points} Max Points Still Attainable: {(remaining - i) * 3} Perfect: {remaining * 3}")
#         if isTotts(afc_points, spuds_points, remaining - i):
#             return i
#             # return afc_fixtures[i].event_date
#     return None





# @typechecked
# def predictedDate(main: int, opponent: int, fixtures: list) -> Optional[datetime.datetime]:
#     remaining = len(fixtures)
#     main_ppg = getPPG(main, fixtures)
#     opponent_ppg = getPPG(opponent, fixtures)
#     for i in range(remaining):
#         if i == 0:
#             print(f"Iteration: {i} Main: {main} Opponent: {opponent} Max Points Still Attainable: {(remaining - i) * 3} Perfect: {remaining * 3}")
#         else:
#             print(f"Iteration: {i} Main: {main_ppg+main} Opponent: {opponent_ppg+opponent} Max Points Still Attainable: {(remaining - i) * 3} Perfect: {remaining * 3}")
#         if isTotts(main_ppg + main, opponent_ppg + opponent, remaining - i):
#             # return i
#             # return fixtures[remaining - i].event_date
#             return datetime.datetime.now()
#         main_ppg += main / (38 - remaining)
#         opponent_ppg += opponent / (38 - remaining)
#     return None


# # does not account for nld x2
# @typechecked
# def latestAllWinsDate(main: int, opponent: int, fixtures: list) -> Optional[datetime.datetime]:
#     remaining = len(fixtures)
#     for i in range(remaining):
#         print(f"Iteration: {i} Main: {main} Opponent: {opponent} Max Points Still Attainable: {(remaining - i) * 3} Perfect: {remaining * 3}")
#         if isTotts(main, opponent, remaining - i):
#             # return i
#             # return fixtures[remaining - i].event_date
#             return datetime.datetime.now()
#         main += 3
#         opponent += 3
#     return None


# # None (no st totts) (afc lose all, tot win all)
# @typechecked
# def afcStopWinningDate(main: int, opponent: int, fixtures: list) -> Optional[datetime.datetime]:
#     remaining = len(fixtures)
#     for i in range(remaining):
#         print(f"Iteration: {i} Main: {main} Opponent: {opponent} Max Points Still Attainable: {(remaining - i) * 3} Perfect: {remaining * 3}")
#         if isTotts(main, opponent, remaining - i):
#             # return i
#             # return fixtures[remaining - i].event_date
#             return datetime.datetime.now()
#         main += 0
#         opponent += 3
#     return None


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
    return len(fixtures) * 3


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
        if f.status_short not in ["PST", "CANC"]:
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
            if sorted([f.home, f.away]) == [42, 47]:  # best :D
                nlds = nlds + 1
    return nlds
