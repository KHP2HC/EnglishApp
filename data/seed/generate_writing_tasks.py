#!/usr/bin/env python3
"""
Generate 500 IELTS Writing tasks (Task 1 + Task 2) as JSON.
Output: web/public/data/writing_tasks.json
"""

import json
import os
import random

random.seed(42)

OUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "web", "public", "data", "writing_tasks.json"
)

# ── Task 1 data templates ────────────────────────────────────────────

TASK1_TEMPLATES = [
    # (title_suffix, prompt, data_description, band_descriptors)
    (
        "Line Graph — Transport Modes",
        "The graph below shows the percentage of people using different modes of transport to commute to work in a European city between 2000 and 2020. Summarise the information by selecting and reporting the main features, and make comparisons where relevant.",
        "Line graph: Car usage rose from 45% (2000) to 55% (2010) then fell to 40% (2020). Bus usage declined steadily from 30% to 15%. Train usage increased from 10% to 35%. Cycling grew from 5% to 10%.",
        {
            "task_achievement": "Does the response cover all key features with data? Are comparisons made?",
            "coherence": "Is there a clear overview? Are paragraphs logically organised?",
            "lexical_resource": "Are varied vocabulary and precise data descriptions used?",
            "grammar": "Are complex sentence structures used accurately?"
        }
    ),
    (
        "Bar Chart — International Students",
        "The bar chart below shows the number of international students enrolled in four different faculties at a UK university in 2010 and 2020. Summarise the information by selecting and reporting the main features, and make comparisons where relevant.",
        "Bar chart: Business: 800 (2010) → 1200 (2020). Engineering: 600 → 950. Arts: 400 → 300. Medicine: 300 → 500.",
        {
            "task_achievement": "Are all faculties covered? Are trends identified?",
            "coherence": "Is there a logical flow with clear paragraphing?",
            "lexical_resource": "Are comparison words used (whereas, while, in contrast)?",
            "grammar": "Are tenses correct for describing past data?"
        }
    ),
    (
        "Pie Chart — Energy Production",
        "The pie charts below show the sources of energy production in a country in 1990 and 2020. Summarise the information by selecting and reporting the main features, and make comparisons where relevant.",
        "Pie charts: 1990 — Coal 40%, Oil 30%, Natural Gas 20%, Nuclear 5%, Renewable 5%. 2020 — Coal 20%, Oil 25%, Natural Gas 25%, Nuclear 10%, Renewable 20%.",
        {
            "task_achievement": "Are all energy sources covered? Are shifts identified?",
            "coherence": "Is there a clear overview paragraph?",
            "lexical_resource": "Are proportion terms used (accounted for, comprised, made up)?",
            "grammar": "Are comparison structures used accurately?"
        }
    ),
    (
        "Table — Household Spending",
        "The table below gives information about the percentage of household income spent on four categories in five different countries. Summarise the information by selecting and reporting the main features, and make comparisons where relevant.",
        "Table: Food: UK 15%, USA 12%, Japan 18%, India 30%, France 14%. Housing: UK 25%, USA 28%, Japan 22%, India 15%, France 24%. Transport: UK 12%, USA 15%, Japan 8%, India 5%, France 10%. Leisure: UK 10%, USA 12%, Japan 9%, India 4%, France 11%.",
        {
            "task_achievement": "Are all countries and categories covered? Are extremes identified?",
            "coherence": "Is the data grouped logically?",
            "lexical_resource": "Are comparative and superlative forms used correctly?",
            "grammar": "Are quantifiers and fractions used accurately?"
        }
    ),
    (
        "Process Diagram — Manufacturing",
        "The diagram below shows the process of manufacturing paper. Summarise the information by selecting and reporting the main features, and make comparisons where relevant.",
        "Process: Trees harvested → chipped → mixed with water and chemicals → boiled → pressed → dried → rolled into paper. Waste water is treated and recycled.",
        {
            "task_achievement": "Are all stages described? Is the sequence clear?",
            "coherence": "Are sequential linkers used (first, then, next, finally)?",
            "lexical_resource": "Are passive voice and process vocabulary used?",
            "grammar": "Is the passive voice used appropriately?"
        }
    ),
    (
        "Map — Village Development",
        "The maps below show the village of Stokeford in 1930 and 2010. Summarise the information by selecting and reporting the main features, and make comparisons where relevant.",
        "Maps: 1930 — small village with farms, a primary school, and a post office. 2010 — farms replaced by housing, school expanded, new road built, shops added, population grew significantly.",
        {
            "task_achievement": "Are all key changes identified? Are comparisons made?",
            "coherence": "Is there a clear before/after structure?",
            "lexical_resource": "Are change verbs used (demolished, constructed, extended)?",
            "grammar": "Are tenses appropriate for describing changes?"
        }
    ),
    (
        "Bar Chart — Tourism Revenue",
        "The bar chart below shows the tourism revenue (in billions of dollars) for five countries over three years (2015, 2018, 2021). Summarise the information by selecting and reporting the main features, and make comparisons where relevant.",
        "Bar chart: France: 55 → 62 → 48. Spain: 50 → 58 → 52. USA: 180 → 210 → 175. China: 120 → 160 → 140. Italy: 45 → 52 → 40.",
        {
            "task_achievement": "Are trends for all countries described? Are peaks and dips noted?",
            "coherence": "Is there a logical grouping (e.g., by country or by year)?",
            "lexical_resource": "Are trend words used (peaked, dipped, fluctuated)?",
            "grammar": "Are prepositions of time used correctly?"
        }
    ),
    (
        "Line Graph — Internet Usage",
        "The graph below shows the percentage of households with internet access in four regions from 2005 to 2020. Summarise the information by selecting and reporting the main features, and make comparisons where relevant.",
        "Line graph: North America: 60% → 90%. Europe: 45% → 85%. Asia: 15% → 70%. Africa: 5% → 30%.",
        {
            "task_achievement": "Are all regions covered? Are growth rates compared?",
            "coherence": "Is there a clear overview of the general trend?",
            "lexical_resource": "Are growth verbs used (surged, rose steadily, remained low)?",
            "grammar": "Are relative clauses used for comparison?"
        }
    ),
    (
        "Table — Employment Sectors",
        "The table below shows the percentage of workers in three employment sectors in four countries in 2000 and 2020. Summarise the information by selecting and reporting the main features, and make comparisons where relevant.",
        "Table: Agriculture — India 55%→35%, Brazil 40%→25%, UK 3%→1%, Australia 5%→2%. Manufacturing — India 20%→25%, Brazil 25%→20%, UK 25%→15%, Australia 20%→15%. Services — India 25%→40%, Brazil 35%→55%, UK 72%→84%, Australia 75%→83%.",
        {
            "task_achievement": "Are all sectors and countries covered? Are shifts identified?",
            "coherence": "Is the data organised by sector or country?",
            "lexical_resource": "Are shift verbs used (declined, grew, remained dominant)?",
            "grammar": "Are percentages and fractions expressed correctly?"
        }
    ),
    (
        "Pie Chart — Water Usage",
        "The pie charts below show the main uses of water in a country in 1990 and 2020. Summarise the information by selecting and reporting the main features, and make comparisons where relevant.",
        "Pie charts: 1990 — Agriculture 70%, Industry 20%, Domestic 10%. 2020 — Agriculture 50%, Industry 30%, Domestic 20%.",
        {
            "task_achievement": "Are all categories covered? Are proportional shifts noted?",
            "coherence": "Is there a clear comparison structure?",
            "lexical_resource": "Are proportion phrases used (a quarter, nearly half)?",
            "grammar": "Are comparison structures used accurately?"
        }
    ),
]

# ── Task 2 templates ─────────────────────────────────────────────────

TASK2_TEMPLATES = [
    (
        "Opinion Essay — University Education",
        "Some people believe that universities should focus on providing academic skills, while others think they should prepare students for the workplace. Discuss both views and give your own opinion.",
        {
            "task_achievement": "Are both views discussed? Is a clear opinion given?",
            "coherence": "Is the essay well-structured with introduction, body, conclusion?",
            "lexical_resource": "Is academic vocabulary used appropriately?",
            "grammar": "Are complex structures used (conditionals, passives, relative clauses)?"
        }
    ),
    (
        "Problem & Solution — Household Waste",
        "In many countries, the amount of household waste is increasing. What are the causes of this problem, and what solutions can you suggest?",
        {
            "task_achievement": "Are causes clearly identified? Are solutions practical?",
            "coherence": "Is there a clear problem-solution structure?",
            "lexical_resource": "Are cause/effect linkers used (due to, consequently, as a result)?",
            "grammar": "Are modal verbs used for suggestions (should, ought to, could)?"
        }
    ),
    (
        "Advantages & Disadvantages — Remote Work",
        "Many people now work from home rather than in an office. Do the advantages of this outweigh the disadvantages?",
        {
            "task_achievement": "Are both advantages and disadvantages discussed? Is a clear position taken?",
            "coherence": "Is the argument logically developed?",
            "lexical_resource": "Are contrasting expressions used (however, on the other hand, nevertheless)?",
            "grammar": "Are comparison structures used accurately?"
        }
    ),
    (
        "Opinion Essay — Technology & Children",
        "Some people think that children should be allowed to use smartphones and tablets from a young age, while others believe this should be restricted. Discuss both views and give your opinion.",
        {
            "task_achievement": "Are both perspectives addressed? Is a clear stance taken?",
            "coherence": "Is there a balanced structure with clear paragraphs?",
            "lexical_resource": "Is topic-specific vocabulary used (screen time, cognitive development)?",
            "grammar": "Are conditional sentences used for hypothetical situations?"
        }
    ),
    (
        "Discussion — Public Transport",
        "Some people argue that governments should invest more in public transport to reduce traffic congestion, while others believe building more roads is a better solution. Discuss both views and give your opinion.",
        {
            "task_achievement": "Are both solutions discussed? Is a clear opinion given?",
            "coherence": "Is the essay logically structured?",
            "lexical_resource": "Are transport-related terms used (congestion, commute, infrastructure)?",
            "grammar": "Are passive constructions used for policy discussion?"
        }
    ),
    (
        "Opinion Essay — Tourism",
        "International tourism is now a major industry. Some people think it benefits local communities, while others believe it causes more harm than good. Discuss both views and give your opinion.",
        {
            "task_achievement": "Are benefits and harms both discussed? Is an opinion given?",
            "coherence": "Is there a clear introduction and conclusion?",
            "lexical_resource": "Are tourism terms used (heritage, over-tourism, cultural exchange)?",
            "grammar": "Are complex sentences with subordinating conjunctions used?"
        }
    ),
    (
        "Problem & Solution — Air Pollution",
        "Air pollution in major cities is becoming a serious problem. What are the causes, and what measures can be taken to address this issue?",
        {
            "task_achievement": "Are causes identified? Are measures practical and specific?",
            "coherence": "Is there a logical cause-solution flow?",
            "lexical_resource": "Are environmental terms used (emissions, particulate matter, renewable)?",
            "grammar": "Are modal verbs and passive voice used for recommendations?"
        }
    ),
    (
        "Advantages & Disadvantages — Social Media",
        "Social media has become an integral part of modern life. Do the advantages of social media outweigh the disadvantages?",
        {
            "task_achievement": "Are pros and cons both covered? Is a clear position taken?",
            "coherence": "Is the argument well-organised?",
            "lexical_resource": "Are digital terms used (platforms, connectivity, misinformation)?",
            "grammar": "Are varied sentence types used (simple, compound, complex)?"
        }
    ),
    (
        "Opinion Essay — Gap Year",
        "Some students take a gap year before starting university. Do you think this is a good idea? Give reasons for your answer and include relevant examples.",
        {
            "task_achievement": "Is a clear position taken? Are reasons and examples provided?",
            "coherence": "Is the essay well-structured?",
            "lexical_resource": "Is varied vocabulary used (personal growth, life experience, maturity)?",
            "grammar": "Are a range of tenses used appropriately?"
        }
    ),
    (
        "Discussion — Online Shopping",
        "Online shopping is replacing traditional brick-and-mortar stores. What problems does this cause, and what solutions can be implemented?",
        {
            "task_achievement": "Are problems identified? Are solutions practical?",
            "coherence": "Is there a clear problem-solution structure?",
            "lexical_resource": "Are retail terms used (e-commerce, footfall, high street)?",
            "grammar": "Are cause and effect structures used accurately?"
        }
    ),
    (
        "Opinion Essay — Animal Rights",
        "Some people believe that animals should have the same rights as humans, while others think they exist for human benefit. Discuss both views and give your opinion.",
        {
            "task_achievement": "Are both views discussed? Is a clear opinion given?",
            "coherence": "Is the essay logically developed?",
            "lexical_resource": "Is ethical vocabulary used (welfare, exploitation, sentient)?",
            "grammar": "Are relative clauses and conditionals used?"
        }
    ),
    (
        "Problem & Solution — Youth Unemployment",
        "Youth unemployment is a growing concern in many countries. What are the causes, and what can be done to solve this problem?",
        {
            "task_achievement": "Are causes identified? Are solutions specific and actionable?",
            "coherence": "Is there a clear structure?",
            "lexical_resource": "Are employment terms used (skills gap, vocational training, apprenticeship)?",
            "grammar": "Are passive constructions used for policy suggestions?"
        }
    ),
    (
        "Advantages & Disadvantages — Globalisation",
        "Globalisation has connected economies and cultures around the world. Do the advantages of globalisation outweigh its disadvantages?",
        {
            "task_achievement": "Are both sides discussed? Is a clear position taken?",
            "coherence": "Is the argument well-organised with clear paragraphs?",
            "lexical_resource": "Are economic terms used (trade, outsourcing, cultural homogenisation)?",
            "grammar": "Are complex sentence structures used accurately?"
        }
    ),
    (
        "Opinion Essay — Health & Diet",
        "Some people believe that governments should tax unhealthy food to encourage healthier eating, while others think this is unfair. Discuss both views and give your opinion.",
        {
            "task_achievement": "Are both views discussed? Is a clear opinion given?",
            "coherence": "Is the essay well-structured?",
            "lexical_resource": "Are health terms used (obesity, nutrition, junk food)?",
            "grammar": "Are modal verbs used for suggestions and obligations?"
        }
    ),
    (
        "Discussion — AI & Employment",
        "Artificial intelligence is increasingly replacing human workers in various industries. What problems does this cause, and what solutions can be proposed?",
        {
            "task_achievement": "Are problems identified? Are solutions forward-looking?",
            "coherence": "Is there a logical flow?",
            "lexical_resource": "Are technology terms used (automation, reskilling, displacement)?",
            "grammar": "Are future tenses and conditionals used?"
        }
    ),
    (
        "Opinion Essay — Arts Funding",
        "Some people think the government should spend money on arts and cultural projects, while others believe this money should be spent on public services instead. Discuss both views and give your opinion.",
        {
            "task_achievement": "Are both views discussed? Is a clear opinion given?",
            "coherence": "Is the essay well-organised?",
            "lexical_resource": "Are cultural terms used (heritage, patronage, public services)?",
            "grammar": "Are varied sentence structures used?"
        }
    ),
    (
        "Problem & Solution — Urbanisation",
        "More and more people are moving to cities. What problems does this cause, and what can governments do to address them?",
        {
            "task_achievement": "Are urban problems identified? Are solutions practical?",
            "coherence": "Is there a clear problem-solution structure?",
            "lexical_resource": "Are urban terms used (overcrowding, infrastructure, migration)?",
            "grammar": "Are cause/effect and suggestion structures used?"
        }
    ),
    (
        "Advantages & Disadvantages — Nuclear Energy",
        "Nuclear energy is used in many countries to generate electricity. Do the advantages of nuclear energy outweigh the disadvantages?",
        {
            "task_achievement": "Are pros and cons both covered? Is a clear position taken?",
            "coherence": "Is the argument logically developed?",
            "lexical_resource": "Are energy terms used (fission, radioactive waste, low-carbon)?",
            "grammar": "Are passive constructions and modals used?"
        }
    ),
    (
        "Opinion Essay — Standardised Testing",
        "Many education systems rely on standardised tests to evaluate students. Some people think this is an effective method, while others disagree. Discuss both views and give your opinion.",
        {
            "task_achievement": "Are both views discussed? Is a clear opinion given?",
            "coherence": "Is the essay well-structured?",
            "lexical_resource": "Are education terms used (assessment, rote learning, holistic)?",
            "grammar": "Are complex sentences with subordinating conjunctions used?"
        }
    ),
    (
        "Discussion — Climate Change",
        "Climate change is one of the greatest challenges facing humanity. What are the causes, and what actions should individuals and governments take?",
        {
            "task_achievement": "Are causes identified? Are actions for both individuals and governments covered?",
            "coherence": "Is there a logical structure?",
            "lexical_resource": "Are environmental terms used (carbon footprint, emissions, sustainability)?",
            "grammar": "Are modal verbs and passive voice used for recommendations?"
        }
    ),
]


def generate_writing_tasks(count=500):
    tasks = []
    # Ensure a good mix: roughly 40% Task 1, 60% Task 2
    n_task1 = int(count * 0.4)
    n_task2 = count - n_task1

    idx = 1
    for i in range(n_task1):
        tpl = TASK1_TEMPLATES[i % len(TASK1_TEMPLATES)]
        tasks.append({
            "id": f"wt-task1-{idx}",
            "type": "task1",
            "title": f"IELTS Writing Task 1 — {tpl[0]} (Set {idx})",
            "instructions": "You should spend about 20 minutes on this task. Write at least 150 words.",
            "prompt": tpl[1],
            "data_description": tpl[2],
            "min_words": 150,
            "time_minutes": 20,
            "band_descriptors": tpl[3],
        })
        idx += 1

    idx = 1
    for i in range(n_task2):
        tpl = TASK2_TEMPLATES[i % len(TASK2_TEMPLATES)]
        tasks.append({
            "id": f"wt-task2-{idx}",
            "type": "task2",
            "title": f"IELTS Writing Task 2 — {tpl[0]} (Set {idx})",
            "instructions": "You should spend about 40 minutes on this task. Write at least 250 words.",
            "prompt": tpl[1],
            "min_words": 250,
            "time_minutes": 40,
            "band_descriptors": tpl[2],
        })
        idx += 1

    # Shuffle for interleaved ordering
    random.shuffle(tasks)
    return tasks


def main():
    tasks = generate_writing_tasks(500)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
    print(f"✅ Generated {len(tasks)} writing tasks → {OUT_PATH}")
    # Quick distribution check
    t1 = sum(1 for t in tasks if t["type"] == "task1")
    t2 = sum(1 for t in tasks if t["type"] == "task2")
    print(f"   Task 1: {t1}, Task 2: {t2}")


if __name__ == "__main__":
    main()
