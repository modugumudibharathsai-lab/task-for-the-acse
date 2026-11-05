export interface ClubMember {
  id: string;
  name: string;
  role: string;
  details: string;
}

export interface ClubJoiningStep {
  order: number;
  title: string;
  description: string;
}

export interface Club {
  id: string;
  name: string;
  category: string;
  description: string;
  themeColor: string;
  members: ClubMember[];
  joiningSteps: ClubJoiningStep[];
  activities: string[];
  availableResources: string[];
}

export const CLUBS_DATA: Club[] = [
  {
    id: "ANC",
    name: "Anti-Ragging Cell (ANC)",
    category: "Statutory",
    description: "The university maintains a strict zero-tolerance policy towards ragging. ANC ensures a safe, welcoming environment for all freshers.",
    themeColor: "rose",
    members: [
      { id: "m1", name: "Prof. Rajiv Sharma", role: "Chief Nodal Officer", details: "Contact for any immediate grievance or ragging reports." },
      { id: "m2", name: "Dr. Smita Rao", role: "Faculty Coordinator", details: "Oversees hostel patrols and anti-ragging squads." }
    ],
    joiningSteps: [],
    activities: ["Daily Hostel Patrols", "Fresher Orientation Programs", "Anonymous Grievance Resolution"],
    availableResources: ["24/7 Helpline Number", "Anonymous Web Portal for Complaints", "Confidential Counseling Sessions"]
  },
  {
    id: "SAC",
    name: "Student Activities Center (SAC)",
    category: "Administrative",
    description: "The core committee governing all student cultural, technical, and sports events across the campus.",
    themeColor: "blue",
    members: [
      { id: "m3", name: "Rahul Verma", role: "Student President", details: "4th Year, CSE. Leads the SAC executive council." },
      { id: "m4", name: "Priya Singh", role: "Cultural Secretary", details: "3rd Year, ECE. Organizes all major university fests." }
    ],
    joiningSteps: [
      { order: 1, title: "Fill the Online Application", description: "Login to the student portal and submit the SAC membership form detailing your past experiences." },
      { order: 2, title: "Portfolio Review", description: "The executive council will review your submission and shortlist candidates based on skill sets." },
      { order: 3, title: "Interview Round", description: "A formal interview with the current SAC committee to gauge your leadership and teamwork skills." },
      { order: 4, title: "Final Induction", description: "Selected candidates are officially inducted during the annual SAC orientation ceremony." }
    ],
    activities: ["Annual Inter-College Fest Organization", "Inter-departmental Sports Tournaments", "Monthly Club Review Meetings"],
    availableResources: ["Event Management Toolkits", "Budget Allocation Portal", "SAC Boardroom Booking"]
  },
  {
    id: "TECH",
    name: "Code & Build Club",
    category: "Technical",
    description: "A community for aspiring software developers, hardware tinkerers, and AI enthusiasts.",
    themeColor: "emerald",
    members: [
      { id: "m5", name: "Amit Patel", role: "Lead Organizer", details: "Full-stack developer and open-source contributor." }
    ],
    joiningSteps: [
      { order: 1, title: "Join the Discord Server", description: "All technical discussions happen on our public Discord server. Link is on the club notice board." },
      { order: 2, title: "Solve the Entry Challenge", description: "Complete a basic algorithmic or web development task to prove your fundamental knowledge." },
      { order: 3, title: "Attend the First Meetup", description: "Come to the lab during our weekly meetup and present your solution to the senior members." }
    ],
    activities: ["Weekly Algorithm Challenges", "Monthly Hackathons (Internal)", "Open Source Contribution Drives"],
    availableResources: ["High-Performance Computing Lab", "Raspberry Pi & Arduino Kits", "Premium Leetcode Subscriptions (Shared)"]
  },
  {
    id: "CULT",
    name: "Cultural Society",
    category: "Cultural",
    description: "Promoting arts, dance, music, and dramatics. The heartbeat of university fests.",
    themeColor: "purple",
    members: [
      { id: "m6", name: "Neha Gupta", role: "Dance Troupe Lead", details: "Choreographer and state-level dancer." }
    ],
    joiningSteps: [
      { order: 1, title: "Auditions", description: "Keep an eye out for audition posters. Prepare a 2-minute performance (dance, singing, drama)." },
      { order: 2, title: "Callback Round", description: "Perform alongside current members to see if your style matches the troupe's dynamics." },
      { order: 3, title: "Rehearsal Bootcamp", description: "Attend a 3-day intensive boot camp. Selection is confirmed after successfully completing this camp." }
    ],
    activities: ["Weekly Dance Rehearsals", "Music Jam Sessions", "Street Play (Nukkad Natak) Performances"],
    availableResources: ["Fully Equipped Dance Studio", "Musical Instruments (Guitars, Keyboards, Drums)", "Costume & Props Wardrobe"]
  },
  {
    id: "ROBO",
    name: "Robotics Club",
    category: "Technical",
    description: "For enthusiasts of mechanical design, electronics, and autonomous systems.",
    themeColor: "indigo",
    members: [{ id: "m7", name: "Ravi Kumar", role: "President", details: "Specializes in autonomous drone navigation." }],
    joiningSteps: [{ order: 1, title: "Orientation", description: "Attend the introductory session on robotics basics." }, { order: 2, title: "Mini Project", description: "Build a line-following robot in a team." }],
    activities: ["Robo-Wars Preparation", "Drone Flying Sessions", "Weekly Hardware Tinker Labs"],
    availableResources: ["3D Printers", "Soldering Stations", "Microcontroller Kits"]
  },
  {
    id: "DEBATE",
    name: "Debate & MUN Society",
    category: "Literary",
    description: "Fostering critical thinking, public speaking, and global awareness.",
    themeColor: "amber",
    members: [{ id: "m8", name: "Sanya Mirza", role: "Secretary", details: "Winner of National MUN 2024." }],
    joiningSteps: [{ order: 1, title: "Mock Debate", description: "Participate in a 5-minute extempore or mock debate round." }],
    activities: ["Weekly Mock UN Sessions", "Debate Tournaments", "Public Speaking Workshops"],
    availableResources: ["Gavel & Podium Setup", "Research Database Access", "Mentorship from Alumni"]
  },
  {
    id: "PHOTO",
    name: "Photography & Videography Club",
    category: "Creative",
    description: "Capturing moments and teaching visual storytelling.",
    themeColor: "slate",
    members: [{ id: "m9", name: "Kabir Singh", role: "Creative Head", details: "Freelance videographer and editor." }],
    joiningSteps: [{ order: 1, title: "Portfolio Submission", description: "Submit your top 5 best photographs." }],
    activities: ["Photo Walks", "Editing Workshops (Premiere Pro, Lightroom)", "Campus Event Coverage"],
    availableResources: ["DSLR Cameras (Lending Library)", "Studio Lighting Setup", "Green Screen Room"]
  },
  {
    id: "LIT",
    name: "Literature Club",
    category: "Literary",
    description: "A haven for bookworms, poets, and aspiring authors.",
    themeColor: "sky",
    members: [{ id: "m10", name: "Ananya Desai", role: "Editor-in-Chief", details: "Heads the university magazine." }],
    joiningSteps: [{ order: 1, title: "Submit a Piece", description: "Provide a short essay, poem, or story." }],
    activities: ["Book Reading Circles", "Open Mic Poetry", "Creative Writing Workshops"],
    availableResources: ["Club Library", "Publishing Guidance", "Quiet Reading Room"]
  },
  {
    id: "ECELL",
    name: "Entrepreneurship Cell",
    category: "Business",
    description: "Incubating student startups and fostering an entrepreneurial mindset.",
    themeColor: "orange",
    members: [{ id: "m11", name: "Rohan Das", role: "Incubation Lead", details: "Running a successful ed-tech startup." }],
    joiningSteps: [{ order: 1, title: "Pitch Deck", description: "Present a basic pitch deck for a startup idea." }],
    activities: ["Startup Pitch Competitions", "Founder Talk Series", "Business Plan Workshops"],
    availableResources: ["Co-working Space", "Seed Funding Network", "Legal & Patent Advice"]
  },
  {
    id: "ASTRO",
    name: "Astronomy Club",
    category: "Science",
    description: "Exploring the cosmos and organizing stargazing events.",
    themeColor: "violet",
    members: [{ id: "m12", name: "Vikram Sarabhai", role: "Coordinator", details: "Astrophotography enthusiast." }],
    joiningSteps: [{ order: 1, title: "Quiz", description: "Clear a basic astrophysics and astronomy quiz." }],
    activities: ["Night Sky Observation", "Astrophysics Seminars", "Telescope Making Workshops"],
    availableResources: ["Celestron Telescopes", "Star Maps", "Astrophotography Mounts"]
  },
  {
    id: "FINANCE",
    name: "Finance & Investment Club",
    category: "Business",
    description: "Learning stock market trading, personal finance, and crypto.",
    themeColor: "green",
    members: [{ id: "m13", name: "Aman Gupta", role: "Fund Manager", details: "Manages the student mock portfolio." }],
    joiningSteps: [{ order: 1, title: "Mock Trading", description: "Participate in a 1-week mock trading simulation." }],
    activities: ["Stock Market Analysis Sessions", "Financial Modeling Workshops", "Budget Day Live Screening"],
    availableResources: ["Bloomberg Terminal Access", "Trading Simulator Software", "Financial Journals"]
  },
  {
    id: "ENV",
    name: "Environmental Society",
    category: "Social",
    description: "Promoting sustainability and green initiatives on campus.",
    themeColor: "lime",
    members: [{ id: "m14", name: "Riya Sharma", role: "Green Ambassador", details: "Led the zero-waste campus drive." }],
    joiningSteps: [{ order: 1, title: "Volunteer", description: "Volunteer for one campus clean-up drive." }],
    activities: ["Tree Plantation Drives", "Waste Management Awareness", "Upcycling Workshops"],
    availableResources: ["Gardening Tools", "Composting Bins", "Eco-friendly Event Kits"]
  },
  {
    id: "AIML",
    name: "AI & ML Club",
    category: "Technical",
    description: "Diving deep into neural networks, LLMs, and data science.",
    themeColor: "cyan",
    members: [{ id: "m15", name: "Dr. Andrew", role: "Faculty Advisor", details: "AI researcher." }],
    joiningSteps: [{ order: 1, title: "Kaggle Task", description: "Complete a beginner Kaggle dataset prediction." }],
    activities: ["Paper Reading Groups", "Kaggle Competitions", "Model Deployment Workshops"],
    availableResources: ["Cloud GPU Credits", "Curated Datasets", "O'Reilly AI Books"]
  },
  {
    id: "FILM",
    name: "Film & Media Club",
    category: "Creative",
    description: "Writing, directing, and producing short films and documentaries.",
    themeColor: "red",
    members: [{ id: "m16", name: "Karan Johar", role: "Director", details: "Award-winning short filmmaker." }],
    joiningSteps: [{ order: 1, title: "Script/Storyboard", description: "Submit a 2-page script or storyboard." }],
    activities: ["Weekend Movie Screenings", "Short Film Contests", "Scriptwriting Workshops"],
    availableResources: ["4K Cinema Cameras", "Audio Recording Gear", "Editing Bays"]
  },
  {
    id: "ART",
    name: "Fine Arts Club",
    category: "Creative",
    description: "Sketching, painting, digital art, and sculpting.",
    themeColor: "fuchsia",
    members: [{ id: "m17", name: "Shruti Hassan", role: "Lead Artist", details: "Specializes in digital illustrations." }],
    joiningSteps: [{ order: 1, title: "Art Submission", description: "Submit 3 pieces of original artwork." }],
    activities: ["Live Sketching Sessions", "Digital Art Bootcamps", "Annual Art Exhibition"],
    availableResources: ["Easels & Canvases", "Wacom Tablets", "Premium Art Supplies"]
  },
  {
    id: "SPORTS",
    name: "Fitness & Sports Club",
    category: "Sports",
    description: "Promoting physical wellness, gym culture, and field sports.",
    themeColor: "yellow",
    members: [{ id: "m18", name: "Virat K", role: "Sports Captain", details: "University Athletics Champion." }],
    joiningSteps: [{ order: 1, title: "Fitness Test", description: "Pass a basic physical endurance test." }],
    activities: ["Morning Yoga", "Inter-hostel Tournaments", "Marathon Training"],
    availableResources: ["Gym Access", "Sports Equipment (Cricket, Football, Tennis)", "Nutrition Plans"]
  },
  {
    id: "WEB3",
    name: "Blockchain & Web3 Club",
    category: "Technical",
    description: "Building decentralized apps, smart contracts, and exploring crypto.",
    themeColor: "blue",
    members: [{ id: "m19", name: "Satoshi N", role: "Tech Lead", details: "Smart contract auditor." }],
    joiningSteps: [{ order: 1, title: "Smart Contract", description: "Deploy a simple 'Hello World' contract on a testnet." }],
    activities: ["Smart Contract Hacking", "Web3 Ideathons", "DeFi Study Groups"],
    availableResources: ["Testnet Faucets", "Ledger Hardware Wallets", "Solidity Course Licenses"]
  },
  {
    id: "CYBER",
    name: "Cyber Security Club",
    category: "Technical",
    description: "Ethical hacking, CTFs, and network security research.",
    themeColor: "slate",
    members: [{ id: "m20", name: "Alice Hacker", role: "CTF Captain", details: "Top 100 on HackTheBox." }],
    joiningSteps: [{ order: 1, title: "CTF Challenge", description: "Find the flag in our beginner web exploitation challenge." }],
    activities: ["Weekly CTF Practice", "Pen-testing Workshops", "Malware Analysis Labs"],
    availableResources: ["Private VPN Access", "HackTheBox VIP Accounts", "Dedicated Kali Linux Servers"]
  },
  {
    id: "MUSIC",
    name: "Music Society",
    category: "Cultural",
    description: "For vocalists, instrumentalists, and music producers.",
    themeColor: "pink",
    members: [{ id: "m21", name: "A.R. Rahman", role: "Band Leader", details: "Multi-instrumentalist." }],
    joiningSteps: [{ order: 1, title: "Audition", description: "Perform a solo vocal or instrumental piece." }],
    activities: ["Acoustic Nights", "Band Wars", "Music Production (Ableton/FL Studio) Workshops"],
    availableResources: ["Soundproof Jam Room", "Microphones & Mixers", "DAW Software Licenses"]
  }
];
