import subprocess
import os
import json

from dateutil.parser import parse as dateutil_parse
import datetime

def export_history():
    os.system('git fast-export HEAD -- joevotes\\votes.json > joevotes\\vote_data')
    data = open('joevotes\\vote_data', 'rb').read()

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
    max_vote = 0
    c = 0

    for segment in data_segments:
        data_pos = segment['data_pos']
        data_length = segment['data_length']
        file_data = data[data_pos:data_pos + data_length]
        if file_data.startswith(b'{'):
            vote_data = json.loads(file_data)
            date = vote_data['last_update']
            if dateutil_parse(date) < datetime.datetime.now() - datetime.timedelta(days=1) :
                continue
            for vote in vote_data['votes']:
                found = False
                for history in vote_history:
                    if vote[0] == history['name']:
                        history['data'][date] = vote[1]
                        if int(vote[1]) != history['last_vote']:
                            history['last_vote'] = int(vote[1])

                        found = True
                        break
                if not found:
                    vote_history.append({
                        "name": vote[0],
                        "data": {date: vote[1]},
                        "last_vote": int(vote[1])
                    })

    max_vote = 0
    for history in vote_history:
        if history['last_vote'] > max_vote:
            max_vote = history['last_vote']

    vote_history = sorted(vote_history, key=lambda x: x['last_vote'], reverse=True)
    with open("joevotes\\vote_history.json", "w") as f:
        f.write(json.dumps(
            {"max_vote": max_vote, "history": vote_history}, indent=4, sort_keys=True))
        f.truncate()
