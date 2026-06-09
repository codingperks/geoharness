# Geoharness

Building an agentic framework using pure Python, removing abstraction from previously used frameworks.

A few overarching goals:
- Understand how basic/unengineered an agent architecture can be whilst still being performant (e.g. no strict graph traversals or lots of tools).
- How well can a different modality of data (this case GeoSpatial) be handled by LLMs - can an agent answer geospatial questions and understand the context.
- Build a local MCP server for this agent's tools to evaluate drawbacks and benefits of MCP in practice from the ground up.

Example target question: 'Is this a good coordinate to place solar panels?'

## Motivation

Commercial AI products I have built have used a graph-based architecture in the quest for robustness and repeatability, using a large set of tools and planners for predictable tool calling. 

As graph-based products grow, I feel that the maintenance overhead of the graph, the increasing difficulty of extensibility and the brittleness of tasks which fail prescribed traversal started to become less worth it for me - especially as these graph based architectures seemed to constrain the power afforded by newly released models.

The alternative — fewer, more primitive tools (web search, file systems, geospatial data feeds) with stronger models — is worth testing properly, and useful to understand the trade offs of agent architecture decisions.

I wanted to use a basic ReAct structure with very few tools and harness components to evaluate how well a simple agent architecture can accomplish complex tasks. Geospatial data seemed relatively complex as a test bed.

The 'pure python' stipulation is just a bit of extra fun, and to understand how popular frameworks abstract away agent architecture.

## Current architecture

A single ReAct loop (`act → observe → reflect`) with a small set of primitive tools. Keen to understand how well an agent can reflect on its own performance — slowly adding structure to the harness as I tune.

**Tools**

| Tool | Source | What it returns |
|---|---|---|
| `web_search` | DuckDuckGo | Broad metadata-based search across multiple pages |
| `web_fetch` | HTTP scrape | Full text of a specific URL for deeper dives |
| `get_climate_data` | NASA POWER | Monthly solar irradiance and temperature averages for a coordinate |
| `get_terrain_data` | OpenTopography (SRTM GL1) | Elevation, slope, and aspect for a ~1km radius around a coordinate |

## Eval

A hand-labelled eval set of 11 locations tests whether the agent reaches the correct GOOD / MARGINAL / BAD verdict from raw geospatial data alone.

Scoring rules are documented in [`eval/solar/eval_rules.md`](eval/solar/eval_rules.md). Locations were selected to cover a spread of latitudes, hemispheres, and failure modes (low irradiance, high cloud cover, bad aspect, steep slope). The eval is intentionally run with `web_search` excluded — the agent must reason from tool data alone, not training knowledge.

**Running the eval:**
```
uv run eval/solar/eval.py
```

Results are saved to `eval/solar/data/output/results/` with a UTC timestamp per run.

## How to currently run

1. Copy `.env.example` to `.env` and fill in your credentials
2. `uv sync` to install dependencies
3. `uv run main.py "[your query here]"`

## Observability

Each agent run is traced end-to-end using [Langfuse](https://langfuse.com). The full loop appears as a single trace named `Geoharness react`, with each LLM call (`act`, `observe`, `reflect`, `output`) as a labelled child generation. This makes it straightforward to inspect prompt inputs, model outputs, and token usage at each step of the loop — useful for prompt tuning and catching hallucinations.

![Langfuse trace](docs/langfuse-trace.png)
