# Security Policy

Netra processes traffic video, stores violation evidence, and exposes a web API. That makes security and privacy part of the design, not an afterthought. This document explains how to report a vulnerability and what security practices the project follows.

---

## Supported Versions

Netra is in early development. Only the latest code on the main branch receives security fixes.

| Version | Supported |
| --- | --- |
| `main` (latest) | Yes |
| Older commits and forks | No |

This table will be updated once tagged releases exist.

---

## Reporting a Vulnerability

**Please do not open a public issue for security problems.**

Report privately using one of these methods:

1. **GitHub private reporting:** use the "Report a vulnerability" button under the repository's **Security** tab (if enabled).
2. **Email:** `[bashutosh017@gmail.com]`

Please include:

- A clear description of the problem and its impact
- Steps to reproduce it (a short proof of concept is ideal)
- The affected file, endpoint, or component
- The version or commit you tested
- Any suggested fix, if you have one

Please do not include real personal data (faces, license plates, private footage) in your report. Use sample or synthetic material.

### What to expect

These are targets, not guarantees:

| Step | Target time |
| --- | --- |
| Acknowledge your report | Within 3 business days |
| Initial assessment | Within 7 days |
| Fix or mitigation plan | Within 30 days, depending on severity |
| Public disclosure | After a fix is available, coordinated with you |

You will be credited in the release notes if you wish.

### Safe harbor

If you act in good faith, avoid privacy violations, avoid damaging data or service availability, and give us reasonable time to fix the issue before disclosure, we will not pursue action against you for your research.

---

## Scope

**In scope**

- The FastAPI backend (`backend/`), including upload, alert, and WebSocket endpoints
- The database layer and queries
- The React dashboard (`frontend/`)
- Handling of uploaded videos, evidence files, and model files
- Default configuration shipped in this repository

**Out of scope**

- Vulnerabilities in third-party packages that are already publicly known and not made worse by Netra (report those upstream)
- Denial of service by sending extreme traffic volume to a self-hosted instance
- Social engineering or physical attacks
- Issues that require an already-compromised server or administrator account
- Detection accuracy problems (missed vehicles or false alerts). These are bugs, not security issues, unless they can be abused to bypass a security control.

---

## Security Considerations for Netra

### 1. File uploads

Uploaded videos are untrusted input.

- Accept only an allow-list of video formats, and check content, not just the file extension.
- Enforce a maximum file size.
- Never use the user's file name as the saved path. Generate a unique name to prevent path traversal (`../../`) and overwriting.
- Store uploads outside any publicly served folder.
- Process videos in a background worker so one large file cannot block the API.

### 2. Model files

PyTorch `.pt` weight files can contain executable code (they use Python's pickle format).

- Only load model files from sources you trust, such as official Ultralytics releases or models you trained yourself.
- Never load a model uploaded by a user.
- Keep model files in `models/` with write access limited to administrators.
- Record the source and checksum of each model you deploy.

### 3. API and WebSocket access

- Require authentication for upload, alert, and evidence endpoints before any real deployment.
- Authenticate WebSocket connections too, since live alerts can reveal sensitive events.
- Set CORS to your exact dashboard address. Do not use a wildcard in production.
- Add rate limits to upload and login-style endpoints.
- Validate every request body and query parameter with Pydantic.
- Return generic error messages. Do not expose stack traces, file paths, or SQL errors.

### 4. Database

- Use SQLAlchemy with parameterized queries. Never build SQL by joining user text into a string.
- Give the application its own database user with only the permissions it needs, not a superuser.
- Use database constraints, such as the severity check on the alerts table, as a second line of defense.
- Keep the database off the public internet.
- Back up regularly and test restoring.

### 5. Secrets and configuration

- Keep passwords, database URLs, and API keys in environment variables or a secrets manager.
- Never commit `.env` files. Add them to `.gitignore`.
- Use different credentials for development and production.
- Rotate any secret that was ever committed by mistake. Deleting the commit is not enough.

### 6. Evidence files and privacy

Traffic footage can contain faces, license plates, and location information, which are often legally protected personal data.

- Collect only what the project needs.
- Control who can view evidence snapshots and clips. Do not serve them from an open folder.
- Define a retention period and delete old footage and evidence automatically.
- Consider blurring faces and plates in stored evidence unless a violation specifically requires them.
- Log who accesses evidence.
- Check the data protection laws that apply where you deploy (for example, local privacy and surveillance rules) and get legal advice for real deployments.
- Do not commit real footage to the repository. Use public sample or synthetic videos for tests.

### 7. Frontend

- Never put secrets in frontend code. Anything shipped to the browser is public.
- Let React escape rendered text. Avoid injecting raw HTML from alert data.
- Serve the dashboard and API over HTTPS in production.

### 8. Dependencies

- Pin versions in `requirements.txt` and `package-lock.json`.
- Run `pip-audit` (Python) and `npm audit` (Node.js) regularly.
- Enable Dependabot or a similar tool to flag vulnerable packages.
- Review new dependencies before adding them.

### 9. Logging and monitoring

- Log authentication failures, rejected uploads, and unusual request patterns.
- Never write passwords, tokens, or full personal data to logs.
- Protect log files with the same care as the database.

---

## Pre-Deployment Checklist

- [ ] Authentication enabled on API and WebSocket
- [ ] HTTPS enabled
- [ ] CORS limited to the real dashboard address
- [ ] Upload type, content, and size validation in place
- [ ] Unique server-generated file names for uploads
- [ ] Only trusted model files loaded
- [ ] Database user has limited permissions
- [ ] No secrets in the repository or frontend code
- [ ] Evidence access restricted and retention period set
- [ ] `pip-audit` and `npm audit` show no unresolved serious issues
- [ ] Debug mode and auto-reload turned off
- [ ] Backups configured and tested
- [ ] Ultralytics license terms reviewed for commercial use

---

## Disclosure Policy

We follow coordinated disclosure. After a fix is released, we will publish a short advisory describing the issue, the affected versions, and the fix, and credit the reporter if they agree.

Thank you for helping keep Netra and the people who appear in its footage safe.