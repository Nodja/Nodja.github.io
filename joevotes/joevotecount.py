import discord
import datetime
import json
import os
import asyncio
import re
import glob

from exporthistory import export_history
# I know the following code is not super pretty, but it works :D


async def update_votes(messages):
    votes = []
    voter_games = {}

    specials_list = ["LEON", "god damn weebs", "Your Mom"]
    specials = {}

    for message in messages:
        for reaction in message.reactions:
            if type(reaction.emoji) is not str:
                continue
            if ord(reaction.emoji[0]) == 128123:  # spooky ghost
                if message.content in specials_list:
                    specials[message.content] = reaction.count
                    continue
                votes.append({"game": message.content,
                              "votes": reaction.count,
                              "votes_rounds": []})
                reactors = await reaction.users().flatten()
                for reactor in reactors:
                    if str(reactor) not in voter_games:
                        voter_games[str(reactor)] = [message.content, ]
                    else:
                        voter_games[str(reactor)].append(message.content)

    for file in glob.glob("votes_round*.json"):
        match = re.match(r"(votes_round\d+).json", file)
        if match:
            olddata = json.load(open(file, 'r'))
            oldvotes = olddata['votes']
            for vote in votes:
                for oldvote in oldvotes:
                    if oldvote['game'] == vote['game']:
                        vote["votes_rounds"].append(oldvote['votes'])

    votes = sorted(votes, key=lambda x: x['votes'], reverse=True)
    top = 5

    top_voters = []
    for voter in voter_games:
        for vote in votes[top:]:
            if vote['game'] in voter_games[voter]:
                top_voters.append(voter)
                break

    votes = sorted(votes, key=lambda x: x['game'].lower())
    filepath = r"votes.json"
    now = datetime.datetime.now()
    vote_data = {
        "last_update": now.strftime("%Y-%m-%d %H:%M:%S"),
        "total_voters": len(voter_games),
        "nontop_voters": len(voter_games) - len(top_voters),
        "specials": specials,
        "votes": votes,
        "top": top
    }

    with open(filepath, 'w') as f:
        f.write(json.dumps(vote_data, indent=4, sort_keys=True))
        f.truncate()

    # push to github, repo preconfigured
    repo_dir = r"C:\Users\Nodja\Desktop\proj\Nodja.github.io"
    os.chdir(repo_dir)

    # os.system("git add joevotes\\votes.json")
    # os.system("git commit -m \"Update votes (automated)\"")

    export_history()
    # os.system("git add joevotes\\vote_history.json")
    # os.system("git commit -m \"Update vote history (automated)\"")

    # os.system("git push origin")


async def fetch_votes():
    print("Running.")
    await client.wait_until_ready()
    print(f"Logged in as {client.user}")
    channel = None
    for guild in client.guilds:
        if guild.id == 308515582817468420:  # JADS
            for c in guild.channels:
                if c.id == 492088331287527454:  # voting channel
                    channel = c

    if channel is None:
        return

    messages = []

    dt_from = datetime.datetime(2018, 9, 22, 20, 7, 46)
    dt_to = datetime.datetime(2018, 9, 22, 20, 19, 3)

    async for message in channel.history(after=dt_from, limit=200):
        if message.created_at >= dt_to:
            break
        # print(message.id, message.created_at, message.content)
        messages.append(message)

    dt_leon = datetime.datetime(2018, 9, 22, 20, 24, 0)
    message = [message async for message in channel.history(after=dt_leon, limit=1)][0]
    messages.append(message)

    await update_votes(messages)
    now = datetime.datetime.now()
    print(f"Done. {now.strftime('%Y-%m-%d %H:%M:%S')}")
    # FIXME: doesnt work for some reason, using external workaround
    await asyncio.sleep(300)

client = discord.Client()
client.loop.create_task(fetch_votes())
client.run(os.environ['DISCORD_TOKEN'], bot=False)
