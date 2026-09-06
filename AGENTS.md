# AGENTS.md

This file defines expectations for coding agents, automated contributors, and AI assistants working on the GameStack repository.

Read `PROJECT.md` before making architectural or product decisions.

---

# 1. Mission

GameStack exists to make self-hosted game servers easy for ordinary gamers.

When choosing between:

```text
more flexibility
```

and:

```text
a dramatically simpler default experience
```

prefer simplicity unless flexibility is necessary for a common use case.

The target customer is **not a DevOps engineer**.

---

# 2. Core Constraints

GameStack is a small, independently maintained project. Keep implementation and ongoing maintenance manageable:

- Prefer boring technology.
- Prefer small dependencies.
- Prefer reusable implementations.
- Prefer incremental releases.
- Avoid infrastructure that requires continuous operation.
- Avoid features creating significant support burden.
- Do not introduce complexity merely because it may be useful later.

A working simple implementation is preferable to an elaborate generalized system that delays validation.

---

# 3. Before Making Changes

Before implementing substantial work:

1. Read `PROJECT.md`.
2. Inspect the existing implementation.
3. Identify whether functionality already exists.
4. Check relevant tests.
5. Determine whether the change belongs in:
   - core runtime
   - GamePack configuration
   - documentation
   - packaging
6. Preserve existing behavior unless a change is explicitly required.

Do not rewrite major subsystems merely to match personal preferences.

---

# 4. Scope Classification

For proposed work, classify features into one of:

### REQUIRED FOR V0.1

Necessary to sell and safely use the first GamePack.

### USEFUL SOON

High value, but launch can succeed without it.

### LATER

Potentially valuable after validation.

### OUT OF SCOPE

Do not implement without an explicit project decision.

When uncertain, choose the smaller scope.

---

# 5. Explicitly Prohibited Scope Creep

Do not introduce any of the following unless explicitly requested:

- AI
- LLMs
- AI troubleshooting
- Kubernetes
- Microservices
- Distributed orchestration
- Cloud-hosted control planes
- Enterprise authentication systems
- Mobile applications
- Multi-tenancy
- Automatic router modification
- Large web frameworks solely for a future dashboard
- Complex plugin frameworks
- Marketplace infrastructure

Do not add abstractions for imaginary future requirements.

---

# 6. Technology Direction

Primary implementation language:

```text
Python
```

Primary runtime dependencies:

```text
Docker
Docker Compose
YAML
Linux
```

Prefer Python for application logic.

Use shell only when:

- bootstrapping the installer
- interacting with platform tooling is significantly simpler in shell
- implementing small packaging scripts

Do not implement complex application logic in Bash if it can be reasonably expressed and tested in Python.

---

# 7. Dependency Policy

Before adding a dependency, ask:

1. Can the standard library handle this cleanly?
2. Is this dependency mature?
3. Does it substantially simplify implementation?
4. What is its maintenance burden?
5. Does it increase installation complexity?
6. Does it introduce security concerns?

Avoid dependencies for trivial functionality.

Do not add large frameworks for small problems.

---

# 8. Architectural Boundary

The core runtime handles generic behavior.

Examples:

```text
configuration
Docker interaction
backups
restore
updates
health checks
diagnostics
notifications
logging
```

Game-specific behavior belongs in GamePacks.

Examples:

```text
container image
ports
storage paths
configuration prompts
environment variables
recommended resources
shutdown requirements
health checks
backup locations
```

If adding support for a game requires modifying many unrelated runtime files, consider whether the missing behavior belongs in the GamePack schema.

However:

> Do not over-generalize based on one game.

Allow at least two concrete use cases to reveal an abstraction before creating complicated generic machinery.

Develop the first two real GamePacks in this repository before extracting the
runtime, specification, or pack collections into separate repositories. Follow
[the repository separation plan](docs/repository-layout.md): keep game-specific
configuration, upstream records, and acceptance guides in `packs/<id>/`, and keep
shared behavior in `src/gamestack/`. Do not add empty candidate packs, a registry,
or commercial licensing enforcement as preparation for the future split.

---

# 9. GamePack Design

GamePacks should become as declarative as practical.

Prefer:

```yaml
storage:
  world:
    path: /data/worlds
```

over:

```python
if game == "valheim":
    world_path = "/data/worlds"
```

Game-specific conditionals scattered through core code are a design smell.

Exceptions are acceptable when the underlying game genuinely requires behavior that cannot reasonably be declarative.

Document such exceptions.

---

# 10. Backwards Compatibility

Until the GamePack schema stabilizes, compatibility requirements are modest.

However:

- Do not silently invalidate user configurations.
- Do not silently move save data.
- Do not silently delete old backups.
- When configuration migration is required, perform it explicitly.
- Prefer migration tools over breaking configuration.

User worlds are more important than architectural cleanliness.

---

# 11. Data Safety

Treat all game saves and Foundry campaign data as irreplaceable.

Any code touching user data must follow this rule:

> **Failure should leave the user with more recoverable copies, not fewer.**

Never:

- recursively delete an unknown path
- delete a save because a container was removed
- delete backups during uninstall without explicit confirmation
- overwrite an existing world without safeguards
- assume an empty variable/path is safe

Before destructive filesystem operations:

1. Resolve the path.
2. Validate that it lies inside an expected GameStack-controlled location.
3. Reject suspicious/root/home-level paths.
4. Log the intended action.
5. Require explicit confirmation where appropriate.

Examples of paths that should trigger hard failure:

```text
/
/home
/home/<user>
/srv
/opt
```

when a more specific GameStack path was expected.

---

# 12. Backup Requirements

Backups must be:

- deterministic
- easy to locate
- easy to enumerate
- easy to restore
- logged
- failure-aware

A backup operation should not report success unless the resulting artifact exists and passes basic validation.

Backups should carry metadata where practical:

```text
game
instance
timestamp
GameStack version
GamePack version
server version if known
```

Retention policies must never delete the newest successful backup.

---

# 13. Restore Requirements

Restore operations must prioritize safety.

Preferred workflow:

```text
validate backup
      ↓
stop server
      ↓
create safety snapshot of current state
      ↓
restore selected backup
      ↓
start server
      ↓
health check
```

If creating a pre-restore snapshot is impractical, clearly warn the user.

Never restore while a server is actively writing save data unless the game explicitly supports it.

---

# 14. Update Requirements

Do not blindly run latest versions.

Preferred workflow:

```text
preflight validation
      ↓
backup
      ↓
graceful shutdown
      ↓
update
      ↓
start
      ↓
health check
```

When possible, retain sufficient information to recover the previously known-good version.

Automatic updates should be conservative.

Reliability is more important than immediate patch adoption unless the update addresses a critical security issue.

---

# 15. Docker Rules

GameStack uses Docker as an implementation detail.

Users should not need to manually invoke Docker for normal operations.

Agents may use:

- Docker Compose
- health checks
- named/bind volumes
- restart policies
- Docker APIs

Prefer generated Compose files that remain readable by advanced users.

Do not hide user data inside opaque locations without a strong reason.

Avoid privileged containers unless absolutely required and explicitly justified.

Do not mount the Docker socket into game containers.

---

# 16. Root Privileges

Minimize root usage.

Root may be required for:

- initial Docker installation
- filesystem setup
- service installation

After setup, normal GameStack operations should run with the least privileges practical.

Do not run game containers as root when upstream images support safer execution.

---

# 17. Networking Rules

Do not expose ports beyond what the game requires.

Do not expose internal administrative interfaces publicly by default.

For every externally exposed port:

- document its purpose
- document protocol
- keep the default minimal

Do not automatically:

- enable UPnP
- modify router settings
- modify firewall rules broadly

without an explicit feature design.

---

# 18. Secrets

Secrets include:

- game passwords
- Discord webhook URLs
- API tokens
- Foundry credentials
- license information

Rules:

- Never log secrets.
- Never commit secrets.
- Never include real secrets in tests.
- Mask secret values in CLI output.
- Use restricted file permissions for persisted secrets.
- Prefer environment/config files outside source-controlled directories.

Example output:

```text
Discord webhook: configured
```

not:

```text
Discord webhook: https://discord.com/api/webhooks/...
```

---

# 19. CLI UX

The CLI is the initial product interface.

Prioritize:

- discoverable commands
- readable errors
- safe defaults
- concise normal output
- detailed debug output

Commands should generally follow:

```text
gamestack <verb> <target>
```

Examples:

```bash
gamestack install valheim
gamestack status valheim
gamestack backup valheim
gamestack restore valheim
gamestack update valheim
```

Use consistent terminology across games.

---

# 20. User-Facing Language

Never assume knowledge of Docker.

Avoid messages like:

```text
Volume mount invalid.
```

Prefer:

```text
GameStack cannot access your Valheim world folder.

Expected location:
/srv/gamestack/valheim/data

Run:
gamestack doctor valheim
```

Technical details can be available under debug logging.

---

# 21. Error Messages

Every actionable error should attempt to communicate:

### WHAT

What failed?

### WHY

What likely caused it?

### ACTION

What should the user do?

Example:

```text
Could not create a backup.

Your server has only 620 MB of free disk space.
At least 2 GB is required for this backup.

Free some disk space and run:

gamestack backup valheim
```

Avoid dumping stack traces into normal output.

---

# 22. Logging

Normal logs should be useful without overwhelming users.

Support a debug mode.

Example:

```bash
gamestack --debug update valheim
```

Logs should be structured enough to diagnose:

- command execution
- Docker failures
- failed health checks
- backup failures
- update failures
- filesystem problems

Never include secrets.

---

# 23. Configuration

Configuration should be:

- human-readable
- versioned
- validated
- backwards-migratable where practical

Prefer YAML when appropriate.

Invalid configuration should fail early with a useful message.

Do not silently ignore unknown critical settings.

---

# 24. Path Handling

Use Python path abstractions such as `pathlib`.

Never build sensitive filesystem paths using unchecked string concatenation.

Validate:

- existence
- ownership where necessary
- expected parent directories
- available disk space

Tests must cover malicious or accidental unsafe paths.

---

# 25. Subprocess Execution

Avoid shell interpolation.

Prefer:

```python
subprocess.run(
    ["docker", "compose", "up", "-d"],
    check=True,
)
```

rather than:

```python
os.system(f"docker compose {user_input}")
```

Never pass untrusted user input through a shell unnecessarily.

Capture failures and translate them into GameStack errors.

---

# 26. Code Style

Prefer:

- small functions
- descriptive names
- explicit behavior
- type hints
- dataclasses or typed models where useful
- minimal hidden state

Avoid:

- clever metaprogramming
- deep inheritance
- global mutable state
- unnecessary design patterns
- premature abstraction

Code should be understandable by a professional developer returning to the project six months later.

---

# 27. Documentation Standards

Every meaningful user-facing feature must include documentation.

When adding a CLI command, document:

```text
Purpose
Syntax
Example
Expected result
Common failure modes
```

When adding a GamePack, document:

- supported version
- upstream image/project
- hardware recommendations
- exposed ports
- storage location
- backup behavior
- update behavior
- known limitations

---

# 28. Testing Requirements

Changes should include relevant tests.

## Unit tests

Required for deterministic core logic.

Examples:

- configuration
- pack validation
- backup retention
- paths
- version handling

## Integration tests

Use for:

- Docker orchestration
- filesystem behavior
- backup/restore
- CLI workflows

## Regression tests

Whenever fixing a reproducible bug, add a test that would have caught it where practical.

---

# 29. GamePack Acceptance Criteria

Before a GamePack is considered supported:

### Install

- Clean installation succeeds on supported OS.

### Lifecycle

- Start works.
- Stop works.
- Restart works.
- Status is accurate.

### Persistence

- Save/world survives container recreation.

### Backup

- Backup succeeds.
- Backup artifact can be identified.
- Retention works.

### Restore

- Known backup restores successfully.

### Update

- Backup occurs before update.
- Server starts successfully afterward.

### Diagnostics

- Common failures produce useful output.

### Documentation

- A target customer can follow Quick Start.

---

# 30. Pull Request / Change Expectations

A meaningful change should explain:

```text
Problem
Approach
User impact
Risks
Testing performed
```

Avoid large unrelated changes in one commit or PR.

Do not mix:

```text
architecture rewrite
+
new GamePack
+
formatting cleanup
```

unless they are genuinely inseparable.

Smaller changes are easier to review and maintain.

---

# 31. Refactoring Rules

Refactor when:

- existing code blocks required functionality
- duplication has become meaningful
- a second concrete use case demonstrates the need for abstraction
- tests protect behavior

Do not refactor because:

- another architecture feels more elegant
- a future feature might someday need it
- a framework is fashionable

Avoid rewriting stable code during product-validation phases.

---

# 32. Performance

GameStack itself is not performance-critical.

Optimize for:

1. reliability
2. maintainability
3. simplicity
4. safety

before micro-performance.

However, avoid actions that meaningfully disrupt game servers.

Examples:

- unnecessarily compressing huge backups while players are active
- aggressive polling
- consuming excessive memory
- blocking shutdown indefinitely

---

# 33. Third-Party Projects

GameStack depends on third-party open-source work.

For every dependency or container:

- identify its license
- preserve required notices
- document the upstream project
- avoid implying GameStack created the underlying server software
- track relevant versions
- avoid unsupported redistribution

Do not modify upstream software unnecessarily.

Prefer configuration and orchestration.

---

# 34. Commercial Awareness

Agents must consider product economics.

A feature that causes frequent manual support may be more harmful than helpful.

Before adding user-facing complexity, consider:

```text
Will this reduce or increase support burden?

Will a $10 customer reasonably expect help configuring this?

Can failure be diagnosed automatically?
```

Support cost is a first-class architectural concern.

---

# 35. Distribution Awareness

Features may generate multiple outputs.

When adding a new GamePack, consider whether the work can also produce:

- tutorial
- documentation
- GitHub example
- troubleshooting content
- landing-page material

Do not compromise engineering quality for marketing, but recognize that GameStack is a commercial product rather than an internal infrastructure platform.

---

# 36. Feature Decision Framework

For new feature requests, evaluate:

### User value

Does this solve a repeated customer problem?

### Frequency

How often will users encounter the problem?

### Complexity

How much code/maintenance does it require?

### Support impact

Will it reduce or increase support?

### Reusability

Does it benefit multiple GamePacks?

### Validation

Do we have evidence that users need it?

Prioritize features with:

```text
High user value
High frequency
Low/moderate complexity
Low support burden
High reuse
```

---

# 37. Game Selection Framework

Before creating a GamePack, evaluate:

- Active player population
- Dedicated server availability
- Persistent-world value
- Existing Docker support
- Hosting difficulty
- Search demand
- Community questions
- Update frequency
- Mod ecosystem
- Support complexity
- Existing easy-host competitors

Prefer games where:

> Hosting is desirable, technically annoying, and already supported by stable underlying server software.

---

# 38. Do Not Optimize for Feature Count

GameStack should win through:

```text
simplicity
reliability
safe defaults
documentation
integration
```

not:

```text
largest number of buttons
largest number of games
most configuration options
```

A GamePack that flawlessly handles five important operations is more valuable than one exposing fifty obscure settings.

---

# 39. MVP Decision Rule

When choosing whether something belongs in V0.1, ask:

> Could someone successfully install, maintain, back up, restore, and update their server without this feature?

If yes, the feature probably does not block V0.1.

---

# 40. Agent Completion Checklist

Before declaring implementation complete, verify:

- [ ] Change aligns with `PROJECT.md`.
- [ ] Scope is appropriate.
- [ ] User data is protected.
- [ ] Secrets are not exposed.
- [ ] Error messages are understandable.
- [ ] Relevant tests exist.
- [ ] Documentation is updated.
- [ ] No unnecessary dependency was added.
- [ ] No unsupported GamePack behavior was introduced.
- [ ] Existing functionality still works.
- [ ] Support burden was considered.
- [ ] Destructive behavior has safeguards.

---

# 41. When Requirements Are Ambiguous

Prefer the solution that is:

1. safer for user data
2. easier for beginners
3. easier to maintain
4. smaller in scope
5. reusable across GamePacks

Do not invent major product requirements.

Document assumptions clearly.

---

# 42. Guiding Principle

Remember what the customer is buying.

They are not paying for:

```text
YAML
Docker Compose
Python scripts
```

They are paying to avoid spending Saturday night troubleshooting a game server instead of playing with their friends.

Every GameStack feature should move the product closer to:

```text
Install
Configure
Play
```

with backups, updates, and recovery quietly handled underneath.