"use client";

import { useState, useEffect } from "react";
import { Book, FileText, Download, BookOpen, Clock, Search } from "lucide-react";
import { getLibraryResources } from "@/actions/library";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

const DUMMY_BORROWED = [
  { id: "b1", title: "Introduction to Algorithms", dueDate: "2026-10-01" },
  { id: "b2", title: "Clean Code", dueDate: "2026-09-25" },
];

const DUMMY_AVAILABLE = [
  { id: "a1", title: "Design Patterns: Elements of Reusable Object-Oriented Software", author: "Erich Gamma" },
  { id: "a2", title: "The Pragmatic Programmer", author: "Andrew Hunt" },
  { id: "a3", title: "Refactoring: Improving the Design of Existing Code", author: "Martin Fowler" },
  { id: "a4", title: "Code Complete", author: "Steve McConnell" },
];

const DUMMY_OVERDUE = [
  { id: "o1", title: "Computer Networking: A Top-Down Approach", dueDate: "2026-09-10", daysOverdue: 8 },
];

export function LibraryView() {
  const [resources, setResources] = useState<any[]>([]);
  const [borrowedSearch, setBorrowedSearch] = useState("");
  const [availableSearch, setAvailableSearch] = useState("");
  const [overdueSearch, setOverdueSearch] = useState("");

  useEffect(() => {
    getLibraryResources().then(setResources);
  }, []);

  const filteredBorrowed = DUMMY_BORROWED.filter(b => b.title.toLowerCase().includes(borrowedSearch.toLowerCase()));
  const filteredAvailable = DUMMY_AVAILABLE.filter(a => a.title.toLowerCase().includes(availableSearch.toLowerCase()));
  const filteredOverdue = DUMMY_OVERDUE.filter(o => o.title.toLowerCase().includes(overdueSearch.toLowerCase()));

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Library</h2>
        <p className="text-muted-foreground">Access physical books and digital study materials.</p>
      </div>

      {/* Section 1: Books in Library & Lended by Student */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold">My Books & Borrowing</h3>
        <div className="grid gap-4 md:grid-cols-3">
          
          <Dialog>
            <DialogTrigger className="w-full text-left outline-none">
              <div className="p-4 rounded-xl border bg-card text-card-foreground shadow-sm flex items-center gap-4 cursor-pointer hover:bg-muted/50 transition-colors">
                <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                  <BookOpen className="h-5 w-5 text-indigo-600" />
                </div>
                <div>
                  <p className="font-semibold text-lg">{DUMMY_BORROWED.length}</p>
                  <p className="text-sm text-muted-foreground">Currently Borrowed</p>
                </div>
              </div>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Currently Borrowed Books</DialogTitle>
              </DialogHeader>
              <div className="relative mb-4">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <input
                  type="search"
                  placeholder="Search borrowed books..."
                  className="w-full rounded-md border border-input bg-background pl-9 pr-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  value={borrowedSearch}
                  onChange={(e) => setBorrowedSearch(e.target.value)}
                />
              </div>
              <div className="space-y-3 max-h-[60vh] overflow-y-auto scrollbar-thin">
                {filteredBorrowed.map(book => (
                  <div key={book.id} className="p-3 border rounded-lg flex justify-between items-center bg-card">
                    <div>
                      <p className="font-medium text-sm">{book.title}</p>
                      <p className="text-xs text-muted-foreground">Due: {book.dueDate}</p>
                    </div>
                  </div>
                ))}
                {filteredBorrowed.length === 0 && <p className="text-sm text-center text-muted-foreground py-4">No borrowed books found.</p>}
              </div>
            </DialogContent>
          </Dialog>

          <Dialog>
            <DialogTrigger className="w-full text-left outline-none">
              <div className="p-4 rounded-xl border bg-card text-card-foreground shadow-sm flex items-center gap-4 cursor-pointer hover:bg-muted/50 transition-colors">
                <div className="h-10 w-10 rounded-full bg-emerald-100 flex items-center justify-center">
                  <Book className="h-5 w-5 text-emerald-600" />
                </div>
                <div>
                  <p className="font-semibold text-lg">1,432</p>
                  <p className="text-sm text-muted-foreground">Available Books</p>
                </div>
              </div>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Available Books</DialogTitle>
              </DialogHeader>
              <div className="relative mb-4">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <input
                  type="search"
                  placeholder="Search available books..."
                  className="w-full rounded-md border border-input bg-background pl-9 pr-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  value={availableSearch}
                  onChange={(e) => setAvailableSearch(e.target.value)}
                />
              </div>
              <div className="space-y-3 max-h-[60vh] overflow-y-auto scrollbar-thin">
                {filteredAvailable.map(book => (
                  <div key={book.id} className="p-3 border rounded-lg flex justify-between items-center bg-card">
                    <div>
                      <p className="font-medium text-sm">{book.title}</p>
                      <p className="text-xs text-muted-foreground">Author: {book.author}</p>
                    </div>
                    <button className="text-xs bg-emerald-100 text-emerald-700 px-2 py-1 rounded font-medium hover:bg-emerald-200 transition-colors shrink-0">
                      Reserve
                    </button>
                  </div>
                ))}
                {filteredAvailable.length === 0 && <p className="text-sm text-center text-muted-foreground py-4">No available books found.</p>}
              </div>
            </DialogContent>
          </Dialog>

          <Dialog>
            <DialogTrigger className="w-full text-left outline-none">
              <div className="p-4 rounded-xl border bg-card text-card-foreground shadow-sm flex items-center gap-4 cursor-pointer hover:bg-muted/50 transition-colors">
                <div className="h-10 w-10 rounded-full bg-rose-100 flex items-center justify-center">
                  <Clock className="h-5 w-5 text-rose-600" />
                </div>
                <div>
                  <p className="font-semibold text-lg">{DUMMY_OVERDUE.length}</p>
                  <p className="text-sm text-muted-foreground">Overdue</p>
                </div>
              </div>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Overdue Books</DialogTitle>
              </DialogHeader>
              <div className="relative mb-4">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <input
                  type="search"
                  placeholder="Search overdue books..."
                  className="w-full rounded-md border border-input bg-background pl-9 pr-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  value={overdueSearch}
                  onChange={(e) => setOverdueSearch(e.target.value)}
                />
              </div>
              <div className="space-y-3 max-h-[60vh] overflow-y-auto scrollbar-thin">
                {filteredOverdue.map(book => (
                  <div key={book.id} className="p-3 border rounded-lg flex justify-between items-center bg-card">
                    <div>
                      <p className="font-medium text-sm">{book.title}</p>
                      <p className="text-xs text-rose-600 font-medium">Overdue by {book.daysOverdue} days</p>
                    </div>
                  </div>
                ))}
                {filteredOverdue.length === 0 && <p className="text-sm text-center text-muted-foreground py-4">No overdue books found.</p>}
              </div>
            </DialogContent>
          </Dialog>

        </div>
      </div>

      {/* Section 2: Currently available digital resources */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold">Digital Resources</h3>
        <div className="grid gap-4">
          {resources.map((resource) => (
            <div key={resource.id} className="flex items-center justify-between p-4 rounded-xl border bg-card text-card-foreground shadow-sm">
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                  <FileText className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="font-semibold">{resource.title}</p>
                  <div className="flex gap-2 items-center text-sm text-muted-foreground">
                    <span className="bg-muted px-2 py-0.5 rounded text-xs">{resource.course_code}</span>
                    <span>{resource.type}</span>
                  </div>
                </div>
              </div>
              <button className="p-2 hover:bg-muted rounded-full transition-colors">
                <Download className="h-5 w-5 text-muted-foreground" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
