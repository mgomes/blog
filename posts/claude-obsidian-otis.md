Date: August 9, 2025
Tags: ai, obsidian, productivity
Summary: How I turned Claude Code into a personalized knowledge assistant using Obsidian

# Teaching Claude Code My Obsidian Vault

## The Starting Point

If you haven't heard of [Claude Code](https://claude.ai/code), it's Anthropic's command-line interface that gives you Claude with access to your filesystem. It can read and write files, run commands, and basically act as a coding assistant that can actually touch your computer.

[Obsidian](https://obsidian.md), on the other hand, is my note-taking software. It's where I store everything - daily notes, research papers, code snippets, random thoughts, scanned PDFs of old receipts, you name it. My vault has grown into this massive interconnected web of markdown files and documents that represents years of accumulated knowledge.

Here's the problem: every time I start a new Claude Code session (or Claude or ChatGPT), it's a blank slate. It doesn't know how I organize my notes. It doesn't know my coding preferences. It doesn't know that I have a massive collection of PDFs sitting in my Obsidian vault. It's like having a brilliant assistant who gets amnesia every morning.

## The Solution: CLAUDE.md

The magic happens with a single file called `CLAUDE.md` that lives in my Obsidian vault. Claude Code automatically reads this file at the start of every session, giving it context about who I am and how I work.

This file tells Claude:
* How my Obsidian vault is organized
* My coding style preferences (like using Go's `any` instead of `interface{}`)
* Where to find specific types of information
* How to interact with my note-taking system
* Custom commands and workflows I've developed

## The Knowledge Layer

In my Obsidian vault, I've created a special folder with files that define who I am:
- A list of my interests (from Formula 1 to cellular automata)
- My movie collection (including physical media 😅)
- Research areas I'm actively exploring
- Even my preferred tools and workflows

This means when I ask Claude to research something, it doesn't just search generically - it searches with context. It knows I care about Raft consensus more than blockchain consensus. It knows I'm interested in arbitrage stories like when [Michael Larson beat Press Your Luck in 1984](https://en.wikipedia.org/wiki/Press_Your_Luck_scandal).

## Searching My Digital Brain

One of the coolest parts of this setup is teaching Claude to search through everything in my Obsidian vault - including PDFs. I've configured it to use macOS's Spotlight (`mdfind`) to search not just my markdown notes but also all those research papers, scanned documents, and random PDFs I've collected over the years.

```bash
mdfind -onlyin ~/Documents/mauricio "quantum computing"
```

Claude can now search through years of accumulated PDFs - research papers, scanned receipts, documentation, random articles I've saved. And with `textutil`, it can extract text from practically any document format:

```bash
textutil -convert txt interesting-paper.pdf -output - extracted.txt
```

No more "sorry, I can't read that format." Everything is searchable, everything is accessible.

## Real Examples

### Daily Notes Without the Hassle

Instead of navigating folder structures, I just say "add this to my notes" and Claude knows exactly where today's note lives (`~/work log/2025/2025-01/2025-01-09.md`). It creates the folder structure if needed, follows my naming conventions, and just works.

![Claude Code Daily Notes](/_Images/claude-code-note.mp4)

### Personalized Research

When I ask Claude to research a topic, it doesn't just search the web. It knows my interests file, so when I ask about consensus algorithms, it focuses on Raft and Paxos (which I care about) rather than blockchain consensus (which I don't). It's like having a research assistant who's read all my papers and knows my field. It even stores the results in my “research” folder.

![Claude Code Research](/_Images/claude-code-research.png)

### Finding That One PDF

Remember that paper you scanned three years ago? The one about... something with quantum? Claude can find it:

![Claude Code PDF Search](/_Images/claude-code-pdf.png)

### TV/Movie Recommendations

If it knows everything I’ve watched and liked, it should be able to recommend new things.

![Claude Code Movie Search](/_Images/claude-code-movies.mp4)

## The Technical Setup

Here's what makes this work:

1. **CLAUDE.md**: Lives at the root of my Obsidian vault, automatically loaded by Claude Code
2. **Context files**: Stored in a special folder with my interests, preferences, and other personal data
3. **Spotlight integration**: All documents in the vault are indexed and searchable
4. **Custom workflows**: Defined in CLAUDE.md for common tasks

The beauty is its simplicity. No APIs, no complex integrations. Just markdown files and bash commands.

## Why This Matters

The real win isn't just the productivity boost (though that's nice). It's the elimination of cognitive overhead. I don't have to context-switch to "talking to a new AI" mode anymore.

Claude knows:
* My conventions and preferences
* Where everything lives
* What I care about
* How I like to work

Every conversation builds on the foundation of my entire knowledge base. It's like having a brilliant assistant who's also read everything you've ever written and remembers all your preferences.

## Building Your Own

Want to create your own personalized Claude Code setup? You'll need:

1. An Obsidian vault (or similar knowledge base)
2. A CLAUDE.md file with your instructions and preferences
3. Some organizational system that makes sense to you
4. Optional: Lists of interests, collections, or other personal context
5. A system like macOS Spotlight that allows you to peek into documents of various types

The investment is maybe an hour of setup, but the compound returns are huge. Every session benefits from the accumulated context.

## What's Next

I'm constantly adding to this setup. Some ideas I'm exploring:
* Integration with my calendar for time-aware context
* Direct access to meeting transcripts so I don’t always have to paste them in
* Connection to my code repositories for better programming assistance
* Reading my RSS feeds directly and plucking out articles it knows I will like

The foundation is solid, and that's what matters. I've turned a brilliant but generic AI into something that actually understands my workflow and knowledge.

In a world of increasingly powerful but impersonal AI tools, making them truly personal feels like the right direction. It's not about the AI being smarter - it's about it being more *yours*.

Cheers!
