# Auto Project Bot

Every month this bot automatically:
1. Asks Claude to generate a trending web project with full code
2. Creates a new GitHub repo and pushes the code
3. Deploys it (GitHub Pages for static / Vercel for others)
4. Posts about it on LinkedIn

---

## Setup (one time only)

### 1. Fork / clone this repo to your GitHub

### 2. Add these GitHub Secrets
Go to your repo → Settings → Secrets and variables → Actions → New repository secret

| Secret Name | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com |
| `BOT_GITHUB_TOKEN` | GitHub → Settings → Developer Settings → Personal Access Tokens (Classic) — give `repo` and `workflow` scope |
| `GITHUB_USERNAME` | Your GitHub username |
| `LINKEDIN_ACCESS_TOKEN` | See LinkedIn setup below |
| `LINKEDIN_PERSON_URN` | Your LinkedIn person URN (see below) |
| `VERCEL_TOKEN` | (optional) https://vercel.com/account/tokens |

### 3. LinkedIn Setup

LinkedIn API requires a developer app:

1. Go to https://www.linkedin.com/developers/apps and create an app
2. Request access to **Share on LinkedIn** and **Sign In with LinkedIn**
3. Get your access token (valid for 60 days — you need to refresh it manually)
4. Get your Person URN:
   - Call: `GET https://api.linkedin.com/v2/me` with your token
   - Copy the `id` field — that is your URN value (just the ID part, not the full urn string)

### 4. Run manually to test

Go to Actions tab → "Monthly Auto Project Bot" → Run workflow

---

## How it works

```
GitHub Actions (cron: 1st of every month)
  ↓
Claude API → generates trending project idea + full HTML/CSS/JS code
  ↓
GitHub API → creates new public repo → pushes all files
  ↓
GitHub Pages or Vercel → live deployment URL
  ↓
LinkedIn API → publishes post with live link
```

---

## Notes

- Static projects deploy to GitHub Pages (free, no limits)
- If you add VERCEL_TOKEN, non-static projects deploy to Vercel
- LinkedIn access token expires every 60 days — refresh it manually in secrets
- Each project repo name includes the month so there are no conflicts
