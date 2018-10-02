import subprocess
import os
import json

from dateutil.parser import parse as dateutil_parse
import datetime

def export_history(dir="joevotes"):
    os.system(f'git fast-export HEAD -- {dir}\\votes.json > {dir}\\vote_data')
    data = open(f'{dir}\\vote_data', 'rb').read()
    data_segments = []
    cur_pos = 0
    while True:
        data_pos_begin = data.find(b'\ndata', cur_pos)
        if data_pos_begin == -1:
            break
        data_pos_end = data.find(b'\n', data_pos_begin + 5)

        data_pos = data_pos_end + 1
        data_length = int(data[data_pos_begin + 5:data_pos_end])
        data_segments.append({
            "data_pos": data_pos,
            "data_length": data_length
        })

        cur_pos = data_pos

    vote_history = []
    c = 0


    max_vote = None
    min_vote = None

    for segment in data_segments:
        data_pos = segment['data_pos']
        data_length = segment['data_length']
        file_data = data[data_pos:data_pos + data_length]
        if file_data.startswith(b'{'):
            vote_data = json.loads(file_data)
            date = vote_data['last_update'] + ' EST'
            if dateutil_parse(date) < datetime.datetime.now() - datetime.timedelta(days=1) :
                continue
            for game in vote_data['votes']:
                found = False
                for history in vote_history:
                    if game['game'] == history['game']:
                        history['data'][date] = game['votes']
                        if int(game['votes']) != history['last_vote']:
                            history['last_vote'] = int(game['votes'])
                        if max_vote is None or int(game['votes']) > max_vote:
                            max_vote = int(game['votes'])
                        if min_vote is None or int(game['votes']) < min_vote:
                            min_vote = int(game['votes'])
                        found = True
                        break
                if not found:
                    vote_history.append({
                        "game": game['game'],
                        "data": {date: game['votes']},
                        "last_vote": int(game['votes'])
                    })

    vote_history = sorted(vote_history, key=lambda x: x['last_vote'], reverse=True)
    with open(f"{dir}\\vote_history.json", "w") as f:
        f.write(json.dumps(
            {"max_vote": max_vote, "min_vote": min_vote, "history": vote_history}, indent=4, sort_keys=True))
        f.truncate()

if __name__ == "__main__":
    export_history(".")