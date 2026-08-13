# GLANCE: 3Blue1Brown redesign

This branch keeps the paper content, section ownership, narration language,
citations and scene order unchanged.  It changes how the existing argument is
made visible.

## Explanatory spine

The film follows a problem-solution arc:

1. Calling an LLM for every node wastes work and can damage good GNN predictions.
2. Hand-written routing rules confuse *GNN difficulty* with *LLM benefit*.
3. Local homophily exposes where the two models complement each other.
4. GLANCE combines cheap signals, ranks nodes under a fixed budget and refines
   only the selected predictions.
5. Counterfactual rewards teach the router whether each LLM call was worth its
   cost; stratified results test the claim where it matters.

The recurring object is `demo_tag()`.  Node 4 is the high-homophily hub and node
9 is the low-homophily node.  Reusing it makes later architecture and result
scenes feel like new views of one object, not unrelated slides.

## Shared visual contract

- Text uses one Vietnamese-capable monospace family; equations remain MathTex.
- GNN is blue, LLM is lime, router is violet, success is mint, failure is red.
- The persistent section header is anchored top-left as `[number][title]`, with
  no divider. Paper sources use the opposite top-right corner so subtitles keep
  the full bottom edge.
- Numbered scene subtitles such as `[02] What happens ...` are not rendered;
  a number-only badge remains beside the section header for render debugging.
  Sequencing labels remain only when they belong to the explanatory diagram.
- Top-level content follows a 12-column grid and a 0.25-unit vertical baseline;
  graph topology may stay organic inside a grid-aligned container.
- Connectors snap only accidental near-horizontal or near-vertical tilt.
  Meaningful graph and fan-out diagonals remain free.
- Adjacent context dims to 10%; anything underneath new text fades out fully.
- Definitions follow a concrete visual.  Equations formalize an image already
  on screen.
- Question frames ask for a prediction before the answer is revealed.
- Each scene keeps one anchor diagram and adds information to it progressively.

## Scene plans changed in this pass

### Section 1: recurring TAG

Template: `BUILD_UP`

- Question: What information exists besides a node's text?
- Anchor: the shared 12-node `demo_tag()`.
- Build: papers become nodes; citations become edges; content and structure
  converge on node A, which aliases shared hub node 4.
- Representation change: documents -> graph -> GNN/LLM routing question.
- Cleanup: remove all overlays before the next internal beat.
- Data: experimental numbers remain sourced through the existing scene code.

### S2_02_TwoQuestions

Template: `DUAL_PANEL`, then linked Venn diagram.

- Question: Which nodes are hard for a GNN, and which actually improve with an
  LLM?
- Anchor: two question cards that morph conceptually into two overlapping sets.
- Answer: only the overlap justifies an LLM call.
- Text: each line is an independent centered mobject, avoiding Pango newline
  alignment drift.
- Cleanup: `clear_scene()` before the first heuristic.

### S3_01_LocalHomophily

Template: `DUAL_PANEL` with a persistent neighborhood.

- Question: How much does node v agree with its neighbors?
- Anchor: node v and four adjacent nodes.
- Build: inspect neighbors first, then reveal the indicator sum and average.
- Concrete value: three matches out of four becomes 0.75.
- Causal test: recolor neighbors from consistent to conflicting and replay
  message passing; the GNN outcome changes in the same diagram.

### S3_02_RelativeDegree

Template: `DUAL_PANEL` plus live number line.

- Question: Compared with its neighbors, how connected is v?
- Anchor: v with two neighbors and their visible extra edges.
- Build: count degrees, motivate the ratio, then show the formula.
- Parameter view: move one marker around the reference value 1 before landing
  on the concrete example.

### S4_02_EndToEnd

Template: `TOP_PERSISTENT_BOTTOM_CONTENT`, then `BUILD_UP`.

- Question: What happens to one familiar node from input to final label?
- Anchor: shared `demo_tag()` with node A mapped to hub node 4.
- Build: graph -> GLANCE -> live class probabilities -> argmax, then open the
  black box into routing, context encoding and refinement.
- Persistent context: the same graph shrinks into the pipeline input.
- Cleanup: the graph and probability view fade before pipeline details reuse
  the center.

### S5_02_TopKProblem

Template: `BUILD_UP` with a live discontinuity.

- Question: Can a gradient pass through top-K?
- Anchor: six scored nodes under a fixed K=2 budget.
- Parameter view: a small score change swaps a rank and makes the discrete
  decision jump.
- Answer: the backward gradient stops at top-K, motivating a reward-based
  objective in the next scene.

## Visual-variety audit

| Section | Primary techniques |
|---|---|
| 1 | document-to-graph morph, persistent TAG, population grid, branching flow |
| 2 | question frame, Venn overlap, graph counterexamples, NCS arithmetic, paired charts |
| 3 | geometry-before-equation, message flashes, number-line sweep, line chart, heatmap, progressive signal assembly |
| 4 | moving camera, persistent overview, live data flow, top-k ranking, ego rings, concatenation morph, MLP diagram |
| 5 | discontinuity animation, counterfactual dual view, live losses, equation build, histograms, ablation bars, scale grid |

No two sections use the same dominant technique as their narrative climax.

## Verification gates

1. `python -m py_compile` for the shared style and all five section files.
2. `python -m unittest discover -s tests -t .` in conda env `graphdm`.
3. Low-quality render of every changed scene.
4. Extract frames near 10%, 25%, 50%, 75% and 90% of each changed scene.
5. Check safe bounds, overlap, semantic color, source stamps, Vietnamese glyphs
   and persistent-element lifecycle.
6. Only after low-quality QA passes, render the final 1080p build.
