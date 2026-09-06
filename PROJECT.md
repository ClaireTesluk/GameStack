# GameStack Project Overview and Roadmap

> **Product decision (2026-09-05):** Minecraft Paper is the first GamePack.
> Implement the private Java playable milestone first; backup, restore, and safe
> updates remain release gates. Earlier Foundry/Valheim recommendations below are
> historical product research, not the current implementation priority.

## 1. Project Summary

**GameStack** is a beginner-friendly platform for deploying and managing self-hosted game servers on spare PCs, home servers, and small Linux machines.

The project is not intended to create or maintain custom game server containers. Instead, GameStack sits above existing open-source Docker images and handles the difficult integration work around them.

The core value proposition is:

**Turn a spare PC into a private game server for friends without needing to learn Docker, Linux administration, backups, or game-server configuration.**

The initial business model should focus on selling small, polished, game-specific deployment products for roughly **$5–10 each**, while gradually building reusable infrastructure that can later evolve into a broader GameStack platform.

---

# 2. Project Constraints

GameStack is a small, independently maintained project. Prefer low maintenance
cost, reusable infrastructure, incremental delivery, and minimal operational
requirements. AI functionality is explicitly out of scope.

Optional maintainer context belongs in the ignored `PROJECTS.local.md` file and
is not part of the public repository.

---

# 3. Target Customer

The primary customer is not an experienced homelab administrator.

The ideal customer is:

> A gamer with an old gaming PC, mini-PC, NAS, or home server who wants to host a persistent multiplayer server for friends but does not want to become a Linux or Docker expert.

Typical customer characteristics:

- Comfortable following basic instructions
- May know how to SSH into a machine
- May have installed Linux before
- Does not understand Docker Compose well
- Does not want to manage reverse proxies or service configuration
- Does not want to manually manage backups
- Does not know SteamCMD
- Does not want to troubleshoot permissions
- Wants something that "just works"

Typical user intent:

> "My friends and I want a Valheim server that stays online even when I'm not playing."

Not:

> "I need enterprise orchestration for 100 game servers."

---

# 4. Market Positioning

GameStack should **not compete directly with Pterodactyl, Pelican, LinuxGSM, or large homelab control panels**.

Those platforms are powerful, but they generally assume the user is willing to think like a server administrator.

GameStack should instead optimize for:

### Simplicity over flexibility

GameStack should present concepts such as:

**Recommended performance**

instead of:

**CPU limit = 400%**

And:

**Automatic world backups every 6 hours**

instead of:

**Configure volume paths and cron jobs**

The product philosophy should be:

> Hide the infrastructure unless the user explicitly wants to see it.

---

# 5. Core Market Gap

The underlying game-server software is generally not the problem.

There are already excellent Docker images for many popular games.

The market gap exists between:

**Existing open-source container**

and:

**Complete, polished, reliable home-server experience**

Existing containers commonly solve:

- Installing the game server
- Starting the game server
- Exposing environment variables
- Updating the application

They often do not provide a complete beginner-oriented solution for:

- Initial system configuration
- Interactive setup
- Automatic backups
- Restore workflows
- Health checks
- Crash recovery
- Update safety
- Rollbacks
- Discord notifications
- Hardware recommendations
- Consistent directory structure
- Migration
- Documentation
- Debugging
- Secure defaults
- Networking guidance

GameStack sells this integration layer.

---

# 6. Initial Product Strategy

Do not begin by building the entire GameStack platform.

Start by selling **individual game-specific deployment packs**.

Working terminology:

**GamePacks**

Examples:

- GameStack Valheim Pack
- GameStack Foundry VTT Pack
- GameStack Project Zomboid Pack
- GameStack Satisfactory Pack
- GameStack Minecraft Paper Pack

Each pack should be independently useful.

Example pricing:

- Individual GamePack: **$7.99–9.99**
- Five-pack bundle: approximately **$24.99**
- Larger bundle later: approximately **$39.99**

Avoid making $5 the standard price because transaction costs and support expectations can make very low-priced software economically unattractive.

---

# 7. What a GamePack Includes

A GamePack should not simply be a Docker Compose file.

A typical product should include:

- Interactive installation
- Docker installation/checking
- Preconfigured Compose setup
- Game-specific configuration
- Persistent storage configuration
- Automatic startup
- Crash recovery
- Health checks
- Scheduled backups
- Easy restore workflow
- Safe updates
- Backup-before-update behavior
- Rollback capability where practical
- Discord notification support
- Simple status commands
- Clear documentation
- Uninstall/removal process

Example:

## Valheim Friends Server Pack

User experience:

```text
./install.sh

GameStack Valheim Setup

Server Name:
The Sanctuary

Password:
********

Maximum Players:
10

Backups:
Every 6 hours

Discord Notifications:
Enabled

Install? [Y/n]
```

The installer then handles the underlying infrastructure.

The customer should not need to manually edit Docker Compose unless they want advanced control.

---

# 8. Product Differentiation

The differentiator should be:

**A complete game-server appliance rather than a container template.**

Do not sell:

> Dockerized Valheim server

Sell:

> Always-online Valheim world for your friends, installed in minutes.

Features should be expressed in gamer terms.

For example:

Instead of:

```text
Bind mount:
/srv/valheim/worlds
```

Use:

```text
World Storage:
18.2 GB
```

Instead of:

```text
Restart policy:
unless-stopped
```

Use:

```text
Automatically restart server after a crash:
Enabled
```

---

# 9. High-Priority Product Categories

## Category A: Survival / Persistent World Games

This is likely the strongest initial category.

Examples:

- Valheim
- Project Zomboid
- Satisfactory
- Palworld
- Enshrouded
- V Rising
- 7 Days to Die
- Terraria
- Core Keeper

These games work well because small groups often want persistent servers.

The user has a clear reason to self-host:

> "We want the world running even when the usual host is offline."

---

# 10. Foundry VTT Opportunity

Foundry VTT is particularly attractive as an early GamePack.

The audience includes technically curious users who are not necessarily system administrators.

Potential product:

## GameStack Foundry VTT Home Server Kit

Features:

- Foundry deployment
- Secure persistent storage
- HTTPS setup
- Reverse proxy configuration
- Automatic certificates
- Scheduled campaign-data backups
- Restore workflow
- Automatic startup
- Update utilities
- Discord alerts
- Health monitoring

Possible price:

**$9.99**

Foundry remains a candidate for a later pack; Minecraft Paper is the selected first product.

---

# 11. Modded GamePack Opportunity

A particularly strong future opportunity is **curated modded server deployments**.

Examples:

- Modded Valheim Friends Server
- BetterMC Friends Server
- Minecraft Paper Community Server
- Project Zomboid Modpack Server

The value comes from creating a known-good configuration.

Example:

## BetterMC Friends Server

Could include:

- Correct Java version
- Correct Minecraft version
- Mod loader
- Modpack installation
- Known-working configuration
- Recommended RAM
- Automated backups
- Update process
- Rollback
- Crash recovery
- Whitelist
- Discord integration

This can be more valuable than generic game deployment because modded servers introduce more failure points.

---

# 12. Community / Streamer Packs

Eventually, GameStack could offer different profiles for the same game.

Example:

## Valheim Friends Pack

Focused on:

- Simplicity
- Small groups
- Backups
- Easy maintenance

## Valheim Community Pack

Focused on:

- Discord integration
- Scheduled restarts
- Player notifications
- Admin tools
- Whitelist management
- Moderator workflows
- Server events

This allows reuse of the same game infrastructure while serving different customer types.

---

# 13. Architecture Direction

Develop the runtime and the first two real GamePacks in one public `gamestack`
repository. Minecraft Paper remains GamePack #1; select GamePack #2 after the first
pack meets its release gates. Foundry and Valheim are candidates, not placeholder
implementations to create now.

Current repository boundaries:

```text
gamestack/
├── src/gamestack/       # Generic CLI, validation, and runtime behavior
├── packs/
│   ├── example/        # Non-runnable schema reference
│   └── minecraft-paper/ # First real GamePack and its acceptance material
├── tests/              # Runtime and pack regression/integration tests
├── docs/               # Shared CLI, schema, roadmap, and release documentation
└── scripts/            # Build and release tooling
```

Keep game-specific settings, upstream pins, notices, and acceptance guides with
the pack. Shared installation, lifecycle, backup, restore, update, and diagnostic
behavior belongs in the engine. The schema documentation and validator stay here
while those two implementations reveal the necessary interface.

Once both packs demonstrate a stable interface, extract the planned repositories
under `gamestackhq`: public `gamestack` (AGPL-3.0), public `pack-spec` (Apache-2.0),
public `community-packs` (AGPL-3.0), private `official-packs` (commercial), and private
`gamestack-site` (proprietary). This is LATER work, not a v0.1 release gate.

See [repository boundaries and extraction gates](docs/repository-layout.md).

---

# 14. GamePack Specification

Game-specific behavior should eventually be described declaratively.

Example:

```yaml
name: Valheim Friends Server

game:
  image: existing-open-source-container

resources:
  memory:
    recommended: 6GB

network:
  ports:
    - 2456-2458/udp

backup:
  paths:
    - /data/worlds
  interval: 6h
  retention: 7

updates:
  strategy: backup-first

health:
  enabled: true

notifications:
  discord:
    events:
      - server_started
      - server_stopped
      - backup_failed
      - update_failed
```

The GameStack runtime interprets this configuration.

This allows future games to be added without rewriting the core platform.

---

# 15. Technology Recommendations

Initial implementation should favor reliability and simplicity.

Potential stack:

### Backend / tooling

- Python
- Docker
- Docker Compose
- YAML configuration

### Installation

Initial versions may use:

```bash
./install.sh
```

or:

```bash
gamestack install valheim
```

Do not require a large web application for V0.1.

### Future dashboard

A lightweight local web UI could eventually provide:

- Server status
- Start / stop
- Backup
- Restore
- Update
- Logs
- Basic settings

The dashboard should come after product validation.

---

# 16. Networking Scope

Networking is a major pain point, but it should not dominate the earliest product.

Initial versions should:

- Detect local IP
- Explain required ports
- Test whether ports appear reachable where possible
- Provide clear forwarding instructions
- Avoid exposing unnecessary services
- Avoid automatically making risky router changes

Later GameStack versions could add:

- UPnP support
- DDNS integration
- Tunneling
- Hosted relay service
- Easy external connectivity

These could eventually support subscription revenue.

For the current $5–10 GamePack model, advanced tunneling is **not required for launch**.

---

# 17. Backup Philosophy

Backups should be one of the strongest GameStack features.

Every supported game should have:

- Game-specific save locations
- Scheduled backups
- Retention policy
- Manual backup command
- Simple restore command
- Backup before updates
- Backup before migrations

Example user experience:

```text
GameStack Backups

1. 2026-09-04 18:00
2. 2026-09-04 12:00
3. 2026-09-04 06:00

Restore backup #2?

This will stop the server before restoring.

[Y/n]
```

Future features may include:

- Backup timeline
- Temporary server cloning
- Off-device backup
- Cloud backup

---

# 18. Update Philosophy

Automatic updates must be conservative.

Ideal workflow:

```text
Check update
    ↓
Create backup
    ↓
Gracefully stop server
    ↓
Update
    ↓
Start server
    ↓
Perform health check
    ↓
Success
```

If health check fails:

```text
Rollback previous known-good configuration
```

Do not prioritize aggressive automatic updates over reliability.

---

# 19. Distribution Strategy

The website should not be the primary discovery mechanism.

Primary funnel:

```text
Google Search
     ↓
YouTube
     ↓
GitHub
     ↓
GameStack Website
     ↓
Checkout
```

The GameStack website serves primarily as:

- Brand home
- Landing pages
- Product descriptions
- Documentation
- Checkout links

Do not build custom ecommerce infrastructure initially.

---

# 20. Checkout / Ecommerce

Use an external ecommerce platform rather than building payment infrastructure.

Preferred initial option:

**Lemon Squeezy**

Reasons:

- Digital product delivery
- Software-oriented features
- Merchant-of-record model
- Tax handling
- License key support if needed later

Possible secondary marketplace:

**itch.io**

GameStack should maintain its own domain even if checkout is external.

Example:

```text
gamestack.example/valheim
```

Click:

```text
Buy for $9.99
```

External checkout handles payment.

---

# 21. YouTube Strategy

YouTube may become the strongest acquisition channel.

The content should be educational first and promotional second.

Example video:

## How to Host a Valheim Server on an Old PC

The video provides the manual setup.

During the tutorial:

> If you want this entire setup preconfigured with automatic backups and updates, the GameStack version is linked below.

This approach is valuable because viewers who think:

> "This is too much setup."

are precisely the target customer.

Potential video topics:

- How to host Valheim
- How to host Foundry VTT
- How to host Project Zomboid
- Best cheap PCs for game servers
- Running multiple game servers
- Docker game hosting tutorials
- Home game server security
- Backup strategies
- Server performance tuning

Each GamePack should ideally produce at least one useful YouTube video.

---

# 22. GitHub Strategy

GitHub should build trust, adoption, and contributions through an open-source
engine and ecosystem interface.

The chosen direction is **open-core + commercial GamePacks**:

- The public engine provides shared installation, lifecycle, backup, restore,
  update, and diagnostic capabilities as they are implemented.
- The planned public specification lets official and community packs use the same
  declarative interface.
- Paid official GamePacks provide curated settings, verified upstream versions,
  acceptance testing, and polished game-specific installation and recovery guides.

Keep the first two real packs in this repository during interface development.
The current repository remains under its existing AGPL-3.0 license; the future
repository plan does not apply commercial terms to the current pack directories.
Pricing and sales delivery details can evolve within this direction. No paid
GamePacks are currently available.

---

# 23. Reddit and Discord Strategy

Do not treat Reddit or Discord primarily as advertising channels.

Use them for:

- Customer research
- Identifying hosting pain points
- Understanding game-specific problems
- Helping users
- Discovering frequently repeated questions

Where community rules permit it, GameStack can be mentioned when directly relevant.

Avoid spam-style promotion.

The long-term goal is to become known as a useful member of relevant hosting communities.

---

# 24. Support Economics

Support cost is one of the largest risks in the business model.

A customer paying $7.99 cannot economically receive an hour of personalized technical support.

The product should therefore be highly self-service.

Included:

- Documentation
- Updates
- Troubleshooting guide
- Installer diagnostics

Not automatically included:

- SSH troubleshooting
- Custom networking work
- Custom migrations
- Remote installation

Possible upsell:

## Installation Assistance

Approximately:

**$49+**

This converts difficult support cases into paid work.

---

# 25. Commercial Readiness

Prepare product delivery, support terms, and third-party licensing review before
launching paid GamePacks.

---

# 26. Legal / Licensing Requirements

Before launch, review the licenses of every open-source container or project used.

GameStack should not accidentally redistribute software in ways prohibited by its license.

Each GamePack should clearly distinguish between:

- GameStack-authored code
- Third-party open-source software
- Proprietary game-server software
- Customer-provided licenses

The product should include appropriate terms covering:

- No guarantee against data loss
- Backups
- Third-party service changes
- Game updates
- Compatibility
- Networking configuration
- Open-source dependencies

The goal should be responsible risk reduction, not attempting to disclaim everything.

---

# 27. Major Risks

## Risk 1: Customers will just use free Docker containers

Mitigation:

GameStack must deliver enough convenience that the purchase feels cheaper than spending an hour figuring out deployment.

---

## Risk 2: Support consumes all profit

Mitigation:

- Strong diagnostics
- Strong documentation
- Supported platforms only
- No unlimited personalized support
- Paid installation assistance

---

## Risk 3: Maintaining many games becomes overwhelming

Mitigation:

Build shared infrastructure and declarative GamePack definitions.

Avoid supporting dozens of games before the platform is stable.

---

## Risk 4: Game updates break deployments

Mitigation:

- Version testing
- Backup-first updates
- Health checks
- Rollback
- Avoid blindly tracking latest versions

---

## Risk 5: Distribution is harder than development

Mitigation:

Every product should have a content strategy.

GamePack development and YouTube content should reinforce one another.

---

## Risk 6: Existing panels move down-market

Mitigation:

Differentiate around beginner UX, specific curated GamePacks, and opinionated defaults.

Do not compete on raw feature count.

---

# 28. What Is Explicitly Out of Scope

For early GameStack development, avoid:

- AI troubleshooting
- Local LLM integration
- Kubernetes
- Multi-node clusters
- Enterprise hosting
- Hundreds of games
- Custom container development
- Mobile apps
- Full marketplace
- Paid cloud infrastructure
- Complex user management
- Multi-tenant hosting
- Automated router configuration
- Custom payment processing

These can be revisited only after validating demand.

---

# 29. Recommended Initial Product

The original candidate for Product #1 was (superseded by the Paper decision above):

## GameStack Foundry VTT Home Server Kit

Target:

Someone who wants to self-host Foundry but does not want to manually configure Docker, HTTPS, backups, and service management.

Potential features:

- Guided installation
- Foundry Docker deployment
- Persistent storage
- Secure reverse proxy
- HTTPS
- Automatic certificate renewal
- Backups
- Restore
- Automatic startup
- Update script
- Health check
- Discord notifications

Target price:

**$9.99**

---

# 30. Recommended Product Sequence

After Foundry:

## Product #2

**Valheim Friends Server**

Target price:

**$7.99–9.99**

---

## Product #3

**Project Zomboid Friends Server**

---

## Product #4

**Satisfactory Friends Server**

---

## Product #5

**Minecraft Paper Friends Server**

Minecraft should likely come after the underlying GameStack infrastructure is stable because its ecosystem introduces additional complexity and competition.

---

# 31. Phase 0 — Validation

Goal:

Prove that people have this problem before building much software.

Tasks:

- Define first product
- Research common hosting problems
- Review competitor installation flows
- Identify required features
- Create mock landing page
- Write pricing copy
- Interview or observe potential users

Success criteria:

At least several users indicate they would plausibly pay roughly $10 to avoid the manual setup.

---

# 32. Phase 1 — First GamePack

Target:

Foundry VTT or Valheim

Build:

- GamePack specification
- Installer
- Configuration generation
- Docker deployment
- Persistent storage
- Status command
- Stop/start/restart
- Backup
- Restore
- Update
- Health check
- Documentation

Do not build a web dashboard yet.

Success criteria:

A non-DevOps user can install the product successfully by following the documentation without live help.

---

# 33. Phase 2 — Productization

Add:

- Better error messages
- Diagnostic command
- Uninstall
- Upgrade GamePack tooling
- Discord notifications
- Improved documentation
- Automated testing
- Release packaging

Example:

```bash
gamestack doctor
```

Output:

```text
Docker                  ✓
Disk space              ✓
Game server             ✓
Backup service          ✓
Network port            ✓
Permissions             ✓
```

Success criteria:

Very few users require direct support.

---

# 34. Phase 3 — Commercial Launch

Create:

- GameStack domain
- Landing page
- Lemon Squeezy account
- Product page
- Basic logo / branding
- Documentation
- GitHub organization
- Terms / licensing
- Demo video

Launch Product #1.

Track:

- Visitors
- Checkout clicks
- Sales
- Refunds
- Support requests
- Installation failures

---

# 35. Phase 4 — Validate Economics

Do not immediately build ten games.

Run the first product long enough to answer:

- Are people willing to pay?
- What acquisition channels work?
- How many support requests occur?
- What features do customers value?
- What features do users struggle with?
- What is the effective hourly maintenance burden?

Strong early validation example:

```text
500 landing-page visitors

20 purchases

4% conversion

$200 revenue
```

This would be meaningful evidence that the concept deserves expansion.

---

# 36. Phase 5 — Second and Third GamePacks

Once the platform works:

Add:

- Valheim
- Project Zomboid
- Satisfactory

Prioritize games with:

- Dedicated-server support
- Persistent worlds
- Multiplayer groups
- Active communities
- Existing Docker containers
- Frequent hosting questions

Measure sales separately for each game.

---

# 37. Phase 6 — Shared GameStack CLI

Once multiple packs exist, consolidate common functionality.

Potential interface:

```bash
gamestack install valheim

gamestack status

gamestack backup valheim

gamestack restore valheim

gamestack update valheim

gamestack logs valheim

gamestack doctor
```

This CLI becomes the foundation for future GameStack products.

---

# 38. Phase 7 — Local Web Dashboard

Only after the CLI and GamePacks are validated should GameStack introduce a local dashboard.

Possible features:

```text
GAMESTACK

Valheim
● Online
3 players
[Manage]

Foundry
● Online
[Manage]

Project Zomboid
○ Offline
[Start]

[Add Server]
```

Management page:

- Server status
- CPU usage
- RAM
- Storage
- Start
- Stop
- Restart
- Backup
- Restore
- Update
- Logs

The dashboard must remain intentionally simple.

---

# 39. Phase 8 — Bundles

After 5+ products exist, test bundles.

Example:

## GameStack Friends Bundle — $24.99

Choose five GamePacks.

Potential products:

- Valheim
- Project Zomboid
- Satisfactory
- Foundry
- Minecraft
- Palworld
- Enshrouded
- V Rising

Bundling raises average order value and improves economics.

---

# 40. Phase 9 — Community Packaging

If GameStack develops adoption, introduce a public GamePack format.

Possible developer workflow:

```bash
gamestack pack init
```

Community members could create support for additional games.

This reduces the founder's maintenance burden.

A future registry could eventually contain:

```text
Valheim Friends
Minecraft Paper
Minecraft BetterMC
Satisfactory
Foundry
Zomboid
Terraria
Vintage Story
V Rising
Enshrouded
```

Community packaging should come well after the core schema is stable.

---

# 41. Possible Long-Term Platform

If GameStack succeeds, the eventual product could become:

> A consumer-friendly operating layer for self-hosted multiplayer gaming.

Long-term capabilities might include:

- Web dashboard
- GamePack store
- Community GamePacks
- Automatic updates
- Backup timeline
- Remote access
- Cloud backups
- Monitoring
- Discord integration
- Server migration
- Hardware recommendations

Potential future recurring services:

## GameStack Connect

Possible features:

- Remote access
- Hosted domain
- External uptime checks
- Tunneling

Possible price:

Approximately **$5/month**

---

## GameStack Backup

Possible features:

- Encrypted off-site backups
- Remote restore
- Disaster recovery

Possible price:

Approximately **$5–10/month**

These should not be built until there is demonstrated demand.

---

# 42. Success Metrics

Early project success should not be measured primarily by GitHub stars.

Important metrics:

### Product

- Successful installs
- Failed installs
- Support requests per sale
- Refund rate

### Commercial

- Landing-page visitors
- Checkout conversion
- Revenue
- Average order value
- Repeat purchases

### Distribution

- YouTube views
- Google traffic
- GitHub traffic
- Email subscribers


---

# 43. Primary Strategic Principle

Every major piece of work should ideally produce multiple forms of value.

Example:

Build Valheim GamePack.

This creates:

1. A sellable product
2. A YouTube tutorial
3. GitHub content
4. Search traffic
5. Documentation
6. Reusable GameStack infrastructure

Avoid work that only creates one isolated output whenever possible.

---

# 44. Initial 90-Day Roadmap

## Weeks 1–2

Research and specification

- Choose first game
- Analyze existing containers
- Identify common installation pain points
- Define V0.1 feature set
- Draft GamePack schema

---

## Weeks 3–5

Build core tooling

- Installer
- Docker orchestration
- Configuration
- Storage
- Start/stop
- Backup
- Restore

---

## Weeks 6–7

Reliability

- Update system
- Health checks
- Diagnostics
- Error handling
- Uninstall
- Testing

---

## Week 8

Documentation

Create:

- Quick start
- Installation guide
- Troubleshooting
- Backup guide
- Restore guide
- Update guide

---

## Weeks 9–10

Commercial setup

- Landing page
- Domain
- Checkout
- GitHub
- Branding
- Product packaging
- Terms

---

## Week 11

Content

Create:

- Installation demo
- Full manual hosting tutorial
- GamePack comparison
- Launch post

---

## Week 12

Launch and observe.

Do not immediately begin Product #2.

First collect:

- Sales
- Installation problems
- User questions
- Refund requests
- Feature requests

Use those findings to decide the next roadmap.

---

# 45. Decision Gates

## Gate 1

Can a non-technical user successfully install GamePack #1?

If no:

Improve UX before adding games.

---

## Gate 2

Will strangers pay approximately $10?

If no:

Reevaluate positioning, product choice, or pricing.

---

## Gate 3

Can GameStack support customers profitably?

If every purchase generates significant manual support:

Fix the product before scaling.

---

## Gate 4

Can common functionality support multiple games?

If every new game requires extensive custom development:

Improve GamePack architecture.

---

## Gate 5

Does distribution work?

If organic traffic does not develop:

Improve content, SEO, partnerships, or channel strategy before dramatically expanding product scope.

---

# 46. Agent Instructions

When analyzing or developing GameStack, agents should follow these principles:

1. **Do not assume the idea is good. Challenge assumptions.**
2. Prefer simple solutions suitable for a small, independently maintained project.
3. Favor existing open-source components over rebuilding infrastructure.
4. Do not introduce AI functionality unless explicitly requested.
5. Optimize for beginner users rather than DevOps professionals.
6. Avoid enterprise features.
7. Prioritize low support burden.
8. Consider commercial viability alongside technical elegance.
9. Treat distribution as equally important as product development.
10. Validate with one product before expanding the catalog.
11. Keep the underlying GameStack architecture reusable.
12. Prefer incremental releases over building the full platform upfront.

When recommending features, classify them as:

- **Required for V0.1**
- **Useful soon**
- **Later**
- **Out of scope**

When evaluating potential GamePacks, consider:

- Game popularity
- Hosting pain
- Existing competition
- Docker/container quality
- Community size
- Update frequency
- Support burden
- Modding complexity
- Search demand
- Willingness to pay
- Ability to reuse GameStack infrastructure

The most important question is not:

> "Can GameStack technically do this?"

It is:

> **"Does this make hosting meaningfully easier for enough people that they will pay for it?"**