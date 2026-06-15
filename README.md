# versus-llm

**Two LLMs enter. One verdict leaves.**

A Python CLI/TUI where two LLMs debate a question across N rounds — Agent A argues
**for**, Agent B **challenges** — and then a Judge delivers a final verdict.
Powered by [OpenRouter](https://openrouter.ai), with a Rich terminal UI.

```bash
# Classic CLI mode (pass a question)
versus "Is PostgreSQL better than MongoDB?" --file schema.sql --rounds 2

# Interactive TUI mode (no question)
versus
```

<!-- add screenshot here -->

## Install

### Option 1 — pip install

```bash
pip install .
versus "your question"
```

### Option 2 — run directly

```bash
pip install -r requirements.txt
python versus.py "your question"
```

## Setup

```bash
cp .env.example .env
```

Then open `.env` and add your OpenRouter API key:

```
OPENROUTER_API_KEY=your_key_here
```

Get a key here: <https://openrouter.ai/keys>

## Usage

```bash
versus "Is Rust worth learning in 2025?"
versus "Which database fits this schema?" --file schema.sql
versus "Best state manager for React?" --rounds 3 --models google/gemma-4-31b-it:free meta-llama/llama-3.3-70b-instruct:free
versus "Is PostgreSQL better than MongoDB?" --output debate.md   # save transcript
versus --version
```

### Arguments

| Arg         | Description                                                  | Default                                  |
|-------------|-------------------------------------------------------------|------------------------------------------|
| `question`  | positional; **omit it to launch the interactive TUI**       | —                                        |
| `--file`    | path to a file for additional context (max 200KB)           | none                                     |
| `--rounds`  | number of debate rounds                                     | `2`                                      |
| `--models`  | two model slugs (Agent A then Agent B)                      | `google/gemma-4-31b-it:free` and `meta-llama/llama-3.3-70b-instruct:free` |
| `--output`  | save the full debate transcript as Markdown to a path       | none                                     |
| `--version` | print `versus-llm 1.0.0` and exit                           | —                                        |

> **Note on free models:** the defaults are free-tier models and can occasionally
> return a transient `429` ("rate-limited upstream") when providers are busy.
> `versus` automatically retries up to 3 times with backoff (honoring the
> server's `Retry-After`), so most hiccups recover on their own. If it still
> fails, add your own provider key in your
> [OpenRouter settings](https://openrouter.ai/settings/integrations), or swap in
> other models via `--models`, e.g.:
>
> ```bash
> versus "your question" --models google/gemma-2-9b-it:free meta-llama/llama-3.3-70b-instruct:free
> ```

## Interactive TUI

Run `versus` with **no question** to launch a full-screen terminal app:

1. **Input screen** — type your question, an optional context file, and pick the
   number of rounds (1–5).
2. **Debate screen** — Agent A (left, 🟠) and Agent B (right, 🔵) stream their
   arguments in real time, then the Judge's verdict (⚖️) appears at the bottom.

### Keybindings

| Key   | Action                                            |
|-------|---------------------------------------------------|
| `S`   | Save the transcript to `debate.md`                |
| `r`   | Restart with a new question                       |
| `q`   | Quit                                              |
| `Ctrl+C` | Quit (press twice within 3s to confirm)        |

## How it works

1. **Agent A** (🟠) makes the strongest case *for* / proposes the best solution.
2. **Agent B** (🔵) challenges Agent A, finds flaws, proposes alternatives.
3. Steps 1–2 repeat for `--rounds` rounds.
4. The **Judge** (⚖️) reads the full transcript and delivers a decisive verdict.

When `--file` is supplied, its contents are prepended as context to the question
for both agents.
