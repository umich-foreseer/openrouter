# Foreseer OpenRouter

Team-funded model access for Foreseer researchers at U-M. Members create their own API keys after an administrator assigns a budget to each member. The default allowance is **$100 per person per month**, across their keys and chatroom usage.

**Start with the [researcher guide](WIKI.md).**

| Looking for… | Read… |
| --- | --- |
| Access, usage, budgets, and data handling | [Researcher guide](WIKI.md) |
| Invitations, member budgets, and billing — for administrators | [Admin guide](ADMIN.md) |
| Small synchronous and Batch REST examples | [Examples guide](examples/README.md) |
| Historical setup evidence | [Initial rollout record](ROLLOUT.md) |

Choose models directly from the [OpenRouter catalog](https://openrouter.ai/models). There is no team model list or allowlist. Use official REST APIs or your preferred compatible client; the repository contains documentation and examples, not a team SDK or administration service.

The examples require Python 3.10+ and use only the standard library. They preview locally by default; `--send` makes a paid request. Keep credentials outside the repository.

Run tests with mocked network responses using `python3 -m unittest discover -s tests -v`. They make no network requests.
