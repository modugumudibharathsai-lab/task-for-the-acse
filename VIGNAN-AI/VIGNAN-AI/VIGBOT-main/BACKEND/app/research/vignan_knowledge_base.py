"""
Vignan University Official Knowledge Base & Source Registry
Curated and structured knowledge from official VFSTR portals, academic regulations,
manuals, notifications, departmental sites, fee structures, and campus guidelines.
"""

from typing import Dict, Any, List

OFFICIAL_SOURCES: List[Dict[str, Any]] = [
    {
        "source_id": "SRC_VIG_01_ABOUT",
        "url": "https://vignan.ac.in/newvignan/aboutus.php",
        "title": "About VFSTR - University Overview, Accreditation & NIRF",
        "type": "official_portal",
        "category": "administration",
        "last_verified": "2026-10-29",
        "key_facts": {
            "full_name": "Vignan's Foundation for Science, Technology and Research (Deemed to be University)",
            "short_name": "VFSTR / Vignan University",
            "established_year": 2008,
            "status": "Deemed to be University under Section 3 of UGC Act 1956",
            "location": "Vadlamudi, Chebrolu Mandal, Guntur District, Andhra Pradesh - 522213",
            "campus_area": "43 acres green Wi-Fi enabled campus",
            "naac_grade": "A+ Grade with CGPA of 3.49",
            "nirf_ranking_2024": "Ranked 75th in University Category, ranked in 101-150 Engineering Band",
            "ugc_category": "Category-II Deemed University status by UGC/MHRD",
            "chancellor": "Dr. Lavu Rathaiah (Founder Chairman)",
            "vice_chancellor": "Prof. P. Nagabhushan",
            "registrar": "Dr. M. S. Raghunathan"
        }
    },
    {
        "source_id": "SRC_VIG_02_REG_R23",
        "url": "https://vignan.ac.in/newvignan/Regulations.php",
        "title": "Academic Regulations R23 for B.Tech Programmes",
        "type": "academic_regulation",
        "category": "academic_policy",
        "last_verified": "2026-10-29",
        "key_facts": {
            "regulation": "R23",
            "applicable_batches": "Admitted 2023-24, 2024-25 onwards",
            "attendance_minimum": "75.0% aggregate across all registered courses in semester",
            "condonation_bracket": "65.0% to 74.9% strictly on valid medical grounds or approved institutional participation",
            "condonation_fee": "Rs. 1,000 per semester",
            "detention_clause": "Below 65.0% aggregate attendance is non-condonable; student is detained and must repeat semester",
            "continuous_internal_eval_weightage": "40 Marks (CIE-1: 15 marks, CIE-2: 15 marks, Quizzes/Assignments: 10 marks)",
            "semester_end_eval_weightage": "60 Marks (Semester End Examination - SEE)",
            "minimum_passing_marks": "35% in SEE (21/60) and 40% aggregate (40/100)",
            "grading_scale": "S (10), A (9), B (8), C (7), D (6), E (5), F (0 - Fail)",
            "promotion_to_year_3": "Must secure at least 50% of total credits prescribed in Year 1",
            "promotion_to_year_4": "Must secure at least 50% of total credits prescribed in Years 1 & 2",
            "revaluation_deadline": "Within 15 days of official result declaration on examination portal",
            "revaluation_fee": "Rs. 1,000 per course script",
            "total_credits_for_btech": "160 Credits for 4-year regular degree, 120 credits for lateral entry"
        }
    },
    {
        "source_id": "SRC_VIG_03_REG_R25_R26",
        "url": "https://vignan.ac.in/newvignan/Regulations.php",
        "title": "Academic Regulations R25 & R26 (NEP 2020 Aligned)",
        "type": "academic_regulation",
        "category": "academic_policy",
        "last_verified": "2026-10-29",
        "key_facts": {
            "regulation": "R25 / R26",
            "alignment": "National Education Policy (NEP 2020) with Multiple Entry / Multiple Exit (MEME)",
            "attendance_requirement": "75.0% mandatory aggregate attendance strictly enforced across LMS and biometric portals",
            "medical_condonation": "65.0% to 74.9% with prior intimation to HoD and medical certification authenticated by campus medical officer",
            "internship_mandate": "Mandatory 6-month industry semester internship in Year 4 Semester 2 (12 credits)",
            "minor_and_honors": "Requires additional 18-20 credits with minimum CGPA of 7.5 without active backlogs"
        }
    },
    {
        "source_id": "SRC_VIG_04_FEES_SCHOLARSHIPS",
        "url": "https://vignan.ac.in/newvignan/fee_str_hyd.php",
        "title": "B.Tech Tuition Fee Structure & V-SAT Merit Scholarships (2024-2026)",
        "type": "official_fee_notification",
        "category": "fees_and_scholarships",
        "last_verified": "2026-10-29",
        "key_facts": {
            "btech_cse_tuition_annual": "Rs. 2,80,000 per year (Category A admission)",
            "btech_ece_tuition_annual": "Rs. 2,00,000 per year",
            "btech_mech_civil_tuition": "Rs. 1,40,000 per year",
            "admission_registration_fee": "Rs. 10,000 (one-time non-refundable)",
            "caution_deposit": "Rs. 5,000 (refundable on course completion)",
            "vsat_rank_1_to_100": "100% Tuition Fee Waiver for all 4 years",
            "vsat_rank_101_to_500": "75% Tuition Fee Waiver for Year 1",
            "vsat_rank_501_to_1000": "50% Tuition Fee Waiver for Year 1",
            "vsat_rank_1001_to_2000": "25% Tuition Fee Waiver for Year 1",
            "ipe_intermediate_percentage_95_plus": "75% Tuition Fee Waiver for Year 1",
            "ipe_intermediate_percentage_90_to_94": "50% Tuition Fee Waiver for Year 1",
            "ipe_intermediate_percentage_80_to_89": "25% Tuition Fee Waiver for Year 1",
            "scholarship_renewal_condition": "Must maintain minimum CGPA of 8.0 with no standing backlogs in any semester",
            "fee_payment_modes": "Online ERP portal via Netbanking/UPI/Cards or Demand Draft payable at Guntur"
        }
    },
    {
        "source_id": "SRC_VIG_05_HOSTELS",
        "url": "https://vignan.ac.in/newvignan/facilities.php",
        "title": "Campus Hostels, Dining, Accommodation & Security Rules",
        "type": "campus_facilities",
        "category": "campus_life",
        "last_verified": "2026-10-29",
        "key_facts": {
            "hostels_boys": "Priyamvada & Vashishta Boys Hostels with AC and Non-AC room options (2, 3, and 4 sharing)",
            "hostels_girls": "Sarojini Devi & Priyadarshini Girls Hostels with 24/7 security and biometric entry",
            "hostel_fee_non_ac": "Rs. 95,000 to Rs. 1,05,000 per academic year (including dining)",
            "hostel_fee_ac": "Rs. 1,35,000 to Rs. 1,45,000 per academic year (including dining)",
            "mess_food": "Hygienic vegetarian and non-vegetarian food (chicken/egg served 3 days a week)",
            "curfew_timings": "Girls Hostel: 6:30 PM (entry); Boys Hostel: 8:00 PM (entry)",
            "outing_permission": "Requires online parent approval via Vignan Student ERP portal before gate pass issuance",
            "amenities": "High-speed Wi-Fi, solar hot water, 24/7 medical room with ambulance, gym, laundry service"
        }
    },
    {
        "source_id": "SRC_VIG_06_TRANSPORT",
        "url": "https://vignan.ac.in/newvignan/facilities.php",
        "title": "University Transportation System - Bus Routes & Fees",
        "type": "campus_facilities",
        "category": "transport",
        "last_verified": "2026-10-29",
        "key_facts": {
            "fleet_size": "50+ luxury GPS-tracked buses operated by VFSTR",
            "coverage_cities": "Guntur, Vijayawada, Tenali, Mangalagiri, Ponnur, Chilakaluripet, Bapatla",
            "guntur_bus_fee": "Rs. 24,000 to Rs. 28,000 per year (depending on boarding stage)",
            "vijayawada_bus_fee": "Rs. 32,000 to Rs. 36,000 per year",
            "tenali_bus_fee": "Rs. 22,000 to Rs. 25,000 per year",
            "bus_pass_issuance": "Available through Transport Office after fee clearance; mandatory RFID bus card scan"
        }
    },
    {
        "source_id": "SRC_VIG_07_PLACEMENTS",
        "url": "https://vignan.ac.in/newvignan/placements.php",
        "title": "Corporate Relations & Placement Statistics (2023-2025)",
        "type": "placement_report",
        "category": "placements",
        "last_verified": "2026-10-29",
        "key_facts": {
            "placement_percentage": "92%+ of eligible registered students placed consistently",
            "highest_package": "Rs. 44.0 LPA (offered by Amazon)",
            "average_package": "Rs. 5.6 LPA across all engineering branches",
            "top_tier_recruiters": "Amazon, Cisco, TCS, Cognizant, Wipro, Accenture, DXC, HCL, Mindtree, Hyundai, KIA",
            "eligibility_for_placements": "Minimum 60% / 6.5 CGPA in 10th, 12th, and B.Tech with no active backlogs",
            "pre_placement_training": "Starts from 2nd year (verbal ability, quantitative aptitude, DSA, coding bootcamps)"
        }
    },
    {
        "source_id": "SRC_VIG_08_GRIEVANCE_SAFETY",
        "url": "https://vignan.ac.in/newvignan/grievance.php",
        "title": "Student Grievance Redressal, Anti-Ragging & Mental Health Support",
        "type": "official_statutory_policy",
        "category": "student_services",
        "last_verified": "2026-10-29",
        "key_facts": {
            "sgrc_committee": "Student Grievance Redressal Committee constituted under UGC Regulations 2023",
            "anti_ragging_policy": "Zero tolerance for ragging. Expulsion, FIR, and 2-year debarment under AP Prohibition of Ragging Act",
            "national_anti_ragging_helpline": "1800-180-5522 (Toll Free, 24/7) / helpline@antiragging.in",
            "campus_anti_ragging_squad": "Dean of Student Affairs Office / Chief Warden / Security Control Room",
            "mental_health_crisis": "National Tele-MANAS Helpline: 14416 / 1800-891-4416 (24/7 Toll-Free Free Counseling)",
            "campus_counseling_cell": "Student Wellness & Counseling Center, Ground Floor, Central Library Building",
            "internal_complaints_committee": "ICC for prevention of sexual harassment headed by senior woman professor"
        }
    },
    {
        "source_id": "SRC_VIG_09_EXAM_CELL",
        "url": "https://vignan.ac.in/newvignan/contact.php",
        "title": "Examination Cell & Administrative Office Directory",
        "type": "official_directory",
        "category": "student_services",
        "last_verified": "2026-10-29",
        "key_facts": {
            "controller_of_examinations": "Ground Floor, A-Block (Administrative Block)",
            "transcript_application": "Apply through Vignan ERP portal or in-person with prescribed fee of Rs. 500 per set",
            "duplicate_hall_ticket": "Issued at Examination Branch with Rs. 100 fine and ID proof",
            "grade_card_correction": "Submit application to Dean Academics / CoE along with original mark sheets",
            "office_hours": "Monday to Saturday: 9:00 AM to 5:00 PM (Lunch break: 1:00 PM to 2:00 PM; Closed 2nd Saturday & Sunday)"
        }
    },
    {
        "source_id": "SRC_VIG_10_CSE_CURRICULUM",
        "url": "https://vignan.ac.in/newvignan/departments/depthome.php?deptid=sch3_dept1&deptnm=CSE&school=sch3",
        "title": "Department of Computer Science & Engineering - Curriculum & Labs",
        "type": "departmental_curriculum",
        "category": "curriculum",
        "last_verified": "2026-10-29",
        "key_facts": {
            "department": "Computer Science and Engineering (CSE)",
            "school": "School of Computing and Informatics (SCI)",
            "head_of_department": "Prof. & HoD, Department of CSE",
            "specializations": "CSE Core, AI & ML, Cyber Security, Data Science, Cloud Computing, IoT",
            "core_subjects_sem_3": "Data Structures, Database Management Systems, Discrete Mathematics, Digital Electronics",
            "core_subjects_sem_4": "Design & Analysis of Algorithms, Operating Systems, Computer Organization & Architecture",
            "core_subjects_sem_5": "Computer Networks, Formal Languages & Automata Theory, Web Technologies, Software Engineering",
            "advanced_labs": "AI Research Lab, IoT & Embedded Systems Lab, Nvidia GPU Supercomputing Center"
        }
    }
]


def get_all_vignan_sources() -> List[Dict[str, Any]]:
    return OFFICIAL_SOURCES

