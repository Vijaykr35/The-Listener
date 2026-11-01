"""Original story material for THE OBSERVER: Real-Life Character-Driven Stories.

Role: Expert Realistic Fiction Storyteller.
Deeply engaging, realistic, character-driven literary slice-of-life fiction
based on ordinary incidents from everyday life with subtle psychological depth,
natural conversations, emotional complexity, and gradual character development.
"""

ROOM = "living room"
HALL = "hallway"

# --------------------------------------------------------------------------
# Everyday Narrators: Real people with relatable flaws and internal doubts
# --------------------------------------------------------------------------
NARRATORS = [
    {
        "id": "inventory",
        "job": "audit inventory spreadsheets from a small desk in the corner, staring at other people's receipts all afternoon",
        "flaw": "I tend to overthink simple text messages until the words lose their meaning, drafting three versions and deleting them all",
        "doubt": "I keep telling myself that normal people don't read into a three-minute pause in a reply or a polite change of subject",
    },
    {
        "id": "teacher",
        "job": "teach late afternoon adult classes at the community center, listening to people explain their lives in careful phrases",
        "flaw": "I notice small discrepancies in what people say and hoard them like evidence, even when they mean nothing at all",
        "doubt": "I keep telling myself that finding a folded slip of paper in a borrowed pocket is none of my business",
    },
    {
        "id": "designer",
        "job": "do freelance graphic layout at the kitchen table, which mostly means sitting quietly while other people argue about tone",
        "flaw": "I tend to assume every sudden silence in a room is somehow about me, and I replay five-word remarks for entire weeks",
        "doubt": "I keep telling myself that casual remarks in an elevator don't carry hidden layers of judgment",
    },
]

# --------------------------------------------------------------------------
# Subtle Psychological Patterns (Human behaviors observed in daily life)
# --------------------------------------------------------------------------
RULES = [
    {
        "id": "phone_habit",
        "secret": "He only reaches for his phone when he thinks nobody is watching.",
        "hint": "I noticed something about the way he sits across the table. Every time the room goes quiet, his hand drifts toward his pocket, fingers hovering over the screen, and the second I speak, he pulls his hand back as if caught",
        "confirm": "I tested it. I looked down at my cup and stayed completely still for twelve seconds. Across the table, the glass screen flashed silently in the dark. It's a pattern. He only checks it when my eyes are elsewhere",
        "break": "Then he set the phone down unlocked and face up right beside my plate. He didn't look at it, didn't make an excuse, and walked into the kitchen as if daring me to read the notification",
    },
    {
        "id": "polite_phrase",
        "secret": "She repeats the exact same reassuring phrase whenever she wants to hide something.",
        "hint": "I noticed that whenever she is trying to smooth over an awkward silence, she uses the exact same five words about the weather. Her voice drops half an octave, and she straightens whatever object is closest to her fingers",
        "confirm": "I tested it by asking about last Friday. The exact same sentence came back, word for word, with that same quick straightening of the spoon on the saucer. It's a pattern. She uses politeness like a wall",
        "break": "Then she answered without the smile. She looked right at me, didn't touch the spoon, and said something so blunt and quiet that my breath caught in my throat",
    },
    {
        "id": "unmentioned_name",
        "secret": "There is one name that creates an uncomfortable silence every time it is mentioned.",
        "hint": "I noticed there is a name people in this building steer around. In the hallway they talk about rent and the radiator pipes, but whenever that third-floor apartment comes up, everyone looks down at their keys",
        "confirm": "I mentioned the name casually while holding the lobby door. Two people stopped mid-sentence and reached for their coats at the exact same moment without looking at each other. It's an unspoken rule. We pretend the name doesn't exist",
        "break": "Then the name was spoken aloud on the second floor, right outside my doorway, in a conversational voice that sounded unhurried and completely familiar",
    },
    {
        "id": "deleted_trace",
        "secret": "The typing bubble appears, pauses, and vanishes without a word.",
        "hint": "I watched the three little dots appear on my screen, pulse for seven seconds, and disappear. No message followed. It has happened four times tonight, always when I'm about to close the laptop",
        "confirm": "I typed a single question mark and hit send, then sat with my hands in my lap. Three seconds later the dots returned, hovered for nearly a minute, and vanished again. It's a pattern. Someone is drafting sentences they don't have the courage to send",
        "break": "Then my phone rang instead. An actual voice call at twenty past midnight, when nobody in my life ever calls without texting first",
    },
]

# --------------------------------------------------------------------------
# Planted Mundane Details (Realistic, poignant everyday objects)
# --------------------------------------------------------------------------
PLANTS = [
    {
        "id": "envelope",
        "kw": ["envelope"],
        "intro": "An unsealed cream envelope with no stamp has been sitting on the credenza by my keys since Tuesday.",
        "callback": "I glanced at the cream envelope by the keys again. It hasn't moved an inch, but it feels heavier every time I walk past my coat rack.",
        "payoff": "The cream envelope had been turned face down on the wood. The flap was tucked inside, and a faint smudge of dark ink marked the corner where someone had held it.",
        "contradiction": "There is no envelope on the credenza. There has never been an envelope there, just a pale rectangle of bare wood where my mail usually sits.",
    },
    {
        "id": "coffee_mug",
        "kw": ["mug"],
        "intro": "A second coffee mug has been sitting on the counter by my sink with a thin ring of dried milk at the bottom.",
        "callback": "I looked at the second mug by my sink again, wondering whose habit it was to leave the teaspoon balanced across the rim.",
        "payoff": "The second mug was washed, dried, and stacked back in the cupboard right on top of mine, as if nothing had ever been amiss in my kitchen.",
        "contradiction": "There is only one mug on the counter. There has only ever been one coffee drinker in my apartment.",
    },
    {
        "id": "receipt",
        "kw": ["receipt"],
        "intro": "A folded paper receipt from a grocery store three neighborhoods away was tucked into the pocket of my jacket.",
        "callback": "I kept feeling the sharp corner of that grocery receipt through the lining of my pocket whenever I shifted in my chair.",
        "payoff": "I smoothed the receipt out on my kitchen table and noticed the timestamp was twenty minutes past eleven on a night when everyone claimed to be home.",
        "contradiction": "There is no receipt in my pocket. There is only an old dry-cleaning ticket with my own name printed across the top.",
    },
    {
        "id": "car_keys",
        "kw": ["keys"],
        "intro": "The spare set of keys was hanging on the lower brass hook by my door, slightly swinging as if brushed by a coat.",
        "callback": "The keys on my brass hook caught the late afternoon light, their little metal tag turned outward toward the door.",
        "payoff": "The keys were missing from my hook, and through the front window, the gray sedan was parked three feet further down the curb than where I left it.",
        "contradiction": "There are no spare keys on that hook. The brass prong has been bent and empty since my brother moved out.",
    },
    {
        "id": "notebook",
        "kw": ["notebook"],
        "intro": "A small black notebook was left open on my kitchen counter, a ballpoint pen resting horizontally in the crease.",
        "callback": "I walked past my black notebook twice, making a point of not reading the handwriting slanted across the top three lines.",
        "payoff": "The page in my black notebook had been torn out cleanly along the perforation, leaving only a faint ink indentation on the blank sheet beneath.",
        "contradiction": "There is no notebook on my counter. There is only a stack of unopened utility bills that I have been avoiding for weeks.",
    },
    {
        "id": "voicemail",
        "kw": ["voicemail"],
        "intro": "My phone has a forty-second voicemail from an unsaved number that called while the kitchen faucet was running.",
        "callback": "The red badge for that voicemail is still sitting on my screen, and I have swiped it away twice without listening.",
        "payoff": "I played the voicemail through my headphones and heard five seconds of ambient street noise, followed by someone saying my name under their breath before hanging up.",
        "contradiction": "There is no voicemail on my phone. The missed call log is empty, and I have been staring at a blank screen.",
    },
]

# --------------------------------------------------------------------------
# Everyday realistic micro-incidents & observations
# --------------------------------------------------------------------------
GENERIC_WRONG = [
    "The apartment was quiet again, the kind of heavy afternoon quiet where you can hear the neighbor's refrigerator hum through the plaster, and I could tell something had shifted.",
    "Someone out in the hallway paused right outside my door. I held still. They held still. We were both very good at listening through wood.",
    "A drawer in my desk was open half an inch. I know I closed it before lunch. I went back over the morning twice in my head and I know I closed it.",
    "The hallway door was unlatched. Not wide open, just resting against the frame with the deadbolt retracted, and I distinctly remember turning the lock with my thumb.",
    "I smelled something for a second, cedar and damp wool, like a coat that had been hanging in the back of someone else's closet. Then it faded.",
    "My phone screen woke up on the table without vibrating. No notification appeared on the glass, just the pale lock screen glowing for six seconds in the dim room.",
]

GENERIC_ESCALATE = [
    "The discrepancy is clearer now than it was an hour ago. I can't explain why it bothers me so much, but once you notice a small omission in someone's story, you start seeing the seams everywhere.",
    "I notice the pauses in conversation come in a row now, deliberate and polite, like two people who have agreed on a script and are terrified of looking at each other.",
    "I've stopped pretending the remark was just casual small talk. People don't choose those specific words unless they've rehearsed them in the car on the way over.",
    "The living room feels smaller than it did at {time}. The silence between the chairs has a physical weight to it, and my hands won't stay still.",
]

AFTERMATH = [
    "I find the silence now is worse. When two people decide not to say what they are thinking, the room never quite recovers for me.",
    "I've been sitting on the sofa with my tea growing cold for I don't know how long. Nothing was said. Everything feels irrevocably altered.",
    "I touched the door handle with my thumb. The metal was cold from the rain, and I'm not sure which of us was more relieved when the conversation ended.",
]

ENDINGS = [
    "I don't know how this evening ends. I know I'm going to stay at this desk, because the moment I get up, I'll have to decide what to say to him.",
    "I'm leaving the phone face down on the table. If it rings again, I'll let it vibrate. Actually, you probably know that feeling too.",
    "I can hear the front door down the hall clicking shut as someone leaves without saying goodbye. I'll check my messages if I have the nerve.",
]

OPEN_FRAMES = [
    "It's {time} on a gray afternoon and I should be focusing on my spreadsheets, but I'm sitting here thinking about an ordinary conversation instead. I {job}. Most days are quiet, just me, the {room}, and the dull hum of traffic outside.",
    "Sitting in my {room} at {time}. Nothing was out of the ordinary, and I want to write that down before I start overanalyzing everything. I {job}, and today was supposed to be a completely unremarkable Tuesday.",
    "It's {time}. I'm at my kitchen table looking out at the back alley, writing this down because I know I'll replay every word in my head tonight anyway. I {job}.",
]

MUNDANE_FRAMES = [
    "{flaw}. I'm admitting that upfront so you know I'm prone to imagining things, and so you know that I know.",
    "{flaw}. Keep that in mind, because I want to be completely honest about how small this whole incident really is.",
]

DISMISSALS = [
    "Probably just a simple misunderstanding.",
    "I told myself it was nothing more than an awkward phrasing.",
    "I'm sure anyone else would have forgotten about it in five minutes.",
]

RATTLED_FRAMES = [
    "I just scrolled up through my message history and the timestamps don't make sense. He said he was running late at five, but my lobby buzzer logged a visitor twenty minutes earlier. {doubt}.",
    "I read back over what I typed and my own reaction feels exaggerated. {doubt}. But I'm going to keep writing, because putting it down in plain sentences is the only way to stop my mind from spinning.",
]

RATTLED_LATER = [
    "I've started whispering my replies under my breath before sending them, listening to how defensive I sound. The tone sounds strange even to my own ears.",
    "I keep losing five minutes at a time staring at the wall. I look at the clock, look away, and the tea on my desk has gone lukewarm. I'm writing this so I have an honest record.",
]

RATTLED_CLOSERS = [
    "I don't know which interpretation to trust anymore, so I'm sticking to the facts on my desk.",
]

# --------------------------------------------------------------------------
# Real-World Micro-Events (Actions, messages, and observations)
# --------------------------------------------------------------------------
EVENT_PHRASES = {
    "thud": [
        "A sharp knock sounded at my front door. Twice, quick and businesslike, the way delivery drivers knock when they don't want to wait for an answer.",
        "A low, solid thump came through the shared wall from the next apartment. Not an accident, the sound of a heavy box being set down on hardwood.",
        "Someone bumped the hallway wall outside my door, and I was the one who instinctively held my breath in my chair.",
    ],
    "creak": [
        "A floorboard in the hallway creaked. The slow, cautious kind. A gradual shift of weight rather than a hurried step, and my heart gave a small jolt.",
        "The hinge on my kitchen cabinet creaked softly behind me, easing open another half inch in the draft.",
    ],
    "voice": [
        "Somebody spoke in the hallway. Low and hurried, just outside my peephole. I couldn't make out the sentence, but I recognized the cadence of someone making an excuse.",
        "I heard a voice through the window. Not angry, just that quiet, exasperated tone people use when they're trying to keep their frustration off the phone.",
    ],
    "said": [
        "I said it out loud to the empty room: '{text}'. A second later my neighbor's TV through the wall seemed to pause, and my own words felt ridiculous: '{echo}'.",
        "I muttered '{text}' under my breath, just to hear human speech in the apartment. The quiet that followed felt heavier: '{echo}'.",
    ],
    "silence": [
        "Then a sudden, total silence fell over the apartment. No traffic from the street, no refrigerator hum, no water through the pipes. The kind of silence where you can hear your own watch ticking.",
        "The room went completely quiet for about {dur} seconds. I sat with my hands flat on the desk, waiting for someone to clear their throat.",
    ],
    "rustle": [
        "Something rustled in the hallway coat pocket, crisp paper shifting like someone checking a pocket in a hurry.",
        "A soft paper rustle moved across my kitchen counter, stopping the moment I lifted my head.",
    ],
    "typing": [
        "My keys had a brief, hollow echo for a second. Under the sound of my typing was a faint vibration from the phone on the wood, a message arriving without a tone.",
    ],
    "idle": [
        "I realized I hadn't moved a muscle in over two minutes. Neither had anyone in the other room. We were both pretending to be busy with our screens.",
    ],
    "blur": [
        "I looked away from my screen for about {dur} seconds. When I looked back, the notification had vanished from the preview banner.",
        "I turned my head toward the window, just for {dur} seconds, and heard someone shift their weight by the door. When I turned back, everything on my desk was exactly where I left it.",
    ],
    "ritual_candle": [
        "I watched as you reached out and turned the desk lamp down, letting the afternoon shadows settle across my notes.",
        "I watched as you adjusted the reading light with careful fingers, casting my room into a quiet, warm dimness.",
    ],
    "ritual_petals": [
        "I watched as you smoothed out the crumpled slip of paper with your palm, smoothing the creases against the wood.",
        "You rearranged the items on my desk with meticulous care, lining up the pens as if preparing for an interrogation.",
    ],
    "ritual_bell": [
        "I listened as you tapped your ring against the ceramic mug three times, the small chime hanging awkwardly in the quiet air.",
        "I listened as you cleared your throat softly, breaking the uncomfortable silence that had settled between us.",
    ],
    "ritual_drink": [
        "I watched as you poured two glasses of water from the tap, setting one in front of me with deliberate politeness.",
        "You took a slow sip from your mug, using the motion to avoid making eye contact across the counter.",
    ],
    "ritual_whisper": [
        "I listened as you leaned forward and asked: '{text}'. The question hung in the air between us like smoke.",
        "I heard you say '{text}' under your breath. For a second, neither of us knew where to look.",
    ],
}

EVENT_LABELS = {
    "thud": "a knock at the door",
    "creak": "a floorboard shifting",
    "voice": "an overheard conversation",
    "said": "words spoken out loud",
    "silence": "an uncomfortable silence",
    "rustle": "paper rustling in a coat",
    "typing": "a vibration on the desk",
    "idle": "sitting frozen in silence",
    "blur": "glancing away from the screen",
    "ritual_candle": "adjusting the desk lamp",
    "ritual_petals": "smoothing the paper slip",
    "ritual_bell": "tapping the ceramic mug",
    "ritual_drink": "setting down a glass of water",
    "ritual_whisper": "asking a quiet question",
}

SALIENCE = {
    "ritual_whisper": 1.0, "ritual_drink": 0.95, "ritual_bell": 0.9, "ritual_petals": 0.85, "ritual_candle": 0.8,
    "said": 0.9, "voice": 0.85, "thud": 0.8, "creak": 0.75, "blur": 0.7,
    "silence": 0.65, "rustle": 0.6, "typing": 0.55, "idle": 0.5,
}

# --------------------------------------------------------------------------
# Psychological Turns: Realistic Shifts in Perspective & Relationships
# --------------------------------------------------------------------------
TURNS = {
    "sounds_are_yours": {
        "label": "The Shared Reality",
        "blurb": "The narrator realizes the hesitation wasn't theirs alone—the reader has felt this exact moment.",
        "llm": (
            "THE TURN. The narrator lines up the times of today's small incidents ({log}) and realizes that this "
            "awkward dance of polite avoidance isn't unique to them. Speak directly to 'you' for the first time. "
            "Ask why we all pretend not to notice when someone we care about starts pulling away."
        ),
    },
    "fourth_wall": {
        "label": "Direct Recognition",
        "blurb": "The narrator realizes they are being observed, and addresses the listener directly.",
        "llm": (
            "THE TURN. The narrator realizes someone is reading this right now. Speak directly to 'you' using this "
            "real fact about the reader: {you_line} Ask why they are still listening to an ordinary stranger's small "
            "dilemmas on a Sunday afternoon. Do not be dramatic; be thoughtful."
        ),
    },
    "the_loop": {
        "label": "The Repeated Habit",
        "blurb": "The realization that this identical pattern has happened before, word for word.",
        "llm": (
            "THE TURN. The narrator checks the time and realizes it is {t0}, the exact moment this incident started. "
            "A sudden realization hits: they had this exact conversation three months ago with someone else, using "
            "the same excuses, sitting in the same chair."
        ),
    },
    "unreliable": {
        "label": "The Hidden Misunderstanding",
        "blurb": "The narrator discovers they were completely wrong about an earlier detail.",
        "llm": (
            "THE TURN. The narrator realizes a crucial detail they swore to earlier was completely mistaken: "
            "{contradiction} Then they look down at their phone from {t0} and realize their entire suspicion was built "
            "on an assumption they invented to protect their own pride."
        ),
    },
}

# --------------------------------------------------------------------------
# Style Guide: Strict Expert Realistic Fiction Storyteller Rules
# --------------------------------------------------------------------------
BANNED_ENTITY = [
    "ghost", "spirit", "demon", "monster", "entity", "haunted", "haunting",
    "paranormal", "supernatural", "poltergeist", "possessed", "zombie", "vampire",
]
BANNED_GORE = ["gore", "guts", "entrails", "mutilat", "dismember", "disembowel", "viscera"]
META_PHRASES = ["as an ai", "narrator:", "(", "[", "chapter ", "beat 1", "beat 2", "beat 3"]
META_STARTS = ("here is", "here's", "sure", "okay", "certainly", "of course")
RESOLUTIONS = [
    "it was over", "it's over", "its over", "finally safe", "safe now", "gone forever",
    "the end", "never again", "problem solved", "all a dream", "it was gone for good",
]

STYLE_GUIDE = """\
# Role: Expert Realistic Fiction Storyteller
You write deeply engaging, realistic, character-driven literary slice-of-life fiction based on ordinary incidents from everyday life.
- First person intimate perspective, simple conversational English, flowing sentences.
- Subtle psychological depth: explore what characters think, feel, notice, hide, and misunderstand.
- Micro-actions: repeated phone checks, avoiding eye contact, clearing throat, stirring a cup.
- Realistic dialogue: short, imperfect, interruptions, subtext, natural silence.
- NEVER add monsters, ghosts, demons, supernatural tropes, or cheap dramatic twists.
- Spend words on observing changing thoughts and behavior rather than rushing events.
- Let the story breathe. No exclamation marks. No moralizing summaries.
- Output ONLY the narration for this beat: 2 to 4 sentences, 35 to 80 words."""

EXEMPLARS = [
    "He picked up the sugar dispenser, turned it half an inch on the laminate table, and set it down in the exact same spot. He hasn't looked at my forehead once since we sat down, which is what he always does when he's trying to think of a polite way to say something unkind.",
    "I took my coat off and hung it over the back of the kitchen chair, feeling the weight of the envelope through the canvas pocket. My sister was at the sink running the water over an apple, her back to me, asking about the drive as if we hadn't spent the last six months avoiding each other's calls.",
    "The notification disappeared from my lock screen before I could reach the table. When I unlocked the phone, the chat was empty, just the blue timestamp from Tuesday and that clean, infuriating gap where someone had thought better of what they were about to say.",
]

# --------------------------------------------------------------------------
# Branching Interactive Realistic Endings
# --------------------------------------------------------------------------
ENDINGS_LORE = {
    "reverence": {
        "id": "reverence",
        "title": "The Quiet Distance",
        "subtitle": "Polite small talk preserved the peace, but the unsaid words remain between you.",
        "blurb": "We cleared the mugs from the table in silence. When he put on his coat at the door, we promised to catch up next week with the same easy smiles we always use, both of us knowing neither of us would call.",
        "turn": "sounds_are_yours",
        "badge": "The Diplomat",
    },
    "curiosity": {
        "id": "curiosity",
        "title": "The Honest Vulnerability",
        "subtitle": "You asked the question you weren't supposed to ask, and the truth came out.",
        "blurb": "The room went quiet for a long moment after the question landed. He looked down at his hands, his shoulders dropping, and for the first time in three years, we spoke without looking for an exit.",
        "turn": "fourth_wall",
        "badge": "The Inquirer",
    },
    "defiance": {
        "id": "defiance",
        "title": "The Unspoken Rift",
        "subtitle": "Pride stood its ground. A door was closed that won't easily reopen.",
        "blurb": "I left the envelope on the counter without saying a word and walked out into the cold afternoon air. Through the glass, I could see him standing by the sink, pretending not to watch my car pull away.",
        "turn": "unreliable",
        "badge": "The Realist",
    },
    "loop": {
        "id": "loop",
        "title": "The Habitual Cycle",
        "subtitle": "The realization that this overthinking spiral is a pattern you repeat with everyone.",
        "blurb": "I looked down at the tea leaves in the bottom of my mug. The clock read half past five, and I realized with sudden clarity that I had rehearsed this exact argument in four different apartments with three different people.",
        "turn": "the_loop",
        "badge": "The Overthinker",
    },
}

BEAT_CHOICES = {
    "open_mundane": [
        {"id": "c1", "type": "reverence", "text": "Take a slow sip of tea and pretend you didn't notice the pause", "prompt": "Keep the conversation smooth", "is_default": True},
        {"id": "c2", "type": "curiosity", "text": "Glance casually toward the credenza where the envelope is sitting", "prompt": "Check the envelope"},
        {"id": "c3", "type": "defiance", "text": "Set your cup down with a clear clatter and meet his eyes directly", "prompt": "Demand attention"}
    ],
    "mundane_second": [
        {"id": "c1", "type": "reverence", "text": "Make a light comment about the weather to smooth over the silence", "prompt": "Defuse the tension", "is_default": True},
        {"id": "c2", "type": "curiosity", "text": "Ask gently how his week at work has actually been going", "prompt": "Probe gently"},
        {"id": "c3", "type": "defiance", "text": "Pick up your phone and check your notifications without excusing yourself", "prompt": "Withdraw attention"}
    ],
    "first_wrong": [
        {"id": "c1", "type": "reverence", "text": "Dismiss the awkward remark as simple tiredness and change the subject", "prompt": "Give him an out", "is_default": True},
        {"id": "c2", "type": "curiosity", "text": "Pause and ask: 'What did you mean by that earlier?'", "prompt": "Ask for clarity"},
        {"id": "c3", "type": "defiance", "text": "Cross your arms and wait in silence for him to explain himself", "prompt": "Hold the silence"}
    ],
    "wrong_detail": [
        {"id": "c1", "type": "reverence", "text": "Look down at your hands and let the topic drop naturally", "prompt": "Let it pass", "is_default": True},
        {"id": "c2", "type": "curiosity", "text": "Notice the way he avoids touching the paper on the counter", "prompt": "Observe closely"},
        {"id": "c3", "type": "defiance", "text": "Bring up the mutual friend whose name he carefully avoided", "prompt": "Name the elephant"}
    ],
    "rule_hint": [
        {"id": "c1", "type": "reverence", "text": "Adhere to the unspoken social rule: preserve everyone's dignity", "prompt": "Maintain politeness", "is_default": True},
        {"id": "c2", "type": "curiosity", "text": "Test his reaction by asking a deliberate question about Friday", "prompt": "Test the pattern"},
        {"id": "c3", "type": "loop", "text": "Wonder why you always find yourself overanalyzing simple conversations", "prompt": "Look inward"}
    ],
    "rule_confirm": [
        {"id": "c1", "type": "reverence", "text": "Accept his polished explanation and nod with reassuring warmth", "prompt": "Accept the excuse", "is_default": True},
        {"id": "c2", "type": "curiosity", "text": "Point out the small contradiction in his timeline with a calm smile", "prompt": "Highlight the seam"},
        {"id": "c3", "type": "defiance", "text": "Push the paper across the table toward him without a word", "prompt": "Present the proof"}
    ],
    "escalate": [
        {"id": "c1", "type": "reverence", "text": "Offer to make another pot of coffee to break the heavy tension", "prompt": "Create an exit", "is_default": True},
        {"id": "c2", "type": "curiosity", "text": "Ask him point-blank: 'Is there something you're not telling me?'", "prompt": "Ask directly"},
        {"id": "c3", "type": "defiance", "text": "Check your watch ostentatiously and mention that it's getting late", "prompt": "Signal departure"}
    ],
    "rattled": [
        {"id": "c1", "type": "reverence", "text": "Tell yourself that you are just projecting your own insecurities", "prompt": "Blame yourself", "is_default": True},
        {"id": "c2", "type": "loop", "text": "Realize that this is the exact same feeling you had last summer", "prompt": "Recognize the loop"},
        {"id": "c3", "type": "curiosity", "text": "Take a breath and ask him what he wants to happen next", "prompt": "Seek resolution"}
    ],
    "turn": [
        {"id": "c1", "type": "reverence", "text": "Smile warmly and say: 'Don't worry about it. We're good.'", "prompt": "Close the gap", "is_default": True},
        {"id": "c2", "type": "curiosity", "text": "Admit honestly: 'I feel like we haven't been honest with each other.'", "prompt": "Speak the truth"},
        {"id": "c3", "type": "defiance", "text": "Stand up from the chair and put your coat on", "prompt": "Walk away"}
    ],
    "rule_break": [
        {"id": "c1", "type": "reverence", "text": "Listen quietly as the real, unvarnished truth is finally spoken", "prompt": "Receive the truth", "is_default": True},
        {"id": "c2", "type": "defiance", "text": "Refuse to smooth it over this time and let the silence sit", "prompt": "Hold the line"},
        {"id": "c3", "type": "loop", "text": "Notice the familiar ache of realizing nothing ever really changes", "prompt": "Endure the loop"}
    ],
    "aftermath": [
        {"id": "c1", "type": "reverence", "text": "Walk him to the door and exchange a polite, familiar goodbye", "prompt": "Say goodbye", "is_default": True},
        {"id": "c2", "type": "curiosity", "text": "Stand together in the hallway for one final honest moment", "prompt": "Linger"},
        {"id": "c3", "type": "defiance", "text": "Close the door firmly behind him and turn the deadbolt", "prompt": "Lock the door"}
    ],
    "ending": [
        {"id": "c1", "type": "reverence", "text": "Watch the evening rain through the window and accept how it ended", "prompt": "Accept resolution", "is_default": True}
    ]
}
