"""Job taxonomy covering the whole Indian labour market — not just white-collar roles.

Deliberately spans every education level, from no formal schooling (daily wage, domestic,
agriculture) through skilled trades and ITI, to graduate and postgraduate professions.
Each sector carries the education level and wage basis typical for it, so the UI can
default sensibly and job seekers aren't shown fields that don't apply to them.
"""

# wage_basis: daily | monthly | annual | contract | piece_rate
# education: none | 8th | 10th | 12th | iti | diploma | graduate | pg
SECTORS = [
    {
        "key": "skilled_trades", "name": "Skilled Trades & Technicians", "icon": "tools",
        "education": "iti", "wage_basis": "daily", "blurb": "Electricians, plumbers, welders, mechanics",
        "roles": ["Electrician", "Plumber", "Welder", "Carpenter", "Painter", "Mason", "Fitter",
                  "AC & Refrigeration Technician", "Mobile Repair Technician", "Two-Wheeler Mechanic",
                  "Car Mechanic", "Lathe / CNC Operator", "Lift Technician", "Solar Panel Installer",
                  "Borewell Operator", "Tile Layer", "Fabricator", "Sheet Metal Worker", "Turner",
                  "Wireman", "Pump Operator", "Generator Technician"],
    },
    {
        "key": "daily_wage", "name": "Daily Wage & Construction", "icon": "hardhat",
        "education": "none", "wage_basis": "daily", "blurb": "Labour, helpers, loading, construction",
        "roles": ["Construction Labour", "Helper", "Loader / Unloader", "Mazdoor", "Road Worker",
                  "Building Cleaner", "Demolition Worker", "Scaffolder", "Concrete Mixer Operator",
                  "Site Watchman", "Earthwork Labour", "Packing Helper", "Warehouse Loader",
                  "Municipality Contract Worker", "Sanitation Worker", "Drainage Worker",
                  "Garbage Collection Staff", "Street Light Maintenance"],
    },
    {
        "key": "domestic", "name": "Domestic & Home Services", "icon": "home",
        "education": "none", "wage_basis": "monthly", "blurb": "Housekeeping, cooks, caretakers, nannies",
        "roles": ["House Maid", "Housekeeping Staff", "Home Cook", "Nanny / Babysitter",
                  "Elderly Caretaker", "Patient Attendant (Home)", "Gardener / Mali", "Watchman",
                  "Driver (Personal)", "Cleaner", "Dishwasher (Home)", "Laundry / Ironing Staff",
                  "Pet Caretaker", "Home Nurse", "Cook (Vegetarian)", "Cook (Non-Vegetarian)",
                  "Part-time Maid", "Live-in Caretaker"],
    },
    {
        "key": "hospitality", "name": "Hotels, Restaurants & Catering", "icon": "utensils",
        "education": "10th", "wage_basis": "monthly", "blurb": "Chefs, servers, hotel and restaurant staff",
        "roles": ["Chef", "Head Chef", "Sous Chef", "Commis Chef", "Tandoor Chef", "Chinese Chef",
                  "South Indian Cook", "Kitchen Helper", "Dishwasher", "Waiter / Server", "Bearer",
                  "Steward", "Captain", "Bartender", "Barista", "Hotel Receptionist", "Front Office Executive",
                  "Housekeeping Supervisor", "Room Attendant", "Laundry Staff", "Banquet Staff",
                  "Catering Staff", "Restaurant Manager", "Cashier", "Delivery Boy", "Food Packer",
                  "Bakery Assistant", "Sweet Shop Staff", "Juice Counter Staff"],
    },
    {
        "key": "healthcare", "name": "Hospital & Healthcare", "icon": "heart",
        "education": "12th", "wage_basis": "monthly", "blurb": "All hospital roles, clinical and support",
        "roles": ["Doctor (MBBS)", "Specialist Doctor", "Dentist", "Staff Nurse", "ANM / GNM Nurse",
                  "Ward Boy", "Ward Aaya", "Patient Attendant", "Lab Technician", "Radiographer",
                  "X-Ray Technician", "Pharmacist", "Physiotherapist", "Dialysis Technician",
                  "OT Technician", "ECG Technician", "Ambulance Driver", "Hospital Receptionist",
                  "Medical Records Clerk", "Hospital Housekeeping", "Biomedical Engineer",
                  "Optometrist", "Dietician", "Medical Representative", "Hospital Billing Executive"],
    },
    {
        "key": "agriculture", "name": "Agriculture & Rural", "icon": "leaf",
        "education": "none", "wage_basis": "daily", "blurb": "Farm work, dairy, poultry, rural trades",
        "roles": ["Farm Labour", "Tractor Driver", "Harvester Operator", "Irrigation Worker",
                  "Dairy Farm Worker", "Milkman", "Poultry Farm Worker", "Goat / Sheep Herder",
                  "Fish Farm Worker", "Plantation Worker", "Nursery Worker", "Horticulture Assistant",
                  "Pesticide Sprayer", "Seed Processing Worker", "Cold Storage Worker",
                  "Mandi / Market Helper", "Agri Equipment Mechanic", "Beekeeper", "Sericulture Worker",
                  "Agriculture Field Officer", "Veterinary Assistant"],
    },
    {
        "key": "retail", "name": "Retail, Kirana & Sales", "icon": "store",
        "education": "10th", "wage_basis": "monthly", "blurb": "Shops, kirana stores, showrooms, field sales",
        "roles": ["Kirana Store Helper", "Shop Assistant", "Counter Salesman", "Cashier",
                  "Store Manager", "Showroom Executive", "Field Sales Executive", "Medical Store Assistant",
                  "Textile Shop Staff", "Jewellery Shop Staff", "Mobile Shop Salesman", "Stock Boy",
                  "Merchandiser", "Billing Operator", "Supermarket Staff", "Vegetable Vendor Assistant",
                  "Hardware Store Staff", "Petrol Pump Attendant", "Sales Officer", "Area Sales Manager"],
    },
    {
        "key": "logistics", "name": "Driving, Delivery & Logistics", "icon": "truck",
        "education": "8th", "wage_basis": "monthly", "blurb": "Drivers, delivery, warehouse, transport",
        "roles": ["Auto Driver", "Taxi / Cab Driver", "Truck Driver", "Heavy Vehicle Driver",
                  "Bus Driver", "Tempo Driver", "Delivery Executive", "Courier Boy", "Rider (Bike)",
                  "Warehouse Staff", "Packing Staff", "Inventory Assistant", "Forklift Operator",
                  "Logistics Coordinator", "Dispatch Clerk", "Loading Supervisor", "Fleet Supervisor"],
    },
    {
        "key": "security", "name": "Security & Facility", "icon": "shield",
        "education": "10th", "wage_basis": "monthly", "blurb": "Guards, supervisors, facility management",
        "roles": ["Security Guard", "Head Security Guard", "Gunman", "Bouncer", "CCTV Operator",
                  "Facility Supervisor", "Building Manager", "Society Caretaker", "Fire Safety Officer",
                  "Gatekeeper", "Parking Attendant"],
    },
    {
        "key": "manufacturing", "name": "Manufacturing & Factory", "icon": "factory",
        "education": "iti", "wage_basis": "monthly", "blurb": "Production, machine operation, quality",
        "roles": ["Machine Operator", "Production Helper", "Assembly Line Worker", "Quality Inspector",
                  "Packing Operator", "Boiler Operator", "Maintenance Technician", "Store Keeper",
                  "Production Supervisor", "Shift Incharge", "Tool Room Operator", "Textile Worker",
                  "Garment Tailor", "Embroidery Worker", "Printing Operator", "Plastic Moulding Operator",
                  "Food Processing Worker", "Chemical Plant Operator"],
    },
    {
        "key": "it", "name": "IT & Software", "icon": "code",
        "education": "graduate", "wage_basis": "annual", "blurb": "Engineering, data, design, QA, support",
        "roles": ["Software Engineer", "Senior Software Engineer", "Full Stack Developer",
                  "Frontend Developer", "Backend Developer", "Mobile App Developer", "DevOps Engineer",
                  "Data Analyst", "Data Scientist", "ML Engineer", "QA / Test Engineer",
                  "Business Analyst", "Product Manager", "UI/UX Designer", "Cloud Engineer",
                  "Database Administrator", "Cybersecurity Analyst", "Technical Support Engineer",
                  "IT Helpdesk", "Network Engineer", "Scrum Master", "Solution Architect"],
    },
    {
        "key": "corporate", "name": "Corporate, Finance & Consulting", "icon": "briefcase",
        "education": "graduate", "wage_basis": "annual", "blurb": "Finance, HR, admin, consulting, insurance",
        "roles": ["Accountant", "Junior Accountant", "Tally Operator", "Chartered Accountant",
                  "Finance Manager", "Auditor", "HR Executive", "HR Manager", "Recruiter",
                  "Talent Acquisition Specialist", "Payroll Executive", "Admin Executive",
                  "Office Assistant", "Data Entry Operator", "Receptionist", "Back Office Executive",
                  "Customer Support Executive", "Tele Caller", "Insurance Advisor", "Insurance Agent",
                  "Loan Officer", "Bank Clerk", "Relationship Manager", "Management Consultant",
                  "Operations Manager", "Business Development Executive", "Digital Marketing Executive",
                  "Content Writer", "Graphic Designer", "Legal Advisor", "Company Secretary"],
    },
    {
        "key": "education", "name": "Education & Training", "icon": "cap",
        "education": "graduate", "wage_basis": "monthly", "blurb": "Teachers, trainers, school staff",
        "roles": ["School Teacher", "Primary Teacher", "Subject Teacher", "Lecturer", "Professor",
                  "Home Tutor", "Coaching Faculty", "Lab Assistant", "Librarian", "Physical Education Teacher",
                  "Anganwadi Worker", "Special Educator", "Training Coordinator", "Placement Officer",
                  "School Admin", "School Bus Driver", "Ayah / Attendant"],
    },
    {
        "key": "government", "name": "Government & Municipality", "icon": "building",
        "education": "10th", "wage_basis": "monthly", "blurb": "Municipal contracts, public works, civic roles",
        "roles": ["Municipality Contractor", "Contract Labour (Civic)", "Sanitary Supervisor",
                  "Water Works Operator", "Public Health Worker", "Field Surveyor", "Clerk",
                  "Peon / Attendant", "Data Entry (Government Scheme)", "ASHA Worker",
                  "Panchayat Assistant", "Revenue Assistant", "Forest Guard", "Home Guard"],
    },
    {
        "key": "beauty_events", "name": "Beauty, Events & Personal Services", "icon": "sparkle",
        "education": "none", "wage_basis": "monthly", "blurb": "Salon, tailoring, events, photography",
        "roles": ["Beautician", "Hair Stylist", "Barber", "Makeup Artist", "Spa Therapist",
                  "Massage Therapist", "Tailor", "Boutique Assistant", "Event Helper",
                  "Decorator", "Photographer", "Videographer", "DJ", "Wedding Planner Assistant",
                  "Mehendi Artist", "Fitness Trainer", "Yoga Instructor", "Swimming Coach"],
    },
]

# Flat lookups used by search filters and AI prompts.
ALL_ROLES = sorted({r for s in SECTORS for r in s["roles"]})
SECTOR_KEYS = [s["key"] for s in SECTORS]

EDUCATION_LEVELS = [
    {"key": "none", "label": "No formal education required"},
    {"key": "8th", "label": "8th pass"},
    {"key": "10th", "label": "10th pass"},
    {"key": "12th", "label": "12th / Intermediate"},
    {"key": "iti", "label": "ITI / Certificate"},
    {"key": "diploma", "label": "Diploma"},
    {"key": "graduate", "label": "Graduate"},
    {"key": "pg", "label": "Post Graduate"},
]

WAGE_BASIS = [
    {"key": "daily", "label": "Daily wage"},
    {"key": "weekly", "label": "Weekly"},
    {"key": "monthly", "label": "Monthly salary"},
    {"key": "annual", "label": "Annual (LPA)"},
    {"key": "contract", "label": "Contract / project"},
    {"key": "piece_rate", "label": "Piece rate"},
]

JOB_TYPES = [
    {"key": "full_time", "label": "Full time"},
    {"key": "part_time", "label": "Part time"},
    {"key": "daily", "label": "Daily / casual"},
    {"key": "contract", "label": "Contract"},
    {"key": "temporary", "label": "Temporary / seasonal"},
    {"key": "apprentice", "label": "Apprentice / trainee"},
    {"key": "wfh", "label": "Work from home"},
]


def sector_for_role(role: str) -> dict | None:
    r = (role or "").strip().lower()
    for s in SECTORS:
        if any(r == x.lower() for x in s["roles"]):
            return s
    for s in SECTORS:   # partial match fallback
        if any(r in x.lower() or x.lower() in r for x in s["roles"] if r):
            return s
    return None


def taxonomy_payload() -> dict:
    return {
        "sectors": [{k: v for k, v in s.items()} for s in SECTORS],
        "education_levels": EDUCATION_LEVELS,
        "wage_basis": WAGE_BASIS,
        "job_types": JOB_TYPES,
        "role_count": len(ALL_ROLES),
    }
