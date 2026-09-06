# Foreseer OpenRouter

Shared funding for approximately ten U-M researchers. Each person has an individual capped inference key. Jimmy (`jimmyzxj`, GitHub `xingjian-zhang`) is the sole OpenRouter administrator. Calls go directly to OpenRouter; no proxy, VM, or Great Lakes setup.

**Start with [WIKI.md](WIKI.md).** Python 3.10+, standard library only. Installation and previews make no paid inference requests.

- `admin.py`: Jimmy-only key administration and usage exports.
- `examples/request.py`: bounded synchronous request with explicit model/provider.
- `examples/batch.py`: text-only Batch beta preview, submission, and status.
- `tests/`: run `python3 -m unittest discover -s tests -v`.

Credentials and private admin state must stay outside this checkout. Researchers receive repository read access later; no invitations are included in the initial rollout.
