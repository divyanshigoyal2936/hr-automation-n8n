# Airtable Schema Reference

## Tables Overview

### 1. Jobs
| Field Name | Type | Options |
|------------|------|---------|
| Job_Title | Single line text | Required |
| Department | Single select | Engineering, Marketing, Sales, HR, Finance, Operations |
| Experience_Level | Single select | Entry (0-2), Junior (2-4), Mid (4-7), Senior (7-10), Lead (10+) |
| Description | Long text | Rich text enabled |
| Required_Skills | Long text | Comma-separated |
| Status | Single select | Draft, Active, Posted, Closed |
| Posted_Date | Date time | ISO format |
| LinkedIn_URL | URL | |
| Wellfound_URL | URL | |
| LinkedIn_Job_ID | Single line text | |
| Wellfound_Job_ID | Single line text | |

### 2. Applicants
| Field Name | Type | Options |
|------------|------|---------|
| Name | Single line text | Required |
| Email | Email | Required |
| Phone | Phone number | |
| Resume_URL | URL | Required |
| Cover_Letter | Long text | |
| LinkedIn_Profile | URL | |
| Referred_By | Single line text | |
| Job_ID | Link to Jobs | Required |
| Status | Single select | New, Evaluated, Shortlisted, Rejected, Hired |
| Submission_Date | Date time | Auto: CREATED_TIME() |
| Parsed_Skills | Long text | Comma-separated |
| Years_Experience | Number | Integer |
| Education_Level | Single select | High School, Bachelor's, Master's, PhD, Other |
| Previous_Companies | Long text | Comma-separated |
| Match_Score | Number | 0-100 |
| Scoring_Breakdown | Long text | JSON string |
| AI_Reasoning | Long text | |
| Evaluation_Date | Date time | |
| HR_Reviewed | Checkbox | Default: false |
| HR_Decision | Single select | approve, reject |
| Review_Date | Date time | |
| Reviewer | Single line text | |
| Shortlist_Date | Date time | |

### 3. Interviews
| Field Name | Type | Options |
|------------|------|---------|
| Candidate_ID | Link to Applicants | Required |
| Job_ID | Link to Jobs | Required |
| Date_Time | Date time | Required |
| Interviewers | Long text | Comma-separated emails |
| Meeting_Link | URL | Google Meet link |
| Status | Single select | Scheduled, Completed, Cancelled, Rescheduled |

### 4. Communications
| Field Name | Type | Options |
|------------|------|---------|
| Candidate_ID | Link to Applicants | Required |
| Email_Type | Single select | Application_Confirmation, Interview_Invitation, Interview_Confirmation, Rejection, Offer, Onboarding |
| Sent_Date | Date time | Auto: CREATED_TIME() |
| Template_Used | Single line text | |
| Recipient | Email | |
| Subject | Single line text | |
| Status | Single select | Sent, Failed, Bounced |

### 5. Job_Templates
| Field Name | Type | Options |
|------------|------|---------|
| Department | Single select | Same as Jobs.Department |
| Experience_Level | Single select | Same as Jobs.Experience_Level |
| Template_Content | Long text | Rich text with placeholders |

## Sample Template Content

```
# {{JOB_TITLE}} - {{DEPARTMENT}}

## About Us
[Company description, mission, values]

## Role Overview
We are seeking a {{EXPERIENCE_LEVEL}} {{JOB_TITLE}} to join our {{DEPARTMENT}} team...

## Key Responsibilities
{{KEY_RESPONSIBILITIES}}

## Required Qualifications
- {{REQUIRED_SKILLS}}
- {{EXPERIENCE_LEVEL}} years of experience
- {{EDUCATION_REQUIREMENTS}}

## Preferred Qualifications
- [Nice-to-have skills]
- [Certifications]
- [Domain experience]

## What We Offer
- Competitive salary: {{SALARY_RANGE}}
- Health, dental, vision insurance
- 401(k) matching
- Flexible PTO
- Remote/hybrid options
- Professional development budget

## Our Culture
[Culture description, team dynamics, work style]

## Equal Opportunity Statement
[Standard EEO statement]
```

## Airtable Views for HR

### Jobs Table Views
- **Active Postings**: Filter Status = "Active" or "Posted"
- **By Department**: Group by Department
- **Pipeline**: Kanban by Status

### Applicants Table Views
- **New Applications**: Filter Status = "New"
- **Awaiting Evaluation**: Filter Status = "New"
- **Evaluated**: Filter Status = "Evaluated"
- **Shortlisted**: Filter Status = "Shortlisted" AND HR_Reviewed = false
- **HR Review Queue**: Filter Status = "Shortlisted" AND HR_Reviewed = false, Sort by Match_Score desc
- **Rejected**: Filter Status = "Rejected"
- **Hired**: Filter Status = "Hired"
- **By Job**: Group by Job_ID
- **Scorecard**: Grid with Name, Job_Title, Match_Score, Status, HR_Decision

### Interviews Table Views
- **Upcoming**: Filter Date_Time > NOW(), Sort by Date_Time
- **This Week**: Filter Date_Time within next 7 days
- **By Candidate**: Group by Candidate_ID
- **Calendar**: Calendar view by Date_Time

### Communications Table Views
- **By Candidate**: Group by Candidate_ID
- **By Type**: Group by Email_Type
- **Recent**: Sort by Sent_Date desc, limit 50

## API Field Names (for n8n)

Use exact field names as shown above in n8n HTTP Request nodes.
Airtable API uses field names as keys in the `fields` object.

Example:
```json
{
  "fields": {
    "Job_Title": "Senior Software Engineer",
    "Department": "Engineering",
    "Status": "Active"
  }
}
```

For linked records (Job_ID, Candidate_ID), use array of record IDs:
```json
{
  "fields": {
    "Job_ID": ["recABC123"]
  }
}
```

## Setup Checklist

- [ ] Create Airtable base
- [ ] Create all 5 tables with fields above
- [ ] Create views for HR team
- [ ] Add sample job templates
- [ ] Generate API key: https://airtable.com/create/tokens
- [ ] Get Base ID from API documentation
- [ ] Test API access with curl
- [ ] Configure n8n Airtable credentials