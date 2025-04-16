Date: April 15, 2025
Tags: ai, mcp
Summary: MCP server for the Kagi search engine written in Go

# Kagi MCP Server

I built a little [Kagi MCP Server](https://github.com/mgomes/kagimcp) last week. It helps language models like Claude search the web and summarize web pages using [Kagi's excellent search and AI capabilities](https://kagi.com).

## Why I built this

I've been using Kagi as my personal search engine for a while now. It's privacy-focused, the results are high quality, and it's not cluttered with ads. As I now work with LLMs frequently, I wanted to bring that same search experience to my LLMs. Kagi itself has an official [MCP server (wrriten in Python)](https://github.com/kagisearch/kagimcp), but I wanted something that compiled neatly into a single binary.

## What it actually does

Kagi MCP Server is a simple Model Context Protocol (MCP) server that implements two main functions:

1. It lets LLMs search the web using Kagi's search API
2. It gives them access to Kagi's FastGPT summarizer to quickly digest web pages

That's it.

## Why MCP?

[MCP (Model Context Protocol)](https://modelcontextprotocol.io/introduction) is an emerging standard for connecting AI models to external tools. I like open standards - they tend to last longer than proprietary solutions. By building on MCP, this server should work with any compliant LLM platform, not just with specific vendors.

## How to use it

If you have a Kagi subscription, you can grab your API key and run this little server alongside your favorite LLM. It works in two modes:

- stdio mode for direct integration with AI platforms
- Server-Sent Events (SSE) mode if you prefer an HTTP-based approach

The code is up on [GitHub](https://github.com/mgomes/kagimcp), and it's written in Go, so it's fast and easy to deploy. The only caveat is that the Kagi search API is currently in beta, so you might need to request access if you don't have it yet. It's also fairly expensive. 😕
