"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { StudentFullData, getStudentData } from "@/data/students-db";
import { apiClient } from "@/lib/api-client";

interface StudentContextType {
  studentData: StudentFullData;
  allStudents: StudentFullData[];
  isLoading: boolean;
  switchStudent: (rollNo: string) => void;
  loginAsStudent: (rollNo: string, password?: string) => Promise<boolean>;
  activateAndLoginStudent: (rollNo: string, otp: string, newPassword: string, confirmPassword: string) => Promise<boolean>;
  logout: () => void;
}

const StudentContext = createContext<StudentContextType | undefined>(undefined);

export const StudentProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeRoll, setActiveRoll] = useState<string>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("vigbot_active_student") || localStorage.getItem("agent65_active_student") || "251FA04E13";
    }
    return "251FA04E13";
  });

  const [studentData, setStudentData] = useState<StudentFullData>(() => getStudentData(activeRoll));
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem("vigbot_active_student", activeRoll);
    }

    // Try fetching live dashboard from backend if token is available
    const syncBackend = async () => {
      try {
        const dash = await apiClient.getDashboard();
        if (dash && dash.profile && dash.profile.roll_no === activeRoll) {
          // Merge any live updates from backend
          setStudentData((prev) => ({
            ...prev,
            profile: {
              ...prev.profile,
              cgpa: dash.profile?.cgpa ?? prev.profile.cgpa,
              feeOutstanding: dash.profile?.fee_outstanding ?? prev.profile.feeOutstanding,
            },
            attendance: {
              ...prev.attendance,
              overallPercentage: dash.profile?.overall_attendance_pct ?? prev.attendance.overallPercentage,
            },
            fees: {
              ...prev.fees,
              outstandingBalance: dash.profile?.fee_outstanding ?? prev.fees.outstandingBalance,
            },
          }));
        }
      } catch (err) {
        // Fallback to synchronized local data
        console.warn("Could not sync with backend", err);
      }
    };
    syncBackend();
  }, [activeRoll]);

  const switchStudent = (rollNo: string) => {
    const clean = rollNo.toUpperCase().trim();
    setActiveRoll(clean);
    setStudentData(getStudentData(clean));
  };

  const loginAsStudent = async (rollNo: string, password?: string): Promise<boolean> => {
    setIsLoading(true);
    const clean = rollNo.toUpperCase().trim();
    const pwd = (password || "").trim();

    try {
      // Authenticate against live secured backend with cryptographic password verification
      const loginResp = await apiClient.login(clean, pwd);

      const actualRoll = loginResp?.roll_no || clean;
      setActiveRoll(actualRoll);
      let sData = getStudentData(actualRoll);
      if (loginResp && loginResp.full_name) {
        sData = {
          ...sData,
          profile: {
            ...sData.profile,
            name: loginResp.full_name,
            rawName: loginResp.full_name.toUpperCase(),
            id: actualRoll,
            programme: loginResp.programme_code || sData.profile.programme,
          },
        };
      }
      setStudentData(sData);
      setIsLoading(false);
      return true;
    } catch (err: any) {
      setIsLoading(false);
      throw err;
    }
  };

  const activateAndLoginStudent = async (rollNo: string, otp: string, newPassword: string, confirmPassword: string): Promise<boolean> => {
    setIsLoading(true);
    const clean = rollNo.toUpperCase().trim();
    try {
      const resp = await apiClient.verifyAndActivate(clean, otp, newPassword, confirmPassword);
      const actualRoll = resp?.roll_no || clean;
      setActiveRoll(actualRoll);
      let sData = getStudentData(actualRoll);
      if (resp && resp.full_name) {
        sData = {
          ...sData,
          profile: {
            ...sData.profile,
            name: resp.full_name,
            rawName: resp.full_name.toUpperCase(),
            id: actualRoll,
            programme: resp.programme_code || sData.profile.programme,
          },
        };
      }
      setStudentData(sData);
      setIsLoading(false);
      return true;
    } catch (err: any) {
      setIsLoading(false);
      throw err;
    }
  };

  const logout = () => {
    apiClient.logout();
    setActiveRoll("251FA04E13");
    setStudentData(getStudentData("251FA04E13"));
  };

  return (
    <StudentContext.Provider
      value={{
        studentData,
        allStudents: [studentData],
        isLoading,
        switchStudent,
        loginAsStudent,
        activateAndLoginStudent,
        logout,
      }}
    >
      {children}
    </StudentContext.Provider>
  );
};

export const useStudent = () => {
  const context = useContext(StudentContext);
  if (!context) {
    throw new Error("useStudent must be used within a StudentProvider");
  }
  return context;
};
