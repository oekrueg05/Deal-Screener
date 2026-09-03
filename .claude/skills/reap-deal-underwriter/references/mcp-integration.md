# REAP OS MCP Integration

Analysts connect to REAP OS through their own MCP connectors — there is no shared or hardcoded
server URL in this skill. Treat the connection as optional and per-user. REAP OS shows up
differently depending on where this skill is running, so check both surfaces before concluding
it isn't available.

## Detecting the connection

Two possible surfaces — check both, in this order:

1. **Direct tool access** (e.g. Claude Code, or any environment where REAP OS is wired up as a
   regular connector): check whether an MCP server exposing REAP OS deal-inbox tools is already
   available in the current session (tool names will be namespaced to whatever REAP OS calls its
   server, e.g. something like `REAP OS:list_deal_inbox` / `REAP OS:get_deal`). In a chat surface
   with `tool_search`, search for it (e.g. `tool_search(query="REAP OS deal inbox")`) rather than
   assuming it's absent just because it's not in the default tool list. Do not assume a specific
   tool name — inspect what's actually available and use it.

2. **Artifact/API access** (claude.ai chat, where REAP OS may only be exposed as an MCP server URL
   usable from within a generated artifact via the Anthropic API's `mcp_servers` parameter, not as
   a directly callable tool): if step 1 finds nothing, check whether a REAP OS server URL is
   listed among the connectors available for use in artifacts (see the artifact/API guidance
   elsewhere in this environment for the current URL/name). If so, pull the deal inbox by writing
   a small one-off artifact that calls the Anthropic API with that MCP server attached and the
   relevant deal-inbox tool invoked — parse the `mcp_tool_result` block from the response the same
   way you'd parse a direct tool call. This artifact is a means to an end (fetching/writing deal
   data), not something to show the student as a deliverable.

If neither surface has anything REAP-OS-like available, skip straight to asking the student for
materials directly. Don't error, don't tell the student to go set up a connector mid-task unless
they specifically ask why you didn't pull the deal automatically.

## Pulling a deal

- If the student names a specific deal, look it up by name/identifier in the deal inbox.
- If the student just says something like "underwrite the new deal Vito sent," pull the most
  recent unprocessed/unread entry in the deal inbox.
- Expect the deal inbox record to contain some mix of: property name, asset type, location,
  price, unit/SF count, and possibly an attached OM or rent roll file. Map whatever comes back
  onto `input-schema.md` the same way you'd map a pasted OM — fields not present are still
  MISSING and go through `asset-defaults.md` like any other gap.
- If the call fails or returns nothing for a named deal — on either surface — tell the student
  plainly (e.g. "Couldn't find that deal in the REAP OS inbox — can you paste the details or
  upload the OM?") rather than silently falling back.

## Writing the result back

After the model and memo are built, if a REAP OS connection is available on either surface, write
the deal's summary fields (the same set as `deal-log-format.md`'s columns, plus links/paths to the
generated model and memo files if REAP OS has fields for that) back to REAP OS — via the direct
tool if that's how it was reached, or via the same artifact/API pattern used to pull it — so the
deal shows up in the shared deal history right away.

- If REAP OS's write tool expects different field names than `deal-log-format.md`, adapt to
  its actual schema — don't force REAP OS to match this skill's internal naming.
- If the write fails, don't block delivery of the model/memo to the student — just note in your
  reply that the REAP OS write didn't go through, and make sure the local `deal_log.csv` row
  still gets written as the fallback record.

## What this skill does not do

- Does not manage the MCP connector setup itself — if a student needs to connect REAP OS,
  point them to the relevant connector settings for whatever surface they're on, but don't
  attempt to configure it for them.
- Does not assume every analyst has REAP OS connected on either surface — the manual-input path
  (pasted OM, rent roll, raw numbers) must keep working exactly as it did before this integration.
