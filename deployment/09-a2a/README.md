# Agent to Agent (A2A) protocol using Strands Agent SDK


## Getting started

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. Configure AWS credentials, follow instructions [here](https://cuddly-sniffle-lrmk2y7.pages.github.io/0.1.x-strands/user-guide/quickstart/#configuring-credentials).

### An example Strands agent that helps with searching AWS documentation.
1. Start the A2A server using `uv run __main__.py`.

### An example Strands agent that provides weather forcast in US
1. Start the A2A server using `uv run __main2__.py`.

### An example Strands agent that work as calculator and current time
1. Start the A2A server using `uv run __main3__.py`.

### An Agent developed with Strands SDK work with above 2 agents via A2A protocal
1.  Start the client using `uv run a2a_client_agent.py`.