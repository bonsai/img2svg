# img2svg Ontology

## 1. Purpose

img2svg is a **raster-to-structured-vector transformation system** for DTPX.

The ontology describes semantic relationships between:

- source images
- conversion intent
- agents
- vectorization engines
- SVG artifacts
- verification observations
- cost
- visual quality
- granularity
- optimization decisions

This is not a data dictionary. It defines **what entities mean and how they relate**.

## 2. Core ontology

```
Image
  │
  ├─ has → Intent
  │          │
  │          └─ interpreted_by → JEV
  │
  └─ transformed_by → Vectorizer
                         │
                         └─ produces → SVG
                                      │
                                      ├─ has → Complexity
                                      └─ rendered_as → RasterObservation
                                                        │
Image ──────────────────────────────────────────────────┘
                                                        ↓
                                                   Verifier
                                                        │
                                      ┌─────────────────┴──────────────┐
                                      ↓                                ↓
                                VisualQuality                       Cost
                                      │                                │
                                      └──────────┬─────────────────────┘
                                                 ↓
                                            Optimizer
                                                 │
                                      evaluates → Candidate
                                                 │
                                      selects → Granularity
                                                 ↓
                                      Recommendation
                                                 │
                                                 ↓
                                               DTPX
```

## 3. Entities

### Image

The original raster asset.

An Image is the **source artifact**, not the semantic meaning of the image.

Relations:

- `has_intent → Intent`
- `input_to → Vectorization`
- `compared_with → RenderedSVG`

### Intent

The purpose or visual role inferred for conversion.

Examples:

- `logo`
- `lineart`
- `diagram`
- `illustration`
- `photo`
- `figure`
- `text-heavy`

Intent is not the output format. It determines which conversion strategy should be explored.

### JEV

The decision/routing agent.

JEV answers:

> What kind of conversion should be attempted, and what search space is appropriate?

Relations:

- `interprets → Image`
- `classifies → Intent`
- `proposes → Route`
- `controls → SearchSpace`

JEV does not perform deterministic vector rendering.

### Route

A conversion strategy.

A Route contains semantic decisions such as:

- engine
- mode
- hierarchical strategy
- color budget
- speckle filtering
- granularity range

Relations:

- `chosen_by → JEV`
- `executed_by → Vectorizer`

### Vectorizer

A deterministic transformation component.

Current implementation:

- VTracer

Relation:

`transforms Image → SVG`

The Vectorizer should not decide the business meaning of the image.

### SVG

The structured vector artifact.

SVG is an **intermediate representation**, not merely an output file.

Relations:

- `produced_by → Vectorization`
- `has_complexity → Complexity`
- `rendered_to → RasterObservation`
- `consumed_by → DTPX`

### Granularity

The abstraction level of vector representation.

`0.0` means coarse representation.

`1.0` means fine representation.

Granularity is not identical to any single VTracer parameter. It is a **control variable** mapped to several renderer parameters.

```
granularity
    ↓
max_colors
filter_speckle
curve/detail settings
mode
...
```

### Candidate

One concrete conversion produced from one point in the search space.

A Candidate is:

```
Image + Route + Granularity → SVG + Measurements
```

Relations:

- `generated_from → Image`
- `uses → Route`
- `has_granularity → Granularity`
- `produces → SVG`
- `observed_by → Verifier`

### Verifier

The observation component.

It does not decide what is aesthetically correct.

It measures the difference between:

```
original Image
       ↕
rasterized SVG
```

Current observations include:

- mean absolute difference
- RMS difference
- SVG element count

Future observations may include:

- perceptual similarity
- OCR preservation
- edge preservation
- color difference

### VisualQuality

An evaluation derived from observations.

It answers:

> How much visual information was preserved?

It is distinct from subjective design quality.

### Complexity

A measurable property of the SVG representation.

Examples:

- element count
- path count
- file size
- color count
- path length
- processing time

### Cost

The computational or representation cost of a Candidate.

Cost may include:

```
render_time
SVG_bytes
element_count
memory
agent_calls
VLM_calls
```

Cost is extensible because DTPX may eventually use different cost models for Web, EPUB, PDF, and print.

### Optimizer

The component that compares Candidates.

It does not create SVGs.

It evaluates the trade-off:

```
VisualQuality ↔ Cost
```

The intended decision model is Pareto-based rather than simply maximizing visual quality.

### ParetoFrontier

The set of Candidates for which no other Candidate is simultaneously:

- at least as visually good
- and no more expensive

with one dimension strictly better.

### KneePoint

A Candidate near the point where additional cost produces diminishing visual improvement.

This is the principal basis for the recommended granularity.

### Recommendation

The proposed conversion setting.

A Recommendation contains:

- selected granularity
- selected Route
- expected visual quality
- expected cost
- reason/evidence

A Recommendation is **not the same thing as the final artifact**.

### DTPX

The consuming/editing system.

DTPX receives structured vector assets as part of the larger publishing compilation pipeline.

```
semantic content
      ↓
DTPX
      ↓
page representation
      ↓
SVG / PDF / EPUB
```

img2svg supplies one class of structured visual asset to this system.

## 4. Agent boundaries

```
JEV
 ├─ understand
 ├─ classify
 └─ route

VTracer
 └─ transform

Verifier
 └─ observe

Optimizer
 ├─ compare
 ├─ calculate Pareto frontier
 └─ select knee point

DTPX
 └─ compose / publish
```

No component should silently absorb another component's responsibility.

## 5. Fundamental transformations

### Semantic routing

```
Image → JEV → Intent → Route
```

### Deterministic conversion

```
Image + Route → VTracer → SVG
```

### Verification

```
SVG → rasterization → Observation
Image ────────────────────┘
```

### Optimization

```
Candidates → ParetoFrontier → KneePoint → Recommendation
```

### Publishing

```
Recommendation + SVG → DTPX
```

## 6. JSONL observation vocabulary

JSONL is the operational representation of ontology instances.

Example:

```json
{"type":"intent","input":"logo.png","intent":"logo"}
{"type":"route","input":"logo.png","engine":"vtracer","granularity":0.5,"max_colors":8,"filter_speckle":4}
{"type":"candidate","input":"logo.png","granularity":0.5,"svg":"build/logo-050.svg"}
{"type":"observation","candidate":"logo-050","visual_quality":0.93,"svg_elements":421,"bytes":28100,"render_time_ms":184}
{"type":"recommendation","input":"logo.png","granularity":0.5,"selection_method":"knee-point"}
```

The JSONL is an **instance/event representation** of this ontology; it is not the ontology itself.

## 7. Key semantic distinction

The central distinction is:

```
meaning       → JEV
strategy      → Route
transformation → VTracer
artifact      → SVG
observation   → Verifier
trade-off     → Optimizer
composition   → DTPX
```

This allows the implementation to replace VTracer, add a VLM, or introduce other vectorizers without changing the core ontology.

## 8. Future extensions

Potential entities:

- VLM
- LLM
- OCR
- SemanticRegion
- TextRegion
- Shape
- Layer
- MediaProfile
- PrintProfile
- WebProfile
- EPUBProfile
- HumanReview
- DesignConstraint
- BrandConstraint

The ontology should grow by adding semantic entities and relations, not by turning every implementation parameter into a first-class concept.
