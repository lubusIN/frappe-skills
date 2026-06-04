<p align="center">
  <img width="250" src=".github/assets/logo.svg" alt="Frappe Agent Skills" />
</p>

# Frappe Skills

Frappe Framework Structured knowledge for AI coding assistants—DocTypes, APIs, testing, and best practices.

> [!NOTE]
> _**AI Authorship Disclosure:**_
> Drafted with GPT-5.3 Codex from official documentation, then reviewed, refined, and validated by humans. Tested with AI assistants and improved through practical iteration.

## Why Frappe Agent Skills?

AI coding assistants are powerful, but they often:
- Generate outdated Frappe patterns (pre-v13, pre-Query Builder)
- Miss critical permission checks in API handlers
- Skip proper DocType controller patterns
- Ignore existing tooling in your project

These Agent Skills solve this by giving AI assistants deep framework knowledge in a structured format they can use.

## Available Skills

#### Core Skills
| Skill | Description |
|-------|-------------|
| `frappe-router` | Entry point-routes to appropriate skill based on task |
| `frappe-project-triage` | Detect project type, installed apps, version, and tooling |

#### Development Skills
| Skill | Description |
|-------|-------------|
| `frappe-app-development` | Scaffold and architect custom Frappe apps with hooks, background jobs, and service layers |
| `frappe-doctype-development` | Create and modify DocTypes, controllers, child tables |
| `frappe-api-development` | Build REST and RPC APIs with proper auth and permissions |

#### UI & Frontend Skills
| Skill | Description |
|-------|-------------|
| `frappe-desk-customization` | Customize Frappe Desk UI with form scripts, list views, and dialogs |
| `frappe-frontend-development` | Build modern Vue 3 frontend apps using Frappe UI |
| `frappe-ui-patterns` | UI/UX patterns derived from official Frappe apps (CRM, Helpdesk, HRMS) |
| `frappe-printing-templates` | Build print formats, email templates, and Jinja-based rendering |
| `frappe-reports` | Create Report Builder, Query Reports (SQL), and Script Reports (Python + JS) |
| `frappe-web-forms` | Build public-facing web forms for data collection |

#### Testing & Infrastructure
| Skill | Description |
|-------|-------------|
| `frappe-testing` | Write and run unit, integration, and UI tests |
| `frappe-manager` | Docker-based dev environments with Frappe Manager |

#### Patterns & Best Practices
| Skill | Description |
|-------|-------------|
| `frappe-enterprise-patterns` | Production patterns for CRM/Helpdesk-style apps |

## Installation

### Using Skills CLI (Recommended)

```bash
# Install all Frappe skills
npx skills add lubusIN/frappe-skills --skills=frappe-*

# Install all skills from all frameworks globally
npx skills add lubusIN/frappe-skills --skills=frappe-* -g

# Or install specific Frappe skills
npx skills add lubusIN/frappe-skills --skills=frappe-doctype-development,frappe-api-development
```

### Manual Installation

```bash
# Clone the parent repo
git clone https://github.com/lubusIN/frappe-skills.git
cd agent-skills

# Copy Frappe skills to your AI assistant's skills directory
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
frappe-doctype-development/
├── SKILL.md              # Main instructions (when to use, procedure, verification)
└── references/           # Deep-dive docs on specific topics
    ├── doctypes.md
    ├── controllers.md
    └── ...
```

When you ask your AI assistant to work on Frappe code, it reads these skills and follows documented procedures rather than guessing.

### Skill Structure

Each SKILL.md follows a standard format:
- **When to use** — Trigger conditions for this skill
- **Inputs required** — What info the agent needs before starting
- **Procedure** — Step-by-step instructions
- **Verification** — Checklist to confirm success
- **Failure modes** — Common issues and fixes
- **Escalation** — When to consult docs or ask user

## Compatibility

- Frappe Framework v13+
- Works with ERPNext, HRMS, and custom apps
- Compatible with any AI assistant that supports Agent Skills

## Contributing

Contributions welcome! To add or improve a skill:

1. Fork this repository
2. Create or modify skill in `<topic>`
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

1. Create `<topic>` directory
2. Add `<topic>/README.md` with topic-specific documentation
3. Create individual directories following the Agent Skills specification
4. Update the main README.md to list the new topic

## Credits

- Inspired by [WordPress Agent Skills](https://github.com/WordPress/agent-skills)
- Built on the [Anthropic Agent Skills Specification](https://agentskills.io/)


## Meet Your Artisans

[LUBUS](https://lubus.in/?utm_source=github&utm_medium=open-source&utm_campaign=frappe-skills) is a web design agency based in Mumbai.

<a href="https://cal.com/lubus">
<img src="https://raw.githubusercontent.com/lubusIN/.github/refs/heads/main/profile/banner.png" />
</a>

## License

Frappe Skills is open-sourced licensed under the [MIT License](LICENSE).
