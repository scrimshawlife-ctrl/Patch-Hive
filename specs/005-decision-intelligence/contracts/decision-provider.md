# Contract — DecisionProvider

Provider-neutral interface:

```python
class DecisionProvider(Protocol):
    def choose(self, request: ChoiceRequest) -> DecisionPacket: ...
    def score(self, request: ScoreRequest) -> DecisionPacket: ...
    def probability(self, request: ProbabilityRequest) -> DecisionPacket: ...
```

## ChoiceRequest
- request_id
- contract_version
- purpose
- evidence_hash + evidence_refs
- choices: stable IDs + concise descriptions
- context: normalized JSON only
- timeout budget

## DecisionPacket
- decision_id
- request_id
- contract_version
- provider
- provider_version
- evidence_hash
- candidate_set_hash / rubric_hash
- result
- probabilities or score where supported
- provider_status
- created_at
- raw_payload_hash (optional)
- no canonical mutation fields

## Rules

1. Adapter output MUST validate before policy sees it.
2. Unknown fields do not acquire authority.
3. Provider-specific metadata stays in adapter/diagnostic storage.
4. Request and packet schemas are versioned.
5. Identical packet + policy version yields identical disposition.
