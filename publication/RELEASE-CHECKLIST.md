# Release checklist — not satisfied by the local teaching server

- [ ] Own the public endpoint and have permission to integrate each downstream service.
- [ ] Implement production account authorization, object ownership checks, read/write scopes and host-appropriate checkout.
- [ ] Verify each tool in the actual host with an account that has sample products and orders.
- [ ] Keep placement retry-safe and distinguish cancellation from a settled refund.
- [ ] Publish accurate privacy, terms, support and usage documentation under the real publisher identity.
- [ ] Make the required review recording and positive/negative scenarios reproducible.
- [ ] Supply accurate titles, read/write/open-world hints and host-required justifications; resolve every required validation error.
- [ ] Keep reviewer credentials and client secrets out of the package and source repo.
- [ ] Complete the target platform's verification, scan, review and publication controls.
- [ ] Verify the listing and connection from a fresh user context; monitor failures and preserve compatibility.

ChatGPT needs a production remote integration, not the loopback token-verification fixture. Claude/Cursor use repository submission; a ZIP alone does not submit the plugin. Hermes requires a pinned catalog PR. Muse uses its own intake. Instinct's public route is unverified.
