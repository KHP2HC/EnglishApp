#!/usr/bin/env python3
"""
Generate 500 IELTS Speaking tests as JSON.
Each test has 3 parts (Introduction, Long Turn, Discussion).
Output: web/public/data/speaking_tests.json
"""

import json
import os
import random

random.seed(42)

OUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "web", "public", "data", "speaking_tests.json"
)

# ── Part 1 topics (Introduction & Interview) ────────────────────────
# Each entry: (topic, [questions])

PART1_TOPICS = [
    ("Hometown", [
        "Let's talk about your hometown. Where is it, and what do you like most about it?",
        "Has your hometown changed much since you were a child?",
        "Would you recommend your hometown as a place to visit? Why or why not?",
        "What is the most interesting place in your hometown?",
        "Do you think you will live there in the future? Why?",
    ]),
    ("Free Time", [
        "What do you enjoy doing in your free time?",
        "Do you prefer spending your free time alone or with others? Why?",
        "Has your free time changed since you were a child?",
        "If you had more free time, what would you do with it?",
        "Do you think people today have enough free time?",
    ]),
    ("Reading", [
        "Do you prefer reading books or watching films? Why?",
        "What kind of books do you enjoy reading?",
        "Do you read electronic books or paper books? Which do you prefer?",
        "Did you read more when you were younger than you do now?",
        "Is there a book you would recommend to everyone?",
    ]),
    ("Food", [
        "What is your favourite type of food?",
        "Do you enjoy cooking? Why or why not?",
        "How often do you eat out at restaurants?",
        "Is there a food from another country you particularly enjoy?",
        "Do you think your diet is healthy? Why or why not?",
    ]),
    ("Travel", [
        "Do you like travelling? Why or why not?",
        "What is the most interesting place you have visited?",
        "Do you prefer travelling alone or with others?",
        "Where would you like to travel in the future?",
        "Has travel become easier in recent years? How?",
    ]),
    ("Music", [
        "What kind of music do you enjoy listening to?",
        "Do you play any musical instruments?",
        "Has your taste in music changed over the years?",
        "Do you prefer listening to live music or recorded music?",
        "Is music an important part of your culture?",
    ]),
    ("Work & Studies", [
        "Are you a student or do you work?",
        "What do you like most about your job or studies?",
        "Is there anything you dislike about your work or studies?",
        "What was your first job?",
        "Would you like to change your job or field of study in the future?",
    ]),
    ("Weather", [
        "What is your favourite type of weather?",
        "Does the weather affect your mood?",
        "What do you do on rainy days?",
        "Is the weather in your country changing?",
        "Would you prefer to live in a hotter or colder climate?",
    ]),
    ("Sports", [
        "Do you enjoy playing or watching sports?",
        "What is the most popular sport in your country?",
        "Did you play sports when you were a child?",
        "Do you think children should do more sport at school?",
        "Have you ever won a sports competition?",
    ]),
    ("Technology", [
        "How often do you use a computer or smartphone?",
        "What is your favourite piece of technology?",
        "Has technology made life easier or more difficult?",
        "Do you think people rely too much on technology?",
        "What technology would you like to see in the future?",
    ]),
    ("Friends", [
        "Do you prefer having a few close friends or many acquaintances?",
        "How did you meet your best friend?",
        "Do you see your friends often?",
        "What do you usually do with your friends?",
        "Is it easy to make new friends as an adult?",
    ]),
    ("Daily Routine", [
        "Is there anything you would like to change about your daily routine?",
        "How do you usually spend your weekends?",
        "Are you a morning person or a night owl?",
        "What is the most important part of your day?",
        "Do you follow the same routine every day?",
    ]),
    ("Animals", [
        "Do you have any pets?",
        "What is your favourite animal and why?",
        "Are there any animals you are afraid of?",
        "Should children learn about animals at school?",
        "How can we protect endangered species?",
    ]),
    ("Shopping", [
        "Do you enjoy shopping? Why or why not?",
        "Do you prefer shopping online or in physical stores?",
        "What was the last thing you bought?",
        "Do you think you are a careful shopper?",
        "Is shopping a popular activity in your country?",
    ]),
    ("Art", [
        "Do you enjoy art? What kind?",
        "Have you ever been to an art gallery or museum?",
        "Do you think art is important in society?",
        "Did you enjoy art classes at school?",
        "Would you like to learn to paint or draw?",
    ]),
    ("Nature", [
        "Do you spend time in nature?",
        "What is your favourite natural landscape?",
        "Is it important for children to spend time outdoors?",
        "How can cities be made greener?",
        "Have you ever been camping or hiking?",
    ]),
    ("Films", [
        "How often do you watch films?",
        "What type of films do you enjoy?",
        "Do you prefer watching films at home or at the cinema?",
        "What was the last film you watched?",
        "Is there a film you would recommend?",
    ]),
    ("Festivals", [
        "What is your favourite festival or holiday?",
        "How do people in your country celebrate New Year?",
        "Are there any traditional festivals in your culture?",
        "Do you think festivals are becoming less important?",
        "What festival would you like to experience in another country?",
    ]),
    ("Health", [
        "Do you try to keep fit and healthy?",
        "What do you do to stay healthy?",
        "Do you think you have a healthy diet?",
        "How important is sleep for you?",
        "What could you do to improve your health?",
    ]),
    ("Languages", [
        "How many languages can you speak?",
        "Why are you learning English?",
        "Do you think it is important to learn foreign languages?",
        "What is the most difficult part of learning a new language?",
        "Would you like to learn another language in the future?",
    ]),
    ("Photography", [
        "Do you enjoy taking photographs?",
        "What kind of things do you like to photograph?",
        "Do you prefer taking photos with a camera or a phone?",
        "How do you store and share your photos?",
        "Do you think photography is an art form?",
    ]),
    ("Social Media", [
        "Do you use social media? Which platforms?",
        "How much time do you spend on social media each day?",
        "Has social media changed the way you communicate?",
        "Do you think social media is addictive? Why?",
        "What are the advantages and disadvantages of social media?",
    ]),
    ("Television", [
        "How much television do you watch?",
        "What kind of programmes do you enjoy?",
        "Do you prefer watching TV alone or with family?",
        "Has streaming changed the way you watch TV?",
        "Do you think there is too much advertising on TV?",
    ]),
    ("Internet", [
        "How often do you use the internet?",
        "What do you usually use the internet for?",
        "Do you think the internet has improved our lives?",
        "Is there anything you dislike about the internet?",
        "How would your life change without the internet?",
    ]),
    ("Hobbies", [
        "What is your favourite hobby?",
        "How did you get interested in your hobby?",
        "How much time do you spend on your hobby?",
        "Are there any hobbies you would like to try?",
        "Do you think hobbies are important? Why?",
    ]),
    ("Home", [
        "Do you live in a house or a flat?",
        "What is your favourite room in your home?",
        "How long have you lived there?",
        "What would you change about your home?",
        "Is your home tidy or messy?",
    ]),
    ("Clothes", [
        "What kind of clothes do you usually wear?",
        "Do you prefer comfortable or fashionable clothes?",
        "How often do you buy new clothes?",
        "Is there a traditional dress in your country?",
        "Do you think clothes are important? Why?",
    ]),
    ("Transport", [
        "How do you usually travel to work or school?",
        "What is the most common form of transport in your city?",
        "Do you ever use public transport?",
        "Is traffic a problem where you live?",
        "Would you like to learn to drive? Why or why not?",
    ]),
    ("Seasons", [
        "Which season do you like best? Why?",
        "What do you usually do in summer?",
        "Does your country have four distinct seasons?",
        "What is the weather like in winter where you live?",
        "Which season is the best for travelling?",
    ]),
    ("Water", [
        "How much water do you drink every day?",
        "Do you prefer tap water or bottled water?",
        "Do you live near the sea or a river?",
        "Do you enjoy water sports like swimming?",
        "Is water pollution a problem in your country?",
    ]),
    ("Colours", [
        "What is your favourite colour?",
        "Do colours affect your mood?",
        "Are there colours you dislike?",
        "Do you wear colourful clothes?",
        "What colours are popular in your culture?",
    ]),
    ("Numbers", [
        "What is your lucky number?",
        "Are there any numbers that are special in your culture?",
        "Do you find maths easy or difficult?",
        "Do you use numbers a lot in your daily life?",
        "Can you remember phone numbers without your phone?",
    ]),
    ("Names", [
        "Does your name have a special meaning?",
        "How did your parents choose your name?",
        "Do people in your country have middle names?",
        "Are there any names that are very common in your country?",
        "Would you ever change your name? Why?",
    ]),
    ("Punctuality", [
        "Are you usually on time?",
        "Do you think being punctual is important?",
        "What do you do if you are running late?",
        "Are people in your country generally punctual?",
        "Has technology helped you be more punctual?",
    ]),
    ("Patience", [
        "Are you a patient person?",
        "What do you do when you have to wait a long time?",
        "Do you think people are less patient nowadays?",
        "Were you more patient as a child?",
        "What makes you lose your patience?",
    ]),
    ("Concentration", [
        "Is it easy for you to concentrate?",
        "What helps you concentrate?",
        "What distracts you the most?",
        "Do you prefer studying in the morning or at night?",
        "Has your ability to concentrate changed over time?",
    ]),
    ("Memory", [
        "Do you have a good memory?",
        "How do you remember important things?",
        "Have you ever forgotten something important?",
        "What is your earliest memory?",
        "Do you think technology has affected our memory?",
    ]),
    ("Time Management", [
        "Do you plan your time carefully?",
        "Do you use a calendar or planner?",
        "Are you good at meeting deadlines?",
        "What would you do with an extra hour each day?",
        "Do you procrastinate? How do you deal with it?",
    ]),
    ("Money", [
        "Do you prefer saving or spending money?",
        "Do you think you are good with money?",
        "Have you ever saved up for something special?",
        "Is cash or card more common where you live?",
        "Do you think money can buy happiness?",
    ]),
    ("Dreams", [
        "Do you remember your dreams?",
        "Do you think dreams have meanings?",
        "Have you ever had a recurring dream?",
        "Do you daydream often?",
        "What was the strangest dream you can remember?",
    ]),
    ("Cooking", [
        "Who usually cooks in your household?",
        "What is the first thing you learned to cook?",
        "Do you follow recipes or improvise?",
        "What is a traditional dish from your country?",
        "Would you like to learn to cook better?",
    ]),
    ("Neighbours", [
        "Do you know your neighbours?",
        "Are you close to your neighbours?",
        "What makes a good neighbour?",
        "Have you ever had a problem with a neighbour?",
        "Do you think it is important to know your neighbours?",
    ]),
    ("School", [
        "What was your favourite subject at school?",
        "Did you enjoy your school days?",
        "Who was your best teacher? Why?",
        "What did you dislike about school?",
        "Would you like to be a teacher? Why?",
    ]),
    ("Future Plans", [
        "What are your plans for the next year?",
        "Where do you see yourself in five years?",
        "Do you make New Year's resolutions?",
        "What is your biggest goal in life?",
        "Do you think it is important to plan ahead?",
    ]),
    ("Happiness", [
        "What makes you happy?",
        "When was the last time you felt really happy?",
        "Do you think happiness is important?",
        "Can money buy happiness?",
        "What do you do to cheer yourself up?",
    ]),
    ("Helping Others", [
        "Do you often help other people?",
        "When was the last time you helped someone?",
        "Do you think people should volunteer more?",
        "Is it easy to ask for help?",
        "Who helps you the most?",
    ]),
    ("Routines & Habits", [
        "Do you have any daily habits?",
        "Is there a habit you would like to break?",
        "Is there a habit you would like to start?",
        "How long does it take to form a habit?",
        "Do you think routines are helpful?",
    ]),
    ("Cities", [
        "Do you live in a city or a town?",
        "What do you like about your city?",
        "What would you change about your city?",
        "Is your city getting bigger or smaller?",
        "Would you prefer to live in a village?",
    ]),
    ("Celebrations", [
        "How do you celebrate your birthday?",
        "What was your best birthday?",
        "How are birthdays celebrated in your country?",
        "Do you prefer giving or receiving gifts?",
        "What is the most important celebration in your culture?",
    ]),
    ("The Ocean", [
        "Do you like going to the beach?",
        "Have you ever travelled by boat?",
        "What do you know about marine life?",
        "Is the ocean important for your country?",
        "Would you like to learn to dive or surf?",
    ]),
]

# ── Part 2 cue cards (Long Turn) ────────────────────────────────────
# Each entry: (topic, prompt_text)

PART2_CUE_CARDS = [
    ("A Memorable Journey",
     "Describe a memorable journey you have taken. You should say:\n• Where you went\n• Who you went with\n• What you did there\n• And explain why it was memorable."),
    ("A Person You Admire",
     "Describe a person you admire. You should say:\n• Who this person is\n• How you know them\n• What they are like\n• And explain why you admire them."),
    ("A Book That Influenced You",
     "Describe a book that has influenced you. You should say:\n• What the book is about\n• When you read it\n• Why you chose to read it\n• And explain how it influenced you."),
    ("A Skill You Want to Learn",
     "Describe a skill you would like to learn. You should say:\n• What the skill is\n• Why you want to learn it\n• How you would learn it\n• And explain how it would benefit you."),
    ("A Difficult Decision",
     "Describe a difficult decision you had to make. You should say:\n• What the decision was\n• When you had to make it\n• Why it was difficult\n• And explain what you decided in the end."),
    ("A Place You Would Like to Visit",
     "Describe a place you would like to visit in the future. You should say:\n• Where it is\n• How you would get there\n• What you would do there\n• And explain why you want to visit it."),
    ("An Important Achievement",
     "Describe an achievement you are proud of. You should say:\n• What it was\n• When it happened\n• How you achieved it\n• And explain why you are proud of it."),
    ("A Gift You Received",
     "Describe a memorable gift you received. You should say:\n• What the gift was\n• Who gave it to you\n• When you received it\n• And explain why it was memorable."),
    ("A Time You Helped Someone",
     "Describe a time when you helped someone. You should say:\n• Who you helped\n• How you helped them\n• Why you helped them\n• And explain how you felt about it."),
    ("A Childhood Memory",
     "Describe a happy memory from your childhood. You should say:\n• What the memory is\n• How old you were\n• Who was with you\n• And explain why it is a happy memory."),
    ("A Restaurant You Enjoy",
     "Describe a restaurant you enjoy going to. You should say:\n• Where it is\n• What type of food it serves\n• Who you go with\n• And explain why you enjoy going there."),
    ("A Piece of Advice",
     "Describe a piece of advice someone gave you. You should say:\n• What the advice was\n• Who gave it to you\n• When you received it\n• And explain how useful it was."),
    ("An Interesting Conversation",
     "Describe an interesting conversation you had. You should say:\n• Who you talked to\n• Where you were\n• What you talked about\n• And explain why it was interesting."),
    ("A Goal You Set",
     "Describe a goal you set for yourself. You should say:\n• What the goal was\n• When you set it\n• What you did to achieve it\n• And explain whether you achieved it."),
    ("A Film That Made You Think",
     "Describe a film that made you think. You should say:\n• What the film was\n• When you watched it\n• What it was about\n• And explain why it made you think."),
    ("A Teacher Who Inspired You",
     "Describe a teacher who inspired you. You should say:\n• Who the teacher was\n• What subject they taught\n• What they were like\n• And explain why they inspired you."),
    ("A City You Would Like to Live In",
     "Describe a city you would like to live in. You should say:\n• Where it is\n• What you know about it\n• What you would do there\n• And explain why you would like to live there."),
    ("A Hobby You Enjoy",
     "Describe a hobby you enjoy. You should say:\n• What the hobby is\n• When you started it\n• How often you do it\n• And explain why you enjoy it."),
    ("A Challenge You Faced",
     "Describe a challenge you faced. You should say:\n• What the challenge was\n• When it happened\n• How you dealt with it\n• And explain what you learned from it."),
    ("An Item You Cannot Live Without",
     "Describe an item you cannot live without. You should say:\n• What it is\n• How long you have had it\n• What you use it for\n• And explain why you cannot live without it."),
    ("A Special Meal",
     "Describe a special meal you had. You should say:\n• When it was\n• Where you had it\n• Who you were with\n• And explain why it was special."),
    ("A Song That Means a Lot to You",
     "Describe a song that means a lot to you. You should say:\n• What the song is\n• When you first heard it\n• What it is about\n• And explain why it means a lot to you."),
    ("A Person Who Made a Difference",
     "Describe a person who made a difference in your life. You should say:\n• Who the person is\n• How you met them\n• What they did\n• And explain how they made a difference."),
    ("A Building You Like",
     "Describe a building you like. You should say:\n• Where it is\n• What it looks like\n• What it is used for\n• And explain why you like it."),
    ("An Event That Changed Your Life",
     "Describe an event that changed your life. You should say:\n• What the event was\n• When it happened\n• What happened as a result\n• And explain how it changed your life."),
    ("A Time You Were Late",
     "Describe a time when you were late for something important. You should say:\n• What you were late for\n• Why you were late\n• What happened as a result\n• And explain how you felt about it."),
    ("A Useful Skill You Learned",
     "Describe a useful skill you have learned. You should say:\n• What the skill is\n• How you learned it\n• How long it took\n• And explain why it is useful."),
    ("An Outdoor Activity You Enjoy",
     "Describe an outdoor activity you enjoy. You should say:\n• What the activity is\n• Where you do it\n• Who you do it with\n• And explain why you enjoy it."),
    ("A Time You Felt Proud",
     "Describe a time when you felt proud of yourself. You should say:\n• What you did\n• When it happened\n• Why you felt proud\n• And explain how it affected you."),
    ("A Person You Would Like to Meet",
     "Describe a famous person you would like to meet. You should say:\n• Who the person is\n• What they are famous for\n• What you would talk about\n• And explain why you would like to meet them."),
    ("A Product You Would Recommend",
     "Describe a product you would recommend to others. You should say:\n• What the product is\n• How long you have used it\n• What you use it for\n• And explain why you would recommend it."),
    ("A Place Where You Feel Relaxed",
     "Describe a place where you feel relaxed. You should say:\n• Where it is\n• How often you go there\n• What you do there\n• And explain why it makes you feel relaxed."),
    ("A Mistake You Learned From",
     "Describe a mistake you made and learned from. You should say:\n• What the mistake was\n• When it happened\n• What the consequences were\n• And explain what you learned from it."),
    ("A Celebration You Enjoyed",
     "Describe a celebration you enjoyed. You should say:\n• What the celebration was\n• Where it took place\n• Who was there\n• And explain why you enjoyed it."),
    ("A Journey That Did Not Go as Planned",
     "Describe a journey that did not go as planned. You should say:\n• Where you were going\n• What went wrong\n• What you did instead\n• And explain how you felt about it."),
    ("A Person Who Is a Good Leader",
     "Describe a person you think is a good leader. You should say:\n• Who the person is\n• What they do\n• How you know them\n• And explain why you think they are a good leader."),
    ("A Time You Received Good News",
     "Describe a time when you received good news. You should say:\n• What the news was\n• Who told you\n• How you reacted\n• And explain why it was good news."),
    ("An App You Use Often",
     "Describe an app you use frequently. You should say:\n• What the app is\n• How long you have used it\n• What you use it for\n• And explain why you find it useful."),
    ("A Family Tradition",
     "Describe a tradition in your family. You should say:\n• What the tradition is\n• When it started\n• How you celebrate it\n• And explain why it is important to your family."),
    ("A Sport You Enjoy Watching or Playing",
     "Describe a sport you enjoy watching or playing. You should say:\n• What the sport is\n• How often you watch or play it\n• Who you do it with\n• And explain why you enjoy it."),
    ("A Time You Tried Something New",
     "Describe a time you tried something new for the first time. You should say:\n• What you tried\n• Why you tried it\n• What happened\n• And explain how you felt about it."),
    ("A Book You Would Recommend",
     "Describe a book you would recommend. You should say:\n• What the book is\n• What it is about\n• When you read it\n• And explain why you would recommend it."),
    ("A Place That Is Important to You",
     "Describe a place that is important to you. You should say:\n• Where it is\n• How often you go there\n• What you do there\n• And explain why it is important to you."),
    ("A Person Who Makes You Laugh",
     "Describe a person who makes you laugh. You should say:\n• Who the person is\n• How you know them\n• What they do\n• And explain why they make you laugh."),
    ("A Decision That Took a Long Time",
     "Describe a decision that took you a long time to make. You should say:\n• What the decision was\n• Why it took so long\n• What helped you decide\n• And explain whether you are happy with the decision."),
    ("A Time You Worked in a Team",
     "Describe a time you worked in a team. You should say:\n• What the team was for\n• Who was in the team\n• What your role was\n• And explain whether the team was successful."),
    ("An Unusual Job You Would Like to Try",
     "Describe an unusual job you would like to try. You should say:\n• What the job is\n• How you heard about it\n• What skills it requires\n• And explain why you would like to try it."),
    ("A Time You Were Surprised",
     "Describe a time when you were surprised. You should say:\n• What surprised you\n• When it happened\n• How you reacted\n• And explain why it was surprising."),
    ("A Garden or Park You Visit",
     "Describe a garden or park you like to visit. You should say:\n• Where it is\n• What it looks like\n• What you do there\n• And explain why you like visiting it."),
    ("A Lesson You Will Never Forget",
     "Describe a lesson you will never forget. You should say:\n• What the lesson was\n• When you learned it\n• How you learned it\n• And explain why you will never forget it."),
]

# ── Part 3 discussion topics ─────────────────────────────────────────
# Each entry: (theme, [questions])

PART3_TOPICS = [
    ("Travel & Culture", [
        "How has travel changed over the past few decades?",
        "Do you think technology has made people more or less connected? Why?",
        "What are the benefits of experiencing different cultures?",
        "Some people say travel broadens the mind. Do you agree or disagree?",
        "How might virtual reality change the way people experience other places?",
    ]),
    ("Education", [
        "What makes a good teacher?",
        "Should education be free for everyone?",
        "How has technology changed education?",
        "Is practical experience more important than theoretical knowledge?",
        "Should schools teach life skills like cooking and budgeting?",
    ]),
    ("Technology & Society", [
        "How has technology affected the way people communicate?",
        "Do you think social media has a positive or negative impact on society?",
        "What are the risks of artificial intelligence?",
        "Should there be limits on technology use for children?",
        "How might technology change the workplace in the future?",
    ]),
    ("Environment", [
        "What are the biggest environmental challenges we face today?",
        "What can individuals do to help the environment?",
        "Should governments do more to protect the environment?",
        "How can we balance economic growth with environmental protection?",
        "Do you think renewable energy will replace fossil fuels completely?",
    ]),
    ("Health & Wellbeing", [
        "Why do you think stress is such a common problem today?",
        "What can governments do to improve public health?",
        "Is mental health given enough attention in your country?",
        "How important is work-life balance?",
        "Should unhealthy food be taxed more heavily?",
    ]),
    ("Work & Career", [
        "How has the nature of work changed in recent years?",
        "Do you think people will work fewer hours in the future?",
        "Is it better to work for a large company or a small one?",
        "How important is job satisfaction compared to salary?",
        "Should people change careers several times in their lives?",
    ]),
    ("Family & Relationships", [
        "How have family structures changed in your country?",
        "Is it better to grow up in a large family or a small one?",
        "What role do grandparents play in modern families?",
        "Has technology brought families closer or pushed them apart?",
        "Should parents be strict or lenient with their children?",
    ]),
    ("Urbanisation", [
        "What are the advantages and disadvantages of living in a big city?",
        "How can cities be made more livable?",
        "Should governments encourage people to move to rural areas?",
        "What problems do rapidly growing cities face?",
        "How might cities look different in 50 years?",
    ]),
    ("Media & News", [
        "How do people get their news today compared to the past?",
        "Is it important to follow the news? Why or why not?",
        "Do you trust the media? Why or why not?",
        "How has social media changed the way news is shared?",
        "Should journalists have more freedom or more regulation?",
    ]),
    ("Globalisation", [
        "What are the main benefits of globalisation?",
        "Has globalisation helped or harmed developing countries?",
        "How has globalisation affected local cultures?",
        "Do you think globalisation will continue or reverse?",
        "Should countries prioritise local or international trade?",
    ]),
    ("Art & Culture", [
        "Why is art important in society?",
        "Should governments fund the arts?",
        "How has digital technology changed the art world?",
        "Do you think traditional arts are disappearing?",
        "Can art change society? How?",
    ]),
    ("Sports & Competition", [
        "Why are sports so popular around the world?",
        "Should professional athletes earn so much money?",
        "How can sports bring people together?",
        "Is too much emphasis placed on winning in sports?",
        "Should extreme sports be banned?",
    ]),
    ("Consumerism", [
        "Has consumerism increased in recent years?",
        "What are the effects of advertising on young people?",
        "Is it better to buy things or experience things?",
        "How can people reduce their consumption?",
        "Do you think online shopping has changed consumer behaviour?",
    ]),
    ("Transport", [
        "What are the best ways to reduce traffic congestion?",
        "Should public transport be free?",
        "How will electric cars change transportation?",
        "Is it better to live in a city with good public transport or one where everyone drives?",
        "What transport problems do rural areas face?",
    ]),
    ("Ageing Population", [
        "What challenges does an ageing population create?",
        "How should society care for elderly people?",
        "Should the retirement age be increased?",
        "What can older people contribute to society?",
        "How might technology help elderly people live independently?",
    ]),
    ("Food & Agriculture", [
        "How has food production changed in recent decades?",
        "Is organic food worth the extra cost?",
        "Should people eat less meat for environmental reasons?",
        "How can we reduce food waste?",
        "What are the risks of genetically modified food?",
    ]),
    ("Crime & Safety", [
        "What causes crime in modern society?",
        "Is prison the best way to deal with criminals?",
        "How can communities be made safer?",
        "Should young offenders be treated differently from adults?",
        "Has technology made crime easier or harder to fight?",
    ]),
    ("Happiness & Success", [
        "What does success mean to you?",
        "Are people in wealthy countries happier?",
        "Can money buy happiness?",
        "How important is having a purpose in life?",
        "What can governments do to improve citizens' happiness?",
    ]),
    ("Communication", [
        "How has communication changed in your lifetime?",
        "Is face-to-face communication still important?",
        "Do you think people communicate better or worse than before?",
        "How can people become better communicators?",
        "Will translation technology replace the need to learn languages?",
    ]),
    ("Innovation & the Future", [
        "What invention has had the biggest impact on humanity?",
        "What technology will change the world in the next 20 years?",
        "Should there be limits on scientific research?",
        "How can society prepare for rapid technological change?",
        "Are you optimistic or pessimistic about the future?",
    ]),
    ("Leadership & Responsibility", [
        "What qualities make a good leader?",
        "Are leaders born or made?",
        "Should leaders be held to higher standards?",
        "How has the role of leadership changed in modern times?",
        "Can anyone become a leader, or does it require special talent?",
    ]),
    ("Tradition vs. Modernity", [
        "Is it important to preserve traditions?",
        "How can societies balance tradition and progress?",
        "Have traditional values been lost in modern life?",
        "Should schools teach traditional skills?",
        "Do you think technology is replacing cultural traditions?",
    ]),
    ("Social Equality", [
        "Is society becoming more equal or less equal?",
        "What can governments do to reduce inequality?",
        "Is education the key to reducing social inequality?",
        "Should men and women always be treated exactly the same?",
        "How can we ensure equal opportunities for everyone?",
    ]),
    ("The Role of Government", [
        "What should the government's main priorities be?",
        "Should governments provide free healthcare?",
        "Is democracy the best form of government?",
        "How can citizens hold their government accountable?",
        "Should governments regulate the internet?",
    ]),
    ("Creativity & Innovation", [
        "Can creativity be taught, or is it innate?",
        "How important is creativity in the workplace?",
        "Has technology made people more or less creative?",
        "Should schools encourage creativity more?",
        "What prevents people from being creative?",
    ]),
    ("Friendship & Social Bonds", [
        "Has the meaning of friendship changed in the digital age?",
        "Is it possible to have real friends online?",
        "What makes a friendship last?",
        "Are friendships more important than family relationships?",
        "How can people maintain friendships over long distances?",
    ]),
    ("The Impact of Advertising", [
        "How does advertising influence our choices?",
        "Should advertising to children be banned?",
        "Is native advertising deceptive?",
        "How has digital advertising changed consumer behaviour?",
        "Should there be stricter rules on advertising?",
    ]),
    ("Work-Life Balance", [
        "Why is work-life balance important?",
        "Has technology made work-life balance harder?",
        "Should the working week be shorter?",
        "How can employers help employees achieve work-life balance?",
        "Is it possible to have a successful career and a happy family life?",
    ]),
    ("Climate Change", [
        "What are the main causes of climate change?",
        "How will climate change affect future generations?",
        "What can ordinary people do about climate change?",
        "Should rich countries pay more to fight climate change?",
        "Do you think we can reverse climate change?",
    ]),
    ("The Role of Art in Education", [
        "Should art and music be compulsory in schools?",
        "How does art education benefit children?",
        "Is STEM more important than the arts in education?",
        "How can schools encourage artistic talent?",
        "Does art education improve academic performance?",
    ]),
    ("Privacy & Security", [
        "Is privacy still possible in the digital age?",
        "Should governments be allowed to monitor communications?",
        "How can people protect their privacy online?",
        "Is the trade-off between security and privacy acceptable?",
        "Should companies be held responsible for data breaches?",
    ]),
    ("The Future of Work", [
        "Will robots replace human workers?",
        "What skills will be most important in the future?",
        "Is the gig economy good or bad for workers?",
        "Should everyone be guaranteed a basic income?",
        "How will remote work change cities?",
    ]),
    ("Tourism & Its Effects", [
        "What are the positive and negative effects of tourism?",
        "Should there be limits on tourist numbers at popular sites?",
        "How can tourism benefit local communities?",
        "Is eco-tourism a solution to overtourism?",
        "How has social media changed travel and tourism?",
    ]),
    ("The Value of Reading", [
        "Is reading still important in the digital age?",
        "Should children read more books?",
        "Has technology changed the way we read?",
        "What can governments do to encourage reading?",
        "Is fiction as valuable as non-fiction?",
    ]),
    ("Mental Health Awareness", [
        "Why is mental health often stigmatised?",
        "How can schools support students' mental health?",
        "Should mental health services be free?",
        "Has social media affected young people's mental health?",
        "What can individuals do to maintain good mental health?",
    ]),
    ("The Influence of Celebrities", [
        "Do celebrities have a responsibility to be role models?",
        "How has celebrity culture changed society?",
        "Is the influence of celebrities mostly positive or negative?",
        "Should celebrities stay out of politics?",
        "How has social media changed celebrity culture?",
    ]),
    ("Sustainable Living", [
        "What does sustainable living mean to you?",
        "Is it possible for everyone to live sustainably?",
        "What can cities do to become more sustainable?",
        "Should products be designed to last longer?",
        "How can individuals reduce their carbon footprint?",
    ]),
    ("The Role of Science", [
        "Should science play a bigger role in policymaking?",
        "Is scientific research adequately funded?",
        "How can we encourage more young people to study science?",
        "Should there be ethical limits on scientific research?",
        "Has science solved more problems than it has created?",
    ]),
    ("Cultural Diversity", [
        "Why is cultural diversity important?",
        "How can societies promote cultural understanding?",
        "Is multiculturalism always beneficial?",
        "Should immigrants adapt to the culture of their new country?",
        "How can schools teach cultural diversity?",
    ]),
    ("The Impact of Streaming", [
        "How has streaming changed the entertainment industry?",
        "Is streaming better than traditional TV?",
        "Has streaming made content more diverse or more homogenised?",
        "Should streaming services be regulated?",
        "How has streaming affected artists and creators?",
    ]),
    ("Ethics & Morality", [
        "Do people need religion to be moral?",
        "Are moral values universal or cultural?",
        "Has technology created new ethical dilemmas?",
        "Should ethics be taught in schools?",
        "Can laws always reflect moral values?",
    ]),
    ("The Importance of Nature", [
        "Why is it important to protect natural habitats?",
        "Should children spend more time in nature?",
        "How does urbanisation affect people's connection to nature?",
        "Can economic development and nature conservation coexist?",
        "What can governments do to protect national parks?",
    ]),
    ("The Future of Education", [
        "Will online learning replace traditional classrooms?",
        "Should exams be the main way to assess students?",
        "How can education systems adapt to a changing world?",
        "Is lifelong learning becoming more important?",
        "Should university education be free?",
    ]),
    ("Social Responsibility", [
        "Do individuals have a responsibility to help their community?",
        "Should wealthy people give more to charity?",
        "Is volunteering important for society?",
        "How can businesses be more socially responsible?",
        "Should social responsibility be taught in schools?",
    ]),
    ("The Role of Sports in Society", [
        "Should governments invest more in sports facilities?",
        "How can sports reduce crime and improve health?",
        "Is too much money spent on professional sports?",
        "Should sports be compulsory in schools?",
        "Can international sports events promote peace?",
    ]),
    ("The Digital Divide", [
        "What is the digital divide, and why does it matter?",
        "How can governments bridge the digital divide?",
        "Is internet access a human right?",
        "How does the digital divide affect education?",
        "Will the digital divide widen or narrow in the future?",
    ]),
    ("The Value of Travel for Young People", [
        "Should young people travel before starting a career?",
        "What can travel teach that books cannot?",
        "Is gap-year travel beneficial or a waste of time?",
        "How can travel broaden a young person's perspective?",
        "Should schools organise more educational trips abroad?",
    ]),
    ("The Impact of AI on Daily Life", [
        "How is artificial intelligence already part of daily life?",
        "Should AI be used in healthcare?",
        "What are the dangers of relying on AI?",
        "Can AI be creative?",
        "How should governments regulate AI?",
    ]),
    ("The Importance of Community", [
        "What makes a strong community?",
        "Has the sense of community declined in modern cities?",
        "How can people build stronger communities?",
        "Should local communities have more power?",
        "Is online community as valuable as in-person community?",
    ]),
    ("The Future of Energy", [
        "Will renewable energy replace fossil fuels?",
        "Should nuclear energy be expanded?",
        "How can individuals reduce their energy consumption?",
        "What role should governments play in energy policy?",
        "Is energy independence important for a country?",
    ]),
]


def _shuffle_deterministic(lst, seed):
    """Return a shuffled copy of *lst* using a deterministic RNG."""
    rng = random.Random(seed)
    copy = list(lst)
    rng.shuffle(copy)
    return copy


def generate_speaking_tests(count=500):
    """Generate *count* unique IELTS speaking tests.

    Uses a round-robin offset scheme so that every test gets a unique
    (Part1, Part2, Part3) combination.  With 50 topics in each pool we
    can produce up to 50 unique combinations per "round"; 10 rounds
    give 500 tests, each with a different topic triplet.
    """
    n1 = len(PART1_TOPICS)     # 50
    n2 = len(PART2_CUE_CARDS)  # 50
    n3 = len(PART3_TOPICS)     # 50

    tests = []
    for i in range(count):
        round_num = i // n1          # 0..9 for 500 tests
        offset = i % n1              # 0..49

        # Each round shifts the Part-2 and Part-3 indices by a different
        # prime offset so no two tests share the same triplet.
        p1_idx = offset
        p2_idx = (offset + round_num * 7) % n2   # step by 7 (coprime to 50)
        p3_idx = (offset + round_num * 13) % n3  # step by 13 (coprime to 50)

        p1 = PART1_TOPICS[p1_idx]
        p2 = PART2_CUE_CARDS[p2_idx]
        p3 = PART3_TOPICS[p3_idx]

        # Deterministic per-test shuffle of questions for variety
        p1_questions = _shuffle_deterministic(p1[1], seed=i)
        p3_questions = _shuffle_deterministic(p3[1], seed=i + 5000)

        tests.append({
            "id": f"ielts-speaking-{i + 1}",
            "title": f"IELTS Speaking Practice Test {i + 1}",
            "parts": [
                {
                    "part": 1,
                    "title": "Part 1 — Introduction & Interview",
                    "instructions": (
                        "The examiner asks general questions about yourself, your home, "
                        "work/studies, and familiar topics. Give full answers (1-2 sentences)."
                    ),
                    "timeMinutes": 4,
                    "questions": p1_questions,
                },
                {
                    "part": 2,
                    "title": f"Part 2 — Long Turn ({p2[0]})",
                    "instructions": (
                        "You have 1 minute to prepare and up to 2 minutes to speak. "
                        "Describe the topic below in detail. The examiner may ask a "
                        "brief follow-up question."
                    ),
                    "timeMinutes": 3,
                    "questions": [p2[1]],
                },
                {
                    "part": 3,
                    "title": f"Part 3 — Discussion ({p3[0]})",
                    "instructions": (
                        "The examiner asks abstract questions related to the Part 2 topic. "
                        "Give extended answers with reasons and examples (3-4 sentences)."
                    ),
                    "timeMinutes": 5,
                    "questions": p3_questions,
                },
            ],
        })
    return tests


def main():
    tests = generate_speaking_tests(500)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(tests, f, indent=2, ensure_ascii=False)
    print(f"✅ Generated {len(tests)} speaking tests → {OUT_PATH}")

    # Verify uniqueness of (p1, p2, p3) triplets
    triplets = set()
    for t in tests:
        key = (t["parts"][0]["title"], t["parts"][1]["title"], t["parts"][2]["title"])
        triplets.add(key)
    print(f"   Unique topic triplets: {len(triplets)} / {len(tests)}")

    # Sample
    sample = tests[0]
    print(f"   Sample: {sample['id']} — {sample['title']}")
    for p in sample["parts"]:
        print(f"     Part {p['part']}: {p['title']} ({len(p['questions'])} questions)")


if __name__ == "__main__":
    main()
