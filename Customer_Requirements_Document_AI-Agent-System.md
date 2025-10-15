# Customer Requirements Document: AI Agent System Development

## Project Overview

We require the development of an AI agent system built using the Claude Agents SDK (https://docs.claude.com/en/api/agent-sdk/) and solely based on this sdk except the non agent functionalities. The system will consist of a **TeamLeader** agent that invokes and delegates tasks to specialized **sub-agents**.[^1][^2][^3]

## System Requirements

### Core Framework

- **Primary SDK**: Claude Agents SDK[^2][^3][^4]
- **Agent Structure**: TeamLeader that invokes and delegates to sub-agents
- **System Prompts**: All agent system prompts must be loaded from external `.md` files, not written directly into the code. The System prompts are provided in /Users/nicholas/Code/Agents/DevTeam_ClaudeSDK/Agents and are not to be altered.


### Agent Configuration

#### TeamLeader Agent

- **Role**: Invokes and delegates tasks to sub-agents
- **System Prompt**: Load from external `.md` file
- **Functionality** The teamleader will work based on his system prompt. There is no need to implement or translate the system prompts workflows into code


#### Sub-Agents with MCP Server Tools

The system must include these specific sub-agents with their designated MCP servers:

1. **ResearchAgent**
    - **MCP Server**: Perplexity MCP Server[^5]
    - **Repository**: https://github.com/cyanheads/perplexity-mcp-server
    - **System Prompt**: Load from external `.md` file
2. **CodeBaseAnalyzer**
    - **MCP Server**: Serena MCP Server[^6]
    - **Repository**: https://github.com/oraios/serena
    - **System Prompt**: Load from external `.md` file
3. **FrontEndCoder**
    - **MCP Server**: Playwright MCP Server[^7]
    - **Repository**: https://github.com/microsoft/playwright-mcp
    - **System Prompt**: Load from external `.md` file
4. **BackEndCoder**
    - **MCP Server**: Serena MCP Server[^6]
    - **Repository**: https://github.com/oraios/serena
    - **System Prompt**: Load from external `.md` file

## Interface Requirements

### System Terminal Interface

- Ability to interact with the TeamLeader through the system terminal. This means simple execution of a main script in a venv, where the user passes the main task to the team.


### API Interface

- Ability to interact with the dev team via API. This means sending a task via api call.


## MCP Server Integration Requirements

Based on the source repositories, the system must integrate:[^5][^7][^6]

1. **Perplexity MCP Server**: Provides web search and research capabilities[^5]
2. **Serena MCP Server**: Provides codebase analysis and coding assistance tools[^6]
3. **Playwright MCP Server**: Provides browser automation and web interaction capabilities[^7]

## Technical Implementation

- **Claude Agents SDK**: Use Python implementation[^3][^4]
- **External System Prompts**: Load all system prompts from `.md` files rather than hardcoding them
- **MCP Integration**: Connect specified MCP servers to their respective agents[^2]


## Deliverables Required

1. TeamLeader agent that can invoke and delegate to sub-agents
2. Four sub-agents (ResearchAgent, CodeBaseAnalyzer, FrontEndCoder, BackEndCoder) with their specified MCP server tools
3. External `.md` file loading system for all agent system prompts
4. Executable via interactiv main script.
5. API interface for dev team interaction

<div align="center">⁂</div>

[^1]: https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk

[^2]: https://docs.claude.com/en/api/agent-sdk/overview

[^3]: https://github.com/anthropics/claude-agent-sdk-typescript

[^4]: https://github.com/anthropics/claude-agent-sdk-python

[^5]: https://github.com/cyanheads/perplexity-mcp-server

[^6]: https://github.com/oraios/serena

[^7]: https://github.com/alexrwilliam/playwright-mcp-server

