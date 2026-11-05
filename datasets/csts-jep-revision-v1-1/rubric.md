# Training and test audit: entity scope and missing information

Read only the assigned input JSON and this rubric. The inputs contain captions, condition and row ID. Original labels, previous judgments and encoder predictions are withheld. Do not inspect other workspace sources or retrieve labels. Your task is semantic annotation, not prediction matching.

For every example, first identify the requested entity/role and feature, extract its two relevant values, then rate their conditional similarity. Record the scope explicitly. Condition scope controls which mentions count.

## Entity scope

* Explicit role words constrain scope. Riders count people actually riding in the described scene. A surfer explicitly catching a wave counts as an active rider; another surfer merely present in the ocean does not automatically count as an active rider. Players exclude explicitly described spectators. People includes all mentioned humans when no narrower role is specified; animals excludes people.
* Resolve clear coreference. A member described within a previously counted group adds no new entity. A singular noun phrase denotes one described entity. Different species do not change an animal total. A quantity condition compares quantity independently of species/type.
* For generic color/type/activity of an object/person, use the principal comparable entities described by the captions. Incidental collars, snow and background objects do not displace the principal dogs under dog color or generic object color. Specify the adopted referent. Flag materially competing equally salient referents for resolution.
* Conditions naming only an entity default to its type. Keep abstraction level consistent across captions. A general category compared with a specific subtype lacks some relevant specificity; use the graded rubric rather than automatically treating a subtype difference as total dissimilarity.

## Rating rules

* Binary feature comparisons use 1/3/5: 5 for established equality, 1 for established inequality, 3 for possible equality given underspecification. Exact counts, categorical gender, and age-category equality use this rule. For example, exact three versus several gives 3. Mixed known/unknown group genders can give 3 when both captions establish relevant gender information and the remaining group members are unspecified. Missing precision is not itself grounds for exclusion.
* Color combinations and genuinely graded features can require 1..5. For graded similarity: 5 fully equivalent on the condition; 4 mostly equivalent with small relevant differences; 3 roughly equivalent with substantial relevant differences or missing specificity; 2 different with only a broad relevant category in common; 1 different on the requested aspect. Guitar versus violin under instrument type is 2. Explain the semantic comparison.
* Distinguish partial feature information from wholly absent feature information. Exact three versus several has recoverable count information in both captions and gives 3. All women versus a woman plus an opponent of unspecified gender has gender information in both captions and can give 3. A blue bus versus a bus whose color is completely unstated lacks color information in one caption and is invalid under Tu. A merely mentioned person gives no recoverable gender value by itself. If the requested feature cannot be extracted or directly inferred from either member of the pair, or a required entity is absent/inapplicable, mark invalid with a concrete reason. Broad descriptions such as cluttered desk or unmade bed can support direct coarse content inference; decide semantically. A presence condition may establish a negative when supported; mere silence does not prove absence.
* Permit ordinary direct high-confidence context: pie/cake as desserts, ordinary sidewalk as level, tennis equipment from tennis, bathroom from toilet/sink, and standard scene/activity implications. Avoid speculative proper identities, unusual situations and unsupported fine details. Treat common context consistently.
* Uncertainty about fine detail differs from uncertainty about the condition's actual referent. Use status needs_scope only when materially different plausible referents/features yield different ratings that the frozen conventions cannot resolve. Supply the best proposed rating and alternatives. A difficult decision or an alternative imaginable in an unusual world is not by itself a scope dispute.

## User-adjudicated anchors

These are semantic policy anchors: pie versus cake under meal type=5; level sidewalk versus ascending stairs under ground angle=1; one active wave rider versus two surfers with one explicitly catching a wave under number of riders=5. These anchor labels stay fixed by user adjudication.

## Output

Write an exhaustive JSON list, in assigned input order, to the assigned review JSON:

{"row_id":"...", "scope":"requested referent/feature, concise", "value_a":"...", "value_b":"...", "status":"rated|invalid|needs_scope", "rating":1..5|null, "confidence":"high|medium|low", "rationale":"one short concrete explanation", "issue_tags":["role_scope|entity_scope|counting|missing_value|direct_inference|graded_type|none"]}

For invalid, rating is null. For needs_scope, include "alternatives" listing different readings/ratings. Use manual semantic judgment for every row. Scripts may format or validate judgments; do not substitute lexical heuristics or default labels for reading captions. Work in batches of roughly 75 to 105 examples and save complete reviewed prefixes after each batch. This is an assistant-model review, not human annotation. Do not run any model API, GPU or training job.

Validity clarification (frozen before second review and model rescoring): wholly absent requested feature information in even one caption is invalid under Tu. Partial recoverable values in both captions can justify 3. The earlier draft wording allowing all wholly unknown attributes to become 3 was too permissive and is superseded by this paragraph.


## User continuation adjudications

Validation exclusion report items 13 (train_624) and 27 (train_1075) were approved for inclusion by the user during this audit. A sippy cup among meal items supports ordinary inference of one beverage for beverage count. A bowl of food and a plate of food provide coarse serving-amount information; lack of measured amounts does not invalidate the comparison. Root-assigned numerical ratings are 5 and 3 respectively; the user explicitly approved inclusion, not numerical labels. Apply these conventions to analogous training/test cases. This does not infer exact contents, color, or temperature from a vessel. Preserve prior judgments and document any retrospective corrections.

The user also approved items 59 (train_1809, size of cow: lean versus large) and 64 (train_2022, room type: computer/furniture/window versus television/books/relaxed occupant). Root assigns 3 to each. Explicit body-build information supports a partial size comparison even when dimensions differ; lean and large can coexist. Described furnished indoor rooms supply partial room-type information even when the exact function is uncertain. This does not make wholly absent size or room information recoverable. These are user inclusion decisions with assistant-assigned numerical grades.

### Later user confirmation: original exclusions before #64

The user then confirmed the ORIGINAL exclusion rationales for all other review-flagged entries before #64. The exact 12 confirmations are in `user_confirmed_original_exclusions_before64.json` (items 6, 7, 11, 14, 15, 16, 26, 28, 31, 50, 58 and 63). This narrows overly broad readings of the preceding paragraph: #64 has computer/television functional clues; generic cushioned furniture or a messy room alone does not supply a room function. Generic food supplies no food type; unnamed wines and diversity alone supply no wine-type identities. Furnishings alone do not establish decor style, 'packed lunch' alone does not identify packaging type, cloudy alone does not identify sky hue, a static plated-food arrangement establishes no named human activity, and an unspecified road sign does not establish an illuminated traffic-signal type. The singular person's-age case with competing foreground child and couch adult remains unresolved scope. Preserve these confirmed exclusions, while the four explicit inclusion decisions take precedence. Apply analogous boundaries semantically, with a source reread and correction history.

### Feature granularity after the confirmation

Extract information at the level requested, rather than excluding because a particular word repeats. For an explicit subtype condition such as wine type, bird type, or musical-instrument type, the generic target noun without contextual subtype information is insufficient. A broader actual category can still support a comparison: Italian cuisine under food type, vegetables under food type, a computer under object type, or striking actions under martial-art type provide relevant information. Concrete entity-only conditions must not acquire an unrequested fine subtype: frozen V4 labels train_1192 (`train`), train_823/4462 (`bed`) and train_3362 (`cat`) accept the shared concrete identity. V4 train_4587 (`food`) is excluded when no food category at all is identified. Preserve this semantic distinction; there is no lexical repeated-noun exclusion rule.
