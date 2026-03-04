# Admin System Setup Guide

## Overview

The admin system allows authorized users to manage all aspects of the JobAlert AI platform including users, job feed sources, jobs, and resumes.

## Initial Setup

### 1. Set Admin Credentials

Add these environment variables to your `.env` file:

```bash
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=your-secure-password-here
```

**⚠️ Important:** Use a strong, unique password for the admin account.

### 2. Initialize Admin User

Run the initialization script to create the admin user and seed default RSS feeds:

```bash
cd backend
python scripts/init_admin.py
```

This script will:
- Create the admin user with the credentials from your `.env` file
- Set `is_admin=True` on the user account
- Give the admin user 999,999 credits (unlimited)
- Seed the database with 5 default RSS feed sources:
  - RemoteOK
  - We Work Remotely
  - Himalayas
  - Real Work From Anywhere
  - RSS App Custom Feed

### 3. Login as Admin

1. Go to the frontend login page: `http://localhost:3000/login`
2. Enter the admin email and password from your `.env` file
3. You'll see an "Admin" link in the sidebar after logging in

## Admin Features

### Dashboard

The admin dashboard shows overview statistics:
- Total users (+ new users this week)
- Total jobs (+ new jobs today)
- Total matches
- Total resumes (+ new resumes this week)
- Active feed sources

### User Management

**View All Users:**
- See all registered users with pagination
- Search by email or name
- Filter by admin status

**User Actions:**
- **Update Credits:** Manually adjust user credit balances
- **Toggle Admin:** Grant or revoke admin access
- **Toggle Active:** Activate or deactivate user accounts

### Feed Source Management ⭐

**The Key Feature - No Backend Restart Required!**

**View All Feeds:**
- See all RSS/XML feed sources
- View scraping statistics (total jobs, last scrape count, success/failure)
- Monitor last scrape time and errors

**Add New Feed:**
1. Click "+ Add Feed Source"
2. Choose feed type:
   - **RSS Feed** - Any RSS/XML job feed
   - **Greenhouse API** - Company-specific Greenhouse boards
   - **Lever API** - Company-specific Lever boards
3. Enter feed details:
   - Name (e.g., "RemoteOK", "Stripe Jobs")
   - URL (full RSS feed URL or company careers page)
   - Company Token (for Greenhouse/Lever only)
4. Click "Create Feed"

The feed will be automatically scraped on the next scheduled run (every 30 minutes by default).

**Edit Feed:**
- Click the pencil icon to update feed details
- Modify name, URL, feed type, or company token

**Toggle Active/Inactive:**
- Click the power icon to enable/disable a feed
- Inactive feeds are not scraped

**Delete Feed:**
- Click the trash icon to permanently remove a feed
- This cannot be undone

**Finding Company Tokens:**

For **Greenhouse**:
1. Visit the company's careers page
2. Look for URLs like: `https://boards.greenhouse.io/COMPANY_TOKEN/jobs/`
3. Extract the `COMPANY_TOKEN` part
4. Example: For Stripe, the token is `stripe`

For **Lever**:
1. Visit the company's careers page
2. Look for URLs like: `https://jobs.lever.co/COMPANY_NAME/`
3. Extract the `COMPANY_NAME` part
4. Example: For Netflix, the name is `netflix`

### Job Management

**View All Jobs:**
- See all ingested jobs with pagination
- Search by title or company
- Filter by source

**Job Actions:**
- **View Job:** Click external link icon to open job posting
- **Delete Job:** Remove job and all associated matches

### Resume Management

**View All Resumes:**
- See all generated resumes with pagination
- View user email, job details, ATS score
- Filter by user

**Resume Actions:**
- **View PDF:** Click file icon to download resume PDF

## How Feed Scraping Works

### Automatic Scraping

The system uses Celery Beat to automatically scrape all **active** feeds every 30 minutes:

1. Worker fetches all `FeedSource` documents where `is_active=True`
2. For each feed:
   - Calls appropriate parser based on `feed_type` (RSS, Greenhouse, Lever)
   - Saves jobs to database with fingerprint deduplication
   - Triggers matching engine for new jobs
   - Updates feed statistics (last_scraped_at, total_jobs_scraped, etc.)
3. If scraping fails, the error is logged to `last_scrape_error`

### Dynamic Feed Management

**No backend restart required!** When you add, edit, or toggle a feed in the admin panel:

1. Changes are saved directly to MongoDB
2. The next scheduled scrape (within 30 minutes) will automatically pick up the changes
3. New feeds are scraped immediately on the next cycle
4. Edited feeds use the new URL/token
5. Disabled feeds are skipped

### Feed Statistics

Each feed tracks:
- `total_jobs_scraped` - Lifetime total
- `last_scrape_job_count` - Jobs found in most recent scrape
- `last_scraped_at` - Timestamp of last scrape attempt
- `last_scrape_success` - Boolean indicating success/failure
- `last_scrape_error` - Error message if scrape failed

## API Endpoints

All admin endpoints require authentication with `is_admin=True`:

```
GET    /api/admin/dashboard          - Dashboard stats
GET    /api/admin/users              - List all users
GET    /api/admin/users/:id          - User details
PATCH  /api/admin/users/:id/credits  - Update credits
PATCH  /api/admin/users/:id/toggle-admin   - Toggle admin
PATCH  /api/admin/users/:id/toggle-active  - Toggle active

GET    /api/admin/feeds              - List all feeds
POST   /api/admin/feeds              - Create feed
PATCH  /api/admin/feeds/:id          - Update feed
PATCH  /api/admin/feeds/:id/toggle   - Toggle active
DELETE /api/admin/feeds/:id          - Delete feed

GET    /api/admin/jobs               - List all jobs
DELETE /api/admin/jobs/:id           - Delete job

GET    /api/admin/resumes            - List all resumes
```

## Security

### Admin Middleware

The backend uses `get_current_admin()` middleware that:
1. Verifies JWT token is valid
2. Checks `is_admin=True` on user account
3. Returns 403 Forbidden if not admin

### Frontend Protection

The frontend uses `admin` middleware on `/admin` routes that:
1. Checks `authStore.isAuthenticated`
2. Checks `authStore.user.is_admin`
3. Redirects to `/dashboard` if not admin

### Best Practices

1. **Strong Password:** Use a complex, unique password for admin accounts
2. **Limited Admin Users:** Only grant admin access to trusted team members
3. **Audit Logs:** Monitor admin actions (future enhancement)
4. **Environment Variables:** Never commit admin credentials to version control

## Troubleshooting

### Feed Not Scraping

1. Check feed is marked as `is_active=True`
2. View `last_scrape_error` for error messages
3. Verify URL is accessible and returns valid RSS/JSON
4. Check Celery worker logs for errors

### Admin Link Not Showing

1. Ensure user has `is_admin=True` in database
2. Refresh page or clear browser cache
3. Check console for auth errors

### Can't Access Admin Pages

1. Verify `ADMIN_EMAIL` and `ADMIN_PASSWORD` in `.env`
2. Run `python scripts/init_admin.py` again
3. Check MongoDB for user with `is_admin=True`

## Database Schema

### FeedSource Document

```python
{
    "name": "RemoteOK",
    "url": "https://remoteok.com/remote-dev-jobs.rss",
    "feed_type": "rss",  # or "greenhouse", "lever"
    "company_token": None,  # for Greenhouse/Lever only
    "is_active": True,
    "last_scraped_at": ISODate("2024-01-15T10:30:00Z"),
    "last_scrape_success": True,
    "last_scrape_error": None,
    "total_jobs_scraped": 1250,
    "last_scrape_job_count": 15,
    "created_at": ISODate("2024-01-01T00:00:00Z"),
    "updated_at": ISODate("2024-01-15T10:30:00Z"),
    "created_by": "admin_user_id"
}
```

### User Document (Admin Fields)

```python
{
    "email": "admin@example.com",
    "is_admin": True,
    "credits": 999999,
    # ... other user fields
}
```

## Future Enhancements

- [ ] Audit log for admin actions
- [ ] Bulk operations (activate/deactivate multiple feeds)
- [ ] Feed scraping schedule customization per feed
- [ ] Export data (users, jobs, resumes)
- [ ] System settings management
- [ ] Email template editor
- [ ] Analytics dashboard

## Support

For issues or questions:
1. Check logs: `backend/logs/` and browser console
2. Review database state using MongoDB Compass
3. Verify environment variables are set correctly
4. Check Celery worker and beat are running

---

**Remember:** The admin system gives you complete control over the platform. Handle admin credentials with care and only grant admin access to trusted users.
