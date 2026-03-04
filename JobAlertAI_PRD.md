# ⚡ JobAlert AI — Product Requirements Document

**Version:** 1.0 — MVP Release
**Date:** March 2026
**Stack:** FastAPI · MongoDB · Nuxt.js 3
**AI Model:** Claude Sonnet (Anthropic)
**Target Users:** All professionals, all industries

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [System Architecture](#2-system-architecture)
3. [Data Models — models.py](#3-data-models--modelspy)
4. [API Routes — routes.py](#4-api-routes--routespy)
5. [Controllers](#5-controllers)
6. [Services](#6-services)
7. [Background Workers](#7-background-workers)
8. [Core User Flows](#8-core-user-flows)
9. [Frontend — Nuxt.js 3](#9-frontend--nuxtjs-3)
10. [Build Plan — 8-Week MVP](#10-build-plan--8-week-mvp)
11. [Non-Functional Requirements](#11-non-functional-requirements)
12. [Open Questions & Decisions](#12-open-questions--decisions)

---

## 1. Product Overview

### 1.1 Vision

JobAlert AI is an AI-powered job hunting platform that monitors thousands of job boards on behalf of users, scores every new posting against their profile, and — only when a user demonstrates intent by clicking through — generates a tailored, ATS-optimised resume ready to submit.

**Core promise: from email alert to submitted application in under 60 seconds.**

### 1.2 Problem Statement

- Job seekers spend 3–5 hours per week manually checking job boards for new postings
- Generic resumes have a 2–3% ATS pass rate; tailored resumes can reach 60–70%
- The tailoring process is time-consuming and most candidates skip it entirely
- Existing alert tools notify but offer no downstream help with the application itself

### 1.3 Solution — Three Layers

| Layer | What It Does |
|---|---|
| **Ingestion** | Continuously parses XML/RSS feeds, paid APIs, and user-submitted URLs for new job postings |
| **Intelligence** | Scores every job against user profiles with a weighted matching engine. Sends one daily digest email of top matches |
| **Action** | When the user clicks through, AI generates a tailored resume on-demand and shows a one-click apply button |

### 1.4 Monetisation Model

Freemium with pay-per-resume micro-transactions. Resumes are **never** generated speculatively — only on user intent. This keeps AI costs near zero for non-converting free users (~$0.011/user/month).

| Tier | Price | Resume Credits | Alerts |
|---|---|---|---|
| Free | $0 / forever | 3 per month | Unlimited (daily digest) |
| Single Resume | $2.99 one-time | 1 credit | — |
| 5-Pack Bundle | $9.99 one-time | 5 credits | — |
| Unlimited Month | $19.99 / month | Unlimited | Instant alerts |
| Resume Audit | $24.99 one-time | Full AI review + report | — |

> **Key insight:** The paywall fires at the highest-intent moment — when a user has clicked through from an email about a specific job they want. Conversion at this point should be 20–30%.

---

## 2. System Architecture

### 2.1 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| API Backend | Python 3.12 + FastAPI | REST API, auth, business logic orchestration |
| Database | MongoDB 7 + Beanie ODM | Documents, matches, resumes |
| Task Queue | Celery + Redis | Background ingestion, scheduling, resume generation |
| AI Engine | Anthropic Claude Sonnet | Resume tailoring, ATS keyword optimisation |
| PDF Export | WeasyPrint | HTML → PDF resume generation |
| File Storage | Cloudflare R2 (S3-compatible) | Resume PDF hosting |
| Email | SendGrid | Job alert digest emails |
| Frontend | Nuxt.js 3 + TailwindCSS | User dashboard and onboarding |

### 2.2 Backend Architecture Pattern

The FastAPI backend follows a strict **4-layer architecture**. Every feature passes through all four layers in order. No layer may skip another.

| Layer | File | Responsibility |
|---|---|---|
| **Route** | `routes.py` | Declares HTTP endpoints. Maps URL + method to a controller function. Zero business logic. |
| **Controller** | `controllers/{name}_controller.py` | Receives parsed request data. Orchestrates service calls. Builds HTTP response. No DB access. |
| **Service** | `services/{name}_service.py` | All business logic, validation, calculations, and DB operations via models. Reusable across controllers. |
| **Model** | `models.py` | Single file. All Beanie document definitions. No logic — pure schema and indexes. |

### 2.3 Request Flow

Every HTTP request follows this exact path — no exceptions:

```
HTTP Request
    ↓
routes.py              → defines @router.post('/jobs/ingest-url')
    ↓  calls
job_controller.py      → parses request, calls service, returns response
    ↓  calls
job_service.py         → business logic, validation, DB operations
    ↓  uses
models.py              → Beanie document (Job, User, Match, Resume...)
    ↓
MongoDB
```

### 2.4 Full Directory Structure

```
backend/
├── app/
│   ├── main.py                        # FastAPI app init, lifespan hooks
│   ├── config.py                      # Settings via pydantic-settings + .env
│   ├── database.py                    # MongoDB connect / disconnect
│   │
│   ├── models.py                      # ALL Beanie documents — single source of truth
│   │
│   ├── routes.py                      # ALL route registrations in one file
│   │                                  # Imports and mounts all routers/controllers
│   │
│   ├── controllers/
│   │   ├── auth_controller.py
│   │   ├── profile_controller.py
│   │   ├── job_controller.py
│   │   └── resume_controller.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── profile_service.py
│   │   ├── job_service.py
│   │   ├── resume_service.py
│   │   ├── matching_service.py
│   │   ├── notification_service.py
│   │   ├── pdf_service.py
│   │   └── ingestion/
│   │       ├── xml_feed_service.py    # RSS, Greenhouse, Lever, custom XML
│   │       ├── url_parser_service.py  # User-pasted URL handler
│   │       └── normalizer.py         # Text cleanup, skill extraction, ATS detect
│   │
│   └── workers/
│       └── celery_worker.py           # Celery app + Beat schedule
│
├── requirements.txt
└── Dockerfile

frontend/
├── pages/
│   ├── login.vue
│   ├── onboarding.vue
│   ├── dashboard.vue
│   ├── matches.vue
│   ├── job/[id].vue
│   ├── profile.vue
│   ├── preferences.vue
│   └── settings.vue
├── components/
│   ├── JobCard.vue
│   ├── ScoreRing.vue
│   ├── ResumePreview.vue
│   ├── ScoreBar.vue
│   ├── UrlIngestModal.vue
│   ├── StatusBadge.vue
│   ├── StatCard.vue
│   ├── NavItem.vue
│   └── EmptyState.vue
├── composables/
│   └── useJobs.ts
├── stores/
│   └── auth.ts                        # Pinia auth store
└── layouts/
    └── app.vue                        # Sidebar layout
```

---

## 3. Data Models — `models.py`

All MongoDB document definitions live in a **single `models.py` file**. This is the single source of truth for data shape across the entire application. No model definitions exist anywhere else.

### 3.1 User

```python
class User(Document):
    email: Indexed(EmailStr, unique=True)
    password_hash: Optional[str]          # None for OAuth users
    google_id: Optional[str]
    credits: int = 3                      # Resume generation credits
    is_active: bool = True
    is_verified: bool = False
    onboarding_complete: bool = False
    profile: UserProfile                  # Embedded
    preferences: JobPreferences           # Embedded
    notification_settings: NotificationSettings  # Embedded
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
```

**Embedded — UserProfile:**

| Field | Type | Description |
|---|---|---|
| full_name | str | Display name |
| phone | Optional[str] | Contact number |
| location | Optional[str] | City, Country |
| linkedin_url | Optional[str] | Profile URL |
| portfolio_url | Optional[str] | Portfolio / GitHub |
| summary | str | Base professional summary |
| skills | List[str] | Skill keywords |
| languages | List[str] | Spoken languages |
| experience | List[WorkExperience] | Jobs with bullets |
| education | List[Education] | Degrees |
| certifications | List[Certification] | Certs and licenses |

**Embedded — JobPreferences:**

| Field | Type | Description |
|---|---|---|
| roles | List[str] | Target job titles |
| industries | List[str] | Target industries |
| locations | List[str] | Preferred cities |
| remote | Optional[bool] | None = no preference |
| salary_min | Optional[int] | Minimum acceptable salary |
| experience_level | Optional[ExperienceLevel] | entry/mid/senior/lead/executive |
| keywords | List[str] | Must-have keywords in JD |
| exclude_keywords | List[str] | Hard-reject if found in JD |
| exclude_companies | List[str] | Hard-reject company names |

**Embedded — NotificationSettings:**

| Field | Type | Description |
|---|---|---|
| email | bool | Email alerts enabled |
| push | bool | Push notifications enabled |
| frequency | NotificationFrequency | instant / daily_digest / weekly_digest |
| min_match_score | int | Only notify if score ≥ this (default 70) |

---

### 3.2 Job

```python
class Job(Document):
    fingerprint: Indexed(str, unique=True)  # MD5(title+company+apply_url)
    source: JobSource                        # xml_feed | rss_feed | api | scrape | user_url
    source_name: str                         # e.g. "RemoteOK", "Greenhouse - Stripe"
    source_url: str
    apply_url: str                           # Direct application link
    title: str
    company: str
    company_logo_url: Optional[str]
    location: Optional[str]
    is_remote: bool
    is_hybrid: bool
    description_raw: str                     # Original HTML/XML
    description_clean: str                   # Normalised plain text for AI + matching
    required_skills: List[str]               # Extracted skill keywords
    preferred_skills: List[str]
    experience_level: Optional[str]          # entry/mid/senior/lead
    salary: Optional[SalaryInfo]             # min, max, currency, period
    ats_platform: ATSPlatform                # greenhouse | lever | workday | ...
    is_active: bool
    posted_at: Optional[datetime]
    scraped_at: datetime
    expires_at: Optional[datetime]
    tags: List[str]
```

---

### 3.3 Match

```python
class Match(Document):
    user_id: ObjectId                        # Indexed
    job_id: ObjectId                         # Indexed
    score: float                             # 0–100 composite score
    score_breakdown: ScoreBreakdown          # Per-dimension scores
    matched_keywords: List[str]              # Skills in both profile and JD
    status: MatchStatus                      # new | viewed | generating | resume_ready | applied | dismissed | saved
    resume_id: Optional[ObjectId]            # Set after successful generation
    notified_at: Optional[datetime]
    viewed_at: Optional[datetime]
    applied_at: Optional[datetime]
    created_at: datetime
```

**Embedded — ScoreBreakdown:**

| Dimension | Weight | Scoring Logic |
|---|---|---|
| title_match | 30% | Role keyword overlap between user.preferences.roles and job.title |
| skills_match | 30% | User skills vs job.required_skills intersection |
| location_match | 15% | Remote preference alignment, city match |
| experience_level_match | 10% | User level vs job level, adjacent = partial credit |
| keyword_match | 10% | Must-have keywords present in description_clean |
| salary_match | 5% | user.preferences.salary_min vs job.salary.max |

---

### 3.4 Resume

```python
class Resume(Document):
    user_id: ObjectId
    job_id: ObjectId
    match_id: ObjectId
    version: int = 1                         # Incremented on regeneration
    content: ResumeContent                   # Embedded — the actual resume data
    html_content: Optional[str]              # Rendered HTML before PDF conversion
    pdf_url: Optional[str]                   # Cloudflare R2 signed URL
    ats_score: Optional[float]               # Estimated ATS pass score 0–100
    keywords_injected: List[str]             # Keywords added from JD by AI
    keywords_missing: List[str]              # Important JD keywords absent from resume
    ai_model: str                            # Model used for generation
    prompt_tokens: int                       # Cost tracking
    completion_tokens: int
    generation_time_ms: int                  # Performance monitoring
    created_at: datetime
```

**Embedded — ResumeContent:**

```python
class ResumeContent(BaseModel):
    summary: str                             # Tailored for this specific role
    skills: List[str]                        # Reordered — most relevant first
    experience: List[ResumeExperience]       # Rewritten bullets per role
    education: List[dict]
    certifications: List[dict]
```

---

### 3.5 Notification

```python
class Notification(Document):
    user_id: ObjectId
    match_id: ObjectId
    job_id: ObjectId
    channel: NotificationChannel             # email | push | in_app
    status: NotificationStatus               # pending | sent | delivered | opened | clicked | failed
    subject: Optional[str]
    body: Optional[str]
    sendgrid_message_id: Optional[str]       # For delivery tracking
    sent_at: Optional[datetime]
    opened_at: Optional[datetime]
    clicked_at: Optional[datetime]
    failed_reason: Optional[str]
    created_at: datetime
```

---

## 4. API Routes — `routes.py`

`routes.py` is the single file that declares all HTTP endpoints and maps them to controllers. It contains **no business logic**. Each route function does three things only: parse the request, call a controller, return the response.

### 4.1 Auth — `/api/auth`

| Method | Path | Controller Function | Auth | Description |
|---|---|---|---|---|
| POST | `/register` | `auth_controller.register` | Public | Create account, return JWT |
| POST | `/login` | `auth_controller.login` | Public | Validate credentials, return JWT |
| GET | `/me` | `auth_controller.me` | Bearer | Return current user |
| POST | `/refresh` | `auth_controller.refresh` | Bearer | Refresh expired JWT |

### 4.2 Profile — `/api/profile`

| Method | Path | Controller Function | Auth | Description |
|---|---|---|---|---|
| PUT | `/` | `profile_controller.update_profile` | Bearer | Update profile (name, skills, experience) |
| PUT | `/preferences` | `profile_controller.update_preferences` | Bearer | Update job search preferences |
| PUT | `/notifications` | `profile_controller.update_notifications` | Bearer | Update alert settings |
| POST | `/onboarding/complete` | `profile_controller.complete_onboarding` | Bearer | Mark onboarding done, trigger initial matching |
| GET | `/credits` | `profile_controller.get_credits` | Bearer | Return current credit balance |

### 4.3 Jobs — `/api/jobs`

| Method | Path | Controller Function | Auth | Description |
|---|---|---|---|---|
| GET | `/` | `job_controller.list_jobs` | Public | Browse all active jobs with filters |
| GET | `/{job_id}` | `job_controller.get_job` | Public | Get single job by ID |
| POST | `/ingest-url` | `job_controller.ingest_url` | Bearer | Submit a job URL for background processing |
| GET | `/my/matches` | `job_controller.list_matches` | Bearer | Get user's scored matches, paginated |
| GET | `/my/matches/{match_id}` | `job_controller.get_match` | Bearer | Get single match with job detail |
| PATCH | `/my/matches/{match_id}/status` | `job_controller.update_match_status` | Bearer | Set status: applied, dismissed, saved |

### 4.4 Resumes — `/api/resumes`

| Method | Path | Controller Function | Auth | Description |
|---|---|---|---|---|
| POST | `/generate/{match_id}` | `resume_controller.generate` | Bearer | Trigger on-demand AI generation (deducts 1 credit) |
| GET | `/{resume_id}` | `resume_controller.get_resume` | Bearer | Get resume content by ID |
| GET | `/match/{match_id}` | `resume_controller.get_by_match` | Bearer | Get resume for a specific match |
| GET | `/{resume_id}/pdf` | `resume_controller.download_pdf` | Bearer | Redirect to R2 signed PDF URL |

### 4.5 Payments — `/api/payments`

| Method | Path | Controller Function | Auth | Description |
|---|---|---|---|---|
| POST | `/checkout` | `payment_controller.create_checkout` | Bearer | Create Stripe Checkout session |
| POST | `/webhook` | `payment_controller.stripe_webhook` | Stripe sig | Handle successful payment, add credits |
| GET | `/history` | `payment_controller.get_history` | Bearer | User's purchase history |

---

## 5. Controllers

Controllers are **thin orchestration layers**. They receive parsed inputs from routes, call one or more service functions, and return structured HTTP responses.

### Controller Rules

- One controller file per feature domain: `auth`, `profile`, `job`, `resume`, `payment`
- Controller functions are `async` and receive typed Pydantic models as inputs
- Controllers call service functions — **never** model methods directly
- Controllers handle HTTP-level concerns: status codes, response shaping, error catching
- If a controller function exceeds ~30 lines, move logic to the service layer
- Controllers never contain `await Job.find(...)` or any direct DB call

### 5.1 auth_controller.py

| Function | Calls Service | Returns |
|---|---|---|
| `register(body: RegisterRequest)` | `auth_service.create_user()` | `201 + TokenResponse` |
| `login(form: OAuth2PasswordRequestForm)` | `auth_service.authenticate_user()` | `200 + TokenResponse` |
| `me(current_user: User)` | — (user resolved by Depends) | `200 + UserResponse` |
| `refresh(token: str)` | `auth_service.refresh_token()` | `200 + TokenResponse` |

### 5.2 profile_controller.py

| Function | Calls Service | Returns |
|---|---|---|
| `update_profile(body, user)` | `profile_service.update_profile()` | `200 + ProfileResponse` |
| `update_preferences(body, user)` | `profile_service.update_preferences()` | `200 + PreferencesResponse` |
| `update_notifications(body, user)` | `profile_service.update_notification_settings()` | `200 + message` |
| `complete_onboarding(user)` | `profile_service.complete_onboarding()` | `200 + message` |
| `get_credits(user)` | `profile_service.get_credit_balance()` | `200 + { credits: int }` |

### 5.3 job_controller.py

| Function | Calls Service | Returns |
|---|---|---|
| `list_jobs(filters)` | `job_service.get_jobs(filters)` | `200 + PaginatedJobResponse` |
| `get_job(job_id)` | `job_service.get_job_by_id(job_id)` | `200 + JobResponse` |
| `ingest_url(url, user)` | `job_service.queue_url_ingestion(url, user_id)` | `202 + message` |
| `list_matches(user, filters)` | `job_service.get_user_matches(user_id, filters)` | `200 + PaginatedMatchResponse` |
| `get_match(match_id, user)` | `job_service.get_match_detail(match_id, user_id)` | `200 + MatchDetailResponse` |
| `update_match_status(match_id, status)` | `job_service.set_match_status(match_id, status)` | `200 + MatchResponse` |

### 5.4 resume_controller.py

| Function | Calls Service | Returns |
|---|---|---|
| `generate(match_id, user)` | `resume_service.generate_on_demand(match_id, user)` | `202 + GeneratingResponse` |
| `get_resume(resume_id, user)` | `resume_service.get_resume(resume_id, user_id)` | `200 + ResumeResponse` |
| `get_by_match(match_id, user)` | `resume_service.get_resume_for_match(match_id, user_id)` | `200 + ResumeResponse` |
| `download_pdf(resume_id, user)` | `resume_service.get_pdf_url(resume_id, user_id)` | `302 redirect to R2 URL` |

---

## 6. Services

Services contain **all business logic**. They are the only layer permitted to query the database (via Beanie models), call external APIs, or perform AI operations. Services are imported by controllers and workers — never by routes directly.

### 6.1 auth_service.py

```
create_user(email, password, full_name)
    → hash password with bcrypt
    → check email not already registered (raise 400 if taken)
    → insert User document
    → return signed JWT

authenticate_user(email, password)
    → fetch User by email (raise 401 if not found)
    → verify bcrypt hash (raise 401 if mismatch)
    → update user.last_login
    → return signed JWT

create_access_token(user_id) → str
    → sign JWT with SECRET_KEY, set expiry

get_current_user(token) → User
    → decode JWT, extract user_id
    → fetch User from DB
    → raise 401 if not found or inactive
```

### 6.2 profile_service.py

```
update_profile(user_id, profile_data: UserProfile) → User
    → validate data
    → set user.profile = profile_data
    → set user.updated_at = now
    → save and return

update_preferences(user_id, preferences: JobPreferences) → User
    → validate data
    → set user.preferences = preferences
    → save
    → trigger: matching_service.run_matching_for_user(user_id) in background

update_notification_settings(user_id, settings: NotificationSettings) → None
    → save settings to user document

complete_onboarding(user_id) → None
    → set user.onboarding_complete = True
    → trigger: matching_service.run_matching_for_user(user_id) in background

get_credit_balance(user_id) → int
    → return user.credits

deduct_credit(user_id) → None
    → atomic decrement user.credits
    → raise HTTP 402 if credits == 0
```

### 6.3 job_service.py

```
get_jobs(filters: JobFilters) → PaginatedResult[Job]
    → build Beanie query with is_active=True
    → apply filters: remote, title text search, location
    → paginate and return

get_job_by_id(job_id: str) → Job
    → fetch Job or raise 404

queue_url_ingestion(url: str, user_id: str) → None
    → push Celery task: ingest_url_task.delay(url, user_id)
    → return immediately (202)

get_user_matches(user_id, filters) → PaginatedResult[MatchDetail]
    → query Match where user_id = user_id
    → apply status filter if provided
    → sort by score descending
    → join Job data for each match
    → return enriched list

get_match_detail(match_id, user_id) → MatchDetail
    → fetch Match, verify match.user_id == user_id (raise 403 if not)
    → fetch associated Job
    → update match.viewed_at if status == new
    → return Match + Job combined

set_match_status(match_id, status: MatchStatus) → Match
    → fetch Match, verify ownership
    → update status and relevant timestamp (applied_at, etc.)
    → save and return
```

### 6.4 resume_service.py

```
generate_on_demand(match_id: str, user: User) → None
    → verify match exists and belongs to user (raise 403)
    → check match.status != already generating or resume_ready
    → call profile_service.deduct_credit(user_id)  ← raises 402 if no credits
    → update match.status = generating
    → push Celery task: generate_resume_task.delay(user_id, job_id, match_id)
    → return 202

generate_resume(user_id, job_id, match_id) → Resume
    ← called by Celery worker only, never by controller
    → fetch User, Job, Match
    → build AI prompt from user.profile + job.description_clean
    → call Claude API, parse JSON response
    → build ResumeContent from parsed data
    → insert Resume document
    → call pdf_service.generate_pdf(resume)
    → update match.resume_id = resume.id
    → update match.status = resume_ready
    → call notification_service.send_resume_ready_email(user, job, resume)
    → return Resume

get_resume(resume_id, user_id) → Resume
    → fetch Resume, verify resume.user_id == user_id (raise 403)
    → return

get_resume_for_match(match_id, user_id) → Resume
    → fetch Match, verify ownership
    → raise 404 if match.resume_id is None
    → return get_resume(match.resume_id, user_id)

get_pdf_url(resume_id, user_id) → str
    → fetch Resume, verify ownership
    → return resume.pdf_url (R2 signed URL)
```

### 6.5 matching_service.py

```
run_matching_for_job(job_id: str) → int
    → fetch Job
    → fetch all active + onboarded Users
    → for each user: call score_job_for_user(job, user)
    → create Match document if score >= MIN_MATCH_SCORE
    → return count of new matches created

run_matching_for_user(user_id: str) → int
    → fetch User
    → fetch recent active jobs (last 30 days), excluding already-matched
    → for each job: call score_job_for_user(job, user)
    → create Match documents above threshold
    → return count

score_job_for_user(job: Job, user: User) → float | None
    → apply hard filters first:
        exclude_keywords present in description_clean → return None
        exclude_companies match job.company → return None
    → calculate 6 weighted dimension scores
    → composite = sum(score * weight for each dimension)
    → return None if composite < MIN_MATCH_SCORE
    → check no existing Match for this user+job pair
    → insert Match with score + breakdown
    → return composite score
```

**Scoring Dimensions:**

| Dimension | Weight | How Scored |
|---|---|---|
| Title match | 30% | Max overlap between user.preferences.roles and job.title words |
| Skills match | 30% | Intersection of user skills + preferences.keywords vs job.required_skills |
| Location match | 15% | Remote preference alignment; city string match; penalise mismatches |
| Experience level | 10% | Exact = 100, adjacent level = 70, two levels away = 40 |
| Keyword match | 10% | Fraction of preferences.keywords found in description_clean |
| Salary match | 5% | job.salary.max >= preferences.salary_min = 100, else scaled |

### 6.6 notification_service.py

```
send_daily_digest(user: User) → None
    → collect all new matches from last 24h with status = new
    → sort by score descending
    → take top match as hero, next 2–4 as compact list
    → count remaining matches for "X more in dashboard" line
    → build HTML email (match data only — NO resume generation)
    → call send_email(user.email, subject, html)
    → insert Notification document
    → update match.notified_at for all included matches

send_resume_ready_email(user, job, resume) → None
    → build HTML email: job details + ATS score + "View & Apply" CTA
    → call send_email(...)
    → insert Notification document

send_instant_alert(user, match, job) → None
    → only called for users with frequency = instant and score >= 85
    → single match email immediately after matching
    → NO resume generation triggered

send_email(to, subject, html) → bool
    → POST to SendGrid /v3/mail/send
    → return True on 202, log error and return False otherwise
```

> **Critical rule:** `notification_service` **never** calls `resume_service`. The email contains match data only. Resume generation is always triggered by the user clicking through, not by the notification system.

### 6.7 ingestion/xml_feed_service.py

```
parse_all_feeds() → int
    → iterate XML_FEEDS registry (RemoteOK, WeWorkRemotely, Jobicy, etc.)
    → for each: call parse_rss_feed(config)
    → return total new jobs saved

parse_rss_feed(client, config) → int
    → fetch URL with httpx
    → parse with feedparser
    → for each entry: extract title, company, location, description, apply_url
    → call normalizer.normalize_job_description(raw_html)
    → call normalizer.extract_skills(clean_text)
    → build fingerprint: MD5(title.lower() + company.lower() + apply_url)
    → call _save_job(job_data)
    → return count of new saves

parse_greenhouse_feed(company_slug) → int
    → GET https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true
    → parse JSON response
    → for each job: extract fields, build job_data dict
    → call _save_job(job_data)

parse_lever_feed(company_slug) → int
    → GET https://api.lever.co/v0/postings/{slug}?mode=json
    → parse JSON response, extract descriptionBodyHtml
    → call _save_job for each posting

parse_custom_xml(url, source_name, xpath_config) → int
    → fetch URL, parse with lxml etree
    → apply xpath_config selectors for each element
    → call _save_job for each extracted job

_save_job(job_data: dict) → bool
    → check existing Job with same fingerprint
    → return False if exists (duplicate)
    → insert new Job document
    → trigger: matching_service.run_matching_for_job(job.id) via Celery
    → return True
```

**Registered XML Feed Sources:**

| Source | URL | Type |
|---|---|---|
| RemoteOK | `https://remoteok.com/remote-jobs.xml` | RSS |
| WeWorkRemotely — Programming | `https://weworkremotely.com/categories/remote-programming-jobs.rss` | RSS |
| WeWorkRemotely — Design | `https://weworkremotely.com/categories/remote-design-jobs.rss` | RSS |
| WeWorkRemotely — Business | `https://weworkremotely.com/categories/remote-business-jobs.rss` | RSS |
| Jobicy — All Remote | `https://jobicy.com/?feed=job_feed&job_region=anywhere` | RSS |
| Greenhouse (per company) | `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs` | JSON API |
| Lever (per company) | `https://api.lever.co/v0/postings/{slug}?mode=json` | JSON API |

### 6.8 ingestion/url_parser_service.py

```
ingest_from_url(url: str, user_id: str) → str | None
    → parse domain from URL
    → route to ATS-specific parser:
        "greenhouse.io"      → _parse_greenhouse_url(client, url)
        "lever.co"           → _parse_lever_url(client, url)
        anything else        → _parse_generic_url(client, url)
    → deduplicate via fingerprint
    → save Job if new
    → trigger matching_service.run_matching_for_job(job_id, specific_user_id=user_id)
    → return job_id

_parse_greenhouse_url(client, url) → dict
    → extract company_slug and job_id from URL path
    → GET https://boards-api.greenhouse.io/v1/boards/{slug}/jobs/{job_id}
    → extract title, location, content (HTML description)
    → call normalizer functions

_parse_lever_url(client, url) → dict
    → extract company_slug and job_id from URL path
    → GET https://api.lever.co/v0/postings/{slug}/{job_id}
    → extract text, categories.location, descriptionBodyHtml

_parse_generic_url(client, url) → dict | None
    → GET with browser User-Agent header
    → BeautifulSoup parse
    → extract title from h1 or [class*="job-title"]
    → extract company from [class*="company"] or domain
    → extract description from main/article/[class*="description"]
    → return None if description < 100 chars (likely blocked)
```

### 6.9 pdf_service.py

```
generate_pdf(resume: Resume) → str | None
    → fetch User and Job for context
    → call _render_html(resume, user.profile, job)
    → store rendered HTML in resume.html_content
    → call WeasyPrint HTML(string=html).write_pdf() → bytes
    → call _upload_pdf(pdf_bytes, resume_id) → url
    → update resume.pdf_url
    → save resume
    → return pdf_url

_render_html(resume, profile, job) → str
    → inject ResumeContent into HTML template
    → ATS-safe layout: no images, no tables for layout, semantic heading hierarchy
    → return complete HTML string

_upload_pdf(pdf_bytes, resume_id) → str
    → if R2 configured: upload to Cloudflare R2, return public URL
    → else: save to /tmp/jobalert_resumes/{id}.pdf, return local path
```

---

## 7. Background Workers

All async work runs in **Celery workers**. The FastAPI app never blocks on long-running tasks.

| Task | Trigger | Schedule | Calls |
|---|---|---|---|
| `ingest_all_feeds` | Celery Beat | Every 30 minutes | `xml_feed_service.parse_all_feeds()` |
| `run_matching_all` | Celery Beat | Every hour (offset +15 min) | `matching_service.run_matching_for_job()` per recent job |
| `send_daily_digests` | Celery Beat | Daily at 18:00 per user timezone | `notification_service.send_daily_digest()` per user |
| `ingest_url_task` | API call (user action) | On demand | `url_parser_service.ingest_from_url()` |
| `generate_resume_task` | API call (user click) | On demand | `resume_service.generate_resume()` |

> **Critical:** `generate_resume_task` is **only** triggered by a user action (clicking through from an alert and confirming generation). It is **never** called by the ingestion pipeline, the matching engine, or the notification service.

### Worker Pipeline Flow

```
[Every 30 min] Celery Beat
    → ingest_all_feeds task
    → xml_feed_service.parse_all_feeds()
    → New jobs saved to MongoDB
    → For each new job: matching_service.run_matching_for_job(job_id)
    → New Match documents created for qualifying users
    → Matches queued for nightly digest

[Daily 18:00] Celery Beat
    → send_daily_digests task
    → notification_service.send_daily_digest(user) per active user
    → Single digest email sent (match data only, no resume)

[User clicks "Generate Resume"]
    → POST /api/resumes/generate/{match_id}
    → resume_controller.generate()
    → resume_service.generate_on_demand()
    → credit check + deduct
    → generate_resume_task.delay(user_id, job_id, match_id)
    → Claude API called, resume generated, PDF created, email sent
```

---

## 8. Core User Flows

### 8.1 Onboarding

```
User visits /login
    → Creates account (email + password)
    → Redirected to /onboarding

/onboarding — 4-step wizard
    Step 1: Personal Info (name, location, LinkedIn)
    Step 2: Work Experience (title, company, bullets)
    Step 3: Skills & Education
    Step 4: Job Preferences (roles, location, salary, remote)

    → profile_controller.complete_onboarding()
    → matching_service.run_matching_for_user() fires in background
    → User redirected to /dashboard
```

### 8.2 Alert → Apply (Happy Path)

```
[Background] New job posted → ingested → scored → match saved

[18:00] User receives daily digest email
    → Top match: "Senior PM at Stripe — 94% match"
    → Email shows: score, title, company, matched skills
    → Email does NOT generate or attach a resume

User clicks hero card in email
    → Lands on /job/{match_id}
    → Page shows: job details, score breakdown, matched keywords

If credits > 0:
    → "Generate My Resume" button
    → User clicks → POST /api/resumes/generate/{match_id}
    → Loading state shown: "Tailoring your resume..." (~8 seconds)
    → Resume appears: summary, reordered skills, rewritten bullets
    → ATS score shown: "82% — Strong match"
    → "Apply Now →" button → opens job apply_url in new tab
    → Match status updated to "applied"

If credits = 0:
    → Paywall shown with blurred resume preview
    → "$2.99 for this resume" or "$9.99 for 5-pack"
    → Stripe Checkout → credits added → generation fires immediately
```

### 8.3 URL Paste Flow

```
User sees a job elsewhere (LinkedIn, company site, etc.)
    → Clicks "Add Job URL" in dashboard
    → UrlIngestModal opens
    → User pastes URL

    → POST /api/jobs/ingest-url?url={url}
    → ingest_url_task queued
    → URL parsed (ATS-specific or generic)
    → Job saved, fingerprint checked for duplicate
    → matching_service scores for this user only
    → New match appears in dashboard within ~10 seconds

Same resume generation flow applies
```

---

## 9. Frontend — Nuxt.js 3

### 9.1 Pages

| Route | File | Layout | Description |
|---|---|---|---|
| `/login` | `pages/login.vue` | default | Register or sign in. Split layout: marketing left, form right |
| `/onboarding` | `pages/onboarding.vue` | default | 4-step profile wizard |
| `/dashboard` | `pages/dashboard.vue` | app | Stats row + recent matches list + URL modal trigger |
| `/matches` | `pages/matches.vue` | app | Full match list with status filter tabs |
| `/job/:id` | `pages/job/[id].vue` | app | Job detail, score breakdown, resume preview, apply CTA |
| `/profile` | `pages/profile.vue` | app | Edit personal info and work experience |
| `/preferences` | `pages/preferences.vue` | app | Edit job search preferences and alert keywords |
| `/settings` | `pages/settings.vue` | app | Notification settings, credit balance, billing history |

### 9.2 Components

| Component | Purpose |
|---|---|
| `JobCard.vue` | Match card — company logo/initial, score ring, tags (remote, salary, level), matched skills, status badge, time ago |
| `ScoreRing.vue` | Animated SVG circular score. Colour: green ≥80, amber ≥60, red <60 |
| `ResumePreview.vue` | In-app resume viewer. Summary → Skills → Experience bullets → Education |
| `ScoreBar.vue` | Horizontal bar for each match dimension in the breakdown panel |
| `UrlIngestModal.vue` | Paste job URL modal. ATS detection feedback. Loading + success states |
| `StatusBadge.vue` | Colour-coded pill: new, resume_ready, applied, dismissed, saved |
| `StatCard.vue` | Dashboard metric tile: icon, large number, label |
| `NavItem.vue` | Sidebar link with active highlight and optional count badge |
| `EmptyState.vue` | Centred state with icon, title, description, CTA slot |
| `Feature.vue` | Icon + text row used on login marketing panel |

### 9.3 State Management

**`stores/auth.ts` (Pinia)**
- State: `token`, `user`, `loading`
- Actions: `login()`, `register()`, `fetchMe()`, `logout()`
- Getter: `isLoggedIn`, `isOnboarded`
- Helper: `authHeaders()` — returns `{ Authorization: Bearer {token} }` for all API calls
- Persisted to localStorage via `pinia-plugin-persistedstate`

**`composables/useJobs.ts`**
- `fetchMatches(status?)` — paginated match list
- `ingestUrl(url)` — submit URL for background processing
- `getResume(matchId)` — fetch resume for a match
- `generateResume(matchId)` — trigger on-demand generation
- Helpers: `scoreColor(score)`, `scoreLabel(score)`, `timeAgo(dateStr)`

### 9.4 Design System

- **Theme:** Dark (navy `#0F172A` base), emerald `#059669` accent, glass-morphism cards
- **Fonts:** Syne (display/headings) + DM Sans (body) + JetBrains Mono (code/scores)
- **Score colours:** Emerald `#6EE7B7` (≥80), Amber `#FBBF24` (≥60), Red `#F87171` (<60)
- **Motion:** CSS transitions on page navigation; SVG stroke animation on ScoreRing; skeleton loaders on data fetch

---

## 10. Build Plan — 8-Week MVP

| Week | Focus | Key Deliverables |
|---|---|---|
| 1 | Foundations | FastAPI scaffold, `models.py`, `routes.py` pattern established, MongoDB + Beanie connected, JWT auth (register + login) |
| 2 | Profile & Preferences | `profile_controller`, `profile_service`, onboarding wizard in Nuxt (4 steps), credit field on User |
| 3 | Job Ingestion | `xml_feed_service` (RSS + Greenhouse + Lever), `url_parser_service`, Celery + Beat setup, deduplication |
| 4 | Matching Engine | `matching_service` with 6-dimension scoring, Match documents, score breakdown, hard filter exclusions |
| 5 | AI Resume Generation | `resume_service` with Claude API, JSON parsing, `ResumeContent` model, credit deduction on trigger |
| 6 | PDF + Notifications | `pdf_service` (WeasyPrint + R2), `notification_service`, daily digest email template |
| 7 | Frontend | Dashboard, matches list, job detail page with resume preview, URL modal, paywall moment |
| 8 | Payments + Launch | Stripe Checkout, webhook credit top-up, QA pass, Docker Compose, deploy to Railway + Vercel |

### Deployment Infrastructure

| Service | Provider | Notes |
|---|---|---|
| API | Railway | Dockerfile deploy, auto-restart, health checks |
| Celery Worker | Railway | Separate service, same image |
| Celery Beat | Railway | Separate service, same image |
| MongoDB | MongoDB Atlas (M0) | Free tier sufficient for MVP |
| Redis | Railway Redis plugin | Shared broker + result backend |
| Frontend | Vercel | Nuxt SSR, automatic preview deploys on PR |
| PDF Storage | Cloudflare R2 | $0.015/GB — effectively free at MVP scale |
| Email | SendGrid | Free tier: 100 emails/day |

---

## 11. Non-Functional Requirements

| Requirement | Target | Implementation |
|---|---|---|
| Resume generation time | < 15s P95 | Claude Sonnet is fast; show animated progress UI |
| Feed ingestion freshness | < 30 min from job posted to user alerted | Celery Beat every 30 min |
| API response time | < 300ms P99 for non-AI routes | Async FastAPI + compound MongoDB indexes |
| Email delivery | < 2 min from trigger | SendGrid transactional API, not batch |
| Job deduplication | Zero duplicates | MD5 fingerprint on title + company + apply_url |
| Free tier AI cost | < $0.02/user/month | Generate only on user click; 3 free credits cap |
| PDF ATS compatibility | Parseable by all major ATS | Plain HTML template, no images, semantic headings |
| Uptime | 99.5% API | Railway auto-restart + `/health` endpoint monitoring |

### Security Requirements

- All endpoints except `/api/auth/register` and `/api/auth/login` require a valid Bearer JWT
- Ownership verified in every service function — users can only access their own Match, Resume, and Notification documents
- Stripe webhook validated with `STRIPE_WEBHOOK_SECRET` signature on every request
- Passwords hashed with bcrypt (12 rounds). Never stored or logged in plain text
- All secrets in `.env` file — never committed to source control
- CORS restricted to known frontend origins in production (`app.jobalert.ai`)
- MongoDB connection uses authentication in production

---

## 12. Open Questions & Decisions

| Question | Options | Current Decision |
|---|---|---|
| Resume generation trigger | On match creation vs on user click | **On user click only** — protects AI budget |
| Email frequency default | Instant vs daily digest | **Daily digest** default; users opt into instant |
| Matching threshold | 50, 60, or 70 minimum score | **60** default; user can configure 50–85 in preferences |
| Cover letter product | Free, paid add-on, or phase 2 | **Phase 2** — $1.99 upsell at resume purchase moment |
| LinkedIn OAuth | MVP or phase 2 | **Phase 2** — complex ToS; Google OAuth sufficient for MVP |
| Auto-apply | Yes / No | **Phase 2** — legal and ToS risk; needs per-ATS implementation |
| Semantic matching | Keyword scoring vs embeddings | **Keyword for MVP**; add embeddings in phase 2 for better recall |
| Multi-language resumes | English only vs localised | **English only** for MVP |

---

*JobAlert AI — PRD v1.0 — Confidential — March 2026*
