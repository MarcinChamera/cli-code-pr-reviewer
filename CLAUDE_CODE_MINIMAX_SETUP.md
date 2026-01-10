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

## Claude on Github

This section covers how to run Claude on Github. These commands set up GitHub Actions that enable Claude/Claude Code to interact with your repository:

1. Install the GitHub CLI:
   ```bash
   sudo apt install gh
   ```

2. Open Claude Code and run `/install-github-app` - this will walk you through a few steps:
   - Install the Claude Code app on GitHub
   - Add an API key (use the MiniMax one)

   This will automatically create 2 PRs with GitHub Actions:
   - **Mention action**: Claude Code can be mentioned from an issue or PR with `@claude`
   - **Pull Request action**: Claude will automatically run and review proposed changes
