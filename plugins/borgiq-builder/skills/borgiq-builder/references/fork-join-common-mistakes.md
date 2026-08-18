# Fork/ForkJoin Common Mistakes

This reference covers common mistakes when working with parallel execution and the fork/forkJoin pattern in BorgIQ workflows.

## Table of Contents

- [Understanding Parallel Execution](#understanding-parallel-execution)
- [Mistake 1: Using inject to merge parallel results](#mistake-1-using-inject-to-merge-parallel-results)
- [Mistake 2: Thinking fork is required for parallel execution](#mistake-2-thinking-fork-is-required-for-parallel-execution)
- [Mistake 3: Using fork for fire-and-forget notifications](#mistake-3-using-fork-for-fire-and-forget-notifications)
- [Mistake 4: Adding multiple sourcePorts to MessageProcessorActor for fork](#mistake-4-adding-multiple-sourceports-to-messageprocessoractor-for-fork)
- [Decision Matrix](#decision-matrix)
- [Visual Guide](#visual-guide)

---

## Understanding Parallel Execution

**Key concept:** Parallel execution is AUTOMATIC in BorgIQ. When an actor connects to multiple downstream actors, they all run concurrently without any explicit fork.

**When to use fork/forkJoin:** ONLY when you need to synchronize and recombine results from parallel paths into a single message.

### Quick Examples

**Parallel without fork (D runs twice):**
```yaml
# A connects to both B and C
# B connects to D
# C connects to D
# Result: D executes twice - once with B's output, once with C's output
```

**Parallel with forkJoin (D runs once with combined results):**
```yaml
# A connects to Fork
# Fork connects to B and C (with path names)
# B and C both connect to ForkJoin
# ForkJoin connects to D
# Result: D executes once with bundled results from both B and C
```

---

## Mistake 1: Using inject to merge parallel results

### WRONG approach:
```
SetVariables → APICall1 → MessageProcessorActor (inject) → ProcessResults
            → APICall2 → MessageProcessorActor (inject) → ProcessResults
            → APICall3 → MessageProcessorActor (inject) → ProcessResults
```

**Why it fails:** The MessageProcessorActor executes THREE times (once per upstream actor). Each execution only has access to ONE upstream result, not all three combined. The "merge" never actually happens.

### CORRECT approach:
```
SetVariables → Fork → APICall1 → ForkJoin → ProcessResults
                   → APICall2 →
                   → APICall3 →
```

**Why it works:** `fork` tracks parallel paths. `forkJoin` waits for ALL paths to complete, then emits ONE message containing all results bundled together.

---

## Mistake 2: Thinking fork is required for parallel execution

### WRONG thinking:
"I need to add a fork actor to make B and C run in parallel"

### Reality:
Parallel execution is AUTOMATIC in BorgIQ. When actor A connects to both B and C, they run concurrently without any explicit fork.

### When to use fork:
ONLY when you need to synchronize and recombine results from parallel paths into a single message.

---

## Mistake 3: Using fork for fire-and-forget notifications

### WRONG:
```
ProcessOrder → Fork → SendEmail → ForkJoin → Done
                   → SendSlack →
```

**Why it's wrong:** If you don't need the combined results of email and Slack sends, fork/forkJoin adds unnecessary complexity and latency (waiting for both to complete).

### CORRECT (simpler):
```
ProcessOrder → SendEmail
            → SendSlack
```

**Why it's correct:** Both notifications run in parallel automatically. Each completes independently. No synchronization needed.

---

## Mistake 4: Adding multiple sourcePorts to MessageProcessorActor for fork

### WRONG:
```yaml
# Fork actor with multiple sourcePorts - THIS IS INCORRECT
sourcePorts:
  - id: SPRTsource1
    name: Source1
  - id: SPRTsource2
    name: Source2
  - id: SPRTdefault
    name: Default
```

**Why it's wrong:** MessageProcessorActor ALWAYS has only `SPRTdefault` as its sourcePort, regardless of action type. The fork action simply injects a `forkId` into the message stream—parallel paths are created via multiple edges, not multiple sourcePorts.

### CORRECT:
```yaml
# Fork actor with only SPRTdefault
sourcePorts:
  - id: SPRTdefault
configuration:
  options:
    action: fork  # Just the action - fork injects forkId into message
edges:
  # Parallel paths created by multiple edges, all using SPRTdefault
  EDGE01xxx:
    sourcePortId: SPRTdefault
    targetActorId: ACTR01api1actor
    type: borgiqEdge
  EDGE01yyy:
    sourcePortId: SPRTdefault
    targetActorId: ACTR01api2actor
    type: borgiqEdge
```

**Key rule:** Only RouterActor, AiRouterActor, InterfaceActor, AiAgentActor, and AgentHarnessActor use multiple sourcePorts. MessageProcessorActor always uses only `SPRTdefault`.

---

## Decision Matrix

| Scenario | Use Fork/ForkJoin? | Reason |
|----------|-------------------|--------|
| Call 4 job APIs, normalize ALL results together | **YES** | Need combined data for normalization |
| Send email AND Slack notification | **NO** | Fire-and-forget, no combined result needed |
| Fetch user profile AND user settings, then merge | **YES** | Downstream needs both datasets |
| Log to 3 different systems | **NO** | Independent operations, no recombination |
| Query 3 databases, return unified response | **YES** | Response requires all query results |
| Trigger 3 webhooks for external systems | **NO** | External systems process independently |

---

## Visual Guide

### Parallel WITHOUT fork (D runs multiple times):
```
     A
    /|\
   B C D      ← B, C, D all run concurrently when A emits
   | | |
   E F G      ← E runs once (from B), F runs once (from C), G runs once (from D)
```

### Parallel WITH fork/forkJoin (E runs once with combined results):
```
     A
     |
   Fork       ← Marks start of tracked parallel paths
    /|\
   B C D      ← B, C, D all run concurrently (same as above)
    \|/
  ForkJoin    ← Waits for ALL paths, bundles results
     |
     E        ← E runs ONCE with access to B, C, and D results
```

---

## Related References

- [workflow-patterns.md](workflow-patterns.md) - Complete workflow pattern examples including fork/forkJoin
- [message-processor-actor.md](message-processor-actor.md) - MessageProcessorActor actions including fork, forkJoin, split, collect
