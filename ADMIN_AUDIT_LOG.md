# ADMIN_AUDIT_LOG

## Schema
Table: `admin_audit_log`

| Column | Type | Notes |
| --- | --- | --- |
| id | int | Primary key |
| actor_user_id | int | FK to users (nullable) |
| actor_role | string | Role at time of action |
| action_type | string | e.g. `credits.grant`, `module.status.update` |
| target_type | string | e.g. `user`, `module`, `export` |
| target_id | string | Optional identifier |
| delta_json | json | Field-level change description |
| reason | text | Required for destructive-ish actions |
| created_at | datetime | UTC timestamp |

## Examples

### Credits grant
```json
{
  "actor_user_id": 12,
  "actor_role": "Admin",
  "action_type": "credits.grant",
  "target_type": "user",
  "target_id": "42",
  "delta_json": {"credits_delta": 3},
  "reason": "manual adjustment",
  "created_at": "2024-09-22T12:00:00Z"
}
```

### Module tombstone
```json
{
  "actor_user_id": 12,
  "actor_role": "Ops",
  "action_type": "module.status.update",
  "target_type": "module",
  "target_id": "88",
  "delta_json": {"from": "active", "to": "tombstoned"},
  "reason": "invalid specs",
  "created_at": "2024-09-22T12:10:00Z"
}
```
