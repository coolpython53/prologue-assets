import time
import textwrap
import random
import json
import pygame
import threading
import requests
import tempfile
import os
import webbrowser
from flask import Flask, request
import logging

#Variables

sound_enabled = True

character = ""

sibling = ""

result = 0

usedElementalSkill = "False"

elementalParticles = 0

enemyHP = 0

health = 100

level = 1

xp = 0

food_inventory = []

inventory = []

max_attk = 5

defense = 5

mora = 0

story_progress = 0

#easter eggs

paimon_trust = 100
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

import threading

def play_sound_and_wait(play_url):
    global sound_enabled
    if not sound_enabled:
        return

    # Use a flag to tell the game when to continue
    waiting_for_audio = threading.Event()

    app = Flask(__name__)
    
    # Hide the annoying "Statue" messages in terminal
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    @app.route('/close')
    def close():
        waiting_for_audio.set() # This "unlocks" the game
        return "Resuming game... you can close this tab."

    @app.route('/')
    def index():
        return f"""
        <html>
        <body style="background-color: #121212; color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; font-family: sans-serif; margin: 0;">
            <div style="text-align: center; border: 2px solid #3d3d3d; padding: 50px; border-radius: 20px; background: #1e1e1e;">
                <h1 style="color: #ffd45e;">Paimon is speaking...</h1>
                <audio id="player" autoplay controls><source src="{play_url}" type="audio/mpeg"></audio>
                <br><br>
                <button onclick="finish()" style="padding: 15px 30px; font-size: 18px; cursor: pointer; background: #4CAF50; color: white; border: none; border-radius: 10px;">
                    DONE (Continue Game)
                </button>
            </div>
            <script>
                function finish() {{
                    fetch('/close').then(() => {{ window.close(); }});
                }}
                document.getElementById('player').onended = finish;
            </script>
        </body>
        </html>
        """

    # Start Flask in a background thread so it doesn't freeze the script
    server_thread = threading.Thread(target=app.run, kwargs={'port': 5000, 'debug': False, 'use_reloader': False})
    server_thread.daemon = True # This ensures the server dies when the game eventually ends
    server_thread.start()

    # Open the browser
    webbrowser.open("http://127.0.0.1:5000")
    
    print("Waiting for Paimon to finish speaking...")
    
    # This PAUSES the game until you click "DONE"
    waiting_for_audio.wait() 
    print("Continuing journey!")

def sp(text, play_url=None, speed=0.03, width=30, wait=1):
    wrapped_text = textwrap.fill(text, width=width)
    
    # Print the text first
    for line in wrapped_text.split("\n"):
        for char in line:
            print(char, end="", flush=True)
            time.sleep(speed)
        print()
    print()

    # If there is sound, open the bridge and WAIT
    if play_url and sound_enabled:
        play_sound_and_wait(play_url)

    if wait == 1:
        w()
def selection(options):
    global result
    
    while True:
        user_input = input("").strip().lower()

        if user_input == "save":
            save_game()
            continue

        try:
            result = int(user_input)
            if 1 <= result <= options:
                return
            else:
                print("Invalid option.")
        except ValueError:
            print("Enter a number or type 'save'.")


def save_game():
    global character, sibling, health, level, xp
    global max_attk, defense, elementalParticles
    global mora, food_inventory, inventory
    global usedElementalSkill, paimon_trust
    global story_progress

    # Collect all game data
    game_data = {
        "character": character,
        "sibling": sibling,
        "health": health,
        "level": level,
        "xp": xp,
        "max_attk": max_attk,
        "defense": defense,
        "elementalParticles": elementalParticles,
        "mora": mora,
        "food_inventory": food_inventory,
        "inventory": inventory,
        "usedElementalSkill": usedElementalSkill,
        "paimon_trust": paimon_trust,
        "story_progress": story_progress
    }

    # Convert to JSON string
    game_json = json.dumps(game_data)

    # Print the JSON string for the user to copy
    print("\n==== COPY THIS SAVE DATA ====")
    print(game_json)
    print("==== END OF SAVE DATA ====")
    print("Copy everything between the lines and save it in a local .txt file. Later, you can paste it to load your game!")  

import json

def load_game():
    global character, sibling, health, level, xp
    global max_attk, defense, elementalParticles
    global mora, food_inventory, inventory
    global usedElementalSkill, paimon_trust
    global story_progress

    save_string = input("Paste your save data here: ")

    try:
        game_data = json.loads(save_string)

        character = game_data["character"]
        sibling = game_data["sibling"]
        health = game_data["health"]
        level = game_data["level"]
        xp = game_data["xp"]
        max_attk = game_data["max_attk"]
        defense = game_data["defense"]
        elementalParticles = game_data["elementalParticles"]
        mora = game_data["mora"]
        food_inventory = game_data["food_inventory"]
        inventory = game_data["inventory"]
        usedElementalSkill = game_data["usedElementalSkill"]
        paimon_trust = game_data["paimon_trust"]
        story_progress = game_data["story_progress"]
        print()
        print("Game loaded successfully!")
        return True
    except:
        print("Failed to load save. Check your pasted data.")
        return False

def st():
    global character, result, health, level, food_inventory
    print("Health: " + str(health))
    print("Your level: " + str(level))
    print("Maximum damage: " + str(max_attk))
    for _ in food_inventory:
        print(_)
    print("Elemental Particles: " + str(elementalParticles))

def w(seconds=0.25):
    time.sleep(seconds)
    
def Character_Selection():
    global character, result, sibling
    # Character picking
    sp("Pick your character")
    sp("1. Aether")
    sp("2. Lumine")
    selection(2)
    if result == 1:
        character = "Aether"
        sibling = "Lumine"
    elif result == 2:
        character = "Lumine"
        sibling = "Aether"
    #Report back to the player
    sp("You picked " + character + "!")
    w()

def fight(EHP, EDM):
    global usedElementalSkill, elementalParticles, enemyHP, health, max_attk, defense, xp
    enemyHP = EHP
    usedElementalSkill = "False"   # Reset at start of fight
    lvl_up()

    while enemyHP > 0 and health > 0:
        print("Your enemy has " + str(enemyHP) + " health now.")
        st()
        print()
        print("1. Attack")
        print("2. Elemental skill")
        print("3. Elemental burst")
        print("4. Eat food")
        selection(4)

        if result == 1:
            sp("You attacked normally.")
            enemyHP -= random.randint(max_attk - 3, max_attk)

        elif result == 2:
            if usedElementalSkill == "False":
                sp("You activated your elemental skill")
                usedElementalSkill = "True"
                enemyHP -= max_attk + 30
                elementalParticles += 20
            else:
                sp("You already used this!")
                continue   # <-- DO NOT restart fight

        elif result == 3:
            if elementalParticles >= 60:
                sp("You used your elemental burst.")
                elementalParticles -= 60
                enemyHP -= (max_attk + 60)
            else:
                sp("Not enough elemental Particles! You need " + str(60 - elementalParticles) + " more!")
                continue   # <-- DO NOT restart fight
        elif result == 4:
            ate = eat_food()
            continue

        elementalParticles += 10
        if enemyHP > 0:
            damage = max(1, random.randint(EDM - (defense * 2), EDM - defense))
            health -= damage
    if health <= 0:
        sp("You were defeated... - Paimon")
        health += 150
        fight(EHP)
    else:
        sp("Enemy defeated! - Paimon")

    usedElementalSkill = "False"   # Reset after fight
    xp += random.randint(EHP, EHP + 300)
    lvl_up()

def lvl_up():
    global xp, level, max_attk, health, defense
    while xp >= 1000:
        max_attk += 5
        xp -= 1000
        level += 1
        health += 10
        defense += 5
        print(f"Level up! You are at level {level}")

def add_food(name, amount, heal):
    global food_inventory
    for item in food_inventory:
        if item["name"] == name:
            item["amount"] += amount
            return
    food_inventory.append({
        "name": name,
        "amount": amount,
        "heal": heal
    })

def eat_food():
    global health, food_inventory

    if len(food_inventory) == 0:
        print("You have no food!")
        return False

    print("Choose a food to eat:")

    # Show all food
    food_list = []
    for item in food_inventory:
        food_list.append(item)

    for i, food in enumerate(food_list, start=1):
        print(
            f"{i}. {food['name']} "
            f"x{food['amount']} "
            f"(Heals {food['heal']} HP)"
        )

    selection(len(food_list))
    chosen_food = food_list[result - 1]

    # Eat the food
    health += chosen_food["heal"]
    print(
        f"You ate {chosen_food['name']} "
        f"and recovered {chosen_food['heal']} HP!"
    )

    chosen_food["amount"] -= 1

    # Remove if empty
    if chosen_food["amount"] <= 0:
        food_inventory.remove(chosen_food)

    return True

def nxt():
    global story_progress
    story_progress += 1

#-------------------------------------------------------------------------------------------------------------------------


#Opening cutscene
def P1():
    global sibling
    sp("So, what you're trying to say is that you fell here... from another world? - Paimon", "https://coolpython53.github.io/prologue-assets/wanderer's-trail/paimon-1.mp3")
    w()
    sp("But when you wanted to leave, and go on to the next world, your path was blocked, by some unknown god? - Paimon")
    sp("Outlanders... Your journey ends here... - Unknown God")
    sp("The arrogation of mankind ends now. - Unknown god")
    if sibling == "Aether":
        sp("You and your sibling battle the god. The god takes away your brother.")
        sp("And just like that, the god took away my brother. Some kind of seal was cast upon me, and I lost my power. So while we used to travel from world to world, we are now trapped here. - You")
    elif sibling == "Lumine":
        sp("You and your sibling battle the god. The god takes away your sister.")
        sp("And just like that, the god took away my sister. Some kind of seal was cast upon me, and I lost my power. So while we used to travel from world to world, we are now trapped here. - You")   
    sp("How many years ago was it? I don't know... But I intend to find out. When I woke, I was all alone... Until I met you two months ago.- You")
    sp("Yeah, Paimon really owes you for that. Otherwise Paimon might have drowned... - Paimon")
    sp("So Paimon will do her best to be a great guide! - Paimon")
    sp("We should head off. Let's get going! - Paimon")
    nxt()

#Bird's eye view (The outlander who caught wind)
def P2():
    sp("Quest: You begin your journey in Starfell Valley, exploring the land and seeing its sights together with Paimon.")
    sp("Oh wowwwww! That's a statue of the seven! There are a few of those statues scattered across the land to show The Seven's protection over the world. - Paimon")
    sp("Among the gods, this one controls the wind. Paimon's not sure whether the god you're looking for is the Anemo God, but... - Paimon")
    sp("Paimon'll take you to the Anemo God's place first! - Paimon")
    nxt()

def P3():
    global mora, xp, result
    sp("1. Follow Paimon")
    sp("2. Walk in the other direction.")
    selection(2)
    if result == 1:
        if sibling == "Aether":
            sp("As we all know, poetry and language flow like the wind... There'll definitely be someone there who knows about your brother! At least, that's what Paimon thinks! - Paimon")
        elif sibling == "Lumine":
            sp("As we all know, poetry and language flow like the wind... There'll definitely be someone there who knows about your sister! At least, that's what Paimon thinks! - Paimon")
        sp("Whether the gods actually answer you is a different story. You never know unless you try. - Paimon")
        sp("You go over to the lake where Paimon is waiting.")
        sp("So, let's hop to it! You can swim right over!")
    elif result == 2:
        sp("Hey! Where are you going? Come to Paimon! Don't stray too far from Paimon! - Paimon")
        sp("You should follow Paimon for now... - Paimon")
        sp("You go to Paimon.")
        P3()
    mora += 975
    xp += 500
    lvl_up()
    nxt()

#Unexpected power (The outlander who caught wind)
def P4():
    sp("Quest: As you advanced, a Statue of the Seven appeared on the horizon ahead of you. At Paimon's suggestion, you go to investigate.")
    sp("You touch the Anemo Statue")
    sp("Ooh! Did you just feel the elements of the world? Seems all you had to do was just touch the statue and you got the power of Anemo! - Paimon")
    sp("As much as they may want it, people in this world can never get a hold of powers as easily as you... - Paimon")
    nxt()
    
def P5():
    global result
    sp("1. I think I know why, It's because...")
    sp("2. This can't be good...")
    selection(2)
    if result == 1:
        sp("Ah-ha, it's because you're not from this world to begin with. - Paimon")
    elif result == 2:
        sp("It's a bit rude to say that about the power the gods just gave you! - Paimon")
    sp("If we keep heading west from here, we'll eventually reach Mondstadt, the City of Freedom. Mondstadt is the city of wind, because they worship the God of Anemo. - Paimon")
    sp("So perhaps, because you got power from the God of Anemo, you can find some clues there. - Paimon")
    if sibling == "Aether":
        sp("There are also lots of bards there, so perhaps one of them has heard news of your brother.")
    elif sibling == "Lumine":
        sp("There are also lots of bards there, so perhaps one of them has heard news of your sister.")
    sp("Let's move on then! The elements in this world responded to your prayers and Paimon thinks that's a lovely sign. - Paimon")
    sp("Anemo slimes appear.")
    nxt()

def P6():
    global mora, xp
    sp("You have spotted a slime.")
    fight(100, 12)
    fight(125, 15)
    sp("These are the Anemo powers you got from the Statue of The Seven. Aww... Paimon's so jealous! Why doesn't Paimon get cool fighting powers!? - Paimon")
    mora += 1100
    add_food("Sweet madame", 10, 150)
    add_food("Teyvat fried egg", 10, 100)
    xp += 575
    lvl_up()
    nxt()

#Forest rendezvous
def P7():
    sp("Quest: Unexpectedly, the power of Anemo within the Statue of the Seven resonated with you. You decided to begin your investigation with the Anemo Archon of Teyvat's Seven Archons. As such, the first order of the day is to reach the land under the Anemo Archon's protection: Mondstadt.")
    sp("A dragon flies above.")
    sp("Wow! What was that? There's something huge, in the sky! It's headed towards the heart of the forest. We must proceed with caution. - Paimon")
    sp("Huh? Look at that! - Paimon")
    sp("You see a boy talking to a dragon.")
    sp("...Don't be afraid... I'm back now... - ???")
    sp("Is he talking... to a dragon? Oh? - Paimon")
    sp("Who's there?! - ???")
    sp("The dragon senses the your presence and roars at the boy. The boy vanishes by using his Anemo powers and the dragon flies away.")
    nxt()

def P8():
    global result, mora, xp
    sp("That was close! Paimon almost got blown away! Luckily Paimon managed to grab hold of your hair! Thanks. - Paimon")
    sp("1. Good thing you didn't pull my hair out.")
    sp("2. Good thing the dragon didn't notice us.")
    selection(2)
    sp("Just what was that? Paimon thought we were gonna get eaten. It definitely has something to do with that weirdo who was talking to the dragon... - Paimon")
    sp("1. I can't believe dragons exist in this world.")
    sp("2. Is talking to dragons normal?")
    selection(2)
    if result == 1:
        sp("Yeah, Paimon gets why you're worried.. - Paimon")
    elif result == 2:
        sp("Of course not! - Paimon")
    sp("Oh? What's that? There's some kind of shiny red thingy on the big rock over there... Let's go take a closer look. Be careful! Paimon doesn't have a good feeling about this... - Paimon")
    sp("You go to the crimson crystal.")
    sp("Paimon's never seen a stone like this before, so Paimon can't tell what it is. All Paimon knows is that it's dangerous. Best we put it away for now. Okay, we've got it! Now let's get out of here. - Paimon")
    sp("You obtained the crimson crystal.")
    fight(300, random.randint(10, 20))
    mora += 1100
    xp += 575
    lvl_up()
    nxt()

#Wind-Riding knight (The outlander who caught wind)
def P9():
    global paimon_trust
    sp("Quest: On the path to Mondstadt, you inadvertently eavesdropped on a meeting between a huge dragon and a mysterious figure. As you proceeded with various doubts in mind, a perky young girl showed up to block your path.")
    sp("Hey, you! Stop right there! - ???")
    sp("As you and Paimon walk through the forest, a mysterious girl in red jumps and landed in front of your path.")
    sp("May the Anemo god protect you, stranger. - ???")
    sp("I am Amber, Outrider for the knights of Favoious. You don't look like citizens of Mondstadt. Explain yourselves. - Amber")
    sp("We're not looking for trouble. - Paimon")
    sp("That's what all the troublemakers say.")
    if character == "Lumine":
        sp("1. Hello, I'm Lumine.")
    elif character == "Aether":
        sp("1. Hello, I'm Aether.")
    selection(1)
    sp("... Doesn't sound like a local name to me. And this... mascot, what's the deal with it? - Amber")
    sp("1. We're friends.")
    sp("2. Emergency food.")
    selection(2)
    if result == 1:
        sp("We've only been traveling partners for two months, but... We've already become the best of friends! - Paimon")
    elif result == 2:
        sp("Hey! That's even worse than being a mascot! - Paimon")
        paimon_trust -= 100
    sp("So, to sum it up, you're traveling partners, right? Well look, there's been a large dragon sighted around Mondstadt recently. Best you get inside the city as soon as possible. It's not far from here, I'll escort you there. - Amber")
    sp("Oh? Aren't you out here for some other reason? - Paimon")
    sp("I am. But not to worry, I can keep you both safe while doing that too. Besides... I'm still not sure if I can trust you two just yet! - Amber")
    sp("1. Why so suspicious?")
    sp("2. That's a rather rude way to speak to guests.")
    selection(2)
    sp("Oh, ahh... I'm sorry. probably not something I should say as a knight. I give you my apologies, uh... strange yet... respectable travelers. - Amber")
    sp("That sounded so fake! - Paimon")
    sp("Do you have something against the type of language usage prescribed by the Knights of Favonius Handbook!? - Amber")
    nxt()
    
def P10():
    global sibling, mora, xp
    sp("So, suspicious travelers, what are you doing here in Mondstadt?")
    if sibling == "Aether":
        sp("Lumine got seperated from her brother during a really, really long journey. Paimon is her travel buddy, helping her to find her brother. - Paimon")
    elif sibling == "Lumine":
        sp("Aether got seperated from his sister during a really, really long journey. Paimon is his travel buddy, helping him find his sister. - Paimon")
    sp("Oh, looking for your family... Huh. Ah... Okay! Let me finish my other stuff first, and then I can help you put up posters around the city. - Amber")
    sp("What exactly do you have to finish doing first? - Paimon")
    sp("It's simple. You'll understand in a bit.")
    mora += 1200
    xp += 625
    lvl_up()
    nxt()
    
#Going upon the breeze
def P11():
    sp("Ah! A hilichurl! - Paimon")
    sp("Quick! Get it! - Amber")
    fight(150, random.randint(15, 20))
    sp("These monsters have been getting too close to the city recently. My task this time is to clear out their camp. - Amber")
    fight(200, random.randint(30, 40))
    fight(220, random.randint(30, 40))
    fight(100, random.randint(30, 40))
    nxt()

def P12():
    global xp, mora
    sp("Heh, nothing to it. Though I've gotta say, you surprised me a little with your moves there... Thanks for the backup. How'd it feel? - Amber")
    sp("1. Barely broke a sweat.")
    sp("2. Those things are tougher than they look.")
    selection(2)
    sp("Now that you mention it, how is it the hilichurls ended up here? These creatures don't seem like the type to set up camp so close to cities like this. - Paimon")
    sp("Exactly. It's more normal for them to be much further out in the wilderness. But because the dragon — Stormterror — has been around a lot more recently, our orchards have been destroyed and the local market has been affected as well.  When the storms hit, we usually end up with at least a few injuries, so the Knights of Favonius have been tied up doing the best they can to defend the area. - Amber")
    sp("So these annoying creatures have been getting closer and closer to the city? - Paimon")
    sp("Exactly. That said, clearing this camp helped make the area a little bit safer. Come with me! A responsible knight must make sure to see you to the city safely. - Amber")
    xp += 925
    mora += 1800
    nxt()

#City of freedom
def P13():
    sp("Quest: With your help, the problem was resolved quickly. Led by Amber, you reach the city of freedom — Mondstadt.")
    sp("Let me officially introduce the city of wind, dandelions, and freedom — Travelers under the protection of the Knights of Favonius — Welcome to Mondstadt! - Amber")
    sp("Finally, no more having to camp outdoors! But... the city folk don't look too cheery. - Paimon")
    sp("Everyone's been put out of place by Stormterror recently. But everything will turn out fine as long as Jean's with us!")
    sp("Jean? - Paimon")
    sp("Acting Grand Master of the Knights of Favonius — Jean, Defender of Mondstadt. With Jean on our side, surely even the vicious Stormterror will be no match for us. - Amber")
    sp("1. (Sounds like someone pretty impressive...)")
    sp("2. (I hope she knows something about the God of Anemo)")
    selection(2)
    sp("Before I take you guys to the Knights of Favonius Headquarters, I have a present for you. It's a reward for helping me clear out that hilichurl camp. - Amber")
    sp("Hey! Why doesn't Paimon get a reward? - Paimon")
    sp("Ahh... Because this reward is useless to you, Paimon. But I'll treat you to a traditional Mondstat delicacy - Sticky honey roast!")
    sp("STICKY HONEY ROAST! - Paimon")
    sp("Come with me, we'll head to the city's ahh... high ground. - Amber")
    nxt()

def P14():
    global mora, xp
    sp("This used to be a bustling street... But with so many Stormterror attacks recently, the usual crowds are nowhere to be seen. Except for the local tavern near the city wall over there. They haven't been affected. If anything, their business is better than ever. - Amber")
    sp("So, the present I want to give you is... A Wind Glider! Outriders use them to ride the wind, and the people of Mondstadt love using them too. I brought you here to give it to you so you can experience it right away! - Amber")
    sp("Oh, you're really excited about these wind gliders, huh! - Paimon")
    sp("Well that's because the wind is the heart and soul of Mondstadt! Alrighty then, enough talk! Let's give it a whirl! It's easy to use, but you still need to pay attention to my instructions. - Amber")
    mora += 1625
    xp += 850
    nxt()

#Dragon storm
def P15():
    sp("Quest: The usually-peaceful Mondstadt was suddenly assailed by a dragon. This is the Stormterror that Amber spoke of, and was the gigantic creature that you encountered in the forest earlier.")
    sp("The sky... - Amber")
    sp("The sky turns dark as the dragon from before arrives. The dragon flies around Mondstadt City and summoning several tornadoes. You get caught with the tornado. You open your wind glider and starts gliding in the sky as the dragon flies over them.")
    sp("Huh? How are you staying afloat like this with just a Wind Glider? - Paimon")
    sp("I'm preventing your fall with the power of a thousand winds. Now, concentrate. See yourself grasping the wind. Harness its energy. - Mysterious voice")
    sp("Who... who said that!? - Paimon")
    fight(500, random.randint(60, 70))
    nxt()

def P16():
    global character, mora, xp
    sp("A—Are you hurt? - Amber")
    sp("You've actually got the power to go up against the dragon... Are you a new ally... or a new storm? - ???")
    sp("Stormterror... is attacking Mondstadt itself! - Amber")
    sp("Kaeya, " + str(character) + ", you've come at the right time. We must... - Amber")
    #different text from game
    sp("Hold up, Amber. Are you perhaps forgetting to introduce us? - Kaeya")
    #------------------------
    sp("Oh... right. This is Kaeya, our Cavalry Captain. - Amber")
    sp("These two are travelers from afar " + str(character) + " and Paimon. - Amber")
    sp("(From afar? Is that all we know of them?) - Kaeya")
    sp("Long story short... - Amber")
    sp("Amber tells Kaeya the whole story...")
    sp("I see. Welcome to Mondstadt — though you haven't arrived at the best of times, I'm afraid. I understand the anguish of being separated from family. I'm not really sure why you're looking for the Anemo God... But everyone has their secrets, right? Haha, relax! I won't press you for more. First and foremost, on behalf of the Knights of Favonius, I would like to extend our thanks to you for your help just now.  - Kaeya")
    sp("1. Well, we couldn't just leave the situation to fester.")
    sp("2. You're welcome! So... Ah... Where's the reward?")
    selection(2)
    if result == 2:
        sp("Ahh... How about a traditional Mondstadt delicacy, Sticky Honey Roast? - Kaeya")
        sp("1. I just heard about that one!")
        selection(1)
    sp("Your fight to defend the city against the dragon just now was witnessed by no small number of citizens. The Acting Grand Master of the Knights of Favonius is also very interested in meeting you, and formally invites you both to our headquarters. - Kaeya")
    sp("You walk to the Knights of Favonious headquarters.")
    sp("This seems to be the Knights of Favonius Headquarters. Let's head in. - Paimon")
    mora += 2400
    xp += 1250
    nxt()

#Knights of favonius
def P17():
    sp("Jean, what's the hurry? I thought we agreed to meet them here. - ???")
    sp("There have been sightings of Stormterror outside the city. Once we meet, we must... - Jean")
    sp("Relax. I'll lend a hand when the time comes. - ???")
    sp("Jean, I've brought them. - Kaeya")
    sp("...")
    sp("...And after it was over, I brought them straight here. - Kaeya")
    sp("Mondstadt welcomes you, windborne travelers. I am Jean, Acting Grand Master of the Knights of Favonius. This is Lisa, our resident Librarian. - Jean")
    sp("Oh! Are you sweeties here to help us out? You're both so adorable! Sadly, the timing is regrettable... Stormterror has caused quite a ruckus in the region since its recent resurgence. Simply put, Mondstadt's elemental sphere and ley lines are now akin to a yarn ball in the paws of a kitten. For a mage, it couldn't get much worse. My skin is one elemental particle away from a full-blown breakout. - Lisa")
    sp("If it weren't for this interference, the Knights of Favonius would have better ways to help you than just putting up missing person posters. We simply ask that you repose in Mondstadt while we help you seek out your sibling. - Jean")
    sp("1. I really should help as well.")
    sp("2. Guess we'll leave it up to you then.")
    
    
def main():
    global story_progress, sound_enabled

    print("1. New Game")
    print("2. Load Game")
    selection(2)

    if result == 2:
        if not load_game():
            print("No save found. Starting new game.")
            Character_Selection()
    else:
        # 🎵 SOUND SETTINGS
        print("Enable sound?")
        print("1. Yes")
        print("2. No")
        selection(2)

        if result == 1:
            sound_enabled = True
        else:
            sound_enabled = False

        Character_Selection()

    # Resume story based on progress
    if story_progress < 1:
        #Opening cutscene
        P1()
    if story_progress < 2:
        #Bird's eye view
        P2()
    if story_progress < 3:
        P3()
    if story_progress < 4:
        #Unexpected power
        P4()
    if story_progress < 5:
        P5()
    if story_progress < 6:
        P6()
    if story_progress < 7:
        #Forest rendezvous
        P7()
    if story_progress < 8:
        P8()
    if story_progress < 9:
        #Wind-riding knight
        P9()
    if story_progress < 10:
        P10()
    if story_progress < 11:
        #Going upon the breeze
        P11()
    if story_progress < 12:
        P12()
    if story_progress < 13:
        #City of freedom
        P13()
    if story_progress < 14:
        P14()
    if story_progress < 15:
        #Dragon Storm
        P15()
    if story_progress < 16:
        P16()
    if story_progress < 17:
        #Knights of Favonius
        P17()
    if story_progress < 18:
        pass
main()
save_game()
#Character_Selection()
#P10()
"""TESTING SAVE JSON
{"character": "Aether", "sibling": "Lumine", "health": 697, "level": 4, "xp": 802, "max_attk": 20, "defense": 20, "elementalParticles": 90, "mora": 5350, "food_inventory": [{"name": "Sweet madame", "amount": 6, "heal": 150}, {"name": "Teyvat fried egg", "amount": 10, "heal": 100}], "inventory": [], "usedElementalSkill": "False", "paimon_trust": 0, "story_progress": 10}"""