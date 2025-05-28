# Agent to Agent (A2A) protocol using Strands Agent SDK


## Getting started

### An example Strands agent that helps with searching AWS documentation.

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. Configure AWS credentials, follow instructions [here](https://cuddly-sniffle-lrmk2y7.pages.github.io/0.1.x-strands/user-guide/quickstart/#configuring-credentials).
3. Start the A2A server using `uv run __main__.py`.
4. Run the test client `uv run test_client.py`.


### An example Strands agent that work as calculator
1. Start the A2A server using `uv run __main2__.py`.

### An Agent developed with Strands SDK work with above 2 agents via A2A protocal
1.  Start the client using `uv run a2a_client_agent.py`.