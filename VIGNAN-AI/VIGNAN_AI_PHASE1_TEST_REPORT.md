# VIGNAN-AI — Phase 1 Comprehensive Verification & Test Report

**Document Version:** 1.0.0  
**Phase:** Phase 1 – Minimal Landing Page + Secure Student Account Activation and Login  
**System:** VIGNAN-AI (VFSTR Intelligent Student Helpdesk & Grievance Resolution Platform)  
**Date:** November 2026  
**Status:** 100% Passed (18/18 Automated Security & Flow Tests)  

---

## 1. Executive Summary

This report documents the verification and test results for **VIGNAN-AI Phase 1**. All 18 specified security and activation criteria were evaluated using an automated end-to-end test suite (`scratch/test_phase1_activation.py`). In addition, the frontend was verified via a production Next.js webpack build with TypeScript typechecking.

- **Automated Security Suite:** 18/18 Passed (100%)
- **Frontend Production Build:** Successful (0 TypeScript errors, 0 build warnings)
- **Database Integrity:** 0 student records deleted; institutional roster preserved.

---

## 2. Automated Test Suite Results (18/18 Passed)

```
============================================================
VIGNAN-AI PHASE 1 SECURITY & ACTIVATION VERIFICATION SUITE
============================================================
[PASS] Test 1: Unlisted registration number rejected from activation
[PASS] Test 2: Synthetic test account (24CSE001) rejected from activation & login
[PASS] Test 3: Check-status returns unactivated for 251FA04001
[PASS] Test 4: Request-otp dispatches OTP and records in student_email_outbox
[PASS] Test 5: Rate limiting rejects 4th OTP request within 15 mins
[PASS] Test 6: Incorrect OTP rejected and decrements attempts_left
[PASS] Test 7: Maximum attempts (3) invalidates OTP
[PASS] Test 8: Weak passwords (<8 chars, no numbers, equals roll no) rejected
[PASS] Test 9: Correct OTP + valid password activates account with PBKDF2 hash and marks OTP used
[PASS] Test 10: Reusing already-used OTP rejected
[PASS] Test 11: Duplicate activation request on already activated student rejected
[PASS] Test 12: Activated student can log in with new password and receives JWT
[PASS] Test 13: Unactivated student cannot log in
[PASS] Test 14: Incorrect password rejected with uniform error
[PASS] Test 15: Password reset via OTP works end-to-end
[PASS] Test 16: Cross-student IDOR access prevented (student isolated to own data)
[PASS] Test 17: Student token rejected from admin endpoints with HTTP 403 Forbidden
[PASS] Test 18: Passwords and OTP codes are strictly excluded from API response bodies
============================================================
TEST RESULTS: 18/18 PASSED
============================================================
```

---

## 3. Detailed Test Specification & Execution Evidence

### Test 1: Unlisted Registration Number Rejection
- **Objective:** Verify that an unregistered or arbitrary roll number cannot request activation.
- **Request:** `POST /api/v1/auth/activation/request-otp {"roll_no": "999FA99999"}`
- **Response:** `HTTP 404 Not Found`
- **Payload:** `{"detail": "Student registration number not found in approved institutional records."}`
- **Outcome:** **PASS**

### Test 2: Synthetic Account Rejection
- **Objective:** Ensure legacy test accounts (`24CSE001`) cannot activate or log in with backdoor passwords.
- **Request (Activation):** `POST /api/v1/auth/activation/request-otp {"roll_no": "24CSE001"}` -> `HTTP 404 Not Found`
- **Request (Login):** `POST /api/v1/auth/login {"username": "24CSE001", "password": "student123"}` -> `HTTP 401 Unauthorized`
- **Outcome:** **PASS**

### Test 3: Status Check for Unactivated Student
- **Objective:** Verify status check accurately reports unactivated state with masked institutional email.
- **Request:** `POST /api/v1/auth/check-status {"roll_no": "251FA04001"}`
- **Response:** `HTTP 200 OK`
- **Payload:** `{"status": "unactivated", "masked_email": "25***01@vignan.ac.in", "message": "Account has not been activated yet. Please proceed with identity verification."}`
- **Outcome:** **PASS**

### Test 4: OTP Dispatch & Audit Recording
- **Objective:** Verify OTP is generated, hashed, and dispatched to institutional email outbox.
- **Request:** `POST /api/v1/auth/activation/request-otp {"roll_no": "251FA04001"}`
- **Response:** `HTTP 200 OK` (`expires_in_seconds: 600`, `requires_admin_verification: false`)
- **Database Audit:** Row created in `student_email_outbox` with recipient `251fa04001@vignan.ac.in` and 6-digit OTP in body.
- **Outcome:** **PASS**

### Test 5: Rate Limiting Enforcement
- **Objective:** Verify maximum 3 OTP requests within 15 minutes.
- **Execution:** Dispatched 3 successive OTP requests; attempted 4th request.
- **Response (4th Request):** `HTTP 429 Too Many Requests`
- **Payload:** `{"detail": "Too many verification requests. Please wait 15 minutes before requesting a new code."}`
- **Outcome:** **PASS**

### Test 6: Failed OTP Attempt Decrement
- **Objective:** Verify invalid OTP submission decrements remaining attempts.
- **Request:** `POST /api/v1/auth/activation/verify-and-activate {"roll_no": "251FA04001", "otp": "000000", ...}`
- **Response:** `HTTP 400 Bad Request` (`Invalid verification code. Attempts remaining: 2`)
- **Database Verification:** `activation_otps.attempts_left == 2`.
- **Outcome:** **PASS**

### Test 7: Maximum Attempt Lockout
- **Objective:** Verify 3 consecutive failed OTP attempts invalidate the token.
- **Execution:** Submitted incorrect OTP 3 times; subsequently submitted correct OTP.
- **Response:** `HTTP 400 Bad Request` (`No pending verification code found. Please request a new code.`)
- **Outcome:** **PASS**

### Test 8: Password Complexity Enforcement
- **Objective:** Verify weak passwords are rejected during activation.
- **Short Password (<8 chars):** `HTTP 400 Bad Request` (`Password must be at least 8 characters long.`)
- **No Numbers:** `HTTP 400 Bad Request` (`Password must contain at least one letter and one number.`)
- **Equals Registration Number:** `HTTP 400 Bad Request` (`Password cannot be your registration number.`)
- **Outcome:** **PASS**

### Test 9: Successful Account Activation
- **Objective:** Verify valid OTP and strong password activates account with PBKDF2 hash.
- **Request:** `POST /api/v1/auth/activation/verify-and-activate {"roll_no": "251FA04001", "otp": "<valid_otp>", "new_password": "ValidPassword@2026", "confirm_password": "ValidPassword@2026"}`
- **Response:** `HTTP 200 OK` + Authenticated JWT Token (`expires_in: 86400`).
- **Database State:** `students.password_hash` updated to `pbkdf2_sha256$100000$...`; `activation_otps.is_used` updated to `1`.
- **Outcome:** **PASS**

### Test 10: OTP Replay Prevention
- **Objective:** Verify an OTP cannot be reused after activation.
- **Request:** Re-submitted same payload from Test 9.
- **Response:** `HTTP 400 Bad Request` (`This account has already been activated. Please sign in with your password.`)
- **Outcome:** **PASS**

### Test 11: Duplicate Activation Request Rejection
- **Objective:** Verify already activated account cannot request activation OTPs.
- **Request:** `POST /api/v1/auth/activation/request-otp {"roll_no": "251FA04001"}`
- **Response:** `HTTP 400 Bad Request` (`This account has already been activated. Please sign in with your password, or use password reset.`)
- **Outcome:** **PASS**

### Test 12: Activated Student Login
- **Objective:** Verify activated student can log in with new password and receives JWT session.
- **Request:** `POST /api/v1/auth/login {"username": "251FA04001", "password": "ValidPassword@2026"}`
- **Response:** `HTTP 200 OK`
- **Payload:** `{"access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer", "expires_in": 86400, "roll_no": "251FA04001"}`
- **Outcome:** **PASS**

### Test 13: Unactivated Student Login Rejection
- **Objective:** Verify unactivated students cannot log in until activation is completed.
- **Request:** `POST /api/v1/auth/login {"username": "251FA04002", "password": "251FA04002"}`
- **Response:** `HTTP 401 Unauthorized`
- **Payload:** `{"detail": "Account is not yet activated. Please activate your account first using your institutional registration number."}`
- **Outcome:** **PASS**

### Test 14: Uniform Error on Incorrect Password
- **Objective:** Verify incorrect password returns uniform error to prevent user enumeration.
- **Request:** `POST /api/v1/auth/login {"username": "251FA04001", "password": "WrongPassword123"}`
- **Response:** `HTTP 401 Unauthorized`
- **Payload:** `{"detail": "Invalid registration number or password."}`
- **Outcome:** **PASS**

### Test 15: End-to-End Password Reset via OTP
- **Objective:** Verify activated student can reset forgotten password via email OTP.
- **Step 1:** `POST /api/v1/auth/password-reset/request-otp {"roll_no": "251FA04001"}` -> `HTTP 200 OK`
- **Step 2:** Dispatched reset OTP extracted from `student_email_outbox`.
- **Step 3:** `POST /api/v1/auth/password-reset/verify-and-reset` with new password `NewResetPassword@2026` -> `HTTP 200 OK`
- **Step 4:** `POST /api/v1/auth/login` with `NewResetPassword@2026` -> `HTTP 200 OK` + JWT Token.
- **Outcome:** **PASS**

### Test 16: Cross-Student IDOR Prevention
- **Objective:** Verify student token cannot access or submit data for another student.
- **Step 1:** Call `/api/v1/auth/me` with `251FA04001` token -> returns `251FA04001` profile.
- **Step 2:** Call `/api/v1/community/hostel` with `student_id: "251FA04002"` using `251FA04001` token.
- **Response:** `HTTP 403 Forbidden`
- **Payload:** `{"detail": "Access forbidden: You are only authorized to access your own student record."}`
- **Outcome:** **PASS**

### Test 17: Administrative Endpoint Protection
- **Objective:** Verify student JWT cannot access administrative APIs.
- **Request:** `GET /api/v1/admin/overview` with student JWT token.
- **Response:** `HTTP 403 Forbidden`
- **Payload:** `{"detail": "Access denied: Administrative privileges required"}`
- **Outcome:** **PASS**

### Test 18: Sensitive Secret Exclusion Audit
- **Objective:** Ensure plaintext passwords, password hashes, and raw OTP codes are never leaked in API response bodies.
- **Execution:** String scanning over all API responses generated during test execution.
- **Verification:** Plaintext passwords found: 0; Raw OTP codes found in responses: 0.
- **Outcome:** **PASS**

---

## 4. Frontend Production Build Verification

```
> vignan-ai@0.1.0 build
> next build --webpack

▲ Next.js 16.3.4 (webpack)
- Environments: .env.local
✓ Running next.config.ts took 43ms

  Creating an optimized production build ...
✓ Compiled successfully in 10.7s
  Running TypeScript ...
  Finished TypeScript in 7.5s ...
  Collecting page data using 9 workers ...
  Generating static pages using 9 workers (0/8) ...
  Generating static pages using 9 workers (2/8) 
  Generating static pages using 9 workers (4/8) 
  Generating static pages using 9 workers (6/8) 
✓ Generating static pages using 9 workers (8/8) in 1363ms
  Finalizing page optimization ...
  Collecting build traces ...

Route (app)
┌ ○ /
├ ○ /_not-found
├ ○ /admin
├ ○ /admin/login
├ ○ /robots.txt
└ ○ /sitemap.xml

○  (Static)  prerendered as static content
```

---

## 5. Verification Sign-Off

All objectives for **Phase 1: Minimal Landing Page + Secure Student Account Activation and Login** have been completed, verified with 18 automated tests, and confirmed production-ready without any TypeScript, compilation, or security regression.

