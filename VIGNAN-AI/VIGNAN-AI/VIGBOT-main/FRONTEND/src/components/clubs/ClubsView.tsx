"use client";

import React, { useState } from 'react';
import { Users, ChevronDown, ChevronUp, Send, CheckCircle2, Loader2, Activity, Package, Search } from 'lucide-react';
import { CLUBS_DATA, Club } from '@/data/clubs';
import { AncSection } from './AncSection';
import { submitClubApplication } from '@/actions/db';
import { useStudent } from '@/context/StudentContext';
import { CURRENT_STUDENT } from '@/data/student';

export function ClubsView() {
  const ancClub = CLUBS_DATA.find(c => c.id === 'ANC');
  const [searchQuery, setSearchQuery] = useState("");
  
  const otherClubs = CLUBS_DATA.filter(c => 
    c.id !== 'ANC' && 
    (c.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
     c.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
     c.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      <div className="flex items-center space-x-3 mb-8">
        <div className="p-3 bg-purple-100 rounded-xl">
          <Users className="w-6 h-6 text-purple-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Clubs & Communities</h1>
          <p className="text-gray-500">Discover and join university organizations</p>
        </div>
      </div>

      {/* Render the specialized Anti-Ragging Cell section at the top */}
      {ancClub && <AncSection club={ancClub} />}

      <div className="flex flex-col sm:flex-row sm:items-center justify-between mt-10 mb-4 gap-4">
        <h2 className="text-xl font-bold text-gray-900">Student Organizations</h2>
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input 
            type="text"
            placeholder="Search clubs, categories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-white shadow-sm"
          />
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {otherClubs.map(club => (
          <ClubCard key={club.id} club={club} />
        ))}
      </div>
    </div>
  );
}

function ClubCard({ club }: { club: Club }) {
  const { studentData } = useStudent();
  const student = studentData?.profile || CURRENT_STUDENT;

  const [expandedJoin, setExpandedJoin] = useState(false);
  const [expandedActivities, setExpandedActivities] = useState(false);
  const [expandedResources, setExpandedResources] = useState(false);
  
  const [isApplying, setIsApplying] = useState(false);
  const [applySuccess, setApplySuccess] = useState<string | null>(null);

  // Map theme colors to Tailwind classes
  const colorMap: Record<string, { bg: string, text: string, border: string, badge: string }> = {
    blue: { bg: 'bg-blue-50', text: 'text-blue-900', border: 'border-blue-200', badge: 'bg-blue-100 text-blue-800' },
    emerald: { bg: 'bg-emerald-50', text: 'text-emerald-900', border: 'border-emerald-200', badge: 'bg-emerald-100 text-emerald-800' },
    purple: { bg: 'bg-purple-50', text: 'text-purple-900', border: 'border-purple-200', badge: 'bg-purple-100 text-purple-800' },
    rose: { bg: 'bg-rose-50', text: 'text-rose-900', border: 'border-rose-200', badge: 'bg-rose-100 text-rose-800' },
  };

  const theme = colorMap[club.themeColor] || colorMap.blue;

  const handleApply = async () => {
    setIsApplying(true);
    
    // Use the actual logged in student's name
    const studentName = student.name;
    
    // Give it a tiny simulated delay for realism
    setTimeout(async () => {
      const result = await submitClubApplication(club.id, studentName, student.id);
      setIsApplying(false);
      
      if (result.success) {
        setApplySuccess(`Application successful! Notification forwarded to ${club.members[0]?.name || 'Club Head'} via WhatsApp.`);
      } else {
        setApplySuccess('Error applying. Please try again.');
      }
    }, 1500);
  };

  return (
    <div className={`border rounded-xl shadow-sm transition-all overflow-hidden ${theme.border} bg-white flex flex-col`}>
      <div className={`p-5 border-b ${theme.border} ${theme.bg}`}>
        <div className="flex justify-between items-start mb-2">
          <h3 className={`text-xl font-bold ${theme.text}`}>{club.name}</h3>
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${theme.badge}`}>
            {club.category}
          </span>
        </div>
        <p className="text-gray-600 text-sm">{club.description}</p>
      </div>

      <div className="p-5 flex-grow space-y-4">
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-3 uppercase tracking-wider">Key Members</h4>
          <div className="space-y-3 mb-5">
            {club.members.map(member => (
              <div key={member.id} className="flex items-start">
                <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center mr-3 shrink-0">
                  <span className="text-sm font-bold text-gray-500">{member.name.charAt(0)}</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">{member.name}</p>
                  <p className="text-xs text-gray-500">{member.role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Activities Section */}
        {club.activities && club.activities.length > 0 && (
          <div className="pt-4 border-t border-gray-100">
            <button 
              onClick={() => setExpandedActivities(!expandedActivities)}
              className="flex items-center justify-between w-full text-left text-sm font-semibold text-gray-700 hover:text-gray-900 transition-colors"
            >
              <span className="flex items-center gap-2"><Activity className="w-4 h-4" /> Activities</span>
              {expandedActivities ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
            
            {expandedActivities && (
              <ul className="mt-3 space-y-2 animate-fade-in pl-6 list-disc text-sm text-gray-600">
                {club.activities.map((activity, idx) => (
                  <li key={idx}>{activity}</li>
                ))}
              </ul>
            )}
          </div>
        )}

        {/* Resources Section */}
        {club.availableResources && club.availableResources.length > 0 && (
          <div className="pt-4 border-t border-gray-100">
            <button 
              onClick={() => setExpandedResources(!expandedResources)}
              className="flex items-center justify-between w-full text-left text-sm font-semibold text-gray-700 hover:text-gray-900 transition-colors"
            >
              <span className="flex items-center gap-2"><Package className="w-4 h-4" /> Available Resources</span>
              {expandedResources ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
            
            {expandedResources && (
              <ul className="mt-3 space-y-2 animate-fade-in pl-6 list-disc text-sm text-gray-600">
                {club.availableResources.map((resource, idx) => (
                  <li key={idx}>{resource}</li>
                ))}
              </ul>
            )}
          </div>
        )}

        {/* Joining Steps Section */}
        {club.joiningSteps.length > 0 && (
          <div className="pt-4 border-t border-gray-100">
            <button 
              onClick={() => setExpandedJoin(!expandedJoin)}
              className="flex items-center justify-between w-full text-left text-sm font-semibold text-gray-700 hover:text-gray-900 transition-colors"
            >
              <span>How to Join (End-to-End Process)</span>
              {expandedJoin ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
            
            {expandedJoin && (
              <div className="mt-4 space-y-4 animate-fade-in">
                {club.joiningSteps.map((step, idx) => (
                  <div key={idx} className="relative pl-6 pb-2 border-l-2 border-gray-200 last:border-0 last:pb-0">
                    <div className={`absolute -left-2 top-0 w-4 h-4 rounded-full border-2 border-white ${theme.bg.replace('50', '500')}`} />
                    <h5 className="text-sm font-bold text-gray-900">Step {step.order}: {step.title}</h5>
                    <p className="text-sm text-gray-600 mt-1">{step.description}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
      
      <div className="p-5 border-t border-gray-100 bg-gray-50 mt-auto">
        {applySuccess ? (
          <div className="flex items-start p-3 bg-emerald-50 text-emerald-800 rounded-lg border border-emerald-100">
            <CheckCircle2 className="w-5 h-5 mr-2 shrink-0 mt-0.5" />
            <p className="text-sm font-medium">{applySuccess}</p>
          </div>
        ) : (
          <button 
            onClick={handleApply}
            disabled={isApplying}
            className={`w-full py-2.5 rounded-lg font-medium transition-colors flex items-center justify-center ${
              isApplying ? 'bg-gray-200 text-gray-500 cursor-not-allowed' : 'bg-gray-900 hover:bg-gray-800 text-white shadow-sm'
            }`}
          >
            {isApplying ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Processing Application...
              </>
            ) : (
              <>
                <Send className="w-4 h-4 mr-2" />
                Enroll Now
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}
