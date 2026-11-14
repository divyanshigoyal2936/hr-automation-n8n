
# HR Automation System with n8n

> Recruitment automation prototype using n8n workflow orchestration, GPT-4 powered content generation and candidate evaluation, and human-in-the-loop decision making.

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![n8n](https://img.shields.io/badge/n8n-1.0+-orange.svg)](https://n8n.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com)
[![Airtable](https://img.shields.io/badge/Airtable-Database-blue.svg)](https://airtable.com)
[![Status](https://img.shields.io/badge/Status-Prototype-yellow.svg)]()

## 🎯 Overview

This project automates most of the recruitment lifecycle, from job description creation to interview scheduling. It is built as four independent n8n workflows that share data through Airtable.

**Projected benefits (design estimates, not yet measured in a live deployment):** faster time-to-hire (est. 30-40%), lower administrative workload (est. 70%), and lower monthly operating cost (est. ₹16.5K-33K vs ₹1.65L-2.5L for a traditional process). These figures should be validated with real usage data before being quoted as results.

Built with **n8n** (visual workflow automation), **OpenAI GPT-4** (via API, pretrained, no custom model training), **Airtable** (centralized database), **Google Calendar/Gmail** (scheduling & communication), and **LinkedIn/Wellfound APIs** (job distribution, subject to API access, see Known Limitations).

## ✨ Features

### 🤖 AI-Powered Automation
- **Job Description Generation** - GPT-4 drafts JDs from Airtable templates and job parameters (temperature 0.7). Company hiring policies can be added to the prompt, where a placeholder currently exists.
- **Candidate Scoring** - GPT-4 returns skills, experience, education and overall scores as JSON (temperature 0.3). A JavaScript node then computes the weighted final score: Skills (40%) + Experience (30%) + Education (15%) + AI Fit (15%)
- **Resume Parsing** - *Placeholder only.* The "Parse Resume Text" node currently returns an empty structure. Real PDF extraction must be integrated (see Customization).

### 👥 Human-in-the-Loop Design
- **HR Approval Gates** - JD review (Workflow 1) and candidate shortlist review (Workflow 4) are implemented. Offer approval is *planned, not implemented*.
- **Decision Transparency** - The HR review email includes each candidate's score, skills, experience, education and AI reasoning
- **HR Decision** - HR can approve or reject shortlisted candidates. Editing or modifying a candidate or JD at a checkpoint is not built in.

### 📅 End-to-End Workflow
- **Multi-Platform Posting** - LinkedIn & Wellfound posting from one workflow run (requires valid API access)
- **Interview Scheduling** - Calendar invitation flow with Google Meet link creation. Currently, the suggested slots are the next 3 weekday business-hour slots; the Google Calendar free/busy result is fetched but not yet used to rank slots.
- **Communication Automation** - Emails at key stages (application confirmation, HR review, interview invitation/confirmation, rejection). Application confirmations are logged to the Communications table; logging for the other email types is not yet implemented.
- **Centralized Data** - Airtable as single source of truth

### 🔒 Enterprise-Oriented Design
- **Self-Hosted Option** - Run n8n on your own infrastructure for greater data control (compliance such as GDPR still depends on your hosting, configuration and policies)
- **Modular Architecture** - 4 independent workflows that communicate through Airtable status fields
- **Webhook Integration** - Connect a custom career site & HR portal
- **Extensible Design** - Add platforms, modify scoring, customize templates

## 🏗️ Architecture

The workflows do not call each other directly. Each one reads and writes **Airtable**, and the `Status` field of the Applicants table passes work from one workflow to the next.

```
                         ┌───────────────────────────────┐
                         │          AIRTABLE             │
                         │  Jobs · Applicants · Interviews│
                         │  Communications · Job_Templates│
                         └───▲─────▲──────▲──────▲───────┘
                             │     │      │      │
   HR (manual run)           │     │      │      │
 ┌──────────────┐   ┌────────┴───┐ │ ┌────┴─────┐│ ┌───────────────────┐
 │ WORKFLOW 1   │───┘            │ │ │WORKFLOW 3││ │ WORKFLOW 4        │
 │ JD + Posting │  OpenAI,Gmail, │ │ │ Matching ││ │ HR Validation &   │
 │              │  LinkedIn,     │ │ │ (6 hrs)  ││ │ Scheduling        │
 └──────────────┘  Wellfound     │ │ └────┬─────┘│ │ (2x/day)          │
                                 │ │      │      │ └───────┬───────────┘
 Career site form                │ │   OpenAI    │      Gmail, Google
 ┌──────────────┐   ┌────────────┴─┴┐             │      Calendar
 │ CANDIDATE    │──▶│ WORKFLOW 2    │─────────────┘
 │ (you build)  │   │ Application   │  status: New → Evaluated/Shortlisted
 └──────────────┘   │ Collection    │          → Rejected / Interview scheduled
                    └───────────────┘
```

## 🔄 The 4 Workflows

| # | Workflow | Trigger | Key Output |
|---|----------|---------|------------|
| **1** | Job Description & Posting | Manual (approval link uses webhook `/approve-job-description`) | JD record in Airtable, LinkedIn/Wellfound posting attempts |
| **2** | Application Collection | Webhook (`/receive-application`) | Validated applicants stored in Airtable, confirmation email (parsed resume data is placeholder) |
| **3** | Candidate Matching | Schedule (6hr) | Scored candidates, auto-shortlist (≥70) |
| **4** | HR Validation & Scheduling | Schedule (2x/day) + webhooks (`/hr-review-decision`, `/select-interview-time`) | HR decisions, calendar events, Meet links, notifications |

All four workflows are exported with `active: false`. Import them and activate each one after configuring credentials.

## 🚀 Quick Start

### Prerequisites
- n8n instance (Cloud or Self-hosted)
- OpenAI API key (GPT-4 access)
- Google Cloud project (Gmail + Calendar APIs)
- Airtable account
- LinkedIn Developer app / Wellfound API access (job-posting APIs are restricted. Confirm availability before relying on Workflow 1 posting, or replace those nodes with manual posting.)

### Option 1: n8n Cloud (Easiest)
```bash
# 1. Sign up at https://n8n.io (n8n Cloud)
# 2. Import all 4 workflows from workflows/ folder
#    (Workflows -> Import from File)
# 3. Configure credentials (see below)
# 4. Activate workflows
# 5. Test Workflow 1: Execute workflow -> check Airtable Jobs table
```

### Option 2: Local Docker
```bash
cd hr-automation-n8n

# 1. Configure environment
cp config/environment.example config/.env
# Edit config/.env with your own API keys (never commit this file)

# 2. Start n8n (Linux/macOS/Git Bash; on Windows PowerShell use ${PWD} instead of $(pwd))
docker volume create n8n_data
docker run -it --rm --name n8n -p 5678:5678 \
  --env-file config/.env \
  -v n8n_data:/home/node/.n8n \
  -v "$(pwd)/workflows:/workflows" \
  n8nio/n8n:latest

# 3. Open http://localhost:5678 and create the owner account on first launch
# 4. Import workflows: UI -> Workflows -> Import from File (select files from workflows/)
```
Notes:
- `N8N_BASIC_AUTH_*` variables were removed in n8n 1.0. Current versions use the owner account created on first launch, so those variables in `environment.example` can be ignored on n8n 1.0+.
- The `n8n_data` volume keeps your credentials and workflows when the container restarts. Without it, `--rm` deletes everything.
- Mounting the `workflows` folder does not import workflows automatically. Import them from the UI (or with `n8n import:workflow` inside the container).
- The workflows read `{{$env.AIRTABLE_BASE_ID}}` inside nodes. If your n8n version blocks environment access in nodes, set `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`.

### Option 3: Production (Kubernetes)
See [Deployment Guide](docs/deployment-guide.md) for Docker Compose, Kubernetes, and nginx/SSL setup.

## ⚙️ Configuration

### 1. Airtable Setup
Create base with 5 tables using [Airtable Schema](docs/airtable-schema.md):
- **Jobs** - Postings with descriptions, requirements, platform URLs
- **Applicants** - Candidates with parsed data, scores, status
- **Interviews** - Scheduled interviews with Meet links
- **Communications** - Audit trail of application confirmation emails (other email types not logged yet)
- **Job_Templates** - JD templates by department/level

Schema gaps to fix before testing Workflow 3: the evaluation prompt reads `Resume_Text` and `Job_Title` from the candidate data, but the Applicants table in the schema has neither field. Add a long-text `Resume_Text` field, and make job data available to the prompt (for example a lookup field from Jobs, or merge the Job record with the Applicant record before the OpenAI node).

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
| `Webhook Security` | Header Auth (`X-Webhook-Token`), recommended on every webhook node | Workflows 1, 2, 4 |

### 3. External Components (You Build)

| Component | Webhook Endpoint | Purpose |
|-----------|------------------|---------|
| Career Site Form | `POST /webhook/receive-application` | Candidate applications |
| JD Approval Link/Page | `POST /webhook/approve-job-description` | HR approves a generated job description |
| HR Review Portal | `POST /webhook/hr-review-decision` | Approve/reject candidates |
| Time Selection Page | `POST /webhook/select-interview-time` | Candidate picks interview slot |

None of these pages exist in this repository yet. Only the example form below is provided.

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
│   ├── 02-application-collection.json       # Application intake + parsing (placeholder parser)
│   ├── 03-candidate-matching.json           # AI scoring + shortlisting
│   └── 04-hr-validation-scheduling.json     # HR review + interview scheduling
├── config/
│   └── environment.example                   # API key template
├── docs/
│   ├── airtable-schema.md                   # Complete table definitions
│   └── deployment-guide.md                  # Docker/K8s/n8n Cloud
├── setup.py                                  # Verification script (checks files exist, prints next steps)
└── README.md
```

## 🔧 Customization

### Scoring Weights (Workflow 3 → "Calculate Final Score")
This matches the weights currently in the workflow:
```javascript
const finalScore = Math.round(
  (requiredSkillsMatch * 0.40) +   // Adjust weights per role
  (experienceMatch * 0.30) +
  (educationMatch * 0.15) +
  (aiScore * 0.15)
);
```
Keep the four weights summing to 1.0.

### Shortlist Threshold (Workflow 3 → "IF: Score >= 70?")
- Default: 70
- Senior roles: 75-80
- High volume: 65

### Email Templates
Edit Gmail nodes in each workflow for your company branding, tone, and links.

### Resume Parser (Workflow 2 → "Parse Resume Text")
This node is currently a **placeholder** that returns empty skills, 0 years of experience and an empty education level. Replace it with real PDF parsing:
- **Option A**: n8n community node `n8n-nodes-pdf-extract`
- **Option B**: External API (DocParser, Pdf.co, AWS Textract)
- **Option C**: Custom microservice with `pdfplumber`

Until this is done, Workflow 3 scores candidates mostly from limited data, so results will not be reliable.

## 📊 Metrics & Monitoring

These are target values to track after deployment. They are not measured results.

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time-to-hire | 14-18 days | Airtable: Submission → Hired date |
| Application → Shortlist | < 1 hour | Workflow 3 execution logs (note: Workflow 3 runs every 6 hours, so this target needs a shorter schedule or a webhook trigger) |
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
| Resume parse returns empty data | Expected with the placeholder node. Integrate a real PDF parsing service |
| Airtable sync errors | Exact field name match (case-sensitive) |
| Email not sending | Check OAuth token expiry, Gmail API quotas |

### Known Limitations (Current Version)

1. **Resume parsing is a placeholder.** No skills, experience or education are extracted from resumes yet.
2. **Mid-flow webhooks.** In Workflows 1 and 4, a Webhook node is connected after an email node. In n8n, a Webhook node is a trigger that starts its own execution. It does not pause the previous run. For true "send email, wait for reply" behavior, use a Wait node (resume on webhook) or treat each webhook as a separate workflow entry point that looks up the record in Airtable.
3. **Data passing needs testing.** After the OpenAI node, later nodes read candidate fields such as `$json.fields.Name` and `$json.id`. In n8n, the OpenAI node output replaces the previous item data, so these may need to reference earlier nodes (for example `$('Node Name').item.json`). Verify with test data.
4. **Interview slot ranking is simplified.** It does not use the Google Calendar free/busy result.
5. **Job-board APIs.** LinkedIn's job-posting API is restricted to approved partners, and the Wellfound endpoint should be verified. Workflow 1 posting may need replacement or manual posting.
6. **Offer approval, onboarding and Hired-stage automation** appear in the schema but are not implemented in any workflow.
7. **No frontend is included.** Career form, HR portal and time selection pages must be built separately.

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

MIT License. Add a `LICENSE` file to the repository root so the badge link works.

## 👤 Author

**Divyanshi**
- GitHub: [@ydivyanshigoyal2936](https://github.com/divyanshigoyal2936)
- LinkedIn: [DivyanshiGoyal](https://linkedin.com/in/divya2936)
- Email: your.email@example.com

## 🙏 Acknowledgments

- [n8n](https://n8n.io) - Workflow automation platform
- [OpenAI](https://openai.com) - GPT-4 (chat completions API)
- [Airtable](https://airtable.com) - Collaborative database

---






























