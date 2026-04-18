<p align="center">
  <img width="250" src=".github/assets/logo.svg" alt="Agent Skills Logo" />
</p>

# Agent Skills

Structured framework knowledge for AI coding assistants: best practices, patterns, and workflows.

> [!NOTE]
> _**AI Authorship Disclosure:**_
> Drafted with GPT-5.3 Codex from official documentation, then reviewed, refined, and validated by humans. Tested with AI assistants and improved through practical iteration.
## Why Agent Skills?

AI coding assistants are powerful, but they often:
- Generate outdated framework patterns and anti-patterns
- Miss critical security checks (permissions, validation, authentication)
- Skip proper architectural patterns and conventions
- Ignore existing tooling and best practices in your project

Agent Skills solve this by giving AI assistants deep framework knowledge in a structured, discoverable format.

## Available Skills

<table style="border: none;" cellspacing="20" cellpadding="10">
<tr style="border: none;">

<td style="border: none; vertical-align: top; width: 33%;">
<img width="60" src=".github/assets/frappe.svg" alt="Frappe Logo" />
<h3>Frappe Framework</h3>
Skills covering the complete Frappe development lifecycle from app scaffolding and DocType development to APIs, UI customization, reports, testing, and production patterns.
<br/><br/>

**[View all (14)](skills/frappe/README.md)**

</td>
</tr>
</table>

## Quick Start

### Using Skills CLI (Recommended)

The easiest way to install is using the [Skills CLI](https://github.com/vercel-labs/skills?tab=readme-ov-file#skills):

```bash
# Install all skills from all frameworks
npx skills add lubusIN/agent-skills

# Install all skills from all frameworks globally
npx skills add lubusIN/agent-skills -g

# Install all Frappe skills
npx skills add lubusIN/agent-skills --skills=frappe-*

# Install specific skills from any framework
npx skills add lubusIN/agent-skills --skills=frappe-doctype-development,frappe-api-development
```

The CLI automatically detects your AI assistant (Claude Code, Cursor, Codex, VS Code) and installs to the correct location.

Refer [Skills CLI](https://github.com/vercel-labs/skills?tab=readme-ov-file#skills) doc for all the available args

### Manual Installation

If you prefer manual installation:

```bash
# Clone this repo
git clone https://github.com/lubusIN/agent-skills.git
cd agent-skills

# Copy all Frappe skills to your AI assistant's skills directory
# Claude Code (global)
cp -r skills/frappe/frappe-* ~/.claude/skills/

# Cursor (global)
cp -r skills/frappe/frappe-* ~/.cursor/skills/

# Or into your project
cp -r skills/frappe/frappe-* /path/to/your-project/.claude/skills/
```

## How It Works

Each skill contains:

```
skills/frappe/frappe-doctype-development/
├── SKILL.md              # Main instructions (when to use, procedure, verification)
└── references/           # Deep-dive docs on specific topics
    ├── doctypes.md
    ├── controllers.md
    └── ...
```

When you ask your AI assistant to work on framework code, it reads these skills and follows documented procedures rather than guessing.

### Skill Structure

Each SKILL.md follows a standard format:
- **When to use** - Trigger conditions for this skill
- **Inputs required** - What info the agent needs before starting
- **Procedure** - Step-by-step instructions
- **Verification** - Checklist to confirm success
- **Failure modes** - Common issues and fixes
- **Escalation** - When to consult docs or ask the user

## Contributing

Contributions welcome! To add or improve a skill:

1. Fork this repository
2. Create or modify skill in `skills/<topic>/<skill-name>/`
3. Ensure SKILL.md has all required sections
4. Test with your AI assistant
5. Submit a pull request

### Skill Authoring Guidelines

- Keep `SKILL.md` short and procedural
- Push detailed content into `references/`
- Include verification steps
- Document failure modes
- Link to official docs when appropriate

### Adding a New Skill

1. Create `skills/<topic>/` directory
2. Add `skills/<topic>/README.md` with topic-specific documentation
3. Create individual skill directories following the Agent Skills specification
4. Update the main README.md to list the new topic

## Credits

- Inspired by [WordPress Agent Skills](https://github.com/WordPress/agent-skills)
- Built on the [Anthropic Agent Skills Specification](https://agentskills.io/)


## Meet Your Artisans

[LUBUS](https://lubus.in/?utm_source=github&utm_medium=open-source&utm_campaign=agent-skills) is a web design agency based in Mumbai.

<a href="https://cal.com/lubus">
<img src="https://raw.githubusercontent.com/lubusIN/.github/refs/heads/main/profile/banner.png" />
</a>

## License

Agent Skills is open-sourced licensed under the [MIT License](LICENSE).
