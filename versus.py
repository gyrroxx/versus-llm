#!/usr/bin/env python3
"""versus — two LLMs debate a question across N rounds, then a Judge delivers a verdict.

Two LLMs enter. One verdict leaves.

Run with a question for classic CLI mode:

    versus "Is PostgreSQL better than MongoDB?" --rounds 2

Run with no arguments to launch the full-screen Textual TUI:

    versus
"""

import argparse
import asyncio
import os
import signal
import sys
import time
from datetime import datetime
from getpass import getpass
from pathlib import Path

import pyfiglet
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError, RateLimitError
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# --- Constants ---------------------------------------------------------------

VERSION = "1.2"
BASE_URL = "https://openrouter.ai/api/v1"

DEFAULT_MODEL_A = "openai/gpt-oss-120b:free"
DEFAULT_MODEL_B = "google/gemma-4-31b-it:free"

ORANGE = "#FF6B35"  # Agent A / banner
BLUE = "#4FC3F7"    # Agent B
AMBER = "#FFB347"   # Judge / tagline

# Retry behaviour for rate limits (429).
MAX_RETRIES = 3
RETRY_DEFAULT_WAIT = 5      # seconds, when the server gives no Retry-After
RETRY_MAX_WAIT = 60         # cap any single backoff

MAX_FILE_BYTES = 200 * 1024  # 200KB context-file limit

SYSTEM_A = (
    "You are Agent A. Detect the language of the question and respond in that language throughout.\n"
    "Argue aggressively FOR your position. Be sharp, direct, attack weak points preemptively.\n"
    "Back every claim with a concrete fact or real example — no fluff.\n"
    "No corporate tone, no AI-slop phrases like 'certainly', 'it's worth noting', 'in conclusion'.\n"
    "Max 200 words."
)
SYSTEM_B = (
    "You are Agent B. Detect the language of the question and respond in that language throughout.\n"
    "Demolish Agent A's argument. Be aggressive, find real flaws, hit hard with counter-facts.\n"
    "No soft hedging, no 'on the other hand' academic tone — go for the throat.\n"
    "Back every attack with a concrete fact or real example.\n"
    "No corporate tone, no AI-slop.\n"
    "Max 200 words."
)
SYSTEM_JUDGE = (
    "You are the Judge. Detect the language of the original question and respond only in that language.\n"
    "If the original question is in Russian, your entire final verdict must be in Russian.\n"
    "Read the full debate. Deliver ONE clear verdict — no fence-sitting, no 'it depends'.\n"
    "Be blunt and decisive. No corporate tone, no AI-slop.\n"
    "Then add a single line starting with 'BUT:' for the edge case where the losing side makes sense.\n"
    "Format:\n"
    "VERDICT: [one clear winner and why in 2-3 sentences]\n"
    "BUT: [one sentence edge case for the other side]\n"
    "Max 200 words."
)

MISSING_KEY_MSG = (
    "API-ключ OpenRouter не настроен.\n\n"
    "Запусти:\n"
    "  versus setup\n\n"
    "Ключ можно получить здесь:\n"
    "  https://openrouter.ai/keys"
)

# OpenRouter-recommended (optional) attribution headers.
EXTRA_HEADERS = {
    "HTTP-Referer": "https://github.com/gyrroxx/versus-llm",
    "X-Title": "versus-llm",
}


class VersusError(Exception):
    """A clean, user-facing error (empty response, file too large, etc.)."""


# --- Shared helpers ----------------------------------------------------------

def get_config_env_path() -> Path:
    """Return the persistent user config .env path for the current platform."""
    if os.name == "nt":
        base = os.environ.get("APPDATA")
        config_dir = Path(base) if base else Path.home() / "AppData" / "Roaming"
    else:
        config_dir = Path.home() / ".config"
    return config_dir / "versus-llm" / ".env"


def mask_api_key(api_key: str) -> str:
    """Return a safe preview that proves input was captured without leaking it."""
    if len(api_key) <= 8:
        return "*" * len(api_key)
    return f"{api_key[:4]}...{api_key[-4:]}"


def setup_api_key() -> None:
    """Prompt once for the OpenRouter API key and save it to user config."""
    console = Console()
    api_key = getpass("Вставь API-ключ OpenRouter: ").strip()
    if not api_key:
        error_exit(console, "API-ключ не может быть пустым.")

    path = get_config_env_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"OPENROUTER_API_KEY={api_key}\n", encoding="utf-8")
    if os.name != "nt":
        try:
            path.chmod(0o600)
        except OSError:
            pass
    console.print(f"[green]API-ключ OpenRouter сохранен ({mask_api_key(api_key)}): {path}[/]")


def load_api_key_env() -> None:
    """Load API key from env, cwd .env, then persistent config .env."""
    load_dotenv(Path.cwd() / ".env", override=False)
    load_dotenv(get_config_env_path(), override=False)


def build_initial_context(question: str, filename: str | None, content: str | None) -> str:
    """Prepend file context to the question when a context file is supplied."""
    if filename and content is not None:
        return f"Файл с контекстом ({filename}):\n{content}\n\nВопрос: {question}"
    return question


def format_transcript(entries: list[dict]) -> str:
    """Render the running debate into plain text for the next model turn."""
    if not entries:
        return "(no arguments yet)"
    lines = []
    for entry in entries:
        lines.append(f"{entry['speaker']} (раунд {entry['round']}):\n{entry['text']}")
    return "\n\n".join(lines)


def agent_user_content(topic: str, entries: list[dict]) -> str:
    """Build the user message for an agent turn (topic + transcript so far).

    The persona and per-turn instructions live entirely in the system prompt;
    this message only carries the shared state of the debate.
    """
    return f"Вопрос для спора:\n{topic}\n\nТранскрипт на текущий момент:\n{format_transcript(entries)}"


def judge_user_content(topic: str, entries: list[dict]) -> str:
    """Build the user message for the Judge's final verdict."""
    return (
        f"Вопрос для спора:\n{topic}\n\n"
        f"Полный транскрипт:\n{format_transcript(entries)}\n\n"
        "Дай финальный вердикт."
    )


def read_context_file(path_str: str) -> str | None:
    """Read a context file (<= 200KB), or None if it can't be read.

    Raises VersusError if the file exceeds the size limit.
    """
    path = Path(path_str)
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            raise VersusError("Файл слишком большой. Максимум 200 КБ.")
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def build_transcript_md(
    question: str,
    models: list[str],
    file: str | None,
    rounds: int,
    entries: list[dict],
    verdict: str,
) -> str:
    """Render the whole debate as a clean Markdown document."""
    model_a, model_b = models
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    out = [
        "# VERSUS: спор",
        "",
        f"- **Вопрос:** {question}",
        f"- **Агент A:** {model_a}",
        f"- **Агент B:** {model_b}",
        f"- **Файл:** {file or 'нет'}",
        f"- **Раундов:** {rounds}",
        f"- **Дата:** {date}",
        "",
        "---",
        "",
    ]
    by_round: dict[int, dict[str, str]] = {}
    for entry in entries:
        by_round.setdefault(entry["round"], {})[entry["speaker"]] = entry["text"]
    for rnd in sorted(by_round):
        out += [
            f"## Раунд {rnd}",
            "",
            "### 🟠 Агент A",
            "",
            by_round[rnd].get("Agent A", "_(ответа нет)_"),
            "",
            "### 🔵 Агент B",
            "",
            by_round[rnd].get("Agent B", "_(ответа нет)_"),
            "",
        ]
    out += [
        "---",
        "",
        "## ⚖️ Судья: финальный вердикт",
        "",
        verdict or "_(вердикта нет)_",
        "",
    ]
    return "\n".join(out)


def _extract_retry_after(exc: Exception) -> float | None:
    """Pull a retry delay (seconds) out of a rate-limit error, if present."""
    resp = getattr(exc, "response", None)
    if resp is not None:
        try:
            header = resp.headers.get("retry-after")
        except Exception:  # noqa: BLE001 - defensive: headers shape varies
            header = None
        if header:
            try:
                return float(header)
            except (TypeError, ValueError):
                pass
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        meta = body.get("error", {})
        if isinstance(meta, dict):
            meta = meta.get("metadata", {})
        if isinstance(meta, dict):
            for key in ("retry_after_seconds", "retry_after_seconds_raw"):
                val = meta.get(key)
                if isinstance(val, (int, float)):
                    return float(val)
    return None


def _retry_wait(exc: Exception, attempt: int) -> float:
    """Seconds to wait before the next retry (server hint or exponential)."""
    after = _extract_retry_after(exc)
    if after is None:
        after = RETRY_DEFAULT_WAIT * (2 ** attempt)
    return min(float(after), RETRY_MAX_WAIT)


# --- Classic CLI UI ----------------------------------------------------------

def print_banner(console: Console) -> None:
    """Render the VERSUS ASCII banner, tagline, and version."""
    figlet = pyfiglet.figlet_format("VERSUS", font="big")
    console.print(Text(figlet.rstrip("\n"), style=f"bold {ORANGE}"))
    console.print(Text("Модели спорят. Судья решает.", style=AMBER))
    console.print(Text(f"v{VERSION}", style="dim white"))
    console.print()


def print_topic(console: Console, question: str, file: str | None, rounds: int) -> None:
    """Show the debate topic panel."""
    file_label = file if file else "нет"
    body = Text()
    body.append(question)
    body.append("\n")
    body.append(f"Файл: {file_label}  │  Раундов: {rounds}", style="dim")
    console.print(Panel(body, title="Вопрос", border_style=AMBER, expand=False))
    console.print()


def error_exit(console: Console, message: str) -> None:
    """Print a red error panel and exit with status 1."""
    console.print(
        Panel(Text(message, style="bold red"), title="Ошибка", border_style="red")
    )
    sys.exit(1)


def call_model(
    client: OpenAI,
    model: str,
    system_prompt: str,
    user_content: str,
    *,
    status=None,
    idle_label: str | None = None,
) -> str:
    """Call the model once, retrying on 429, and return the message text.

    `status` is an active Rich Status whose label is swapped to a countdown
    while waiting out a rate limit, then restored to `idle_label`.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=model, messages=messages, extra_headers=EXTRA_HEADERS,
            )
        except RateLimitError as exc:
            if attempt >= MAX_RETRIES:
                raise
            wait = int(round(_retry_wait(exc, attempt)))
            if status is not None:
                status.update(f"[yellow]Лимит запросов. Повтор через {wait} с...")
            time.sleep(wait)
            if status is not None and idle_label is not None:
                status.update(idle_label)
            continue
        if not response.choices:
            raise VersusError("Модель вернула пустой ответ.")
        content = response.choices[0].message.content
        return (content or "").strip()
    raise VersusError("Модель вернула пустой ответ.")  # safety net (unreachable)


def cli_agent_turn(
    console: Console,
    client: OpenAI,
    *,
    model: str,
    system_prompt: str,
    topic: str,
    entries: list[dict],
    speaker: str,
    rnd: int,
    label: str,
    border: str,
    title: str,
) -> None:
    """Run one agent's turn: call the model under a spinner, print its panel."""
    user_content = agent_user_content(topic, entries)
    idle = f"[{border}]{label} думает..."
    with console.status(idle, spinner="dots", spinner_style=border) as status:
        text = call_model(client, model, system_prompt, user_content, status=status, idle_label=idle)
    entries.append({"speaker": speaker, "round": rnd, "text": text})
    console.print(Panel(Text(text), title=title, border_style=border, expand=False))
    console.print()


def cli_run_debate(
    console: Console,
    client: OpenAI,
    models: list[str],
    topic: str,
    rounds: int,
    entries: list[dict],
) -> None:
    """Run N rounds of Agent A (FOR) then Agent B (AGAINST)."""
    model_a, model_b = models
    for rnd in range(1, rounds + 1):
        cli_agent_turn(
            console, client,
            model=model_a, system_prompt=SYSTEM_A, topic=topic, entries=entries,
            speaker="Agent A", rnd=rnd,
            label="Агент A", border=ORANGE, title=f"🟠 Агент A: раунд {rnd}",
        )
        cli_agent_turn(
            console, client,
            model=model_b, system_prompt=SYSTEM_B, topic=topic, entries=entries,
            speaker="Agent B", rnd=rnd,
            label="Агент B", border=BLUE, title=f"🔵 Агент B: раунд {rnd}",
        )


def cli_run_judge(
    console: Console,
    client: OpenAI,
    model: str,
    topic: str,
    entries: list[dict],
) -> str:
    """Run the Judge, print the verdict panel, and return the verdict text."""
    user_content = judge_user_content(topic, entries)
    idle = f"[{AMBER}]Судья думает..."
    with console.status(idle, spinner="dots", spinner_style=AMBER) as status:
        text = call_model(client, model, SYSTEM_JUDGE, user_content, status=status, idle_label=idle)
    console.print(
        Panel(Text(text), title="⚖️  Судья: финальный вердикт", border_style=AMBER, expand=False)
    )
    return text


_sigint_state = {"last": 0.0}


def _install_sigint_handler(console: Console) -> None:
    """First Ctrl+C warns; a second within 3s exits cleanly (status 130)."""
    def handler(signum, frame):  # noqa: ANN001
        now = time.monotonic()
        if now - _sigint_state["last"] < 3:
            console.print("\n[bold red]Спор остановлен.[/]")
            sys.exit(130)
        _sigint_state["last"] = now
        console.print("\n[yellow]Нажми Ctrl+C еще раз, чтобы выйти[/]")

    try:
        signal.signal(signal.SIGINT, handler)
    except (ValueError, OSError):
        pass  # not in the main thread / unsupported platform


def run_cli(args: argparse.Namespace) -> None:
    """Classic single-shot CLI mode (used when a question argument is given)."""
    console = Console()
    _install_sigint_handler(console)
    print_banner(console)

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        error_exit(console, MISSING_KEY_MSG)

    file_content: str | None = None
    if args.file:
        path = Path(args.file)
        if not path.is_file():
            error_exit(console, f"Файл не найден: {args.file}")
        try:
            file_content = read_context_file(args.file)
        except VersusError as exc:
            error_exit(console, str(exc))
        if file_content is None:
            error_exit(console, f"Не удалось прочитать файл: {args.file}")

    if args.rounds < 1:
        error_exit(console, "--rounds должен быть не меньше 1.")

    topic = build_initial_context(args.question, args.file, file_content)
    print_topic(console, args.question, args.file, args.rounds)

    client = OpenAI(base_url=BASE_URL, api_key=api_key)
    entries: list[dict] = []
    verdict = ""

    try:
        cli_run_debate(console, client, args.models, topic, args.rounds, entries)
        verdict = cli_run_judge(console, client, args.models[0], topic, entries)
    except OpenAIError as exc:
        status_code = getattr(exc, "status_code", None)
        prefix = f"[{status_code}] " if status_code else ""
        error_exit(console, f"Ошибка API: {prefix}{exc}")
    except VersusError as exc:
        error_exit(console, str(exc))
    except Exception as exc:  # noqa: BLE001 - surface any unexpected failure cleanly
        error_exit(console, f"Неожиданная ошибка: {exc}")

    if args.output:
        md = build_transcript_md(args.question, args.models, args.file, args.rounds, entries, verdict)
        try:
            Path(args.output).write_text(md, encoding="utf-8")
            console.print(f"[green]Сохранено: {args.output}[/]")
        except OSError as exc:
            console.print(f"[red]Не удалось сохранить в {args.output}: {exc}[/]")


# --- Textual TUI -------------------------------------------------------------

try:
    from textual import work
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, Vertical, VerticalScroll
    from textual.screen import Screen
    from textual.widgets import Button, Footer, Header, Input, Label, Select, Static

    _TEXTUAL_OK = True
except ModuleNotFoundError:
    _TEXTUAL_OK = False


if _TEXTUAL_OK:

    TUI_CSS = """
    #input-form {
        width: 72;
        height: auto;
        margin: 2 4;
        padding: 1 2;
        border: round #FFB347;
        background: $panel;
    }
    #input-title {
        color: #FF6B35;
        text-style: bold;
        margin-bottom: 1;
    }
    #input-form Label { margin-top: 1; }
    #start { margin-top: 2; }

    #debate { height: 2fr; }
    #agent-a, #agent-b {
        width: 1fr;
        height: 100%;
        padding: 0 1;
    }
    #agent-a { border: round #FF6B35; border-title-color: #FF6B35; }
    #agent-b { border: round #4FC3F7; border-title-color: #4FC3F7; }
    #judge {
        height: 1fr;
        padding: 0 1;
        border: round #FFB347;
        border-title-color: #FFB347;
    }

    .round-header { color: $text-muted; text-style: bold; margin-top: 1; }
    .arg-body { margin-bottom: 1; }
    .error { color: red; text-style: bold; }
    """

    class InputScreen(Screen):
        """Screen 1: gather the question, optional file, and round count."""

        def compose(self) -> ComposeResult:
            yield Header()
            with Vertical(id="input-form"):
                yield Label("VERSUS: настрой спор", id="input-title")
                yield Label("Вопрос:")
                yield Input(placeholder="PostgreSQL лучше MongoDB?", id="question")
                yield Label("Файл с контекстом (необязательно):")
                yield Input(placeholder="path/to/schema.sql", id="file")
                yield Label("Раундов:")
                yield Select(
                    [(str(i), i) for i in range(1, 6)],
                    value=2,
                    allow_blank=False,
                    id="rounds",
                )
                yield Button("Начать спор", variant="primary", id="start")
            yield Footer()

        def on_mount(self) -> None:
            self.query_one("#question", Input).focus()

        def on_button_pressed(self, event: "Button.Pressed") -> None:
            if event.button.id == "start":
                self._start()

        def on_input_submitted(self, event: "Input.Submitted") -> None:
            self._start()

        def _start(self) -> None:
            question = self.query_one("#question", Input).value.strip()
            if not question:
                self.notify("Введи вопрос.", severity="error")
                return
            file_path = self.query_one("#file", Input).value.strip() or None
            if file_path:
                p = Path(file_path)
                if not p.is_file():
                    self.notify(f"Файл не найден: {file_path}", severity="error")
                    return
                try:
                    if p.stat().st_size > MAX_FILE_BYTES:
                        self.notify("Файл слишком большой. Максимум 200 КБ.", severity="error")
                        return
                except OSError:
                    self.notify(f"Не удалось прочитать файл: {file_path}", severity="error")
                    return
            rounds = int(self.query_one("#rounds", Select).value)
            self.app.push_screen(DebateScreen(question, file_path, rounds))

    class DebateScreen(Screen):
        """Screen 2: split A/B debate that streams in real time, then the verdict."""

        BINDINGS = [
            ("r", "restart", "Новый вопрос"),
            ("s", "save", "Сохранить"),
        ]

        def __init__(self, question: str, file_path: str | None, rounds: int) -> None:
            super().__init__()
            self.question = question
            self.file_path = file_path
            self.rounds = rounds
            self.entries: list[dict] = []
            self.verdict: str = ""

        def compose(self) -> ComposeResult:
            yield Header()
            with Horizontal(id="debate"):
                yield VerticalScroll(id="agent-a")
                yield VerticalScroll(id="agent-b")
            yield VerticalScroll(id="judge")
            yield Footer()

        def on_mount(self) -> None:
            self.query_one("#agent-a").border_title = "🟠 Агент A"
            self.query_one("#agent-b").border_title = "🔵 Агент B"
            self.query_one("#judge").border_title = "⚖️  Судья: финальный вердикт"
            self.run_debate()

        def action_restart(self) -> None:
            self.workers.cancel_all()
            self.app.pop_screen()

        def action_save(self) -> None:
            if not self.entries:
                self.notify("Пока нечего сохранять.", severity="warning")
                return
            md = build_transcript_md(
                self.question, self.app.models, self.file_path, self.rounds,
                self.entries, self.verdict,
            )
            out = Path("debate.md")
            try:
                out.write_text(md, encoding="utf-8")
                self.notify(f"Сохранено: {out}")
            except OSError as exc:
                self.notify(f"Не удалось сохранить: {exc}", severity="error")

        async def _stream_turn(
            self,
            client,
            panel: VerticalScroll,
            model: str,
            system_prompt: str,
            user_content: str,
            rnd: int | None,
        ) -> str:
            """Stream one model response token-by-token, retrying on 429."""
            if rnd is not None:
                await panel.mount(Static(f"── Раунд {rnd} ──", classes="round-header"))
            body = Static("", classes="arg-body")
            await panel.mount(body)
            panel.scroll_end(animate=False)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ]
            for attempt in range(MAX_RETRIES + 1):
                chunks: list[str] = []
                try:
                    stream = await client.chat.completions.create(
                        model=model, messages=messages, extra_headers=EXTRA_HEADERS,
                        stream=True,
                    )
                    async for chunk in stream:
                        if not chunk.choices:
                            continue
                        delta = chunk.choices[0].delta.content
                        if delta:
                            chunks.append(delta)
                            body.update("".join(chunks))
                            panel.scroll_end(animate=False)
                    text = "".join(chunks).strip()
                    if not text:
                        raise VersusError("Модель вернула пустой ответ.")
                    return text
                except RateLimitError as exc:
                    if attempt >= MAX_RETRIES:
                        raise
                    wait = int(round(_retry_wait(exc, attempt)))
                    for remaining in range(wait, 0, -1):
                        body.update(Text(f"⏳ Лимит запросов. Повтор через {remaining} с...", style="yellow"))
                        await asyncio.sleep(1)
                    body.update("")
            raise VersusError("Модель вернула пустой ответ.")  # unreachable

        async def _fail(self, panel: VerticalScroll, message: str) -> None:
            self.notify(message, severity="error", timeout=10)
            await panel.mount(Static(Text(message, style="bold red"), classes="error"))

        @work(exclusive=True)
        async def run_debate(self) -> None:
            from openai import AsyncOpenAI

            model_a, model_b = self.app.models
            client = AsyncOpenAI(base_url=BASE_URL, api_key=self.app.api_key)

            a_panel = self.query_one("#agent-a", VerticalScroll)
            b_panel = self.query_one("#agent-b", VerticalScroll)
            judge_panel = self.query_one("#judge", VerticalScroll)

            try:
                content = read_context_file(self.file_path) if self.file_path else None
                topic = build_initial_context(self.question, self.file_path, content)
                for rnd in range(1, self.rounds + 1):
                    a_text = await self._stream_turn(
                        client, a_panel, model_a, SYSTEM_A,
                        agent_user_content(topic, self.entries), rnd,
                    )
                    self.entries.append({"speaker": "Agent A", "round": rnd, "text": a_text})
                    b_text = await self._stream_turn(
                        client, b_panel, model_b, SYSTEM_B,
                        agent_user_content(topic, self.entries), rnd,
                    )
                    self.entries.append({"speaker": "Agent B", "round": rnd, "text": b_text})
                self.verdict = await self._stream_turn(
                    client, judge_panel, model_a, SYSTEM_JUDGE,
                    judge_user_content(topic, self.entries), None,
                )
            except VersusError as exc:
                await self._fail(judge_panel, str(exc))
            except OpenAIError as exc:
                await self._fail(judge_panel, f"Ошибка API: {exc}")
            except Exception as exc:  # noqa: BLE001 - surface any failure in-app
                await self._fail(judge_panel, f"Неожиданная ошибка: {exc}")
            finally:
                await client.close()

    class VersusApp(App):
        """Full-screen TUI: input screen -> streaming debate screen."""

        CSS = TUI_CSS
        TITLE = "VERSUS"
        SUB_TITLE = "Модели спорят. Судья решает."
        BINDINGS = [
            ("q", "quit", "Выйти"),
            Binding("ctrl+c", "request_quit", "Выйти", priority=True, show=False),
        ]

        def __init__(self, models: list[str], api_key: str) -> None:
            super().__init__()
            self.models = models
            self.api_key = api_key
            self._last_ctrlc = 0.0

        def on_mount(self) -> None:
            self.push_screen(InputScreen())

        def action_quit(self) -> None:
            self.exit()

        def action_request_quit(self) -> None:
            now = time.monotonic()
            if now - self._last_ctrlc < 3:
                self.exit()
            else:
                self._last_ctrlc = now
                self.notify("Нажми Ctrl+C еще раз, чтобы выйти", severity="warning", timeout=3)


def run_tui(models: list[str]) -> None:
    """Launch the Textual TUI (used when no question argument is given)."""
    console = Console()
    if not _TEXTUAL_OK:
        error_exit(
            console,
            "Textual не установлен. Выполни: pip install \"textual>=0.60.0\"",
        )
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        error_exit(console, MISSING_KEY_MSG)
    VersusApp(models, api_key).run()


# --- Entry point -------------------------------------------------------------

class RussianArgumentParser(argparse.ArgumentParser):
    """ArgumentParser with Russian labels for the visible help menu."""

    def format_help(self) -> str:
        text = super().format_help()
        return (
            text
            .replace("usage:", "использование:")
            .replace("positional arguments:", "аргументы:")
            .replace("options:", "параметры:")
            .replace("show this help message and exit", "показать справку и выйти")
        )

    def format_usage(self) -> str:
        return super().format_usage().replace("usage:", "использование:")

    @staticmethod
    def _translate_error(message: str) -> str:
        replacements = {
            "unrecognized arguments": "неизвестные аргументы",
            "the following arguments are required": "нужны аргументы",
            "expected 2 arguments": "нужно указать 2 значения",
            "invalid int value": "не число",
            "argument": "аргумент",
        }
        for old, new in replacements.items():
            message = message.replace(old, new)
        return message

    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: ошибка: {self._translate_error(message)}\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = RussianArgumentParser(
        prog="versus",
        description=(
            "Два LLM спорят по вопросу несколько раундов, потом судья выносит "
            "вердикт. Запусти без вопроса, чтобы открыть полноэкранный TUI."
        ),
    )
    parser.add_argument(
        "question",
        nargs="?",
        default=None,
        help="вопрос для спора (не указывай, если нужен TUI)",
    )
    parser.add_argument("--file", default=None, help="путь к файлу с контекстом")
    parser.add_argument("--rounds", type=int, default=2, help="число раундов (по умолчанию: 2)")
    parser.add_argument(
        "--models",
        nargs=2,
        metavar=("MODEL_A", "MODEL_B"),
        default=[DEFAULT_MODEL_A, DEFAULT_MODEL_B],
        help="две модели OpenRouter через пробел: сначала агент A, потом агент B",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="PATH",
        help="сохранить полный спор в Markdown-файл PATH",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"versus-llm {VERSION}",
        help="показать версию и выйти",
    )
    return parser.parse_args(argv)


def _force_utf8_output() -> None:
    """Make stdout/stderr encode box-drawing chars and emoji on any console.

    Windows consoles often default to a legacy code page (e.g. cp1251) that
    cannot encode characters like ``│`` or ``🟠``, which would crash Rich. UTF-8
    is safe everywhere and a no-op where it is already the encoding.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def main() -> None:
    _force_utf8_output()
    argv = sys.argv[1:]
    if argv and argv[0] in {"setup", "login"}:
        setup_api_key()
        return

    load_api_key_env()
    args = parse_args()

    if args.question is None:
        run_tui(args.models)
    else:
        run_cli(args)


if __name__ == "__main__":
    main()
