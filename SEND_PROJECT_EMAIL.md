# 📧 How to Send Project Requirements to JARVIS

## Quick Answer

**Send your project requirements to:**

```
johnmwangi1729+jarvis@gmail.com
```

Or simply send to your regular email with `[JARVIS]` in the subject:

```
johnmwangi1729@gmail.com
Subject: [JARVIS] Your Project Name
```

---

## Email Template

Copy and paste this template:

```
To: johnmwangi1729+jarvis@gmail.com
Subject: [JARVIS] Build TaskMaster Pro

Hi JARVIS,

I need a new project built ASAP. Here are the requirements:

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

## What Happens Next?

1. **You send email** → `johnmwangi1729+jarvis@gmail.com`
2. **JARVIS receives** → Detects project requirements
3. **Extracts requirements** → Creates JSON spec
4. **Generates architecture** → ERD, API specs, diagrams
5. **Sends for review** → You approve or request changes
6. **Generates code** → Full application with tests
7. **Creates GitHub repo** → Pushes code and opens PR
8. **Sends completion** → Email with links and summary

---

## Email Format Requirements

### Required Fields

- **Project Name:** Clear, descriptive name
- **Stack:** Technologies to use (React, Node.js, etc.)
- **Features:** List of features to implement

### Optional Fields

- **Deadline:** When you need it
- **Budget:** If applicable
- **Additional Notes:** Any special requirements

### Example Formats

**Minimal:**
```
Project Name: Todo App
Stack: React, Node.js
Features:
- Add tasks
- Mark complete
- Delete tasks
```

**Detailed:**
```
Project Name: E-commerce Platform
Stack: Next.js, TypeScript, PostgreSQL, Stripe, Tailwind CSS
Deadline: 3 weeks
Budget: $5000

Core Features:
- User authentication (email/password, OAuth)
- Product catalog with search
- Shopping cart and checkout
- Payment processing (Stripe)
- Order management
- Admin dashboard

Technical Requirements:
- RESTful API with OpenAPI docs
- Responsive design (mobile-first)
- SEO optimized
- Unit and integration tests
- CI/CD pipeline

Additional Notes:
- Use TypeScript throughout
- Follow Airbnb style guide
- Include comprehensive documentation
```

---

## Testing the Setup

### 1. Send Test Email

Send yourself a test email:

**To:** johnmwangi1729+jarvis@gmail.com  
**Subject:** [JARVIS] Test Project  
**Body:**
```
Project Name: Test App
Stack: React
Features:
- Hello World component
```

### 2. Check Processing

```bash
# Check if JARVIS received it
python -m jarvis.hooks.email_monitor --once
```

### 3. View Results

Check these directories:
```
jarvis_output/
├── specs/           # Extracted requirements
├── architecture/    # Generated architecture
└── generated_code/  # Generated application
```

---

## Email Commands

After sending initial requirements, you can send follow-up commands:

- **"Approved"** - Approve architecture and start coding
- **"Pause"** - Pause current project
- **"Resume"** - Resume paused project
- **"Status"** - Get project status update
- **"Cancel"** - Cancel current project
- **"Changes: [description]"** - Request changes

---

## Gmail Alias Benefits

Using `johnmwangi1729+jarvis@gmail.com`:

✅ All emails go to your regular inbox  
✅ Easy to filter with Gmail rules  
✅ No new account needed  
✅ Can track JARVIS projects separately  

### Set Up Gmail Filter

1. Go to Gmail Settings → Filters
2. Create filter:
   - **To:** johnmwangi1729+jarvis@gmail.com
   - **Or has words:** [JARVIS]
3. Apply label: "JARVIS Projects"
4. Mark as important

---

## Monitoring Options

### Option 1: Manual Check (Current)

```bash
# Check inbox manually
python -m jarvis.hooks.email_monitor --once
```

### Option 2: Scheduled Check

```bash
# Check every 5 minutes
python -m jarvis.hooks.email_monitor --daemon --interval 300
```

### Option 3: Windows Task Scheduler

Create a scheduled task to check hourly:

```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "-m jarvis.hooks.email_monitor --once" -WorkingDirectory "C:\Users\john\Desktop\jarvis"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName "JARVIS Email Check" -Action $action -Trigger $trigger
```

---

## Example Projects to Try

### 1. Simple Todo App
```
To: johnmwangi1729+jarvis@gmail.com
Subject: [JARVIS] Todo App

Project Name: Simple Todo
Stack: React, Node.js, MongoDB
Features:
- Add/edit/delete tasks
- Mark as complete
- Filter by status
```

### 2. Weather Dashboard
```
To: johnmwangi1729+jarvis@gmail.com
Subject: [JARVIS] Weather Dashboard

Project Name: Weather Dashboard
Stack: React, OpenWeather API
Features:
- Current weather display
- 5-day forecast
- Search by city
- Charts and graphs
```

### 3. Blog Platform
```
To: johnmwangi1729+jarvis@gmail.com
Subject: [JARVIS] Blog Platform

Project Name: DevBlog
Stack: Next.js, TypeScript, PostgreSQL, Tailwind CSS
Features:
- Create/edit/delete posts
- Markdown support
- Comments system
- User authentication
- Admin dashboard
- SEO optimization
```

---

## Troubleshooting

### Email Not Processed

**Check:**
1. Subject contains `[JARVIS]` or "Project"
2. Email includes "Project Name:" and "Stack:"
3. Email is in inbox (not spam)

**Solution:**
```bash
# Check inbox manually
python -m jarvis.hooks.email_monitor --once
```

### No Response

**Check:**
1. Email monitor is running
2. Gmail credentials are valid
3. Check `jarvis_output/` for generated files

**Solution:**
```bash
# Run full demo to test
python demo_full_stack_automation.py
```

---

## Summary

**Your JARVIS Email:**
```
johnmwangi1729+jarvis@gmail.com
```

**Or with subject tag:**
```
To: johnmwangi1729@gmail.com
Subject: [JARVIS] Your Project
```

**Required in email:**
- Project Name
- Stack
- Features

**What you get:**
- Architecture documents
- Generated code
- GitHub repository
- Completion notification

---

**Send your first project email now!** 🚀

For detailed setup, see `EMAIL_SETUP_GUIDE.md`
