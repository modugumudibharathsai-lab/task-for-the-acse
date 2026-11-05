import { processQuery, detectDistress } from "./ai-engine";
import { calculateConsecutiveClassesNeeded } from "./utils";
import { CURRENT_STUDENT } from "../data/student";

console.log("=== RUNNING VERIFICATION FOR VIGBOT ===");

// 1. Check Student Auth & RLS
console.log("1. Authenticated Student:", CURRENT_STUDENT.name, CURRENT_STUDENT.id);
if (CURRENT_STUDENT.id !== "251FA04E13") throw new Error("Incorrect student ID");

// 2. Test Attendance Calculation
const needed75 = calculateConsecutiveClassesNeeded(34, 50, 75);
console.log("2. Consecutive classes needed for 34/50 to reach 75%:", needed75);
if (needed75 !== 14) throw new Error(`Expected 14 consecutive classes, got ${needed75}`);

// 3. Test Question: What is my attendance in Digital Electronics?
const res1 = processQuery("What is my attendance in Digital Electronics?");
console.log("3. Attendance Question Response:", res1.category, res1.sourceAgent);
console.log("   Text:", res1.text);
if (!res1.text.includes("68%") || !res1.text.includes("14 classes consecutively")) {
  throw new Error("Attendance response missing 68% or 14 classes consecutively");
}

// 4. Test Multi-Turn Context Retention:
// Turn 1: "When is my Digital Electronics exam?"
const turn1 = processQuery("When is my Digital Electronics exam?");
console.log("4. Turn 1 (Exam):", turn1.text.substring(0, 80) + "...");
if (!turn1.text.includes("18 September") || !turn1.text.includes("Hall A2")) {
  throw new Error("Exam date missing 18 September or Hall A2");
}

// Turn 2: "What is my attendance in that subject?"
const turn2 = processQuery("What is my attendance in that subject?", [
  { role: "user", content: "When is my Digital Electronics exam?" },
  { role: "assistant", content: turn1.text, responseMeta: turn1 },
], "Digital Electronics");
console.log("   Turn 2 (Attendance in that subject):", turn2.text.substring(0, 80) + "...");
if (!turn2.text.includes("Digital Electronics") || !turn2.text.includes("68%")) {
  throw new Error("Failed to retain context for Digital Electronics attendance");
}

// Turn 3: "How many classes do I need to attend to reach 75%?"
const turn3 = processQuery("How many classes do I need to attend to reach 75%?", [
  { role: "user", content: "When is my Digital Electronics exam?" },
  { role: "assistant", content: turn1.text, responseMeta: turn1 },
  { role: "user", content: "What is my attendance in that subject?" },
  { role: "assistant", content: turn2.text, responseMeta: turn2 },
], "Digital Electronics");
console.log("   Turn 3 (Consecutive needed):", turn3.text.substring(0, 80) + "...");
if (!turn3.text.includes("14 classes consecutively")) {
  throw new Error("Failed to calculate 14 consecutive classes in multi-turn context");
}

// 5. Test Mandatory Distress Detection
const distressQuery = "I don't think I can handle this anymore.";
const isDistressDetected = detectDistress(distressQuery);
console.log("5. Distress detected:", isDistressDetected);
if (!isDistressDetected) throw new Error("Distress detection failed for phrase");

const distressResponse = processQuery(distressQuery);
console.log("   Distress Category:", distressResponse.category, distressResponse.sourceAgent);
if (distressResponse.category !== "DISTRESS_SUPPORT" || !distressResponse.isDistress) {
  throw new Error("Distress response did not switch to DISTRESS_SUPPORT");
}
if (distressResponse.sourceAgent !== "Distress Escalation & Counseling") {
  throw new Error("Distress response not routed to Distress Counseling");
}

// 6. Test Fee Status
const feeRes = processQuery("What is my fee status?");
console.log("6. Fee Query:", feeRes.category, feeRes.sourceAgent);
if (!feeRes.text.includes("28,000") || !feeRes.text.includes("1,20,000")) {
  throw new Error("Fee response missing amounts");
}

// 7. Test Curriculum
const currRes = processQuery("How many credits do I still need to graduate?");
console.log("7. Curriculum Query:", currRes.category, currRes.sourceAgent);
if (!currRes.text.includes("72 credits") || !currRes.text.includes("24 credits")) {
  throw new Error("Curriculum response missing credit counts");
}

// 8. Test Second Formative Assessment
const fa2Res = processQuery("When is the second formative assessment?");
console.log("8. FA2 Query:", fa2Res.text.substring(0, 80) + "...");
if (!fa2Res.text.includes("15 Oct 2026")) {
  throw new Error("FA2 query missing date");
}

// 9. Test Policies
const polRes = processQuery("What does the attendance policy say?");
console.log("9. Policy Query:", polRes.text.substring(0, 80) + "...");
if (!polRes.text.includes("75%")) {
  throw new Error("Policy query missing 75%");
}

console.log("=== ALL VIGBOT LOGICAL TESTS PASSED SUCCESSFULLY! ===");
