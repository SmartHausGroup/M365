# ADR 0001: Repository Structure and Technology Choices

Status: Accepted

Context:
We need an enterprise-ready structure to build multiple M365-related services with shared libraries, CI, and strong engineering practices.

Decision:
- Use Python 3.11, FastAPI for service surfaces initially.
- Use `src/` layout with packages: `smarthaus_common`, `smarthaus_graph`, `provisioning_api`.
- Add Typer-based CLI for developer operations.
- Add CI with lint, typecheck, tests.

Consequences:
- Enables incremental addition of services.
- Clear separation of concerns and reusable Graph client.

