# JARVIS Email Setup Guide

## 📧 How to Send Project Requirements to JARVIS

JARVIS can monitor your Gmail inbox for project requirement emails and automatically process them.

---

## Option 1: Use Your Existing Gmail (Recommended)

**Your JARVIS Email:** `johnmwangi1729@gmail.com`

### How It Works

1. **Send yourself an email** with project requirements
2. **JARVIS monitors** your inbox for keywords like "Project", "Requirements", "Build"
3. **Automatically extracts** requirements and starts the workflow

### Email Format

**To:** johnmwangi1729@gmail.com  
**Subject:** [JARVIS] New Project: [Project Name]  
**Body:**

```
Hi JARVIS,

I need a new project built. Here are the requirements:

Project Name: TaskMaster Pro
Stack: React, TypeScript, Node.js, PostgreSQL, Tailwind CSS
Deadline: 2 weeks

Features:
- User authentication (email/password)
- Task management (CRUD operations)
- Dashboard with analytics
- REST API with OpenAPI docs
- Real-time notifications
- Dark mode support

Please use best practices and include tests.

Thanks!
```

---

## Option 2: Create a Dedicated JARVIS Email

For better organization, create a dedicated email:

### Recommended Email Addresses

1. **jarvis@yourdomain.com** (if you have a domain)
2. **jarvis.assistant@gmail.com** (create new Gmail)
3. **yourname+jarvis@gmail.com** (Gmail alias)

### Setup Steps

1. **Create Gmail Account**
   - Go to https://accounts.google.com/signup
   - Create: `jarvis.assistant.yourname@gmail.com`

2. **Enable App Password**
   - Go to Google Account → Security
   - Enable 2-Step Verification
   - Generate App Password
   - Copy the 16-character password

3. **Update .env File**
   ```bash
   JARVIS_INBOX_EMAIL=jarvis.assistant.yourname@gmail.com
   JARVIS_INBOX_PASSWORD=your_app_password_here
   ```

---

## Option 3: Use Gmail Alias (Easiest)

Gmail supports aliases with the `+` symbol:

**Your Email:** johnmwangi1729@gmail.com  
**JARVIS Alias:** johnmwangi1729+jarvis@gmail.com

### Benefits
- No new account needed
- All emails go to your existing inbox
- Easy to filter with Gmail rules

### Setup Gmail Filter

1. Go to Gmail Settings → Filters and Blocked Addresses
2. Create new filter:
   - **To:** johnmwangi1729+jarvis@gmail.com
   - **Has the words:** JARVIS OR Project Requirements
3. Apply label: "JARVIS Projects"
4. Mark as important

---

## Current Configuration

Your `.env` file has:

```bash
NOTIFICATION_EMAIL=johnmwangi1729@gmail.com
NOTIFICATION_EMAIL_PASSWORD=vnoa yelb vppd dmtw
```

This is configured for **sending** notifications. For **receiving** project requests, add:

```bash
# JARVIS Inbox (for receiving project requirements)
JARVIS_INBOX_EMAIL=johnmwangi1729+jarvis@gmail.com
JARVIS_INBOX_PASSWORD=vnoa yelb vppd dmtw
JARVIS_INBOX_LABEL=JARVIS Projects
```

---

## Email Monitoring Setup

### 1. Install Gmail API Credentials

```bash
# Install Google Client Library
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Enable Gmail API

1. Go to https://console.cloud.google.com/
2. Create new project: "JARVIS Assistant"
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json`
6. Save to: `gmail_credentials.json`

### 3. Update .env

```bash
GMAIL_CREDENTIALS=gmail_credentials.json
```

### 4. Authenticate

```bash
python -m jarvis.skills.email_intake --authenticate
```

This will:
- Open browser for OAuth
- Grant JARVIS access to Gmail
- Save token for future use

---

## Automated Email Monitoring

### Option A: Manual Check

```bash
# Check inbox for new project emails
python jarvis_cli.py skill run email_intake --action poll
```

### Option B: Scheduled Monitoring (Recommended)

Create a scheduled task to check every hour:

**Windows Task Scheduler:**
```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "python" -Argument "jarvis_cli.py skill run email_intake --action poll" -WorkingDirectory "C:\Users\john\Desktop\jarvis"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName "JARVIS Email Monitor" -Action $action -Trigger $trigger
```

**Or use Python scheduler:**
```bash
python -m jarvis.hooks.email_monitor
```

### Option C: Real-time Monitoring

```bash
# Start email monitoring daemon
python -m jarvis.hooks.email_monitor --daemon
```

This will:
- Check inbox every 5 minutes
- Detect new project emails
- Automatically trigger workflow
- Send confirmation email

---

## Email Templates

### Template 1: Simple Project

```
Subject: [JARVIS] Build a Todo App

Hi JARVIS,

Project Name: Simple Todo App
Stack: React, Node.js, MongoDB
Deadline: 1 week

Features:
- Add/edit/delete tasks
- Mark as complete
- Filter by status

Thanks!
```

### Template 2: Complex Project

```
Subject: [JARVIS] E-commerce Platform

Hi JARVIS,

I need a full e-commerce platform built ASAP.

Project Name: ShopMaster
Stack: Next.js, TypeScript, PostgreSQL, Stripe, Tailwind CSS
Deadline: 3 weeks
Budget: $5000

Core Features:
- User authentication (email/password, OAuth)
- Product catalog with search and filters
- Shopping cart and checkout
- Payment processing (Stripe)
- Order management
- Admin dashboard
- Email notifications

Technical Requirements:
- RESTful API with OpenAPI docs
- Responsive design (mobile-first)
- SEO optimized
- Unit and integration tests
- CI/CD pipeline
- Docker deployment

Additional Notes:
- Use TypeScript throughout
- Follow Airbnb style guide
- Include comprehensive documentation
- Set up error tracking (Sentry)

Please generate architecture first and wait for approval before coding.

Thanks!
```

### Template 3: Quick Prototype

```
Subject: [JARVIS] Quick Prototype Needed

Hi JARVIS,

Need a quick prototype for a client meeting tomorrow.

Project: Weather Dashboard
Stack: React, OpenWeather API
Deadline: 24 hours

Features:
- Current weather display
- 5-day forecast
- Search by city
- Nice UI with charts

Keep it simple and clean!
```

---

## Workflow After Sending Email

1. **Email Sent** → JARVIS inbox
2. **JARVIS Detects** → New project email
3. **Extracts Requirements** → JSON spec created
4. **Sends Confirmation** → "Requirements received, starting work..."
5. **Generates Architecture** → Sends for review
6. **Awaits Approval** → Reply "Approved" to continue
7. **Generates Code** → Creates GitHub repo
8. **Sends Completion** → "Project ready for review"

---

## Email Commands

Send these commands to control JARVIS:

- **"Approved"** - Approve architecture and start coding
- **"Pause"** - Pause current project
- **"Resume"** - Resume paused project
- **"Status"** - Get project status update
- **"Cancel"** - Cancel current project
- **"Help"** - Get help and available commands

---

## Testing the Setup

### Test 1: Send Test Email

```bash
# Send yourself a test email
python -c "
from jarvis.skills.email_notifier import EmailNotifierSkill
skill = EmailNotifierSkill()
skill.execute(
    to='johnmwangi1729@gmail.com',
    subject='[JARVIS] Test Project',
    body='This is a test. Project Name: Test App, Stack: React'
)
"
```

### Test 2: Check Inbox

```bash
# Check if JARVIS can read the email
python jarvis_cli.py skill run email_intake --action poll
```

### Test 3: Parse Email

```bash
# Parse the test email
python demo_full_stack_automation.py
```

---

## Security Best Practices

1. **Use App Passwords** - Never use your main Gmail password
2. **Enable 2FA** - Protect your Google account
3. **Limit Permissions** - Only grant necessary Gmail scopes
4. **Rotate Passwords** - Change app passwords regularly
5. **Monitor Access** - Check Google account activity
6. **Use Aliases** - Keep JARVIS emails separate

---

## Troubleshooting

### Email Not Detected

**Check:**
- Subject line contains [JARVIS] or "Project"
- Email is in inbox (not spam)
- Gmail credentials are valid
- OAuth token hasn't expired

**Solution:**
```bash
python -m jarvis.skills.email_intake --authenticate
```

### Authentication Failed

**Check:**
- App password is correct (16 characters, no spaces)
- 2-Step Verification is enabled
- Gmail API is enabled in Google Cloud Console

**Solution:**
1. Generate new app password
2. Update .env file
3. Re-authenticate

### Emails Going to Spam

**Solution:**
1. Mark JARVIS emails as "Not Spam"
2. Add to contacts
3. Create Gmail filter to never send to spam

---

## Recommended Setup

For the best experience, I recommend:

1. **Use Gmail Alias:** `johnmwangi1729+jarvis@gmail.com`
2. **Create Gmail Filter:** Label as "JARVIS Projects"
3. **Set Up Monitoring:** Run email monitor daemon
4. **Test Workflow:** Send a test project email

---

## Quick Start

```bash
# 1. Update .env
echo "JARVIS_INBOX_EMAIL=johnmwangi1729+jarvis@gmail.com" >> .env
echo "JARVIS_INBOX_PASSWORD=vnoa yelb vppd dmtw" >> .env

# 2. Send test email to yourself
# Subject: [JARVIS] Test Project
# Body: Project Name: Test, Stack: React

# 3. Check inbox
python jarvis_cli.py skill run email_intake --action poll

# 4. Start monitoring
python -m jarvis.hooks.email_monitor --daemon
```

---

## Summary

**Your JARVIS Email Options:**

1. ✅ **johnmwangi1729@gmail.com** (current)
2. ✅ **johnmwangi1729+jarvis@gmail.com** (recommended alias)
3. ⭐ **Create dedicated Gmail** (best for production)

**Recommended:** Use the alias `johnmwangi1729+jarvis@gmail.com` for now, then create a dedicated email later if needed.

---

**Send your first project email to get started!** 📧
