\# SKILL.md



\## Skill name



No AI Slop Text Cleanup



\## Purpose



\## Primary language priority



The main target language for this skill is Russian.



If the project contains Russian and English text, Russian text has higher priority.



The agent must assume that most visible product copy, website text, documentation, README sections, UI labels, and marketing text may be written in Russian. Do not treat Russian copy as secondary.



When cleaning the project, check Russian text first, then English text.



The Russian cleanup rules are stricter than the English ones because Russian AI-slop often sounds even worse when it is translated from English corporate language.



\## Russian-first cleanup rule



Russian text must sound like normal Russian written by a real person, not like translated SaaS marketing.



Avoid text that sounds like this:



```text

Мы предлагаем инновационные цифровые решения для эффективной оптимизации бизнес-процессов.

```



Prefer text like this:



```text

Мы делаем сайты, Telegram-ботов и панели под конкретную задачу бизнеса.

```



The agent must aggressively rewrite Russian phrases that look like:



```text

цифровые решения

инновационные решения

современные технологии

комплексный подход

индивидуальный подход

эффективное управление

оптимизация бизнес-процессов

повышение эффективности

масштабируемые решения

автоматизация процессов

вывести бизнес на новый уровень

широкий спектр услуг

надежный партнер

для вашего успеха

под ключ

уникальные потребности бизнеса

качественный сервис

удобный интерфейс

простое и эффективное решение

```



These phrases are not banned forever, but they are guilty until proven useful.



If the phrase does not explain a real action, feature, object, user, result, price, deadline, or process, rewrite it.



\## Russian tone target



Russian copy should be:



```text

прямой

живой

понятный

конкретный

без канцелярита

без корпоративного тона

без перевода с английского

```



Russian copy should not be:



```text

канцелярским

мотивационным

слишком рекламным

похожим на ChatGPT

похожим на лендинг агентства из 2017

похожим на перевод английского SaaS-сайта

```



\## Russian rewrite examples



Bad:



```text

Мы помогаем бизнесу выйти на новый уровень с помощью современных цифровых решений.

```



Good:



```text

Мы собираем сайты, Telegram-ботов и панели, которые закрывают конкретные задачи бизнеса.

```



Bad:



```text

Наши решения позволяют оптимизировать рабочие процессы и повысить эффективность команды.

```



Good:



```text

Бот принимает заявки, отправляет уведомления и сохраняет клиентов в таблицу.

```



Bad:



```text

Индивидуальный подход к каждому клиенту.

```



Good:



```text

Сначала разбираем, как у вас сейчас идут заявки, потом собираем логику под этот процесс.

```



Bad:



```text

Удобный и интуитивно понятный интерфейс.

```



Good:



```text

Админ видит заявки, статусы, контакты и комментарии в одной панели.

```



Bad:



```text

Автоматизируйте бизнес-процессы быстро и эффективно.

```



Good:



```text

Уберите ручные ответы, напоминания и копирование заявок в таблицу.

```



Bad:



```text

Мы создаем качественные сайты под ключ для вашего бизнеса.

```



Good:



```text

Делаем лендинги, которые сразу объясняют оффер и ведут человека к заявке.

```



\## Russian scan commands



The agent must search for Russian corporate and AI-slop markers:



```bash

grep -RInE "цифровые решения|инновационные решения|современные технологии|комплексный подход|индивидуальный подход|эффективное управление|оптимизация бизнес-процессов|повышение эффективности|масштабируемые решения|автоматизация процессов|вывести.\*новый уровень|широкий спектр услуг|надежный партнер|для вашего успеха|уникальные потребности|качественный сервис|интуитивно понятный|под ключ" . \\

&#x20; --exclude-dir=node\_modules \\

&#x20; --exclude-dir=.git \\

&#x20; --exclude-dir=dist \\

&#x20; --exclude-dir=build \\

&#x20; --exclude-dir=.next

```



Also search for translated English SaaS patterns in Russian:



```bash

grep -RInE "позволяет вам|помогает вам|создан\[аоы]? для|разработан\[аоы]? для|благодаря нашему|с помощью нашего|откройте для себя|погрузитесь|попрощайтесь|скажите привет|новый способ|будущее|революционный|мощная платформа|единое решение" . \\

&#x20; --exclude-dir=node\_modules \\

&#x20; --exclude-dir=.git \\

&#x20; --exclude-dir=dist \\

&#x20; --exclude-dir=build \\

&#x20; --exclude-dir=.next

```



\## Russian final check



Before finishing, the agent must verify:



```text

No Russian copy sounds like translated English.

No Russian copy uses empty business phrases without concrete meaning.

No Russian copy uses канцелярит where normal words would work.

No Russian copy says "решения" unless it is clear what those solutions actually are.

No Russian copy says "эффективность" without explaining what becomes faster, cheaper, simpler, or automatic.

```





This skill is used by LLM agents working inside a codebase to detect, rewrite, and prevent text that looks corporate, generic, over-polished, robotic, or obviously generated by AI.



The goal is simple:



Make all project text sound human, direct, specific, and useful.



This applies to every text surface in the project:



\* website copy

\* landing pages

\* UI text

\* buttons

\* forms

\* empty states

\* error messages

\* onboarding screens

\* README files

\* documentation

\* comments intended for humans

\* changelogs

\* package descriptions

\* metadata

\* prompts

\* examples

\* marketing text

\* help text

\* emails or message templates inside the repo



The agent must aggressively remove AI-slop patterns, corporate filler, fake confidence, generic startup language, and unnecessary long punctuation.



\## Core rule



Do not preserve text just because it is grammatically correct.



If the text sounds like a SaaS landing page template, a LinkedIn post, a corporate brochure, or ChatGPT filler, rewrite it.



Good text should feel like a real person wrote it for a real user.



\## Non-negotiable rules



\### 1. Remove long dash style



Avoid em dashes and repeated long dash formatting.



Bad:



```text

Build faster — without the complexity.

```



Good:



```text

Build faster without the mess.

```



Bad:



```text

Everything you need — all in one place.

```



Good:



```text

Everything you need in one place.

```



Use commas, periods, colons, parentheses, or simple sentence splitting instead.



Allowed only when there is a strong technical reason, which is rare.



\### 2. Remove generic corporate phrases



Delete or rewrite phrases like:



```text

empower

seamless

leverage

robust

scalable solution

unlock your potential

streamline your workflow

elevate your experience

take your business to the next level

all-in-one platform

cutting-edge

revolutionary

game-changing

next-generation

innovative solution

transform the way you

designed to help you succeed

effortlessly manage

supercharge your productivity

built for teams of all sizes

crafted with care

powerful yet simple

intuitive interface

reimagine

modern solution

future-proof

frictionless

drive growth

optimize operations

enhance collaboration

boost efficiency

maximize impact

```



These are usually empty. Replace them with concrete meaning.



Bad:



```text

A powerful all-in-one platform to streamline your workflow.

```



Good:



```text

Manage orders, clients, and payments from one dashboard.

```



\### 3. Remove AI-flavored structure



Avoid text that feels like it came from a prompt response.



Bad patterns:



```text

Whether you're a small business or a growing team...

In today's fast-paced world...

Our solution is designed to...

Say goodbye to...

Say hello to...

With X, you can...

At its core...

More than just...

Not just X, but Y...

From X to Y, we help you...

```



Rewrite into direct claims.



Bad:



```text

Whether you're a freelancer or a growing team, our platform helps you manage your workflow with ease.

```



Good:



```text

Track tasks, deadlines, and clients without opening five different tools.

```



\### 4. Remove fake excitement



Do not overhype normal features.



Bad:



```text

Experience the future of task management.

```



Good:



```text

Create tasks, assign owners, and see what is late.

```



Bad:



```text

Unlock a smarter way to work.

```



Good:



```text

Spend less time checking spreadsheets.

```



\### 5. Prefer specific over impressive



Every claim should answer at least one of these:



\* What does it do?

\* Who is it for?

\* What pain does it remove?

\* What changes after using it?

\* What is the user supposed to do next?



Bad:



```text

We create digital solutions for modern businesses.

```



Good:



```text

We build Telegram bots for bookings, orders, reminders, and client support.

```



Bad:



```text

Improve your operations with automation.

```



Good:



```text

Replace manual WhatsApp replies with automatic booking messages.

```



\### 6. Use normal human rhythm



Prefer short and medium sentences.



Avoid stacked abstractions.



Bad:



```text

Our comprehensive ecosystem enables businesses to efficiently orchestrate mission-critical workflows across multiple operational touchpoints.

```



Good:



```text

Your team can see requests, assign work, and close tasks in one place.

```



\### 7. Do not sound like a corporate brand book



Avoid sterile phrases like:



```text

we are committed to excellence

customer-centric approach

tailored to your unique needs

trusted by professionals

built with passion

designed for success

your trusted partner

```



Rewrite with proof, process, or actual offer.



Bad:



```text

We are committed to delivering tailored solutions for your unique business needs.

```



Good:



```text

We look at how your business takes requests, then build the bot around that flow.

```



\### 8. Remove empty adjectives



Words like these are usually weak unless backed by proof:



```text

powerful

simple

smart

modern

beautiful

fast

easy

advanced

premium

professional

intuitive

flexible

reliable

secure

seamless

robust

dynamic

unique

```



Do not ban them blindly. Challenge them.



If a word cannot be proven or shown, delete it.



Bad:



```text

A simple and powerful dashboard.

```



Good:



```text

A dashboard with orders, clients, payments, and status filters.

```



\### 9. Do not use vague benefit stacks



Bad:



```text

Save time, reduce costs, and grow faster.

```



Good:



```text

Stop copying client requests from Telegram into a spreadsheet.

```



Bad:



```text

Boost productivity and improve collaboration.

```



Good:



```text

Everyone sees who owns the task and when it is due.

```



\### 10. Keep the user's domain language



Use words the actual target audience would use.



For local business owners:



Good:



```text

записи

клиенты

заявки

оплаты

напоминания

мастера

администратор

свободные слоты

```



Bad:



```text

операционные процессы

коммуникационные точки

воронки взаимодействия

```



For developers:



Good:



```text

install

run

config

env

API key

CLI

deploy

```



Bad:



```text

developer experience ecosystem

integration journey

```



\## Text surfaces to scan



The agent must inspect text in:



```text

README.md

AGENTS.md

CLAUDE.md

SKILL.md

docs/\*\*

content/\*\*

app/\*\*

pages/\*\*

src/\*\*

components/\*\*

public/\*\*

package.json

\*.md

\*.mdx

\*.txt

\*.json

\*.tsx

\*.jsx

\*.ts

\*.js

\*.html

\*.css

\*.scss

```



Pay special attention to:



\* hero sections

\* feature cards

\* pricing sections

\* FAQ

\* CTA blocks

\* footer text

\* meta titles

\* meta descriptions

\* empty states

\* onboarding copy

\* README intro

\* installation instructions

\* usage examples

\* contribution text

\* generated docs



\## Rewrite priorities



Use this order:



1\. Remove obvious AI-slop.

2\. Remove long dashes.

3\. Replace vague claims with concrete claims.

4\. Shorten sentences.

5\. Make the tone more human.

6\. Preserve product meaning.

7\. Preserve technical accuracy.

8\. Preserve existing brand voice if it is actually distinct.

9\. Avoid making everything too casual unless the project already uses that tone.

10\. Make final text consistent across the repo.



\## Tone target



The target tone is:



```text

clear

direct

specific

human

confident without hype

useful

plain but not boring

```



The target tone is not:



```text

corporate

LinkedIn-style

startup-template

AI-generated

over-friendly

fake premium

too poetic

too motivational

too salesy

```



\## Language rules



\### For English text



Use plain English.



Prefer:



```text

Build

Create

Send

Track

Manage

Connect

Run

Deploy

Install

Use

Fix

Check

```



Avoid:



```text

Leverage

Empower

Elevate

Reimagine

Streamline

Harness

Unlock

Optimize

Facilitate

Orchestrate

```



\### For Russian text



Use normal Russian, not translated corporate English.



Prefer:



```text

делаем

собираем

запускаем

подключаем

показываем

проверяем

заявка

клиент

оплата

запись

бот

сайт

панель

```



Avoid:



```text

осуществляем

реализуем комплексные решения

повышаем эффективность

оптимизируем бизнес-процессы

цифровая трансформация

индивидуальный подход

инновационные инструменты

```



Bad:



```text

Мы реализуем комплексные цифровые решения для оптимизации бизнес-процессов.

```



Good:



```text

Мы делаем сайты, Telegram-ботов и панели, которые закрывают конкретную задачу бизнеса.

```



\## Rewrite examples



\### Example 1



Bad:



```text

Empower your team with a seamless all-in-one platform designed to streamline collaboration.

```



Good:



```text

Keep tasks, owners, deadlines, and comments in one shared workspace.

```



\### Example 2



Bad:



```text

Unlock the full potential of your business with our innovative automation solutions.

```



Good:



```text

Automate bookings, reminders, and client replies in Telegram.

```



\### Example 3



Bad:



```text

A modern solution for businesses of all sizes.

```



Good:



```text

For small teams that still manage clients in chats and spreadsheets.

```



\### Example 4



Bad:



```text

Наш сервис помогает бизнесу выйти на новый уровень за счет современных цифровых решений.

```



Good:



```text

Мы собираем Telegram-бота под ваш бизнес за 1-2 дня.

```



\### Example 5



Bad:



```text

Интуитивно понятный интерфейс для эффективного управления заявками.

```



Good:



```text

Администратор видит новые заявки, статусы и контакты клиентов в одной таблице.

```



\### Example 6



Bad:



```text

Built for speed, simplicity, and scale.

```



Good:



```text

Start with one bot. Add payments, CRM, or admin roles later.

```



\### Example 7



Bad:



```text

Say goodbye to manual processes and hello to effortless automation.

```



Good:



```text

The bot asks the client for details and sends the request to your manager.

```



\## README rules



README files must be useful first.



A README should not start like a pitch deck.



Bad:



```text

Welcome to the future of AI-powered productivity.

```



Good:



```text

This is a CLI tool for comparing LLM responses from different providers.

```



A good README intro should answer:



```text

What is this?

Who is it for?

What does it do?

How do I run it?

What do I need before using it?

```



Recommended README structure:



```text

\# Project Name



One sentence explaining what the project does.



\## What it does



\- Specific feature

\- Specific feature

\- Specific feature



\## Requirements



\- Node.js version

\- Python version

\- API keys

\- Database

\- Other required tools



\## Setup



Steps that actually work.



\## Usage



Commands and examples.



\## Configuration



Environment variables and options.



\## Notes



Known limits, assumptions, or warnings.

```



Avoid README sections like:



```text

Why choose us

Our mission

Revolutionizing the future

Key benefits

Experience the difference

```



Unless the project truly needs marketing copy.



\## Website copy rules



\### Hero section



Hero text must be concrete.



Bad:



```text

Transform the way your business works with powerful automation.

```



Good:



```text

Telegram bots for bookings, orders, reminders, and client support.

```



Bad:



```text

Build smarter. Move faster. Grow better.

```



Good:



```text

Launch a working client bot in 1-2 days.

```



Hero should include:



```text

what it is

who it is for

main outcome

CTA

```



\### Feature cards



Feature cards must describe real features.



Bad:



```text

Seamless integration

```



Good:



```text

Connects to Telegram, Google Sheets, and your CRM.

```



Bad:



```text

Smart automation

```



Good:



```text

Sends reminders before appointments.

```



\### Buttons



Buttons should be direct.



Good:



```text

Start

Book a call

See pricing

Open dashboard

Create bot

Install package

Read docs

```



Avoid:



```text

Unlock now

Start your journey

Experience the future

Transform today

```



\### Empty states



Empty states should explain what happened and what to do.



Bad:



```text

Nothing here yet.

```



Better:



```text

No orders yet. New orders will appear here after clients submit the form.

```



\### Error messages



Error messages should be specific and useful.



Bad:



```text

Something went wrong.

```



Better:



```text

Could not send the request. Check your internet connection and try again.

```



\### Pricing text



Pricing should avoid fake value language.



Bad:



```text

Flexible plans designed to grow with you.

```



Good:



```text

Start with one bot. Add extra branches, managers, or integrations when needed.

```



\## Documentation rules



Docs must be practical.



Avoid filler intros.



Bad:



```text

This guide will walk you through the simple and seamless process of configuring your environment.

```



Good:



```text

Set these variables before running the app.

```



Bad:



```text

Let's dive into the exciting world of configuration.

```



Good:



```text

Create `.env.local` in the project root.

```



Docs should prefer:



```text

Do this.

Then this.

Expected result.

Common error.

How to fix it.

```



\## Code comment rules



Do not rewrite necessary technical comments.



Remove comments that only explain obvious code.



Bad:



```text

// This function handles the button click

```



Good:



```text

// Retry once because Telegram sometimes returns 429 for burst sends

```



Keep comments when they explain:



\* business logic

\* workaround

\* non-obvious behavior

\* external API limitation

\* security decision

\* performance reason



\## Metadata rules



Inspect metadata too.



Bad:



```json

{

&#x20; "description": "A powerful modern solution for seamless productivity"

}

```



Good:



```json

{

&#x20; "description": "CLI tool for comparing LLM outputs from multiple providers"

}

```



For SEO metadata, avoid generic marketing.



Bad:



```text

Best platform to transform your business with innovative AI solutions.

```



Good:



```text

Telegram bot development for bookings, orders, reminders, and client support in Kazakhstan.

```



\## Agent workflow



When this skill is triggered, the agent must follow this process.



\### Step 1: Find text



Search the repo for text-heavy files and UI copy.



Recommended commands:



```bash

find . -type f \\

&#x20; \\( -name "\*.md" -o -name "\*.mdx" -o -name "\*.txt" -o -name "\*.json" -o -name "\*.tsx" -o -name "\*.jsx" -o -name "\*.ts" -o -name "\*.js" -o -name "\*.html" \\) \\

&#x20; -not -path "./node\_modules/\*" \\

&#x20; -not -path "./.git/\*" \\

&#x20; -not -path "./dist/\*" \\

&#x20; -not -path "./build/\*" \\

&#x20; -not -path "./.next/\*"

```



\### Step 2: Search for slop markers



Use targeted search.



```bash

grep -RInE "empower|seamless|leverage|unlock|streamline|elevate|reimagine|cutting-edge|game-changing|next-generation|innovative|all-in-one|robust|scalable|frictionless|supercharge|transform the way|take.\*next level|future of|designed to help|effortlessly|powerful yet simple" . \\

&#x20; --exclude-dir=node\_modules \\

&#x20; --exclude-dir=.git \\

&#x20; --exclude-dir=dist \\

&#x20; --exclude-dir=build \\

&#x20; --exclude-dir=.next

```



Search for long dash style:



```bash

grep -RIn "—" . \\

&#x20; --exclude-dir=node\_modules \\

&#x20; --exclude-dir=.git \\

&#x20; --exclude-dir=dist \\

&#x20; --exclude-dir=build \\

&#x20; --exclude-dir=.next

```



Search for repeated AI-ish patterns:



```bash

grep -RInE "Whether you're|In today's|Say goodbye|Say hello|At its core|More than just|Not just|designed for|built for teams|trusted by|crafted with care" . \\

&#x20; --exclude-dir=node\_modules \\

&#x20; --exclude-dir=.git \\

&#x20; --exclude-dir=dist \\

&#x20; --exclude-dir=build \\

&#x20; --exclude-dir=.next

```



For Russian projects:



```bash

grep -RInE "цифровые решения|индивидуальный подход|оптимизация бизнес-процессов|повышение эффективности|инновационные|современные технологии|вывести.\*новый уровень|комплексные решения|эффективное управление|трансформация бизнеса" . \\

&#x20; --exclude-dir=node\_modules \\

&#x20; --exclude-dir=.git \\

&#x20; --exclude-dir=dist \\

&#x20; --exclude-dir=build \\

&#x20; --exclude-dir=.next

```



\### Step 3: Review context before rewriting



Do not blindly replace words.



Before editing, understand:



\* what the product actually does

\* who the user is

\* what the page or document is trying to explain

\* what claims must stay true

\* what technical terms must remain unchanged



\### Step 4: Rewrite in place



Rewrite copy directly in the files.



Do not create a separate "suggestions" file unless explicitly asked.



Do not only report issues. Fix them.



\### Step 5: Preserve meaning



Never invent features.



Bad rewrite:



```text

Connects to Stripe, Notion, Slack, and HubSpot.

```



Only write this if the project really supports those integrations.



If unsure, use safer wording:



```text

Can be connected to external tools if the integration is added.

```



Better:



```text

Currently supports Telegram-based flows.

```



\### Step 6: Keep formatting valid



After editing, check that:



\* JSX strings are valid

\* quotes are escaped

\* JSON remains valid

\* Markdown headings still make sense

\* links are not broken

\* code blocks are not corrupted

\* translation keys are unchanged

\* environment variable names are unchanged

\* package names are unchanged



\### Step 7: Final scan



Run another search for banned markers.



The final result should contain no obvious AI-slop phrases unless they appear inside examples that intentionally show bad text.



\## Strict banned patterns



Unless inside this SKILL.md or an explicit "bad example", avoid these:



```text

unlock your potential

elevate your

seamless experience

seamlessly

streamline your workflow

empower your team

empowering

leverage

revolutionize

revolutionary

game-changing

cutting-edge

next-generation

future of

transform the way

take your business to the next level

all-in-one solution

powerful platform

robust solution

scalable solution

innovative solution

drive growth

maximize impact

boost productivity

enhance collaboration

crafted with care

designed for success

built for everyone

effortless

effortlessly

supercharge

reimagine

frictionless

your trusted partner

tailored to your unique needs

```



Russian banned patterns:



```text

индивидуальный подход

комплексные решения

цифровая трансформация

оптимизация бизнес-процессов

повышение эффективности

вывести бизнес на новый уровень

современные технологии

инновационные решения

эффективное управление

широкий спектр услуг

надежный партнер

для вашего успеха

уникальные потребности бизнеса

```



\## Long dash policy



The em dash character is banned in normal copy:



```text

—

```



Replace it with:



\* a period

\* a comma

\* a colon

\* parentheses

\* a simple hyphen only when technically appropriate

\* sentence split



Bad:



```text

Fast setup — no code required.

```



Good:



```text

Fast setup. No code required.

```



Bad:



```text

AI agents — built for real teams.

```



Good:



```text

AI agents built for real teams.

```



Bad:



```text

One dashboard — every client, task, and payment.

```



Good:



```text

One dashboard for clients, tasks, and payments.

```



\## Anti-slop decision test



For every important sentence, ask:



```text

Could this sentence appear on 10,000 other startup sites?

```



If yes, rewrite it.



Ask:



```text

Would a real user understand what changes after using this?

```



If no, rewrite it.



Ask:



```text

Does this sentence name a real feature, action, user, object, or result?

```



If no, rewrite it.



Ask:



```text

Is this sentence trying to sound expensive instead of being useful?

```



If yes, rewrite it.



\## Good copy patterns



Use patterns like:



```text

Do X without Y.

```



Example:



```text

Take bookings without answering every message by hand.

```



```text

For X who need Y.

```



Example:



```text

For barbers, salons, clinics, and small teams that take bookings in Telegram.

```



```text

X happens automatically.

```



Example:



```text

The bot sends a reminder before the appointment.

```



```text

User does X. System does Y.

```



Example:



```text

The client picks a time. The bot sends the request to your admin.

```



```text

Start with X. Add Y later.

```



Example:



```text

Start with bookings. Add payments and CRM later.

```



\## Bad to good replacement table



| Bad                      | Better                                        |

| ------------------------ | --------------------------------------------- |

| Streamline your workflow | Remove manual steps                           |

| Seamless experience      | Works without extra steps                     |

| Unlock growth            | Get more requests without more admin work     |

| Powerful platform        | Dashboard for requests, clients, and payments |

| Innovative solution      | Tool that handles bookings in Telegram        |

| Tailored to your needs   | Built around your current booking flow        |

| Boost productivity       | Spend less time copying data                  |

| Enhance collaboration    | Everyone sees who owns each task              |

| Effortless automation    | Automatic reminders and replies               |

| Transform your business  | Replace manual client handling with a bot     |

| Современное решение      | Бот, который принимает заявки в Telegram      |

| Индивидуальный подход    | Сначала разбираем, как у вас идут заявки      |

| Оптимизация процессов    | Убираем ручные сообщения и таблицы            |

| Повышение эффективности  | Админ тратит меньше времени на повторы        |

| Инновационные технологии | Telegram, формы, уведомления и интеграции     |



\## What not to change



Do not rewrite:



\* API names

\* package names

\* commands

\* code identifiers

\* environment variables

\* legal text unless asked

\* license text

\* quotes from external sources

\* test snapshots unless updating tests intentionally

\* user-provided testimonials unless asked

\* changelog entries where wording matters historically



Do not remove necessary technical precision.



Bad rewrite:



```text

Run the thing.

```



Good:



```text

Run `npm run dev` from the project root.

```



\## Handling marketing pages



Marketing pages can still sell. They just cannot sound fake.



Good marketing is allowed:



```text

Get a working Telegram bot in 1-2 days.

```



Bad marketing is not allowed:



```text

Unlock the future of customer engagement with our revolutionary automation platform.

```



Use concrete selling points:



```text

7 days free

setup in 1-2 days

Telegram-first

custom flow

admin notifications

client reminders

payment-ready

CRM-ready

```



Do not add these claims unless they are true for the project.



\## Handling premium tone



Premium does not mean vague.



Bad premium:



```text

An elevated digital experience crafted for ambitious brands.

```



Good premium:



```text

A clean site with strong visuals, fast loading, and a clear offer.

```



Bad premium:



```text

Where design meets innovation.

```



Good premium:



```text

A landing page that explains the offer in the first screen.

```



\## Handling technical products



For developer tools, be even more direct.



Bad:



```text

A next-generation developer experience for modern AI workflows.

```



Good:



```text

Compare prompts across OpenAI, Anthropic, and OpenRouter from the terminal.

```



Bad:



```text

Seamlessly integrate into your development workflow.

```



Good:



```text

Install it with pip and run it from any project folder.

```



\## Handling AI products



AI products attract the worst slop. Be stricter.



Avoid:



```text

AI-powered

intelligent

smart

autonomous

agentic

next-gen AI

AI revolution

human-like

magic

```



Use these only when they explain a real feature.



Bad:



```text

AI-powered assistant that transforms your productivity.

```



Good:



```text

The assistant reads your tasks, asks follow-up questions, and writes a daily plan.

```



Bad:



```text

Autonomous agents for modern teams.

```



Good:



```text

Agents that can read issues, update docs, and open pull requests after approval.

```



\## Editing style



When rewriting, prefer:



```text

shorter sentence

clear noun

active verb

specific object

visible outcome

```



Avoid:



```text

abstract noun

passive construction

stacked adjective

fake benefit

motivational tone

```



Bad:



```text

Our platform enables the acceleration of operational efficiency through automation.

```



Good:



```text

The bot answers common questions and sends booking requests to your admin.

```



\## Before and after requirement



For large rewrites, the agent should internally compare before and after.



The new version must be:



\* shorter or clearer

\* less generic

\* less corporate

\* more specific

\* free of em dashes

\* accurate to the project



If the rewrite only changes style but not clarity, improve it again.



\## Final response format for agents



After making changes, respond with:



```text

Done.



Changed:

\- rewrote website copy to remove generic AI/corporate phrasing

\- removed em dashes from user-facing text

\- cleaned README intro and usage sections

\- made feature descriptions more concrete



Checked:

\- no obvious AI-slop phrases left outside intentional examples

\- no em dashes left outside this skill or intentional examples

\- JSON/JSX/Markdown formatting preserved

```



If some files could not be safely edited, say exactly which ones and why.



Do not write a long essay in the final response.



\## Final quality bar



The project should not sound like this:



```text

Empower your business with a seamless AI-powered platform designed to streamline operations and unlock growth.

```



It should sound like this:



```text

A Telegram bot that takes client requests, sends reminders, and keeps orders in one dashboard.

```



That is the standard.



