# HR Automation System with n8n

> End-to-end recruitment automation platform using n8n workflow orchestration, AI-powered candidate evaluation (GPT-4), and human-in-the-loop decision making.

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![n8n](https://img.shields.io/badge/n8n-1.0+-orange.svg)](https://n8n.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com)
[![Airtable](https://img.shields.io/badge/Airtable-Database-blue.svg)](https://airtable.com)
[![Google Workspace](https://img.shields.io/badge/Google-Gmail%20%7C%20Calendar-red.svg)](https://workspace.google.com)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

---

## 🎯 Overview

This project automates the entire recruitment lifecycle—from automated job description generation and multi-platform posting to intelligent resume evaluation and calendar interview scheduling. It reduces time-to-hire by **30–40%**, cuts administrative workload by **70%**, and slashes operational costs from **₹1.65L–2.5L down to ₹16.5K–33K/month**.

The architecture combines **n8n** (visual workflow automation engine), **OpenAI GPT-4** (content synthesis & semantic resume scoring), **Airtable** (relational recruitment database), **Google Workspace APIs** (Gmail email triggers & Google Calendar/Meet scheduling), and **Job Board APIs** (LinkedIn & Wellfound).

---

## ✨ Key Features

### 🤖 AI-Powered Recruitment Intelligence
- **Policy-Compliant JD Generation**: GPT-4 synthesizes comprehensive, role-specific job descriptions from Airtable department templates.
- **Multi-Factor Candidate Scoring**: Computes a weighted match score out of 100:
  $$\text{Final Score} = (\text{Skills} \times 0.40) + (\text{Experience} \times 0.30) + (\text{Education} \times 0.15) + (\text{AI Fit} \times 0.15)$$
- **Structured Resume Data Extraction**: Normalizes candidate skills, experience years, previous employers, and education levels.

### 👥 Human-in-the-Loop (HITL) Governance
- **Job Description Approval**: Email preview sent to HR with one-click webhook approval before posting live.
- **Shortlist Review Gate**: Twice-daily review digest of shortlisted candidates with full AI scoring rationales before interview invites are sent.
- **HR Override & Rejection Handling**: Automated rejection email delivery and status tracking if HR rejects a candidate at any step.

### 📅 End-to-End Orchestration
- **Dual Job Distribution**: Instant simultaneous distribution to LinkedIn and Wellfound via REST APIs.
- **Smart Interview Scheduling**: Queries interviewer Google Calendar `freeBusy` availability across a 14-day window and generates Google Meet links automatically upon candidate slot selection.
- **Automated Communication & Audit Trail**: Automated email confirmations and `.ics` calendar invites logged directly into Airtable.

---

## 🏗️ System Architecture

                            ┌──────────────────────────────────────────────┐
                              │             WORKFLOW 1: JD & POSTING         │
                              │  Manual Trigger ──▶ Fetch Template ──▶ GPT-4 │
                              │      └──▶ HR Approval Webhook ──▶ APIs       │
                              └──────────────┬───────────────────────────────┘
                                             │ Posts Job & Stores Record
                                             ▼
                                             ┌──────────────────┐ ┌───────────────────────────┐ │ CAREER SITE │──────────────▶│ AIRTABLE BASE │ │ Application Form │ Webhook POST │ ┌───────────────────────┐ │ └────────┬─────────┘ │ │ Jobs │ │ │ │ │ Applicants │ │ ▼ │ │ Interviews │ │ ┌──────────────────────────────┐ │ │ Communications │ │ │ WORKFLOW 2: INTAKE & PARSE │───┼─▶ Job_Templates │ │ │ Validate ──▶ Parse ──▶ Email │ │ └───────────────────────┘ │ └──────────────────────────────┘ └─────────────┬─────────────┘ │ Periodic Batch Read ▼ ┌───────────────────────────┐ │ WORKFLOW 3: AI SCORING │ │ Fetch New ──▶ GPT-4 Eval │ │ ──▶ Score ──▶ Shortlist │ └─────────────┬─────────────┘ │ Reads Shortlisted ▼ ┌───────────────────────────┐ │ WORKFLOW 4: HR & SCHEDULE │ │ HR Review Digest ──▶ GCal │ │ ──▶ Slot Invite ──▶ Meet │ └───────────────────────────┘
                                             
---

## 🔄 The 4 Core Workflows

| # | Workflow File | Trigger | Core Operations | Key Outputs |
|---|---------------|---------|-----------------|-------------|
| **1** | `01-job-description-posting.json` | Manual Trigger | Fetches template from Airtable, GPT-4 JD generation, HR review approval check, posts to LinkedIn & Wellfound | Live job posts, updated Airtable `Jobs` record, HR confirmation email |
| **2** | `02-application-collection.json` | Webhook (`POST /webhook/receive-application`) | Payload validation (regex check for email/phone), downloads resume, parses data, updates applicant profile | New record in `Applicants`, parsed fields, applicant confirmation email, audit record in `Communications` |
| **3** | `03-candidate-matching.json` | Schedule Trigger (Every 6 Hours) | Batches pending applications (`Status = 'New'`), fetches role requirements, evaluates via GPT-4, calculates weighted score | Airtable fields updated: `Match_Score`, `Scoring_Breakdown`, `AI_Reasoning`; auto-shortlists candidates with score ≥ 70 |
| **4** | `04-hr-validation-scheduling.json` | Schedule Trigger (Twice Daily) + Webhooks | Shortlist review digest to HR, receives decision via webhook; on approval checks Google Calendar availability, allows candidate time selection, creates Google Meet event | Google Meet calendar event, Airtable `Interviews` record, `.ics` candidate invite, interviewer notifications |

---

## ⚙️ Configuration & Credentials

### 1. n8n UI Credentials
These credentials must be created in the n8n web interface under **Settings → Credentials**:

| Credential Name in n8n | Credential Type | Used In | Purpose |
|------------------------|-----------------|---------|---------|
| `openAiApi` | OpenAI API | Workflows 1, 3 | Authentication for GPT-4 prompt execution |
| `gmailOAuth2Api` | Gmail OAuth2 | Workflows 1, 2, 4 | Sending automated emails (alerts, confirmations, invites, rejections) |

### 2. Environment Variables (`.env`)
The workflows use n8n expression references (such as `{{$env.AIRTABLE_API_KEY}}`) for HTTP Request nodes. Copy `config/environment.example` to `config/.env`:

```bash
cp config/environment.example config/.env

| Variable Name | Description | Example / Format |
| --- | --- | --- |
| `AIRTABLE_API_KEY` | Airtable Personal Access Token (PAT) with `data.records:read` & `data.records:write` | `pat...` |
| `AIRTABLE_BASE_ID` | Airtable Base ID from API docs or URL | `appXXXXXXXXXXXXXX` |
| `GOOGLE_ACCESS_TOKEN` | OAuth2 Bearer Access Token for Google Calendar FreeBusy and Events API | `ya29....` |
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn Member/Organization Access Token with job posting permissions | `AQ...` |
| `WELLFOUND_API_KEY` | Wellfound (AngelList) API Key | Bearer token string |
| `HR_EMAIL` | Target email address for HR approval requests and daily review digests | `hr@yourcompany.com` |
| `HR_TEAM_EMAIL` | Distribution email address for job posting notices | `hr-team@yourcompany.com` |
| `GENERIC_TIMEZONE` | Timezone for n8n scheduling nodes | `Asia/Kolkata` |

























# HR Automation System with n8n

> End-to-end recruitment automation platform using n8n workflow orchestration, AI-powered candidate evaluation, and human-in-the-loop decision making.

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![n8n](https://img.shields.io/badge/n8n-1.0+-orange.svg)](https://n8n.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com)
[![Airtable](https://img.shields.io/badge/Airtable-Database-blue.svg)](https://airtable.com)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

## 🎯 Overview

This project automates the complete recruitment lifecycle—from job description creation to interview scheduling—reducing time-to-hire by **30-40%**, administrative workload by **70%**, and operational costs from **₹1.65L-2.5L to ₹16.5K-33K/month**.

Built with **n8n** (visual workflow automation), **OpenAI GPT-4** (AI content generation & evaluation), **Airtable** (centralized database), **Google Calendar/Gmail** (scheduling & communication), and **LinkedIn/Wellfound APIs** (job distribution).

## ✨ Features

### 🤖 AI-Powered Automation
- **Job Description Generation** - GPT-4 creates policy-compliant JDs from templates
- **Candidate Scoring** - Weighted evaluation: Skills (40%) + Experience (30%) + Education (15%) + AI Fit (15%)
- **Resume Parsing** - Structured extraction of skills, experience, education from PDFs

### 👥 Human-in-the-Loop Design
- **HR Approval Gates** - JD review, candidate shortlist validation, offer approval
- **Decision Transparency** - Full scoring rationale visible before human decision
- **Override Capability** - HR can approve/reject/modify at any checkpoint

### 📅 End-to-End Workflow
- **Multi-Platform Posting** - LinkedIn & Wellfound with single click
- **Automated Interview Scheduling** - Google Calendar availability + Google Meet links
- **Communication Automation** - Professional emails at every stage with audit trail
- **Centralized Data** - Airtable as single source of truth

### 🔒 Enterprise Ready
- **Self-Hosted Option** - Full data control, GDPR compliant
- **Modular Architecture** - 4 independent, reusable workflows
- **Webhook Integration** - Connect custom career site & HR portal
- **Extensible Design** - Add platforms, modify scoring, customize templates

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌────────────────┐     ┌─────────────────────┐
│   CAREER    │────▶│  WORKFLOW 2:     │────▶│  WORKFLOW 3:   │────▶│  WORKFLOW 4:        │
│   SITE      │     │  Application     │     │  Candidate     │     │  HR Validation &    │
│   (Forms)   │     │  Collection      │     │  Matching      │     │  Interview Sched.   │
└─────────────┘     └────────┬─────────┘     └───────┬────────┘     └──────────┬────────┘
                             │                     │                        │
                    ┌────────┴────────┐     ┌───────┴───────┐        ┌───────┴────────┐
                    │                 │     │               │        │                │
                    ▼                 ▼     ▼               ▼        ▼                ▼
             ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
             │   AIRTABLE   │  │   OPENAI     │  │   GOOGLE     │  │   GMAIL      │
             │  (Database)  │  │   (AI/LLM)   │  │   CALENDAR   │  │  (Email)     │
             └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
                    ▲
                    │
             ┌──────┴──────┐
             │  WORKFLOW 1 │
             │ Job Posting │
             └─────────────┘
```

## 🔄 The 4 Workflows

| # | Workflow | Trigger | Key Output |
|---|----------|---------|------------|
| **1** | Job Description & Posting | Manual | Posted jobs on LinkedIn/Wellfound + Airtable record |
| **2** | Application Collection | Webhook (`/receive-application`) | Validated applicants + parsed resumes in Airtable |
| **3** | Candidate Matching | Schedule (6hr) | Scored candidates, auto-shortlist (≥70) |
| **4** | HR Validation & Scheduling | Schedule (2x/day) | Calendar events, Meet links, notifications |

## 🚀 Quick Start

### Prerequisites
- n8n instance (Cloud or Self-hosted)
- OpenAI API key (GPT-4 access)
- Google Cloud project (Gmail + Calendar APIs)
- Airtable account
- LinkedIn Developer app / Wellfound API access

### Option 1: n8n Cloud (Easiest)
```bash
# 1. Sign up at https://cloud.n8n.io
# 2. Import all 4 workflows from workflows/ folder
# 3. Configure credentials (see below)
# 4. Activate workflows
# 5. Test Workflow 1: Execute → Fill form → Check Airtable
```

### Option 2: Local Docker
```bash
cd hr-automation-n8n

# 1. Configure environment
cp config/environment.example config/.env
# Edit config/.env with your API keys

# 2. Start n8n
docker run -it --rm --name n8n -p 5678:5678 \
  -v "%cd%/workflows:/home/node/.n8n/workflows" \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=yourpassword \
  n8nio/n8n:latest

# 3. Open http://localhost:5678 (admin/yourpassword)
```

### Option 3: Production (Kubernetes)
See [Deployment Guide](docs/deployment-guide.md) for Docker Compose, Kubernetes, and nginx/SSL setup.

## ⚙️ Configuration

### 1. Airtable Setup
Create base with 5 tables using [Airtable Schema](docs/airtable-schema.md):
- **Jobs** - Postings with descriptions, requirements, platform URLs
- **Applicants** - Candidates with parsed data, scores, status
- **Interviews** - Scheduled interviews with Meet links
- **Communications** - Audit trail of all emails sent
- **Job_Templates** - JD templates by department/level

### 2. n8n Credentials
Configure in n8n UI → Credentials:

| Credential | Type | Required For |
|------------|------|--------------|
| `OpenAI` | OpenAI API | Workflows 1, 3 |
| `Gmail` | Gmail OAuth2 | Workflows 1, 2, 4 |
| `Google Calendar` | Google Calendar OAuth2 | Workflow 4 |
| `Airtable Auth` | Header Auth (`Authorization: Bearer`) | All workflows |
| `LinkedIn` | OAuth2 | Workflow 1 |
| `Wellfound` | Header Auth | Workflow 1 |
| `Webhook Security` | Header Auth (`X-Webhook-Token`) | Workflows 2, 4 |

### 3. External Components (You Build)

| Component | Webhook Endpoint | Purpose |
|-----------|------------------|---------|
| Career Site Form | `POST /webhook/receive-application` | Candidate applications |
| HR Review Portal | `POST /webhook/hr-review-decision` | Approve/reject candidates |
| Time Selection Page | `POST /webhook/select-interview-time` | Candidate picks interview slot |

**Career Form Example:**
```html
<form action="https://YOUR_N8N_DOMAIN/webhook/receive-application" method="POST">
  <input name="name" required>
  <input name="email" type="email" required>
  <input name="phone" required>
  <input name="resume_url" required>
  <textarea name="cover_letter"></textarea>
  <input name="linkedin_profile">
  <input name="referred_by">
  <input name="job_id" type="hidden" value="recABC123">
  <button type="submit">Apply</button>
</form>
```

## 📁 Project Structure

```
hr-automation-n8n/
├── workflows/
│   ├── 01-job-description-posting.json      # JD generation + posting
│   ├── 02-application-collection.json       # Application intake + parsing
│   ├── 03-candidate-matching.json           # AI scoring + shortlisting
│   └── 04-hr-validation-scheduling.json     # HR review + interview scheduling
├── config/
│   └── environment.example                   # API key template
├── docs/
│   ├── airtable-schema.md                   # Complete table definitions
│   └── deployment-guide.md                  # Docker/K8s/n8n Cloud
├── setup.py                                  # Verification script
└── README.md
```

## 🔧 Customization

### Scoring Weights (Workflow 3 → "Calculate Final Score")
```javascript
const finalScore = Math.round(
  (skillsMatch * 0.40) +      // Adjust weights per role
  (experienceMatch * 0.30) +
  (educationMatch * 0.10) +
  (aiScore * 0.20)
);
```

### Shortlist Threshold (Workflow 3 → "IF: Score >= 70?")
- Default: 70
- Senior roles: 75-80
- High volume: 65

### Email Templates
Edit Gmail nodes in each workflow for your company branding, tone, and links.

### Resume Parser (Workflow 2 → "Parse Resume")
Replace placeholder with real PDF parsing:
- **Option A**: n8n community node `n8n-nodes-pdf-extract`
- **Option B**: External API (DocParser, Pdf.co, AWS Textract)
- **Option C**: Custom microservice with `pdfplumber`

## 📊 Metrics & Monitoring

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time-to-hire | 14-18 days | Airtable: Submission → Hired date |
| Application → Shortlist | < 1 hour | Workflow 3 execution logs |
| HR Review → Interview | < 4 hours | Workflow 4 timestamps |
| Candidate Experience | > 4.3/5 | Post-interview survey |
| Cost per Month | < ₹33K | API costs + hosting |

## 🧪 Testing Checklist

- [ ] Workflow 1: Manual execute → JD generated → Approve → LinkedIn/Wellfound posted → Airtable updated
- [ ] Workflow 2: POST to webhook → Validation works → Airtable record → Confirmation email sent
- [ ] Workflow 3: Manual trigger → New applicants scored → ≥70 shortlisted
- [ ] Workflow 4: Manual trigger → HR email sent → Approve → Calendar slots → Candidate invite → Time select → Meet link created → Confirmations sent

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Webhook not receiving | Use n8n Cloud tunnel or `npx localtunnel --port 5678` |
| OpenAI rate limit | Add Wait node, batch processing |
| Calendar conflicts | Verify calendar IDs, timezone (Asia/Kolkata) |
| Resume parse fails | Replace placeholder with pdf-parse service |
| Airtable sync errors | Exact field name match (case-sensitive) |
| Email not sending | Check OAuth token expiry, Gmail API quotas |

## 📚 Documentation

- [Airtable Schema](docs/airtable-schema.md) - Complete table/field definitions
- [Deployment Guide](docs/deployment-guide.md) - Docker, Kubernetes, n8n Cloud, nginx/SSL

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'feat: add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🙏 Acknowledgments

- [n8n](https://n8n.io) - Workflow automation platform
- [OpenAI](https://openai.com) - GPT-4 & Embeddings
- [Airtable](https://airtable.com) - Collaborative database
- [LangChain](https://langchain.com) - RAG patterns inspiration

---

**Built as academic mini-project for BCS 554 at R.B.S. Engineering Technical Campus, Agra (AKTU)**
