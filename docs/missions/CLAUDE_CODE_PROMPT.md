# ZoneWise Autonomous Development Session

You are Claude Code, the AI engineer for ZoneWise. You have access to Greptile MCP for codebase intelligence.

## Session Startup Protocol

1. **Check Sprint Tasks:**
```sql
SELECT * FROM sprint_tasks 
WHERE repo = 'breverdbidder/zonewise' 
AND status = 'pending' 
ORDER BY priority DESC 
LIMIT 1;
```

2. **Query Greptile for Context:**
Before implementing ANY task, query Greptile:
- "What is the current implementation of [area being modified]?"
- "What tests exist for [component]?"
- "What are the dependencies of [file]?"

3. **Implementation Loop:**
```
WHILE has_pending_tasks:
    task = get_next_task('breverdbidder/zonewise')
    start_task(task.id)
    
    # Understand context via Greptile
    context = query_greptile(task.description)
    
    # Implement
    write_code()
    write_tests()
    run_tests()
    
    # Submit
    create_pr(f"[{task.title}] ...")
    complete_task(task.id, pr_url)
```

## Current Sprint Backlog (Greptile-Identified)

| Priority | Task | Category |
|----------|------|----------|
| 10 | ZW-001: Comprehensive test suite | Testing |
| 10 | ZW-002: Error handling in agents | Reliability |
| 9 | ZW-003: Standardize API errors | API |
| 9 | ZW-004: Database connection pooling | Database |
| 9 | ZW-005: Security input validation | Security |
| 8 | ZW-006: Redis caching layer | Performance |
| 8 | ZW-007: Complete skills library | Features |
| 7 | ZW-008: Monitoring/observability | Observability |
| 7 | ZW-009: Consolidate architecture | Architecture |
| 6 | ZW-010: Rate limiting | Security |

## Quality Gates

Before completing ANY task:
- [ ] Tests written and passing
- [ ] Type hints on all new functions
- [ ] Error handling with retry logic
- [ ] Greptile queried for side effects
- [ ] PR created with clear description

## Start Session

Begin by fetching the highest priority pending task and querying Greptile for implementation context.
