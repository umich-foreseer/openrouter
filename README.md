# Foreseer OpenRouter

Team-funded access to model APIs for Foreseer researchers at U-M. Use your individual API key to call OpenRouter from Python and record the model, provider, and cost of your experiments.

**New here? Start with the [researcher guide](WIKI.md).** It covers requesting access, making your first request, and planning an experiment.

| Looking for… | Read… |
| --- | --- |
| Access, allowances, data use, or troubleshooting | [Researcher guide](WIKI.md) |
| Shared model list and request defaults | [models.json](models.json) |
| Commands for running and adapting the sample scripts | [Examples guide](examples/README.md) |
| Key administration and billing procedures — for Jimmy | [Admin runbook](ADMIN.md) |
| Evidence from the initial setup | [Dated rollout record](ROLLOUT.md) |

Use the official OpenRouter REST API or your preferred compatible client. This repository supplies a shared configuration file and small direct-API examples, not a client framework.

The examples need Python 3.10+ and use only the standard library. They preview requests by default; sending requires an explicit flag. Credentials belong outside this repository.

## Repository contents

- `models.json`: the shared, explicitly reviewed model list and example defaults.
- `examples/`: small synchronous and Batch scripts to adapt for research.
- `admin.py`: Jimmy's key lifecycle and usage-reporting CLI.
- `tests/`: mocked CLI tests; run `python3 -m unittest discover -s tests -v` from the repository root.
