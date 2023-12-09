from mobfot import MobFot
import csv
import json

def add_event(events):
    new_event = {
        "goal": 0,
        "assist": 0,
        "subbedOutTime": None,
        "subbedInTime": None,
        "yellowCard": 0,
        "redCard": 0
    }
    if 'g' in events:
        new_event['goal'] = events['g']
    if 'as' in events:
        new_event['assist'] = events['as']
    if 'sub' in events:
        new_event['subbedOutTime'] = events['sub'].get('subbedOut', None)
        new_event['subbedInTime'] = events['sub'].get('subbedIn', None)
    if 'yc' in events:
        new_event['yellowCard'] = events['yc']
    if 'rc' in events:
        new_event['redCard'] = events['rc']
    return new_event

def extract_percentage(value):
    if isinstance(value, str):
        start = value.find('(')
        end = value.find('%')
        if start != -1 and end != -1 and start < end:
            return int(value[start+1:end].strip())
    return value
def add_stats(stats):
    new_stats = {
        'total_shots':0,
        'accurate_passes':'0',
        'chances_created':0,
        'expected_goals(xG)':0,
        'expected_goals_on_target(xGOT)':0,
        'expected_assists(xA)':0,
        'xG+xA':0,
        'shot_accuracy':'0',
        'blocked_shots':0,
        'touches':0,
        'touches_in_opposition_box':0,
        'passes_into_final_third':0,
        'accurate_long_balls':'0',
        'dispossessed':0,
        'xG_Non_penalty':0,
        'tackles_won':'0',
        'clearances':0,
        'headed_clearance':0,
        'defensive_actions':0,
        'recoveries':0,
        'dribbled_past':0,
        'duels_won':0,
        'duels_lost':0,
        'ground_duels_won':'0',
        'aerial_duels_won':'0',
        'was_fouled':0,
        'fouls_commited':0,
        'successful_dribbles':'0',
        'penalties_won':0,
        'big_chances_missed':0,
        'accurate_crosses':'0',

    }
    for stat_group in stats:
        for stat_title, stat_value in stat_group.get('stats', {}).items():
            if stat_title == 'Total shots':
                new_stats['total_shots'] = stat_value.get('value', 0)
            elif stat_title == 'Accurate passes':
                new_stats['accurate_passes'] = extract_percentage(stat_value.get('value', '0'))
            elif stat_title == 'Chances created':
                new_stats['chances_created'] = stat_value.get('value', 0)
            elif stat_title == 'Expected goals (xG)':
                new_stats['expected_goals(xG)'] = float(stat_value.get('value', '0'))
            elif stat_title == 'Expected goals on target (xGOT)':
                new_stats['expected_goals_on_target(xGOT)'] = float(stat_value.get('value', '0'))
            elif stat_title == 'Expected assists (xA)':
                new_stats['expected_assists(xA)'] = float(stat_value.get('value', '0'))
            elif stat_title == 'xG + xA':
                new_stats['xG+xA'] = float(stat_value.get('value', '0'))
            elif stat_title == 'Shot accuracy':
                new_stats['shot_accuracy'] = extract_percentage(stat_value.get('value', '0'))
            elif stat_title == 'Blocked shots':
                new_stats['blocked_shots'] = stat_value.get('value', 0)
            elif stat_title == 'Touches':
                new_stats['touches'] = stat_value.get('value', 0)
            elif stat_title == 'Touches in opposition box':
                new_stats['touches_in_opposition_box'] = stat_value.get('value', 0)
            elif stat_title == 'Passes into final third':
                new_stats['passes_into_final_third'] = stat_value.get('value', 0)
            elif stat_title == 'Accurate long balls':
                new_stats['accurate_long_balls'] = extract_percentage(stat_value.get('value', '0'))
            elif stat_title == 'Dispossessed':
                new_stats['dispossessed'] = stat_value.get('value', 0)
            elif stat_title == 'xG Non-penalty':
                new_stats['xG_Non_penalty'] = float(stat_value.get('value', '0'))
            elif stat_title == 'Tackles won':
                new_stats['tackles_won'] = extract_percentage(stat_value.get('value', '0'))
            elif stat_title == 'Clearances':
                new_stats['clearances'] = stat_value.get('value', 0)
            elif stat_title == 'Headed clearance':
                new_stats['headed_clearance'] = stat_value.get('value', 0)
            elif stat_title == 'Defensive actions':
                new_stats['defensive_actions'] = stat_value.get('value', 0)
            elif stat_title == 'Recoveries':
                new_stats['recoveries'] = stat_value.get('value', 0)
            elif stat_title == 'Dribbled past':
                new_stats['dribbled_past'] = stat_value.get('value', 0)
            elif stat_title == 'Duels won':
                new_stats['duels_won'] = stat_value.get('value', 0)
            elif stat_title == 'Duels lost':
                new_stats['duels_lost'] = stat_value.get('value', 0)
            elif stat_title == 'Ground duels won':
                new_stats['ground_duels_won'] = extract_percentage(stat_value.get('value', '0'))
            elif stat_title == 'Aerial duels won':
                new_stats['aerial_duels_won'] = extract_percentage(stat_value.get('value', '0'))
            elif stat_title == 'Was fouled':
                new_stats['was_fouled'] = stat_value.get('value', 0)
            elif stat_title == 'Fouls committed':
                new_stats['fouls_commited'] = stat_value.get('value', 0)
            elif stat_title == 'Successful dribbles':
                new_stats['successful_dribbles'] = extract_percentage(stat_value.get('value', '0'))
            elif stat_title == 'Penalties won':
                new_stats['penalties_won'] = stat_value.get('value', 0)
            elif stat_title == 'Big chances missed':
                new_stats['big_chances_missed'] = stat_value.get('value', 0)
            elif stat_title == 'Accurate crosses':
                new_stats['accurate_crosses'] = extract_percentage(stat_value.get('value', '0'))

    return new_stats

def filter_non_lists(input_list):
    return [item for item in input_list if isinstance(item, list)]

def flatten_list_of_dicts(input_list):
    return [item for sublist in input_list for item in sublist]

def convert_json_to_csv(json_data, csv_filename):
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=json_data[0].keys())
        writer.writeheader()
        writer.writerows(json_data)
    print(f"JSON 데이터가 {csv_filename} 파일로 성공적으로 변환되어 저장되었습니다.")

def remove_key_from_json(json_data, key_to_remove):
    for item in json_data:
        if key_to_remove in item:
            del item[key_to_remove]

fotmob = MobFot()

result = fotmob.get_match_details(4193574)

content = result.get('content', {}).get('lineup', {}).get('lineup', {})

team1 = content[0].get('optaLineup',{})
t1_bench = team1.get('bench',{})
t1_players = team1.get('players',{})
t1_players = t1_players+[item for sublist in t1_bench for item in sublist]

team2 = content[1].get('optaLineup',{})
t2_bench = team2.get('bench',{})
t2_players = team2.get('players',{})
t2_players = t2_players+[item for sublist in t2_bench for item in sublist]

data = t1_players + t2_players

for sublist in data:
    for player in sublist:
        if isinstance(player, dict):
            del player['id']
            del player['positionId']
            del player['localizedPosition']
            del player['shirt']
            del player['usualPosition']
            del player['usingOptaId']
            del player['teamId']
            del player['imageUrl']
            del player['pageUrl']
            del player['role']
            del player['teamData']
            del player['shotmap']
            player['name'] = player['name'].get('fullName', '')
            player['rating'] = player['rating'].get('num', '')
            player['fantasyScore'] = player['fantasyScore'].get('num', '')
            player.update(add_event(player['events']))
            player.update(add_stats(player['stats']))
            del player['events']
            del player['stats']

data = filter_non_lists((data))
data = flatten_list_of_dicts((data))

remove_key_from_json(data,'shortName')
remove_key_from_json(data,'isHomeTeam')
remove_key_from_json(data,'timeSubbedOn')
remove_key_from_json(data,'timeSubbedOff')
remove_key_from_json(data,'subbedInTime')

convert_json_to_csv(data, 'output.csv')

with open('data.json', 'w') as file:
    json.dump(data, file, indent=4)

