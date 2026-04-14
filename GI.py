import time
import textwrap
import random
import json
import threading
import os
import webbrowser
import logging
from flask import Flask
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# =========================
# GLOBAL VARIABLES
# =========================
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
max_attk = 10
defense = 5
mora = 0
story_progress = 0
paimon_trust = 100
sound_enabled = False
bridge_opened = False

# =========================
# 🎧 AUDIO BRIDGE SYSTEM
# =========================


app = Flask(__name__)

# =========================
# 🔊 SFX SYSTEM (voice / effects)
# =========================
audio_event = threading.Event()

current_audio = {
    "url": None,
    "ready": False
}

# =========================
# 🎵 MUSIC SYSTEM (background layer)
# =========================
current_music = {
    "url": None,
    "playing": False,
    "loop": True
}

# =========================
# 🌐 FLASK ROUTES
# =========================

@app.route("/")
def index():
    return """
    <html>
    <body style="background:#111;color:white;text-align:center;padding-top:20vh;font-family:sans-serif;">

        <div id="setup">
            <h2 style="color:#ffd452;">Audio Bridge</h2>
            <button id="startBtn"
                style="padding:15px 40px;font-size:20px;cursor:pointer;background:#4a90e2;color:white;border:none;border-radius:5px;">
                Connect Audio
            </button>
        </div>

        <div id="activeMsg" style="display:none;">
            <h2>🔊 Audio Active</h2>
            <p>Keep this tab open.</p>
        </div>

        <audio id="sfxPlayer"></audio>
        <audio id="musicPlayer"></audio>

        <script>
            const sfxPlayer = document.getElementById('sfxPlayer');
            const musicPlayer = document.getElementById('musicPlayer');

            const startBtn = document.getElementById('startBtn');
            const setup = document.getElementById('setup');
            const activeMsg = document.getElementById('activeMsg');

            startBtn.onclick = () => {
                setup.style.display = 'none';
                activeMsg.style.display = 'block';

                sfxPlayer.play().catch(() => {});
                musicPlayer.play().catch(() => {});

                checkSFX();
                checkMusic();
            };

            // =========================
            // 🔊 SFX LOOP
            // =========================
            async function checkSFX() {
                try {
                    const res = await fetch('/get_next_audio');
                    const data = await res.json();

                    if (data.url) {
                        sfxPlayer.src = data.url;
                        sfxPlayer.play();
                        sfxPlayer.onended = () => fetch('/mark_done');
                    }
                } catch (e) {}

                setTimeout(checkSFX, 300);
            }

            // =========================
            // 🎵 MUSIC LOOP
            // =========================
            async function checkMusic() {
                try {
                    const res = await fetch('/get_music');
                    const data = await res.json();

                    if (data.url) {
                        if (musicPlayer.src !== data.url) {
                            musicPlayer.src = data.url;
                            musicPlayer.loop = data.loop;
                            musicPlayer.play().catch(() => {});
                        }
                    } else {
                        musicPlayer.pause();
                        musicPlayer.src = "";
                    }
                } catch (e) {}

                setTimeout(checkMusic, 1000);
            }
        </script>

    </body>
    </html>
    """


# =========================
# 🔊 SFX ROUTES
# =========================

@app.route("/get_next_audio")
def get_next_audio():
    global current_audio
    if current_audio["ready"] and current_audio["url"]:
        url = current_audio["url"]
        current_audio["ready"] = False
        return json.dumps({"url": url})
    return json.dumps({"url": None})


@app.route("/mark_done")
def mark_done():
    audio_event.set()
    return "ok"


# =========================
# 🎵 MUSIC ROUTE
# =========================

@app.route("/get_music")
def get_music():
    global current_music
    if current_music["playing"] and current_music["url"]:
        return json.dumps({
            "url": current_music["url"],
            "loop": current_music["loop"]
        })
    return json.dumps({"url": None, "loop": False})


# =========================
# 🎧 PYTHON AUDIO FUNCTIONS
# =========================

def play_sound_and_wait(url):
    """Blocking SFX (voice lines / effects)."""
    if not sound_enabled:
        return
    current_audio["url"] = url
    current_audio["ready"] = True
    audio_event.clear()
    audio_event.wait(timeout=60)


def sound(url):
    play_sound_and_wait(url)



# =========================
# 🎵 MUSIC CONTROL API
# =========================

def music(url, loop=True):
    """Start background music (non-blocking)."""
    global current_music
    current_music["url"] = url
    current_music["playing"] = True
    current_music["loop"] = loop


def stop_music():
    """Stop background music."""
    global current_music
    current_music["playing"] = False
    current_music["url"] = None
# =========================
# CORE UTILITIES
# =========================

def w(seconds=0.5):
    """Wait for a brief moment."""
    time.sleep(seconds)

def sp(text, play_url=None, speed=0.03, width=50, wait=1):
    """Prints scrolling text and plays audio if a URL is provided."""
    wrapped_text = textwrap.fill(text, width=width)
    if play_url and sound_enabled:
        threading.Thread(target=play_sound_and_wait, args=(play_url,), daemon=True).start()
    for line in wrapped_text.split("\n"):
        for char in line:
            print(char, end="", flush=True)
            time.sleep(speed)
        print()
    if play_url and sound_enabled:
        audio_event.wait(timeout=60)
    if wait == 1: time.sleep(0.25)
    print()

def selection(options):
    """Handles user input and menus."""
    global result
    while True:
        user_input = input(">> ").strip().lower()
        if user_input == "save": 
            save_game()
            continue
        try:
            result = int(user_input)
            if 1 <= result <= options: return
        except: print("Enter a number.")

def save_game():
    """Placeholder for save logic."""
    print("\n--- GAME SAVED ---")
    print(f"Character: {character} | Level: {level} | Progress: {story_progress}\n")

def lvl_up():
    """Handles leveling up attributes."""
    global xp, level, max_attk, health, defense
    while xp >= 1000:
        level += 1; max_attk += 5; health += 20; defense += 5; xp -= 1000
        print(f"\n✨ LEVEL UP! Level {level} ✨")

def fight(EHP, EDM):
    """The combat engine."""
    global health, enemyHP, elementalParticles, usedElementalSkill, xp
    enemyHP = EHP
    usedElementalSkill = "False"
    while enemyHP > 0 and health > 0:
        print(f"\nHP: {health} | Enemy: {enemyHP} | Particles: {elementalParticles}")
        print("1. Attack | 2. Skill | 3. Burst | 4. Food")
        selection(4)
        if result == 1: 
            dmg = random.randint(max_attk-3, max_attk)
            print(f"You hit for {dmg}!")
            enemyHP -= dmg
        elif result == 2:
            if usedElementalSkill == "False":
                print("Elemental Skill!")
                enemyHP -= (max_attk + 30); elementalParticles += 20; usedElementalSkill = "True"
            else: print("On cooldown!"); continue
        elif result == 3:
            if elementalParticles >= 60:
                print("ELEMENTAL BURST!")
                enemyHP -= (max_attk + 60); elementalParticles -= 60
            else: print("Not enough energy!"); continue
        elif result == 4:
            if not eat_food(): continue
        
        if enemyHP > 0:
            dmg = max(1, random.randint(EDM - (defense * 2), EDM - defense))
            health -= dmg
            print(f"Enemy hit you for {dmg}!")

    if health <= 0:
        print("Defeated..."); health = 100; fight(EHP, EDM)
    else:
        print("Victory!")
        xp += EHP; lvl_up()

def add_food(name, amount, heal):
    """Add items to the food bag."""
    food_inventory.append({"name": name, "amount": amount, "heal": heal})

def eat_food():
    """Healing logic."""
    global health
    if not food_inventory: 
        print("No food!")
        return False
    for i, f in enumerate(food_inventory, 1): print(f"{i}. {f['name']} x{f['amount']}")
    selection(len(food_inventory))
    f = food_inventory[result-1]
    health += f['heal']; f['amount'] -= 1
    if f['amount'] <= 0: food_inventory.remove(f)
    return True

def nxt():
    """Advance story marker."""
    global story_progress
    story_progress += 1

# =========================
# MAIN BOOTSTRAP
# =========================

def main():
    global sound_enabled, character, sibling
    print("--- GENSHIN IMPACT: TEXT ADVENTURE ---")
    print("1. New Game | 2. Load Game")
    selection(2)
    if result == 1:
        print("\nEnable Sound?\n1. Yes | 2. No")
        selection(2)
        if result == 1:
            sound_enabled = True
            webbrowser.open("http://127.0.0.1:5000")
            time.sleep(2)
        
        sp("Pick your character: 1. Aether | 2. Lumine")
        selection(2)
        character = "Aether" if result == 1 else "Lumine"
        sibling = "Lumine" if result == 1 else "Aether"

    # Chapter List for progression
    chapters = [P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11, P12, P13, P14, P15, P16, P17]
    
    for i in range(story_progress, len(chapters)):
        chapters[i]()


def P1():
    global sibling
    music("https://coolpython53.github.io/prologue-assets/wanderer's-trail/music/encounter_with_the_unknown_god")
    sp("So... what you're trying to say is that you fell here... from another world? - Paimon", "https://coolpython53.github.io/prologue-assets/wanderer's-trail/paimon-1.mp3")
    w()
    sp("But when you wanted to leave, and go on to the next world, your path was blocked by some unknown god? - Paimon", "https://coolpython53.github.io/prologue-assets/wanderer's-trail/paimon-2.mp3")
    sound("https://coolpython53.github.io/prologue-assets/wanderer's-trail/paimon-3.mp3")
    sp("Outlanders... Your journey ends here... - Unknown God", "https://coolpython53.github.io/prologue-assets/wanderer's-trail/Asmoday-4.mp3")
    sp("Who're you?!", "https://coolpython53.github.io/prologue-assets/wanderer's-trail/Lumine-5.mp3")
    sp("The sustainer of heavanly principles. The arrogation of mankind ends now. - Unknown god", "https://coolpython53.github.io/prologue-assets/wanderer's-trail/Asmoday-6.mp3")
    if sibling == "Aether":
        sp("You and your sibling battle the god. The god takes away your brother.")
        sp("And just like that, the god took away my brother. Some kind of seal was cast upon me, and I lost my power. So whilst we used to travel from world to world, we are now trapped here. - You", "https://coolpython53.github.io/prologue-assets/wanderer's-trail/Lumine-7.mp3")
        sound("https://coolpython53.github.io/prologue-assets/wanderer's-trail/Lumine-8.mp3")
    elif sibling == "Lumine":
        sp("You and your sibling battle the god. The god takes away your sister.")
        sp("And just like that, the god took away my sister. Some kind of seal was cast upon me, and I lost my power. So while we used to cross to world after world, we are now trapped here. - You", "https://coolpython53.github.io/prologue-assets/wanderer's-trail/Aether-7.mp3")   
        sound("https://coolpython53.github.io/prologue-assets/wanderer's-trail/Aether-8.mp3")
    sp("How many years ago was it? I don't know... But I intend to find out. When I woke, I was all alone... Until I met you two months ago.- You")
    if sibling == "Aether":
        sound("https://coolpython53.github.io/prologue-assets/wanderer's-trail/Lumine-9.mp3")
        sound("https://coolpython53.github.io/prologue-assets/wanderer's-trail/Lumine-10.mp3")
    elif sibling == "Lumine":
        
        pass
    stop_music()
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
if __name__ == "__main__":
    # start Flask FIRST in background thread
    threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False),
        daemon=True
    ).start()

    # run game in MAIN thread (so input() works)
    main()