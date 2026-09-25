# Data model

Initial implementation SHOULD prefer append-only decision records.

## decision_requests
- id (stable UUID/string)
- contract_version
- purpose
- evidence_hash
- candidate_set_hash/rubric_hash
- idempotency_key (unique)
- created_at

## decision_attempts
- id
- request_id FK
- provider
- provider_version
- attempt_number
- status
- latency_ms
- error_code nullable
- raw_payload_hash nullable
- created_at

## decision_packets
- id
- request_id FK
- attempt_id FK
- schema_version
- result_json
- result_hash
- created_at

## decision_dispositions
- id
- decision_packet_id FK
- policy_version
- disposition
- reason_codes JSON
- created_at

No table above may directly update canonical inventory. Existing confirmation/application services own that transition.
