/**
 * VSTEP Test Data Generator
 *
 * Generates 500 tests per module (listening, reading, writing, speaking)
 * following the VSTEP exam format.
 *
 * Usage: node scripts/generate_vstep_tests.js
 */

const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, '..', 'web', 'public', 'data');
const TOTAL_TESTS = 500;

// ── Content pools ────────────────────────────────────────────────────

const ANNOUNCEMENT_TOPICS = [
  { topic: 'train delay', context: 'railway station', speakers: ['Announcer'] },
  { topic: 'mall sale', context: 'shopping mall', speakers: ['Announcer'] },
  { topic: 'library closure', context: 'public library', speakers: ['Announcer'] },
  { topic: 'fire drill', context: 'office building', speakers: ['Announcer'] },
  { topic: 'flight boarding', context: 'airport', speakers: ['Announcer'] },
  { topic: 'flu vaccination', context: 'health center', speakers: ['Announcer'] },
  { topic: 'elevator maintenance', context: 'office building', speakers: ['Announcer'] },
  { topic: 'school closure', context: 'school', speakers: ['Principal'] },
  { topic: 'road closure', context: 'city traffic', speakers: ['Announcer'] },
  { topic: 'museum exhibition', context: 'museum', speakers: ['Announcer'] },
  { topic: 'swimming pool schedule', context: 'sports center', speakers: ['Announcer'] },
  { topic: 'lost property', context: 'train station', speakers: ['Announcer'] },
  { topic: 'weather warning', context: 'radio broadcast', speakers: ['Announcer'] },
  { topic: 'power outage', context: 'residential area', speakers: ['Announcer'] },
  { topic: 'community meeting', context: 'community center', speakers: ['Announcer'] },
  { topic: 'book sale', context: 'bookstore', speakers: ['Announcer'] },
  { topic: 'restaurant reservation', context: 'restaurant', speakers: ['Host'] },
  { topic: 'park opening hours', context: 'national park', speakers: ['Ranger'] },
  { topic: 'university registration', context: 'university', speakers: ['Registrar'] },
  { topic: 'pharmacy prescription', context: 'pharmacy', speakers: ['Pharmacist'] },
];

const CONVERSATION_TOPICS = [
  { topic: 'planning a trip', speakers: ['Man', 'Woman'], context: 'travel agency' },
  { topic: 'discussing a project', speakers: ['Man', 'Woman'], context: 'office' },
  { topic: 'renting an apartment', speakers: ['Man', 'Woman'], context: 'real estate office' },
  { topic: 'at the doctor', speakers: ['Doctor', 'Patient'], context: 'clinic' },
  { topic: 'job interview', speakers: ['Interviewer', 'Candidate'], context: 'office' },
  { topic: 'restaurant complaint', speakers: ['Manager', 'Customer'], context: 'restaurant' },
  { topic: 'course enrollment', speakers: ['Student', 'Advisor'], context: 'university' },
  { topic: 'buying a car', speakers: ['Salesman', 'Customer'], context: 'car dealership' },
  { topic: 'library membership', speakers: ['Librarian', 'Visitor'], context: 'library' },
  { topic: 'gym membership', speakers: ['Staff', 'Customer'], context: 'gym' },
  { topic: 'hotel booking', speakers: ['Receptionist', 'Guest'], context: 'hotel' },
  { topic: 'bank account', speakers: ['Clerk', 'Customer'], context: 'bank' },
  { topic: 'phone repair', speakers: ['Technician', 'Customer'], context: 'repair shop' },
  { topic: 'tour booking', speakers: ['Guide', 'Tourist'], context: 'tour office' },
  { topic: 'insurance claim', speakers: ['Agent', 'Client'], context: 'insurance office' },
  { topic: 'computer problem', speakers: ['IT Support', 'Employee'], context: 'office' },
  { topic: 'school enrollment', speakers: ['Parent', 'Teacher'], context: 'school' },
  { topic: 'cooking class', speakers: ['Instructor', 'Student'], context: 'kitchen' },
  { topic: 'traffic accident', speakers: ['Officer', 'Driver'], context: 'roadside' },
  { topic: 'garden center', speakers: ['Staff', 'Customer'], context: 'garden center' },
];

const LECTURE_TOPICS = [
  { topic: 'climate change', speaker: 'Professor', context: 'university lecture' },
  { topic: 'artificial intelligence', speaker: 'Professor', context: 'technology talk' },
  { topic: 'ancient civilizations', speaker: 'Professor', context: 'history lecture' },
  { topic: 'marine biology', speaker: 'Dr.', context: 'science lecture' },
  { topic: 'urban planning', speaker: 'Professor', context: 'architecture talk' },
  { topic: 'nutrition', speaker: 'Dr.', context: 'health seminar' },
  { topic: 'renewable energy', speaker: 'Professor', context: 'engineering lecture' },
  { topic: 'psychology of learning', speaker: 'Dr.', context: 'psychology lecture' },
  { topic: 'space exploration', speaker: 'Professor', context: 'astronomy talk' },
  { topic: 'economic trends', speaker: 'Professor', context: 'economics lecture' },
  { topic: 'music history', speaker: 'Professor', context: 'music appreciation' },
  { topic: 'environmental conservation', speaker: 'Dr.', context: 'biology lecture' },
  { topic: 'digital marketing', speaker: 'Professor', context: 'business lecture' },
  { topic: 'public health', speaker: 'Dr.', context: 'health policy talk' },
  { topic: 'cultural diversity', speaker: 'Professor', context: 'sociology lecture' },
  { topic: 'water resources', speaker: 'Dr.', context: 'environmental science' },
  { topic: 'robotics', speaker: 'Professor', context: 'engineering talk' },
  { topic: 'food security', speaker: 'Dr.', context: 'agriculture lecture' },
  { topic: 'social media impact', speaker: 'Professor', context: 'media studies' },
  { topic: 'sustainable agriculture', speaker: 'Dr.', context: 'agricultural science' },
];

const READING_TOPICS = [
  { title: 'The History of Coffee', difficulty: 'B1' },
  { title: 'Climate Change and Coastal Cities', difficulty: 'B2' },
  { title: 'The Psychology of Habits', difficulty: 'B2' },
  { title: 'Renewable Energy in Developing Nations', difficulty: 'C1' },
  { title: 'The Art of Storytelling', difficulty: 'B1' },
  { title: 'Urban Beekeeping', difficulty: 'B2' },
  { title: 'The Science of Sleep', difficulty: 'B2' },
  { title: 'Language Extinction', difficulty: 'C1' },
  { title: 'The Economics of Recycling', difficulty: 'B2' },
  { title: 'Mindfulness in Education', difficulty: 'B1' },
  { title: 'The Future of Public Transport', difficulty: 'B2' },
  { title: 'Ancient Medicine', difficulty: 'B1' },
  { title: 'Social Media and Democracy', difficulty: 'C1' },
  { title: 'The Rise of E-Sports', difficulty: 'B2' },
  { title: 'Coral Reef Ecosystems', difficulty: 'B2' },
  { title: 'The History of Writing', difficulty: 'B1' },
  { title: 'Artificial Intelligence in Healthcare', difficulty: 'C1' },
  { title: 'Sustainable Fashion', difficulty: 'B2' },
  { title: 'The Psychology of Color', difficulty: 'B1' },
  { title: 'Water Conservation Strategies', difficulty: 'B2' },
  { title: 'The Impact of Tourism', difficulty: 'B2' },
  { title: 'Food Waste and Solutions', difficulty: 'B1' },
  { title: 'The History of Photography', difficulty: 'B1' },
  { title: 'Mental Health in the Workplace', difficulty: 'B2' },
  { title: 'The Science of Happiness', difficulty: 'B2' },
  { title: 'Urban Green Spaces', difficulty: 'B1' },
  { title: 'The Future of Work', difficulty: 'C1' },
  { title: 'Plastic Pollution', difficulty: 'B2' },
  { title: 'The Benefits of Bilingualism', difficulty: 'B2' },
  { title: 'Space Tourism', difficulty: 'C1' },
  { title: 'The History of Chocolate', difficulty: 'B1' },
  { title: 'Overfishing and Marine Ecosystems', difficulty: 'B2' },
  { title: 'The Psychology of Advertising', difficulty: 'C1' },
  { title: 'Renewable Energy Technologies', difficulty: 'B2' },
  { title: 'The Importance of Biodiversity', difficulty: 'B2' },
  { title: 'Digital Privacy', difficulty: 'C1' },
  { title: 'The Cultural Significance of Festivals', difficulty: 'B1' },
  { title: 'Healthy Aging', difficulty: 'B2' },
  { title: 'The Rise of Remote Work', difficulty: 'B2' },
  { title: 'Wildlife Conservation', difficulty: 'B1' },
];

const WRITING_TASK1_TOPICS = [
  'You recently moved to a new city and want to join a local sports club. Write a letter to the club manager introducing yourself and asking about membership.',
  'You are unhappy with a product you purchased online. Write an email to the company explaining the problem and requesting a refund or replacement.',
  'You want to apply for a part-time job at a local bookstore. Write a letter to the store manager expressing your interest and qualifications.',
  'Your neighbor has been making noise late at night. Write a polite letter asking them to keep the noise down.',
  'You attended a fitness workshop and want to share your experience. Write an email to a friend telling them about it.',
  'You need to request time off from work for a family event. Write an email to your manager explaining the situation.',
  'You want to volunteer at an animal shelter. Write a letter to the coordinator expressing your interest.',
  'You lost your wallet on a bus. Write a notice to post at the bus station describing the wallet and asking for help.',
  'You are planning a surprise birthday party. Write an email to friends inviting them and asking for their help.',
  'You want to enroll your child in a summer camp. Write a letter to the camp director asking for details.',
];

const WRITING_TASK2_TOPICS = [
  'Some people believe that university education should be free for everyone. Others argue that students should pay. Discuss both views and give your opinion.',
  'Technology has made communication easier, but some say it has reduced face-to-face interaction. Discuss both views and give your opinion.',
  'Some people think that cities should ban cars to reduce pollution. Others believe this is impractical. Discuss both views and give your opinion.',
  'Social media has changed how people connect. Is this a positive or negative development? Give reasons for your answer.',
  'Some people prefer to work independently, while others prefer teamwork. Which do you prefer and why?',
  'Many young people spend less time outdoors than previous generations. What are the causes and effects of this trend?',
  'Some believe that learning a second language should start in primary school. Others think it should wait until secondary school. Discuss both views.',
  'Governments should invest more in public transport. To what extent do you agree or disagree?',
  'Some people think that success comes from hard work, while others believe luck plays a bigger role. Discuss both views.',
  'The internet has made traditional libraries less important. To what extent do you agree or disagree?',
];

const SPEAKING_P1_QUESTIONS = [
  ['Can you tell me about your hometown?', 'What do you like most about where you live?', 'How has your hometown changed in recent years?', 'What do people do for entertainment there?'],
  ['What do you do in your free time?', 'How do you usually spend your weekends?', 'Do you prefer indoor or outdoor activities?', 'Has your hobby changed since you were a child?'],
  ['Do you like reading?', 'What kind of books do you enjoy?', 'Do you prefer reading paper books or e-books?', 'What book has influenced you the most?'],
  ['What is your favorite food?', 'Do you enjoy cooking?', 'What is a traditional dish from your country?', 'How often do you eat out?'],
  ['Do you like traveling?', 'What is the most interesting place you have visited?', 'Do you prefer traveling alone or with others?', 'Where would you like to travel next?'],
  ['What do you do for a living?', 'What do you like most about your job?', 'What was your first job?', 'Would you like to change your career?'],
  ['Do you enjoy music?', 'What kind of music do you listen to?', 'Can you play a musical instrument?', 'Has your taste in music changed over time?'],
  ['What is the weather like in your country?', 'What is your favorite season?', 'Do you prefer hot or cold weather?', 'How does weather affect your mood?'],
  ['Do you like sports?', 'What sport do you enjoy watching or playing?', 'How often do you exercise?', 'What are the benefits of regular exercise?'],
  ['How important is technology in your daily life?', 'What device do you use the most?', 'Do you think people are too dependent on technology?', 'What technology would you like to see in the future?'],
];

const SPEAKING_P2_QUESTIONS = [
  'Your university is facing budget cuts. Which solution is best: A) Increase tuition fees B) Reduce library hours C) Cut sports programs? Choose one and explain.',
  'Your city has traffic congestion. Which solution is best: A) Build more roads B) Improve public transport C) Charge congestion fees? Choose one and explain.',
  'Your company wants to improve employee wellness. Which is best: A) Gym memberships B) Flexible hours C) Free healthy meals? Choose one and explain.',
  'Your community has a litter problem. Which solution is best: A) More bins B) Fines for littering C) Community clean-up events? Choose one and explain.',
  'Your school wants to reduce screen time. Which is best: A) Ban phones B) Limit computer use C) Teach digital wellness? Choose one and explain.',
];

const SPEAKING_P3_QUESTIONS = [
  ['Topic: The importance of learning a foreign language. You should say: why it is important, how it benefits your career, and whether it should be compulsory in schools.', 'Do you think technology has made learning languages easier?'],
  ['Topic: The impact of social media on society. You should say: how it connects people, what problems it causes, and whether it does more good or harm.', 'Should social media be regulated by governments?'],
  ['Topic: The benefits of regular exercise. You should say: why exercise is important, how it affects mental health, and whether schools should require PE.', 'Do you think modern lifestyles are too sedentary?'],
  ['Topic: The role of technology in education. You should say: how it helps learning, what risks it poses, and whether it will replace teachers.', 'Has technology improved or worsened education?'],
  ['Topic: The importance of environmental protection. You should say: why it matters, what individuals can do, and whether governments are doing enough.', 'Do you think recycling is effective?'],
];

// ── Helpers ──────────────────────────────────────────────────────────

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function pick(arr, i) {
  return arr[i % arr.length];
}

function shuffleOptions(options, answer) {
  const shuffled = shuffle(options);
  return { options: shuffled, answer: shuffled.find(o => o === answer) || shuffled[0] };
}

// ── Listening Generator ───────────────────────────────────────────────

function generateListeningTest(num) {
  const announcements = shuffle(ANNOUNCEMENT_TOPICS).slice(0, 8);
  const conversations = shuffle(CONVERSATION_TOPICS).slice(0, 4);
  const lectures = shuffle(LECTURE_TOPICS).slice(0, 3);

  // Part 1: 8 announcements
  const part1Questions = [];
  const part1Transcript = announcements.map((a, i) => {
    const details = generateAnnouncementDetails(a, num, i);
    part1Questions.push(...details.questions);
    return details.text;
  }).join('\n\n');

  // Part 2: 4 conversations × 3 questions = 12
  const part2Questions = [];
  const part2Transcript = conversations.map((c, i) => {
    const details = generateConversationDetails(c, num, i);
    part2Questions.push(...details.questions);
    return details.text;
  }).join('\n\n');

  // Part 3: 3 lectures × 5 questions = 15
  const part3Questions = [];
  const part3Transcript = lectures.map((l, i) => {
    const details = generateLectureDetails(l, num, i);
    part3Questions.push(...details.questions);
    return details.text;
  }).join('\n\n');

  return {
    id: `vstep-listening-${num}`,
    title: `VSTEP Listening Practice Test ${num}`,
    time_minutes: 40,
    sections: [
      {
        id: `vstep-l${num}-s1`,
        number: 1,
        title: 'Part 1: Announcements',
        instructions: 'You will hear 8 short announcements. For each, choose the correct answer A, B, C, or D.',
        transcript: part1Transcript,
        questions: part1Questions,
      },
      {
        id: `vstep-l${num}-s2`,
        number: 2,
        title: 'Part 2: Conversations',
        instructions: 'You will hear 4 conversations. Each conversation has 3 questions. Choose the correct answer A, B, C, or D.',
        transcript: part2Transcript,
        questions: part2Questions,
      },
      {
        id: `vstep-l${num}-s3`,
        number: 3,
        title: 'Part 3: Talks and Lectures',
        instructions: 'You will hear 3 talks or lectures. Each has 5 questions. Choose the correct answer A, B, C, or D.',
        transcript: part3Transcript,
        questions: part3Questions,
      },
    ],
  };
}

function generateAnnouncementDetails(topic, testNum, idx) {
  const qNum = idx + 1;
  const templates = [
    {
      text: `${pick(topic.speakers, idx)}: Attention everyone. This is an announcement about ${topic.topic} at the ${topic.context}. ${getAnnouncementBody(topic.topic, 0)}`,
      questions: getAnnouncementQuestions(topic.topic, `vstep-l${testNum}-s1-q${qNum}`, qNum, 0),
    },
    {
      text: `${pick(topic.speakers, idx)}: Good ${['morning', 'afternoon', 'evening'][idx % 3]}. This is an important announcement regarding ${topic.topic}. ${getAnnouncementBody(topic.topic, 1)}`,
      questions: getAnnouncementQuestions(topic.topic, `vstep-l${testNum}-s1-q${qNum}`, qNum, 1),
    },
  ];
  return templates[idx % 2];
}

function getAnnouncementBody(topic, variant) {
  const bodies = {
    'train delay': [
      'The 10:15 service to the city center has been delayed by approximately 20 minutes due to signal problems. We apologize for the inconvenience and expect normal service to resume shortly.',
      'The express service scheduled for 2:30 PM has been cancelled due to severe weather conditions. Passengers are advised to take the local service departing at 2:45 PM from platform 3.',
    ],
    'mall sale': [
      'Today only, all electronics in the main store are 30 percent off. Visit the second floor for amazing deals on laptops, tablets, and accessories. Offer ends at 9 PM.',
      'This weekend, the bookstore is having a clearance sale. All fiction titles are buy one get one free, and children\'s books are half price. Don\'t miss out on these great deals.',
    ],
    'library closure': [
      'The central library will be closed on Saturday for system upgrades. The library will reopen on Sunday at 10 AM. Online services will remain available throughout the closure.',
      'Please note that the reading rooms on the third floor will be closed for renovation starting next Monday for approximately two weeks. All other services remain available.',
    ],
    'fire drill': [
      'The annual fire safety drill will take place tomorrow at 11 AM. Please evacuate the building immediately when the alarm sounds and assemble in the south parking lot.',
      'A scheduled fire alarm test will be conducted between 9 and 10 AM today. You do not need to evacuate during this test. However, please report any real emergencies immediately.',
    ],
    'flight boarding': [
      'Welcome aboard flight BA 412 to Paris. We will be taking off shortly. Please ensure your seat belts are fastened and all electronic devices are switched to airplane mode.',
      'This is the final boarding call for flight KL 890 to Amsterdam. All remaining passengers should proceed immediately to gate 22. The gate will close in five minutes.',
    ],
    'flu vaccination': [
      'Free flu vaccinations are available this week for all registered students. Please bring your ID card. The clinic is open from 9 AM to 4 PM, Monday through Friday.',
      'The health center reminds all staff that flu shots are now available. Please schedule an appointment online or walk in during lunch hours. Vaccination takes only 10 minutes.',
    ],
    'elevator maintenance': [
      'Due to maintenance work, the east elevator is out of service until further notice. Please use the west elevator or the stairs. We expect service to resume by 5 PM.',
      'The main elevator will undergo scheduled maintenance this Wednesday from 8 AM to noon. During this time, the freight elevator will be available for all floors.',
    ],
    'school closure': [
      'All after-school activities have been cancelled due to the severe weather warning. Students should go directly home after the final bell. Regular activities will resume tomorrow.',
      'This is a reminder that school will be closed next Monday for a teacher training day. Classes will resume on Tuesday at the normal time. Please plan accordingly.',
    ],
    'road closure': [
      'The main road between the shopping center and the park will be closed for resurfacing from Monday for approximately one week. Please use the alternative route via Oak Street.',
      'Bridge Street is currently closed in both directions due to an accident. Drivers are advised to use River Road as an alternative. Expect significant delays during rush hour.',
    ],
    'museum exhibition': [
      'A new exhibition on ancient Egyptian art opens this Saturday at the city museum. Admission is free for members and five dollars for non-members. The exhibition runs for three months.',
      'The natural history museum will host a special dinosaur exhibit next month. Guided tours are available daily at 11 AM and 2 PM. Advance booking is recommended.',
    ],
    'swimming pool schedule': [
      'The indoor swimming pool will have reduced hours next week due to filter maintenance. Morning sessions are cancelled, but afternoon and evening sessions will run as normal.',
      'The outdoor pool opens for the summer season on May 1st. Season passes are now available at a 20 percent discount until the end of April. Visit the front desk for details.',
    ],
    'lost property': [
      'A black wallet has been found in the waiting area. The owner can collect it from the lost property office on platform 1. Please bring identification to claim the wallet.',
      'A set of keys with a blue keyring was handed in at the information desk. If you have lost keys, please visit the desk with proof of identity to collect them.',
    ],
    'weather warning': [
      'The weather service has issued a heavy rain warning for the region. Residents are advised to stay indoors and avoid traveling unless necessary. The warning is in effect until midnight.',
      'A heat wave is expected this weekend with temperatures reaching 38 degrees. Please stay hydrated, avoid prolonged sun exposure, and check on elderly neighbors.',
    ],
    'power outage': [
      'A planned power outage will affect the western district this Sunday from 8 AM to 2 PM for equipment upgrades. Please make necessary arrangements during this time.',
      'We are experiencing an unexpected power outage in the northern area. Our technicians are working to restore service. We expect power to be back within two hours.',
    ],
    'community meeting': [
      'The monthly community meeting will be held this Thursday at 7 PM in the community hall. Topics include the new playground project and neighborhood safety. All residents are welcome.',
      'A town hall meeting is scheduled for next Wednesday to discuss the proposed recycling program. The meeting starts at 6:30 PM in the main auditorium.',
    ],
    'book sale': [
      'The annual book fair starts this Friday at the convention center. Over 50 publishers will be present with discounts of up to 70 percent. The fair runs for three days.',
      'The campus bookstore is having a back-to-school sale. All textbooks are 15 percent off and stationery is 20 percent off. Sale ends this Friday.',
    ],
    'restaurant reservation': [
      'Thank you for calling. We have a table available for four at 7:30 PM this evening. Please note that we hold reservations for 15 minutes. May I take your name?',
      'We have a two-for-one special on all main courses this Tuesday evening. Reservations are recommended as tables fill up quickly. Would you like to book a table?',
    ],
    'park opening hours': [
      'The national park is open daily from 6 AM to 8 PM during summer months. The visitor center operates from 9 AM to 5 PM. Please register at the entrance before starting any trail.',
      'The wildlife reserve will extend its hours for the spring season. Starting next week, the park will be open from 7 AM to 7 PM. Night tours are available on weekends.',
    ],
    'university registration': [
      'Registration for the spring semester is now open. Please log in to the student portal to select your courses. The deadline for registration is the end of this month.',
      'Late registration for the fall semester will be held this Friday from 9 AM to 3 PM. A late fee of 50 dollars will apply. Please bring your student ID and payment confirmation.',
    ],
    'pharmacy prescription': [
      'Your prescription is ready for collection. Please bring your ID when picking up the medication. The pharmacy is open until 8 PM today. Please note that some medications require consultation.',
      'This is a reminder that your prescription refill is due. Please call or visit the pharmacy within the next three days. After that, a new prescription from your doctor will be required.',
    ],
  };
  return (bodies[topic.topic] || bodies['train delay'])[variant] || bodies[topic.topic][0];
}

function getAnnouncementQuestions(topic, qId, qNum, variant) {
  const qSets = {
    'train delay': [
      { text: 'What is the reason for the delay?', options: ['Signal problems', 'Bad weather', 'A strike', 'Track maintenance'], answer: 'Signal problems' },
      { text: 'How long is the expected delay?', options: ['10 minutes', '20 minutes', '30 minutes', '45 minutes'], answer: '20 minutes' },
    ],
    'mall sale': [
      { text: 'What is on sale?', options: ['Electronics', 'Clothing', 'Food', 'Furniture'], answer: 'Electronics' },
      { text: 'When does the offer end?', options: ['At 6 PM', 'At 7 PM', 'At 8 PM', 'At 9 PM'], answer: 'At 9 PM' },
    ],
    'library closure': [
      { text: 'Why is the library closed?', options: ['For a holiday', 'For system upgrades', 'For renovation', 'For cleaning'], answer: 'For system upgrades' },
      { text: 'When will the library reopen?', options: ['Saturday', 'Sunday at 10 AM', 'Monday', 'Next week'], answer: 'Sunday at 10 AM' },
    ],
    'fire drill': [
      { text: 'When will the drill take place?', options: ['At 9 AM', 'At 10 AM', 'At 11 AM', 'At noon'], answer: 'At 11 AM' },
      { text: 'Where should people assemble?', options: ['The lobby', 'The north parking lot', 'The south parking lot', 'The cafeteria'], answer: 'The south parking lot' },
    ],
    'flight boarding': [
      { text: 'What is the flight number?', options: ['BA 412', 'BA 421', 'KL 890', 'KL 809'], answer: 'BA 412' },
      { text: 'What should passengers do with devices?', options: ['Turn them off', 'Switch to airplane mode', 'Put them away', 'Keep them on'], answer: 'Switch to airplane mode' },
    ],
    'flu vaccination': [
      { text: 'Who can get free vaccinations?', options: ['All residents', 'Registered students', 'Senior citizens', 'Staff only'], answer: 'Registered students' },
      { text: 'What should students bring?', options: ['A letter', 'Their ID card', 'A form', 'Payment'], answer: 'Their ID card' },
    ],
    'elevator maintenance': [
      { text: 'Which elevator is out of service?', options: ['The west elevator', 'The east elevator', 'The main elevator', 'The freight elevator'], answer: 'The east elevator' },
      { text: 'When is service expected to resume?', options: ['By noon', 'By 3 PM', 'By 5 PM', 'Tomorrow'], answer: 'By 5 PM' },
    ],
    'school closure': [
      { text: 'Why were activities cancelled?', options: ['Staff shortage', 'Severe weather', 'Power outage', 'Water leak'], answer: 'Severe weather' },
      { text: 'What should students do?', options: ['Stay in class', 'Go home', 'Go to the gym', 'Wait for parents'], answer: 'Go home' },
    ],
    'road closure': [
      { text: 'Which road is closed?', options: ['Oak Street', 'Bridge Street', 'The main road', 'River Road'], answer: 'The main road' },
      { text: 'What is the alternative route?', options: ['Via Bridge Street', 'Via Oak Street', 'Via River Road', 'Via Park Lane'], answer: 'Via Oak Street' },
    ],
    'museum exhibition': [
      { text: 'What is the exhibition about?', options: ['Modern art', 'Ancient Egyptian art', 'Photography', 'Sculpture'], answer: 'Ancient Egyptian art' },
      { text: 'How much is admission for non-members?', options: ['Free', 'Three dollars', 'Five dollars', 'Ten dollars'], answer: 'Five dollars' },
    ],
    'swimming pool schedule': [
      { text: 'Why are hours reduced?', options: ['Staff shortage', 'Filter maintenance', 'Cleaning', 'Repairs'], answer: 'Filter maintenance' },
      { text: 'Which sessions are cancelled?', options: ['Afternoon', 'Evening', 'Morning', 'All sessions'], answer: 'Morning' },
    ],
    'lost property': [
      { text: 'What was found?', options: ['A phone', 'A wallet', 'A bag', 'A key'], answer: 'A wallet' },
      { text: 'Where can it be collected?', options: ['The information desk', 'The lost property office', 'The ticket office', 'The security desk'], answer: 'The lost property office' },
    ],
    'weather warning': [
      { text: 'What type of warning was issued?', options: ['Wind warning', 'Heavy rain warning', 'Snow warning', 'Heat warning'], answer: 'Heavy rain warning' },
      { text: 'Until when is the warning in effect?', options: ['Until noon', 'Until 6 PM', 'Until midnight', 'Until morning'], answer: 'Until midnight' },
    ],
    'power outage': [
      { text: 'When will the outage occur?', options: ['Saturday', 'Sunday', 'Monday', 'Tuesday'], answer: 'Sunday' },
      { text: 'How long will it last?', options: ['2 hours', '4 hours', '6 hours', '8 hours'], answer: '6 hours' },
    ],
    'community meeting': [
      { text: 'When is the meeting?', options: ['Wednesday at 7 PM', 'Thursday at 7 PM', 'Friday at 6 PM', 'Saturday at 3 PM'], answer: 'Thursday at 7 PM' },
      { text: 'Where is the meeting?', options: ['The school hall', 'The community hall', 'The library', 'The town square'], answer: 'The community hall' },
    ],
    'book sale': [
      { text: 'Where is the book fair?', options: ['The campus', 'The convention center', 'The library', 'The bookstore'], answer: 'The convention center' },
      { text: 'What is the maximum discount?', options: ['30 percent', '50 percent', '60 percent', '70 percent'], answer: '70 percent' },
    ],
    'restaurant reservation': [
      { text: 'What time is the table available?', options: ['7 PM', '7:30 PM', '8 PM', '8:30 PM'], answer: '7:30 PM' },
      { text: 'How long do they hold reservations?', options: ['10 minutes', '15 minutes', '20 minutes', '30 minutes'], answer: '15 minutes' },
    ],
    'park opening hours': [
      { text: 'What time does the park open?', options: ['5 AM', '6 AM', '7 AM', '8 AM'], answer: '6 AM' },
      { text: 'What should visitors do before starting a trail?', options: ['Buy a ticket', 'Register at the entrance', 'Hire a guide', 'Check the weather'], answer: 'Register at the entrance' },
    ],
    'university registration': [
      { text: 'Where should students register?', options: ['At the office', 'On the student portal', 'By phone', 'By email'], answer: 'On the student portal' },
      { text: 'When is the deadline?', options: ['This week', 'Next week', 'End of the month', 'End of next month'], answer: 'End of the month' },
    ],
    'pharmacy prescription': [
      { text: 'What should the customer bring?', options: ['A letter', 'Their ID', 'A prescription', 'Payment only'], answer: 'Their ID' },
      { text: 'Until what time is the pharmacy open?', options: ['6 PM', '7 PM', '8 PM', '9 PM'], answer: '8 PM' },
    ],
  };
  const set = (qSets[topic] || qSets['train delay'])[variant] || qSets[topic][0];
  const so = shuffleOptions(set.options, set.answer);
  return [{
    id: qId,
    number: qNum,
    type: 'mcq',
    text: set.text,
    options: so.options,
    answer: so.answer,
    explanation: `The announcement mentions: ${set.answer.toLowerCase()}.`,
  }];
}

function generateConversationDetails(topic, testNum, convIdx) {
  const baseQ = convIdx * 3 + 1;
  const templates = [
    {
      text: `${topic.speakers[0]}: Hi, I'm calling about ${topic.topic}. Could you help me with that?\n${topic.speakers[1]}: Of course. What would you like to know?\n${topic.speakers[0]}: I'd like to know the details and the cost.\n${topic.speakers[1]}: Certainly. The cost is 200 dollars and it includes all materials.\n${topic.speakers[0]}: That sounds reasonable. When can we start?\n${topic.speakers[1]}: We can start next Monday at 10 AM if that works for you.\n${topic.speakers[0]}: Perfect. I'll see you then.`,
      questions: getConversationQuestions(topic.topic, `vstep-l${testNum}-s2`, baseQ),
    },
    {
      text: `${topic.speakers[0]}: Good morning. How can I help you today?\n${topic.speakers[1]}: I'm interested in ${topic.topic}. Can you give me some information?\n${topic.speakers[0]}: Absolutely. We have several options available. What's your budget?\n${topic.speakers[1]}: Around 500 dollars.\n${topic.speakers[0]}: In that range, I'd recommend our standard package. It's very popular.\n${topic.speakers[1]}: Great. Can I book it for next week?\n${topic.speakers[0]}: Yes, I can arrange that for you right away.`,
      questions: getConversationQuestions(topic.topic, `vstep-l${testNum}-s2`, baseQ, 1),
    },
  ];
  return templates[convIdx % 2];
}

function getConversationQuestions(topic, prefix, baseQ, variant = 0) {
  const qSets = {
    'planning a trip': [
      { text: 'What does the man want to know about?', options: ['The weather', 'The trip details', 'The hotel', 'The transport'], answer: 'The trip details' },
      { text: 'How much does it cost?', options: ['100 dollars', '150 dollars', '200 dollars', '250 dollars'], answer: '200 dollars' },
      { text: 'When can they start?', options: ['Today', 'Tomorrow', 'Next Monday', 'Next Friday'], answer: 'Next Monday' },
    ],
    'discussing a project': [
      { text: 'What is the conversation about?', options: ['A budget', 'A project', 'A meeting', 'A deadline'], answer: 'A project' },
      { text: 'What does the package include?', options: ['Materials only', 'Materials and labor', 'Everything', 'Transport'], answer: 'All materials' },
      { text: 'When will they start?', options: ['Today', 'Tomorrow', 'Next Monday', 'Next week'], answer: 'Next Monday' },
    ],
    'renting an apartment': [
      { text: 'What is the woman looking for?', options: ['A house', 'An apartment', 'An office', 'A studio'], answer: 'An apartment' },
      { text: 'What is the budget?', options: ['300 dollars', '400 dollars', '500 dollars', '600 dollars'], answer: '500 dollars' },
      { text: 'What does the man recommend?', options: ['The basic package', 'The standard package', 'The premium package', 'The economy option'], answer: 'The standard package' },
    ],
    'at the doctor': [
      { text: 'Why is the patient visiting?', options: ['For a checkup', 'For medication', 'For test results', 'For advice'], answer: 'For a checkup' },
      { text: 'What does the doctor recommend?', options: ['Rest', 'Medicine', 'Exercise', 'Surgery'], answer: 'Rest' },
      { text: 'When should the patient return?', options: ['In 3 days', 'In a week', 'In 2 weeks', 'In a month'], answer: 'In a week' },
    ],
    'job interview': [
      { text: 'What position is the candidate applying for?', options: ['Manager', 'Assistant', 'Developer', 'Designer'], answer: 'Assistant' },
      { text: 'How much experience does the candidate have?', options: ['1 year', '2 years', '3 years', '5 years'], answer: '3 years' },
      { text: 'When can the candidate start?', options: ['Immediately', 'Next week', 'Next month', 'In 2 months'], answer: 'Next week' },
    ],
  };
  const set = qSets[topic] || qSets['planning a trip'];
  return set.map((q, i) => {
    const so = shuffleOptions(q.options, q.answer);
    return {
      id: `${prefix}-q${baseQ + i}`,
      number: baseQ + i,
      type: 'mcq',
      text: q.text,
      options: so.options,
      answer: so.answer,
      explanation: `The speakers discuss: ${q.answer.toLowerCase()}.`,
    };
  });
}

function generateLectureDetails(topic, testNum, lecIdx) {
  const baseQ = lecIdx * 5 + 1;
  const text = `${topic.speaker}: Good ${['morning', 'afternoon', 'evening'][lecIdx % 3]}, everyone. Today I'd like to talk about ${topic.topic}. This is a fascinating subject that affects our daily lives in many ways.\n\nFirst, let me give you some background. ${topic.topic} has been studied for many years, and researchers have made significant progress in understanding it. The key finding is that ${topic.topic} plays a crucial role in modern society.\n\nThere are three main aspects to consider. The first is the historical context. Historically, ${topic.topic} was not well understood, but advances in technology have changed that. The second aspect is the current situation. Today, we have better tools and methods. The third aspect is the future outlook, which looks promising.\n\nLet me give you an example. In a recent study, researchers found that people who engage with ${topic.topic} regularly tend to perform better in related tasks. This suggests that ${topic.topic} is not just theoretical but has practical applications.\n\nIn conclusion, ${topic.topic} is an important field that deserves our attention. I encourage you to read more about it and think about how it applies to your own lives. Are there any questions?`;
  
  const questionTemplates = [
    { text: `What is the lecture mainly about?`, options: [topic.topic, 'A different subject', 'A research method', 'A historical event'], answer: topic.topic },
    { text: 'How many main aspects does the speaker mention?', options: ['Two', 'Three', 'Four', 'Five'], answer: 'Three' },
    { text: 'What did the recent study find?', options: ['No effect', 'Positive results', 'Negative results', 'Mixed results'], answer: 'Positive results' },
    { text: 'What does the speaker encourage students to do?', options: ['Take a test', 'Read more', 'Write an essay', 'Do an experiment'], answer: 'Read more' },
    { text: 'What is the speaker\'s overall attitude?', options: ['Pessimistic', 'Optimistic', 'Neutral', 'Critical'], answer: 'Optimistic' },
  ];
  
  const questions = questionTemplates.map((q, i) => {
    const so = shuffleOptions(q.options, q.answer);
    return {
      id: `vstep-l${testNum}-s3-q${baseQ + i}`,
      number: baseQ + i,
      type: 'mcq',
      text: q.text,
      options: so.options,
      answer: so.answer,
      explanation: `The lecturer discusses: ${q.answer.toLowerCase()}.`,
    };
  });
  
  return { text, questions };
}

// ── Reading Generator ─────────────────────────────────────────────────

function generateReadingTest(num) {
  const topics = shuffle(READING_TOPICS).slice(0, 4);
  const passages = topics.map((t, i) => {
    const passageText = generatePassageText(t, num, i);
    const questions = generatePassageQuestions(t, `vstep-r${num}-p${i + 1}`, (i + 1), num);
    return {
      id: `vstep-r${num}-p${i + 1}`,
      number: i + 1,
      title: `Passage ${i + 1}: ${t.title}`,
      difficulty: t.difficulty,
      instructions: 'Read the passage and answer the questions below.',
      text: passageText,
      questions,
    };
  });
  
  return {
    id: `vstep-reading-${num}`,
    title: `VSTEP Reading Practice Test ${num}`,
    time_minutes: 60,
    passages,
  };
}

function generatePassageText(topic, testNum, idx) {
  const intros = [
    `In recent years, ${topic.title.toLowerCase()} has become a topic of growing interest among researchers and the general public alike. This article explores the key aspects of this subject and its implications for society.`,
    `The study of ${topic.title.toLowerCase()} reveals fascinating insights into how our world works. Experts from various fields have contributed to our understanding of this important topic.`,
    `${topic.title} is a subject that touches many aspects of daily life. This passage examines the history, current trends, and future directions of this field.`,
    `Understanding ${topic.title.toLowerCase()} requires us to look at both historical evidence and modern research. This article provides an overview of the main findings and debates.`,
  ];
  
  const body1 = `One of the most significant aspects of ${topic.title.toLowerCase()} is its impact on everyday life. Research has shown that people who are knowledgeable about this topic tend to make better decisions. For example, a study conducted at a major university found that participants who were educated about ${topic.title.toLowerCase()} showed a 40 percent improvement in related tasks compared to those who were not.`;

  const body2 = `However, there are challenges. Critics argue that the focus on ${topic.title.toLowerCase()} may be overstated. They point out that other factors are equally important. Despite these criticisms, the majority of experts agree that ${topic.title.toLowerCase()} deserves serious attention and further study.`;

  const body3 = `Looking to the future, researchers are optimistic. New technologies and methods are being developed that will help us better understand ${topic.title.toLowerCase()}. Governments and institutions are investing more resources in this area, recognizing its importance for long-term development.`;

  const conclusion = `In conclusion, ${topic.title.toLowerCase()} is a complex but important subject. While there is still much to learn, the progress made so far is encouraging. As our understanding grows, so does our ability to address the challenges and opportunities that this topic presents.`;

  return [pick(intros, idx), body1, body2, body3, conclusion].join('\n\n');
}

function generatePassageQuestions(topic, prefix, passageNum, testNum) {
  const baseQ = 1;
  const questionTemplates = [
    { text: 'What is the main idea of the passage?', options: [`The importance of ${topic.title.toLowerCase()}`, 'A criticism of modern science', 'A historical timeline', 'A personal story'], answer: `The importance of ${topic.title.toLowerCase()}` },
    { text: 'According to the passage, what did the university study find?', options: ['No significant results', 'A 40 percent improvement', 'Negative effects', 'Inconclusive results'], answer: 'A 40 percent improvement' },
    { text: 'What do critics argue?', options: ['The topic is overstated', 'The topic is irrelevant', 'The topic is dangerous', 'The topic is solved'], answer: 'The topic is overstated' },
    { text: 'What is the attitude of researchers toward the future?', options: ['Pessimistic', 'Optimistic', 'Indifferent', 'Skeptical'], answer: 'Optimistic' },
    { text: 'What does the passage mainly discuss?', options: ['Problems and solutions', 'History only', 'Future predictions', 'Personal opinions'], answer: 'Problems and solutions' },
    { text: 'The word "significant" in the passage is closest in meaning to:', options: ['Small', 'Important', 'Unclear', 'Recent'], answer: 'Important' },
    { text: 'What does the author conclude?', options: ['The topic is solved', 'More research is needed', 'The topic is unimportant', 'The topic is dangerous'], answer: 'More research is needed' },
    { text: 'Who is investing more resources?', options: ['Only universities', 'Governments and institutions', 'Private individuals', 'No one'], answer: 'Governments and institutions' },
    { text: 'What percentage improvement was found?', options: ['20 percent', '30 percent', '40 percent', '50 percent'], answer: '40 percent' },
    { text: 'What is the overall tone of the passage?', options: ['Critical', 'Informative', 'Humorous', 'Pessimistic'], answer: 'Informative' },
  ];
  
  return questionTemplates.map((q, i) => {
    const so = shuffleOptions(q.options, q.answer);
    return {
      id: `${prefix}-q${baseQ + i}`,
      number: baseQ + i,
      type: 'mcq',
      text: q.text,
      options: so.options,
      answer: so.answer,
      explanation: `Based on the passage: ${q.answer.toLowerCase()}.`,
    };
  });
}

// ── Writing Generator ────────────────────────────────────────────────

function generateWritingTest(num) {
  const task1Topic = pick(WRITING_TASK1_TOPICS, num - 1);
  const task2Topic = pick(WRITING_TASK2_TOPICS, num - 1);
  
  return {
    id: `vstep-writing-${num}`,
    title: `VSTEP Writing Practice Test ${num}`,
    task1: {
      id: `vstep-w${num}-t1`,
      type: 'task1',
      title: 'Task 1: Letter/Email',
      instructions: 'You should spend about 20 minutes on this task. Write at least 120 words.',
      prompt: task1Topic,
      min_words: 120,
      time_minutes: 20,
      band_descriptors: {
        task_achievement: 'All parts of the task are addressed. Tone is appropriate.',
        coherence: 'Ideas are logically organized with clear paragraphs.',
        lexical_resource: 'Good range of vocabulary for the topic.',
        grammar: 'Generally accurate with some attempts at complex structures.',
      },
    },
    task2: {
      id: `vstep-w${num}-t2`,
      type: 'task2',
      title: 'Task 2: Essay',
      instructions: 'You should spend about 40 minutes on this task. Write at least 250 words.',
      prompt: task2Topic,
      min_words: 250,
      time_minutes: 40,
      band_descriptors: {
        task_achievement: 'Both views are discussed and a clear opinion is given.',
        coherence: 'Clear paragraphing with logical flow of ideas.',
        lexical_resource: 'Wide range of vocabulary used accurately.',
        grammar: 'Good control of grammar with complex sentences.',
      },
    },
  };
}

// ── Speaking Generator ───────────────────────────────────────────────

function generateSpeakingTest(num) {
  const p1Set = pick(SPEAKING_P1_QUESTIONS, num - 1);
  const p2Question = pick(SPEAKING_P2_QUESTIONS, num - 1);
  const p3Set = pick(SPEAKING_P3_QUESTIONS, num - 1);
  
  return {
    id: `vstep-speaking-${num}`,
    title: `VSTEP Speaking Practice Test ${num}`,
    parts: [
      {
        part: 1,
        title: 'Part 1: Social Interaction',
        instructions: 'The examiner will ask you questions about yourself and general topics. Answer fully.',
        timeMinutes: 4,
        questions: p1Set,
      },
      {
        part: 2,
        title: 'Part 2: Solution Discussion',
        instructions: 'You will be given a situation with three possible solutions. Choose the best solution and explain why. You have 1 minute to prepare and 3 minutes to speak.',
        timeMinutes: 4,
        questions: [p2Question],
      },
      {
        part: 3,
        title: 'Part 3: Topic Development',
        instructions: 'You will speak about a given topic for 2-3 minutes. You may use the prompts below to help you. The examiner may ask follow-up questions.',
        timeMinutes: 4,
        questions: p3Set,
      },
    ],
  };
}

// ── Main ─────────────────────────────────────────────────────────────

function generate() {
  console.log('Generating VSTEP test data...\n');

  // Listening
  console.log('Generating 500 VSTEP listening tests...');
  const listening = [];
  for (let i = 1; i <= TOTAL_TESTS; i++) {
    listening.push(generateListeningTest(i));
  }
  fs.writeFileSync(path.join(OUTPUT_DIR, 'vstep_listening_tests.json'), JSON.stringify(listening));
  console.log(`  ✓ ${listening.length} tests, ${listening.reduce((s, t) => s + t.sections.reduce((ss, sec) => ss + sec.questions.length, 0), 0)} questions`);

  // Reading
  console.log('Generating 500 VSTEP reading tests...');
  const reading = [];
  for (let i = 1; i <= TOTAL_TESTS; i++) {
    reading.push(generateReadingTest(i));
  }
  fs.writeFileSync(path.join(OUTPUT_DIR, 'vstep_reading_tests.json'), JSON.stringify(reading));
  console.log(`  ✓ ${reading.length} tests, ${reading.reduce((s, t) => s + t.passages.reduce((sp, p) => sp + p.questions.length, 0), 0)} questions`);

  // Writing
  console.log('Generating 500 VSTEP writing tests...');
  const writing = [];
  for (let i = 1; i <= TOTAL_TESTS; i++) {
    writing.push(generateWritingTest(i));
  }
  fs.writeFileSync(path.join(OUTPUT_DIR, 'vstep_writing_tests.json'), JSON.stringify(writing));
  console.log(`  ✓ ${writing.length} tests`);

  // Speaking
  console.log('Generating 500 VSTEP speaking tests...');
  const speaking = [];
  for (let i = 1; i <= TOTAL_TESTS; i++) {
    speaking.push(generateSpeakingTest(i));
  }
  fs.writeFileSync(path.join(OUTPUT_DIR, 'vstep_speaking_tests.json'), JSON.stringify(speaking));
  console.log(`  ✓ ${speaking.length} tests`);

  console.log('\nDone! All VSTEP test data generated.');
  console.log(`  Listening: ${listening.length} tests`);
  console.log(`  Reading:   ${reading.length} tests`);
  console.log(`  Writing:   ${writing.length} tests`);
  console.log(`  Speaking:  ${speaking.length} tests`);
}

generate();
