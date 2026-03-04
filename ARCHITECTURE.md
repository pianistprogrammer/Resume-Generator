# 🏗️ JobAlert AI - System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER BROWSER                               │
│                    (Nuxt 3 + Tailwind + Pinia)                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                               │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │    Routes    │→ │ Controllers  │→ │   Services   │              │
│  └──────────────┘  └──────────────┘  └──────┬───────┘              │
│                                              │                       │
│                                              ▼                       │
│                                        ┌──────────┐                 │
│                                        │  Models  │                 │
│                                        └──────────┘                 │
└────────────────────────────┬───────────────────────────────────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
     ┌──────────┐     ┌──────────┐    ┌──────────┐
     │ MongoDB  │     │  Redis   │    │ Celery   │
     │  (Beanie)│     │ (Cache)  │    │ Workers  │
     └──────────┘     └──────────┘    └──────────┘
```

---

## Data Flow: Job Ingestion → Matching → Resume Generation

```
RSS FEEDS                     USER URL
   │                             │
   └──────────┬──────────────────┘
              ▼
   ┌────────────────────┐
   │  Job Ingestion     │
   │  - Parse HTML/XML  │
   │  - Extract skills  │
   │  - Normalize text  │
   │  - Generate hash   │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │   Deduplication    │───→ Exists? → Skip
   │   (MD5 hash)       │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │   Create Job       │
   │   (MongoDB)        │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │  Matching Engine   │
   │  - Score vs users  │
   │  - 6 dimensions    │
   │  - Apply filters   │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │   Create Matches   │
   │   (score >= 60)    │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │  Daily Digest      │───→ Email to user
   │  (Celery Beat)     │
   └────────────────────┘
            │
            ▼
   ┌────────────────────┐
   │  User clicks       │
   │  "Generate Resume" │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │  Deduct 1 Credit   │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │  Queue Celery Task │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │  Claude AI API     │
   │  - Build prompt    │
   │  - Parse JSON      │
   │  - Tailor content  │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │  Generate PDF      │───→ Upload to R2
   │  (WeasyPrint)      │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │  Update Match      │
   │  status = ready    │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │  Send Email        │───→ "Resume ready!"
   │  (SendGrid)        │
   └────────────────────┘
```

---

## Matching Algorithm Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER PROFILE                              │
│  - Desired roles: ["Software Engineer", "Backend Dev"]      │
│  - Skills: ["Python", "FastAPI", "MongoDB", "Docker"]       │
│  - Location: "San Francisco" + Remote OK                    │
│  - Experience: 3-5 years (Mid-level)                        │
│  - Salary: $120k - $180k                                    │
│  - Keywords: ["API", "microservices"]                       │
│  - Exclude: ["blockchain", "crypto"]                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    JOB POSTING                               │
│  - Title: "Senior Backend Engineer"                         │
│  - Company: "TechCorp"                                       │
│  - Skills: ["Python", "FastAPI", "PostgreSQL", "AWS"]       │
│  - Location: "Remote"                                        │
│  - Experience: "Mid to Senior"                              │
│  - Salary: $140k - $200k                                    │
│  - Description: "...building microservices..."              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               SCORING ENGINE (6 Dimensions)                  │
│                                                              │
│  ┌──────────────────────────────────────────┐               │
│  │ 1. Title Match (30%)                     │               │
│  │    "Senior Backend Engineer" vs          │               │
│  │    ["Software Engineer", "Backend Dev"]  │               │
│  │    → 75% (partial match)                 │               │
│  └──────────────────────────────────────────┘               │
│  Score contribution: 0.75 × 30 = 22.5                       │
│                                                              │
│  ┌──────────────────────────────────────────┐               │
│  │ 2. Skills Match (30%)                    │               │
│  │    User has: 2/4 job skills              │               │
│  │    ["Python" ✓, "FastAPI" ✓,            │               │
│  │     "PostgreSQL" ✗, "AWS" ✗]            │               │
│  │    → 50%                                 │               │
│  └──────────────────────────────────────────┘               │
│  Score contribution: 0.50 × 30 = 15.0                       │
│                                                              │
│  ┌──────────────────────────────────────────┐               │
│  │ 3. Location Match (15%)                  │               │
│  │    Remote job + user accepts remote      │               │
│  │    → 100%                                │               │
│  └──────────────────────────────────────────┘               │
│  Score contribution: 1.0 × 15 = 15.0                        │
│                                                              │
│  ┌──────────────────────────────────────────┐               │
│  │ 4. Experience Match (10%)                │               │
│  │    "Mid to Senior" matches "Mid-level"   │               │
│  │    → 100%                                │               │
│  └──────────────────────────────────────────┘               │
│  Score contribution: 1.0 × 10 = 10.0                        │
│                                                              │
│  ┌──────────────────────────────────────────┐               │
│  │ 5. Keyword Match (10%)                   │               │
│  │    Required: ["API", "microservices"]    │               │
│  │    Found in JD: 2/2                      │               │
│  │    → 100%                                │               │
│  └──────────────────────────────────────────┘               │
│  Score contribution: 1.0 × 10 = 10.0                        │
│                                                              │
│  ┌──────────────────────────────────────────┐               │
│  │ 6. Salary Match (5%)                     │               │
│  │    Ranges overlap: $140k-$180k           │               │
│  │    → 100%                                │               │
│  └──────────────────────────────────────────┘               │
│  Score contribution: 1.0 × 5 = 5.0                          │
│                                                              │
│  ┌──────────────────────────────────────────┐               │
│  │ TOTAL SCORE: 77.5%                       │               │
│  │ THRESHOLD: 60% → CREATE MATCH ✓          │               │
│  └──────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Schema Relationships

```
┌──────────────────┐
│      USER        │
│                  │
│  - id            │
│  - email         │
│  - password_hash │
│  - credits: 3    │
│  ├─ profile      │──┐
│  ├─ preferences  │  │
│  └─ settings     │  │
└────────┬─────────┘  │
         │            │
         │            │
         ▼            │
┌──────────────────┐  │
│      MATCH       │  │
│                  │  │
│  - user_id ──────┼──┘
│  - job_id        │
│  - score: 77.5   │
│  - status: new   │
│  - resume_id     │──┐
│  └─ breakdown    │  │
└────────┬─────────┘  │
         │            │
         ▼            │
┌──────────────────┐  │
│       JOB        │  │
│                  │  │
│  - id            │  │
│  - title         │  │
│  - company       │  │
│  - fingerprint   │  │
│  - skills []     │  │
└──────────────────┘  │
                      │
                      │
                      ▼
         ┌──────────────────┐
         │     RESUME       │
         │                  │
         │  - id            │
         │  - match_id      │
         │  - user_id       │
         │  - content       │
         │  - pdf_url       │
         │  - ats_score     │
         └──────────────────┘
```

---

## Celery Task Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Celery Beat (Scheduler)                   │
└─────────────┬───────────────────────────────────────────────┘
              │
              ├──→ Every 30 min: ingest_all_feeds_task
              │
              ├──→ Every 1 hour: run_matching_all_task
              │
              └──→ Daily 6 PM:   send_daily_digests_task
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Redis (Message Broker)                    │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Celery Worker Pool                        │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Worker 1 │  │ Worker 2 │  │ Worker 3 │  │ Worker 4 │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘

Task Types:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 ingest_all_feeds_task        → Parse RSS feeds
🔗 ingest_url_task              → Parse user URL
🎯 run_matching_all_task        → Score jobs vs users
✨ generate_resume_task         → Claude AI generation
📧 send_daily_digests_task      → Email notifications
```

---

## Frontend Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Pages                                │
│                                                              │
│  /login          ──→  Register/Login split view             │
│  /                ──→  Redirect based on auth               │
│  /dashboard      ──→  Stats + recent matches               │
│  /matches        ──→  Full match list (TODO)                │
│  /job/:id        ──→  Job detail + resume gen (TODO)        │
│  /onboarding     ──→  4-step wizard (TODO)                  │
│  /profile        ──→  Edit profile (TODO)                   │
│  /preferences    ──→  Job preferences (TODO)                │
│  /settings       ──→  Billing + credits (TODO)              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├──→ Layouts
                 │    └─ app.vue (sidebar + nav)
                 │
                 ├──→ Stores (Pinia)
                 │    └─ auth.ts (login, register, logout)
                 │
                 ├──→ Composables
                 │    └─ useJobs.ts (API calls + helpers)
                 │
                 └──→ Components (TODO)
                      ├─ JobCard.vue
                      ├─ ScoreRing.vue
                      ├─ ResumePreview.vue
                      └─ UrlIngestModal.vue
```

---

## Technology Stack

```
Frontend                Backend                 Infrastructure
━━━━━━━━                ━━━━━━━━                ━━━━━━━━━━━━━━━
Nuxt 3                  FastAPI                 Docker
Vue 3                   Python 3.12             MongoDB
TypeScript              Beanie ODM              Redis
Tailwind CSS            Celery                  Railway
Pinia                   Anthropic SDK           Vercel
                        httpx                   Cloudflare R2
                        BeautifulSoup           SendGrid
                        feedparser              Stripe
                        WeasyPrint
```

---

This architecture supports:
- ✅ Horizontal scaling (stateless API)
- ✅ Background processing (Celery)
- ✅ Real-time matching (event-driven)
- ✅ AI integration (Claude API)
- ✅ Deduplication (fingerprinting)
- ✅ Freemium monetization (credits)
