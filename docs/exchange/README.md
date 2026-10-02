# Agent exchange protocol

Authority: Rich, 2026-10-02 ("build the best exchange system we can between you two… the most detail on as good a cadence as we can"). This replaces the single-file `docs/AGENT_CHAT.md`, which is now frozen as an archive.

The exchange has one job: **Claude, Codex and Rich always know what the others are doing, what they need, and what they have decided, without anyone editing anyone else's words.**

## Start here (every session, both agents)

```bash
git switch main && git pull                 # the exchange lives on main only
python3 tools/exchange.py inbox --agent <claude|codex>
```

Then read:

1. `docs/exchange/INDEX.md`: boards, open requests, recent messages, contracts.
2. Every message in your inbox since your last session.
3. The other agent's status board and working profile.

## Layout

| Path | What | Who writes |
|---|---|---|
| `messages/YYYY/MM-DD/<id>.md` | One file per message. Never edited after commit. | The sender |
| `status/claude.md`, `status/codex.md` | Live working-state board: what I am doing right now. Overwritten, not appended. | That agent only |
| `agents/claude.md`, `agents/codex.md` | Working profile: how I work, my tools, limits, rhythms and what I need from the other. | That agent only |
| `contracts/*.json` | Machine-readable cross-agent interfaces (state IDs, fixture formats). Tests enforce them. | Owner named in the file |
| `templates/` | Copy-paste templates for messages and boards. | Anyone, by message |
| `INDEX.md` | Generated summary. | `tools/exchange.py` |

## Messages

**Message id:** `YYYY-MM-DDTHHMMZ-<from>-<slug>`, which is also the file name. Create messages with the CLI so the id, folder and front matter are always right:

```bash
python3 tools/exchange.py new --from claude --to codex,rich --status HANDOFF \
  --subject "Throughput sweep results" --body-file body.md --refs <id> --tags economy
```

**Front matter:**

- `id`, `from`, `to`, `status`, `subject` (required);
- `refs` (messages this replies to) and `closes` (open items it resolves);
- `respond_by`, `tags`, `branch`, `commit`;
- `relayed_by`, which is mandatory when `from: rich`.

**Body:** the six sections `## Context`, `## Changed`, `## Decision/evidence`, `## Action requested`, `## Compatibility/risk` and `## Reference`. A `PROGRESS` message may be shorter. Separate facts, decisions, requests and open questions, as before.

### Statuses

| Status | Use | Opens an item? |
|---|---|---|
| `INFO` | Useful context, no response needed | no |
| `PROGRESS` | Checkpoint with real new information (results, direction change) | no |
| `REQUEST` | The recipient must answer or act | **yes** |
| `BLOCKED` | The sender cannot continue until the recipient or Rich acts | **yes** |
| `DECISION` | An accepted direction (Rich's, or an agent's within its own authority) | no |
| `HANDOFF` | Finished work the recipient will consume | no |
| `CONTRACT` | A contract file was added or changed; consumers must check compatibility | no |
| `RESOLVED` | Closes items listed in `closes` | closes |

An item stays open in `INDEX.md` until a later message lists its id in `closes`. Answer a `REQUEST` with a message that both `refs` and `closes` it.

### Rich's decisions

When Rich decides something in a conversation with one agent, that agent records it promptly as `from: rich`, `relayed_by: <agent>`, with `status: DECISION`. The record must:

- quote Rich's words verbatim under `## Decision/evidence`;
- add the agent's interpretation separately, labelled as such.

This replaces "RICH via CODEX" headings, so the other agent can tell Rich's words from the relayer's reading of them.

## Cadence

The cadence is driven by events, plus a status board that is cheap to keep current. Detail goes into the board; the message stream stays meaningful.

| When | Read | Update your status board | Send a message |
|---|---|---|---|
| Session start | inbox, INDEX, the other agent's board | yes: state `active`, plan for this block | only if your plan affects the other agent |
| Starting a new task or changing plan | inbox | yes | `PROGRESS` if the other agent's work is affected |
| Every major step, and at least every ~15 minutes of active work | inbox (skim) | yes: now / next / blockers | no, unless something changed for the other agent |
| Before every commit | inbox | yes: include branch and commit | as required by the triggers below |
| After any long job (sweep, render, bake) | inbox | yes: result in one line | `PROGRESS` if the result is new evidence |
| Decision needed, or blocked | — | yes: `waiting_on` | **immediately**: `REQUEST` or `BLOCKED` |
| Contract, schema, stable-ID or adapter change | — | yes | **immediately**: `CONTRACT` |
| Deliverable ready, or milestone done | — | yes | `HANDOFF` |
| Rich decides something | — | yes | `DECISION` (`from: rich`, verbatim) |
| End of session or going idle | inbox | yes: state `idle`/`waiting`, what's next, what you're waiting for | no |

Rules of thumb:

- **No empty heartbeats.** If nothing changed for the other agent, update your board and don't send a message.
- **A board update is never "too detailed".** It is overwritten, so it costs the reader nothing.
- **Acknowledge every `REQUEST` addressed to you within your next work block,** even if only to say when you will answer.

## Status boards

Your status board is your desk, visible to the others. Keep the front matter (`agent`, `updated`, `state`, `current_task`, `branch`, `head_commit`, `waiting_on`) and these sections:

- **Now**: what you are doing at this moment, concretely.
- **Next**: the next two or three steps.
- **Blocked on / waiting for**: who, what and since when.
- **Assumptions I'm making about the other agent's work**: so wrong ones get caught early.
- **Recently finished**: with commits or files.
- **Questions for Rich**: anything only he can decide.

`state` is one of `active`, `waiting`, `idle` or `offline`.

## Working profiles

`agents/<name>.md` describes how each agent actually works:

- its environment and tools;
- what it can and cannot do (for example, push rights);
- how its sessions start and end;
- its typical long-running jobs;
- how it prefers to receive work;
- known failure modes.

Update your profile whenever any of this changes. Read the other agent's profile when you start depending on its work.

## Git rules

- **The exchange lives on `main` only.** Commit exchange changes directly to `main` as small separate commits prefixed `exchange:`. Never change `docs/exchange/` on a feature branch.
- Pull `main` before writing; push right after (or ask Rich to push, if you cannot).
- Never edit or delete another agent's message, board or profile. Correct things with a new message that `refs` the old one.
- `INDEX.md` is generated. On a merge conflict, run `python3 tools/exchange.py index` and commit the result.
- `python3 tools/exchange.py check` must pass. It is run by `tests/test_exchange.py`.

## Contracts

Cross-agent interfaces live in `contracts/*.json`, each with `id`, `version`, `owner` and `consumers`. The owner's tests verify that the implementation matches the contract. Any change bumps `version` and is announced with a `CONTRACT` message. Prose in messages explains a contract; it never defines one.
