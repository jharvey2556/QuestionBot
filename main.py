from get_challenge import main as get_challenge
import discord
from discord import app_commands
import random
from columnar import columnar
import json
import sys

questions = {}
client = discord.Client(intents=discord.Intents.all())

token = sys.argv[1:]

@client.event
async def on_ready():
    on_ready.addq = False
    on_ready.addq_user = 123
    on_ready.question_toggle = False
    print("ready")
    on_ready.choices = []
    with open("questions.json","r") as f:
        on_ready.questions = json.load(f)

    with open("choices.txt","r") as f:
        for line in f.readlines():
            line = line.strip()
            line = line.split(",")
            line.pop(4)
            on_ready.choices.append(line)
 
@client.event
async def on_message(message):

    if message.author == client.user:
        return
    msg = message.content

    with open("save.json","r") as f:
        users = json.load(f)

    user = message.author.id

    if on_ready.addq == True:
        if message.author.id == on_ready.addq_user:
            if on_ready.question_toggle == False:
                addq_question = msg.split(",")
                on_ready.questions[addq_question[0]] = addq_question[1]
                with open("questions.json","w") as f:
                    json.dump(on_ready.questions, f)
                await message.channel.send("Enter the answers on one line with commas seperating them. eg: Red,Yellow,Blue,Green")
                on_ready.question_toggle = True
            else:
                i = 0
                addq_answer_temp = msg.split(",")
                addq_answer = []
                for y in addq_answer_temp:
                    i += 1
                    if i == 1:
                        y = "A ." + y
                    elif i == 2:
                        y = "B ." + y
                    elif i == 3:
                        y =  "C. " + y
                    elif i == 4:
                        y = "D. " + y
                    addq_answer.append(y)
                on_ready.choices.append(addq_answer)
                with open("choices.txt","w") as f:
                    for element in on_ready.choices:
                        for x in element:
                            f.write(str(x) + ",")
                        f.write("\n")
                await message.channel.send("Question added!")
                on_ready.question_toggle == False
                on_ready.addq = False

    questions = on_ready.questions
    async def trivia():
        randomnum = random.randint(1,len(questions))
        question_list = list(questions.keys())
        print(question_list)

        question = question_list[randomnum - 1]
        choice = on_ready.choices[randomnum - 1]
        choice_sep = "\n".join(choice)

        em = discord.Embed(title = f"{question}\n{choice_sep}")
        await message.channel.send(embed=em)

        answered = False
        while answered == False:
            response = await client.wait_for("message")
            if response.content.upper() in ["A","B","C","D"]:
                answer = response.content.upper()
                break
        
        if answer == questions[question]:
            return "correct"
        else:
            return "wrong"

    if msg == "$addquestion":
        on_ready.addq = True
        on_ready.addq_user = message.author.id
        await message.channel.send("Enter the question followed by a comma and then the letter which will represent the correct answer.\neg: What colour is a banana?,A")

    if msg == "$question":
        if await trivia() == "correct":
            await message.channel.send(f"Correct! <@{message.author.id}> gets +1 point")
            if str(user) in users:
                users[str(user)]["points"] += 1
            else:
                users[str(user)] = {}
                users[str(user)]["points"] = 1
        else:
            await message.channel.send("That is incorrect!")

    if msg == "$leaderboard":
        lb_list = []
        m = 0
        for user in users:
            lb_user = await client.fetch_user(user)
            lb_user = str(lb_user).split("#")[0]
            lb_points = users[user]["points"]
            lb_temp_list = [lb_user,lb_points]
            lb_list.append(lb_temp_list)
        lb_list_sort = sorted(lb_list,key=lambda l:l[1], reverse=True)
        lb_sep = ""
        col_width = max(len(str(word)) for row in lb_list_sort for word in row) + 5
        for n in lb_list_sort:
            if m == 10:
                break
            m += 1
            lb_sep += str(m) + ". " + n[0].ljust(col_width) + str(n[1]).ljust(col_width) + "\n"
        em = discord.Embed(title = f"__Leaderboard__\n{lb_sep}")
        await message.channel.send(embed=em)

    if msg == "$points":
        if str(user) in users:
            pass
        else:
            users[str(user)] = {}
            users[str(user)]["points"] = 0
        await message.channel.send(f"<@{message.author.id}>, You have {users[str(user)]['points']} points")

    with open("save.json","w") as f:
        users = json.dump(users, f)

client.run(token)



"""
add functionality to clear points for admins
view other peoples points
"""
