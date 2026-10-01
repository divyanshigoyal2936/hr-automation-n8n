# Deployment Guide

## Option 1: n8n Cloud (Easiest)
1. Sign up at https://cloud.n8n.io
2. Import workflows via Workflows → Import
3. Add credentials in n8n Cloud
4. Activate workflows

## Option 2: Self-Hosted with Docker

### Quick Start
```bash
cd hr-automation-n8n
docker-compose up -d
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - WEBHOOK_URL=https://your-domain.com/
      - GENERIC_TIMEZONE=Asia/Kolkata
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  n8n_data:
  postgres_data:
```

### Environment File (.env)
```bash
N8N_PASSWORD=your_secure_password
DB_PASSWORD=your_db_password
```

### With Reverse Proxy (nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5678;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

## Option 3: Kubernetes (Production)

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: n8n
spec:
  replicas: 2
  selector:
    matchLabels:
      app: n8n
  template:
    metadata:
      labels:
        app: n8n
    spec:
      containers:
      - name: n8n
        image: n8nio/n8n:latest
        ports:
        - containerPort: 5678
        env:
        - name: N8N_HOST
          value: "0.0.0.0"
        - name: N8N_PORT
          value: "5678"
        - name: N8N_PROTOCOL
          value: "https"
        - name: N8N_BASIC_AUTH_ACTIVE
          value: "true"
        - name: N8N_BASIC_AUTH_USER
          valueFrom:
            secretKeyRef:
              name: n8n-secrets
              key: basic-auth-user
        - name: N8N_BASIC_AUTH_PASSWORD
          valueFrom:
            secretKeyRef:
              name: n8n-secrets
              key: basic-auth-password
        - name: WEBHOOK_URL
          value: "https://n8n.your-domain.com/"
        - name: DB_TYPE
          value: "postgresdb"
        - name: DB_POSTGRESDB_HOST
          value: "postgres"
        - name: DB_POSTGRESDB_PORT
          value: "5432"
        - name: DB_POSTGRESDB_DATABASE
          value: "n8n"
        - name: DB_POSTGRESDB_USER
          valueFrom:
            secretKeyRef:
              name: n8n-secrets
              key: db-user
        - name: DB_POSTGRESDB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: n8n-secrets
              key: db-password
        volumeMounts:
        - name: n8n-data
          mountPath: /home/node/.n8n
      volumes:
      - name: n8n-data
        persistentVolumeClaim:
          claimName: n8n-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: n8n
spec:
  selector:
    app: n8n
  ports:
  - port: 5678
    targetPort: 5678
```

## Credentials Setup in n8n

### 1. OpenAI API
- Type: OpenAI API
- API Key: `sk-...`

### 2. Gmail OAuth2
- Type: Gmail OAuth2 API
- Client ID: From Google Cloud Console
- Client Secret: From Google Cloud Console
- Scopes: `https://www.googleapis.com/auth/gmail.send`, `https://www.googleapis.com/auth/gmail.compose`

### 3. Google Calendar OAuth2
- Type: Google Calendar OAuth2 API
- Same credentials as Gmail
- Scopes: `https://www.googleapis.com/auth/calendar`, `https://www.googleapis.com/auth/calendar.events`

### 4. Airtable
- Type: Header Auth
- Name: Authorization
- Value: `Bearer YOUR_API_KEY`

### 5. LinkedIn OAuth2
- Type: OAuth2 API
- Auth URL: `https://www.linkedin.com/oauth/v2/authorization`
- Token URL: `https://www.linkedin.com/oauth/v2/accessToken`
- Client ID/Secret: From LinkedIn Developer Portal
- Scopes: `w_member_social`, `r_organization_social`

### 6. Webhook Security
- Type: Header Auth
- Name: X-Webhook-Token
- Value: Your secure random token

## Testing Checklist

### Workflow 1: Job Posting
- [ ] Manual trigger executes
- [ ] Template fetched from Airtable
- [ ] OpenAI generates description
- [ ] Approval email sent to HR
- [ ] Webhook receives approval
- [ ] Job stored in Airtable
- [ ] Posted to LinkedIn
- [ ] Posted to Wellfound
- [ ] URLs updated in Airtable
- [ ] Confirmation email sent

### Workflow 2: Application Collection
- [ ] Webhook receives POST
- [ ] Validation catches missing fields
- [ ] Error email sent for invalid
- [ ] Valid app stored in Airtable
- [ ] Resume downloaded
- [ ] Resume parsed (mock)
- [ ] Parsed data updated in Airtable
- [ ] Confirmation email sent
- [ ] Communication logged

### Workflow 3: Candidate Matching
- [ ] Schedule triggers every 6h
- [ ] New applications fetched
- [ ] Job details fetched per candidate
- [ ] OpenAI evaluates each candidate
- [ ] Score calculated with weights
- [ ] Score saved to Airtable
- [ ] Candidates ≥70 shortlisted

### Workflow 4: HR Validation & Scheduling
- [ ] Schedule triggers twice daily
- [ ] Shortlisted candidates fetched
- [ ] HR review email sent
- [ ] Webhook receives decision
- [ ] Decision recorded
- [ ] If approve: calendar slots found
- [ ] Time slots ranked
- [ ] Invitation sent to candidate
- [ ] Webhook receives time selection
- [ ] Calendar event created
- [ ] Interview recorded in Airtable
- [ ] Confirmation sent to candidate
- [ ] Interviewers notified
- [ ] If reject: rejection email sent
- [ ] Status updated to Rejected

## Monitoring & Maintenance

### Daily
- Check n8n executions for failures
- Verify Airtable sync
- Monitor email deliverability

### Weekly
- Review shortlist quality
- Check API rate limits
- Update job templates

### Monthly
- Rotate API keys
- Review scoring accuracy
- Analyze time-to-hire metrics
- Backup Airtable data

## Troubleshooting

### Webhook not receiving
- Check n8n tunnel/external URL
- Verify webhook path matches
- Check firewall/security groups

### OpenAI rate limits
- Add delay between requests
- Implement exponential backoff
- Consider batching

### Google Calendar conflicts
- Verify calendar IDs
- Check timezone settings
- Ensure calendar sharing permissions

### Airtable sync issues
- Verify API key permissions
- Check base ID
- Validate field names match exactly

### Email not sending
- Check Gmail OAuth2 token expiry
- Verify sender email verified
- Check spam folder
- Review Gmail API quotas