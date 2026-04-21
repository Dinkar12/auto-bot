import os
import json
import base64
import requests
import time
from datetime import datetime

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
VERCEL_TOKEN = os.environ.get("VERCEL_TOKEN", "")
GITHUB_USERNAME = os.environ["GITHUB_USERNAME"]


# ─────────────────────────────────────────
# STEP 1: Generate project using Claude
# ─────────────────────────────────────────

def generate_project():
    print("[1/4] Asking Claude to generate a trending project...")

    today = datetime.now().strftime("%B %Y")

    prompt = f"""You are an expert developer building impressive portfolio projects. Today is {today}.

Think about what is TRENDING right now — AI tools, dashboards, productivity apps, finance trackers, 
dev tools, etc. Generate a fully working web project that would impress recruiters on LinkedIn.

Return ONLY valid JSON (absolutely no markdown, no backticks, no explanation). Use this exact structure:

{{
  "repo_name": "kebab-case-repo-name-{datetime.now().strftime('%Y-%m')}",
  "title": "Project Display Title",
  "description": "One line description of the project",
  "deploy_type": "static",
  "files": {{
    "index.html": "FULL complete HTML content here",
    "style.css": "FULL complete CSS content here",
    "script.js": "FULL complete JS content here"
  }},
  "tech_stack": ["HTML", "CSS", "JavaScript"]
}}

Rules:
- deploy_type must be "static" (HTML/CSS/JS only — no frameworks)
- The project must be VISUALLY stunning with modern design (glassmorphism, gradients, animations)
- It must have REAL functionality (not just a landing page)
- Make it something a developer would genuinely be proud to show
- All file contents must be complete and working — no placeholders"""

    res = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 8000,
            "messages": [{"role": "user", "content": prompt}]
        }
    )

    data = res.json()
    if "content" not in data:
        raise Exception(f"Claude API error: {data}")
    raw = data["content"][0]["text"].strip()

    # Strip markdown fences if Claude added them
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            try:
                return json.loads(part)
            except Exception:
                continue

    return json.loads(raw)


# ─────────────────────────────────────────
# STEP 2: Create GitHub repo and push code
# ─────────────────────────────────────────

def create_github_repo(repo_name, description):
    print(f"[2/4] Creating GitHub repo: {repo_name}")

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    res = requests.post(
        "https://api.github.com/user/repos",
        headers=headers,
        json={
            "name": repo_name,
            "description": description,
            "public": True,
            "auto_init": False
        }
    )

    if res.status_code not in [200, 201]:
        raise Exception(f"Failed to create repo: {res.text}")

    print(f"    Repo created: https://github.com/{GITHUB_USERNAME}/{repo_name}")
    time.sleep(2)


def push_files_to_github(repo_name, files, title, tech_stack):
    print("    Pushing files to GitHub...")

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Add README
    files["README.md"] = f"""# {title}

Auto-generated portfolio project — built with {', '.join(tech_stack)}.

## Live Demo
https://{GITHUB_USERNAME}.github.io/{repo_name}

---
*Generated automatically using Claude AI + GitHub Actions*
"""

    for filename, content in files.items():
        if isinstance(content, str):
            encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        else:
            encoded = base64.b64encode(content).decode("utf-8")

        res = requests.put(
            f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/contents/{filename}",
            headers=headers,
            json={
                "message": f"Add {filename}",
                "content": encoded
            }
        )

        if res.status_code not in [200, 201]:
            print(f"    Warning: Failed to push {filename}: {res.status_code}")
        else:
            print(f"    Pushed: {filename}")

        time.sleep(0.5)


# ─────────────────────────────────────────
# STEP 3: Deploy
# ─────────────────────────────────────────

def enable_github_pages(repo_name):
    print("[3/4] Enabling GitHub Pages...")

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    res = requests.post(
        f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/pages",
        headers=headers,
        json={"source": {"branch": "main", "path": "/"}}
    )

    live_url = f"https://{GITHUB_USERNAME}.github.io/{repo_name}"
    print(f"    Live (may take 1-2 min to activate): {live_url}")
    return live_url


def deploy_to_vercel(repo_name, files):
    print("[3/4] Deploying to Vercel...")

    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}",
        "Content-Type": "application/json"
    }

    vercel_files = [
        {"file": name, "data": content}
        for name, content in files.items()
    ]

    res = requests.post(
        "https://api.vercel.com/v13/deployments",
        headers=headers,
        json={
            "name": repo_name,
            "files": vercel_files,
            "projectSettings": {"framework": None},
            "target": "production"
        }
    )

    data = res.json()
    url = data.get("url", f"{repo_name}.vercel.app")
    live_url = f"https://{url}"
    print(f"    Deployed: {live_url}")
    return live_url


def deploy(repo_name, deploy_type, files):
    if VERCEL_TOKEN and deploy_type != "static":
        return deploy_to_vercel(repo_name, files)
    else:
        return enable_github_pages(repo_name)





# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    print("=" * 50)
    print("Auto Project Bot — Starting Pipeline")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    project = generate_project()
    print(f"    Project: {project['title']}")
    print(f"    Repo: {project['repo_name']}")

    create_github_repo(project["repo_name"], project["description"])
    push_files_to_github(
        project["repo_name"],
        project["files"],
        project["title"],
        project["tech_stack"]
    )

    live_url = deploy(
        project["repo_name"],
        project.get("deploy_type", "static"),
        project["files"]
    )

    print("=" * 50)
    print("Pipeline complete.")
    print(f"Repo  : https://github.com/{GITHUB_USERNAME}/{project['repo_name']}")
    print(f"Live  : {live_url}")
    print("=" * 50)


if __name__ == "__main__":
    main()
