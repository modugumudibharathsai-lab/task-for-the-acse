# VIGBOT

An AI-powered university assistant — a single place for students to check attendance, marks, exams, fees, timetable, and university policies, and to ask an AI assistant about any of it in plain language.

Built with [Next.js](https://nextjs.org) 16, React 19, TypeScript, Tailwind CSS v4, and [shadcn/ui](https://ui.shadcn.com).

---

## Running it on your own laptop

You need **Node.js** installed first — it's the program that runs this project. If you don't have it:

1. Go to [nodejs.org](https://nodejs.org) and download the **LTS** version for your operating system.
2. Run the installer with the default options.
3. This also installs **npm** (Node Package Manager) automatically — you don't need to install it separately.

### What is npm?

npm is the tool that downloads all the third-party code this project depends on (React, Tailwind, etc.) and saves it into a `node_modules` folder. It comes bundled with Node.js, so once Node is installed, `npm` is available in your terminal automatically. Every command below is typed into a terminal — on Windows that's **PowerShell** or **Command Prompt**, on Mac/Linux it's **Terminal**.

To check both are installed, open a terminal and run:

```bash
node -v
npm -v
```

Both should print a version number. This project needs **Node.js 20 or newer**.

### 1. Get the code

Navigate to the `FRONTEND` folder within the StudentHelpdesk repository:

```bash
cd FRONTEND
```

### 2. Install dependencies

From inside the project folder, run:

```bash
npm install
```

This reads `package.json` and downloads everything the project needs into a `node_modules` folder. It only needs to be run once (and again later if `package.json` changes) — it can take a minute or two the first time.

> **Prefer a different package manager?** `yarn install`, `pnpm install`, or `bun install` all work the same way — pick whichever you already have set up. If you're not sure, `npm` is the safest default since it ships with Node.js.

### 3. Start the app

```bash
npm run dev
```

This starts a local development server. Once it prints something like:

```
✓ Ready in 1946ms
- Local: http://localhost:3000
```

open **[http://localhost:3000](http://localhost:3000)** in your browser. The app hot-reloads — any code changes you save will show up in the browser automatically without restarting the server.

To stop the server, go back to the terminal and press `Ctrl + C`.

---

## Other useful commands

| Command | What it does |
|---|---|
| `npm run dev` | Start the local development server (with hot reload) |
| `npm run build` | Build an optimized production version of the app |
| `npm run start` | Run the production build locally (run `npm run build` first) |
| `npm run lint` | Check the code for lint errors |

---

## Project structure

```
src/
  app/            Next.js App Router entry point (layout.tsx, page.tsx, global styles)
  components/      All UI components, grouped by feature
    ui/            Shared shadcn/ui primitives (Button, Card, Badge, Dialog, Sheet, ...)
    landing/        Marketing landing page shown before sign-in
    auth/           Login screen
    ai-helpdesk/    The AI assistant chat panel
    sidebar/, header/  App navigation shell
    attendance/, marks/, fees/, timetable/, examinations/, curriculum/,
    policies/, circulars/, calendar/, services/   One folder per dashboard screen
  data/           Static reference structures and offline fallback data
  lib/            Shared utilities, API client (api-client.ts), and fallback intelligence engine (ai-engine.ts)
  context/        Student authentication, RLS session state, and agent chat context
```

The frontend connects directly to the FastAPI backend (`http://localhost:8000/api/v1`) with full Row-Level Security (RLS) enforcement, 18 ML campus intents, and live `routed_by` telemetry (Tier 1 Rules, Tier 2 Local ML Classifier, Tier 3 PII-Redacted Gemini 3.5 Flash). If the backend is unreachable, it gracefully falls back to local deterministic rule evaluation.

### Statutory Attendance Policy
- **75% Mandatory Attendance**: Required for regular End-Semester Examination clearance.
- **65%–74.9% Medical Condonation**: Permitted upon approval by Dean (Academics) on verified medical grounds.
- **<65% Severe Detention**: Student is debarred and receives an 'F-Detained' grade.

## Design system

- **Colors & fonts**: defined as CSS variables in `src/app/globals.css`, using Plus Jakarta Sans as the primary typeface.
- **Components**: shared UI primitives live in `src/components/ui/` and follow [shadcn/ui](https://ui.shadcn.com) conventions. To add a new one: `npx shadcn@latest add <component-name>`.
- Everything is styled with Tailwind CSS v4 utility classes, including [container queries](https://tailwindcss.com/docs/responsive-design#container-queries) (`@container`, `@lg:`, etc.) so dashboard grids reflow based on the space actually available, not just the browser window width.

## Troubleshooting

- **`npm install` fails or hangs**: delete the `node_modules` folder and the `package-lock.json` file, then run `npm install` again.
- **Port 3000 already in use**: another process is already using that port. Either stop it, or run `npm run dev -- -p 3001` to use a different port.
- **Changes not showing up**: make sure the terminal running `npm run dev` is still open and hasn't shown an error. A hard browser refresh (`Ctrl+Shift+R`) can also help.
