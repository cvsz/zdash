# Realtime Event Model

The realtime event system provides live updates to the frontend via WebSockets.

- **Connection**: Authenticated using standard token methods.
- **Scoping**: Subscriptions are strictly scoped to the user's current `organization_id` and `workspace_id`.
- **Events**: Include system alerts, trading signals, and worker task updates.
