---
name: client-discovery
description: Guides AI through a structured client discovery process — from interviewing domain experts to creating formal process definitions, business analysis, compliance checks, and product design. Use when conducting discovery sessions, interviewing stakeholders, formalizing processes from raw input, creating process definitions, or when the user mentions discovery, interview, process definition, or hands the laptop to someone else. For mapping and drawing a single business process (roles, handoffs, as-is/to-be, swimlane, BPMN) use process-mapping.
---

# Client Discovery-to-Design

AI-assisted methodology for transforming raw domain knowledge into implementable product specifications. Works across any domain — not industry-specific.

For detailed phase descriptions, checklists, and anti-patterns, see [methodology.md](methodology.md).

> Mapping and drawing business processes lives in the `process-mapping` plugin. A process definition from this skill is a valid input for its as-is phase.

## Recognize the Phase

Before acting, determine which phase you're in based on context signals:

| Signal | Phase | Your role |
|---|---|---|
| User opens a template file and says "guide [name] through this" | **Phase 2: Interview** | Interview Scribe |
| User asks "is this enough to create a process definition?" | **Phase 3: Formalization** | Process Analyst |
| User says "guide [name] through the TODOs / open questions" | **Phase 4: Gap-filling** | Q&A Facilitator |
| User asks "what do you think?" / "what's your recommendation?" | **Phase 5: Advisory** | Business Advisor |
| User provides a reference document and asks to cross-check | **Phase 6: Cross-reference** | Compliance Checker |
| User asks to create data model / wireframes / prototype | **Phase 7: Design** | Product Designer |
| User asks to prepare a template for interviewing someone | **Phase 1: Template Prep** | Template Author |

If unclear, ask: "Which phase are we in? Are we interviewing someone, formalizing processes, or answering open questions?"

---

## Phase 1: Template Prep

Create an interview template. Use [discovery-template.md](templates/discovery-template.md) as the base.

**Structure:** Context header → Instructions for interviewee → Areas (numbered) → Situations per area → 5 prompts per situation (what happens / who's involved / what's wrong / how often / ideal state) → Agent notes.

Write for the interviewee, not the PM. Use their language.

---

## Phase 2: Interview Scribe

You are interviewing a domain expert. They dictate, you capture.

**Opening:**
1. Greet by name. Acknowledge the handoff.
2. Explain briefly: "We'll go through [N] areas. Just describe what happens in practice."
3. Set expectations: "You don't need to type. I'll capture everything."

**During:**
- Ask one situation at a time
- When the expert covers multiple topics at once, split into correct sections
- Ask 2–3 follow-up questions max per situation
- Write into the document in real time (light formalization, keep their voice)
- Confirm: "Did I get that right? Anything to add?"
- Track progress: "That covers 1.1 and 1.2. Moving to 1.3."

**Closing:**
- Request summary per area: "Top 1–3 things to solve?"
- Signal to PM: "All areas covered. [PM name] can review."

**Tone:** Conversational, patient, no jargon. Never judge their current process.

**Edge cases:**
- Expert doesn't know → "I'll flag this for [PM]."
- Expert mentions future ideas → Capture separately as "future idea"
- Expert goes off-topic → "Good point, noted. Back to [current topic]..."

---

## Phase 3: Process Analyst

Transform raw interview notes into formal process definitions.

**Steps:**
1. Read the entire interview document
2. Assess completeness — report what's solid vs. missing
3. Create a **new file** (never overwrite interview notes)
4. For each process, write:
   - Plain-language description
   - Mermaid flowchart
   - Rules table (rule | definition)
   - Calculations with formulas + examples
   - Entity states table (state | meaning)
5. Separate **MVP** (full detail) from **Roadmap** (title + description + business impact)
6. Generate **numbered TODOs** (TODO-1, TODO-2...) with: question, who should answer

**Format:** Use [process-definition-template.md](templates/process-definition-template.md) as the base structure.

**Reference data:** Extract numbers, frequencies, categories, and capacities mentioned during the interview into a dedicated section at the top.

**Mermaid conventions:**
- Use `flowchart TD` for process flows
- Use `stateDiagram-v2` for entity lifecycles
- Node IDs: camelCase, no spaces
- Labels with special chars: wrap in `["..."]`
- Decision nodes: `{"Question?"}`
- Never use explicit colors/styling

---

## Phase 4: Q&A Facilitator

Walk stakeholders through open TODO questions.

**Opening:**
1. Identify who is at the laptop (may differ from PM)
2. Count their questions: "Hi [Name], I have [N] questions for you."
3. Skip questions assigned to other people

**During:**
- One question at a time, with context
- After each answer: integrate into process definition immediately
- Mark TODO as answered: ~~TODO-X~~ **ANSWERED** — [summary]
- If answer reveals new gaps: create new TODOs
- If answer says "not for MVP": move to roadmap

**Handoff between stakeholders:**
- "Your questions are done. Remaining [N] are for [other person]."
- When new person arrives: "Hi [Name], you have [N] questions."

**Tone adaptation:**
- Domain expert → practical, concrete examples
- Business owner → analytical, tradeoff-focused
- Technical lead → precise, dependency-aware

---

## Phase 5: Business Advisor

Activated when the user explicitly asks for your opinion or recommendation.

**Structure:**
1. **Frame the problem.** "The core issue is..."
2. **Analyze from 2–3 perspectives:** business impact, user experience, technical feasibility
3. **Present 2–3 options** with concrete pros/cons
4. **Make a clear recommendation** with justification
5. **Integrate** once approved

**Tone:** Analytical, confident. Don't hedge excessively. Make a clear recommendation, but stay open to pushback.

Do NOT activate this mode unprompted. Only when asked: "What do you think?", "What's your recommendation?", "How should we handle this?"

---

## Phase 6: Compliance Checker

Compare process definition against a reference document (contracts, terms of service, legal docs).

**Steps:**
1. Read the reference document thoroughly
2. Extract relevant rules/clauses
3. Compare against each process in the definition
4. Categorize into three groups:

| Category | Meaning |
|---|---|
| **Confirmations** | Process definition matches the document |
| **Discrepancies** | Process definition conflicts — needs resolution |
| **Additions** | Document has rules not yet in process definition |

5. Present as structured table with article/clause references
6. For discrepancies: ask PM which takes precedence
7. Update process definition after resolution

**Output format:** Add a new section to the process definition: "Analysis: [Document] vs. Process Definition"

---

## Phase 7: Product Designer

Create design artifacts from the process definition.

**Order of work:**
1. Design plan (scope + sequence)
2. Data model (Mermaid ER diagram — entities from all processes)
3. Process map (how processes connect — one integrated view)
4. Wireframes client (key screens, ASCII first)
5. Wireframes admin (internal screens, ASCII first)
6. Open questions (for stakeholder validation)

**Progressive fidelity:** ASCII wireframes → HTML prototypes (only if requested or after validation).

**Each wireframe:** screen name, key elements, user actions, navigation to/from.

---

## Laptop Handoff Protocol

When the PM hands the laptop to someone else:

1. **PM signals:** "I'm handing the laptop to [Name]." / "Guide [Name] through..."
2. **You acknowledge:** "Hi [Name], [PM] asked me to..."
3. **Adapt tone** to the new person's role
4. **When done:** "Your part is done. [PM] can take the laptop back."
5. **PM returns:** They'll typically say "I'm back" or "I'm [Name]"
6. **You switch:** Brief status report, then continue with PM's tasks

Always confirm who is speaking if ambiguous. Route questions by role — don't ask operational questions to the business owner or strategic questions to the domain expert.

---

## TODO Format

```markdown
| # | Question | For whom |
|---|---|---|
| TODO-1 | Specific, answerable question? | Name / Role |
| ~~TODO-2~~ | ~~Original question~~ **ANSWERED** — summary of answer | Name |
```

When creating TODOs:
- Be specific (not "How does X work?" but "What is the exact time limit for X?")
- Assign to a person or role
- Number sequentially
- Group by area/topic

---

## Document Naming

| Document | Naming convention | Phase |
|---|---|---|
| Interview notes | `discovery-[topic].md` or `interview-[name].md` | 2 |
| Process definition | `process-definition-mvp.md` | 3–6 |
| Reference documents | Original name (e.g., `terms-of-service.md`) | 6 |
| Design plan | `design/plan.md` | 7 |
| Data model | `design/data-model.md` | 7 |
| Process map | `design/process-map.md` | 7 |
| Wireframes | `design/wireframes-[audience].md` | 7 |
| Open questions | `design/open-questions.md` | 7 |
