import path from 'path';
import fs from 'fs';

export function getDb(): any {
  const isVercel = process.env.VERCEL === '1' || process.env.NODE_ENV === 'production';
  const vigbotPath = path.resolve(process.cwd(), '../database/vigbot.db');
  let dbPath = fs.existsSync(vigbotPath) ? vigbotPath : path.resolve(process.cwd(), '../database/student_helpdesk.db');
  
  if (isVercel) {
    dbPath = fs.existsSync('/tmp/vigbot.db') ? '/tmp/vigbot.db' : '/tmp/student_helpdesk.db';
    const bundledPath = fs.existsSync(path.resolve(process.cwd(), 'vigbot.db')) 
      ? path.resolve(process.cwd(), 'vigbot.db') 
      : path.resolve(process.cwd(), 'student_helpdesk.db');
    
    if (!fs.existsSync(dbPath)) {
      if (fs.existsSync(bundledPath)) {
        try {
          fs.copyFileSync(bundledPath, dbPath);
          console.log("Mock Database copied to /tmp successfully for Vercel execution.");
        } catch (e) {
          console.warn("Failed to copy bundled DB to /tmp:", e);
        }
      } else {
        console.warn("Bundled DB not found at", bundledPath);
      }
    }
  }
  
  try {
    const Database = require('better-sqlite3');
    if (fs.existsSync(dbPath)) {
      return new Database(dbPath);
    }
    return null;
  } catch (e) {
    console.warn("better-sqlite3 is not available in this environment. Falling back to API client.", e);
    return null;
  }
}
