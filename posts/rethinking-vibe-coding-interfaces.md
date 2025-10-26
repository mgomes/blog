Date: October 25, 2025
Tags: ai, vibe coding, automation
Summary: what if AI coding looked more like software development and less like chat?

# Rethinking the Interface for Vibe Coding

https://youtu.be/kGakSweVNsk

## Exploring 3xo, a Kanban-style Agent Workspace

I’ve been experimenting with different ways to interact with coding agents, and one idea has started to feel especially natural: a Kanban board.

Instead of a chat window, **3xo** (pronounced "exo") is a desktop app that turns agent collaboration into something that looks and feels like software development. You can spin up Claude Code and OpenAI Codex, assign them to tasks, and watch work move through a familiar flow: **Backlog → In Progress → Ready for Review → Completed**.

Each project in 3xo has its own working directory, so as agents write and review code you can open the folder and see changes happen in real time. In the demo, for instance, I create a simple “Hello World” Python script with a 90s-style ASCII art twist. Codex handles the backend work while Claude reviews it. If a review fails, the card automatically moves back to “In Progress.” When it passes, it’s marked complete.

You can control concurrency and decide how many agents work at once. Maybe Claude handles frontend, Codex takes backend, and another agent reviews. Or you can let the whole thing run autonomously and check back later.

Watching the cards move across the board is surprisingly satisfying. It’s a small interface shift, but it changes the entire rhythm of how you collaborate with AI. Instead of a conversation, it feels like managing a team.

The larger question this experiment explores is: **what if AI coding looked more like software development and less like chat?** You could queue up dozens of cards, step away, and return to a project that’s been built and reviewed.

3xo runs locally as a desktop app, and I plan to publish a signed build soon for anyone curious to try it out.

Let me know what you think.
