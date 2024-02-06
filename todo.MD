TODO:
- Add type-checker

Potential features:
- Structured approach for batched data handling and retrieval
- Eventing on commands - customizable supporting queues
- Optimistic concurrency and retries on entity mutation
- Ledger pattern data models as option for entity data storage
- Identity and permissions through configuration
- Structured logging pattern/ approach
- Structured outgoing requests approach
- UI server side rendering and frontend with REST

Started:
- CLI to generate boilerplate
  - Basic arch. and introspection approach

- CQRS
  - versioned commands, queries and their endpoints

- Repo pattern
  - "Unit of Work" repo sessions
  - consistent DB session across request bounds
  - Consistent entity objects across request, bounds (intentional refresh option approach still needed)
