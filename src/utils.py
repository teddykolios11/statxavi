import pandas as pd

def split_shot_end_location(location):
    x = location[0]
    y = location[1]
    z = location[2] if len(location) > 2 else None
    return pd.Series([x, y, z])

PCA_N_COMPONENTS = 10

top_league_comp_ids = {
 'La Liga': 11,
 'Ligue 1': 7,
 'Premier League': 2,
 'Serie A': 12,
 'UEFA Euro': 55,
 'FIFA World Cup': 43
}

season_ids = {
    '2015/2016': 27,
    '2018': 3,
    '2020': 43,
    '2022': 106,
    '2024': 282
}

POSITION_GROUPS = {
    # Goalkeeper
    "Goalkeeper": "Goalkeeper",

    # Defenders
    "Right Wing Back": "Fullback",
    "Right Back": "Fullback",
    "Right Center Back": "Center Back",
    "Center Back": "Center Back",
    "Left Center Back": "Center Back",
    "Left Back": "Fullback",
    "Left Wing Back": "Fullback",

    # Midfielders
    "Right Defensive Midfield": "Center Midfielder",
    "Center Defensive Midfield": "Center Midfielder",
    "Left Defensive Midfield": "Center Midfielder",
    "Right Center Midfield": "Center Midfielder",
    "Center Midfield": "Center Midfielder",
    "Left Center Midfield": "Center Midfielder",

    # Wingers / attacking midfielders
    "Right Wing": "Outside Midfielder",
    "Right Midfield": "Outside Midfielder",
    "Right Attacking Midfield": "Attacking Midfielder",
    "Center Attacking Midfield": "Attacking Midfielder",
    "Left Attacking Midfield": "Attacking Midfielder",
    "Left Midfield": "Outside Midfielder",
    "Left Wing": "Outside Midfielder",

    # Forwards
    "Right Center Forward": "Forward",
    "Center Forward": "Forward",
    "Left Center Forward": "Forward",
    "Secondary Striker": "Forward",
}

PCA_VOLUME_COLUMNS = (
    "goals",
    "xG",
    "shots",
    "xA",
    "shot_assists",
    "progressive_passes",
    "passes_completed",
    "dribbles_attempted",
    "dribbles_completed",
    "carries",
    "progressive_carries",
    "ball_recoveries_won",
    "interceptions_won",
    "duels",
    "tackles_won",
    "blocks",
    "clearances",
    "pressures",
    "fouls",
    "poss_won_final_third",
)

PCA_FEATURE_COLUMNS = (
    "goals_per90",
    "xG_per90",
    "shots_per90",
    "xA_per90",
    "shot_assists_per90",
    "progressive_passes_per90",
    "passes_completed_per90",
    "pass_completion_pct",
    "dribbles_attempted_per90",
    "dribbles_completed_per90",
    "carries_per90",
    "progressive_carries_per90",
    "ball_recoveries_won_per90",
    "interceptions_won_per90",
    "duels_per90",
    "tackles_won_per90",
    "blocks_per90",
    "clearances_per90",
    "pressures_per90",
    "fouls_per90",
    "poss_won_final_third_per90",
)

event_types = [
    "passes",
    "dribbles",
    "carries",
    "shots",
    "duels",
    "clearances",
    "blocks",
    "interceptions",
    "ball_recoveries",
    "pressures",
    "fouls",
    "player_minutes",
]

pass_columns = [
    # Identity
    "match_id",
    "id",
    "index",

    # Time
    "period",
    "minute",
    "second",

    # Player/team
    "player_id",
    "player",
    "team_id",
    "team",
    "position",

    # Spatial
    "location",
    "pass_end_location",

    # Basic pass properties
    "duration",
    "pass_length",
    "pass_angle",
    "pass_height",
    "pass_body_part",
    "pass_outcome",

    # Recipient
    "pass_recipient_id",
    "pass_recipient",

    # Chance creation
    "pass_shot_assist",
    "pass_goal_assist",
    "pass_assisted_shot_id",

    # Pass style
    "pass_cross",
    "pass_cut_back",
    "pass_through_ball",
    "pass_switch",
    "pass_type",
    "pass_technique",

    # Context
    "play_pattern",
    "under_pressure",
    "possession",
    "possession_team_id",

    # Relationships
    "related_events",
]

dribble_columns = [
    # Identity
    "match_id",
    "id",
    "index",

    # Time
    "period",
    "minute",
    "second",

    # Player / team
    "player_id",
    "player",
    "team_id",
    "team",
    "position",

    # Spatial
    "location",

    # Dribble attributes
    "dribble_outcome",
    "dribble_nutmeg",
    "dribble_overrun",

    # Context
    "under_pressure",
    "play_pattern",
    "possession",
    "possession_team_id",
]

carry_columns = [
    # Identity
    "match_id",
    "id",
    "index",

    # Time
    "period",
    "minute",
    "second",

    # Player / team
    "player_id",
    "player",
    "team_id",
    "team",
    "position",

    # Spatial
    "location",
    "carry_end_location",

    # Carry properties
    "duration",

    # Context
    "under_pressure",
    "play_pattern",
    "possession",
    "possession_team_id",
]

shot_columns = [
    # Identity
    "match_id",
    "id",
    "index",

    # Time
    "period",
    "minute",
    "second",

    # Player / team
    "player_id",
    "player",
    "team_id",
    "team",
    "position",

    # Spatial
    "location",
    "shot_end_location",

    # Core shot attributes
    "shot_statsbomb_xg",
    "shot_outcome",
    "shot_body_part",
    "shot_type",
    "shot_technique",

    # Shot context
    "shot_first_time",
    "shot_one_on_one",
    "shot_open_goal",
    "under_pressure",

    # Chance-creation linkage
    "shot_key_pass_id",

    # Match context
    "play_pattern",
    "possession",
    "possession_team_id",

    # Rich shot context
    "shot_freeze_frame",
]

interception_columns = [
    # Identity
    "match_id",
    "id",
    "index",

    # Time
    "period",
    "minute",
    "second",

    # Player / team
    "player_id",
    "player",
    "team_id",
    "team",
    "position",

    # Spatial
    "location",

    # Interception attributes
    "interception_outcome",

    # Context
    "counterpress",
    "under_pressure",
    "play_pattern",
    "possession",
    "possession_team_id",
]

pressure_columns = [
    # Identity
    "match_id",
    "id",
    "index",

    # Time
    "period",
    "minute",
    "second",

    # Player / team
    "player_id",
    "player",
    "team_id",
    "team",
    "position",

    # Spatial
    "location",

    # Pressure attributes
    "duration",
    "counterpress",

    # Context
    "play_pattern",
    "possession",
    "possession_team_id",

    # Event relationships
    "related_events",
]

duel_columns = [
    # Identity
    "match_id",
    "id",
    "index",

    # Time
    "period",
    "minute",
    "second",

    # Player / team
    "player_id",
    "player",
    "team_id",
    "team",
    "position",

    # Spatial
    "location",

    # Duel attributes
    "duel_type",
    "duel_outcome",

    # Context
    "counterpress",
    "play_pattern",
    "possession",
    "possession_team_id",

    # Relationships
    "related_events",
]

clearance_columns = [
    # Identity
    "match_id",
    "id",
    "index",

    # Time
    "period",
    "minute",
    "second",

    # Player / team
    "player_id",
    "player",
    "team_id",
    "team",
    "position",

    # Spatial
    "location",

    # Clearance attributes
    "clearance_body_part",
    "clearance_aerial_won",

    # Context
    "under_pressure",
    "play_pattern",
    "possession",
    "possession_team_id",

    # Relationships
    "related_events",
]

block_columns = [
    # Identity
    "match_id",
    "id",
    "index",

    # Time
    "period",
    "minute",
    "second",

    # Player / team
    "player_id",
    "player",
    "team_id",
    "team",
    "position",

    # Spatial
    "location",

    # Block attributes
    "block_offensive",
    "block_deflection",
    "block_save_block",

    # Context
    "counterpress",
    "play_pattern",
    "possession",
    "possession_team_id",

    # Relationships
    "related_events",
]

ball_recovery_columns = [
    # Identity
    "match_id",
    "id",
    "index",

    # Time
    "period",
    "minute",
    "second",

    # Player / team
    "player_id",
    "player",
    "team_id",
    "team",
    "position",

    # Spatial
    "location",

    # Recovery attributes
    "ball_recovery_offensive",
    "ball_recovery_recovery_failure",

    # Context
    "under_pressure",
    "play_pattern",
    "possession",
    "possession_team_id",

    # Relationships
    "related_events",
]

foul_columns = [
    # Identity
    "match_id",
    "id",
    "index",

    # Time
    "period",
    "minute",
    "second",

    # Player / team
    "player_id",
    "player",
    "team_id",
    "team",
    "position",

    # Spatial
    "location",

    # Foul attributes
    "foul_committed_card",
    "foul_committed_type",
    "foul_committed_advantage",
    "foul_committed_offensive",
    "foul_committed_penalty",

    # Context
    "counterpress",
    "play_pattern",
    "possession",
    "possession_team_id",

    # Relationships
    "related_events",
]