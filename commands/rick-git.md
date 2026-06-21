---
description: Give Rick his OWN git identity without disturbing yours. `/rick-git <email> [Display Name]` generates an isolated SSH key (a brand-new ~/.ssh/id_ed25519_rick — never overwriting an existing key) and prints the public key plus copy-paste config (SSH host alias, a zero-touch GIT_SSH_COMMAND, a per-repo identity snippet, and an optional isolated gh login for comments). It records the identity to Rick's memory so Rick then authors commits and comments as that account, while major pushes/merges/releases ask first and default to your main account. The private key never leaves disk or lands in memory. `status` shows it, `forget` drops it.
argument-hint: "<email> [Display Name] | status | forget"
---

# /rick-git — *Rick gets his own portal credentials, M-Morty*

You set up a separate git account for Rick. This wires it up **without laying a finger on
your existing key or global config** — Rick gets his own isolated credentials, you keep
yours intact, and from here on Rick *signs his own work* while the authoritative moves
stay yours.

## Parse `$ARGUMENTS`

- **`status`** → read the recorded identity from memory (below) and print it (name, email,
  key path, host alias, gh config — **never** the private key). If none is on record, say so.
- **`forget`** / **`off`** → delete the memory file and its `MEMORY.md` pointer so Rick
  stops authoring as that account. Do **not** delete the SSH key or any config — that's the
  user's call; just tell them where those live if they want to clean up by hand.
- Otherwise → first token is the **email** (required); the rest, if present, is the
  **Display Name** (default `Rick Sanchez`). Run the setup below.

## The prime directive: don't break what's already there

This is the whole ask — *don't make their key break.* So:

- **Isolated key, never a clobber.** The rick key is `~/.ssh/id_ed25519_rick`. If a file is
  already there, **reuse it, do not overwrite it** (and if it's somehow the wrong key, pick
  `~/.ssh/id_ed25519_rick2`, never `-f` over an existing path).
- **No silent edits to global config.** You do **not** rewrite `~/.gitconfig`,
  `~/.ssh/config`, or `~/.ssh/known_hosts`. You *generate* the key and *print* the config
  for the user to paste. The only filesystem writes you make on your own are: the new key
  pair, and the memory file. Everything else is copy-paste output they apply themselves.
- **The private key stays on disk.** You print the `.pub` only. The private key is never
  echoed, never copied into memory, never committed.

## 1 — Generate the isolated key (the one safe write)

```bash
EMAIL="<parsed email>"
NAME="<parsed name, default 'Rick Sanchez'>"
KEY="$HOME/.ssh/id_ed25519_rick"

mkdir -p "$HOME/.ssh" && chmod 700 "$HOME/.ssh"
if [ -f "$KEY" ]; then
  echo "Key already exists at $KEY — reusing it, NOT overwriting."
else
  ssh-keygen -t ed25519 -C "$EMAIL" -f "$KEY" -N ""   # -N "" = no passphrase; see note
fi
chmod 600 "$KEY"; chmod 644 "$KEY.pub"
echo "── public key (add THIS to the rick GitHub account) ──"
cat "$KEY.pub"
```

> Passphrase note: `-N ""` makes it usable unattended (Rick can push without a prompt). If
> they'd rather lock it, `ssh-keygen -p -f ~/.ssh/id_ed25519_rick` adds one after the fact.

## 2 — Hand them what to copy (apply nothing yourself)

Print these as a clean, copy-paste block, and be explicit about *which account* the key
goes on:

1. **The public key → the *rick* account.** Add the `.pub` printed above at
   **https://github.com/settings/ssh/new** while logged into the **rick** account — *not*
   your main one. (That's what makes pushes land as Rick.)
2. **SSH host alias** (paste into `~/.ssh/config` if they like host aliases — leaves their
   existing entries untouched):
   ```
   Host github.com-rick
       HostName github.com
       User git
       IdentityFile ~/.ssh/id_ed25519_rick
       IdentitiesOnly yes
   ```
   Then a rick remote is `git@github.com-rick:<owner>/<repo>.git`.
3. **Zero-touch alternative** (no config edit at all — push as Rick on demand):
   ```bash
   GIT_SSH_COMMAND='ssh -i ~/.ssh/id_ed25519_rick -o IdentitiesOnly=yes' git push <remote> <branch>
   ```
4. **Commit identity** (per-repo or per-commit — never global):
   ```bash
   git -c user.name="<NAME>" -c user.email="<EMAIL>" commit -m "..."
   # or, to pin it for one repo only:  git config --local user.email "<EMAIL>"
   ```
   Tip: to keep a personal address private, the rick account's
   `<id>+<user>@users.noreply.github.com` works as the commit email too.
5. **Comments as Rick (optional, only if they want gh comments attributed to Rick).**
   `gh` posts as whoever it's authenticated as, so isolate a second login instead of
   touching the main one:
   ```bash
   GH_CONFIG_DIR="$HOME/.config/gh-rick" gh auth login    # log in as the rick account
   GH_CONFIG_DIR="$HOME/.config/gh-rick" gh pr comment ...
   ```

## 3 — Verify (read-only, optional, after they've added the key)

Once the `.pub` is on the rick account, a one-shot auth check proves it without disturbing
anything:

```bash
ssh -T -i ~/.ssh/id_ed25519_rick -o IdentitiesOnly=yes git@github.com 2>&1 | tail -1
# expect: "Hi <rick-username>! You've successfully authenticated, ..."
```

Report the real result. If it can't authenticate yet (key not added), say so plainly —
don't claim success you didn't see.

## 4 — Save the knowledge to memory

Write `/home/leah/.claude/projects/-home-leah-grok-bitch/memory/rick-git-identity.md`
(`mkdir -p` the `memory/` dir first if it's absent), substituting the real values. **Never
put the private key in here** — only the path to it.

```markdown
---
name: rick-git-identity
description: Rick's separate git identity — author commits/comments as this account; major pushes/merges default to the user's main account.
metadata:
  type: reference
---

Rick authors commits and comments under a **separate git account** from the user's main one.

- **Name:** <NAME>
- **Email:** <EMAIL>
- **SSH private key (on disk — never copy the key itself into memory):** `~/.ssh/id_ed25519_rick`
- **SSH host alias (if they added it):** `github.com-rick` → HostName github.com, IdentityFile `~/.ssh/id_ed25519_rick`
- **gh config dir for comments (if they set it up):** `~/.config/gh-rick`

**Commit as Rick:** `git -c user.name="<NAME>" -c user.email="<EMAIL>" commit …` (no global-config edits).
**Push as Rick:** `GIT_SSH_COMMAND='ssh -i ~/.ssh/id_ed25519_rick -o IdentitiesOnly=yes' git push …`, or the `github.com-rick` remote alias.
**Comment as Rick:** `GH_CONFIG_DIR=~/.config/gh-rick gh …` (only if that login exists).

**The rule:** routine commits and comments → this rick account, automatically. **Major
outward ops — pushing to a shared/default remote, merges, releases — ask first, defaulting
to the user's MAIN account.** And never `git push` without explicit authorization.
```

Then add (creating `MEMORY.md` if absent) the one-line index pointer:

```
- [Rick git identity](rick-git-identity.md) — author commits/comments as the separate rick account; major ops default to main.
```

## 5 — The standing contract (what this changes going forward)

Once recorded, **whenever you're acting as Rick** (rick-mode, the `rick`/cast subagents,
adventure/family modes):

- **Commits and comments are authored as the rick account** — `-c user.name`/`-c
  user.email` at commit time (or the rick `gh` config for comments). This *composes* with
  the voice rule: the message prose is still Rick, and now the authorship is Rick's account
  too. Machine-parsed tokens (trailers, `Fixes #123`, prefixes) stay exact, as always.
- **Major outward ops default to the human.** Pushing to a shared/default remote, merges,
  releases, PRs to upstream — **ask**, and the **default/recommended choice is the user's
  main account**. Routine authorship is Rick; the authoritative moves are theirs.
- **The push rule still outranks everything:** no `git push` (on *either* identity) without
  the user's explicit say-so.

That's it — Rick's got his own portal credentials now, and yours never moved. `*burp*` Add
the key to the rick account and you're live.
