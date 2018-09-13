import discord
import datetime
import json
import os
import asyncio

# I know the following code is not super pretty, but it works :D

async def update_votes(messages):
    votes = [] # list of lists [gamename, nr_votes]
    voters = {} # key will be voter id (user#1234), value will be list of games voted on
    
    
    for message in messages:
        for reaction in message.reactions:
            if ord(reaction.emoji) == 128077: # thumbs up
                votes.append([message.content, reaction.count])
                reactors = await reaction.users().flatten()
                for reactor in reactors:
                    if str(reactor) not in voters:
                        voters[str(reactor)] = [message.content, ]
                    else:
                        voters[str(reactor)].append(message.content)
    olddata = json.load(open('oldvotes.json', 'r'))
    oldvotes = olddata['votes']
    for vote in votes:
        for oldvote in oldvotes:
            if oldvote[0] == vote[0]:
                diff = vote[1] - oldvote[1]
                if diff > 0:
                    diff = f"+{diff}"
                else:
                    diff = f"{diff}"
                vote.append(diff)
    
    olddata_date = olddata['last_update']
    
    votes = sorted(votes, key=lambda x: x[1], reverse=True)
    top_x = votes[:10]
    
    topx_voters = []
    for voter in voters:
        for top in top_x:
            # print(top, voters[voter])
            if top[0] in voters[voter]:
                topx_voters.append(voter)
                break
    
    filepath = r"C:\Users\Nodja\Desktop\proj\Nodja.github.io\joevotes\votes.json"
    now = datetime.datetime.now()
    vote_data = {
        "last_update": now.strftime("%Y-%m-%d %H:%M:%S"),
        "compare_date": olddata_date,
        "total_voters": len(voters),
        "nontop_voters": len(voters) - len(topx_voters),
        "votes": votes
    }
    
    with open(filepath, 'w') as f:
        f.write(json.dumps(vote_data))
        f.truncate()
    
    # push to github, repo preconfigured
    repo_dir = r"C:\Users\Nodja\Desktop\proj\Nodja.github.io"
    os.chdir(repo_dir)
    os.system("git add joevotes\\votes.json")
    os.system("git commit -m \"Update votes (automated)\"")
    os.system("git push origin")
    
    
async def fetch_votes():
    print("Running.")
    await client.wait_until_ready()
    print(f"Logged in as {client.user}")
    channel = None
    for guild in client.guilds:
        if guild.id == 308515582817468420: # JADS
            for c in guild.channels:
                if c.id == 375432166659588099: # voting channel
                    channel = c
    
    if channel is None:
        return
    
    messages = []
    
    dt_from = datetime.datetime(2018, 9, 8, 18, 41, 26, 689000)
    dt_to = datetime.datetime(2018, 9, 8, 19, 0, 4)
    
    
    async for message in channel.history(after=dt_from, limit=200):
        if message.created_at >= dt_to:
            break
        # print(message.id, message.created_at, message.content)
        messages.append(message)
        
    await update_votes(messages)
    now = datetime.datetime.now()
    print(f"Done. {now.strftime('%Y-%m-%d %H:%M:%S')}")
    await asyncio.sleep(300) # FIXME: doesnt work for some reason, using external workaround

client = discord.Client() 
client.loop.create_task(fetch_votes())
client.run("discord token", bot=False)



