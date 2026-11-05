export interface TimetableSlot {
  id: string;
  time: string;
  startTime: string;
  endTime: string;
  subject: string;
  code: string;
  room: string;
  faculty: string;
  type: "Lecture" | "Lab" | "Break" | "Tutorial" | "Self Learning" | "Counseling";
  status: "Completed" | "Current" | "Next" | "Upcoming";
}

export interface SectionDetails {
  section: string;
  room: string;
  classTeacher: string;
  timetableCoordinator: string;
  coordinatorPhone: string;
  hodCse: string;
}

export const SECTION_METADATA: SectionDetails = {
  section: "Section-7",
  room: "N-312",
  classTeacher: "Mr. T. Latesh Babu",
  timetableCoordinator: "Mr. Uttej Kumar Nannapaneni",
  coordinatorPhone: "+91 95737 93802",
  hodCse: "Dr. S V Phani Kumar",
};

export const WEEKLY_TIMETABLE: Record<string, TimetableSlot[]> = {
  "Monday": [
    {"id": "MON-1", "time": "09:05 AM \u2013 10:45 AM", "startTime": "09:05 AM", "endTime": "10:45 AM", "subject": "Object Oriented Programming Through Java [P]", "code": "OOPS-25CS204", "room": "N-312 / Java Lab", "faculty": "Mr. T. Latesh Babu, Manikanta Reddy, Vamsi Krishna, Shaik Shamsheer Bhash", "type": "Lab", "status": "Upcoming"},
    {"id": "MON-2", "time": "11:00 AM \u2013 11:50 AM", "startTime": "11:00 AM", "endTime": "11:50 AM", "subject": "Self Learning / Advanced Learning", "code": "SELF-LEARN", "room": "N-312", "faculty": "Faculty Mentors", "type": "Self Learning", "status": "Upcoming"},
    {"id": "MON-3", "time": "12:30 PM \u2013 01:20 PM", "startTime": "12:30 PM", "endTime": "01:20 PM", "subject": "Digital Logic design [L]", "code": "DLD-25CS205", "room": "N-312", "faculty": "Mrs Archana", "type": "Lecture", "status": "Upcoming"},
    {"id": "MON-4", "time": "01:20 PM \u2013 02:10 PM", "startTime": "01:20 PM", "endTime": "02:10 PM", "subject": "Counseling / Mentorship", "code": "COUN", "room": "N-312", "faculty": "Mr. T. Latesh Babu (Class Teacher)", "type": "Counseling", "status": "Upcoming"},
    {"id": "MON-5", "time": "02:20 PM \u2013 03:10 PM", "startTime": "02:20 PM", "endTime": "03:10 PM", "subject": "Data Structures [L]", "code": "DS-25CS201", "room": "N-312", "faculty": "Dr. R. Prathap Kumar", "type": "Lecture", "status": "Upcoming"},
    {"id": "MON-6", "time": "03:10 PM \u2013 04:00 PM", "startTime": "03:10 PM", "endTime": "04:00 PM", "subject": "Database Management System [L]", "code": "DBMS-25CS203", "room": "N-312", "faculty": "Ms. Y. Sai Eswari", "type": "Lecture", "status": "Upcoming"},
  ],
  "Tuesday": [
    {"id": "TUE-1", "time": "08:15 AM \u2013 09:05 AM", "startTime": "08:15 AM", "endTime": "09:05 AM", "subject": "Discrete Mathematical Structures [L]", "code": "DMS-25MT202", "room": "N-314", "faculty": "Dr. N. Santhosh", "type": "Lecture", "status": "Upcoming"},
    {"id": "TUE-2", "time": "09:05 AM \u2013 10:45 AM", "startTime": "09:05 AM", "endTime": "10:45 AM", "subject": "Data Wrangling and Visualization [T]", "code": "DW-25CS202", "room": "N-314", "faculty": "Dr. M. Raja Rao, Bhavvanjali, Pallaprolu Kavya Sri", "type": "Tutorial", "status": "Upcoming"},
    {"id": "TUE-3", "time": "11:00 AM \u2013 11:50 AM", "startTime": "11:00 AM", "endTime": "11:50 AM", "subject": "Self Learning / Advanced Learning", "code": "SELF-LEARN", "room": "N-312", "faculty": "Faculty Mentors", "type": "Self Learning", "status": "Upcoming"},
    {"id": "TUE-4", "time": "12:30 PM \u2013 01:20 PM", "startTime": "12:30 PM", "endTime": "01:20 PM", "subject": "Data Structures [L]", "code": "DS-25CS201", "room": "N-312", "faculty": "Dr. R. Prathap Kumar", "type": "Lecture", "status": "Upcoming"},
    {"id": "TUE-5", "time": "01:20 PM \u2013 02:10 PM", "startTime": "01:20 PM", "endTime": "02:10 PM", "subject": "Database Management System [L]", "code": "DBMS-25CS203", "room": "N-312", "faculty": "Ms. Y. Sai Eswari", "type": "Lecture", "status": "Upcoming"},
    {"id": "TUE-6", "time": "02:20 PM \u2013 03:10 PM", "startTime": "02:20 PM", "endTime": "03:10 PM", "subject": "Digital Logic design [L]", "code": "DLD-25CS205", "room": "N-312", "faculty": "Mrs Archana", "type": "Lecture", "status": "Upcoming"},
    {"id": "TUE-7", "time": "03:10 PM \u2013 04:00 PM", "startTime": "03:10 PM", "endTime": "04:00 PM", "subject": "Object Oriented Programming Through Java [L]", "code": "OOPS-25CS204", "room": "N-312", "faculty": "Mr. T. Latesh Babu", "type": "Lecture", "status": "Upcoming"},
  ],
  "Wednesday": [
    {"id": "WED-1", "time": "08:15 AM \u2013 09:05 AM", "startTime": "08:15 AM", "endTime": "09:05 AM", "subject": "Digital Logic design [L]", "code": "DLD-25CS205", "room": "N-312", "faculty": "Mrs Archana", "type": "Lecture", "status": "Upcoming"},
    {"id": "WED-2", "time": "09:05 AM \u2013 10:45 AM", "startTime": "09:05 AM", "endTime": "10:45 AM", "subject": "Discrete Mathematical Structures [T]", "code": "DMS-25MT202", "room": "N-312", "faculty": "Dr. N. Santhosh", "type": "Tutorial", "status": "Upcoming"},
    {"id": "WED-3", "time": "11:00 AM \u2013 11:50 AM", "startTime": "11:00 AM", "endTime": "11:50 AM", "subject": "Self Learning / Advanced Learning", "code": "SELF-LEARN", "room": "N-312", "faculty": "Faculty Mentors", "type": "Self Learning", "status": "Upcoming"},
    {"id": "WED-4", "time": "12:30 PM \u2013 01:20 PM", "startTime": "12:30 PM", "endTime": "01:20 PM", "subject": "Artificial Intelligence [L]", "code": "AI-24CS302", "room": "N-312", "faculty": "Dr. M. Sunil Babu", "type": "Lecture", "status": "Upcoming"},
    {"id": "WED-5", "time": "01:20 PM \u2013 02:10 PM", "startTime": "01:20 PM", "endTime": "02:10 PM", "subject": "Database Management System [L]", "code": "DBMS-25CS203", "room": "N-312", "faculty": "Ms. Y. Sai Eswari", "type": "Lecture", "status": "Upcoming"},
    {"id": "WED-6", "time": "02:20 PM \u2013 03:10 PM", "startTime": "02:20 PM", "endTime": "03:10 PM", "subject": "Data Structures [T]", "code": "DS-25CS201", "room": "N-312", "faculty": "Naga Lakshmi, Shaik Thayab", "type": "Tutorial", "status": "Upcoming"},
  ],
  "Thursday": [
    {"id": "THU-1", "time": "09:05 AM \u2013 10:45 AM", "startTime": "09:05 AM", "endTime": "10:45 AM", "subject": "Database Management System [P]", "code": "DBMS-25CS203", "room": "N-312 / DBMS Lab", "faculty": "Ms. Y. Sai Eswari, Nemalikanti Deena, Mathangi Haveela, Kommuri Ramya", "type": "Lab", "status": "Upcoming"},
    {"id": "THU-2", "time": "11:00 AM \u2013 11:50 AM", "startTime": "11:00 AM", "endTime": "11:50 AM", "subject": "Self Learning / Advanced Learning", "code": "SELF-LEARN", "room": "N-312", "faculty": "Faculty Mentors", "type": "Self Learning", "status": "Upcoming"},
    {"id": "THU-3", "time": "12:30 PM \u2013 02:10 PM", "startTime": "12:30 PM", "endTime": "02:10 PM", "subject": "Artificial Intelligence [T]", "code": "AI-24CS302", "room": "N-312", "faculty": "Dr. M. Sunil Babu, Palagani Pavani, Mulpuri Koti surya sama prabh", "type": "Tutorial", "status": "Upcoming"},
    {"id": "THU-4", "time": "02:20 PM \u2013 03:10 PM", "startTime": "02:20 PM", "endTime": "03:10 PM", "subject": "Discrete Mathematical Structures [L]", "code": "DMS-25MT202", "room": "N-312", "faculty": "Dr. N. Santhosh", "type": "Lecture", "status": "Upcoming"},
    {"id": "THU-5", "time": "03:10 PM \u2013 04:00 PM", "startTime": "03:10 PM", "endTime": "04:00 PM", "subject": "Object Oriented Programming Through Java [L]", "code": "OOPS-25CS204", "room": "N-312", "faculty": "Mr. T. Latesh Babu", "type": "Lecture", "status": "Upcoming"},
  ],
  "Friday": [
    {"id": "FRI-1", "time": "09:05 AM \u2013 10:45 AM", "startTime": "09:05 AM", "endTime": "10:45 AM", "subject": "Data Structures [P]", "code": "DS-25CS201", "room": "N-312 / DS Lab", "faculty": "Dr. R. Prathap Kumar, Naga Lakshmi, Shaik Thayab, Adil Shaik", "type": "Lab", "status": "Upcoming"},
    {"id": "FRI-2", "time": "11:00 AM \u2013 11:50 AM", "startTime": "11:00 AM", "endTime": "11:50 AM", "subject": "Self Learning / Advanced Learning", "code": "SELF-LEARN", "room": "N-312", "faculty": "Faculty Mentors", "type": "Self Learning", "status": "Upcoming"},
    {"id": "FRI-3", "time": "12:30 PM \u2013 01:20 PM", "startTime": "12:30 PM", "endTime": "01:20 PM", "subject": "Discrete Mathematical Structures [L]", "code": "DMS-25MT202", "room": "N-312", "faculty": "Dr. N. Santhosh", "type": "Lecture", "status": "Upcoming"},
    {"id": "FRI-4", "time": "01:20 PM \u2013 02:10 PM", "startTime": "01:20 PM", "endTime": "02:10 PM", "subject": "Artificial Intelligence [L]", "code": "AI-24CS302", "room": "N-312", "faculty": "Dr. M. Sunil Babu", "type": "Lecture", "status": "Upcoming"},
    {"id": "FRI-5", "time": "02:20 PM \u2013 03:10 PM", "startTime": "02:20 PM", "endTime": "03:10 PM", "subject": "Database Management System [T]", "code": "DBMS-25CS203", "room": "N-312", "faculty": "Nemalikanti Deena, Mathangi Haveela, Kommuri Ramya", "type": "Tutorial", "status": "Upcoming"},
  ],
  "Saturday": [
    {"id": "SAT-1", "time": "08:15 AM \u2013 09:05 AM", "startTime": "08:15 AM", "endTime": "09:05 AM", "subject": "Artificial Intelligence [L]", "code": "AI-24CS302", "room": "N-314A", "faculty": "Dr. M. Sunil Babu", "type": "Lecture", "status": "Upcoming"},
    {"id": "SAT-2", "time": "09:05 AM \u2013 10:45 AM", "startTime": "09:05 AM", "endTime": "10:45 AM", "subject": "Data Wrangling and Visualization [P]", "code": "DW-25CS202", "room": "N-314A", "faculty": "Dr. M. Raja Rao, Bhavvanjali, Pallaprolu Kavya Sri", "type": "Lab", "status": "Upcoming"},
    {"id": "SAT-3", "time": "11:00 AM \u2013 11:50 AM", "startTime": "11:00 AM", "endTime": "11:50 AM", "subject": "Self Learning / Advanced Learning", "code": "SELF-LEARN", "room": "N-312", "faculty": "Faculty Mentors", "type": "Self Learning", "status": "Upcoming"},
    {"id": "SAT-4", "time": "12:30 PM \u2013 01:20 PM", "startTime": "12:30 PM", "endTime": "01:20 PM", "subject": "Object Oriented Programming Through Java [L]", "code": "OOPS-25CS204", "room": "N-312", "faculty": "Mr. T. Latesh Babu", "type": "Lecture", "status": "Upcoming"},
    {"id": "SAT-5", "time": "01:20 PM \u2013 02:10 PM", "startTime": "01:20 PM", "endTime": "02:10 PM", "subject": "Data Structures [L]", "code": "DS-25CS201", "room": "N-312", "faculty": "Dr. R. Prathap Kumar", "type": "Lecture", "status": "Upcoming"},
    {"id": "SAT-6", "time": "02:20 PM \u2013 03:10 PM", "startTime": "02:20 PM", "endTime": "03:10 PM", "subject": "Digital Logic design [T]", "code": "DLD-25CS205", "room": "N-312", "faculty": "Mrs Archana, Mr K. Raj Kiran", "type": "Tutorial", "status": "Upcoming"},
  ],
};

export const TODAY_TIMETABLE = {
  day: "Saturday",
  date: "13 September 2026",
  sourceAgent: "Timetable Engine - Section 7 N-312",
  slots: WEEKLY_TIMETABLE["Saturday"] || [],
};
