# References and version choices

Checked November 2, 2026. The runnable dependency lock resolves MCP Python SDK **2.3.0**. The examples use its v2 API, including `from mcp.server import MCPServer` and `from mcp import Client`.

- [Official Python SDK](https://py.sdk.modelcontextprotocol.io/)
- [First steps and primitives](https://py.sdk.modelcontextprotocol.io/get-started/first-steps/)
- [Running a server and transport choices](https://py.sdk.modelcontextprotocol.io/run/)
- [Client transports and header configuration](https://py.sdk.modelcontextprotocol.io/client/transports/)
- [Authorization and token verification](https://py.sdk.modelcontextprotocol.io/run/authorization/)
- [MCP specification](https://modelcontextprotocol.io/specification/2026-07-28)
- [MCP Tasks extension](https://modelcontextprotocol.io/extensions/tasks/overview)
- [OpenAI plugin submission](https://developers.openai.com/plugins/deploy/submission)
- [OpenAI plugin guidelines](https://developers.openai.com/plugins/plugin-guidelines)
- [Claude connector submission](https://claude.com/docs/connectors/building/submission)
- [Claude connector review checklist](https://claude.com/docs/connectors/building/review-criteria)

Application choices such as SQLite operation ledgers, queue leases, quotas and revision preconditions are tutorial designs, not guarantees provided automatically by the MCP protocol. Directory requirements can change; the evidence lesson does not submit anything.

## Store track and packaging

The six store lessons are local fictional teaching fixtures. Provider calls are real loopback HTTP; no external geocoding, courier, payment or production identity service is contacted. The publication format sources and checked example repository are linked in [publication/SOURCES.md](publication/SOURCES.md) and [publication/README.md](publication/README.md). The original documentation track is preserved.
