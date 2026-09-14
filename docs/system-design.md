# Rememzo Product Brief

An unified MCP memory for all of your AI agents.

Supports Claude/ChatGPT Desktop, Web, claude-code, codex, hermes, opencode - whatever supports mcp. 

## Types of memory

2 types of memories are saved:  
- User specific memory.
- Project specific memory.
- ~~General memory. (NO, increase confusion)~~

1. Facts about user:
It is similar to human Episodic Memory. Memories of specific personal experiences, events, discussion and life episodes tied to times and places. 
[1] (https://www.psychologytoday.com/us/basics/memory/types-of-memory), 
[2] (https://pmc.ncbi.nlm.nih.gov/articles/PMC7965175/), 
[3] (https://en.wikipedia.org/wiki/Memory)

2. Project based memory:
Working memory of specific project. Timeline, worklog, feature, todo, future, etc.

3. General memory: (WE drop the idea to keep a separate General memory. Instead user memory will be used)
Not bind to a project, nor facts about users. But other discussions including planning for a new thing, brainstroming on a random thing, etc.

## Connectivity:
- All memories are shared among connected agents. 
- Project memories shated with team. 


# System Brief

## Account
- A single MCP server get connected with different AI Agents.
- APIKey based connection.
- One user one Personal account.

## Organization
- One user can be connected to multiple organization. Similar to opnerouter.
- A project is associated with eiter an organization or a personal account.

## Server
- Has N mcp tools exposed to AI agents. Agents decides what to save and where to save.
- Asynchonous tool calling, 
- Rate limiting. N calls/min.
- self hostable.

## Database
- SQLite DB for local use (expose locally or tunneling)
- Postgres for hosted service. (we will host it under rememzo.taufiq.cc - neon postgres via api) # not a discussion now.

## Memory format
- converted into vector using small local embedding model or keep raw (should do study)
- reusable unified structure for all types of memory. 


# Stages
## V0.1 deliverable
- self host locally - (if want expose via tunnel)
- mcp connection auth - apikey
- save to local sqlite db - Memory, User, Project
- tools: CRUD memory, CRUD project
- 2 types of memory: USER, PROJECT
- pytest
- focus on MCP only core product, not user/organization account side.
- detailed docstring and documentation for LLM.
- easy dev setup via single cmd: cmd -> get from github -> auto setup and always running service -> add to client via custom plugin/config file edit

## V0.2
- team support
- deploy as service

### Role based permission
| Action | Owner | Admin | Member | Guest |
|---|---:|---:|---:|---:|
| View/search memories | Yes | Yes | Yes | Yes |
| Add/update memories | Yes | Yes | Yes | No |
| Forget/delete memories | Yes | Yes | Yes | No |
| Edit project details | Yes | Yes | Yes | No |
| Add Admin | Yes | Yes | No | No |
| Add Member/Guest | Yes | Yes | No | No |
| Remove Member/Guest | Yes | Yes | No | No |
| Remove/demote Admin | Yes | No | No | No |
| Transfer ownership | Yes | No | No | No |
| Delete project | Yes | No | No | No |

## V0.3
- auto skill creator


## Other Memory Tools
mem0, supermemory, ...

Mem0 format:
```json
{
    "id":"5b94a28b-6fa8-401d-a104-7fbbc5f39e93",
    "memory":"User discovered that Mem0 was already connected but empty and decided to use Mem0 as a persistent memory store across sessions",
    "user_id":"taufiq",
    "metadata":{},
    "categories":["technology"],
    "created_at":"2026-07-04T16:27:36-07:00",
    "updated_at":"2026-07-06T06:17:12.061568-07:00",
    "expiration_date":null,
    "structured_attributes":{
        "day":4,"hour":23,"year":2026,"month":7,"minute":27,"quarter":3,"is_weekend":true,"day_of_week":"saturday","day_of_year":185,"week_of_year":27
    },
    "replaced_by":"6413b958-b679-4da8-aba2-92162c8da73e",
    "synthesized":false,
    "lifecycle_state":"superseded",
}
```