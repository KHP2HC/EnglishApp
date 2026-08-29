"""Generate reading_tests.json with ~500 IELTS-style reading tests.

Each test has 3 passages (3 parts), mirroring the IELTS Academic Reading paper.
The generator builds passages from a topic bank and creates varied tests by
rotating through topics and question styles.
"""

import json
import os
import random

SEED_DIR = os.path.dirname(__file__)
OUTPUT = os.path.join(SEED_DIR, "reading_tests.json")

# ---------------------------------------------------------------------------
# Passage bank: each entry is a fully-formed passage with questions.
# ---------------------------------------------------------------------------

PASSAGES = []


def _passage(pid, title, difficulty, paras, questions):
    PASSAGES.append({
        "id": pid,
        "number": 0,  # filled per-test
        "title": title,
        "difficulty": difficulty,
        "instructions": "You should spend about 20 minutes on the questions for this passage.",
        "text": "\n\n".join(paras),
        "questions": questions,
    })


# ===========================================================================
# Topic 1: Renewable energy
# ===========================================================================
_passage(
    "T1",
    "The Global Shift Towards Renewable Energy",
    "B2",
    [
        "A  Renewable energy sources such as wind, solar and hydroelectric power have grown dramatically in importance over the past two decades. Concerns about climate change, combined with falling costs of technology, have pushed governments and businesses to invest heavily in clean energy. In many countries, renewables now generate a significant share of the electricity used by homes and factories.",
        "B  Wind power has been one of the fastest-growing sources. Modern wind turbines are far more efficient than older models, and offshore wind farms can now be built in deep water where winds are stronger and more consistent. Solar panels have also become cheaper and more effective, thanks to advances in materials science. In some regions, the cost of generating electricity from sunlight is now lower than from coal or gas.",
        "C  Despite these advances, renewable energy still faces challenges. The sun does not always shine, and the wind does not always blow, so energy storage is essential. Batteries and other storage systems are improving, but they remain expensive at the scale needed to power entire cities. There are also concerns about the environmental impact of mining the materials used in solar panels and batteries.",
        "D  Governments have responded with a range of policies. Some offer financial incentives for installing solar panels, while others set targets for reducing carbon emissions. International agreements have encouraged cooperation, but progress varies widely between countries. Developing nations, in particular, often struggle to fund the transition to cleaner energy.",
        "E  Looking ahead, most experts agree that the transition to renewable energy will continue. The falling cost of technology and growing public concern about the environment are powerful forces. However, the speed of change will depend on political will, investment in storage and the ability of countries to cooperate on a global scale.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "Renewable energy has become cheaper over the past twenty years.", "answer": "TRUE", "explanation": "Paragraph A mentions falling costs of technology."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "Offshore wind farms can only be built in shallow water.", "answer": "FALSE", "explanation": "Paragraph B says they can be built 'in deep water'."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "Energy storage systems are currently cheap enough to power whole cities.", "answer": "FALSE", "explanation": "Paragraph C says they 'remain expensive at the scale needed'."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "All countries are progressing at the same speed towards clean energy.", "answer": "FALSE", "explanation": "Paragraph D notes 'progress varies widely between countries'."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "What has helped solar panels become more effective?", "options": ["better weather", "advances in materials science", "lower electricity demand", "more wind"], "answer": "advances in materials science", "explanation": "Paragraph B attributes progress to advances in materials science."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "Why is energy storage important for renewables?", "options": ["the sun does not always shine and wind is not constant", "batteries are too cheap", "governments require it", "coal is running out"], "answer": "the sun does not always shine and wind is not constant", "explanation": "Paragraph C explains the intermittency problem."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "Which group often struggles to fund the clean energy transition?", "options": ["large corporations", "developing nations", "offshore companies", "international banks"], "answer": "developing nations", "explanation": "Paragraph D says developing nations struggle to fund the transition."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "Modern wind ______ are far more efficient than older models.", "answer": ["turbines"], "max_words": 1, "explanation": "Paragraph B: 'Modern wind turbines are far more efficient'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "There are concerns about the environmental impact of ______ the materials used in panels and batteries.", "answer": ["mining"], "max_words": 1, "explanation": "Paragraph C mentions mining the materials."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "Some governments offer financial ______ for installing solar panels.", "answer": ["incentives"], "max_words": 1, "explanation": "Paragraph D: 'financial incentives'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "The speed of change will depend on political ______, investment and cooperation.", "answer": ["will"], "max_words": 1, "explanation": "Paragraph E: 'political will'."},
        {"id": "Q12", "number": 12, "type": "tfng", "text": "The passage concludes that the renewable transition is certain to stop.", "answer": "FALSE", "explanation": "Paragraph E says the transition 'will continue'."},
        {"id": "Q13", "number": 13, "type": "mcq", "text": "What is the main idea of the passage?", "options": ["Renewable energy has no problems", "Renewable energy is growing but faces challenges", "Coal is the future of energy", "Wind energy is impossible"], "answer": "Renewable energy is growing but faces challenges", "explanation": "The passage covers growth, benefits and challenges."},
    ],
)

# ===========================================================================
# Topic 2: Sleep and memory
# ===========================================================================
_passage(
    "T2",
    "Sleep and the Consolidation of Memory",
    "C1",
    [
        "A  For decades, researchers have puzzled over why humans and other animals need sleep. Among the many theories, one of the strongest links sleep to memory. The idea is simple: while we sleep, the brain processes the events of the day, strengthening useful memories and discarding unimportant ones.",
        "B  The process begins with the formation of a memory in a part of the brain called the hippocampus. During deep sleep, the brain appears to replay the day's events, transferring these memories to the neocortex for long-term storage. This transfer is thought to be why people who sleep well after studying often remember more than those who stay awake.",
        "C  Not all memories are treated equally. Emotional experiences are usually remembered more vividly than neutral ones, and the brain seems to prioritise them during sleep. This may have an evolutionary explanation: remembering dangerous situations helps an animal survive. However, it also means that negative events can become deeply fixed in the mind.",
        "D  The amount of sleep needed varies with age. Babies and children require far more than adults, reflecting the rapid development of their brains. Among adults, most function best with between seven and nine hours, though a small minority are genuinely able to manage on less.",
        "E  Modern habits pose a threat to this natural process. Screens and artificial light can delay the onset of sleep, while irregular schedules disrupt the timing of the sleep cycle. Sleep researchers increasingly argue that protecting sleep is as important as diet and exercise for maintaining a healthy brain.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "The passage states that sleep helps the brain process the events of the day.", "answer": "TRUE", "explanation": "Paragraph A links sleep to processing daily events."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "The hippocampus is responsible for long-term storage of memories.", "answer": "FALSE", "explanation": "Paragraph B says memories are transferred to the neocortex for long-term storage."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "People who sleep after studying often remember more than those who stay awake.", "answer": "TRUE", "explanation": "Paragraph B states this directly."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "Emotional memories are usually forgotten more quickly than neutral ones.", "answer": "FALSE", "explanation": "Paragraph C says emotional experiences are remembered more vividly."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "Where do memories first form before being transferred?", "options": ["the neocortex", "the hippocampus", "the nervous system", "the spine"], "answer": "the hippocampus", "explanation": "Paragraph B describes the hippocampus as the site of initial formation."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "Why might the brain prioritise emotional memories?", "options": ["they take less energy", "remembering danger helps survival", "they are easier to process", "they are always positive"], "answer": "remembering danger helps survival", "explanation": "Paragraph C offers this evolutionary explanation."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "According to the passage, which group needs the most sleep?", "options": ["adults", "babies and children", "the elderly", "students"], "answer": "babies and children", "explanation": "Paragraph D says babies and children require far more sleep."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "During deep sleep, memories are transferred from the hippocampus to the ______.", "answer": ["neocortex"], "max_words": 1, "explanation": "Paragraph B: 'to the neocortex'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "A small minority of adults are able to manage on ______ than seven hours.", "answer": ["less"], "max_words": 1, "explanation": "Paragraph D: 'manage on less'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "Screens and artificial light can ______ the onset of sleep.", "answer": ["delay"], "max_words": 1, "explanation": "Paragraph E: 'delay the onset of sleep'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "Researchers argue that protecting sleep is as important as diet and ______.", "answer": ["exercise"], "max_words": 1, "explanation": "Paragraph E: 'diet and exercise'."},
        {"id": "Q12", "number": 12, "type": "mcq", "text": "What is the main purpose of paragraph E?", "options": ["to describe how dreams form", "to warn about modern threats to sleep", "to explain the history of sleep research", "to compare adults and children"], "answer": "to warn about modern threats to sleep", "explanation": "Paragraph E focuses on modern habits threatening sleep."},
        {"id": "Q13", "number": 13, "type": "tfng", "text": "The passage claims that irregular schedules help the sleep cycle.", "answer": "FALSE", "explanation": "Paragraph E says irregular schedules disrupt the sleep cycle."},
    ],
)

# ===========================================================================
# Topic 3: Urban farming
# ===========================================================================
_passage(
    "T3",
    "Farming in the City",
    "B2",
    [
        "A  As the world's urban population grows, the question of how to feed city dwellers has become increasingly urgent. One answer that has attracted attention is urban farming: growing food within the city itself. Supporters argue that urban farms reduce the distance food travels, provide fresh produce and create green jobs.",
        "B  Urban farms take many forms. Rooftop gardens use otherwise empty space, while vertical farms grow crops in stacked layers under artificial light. Community gardens allow residents to grow vegetables together, often on unused plots of land. Each approach has its own advantages: rooftop gardens are relatively simple to build, while vertical farms can operate all year round.",
        "C  The benefits extend beyond food. Urban farms can lower the temperature of buildings, reducing the need for air conditioning. They also absorb rainwater, helping to prevent floods, and provide habitats for insects and birds. In deprived areas, community gardens have been shown to improve mental health and bring neighbours together.",
        "D  Nevertheless, urban farming is not a complete solution to food security. The amount of food produced in cities remains small compared with what is needed, and the costs of setting up vertical farms are high. Critics point out that a truly secure food system still depends on rural agriculture and global trade.",
        "E  The future of urban farming will depend on technology and policy. Cheaper LED lighting and improved growing systems could make vertical farms more affordable, while city governments could encourage the trend by providing land and training. Whether urban farming becomes a major source of food or remains a valuable supplement will depend on these choices.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "Urban farming is the complete solution to feeding city populations.", "answer": "FALSE", "explanation": "Paragraph D says it is 'not a complete solution'."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "Vertical farms can operate throughout the year.", "answer": "TRUE", "explanation": "Paragraph B says vertical farms 'can operate all year round'."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "Community gardens can improve mental health.", "answer": "TRUE", "explanation": "Paragraph C states this benefit."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "Urban farms always increase the temperature of buildings.", "answer": "FALSE", "explanation": "Paragraph C says they can lower building temperature."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "Which form of urban farming grows crops in stacked layers?", "options": ["rooftop gardens", "vertical farms", "community gardens", "orchards"], "answer": "vertical farms", "explanation": "Paragraph B describes vertical farms growing crops in stacked layers."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "Which benefit of urban farms is mentioned in paragraph C?", "options": ["increasing traffic", "absorbing rainwater", "raising food prices", "reducing jobs"], "answer": "absorbing rainwater", "explanation": "Paragraph C mentions absorbing rainwater to prevent floods."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "What is a major disadvantage of vertical farms?", "options": ["low food quality", "high setup costs", "lack of artificial light", "they take too much land"], "answer": "high setup costs", "explanation": "Paragraph D says the costs of setting up vertical farms are high."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "Supporters argue that urban farms reduce the ______ food travels.", "answer": ["distance"], "max_words": 1, "explanation": "Paragraph A: 'reduce the distance food travels'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "Community gardens allow residents to grow ______ together.", "answer": ["vegetables"], "max_words": 1, "explanation": "Paragraph B: 'grow vegetables together'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "A secure food system still depends on ______ agriculture and global trade.", "answer": ["rural"], "max_words": 1, "explanation": "Paragraph D: 'rural agriculture'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "Cheaper LED lighting could make vertical farms more ______.", "answer": ["affordable"], "max_words": 1, "explanation": "Paragraph E: 'more affordable'."},
        {"id": "Q12", "number": 12, "type": "mcq", "text": "Which is NOT mentioned as a form of urban farming?", "options": ["rooftop gardens", "vertical farms", "community gardens", "deep-sea fishing"], "answer": "deep-sea fishing", "explanation": "The passage mentions rooftop gardens, vertical farms and community gardens."},
        {"id": "Q13", "number": 13, "type": "tfng", "text": "The passage suggests city governments could help urban farming by providing land and training.", "answer": "TRUE", "explanation": "Paragraph E: 'providing land and training'."},
    ],
)

# ===========================================================================
# Topic 4: The history of maps
# ===========================================================================
_passage(
    "T4",
    "From Papyrus to GPS: A Short History of Maps",
    "C1",
    [
        "A  Maps are among the oldest tools of human civilisation. Before writing was widely used, people drew simple sketches in sand and on animal skins to show where food and water could be found. The earliest surviving maps come from ancient Babylon and Egypt, where they were used to record land ownership and plan journeys.",
        "B  The Greeks made a crucial contribution by applying mathematics to geography. Scholars such as Eratosthenes calculated the size of the Earth with surprising accuracy, and Ptolemy produced a world map that remained influential for more than a thousand years. His system of latitude and longitude, though imperfect, became the basis for navigation.",
        "C  During the age of exploration, maps became tools of power. European nations competed to chart unknown coastlines, and accurate maps were treated as military secrets. The invention of printing allowed maps to be copied and distributed widely, spreading knowledge but also spreading errors, since mistakes were often repeated by later cartographers.",
        "D  The twentieth century transformed map-making completely. Aerial photography made it possible to map large areas quickly, and later satellite images provided an even more detailed view of the Earth. The rise of digital technology created interactive maps that can be updated instantly and combined with other data, such as traffic conditions.",
        "E  Today, most people carry a map in their pocket in the form of a smartphone. Global positioning systems, or GPS, tell users exactly where they are and guide them to their destination. Yet some researchers worry that reliance on digital maps is weakening our natural sense of direction, and that the skill of reading a paper map is being lost.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "The earliest surviving maps come from ancient Babylon and Egypt.", "answer": "TRUE", "explanation": "Paragraph A states this."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "Ptolemy invented the first compass.", "answer": "FALSE", "explanation": "The passage credits Ptolemy with a world map and latitude/longitude, not a compass."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "Accurate maps were sometimes kept secret during the age of exploration.", "answer": "TRUE", "explanation": "Paragraph C says maps were treated as military secrets."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "The invention of printing eliminated all map errors.", "answer": "FALSE", "explanation": "Paragraph C says errors were often repeated."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "Who calculated the size of the Earth?", "options": ["Ptolemy", "Eratosthenes", "Columbus", "Babylonian scribes"], "answer": "Eratosthenes", "explanation": "Paragraph B: 'Eratosthenes calculated the size of the Earth'."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "What did the Greeks apply to geography?", "options": ["art", "mathematics", "religion", "poetry"], "answer": "mathematics", "explanation": "Paragraph B: 'applying mathematics to geography'."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "What concern do researchers have about digital maps?", "options": ["they are too expensive", "they may weaken our sense of direction", "they show too much detail", "they cannot be updated"], "answer": "they may weaken our sense of direction", "explanation": "Paragraph E raises this concern."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "Ptolemy's system of latitude and ______ became the basis for navigation.", "answer": ["longitude"], "max_words": 1, "explanation": "Paragraph B: 'latitude and longitude'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "The invention of ______ allowed maps to be copied and distributed widely.", "answer": ["printing"], "max_words": 1, "explanation": "Paragraph C: 'invention of printing'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "Aerial photography made it possible to map large areas ______.", "answer": ["quickly"], "max_words": 1, "explanation": "Paragraph D: 'quickly'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "Most people now carry a map in the form of a ______.", "answer": ["smartphone"], "max_words": 1, "explanation": "Paragraph E: 'in the form of a smartphone'."},
        {"id": "Q12", "number": 12, "type": "tfng", "text": "The passage says the skill of reading a paper map is increasing.", "answer": "FALSE", "explanation": "Paragraph E says the skill 'is being lost'."},
        {"id": "Q13", "number": 13, "type": "mcq", "text": "What is the best title for the passage?", "options": ["The dangers of GPS", "A short history of maps", "How to read a map", "The geography of Babylon"], "answer": "A short history of maps", "explanation": "The passage surveys the development of maps from ancient times to GPS."},
    ],
)

# ===========================================================================
# Topic 5: Ocean plastics
# ===========================================================================
_passage(
    "T5",
    "The Problem of Plastic in the Ocean",
    "B2",
    [
        "A  Plastic is everywhere in the modern world. It is light, strong and cheap, which makes it useful for packaging, building and medicine. However, the same qualities that make plastic valuable also make it a serious environmental problem. Each year, millions of tonnes of plastic waste enter the ocean, where it can remain for hundreds of years.",
        "B  Once in the ocean, plastic breaks down into smaller pieces called microplastics. These tiny particles are easily swallowed by fish and other sea creatures. Scientists have found microplastics in the stomachs of animals from the deepest trenches to the surface of the open ocean, and even in drinking water.",
        "C  The effects on wildlife are often severe. Sea turtles mistake plastic bags for jellyfish and eat them, while seabirds feed plastic to their chicks. Larger pieces of plastic can trap animals, preventing them from swimming or feeding. Over time, plastic also enters the food chain, and researchers are only beginning to understand the potential risks to human health.",
        "D  Cleaning up the ocean is difficult and expensive. Boats and nets can remove some plastic, but most of it is too small or scattered to collect. For this reason, many experts argue that the most effective solution is to prevent plastic from reaching the sea in the first place. This means reducing the use of single-use plastics, improving recycling and managing waste more carefully on land.",
        "E  Governments, businesses and individuals all have a role to play. Some countries have banned plastic bags, while others have introduced charges for single-use cups. Companies are developing biodegradable materials and designing products that are easier to recycle. Individuals can help by choosing reusable items and disposing of waste responsibly. Although the problem is enormous, small actions, multiplied across millions of people, can make a real difference.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "Plastic is cheap and strong, which makes it useful.", "answer": "TRUE", "explanation": "Paragraph A lists these qualities."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "Microplastics are only found in the deepest parts of the ocean.", "answer": "FALSE", "explanation": "Paragraph B says they are found from the deepest trenches to the surface."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "Sea turtles mistake plastic bags for jellyfish.", "answer": "TRUE", "explanation": "Paragraph C states this."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "Cleaning up the ocean is easy and inexpensive.", "answer": "FALSE", "explanation": "Paragraph D says it is 'difficult and expensive'."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "What are microplastics?", "options": ["large plastic bags", "small pieces of broken-down plastic", "a type of fish", "chemical waste"], "answer": "small pieces of broken-down plastic", "explanation": "Paragraph B defines microplastics."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "Why do many experts argue for prevention rather than cleanup?", "options": ["cleanup is too slow but works perfectly", "most plastic is too small or scattered to collect", "prevention is impossible", "the ocean is too cold"], "answer": "most plastic is too small or scattered to collect", "explanation": "Paragraph D explains the difficulty of collecting small plastic."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "Which action has some countries taken?", "options": ["banned plastic bags", "closed all factories", "stopped all shipping", "removed all fish"], "answer": "banned plastic bags", "explanation": "Paragraph E: 'Some countries have banned plastic bags'."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "Millions of tonnes of plastic waste ______ the ocean each year.", "answer": ["enter"], "max_words": 1, "explanation": "Paragraph A: 'enter the ocean'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "Plastic breaks down into smaller pieces called ______.", "answer": ["microplastics"], "max_words": 1, "explanation": "Paragraph B: 'called microplastics'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "Seabirds sometimes feed plastic to their ______.", "answer": ["chicks"], "max_words": 1, "explanation": "Paragraph C: 'feed plastic to their chicks'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "Companies are developing ______ materials that break down naturally.", "answer": ["biodegradable"], "max_words": 1, "explanation": "Paragraph E: 'biodegradable materials'."},
        {"id": "Q12", "number": 12, "type": "tfng", "text": "The passage states that plastic can remain in the ocean for hundreds of years.", "answer": "TRUE", "explanation": "Paragraph A: 'can remain for hundreds of years'."},
        {"id": "Q13", "number": 13, "type": "mcq", "text": "What is the main message of paragraph E?", "options": ["the problem is impossible to solve", "everyone can contribute to solving the problem", "only governments can act", "plastic should be used more"], "answer": "everyone can contribute to solving the problem", "explanation": "Paragraph E describes actions for governments, businesses and individuals."},
    ],
)

# ===========================================================================
# Topic 6: Learning a second language
# ===========================================================================
_passage(
    "T6",
    "Why Learning a Second Language Matters",
    "B2",
    [
        "A  In an increasingly connected world, the ability to speak more than one language has become a valuable skill. Bilingualism, the ability to use two languages, is the norm in many countries, and millions of people grow up speaking two or more languages from an early age.",
        "B  The benefits of bilingualism are not limited to communication. Studies have shown that people who speak two languages perform better on tasks that require attention and multitasking. The brain must constantly select the right language and suppress the other, a process that appears to strengthen general mental abilities.",
        "C  Learning a second language also opens cultural doors. It allows people to read books, watch films and form friendships that would otherwise be inaccessible. Understanding another language can foster empathy, as it reveals how other people think and express themselves.",
        "D  Despite these benefits, many adults find learning a language difficult. The grammar may be unfamiliar, and pronunciation can be challenging. One common obstacle is lack of confidence: learners are often afraid of making mistakes and therefore avoid speaking. Teachers now emphasise that making errors is a natural part of the process.",
        "E  Technology has made language learning more accessible than ever. Apps, online courses and video calls allow learners to practise with native speakers from anywhere in the world. However, experts agree that there is no substitute for regular practice and genuine interest. A language is not simply learned; it is lived.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "Bilingualism is rare in most countries.", "answer": "FALSE", "explanation": "Paragraph A says it is 'the norm in many countries'."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "Bilingual people may perform better on tasks requiring attention.", "answer": "TRUE", "explanation": "Paragraph B states this."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "Making mistakes is a natural part of learning a language.", "answer": "TRUE", "explanation": "Paragraph D states this."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "Apps can replace all forms of regular practice.", "answer": "FALSE", "explanation": "Paragraph E says there is 'no substitute for regular practice'."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "Which task do bilingual people perform better on?", "options": ["remembering phone numbers", "tasks requiring attention and multitasking", "running long distances", "cooking"], "answer": "tasks requiring attention and multitasking", "explanation": "Paragraph B lists these tasks."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "Why can learning a language foster empathy?", "options": ["it is easy", "it reveals how others think", "it makes people travel", "it increases salary"], "answer": "it reveals how others think", "explanation": "Paragraph C explains this benefit."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "What is one common obstacle for adult learners?", "options": ["too many books", "lack of confidence", "too much practice", "excessive grammar study"], "answer": "lack of confidence", "explanation": "Paragraph D mentions learners being afraid of making mistakes."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "Bilingualism is the ability to use ______ languages.", "answer": ["two"], "max_words": 1, "explanation": "Paragraph A: 'use two languages'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "The brain must constantly select the right language and ______ the other.", "answer": ["suppress"], "max_words": 1, "explanation": "Paragraph B: 'suppress the other'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "Learners are often afraid of making ______.", "answer": ["mistakes"], "max_words": 1, "explanation": "Paragraph D: 'afraid of making mistakes'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "Video calls allow learners to practise with ______ speakers anywhere.", "answer": ["native"], "max_words": 1, "explanation": "Paragraph E: 'with native speakers'."},
        {"id": "Q12", "number": 12, "type": "tfng", "text": "The passage claims that language is simply learned, not lived.", "answer": "FALSE", "explanation": "Paragraph E says 'A language is not simply learned; it is lived.'"},
        {"id": "Q13", "number": 13, "type": "mcq", "text": "What is the writer's attitude towards technology in language learning?", "options": ["it makes learning impossible", "it is helpful but cannot replace practice", "it is dangerous", "it is the only way to learn"], "answer": "it is helpful but cannot replace practice", "explanation": "Paragraph E balances technology's benefits with the need for practice."},
    ],
)

# ===========================================================================
# Topic 7: The psychology of habits
# ===========================================================================
_passage(
    "T7",
    "The Science of Building Good Habits",
    "C1",
    [
        "A  Every person has habits: automatic behaviours that are performed without much conscious thought. Brushing teeth, checking a phone or taking a particular route to work are all examples. Habits are powerful because they free the brain to focus on other things, but they can also be difficult to change.",
        "B  Psychologists describe a habit as a loop with three parts: a cue, a routine and a reward. The cue triggers the behaviour, the routine is the behaviour itself, and the reward is what the brain receives for performing it. Over time, the brain learns to associate the cue with the reward, making the routine automatic.",
        "C  Understanding this loop is the key to changing habits. To break a bad habit, it is often easier to keep the same cue and reward but replace the routine. For example, a person who snacks when stressed could substitute a short walk for the snack. The cue and the feeling of relief remain, but the behaviour changes.",
        "D  Building new habits requires patience. Research suggests that it can take anywhere from a few weeks to several months for a behaviour to become automatic, depending on its complexity. Consistency matters more than intensity: practising a little every day is more effective than practising a lot occasionally.",
        "E  Environment also plays a crucial role. People are far more likely to follow good habits when the environment makes them easy. Keeping fruit visible and sweets hidden, or placing running shoes by the door, are simple strategies that work. By designing surroundings thoughtfully, individuals can make healthy behaviour the default choice.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "Habits are performed without much conscious thought.", "answer": "TRUE", "explanation": "Paragraph A: 'without much conscious thought'."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "A habit loop consists of four parts.", "answer": "FALSE", "explanation": "Paragraph B describes three parts: cue, routine, reward."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "To break a bad habit, it is often useful to keep the cue and reward but change the routine.", "answer": "TRUE", "explanation": "Paragraph C explains this strategy."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "Practising intensely occasionally is more effective than practising a little daily.", "answer": "FALSE", "explanation": "Paragraph D says consistency matters more than intensity."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "Which is the correct order of the habit loop?", "options": ["reward, cue, routine", "cue, routine, reward", "routine, reward, cue", "reward, routine, cue"], "answer": "cue, routine, reward", "explanation": "Paragraph B describes the loop in this order."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "What is the example given for replacing a bad routine?", "options": ["watching TV", "substituting a short walk for a snack", "sleeping longer", "drinking coffee"], "answer": "substituting a short walk for a snack", "explanation": "Paragraph C gives this example."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "How long can it take for a behaviour to become automatic?", "options": ["a few days", "a few weeks to several months", "a few hours", "over a year"], "answer": "a few weeks to several months", "explanation": "Paragraph D: 'anywhere from a few weeks to several months'."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "The cue triggers the ______, which is the behaviour itself.", "answer": ["routine"], "max_words": 1, "explanation": "Paragraph B: 'the routine is the behaviour itself'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "Consistency matters more than ______.", "answer": ["intensity"], "max_words": 1, "explanation": "Paragraph D: 'more than intensity'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "People are more likely to follow good habits when the ______ makes them easy.", "answer": ["environment"], "max_words": 1, "explanation": "Paragraph E: 'environment also plays a crucial role'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "Placing running shoes by the door is a simple ______.", "answer": ["strategy"], "max_words": 1, "explanation": "Paragraph E: 'simple strategies'."},
        {"id": "Q12", "number": 12, "type": "mcq", "text": "What does the passage suggest about the reward in a habit loop?", "options": ["it is always unhealthy", "the brain receives it for performing the routine", "it replaces the cue", "it makes habits impossible to change"], "answer": "the brain receives it for performing the routine", "explanation": "Paragraph B describes the reward's role."},
        {"id": "Q13", "number": 13, "type": "tfng", "text": "The passage says habits can never be changed.", "answer": "FALSE", "explanation": "The passage explains how habits can be changed."},
    ],
)

# ===========================================================================
# Topic 8: The history of tea
# ===========================================================================
_passage(
    "T8",
    "Tea: A Global Story",
    "B2",
    [
        "A  Tea is the second most consumed drink in the world, after water. Its story begins in China, where, according to legend, the emperor Shen Nong discovered the drink around 2700 BCE when leaves from a wild tree fell into his cup of boiling water.",
        "B  For centuries, tea was a luxury enjoyed mainly by the wealthy in China. Over time, its popularity spread to Japan, where it became central to elaborate tea ceremonies. By the seventeenth century, tea had reached Europe through trade routes, and it quickly became fashionable among the upper classes.",
        "C  The demand for tea had enormous consequences. It drove the growth of the British East India Company and helped shape global trade. However, the trade also had a darker side. To balance its purchases of Chinese tea, Britain began exporting opium to China, leading to conflict in the nineteenth century.",
        "D  Today, tea is grown in dozens of countries. India, China and Kenya are among the largest producers. Different regions produce distinctive varieties, from the delicate green teas of Japan to the strong black teas of Assam. The way tea is prepared also varies enormously, from the sweet mint tea of North Africa to the milky tea of Britain.",
        "E  The future of tea faces challenges. Climate change threatens the regions where tea is grown, and younger consumers in some countries are turning to coffee. Yet tea remains deeply woven into the cultures of billions of people, and its story is far from over.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "Tea is the most consumed drink in the world.", "answer": "FALSE", "explanation": "Paragraph A says it is the second most consumed, after water."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "According to legend, tea was discovered in China.", "answer": "TRUE", "explanation": "Paragraph A tells the legend of Shen Nong in China."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "Tea reached Europe in the sixteenth century.", "answer": "FALSE", "explanation": "Paragraph B says the seventeenth century."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "Tea helped shape global trade.", "answer": "TRUE", "explanation": "Paragraph C states this."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "Who discovered tea according to legend?", "options": ["a British trader", "Emperor Shen Nong", "a Japanese monk", "an Indian farmer"], "answer": "Emperor Shen Nong", "explanation": "Paragraph A tells this legend."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "What did Britain export to China to balance tea purchases?", "options": ["silk", "opium", "cotton", "spices"], "answer": "opium", "explanation": "Paragraph C: 'exporting opium to China'."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "Which country is NOT mentioned as a large tea producer?", "options": ["India", "China", "Kenya", "Brazil"], "answer": "Brazil", "explanation": "Paragraph D lists India, China and Kenya."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "Tea is the second most consumed drink after ______.", "answer": ["water"], "max_words": 1, "explanation": "Paragraph A: 'after water'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "In Japan, tea became central to elaborate ______ ceremonies.", "answer": ["tea"], "max_words": 1, "explanation": "Paragraph B: 'elaborate tea ceremonies'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "The demand for tea drove the growth of the British East India ______.", "answer": ["company"], "max_words": 1, "explanation": "Paragraph C: 'British East India Company'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "Climate change threatens the ______ where tea is grown.", "answer": ["regions"], "max_words": 1, "explanation": "Paragraph E: 'the regions where tea is grown'."},
        {"id": "Q12", "number": 12, "type": "tfng", "text": "The passage says younger consumers in some countries are turning to coffee.", "answer": "TRUE", "explanation": "Paragraph E mentions this trend."},
        {"id": "Q13", "number": 13, "type": "mcq", "text": "What is the main idea of the passage?", "options": ["tea is only drunk in Asia", "tea has spread from China to become a global drink", "tea is bad for health", "coffee is replacing tea everywhere"], "answer": "tea has spread from China to become a global drink", "explanation": "The passage traces tea's global journey."},
    ],
)

# ===========================================================================
# Topic 9: Artificial intelligence in medicine
# ===========================================================================
_passage(
    "T9",
    "Artificial Intelligence in Healthcare",
    "C1",
    [
        "A  Artificial intelligence, or AI, is rapidly changing the field of medicine. Computers can now analyse medical images, predict patient outcomes and even suggest treatment plans. These tools do not replace doctors, but they can support them by processing vast amounts of data far more quickly than the human brain.",
        "B  One of the most promising applications is in diagnosis. AI systems trained on thousands of X-rays and scans can detect signs of disease that might be missed by the human eye. In some studies, AI has been shown to identify certain types of cancer as accurately as experienced specialists.",
        "C  AI is also being used to personalise medicine. By analysing a patient's genes and medical history, algorithms can predict which treatments are likely to work best. This approach, known as precision medicine, aims to move away from one-size-fits-all treatments towards care that is tailored to the individual.",
        "D  However, the use of AI in healthcare raises important questions. If an AI system makes a mistake, who is responsible? There are also concerns about privacy, since the data used to train these systems is often highly sensitive. Furthermore, algorithms are only as good as the data they learn from, and biased data can lead to unfair or inaccurate results.",
        "E  Despite these challenges, the direction of travel seems clear. Hospitals are already using AI to prioritise patients, and wearable devices are collecting health data around the clock. The hope is that, used wisely, AI can make healthcare more accurate, more efficient and more accessible for everyone.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "AI tools are designed to replace doctors.", "answer": "FALSE", "explanation": "Paragraph A says they 'do not replace doctors'."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "AI can process vast amounts of data more quickly than humans.", "answer": "TRUE", "explanation": "Paragraph A states this."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "AI has been shown to identify some cancers as accurately as specialists.", "answer": "TRUE", "explanation": "Paragraph B states this."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "Biased data cannot affect AI results.", "answer": "FALSE", "explanation": "Paragraph D says biased data can lead to unfair results."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "What is one promising application of AI in medicine?", "options": ["replacing all nurses", "diagnosis using medical images", "building hospitals", "training doctors"], "answer": "diagnosis using medical images", "explanation": "Paragraph B describes this application."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "What is precision medicine?", "options": ["treatment tailored to the individual", "a type of surgery", "a form of exercise", "a new drug"], "answer": "treatment tailored to the individual", "explanation": "Paragraph C defines precision medicine."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "Which concern about AI is mentioned in paragraph D?", "options": ["cost", "privacy of sensitive data", "lack of computers", "too few doctors"], "answer": "privacy of sensitive data", "explanation": "Paragraph D raises privacy concerns."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "AI systems can detect signs of disease that might be ______ by the human eye.", "answer": ["missed"], "max_words": 1, "explanation": "Paragraph B: 'might be missed'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "Precision medicine aims to move away from one-size-fits-all ______.", "answer": ["treatments"], "max_words": 1, "explanation": "Paragraph C: 'away from one-size-fits-all treatments'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "Algorithms are only as good as the ______ they learn from.", "answer": ["data"], "max_words": 1, "explanation": "Paragraph D: 'only as good as the data'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "Wearable ______ are collecting health data around the clock.", "answer": ["devices"], "max_words": 1, "explanation": "Paragraph E: 'wearable devices'."},
        {"id": "Q12", "number": 12, "type": "mcq", "text": "What is the writer's overall attitude towards AI in healthcare?", "options": ["it should be banned", "it is helpful if used wisely", "it is already perfect", "it has no value"], "answer": "it is helpful if used wisely", "explanation": "Paragraph E expresses cautious optimism."},
        {"id": "Q13", "number": 13, "type": "tfng", "text": "The passage says hospitals are already using AI to prioritise patients.", "answer": "TRUE", "explanation": "Paragraph E states this."},
    ],
)

# ===========================================================================
# Topic 10: Coral reefs
# ===========================================================================
_passage(
    "T10",
    "The Fragile World of Coral Reefs",
    "B2",
    [
        "A  Coral reefs are among the most diverse ecosystems on Earth. Although they cover less than one percent of the ocean floor, they support roughly a quarter of all marine species. Reefs also protect coastlines from storms and provide income for millions of people through fishing and tourism.",
        "B  A coral reef is built by tiny animals called polyps. These creatures secrete a hard skeleton of calcium carbonate, and over many generations, these skeletons accumulate to form the structure of the reef. Most corals also live in partnership with microscopic algae that provide them with food through photosynthesis.",
        "C  Reefs are under severe threat. Rising water temperatures cause corals to expel the algae living in their tissues, turning them white. This process, known as bleaching, can kill corals if the water remains too warm for too long. Ocean acidification, caused by the absorption of carbon dioxide, also weakens coral skeletons.",
        "D  Human activities add to the pressure. Overfishing removes species that keep the reef balanced, while pollution from agriculture and industry smothers corals with nutrients and sediment. Coastal development can physically destroy reef habitats, and careless tourism causes further damage.",
        "E  Efforts to protect reefs are growing. Marine protected areas give damaged reefs time to recover, and scientists are experimenting with techniques to grow more resilient corals in nurseries. Some projects even transplant corals to damaged reefs. However, the long-term survival of coral reefs will depend on reducing global carbon emissions.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "Coral reefs cover more than one percent of the ocean floor.", "answer": "FALSE", "explanation": "Paragraph A says less than one percent."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "Reefs support about a quarter of all marine species.", "answer": "TRUE", "explanation": "Paragraph A states this."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "Corals are built by tiny animals called polyps.", "answer": "TRUE", "explanation": "Paragraph B states this."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "Bleaching always kills corals.", "answer": "FALSE", "explanation": "Paragraph C says it can kill them if water stays too warm."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "What do the algae in coral tissues provide?", "options": ["shelter", "food through photosynthesis", "calcium carbonate", "protection from storms"], "answer": "food through photosynthesis", "explanation": "Paragraph B describes the partnership."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "What is coral bleaching?", "options": ["corals turning white after expelling algae", "corals growing larger", "corals moving to deeper water", "corals changing colour permanently"], "answer": "corals turning white after expelling algae", "explanation": "Paragraph C describes the bleaching process."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "How does ocean acidification affect corals?", "options": ["it helps them grow", "it weakens their skeletons", "it makes them more colourful", "it attracts more fish"], "answer": "it weakens their skeletons", "explanation": "Paragraph C states this."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "Reefs protect coastlines from ______.", "answer": ["storms"], "max_words": 1, "explanation": "Paragraph A: 'protect coastlines from storms'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "Polyps secrete a hard skeleton of calcium ______.", "answer": ["carbonate"], "max_words": 1, "explanation": "Paragraph B: 'calcium carbonate'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "Rising water temperatures cause corals to ______ the algae.", "answer": ["expel"], "max_words": 1, "explanation": "Paragraph C: 'expel the algae'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "Marine protected areas give damaged reefs time to ______.", "answer": ["recover"], "max_words": 1, "explanation": "Paragraph E: 'time to recover'."},
        {"id": "Q12", "number": 12, "type": "tfng", "text": "Scientists are growing more resilient corals in nurseries.", "answer": "TRUE", "explanation": "Paragraph E states this."},
        {"id": "Q13", "number": 13, "type": "mcq", "text": "What will the long-term survival of reefs ultimately depend on?", "options": ["more tourism", "reducing global carbon emissions", "building artificial reefs", "removing all fish"], "answer": "reducing global carbon emissions", "explanation": "Paragraph E concludes with this."},
    ],
)

# ===========================================================================
# Topic 11: The future of work
# ===========================================================================
_passage(
    "T11",
    "Remote Work and the Changing Workplace",
    "B2",
    [
        "A  The way people work has changed dramatically in recent years. Advances in technology, together with global events, have made remote work common in many industries. Employees who once travelled to an office every day now collaborate with colleagues across the world from their homes.",
        "B  The advantages of remote work are clear to many. Workers save time and money by avoiding long commutes, and many report greater flexibility and job satisfaction. Companies can also benefit by hiring talent from anywhere, rather than being limited to those who live near an office.",
        "C  However, remote work is not without difficulties. Some employees struggle with loneliness and find it hard to separate work from personal life. Managers face the challenge of keeping teams motivated and ensuring that communication remains effective when people are not physically together.",
        "D  The transition to remote work has not been equal. People in jobs that require physical presence, such as healthcare, retail and construction, have not been able to work from home. There are also concerns that those who work remotely may be overlooked for promotions, since they are less visible to senior staff.",
        "E  Most experts believe that the future will be hybrid, with some days spent in the office and others at home. This model offers flexibility while preserving the social connections that develop in shared spaces. For it to succeed, companies will need to invest in new tools, rethink management practices and ensure that remote workers are treated fairly.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "Remote work is common in many industries.", "answer": "TRUE", "explanation": "Paragraph A states this."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "Remote workers never save money.", "answer": "FALSE", "explanation": "Paragraph B says workers save time and money."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "Some remote workers struggle with loneliness.", "answer": "TRUE", "explanation": "Paragraph C mentions this."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "All workers have been able to work from home equally.", "answer": "FALSE", "explanation": "Paragraph D says healthcare, retail and construction workers could not."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "Which is a benefit of remote work for companies?", "options": ["lower productivity", "hiring talent from anywhere", "fewer customers", "shorter working hours"], "answer": "hiring talent from anywhere", "explanation": "Paragraph B lists this benefit."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "What challenge do managers face with remote teams?", "options": ["too much supervision", "keeping teams motivated", "finding office space", "training new staff"], "answer": "keeping teams motivated", "explanation": "Paragraph C mentions this challenge."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "Why might remote workers be overlooked for promotions?", "options": ["they work too hard", "they are less visible to senior staff", "they lack skills", "they refuse to communicate"], "answer": "they are less visible to senior staff", "explanation": "Paragraph D raises this concern."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "Workers save time and money by avoiding long ______.", "answer": ["commutes"], "max_words": 1, "explanation": "Paragraph B: 'avoiding long commutes'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "Some employees find it hard to separate work from ______ life.", "answer": ["personal"], "max_words": 1, "explanation": "Paragraph C: 'work from personal life'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "Jobs that require physical ______ have not been able to work from home.", "answer": ["presence"], "max_words": 1, "explanation": "Paragraph D: 'require physical presence'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "Most experts believe the future will be ______.", "answer": ["hybrid"], "max_words": 1, "explanation": "Paragraph E: 'the future will be hybrid'."},
        {"id": "Q12", "number": 12, "type": "mcq", "text": "What will companies need for a successful hybrid model?", "options": ["fewer workers", "new tools and new management practices", "larger offices", "longer meetings"], "answer": "new tools and new management practices", "explanation": "Paragraph E lists these needs."},
        {"id": "Q13", "number": 13, "type": "tfng", "text": "The passage believes hybrid work offers both flexibility and social connection.", "answer": "TRUE", "explanation": "Paragraph E states this."},
    ],
)

# ===========================================================================
# Topic 12: Bees and pollination
# ===========================================================================
_passage(
    "T12",
    "The Critical Role of Bees",
    "C1",
    [
        "A  Bees are often seen as simple insects, but their role in the natural world is extraordinary. As they move from flower to flower collecting nectar, they carry pollen from one plant to another. This process, known as pollination, is essential for the reproduction of around three-quarters of the world's flowering plants.",
        "B  The economic value of pollination is enormous. Many of the crops we rely on for food, including apples, almonds and coffee, depend on bees and other pollinators. Without them, harvests would shrink dramatically and food prices would rise. It has been estimated that pollinators contribute hundreds of billions of dollars to the global economy each year.",
        "C  Bee populations, however, are in decline. The causes include the loss of natural habitats, the widespread use of pesticides and the spread of diseases and parasites. Climate change also plays a part, altering the timing of flowering and disrupting the relationship between bees and the plants they depend on.",
        "D  Scientists are working to understand these threats and find solutions. Some are breeding bees that are more resistant to disease, while others are studying how landscapes can be managed to provide better habitats. Farmers are being encouraged to plant wildflower strips and reduce the use of harmful chemicals.",
        "E  The decline of bees is a reminder of how closely human wellbeing is linked to the health of the natural world. Protecting pollinators is not merely an environmental issue; it is also an economic and social necessity. If bees disappear, the consequences would be felt at every dinner table.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "Pollination is essential for around three-quarters of flowering plants.", "answer": "TRUE", "explanation": "Paragraph A states this."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "Coffee production does not depend on pollinators.", "answer": "FALSE", "explanation": "Paragraph B lists coffee as depending on bees."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "Bee populations are increasing worldwide.", "answer": "FALSE", "explanation": "Paragraph C says populations are in decline."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "Climate change disrupts the relationship between bees and plants.", "answer": "TRUE", "explanation": "Paragraph C states this."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "What is pollination?", "options": ["the process of making honey", "carrying pollen from one plant to another", "the growth of flowers", "the collection of nectar"], "answer": "carrying pollen from one plant to another", "explanation": "Paragraph A defines pollination."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "Which is NOT mentioned as a cause of bee decline?", "options": ["loss of habitats", "pesticides", "diseases and parasites", "too many flowers"], "answer": "too many flowers", "explanation": "Paragraph C lists habitat loss, pesticides and disease."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "How are farmers being encouraged to help bees?", "options": ["planting wildflower strips", "using more pesticides", "removing hedges", "importing foreign bees"], "answer": "planting wildflower strips", "explanation": "Paragraph D describes this encouragement."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "Bees carry ______ from one plant to another.", "answer": ["pollen"], "max_words": 1, "explanation": "Paragraph A: 'carry pollen'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "Pollinators contribute hundreds of billions of dollars to the global ______.", "answer": ["economy"], "max_words": 1, "explanation": "Paragraph B: 'global economy'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "Scientists are breeding bees that are more ______ to disease.", "answer": ["resistant"], "max_words": 1, "explanation": "Paragraph D: 'more resistant to disease'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "Protecting pollinators is an economic and ______ necessity.", "answer": ["social"], "max_words": 1, "explanation": "Paragraph E: 'economic and social necessity'."},
        {"id": "Q12", "number": 12, "type": "mcq", "text": "What is the main message of the passage?", "options": ["bees are dangerous", "protecting pollinators is essential", "bees only matter for honey", "insects have no value"], "answer": "protecting pollinators is essential", "explanation": "The passage stresses the importance of bees."},
        {"id": "Q13", "number": 13, "type": "tfng", "text": "The passage claims the decline of bees would have no effect on food prices.", "answer": "FALSE", "explanation": "Paragraph B says food prices would rise."},
    ],
)

# ===========================================================================
# Topic 13: Libraries in the digital age
# ===========================================================================
_passage(
    "T13",
    "Libraries in the Digital Age",
    "B2",
    [
        "A  For centuries, libraries have been places where people gather to read, study and learn. Their shelves hold books, newspapers and maps that record human knowledge. Yet in an age when almost any information can be found online, the role of the library is being questioned.",
        "B  Some people argue that libraries are no longer necessary. If a book can be downloaded in seconds, why travel to a building to borrow a paper copy? Supporters of this view point to falling visitor numbers in some countries and the closure of branches as evidence that libraries are losing relevance.",
        "C  However, many believe that libraries are more important than ever. Beyond lending books, modern libraries offer free internet access, computer classes and quiet study spaces. They provide a refuge for people who cannot afford technology at home, helping to narrow the digital divide.",
        "D  Libraries are also evolving as community centres. They host reading groups, children's activities and events that bring people together. In many towns, the library is one of the few public spaces where anyone can enter without spending money, making it a vital part of social life.",
        "E  The future of libraries will depend on how they adapt. Some have already transformed themselves into digital hubs, offering e-books and online resources alongside traditional services. Rather than disappearing, libraries seem likely to change, continuing their mission of making knowledge accessible to all.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "Libraries have been places for reading and learning for centuries.", "answer": "TRUE", "explanation": "Paragraph A states this."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "Visitor numbers in libraries are rising in every country.", "answer": "FALSE", "explanation": "Paragraph B mentions falling visitor numbers in some countries."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "Libraries help narrow the digital divide.", "answer": "TRUE", "explanation": "Paragraph C states this."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "Libraries always charge money for entry.", "answer": "FALSE", "explanation": "Paragraph D says anyone can enter without spending money."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "What is one argument that libraries are no longer necessary?", "options": ["books can be downloaded quickly", "libraries are too big", "reading is unpopular", "computers are expensive"], "answer": "books can be downloaded quickly", "explanation": "Paragraph B presents this argument."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "Which service do modern libraries offer beyond lending books?", "options": ["free internet access", "public transport", "medical care", "food markets"], "answer": "free internet access", "explanation": "Paragraph C lists this service."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "What does the passage say about libraries as community centres?", "options": ["they only store books", "they host events that bring people together", "they are always empty", "they sell books"], "answer": "they host events that bring people together", "explanation": "Paragraph D describes this role."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "Libraries provide a ______ for people who cannot afford technology.", "answer": ["refuge"], "max_words": 1, "explanation": "Paragraph C: 'provide a refuge'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "Some libraries have transformed themselves into digital ______.", "answer": ["hubs"], "max_words": 1, "explanation": "Paragraph E: 'digital hubs'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "Libraries continue their mission of making ______ accessible to all.", "answer": ["knowledge"], "max_words": 1, "explanation": "Paragraph E: 'making knowledge accessible'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "In many towns, the library is one of the few public ______ where anyone can enter freely.", "answer": ["spaces"], "max_words": 1, "explanation": "Paragraph D: 'public spaces'."},
        {"id": "Q12", "number": 12, "type": "tfng", "text": "The passage predicts libraries will disappear completely.", "answer": "FALSE", "explanation": "Paragraph E says they seem likely to change, not disappear."},
        {"id": "Q13", "number": 13, "type": "mcq", "text": "What is the writer's attitude towards libraries?", "options": ["they are useless", "they are evolving and remain valuable", "they should be closed", "they are only for children"], "answer": "they are evolving and remain valuable", "explanation": "The passage presents libraries as adapting and continuing their mission."},
    ],
)

# ===========================================================================
# Topic 14: Mars exploration
# ===========================================================================
_passage(
    "T14",
    "The Quest to Explore Mars",
    "C1",
    [
        "A  Of all the planets in the solar system, Mars has captured the human imagination most strongly. Its red surface, visible even from Earth, and its similarity in some ways to our own planet have made it the focus of intense scientific study and ambitious plans for exploration.",
        "B  Robotic missions have revealed a great deal about Mars. Orbiters have mapped its surface in detail, while rovers have analysed rocks and soil, finding evidence that liquid water once flowed across the planet. These discoveries have raised the possibility that Mars may once have supported microbial life.",
        "C  The question of sending humans to Mars is far more challenging. The journey takes many months, and astronauts would face dangers including radiation, low gravity and the difficulty of producing food and water. The cost of such missions is enormous, and the technology needed to keep people alive on Mars is still being developed.",
        "D  Despite these obstacles, interest in crewed missions has grown. Several space agencies and private companies have announced plans to visit Mars, with some aiming to establish permanent bases. Proponents argue that exploring Mars would drive technological innovation and inspire future generations, just as the Moon landings did.",
        "E  Critics question whether the enormous expense is justified while problems on Earth remain unsolved. They argue that the resources spent on Mars missions could be used to tackle climate change, poverty and disease. The debate is unlikely to be resolved soon, but the dream of reaching Mars continues to push the boundaries of what is possible.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "Mars has captured the human imagination more strongly than any other planet.", "answer": "TRUE", "explanation": "Paragraph A says 'Of all the planets... Mars has captured the human imagination most strongly'."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "Orbiters have found evidence that water once flowed on Mars.", "answer": "TRUE", "explanation": "Paragraph B says liquid water once flowed across the planet."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "The journey to Mars takes only a few days.", "answer": "FALSE", "explanation": "Paragraph C says it takes many months."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "Some private companies plan to establish bases on Mars.", "answer": "TRUE", "explanation": "Paragraph D states this."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "What have rovers analysed on Mars?", "options": ["weather patterns", "rocks and soil", "oceans", "mountain ranges"], "answer": "rocks and soil", "explanation": "Paragraph B: 'analysed rocks and soil'."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "Which danger do astronauts face on Mars missions?", "options": ["too much oxygen", "radiation", "excessive gravity", "heavy rainfall"], "answer": "radiation", "explanation": "Paragraph C lists radiation as a danger."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "What do proponents argue exploring Mars would do?", "options": ["solve all Earth's problems", "drive technological innovation", "replace space stations", "reduce costs"], "answer": "drive technological innovation", "explanation": "Paragraph D says it would drive technological innovation."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "Mars is visible from Earth because of its red ______.", "answer": ["surface"], "max_words": 1, "explanation": "Paragraph A: 'Its red surface, visible even from Earth'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "Orbiters have mapped the surface of Mars in ______.", "answer": ["detail"], "max_words": 1, "explanation": "Paragraph B: 'mapped its surface in detail'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "Astronauts would face the difficulty of producing food and ______.", "answer": ["water"], "max_words": 1, "explanation": "Paragraph C: 'producing food and water'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "Critics argue the resources could be used to tackle climate change, poverty and ______.", "answer": ["disease"], "max_words": 1, "explanation": "Paragraph E: 'climate change, poverty and disease'."},
        {"id": "Q12", "number": 12, "type": "mcq", "text": "Why do critics question Mars missions?", "options": ["Mars is too far", "the expense could be used for Earth's problems", "robots are unnecessary", "space is not interesting"], "answer": "the expense could be used for Earth's problems", "explanation": "Paragraph E presents this argument."},
        {"id": "Q13", "number": 13, "type": "tfng", "text": "The passage says the debate about Mars missions is likely to be resolved soon.", "answer": "FALSE", "explanation": "Paragraph E says the debate is 'unlikely to be resolved soon'."},
    ],
)

# ===========================================================================
# Topic 15: Nutrition and diet trends
# ===========================================================================
_passage(
    "T15",
    "Fashionable Diets and the Science of Nutrition",
    "B2",
    [
        "A  Every few years, a new diet becomes fashionable. Low-fat diets gave way to low-carbohydrate diets, and these have been followed by intermittent fasting and plant-based eating. Each new trend promises better health and weight loss, but separating useful advice from fashion is not always easy.",
        "B  The basic science of nutrition, however, has not changed as quickly. A healthy diet is one that provides the right balance of carbohydrates, proteins, fats, vitamins and minerals. Most nutritionists agree that eating a wide variety of whole foods, including vegetables, fruits, whole grains and lean proteins, is the most reliable approach.",
        "C  Some popular diets are supported by genuine evidence. Diets that reduce processed foods and added sugar are associated with lower risks of heart disease and diabetes. Others, however, are based on very limited research or on studies involving only small numbers of people, and their long-term effects remain unknown.",
        "D  The food industry has responded to diet trends by creating products to match them. Supermarkets now stock gluten-free, sugar-free and high-protein versions of common foods. While some of these products are useful, others are expensive and offer little health benefit, making it important for consumers to read labels carefully.",
        "E  Experts advise a cautious approach. Before adopting a new diet, people should consider whether it is sustainable, affordable and supported by reliable evidence. The best diet, many conclude, is not necessarily the most fashionable one, but the one that can be maintained over a lifetime.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "The basic science of nutrition changes as quickly as diet trends.", "answer": "FALSE", "explanation": "Paragraph B says it 'has not changed as quickly'."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "Eating a wide variety of whole foods is recommended by most nutritionists.", "answer": "TRUE", "explanation": "Paragraph B states this."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "All popular diets are supported by strong evidence.", "answer": "FALSE", "explanation": "Paragraph C says some are based on limited research."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "The food industry has ignored diet trends.", "answer": "FALSE", "explanation": "Paragraph D says it has responded by creating products."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "Which diet is mentioned as a recent trend?", "options": ["high-sugar diets", "intermittent fasting", "all-meat diets", "raw water diets"], "answer": "intermittent fasting", "explanation": "Paragraph A lists intermittent fasting."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "What do nutritionists agree on?", "options": ["all fats are harmful", "a wide variety of whole foods is best", "protein should be avoided", "sugar is essential"], "answer": "a wide variety of whole foods is best", "explanation": "Paragraph B states this."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "Why should consumers read labels carefully?", "options": ["some products offer little health benefit", "all labels are wrong", "prices are hidden", "products are dangerous"], "answer": "some products offer little health benefit", "explanation": "Paragraph D explains this."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "Diets that reduce processed foods are associated with lower risks of heart ______ and diabetes.", "answer": ["disease"], "max_words": 1, "explanation": "Paragraph C: 'heart disease and diabetes'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "Supermarkets stock gluten-free, sugar-free and high-______ versions of foods.", "answer": ["protein"], "max_words": 1, "explanation": "Paragraph D: 'high-protein versions'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "People should consider whether a diet is sustainable, affordable and supported by ______ evidence.", "answer": ["reliable"], "max_words": 1, "explanation": "Paragraph E: 'reliable evidence'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "The best diet is the one that can be maintained over a ______.", "answer": ["lifetime"], "max_words": 1, "explanation": "Paragraph E: 'over a lifetime'."},
        {"id": "Q12", "number": 12, "type": "mcq", "text": "What is the writer's advice about new diets?", "options": ["adopt them immediately", "consider sustainability and evidence", "avoid all food", "only follow celebrity advice"], "answer": "consider sustainability and evidence", "explanation": "Paragraph E offers this advice."},
        {"id": "Q13", "number": 13, "type": "tfng", "text": "The passage says gluten-free products are always cheaper.", "answer": "FALSE", "explanation": "Paragraph D says some are expensive."},
    ],
)

# ===========================================================================
# Topic 16: Water scarcity
# ===========================================================================
_passage(
    "T16",
    "Water: The Scarce Resource",
    "C1",
    [
        "A  Water covers more than seventy percent of the Earth's surface, yet only a tiny fraction of it is available for human use. Most of the planet's water is salt water in the oceans, and much of the fresh water is locked in ice caps and glaciers. Access to clean water is therefore one of the defining challenges of the twenty-first century.",
        "B  Agriculture is by far the largest consumer of fresh water. Irrigation accounts for around seventy percent of all water drawn from rivers and underground sources. As the global population grows and diets change, the demand for food, and therefore for water, is expected to rise significantly.",
        "C  Climate change is making the problem worse. Changes in rainfall patterns mean that some regions receive more water than they can use, while others face severe droughts. Rising temperatures increase the rate of evaporation, reducing the amount of water stored in reservoirs and rivers.",
        "D  Technology offers some solutions. Drip irrigation delivers water directly to plant roots, using far less than traditional methods. Desalination plants can turn sea water into drinking water, although they are expensive and consume large amounts of energy. Recycling wastewater for agriculture is another growing practice.",
        "E  Ultimately, managing water wisely will require cooperation between countries that share rivers and underground aquifers. It will also require changes in everyday behaviour, from fixing leaking pipes to using water more efficiently at home. The challenge is enormous, but the cost of inaction would be far greater.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "Most of the Earth's water is available for human use.", "answer": "FALSE", "explanation": "Paragraph A says only a tiny fraction is available."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "Irrigation accounts for about seventy percent of water drawn from sources.", "answer": "TRUE", "explanation": "Paragraph B states this."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "Climate change is making the water problem worse.", "answer": "TRUE", "explanation": "Paragraph C states this."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "Desalination plants are cheap to operate.", "answer": "FALSE", "explanation": "Paragraph D says they are expensive and use large amounts of energy."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "Where is most of the Earth's fresh water?", "options": ["in rivers", "in ice caps and glaciers", "in lakes", "in the soil"], "answer": "in ice caps and glaciers", "explanation": "Paragraph A states this."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "What is the largest consumer of fresh water?", "options": ["industry", "agriculture", "households", "transport"], "answer": "agriculture", "explanation": "Paragraph B says agriculture is the largest consumer."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "How does drip irrigation help?", "options": ["it uses more water", "it delivers water directly to plant roots", "it removes salt", "it cools the soil"], "answer": "it delivers water directly to plant roots", "explanation": "Paragraph D describes drip irrigation."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "Most of the planet's water is ______ water in the oceans.", "answer": ["salt"], "max_words": 1, "explanation": "Paragraph A: 'salt water in the oceans'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "Rising temperatures increase the rate of ______.", "answer": ["evaporation"], "max_words": 1, "explanation": "Paragraph C: 'increase the rate of evaporation'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "Recycling ______ for agriculture is a growing practice.", "answer": ["wastewater"], "max_words": 1, "explanation": "Paragraph D: 'Recycling wastewater'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "Managing water wisely will require cooperation between countries that share rivers and underground ______.", "answer": ["aquifers"], "max_words": 1, "explanation": "Paragraph E: 'underground aquifers'."},
        {"id": "Q12", "number": 12, "type": "mcq", "text": "What is the main idea of the passage?", "options": ["water is unlimited", "access to clean water is a major challenge", "desalination is free", "agriculture uses no water"], "answer": "access to clean water is a major challenge", "explanation": "The passage stresses the scarcity and importance of water."},
        {"id": "Q13", "number": 13, "type": "tfng", "text": "The passage says fixing leaking pipes is part of managing water wisely.", "answer": "TRUE", "explanation": "Paragraph E mentions fixing leaking pipes."},
    ],
)

# ===========================================================================
# Topic 17: The rise of e-commerce
# ===========================================================================
_passage(
    "T17",
    "The Transformation of Shopping",
    "B2",
    [
        "A  Shopping has changed more in the past twenty years than in the previous century. The growth of e-commerce has moved buying and selling online, and companies such as Amazon have become some of the largest retailers in the world. For many consumers, buying goods with a few clicks is now routine.",
        "B  The convenience of online shopping is obvious. Customers can compare prices instantly, read reviews and have products delivered to their door. Small businesses can also reach customers far beyond their local area, while traditional shops face intense competition from their online rivals.",
        "C  However, the rise of e-commerce has consequences that extend beyond convenience. Delivery vehicles add to traffic and pollution, while packaging creates mountains of waste. The closure of town-centre shops has changed the character of high streets and reduced the number of jobs in retail.",
        "D  Consumers are increasingly aware of these costs. Some are choosing to support local shops and buy second-hand goods, while others look for products with less packaging. There has also been a growth in 'click and collect' services, which combine the convenience of online ordering with a visit to a physical store.",
        "E  The future of shopping is likely to be a mixture of online and offline. Technology such as augmented reality may allow customers to 'try on' clothes without leaving home, while data-driven recommendations could make online shopping even more personalised. The challenge will be to enjoy the benefits of e-commerce while limiting its negative effects.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "E-commerce has changed shopping more in twenty years than in the previous century.", "answer": "TRUE", "explanation": "Paragraph A states this."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "Online shopping always results in less packaging waste.", "answer": "FALSE", "explanation": "Paragraph C says packaging creates mountains of waste."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "Small businesses can reach customers beyond their local area online.", "answer": "TRUE", "explanation": "Paragraph B states this."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "The closure of town-centre shops has created jobs.", "answer": "FALSE", "explanation": "Paragraph C says it reduced the number of retail jobs."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "What can customers do online according to paragraph B?", "options": ["compare prices instantly", "cook meals", "drive cars", "plant trees"], "answer": "compare prices instantly", "explanation": "Paragraph B lists this benefit."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "Which is a consequence of e-commerce mentioned in paragraph C?", "options": ["less traffic", "more packaging waste", "lower prices for all", "more town-centre shops"], "answer": "more packaging waste", "explanation": "Paragraph C mentions mountains of packaging waste."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "What is 'click and collect'?", "options": ["a type of advertisement", "combining online ordering with a store visit", "buying only in markets", "a payment method"], "answer": "combining online ordering with a store visit", "explanation": "Paragraph D describes this service."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "Customers can compare prices instantly and read ______.", "answer": ["reviews"], "max_words": 1, "explanation": "Paragraph B: 'read reviews'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "Delivery vehicles add to traffic and ______.", "answer": ["pollution"], "max_words": 1, "explanation": "Paragraph C: 'traffic and pollution'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "Some consumers are choosing to buy ______-hand goods.", "answer": ["second"], "max_words": 1, "explanation": "Paragraph D: 'buy second-hand goods'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "Augmented reality may allow customers to 'try on' clothes without leaving ______.", "answer": ["home"], "max_words": 1, "explanation": "Paragraph E: 'without leaving home'."},
        {"id": "Q12", "number": 12, "type": "tfng", "text": "The passage says the future of shopping will be purely online.", "answer": "FALSE", "explanation": "Paragraph E says it will be a mixture of online and offline."},
        {"id": "Q13", "number": 13, "type": "mcq", "text": "What challenge does the passage identify for the future?", "options": ["enjoying e-commerce while limiting negative effects", "making all shopping offline", "increasing packaging", "removing all shops"], "answer": "enjoying e-commerce while limiting negative effects", "explanation": "Paragraph E identifies this challenge."},
    ],
)

# ===========================================================================
# Topic 18: Volcanoes
# ===========================================================================
_passage(
    "T18",
    "Understanding Volcanoes",
    "C1",
    [
        "A  Volcanoes are openings in the Earth's crust through which molten rock, ash and gases escape from deep below the surface. They are found in regions where tectonic plates meet, as well as in 'hot spots' far from plate boundaries. There are roughly 1,500 active volcanoes on Earth, although only a fraction erupt in any given year.",
        "B  The power of a volcanic eruption depends on several factors. The thickness of the magma, its temperature and the amount of gas it contains all play a role. Fast-moving clouds of hot gas and ash, known as pyroclastic flows, are among the most dangerous effects, racing down slopes at enormous speed and destroying everything in their path.",
        "C  Volcanoes also have positive effects. Volcanic soils are among the most fertile in the world, which is why people continue to farm on the slopes of active volcanoes despite the risks. Eruptions can also create new land, and the gases released during eruptions help form the atmosphere and regulate the climate over long periods.",
        "D  Predicting eruptions is difficult but improving. Scientists monitor earthquakes, changes in the shape of the ground and the gases escaping from vents. When several of these signals change together, an eruption may be near, allowing warnings to be issued and people to be evacuated.",
        "E  Living with volcanoes requires preparation. Communities in volcanic regions develop evacuation plans, and scientists work to map the areas most at risk. While no one can stop an eruption, careful monitoring and planning can save thousands of lives.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "Volcanoes are only found where tectonic plates meet.", "answer": "FALSE", "explanation": "Paragraph A says they are also found in hot spots."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "Pyroclastic flows are slow-moving clouds of gas.", "answer": "FALSE", "explanation": "Paragraph B says they race down slopes at enormous speed."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "Volcanic soils are among the most fertile in the world.", "answer": "TRUE", "explanation": "Paragraph C states this."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "Predicting eruptions is now completely accurate.", "answer": "FALSE", "explanation": "Paragraph D says it is 'difficult but improving'."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "What is a pyroclastic flow?", "options": ["a slow-moving river of lava", "a fast-moving cloud of hot gas and ash", "a wave caused by an earthquake", "a rain of cold water"], "answer": "a fast-moving cloud of hot gas and ash", "explanation": "Paragraph B defines it."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "Why do people farm on the slopes of active volcanoes?", "options": ["the soil is fertile", "the land is free", "it is safer", "volcanoes are beautiful"], "answer": "the soil is fertile", "explanation": "Paragraph C explains this."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "Which signal do scientists monitor to predict eruptions?", "options": ["animal behaviour", "changes in ground shape", "ocean temperature", "wind speed"], "answer": "changes in ground shape", "explanation": "Paragraph D lists changes in the shape of the ground."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "Volcanoes are openings through which molten rock, ash and ______ escape.", "answer": ["gases"], "max_words": 1, "explanation": "Paragraph A: 'ash and gases'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "The power of an eruption depends on the ______ of the magma and the amount of gas.", "answer": ["thickness"], "max_words": 1, "explanation": "Paragraph B: 'thickness of the magma'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "Eruptions can create new ______.", "answer": ["land"], "max_words": 1, "explanation": "Paragraph C: 'create new land'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "Communities in volcanic regions develop evacuation ______.", "answer": ["plans"], "max_words": 1, "explanation": "Paragraph E: 'evacuation plans'."},
        {"id": "Q12", "number": 12, "type": "mcq", "text": "What is the main message of the passage?", "options": ["volcanoes are only dangerous", "monitoring and planning can save lives", "volcanoes have no benefits", "eruptions cannot be studied"], "answer": "monitoring and planning can save lives", "explanation": "Paragraph E concludes with this message."},
        {"id": "Q13", "number": 13, "type": "tfng", "text": "There are about 1,500 active volcanoes on Earth.", "answer": "TRUE", "explanation": "Paragraph A states this."},
    ],
)

# ===========================================================================
# Topic 19: Education technology
# ===========================================================================
_passage(
    "T19",
    "Technology in the Classroom",
    "B2",
    [
        "A  Computers and tablets have become common sights in classrooms around the world. From interactive whiteboards to online learning platforms, technology has changed how lessons are delivered and how students learn. Supporters argue that these tools make education more engaging and accessible.",
        "B  One of the clearest benefits is access to information. Students can research any topic online, watch educational videos and practise skills with interactive software. Online platforms also allow teachers to track progress and provide feedback more efficiently than with paper exercises alone.",
        "C  However, technology in the classroom is not a magic solution. Devices can be distracting, and students may spend more time on games than on learning. There are also concerns about equality: not every family can afford a computer or a reliable internet connection, and this 'digital divide' can widen the gap between rich and poor students.",
        "D  Successful use of technology depends on good teaching. Research suggests that simply providing devices has little effect on results unless teachers are trained to use them well. The most effective classrooms use technology as a tool to support clear goals, rather than as a replacement for skilled instruction.",
        "E  Looking forward, the role of technology in education is likely to grow. Artificial intelligence could personalise learning, adapting lessons to each student's level, while virtual reality could take students on virtual field trips. The challenge will be to use these tools in ways that are fair, effective and genuinely beneficial to learning.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "Technology has changed how lessons are delivered.", "answer": "TRUE", "explanation": "Paragraph A states this."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "Devices are never distracting in the classroom.", "answer": "FALSE", "explanation": "Paragraph C says devices can be distracting."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "Providing devices alone improves student results.", "answer": "FALSE", "explanation": "Paragraph D says this has little effect unless teachers are trained."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "The digital divide can widen the gap between rich and poor students.", "answer": "TRUE", "explanation": "Paragraph C states this."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "What is one benefit of online learning platforms?", "options": ["they replace teachers", "they allow teachers to track progress", "they make all learning free", "they remove homework"], "answer": "they allow teachers to track progress", "explanation": "Paragraph B lists this benefit."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "What does research suggest about providing devices?", "options": ["it is the only thing needed", "it has little effect without teacher training", "it always improves results", "it is harmful"], "answer": "it has little effect without teacher training", "explanation": "Paragraph D states this."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "How could AI personalise learning?", "options": ["by making all students do the same work", "by adapting lessons to each student's level", "by removing tests", "by replacing books"], "answer": "by adapting lessons to each student's level", "explanation": "Paragraph E describes this possibility."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "Students can research any topic online and watch educational ______.", "answer": ["videos"], "max_words": 1, "explanation": "Paragraph B: 'watch educational videos'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "Not every family can afford a computer or a reliable internet ______.", "answer": ["connection"], "max_words": 1, "explanation": "Paragraph C: 'reliable internet connection'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "The most effective classrooms use technology as a ______ to support clear goals.", "answer": ["tool"], "max_words": 1, "explanation": "Paragraph D: 'as a tool'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "Virtual reality could take students on virtual field ______.", "answer": ["trips"], "max_words": 1, "explanation": "Paragraph E: 'virtual field trips'."},
        {"id": "Q12", "number": 12, "type": "mcq", "text": "What is the writer's view on technology in education?", "options": ["it should be banned", "it is useful when used well", "it is always harmful", "it has no value"], "answer": "it is useful when used well", "explanation": "Paragraphs D and E express this balanced view."},
        {"id": "Q13", "number": 13, "type": "tfng", "text": "The passage says virtual reality could replace all teachers.", "answer": "FALSE", "explanation": "The passage says it could take students on virtual field trips, not replace teachers."},
    ],
)

# ===========================================================================
# Topic 20: The history of money
# ===========================================================================
_passage(
    "T20",
    "A Short History of Money",
    "B2",
    [
        "A  Money is one of the oldest inventions of human society, but it has not always taken the form of coins and banknotes. Before money existed, people exchanged goods directly, a system known as barter. This worked well between small groups, but it had a major problem: each person had to find someone who wanted exactly what they had to offer.",
        "B  The solution was the invention of money. The first known coins were made in Lydia, in modern-day Turkey, around 600 BCE. Coins were valuable because they were made of precious metals and carried an official stamp that guaranteed their weight and purity. Over time, paper money appeared, first in China and later in Europe.",
        "C  For most of history, money was linked to gold and silver. Governments promised that their banknotes could be exchanged for a fixed amount of gold, a system known as the gold standard. This made money stable, but it also limited how much money governments could create. Most countries abandoned the gold standard during the twentieth century.",
        "D  Today, most money is not physical at all. The majority of money exists as numbers in computer systems, moved between accounts when people use cards or make online payments. This digital money is fast and convenient, but it also raises new questions about security and privacy.",
        "E  The latest development is cryptocurrency, a form of digital money that is not controlled by any government or bank. Supporters say it offers freedom and lower transaction costs, while critics point out that its value can change wildly and that it is sometimes used for illegal activities. Whatever its future, money will continue to evolve.",
    ],
    [
        {"id": "Q1", "number": 1, "type": "tfng", "text": "Barter was a system of exchanging goods directly.", "answer": "TRUE", "explanation": "Paragraph A defines barter."},
        {"id": "Q2", "number": 2, "type": "tfng", "text": "The first known coins were made in Europe.", "answer": "FALSE", "explanation": "Paragraph B says they were made in Lydia, in modern-day Turkey."},
        {"id": "Q3", "number": 3, "type": "tfng", "text": "Paper money first appeared in China.", "answer": "TRUE", "explanation": "Paragraph B states this."},
        {"id": "Q4", "number": 4, "type": "tfng", "text": "Most countries still use the gold standard.", "answer": "FALSE", "explanation": "Paragraph C says most abandoned it during the twentieth century."},
        {"id": "Q5", "number": 5, "type": "mcq", "text": "What was the main problem with barter?", "options": ["it was too fast", "finding someone who wanted what you had", "coins were rare", "paper was expensive"], "answer": "finding someone who wanted what you had", "explanation": "Paragraph A explains this problem."},
        {"id": "Q6", "number": 6, "type": "mcq", "text": "Why were early coins valuable?", "options": ["they were light", "they were made of precious metals with an official stamp", "they could be folded", "they were made of paper"], "answer": "they were made of precious metals with an official stamp", "explanation": "Paragraph B explains this."},
        {"id": "Q7", "number": 7, "type": "mcq", "text": "What is the gold standard?", "options": ["a system linking money to gold", "a type of coin", "a bank in China", "a digital payment method"], "answer": "a system linking money to gold", "explanation": "Paragraph C defines it."},
        {"id": "Q8", "number": 8, "type": "completion", "text": "The first known coins were made around 600 ______.", "answer": ["BCE"], "max_words": 1, "explanation": "Paragraph B: 'around 600 BCE'."},
        {"id": "Q9", "number": 9, "type": "completion", "text": "Paper money first appeared in China and later in ______.", "answer": ["Europe"], "max_words": 1, "explanation": "Paragraph B: 'later in Europe'."},
        {"id": "Q10", "number": 10, "type": "completion", "text": "Most money today exists as numbers in computer ______.", "answer": ["systems"], "max_words": 1, "explanation": "Paragraph D: 'computer systems'."},
        {"id": "Q11", "number": 11, "type": "completion", "text": "Cryptocurrency is a form of digital money not controlled by any ______ or bank.", "answer": ["government"], "max_words": 1, "explanation": "Paragraph E: 'not controlled by any government'."},
        {"id": "Q12", "number": 12, "type": "mcq", "text": "What is a criticism of cryptocurrency mentioned in the passage?", "options": ["it is too expensive", "its value can change wildly", "it cannot be used online", "it is only used by governments"], "answer": "its value can change wildly", "explanation": "Paragraph E mentions this criticism."},
        {"id": "Q13", "number": 13, "type": "tfng", "text": "The passage says money will stop evolving.", "answer": "FALSE", "explanation": "Paragraph E says 'money will continue to evolve'."},
    ],
)

# ---------------------------------------------------------------------------
# Generator: build 500 tests from the passage bank.
# ---------------------------------------------------------------------------

TEST_TITLES = [
    "IELTS Academic Reading Practice Test",
    "IELTS Reading Mock Test",
    "IELTS Reading Practice Paper",
    "Academic Reading Test",
    "IELTS Reading Full Test",
]


def build_tests(count=500):
    """Generate *count* tests, each combining 3 passages from the bank."""
    tests = []
    n = len(PASSAGES)
    idx = 0
    for t in range(count):
        # Pick 3 distinct passages by rotating through the bank.
        p1 = PASSAGES[idx % n]
        p2 = PASSAGES[(idx + 1) % n]
        p3 = PASSAGES[(idx + 2) % n]
        idx += 3

        # Assign passage numbers and renumber questions.
        passages = []
        qnum = 1
        for pos, base in enumerate([p1, p2, p3], start=1):
            passage = json.loads(json.dumps(base))  # deep copy
            passage["number"] = pos
            questions = []
            for q in passage["questions"]:
                q = json.loads(json.dumps(q))
                q["number"] = qnum
                q["id"] = f"Q{qnum}"
                questions.append(q)
                qnum += 1
            passage["questions"] = questions
            passages.append(passage)

        tests.append({
            "id": f"academic-{t + 1}",
            "title": f"{TEST_TITLES[t % len(TEST_TITLES)]} {t + 1}",
            "time_minutes": 60,
            "passages": passages,
        })
    return tests


def main():
    tests = build_tests(500)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(tests, f, ensure_ascii=False, indent=2)
    total_q = sum(len(p["questions"]) for t in tests for p in t["passages"])
    print(f"Generated {len(tests)} tests with 3 passages each.")
    print(f"Total passages: {len(tests) * 3}")
    print(f"Total questions: {total_q}")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
