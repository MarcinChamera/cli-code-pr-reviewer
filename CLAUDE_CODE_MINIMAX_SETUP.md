# MiniMax-M2.1 Setup with Claude Code

To use MiniMax-M2.1 model with Claude Code instead of Anthropic's Sonnet/Opus models:

1. Run `/logout` in Claude Code
2. Go to https://platform.minimax.io/user-center/payment/coding-plan and copy your MiniMax API Key
3. Remove `~/.claude/auth.json` file
4. Open `~/.claude/settings.json` and ensure it looks like this:
   ```json
   {
     "env": {
       "ANTHROPIC_AUTH_TOKEN": "MIN_MAX_API_KEY",
       "ANTHROPIC_BASE_URL": "https://api.minimax.io/anthropic",
       "ANTHROPIC_DEFAULT_HAIKU_MODEL": "MiniMax-M2.1",
       "ANTHROPIC_DEFAULT_OPUS_MODEL": "MiniMax-M2.1",
       "ANTHROPIC_DEFAULT_SONNET_MODEL": "MiniMax-M2.1",
       "ANTHROPIC_MODEL": "MiniMax-M2.1",
       "API_TIMEOUT_MS": "3000000",
       "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": 1
     },
     "includeCoAuthoredBy": false
   }
   ```
   - Replace `ANTHROPIC_AUTH_TOKEN` value with your real MiniMax API key
   - Use `https://api.minimax.io/anthropic` (global link), not `https://api.minimaxi.com/anthropic` (China link)

5. Export the environment variables and start Claude Code:
   ```bash
   export ANTHROPIC_AUTH_TOKEN="sk-cp-YOUR_FULL_KEY_HERE"
   export ANTHROPIC_BASE_URL="https://api.minimax.io/anthropic"
   claude
   ```
   **Important**: Do not authorize the browser login, or you'll create a new Anthropic session and encounter an "Auth conflict" error.

## Claude on GitHub

This section covers how to run Claude on GitHub with MiniMax. These commands set up GitHub Actions that enable Claude/Claude Code to interact with your repository:

### Step 1: Install GitHub CLI

```bash
sudo apt install gh
```

### Step 2: Install GitHub App

Open Claude Code and run `/install-github-app` - this will walk you through:
- Installing the Claude Code app on GitHub
- Adding an API key (use the MiniMax one)

This will automatically create 2 PRs with GitHub Actions:
- **Mention action**: Claude can be mentioned from an issue or PR with `@claude`
- **Pull Request action**: Claude will automatically run and review proposed changes

### Step 3: Add Required GitHub Secrets

The GitHub Actions need MiniMax API credentials. Add these secrets via GitHub UI or CLI:

**Using GitHub UI:**
1. Go to your repo → Settings → Secrets and variables → Actions
2. Add the following secrets:

**Using CLI:**
```bash
# Add MiniMax API key (get from https://platform.minimax.io/user-center/payment/coding-plan)
gh secret set ANTHROPIC_API_KEY --body "sk-cp-YOUR_MINIMAX_API_KEY"

# Add MiniMax base URL
gh secret set ANTHROPIC_BASE_URL --body "https://api.minimax.io/anthropic"
```

### Step 4: Update Workflow Files

The default workflow files need a small modification to use MiniMax. Update `.github/workflows/claude.yml` and `.github/workflows/claude-code-review.yml` to include an `env` section with `ANTHROPIC_BASE_URL` and `github_token` in the `with` section:

```yaml
- name: Run Claude Code Review
  id: claude-review
  uses: anthropics/claude-code-action@v1
  env:
    ANTHROPIC_BASE_URL: ${{ secrets.ANTHROPIC_BASE_URL }}
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    github_token: ${{ secrets.GITHUB_TOKEN }}
    plugin_marketplaces: 'https://github.com/anthropics/claude-code.git'
    plugins: 'code-review@claude-code-plugins'
    prompt: '/code-review:code-review ${{ github.repository }}/pull/${{ github.event.pull_request.number }}'
```

Key changes:
- **`env` section**: Passes `ANTHROPIC_BASE_URL` to the action (required for MiniMax)
- **`github_token`**: Required to bypass OIDC workflow validation in PRs
