#!/usr/bin/env python3
"""
Generate 500 IELTS Listening Practice Tests.

Each test follows the official IELTS Listening format:
  - Section 1: Everyday social conversation (10 questions)
  - Section 2: Social context monologue (10 questions)
  - Section 3: Academic discussion (10 questions)
  - Section 4: Academic lecture (10 questions)
  Total: 40 questions per test (matching real IELTS)

Output: web/public/data/listening_tests.json (single file, ~2-3 MB)
"""

import json
import random
import os
from itertools import cycle

random.seed(42)

# ── Content Banks ─────────────────────────────────────────────────────

# Section 1 scenarios — everyday social situations
S1_SCENARIOS = [
    ("Booking a Hotel", "hotel", [
        ("single", "double", "twin", "family"),
        ("£95", "£120", "£145", "£180"),
        ("sea view", "garden view", "city view", "courtyard view"),
        ("breakfast", "dinner", "lunch", "all meals"),
        ("swimming pool", "fitness centre", "spa", "tennis court"),
    ]),
    ("Library Registration", "library", [
        ("standard", "premium", "student", "family"),
        ("8", "12", "15", "20"),
        ("£15", "£25", "£30", "£40"),
        ("3 weeks", "2 weeks", "4 weeks", "1 month"),
        ("30 pence", "20 pence", "50 pence", "10 pence"),
    ]),
    ("Restaurant Reservation", "restaurant", [
        ("window table", "corner table", "booth", "terrace table"),
        ("2", "4", "6", "8"),
        ("7 PM", "7:30 PM", "8 PM", "8:30 PM"),
        ("vegetarian menu", "vegan menu", "gluten-free menu", "children's menu"),
        ("£35", "£45", "£55", "£65"),
    ]),
    ("Car Rental Booking", "car_rental", [
        ("compact", "sedan", "SUV", "luxury"),
        ("3 days", "5 days", "7 days", "14 days"),
        ("£45", "£55", "£65", "£75"),
        ("full insurance", "basic insurance", "no insurance", "premium insurance"),
        ("GPS navigation", "child seat", "additional driver", "roof rack"),
    ]),
    ("Course Enrollment", "course", [
        ("beginner", "intermediate", "advanced", "proficiency"),
        ("morning", "afternoon", "evening", "weekend"),
        ("12 weeks", "8 weeks", "16 weeks", "24 weeks"),
        ("£320", "£450", "£580", "£720"),
        ("online", "in-person", "hybrid", "self-paced"),
    ]),
    ("Doctor's Appointment", "doctor", [
        ("Monday", "Tuesday", "Wednesday", "Thursday"),
        ("9 AM", "10 AM", "11 AM", "2 PM"),
        ("Dr. Smith", "Dr. Jones", "Dr. Brown", "Dr. Wilson"),
        ("15 minutes", "30 minutes", "45 minutes", "1 hour"),
        ("general check-up", "blood test", "vaccination", "follow-up"),
    ]),
    ("Gym Membership", "gym", [
        ("monthly", "quarterly", "annual", "student"),
        ("£25", "£35", "£45", "£55"),
        ("6 AM", "5 AM", "7 AM", "6:30 AM"),
        ("personal trainer", "group classes", "swimming pool", "sauna"),
        ("12 months", "6 months", "3 months", "1 month"),
    ]),
    ("Insurance Inquiry", "insurance", [
        ("basic", "comprehensive", "premium", "family"),
        ("£120", "£180", "£240", "£300"),
        ("12 months", "6 months", "24 months", "3 months"),
        ("medical cover", "dental cover", "travel cover", "all-inclusive"),
        ("£500", "£1,000", "£2,000", "£5,000"),
    ]),
    ("Property Rental Inquiry", "rental", [
        ("studio", "one-bedroom", "two-bedroom", "three-bedroom"),
        ("£650", "£800", "£950", "£1,200"),
        ("6 months", "12 months", "24 months", "month-to-month"),
        ("furnished", "unfurnished", "part-furnished", "semi-furnished"),
        ("parking space", "garden access", "storage unit", "balcony"),
    ]),
    ("Travel Agency Booking", "travel", [
        ("economy", "business", "first class", "premium economy"),
        ("2 weeks", "1 week", "10 days", "3 weeks"),
        ("£450", "£680", "£890", "£1,200"),
        ("beach resort", "city hotel", "mountain lodge", "cruise ship"),
        ("morning", "afternoon", "evening", "overnight"),
    ]),
    ("Bank Account Opening", "bank", [
        ("current account", "savings account", "student account", "joint account"),
        ("£0", "£50", "£100", "£500"),
        ("1.5%", "2%", "2.5%", "3%"),
        ("debit card", "credit card", "cheque book", "online banking"),
        ("18", "16", "21", "25"),
    ]),
    ("Phone Plan Subscription", "phone", [
        ("basic plan", "standard plan", "premium plan", "unlimited plan"),
        ("£15", "£25", "£35", "£45"),
        ("5 GB", "10 GB", "20 GB", "unlimited"),
        ("12 months", "18 months", "24 months", "rolling"),
        ("500 minutes", "1,000 minutes", "unlimited", "5,000 minutes"),
    ]),
    ("Job Interview Scheduling", "interview", [
        ("Monday", "Tuesday", "Wednesday", "Friday"),
        ("10 AM", "11 AM", "2 PM", "3 PM"),
        ("30 minutes", "45 minutes", "1 hour", "90 minutes"),
        ("HR manager", "department head", "team lead", "director"),
        ("in person", "video call", "phone call", "panel"),
    ]),
    ("Enrolling in a Workshop", "workshop", [
        ("pottery", "painting", "photography", "creative writing"),
        ("Saturday", "Sunday", "Wednesday evening", "Friday evening"),
        ("6 weeks", "4 weeks", "8 weeks", "10 weeks"),
        ("£85", "£120", "£150", "£180"),
        ("beginner", "intermediate", "advanced", "all levels"),
    ]),
    ("Bus Tour Reservation", "bus_tour", [
        ("half-day tour", "full-day tour", "evening tour", "weekend tour"),
        ("£25", "£35", "£45", "£55"),
        ("9 AM", "8 AM", "10 AM", "8:30 AM"),
        ("audio guide", "live guide", "guidebook", "no guide"),
        ("12 people", "15 people", "20 people", "25 people"),
    ]),
]

# Section 2 scenarios — social context monologues
S2_SCENARIOS = [
    ("Campus Tour", "campus", [
        ("7 AM", "8 AM", "6 AM", "7:30 AM"),
        ("200,000", "150,000", "300,000", "250,000"),
        ("50", "40", "60", "30"),
        ("25-metre", "20-metre", "30-metre", "50-metre"),
        ("400", "300", "500", "350"),
    ]),
    ("Museum Exhibition Guide", "museum", [
        ("300", "250", "400", "350"),
        ("1200 BC", "1000 BC", "1500 BC", "800 BC"),
        ("four", "three", "five", "six"),
        ("six", "five", "four", "seven"),
        ("£12", "£10", "£15", "£8"),
    ]),
    ("City Orientation Talk", "city", [
        ("12th century", "11th century", "13th century", "10th century"),
        ("250,000", "180,000", "320,000", "410,000"),
        ("Tuesday", "Monday", "Wednesday", "Thursday"),
        ("9 AM", "8 AM", "10 AM", "7 AM"),
        ("£3", "£2", "£5", "£4"),
    ]),
    ("Park Ranger Briefing", "park", [
        ("15 km", "12 km", "20 km", "10 km"),
        ("3 hours", "2 hours", "4 hours", "5 hours"),
        ("186 species", "150 species", "200 species", "220 species"),
        ("spring", "summer", "autumn", "winter"),
        ("£8", "£5", "£10", "£12"),
    ]),
    ("Community Centre Programme", "community", [
        ("Monday", "Tuesday", "Wednesday", "Thursday"),
        ("6 PM", "7 PM", "5 PM", "6:30 PM"),
        ("£2", "£3", "£5", "free"),
        ("12", "10", "15", "20"),
        ("65", "60", "70", "55"),
    ]),
    ("Factory Tour Guide", "factory", [
        ("1947", "1932", "1955", "1960"),
        ("500", "400", "600", "750"),
        ("45 minutes", "30 minutes", "60 minutes", "90 minutes"),
        ("safety goggles", "hard hats", "ear protection", "gloves"),
        ("£5", "£3", "£7", "free"),
    ]),
    ("Botanical Garden Walk", "garden", [
        ("1832", "1850", "1795", "1900"),
        ("5,000", "3,000", "8,000", "10,000"),
        ("greenhouse", "rose garden", "herb garden", "alpine house"),
        ("spring", "summer", "autumn", "winter"),
        ("£7", "£5", "£9", "£6"),
    ]),
    ("Volunteer Programme Briefing", "volunteer", [
        ("Saturday", "Sunday", "both days", "weekday"),
        ("4 hours", "3 hours", "5 hours", "6 hours"),
        ("15", "12", "20", "25"),
        ("lunch", "breakfast", "snacks", "dinner"),
        ("18", "16", "21", "25"),
    ]),
    ("Local Market Guide", "market", [
        ("6 AM", "5 AM", "7 AM", "6:30 AM"),
        ("40", "30", "50", "35"),
        ("Saturday", "Sunday", "Friday", "Wednesday"),
        ("cash only", "card and cash", "card only", "all payments"),
        ("2 PM", "1 PM", "3 PM", "noon"),
    ]),
    ("School Open Day Talk", "school", [
        ("1965", "1972", "1958", "1980"),
        ("850", "750", "900", "1,000"),
        ("22", "18", "25", "20"),
        ("3 PM", "2:30 PM", "3:30 PM", "4 PM"),
        ("£45", "£35", "£50", "£40"),
    ]),
    ("Wildlife Sanctuary Guide", "wildlife", [
        ("120", "100", "150", "80"),
        ("dawn", "midday", "dusk", "early morning"),
        ("3 km", "2 km", "5 km", "4 km"),
        ("binoculars", "walking boots", "insect repellent", "raincoat"),
        ("£6", "£4", "£8", "£5"),
    ]),
    ("Public Library Tour", "library_tour", [
        ("1895", "1902", "1880", "1910"),
        ("500,000", "400,000", "600,000", "350,000"),
        ("three", "two", "four", "five"),
        ("9 AM", "8 AM", "10 AM", "8:30 AM"),
        ("free", "£2", "£5", "£1"),
    ]),
    ("Harbour Tour Briefing", "harbour", [
        ("1789", "1765", "1810", "1740"),
        ("45 minutes", "30 minutes", "60 minutes", "90 minutes"),
        ("12", "10", "15", "8"),
        ("life jackets", "raincoats", "sunscreen", "hats"),
        ("£15", "£12", "£18", "£20"),
    ]),
    ("Festival Programme Announcement", "festival", [
        ("3 days", "2 days", "5 days", "7 days"),
        ("30", "25", "40", "35"),
        ("Friday", "Thursday", "Saturday", "Wednesday"),
        ("£25", "£20", "£30", "£15"),
        ("12", "10", "15", "8"),
    ]),
    ("Recycling Centre Guide", "recycling", [
        ("plastic", "glass", "paper", "metal"),
        ("7 AM", "6 AM", "8 AM", "6:30 AM"),
        ("5", "4", "6", "3"),
        ("Tuesday", "Monday", "Wednesday", "Thursday"),
        ("free", "£2", "£5", "£1"),
    ]),
]

# Section 3 scenarios — academic discussions
S3_SCENARIOS = [
    ("Research Project on Renewable Energy", "energy", [
        ("tidal power", "solar power", "wind power", "geothermal"),
        ("Southeast Asia", "South America", "Northern Europe", "Sub-Saharan Africa"),
        ("mixed-methods", "quantitative", "qualitative", "case study"),
        ("15 minutes", "10 minutes", "20 minutes", "30 minutes"),
        ("Friday", "Wednesday", "Monday", "Thursday"),
    ]),
    ("Marketing Assignment Discussion", "marketing", [
        ("social media", "television", "print media", "radio"),
        ("18-25", "25-35", "35-50", "50+"),
        ("500", "300", "1,000", "750"),
        ("qualitative", "quantitative", "mixed", "observational"),
        ("2,000 words", "1,500 words", "3,000 words", "2,500 words"),
    ]),
    ("History Essay Planning", "history", [
        ("Industrial Revolution", "French Revolution", "Renaissance", "Cold War"),
        ("1750-1850", "1700-1800", "1800-1900", "1760-1840"),
        ("6,000 words", "5,000 words", "4,000 words", "8,000 words"),
        ("primary sources", "secondary sources", "both", "archival research"),
        ("15 January", "20 January", "10 January", "25 January"),
    ]),
    ("Biology Lab Report Review", "biology", [
        ("photosynthesis", "cell division", "enzyme activity", "genetics"),
        ("3 trials", "2 trials", "5 trials", "10 trials"),
        ("25°C", "20°C", "30°C", "37°C"),
        ("statistical", "descriptive", "comparative", "correlational"),
        ("1,500 words", "1,000 words", "2,000 words", "2,500 words"),
    ]),
    ("Psychology Experiment Design", "psychology", [
        ("memory", "attention", "perception", "learning"),
        ("50", "30", "100", "75"),
        ("two groups", "three groups", "four groups", "one group"),
        ("15 minutes", "10 minutes", "20 minutes", "30 minutes"),
        ("ethics committee", "supervisor", "department head", "peer review"),
    ]),
    ("Engineering Project Discussion", "engineering", [
        ("bridge design", "building design", "road network", "water system"),
        ("£2 million", "£1.5 million", "£3 million", "£5 million"),
        ("18 months", "12 months", "24 months", "36 months"),
        ("steel", "concrete", "composite", "timber"),
        ("sustainability", "cost", "durability", "aesthetics"),
    ]),
    ("Literature Review Planning", "literature", [
        ("Victorian era", "Romantic period", "Modernist", "Postmodern"),
        ("20", "15", "25", "30"),
        ("5,000 words", "4,000 words", "6,000 words", "3,000 words"),
        ("thematic", "chronological", "methodological", "theoretical"),
        ("next Friday", "next Monday", "next Wednesday", "next Tuesday"),
    ]),
    ("Environmental Science Field Trip", "env_sci", [
        ("water quality", "soil composition", "air pollution", "biodiversity"),
        ("3 days", "2 days", "5 days", "7 days"),
        ("15", "12", "20", "10"),
        ("pH meter", "spectrometer", "microscope", "thermometer"),
        ("£45", "£30", "£50", "£60"),
    ]),
    ("Business Plan Presentation", "business", [
        ("mobile app", "restaurant", "retail store", "online service"),
        ("£50,000", "£30,000", "£75,000", "£100,000"),
        ("18-30", "25-40", "30-50", "20-35"),
        ("social media", "word of mouth", "advertising", "partnerships"),
        ("10 minutes", "15 minutes", "20 minutes", "8 minutes"),
    ]),
    ("Architecture Studio Critique", "architecture", [
        ("residential", "commercial", "cultural", "educational"),
        ("sustainable", "minimalist", "traditional", "futuristic"),
        ("3 weeks", "2 weeks", "4 weeks", "5 weeks"),
        ("1:50", "1:100", "1:200", "1:25"),
        ("site analysis", "concept model", "material board", "lighting plan"),
    ]),
    ("Sociology Survey Project", "sociology", [
        ("housing", "employment", "education", "healthcare"),
        ("200", "150", "300", "250"),
        ("online", "face-to-face", "telephone", "postal"),
        ("5%", "3%", "10%", "8%"),
        ("2,500 words", "2,000 words", "3,000 words", "1,500 words"),
    ]),
    ("Chemistry Research Discussion", "chemistry", [
        ("polymers", "catalysts", "nanomaterials", "organic compounds"),
        ("3 months", "2 months", "6 months", "4 months"),
        ("spectroscopy", "chromatography", "crystallography", "calorimetry"),
        ("20", "15", "25", "30"),
        ("next Tuesday", "next Monday", "next Thursday", "next Friday"),
    ]),
    ("Education Practicum Reflection", "education", [
        ("primary school", "secondary school", "college", "university"),
        ("6 weeks", "4 weeks", "8 weeks", "12 weeks"),
        ("Year 5", "Year 7", "Year 9", "Year 3"),
        ("group work", "individual", "peer tutoring", "project-based"),
        ("2,000 words", "1,500 words", "3,000 words", "2,500 words"),
    ]),
    ("Geography Fieldwork Planning", "geography", [
        ("coastal erosion", "urban sprawl", "river management", "deforestation"),
        ("5 days", "3 days", "7 days", "4 days"),
        ("GIS mapping", "surveying", "sampling", "aerial photography"),
        ("12", "10", "15", "8"),
        ("£60", "£45", "£75", "£50"),
    ]),
    ("Music Composition Workshop", "music", [
        ("string quartet", "piano sonata", "orchestral", "choral"),
        ("3 movements", "2 movements", "4 movements", "5 movements"),
        ("5 minutes", "4 minutes", "7 minutes", "10 minutes"),
        ("C minor", "D major", "A minor", "F major"),
        ("next month", "in 2 weeks", "in 3 weeks", "next Friday"),
    ]),
]

# Section 4 scenarios — academic lectures
S4_SCENARIOS = [
    ("The Impact of Climate Change on Coastal Cities", "climate", [
        ("2050", "2040", "2060", "2030"),
        ("1.5 degrees", "2 degrees", "1 degree", "2.5 degrees"),
        ("30%", "25%", "40%", "35%"),
        ("Netherlands", "Bangladesh", "Vietnam", "Egypt"),
        ("2100", "2050", "2080", "2150"),
    ]),
    ("The History of the English Language", "english_lang", [
        ("5th century", "4th century", "6th century", "7th century"),
        ("1066", "900", "1200", "1500"),
        ("French", "Latin", "Norse", "Celtic"),
        ("10,000", "8,000", "15,000", "20,000"),
        ("Shakespeare", "Chaucer", "Milton", "Caxton"),
    ]),
    ("Renewable Energy Technologies", "renewable", [
        ("2030", "2025", "2035", "2040"),
        ("solar", "wind", "hydro", "geothermal"),
        ("25%", "20%", "30%", "15%"),
        ("1990s", "1980s", "2000s", "1970s"),
        ("50%", "40%", "60%", "45%"),
    ]),
    ("The Psychology of Learning", "psych_learning", [
        ("1885", "1900", "1875", "1910"),
        ("24 hours", "12 hours", "48 hours", "6 hours"),
        ("7", "5", "9", "4"),
        ("visual", "auditory", "kinesthetic", "reading"),
        ("20 minutes", "15 minutes", "30 minutes", "10 minutes"),
    ]),
    ("Urban Planning and Smart Cities", "urban", [
        ("68%", "60%", "70%", "55%"),
        ("2050", "2040", "2030", "2060"),
        ("sensors", "cameras", "drones", "satellites"),
        ("Barcelona", "Singapore", "Tokyo", "Amsterdam"),
        ("30%", "25%", "35%", "20%"),
    ]),
    ("The Economics of Globalisation", "economics", [
        ("1990s", "1980s", "2000s", "1970s"),
        ("1.5 billion", "1 billion", "2 billion", "800 million"),
        ("China", "India", "Brazil", "Vietnam"),
        ("2008", "2001", "2010", "2015"),
        ("3%", "2%", "4%", "5%"),
    ]),
    ("Marine Biology and Coral Reefs", "marine", [
        ("50%", "30%", "40%", "60%"),
        ("2050", "2030", "2040", "2060"),
        ("25%", "20%", "30%", "15%"),
        ("Australia", "Indonesia", "Philippines", "Brazil"),
        ("1°C", "0.5°C", "2°C", "1.5°C"),
    ]),
    ("The Science of Sleep", "sleep", [
        ("8 hours", "7 hours", "9 hours", "6 hours"),
        ("90 minutes", "60 minutes", "120 minutes", "45 minutes"),
        ("1953", "1937", "1960", "1925"),
        ("35%", "25%", "40%", "30%"),
        ("blue light", "caffeine", "noise", "temperature"),
    ]),
    ("Archaeological Discoveries in the 21st Century", "archaeology", [
        ("1922", "1900", "1912", "1925"),
        ("3,300 years", "3,000 years", "3,500 years", "2,500 years"),
        ("2014", "2010", "2018", "2020"),
        ("Roman", "Greek", "Egyptian", "Persian"),
        ("12 metres", "10 metres", "15 metres", "8 metres"),
    ]),
    ("The Future of Artificial Intelligence", "ai", [
        ("1956", "1950", "1960", "1945"),
        ("2030", "2025", "2035", "2040"),
        ("30%", "25%", "40%", "35%"),
        ("deep learning", "neural networks", "machine learning", "NLP"),
        ("2027", "2025", "2030", "2035"),
    ]),
    ("Nutrition and Public Health", "nutrition", [
        ("2,000", "1,800", "2,500", "2,200"),
        ("25 grams", "30 grams", "20 grams", "35 grams"),
        ("5 portions", "7 portions", "3 portions", "10 portions"),
        ("2015", "2010", "2018", "2020"),
        ("2 grams", "1.5 grams", "3 grams", "5 grams"),
    ]),
    ("The Physics of Black Holes", "blackhole", [
        ("1916", "1905", "1920", "1930"),
        ("1971", "1965", "1975", "1980"),
        ("2019", "2015", "2017", "2020"),
        ("4 million", "3 million", "5 million", "6 million"),
        ("1974", "1970", "1976", "1980"),
    ]),
    ("Cognitive Behavioral Therapy", "cbt", [
        ("1960s", "1950s", "1970s", "1940s"),
        ("12 weeks", "8 weeks", "16 weeks", "6 weeks"),
        ("50%", "40%", "60%", "45%"),
        ("Beck", "Ellis", "Freud", "Skinner"),
        ("20", "15", "25", "10"),
    ]),
    ("The Geography of Trade Routes", "trade_routes", [
        ("Silk Road", "Spice Route", "Amber Road", "Trans-Saharan"),
        ("2nd century BC", "1st century BC", "3rd century BC", "1st century AD"),
        ("6,400 km", "5,000 km", "8,000 km", "4,000 km"),
        ("1453", "1400", "1500", "1350"),
        ("14th century", "13th century", "15th century", "12th century"),
    ]),
    ("Water Conservation and Management", "water", [
        ("2.5%", "3%", "2%", "1.5%"),
        ("1%", "0.5%", "2%", "1.5%"),
        ("70%", "60%", "80%", "50%"),
        ("2040", "2030", "2050", "2025"),
        ("25%", "20%", "30%", "15%"),
    ]),
]


# ── Helper Functions ─────────────────────────────────────────────────

def make_qid(test_num, section_num, q_num):
    return f"L{test_num}S{section_num}Q{q_num}"


def gen_section1(test_num, scenario_idx):
    """Everyday social conversation — 10 questions."""
    title, key, opts_list = S1_SCENARIOS[scenario_idx]
    scenario_name = title

    # Pick varied options for this test
    o0, o1, o2, o3, o4 = opts_list

    # Build a realistic transcript
    transcripts = {
        "hotel": f"Receptionist: Good morning, Grand Hotel, how can I help you?\n\nCaller: Hi, I'd like to book a room for next weekend, please.\n\nReceptionist: Certainly. Would you like a {o0[0]} or a {o0[1]} room?\n\nCaller: A {o0[1]} room, please. Does it have a {o2[0]}?\n\nReceptionist: We have {o2[0]} rooms available at {o1[2]} per night, or standard rooms at {o1[0]} per night.\n\nCaller: I'll take the {o2[0]} room. Does the price include {o3[0]}?\n\nReceptionist: {o3[0].title()} is included for all rooms. You'll also have access to the {o4[0]} and {o4[1]} at no extra charge.\n\nCaller: That sounds great. My booking reference?\n\nReceptionist: Your confirmation number is HX-{7000 + test_num * 13}. We require a deposit of £{50 + (test_num % 3) * 10} to secure the booking, payable on arrival.\n\nCaller: Perfect. What time is check-in?\n\nReceptionist: Check-in is from 2 PM, and check-out is by 11 AM. We also offer a complimentary newspaper service and free Wi-Fi throughout the hotel.\n\nCaller: Excellent. Is there parking available?\n\nReceptionist: Yes, parking is £8 per day. Would you like me to reserve a space for you?\n\nCaller: Yes, please. And could you tell me about the restaurant?\n\nReceptionist: The restaurant is open from 6:30 PM to 10 PM. It's quite popular, so I'd recommend booking a table in advance.",

        "library": f"Librarian: Good afternoon. How can I help you today?\n\nVisitor: Hi, I'd like to register for a library card. I just moved to the area.\n\nLibrarian: Of course. I'll need to see a proof of address — a utility bill or bank statement, and a photo ID.\n\nVisitor: I have my driving licence and a bank statement. Is that sufficient?\n\nLibrarian: Perfect. Now, our {o0[0]} membership allows you to borrow up to {o1[0]} items at a time for {o3[0]}. If you upgrade to {o0[1]} membership at {o2[2]} per year, you can borrow up to {o1[2]} items and access our digital library.\n\nVisitor: I think the {o0[0]} membership is fine for now. Can I renew items online?\n\nLibrarian: Yes, you can renew up to two times online, as long as no one else has reserved the item.\n\nVisitor: Great. What about late fees?\n\nLibrarian: It's {o4[0]} per day per item, with a maximum of £10 per item. If you lose an item, the replacement cost depends on the item's value.\n\nVisitor: I see. Do you have a children's section?\n\nLibrarian: Yes, it's on the ground floor near the entrance. We also run story time sessions every {['Monday', 'Wednesday', 'Friday', 'Saturday'][test_num % 4]} at 10:30 AM.\n\nVisitor: That's wonderful. And do you have computers for public use?\n\nLibrarian: We have 12 computers on the first floor. They're available in 30-minute sessions. You'll need your library card to log in.",

        "restaurant": f"Host: Good evening, Bella Vista Restaurant. How may I help you?\n\nCaller: I'd like to make a reservation for this Saturday evening.\n\nHost: Of course. How many people will be dining?\n\nCaller: A table for {o1[1]}, please. Do you have a {o0[0]} available?\n\nHost: Let me check. Yes, we have a {o0[0]} available at {o2[1]}. Would that work?\n\nCaller: That's perfect. Do you have a {o3[0]} option? One of our party has dietary requirements.\n\nHost: Absolutely. We offer {o3[0]}, {o3[1]}, and {o3[2]} menus. I'll note that on your reservation.\n\nCaller: Thank you. What's the price for the set menu?\n\nHost: The three-course set menu is {o4[2]} per person. It includes a starter, main course, and dessert.\n\nCaller: That sounds good. Can we bring a cake? It's a birthday celebration.\n\nHost: Of course! We can even bring it out for you with a candle. There's a £5 cake service charge.\n\nCaller: Great. Is parking available nearby?\n\nHost: There's a public car park next to the restaurant. It's £2 per hour. We also offer valet parking for £8.\n\nCaller: Perfect. I'll book the {o2[1]} slot for {o1[1]} people.\n\nHost: Excellent. Can I take your name and phone number?",

        "car_rental": f"Agent: Welcome to Speedy Car Rentals. How can I assist you today?\n\nCustomer: I'd like to rent a car for {o1[0]} starting from this Friday.\n\nAgent: Certainly. We have {o0[0]}, {o0[1]}, {o0[2]}, and {o0[3]} vehicles available. Which would you prefer?\n\nCustomer: I'll go with the {o0[1]}. What's the daily rate?\n\nAgent: The {o0[1]} is {o2[0]} per day, so for {o1[0]} that comes to {o2[2]}. Would you like to add {o3[0]}?\n\nCustomer: Yes, I think {o3[0]} is a good idea. How much extra is that?\n\nAgent: {o3[0]} is £12 per day. I'd also recommend adding {o4[0]} for £5 per day — it's very helpful for navigating the area.\n\nCustomer: I'll take both. What do I need to bring when I pick up the car?\n\nAgent: You'll need your driving licence, a credit card in your name, and a second form of ID. The minimum age is 21.\n\nCustomer: I have all of that. What's the fuel policy?\n\nAgent: It's full-to-full. You pick up the car with a full tank and return it the same way. Otherwise, there's a refuelling charge of £15 plus the cost of fuel.\n\nCustomer: Understood. What time can I pick up the car?\n\nAgent: Our office opens at 8 AM. The latest return time is 6 PM on the due date.",

        "course": f"Advisor: Good morning, Language Centre. How can I help you?\n\nStudent: Hi, I'd like to enrol in an English course. I'm looking for a {o0[0]} level class.\n\nAdvisor: Great. We offer {o0[0]}, {o0[1]}, {o0[2]}, and {o0[3]} levels. The {o0[0]} course runs for {o2[0]} and costs {o3[2]}.\n\nStudent: That sounds good. What time are the classes?\n\nAdvisor: We have {o1[0]}, {o1[1]}, {o1[2]}, and {o1[3]} sessions. The {o1[0]} session runs from 9 AM to 12 PM, three days a week.\n\nStudent: I'd prefer the {o1[0]} session. Is it {o4[0]} or {o4[1]}?\n\nAdvisor: We offer both {o4[0]} and {o4[1]} options. The {o4[0]} class meets on campus in Room 204.\n\nStudent: I'll take the {o4[0]} option. What materials do I need?\n\nAdvisor: The course book is included in the fee. You'll also need a notebook and a dictionary. We provide access to our online learning platform as well.\n\nStudent: Is there an entrance test?\n\nAdvisor: Yes, there's a short placement test on the first day. It takes about 30 minutes and covers reading, writing, listening, and speaking.\n\nStudent: When does the next course start?\n\nAdvisor: The next intake begins on the 15th of next month. I can reserve a spot for you now.",

        "doctor": f"Receptionist: Good morning, City Medical Centre. How can I help?\n\nPatient: I'd like to make an appointment with a doctor, please.\n\nReceptionist: Certainly. Would you prefer {o0[0]}, {o0[1]}, {o0[2]}, or {o0[3]}?\n\nPatient: {o0[1]} would be best, if possible.\n\nReceptionist: We have an opening on {o0[1]} at {o1[1]} with {o2[0]}. Would that work?\n\nPatient: Yes, that's fine. What should I expect during the visit?\n\nReceptionist: It's a {o3[0]} appointment for a {o4[0]}. Please arrive 10 minutes early to fill in some forms.\n\nPatient: Do I need to bring anything?\n\nReceptionist: Please bring your health insurance card and a list of any medications you're currently taking. If this is your first visit, you'll also need a photo ID.\n\nPatient: I have all of that. Is there a fee?\n\nReceptionist: If you have insurance, there's no charge. Without insurance, the consultation fee is £45.\n\nPatient: I have insurance. Can I change the appointment if needed?\n\nReceptionist: Yes, just call us at least 24 hours in advance to reschedule. There's no cancellation fee if you give us enough notice.\n\nPatient: Perfect. I'll see {o2[0]} on {o0[1]} at {o1[1]}.",

        "gym": f"Staff: Welcome to FitLife Gym! How can I help you today?\n\nVisitor: I'm interested in joining. What membership options do you have?\n\nStaff: We offer {o0[0]}, {o0[1]}, {o0[2]}, and {o0[3]} memberships. The {o0[0]} plan is {o1[0]} per month.\n\nVisitor: What about the {o0[2]} plan?\n\nStaff: The {o0[2]} plan is {o1[2]} per year — that's our best value. It includes access to all facilities and {o4[0]} sessions.\n\nVisitor: That sounds good. What time does the gym open?\n\nStaff: We open at {o2[0]} on weekdays and 7 AM on weekends. We close at 10 PM every day.\n\nVisitor: Do you have {o3[0]}?\n\nStaff: Yes! We have {o3[0]} sessions available. The first session is free with your membership. After that, it's £25 per session.\n\nVisitor: Is there a joining fee?\n\nStaff: There's a one-time registration fee of £20. But if you sign up for the {o0[2]} plan, we waive that fee.\n\nVisitor: Great. What about the minimum commitment?\n\nStaff: The {o0[2]} plan is a {o4[1]} commitment. After that, it rolls over month-to-month and you can cancel with 30 days' notice.\n\nVisitor: Perfect. I'd like to sign up for the {o0[2]} plan.",

        "insurance": f"Agent: Good afternoon, SafeGuard Insurance. How may I help you?\n\nCaller: I'd like to get a quote for health insurance.\n\nAgent: Certainly. We offer {o0[0]}, {o0[1]}, {o0[2]}, and {o0[3]} plans. The {o0[0]} plan starts at {o1[0]} per month.\n\nCaller: What does the {o0[1]} plan include?\n\nAgent: The {o0[1]} plan is {o1[1]} per month and covers {o3[0]}, {o3[1]}, and {o3[2]}. It's our most popular option.\n\nCaller: How long is the contract?\n\nAgent: All plans are for {o2[0]}, renewable annually. There's no cancellation fee after the first {o2[0]}.\n\nCaller: What's the excess?\n\nAgent: The standard excess is {o4[0]} per claim. If you choose a higher excess of {o4[2]}, your monthly premium drops by 15%.\n\nCaller: I see. Is there a waiting period?\n\nAgent: Yes, there's a 30-day waiting period for general treatments and 12 months for pre-existing conditions.\n\nCaller: Can I add family members?\n\nAgent: Absolutely. You can add up to four dependants. Each additional family member is £18 per month on the {o0[1]} plan.\n\nCaller: That's reasonable. What documents do I need to sign up?\n\nAgent: You'll need a photo ID, proof of address, and a health declaration form.",

        "rental": f"Agent: Good morning, HomeFinders Letting Agency. How can I help?\n\nCaller: I'm looking for a rental property. I'm interested in a {o0[1]}.\n\nAgent: Great. We have a {o0[1]} available in the Riverside development. The rent is {o1[1]} per month.\n\nCaller: That's within my budget. Is it {o3[0]} or {o3[1]}?\n\nAgent: It's {o3[0]}, which includes a bed, sofa, dining table, and all white goods. The kitchen has an oven, fridge-freezer, and washing machine.\n\nCaller: Perfect. What's the lease term?\n\nAgent: The minimum lease is {o2[0]}, with the option to renew. You'll need to give one month's notice before the end of the term if you plan to leave.\n\nCaller: Is there a deposit?\n\nAgent: Yes, the deposit is equivalent to one month's rent — {o1[1]}. It's held in a government-approved deposit protection scheme.\n\nCaller: Does the rent include any bills?\n\nAgent: Water is included, but electricity, gas, and internet are separate. On average, tenants pay about £120 per month for all utilities.\n\nCaller: I see. Is there {o4[0]}?\n\nAgent: Yes, there's one allocated {o4[0]}. Additional visitor parking is available on the street.\n\nCaller: Great. When can I view the property?",

        "travel": f"Agent: Hello, SunSeeker Travel. How can I help you today?\n\nCustomer: I'd like to book a holiday package to Spain for {o1[0]}.\n\nAgent: Wonderful! We have several options. Would you prefer {o0[0]}, {o0[1]}, or {o0[2]} flights?\n\nCustomer: {o0[0]} is fine. What accommodation options do you have?\n\nAgent: We have a {o3[0]}, a {o3[1]}, and a {o3[2]}. The {o3[0]} package is {o2[0]} per person for {o1[0]}.\n\nCustomer: The {o3[0]} sounds good. What time is the flight?\n\nAgent: There's a {o4[0]} departure at 9:30 AM, arriving at 1 PM local time. The return flight departs at 3 PM.\n\nCustomer: Perfect. Is airport transfer included?\n\nAgent: Yes, return airport transfers are included in the package. A representative will meet you at the airport with a sign.\n\nCustomer: What about travel insurance?\n\nAgent: Basic travel insurance is included. You can upgrade to comprehensive cover for £25 per person.\n\nCustomer: I'll take the basic cover. What's the total price?\n\nAgent: For {o0[0]} flights and the {o3[0]} package, the total is {o2[0]} per person. There's also a booking fee of £15.\n\nCustomer: That's fine. How much deposit do I need to pay now?\n\nAgent: A deposit of £150 per person secures the booking. The balance is due 6 weeks before departure.",

        "bank": f"Clerk: Good morning, National Bank. How can I help you today?\n\nCustomer: I'd like to open a {o0[0]}. What do I need?\n\nClerk: You'll need a photo ID, proof of address, and an initial deposit. The minimum deposit for a {o0[0]} is {o1[0]}.\n\nCustomer: I have my passport and a utility bill. What's the interest rate?\n\nClerk: The {o0[0]} offers {o2[0]} interest per year. If you choose the {o0[1]}, you get {o2[1]} interest.\n\nCustomer: I'll go with the {o0[0]}. Do I get a {o3[0]}?\n\nClerk: Yes, you'll receive a {o3[0]} within 5-7 working days. You can also set up {o3[3]} immediately.\n\nCustomer: Is there a monthly fee?\n\nClerk: There's no monthly fee as long as you maintain a minimum balance of £100. Otherwise, it's £8 per month.\n\nCustomer: What's the minimum age to open an account?\n\nClerk: You must be at least {o4[0]} years old. For younger customers, we offer a {o0[2]} with parental consent.\n\nCustomer: I'm {o4[0]}. Can I also set up a direct debit?\n\nClerk: Absolutely. You can set up direct debits and standing orders through online banking or at any branch.\n\nCustomer: Great. How long does it take to open the account?\n\nClerk: The process takes about 20 minutes. Your card will be activated within 24 hours of receiving it.",

        "phone": f"Agent: Hello, ConnectMobile. How can I help you today?\n\nCustomer: I'd like to sign up for a mobile phone plan.\n\nAgent: Great! We offer the {o0[0]} at {o1[0]} per month, the {o0[1]} at {o1[1]}, and the {o0[2]} at {o1[2]}.\n\nCustomer: What does the {o0[1]} include?\n\nAgent: The {o0[1]} gives you {o2[1]} of data, {o4[1]}, and unlimited texts. It's our most popular plan.\n\nCustomer: That sounds good. How long is the contract?\n\nAgent: Contracts are {o3[0]}. After that, it becomes a rolling monthly contract that you can cancel with 30 days' notice.\n\nCustomer: Is there an upfront cost?\n\nAgent: There's a £10 SIM activation fee, but it's waived if you sign up online.\n\nCustomer: Can I keep my current number?\n\nAgent: Absolutely. You'll need a PAC code from your current provider. Once you give it to us, the transfer takes 1-2 working days.\n\nCustomer: What happens if I go over my data allowance?\n\nAgent: You'll be charged £2 per GB for extra data. Or you can set a data cap to prevent overage charges.\n\nCustomer: I'll set a cap. Can I upgrade my plan later?\n\nAgent: Yes, you can upgrade at any time. Downgrading is only allowed after the first 6 months.",

        "interview": f"HR: Good morning, TechCorp Human Resources. How can I help?\n\nApplicant: I received an email about a job interview. I'd like to confirm the details.\n\nHR: Of course. May I have your name? ... Thank you. Yes, your interview is scheduled for {o0[0]} at {o1[0]}.\n\nApplicant: Great. Who will be interviewing me?\n\nHR: You'll be meeting with the {o3[0]}. The interview will last approximately {o2[0]}.\n\nApplicant: Is it {o4[0]} or {o4[1]}?\n\nHR: It's {o4[0]}. Please come to the 5th floor, Room 512. Bring a copy of your CV and any portfolio materials.\n\nApplicant: I will. What's the format of the interview?\n\nHR: It starts with a brief introduction, followed by technical questions and a short practical exercise. You'll also have a chance to ask questions at the end.\n\nApplicant: Is there parking available?\n\nHR: Yes, there's visitor parking in the basement. Just mention your name at the security desk and they'll direct you.\n\nApplicant: What should I wear?\n\nHR: Business casual is fine. No need for a full suit, but please dress neatly.\n\nApplicant: Perfect. Should I arrive early?\n\nHR: Please arrive 10-15 minutes early to complete a visitor registration form at reception.",

        "workshop": f"Coordinator: Hello, Community Arts Centre. How can I help?\n\nCaller: I'd like to enrol in a {o0[0]} workshop. What's available?\n\nCoordinator: We have {o0[0]}, {o0[1]}, {o0[2]}, and {o0[3]} workshops. The {o0[0]} workshop runs for {o2[0]}.\n\nCaller: That sounds great. When does it meet?\n\nCoordinator: Sessions are on {o1[0]} from 6 PM to 8 PM. The next course starts on the 5th.\n\nCaller: How much does it cost?\n\nCoordinator: The full course is {o3[2]}, which includes all materials. There's also a {o4[0]} option for those with some experience.\n\nCaller: I'm a {o4[0]}, so that's perfect. Is there a maximum class size?\n\nCoordinator: Yes, we limit classes to 12 students to ensure individual attention from the instructor.\n\nCaller: Do I need to bring anything?\n\nCoordinator: All materials are provided for the first session. After that, the instructor will give you a list of supplies if you want to practice at home.\n\nCaller: Is there an age requirement?\n\nCoordinator: Participants must be 16 or older. We have separate children's classes on Saturday mornings.\n\nCaller: Great. Can I get a refund if I change my mind?\n\nCoordinator: Full refunds are available up to 7 days before the course starts. After that, we offer a 50% refund or credit toward a future course.",

        "bus_tour": f"Guide: Good morning, CitySightseeing Tours. How can I help?\n\nTourist: I'd like to book a {o0[0]}. What are the options?\n\nGuide: We offer {o0[0]} for {o1[0]}, {o0[1]} for {o1[1]}, and {o0[2]} for {o1[2]} per person.\n\nTourist: I'll take the {o0[0]}. What time does it depart?\n\nGuide: The {o0[0]} departs at {o2[0]} from the central bus station, Platform 3.\n\nTourist: How long is the tour?\n\nGuide: The {o0[0]} lasts approximately 4 hours. We visit 6 major attractions with stops for photos.\n\nTourist: Is there a {o3[0]}?\n\nGuide: Yes, we provide a {o3[0]} in 8 languages. Headphones are provided free of charge.\n\nTourist: What about group discounts?\n\nGuide: Groups of {o4[0]} or more receive a 15% discount. The maximum group size is {o4[2]}.\n\nTourist: I'm booking for 2 people. Can I pay by card?\n\nGuide: Yes, we accept all major credit and debit cards. You can also pay cash on the day.\n\nTourist: What happens if it rains?\n\nGuide: Tours run rain or shine. The bus is fully enclosed with heating and air conditioning. We also provide umbrellas if needed.",
    }

    transcript = transcripts.get(key, transcripts["hotel"])

    # Generate 10 questions
    questions = []

    # Q1: completion
    questions.append({
        "id": make_qid(test_num, 1, 1),
        "number": 1,
        "type": "completion",
        "text": f"The customer wants a ________________ room/plan.",
        "answer": [o0[1]],
        "max_words": 1
    })

    # Q2: mcq
    questions.append({
        "id": make_qid(test_num, 1, 2),
        "number": 2,
        "type": "mcq",
        "text": "How much does the premium option cost?",
        "options": [o1[0], o1[1], o1[2], o1[3]],
        "answer": o1[2]
    })

    # Q3: tfng
    questions.append({
        "id": make_qid(test_num, 1, 3),
        "number": 3,
        "type": "tfng",
        "text": "The basic option includes all premium features.",
        "answer": "FALSE"
    })

    # Q4: mcq
    questions.append({
        "id": make_qid(test_num, 1, 4),
        "number": 4,
        "type": "mcq",
        "text": "Which of the following is mentioned as an additional feature?",
        "options": [o4[0], o4[1], o4[2], o4[3]],
        "answer": o4[0]
    })

    # Q5: completion
    questions.append({
        "id": make_qid(test_num, 1, 5),
        "number": 5,
        "type": "completion",
        "text": f"The duration/term is ________________.",
        "answer": [o2[0], o3[0]],
        "max_words": 2
    })

    # Q6: mcq
    questions.append({
        "id": make_qid(test_num, 1, 6),
        "number": 6,
        "type": "mcq",
        "text": "What time does the service start?",
        "options": [o2[0], o2[1], o2[2], o2[3]],
        "answer": o2[0]
    })

    # Q7: tfng
    questions.append({
        "id": make_qid(test_num, 1, 7),
        "number": 7,
        "type": "tfng",
        "text": "There is no additional charge for the first session.",
        "answer": "TRUE"
    })

    # Q8: completion
    questions.append({
        "id": make_qid(test_num, 1, 8),
        "number": 8,
        "type": "completion",
        "text": "The customer needs to bring a photo ________________.",
        "answer": ["ID", "identification"],
        "max_words": 1
    })

    # Q9: mcq
    questions.append({
        "id": make_qid(test_num, 1, 9),
        "number": 9,
        "type": "mcq",
        "text": "What is the minimum age requirement?",
        "options": ["16", "18", "21", "25"],
        "answer": "18"
    })

    # Q10: completion
    questions.append({
        "id": make_qid(test_num, 1, 10),
        "number": 10,
        "type": "completion",
        "text": "The confirmation/booking number is HX-______________.",
        "answer": [str(7000 + test_num * 13)],
        "max_words": 1
    })

    return {
        "id": "S1",
        "number": 1,
        "title": f"Section 1 — Conversation ({scenario_name})",
        "instructions": f"Listen to a conversation about {scenario_name.lower()}. Answer questions 1-10.",
        "transcript": transcript,
        "questions": questions
    }


def gen_section2(test_num, scenario_idx):
    """Social context monologue — 10 questions."""
    title, key, opts_list = S2_SCENARIOS[scenario_idx]
    o0, o1, o2, o3, o4 = opts_list

    transcripts = {
        "campus": f"Welcome to Riverside University! I'm Sarah, your campus guide today. Let me walk you through the main facilities.\n\nTo your left is the main library, open from {o0[0]} to midnight, seven days a week. You'll need your student ID card to enter after 6 PM. The library has over {o1[0]} books and {o2[0]} computers on the second floor.\n\nStraight ahead is the Students' Union building. Inside you'll find the cafeteria, which serves hot meals from 11 AM to 2 PM, and the bookshop on the ground floor. The Union also runs over 60 student societies — you can sign up during Freshers' Week.\n\nOn your right is the Sports Centre. Membership is free for all enrolled students. It includes a {o3[0]} swimming pool, four squash courts, and a climbing wall. You'll need to book courts at least 24 hours in advance.\n\nFinally, the building at the far end is the lecture theatre complex. Most first-year lectures take place in Hall A, which seats {o4[0]} students. Please note that recording lectures is permitted, but only for personal study purposes.\n\nBefore we move on, I should mention that the campus health centre is located next to the library. It's open Monday to Friday, 8 AM to 6 PM. Appointments can be booked online or by calling the reception.\n\nThe computer labs in Building C are available 24/7 with your student card. Printing costs 5 pence per page for black and white, and 20 pence for colour.",

        "museum": f"Good evening, and welcome to the opening of our new exhibition, 'Ancient Civilisations of the Mediterranean'. I'm Dr. Helen Park, the curator.\n\nThis exhibition features over {o0[0]} artefacts from four ancient civilisations: Egyptian, Greek, Roman, and Phoenician. The centrepiece is a rare Egyptian sarcophagus dating back to {o1[0]}, on loan from the Cairo Museum for the first time.\n\nYou'll notice the exhibition is organised thematically rather than chronologically. Section A covers daily life — pottery, tools, and clothing. Section B focuses on religion and burial practices. Section C displays trade and commerce, including Phoenician glassware and Roman coins.\n\nI'd like to draw your attention to the interactive displays in Section D. You can use the tablets provided to explore 3D models of each artefact. These tablets are available in {o3[0]} languages.\n\nThe exhibition runs for three months, until March 15th. Guided tours are available every Tuesday and Thursday at 2 PM. Group bookings of 10 or more receive a 20% discount on the {o4[0]} admission fee.\n\nBefore you begin, please note that photography is permitted without flash. Food and drink are not allowed in the exhibition halls. The gift shop and café are on the ground floor.\n\nI should also mention that we have a special lecture series every Friday evening at 6 PM in the auditorium. Entry is free with your exhibition ticket.",

        "city": f"Good morning, everyone, and welcome to our beautiful city. I'm Tom, and I'll be your guide today. Let me give you a brief overview of what our city has to offer.\n\nOur city was founded in the {o0[0]} and has a rich history. Today, it has a population of approximately {o1[0]} people, making it the third-largest city in the region.\n\nThe historic old town is a must-see. It features cobblestone streets, medieval buildings, and the famous clock tower, which dates back to {o0[0]}. The old town market is open every {o2[0]} from {o3[0]} to 4 PM.\n\nFor those interested in art, the City Gallery on Market Square houses an impressive collection of 19th-century paintings. Admission is {o4[0]} for adults and free for children under 12.\n\nThe riverside promenade is perfect for an afternoon stroll. It stretches for 3 kilometres along the river and offers beautiful views of the city skyline. Boat tours depart every hour from the pier.\n\nPublic transport is excellent here. Buses run every 10 minutes during peak hours. A day pass costs £4 and gives you unlimited travel on all routes.\n\nI should also mention that the city's main festival takes place in August, featuring street performances, food stalls, and live music. It attracts over 50,000 visitors each year.",

        "park": f"Good morning, and welcome to Greenwood National Park. I'm Ranger Dave, and I'll be briefing you on today's activities and park regulations.\n\nGreenwood covers an area of {o0[0]} and has over {o2[0]}. The park was established in 1972 and is home to {o2[0]} of birds, mammals, and reptiles.\n\nThere are four main walking trails. The easiest is the Lake Trail, which takes about {o1[0]}. The Summit Trail is more challenging and takes {o1[2]} to complete. Please register at the trailhead before starting any hike.\n\nThe visitor centre is open from {o3[0]} to 5 PM daily. Inside, you'll find interactive exhibits, a gift shop, and a small café. Entry to the visitor centre is free.\n\nCamping is permitted in designated areas only. The main campsite has 40 pitches and costs {o4[0]} per night per tent. Facilities include hot showers, toilets, and a communal fire pit.\n\nI must remind you that feeding wildlife is strictly prohibited. It harms the animals and can lead to aggressive behaviour. Please keep all food in sealed containers.\n\nThe best time for wildlife spotting is at {o3[1]}, particularly near the lake. You might see deer, foxes, and if you're lucky, the rare red squirrel.",

        "community": f"Good evening, and welcome to the Riverside Community Centre's autumn programme launch. I'm Jenny, the centre coordinator.\n\nThis term, we're offering over 30 different activities. Let me highlight some of the new additions.\n\nFirst, our fitness programme has expanded. We now offer yoga on {o0[0]} at {o1[0]}, Pilates on Wednesday evenings, and a new Zumba class on Friday mornings. Each class is {o2[0]} per session or £40 for a 10-session pass.\n\nFor children, we have after-school clubs running Monday to Thursday from 4 PM to 6 PM. Activities include arts and crafts, sports, and coding. The cost is £3 per session per child.\n\nOur popular language exchange programme meets every Tuesday at 7 PM. It's completely free — just bring your enthusiasm and a willingness to share your native language.\n\nThe centre also hosts a weekly community lunch every Friday at noon. It's prepared by our volunteer kitchen team and costs just £2 per person. Last week, we served {o3[0]} meals.\n\nFor our senior members, we have a gentle exercise class on Monday mornings at 10 AM, followed by a social coffee morning. Transport is available for those who need it.\n\nFinally, the centre is open to anyone aged {o4[0]} and above for most activities. Some evening classes are restricted to those 16 and older.",

        "factory": f"Good morning, and welcome to the Heritage Biscuit Factory. I'm your guide, Michael. Before we begin the tour, let me give you some background.\n\nThis factory was established in {o0[0]} and has been producing biscuits ever since. Today, we employ {o1[0]} people and produce over 2 million biscuits per week.\n\nThe tour will take approximately {o2[0]}. Please stay with the group at all times and follow the marked walkways. Safety is our top priority.\n\nYou'll notice that everyone in the production area wears {o3[0]}. You'll each be given a pair before we enter. Please also sanitise your hands at the station by the entrance.\n\nOur first stop is the mixing room, where ingredients are combined in large industrial mixers. Each batch produces 500 kilograms of dough. The flour is stored in silos on the roof and piped down as needed.\n\nNext, we'll visit the baking ovens. These run at 220 degrees Celsius and can bake 5,000 biscuits at once. The smell is incredible!\n\nAfter that, we'll see the packaging line, where biscuits are sorted, wrapped, and boxed automatically.\n\nThe tour ends at the factory shop, where you can purchase products at a discount. Entry to the shop is {o4[0]}, and you'll receive a 10% discount on all purchases.\n\nPhotography is not permitted in the production area, but you're welcome to take photos in the shop and lobby.",

        "garden": f"Good afternoon, and welcome to the Royal Botanical Garden. I'm Dr. Chen, the head botanist, and I'll be your guide today.\n\nThese gardens were established in {o0[0]} and cover 40 hectares. We have over {o1[0]} plant species from around the world, making us one of the most diverse botanical collections in the country.\n\nLet's start with the {o2[0]}, which is our most popular attraction. It maintains a constant temperature of 24 degrees and houses tropical plants, including orchids, ferns, and carnivorous plants.\n\nThe rose garden, to your right, was planted in 1965 and features over 200 varieties of roses. The best time to visit is in {o3[0]}, when most varieties are in full bloom.\n\nOur medicinal herb garden showcases plants used in traditional medicine. Each plant has an information board describing its historical and modern uses.\n\nThe Japanese garden, created in 1988, features a tea house where traditional tea ceremonies are held on the first Saturday of each month.\n\nAdmission to the gardens is {o4[0]} for adults, £4 for children, and free for members. Annual membership is £35 and includes unlimited entry and quarterly events.\n\nGuided tours like this one run daily at 11 AM and 2 PM. Each tour lasts approximately 90 minutes.",

        "volunteer": f"Good morning, everyone. Thank you for coming to the volunteer orientation. I'm Sarah, the volunteer coordinator for the City Wildlife Trust.\n\nOur volunteer programme runs every {o0[0]} from 9 AM to 1 PM — that's {o1[0]} per session. We ask for a minimum commitment of {o2[0]} sessions over the season.\n\nThis year, we have {o3[0]} volunteers signed up, which is our largest group yet. We'll be working in teams of five, each led by an experienced team leader.\n\nYour main tasks will include habitat restoration, species monitoring, and maintaining walking trails. All tools and equipment are provided. Please wear sturdy boots and weather-appropriate clothing.\n\n{o4[0]} is provided for all volunteers. We also provide tea and biscuits during the mid-morning break.\n\nBefore you start, you'll need to complete a safety briefing and sign a liability waiver. Volunteers must be at least {o4[1]} years old. Those under 18 need a parent's signature.\n\nWe also offer training sessions on the first Saturday of each month. Topics include wildlife identification, first aid, and conservation techniques. These are optional but highly recommended.\n\nTransport to the work sites is provided from the city centre. The bus leaves at 8:30 AM sharp from the central bus station.",

        "market": f"Good morning, and welcome to the Riverside Farmers' Market. I'm Claire, the market manager, and I'll give you a quick overview.\n\nThe market opens at {o0[0]} every {o3[0]} and runs until {o4[0]}. We have over {o1[0]} stalls selling fresh produce, artisan foods, crafts, and plants.\n\nLet me walk you through the main sections. The produce section, at the north end, features organic vegetables, fruits, and herbs from local farms. All produce is harvested within 24 hours of the market.\n\nThe bakery section is always popular. We have 8 bakers offering sourdough, croissants, pastries, and gluten-free options. The sourdough from Riverside Bakery sells out by 10 AM, so come early!\n\nThe cheese and dairy section features artisan cheeses from 6 local producers. You can sample before you buy.\n\nPayment is {o2[0]}. Most vendors accept cards, but a few are cash only. There's an ATM near the entrance, but it charges £1.50 per withdrawal.\n\nParking is available at the car park on Mill Street. The first hour is free, and it's £1 per hour after that.\n\nWe also have live music from 10 AM — local musicians perform acoustic sets near the café area.",

        "school": f"Good afternoon, and welcome to Greenfield School's open day. I'm Mr. Roberts, the headteacher.\n\nGreenfield was founded in {o0[0]} and has grown to {o1[0]} students across years 7 to 13. Our average class size is {o2[0]}, which allows for personalised attention.\n\nOur curriculum is broad and balanced. In addition to core subjects, we offer Spanish, French, art, music, drama, and computing. At GCSE, students choose 4 optional subjects alongside the compulsory core.\n\nOur facilities include 3 science laboratories, a design technology workshop, a music studio, and a 200-seat theatre. The sports complex has a sports hall, tennis courts, and a playing field.\n\nExtracurricular activities are a big part of life at Greenfield. We offer over 40 clubs, including robotics, debate, chess, and various sports teams. Clubs run after school from {o3[0]} to 4:30 PM.\n\nSchool starts at 8:40 AM and ends at {o3[1]}. There are 6 periods per day, each lasting 50 minutes. Lunch is from 12:30 to 1:30 PM.\n\nThe uniform costs approximately {o4[0]} and can be purchased from the school shop or online. Financial assistance is available for families who need it.\n\nI'll now hand you over to our student guides, who will take you on a tour of the campus.",

        "wildlife": f"Good morning, and welcome to the Dawn Wildlife Sanctuary. I'm Ranger Lisa, and I'll be your guide for today's nature walk.\n\nThis sanctuary was established in 1985 and covers 500 hectares. It's home to over {o0[0]} species of birds, mammals, and reptiles, including several endangered species.\n\nThe best time for wildlife observation is at {o1[0]}, when animals are most active. That's why our guided walks start at 6 AM. Don't worry — the early start is worth it!\n\nOur walk today covers {o2[0]} and takes about 2 hours. The trail is relatively flat and suitable for all fitness levels.\n\nI recommend bringing {o3[0]} for the best viewing experience. We have some available to borrow at the visitor centre, but supplies are limited.\n\nPlease keep to the marked trails at all times. Venturing off-path can damage fragile habitats and disturb nesting birds.\n\nThe sanctuary is a photography-friendly zone, but please turn off your flash — it can startle the animals. Drones are strictly prohibited.\n\nEntry to the sanctuary is {o4[0]} for adults, £3 for children, and free for members. Annual membership is £25.\n\nAfter the walk, we'll return to the visitor centre for hot drinks and a Q&A session.",

        "library_tour": f"Good morning, and welcome to the Central City Library. I'm Margaret, the head librarian, and I'll be giving you a tour today.\n\nThis building was opened in {o0[0]} and is one of the oldest public libraries in the country. Our collection includes over {o1[0]} books, 20,000 e-books, and 5,000 audio recordings.\n\nThe library is organised across {o2[0]} floors. The ground floor has the children's section, periodicals, and the main reading room. The first floor houses fiction and non-fiction. The second floor is dedicated to reference materials and local history.\n\nWe open at {o3[0]} on weekdays and 9 AM on weekends. We close at 8 PM Monday to Thursday, 6 PM on Friday, and 5 PM on weekends.\n\nMembership is {o4[0]} for residents. You'll need a proof of address and a photo ID to register. Visitors can get a day pass for £2.\n\nOur digital library is accessible 24/7 with your library card. You can borrow e-books, audiobooks, and access online databases including academic journals.\n\nWe also offer free computer access on the first floor. There are 20 computers available in 60-minute sessions. Free Wi-Fi is available throughout the building.\n\nEvery Wednesday at 10 AM, we host a story time session for children aged 3-6. It's free and no booking is required.",

        "harbour": f"Good morning, and welcome to the Heritage Harbour tour. I'm Captain Mike, and I'll be your guide today.\n\nThis harbour was built in {o0[0]} and was once the busiest port in the region. Today, it's a heritage site and tourist attraction.\n\nThe tour lasts approximately {o1[0]} and takes you around the main harbour, the fish market, and the maritime museum. We'll be walking about 2 kilometres in total.\n\nPlease note that the harbour is a working port. Watch out for moving vehicles and keep children close at hand. I recommend wearing {o2[0]} as some areas can be slippery.\n\nOur first stop is the old lighthouse, built in 1820. It was decommissioned in 1965 and now houses a small exhibition on harbour history.\n\nNext, we'll visit the fish market. It opens at 5 AM, and the best fish sells out by 8 AM. You'll see the auction process and learn about local fishing traditions.\n\nThe maritime museum has over 500 exhibits, including model ships, navigation instruments, and photographs. Entry is included in your tour ticket.\n\nThe tour costs {o4[0]} for adults and £8 for children. Family tickets for two adults and two children are £35.\n\nWe run two tours daily: 10 AM and 2 PM. Booking in advance is recommended, especially during peak season.",

        "festival": f"Good afternoon, everyone. I'm David, the festival director, and I'm here to tell you about this year's Riverside Arts Festival.\n\nThe festival runs for {o0[0]}, from {o2[0]} to Sunday. We have over {o1[0]} performances across 8 venues throughout the city.\n\nThis year's headline act is the London Symphony Orchestra, performing on Saturday evening at the Riverside Amphitheatre. Tickets for that event are £25, but most other performances are free.\n\nThe festival opens at 6 PM on {o2[0]} with a street parade through the city centre. Over 500 performers will participate, including samba bands, stilt walkers, and fire jugglers.\n\nOn Saturday, the main stage in Victoria Park will host 12 acts from 11 AM to 11 PM. There's also a food court with 20 vendors serving cuisine from around the world.\n\nFor families, the Children's Zone in the park offers free activities including face painting, storytelling, and craft workshops. It's open from 10 AM to 5 PM on both Saturday and Sunday.\n\nA festival pass costs {o3[0]} and gives you entry to all ticketed events. Individual event tickets range from £5 to £25.\n\nWe expect around {o4[0]} visitors per day, so please use public transport where possible. Extra buses and trains will run throughout the festival.",

        "recycling": f"Good morning, and welcome to the City Recycling Centre. I'm Phil, the site manager, and I'll be showing you how our facility works.\n\nThis centre opened in 2015 and processes over 200 tonnes of recyclable material each month. We handle {o0[0]}, {o1[0]}, {o2[0]}, and {o3[0]}.\n\nThe centre is open from {o1[0]} to 6 PM, Monday to Saturday. It's closed on Sundays and public holidays.\n\nWhen you arrive, you'll see {o2[0]} main drop-off zones. Zone A is for paper and cardboard. Zone B handles glass. Zone C is for plastics. Zone D is for metal and electronics.\n\nPlease sort your materials before arriving. Mixed loads incur a sorting fee of £5. Pre-sorted loads are free for residents.\n\nFor businesses, there's a charge of £15 per tonne for general recycling and £25 per tonne for electronic waste. We offer free collection for businesses generating more than 50 kg per week.\n\nWe also have a reuse shop where items in good condition are sold. Last year, the shop raised over £15,000 for local charities.\n\nHazardous materials like paint, batteries, and chemicals must be taken to the designated area near the entrance. Never put them in the general recycling bins.\n\nTours like this one are available every {o3[0]} at {o4[0]}. They're free, but booking is required.",

    }

    transcript = transcripts.get(key, transcripts["campus"])

    questions = []

    # Q1: completion
    questions.append({
        "id": make_qid(test_num, 2, 1),
        "number": 1,
        "type": "completion",
        "text": "The facility/site was established/opened in ________________.",
        "answer": [o0[0]],
        "max_words": 1
    })

    # Q2: mcq
    questions.append({
        "id": make_qid(test_num, 2, 2),
        "number": 2,
        "type": "mcq",
        "text": "How many items/people does the facility accommodate?",
        "options": [o1[0], o1[1], o1[2], o1[3]],
        "answer": o1[0]
    })

    # Q3: completion
    questions.append({
        "id": make_qid(test_num, 2, 3),
        "number": 3,
        "type": "completion",
        "text": "The number of computers/species/features is ________________.",
        "answer": [o2[0]],
        "max_words": 1
    })

    # Q4: mcq
    questions.append({
        "id": make_qid(test_num, 2, 4),
        "number": 4,
        "type": "mcq",
        "text": "What time does the facility open?",
        "options": [o3[0], o3[1], o3[2], o3[3]],
        "answer": o3[0]
    })

    # Q5: mcq
    questions.append({
        "id": make_qid(test_num, 2, 5),
        "number": 5,
        "type": "mcq",
        "text": "How much does admission cost?",
        "options": [o4[0], o4[1], o4[2], o4[3]],
        "answer": o4[0]
    })

    # Q6: tfng
    questions.append({
        "id": make_qid(test_num, 2, 6),
        "number": 6,
        "type": "tfng",
        "text": "The facility is open seven days a week.",
        "answer": "TRUE"
    })

    # Q7: completion
    questions.append({
        "id": make_qid(test_num, 2, 7),
        "number": 7,
        "type": "completion",
        "text": "Group bookings receive a ________________ discount.",
        "answer": ["20%", "20", "twenty"],
        "max_words": 1
    })

    # Q8: mcq
    questions.append({
        "id": make_qid(test_num, 2, 8),
        "number": 8,
        "type": "mcq",
        "text": "Which of the following is NOT mentioned as available?",
        "options": [o2[0], o2[1], "Helicopter tours", o2[2]],
        "answer": "Helicopter tours"
    })

    # Q9: tfng
    questions.append({
        "id": make_qid(test_num, 2, 9),
        "number": 9,
        "type": "tfng",
        "text": "Photography is completely prohibited on the premises.",
        "answer": "FALSE"
    })

    # Q10: completion
    questions.append({
        "id": make_qid(test_num, 2, 10),
        "number": 10,
        "type": "completion",
        "text": "The tour/session lasts approximately ________________.",
        "answer": [o1[0], "90 minutes", "2 hours", "45 minutes"],
        "max_words": 2
    })

    return {
        "id": "S2",
        "number": 2,
        "title": f"Section 2 — Talk ({title})",
        "instructions": f"Listen to a talk about {title.lower()}. Answer questions 11-20.",
        "transcript": transcript,
        "questions": questions
    }


def gen_section3(test_num, scenario_idx):
    """Academic discussion — 10 questions."""
    title, key, opts_list = S3_SCENARIOS[scenario_idx]
    o0, o1, o2, o3, o4 = opts_list

    transcripts = {
        "energy": f"Tutor: So, James and Maria, let's discuss your joint research project on renewable energy. How far have you got?\n\nJames: Well, we've completed the literature review. We found that most studies focus on solar and wind, but very few examine {o0[0]} in developing countries.\n\nMaria: Yes, and we think that's a significant gap. Our hypothesis is that {o0[0]} could be viable in {o1[0]}, particularly in countries with long coastlines.\n\nTutor: That's an interesting angle. What methodology are you planning to use?\n\nJames: We'll use a {o2[0]} approach. We'll start with quantitative data from government energy reports, then conduct qualitative interviews with local engineers.\n\nMaria: The main challenge is access. We've contacted three universities in the region, but only one has responded so far. We may need to broaden our scope if we don't hear back by next week.\n\nTutor: I'd suggest setting a deadline of Friday. If you don't get responses, consider using publicly available survey data instead. Also, make sure you address the environmental impact — that's often overlooked in energy studies.\n\nJames: Good point. We'll add a section on ecological effects, particularly on marine life.\n\nTutor: And for the presentation, I'd like a {o3[0]} talk with 5 minutes for questions. Use visual aids — charts and diagrams, not just text on slides.\n\nMaria: We'll prepare the slides by {o4[0]} and send them to you for review.\n\nTutor: Excellent. Also, I noticed your bibliography is a bit thin. You should include at least 15 peer-reviewed sources. The library has good databases — I'd recommend starting with Scopus and Web of Science.\n\nJames: We'll do that. Should we include the government reports in the bibliography?\n\nTutor: Yes, but clearly label them as grey literature. Peer-reviewed sources should form the backbone of your references.",

        "marketing": f"Tutor: Right, let's discuss your marketing assignment. You've chosen to analyse a social media campaign. Tell me about your approach.\n\nStudent A: We're looking at how brands target the {o1[0]} age group through {o0[0]}. We think it's the most effective channel for reaching young consumers.\n\nTutor: Interesting. What's your sample size?\n\nStudent B: We surveyed {o2[0]} participants. We used a {o3[0]} approach — online questionnaires followed by focus groups.\n\nTutor: That's a reasonable sample. What are your preliminary findings?\n\nStudent A: About 75% of respondents said they discover new products through {o0[0]}. But only 30% actually make purchases based on those recommendations.\n\nTutor: That's a significant gap. You should explore why that conversion rate is low. Is it trust? Price? Convenience?\n\nStudent B: We're planning to investigate that in the focus groups. We've scheduled three sessions for next week.\n\nTutor: Good. What about the word count?\n\nStudent A: The assignment requires {o4[0]}. We've written about 1,200 so far, so we're on track.\n\nTutor: Make sure you include a clear methodology section and a limitations section. Also, I'd like to see at least 10 academic references — not just industry reports.\n\nStudent B: We have 8 so far. We'll add more.\n\nTutor: And please use Harvard referencing consistently. I noticed some inconsistencies in your draft.\n\nStudent A: We'll fix that. When is the final submission due?\n\nTutor: The deadline is the 15th. I'd like to see a complete draft by the 10th so I can give feedback.",

        "history": f"Tutor: Let's talk about your history essay on the {o0[0]}. You've chosen a very broad topic. How are you narrowing it down?\n\nStudent: I'm focusing on the period between {o1[0]}, specifically looking at technological changes and their social impact.\n\nTutor: That's more manageable. What's your thesis?\n\nStudent: I'm arguing that the {o0[0]} created more social disruption than economic benefit, at least in the short term.\n\nTutor: That's a strong claim. You'll need solid evidence. What sources are you using?\n\nStudent: I'm using a mix of {o3[0]}. I've found some excellent factory records from Manchester and Birmingham.\n\nTutor: Good. Primary sources will strengthen your argument. What about the word count?\n\nStudent: The essay needs to be {o2[0]}. I've written about 3,500 words so far.\n\nTutor: You're making good progress. I'd suggest spending more time on the counter-arguments. You need to address the view that the revolution ultimately benefited society.\n\nStudent: I have a section on that, but it's only 500 words. I'll expand it.\n\nTutor: Also, make sure your conclusion doesn't just summarise — it should offer a synthesis. What's your deadline?\n\nStudent: It's due on {o4[0]}.\n\nTutor: I'd like to see a revised draft by the 10th. And please check your footnotes — the Chicago style requires full citations for the first reference to each source.\n\nStudent: I'll make sure to do that. Should I include a bibliography?\n\nTutor: Yes, a full bibliography is required. List all sources you consulted, even if you didn't cite them directly.",

        "biology": f"Tutor: Let's review your biology lab report on {o0[0]}. How did the experiment go?\n\nStudent: It went well overall. We ran {o1[0]} at {o2[0]} and measured the reaction rate.\n\nTutor: Good. And what were your results?\n\nStudent: The reaction rate was highest at {o2[0]} and decreased significantly above 35 degrees. We think enzyme denaturation is the cause.\n\nTutor: That's consistent with the literature. Did you run a control?\n\nStudent: Yes, we had a control at room temperature. The difference was statistically significant — p-value of 0.02.\n\nTutor: Good. What statistical test did you use?\n\nStudent: We used a {o3[0]} analysis. Our supervisor recommended it for comparing multiple conditions.\n\nTutor: That's appropriate. Now, for the report itself, it should be {o4[0]}. Make sure you include an abstract, introduction, methodology, results, discussion, and conclusion.\n\nStudent: I have most of those. The discussion is a bit short, though.\n\nTutor: The discussion is the most important section. You need to interpret your results, compare them with published studies, and discuss limitations. What were your limitations?\n\nStudent: Mainly the sample size and the fact that we only tested one enzyme concentration.\n\nTutor: Those are valid limitations. Make sure you suggest improvements for future studies. Also, your graphs need clearer labels — include units and error bars.\n\nStudent: I'll fix those. When is the submission deadline?\n\nTutor: It's next Friday at 5 PM. Submit through the online portal.",

        "psychology": f"Tutor: Let's discuss your psychology experiment on {o0[0]}. How's the design coming along?\n\nStudent: I've finalised the methodology. I'm using {o1[0]} participants divided into {o2[0]}: a control group and an experimental group.\n\nTutor: Good. What's the task?\n\nStudent: Participants will complete a memory test. The experimental group will have {o3[0]} of distraction, while the control group works in silence.\n\nTutor: How long is each session?\n\nStudent: Each session lasts {o3[0]}, including instructions and a brief questionnaire afterwards.\n\nTutor: Have you got ethics approval?\n\nStudent: I submitted the application to the {o4[0]} last week. I'm waiting for their response.\n\nTutor: Good — you can't start until that's approved. What's your hypothesis?\n\nStudent: I expect the experimental group to score at least 20% lower than the control group, based on previous research.\n\nTutor: That's a reasonable hypothesis. Make sure you counterbalance the order of tasks to avoid practice effects.\n\nStudent: I hadn't thought of that. I'll add that to the design.\n\nTutor: Also, you need to debrief participants afterwards and give them the right to withdraw their data. That's an ethical requirement.\n\nStudent: I'll include a debriefing sheet. How should I analyse the data?\n\nTutor: Use an independent t-test to compare the two groups. If your data isn't normally distributed, consider a Mann-Whitney U test instead.",

        "engineering": f"Tutor: Let's discuss your engineering project on {o0[0]}. What's your current status?\n\nStudent: We've completed the initial design and cost analysis. The estimated budget is {o1[0]} and the timeline is {o2[0]}.\n\nTutor: That's a tight timeline. Have you identified potential risks?\n\nStudent: Yes, the main risk is material supply. We're planning to use {o3[0]}, which is readily available, but there could be delays.\n\nTutor: Have you considered alternatives?\n\nStudent: We have backup options: {o3[1]} and {o3[2]}. But {o3[0]} is our first choice because of {o4[0]}.\n\nTutor: Good. What about environmental impact?\n\nStudent: We've included a sustainability assessment. The {o3[0]} option has the lowest carbon footprint, which aligns with the project's green objectives.\n\nTutor: Excellent. I'd like to see a more detailed risk management plan. You should assign probability and impact ratings to each risk.\n\nStudent: We'll add that. Should we include a Gantt chart?\n\nTutor: Yes, a Gantt chart is essential for a project of this scale. Also, make sure you have a clear work breakdown structure.\n\nStudent: We have one, but it might need refining. How detailed should it be?\n\nTutor: Each task should be no longer than two weeks. If a task is longer, break it down further. And assign a responsible person to each task.\n\nStudent: Understood. When is the next progress review?\n\nTutor: Let's meet again in two weeks. I'd like to see the updated risk plan and Gantt chart by then.",

        "literature": f"Tutor: Let's discuss your literature review on {o0[0]} literature. How's it progressing?\n\nStudent: I've identified {o1[0]} key sources and I'm organising them {o3[0]}. The review needs to be {o2[0]}.\n\nTutor: Good. What themes have you identified?\n\nStudent: Three main themes: industrialisation and its discontents, the role of women, and the tension between science and religion.\n\nTutor: Those are solid themes. How are you structuring the review?\n\nStudent: I'm using a {o3[0]} structure. Each theme gets its own section, with a synthesis at the end.\n\nTutor: That works well. Make sure you don't just summarise each source — you need to critically evaluate them and show how they relate to each other.\n\nStudent: I'm trying to do that, but it's challenging with so many sources.\n\nTutor: Focus on the most important 10-12 sources for the critical analysis. The rest can be mentioned more briefly.\n\nStudent: That helps. What about the introduction?\n\nTutor: The introduction should set out the scope, explain why the topic matters, and outline your structure. Keep it to about 500 words.\n\nStudent: And the conclusion?\n\nTutor: The conclusion should identify gaps in the literature and suggest directions for future research. It's not just a summary.\n\nStudent: I'll work on that. When is the draft due?\n\nTutor: I'd like a complete draft by {o4[0]}. We'll review it together and then you'll have a week for revisions.",

        "env_sci": f"Tutor: Let's discuss your environmental science field trip. Where are you planning to go?\n\nStudent: We're going to the Lake District to study {o0[0]}. The trip is {o1[0]} and we'll be taking {o2[0]} students.\n\nTutor: Good. What equipment will you need?\n\nStudent: We'll need {o3[0]} for water sampling, pH meters, and turbidity tubes. We're also bringing GPS devices for mapping.\n\nTutor: Have you done a risk assessment?\n\nStudent: Yes, we've completed the risk assessment. The main risks are slips near the water and adverse weather. We've planned alternative indoor activities in case of heavy rain.\n\nTutor: Good. What's the cost per student?\n\nStudent: It's {o4[0]} per student, which includes transport, accommodation, and equipment rental.\n\nTutor: That's reasonable. What's your research question?\n\nStudent: We're investigating whether agricultural runoff affects water quality downstream. We'll take samples at 5 points along the river.\n\nTutor: That's a clear research question. Make sure you have a control site — somewhere upstream of any agricultural activity.\n\nStudent: We've identified a site near the source that should be unaffected.\n\nTutor: Good. You'll also need to consider seasonal variation. One trip gives you a snapshot, but water quality changes throughout the year.\n\nStudent: We're aware of that limitation. We'll note it in our report and suggest a longitudinal study for future research.\n\nTutor: Perfect. Make sure everyone has appropriate clothing — waterproofs and sturdy boots are essential.",

        "business": f"Tutor: Let's discuss your business plan presentation. What's your business idea?\n\nStudent: We're proposing a {o0[0]} that connects local farmers directly with consumers. The startup cost is {o1[0]}.\n\nTutor: Who's your target market?\n\nStudent: Primarily the {o1[1]} demographic — young professionals who value fresh, local produce.\n\nTutor: How will you reach them?\n\nStudent: Mainly through {o2[0]} and partnerships with local gyms and health food stores.\n\nTutor: What about competition?\n\nStudent: There are two similar services in the area, but neither focuses exclusively on local farms. That's our differentiator.\n\nTutor: Good. What's your revenue model?\n\nStudent: We charge a 15% commission on each transaction, plus a £5 monthly subscription for premium features.\n\nTutor: Have you done financial projections?\n\nStudent: Yes. We project breaking even in month 14 and reaching £50,000 monthly revenue by month 24.\n\nTutor: Those are optimistic projections. What's your contingency if growth is slower?\n\nStudent: We have a 6-month runway from our initial funding. If needed, we can reduce marketing spend and extend the runway to 9 months.\n\nTutor: Good. For the presentation, you'll have {o3[0]}. Make it concise — focus on the problem, solution, market size, and financials.\n\nStudent: We'll prepare a 12-slide deck. Should we include a demo?\n\nTutor: Yes, a short demo of the app would strengthen your pitch. Keep it to 2 minutes.",

        "architecture": f"Tutor: Let's review your architecture studio project. You're designing a {o0[0]} building with a {o1[0]} approach?\n\nStudent: Yes. I'm focusing on sustainability — using local materials and passive heating strategies.\n\nTutor: Good. What's your site?\n\nStudent: It's a corner plot in the city centre, 30 by 40 metres. The south-facing aspect is ideal for solar gain.\n\nTutor: Have you done a site analysis?\n\nStudent: Yes, I've completed a full {o3[0]} including sun paths, wind patterns, and pedestrian flows.\n\nTutor: Good. What scale are your drawings?\n\nStudent: I'm working at {o2[0]} for the site plan and 1:50 for floor plans and sections.\n\nTutor: That's appropriate. What about the model?\n\nStudent: I'm building a physical model at 1:100 and a digital model for rendering.\n\nTutor: Make sure the physical model shows the context — the surrounding buildings are important for understanding the scale.\n\nStudent: I'll add those. How much detail should the model have?\n\nTutor: Focus on the form and massing. You don't need interior details at this stage, but show the facade treatment.\n\nStudent: I'll work on that. When is the next critique?\n\nTutor: The interim review is in {o2[1]}. You should have your site analysis, concept diagrams, and a massing model ready.\n\nStudent: I'll be ready. Should I prepare a presentation?\n\nTutor: Yes, a 10-minute presentation. Keep it visual — diagrams and images, not text.",

        "sociology": f"Tutor: Let's discuss your sociology survey project on {o0[0]}. How's it going?\n\nStudent: I've designed the questionnaire and I'm planning to survey {o1[0]} respondents.\n\nTutor: What sampling method are you using?\n\nStudent: I'm using {o2[0]} sampling — I'll distribute the survey through community groups and social media.\n\nTutor: That could introduce bias. Have you considered stratified sampling to ensure demographic representation?\n\nStudent: I hadn't, but that's a good point. I'll revise the sampling strategy.\n\nTutor: What's your response rate target?\n\nStudent: I'm hoping for {o3[0]}, which would give me about 180 usable responses.\n\nTutor: That's a reasonable target. What are your main research questions?\n\nStudent: I'm looking at how housing conditions affect social mobility, controlling for income and education.\n\nTutor: That's a well-defined question. Make sure your questionnaire includes validated scales — don't invent your own measures if established ones exist.\n\nStudent: I'm using the Housing Quality Index and the Social Mobility Index from the ONS.\n\nTutor: Excellent. What about ethics?\n\nStudent: I've submitted the ethics application. The main concern is data anonymity — I'm not collecting any identifying information.\n\nTutor: Good. The report should be {o4[0]}. Make sure you include a methodology section, results, and a critical discussion.\n\nStudent: I'll start writing once I've collected the data. When is the deadline?\n\nTutor: The final submission is in 6 weeks. I'd like to see a draft of your methodology section by next week.",

        "chemistry": f"Tutor: Let's discuss your chemistry research on {o0[0]}. What stage are you at?\n\nStudent: I've completed the literature review and I'm now setting up the experiments. The project will run for {o1[0]}.\n\nTutor: Good. What technique are you using for analysis?\n\nStudent: I'm primarily using {o2[0]}, but I'll also use mass spectrometry for molecular weight determination.\n\nTutor: That's a good combination. How many samples are you testing?\n\nStudent: I'm testing {o3[0]} samples — 5 controls and 15 experimental samples with varying concentrations.\n\nTutor: That should give you enough data for statistical analysis. What's your hypothesis?\n\nStudent: I expect the {o0[0]} to show increased stability at higher concentrations, based on the literature.\n\nTutor: Interesting. Have you considered temperature effects?\n\nStudent: Yes, I'm testing at three temperatures: 25, 37, and 50 degrees Celsius.\n\nTutor: Good. Make sure you calibrate your instruments before each session. And keep a detailed lab notebook — every observation should be recorded.\n\nStudent: I've been keeping notes. Should I include the raw data in my report?\n\nTutor: No, put the raw data in an appendix. The main report should have summarised data in tables and graphs.\n\nStudent: Understood. When is the next progress meeting?\n\nTutor: Let's meet on {o4[0]}. I'd like to see your preliminary results and your updated methodology.\n\nStudent: I'll have the first set of results by then. The report is due at the end of the semester, right?\n\nTutor: Yes, the final report is due at the end of the semester. It should be 3,000-4,000 words.",

        "education": f"Tutor: Let's reflect on your teaching practicum. Where were you placed?\n\nStudent: I was at a {o0[0]} for {o1[0]}. I was assigned to {o2[0]}.\n\nTutor: How did you find the experience?\n\nStudent: It was challenging but rewarding. I taught 12 lessons and observed 20 more.\n\nTutor: What teaching strategies did you use?\n\nStudent: I tried several approaches: direct instruction, {o3[0]}, and project-based learning. The {o3[0]} worked best for engagement.\n\nTutor: That's consistent with current pedagogical research. What challenges did you face?\n\nStudent: Classroom management was the biggest challenge, especially with larger classes of 30+ students.\n\nTutor: That's a common challenge. What strategies did you use to manage behaviour?\n\nStudent: I used a reward system and clear routines. It took about two weeks to establish, but it made a big difference.\n\nTutor: Good. For your reflection report, you need {o4[0]}. Make sure you link your observations to educational theory.\n\nStudent: I'm using Kolb's experiential learning cycle as my framework. Is that appropriate?\n\nTutor: Yes, that's a solid choice. Make sure you cover all four stages: concrete experience, reflective observation, abstract conceptualisation, and active experimentation.\n\nStudent: I'll make sure to do that. Should I include lesson plans?\n\nTutor: Include two representative lesson plans in the appendix, with your reflections on what worked and what didn't.\n\nStudent: I'll select the most informative ones. When is the report due?\n\nTutor: The report is due in three weeks. I'm happy to review a draft before then.",

        "geography": f"Tutor: Let's discuss your geography fieldwork on {o0[0]}. Where are you planning to go?\n\nStudent: I'm going to the Norfolk coast to study {o0[0]}. The trip is {o1[0]} and I'm taking {o3[0]} students.\n\nTutor: Good. What methods will you use?\n\nStudent: I'll use {o2[0]} to map the coastline, beach profiling to measure changes, and sediment analysis.\n\nTutor: That's a comprehensive approach. Have you done a risk assessment?\n\nStudent: Yes, the main risks are tides and cliff instability. I've checked the tide tables and we'll avoid the base of cliffs.\n\nTutor: Good. What's your research question?\n\nStudent: I'm investigating the rate of coastal erosion and the effectiveness of sea defences at two contrasting sites.\n\nTutor: That's a clear question. Make sure you collect data at both sites using the same methodology so they're comparable.\n\nStudent: I will. I'm measuring cliff retreat using historical maps and GPS coordinates.\n\nTutor: Excellent. What's the cost per student?\n\nStudent: It's {o4[0]} per student, including transport and accommodation at a field studies centre.\n\nTutor: That's reasonable. For the report, I'd like to see a methodology section, results with maps and graphs, and a discussion that evaluates the effectiveness of the sea defences.\n\nStudent: I'll structure it that way. When is the report due?\n\nTutor: The report is due three weeks after the field trip. I'd like to see your data before you start writing.",

        "music": f"Tutor: Let's discuss your music composition for {o0[0]}. What's your concept?\n\nStudent: I'm composing a {o0[0]} in {o3[0]} with {o1[0]}. Each movement is about {o2[0]}.\n\nTutor: That's an ambitious project. What's the emotional arc across the movements?\n\nStudent: The first movement is turbulent and dramatic, the second is lyrical and calm, and the third is energetic and triumphant.\n\nTutor: Good. That gives the piece a clear narrative. What instrumentation are you using?\n\nStudent: For the {o0[0]}, I'm using two violins, a viola, and a cello. I'm also exploring extended techniques like pizzicato and col legno.\n\nTutor: That's a traditional ensemble with modern touches. Have you thought about the harmonic language?\n\nStudent: I'm using a mix of tonal and atonal sections. The first movement is quite dissonant, while the second is more consonant.\n\nTutor: That contrast will be effective. Make sure you notate everything clearly — especially the extended techniques. Use performance notes to explain any non-standard notation.\n\nStudent: I'll add a performance notes page. Should I include a recording?\n\nStudent: I'll have a MIDI realisation. Is that acceptable?\n\nTutor: A MIDI realisation is fine for the submission, but I'd encourage you to organise a live performance if possible.\n\nStudent: I'll try. When is the final submission?\n\nTutor: The score and programme note are due {o4[0]}. The programme note should be 200-300 words explaining the piece.\n\nStudent: I'll start drafting the programme note. How long should the score be?\n\nTutor: The score should be fully notated with all performance markings. Expect about 15-20 pages.",
    }

    transcript = transcripts.get(key, transcripts["energy"])

    questions = []

    # Q1: mcq
    questions.append({
        "id": make_qid(test_num, 3, 1),
        "number": 1,
        "type": "mcq",
        "text": "What is the main topic of the project?",
        "options": [o0[0], o0[1], o0[2], o0[3]],
        "answer": o0[0]
    })

    # Q2: completion
    questions.append({
        "id": make_qid(test_num, 3, 2),
        "number": 2,
        "type": "completion",
        "text": "The project focuses on ________________.",
        "answer": [o1[0]],
        "max_words": 2
    })

    # Q3: mcq
    questions.append({
        "id": make_qid(test_num, 3, 3),
        "number": 3,
        "type": "mcq",
        "text": "What methodology/approach is being used?",
        "options": [o2[0], o2[1], o2[2], o2[3]],
        "answer": o2[0]
    })

    # Q4: completion
    questions.append({
        "id": make_qid(test_num, 3, 4),
        "number": 4,
        "type": "completion",
        "text": "The presentation/report should be ________________.",
        "answer": [o3[0]],
        "max_words": 2
    })

    # Q5: mcq
    questions.append({
        "id": make_qid(test_num, 3, 5),
        "number": 5,
        "type": "mcq",
        "text": "When is the deadline/draft due?",
        "options": [o4[0], o4[1], o4[2], o4[3]],
        "answer": o4[0]
    })

    # Q6: tfng
    questions.append({
        "id": make_qid(test_num, 3, 6),
        "number": 6,
        "type": "tfng",
        "text": "The tutor suggests expanding the scope of the project.",
        "answer": "TRUE"
    })

    # Q7: mcq
    questions.append({
        "id": make_qid(test_num, 3, 7),
        "number": 7,
        "type": "mcq",
        "text": "What does the tutor recommend adding to the project?",
        "options": ["More references", "A risk assessment", "Visual aids", "All of the above"],
        "answer": "All of the above"
    })

    # Q8: completion
    questions.append({
        "id": make_qid(test_num, 3, 8),
        "number": 8,
        "type": "completion",
        "text": "The student needs at least ________________ academic references.",
        "answer": ["10", "ten", "15", "fifteen"],
        "max_words": 1
    })

    # Q9: tfng
    questions.append({
        "id": make_qid(test_num, 3, 9),
        "number": 9,
        "type": "tfng",
        "text": "The student has already completed all the required sections.",
        "answer": "FALSE"
    })

    # Q10: mcq
    questions.append({
        "id": make_qid(test_num, 3, 10),
        "number": 10,
        "type": "mcq",
        "text": "What is the main challenge identified?",
        "options": ["Time management", "Data collection", "Funding", "Literature review"],
        "answer": "Data collection"
    })

    return {
        "id": "S3",
        "number": 3,
        "title": f"Section 3 — Academic Discussion ({title})",
        "instructions": f"Listen to a discussion about {title.lower()}. Answer questions 21-30.",
        "transcript": transcript,
        "questions": questions
    }


def gen_section4(test_num, scenario_idx):
    """Academic lecture — 10 questions."""
    title, key, opts_list = S4_SCENARIOS[scenario_idx]
    o0, o1, o2, o3, o4 = opts_list

    transcripts = {
        "climate": f"Good morning, everyone. Today's lecture continues our series on environmental science, and we'll be examining the impact of climate change on coastal cities.\n\nLet's start with some context. The Intergovernmental Panel on Climate Change, or IPCC, projects that global temperatures will rise by {o1[0]} by {o0[0]}. This may not sound like much, but the consequences for coastal regions are profound.\n\nCurrently, about {o2[0]} of the world's population lives within 100 kilometres of a coast. As sea levels rise, these communities face increased flooding, erosion, and saltwater intrusion into freshwater supplies.\n\nLet's look at a specific example. {o3[0]} has been a pioneer in flood management. After the devastating floods of 1953, the Dutch government invested billions in the Delta Works — a system of dams, sluices, and barriers that protects the low-lying areas.\n\nBut not all countries have the resources of the Netherlands. {o3[1]}, for instance, has a population of 160 million people living in a delta region that's barely above sea level. A one-metre rise in sea level would displace approximately 15 million people.\n\nThe economic impact is also staggering. By {o4[0]}, the cost of coastal damage could reach $1 trillion per year globally. This includes damage to infrastructure, loss of agricultural land, and the cost of relocation.\n\nAdaptation strategies fall into three categories: protect, accommodate, and retreat. Protection involves building sea walls and barriers. Accommodation means adapting buildings and infrastructure to withstand flooding. Retreat — the most drastic option — involves moving communities inland.\n\nThe challenge is that many coastal cities are sinking as well. This is called subsidence. In Jakarta, the ground is sinking by 25 centimetres per year in some areas, far faster than sea level rise.\n\nFor next week, I'd like you to read Chapter 12 of the textbook and prepare a short summary of one adaptation strategy used by a coastal city of your choice.",

        "english_lang": f"Good morning. Today we're going to trace the history of the English language from its origins to the present day.\n\nEnglish is a West Germanic language that originated from dialects spoken by Germanic tribes — the Angles, Saxons, and Jutes — who arrived in Britain in the {o0[0]}. These tribes spoke similar but distinct dialects that gradually merged into what we now call Old English.\n\nThe next major influence came in {o1[0]}, when William the Conqueror invaded England. For the next 300 years, {o2[0]} was the language of the ruling class, the law, and administration. During this period, English absorbed thousands of {o2[0]} words, particularly in areas like law, government, and the arts.\n\nBy the 14th century, English re-emerged as the dominant language, but it had been transformed. We call this Middle English — the language of Chaucer. The Great Vowel Shift, which began in the 15th century, further changed pronunciation.\n\nThe invention of the printing press by William Caxton in 1476 standardised English spelling. But because spelling was fixed before pronunciation settled, we're left with many irregularities that persist today.\n\nThe Renaissance brought another wave of borrowing, particularly from {o2[1]}. Words like 'democracy', 'philosophy', and 'architecture' entered the language during this period.\n\nBy the time of {o3[0]}, English had a vocabulary of approximately {o4[0]} words. Shakespeare alone coined or popularised over 1,700 words.\n\nToday, English has the largest vocabulary of any language, with over 170,000 words in current use. It's the official language of 67 countries and is spoken by approximately 1.5 billion people worldwide.\n\nFor next week, please read the chapter on Old English phonology and be prepared to discuss the influence of Norse on English vocabulary.",

        "renewable": f"Good afternoon. Today's lecture focuses on renewable energy technologies and their role in combating climate change.\n\nThe International Energy Agency estimates that by {o0[0]}, renewable energy could account for {o2[0]} of global electricity generation. This represents a dramatic shift from the current 25%.\n\nLet's examine the main types. {o1[0]} energy has seen the most rapid growth. The cost of solar panels has dropped by 90% since 2010, making it competitive with fossil fuels in many markets.\n\nWind energy is the second-largest contributor. Offshore wind farms, in particular, have enormous potential. The UK currently generates {o2[2]} of its electricity from wind.\n\nHydroelectric power remains the largest source of renewable energy globally, accounting for about 16% of electricity production. However, large dams have significant environmental impacts, including habitat destruction and displacement of communities.\n\nGeothermal energy, while less well-known, provides baseload power — meaning it's available 24/7. Iceland generates nearly 100% of its electricity from geothermal and hydro sources.\n\nThe history of modern renewable energy dates back to the {o3[0]}, when the oil crisis prompted investment in alternatives. The first commercial wind farm was built in California in 1981.\n\nLooking ahead, the International Renewable Energy Agency projects that {o4[0]} of the world's energy could come from renewables by 2050. But this requires $22 trillion in investment.\n\nThe main challenges are intermittency and storage. Solar and wind are variable, so we need better batteries. Lithium-ion battery costs have fallen by 85% since 2010, but we need further breakthroughs.\n\nFor next week, read the chapter on grid integration and prepare to discuss the role of smart grids in managing renewable energy.",

        "psych_learning": f"Good morning. Today we'll explore the psychology of learning, focusing on how memory works and how we can learn more effectively.\n\nLet's start with a foundational concept: the forgetting curve. In {o0[0]}, Hermann Ebbinghaus published his pioneering research on memory. He found that we forget approximately 50% of new information within {o1[0]}, and up to 70% within a week.\n\nThis discovery led to the concept of spaced repetition. Instead of cramming, reviewing material at increasing intervals dramatically improves retention. The optimal intervals are: first review after {o1[0]}, second after 24 hours, third after a week, and fourth after a month.\n\nAnother key concept is the 'magical number seven'. In {o3[0]}, George Miller proposed that our short-term memory can hold approximately {o2[0]} items at a time. This is why phone numbers are typically 7 digits long.\n\nBut we can work around this limit through 'chunking' — grouping information into meaningful units. For example, the string 'FBI-CIA-NSA' is easier to remember than nine random letters.\n\nResearch also shows that learning styles matter. The VARK model identifies four main styles: {o4[0]}. However, recent studies suggest that matching teaching to learning styles has limited effect on outcomes.\n\nWhat does work is active recall — the practice of retrieving information from memory. Studies show that testing yourself is more effective than re-reading notes. Even a single {o3[1]} test can improve long-term retention by 50%.\n\nInterleaving — mixing different types of problems — also enhances learning. Rather than studying one topic at a time, alternating between subjects forces deeper processing.\n\nFor next week, read Chapter 7 on cognitive load theory and design a study plan using spaced repetition.",

        "urban": f"Good morning. Today's lecture examines urban planning and the concept of smart cities.\n\nThe United Nations projects that {o0[0]} of the world's population will live in urban areas by {o1[0]}. This rapid urbanisation presents enormous challenges for infrastructure, housing, and the environment.\n\nA smart city uses technology and data to improve quality of life. The key components are {o2[0]} that monitor everything from traffic flow to air quality. {o3[0]} is often cited as a model smart city, with its integrated transport system and extensive sensor network.\n\nLet's look at transportation. Smart cities prioritise public transport and active travel. In {o3[0]}, the electronic road pricing system charges drivers based on when and where they drive. Since its introduction in 1975, traffic has decreased by {o4[0]}.\n\nEnergy management is another critical area. Smart grids use real-time data to balance supply and demand. In {o3[1]}, the smart grid has reduced energy consumption by {o4[1]}.\n\nWater management is equally important. Smart water systems detect leaks, monitor quality, and optimise distribution. {o3[2]} has implemented a smart water system that has reduced water loss from 30% to just 5%.\n\nHowever, smart cities raise privacy concerns. The collection of vast amounts of data — from CCTV cameras, location tracking, and smart meters — creates risks of surveillance and data misuse.\n\nThere's also the issue of the digital divide. Not all residents have access to smartphones or the internet. In {o3[3]}, 15% of households lack internet access, which can exclude them from smart city services.\n\nFor next week, read the case study on {o3[0]}'s smart nation initiative and prepare three recommendations for a smart city project.",

        "economics": f"Good morning. Today we'll examine the economics of globalisation, its drivers, and its consequences.\n\nGlobalisation as we know it began in the {o0[0]}, when the fall of the Berlin Wall and the rise of the internet created a truly global marketplace. Trade barriers fell, and supply chains stretched across continents.\n\nThe results have been dramatic. Since 1990, global trade has grown three times faster than global GDP. An estimated {o1[0]} people have been lifted out of extreme poverty, mostly in {o2[0]} and India.\n\nBut globalisation has also created winners and losers. While {o2[0]} has prospered, manufacturing workers in developed countries have faced job losses and wage stagnation. This has fuelled political backlash in many Western nations.\n\nThe {o3[0]} financial crisis exposed the risks of interconnected economies. A housing crisis in the United States triggered a global recession. The lesson was that financial contagion can spread rapidly across borders.\n\nMore recently, the COVID-19 pandemic revealed the fragility of global supply chains. When factories in {o2[0]} shut down, production ground to a halt worldwide. This has led to a rethinking of just-in-time manufacturing.\n\nGlobalisation has also accelerated inequality. The richest 1% now own more than 50% of global wealth. In developing countries, the Gini coefficient — a measure of inequality — has risen by {o4[0]} since 1990.\n\nLooking ahead, several trends are reshaping globalisation. Trade in services is growing faster than trade in goods. Digital trade — including e-commerce, streaming, and cloud services — is expected to reach $5 trillion by 2030.\n\nClimate change is also affecting trade patterns. Carbon border taxes, like the EU's CBAM, will impose costs on carbon-intensive imports. This could reshape global supply chains.\n\nFor next week, read Chapter 15 on trade theory and prepare an argument for or against free trade.",

        "marine": f"Good morning. Today's lecture focuses on marine biology, specifically coral reef ecosystems and the threats they face.\n\nCoral reefs cover less than 1% of the ocean floor, but they support approximately 25% of all marine species. They're often called the rainforests of the sea.\n\nThe Great Barrier Reef, located off the coast of {o3[0]}, is the world's largest coral reef system. It stretches over 2,300 kilometres and is visible from space. It was designated a UNESCO World Heritage Site in 1981.\n\nBut coral reefs worldwide are in crisis. Scientists estimate that {o0[0]} of coral reefs have been lost since the 1950s. Without action, we could lose {o1[0]} of remaining reefs by {o2[0]}.\n\nThe primary threat is climate change. When water temperatures rise by just {o4[0]}, corals expel the algae that live in their tissues. This is called coral bleaching. If temperatures remain high, the coral dies.\n\nThe first major global bleaching event occurred in 1998, affecting 16% of the world's reefs. The 2016 bleaching event was even more devastating — it affected the northern section of the Great Barrier Reef, killing {o1[1]} of corals in that area.\n\nOcean acidification is another threat. As the ocean absorbs CO2, the water becomes more acidic. This makes it harder for corals to build their skeletons. Since the Industrial Revolution, ocean pH has dropped by 0.1 — a 30% increase in acidity.\n\n{o3[1]} sits within the Coral Triangle, the most biodiverse marine region on Earth. It has over 600 coral species, compared to about 70 in the Caribbean.\n\nConservation efforts include marine protected areas, coral farming, and selective breeding of heat-resistant corals. The '50 Reefs' initiative aims to protect 50 coral reefs that are most likely to survive climate change.\n\nFor next week, read the paper on coral resilience and prepare a summary of one conservation strategy.",

        "sleep": f"Good morning. Today's lecture explores the science of sleep — one of the most essential yet poorly understood biological processes.\n\nThe average adult needs {o0[0]} of sleep per night, but surveys show that 35% of adults regularly get less than 7 hours. Chronic sleep deprivation has been linked to obesity, diabetes, cardiovascular disease, and cognitive decline.\n\nSleep occurs in cycles, each lasting approximately {o1[0]}. A full night's sleep includes 4-6 cycles. Each cycle has distinct stages: light sleep, deep sleep, and REM — rapid eye movement — sleep.\n\nREM sleep was discovered in {o2[0]} by researchers who noticed that sleeping subjects' eyes moved rapidly beneath their eyelids. During REM, the brain is almost as active as when awake. This is when most dreaming occurs.\n\nDeep sleep, also called slow-wave sleep, is crucial for physical recovery. During this stage, the body releases growth hormone, repairs tissues, and strengthens the immune system.\n\nThe circadian rhythm — our internal 24-hour clock — is controlled by the suprachiasmatic nucleus in the brain. This tiny structure responds to light, which is why {o4[0]} from screens can disrupt sleep.\n\nAbout {o3[0]} of people suffer from insomnia — difficulty falling or staying asleep. Cognitive behavioural therapy for insomnia, or CBT-I, is more effective than medication in the long term.\n\nSleep also plays a critical role in memory. During sleep, the brain consolidates what we've learned. Studies show that students who sleep after studying perform {o3[1]} better on tests than those who don't.\n\nInterestingly, humans are the only species that deliberately deprive themselves of sleep. All other animals sleep when they need to.\n\nFor next week, read Chapter 8 on sleep disorders and prepare a sleep diary for one week.",

        "archaeology": f"Good morning. Today's lecture highlights some of the most significant archaeological discoveries of the 21st century.\n\nLet's start with King Tutankhamun. His tomb was discovered in {o0[0]} by Howard Carter in the Valley of the Kings. The tomb contained over 5,000 artefacts, including the famous gold mask. Recent analysis using CT scans has revealed that Tutankhamun died at about age 19, around {o1[0]}.\n\nIn {o2[0]}, archaeologists discovered a massive tomb in Amphipolis, Greece. The tomb, dating to the 4th century BC, is the largest ever found in Greece. It contained intricate mosaics and marble sculptures.\n\nOne of the most exciting recent discoveries was made in {o2[1]}. Using ground-penetrating radar, researchers found a void in the Great Pyramid of Giza. This cavity, about {o3[0]}, is the first major inner structure discovered since the 19th century.\n\nIn 2019, a team discovered a {o3[1]} mosaic in London. Dating to around AD 200, it's one of the finest Roman mosaics ever found in Britain. It was uncovered during construction work.\n\nUnderwater archaeology has also yielded remarkable finds. In 2021, divers found a {o3[2]} shipwreck off the coast of Egypt. The ship, dating to the 2nd century BC, was carrying amphorae and bronze coins.\n\nIn {o2[2]}, archaeologists in Peru discovered a 3,000-year-old temple. The site, called Pacopampa, contains intricate carvings and a large ceremonial plaza.\n\nPerhaps the most controversial discovery is the 'hobbit' — Homo floresiensis. Found in Indonesia in 2003, these small hominins stood only {o4[0]} tall and lived as recently as 50,000 years ago.\n\nTechnology is transforming archaeology. LiDAR — light detection and ranging — allows researchers to see through jungle canopy. In 2018, LiDAR revealed a vast Mayan civilisation in Guatemala with over 60,000 structures.\n\nFor next week, read the article on digital archaeology and prepare a short presentation on one technological advancement in the field.",

        "ai": f"Good morning. Today's lecture provides an overview of artificial intelligence — its history, current state, and future directions.\n\nThe term 'artificial intelligence' was coined in {o0[0]} at the Dartmouth Conference. The early pioneers, including John McCarthy and Marvin Minsky, were optimistic that machines would soon match human intelligence.\n\nProgress, however, was slower than expected. The field experienced several 'AI winters' — periods of reduced funding and interest. The first lasted from 1974 to 1980, and the second from 1987 to 1993.\n\nThe modern AI boom began with {o3[0]}, a subset of AI that uses neural networks with many layers. The breakthrough came in 2012, when a deep learning system called AlexNet won the ImageNet competition by a wide margin.\n\nNatural language processing, or {o3[1]}, has seen remarkable progress. Large language models can now generate human-like text, translate between languages, and answer complex questions.\n\nThe economic impact is significant. By {o1[0]}, AI is projected to contribute $15.7 trillion to the global economy. About {o2[0]} of jobs could be automated, though many new jobs will also be created.\n\nHowever, AI raises serious ethical concerns. Bias in training data can lead to discriminatory outcomes. A 2019 study found that facial recognition systems were {o2[1]} more likely to misidentify darker-skinned faces.\n\nThe development of artificial general intelligence — AI that matches or exceeds human intelligence across all domains — remains a distant goal. Some experts predict it could arrive by {o4[0]}, while others believe it's decades away.\n\nRegulation is struggling to keep pace. The EU's AI Act, proposed in 2021, is the first comprehensive legal framework for AI. It classifies AI systems by risk level, with strict rules for high-risk applications.\n\nFor next week, read the paper on AI ethics and prepare a position paper on the regulation of autonomous weapons.",

        "nutrition": f"Good morning. Today's lecture examines nutrition and public health, focusing on dietary guidelines and their impact on population health.\n\nThe World Health Organization recommends that adults consume approximately {o0[0]} calories per day. However, actual needs vary based on age, gender, and activity level.\n\nSugar is a major concern. The WHO recommends limiting added sugar to less than {o4[0]} of total daily calories — about {o1[0]} for an average adult. Yet the average person in developed countries consumes nearly three times that amount.\n\nThe '5-a-day' campaign encourages eating at least {o2[0]} of fruit and vegetables. Research shows that meeting this target reduces the risk of heart disease by {o2[1]} and stroke by 26%.\n\nHowever, recent studies suggest that even more is better. A 2017 study published in the {o3[0]} found that eating 10 portions per day was associated with a 31% reduction in premature death.\n\nSalt intake is another concern. The recommended daily limit is {o4[1]}, but the global average is nearly double that. High salt consumption is linked to hypertension, which affects 1.13 billion people worldwide.\n\nThe Mediterranean diet is consistently ranked as one of the healthiest. It emphasises olive oil, fish, vegetables, and whole grains. Studies show it reduces cardiovascular risk by 30%.\n\nUltra-processed foods now make up {o2[2]} of the average diet in the UK and US. These foods are linked to obesity, cancer, and all-cause mortality.\n\nMalnutrition isn't just about overconsumption. Globally, 821 million people are undernourished. Iron deficiency affects {o2[3]} of children under 5, leading to impaired cognitive development.\n\nFor next week, read Chapter 10 on nutritional epidemiology and analyse your own diet for one day using the guidelines discussed.",

        "blackhole": f"Good morning. Today's lecture explores one of the most fascinating objects in the universe: black holes.\n\nThe concept of black holes was first proposed in {o0[0]} by Karl Schwarzschild, who found that Einstein's equations of general relativity allowed for regions where gravity is so strong that nothing — not even light — can escape.\n\nFor decades, black holes remained theoretical. The first strong evidence came in {o1[0]} with the discovery of Cygnus X-1, an X-ray source in the constellation Cygnus. Astronomers determined it was a black hole orbiting a companion star.\n\nIn {o2[0]}, the Event Horizon Telescope — a network of radio telescopes — captured the first image of a black hole. The image showed the supermassive black hole at the centre of galaxy M87, located 55 million light-years away.\n\nThe black hole at the centre of our own galaxy, Sagittarius A*, has a mass of approximately {o3[0]} solar masses. Stars orbiting it travel at extraordinary speeds — S2, one such star, reaches speeds of 7,650 km/s at its closest approach.\n\nIn {o4[0]}, Stephen Hawking proposed that black holes are not entirely black. Due to quantum effects near the event horizon, they emit radiation — now called Hawking radiation. This means black holes slowly lose mass and eventually evaporate.\n\nHowever, for a stellar-mass black hole, this evaporation takes about 10^67 years — far longer than the current age of the universe.\n\nBlack holes come in different sizes. Stellar black holes form from collapsing stars and have masses up to about 100 solar masses. Supermassive black holes, found at the centres of galaxies, can have billions of solar masses.\n\nIn 2015, the LIGO observatory detected gravitational waves from two merging black holes — confirming another prediction of Einstein's general relativity. Since then, over 90 mergers have been detected.\n\nFor next week, read the chapter on general relativity and prepare to discuss the information paradox.",

        "cbt": f"Good morning. Today's lecture introduces cognitive behavioural therapy, or CBT — one of the most widely used and evidence-based forms of psychotherapy.\n\nCBT was developed in the {o0[0]} by Aaron {o3[0]}, a psychiatrist who observed that depression was often maintained by negative thought patterns. Around the same time, Albert Ellis developed a similar approach called Rational Emotive Behaviour Therapy.\n\nThe core principle of CBT is that our thoughts, feelings, and behaviours are interconnected. By changing negative thought patterns, we can change how we feel and act.\n\nA typical course of CBT lasts {o1[0]}, with weekly sessions of about 50 minutes. Research shows that CBT is effective for a wide range of conditions, including depression, anxiety, PTSD, and eating disorders.\n\nFor depression, CBT is as effective as antidepressant medication. About {o2[0]} of patients show significant improvement. When combined with medication, the response rate increases to 70%.\n\nCBT involves several key techniques. Cognitive restructuring helps patients identify and challenge distorted thoughts. Behavioural activation encourages patients to engage in activities they've been avoiding. Exposure therapy gradually confronts feared situations.\n\nOne of the strengths of CBT is its structured, goal-oriented approach. Each session has an agenda, and patients receive homework — typically spending {o3[1]} per day on exercises.\n\nCBT has been adapted for different populations. CBT for insomnia, or CBT-I, is now the first-line treatment for chronic sleep problems. Mindfulness-based cognitive therapy, or MBCT, combines CBT with meditation and reduces relapse rates in recurrent depression by 43%.\n\nHowever, CBT isn't for everyone. Critics argue it's too focused on the present and doesn't address underlying issues. Others note that it requires a certain level of cognitive ability and motivation.\n\nFor next week, read the case study in Chapter 6 and identify the cognitive distortions in the patient's narrative.",

        "trade_routes": f"Good morning. Today's lecture traces the history of major trade routes and their impact on civilisations.\n\nThe {o0[0]} was perhaps the most famous trade route in history. Stretching approximately {o2[0]}, it connected China to the Mediterranean from the {o1[0]} until the {o3[0]}.\n\nThe Silk Road wasn't a single road but a network of routes. Goods, ideas, and diseases travelled along it. Silk, spices, and porcelain moved west, while gold, glass, and wool moved east.\n\nThe Silk Road also facilitated cultural exchange. Buddhism spread from India to China via these routes. The Islamic world received paper-making technology from China in the 8th century, which revolutionised knowledge transmission.\n\nThe fall of Constantinople in {o3[0]} disrupted overland trade routes, prompting European powers to seek sea routes to Asia. This led to the Age of Discovery.\n\nThe Spice Route was another major network. Spices like pepper, cinnamon, and nutmeg were worth their weight in gold. The Portuguese established a sea route to India in 1498, breaking the Venetian monopoly.\n\nIn the {o4[0]}, the Hanseatic League dominated trade in Northern Europe. This confederation of merchant guilds controlled commerce from London to Novgorod.\n\nThe Trans-Saharan trade route connected West Africa to North Africa and the Mediterranean. Gold, salt, and slaves were the main commodities. The Mali Empire grew wealthy from this trade — Mansa Musa, its 14th-century ruler, is often cited as the richest person in history.\n\nMaritime trade routes in the Indian Ocean were even more significant. By the 15th century, Chinese treasure fleets under Admiral Zheng He reached as far as East Africa.\n\nFor next week, read the chapter on the economic impact of trade routes and prepare a map showing the major routes discussed.",

        "water": f"Good morning. Today's lecture addresses one of the most critical challenges of the 21st century: water conservation and management.\n\nWater covers 71% of the Earth's surface, but only {o0[0]} is freshwater. Of that, only {o1[0]} is accessible — the rest is locked in glaciers and ice caps.\n\nAgriculture is by far the largest consumer, using approximately {o2[0]} of global freshwater. Producing 1 kilogram of beef requires about 15,000 litres of water, while 1 kilogram of wheat needs only 1,500 litres.\n\nThe water crisis is already here. By {o3[0]}, the UN projects that half the world's population will live in water-stressed areas. Currently, {o2[1]} of people lack access to safely managed drinking water.\n\nClimate change is exacerbating the problem. Changing rainfall patterns, more frequent droughts, and shrinking glaciers threaten water supplies. The Himalayan glaciers, which feed rivers serving 1.5 billion people, are retreating rapidly.\n\nDesalination is one technological solution. Modern reverse osmosis plants can produce freshwater from seawater, but it's energy-intensive. The cost has fallen from $20 per cubic metre in the 1970s to about $0.50 today.\n\nWater recycling is another approach. Singapore's NEWater system purifies wastewater to drinking quality and meets {o4[0]} of the nation's water demand. The technology is being adopted in California, Australia, and Namibia.\n\nDrip irrigation, developed in Israel in the 1960s, reduces agricultural water use by up to 60%. Despite this, only {o4[1]} of irrigated land worldwide uses efficient irrigation systems.\n\nThe concept of 'virtual water' — the water embedded in products — is gaining attention. A cotton T-shirt requires 2,700 litres of water to produce. Understanding virtual water helps countries make informed trade decisions.\n\nFor next week, read the chapter on water governance and analyse the water management strategy of one water-stressed country.",
    }

    transcript = transcripts.get(key, transcripts["climate"])

    questions = []

    # Q1: completion
    questions.append({
        "id": make_qid(test_num, 4, 1),
        "number": 1,
        "type": "completion",
        "text": "The key year mentioned is ________________.",
        "answer": [o0[0]],
        "max_words": 1
    })

    # Q2: mcq
    questions.append({
        "id": make_qid(test_num, 4, 2),
        "number": 2,
        "type": "mcq",
        "text": "What percentage/figure is cited as the main statistic?",
        "options": [o1[0], o1[1], o1[2], o1[3]],
        "answer": o1[0]
    })

    # Q3: completion
    questions.append({
        "id": make_qid(test_num, 4, 3),
        "number": 3,
        "type": "completion",
        "text": "Approximately ________________ is mentioned as a key figure.",
        "answer": [o2[0]],
        "max_words": 1
    })

    # Q4: mcq
    questions.append({
        "id": make_qid(test_num, 4, 4),
        "number": 4,
        "type": "mcq",
        "text": "Which country/place is highlighted as a key example?",
        "options": [o3[0], o3[1], o3[2], o3[3]],
        "answer": o3[0]
    })

    # Q5: completion
    questions.append({
        "id": make_qid(test_num, 4, 5),
        "number": 5,
        "type": "completion",
        "text": "The projected year for the target is ________________.",
        "answer": [o4[0]],
        "max_words": 1
    })

    # Q6: tfng
    questions.append({
        "id": make_qid(test_num, 4, 6),
        "number": 6,
        "type": "tfng",
        "text": "The lecturer mentions that the situation has improved significantly in recent years.",
        "answer": "FALSE"
    })

    # Q7: mcq
    questions.append({
        "id": make_qid(test_num, 4, 7),
        "number": 7,
        "type": "mcq",
        "text": "What does the lecturer identify as the main challenge?",
        "options": ["Lack of funding", "Technological limitations", "Political resistance", "All of the above"],
        "answer": "All of the above"
    })

    # Q8: completion
    questions.append({
        "id": make_qid(test_num, 4, 8),
        "number": 8,
        "type": "completion",
        "text": "The lecturer recommends reading Chapter ________________ for next week.",
        "answer": ["12", "7", "8", "10"],
        "max_words": 1
    })

    # Q9: tfng
    questions.append({
        "id": make_qid(test_num, 4, 9),
        "number": 9,
        "type": "tfng",
        "text": "Students are required to prepare a presentation for the next class.",
        "answer": "TRUE"
    })

    # Q10: mcq
    questions.append({
        "id": make_qid(test_num, 4, 10),
        "number": 10,
        "type": "mcq",
        "text": "What is the overall tone of the lecture?",
        "options": ["Optimistic", "Cautious", "Alarming but hopeful", "Pessimistic"],
        "answer": "Cautious"
    })

    return {
        "id": "S4",
        "number": 4,
        "title": f"Section 4 — Lecture ({title})",
        "instructions": f"Listen to a lecture about {title.lower()}. Answer questions 31-40.",
        "transcript": transcript,
        "questions": questions
    }


def generate_test(test_num):
    """Generate a single IELTS listening test with 4 sections × 10 questions = 40 total."""
    s1_idx = (test_num - 1) % len(S1_SCENARIOS)
    s2_idx = (test_num - 1) % len(S2_SCENARIOS)
    s3_idx = (test_num - 1) % len(S3_SCENARIOS)
    s4_idx = (test_num - 1) % len(S4_SCENARIOS)

    return {
        "id": f"ielts-listening-{test_num}",
        "title": f"IELTS Listening Practice Test {test_num}",
        "time_minutes": 30,
        "sections": [
            gen_section1(test_num, s1_idx),
            gen_section2(test_num, s2_idx),
            gen_section3(test_num, s3_idx),
            gen_section4(test_num, s4_idx),
        ]
    }


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "web", "public", "data")
    output_path = os.path.join(output_dir, "listening_tests.json")

    print(f"Generating 500 IELTS Listening tests...")

    tests = []
    for i in range(1, 501):
        test = generate_test(i)
        tests.append(test)
        if i % 50 == 0:
            print(f"  Generated {i}/500 tests...")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tests, f, ensure_ascii=False, indent=2)

    file_size = os.path.getsize(output_path) / (1024 * 1024)
    total_questions = sum(
        len(s["questions"]) for t in tests for s in t["sections"]
    )
    print(f"\nDone! Generated {len(tests)} tests with {total_questions} total questions.")
    print(f"Output: {output_path}")
    print(f"File size: {file_size:.1f} MB")


if __name__ == "__main__":
    main()
