from sqlalchemy import ARRAY, BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Table, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Country(Base):
    __tablename__ = 'countries'
    __table_args__ = {'schema': 'predictionsbot'}

    country = Column(String, primary_key=True, unique=True)
    code = Column(String)
    flag = Column(String)


t_predictions_2021_2022 = Table(
    'predictions_2021-2022', metadata,
    Column('prediction_id', String),
    Column('user_id', BigInteger),
    Column('prediction_string', String),
    Column('fixture_id', Integer),
    Column('timestamp', DateTime),
    Column('prediction_score', Integer),
    Column('home_goals', Integer),
    Column('away_goals', Integer),
    Column('scorers', JSON),
    Column('guild_id', BigInteger),
    schema='predictionsbot'
)


class Season(Base):
    __tablename__ = 'seasons'
    __table_args__ = {'schema': 'predictionsbot'}

    season = Column(String, primary_key=True)


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'predictionsbot'}

    user_id = Column(BigInteger, primary_key=True, unique=True)
    tz = Column(String, server_default=text("'UTC'::character varying"))
    allow_notifications = Column(Boolean, server_default=text("false"))


class League(Base):
    __tablename__ = 'leagues'
    __table_args__ = {'schema': 'predictionsbot'}

    league_id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    season = Column(ForeignKey('predictionsbot.seasons.season'))
    logo = Column(String)
    country = Column(ForeignKey('predictionsbot.countries.country'))

    country1 = relationship('Country')
    season1 = relationship('Season')


class Team(Base):
    __tablename__ = 'teams'
    __table_args__ = {'schema': 'predictionsbot'}

    team_id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    logo = Column(String)
    country = Column(ForeignKey('predictionsbot.countries.country'))
    nicknames = Column(ARRAY(String(length=50)))

    country1 = relationship('Country')


class Fixture(Base):
    __tablename__ = 'fixtures'
    __table_args__ = {'schema': 'predictionsbot'}

    home = Column(ForeignKey('predictionsbot.teams.team_id'))
    away = Column(ForeignKey('predictionsbot.teams.team_id'))
    fixture_id = Column(Integer, primary_key=True)
    league_id = Column(ForeignKey('predictionsbot.leagues.league_id'))
    event_date = Column(DateTime)
    goals_home = Column(Integer)
    goals_away = Column(Integer)
    new_date = Column(DateTime)
    scorable = Column(Boolean, server_default=text("false"))
    status_short = Column(String)
    notifications_sent = Column(Boolean, server_default=text("false"))
    season = Column(ForeignKey('predictionsbot.seasons.season'))

    # team = relationship('Team', primaryjoin='Fixture.away == Team.team_id', back_populates="away_fixtures") #adds away_fixtures callable to Team class (Team.away_fixtures becomes possible)
    # team1 = relationship('Team', primaryjoin='Fixture.home == Team.team_id', back_populates="home_fixtures")
    
    away_team = relationship('Team', primaryjoin='Fixture.away == Team.team_id')
    home_team = relationship('Team', primaryjoin='Fixture.home == Team.team_id')
    league = relationship('League')
    season1 = relationship('Season')


class Guild(Base):
    __tablename__ = 'guilds'
    __table_args__ = {'schema': 'predictionsbot'}

    guild_id = Column(BigInteger, primary_key=True)
    main_team = Column(ForeignKey('predictionsbot.teams.team_id'), nullable=False)

    team = relationship('Team')


class Player(Base):
    __tablename__ = 'players'
    __table_args__ = {'schema': 'predictionsbot'}

    player_id = Column(Integer, primary_key=True, unique=True)
    season = Column(ForeignKey('predictionsbot.seasons.season'))
    team_id = Column(ForeignKey('predictionsbot.teams.team_id'))
    player_name = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    nicknames = Column(ARRAY(String(length=50)))
    sidelined = Column(Boolean, server_default=text("false"))
    sidelined_start = Column(DateTime)
    sidelined_end = Column(DateTime)
    sidelined_reason = Column(String)
    active = Column(Boolean, server_default=text("true"))

    season1 = relationship('Season')
    team = relationship('Team')


class Prediction(Base):
    __tablename__ = 'predictions'
    __table_args__ = {'schema': 'predictionsbot'}

    prediction_id = Column(String, primary_key=True, unique=True)
    user_id = Column(ForeignKey('predictionsbot.users.user_id'))
    prediction_string = Column(String)
    fixture_id = Column(ForeignKey('predictionsbot.fixtures.fixture_id'))
    timestamp = Column(DateTime, server_default=text("now()"))
    prediction_score = Column(Integer)
    home_goals = Column(Integer)
    away_goals = Column(Integer)
    scorers = Column(JSON)
    guild_id = Column(ForeignKey('predictionsbot.guilds.guild_id'), nullable=False, server_default=text("0"))

    fixture = relationship('Fixture')
    guild = relationship('Guild')
    user = relationship('User')
