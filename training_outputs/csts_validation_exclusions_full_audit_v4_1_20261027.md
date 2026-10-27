# Full audit of excluded validation comparisons

**Snapshot:** validation audit version 4.1, commit `2fba6facd338afe79d00507d5904b954fb301600`. All **258 current exclusions** are documented below. Current labels, inclusion decisions, training examples and saved predictions remain fixed during this documentation review.

## Summary statistics

| Measure | Count |
|---|---:|
| Original validation comparisons | 1,830 |
| Currently usable | 1,572 |
| Excluded comparisons | 258 |
| Excluded share of original validation | 14.10% |
| Invalid | 257 |
| Excluded for unresolved scope | 1 |
| Distinct excluded condition strings | 197 |
| Excluded caption pairs | 239 |
| Excluded source groups | 208 |
| Previously excluded in version 3 | 255 |
| Previously accepted in version 3, now excluded | 3 |

The three newly excluded comparisons are `train_1693`, `train_3209` and `train_7271`. The current scope exclusion is `train_1693`. Every excluded comparison has a null current rating. Original supplied ratings are preserved as historical source values.

### Recorded exclusion reasons

| Primary reason | Comparisons | Share of exclusions |
|---|---:|---:|
| Requested attribute absent in caption A | 97 | 37.6% |
| Requested attribute absent in caption B | 89 | 34.5% |
| Requested attribute absent in both captions | 33 | 12.8% |
| Required entity absent or inapplicable | 29 | 11.2% |
| Inference threshold | 9 | 3.5% |
| Unresolved referent | 1 | 0.4% |

One primary reason is assigned per comparison, so this table sums to 258. Policy codes can overlap. Missing-side codes describe the documentation review; Scope can flag a referent issue within an invalid record as well as the single formal scope exclusion.

### Semantic nature of conditions

| Condition family | Comparisons | Share of exclusions |
|---|---:|---:|
| Color/appearance | 83 | 32.2% |
| Identity/type | 40 | 15.5% |
| Count/quantity | 38 | 14.7% |
| Presence/absence | 18 | 7.0% |
| Location/scene | 15 | 5.8% |
| Spatial relation/posture | 15 | 5.8% |
| Action/activity | 13 | 5.0% |
| Other | 12 | 4.7% |
| Emotion/sentiment | 8 | 3.1% |
| Age | 5 | 1.9% |
| Purpose/function | 4 | 1.6% |
| Composition/contents | 3 | 1.2% |
| Gender | 3 | 1.2% |
| Time/event | 1 | 0.4% |

Families and primary reasons are assistant-coded descriptive categories for this report. Each case retains its exact condition wording.

### Policy-consistency review

| Documentation flag | Comparisons | Share of exclusions |
|---|---:|---:|
| Policy consistent | 204 | 79.1% |
| Review scope or feature | 38 | 14.7% |
| Review ordinary inference | 15 | 5.8% |
| Check recorded rationale | 1 | 0.4% |

**54 comparisons have review flags:** 38 about scope or feature granularity, 15 about ordinary contextual inference and one about the recorded rationale. These flags identify questions for your adjudication. They preserve the current exclusions and supply no replacement labels. The remaining 204 align with the documented policy in this assistant review.

The rationale flag is `train_5292`: the adopted scope is physical stature, and both captions omit stature. The recorded reason also discusses unavailable elevation. Caption B explicitly places the skateboarder in the air, mid jump. Your review can settle whether the intended feature is stature or elevation and whether the recorded reason needs revision.

## Exact policy and decision procedure

The following codes are navigation labels for the policy text used during the audit. The verbatim rubric and resolution policy are reproduced at the end. The version-4.1 implementation repair changed calibration preservation through explicit decision classes; its exclusion criteria and 258 excluded-example IDs stayed fixed.

| Code | Operational rule |
|---|---|
| S1 | Requested entity and role scope; principal comparable referent |
| S2 | Entity-only condition defaults to type |
| S3 | Required feature wholly unavailable in either caption or required entity absent |
| S4 | Partial recoverable information supports a comparison; missing precision alone supplies no exclusion |
| S5 | Ordinary direct high-confidence context permitted |
| S6 | Unsupported fine details, speculative identity or unusual assumptions exceed inference threshold |
| S7 | Ambiguity requires materially competing referents/features and ratings beyond the scope conventions |
| S8 | Reader disagreement alone supplies no ambiguity exclusion |

### How the rules were applied

1. Identify the requested entity or role and feature. Active rider counts follow actual riding; incidental participants follow the condition scope. Entity-only conditions default to type.
2. Extract a relevant value from each caption using direct wording or ordinary high-confidence context. Generic type information can supply a coarse value.
3. When both captions provide recoverable partial values, use the rating scale to represent possible equality or incomplete correspondence. Fine precision alone supplies no exclusion.
4. A wholly unavailable requested attribute in either caption, or an absent/inapplicable required entity, receives invalid status and a null rating.
5. A scope exclusion requires concrete competing interpretations with different comparison outcomes that the scope conventions leave unresolved. Reader disagreement alone supplies no scope exclusion.
6. Preserve user-adjudicated anchors and defensible calibration-only grades. Record focused semantic adjudication and any final quality-check exception.

The invalidity wording was clarified during the first review. All six readers revisited affected records before final adjudication. The exact final wording appears in the verbatim archive. Ordinary inference was evaluated case by case, including 16 recorded root quality decisions; the case-level reasons and present review flags expose places where its application may warrant discussion.

### What the documentation check covers

Six separate assistant contexts reviewed 43 current exclusions each. They received captions, exact conditions, current exclusions, adopted scopes/values and recorded reasons. They mapped the existing decisions to policy clauses and flagged potential conflicts. Encoder predictions and original numerical ratings were withheld from that documentation pass. Original supplied ratings are added to this final report for provenance. The same assistant model family supplies these checks, and independent human error rates remain unmeasured.

## Cases flagged for your review

| ID | Condition | Flag | Review question |
|---|---|---|---|
| `train_5292` | height of man | Check recorded rationale | Should height retain the recorded stature scope, with the elevation claim corrected, or refer to elevation during the trick? |
| `train_180` | room decor style | Review scope or feature | Should room decor style compare the described furnishing character when only A names a design category? |
| `train_278` | type of food packaging | Review scope or feature | Does packed lunch supply enough coarse packaging information for comparison with containers, or must an enclosing vessel or material be identified? |
| `train_625` | type of food | Review scope or feature | Should named vegetables versus generic plate food receive a coarse type comparison, with the napkin branding excluded from food identification? |
| `train_630` | type of wine in glass | Review scope or feature | Does wine type require an identified variety in each caption, or may the shared wine category support a comparison with partial specificity? |
| `train_631` | types of wine | Review scope or feature | Should this plural type condition compare coarse wine categories and diversity, or require the identities of the individual varieties? |
| `train_1074` | type of food | Review scope or feature | For food type, should generic bowl food count as a recoverable broad category when B names eggs and fruit? |
| `train_1075` | amount of food | Review scope or feature | May a bowl of food and a plate of eggs and fruit support a coarse serving amount comparison, or is a measured quantity required? |
| `train_1132` | type of room | Review scope or feature | Should the furnished room category or ordinary seating context be treated as partial room type information for comparison with living room? |
| `train_1476` | name of place | Review scope or feature | Should room versus bedroom remain comparable under the policy for partial type specificity? |
| `train_1693` | person's age | Review scope or feature | Do the principal comparable referent conventions select the couch adults, or should this condition cover every described human? |
| `train_1809` | size of cow | Review scope or feature | Does size of cow include body build or bulk, or specifically overall stature and scale? |
| `train_2021` | type of signals | Review scope or feature | Does type of signals include road signs, or does it specifically require illuminated traffic signals? |
| `train_2022` | type of room | Review scope or feature | Should a broad room category or ordinary living space inference count as recoverable room type here? |
| `train_2038` | type of area involved | Review scope or feature | Should bedroom versus a room of unspecified function be treated as a meaningful type comparison under the frozen policy? |
| `train_2294` | type of flowers | Review scope or feature | Should flower type require a botanical variety, or can generic and seasonal flower descriptions support a comparison? |
| `train_2851` | type of chair | Review scope or feature | Does type of chair require a named chair subtype, or is the shared generic chair category a valid comparable type? |
| `train_3108` | type of food | Review scope or feature | Does generic food supply a coarse type value under the frozen general category versus subtype rule? |
| `train_3109` | number of dishes | Review scope or feature | Should dishes mean serving containers, including cups, or prepared food dishes in this comparison? |
| `train_3165` | type of animal | Review scope or feature | Should the string controlled stork be treated as a kite representation or as an animal type mention for this condition? |
| `train_3228` | color of animal | Review scope or feature | Should this generic animal color condition include the depicted color of a teddy bear, or require a living animal? |
| `train_3229` | animal species | Review scope or feature | Should animal species include the animal represented by a stuffed toy, or require an actual animal? |
| `train_3478` | location of ball | Review scope or feature | Should location of ball be restricted to height, or may player and racket relative locations supply comparable values? |
| `train_3625` | color of object | Review scope or feature | Should the comparable object be tennis clothing or the shared racket under the principal entity convention? |
| `train_4587` | food | Review scope or feature | Should food versus pizza be treated as a general category and subtype comparison under the entity-only type rule? |
| `train_4811` | position of racket | Review scope or feature | Does racket position include a coarse ready-to-hit posture, or require a stated physical height or orientation? |
| `train_6770` | action of girl | Review scope or feature | Should action include the stated activity of enjoying the weather, or require an observable bodily action? |
| `train_7833` | type of construction work | Review scope or feature | Should type of construction work include coarse wood or structural metal work, or require an identified task? |
| `train_7861` | type of animals | Review scope or feature | Is a coarse animal category recoverable from A's malformed description for the established type comparison? |
| `train_8373` | location | Review scope or feature | Should location include furniture-level placement when one caption gives outside and the other gives a highchair? |
| `train_8568` | location | Review scope or feature | Should generic location admit the stated airborne position alongside A's position near a cone? |
| `train_8829` | relationship of players | Review scope or feature | Should relationship compare the described functional player interactions, or specifically teammates versus opponents? |
| `train_9751` | color of object | Review scope or feature | Should the explanation use the recorded floor scope alone, or should a different principal object be specified? |
| `train_9946` | activity of person | Review scope or feature | Should activity include the recoverable state of being in the pool, or require an explicit bodily action? |
| `train_10037` | color of object | Review scope or feature | Should this case use the recorded bicycle scope and explain the absent bicycle colors? |
| `train_10380` | type of trick | Review scope or feature | Does the general bicycle trick category provide enough recoverable type information for this condition? |
| `train_10537` | type of instrument | Review scope or feature | Should the general musical instrument category count as partial type information for this comparison? |
| `train_11010` | clothing style | Review scope or feature | Should clothing style require an overall dress category, or can the stated garment choices supply partial style information? |
| `train_11341` | means of flotation | Review scope or feature | Can assistance from the man count as partial flotation means, or must the actual buoyancy mechanism be identified? |
| `train_332` | color of blanketed sky | Review ordinary inference | Should cloudy count as coarse sky color information under ordinary visual inference, or does this condition require a stated hue? |
| `train_624` | number of beverages | Review ordinary inference | May a sippy cup in a meal setting establish one beverage, or must drink contents be stated? |
| `train_1082` | name of activity | Review ordinary inference | Does the plated snack and cup supply a usable serving or eating activity at the same coarse level as apple preparation? |
| `train_2367` | player's action | Review ordinary inference | Does this tennis scene supply enough direct context for a coarse playing tennis action under the permitted inference rule? |
| `train_2385` | size of animal | Review ordinary inference | May characteristic species size supply a coarse animal size value here, or does the condition require individual stature? |
| `train_3708` | color of bathroom features | Review ordinary inference | Should clear or transparent glass appearance count as recoverable feature color here? |
| `train_4206` | color of object | Review ordinary inference | Should ordinary pizza and topping colors supply coarse appearance values, or must pizza hues be expressly described? |
| `train_4489` | presence of suitcase | Review ordinary inference | Should ordinary luggage collection context establish suitcase presence here, or must the suitcase form be stated? |
| `train_5787` | skill level of subject | Review ordinary inference | Can demonstrated wave riding supply coarse skill information here, or must skill level explicitly distinguish proficiency categories? |
| `train_5933` | type of surface | Review ordinary inference | Does an inferred tennis court supply sufficient coarse surface information alongside clay, or does this feature require a surface material? |
| `train_6553` | location of action | Review ordinary inference | May diving supply a coarse water setting for this location comparison, or must the waterbody be identified? |
| `train_7607` | speed of cyclists | Review ordinary inference | Does riding on the bumpy racetrack provide an ordinary coarse speed inference under the permitted context rule? |
| `train_8650` | speed of players | Review ordinary inference | Can crossing home plate in this scoring context support a coarse speed value comparable with walking? |
| `train_10241` | position of person | Review ordinary inference | Can ordinary riding posture count as position here, or is airborne versus grounded position the intended feature? |
| `train_11335` | woman stance | Review ordinary inference | Should ordinary riding posture or the shared mounted position supply stance information here? |

## All 258 excluded comparisons

Each entry preserves the recorded exclusion and rationale. The audit explanation identifies the requested feature and missing information. Policy-check flags and questions remain separate from the source decision. The review workbook provides editable Decision, Rating and Notes columns keyed by the same source IDs.

### 001. train_51: color of vehicle

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A number of locomotive train engines and cars on multiple set of train tracks.

**Caption B:** A blue and yellow train passing under a large tree with factories in the background.

**Adopted scope:** train colors

**Extracted A:** unspecified

**Extracted B:** blue and yellow

**Recorded reason, verbatim:**

> First caption supplies no vehicle color information. / Only the second supplies the vehicles colors.

**Audit explanation:** A describes locomotive engines and cars on several tracks and supplies their vehicle types and setting. B explicitly gives its train blue and yellow colors. The current exclusion follows from A having no recoverable train color, leaving the requested vehicle color comparison unavailable on that side.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 002. train_95: color of sheets

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A bed with white sheets and pillow, and a box of tissue on the headboard.

**Caption B:** A bedroom with a bed and a nightstand that has a red phone and a lamp on it.

**Adopted scope:** bed sheet color

**Extracted A:** white

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption supplies no sheet color information. / Second caption does not establish the bed sheet color.

**Audit explanation:** A explicitly describes white sheets and a pillow on its bed. B describes a bedroom, bed, nightstand, red phone and lamp, with sheet color left unspecified. The red belongs to the phone, so the current exclusion concerns the unavailable sheet color in B.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 003. train_102: action of people

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Action/activity. **Policy:** S1, S3, S6.

**Caption A:** A busy street with many business off to the side with a large clock.

**Caption B:** A group of people walking on a walkway filled with clocks mounted on poles.

**Adopted scope:** activity of described people

**Extracted A:** no people described

**Extracted B:** walking

**Recorded reason, verbatim:**

> Busy street does not establish a specific human activity. / First caption gives no actor or human activity to compare.

**Audit explanation:** B explicitly describes a group of people walking on a walkway, giving both human actors and their activity. A describes a busy street, businesses and a large clock. The current exclusion treats A as lacking a described human actor whose action could be compared with walking.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 004. train_103: people on street

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S2, S3.

**Caption A:** A busy street with many business off to the side with a large clock.

**Caption B:** A group of people walking on a walkway filled with clocks mounted on poles.

**Adopted scope:** type of people on street/walkway

**Extracted A:** no people described

**Extracted B:** group of people, subtype unspecified

**Recorded reason, verbatim:**

> First caption supplies no explicitly described people entity. / A busy street alone does not explicitly establish people.

**Audit explanation:** Under the entity-only convention, this condition concerns the type of people on the street or walkway. B supplies a group of people walking among clocks. A supplies a busy street, businesses and a clock, leaving any comparable human entity and its type unestablished.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 005. train_150: color of bus

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A large green and white double decker bus parked to another green and white double decker bus.

**Caption B:** A bus is driving out of a parking lot and getting on the main road.

**Adopted scope:** bus colors

**Extracted A:** green and white

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption supplies no bus color information. / Second caption does not establish the bus color.

**Audit explanation:** A explicitly gives both double decker buses green and white coloring. B describes a bus driving out of a parking lot onto the main road, supplying motion and location alone. Its bus color is wholly unspecified, which is the concrete missing value behind the current exclusion.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 006. train_180: room decor style

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S3, S4, S5.

**Caption A:** The bedroom is decorated in modern style with hardwood floor, and painted walls with one having a contrasting color.

**Caption B:** A living room with brown leather furniture and a fire place and a book shelf.

**Adopted scope:** room decoration style

**Extracted A:** modern with hardwood and contrasting painted wall

**Extracted B:** leather furniture, fireplace and bookshelves; style unspecified

**Recorded reason, verbatim:**

> Leather furnishings do not establish a comparable overall decor style.

**Audit explanation:** The current exclusion requires an overall decor style category. A explicitly calls its bedroom modern and adds hardwood and contrasting walls. B describes brown leather furniture, a fireplace and a bookshelf; the recorded decision treats those furnishings as insufficient to extract its overall style.

**Policy check:** Review scope or feature.

**Review issue:** B supplies concrete furnishing and decor properties. Those properties may support a coarser style comparison even with its named design category unspecified.

**Question for your review:** Should room decor style compare the described furnishing character when only A names a design category?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 007. train_278: type of food packaging

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S3, S4.

**Caption A:** A packed lunch consisting of two wraps, an orange with blueberries, raspberries, and carrots with broccoli 

**Caption B:** A couple of yellow containers filled with rice and vegetables next to a clear container filled with even more vegetables.

**Adopted scope:** packed-food packaging type

**Extracted A:** packed lunch, packaging unspecified

**Extracted B:** yellow and clear containers

**Recorded reason, verbatim:**

> The first caption does not identify a packaging type. / Packed lunch does not specify a particular packaging type.

**Audit explanation:** A describes a packed lunch made of wraps, fruit and vegetables, while B explicitly places rice and vegetables in yellow and clear containers. The exclusion treats A's packaging type as wholly unspecified because the wording identifies a packed meal without naming its enclosing material or vessel.

**Policy check:** Review scope or feature.

**Review issue:** Packed lunch establishes coarse packaging context. The policy permits recoverable general categories and partial type precision, so the required packaging specificity needs review.

**Question for your review:** Does packed lunch supply enough coarse packaging information for comparison with containers, or must an enclosing vessel or material be identified?

**History:** supplied source rating 4; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 008. train_287: next action of person

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Action/activity. **Policy:** S1, S3, S6.

**Caption A:** The batter has just hit the baseball, and is ready to run to first base.

**Caption B:** A man holding a baseball bat with two hands at a professional ball game.

**Adopted scope:** principal person next action

**Extracted A:** ready to run to first base

**Extracted B:** next action unstated while holding bat

**Recorded reason, verbatim:**

> Holding a bat at a game does not establish the next particular action.

**Audit explanation:** A states that the batter has hit the ball and is ready to run to first base, directly supplying his next action. B describes a man holding a bat with two hands at a ball game. The current exclusion reflects B leaving his next particular action unspecified.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 009. train_293: presence of animal

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S1, S3.

**Caption A:** A city with lots of tall buildings and a cat stopped at a traffic light.

**Caption B:** A busy downtown intersection with street signs, pedestrian crossing signal, and large commercial buildings.

**Adopted scope:** animal presence

**Extracted A:** present: cat

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Final blind invalid consensus: Animal present in A; B never establishes animal presence or absence. / A cat is present; animal presence is unspecified downtown. / A explicitly includes a cat; B supplies no animal presence information.

**Audit explanation:** A explicitly includes a cat stopped at a traffic light, establishing animal presence. B describes an intersection, street signs, a crossing signal and buildings, leaving animal presence and absence unreported. The current exclusion follows the policy that silence about animals supplies neither side of a presence comparison.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 010. train_326: color of capped wave

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** a man lays down on a surf board as he paddles through the water

**Caption B:** A man wearing a wet suit surfboarding on top of a white capped wave.

**Adopted scope:** wave-cap color

**Extracted A:** no capped wave described

**Extracted B:** white

**Recorded reason, verbatim:**

> The first caption does not establish any capped-wave color. / First caption mentions water but no colored wave cap.

**Audit explanation:** B explicitly describes a white capped wave beneath a surfboarding man, giving the requested cap color. A describes a man lying on a surfboard and paddling through water. The current exclusion reflects A leaving any capped wave, and therefore a comparable wave cap color, undescribed.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 011. train_332: color of blanketed sky

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S3, S5, S6.

**Caption A:** A surfer surfs in the ocean as many kites fly in the cloudy sky.

**Caption B:** A lone kite is flying above the water and under a blue blanketed sky.

**Adopted scope:** sky color

**Extracted A:** cloudy, color unspecified

**Extracted B:** blue

**Recorded reason, verbatim:**

> Cloud cover does not reliably establish sky color. / Cloud cover alone does not uniquely establish the skys color.

**Audit explanation:** A describes a cloudy sky above a surfer and flying kites, while B explicitly describes a blue sky above a lone kite. The current exclusion treats cloud cover in A as insufficient to extract a sky hue, since cloudy describes atmospheric cover without specifying its color.

**Policy check:** Review ordinary inference.

**Review issue:** Cloudy provides ordinary visual context that may support a coarse gray or white sky appearance. The permitted inference threshold should govern whether that contextual value is usable.

**Question for your review:** Should cloudy count as coarse sky color information under ordinary visual inference, or does this condition require a stated hue?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 012. train_588: brightness

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A close up of a traffic light indicates a green light and a protected left turn.

**Caption B:** There is a sign in a foreign language and a street light in this picture.

**Adopted scope:** principal light illumination/brightness

**Extracted A:** green signal illuminated; intensity unspecified

**Extracted B:** street light, illumination unspecified

**Recorded reason, verbatim:**

> Neither caption establishes a comparable level of brightness. / Light presence alone does not establish comparable brightness.

**Audit explanation:** A describes a traffic light showing green and a protected left turn, establishing a signal state. B mentions a foreign language sign and a street light. The recorded brightness scope concerns light intensity, and neither caption gives a comparable brightness level; B also leaves illumination state unspecified.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 013. train_624: number of beverages

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S3, S5.

**Caption A:** There are various food items including pickles, tomatoes, carrots, broccoli; as well as a sippy cup, spoon, fork, and whale napkin.

**Caption B:** A glass of juice sits between two plates of food near pizza hut napkins on a dark yellow tablecloth.

**Adopted scope:** number of beverages

**Extracted A:** sippy cup, no drink specified

**Extracted B:** 1 glass of juice

**Recorded reason, verbatim:**

> A sippy cup does not establish a beverage or beverage count. / A cup alone does not establish a beverage count.

**Audit explanation:** B explicitly supplies one glass of juice, establishing a beverage to count. A lists food, utensils, a napkin and a sippy cup, with the cup contents unstated. The current exclusion treats the drinking vessel as insufficient evidence for the presence and quantity of beverages in A.

**Policy check:** Review ordinary inference.

**Review issue:** A sippy cup among meal items provides ordinary drinking context. Inferring one beverage may fall within permitted standard scene implications, subject to the chosen vessel versus contents convention.

**Question for your review:** May a sippy cup in a meal setting establish one beverage, or must drink contents be stated?

**History:** supplied source rating 5; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 014. train_625: type of food

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S2, S3, S4, S6.

**Caption A:** There are various food items including pickles, tomatoes, carrots, broccoli; as well as a sippy cup, spoon, fork, and whale napkin.

**Caption B:** A glass of juice sits between two plates of food near pizza hut napkins on a dark yellow tablecloth.

**Adopted scope:** food types

**Extracted A:** pickles, tomatoes, carrots and broccoli

**Extracted B:** food on two plates, types unspecified

**Recorded reason, verbatim:**

> Second has unidentified food; branded napkins do not establish food types.

**Audit explanation:** A identifies pickles, tomatoes, carrots and broccoli, giving specific food types. B identifies food on two plates and a glass of juice beside Pizza Hut napkins. The current exclusion treats the plate contents as type-unspecified and declines to infer pizza from the napkin branding.

**Policy check:** Review scope or feature.

**Review issue:** B establishes the general food category. The distinction between recoverable generic type information and wholly absent subtype information needs application under the graded type convention.

**Question for your review:** Should named vegetables versus generic plate food receive a coarse type comparison, with the napkin branding excluded from food identification?

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 015. train_630: type of wine in glass

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S2, S3, S4.

**Caption A:** Red wine pours in a glass; another glass is beside it and cheese straws in the back.

**Caption B:** Three different types of wine in three wine glasses on a white piece of paper on a bar.

**Adopted scope:** wine type

**Extracted A:** red wine

**Extracted B:** three distinct wine types, identities unspecified

**Recorded reason, verbatim:**

> Second establishes three wines without identifying any wine type.

**Audit explanation:** A explicitly identifies red wine pouring into a glass. B describes three different types of wine in three glasses, supplying diversity and count while leaving their identities unspecified. The current exclusion requires identifiable wine varieties on both sides and treats B as lacking a recoverable variety value.

**Policy check:** Review scope or feature.

**Review issue:** Both captions establish wine, and B additionally establishes multiple varieties. A coarse wine category comparison may remain available under the policy for general versus specific types.

**Question for your review:** Does wine type require an identified variety in each caption, or may the shared wine category support a comparison with partial specificity?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 016. train_631: types of wine

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S2, S3, S4.

**Caption A:** Red wine pours in a glass; another glass is beside it and cheese straws in the back.

**Caption B:** Three different types of wine in three wine glasses on a white piece of paper on a bar.

**Adopted scope:** wine type collection

**Extracted A:** red wine

**Extracted B:** three distinct unnamed wine types

**Recorded reason, verbatim:**

> Second establishes diversity without providing comparable wine-type identities.

**Audit explanation:** A supplies red wine as the identified member of its wine type collection. B supplies three distinct wines in separate glasses without naming any variety. The current exclusion treats knowledge of diversity alone as insufficient to extract B's wine type identities for the requested collection comparison.

**Policy check:** Review scope or feature.

**Review issue:** B provides a general wine category and a diverse collection. Review whether those are partial type values under the graded rubric or wholly missing identities at the required scope.

**Question for your review:** Should this plural type condition compare coarse wine categories and diversity, or require the identities of the individual varieties?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 017. train_694: layout of bedroom

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Spatial relation/posture. **Policy:** S1, S3.

**Caption A:** A bedroom with an open suitcase on the floor and a laptop on a chair

**Caption B:** A carpeted bedroom has different wood toned furniture, a small lamp, and a yellow striped pillow.

**Adopted scope:** bedroom layout

**Extracted A:** suitcase on floor, laptop on chair

**Extracted B:** furniture and accessories, positions unspecified

**Recorded reason, verbatim:**

> Second identifies furnishings but supplies no comparable spatial layout.

**Audit explanation:** A locates an open suitcase on the bedroom floor and a laptop on a chair, giving explicit placement relations. B lists carpet, wood toned furniture, a lamp and a striped pillow. The current exclusion reflects B leaving the spatial arrangement of those bedroom elements unspecified.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 018. train_731: number of people

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** A person is crossing a brick road in an area with residential buildings and lots of trees.

**Caption B:** A traffic light sitting next to a tree on the side of a street.

**Adopted scope:** number of people

**Extracted A:** 1

**Extracted B:** no people described

**Recorded reason, verbatim:**

> Second caption supplies no people count or established absence. / Second caption establishes no people count or explicit absence.

**Audit explanation:** A explicitly describes one person crossing a brick road, supplying a human count. B describes a traffic light beside a tree on the side of a street. The current exclusion reflects B providing neither people to count nor an established absence from which a zero count could follow.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 019. train_737: age of player

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Age. **Policy:** S1, S3.

**Caption A:** A baseball player wearing green and white standing next to a baseball player wearing red and gray on a baseball field.

**Caption B:** A young baseball player gets ready to swing for the ball while two men watch.

**Adopted scope:** principal players age category

**Extracted A:** unspecified

**Extracted B:** young player

**Recorded reason, verbatim:**

> The first caption does not establish the players' age range. / First caption does not establish player ages.

**Audit explanation:** B explicitly calls its principal baseball player young, supplying an age category; the two watching men occupy a different role. A describes two baseball players through uniform colors and their position on a field. The current exclusion reflects A leaving the players' ages unspecified.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 020. train_805: sidewalk

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S2, S3.

**Caption A:** A rainy view of some people crossing a street with a red traffic light.

**Caption B:** A brick laid sidewalk that is wet from rain, with a woman walking on the sidewalk and holding an umbrella.

**Adopted scope:** sidewalk type

**Extracted A:** no sidewalk described

**Extracted B:** brick sidewalk

**Recorded reason, verbatim:**

> Crossing a street does not establish a sidewalk to compare. / Crossing a street does not establish a sidewalk to compare.

**Audit explanation:** The entity-only condition defaults to sidewalk type. B explicitly describes a brick laid sidewalk wet from rain and a woman walking on it. A describes people crossing a rainy street beneath a red traffic light, leaving a sidewalk and its construction type undescribed.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 021. train_822: activity

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Action/activity. **Policy:** S1, S3.

**Caption A:** Person in jeans and painted toe nails in a hotel room, sitting on the bed. 

**Caption B:** A bed in a room with some lights on the side of the bed

**Adopted scope:** person activity

**Extracted A:** sitting on bed

**Extracted B:** no person described

**Recorded reason, verbatim:**

> Second caption describes furniture without a person's activity. / The second description lacks an actor with an activity.

**Audit explanation:** A describes a person sitting on a hotel room bed, directly supplying the human activity. B describes a bed and lights beside it, with no human actor described. The current exclusion reflects the absence of a comparable person whose activity could be extracted from B.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 022. train_881: color of clothing

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A puppy all dressed up with a nice red tie with hearts on it.

**Caption B:** A brown tabby cat wearing shirt collar and a neck tie wearing a cute expression.

**Adopted scope:** animals clothing color

**Extracted A:** red tie

**Extracted B:** collar and tie, colors unspecified

**Recorded reason, verbatim:**

> Second caption gives no color for the clothing. / Only the first supplies the color of clothing.

**Audit explanation:** A explicitly gives the puppy a red tie with hearts, supplying clothing color. B gives the tabby cat a shirt collar and necktie while describing the cat itself as brown. The current exclusion reflects B leaving its clothing colors unspecified; the coat color concerns a different feature.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 023. train_922: number of people

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3, S4.

**Caption A:** A bunch of train box cars on a track and people are walking on the sidewalk.

**Caption B:** A truck and luggage sitting on a cart by the dining saloon car of a train.

**Adopted scope:** number of people

**Extracted A:** plural walking people, total unspecified

**Extracted B:** no people described

**Recorded reason, verbatim:**

> Second caption does not establish a people count. / Second description gives no person count or established absence.

**Audit explanation:** A describes people walking on a sidewalk beside train box cars, establishing a plural human count even with its exact total unspecified. B describes a truck, luggage, a cart and a train dining car. The current exclusion reflects B providing neither a human count nor established human absence.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 024. train_979: colors

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A plate with an iced and decorated cake next to a bowl of oranges.

**Caption B:** Large multi-layered white frosted cake being cut with green plastic knife on striped table cloth.

**Adopted scope:** principal cake color

**Extracted A:** unspecified

**Extracted B:** white frosting

**Recorded reason, verbatim:**

> No first cake color is specified or reliably inferable.

**Audit explanation:** The adopted generic color scope concerns the principal cakes. B explicitly describes white frosting on its multilayered cake. A describes an iced and decorated cake beside oranges, with cake and icing hues unspecified. The current exclusion reflects that missing cake color; the oranges concern an incidental object.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 025. train_1068: sentiment of man

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Emotion/sentiment. **Policy:** S1, S3, S6.

**Caption A:** A man sits on a couch smiling next to a dog as a boy plays a video game.

**Caption B:** A man in a gray tank top lays on a couch with a cute black and white dog.

**Adopted scope:** man's sentiment

**Extracted A:** happy/smiling

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Second man's posture does not establish sentiment. / The second mans emotional state cannot be extracted reliably.

**Audit explanation:** A describes the man smiling on a couch beside a dog, supporting positive sentiment. B describes a man lying on a couch with a dog and calls the dog cute. The current exclusion reflects B providing posture and the dog's appearance while leaving the man's emotional state unspecified.

**Policy check:** Policy consistent.

**History:** supplied source rating 4; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 026. train_1074: type of food

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S2, S3, S4.

**Caption A:** The bowl of food on the table is next to a couple of forks and glasses.

**Caption B:** A close up shot of a plate with eggs and fruit on a table.

**Adopted scope:** food type

**Extracted A:** unspecified food

**Extracted B:** eggs and fruit

**Recorded reason, verbatim:**

> First caption names food without identifying its type.

**Audit explanation:** B identifies eggs and fruit on a plate, providing specific food types. A describes a bowl of food beside forks and glasses, identifying a general edible category and its vessel. The current exclusion treats A as lacking the food subtype information needed to compare its contents with eggs and fruit.

**Policy check:** Review scope or feature.

**Review issue:** A provides the general food category, creating a possible generic versus specific type comparison. The policy distinguishes partial type precision from wholly absent feature information.

**Question for your review:** For food type, should generic bowl food count as a recoverable broad category when B names eggs and fruit?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 027. train_1075: amount of food

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3, S4, S5.

**Caption A:** The bowl of food on the table is next to a couple of forks and glasses.

**Caption B:** A close up shot of a plate with eggs and fruit on a table.

**Adopted scope:** amount of food

**Extracted A:** food in bowl; quantity unspecified

**Extracted B:** eggs and fruit on plate; quantity unspecified

**Recorded reason, verbatim:**

> The vessels do not establish food quantity or serving size in either caption.

**Audit explanation:** A gives a bowl of food on a table, and B gives a plate with eggs and fruit. The current exclusion treats the vessels and identified foods as insufficient to determine food quantity or serving size in either caption, leaving the requested amount unavailable at that precision.

**Policy check:** Review scope or feature.

**Review issue:** Both captions describe one filled food vessel, which may establish coarse serving amounts. Exclusion may depend on requiring finer quantity precision than the condition states.

**Question for your review:** May a bowl of food and a plate of eggs and fruit support a coarse serving amount comparison, or is a measured quantity required?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 028. train_1082: name of activity

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Action/activity. **Policy:** S1, S3, S5.

**Caption A:** a piece of cheese and carrot sitting on a tiny little saucer with a cup next to it

**Caption B:** The core of an apple and peels with a knife on a cutting board

**Adopted scope:** human food-related activity

**Extracted A:** no activity described

**Extracted B:** apple cut/peeled, actor not described

**Recorded reason, verbatim:**

> First static food arrangement does not establish any named activity.

**Audit explanation:** A describes cheese and carrot on a tiny saucer beside a cup, presenting a static food arrangement. B describes an apple core and peels with a knife on a cutting board, supporting food preparation. The current exclusion treats A as lacking a recoverable named food related activity.

**Policy check:** Review ordinary inference.

**Review issue:** The saucer, small food pieces and cup may support a coarse snack serving activity through ordinary scene context. The policy permits standard activity implications without requiring an explicit actor.

**Question for your review:** Does the plated snack and cup supply a usable serving or eating activity at the same coarse level as apple preparation?

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 029. train_1089: advertisement on vehicle

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Composition/contents. **Policy:** S1, S3.

**Caption A:** A street with two cars and a bus in between the cars with a Coca Cola advertisement on the side of the bus.

**Caption B:** A white metro bus with pink and purple trim drives down a city street in front of a glass building.

**Adopted scope:** vehicle advertisement content

**Extracted A:** Coca-Cola advertisement

**Extracted B:** no advertisement described

**Recorded reason, verbatim:**

> Colored bus trim does not establish advertising content. / Second caption supplies no advertising text or established absence.

**Audit explanation:** A explicitly places a Coca Cola advertisement on the side of its bus. B gives a white metro bus with pink and purple trim traveling through a city street. The current exclusion reflects B leaving advertisement presence and content unspecified; decorative trim alone supplies no advertising identity.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 030. train_1130: color of paper

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A room with a bed and a large sliding glass door to an outdoor deck.

**Caption B:** A bed with white sheets and pillow, and a box of tissue on the headboard.

**Adopted scope:** paper color

**Extracted A:** no paper described

**Extracted B:** tissues, color not explicit

**Recorded reason, verbatim:**

> Neither caption establishes a comparable paper color. / Neither caption provides a comparable paper color value.

**Audit explanation:** A describes a room, bed, sliding glass door and outdoor deck, with no paper entity supplied. B mentions a box of tissues on a bed headboard, leaving tissue color unspecified. The current exclusion therefore includes an absent comparable paper referent in A and an unavailable paper color in B.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 031. train_1132: type of room

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Location/scene. **Policy:** S2, S3, S4, S5.

**Caption A:** Rough wood-frame furniture with striped cushions, in a bright room with a white tile floor.

**Caption B:** A living room with a couch next to a chair in front of a TV.

**Adopted scope:** room type

**Extracted A:** furnished room, subtype unspecified

**Extracted B:** living room

**Recorded reason, verbatim:**

> Final blind invalid consensus: Cushioned wooden furniture does not establish A’s room type sufficiently. / Generic cushioned furniture does not establish the first room type. / Cushioned furniture and tile do not establish A's particular room type.

**Audit explanation:** B explicitly identifies a living room with a couch, chair and television. A describes a bright room with cushioned wood frame furniture and a white tile floor. The current exclusion treats A's furnishing description as insufficient to identify the functional room subtype requested by the condition.

**Policy check:** Review scope or feature.

**Review issue:** A supplies a general room category and seating context. The graded type rule and ordinary room function inference may permit a coarser comparison with B's explicit living room.

**Question for your review:** Should the furnished room category or ordinary seating context be treated as partial room type information for comparison with living room?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 032. train_1133: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** Rough wood-frame furniture with striped cushions, in a bright room with a white tile floor.

**Caption B:** A living room with a couch next to a chair in front of a TV.

**Adopted scope:** principal furniture color

**Extracted A:** unspecified; striped cushions without hues

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption supplies no comparable object color. / Second caption gives no object colors to compare.

**Audit explanation:** The adopted generic object scope concerns the principal furniture. A describes wood frame furniture with striped cushions, naming a pattern without its hues; its white tile floor concerns a separate surface. B describes a couch, chair and television with colors unspecified, leaving comparable furniture color unavailable in both captions.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 033. train_1183: number of seats

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3, S4.

**Caption A:** A room with a bed, matching curtains, and some chairs with clothes in them.

**Caption B:** A bedroom with a bed and a nightstand that has a red phone and a lamp on it.

**Adopted scope:** number of chair seats

**Extracted A:** multiple chairs, exact count unspecified

**Extracted B:** no seats described

**Recorded reason, verbatim:**

> Second caption mentions no seats or established absence. / Second description does not establish any chair count or absence.

**Audit explanation:** Under the recorded chair seat scope, A describes some chairs containing clothes and thus establishes multiple seats with an uncertain exact total. B describes a bed, nightstand, phone and lamp. The current exclusion reflects B supplying neither chair seats to count nor an established absence of them.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 034. train_1193: number of people

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3, S4.

**Caption A:** A train track with a green caboose car and a silver and yellow train.

**Caption B:** A train departs one one side of the tracks as people wait on the opposite side.

**Adopted scope:** number of people

**Extracted A:** no people described

**Extracted B:** waiting people, plural count unspecified

**Recorded reason, verbatim:**

> The first caption provides no extractable number of people. / First caption provides no people to count.

**Audit explanation:** B describes people waiting on the opposite side of departing train tracks, supplying a plural human count despite unspecified precision. A describes a green caboose and a silver and yellow train on tracks. The current exclusion reflects A leaving people and their count unreported, including any established absence.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 035. train_1223: color of clothing

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A woman sitting in the snow with her snowboard on and a man standing next to a snowboard.

**Caption B:** A snowboarder wearing a yellow coat and brown pants rides down a snow covered hill.

**Adopted scope:** people's clothing colors

**Extracted A:** unspecified

**Extracted B:** yellow coat and brown pants

**Recorded reason, verbatim:**

> The first caption supplies no clothing color information. / First caption provides no clothing colors to compare.

**Audit explanation:** B explicitly gives the snowboarder a yellow coat and brown pants, establishing clothing colors. A describes a woman sitting in snow with her snowboard and a man standing beside a snowboard. The current exclusion reflects A leaving the clothing colors of both described people unspecified.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 036. train_1228: color

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A white dish with half eaten food above a plate with puffs and steak.

**Caption B:** Glasses of wine sit in the middle of a table behind a plate of dessert.

**Adopted scope:** principal dish/food color

**Extracted A:** white dish; food colors unstated

**Extracted B:** dish and food colors unstated

**Recorded reason, verbatim:**

> Second caption provides no comparable object color. / Second caption supplies no comparable dish or food color.

**Audit explanation:** A explicitly calls its dish white and mentions food, puffs and steak. B describes wine glasses behind a plate of dessert, with the plate and food colors unspecified. Under the adopted dish and food color scope, the current exclusion reflects B lacking any comparable stated color value.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 037. train_1251: color of ornamental clock

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** An ornate clock beneath an arch flanked by statues and a locomotive bas relief.

**Caption B:** A blue ornamental clock adorned with an eagle is hung on a white columned building.

**Adopted scope:** clock color

**Extracted A:** unspecified

**Extracted B:** blue

**Recorded reason, verbatim:**

> First caption provides no clock color information. / Only the second supplies the ornamental clocks color.

**Audit explanation:** B explicitly identifies its ornamental clock as blue, separate from the white columned building. A describes an ornate clock beneath an arch, flanked by statues and a locomotive relief. The current exclusion reflects A supplying ornamentation and location while leaving the clock's color wholly unspecified.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 038. train_1256: number of dish

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** A table setting with a candle and a glass with limes on the side.

**Caption B:** A tall case of flowers on an elaborate dining area sit alongside two wine glasses and a dish.


**Adopted scope:** number of serving dishes, excluding drinking glasses

**Extracted A:** no dish described

**Extracted B:** 1 dish

**Recorded reason, verbatim:**

> The first caption does not establish a dish count. / First caption names no dish whose count can be extracted.

**Audit explanation:** The recorded scope counts serving dishes and excludes drinking glasses. B explicitly describes one dish beside two wine glasses and flowers. A describes a candle and a glass with limes at a table setting. The current exclusion reflects A leaving serving dish count and established absence unspecified.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 039. train_1257: presence of dish

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S1, S3.

**Caption A:** A table setting with a candle and a glass with limes on the side.

**Caption B:** A tall case of flowers on an elaborate dining area sit alongside two wine glasses and a dish.


**Adopted scope:** serving dish presence

**Extracted A:** unspecified

**Extracted B:** present

**Recorded reason, verbatim:**

> Final blind invalid consensus: A mentions a glass but never establishes presence or absence of dishes. / A dish is explicit only in the second caption.

**Audit explanation:** B explicitly includes a dish beside wine glasses and flowers, establishing serving dish presence. A mentions a candle and a glass with limes in a table setting, leaving serving dishes unreported. The current exclusion follows from A supplying neither serving dish presence nor a supported negative presence value.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 040. train_1295: color of cat

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A cat and a bird are by a plate with chips and a sandwich on it.

**Caption B:** A black cat sitting on a table next to a bowl of chicken soup.

**Adopted scope:** cat coat color

**Extracted A:** unspecified

**Extracted B:** black

**Recorded reason, verbatim:**

> The first caption supplies no cat color information. / First caption does not establish the cat color.

**Audit explanation:** B explicitly describes its cat as black while placing it beside chicken soup. A describes a cat and bird near chips and a sandwich, with the cat's coat color unspecified. The current exclusion concerns that missing cat color in A; the other animals and food supply no replacement value.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 041. train_1339: number of phones

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** A bedroom with a bed and a nightstand that has a red phone and a lamp on it.

**Caption B:** A neatly-made bed with a gold and white bedspread flanked by lamps and a large wood headboard.

**Adopted scope:** number of phones

**Extracted A:** 1

**Extracted B:** no phone described

**Recorded reason, verbatim:**

> The second caption does not establish any phone count. / Second caption provides no phones whose count is extractable.

**Audit explanation:** A explicitly places one red phone on a bedroom nightstand, supplying the requested phone count. B describes a made bed, bedspread, lamps and headboard. The current exclusion reflects B leaving phones unreported, which supplies neither a recoverable phone count nor a supported zero count.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 042. train_1355: presence of animal

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S1, S3.

**Caption A:** A bedroom contains a dresser and mirror, a side table and lamp and a twin bed with matching bed covers and pillows.

**Caption B:** A bed sitting on top of white drawers and topped with a stuffed animal next to a cat.

**Adopted scope:** animal presence

**Extracted A:** unspecified

**Extracted B:** present: cat

**Recorded reason, verbatim:**

> Final blind invalid consensus: A never establishes animal presence or absence; B explicitly includes a cat. / Cat presence is explicit; the bedroom description leaves animals unspecified. / B explicitly includes a cat; A leaves animal presence unreported.

**Audit explanation:** B explicitly describes a cat beside a bed and separately mentions a stuffed animal, establishing live animal presence through the cat. A lists bedroom furniture, bed covers and pillows. The current exclusion reflects A leaving animal presence and absence unreported; its furniture inventory supplies neither value.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 043. train_1392: color of clothing

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A person wearing a shirt of pink, blue and white, wearing a brown tie with a picture ladybug on it.

**Caption B:** Up close shot of a mans shirt, necktie, and two pens in his pocket

**Adopted scope:** shirt and tie colors

**Extracted A:** pink, blue and white shirt; brown tie

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption supplies no clothing color information. / Second caption supplies no comparable clothing colors.

**Audit explanation:** A explicitly describes a pink, blue and white shirt and a brown tie with a ladybug picture. B names a man's shirt, necktie and pocket pens, supplying the clothing referents without their hues. The current exclusion follows from B having no recoverable shirt or tie color.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 044. train_1393: color of clothing

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A person wearing a shirt of pink, blue and white, wearing a brown tie with a picture ladybug on it.

**Caption B:** Up close shot of a mans shirt, necktie, and two pens in his pocket

**Adopted scope:** shirt and tie colors

**Extracted A:** pink, blue and white shirt; brown tie

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption supplies no clothing color information. / Second caption supplies no comparable clothing colors.

**Audit explanation:** Caption A identifies a pink, blue and white shirt and a brown tie. Caption B describes a man's shirt and necktie, together with pens in his pocket, while leaving their colors unspecified. Clothing colors are therefore unavailable in B for the recorded shirt and tie comparison.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 045. train_1405: number of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** The overhead view of a tiled bathroom  with a tub, shower, toilet, bidet, and sink.

**Caption B:** This is a well designed bathroom that is plain and elegant at the same time.

**Adopted scope:** number of bathroom objects

**Extracted A:** 5 named fixtures

**Extracted B:** no objects identified

**Recorded reason, verbatim:**

> Five fixtures are listed first; the second provides no object count. / Second caption provides no countable bathroom objects.

**Audit explanation:** Caption A lists a tub, shower, toilet, bidet and sink, supplying five named bathroom fixtures. Caption B describes a plain, elegant bathroom through its overall design and names no individual fixtures. The requested bathroom object count remains unavailable in B; the room label supplies no recoverable fixture total.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 046. train_1421: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A sketched drawing of a boy in a blue shirt on his skateboard at a city park.

**Caption B:** a person riding a skate board in front of a wall covered in grafitti

**Adopted scope:** principal skateboard color

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption supplies no comparable object color. / Second caption gives no comparable object color.

**Audit explanation:** The recorded scope selects skateboard color. Caption A supplies a blue shirt worn by a boy on a skateboard, and caption B describes a person riding a skateboard beside graffiti. Each skateboard's color remains unspecified. The shirt color in A belongs to a separate entity and supplies no skateboard color value.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 047. train_1428: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** View from doorway and of door to small room with tiled floor and a toilet.

**Caption B:** This appears to be a small bathroom, with a blue rug and toilet cover.

**Adopted scope:** principal bathroom fixture colors

**Extracted A:** unspecified

**Extracted B:** toilet-cover and rug blue; toilet color unspecified

**Recorded reason, verbatim:**

> First caption supplies no comparable object color. / First caption supplies no object color for comparison.

**Audit explanation:** Caption A describes a toilet and tiled floor in a small room while leaving every mentioned object's color unspecified. Caption B gives blue for a rug and toilet cover. The exclusion therefore rests on A's missing color information, regardless of whether B's toilet cover is included within the principal bathroom fixture scope.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 048. train_1447: number of people

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** The elephant with a sit on his back ready for  people to ride on it.

**Caption B:** A man leading an elephant across a dirt yard with another elephant in the background.

**Adopted scope:** number of people actually described in scene

**Extracted A:** prospective riders only; no present people established

**Extracted B:** 1 man

**Recorded reason, verbatim:**

> Readiness for people does not establish present people or their count. / Readiness for riders does not establish an actual people count.

**Audit explanation:** Caption A describes an elephant equipped and ready for people to ride. Those people are prospective riders, with their actual presence and count left unspecified. Caption B explicitly includes one man leading an elephant. The requested count concerns people actually described in the scene, leaving A without a recoverable count.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 049. train_1469: number of people

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3, S4.

**Caption A:** A narrow street in a city with automobiles parked on the side and a blue "Police" sign in the middle.

**Caption B:** The city is busy with traffic today as people wait to board the bus.

**Adopted scope:** number of people

**Extracted A:** no people described

**Extracted B:** waiting people, plural total unspecified

**Recorded reason, verbatim:**

> First caption provides no people count or established absence. / First caption establishes no people count or explicit absence.

**Audit explanation:** Caption A describes parked automobiles, a city street and a Police sign, with human presence left unspecified. Caption B describes people waiting to board a bus, establishing a plural group even though its exact size is missing. The exclusion rests on A's unavailable people count; B already provides partial quantity information.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 050. train_1476: name of place

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S3, S4, S6.

**Caption A:** A bedroom with an open suitcase on the floor and a laptop on a chair

**Caption B:** A room is very messy as it may be inhabited by a college student

**Adopted scope:** place/room type

**Extracted A:** bedroom

**Extracted B:** messy room, residential subtype uncertain

**Recorded reason, verbatim:**

> College inhabitant speculation does not establish bedroom function. / Second caption does not establish a specific room function.

**Audit explanation:** The current exclusion treats the requested place name as a specific room function. Caption A explicitly identifies a bedroom. Caption B supplies a messy room and a speculative college student inhabitant, leaving that function uncertain. Its explicit room category provides a broader place type that warrants policy review.

**Policy check:** Review scope or feature.

**Review issue:** B explicitly identifies a room. Exclusion for missing bedroom specificity may conflict with the rule allowing broad type versus specific subtype comparisons.

**Question for your review:** Should room versus bedroom remain comparable under the policy for partial type specificity?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 051. train_1477: name of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S2, S3.

**Caption A:** A bedroom with an open suitcase on the floor and a laptop on a chair

**Caption B:** A room is very messy as it may be inhabited by a college student

**Adopted scope:** named object types

**Extracted A:** suitcase, laptop and chair

**Extracted B:** messy room, no object types named

**Recorded reason, verbatim:**

> Second caption identifies no comparable individual object types. / Second caption gives no objects whose types can be compared.

**Audit explanation:** Caption A names a suitcase, laptop and chair inside a bedroom. Caption B describes a messy room and a possible college student occupant, leaving individual objects unnamed. Under the recorded scope of named object types, B supplies no comparable object identity; general messiness alone establishes no particular suitcase, laptop or chair.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 052. train_1493: animal near person

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S2, S3.

**Caption A:** A person standing in the ocean holding a surfboard while a dog stands on it.

**Caption B:** A man with a surf board is standing on the beach with other people.

**Adopted scope:** animal near person type

**Extracted A:** dog

**Extracted B:** no animal described

**Recorded reason, verbatim:**

> The second caption establishes no animal near the person. / Second caption supplies no nearby animal to compare.

**Audit explanation:** The entity phrase animal near person is treated as a request for animal type. Caption A describes a dog standing on the surfboard held by a person. Caption B describes a man with a surfboard and other people on a beach, supplying no animal entity for the requested type comparison.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 053. train_1504: number of people

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3, S4.

**Caption A:** A train pumps out steam while going down a track on a cloudy day.

**Caption B:** The train is on the railroad and the passengers are waiting for it to stop.

**Adopted scope:** number of people

**Extracted A:** no people described

**Extracted B:** passengers, plural number unspecified

**Recorded reason, verbatim:**

> First caption supplies no people count or established absence. / First caption establishes no people count or explicit absence.

**Audit explanation:** Caption A describes a steaming train traveling on a cloudy day and leaves people unspecified. Caption B explicitly mentions passengers waiting for the train to stop, providing a plural human group with an uncertain total. The missing count information is in A; its silence about people supplies no established zero.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 054. train_1550: beverage temperature

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Other. **Policy:** S3, S6.

**Caption A:** a plate covered with bananas with a coffee cup filled with some type of beverage

**Caption B:** A plate with a couple of scones and a kettle that may be tea.

**Adopted scope:** beverage temperature

**Extracted A:** unspecified drink in coffee cup; temperature unknown

**Extracted B:** possible tea in kettle; temperature unknown

**Recorded reason, verbatim:**

> Containers and possible tea do not establish beverage temperature. / Neither vessel establishes the beverage's actual temperature.

**Audit explanation:** Caption A places an unspecified beverage in a coffee cup beside bananas. Caption B describes a kettle with a tentative tea reference beside scones. Neither caption supplies temperature, steam, heating or another direct thermal cue. Inferring actual drink temperature from the vessels or possible tea would exceed the recorded evidence threshold.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 055. train_1599: presence of grass

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S1, S3.

**Caption A:** a train is on it's tracks next to a dirt road and grassy patch

**Caption B:** a train making it's way down a track with smoke coming out of the stack

**Adopted scope:** grass presence

**Extracted A:** present: grassy patch

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Final blind invalid consensus: Grass is explicit in A and neither confirmed nor denied in B. / Grass is explicit beside the first train, unspecified beside second. / A explicitly includes grass; B supplies no grass presence information.

**Audit explanation:** Caption A explicitly includes a grassy patch beside the train and dirt road, establishing grass presence. Caption B describes a train moving along a track with smoke from its stack, leaving the surrounding ground cover unspecified. The requested presence comparison lacks a grass value in B; omission establishes neither presence nor absence.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 056. train_1680: color of bowl

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A white bowl sitting on top of a table next to carrots and cabbage.

**Caption B:** A plate of food with lemon wedges on the plate and on the table.

**Adopted scope:** bowl color

**Extracted A:** white

**Extracted B:** no bowl described; plate instead

**Recorded reason, verbatim:**

> Second caption describes plate, not required bowl entity. / Second caption lacks the required bowl and its color.

**Audit explanation:** Caption A explicitly describes a white bowl on a table beside carrots and cabbage. Caption B identifies a plate of food with lemon wedges and supplies no bowl. The condition specifically requires bowl color, so B lacks the required entity as well as its color; the named plate supplies a different vessel.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 057. train_1681: name of vegetables

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S2, S3.

**Caption A:** A white bowl sitting on top of a table next to carrots and cabbage.

**Caption B:** A plate of food with lemon wedges on the plate and on the table.

**Adopted scope:** vegetable names

**Extracted A:** carrots and cabbage

**Extracted B:** no vegetables identified; lemon wedges are fruit

**Recorded reason, verbatim:**

> Second caption supplies no named vegetable type. / Second caption names fruit but supplies no vegetable type.

**Audit explanation:** Caption A names carrots and cabbage beside a white bowl, giving recoverable vegetable types. Caption B describes unspecified food and lemon wedges on a plate and table. Lemon is a fruit, and the general food reference establishes no vegetable identity. B therefore lacks a described vegetable for the requested name comparison.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 058. train_1693: person's age

**Current status:** excluded_ambiguous. **Current rating:** excluded/null. **Family:** Age. **Policy:** S1, S7.

**Caption A:** Dogs and child on the floor in front of an adult seated on a couch.

**Caption B:** A man in a gray tank top lays on a couch with a cute black and white dog.

**Adopted scope:** age of first caption person: foreground child or couch adult

**Extracted A:** child and adult

**Extracted B:** adult man

**Recorded reason, verbatim:**

> The first scene has both a foreground child and a couch adult; either can be compared with the second man, yielding different age ratings.

**Audit explanation:** The exclusion records two possible age referents in A: the child on the floor and the adult seated on the couch. Caption B has a man on a couch. Selecting the child, the couch adult, or the complete human age composition changes the comparison; the current record leaves that scope unresolved.

**Policy check:** Review scope or feature.

**Review issue:** The shared couch role may select the two adults under principal comparable referent conventions. An all-human reading is also available and deserves explicit scope adjudication.

**Question for your review:** Do the principal comparable referent conventions select the couch adults, or should this condition cover every described human?

**Recorded competing scopes:**

- couch adult compared with couch man: adult compared with adult; recorded alternative rating 5.
- foreground child compared with principal man: child compared with adult; recorded alternative rating 1.
- all described humans age composition: child and adult compared with adult; recorded alternative rating 3.

**History:** supplied source rating 2; version-3 status agreement, rating 3. Current decision pathway: focused_semantic_adjudication.

### 059. train_1809: size of cow

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3, S4.

**Caption A:** A lean cow eats grass in the foreground as a horse climbs the hillside behind.

**Caption B:** A large cow with small horns is sticking its tongue out and is surrounded by green grass.

**Adopted scope:** overall cow size

**Extracted A:** lean body condition; overall size unstated

**Extracted B:** large overall size

**Recorded reason, verbatim:**

> Lean specifies body condition rather than the cow's overall size, which is unavailable in the first caption.

**Audit explanation:** The recorded exclusion interprets cow size as overall physical scale. Caption A calls the cow lean, supplying body condition while leaving height or overall scale unspecified. Caption B calls its cow large. Lean build may still provide a recoverable size dimension if the user's intended feature includes body bulk.

**Policy check:** Review scope or feature.

**Review issue:** Lean supplies physical build information. Restricting size to overall scale may discard a partial recoverable value under the broader condition wording.

**Question for your review:** Does size of cow include body build or bulk, or specifically overall stature and scale?

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 060. train_1870: activity

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Action/activity. **Policy:** S1, S3, S6.

**Caption A:** Two motorcycles are near a curve in the road in front of a two story house.

**Caption B:** a rider on a motorcycle gives a thumbs up as he drives on a street

**Adopted scope:** principal motorcycle activity

**Extracted A:** near road curve; motion unspecified

**Extracted B:** riding and giving thumbs up

**Recorded reason, verbatim:**

> Motorcycles being near a road curve does not establish an activity.

**Audit explanation:** Caption A locates two motorcycles near a curve in a road and in front of a house, leaving their movement or use unspecified. Caption B explicitly describes riding on a street and giving a thumbs up. The recorded principal motorcycle activity comparison lacks an activity value in A; proximity to a road supplies location.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 061. train_1875: perspective of batter in sport

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Location/scene. **Policy:** S1, S3, S6.

**Caption A:** A crowd is watching a batter getting ready to take aim at a pitch.

**Caption B:** A shot from behind of a batter poised, waiting for the ball to be thrown.

**Adopted scope:** camera perspective on batter

**Extracted A:** unspecified

**Extracted B:** from behind

**Recorded reason, verbatim:**

> Audience presence does not establish camera position. / Only the second establishes the visual perspective on the batter.

**Audit explanation:** Caption A describes a crowd watching a batter prepare for a pitch, with no stated camera position relative to the batter. Caption B explicitly supplies a shot from behind. For the recorded camera perspective scope, A lacks the requested viewing direction; the crowd's presence identifies spectators without fixing the photographer's viewpoint.

**Policy check:** Policy consistent.

**History:** supplied source rating 4; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 062. train_1906: absence of hand towel

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S1, S3.

**Caption A:** A kitchen with two sinks with a dish rack in one and dirty dishes in another.

**Caption B:** The stove is shiny and has a hand-towel with an A hanging off its handle.

**Adopted scope:** whether hand towel is absent

**Extracted A:** unknown

**Extracted B:** not absent: towel present

**Recorded reason, verbatim:**

> Final blind invalid consensus: A gives no towel information; B explicitly contradicts towel absence. / Second towel defeats absence; first caption never establishes towel absence. / A does not establish towel absence; B explicitly includes a towel.

**Audit explanation:** Caption A describes two kitchen sinks, a dish rack and dirty dishes, leaving hand towel presence unspecified. Caption B explicitly places a hand towel on the stove handle, establishing presence and therefore a negative value for towel absence. A supplies neither towel presence nor a supported absence, leaving the requested comparison unavailable.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 063. train_2021: type of signals

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S2, S3, S4.

**Caption A:** A view of a city street with oncoming traffic taken through metal posts of a sign.

**Caption B:** This stop light is advanced in that it has red turn signals and green as well

**Adopted scope:** traffic signal type

**Extracted A:** unspecified sign seen through its posts

**Extracted B:** illuminated red and green turn signals

**Recorded reason, verbatim:**

> An unspecified sign does not establish a traffic-signal type in the first caption.

**Audit explanation:** The recorded scope requires a traffic signal type. Caption A describes a city street viewed through metal posts belonging to an unspecified sign. Caption B identifies a stop light with red and green turn signals. A lacks an explicitly identified traffic light, while its sign could supply a broader traffic control object reading.

**Policy check:** Review scope or feature.

**Review issue:** The condition says type of signals. Whether street signage belongs within that scope determines whether A has a coarse comparable type or lacks the required entity.

**Question for your review:** Does type of signals include road signs, or does it specifically require illuminated traffic signals?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 064. train_2022: type of room

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S3, S4, S5.

**Caption A:** A photo of a computer screen with furniture in the background and sunlight beaming through the window.

**Caption B:** A room with a plant, television, a stack of books and someone with their feet up in it. 

**Adopted scope:** room type

**Extracted A:** unspecified furnished room with computer

**Extracted B:** unspecified furnished room with television and reclining person

**Recorded reason, verbatim:**

> Neither caption reliably establishes a room type. / Neither furniture list uniquely establishes a specific room type.

**Audit explanation:** The current exclusion seeks a specific room function in each caption. Caption A gives a computer screen, furniture and window sunlight. Caption B gives a room with a television, plant, books and a person with feet up. Specific functions remain uncertain. Both captions support the broader furnished room category.

**Policy check:** Review scope or feature.

**Review issue:** Both scenes support room as a broad type, and B has living space cues. Requiring a unique functional subtype may conflict with partial type comparison policy.

**Question for your review:** Should a broad room category or ordinary living space inference count as recoverable room type here?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 065. train_2023: number of people

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** A photo of a computer screen with furniture in the background and sunlight beaming through the window.

**Caption B:** A room with a plant, television, a stack of books and someone with their feet up in it. 

**Adopted scope:** number of people

**Extracted A:** no person described

**Extracted B:** one person

**Recorded reason, verbatim:**

> First caption provides no people count or explicit absence. / First caption gives no person count or explicit absence.

**Audit explanation:** Caption A describes a computer screen, background furniture and sunlight through a window, with people left unspecified. Caption B explicitly mentions someone with their feet up, establishing one described person. The exclusion rests on A's unavailable people count; furniture and a computer establish neither an occupant total nor an empty room.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 066. train_2038: type of area involved

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S3, S4, S5.

**Caption A:** White vertical blinds hang in the windows of a white room with wood flooring, with a bed, a lamp, and a bookshelf with a small television on top of it.

**Caption B:** A room with two pictures on the wall and a table with a computer monitor on it.  A wooden floor and a table with a yellow bowl and a grey and white rug.

**Adopted scope:** room type

**Extracted A:** bedroom

**Extracted B:** room with tables and computer, function unspecified

**Recorded reason, verbatim:**

> First implies bedroom; second furnishings do not establish a room function.

**Audit explanation:** Caption A describes a room containing a bed, supporting the recorded bedroom interpretation. Caption B describes a room with pictures, tables, a computer monitor, bowl and rug, leaving its specific function uncertain. The current exclusion requires a functional subtype in B even though its broader room type is explicit.

**Policy check:** Review scope or feature.

**Review issue:** B supplies the broad room category, while A supports bedroom. The policy permits comparisons with missing type specificity when both captions provide recoverable categories.

**Question for your review:** Should bedroom versus a room of unspecified function be treated as a meaningful type comparison under the frozen policy?

**History:** supplied source rating 4; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 067. train_2146: style of room

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3, S6.

**Caption A:** A vintage-styled attic bathroom is painted a great shade of green, and has a claw-foot tub.

**Caption B:** A bathroom with two sinks, a rug, shower curtain and a tub in it. 

**Adopted scope:** bathroom style

**Extracted A:** vintage attic bathroom, green, claw-foot tub

**Extracted B:** style unspecified; standard bathroom fixtures

**Recorded reason, verbatim:**

> Fixtures alone do not establish second room's style. / Only the first establishes a room decor style.

**Audit explanation:** Caption A establishes vintage decor through the vintage styled attic bathroom description, green paint and claw foot tub. Caption B lists two sinks, a rug, shower curtain and tub, supplying fixtures without an expressed decor style. For the requested room style, B lacks a recoverable stylistic value from those ordinary fixtures alone.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 068. train_2149: number of slices

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** A glass table with a spinach pizza, a bottle of wine, and two filled glasses.

**Caption B:** Two slices of pizza on a plate next to a box of bread sticks.

**Adopted scope:** pizza slice count

**Extracted A:** unspecified for pizza

**Extracted B:** two slices

**Recorded reason, verbatim:**

> Whole pizza description does not establish any slice count. / First caption identifies pizza without establishing a slice count.

**Audit explanation:** Caption A identifies a spinach pizza on a glass table with wine and filled glasses, leaving its division into slices unspecified. Caption B explicitly describes two pizza slices. The requested slice count is unavailable in A; a singular pizza establishes one pizza object while leaving the number of slices unresolved.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 069. train_2183: type of fruit

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S2, S3.

**Caption A:** A woman sits near a table with a cake and a bowl of oranges.

**Caption B:** A little girl wears a pink and white striped shirt sits in front of a large cake with chocolate icing.

**Adopted scope:** fruit type

**Extracted A:** oranges

**Extracted B:** no fruit described

**Recorded reason, verbatim:**

> The second caption supplies no fruit entity or type. / Second caption provides no fruit to compare.

**Audit explanation:** Caption A explicitly names oranges in a bowl near a woman and cake. Caption B describes a little girl sitting before a cake with chocolate icing, supplying no fruit entity. The requested fruit type is therefore available as oranges in A and unavailable in B; cake and chocolate icing establish different food categories.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 070. train_2203: presence of liquid

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S1, S3.

**Caption A:** Plate of food ready to be served, each has a fried egg on top.

**Caption B:** A table set for breakfast with tea an two plates with eggs and sausages.

**Adopted scope:** presence of liquid

**Extracted A:** unspecified

**Extracted B:** present: tea

**Recorded reason, verbatim:**

> Final blind invalid consensus: A gives no liquid information; B explicitly supplies tea. / Tea establishes liquid; an egg dish establishes no liquid presence. / Tea establishes liquid in B; A leaves liquid presence unspecified.

**Audit explanation:** Caption A describes prepared plates of food with fried eggs on top and leaves liquid presence unspecified. Caption B explicitly includes tea in a breakfast setting, establishing a liquid. The exclusion rests on A's missing liquid presence value; prepared eggs and general food wording establish neither a beverage nor a supported absence of liquid.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 071. train_2228: number of ring binder

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** Knitting yarn, a spool of thread, a book, a remote control, a clip board, and three ring binder are on a couch. 

**Caption B:** A wooden desk with a lot of clutter on it and a desktop computer and monitor on the desk.

**Adopted scope:** ring-binder count

**Extracted A:** one three-ring binder

**Extracted B:** no binder described among unspecified clutter

**Recorded reason, verbatim:**

> The second caption provides no ring-binder count. / Three-ring describes binder design; second gives no binder count.

**Audit explanation:** Caption A describes a three ring binder among yarn, thread, a book and other couch objects; the singular binder phrase supplies one binder. Caption B mentions desk clutter and a computer, with binders unspecified. General clutter leaves the requested binder count unavailable, and the three in A describes the binder's ring design.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 072. train_2237: number of animals

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3, S4.

**Caption A:** two photos of an old street with horses and a new street with a truck

**Caption B:** A series of two photographs one showing a city in the past and the other in the future.

**Adopted scope:** animal count in photographs

**Extracted A:** plural horses, exact number unspecified

**Extracted B:** no animals described

**Recorded reason, verbatim:**

> The second caption gives no animal count. / Second caption supplies no animals whose count is extractable.

**Audit explanation:** Caption A describes horses in an old street photograph, providing a plural animal quantity with an uncertain exact total. Caption B describes two photographs showing a city in the past and future, leaving animal presence and number unspecified. The exclusion rests on B's unavailable animal count, while A already supplies a plural quantity.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 073. train_2294: type of flowers

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S2, S3, S4.

**Caption A:** Two cats playing on a table with a vase and flowers in the middle.

**Caption B:** A black and white cat napping in front of a mural of autumn flowers and leaves.

**Adopted scope:** flower type

**Extracted A:** unspecified flowers in vase

**Extracted B:** autumn flowers depicted in mural, species unspecified

**Recorded reason, verbatim:**

> Neither caption identifies a comparable botanical flower type. / First flower varieties are missing; second describes painted flowers.

**Audit explanation:** The current exclusion requires botanical flower varieties. Caption A supplies flowers in a vase, and caption B supplies autumn flowers represented in a mural. Species identities remain unspecified in both. The actual condition asks type of flowers, so their shared flower category and B's seasonal description may provide broader recoverable type information.

**Policy check:** Review scope or feature.

**Review issue:** The recorded botanical species scope is narrower than the condition wording. Both captions identify flowers, and depicted flowers can still have a type.

**Question for your review:** Should flower type require a botanical variety, or can generic and seasonal flower descriptions support a comparison?

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 074. train_2359: number of cups

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** A bowl of food sitting on top of a table on a blue plate.

**Caption B:** a plate covered with bananas with a coffee cup filled with some type of beverage

**Adopted scope:** number of cups

**Extracted A:** no cup described

**Extracted B:** one coffee cup

**Recorded reason, verbatim:**

> The first caption establishes a bowl, not a cup count. / First caption names bowl and plate but no cup.

**Audit explanation:** Caption A describes a bowl of food resting on a blue plate on a table, leaving cups unspecified. Caption B explicitly includes one coffee cup filled with a beverage beside bananas. The requested cup count is unavailable in A; the bowl and plate establish separate vessel types without establishing a cup total.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 075. train_2367: player's action

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Action/activity. **Policy:** S1, S3, S4, S5.

**Caption A:** A tennis player and a ball on a court that is surrounded by a fence.

**Caption B:** A man in blue shorts and a loose fitting shirt swinging a tennis racket.

**Adopted scope:** principal player's action

**Extracted A:** unspecified on court

**Extracted B:** swinging racket

**Recorded reason, verbatim:**

> The first caption provides no player action to compare. / First caption names a player but no current action.

**Audit explanation:** The current exclusion requires an identifiable player action in A. Caption A places a tennis player and ball on a fenced court, while caption B explicitly describes a man swinging a tennis racket. A lacks a specific movement verb. The ordinary tennis scene may support a coarse playing tennis activity.

**Policy check:** Review ordinary inference.

**Review issue:** A tennis player with a ball on a tennis court may support ordinary activity inference. The frozen policy permits standard scene and activity implications.

**Question for your review:** Does this tennis scene supply enough direct context for a coarse playing tennis action under the permitted inference rule?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 076. train_2379: size of floral arrangement

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3, S6.

**Caption A:** A large floral arrangement sitting on a table in the entryway of a house.

**Caption B:** A bouquet of flowers is stuffed inside an arrangement of wine glasses on a table.

**Adopted scope:** floral arrangement size

**Extracted A:** large

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Second caption supplies no reliable floral arrangement size. / Only the first gives floral arrangement size; second omits it.

**Audit explanation:** Caption A explicitly calls the floral arrangement large and locates it on an entryway table. Caption B describes a bouquet placed inside an arrangement of wine glasses on a table, leaving the bouquet's overall size unspecified. Multiple glasses and the word bouquet supply arrangement context without a reliable large or small size value.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 077. train_2385: size of animal

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3, S4, S5.

**Caption A:** A woman squatting down and reaching out to touch an elephants trunk that is pointed towards her.

**Caption B:** A man leading an elephant across a dirt yard with another elephant in the background.

**Adopted scope:** elephants' size

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Neither caption establishes the elephant's size. / Neither description gives the animals size with sufficient specificity.

**Audit explanation:** The current exclusion seeks size information beyond the named animal species. Caption A describes a woman reaching toward an elephant's trunk, and caption B describes a man leading an elephant with another behind. Individual sizes remain unstated. Elephant identity may support an ordinary coarse large animal inference in both captions.

**Policy check:** Review ordinary inference.

**Review issue:** Elephants commonly support a coarse large animal size category. The recorded exclusion may demand more individual size precision than the intended feature requires.

**Question for your review:** May characteristic species size supply a coarse animal size value here, or does the condition require individual stature?

**History:** supplied source rating 5; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 078. train_2440: color of sky

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A clock tower and several buildings against a background of a partly cloudy blue sky.

**Caption B:** People satnding next to a a building with a clock at the top of it.

**Adopted scope:** sky color

**Extracted A:** partly cloudy blue

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Second caption provides no information about sky color. / Second caption provides no sky color for comparison.

**Audit explanation:** Caption A explicitly describes a partly cloudy blue sky behind a clock tower and buildings. Caption B describes people beside a building with a clock at the top, leaving the sky and its color unspecified. The requested sky color comparison therefore lacks a value in B; the building setting alone supplies no color.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 079. train_2494: consciousness

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Other. **Policy:** S1, S3, S5.

**Caption A:** A person in a gray and black hooded jacket working with a laptop computer.

**Caption B:** A close up of a desk looking at the keyboard and mouse and monitor.

**Adopted scope:** person's consciousness

**Extracted A:** awake, working on laptop

**Extracted B:** no person described

**Recorded reason, verbatim:**

> The second caption contains no person whose consciousness can be evaluated. / Second caption provides no person whose consciousness is assessable.

**Audit explanation:** Caption A describes a person working with a laptop, supporting an awake consciousness value through the stated activity. Caption B describes a close view of a desk, keyboard, mouse and monitor, with no person identified. The requested consciousness comparison requires a human referent in each caption, and B lacks that required entity.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 080. train_2671: number of bottles

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** Tea, a tea cup, a teddy bear, and a tea brewer sit on a countertop. 

**Caption B:** A teddy bear sitting next to a cup on a saucer with a tea towel and two bottles in the background.

**Adopted scope:** bottle count

**Extracted A:** no bottles described

**Extracted B:** two bottles

**Recorded reason, verbatim:**

> First caption supplies no bottle count or established absence. / First caption establishes no bottle count or explicit absence.

**Audit explanation:** Caption A lists tea, a tea cup, teddy bear and tea brewer on a counter, leaving bottles unspecified. Caption B explicitly includes two bottles behind a teddy bear and cup. The requested bottle count is unavailable in A; the listed tea equipment establishes neither a bottle quantity nor an explicit absence of bottles.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 081. train_2679: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** Various tools are sitting on a table with a notepad and pen ready for note taking.

**Caption B:** A hand, in a claw like position, hovers over a pair of scissors with black handles.

**Adopted scope:** principal tool color

**Extracted A:** unspecified

**Extracted B:** black handles on scissors

**Recorded reason, verbatim:**

> First caption does not establish a comparable object color. / Only the second supplies a relevant tool color.

**Audit explanation:** Caption A describes various tools on a table with a pad and pen and leaves their colors unspecified. Caption B supplies black handles on a pair of scissors. Under the principal tool color scope, A lacks the requested color information, while B provides at least a recoverable component color for its principal tool.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 082. train_2763: number of towels

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** A pot and pan sitting on a stove top under a microwave next to a collection of knives.

**Caption B:** The stove is shiny and has a hand-towel with an A hanging off its handle.

**Adopted scope:** towel count

**Extracted A:** no towel described

**Extracted B:** one hand towel

**Recorded reason, verbatim:**

> The first caption provides no information about towel count. / First caption provides no towels whose count is extractable.

**Audit explanation:** Caption A lists a pot, pan, stove, microwave and knives, leaving towel presence and number unspecified. Caption B explicitly describes a hand towel hanging from a stove handle, giving one described towel. The requested towel count lacks a value in A; a list of kitchen objects supplies no established towel total.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 083. train_2850: color of clothing

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A living room with a television, desk, chairs, and a person with a blue shirt leaning over the desk.

**Caption B:** A man is seen in the mirror and there is a lot of clothes on top of a chair

**Adopted scope:** person's clothing color

**Extracted A:** blue shirt

**Extracted B:** unspecified clothing colors

**Recorded reason, verbatim:**

> Second caption supplies no clothing color information. / Only the first supplies a color of clothing.

**Audit explanation:** Caption A describes a person wearing a blue shirt while leaning over a desk in a living room. Caption B describes a man visible in a mirror and clothes piled on a chair, leaving clothing colors unspecified. The requested person's clothing color comparison therefore lacks a value in B, including for the visible man.

**Policy check:** Policy consistent.

**History:** supplied source rating 4; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 084. train_2851: type of chair

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S2, S3, S4.

**Caption A:** A living room with a television, desk, chairs, and a person with a blue shirt leaning over the desk.

**Caption B:** A man is seen in the mirror and there is a lot of clothes on top of a chair

**Adopted scope:** chair type

**Extracted A:** unspecified chairs

**Extracted B:** unspecified chair

**Recorded reason, verbatim:**

> Neither caption establishes a particular subtype of the mentioned chairs.

**Audit explanation:** The current exclusion requires a particular chair subtype. Caption A mentions chairs among living room furniture, and caption B mentions a chair supporting clothes. Neither supplies a narrower design category. Both explicitly identify the requested chair type at a general level, creating a policy question about the required abstraction level.

**Policy check:** Review scope or feature.

**Review issue:** Both captions explicitly identify chairs. Exclusion solely for absent subtype precision may conflict with the rule allowing recoverable generic type information.

**Question for your review:** Does type of chair require a named chair subtype, or is the shared generic chair category a valid comparable type?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 085. train_2863: illumination near bed

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Other. **Policy:** S1, S3.

**Caption A:** The twin bed is neatly made with white sheets and a pair of pillows.

**Caption B:** A bedroom with a bed and a nightstand that has a red phone and a lamp on it.

**Adopted scope:** illumination near bed

**Extracted A:** unspecified

**Extracted B:** lamp on bedside nightstand

**Recorded reason, verbatim:**

> The first caption supplies no information about illumination near the bed. / First caption provides no illumination source near the bed.

**Audit explanation:** Caption A describes a neatly made twin bed, white sheets and pillows, leaving nearby lighting and light sources unspecified. Caption B places a lamp on a nightstand beside a bed. Under the recorded illumination source reading, B supplies a bedside lamp and A supplies no corresponding light source or lighting value.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 086. train_2881: speed of trains

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Other. **Policy:** S1, S3, S4, S6.

**Caption A:** A train pumps out steam while going down a track on a cloudy day.

**Caption B:** A group of people at a train station next to a red and black train.

**Adopted scope:** train speed or motion rate

**Extracted A:** moving, exact speed unspecified

**Extracted B:** speed and motion unspecified at station

**Recorded reason, verbatim:**

> Neither caption provides enough information to compare train speed. / Neither caption establishes the trains' comparative speed.

**Audit explanation:** Caption A describes a train going down a track, giving motion information while leaving its rate unspecified. Caption B places a group of people beside a train at a station, leaving the train's motion and speed unspecified. The exclusion rests on B's unavailable speed value; station location alone establishes no definite motion state.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 087. train_2989: number of tables

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** A laptop on a bed with a picture of a Reggae man behind it.

**Caption B:** An empty blue bed sitting next to a small wooden table with an open laptop.

**Adopted scope:** table count

**Extracted A:** no table described

**Extracted B:** one small table

**Recorded reason, verbatim:**

> First caption provides no table count or established absence. / First caption establishes no table count or explicit absence.

**Audit explanation:** The requested comparison concerns table quantity. Caption A places a laptop on a bed and mentions a picture behind it, leaving tables and their quantity unspecified. Caption B explicitly places an open laptop on one small wooden table. The current exclusion follows the unavailable table count in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 088. train_2994: number of drinking glasses

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** Three used clear drinking glasses sit next a plate on a counter with a lit tealight candle.

**Caption B:** A sink is in the corner of a room lighted by lamps and candles.

**Adopted scope:** drinking-glass count

**Extracted A:** three

**Extracted B:** no drinking glasses described

**Recorded reason, verbatim:**

> The second caption does not establish any drinking-glass count. / Second caption gives no drinking glasses to count.

**Audit explanation:** Caption A explicitly counts three clear drinking glasses beside a plate and candle. Caption B describes a sink, lamps and candles, leaving drinking glasses unmentioned. The requested drinking glass quantity therefore has an extracted value only in A; B supplies neither a quantity nor an established absence.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 089. train_3038: color of building

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A busy street with many business off to the side with a large clock.

**Caption B:** A gold clock sticking out of the side of a tan building with sky in the background.

**Adopted scope:** building color

**Extracted A:** unspecified

**Extracted B:** tan

**Recorded reason, verbatim:**

> The first caption does not establish any building color. / First caption does not establish a building color.

**Audit explanation:** The condition requests building color. Caption A describes a busy street, businesses and a large clock, with building colors left open. Caption B explicitly identifies a tan building supporting a gold clock. The gold clock color belongs to the device; the unavailable comparison value is building color in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 090. train_3103: size of device

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A building with a glass ceiling and a large clock mounted inside of it.

**Caption B:** a clock hanging down off a brick wall in a row of circular hanging light shades

**Adopted scope:** clock size

**Extracted A:** large

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption does not establish the clock's size. / Second caption does not establish the clock's size.

**Audit explanation:** The recorded scope identifies the clock as the device whose size is requested. Caption A calls its interior clock large. Caption B describes a clock hanging from a brick wall among circular light shades, leaving clock dimensions unspecified. The surrounding wall and shades supply placement information without establishing the clock size.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 091. train_3108: type of food

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S3, S4.

**Caption A:** Food with a metal utensil under it with a cup on the side of the plate.

**Caption B:** A closeup view of a pizza on a table with a beer behind it.

**Adopted scope:** food type

**Extracted A:** unspecified food

**Extracted B:** pizza

**Recorded reason, verbatim:**

> Generic food does not establish the first food type.

**Audit explanation:** The current exclusion treats the word food in A as wholly unavailable food type information. A describes food with a metal utensil, cup and plate, while B specifies pizza. The missing value is a narrower food category in A. This documents the existing decision while preserving the distinction between generic type and absent type.

**Policy check:** Review scope or feature.

**Review issue:** A explicitly supplies the broad food category; the policy allows comparisons between general categories and specific subtypes when relevant type information is recoverable.

**Question for your review:** Does generic food supply a coarse type value under the frozen general category versus subtype rule?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 092. train_3109: number of dishes

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3, S7.

**Caption A:** Food with a metal utensil under it with a cup on the side of the plate.

**Caption B:** A closeup view of a pizza on a table with a beer behind it.

**Adopted scope:** dish count

**Extracted A:** one plate and one cup: two

**Extracted B:** no dish described

**Recorded reason, verbatim:**

> The second caption does not establish a comparable dish count. / Second caption names pizza and beer but no serving dishes.

**Audit explanation:** Under the recorded serving container scope, A names one plate and one cup, producing two described pieces of tableware. B names pizza and beer on a table while leaving serving containers unspecified. The current exclusion therefore rests on missing container quantity in B. The condition wording also permits a food dish interpretation.

**Policy check:** Review scope or feature.

**Review issue:** The recorded scope counts crockery, including a cup; dishes can also mean prepared food portions, which could make pizza relevant.

**Question for your review:** Should dishes mean serving containers, including cups, or prepared food dishes in this comparison?

**History:** supplied source rating 4; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 093. train_3153: presence of animal

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S1, S3.

**Caption A:** A guy on a skateboard doing tricks at a city skate park as others look on.

**Caption B:** Four people and a dog watching a young man do stunts on a skateboard.

**Adopted scope:** nonhuman animal presence

**Extracted A:** unspecified

**Extracted B:** present: dog

**Recorded reason, verbatim:**

> Final blind invalid consensus: A never establishes animal presence or absence; B explicitly includes a dog. / Second caption establishes a dog; first leaves animal presence unspecified. / B explicitly includes a dog; A supplies no animal presence information.

**Audit explanation:** The requested feature is presence of a nonhuman animal. Caption A describes a skateboarder and observers at a skate park, leaving animal presence open. Caption B explicitly includes a dog watching with four people. The current exclusion follows A providing neither animal presence nor an established negative value.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 094. train_3165: type of animal

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S3, S5.

**Caption A:** Three people standing on a grass covered hill and controlling kite string that are connected to a large stork.

**Caption B:** A quite big flock of large birds are flying over what appears to be a kite.

**Adopted scope:** type of actual animal

**Extracted A:** stork-shaped kite controlled by strings

**Extracted B:** large birds, species unspecified

**Recorded reason, verbatim:**

> The ordinary string-controlled stork reading is an artificial kite rather than an actual animal.

**Audit explanation:** The recorded interpretation treats the large stork connected to kite strings in A as a stork shaped kite controlled by people. B describes a flock of large birds flying above an apparent kite. Under the adopted actual animal scope, A lacks the living animal referent needed to compare animal types.

**Policy check:** Review scope or feature.

**Review issue:** A literally names a stork, while the kite interpretation derives from its connection to controlled strings. The exclusion depends on treating that named entity as an artificial representation.

**Question for your review:** Should the string controlled stork be treated as a kite representation or as an animal type mention for this condition?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 095. train_3183: countertop

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S2, S3.

**Caption A:** A free standing tub in a bathroom well lit from the light coming through the window.

**Caption B:** A vanity and counter top with a sink and a commode in the corner.

**Adopted scope:** countertop type

**Extracted A:** no countertop described

**Extracted B:** vanity countertop

**Recorded reason, verbatim:**

> The first caption supplies no countertop entity for comparison. / First caption does not provide a countertop to compare.

**Audit explanation:** The entity only condition is recorded as countertop type. Caption A describes a freestanding bathtub in a bright bathroom and supplies no countertop referent. Caption B explicitly names a vanity countertop with a sink and commode nearby. The current exclusion follows the unavailable countertop entity in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 096. train_3207: number of people

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** A man riding atop an elephant while the elephant plays with a soccer ball.

**Caption B:** An elephant with a red bench on its back and a red and yellow blanket over it's body.

**Adopted scope:** people count

**Extracted A:** one rider

**Extracted B:** no person described

**Recorded reason, verbatim:**

> Second caption supplies no people count or established absence. / Second caption establishes no rider count or explicit absence.

**Audit explanation:** The condition counts all described people. Caption A explicitly describes one man riding an elephant. Caption B describes an elephant carrying a red bench and blanket, leaving people and their quantity unspecified. The current exclusion concerns missing people count information in B; the bench alone establishes no rider quantity.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 097. train_3208: color of wine

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** Three goblets with white, red, and blush wines in them are lined up on the table.

**Caption B:** A place setting with empty wine glasses has a piece of paper at the table.

**Adopted scope:** wine color

**Extracted A:** white, red and blush

**Extracted B:** no wine in the empty glasses

**Recorded reason, verbatim:**

> The second scene establishes empty glasses without wine color to compare. / Second explicitly contains no wine whose color can be compared.

**Audit explanation:** Caption A supplies three wine colors through white, red and blush wines in goblets. Caption B explicitly describes empty wine glasses in a place setting. Under the requested wine color scope, the empty glasses lack the wine entity needed for a color value, which explains the current exclusion.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 098. train_3209: wine on table

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S2, S3.

**Caption A:** Three goblets with white, red, and blush wines in them are lined up on the table.

**Caption B:** A place setting with empty wine glasses has a piece of paper at the table.

**Adopted scope:** type of wine on table under entity-only default

**Extracted A:** white, red and blush wine

**Extracted B:** empty wine glasses, no wine

**Recorded reason, verbatim:**

> Explicitly empty glasses supply no wine entity or wine type to compare.

**Audit explanation:** The recorded entity only interpretation asks for the type of wine on the table. A identifies white, red and blush wines in three goblets. B supplies empty wine glasses and a piece of paper. The current exclusion follows the missing wine entity in B under this adopted wine type scope.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status agreement, rating 1. Current decision pathway: focused_semantic_adjudication.

### 099. train_3217: color of animal

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A dog lies on its side and digs in the sand at the beach.

**Caption B:** A white, brown and black dog holding a green ball while standing in the ocean.

**Adopted scope:** dog coat color

**Extracted A:** unspecified

**Extracted B:** white, brown and black

**Recorded reason, verbatim:**

> The first caption supplies no dog color information. / First caption does not establish the dog's color.

**Audit explanation:** The requested animal color refers to each principal dog. Caption A describes a dog lying on its side and digging in beach sand, with coat color unspecified. Caption B explicitly gives white, brown and black coat colors. Beach location and digging activity supply no coat color value for A.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 100. train_3228: color of animal

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A tan stuffed teddy bear sits on a blue couch beside a red checkered pillow.

**Caption B:** A black and brown dogs lays his head on a pillow on a bed.

**Adopted scope:** actual animal color

**Extracted A:** tan teddy-bear toy, no actual animal

**Extracted B:** black and brown dog

**Recorded reason, verbatim:**

> The first entity is a toy, not an actual animal. / First has a toy rather than an actual animal.

**Audit explanation:** The current exclusion adopts actual animal color as the requested scope. Caption A explicitly describes a tan stuffed teddy bear on a couch, while B describes a black and brown dog on a bed. A supplies the toy color, yet lacks an actual animal under the adopted scope.

**Policy check:** Review scope or feature.

**Review issue:** Both principal entities have explicit colors. Exclusion depends on restricting animal to living animals and excluding the represented bear.

**Question for your review:** Should this generic animal color condition include the depicted color of a teddy bear, or require a living animal?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 101. train_3229: animal species

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S3.

**Caption A:** A tan stuffed teddy bear sits on a blue couch beside a red checkered pillow.

**Caption B:** A black and brown dogs lays his head on a pillow on a bed.

**Adopted scope:** actual animal species

**Extracted A:** teddy-bear toy, no actual animal

**Extracted B:** dog

**Recorded reason, verbatim:**

> The first caption contains no actual animal species entity. / An actual animal species is absent from first caption.

**Audit explanation:** The recorded scope requires an actual animal species. Caption A describes a stuffed teddy bear, establishing a toy with bear representation. Caption B describes a dog with its head on a pillow. The current exclusion follows A lacking a living animal species referent under the adopted actual animal requirement.

**Policy check:** Review scope or feature.

**Review issue:** The condition says animal species without an explicit living animal qualifier; A supplies a bear representation whose eligibility determines whether comparison is possible.

**Question for your review:** Should animal species include the animal represented by a stuffed toy, or require an actual animal?

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 102. train_3234: type of room

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Location/scene. **Policy:** S3, S6.

**Caption A:** A rolling wooden bed bed and platform with a marker drawing chalk board attached to one side of the platform.

**Caption B:** A bedroom with a bed and a nightstand that has a red phone and a lamp on it.

**Adopted scope:** room type

**Extracted A:** no room specified for rolling bed/platform

**Extracted B:** bedroom

**Recorded reason, verbatim:**

> The first unusual structure does not establish a room type. / First object description does not reliably establish a room type.

**Audit explanation:** Caption A describes an unusual rolling wooden bed and platform with an attached chalkboard, leaving its surrounding room unnamed. Caption B explicitly identifies a bedroom with a bed and nightstand. The current exclusion reflects insufficient support for assigning a room type to A from this unusual movable structure alone.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 103. train_3262: size of bus

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3, S6.

**Caption A:** A bus is driving out of a parking lot and getting on the main road.

**Caption B:** A blue and white double decker bus parked in front of a tall building.

**Adopted scope:** bus size

**Extracted A:** unspecified

**Extracted B:** tall double-decker form

**Recorded reason, verbatim:**

> The first bus's size or deck count is unavailable. / First bus size cannot be reliably determined.

**Audit explanation:** The requested feature is bus size. Caption A describes a bus moving from a parking lot onto a road and provides no dimensions or deck configuration. Caption B identifies a double decker bus, supporting its tall form. The current exclusion rests on A lacking a comparable bus size value.

**Policy check:** Policy consistent.

**History:** supplied source rating 4; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 104. train_3293: color of cloth

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** This is a well designed bathroom that is plain and elegant at the same time.

**Caption B:** A nice clean bathroom with a white towel on the corner of the sink.

**Adopted scope:** cloth color

**Extracted A:** no cloth described

**Extracted B:** white towel

**Recorded reason, verbatim:**

> The first caption supplies no cloth entity or color. / First caption supplies no cloth whose color can be compared.

**Audit explanation:** The cloth color condition requires a cloth referent in each caption. A characterizes a bathroom as plain and elegant, leaving cloth items unmentioned. B explicitly describes a white towel at the sink. The current exclusion follows the missing cloth entity and consequent unavailable cloth color in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 105. train_3363: activity

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Action/activity. **Policy:** S1, S3.

**Caption A:** A dog laying on top of a cat, as the cat tries to push it away.

**Caption B:** Close up back and back of head of a cat in dark with two rectangles of light on ground in front.

**Adopted scope:** principal cat's activity

**Extracted A:** pushing dog away

**Extracted B:** activity unspecified in rear close-up

**Recorded reason, verbatim:**

> Second specifies appearance and viewpoint without establishing an animal activity.

**Audit explanation:** The adopted comparable referent is the cat in each caption. A explicitly describes its cat trying to push away a dog lying on it. B describes a close view of a cat from behind with light rectangles ahead, leaving the cat activity unspecified. Viewpoint and surroundings supply no definite comparable activity.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 106. train_3478: location of ball

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Spatial relation/posture. **Policy:** S1, S3, S4.

**Caption A:** The tennis player is crouched down, making an effort to hit a low ball.

**Caption B:** A man in white shorts and a white shirt hitting a ball with a racket.

**Adopted scope:** ball position

**Extracted A:** low near ground

**Extracted B:** unspecified relative height while struck

**Recorded reason, verbatim:**

> Hitting with racket does not establish ball height. / Only the first establishes the balls height or location.

**Audit explanation:** The recorded exclusion narrows ball location to vertical height. A establishes a low ball through a crouching tennis player attempting a hit. B establishes a ball being struck with a racket while leaving its height unspecified. The current missing value is B ball height. A coarser racket relative position is available.

**Policy check:** Review scope or feature.

**Review issue:** The condition requests ball location, while the rationale requires ball height. B locates the ball at racket contact, supplying a recoverable spatial relation.

**Question for your review:** Should location of ball be restricted to height, or may player and racket relative locations supply comparable values?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 107. train_3518: type of drink

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S3.

**Caption A:** a plate with a sandwich on it on a wooden table next to a tall glass

**Caption B:** A meal of a lunch meat sandwich and iced tea is on the table.

**Adopted scope:** drink type

**Extracted A:** no drink contents specified for tall glass

**Extracted B:** iced tea

**Recorded reason, verbatim:**

> A tall glass does not establish drink type. / Only the second identifies the type of beverage.

**Audit explanation:** Caption A names a sandwich, plate and tall glass on a wooden table, leaving any drink contents unidentified. Caption B explicitly identifies iced tea beside a lunch meat sandwich. The requested beverage type is therefore available only in B; the glass shape in A supplies no particular drink type.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 108. train_3534: size of room

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A small living area contains the kitchen, dining room table, living room furniture and a view into the bathroom.

**Caption B:** A metal cart stands in a modern kitchen with hardwood floors and wooden cabinets.

**Adopted scope:** room size

**Extracted A:** small living area

**Extracted B:** kitchen size unspecified

**Recorded reason, verbatim:**

> Second caption provides no room-size information. / Only the first supplies a room size description.

**Audit explanation:** The requested room size has an explicit small value in A, which describes a living area containing several domestic spaces. B describes a kitchen with a metal cart, hardwood floors and wooden cabinets, leaving room dimensions unspecified. Furniture, finishes and the modern style supply no definite kitchen size for comparison.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 109. train_3567: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** There is a snow boarder doing stunts on a snow board and some people walking near him.

**Caption B:** A snowboarder wearing a yellow coat and brown pants rides down a snow covered hill.

**Adopted scope:** principal sporting object's color: snowboard

**Extracted A:** unspecified snowboard color

**Extracted B:** unspecified snowboard color

**Recorded reason, verbatim:**

> The first caption supplies no comparable object color. / First caption supplies no comparable object colors.

**Audit explanation:** The recorded principal object is the snowboard. Caption A describes a snowboarder performing stunts while nearby people walk, with board color unspecified. Caption B describes a snowboarder in a yellow coat and brown pants, while also leaving board color unspecified. The clothing colors belong to garments outside the adopted snowboard scope.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 110. train_3582: address of street

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Location/scene. **Policy:** S1, S3, S6.

**Caption A:** A street pole with a street sign on it that says B 86 Street, and a lamp post in the distance.

**Caption B:** A row of parking meters on the side of a street next to a building.

**Adopted scope:** street address/name

**Extracted A:** B 86 Street

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Second caption provides no street address. / Only the first supplies a street name or address.

**Audit explanation:** The condition requests the street address or name. Caption A provides the sign text B 86 Street. Caption B describes parking meters beside a street and building, with street identity unspecified. Meters and a building establish a streetscape while providing no supported address value, explaining the current exclusion.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 111. train_3618: color of animal

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A dog with a ball running along the edge of the ocean at the beach.

**Caption B:** A black and white dog stands beside a green and pink Frisbee on a sunny day.

**Adopted scope:** principal dog color

**Extracted A:** unspecified

**Extracted B:** black and white

**Recorded reason, verbatim:**

> The first caption supplies no dog color information. / First caption does not describe the dog's color.

**Audit explanation:** The animal color condition refers to each principal dog. Caption A describes a dog carrying a ball along an ocean beach, with coat color unspecified. Caption B explicitly calls its dog black and white. The green and pink Frisbee in B is incidental to the requested dog coat comparison.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 112. train_3619: color of dog

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A dog with a ball running along the edge of the ocean at the beach.

**Caption B:** A black and white dog stands beside a green and pink Frisbee on a sunny day.

**Adopted scope:** dog coat color

**Extracted A:** unspecified

**Extracted B:** black and white

**Recorded reason, verbatim:**

> The first caption supplies no dog color information. / First caption does not describe the dog's color.

**Audit explanation:** The requested feature is dog coat color. A describes a dog running with a ball at the edge of the ocean, leaving its coat colors open. B explicitly describes a black and white dog beside a Frisbee. The current exclusion follows the unavailable coat color value in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 113. train_3623: view of animal

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Spatial relation/posture. **Policy:** S1, S3.

**Caption A:** The dog is getting a breathe of fresh air while riding in the car.

**Caption B:** A view of a dog with his head sticking out of a car window through a mirror.

**Adopted scope:** viewpoint on dog

**Extracted A:** unspecified

**Extracted B:** mirror reflection of head at window

**Recorded reason, verbatim:**

> The first caption does not establish the observer's view of the dog. / First caption does not establish the viewing perspective.

**Audit explanation:** The recorded view condition concerns observer perspective on the dog. A describes a dog enjoying fresh air while riding in a car, without specifying the viewing perspective. B explicitly presents the dog head outside a window through a mirror. The current exclusion rests on A lacking a comparable observer viewpoint.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 114. train_3625: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A tennis court with a person in shorts and a hat jumping up and swinging the tennis racquet.

**Caption B:** The girl is wearing a red and white tennis dress and has her racquet ready to hit.

**Adopted scope:** tennis clothing color

**Extracted A:** unspecified

**Extracted B:** red and white

**Recorded reason, verbatim:**

> First caption gives no color for comparable objects. / First caption supplies no relevant object color to compare.

**Audit explanation:** The recorded scope selects tennis clothing as the object whose color is compared. A mentions shorts and a hat with their colors unspecified. B explicitly supplies a red and white tennis dress. The current exclusion follows missing clothing colors in A. Both captions also mention rackets whose colors remain unspecified.

**Policy check:** Review scope or feature.

**Review issue:** The generic object condition is resolved as clothing. The shared tennis racket is another principal object. This affects which colors are treated as available.

**Question for your review:** Should the comparable object be tennis clothing or the shared racket under the principal entity convention?

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 115. train_3627: sentiment of people

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Emotion/sentiment. **Policy:** S1, S3, S6.

**Caption A:** A girl has a spoon in her mouth in front of her lunch at school.

**Caption B:** A young boy who is using a fork and knife to eat a pizza.

**Adopted scope:** people emotional sentiment

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Eating descriptions establish neither person's emotional state. / Neither description establishes a reliable emotional state for comparison.

**Audit explanation:** Caption A describes a girl with a spoon in her mouth at a school lunch. Caption B describes a boy using a fork and knife to eat pizza. The requested emotional sentiment is unspecified in both descriptions; the eating actions and utensils provide no direct high confidence indication of either child emotional state.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 116. train_3650: number of bookshelves

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** From this vantage point it is easy to see the wall of windows and the patio outside.

**Caption B:** a room with a couch chair bookshelf and a window view of the city

**Adopted scope:** bookshelf count

**Extracted A:** no bookshelf established

**Extracted B:** 1 bookshelf

**Recorded reason, verbatim:**

> First caption supplies no bookshelf count or established absence. / First caption establishes no bookshelf count or explicit absence.

**Audit explanation:** The requested quantity is the number of bookshelves. A describes a wall of windows and an outside patio, leaving bookshelves unmentioned. B explicitly lists a bookshelf among room furnishings. The current exclusion follows A supplying neither a bookshelf quantity nor an established absence; B supplies one described bookshelf.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 117. train_3708: color of bathroom features

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3, S5, S6.

**Caption A:** A large bathroom with marble countertops and a standup shower with a glass door.

**Caption B:** Three piece bathroom photo with granite countertop and multi colored beige tile around the tub.

**Adopted scope:** bathroom fixture colors

**Extracted A:** unspecified

**Extracted B:** beige and multicolored tile

**Recorded reason, verbatim:**

> Marble material does not reliably establish bathroom feature colors. / Material names do not establish first bathroom feature colors.

**Audit explanation:** The recorded exclusion treats bathroom feature colors in A as unavailable: marble countertops specify material, and the shower door is glass. B explicitly supplies multicolored beige tile around a tub. Marble alone leaves hue open. The glass door offers a possible ordinary transparent appearance that the current color extraction leaves unused.

**Policy check:** Review ordinary inference.

**Review issue:** A glass shower door may supply a clear or transparent appearance under ordinary contextual inference, depending on the intended breadth of color of bathroom features.

**Question for your review:** Should clear or transparent glass appearance count as recoverable feature color here?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 118. train_3784: type of view

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Spatial relation/posture. **Policy:** S1, S3.

**Caption A:** A view of a living room and dining room from up on another floor

**Caption B:** A room with a fire place, chair, couch, two lamps, tables, television and ottomans. 

**Adopted scope:** viewpoint on room

**Extracted A:** from an upper floor

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption does not establish a comparable viewing angle. / Second caption does not specify a viewing perspective.

**Audit explanation:** The recorded view type is camera or observer position relative to the room. A explicitly presents a living and dining room from another floor above. B lists a fireplace, seating, lamps and other furnishings, leaving viewpoint unspecified. The current exclusion follows the unavailable viewing angle in B.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 119. train_3799: number of pictures

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** A room with two beds, two lamps, two pictures and a telephone in it. 

**Caption B:** A motel large motel room with a flat screen television, chairs, table and a bed.

**Adopted scope:** picture count

**Extracted A:** 2

**Extracted B:** no pictures established

**Recorded reason, verbatim:**

> Second caption establishes no number of pictures. / Second caption establishes no picture count or explicit absence.

**Audit explanation:** The requested feature counts pictures. Caption A explicitly names two pictures in a room with two beds and two lamps. Caption B lists motel room furniture and a television, leaving pictures unmentioned. The current exclusion follows B supplying neither a picture quantity nor an established absence of pictures.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 120. train_3811: chopped vegetables

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S2, S3.

**Caption A:** The core of an apple and peels with a knife on a cutting board

**Caption B:** A bunch of chopped uncooked vegetables together including potatoes, carrots and other types of vegetables.

**Adopted scope:** chopped vegetable type

**Extracted A:** no vegetables: apple remains

**Extracted B:** potatoes, carrots and other vegetables

**Recorded reason, verbatim:**

> The first caption does not provide a chopped-vegetable entity. / First caption contains no chopped vegetables to compare.

**Audit explanation:** Under the entity only default, the condition requests chopped vegetable type. Caption A describes an apple core and peels beside a knife, establishing fruit remains. Caption B explicitly describes chopped vegetables including potatoes and carrots. The current exclusion follows the absence of a chopped vegetable referent in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 121. train_3820: color of river

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** a train is on it's tracks next to a dirt road and grassy patch

**Caption B:** A train on a rail line on the bridge on top of a river

**Adopted scope:** river color

**Extracted A:** no river established

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Neither caption establishes a comparable river color. / Neither caption supplies a comparable river color value.

**Audit explanation:** The requested feature is river color. Caption A places a train beside a dirt road and grass, leaving a river unestablished. Caption B explicitly places a rail bridge above a river while leaving water color unspecified. The current exclusion therefore has a missing river entity in A and missing river color in B.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 122. train_3899: type of vehicle

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S3, S6.

**Caption A:** Two traffic lights are suspended above a road with parked cars, surrounded by buildings, with a person crossing it

**Caption B:** A traffic light on a busy street with the word "TAXI" printed on it.

**Adopted scope:** vehicle type

**Extracted A:** cars

**Extracted B:** no vehicle established; TAXI is printed text

**Recorded reason, verbatim:**

> The word TAXI on a light does not establish a taxi vehicle. / TAXI lettering does not establish an actual vehicle's presence.

**Audit explanation:** Caption A explicitly describes parked cars beneath traffic lights, supplying a vehicle type. Caption B describes a traffic light bearing the printed word TAXI on a busy street. Under the recorded vehicle scope, lettering identifies text on a signal and leaves an actual vehicle referent and its type unavailable in B.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 123. train_3951: number of vehicles

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** An old television set and a car is visible on the screen and a light is reflecting off of it.

**Caption B:** A photo of a TV set net to a wood vanity and stool with a green wall behind both.

**Adopted scope:** depicted vehicle count

**Extracted A:** 1 car shown on TV

**Extracted B:** no vehicle established

**Recorded reason, verbatim:**

> Second caption provides no vehicle information or established absence. / Second scene does not establish vehicle presence or absence.

**Audit explanation:** The recorded scope includes vehicles depicted on a television screen. Caption A explicitly describes one car visible on an old television. Caption B describes a television beside a vanity and stool with a green wall, leaving any vehicle imagery unspecified. The current exclusion follows unavailable depicted vehicle quantity in B.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 124. train_4076: name of room

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Location/scene. **Policy:** S2, S3, S6.

**Caption A:** A room with a leather chair and a clock on the wall behind the chair.

**Caption B:** The view of a dining room an a living room, where a woman is sitting on the couch.

**Adopted scope:** room function type

**Extracted A:** room with chair and clock; function unavailable

**Extracted B:** dining room and living room

**Recorded reason, verbatim:**

> A chair and wall clock do not establish the room's function.

**Audit explanation:** The requested room name is interpreted as room function type. A supplies a leather chair and wall clock inside an otherwise unnamed room. B explicitly identifies dining and living rooms. The current exclusion reflects the inability to assign A a particular room function reliably from those widely usable furnishings alone.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 125. train_4079: number of legs of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3, S6.

**Caption A:** A desk with a bunch of items that would be found in the purse on the desk.

**Caption B:** The table has weapons and other items that can be used to make a weapon.

**Adopted scope:** principal furniture leg count

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Neither caption establishes the furniture's number of legs. / Furniture names do not reliably establish an exact leg count.

**Audit explanation:** The adopted object scope is the principal furniture, a desk in A and table in B. Both captions describe items resting on the furniture while leaving supports unmentioned. Exact furniture leg counts remain unavailable because desk and table designs vary. The current exclusion follows the unsupported fine count in both captions.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 126. train_4097: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A refrigerator with the door open in one picture and closed in the other.

**Caption B:** A refrigerator has magnets and papers and food on top of it in the corner of a yellow tiled kitchen

**Adopted scope:** refrigerator color

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Neither caption supplies the refrigerator's color. / Neither caption establishes the refrigerator's color.

**Audit explanation:** The principal comparable objects are refrigerators. A describes refrigerator door states across two pictures, while B describes magnets, papers and food around a refrigerator in a yellow tiled kitchen. Neither description supplies refrigerator color. The yellow color belongs to the kitchen tiles and leaves the requested appliance color unavailable.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 127. train_4113: color of vehicle

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** Several buses travelling in one direction and a cab travelling in the opposite direction.

**Caption B:** A row of red and yellow buses with people standing around and a few merchandise stands and parked motorbikes.

**Adopted scope:** principal bus colors

**Extracted A:** unspecified

**Extracted B:** red and yellow

**Recorded reason, verbatim:**

> The first caption supplies no vehicle color information. / First caption does not establish vehicle colors.

**Audit explanation:** The adopted vehicle referents are the buses in both captions. A describes several buses traveling together and a cab moving oppositely, with vehicle colors unspecified. B explicitly identifies red and yellow buses near people and merchandise stands. The current exclusion follows missing bus color information in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 128. train_4206: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3, S5.

**Caption A:** A pizza sitting on top of a wooden cutting board next to a white plate.

**Caption B:** A hot pizza on the table is loaded with pepperoni and cheese and sausage.

**Adopted scope:** principal pizza color

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption does not establish a comparable object color. / Second caption does not establish a comparable object color.

**Audit explanation:** The recorded principal object is the pizza. A places pizza on a wooden cutting board beside a white plate, while B specifies pepperoni, cheese and sausage toppings. The current extraction treats pizza colors as unavailable in both captions. The white plate color belongs to an incidental object outside that adopted pizza scope.

**Policy check:** Review ordinary inference.

**Review issue:** B names toppings with ordinary recognizable appearances, and both captions identify pizza. The current exclusion may require a stricter color inference threshold than other ordinary context cases.

**Question for your review:** Should ordinary pizza and topping colors supply coarse appearance values, or must pizza hues be expressly described?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 129. train_4234: animal's age

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Age. **Policy:** S1, S3, S4.

**Caption A:** A kitten coming indoors through a cat door near a toy on a string

**Caption B:** A grey cat looks up and meows, as the cat wears a purple leash.

**Adopted scope:** cat age category

**Extracted A:** kitten: juvenile

**Extracted B:** cat; age unspecified

**Recorded reason, verbatim:**

> Cat does not reliably establish adult age. / Only the first establishes a specific animal age category.

**Audit explanation:** The requested feature is cat age category. Caption A explicitly calls its animal a kitten, establishing a juvenile. Caption B describes a grey cat meowing in a purple leash, leaving age unspecified. The generic cat category supplies species information while providing no recoverable age category under the recorded scope.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 130. train_4279: color of plate

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** Two white plates have hash browns and an egg dish on them as they sit on a brown table.

**Caption B:** A man in a restaurant sitting in front of a plate of breakfast food.

**Adopted scope:** plate color

**Extracted A:** white

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Second caption does not establish plate color. / Only the first supplies a color for the plates.

**Audit explanation:** The requested feature is the color of the food plates. Caption A explicitly calls its two plates white. Caption B describes a man sitting before a plate of breakfast food in a restaurant, leaving that plate's color unavailable. Restaurant setting and breakfast contents supply no plate color.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 131. train_4307: number of bottles

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** Two bottles of wine on a table with a half full glass of red wine.

**Caption B:** Several wine glasses have just a little bit of wine in each of them.

**Adopted scope:** wine bottle count

**Extracted A:** 2 bottles

**Extracted B:** no bottles established

**Recorded reason, verbatim:**

> The second caption does not establish any bottle count. / Second caption describes glasses without establishing bottle count.

**Audit explanation:** The condition counts wine bottles. Caption A establishes two bottles alongside a half full glass. Caption B establishes several wine glasses containing small amounts of wine, leaving bottles and their count unreported. The glass quantity supplies a different entity count, and silence about bottles supplies no established zero.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 132. train_4421: number of buckets

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** A bathroom with toilet, sink with cabinet and wall mirror, and three bucket containers on the floor.

**Caption B:** A toilet and a bidet are in a beige tiled bathroom with a shower stall.

**Adopted scope:** bucket count

**Extracted A:** 3 buckets

**Extracted B:** no buckets established

**Recorded reason, verbatim:**

> The second caption does not establish any bucket count. / Second caption provides no buckets whose count is extractable.

**Audit explanation:** The requested quantity concerns buckets within the bathrooms. Caption A explicitly lists three bucket containers on the floor. Caption B lists a toilet, bidet, tiled bathroom and shower stall, leaving bucket presence and quantity unreported. These bathroom fixtures provide no bucket count, including no established absence.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 133. train_4488: presence of instrument

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S1, S3, S6.

**Caption A:** A guitar case, a backpack, and a suitcase all placed next to each other.

**Caption B:** A pile of luggage waiting to be picked up and taken to their destination.

**Adopted scope:** musical instrument presence

**Extracted A:** guitar case only; instrument unconfirmed

**Extracted B:** luggage only; instrument unconfirmed

**Recorded reason, verbatim:**

> Final blind invalid consensus: A guitar case does not establish an instrument; B supplies no instrument information. / A guitar case establishes neither its contents nor an instrument. / A guitar case does not establish an instrument inside either luggage collection.

**Audit explanation:** The feature asks whether a musical instrument is present. Caption A names a guitar case alongside a backpack and suitcase, leaving the case's contents unestablished. Caption B names a pile of luggage with unspecified contents. Establishing instrument presence would require assumptions about contents in each described collection.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 134. train_4489: presence of suitcase

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S3, S5, S6.

**Caption A:** A guitar case, a backpack, and a suitcase all placed next to each other.

**Caption B:** A pile of luggage waiting to be picked up and taken to their destination.

**Adopted scope:** suitcase presence

**Extracted A:** explicitly present

**Extracted B:** luggage present, suitcase presence unestablished

**Recorded reason, verbatim:**

> Generic luggage does not establish that a suitcase is present.

**Audit explanation:** The requested presence feature concerns a suitcase. Caption A explicitly includes a suitcase among three luggage items. Caption B describes a pile of luggage awaiting collection, leaving the particular luggage forms unstated. The current exclusion treats that broad collection description as insufficient to establish a suitcase within it.

**Policy check:** Review ordinary inference.

**Review issue:** A pile of luggage awaiting collection may support an ordinary suitcase inference. Luggage can include other bag types.

**Question for your review:** Should ordinary luggage collection context establish suitcase presence here, or must the suitcase form be stated?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 135. train_4538: color of room

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3, S6.

**Caption A:** A bedroom with polar bear wallpaper and a nightstand that has many drawers and a Smurf figurine on top.

**Caption B:** A bathroom with a white and checkered bathtub wall and white cabinets with miscellaneous items on it.

**Adopted scope:** room colors

**Extracted A:** unspecified; polar bear wallpaper gives no color

**Extracted B:** white and checkered

**Recorded reason, verbatim:**

> Wallpaper subject does not establish the first room's actual colors. / Wallpaper motif does not establish the room's actual colors.

**Audit explanation:** The comparison concerns room colors. Caption A identifies a bedroom with polar bear wallpaper, drawers and a Smurf figurine, leaving the room's actual palette unstated. Caption B supplies white cabinets and a white and checkered bathtub wall. Inferring the bedroom palette from decorative subjects would require additional visual assumptions.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 136. train_4586: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A slice of pizza on a white plate with a knife and fork laying on the plate.

**Caption B:** Food with a metal utensil under it with a cup on the side of the plate.

**Adopted scope:** food plate color

**Extracted A:** white

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption does not establish a comparable object color. / Second caption does not establish a comparable object color.

**Audit explanation:** The recorded scope selects the shared food plate as the comparable object. Caption A explicitly describes a white plate beneath pizza, a knife and a fork. Caption B mentions a plate beside a cup and beneath food with a metal utensil, leaving the plate's color unavailable under that scope.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 137. train_4587: food

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S2, S3, S4.

**Caption A:** A slice of pizza on a white plate with a knife and fork laying on the plate.

**Caption B:** Food with a metal utensil under it with a cup on the side of the plate.

**Adopted scope:** principal food type

**Extracted A:** pizza

**Extracted B:** food, identifiable dish category unavailable

**Recorded reason, verbatim:**

> B provides no recoverable food category beyond the word food.

**Audit explanation:** The entity-only condition food requests the principal food type. Caption A identifies a slice of pizza. Caption B identifies food on a plate with a utensil and a cup, leaving a dish category unstated. The current exclusion treats this broad food description as wholly unavailable type information despite its recoverable general category.

**Policy check:** Review scope or feature.

**Review issue:** The policy allows general categories compared with specific subtypes to retain partial type information. B explicitly supplies the general food category.

**Question for your review:** Should food versus pizza be treated as a general category and subtype comparison under the entity-only type rule?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 138. train_4659: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** Two kites in the air with swirly tails against a blue sky, over a green hill, and beach with people.

**Caption B:** A man standing in a grass field and flying a multi-colored kite in the sky above him.

**Adopted scope:** principal kite colors

**Extracted A:** unspecified

**Extracted B:** multicolored

**Recorded reason, verbatim:**

> First caption specifies landscape colors but no kite color.

**Audit explanation:** The principal comparable objects are the kites. Caption A describes two kites with swirly tails against a blue sky and above a green hill, leaving the kites' own colors unstated. Caption B explicitly calls its kite multicolored. The landscape colors belong to separate entities outside the adopted kite scope.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 139. train_4743: presence of flag near desk

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S1, S3.

**Caption A:** A laptop, cell phone, and mouse sit on a cluttered desk near a California flag.

**Caption B:** An office workspace with two screens, a laptop, an ergonomic keyboard and other electronics.

**Adopted scope:** flag presence near desk

**Extracted A:** California flag present

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Final blind invalid consensus: A flag is present in A; B never establishes flag presence or absence. / Flag is explicit near first desk, unspecified near second workspace. / A specifies a flag near the desk; B leaves flag presence unreported.

**Audit explanation:** The condition asks whether a flag is present near the desk. Caption A places a cluttered desk near a California flag. Caption B describes an office workspace with screens, a laptop, a keyboard and other electronics, leaving nearby flag presence unreported. Its equipment inventory establishes neither flag presence nor absence.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 140. train_4745: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A bathroom features a door with a window, a towel rack, a stack of towls and cabinets.

**Caption B:** Some white towels hanging under a white vanity next to a glass shower unit.

**Adopted scope:** principal bathroom object colors

**Extracted A:** unavailable

**Extracted B:** white towels and vanity

**Recorded reason, verbatim:**

> A supplies no comparable object colors.

**Audit explanation:** The recorded object scope concerns bathroom furnishings, particularly the shared towels and cabinetry. Caption A lists a windowed door, towel rack, towels and cabinets with their colors unstated. Caption B identifies white towels and a white vanity. A therefore supplies no comparable color for the principal bathroom objects.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 141. train_4802: time of day

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Time/event. **Policy:** S3, S6.

**Caption A:** An asian child is eating noodles with a fork with help using his own hands in the kitchen.

**Caption B:** A small child in a high chair with a large pile of food in front of them.

**Adopted scope:** time of day

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Neither caption establishes any time of day. / Neither caption supplies a time of day or direct clue.

**Audit explanation:** The requested feature is time of day. Caption A places a child eating noodles in a kitchen. Caption B places a small child in a high chair before food. These feeding scenes provide no clock time, lighting description or named meal that directly establishes a time category in either caption.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 142. train_4811: position of racket

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Spatial relation/posture. **Policy:** S1, S3, S4.

**Caption A:** The girl is wearing a red and white tennis dress and has her racquet ready to hit.

**Caption B:** A tennis player has lowered her racket to return the ball with a scoop.

**Adopted scope:** racket's spatial position

**Extracted A:** ready to hit, physical position unavailable

**Extracted B:** lowered for scoop return

**Recorded reason, verbatim:**

> Readiness does not identify the first racket's spatial position.

**Audit explanation:** The current scope asks for the racket's spatial position. Caption A says the girl has her racquet ready to hit, leaving its height and orientation unstated. Caption B explicitly places the racket lowered for a scoop return. The exclusion treats readiness as insufficient physical position information for the comparison.

**Policy check:** Review scope or feature.

**Review issue:** Ready to hit supplies a coarse racket preparation state. A broader posture reading may preserve partial feature information while the exact position remains unavailable.

**Question for your review:** Does racket position include a coarse ready-to-hit posture, or require a stated physical height or orientation?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 143. train_4823: color of t-shirt

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A girl in a pink t-shirt and white tennis shoes holds out her racket.

**Caption B:** A woman jumping up to a hit a tennis ball on a tennis court.

**Adopted scope:** T-shirt color

**Extracted A:** pink

**Extracted B:** no T-shirt established

**Recorded reason, verbatim:**

> Second caption supplies no shirt color. / Only the first supplies the color of a shirt.

**Audit explanation:** The feature specifically concerns a T-shirt's color. Caption A describes a girl wearing a pink T-shirt and white tennis shoes. Caption B describes a woman jumping to hit a tennis ball, leaving her upper clothing and its color unstated. The required T-shirt referent is therefore unestablished in B.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 144. train_4913: number of beverages

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3, S4.

**Caption A:** Bottles of booze sit in the background behind a sandwich and a bit of beets.

**Caption B:** a sandwhich cut into half with olives and  a pickel sitting on a plate

**Adopted scope:** beverage count

**Extracted A:** plural bottles of booze; exact count unknown

**Extracted B:** no beverages established

**Recorded reason, verbatim:**

> Second caption supplies no beverage count or explicit absence. / Second caption gives no beverage count or explicit absence.

**Audit explanation:** The requested quantity is the number of beverages. Caption A establishes plural bottles of booze behind a sandwich, supplying coarse beverage quantity. Caption B describes a sandwich, olives and a pickle on a plate, leaving beverages and their number unreported. The exclusion concerns B's missing beverage information, with A's imprecise plural count remaining recoverable.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 145. train_4923: object child is holding

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S3, S6.

**Caption A:** A young child looks at the camera as he holds a tennis racket on the court.

**Caption B:** The boy have brought several tennis balls with him to to tennis court in order to practice  his serve.

**Adopted scope:** object held by child

**Extracted A:** tennis racket

**Extracted B:** tennis balls brought; current held object unspecified

**Recorded reason, verbatim:**

> Bringing tennis balls does not establish the object currently held.

**Audit explanation:** The condition selects the object the child currently holds. Caption A explicitly places a tennis racket in the child's hands. Caption B says the boy brought several tennis balls to practice serving, leaving his present hand contents unstated. Bringing equipment establishes possession or transport while the requested holding relation remains unavailable.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 146. train_4978: color of scissors

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3, S5.

**Caption A:** A man holding a large pair of red scissors in front of a crowd.

**Caption B:** A large group of business men about the cut the ribbon at a grand opening.

**Adopted scope:** ceremonial scissors color

**Extracted A:** red

**Extracted B:** unspecified; scissors inferred from ribbon cutting

**Recorded reason, verbatim:**

> Second caption does not establish any scissors color. / Red is given only first; second gives no scissor color.

**Audit explanation:** The requested feature is scissors color. Caption A explicitly gives the large scissors a red color. Caption B describes business men preparing to cut a ribbon at a grand opening. That activity can support ordinary ceremonial scissors inference, while supplying no color for the inferred scissors, leaving the requested comparison unavailable.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 147. train_4988: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A street with a lot of traffic next to a sidewalk filled with people on a rainy day.

**Caption B:** A red fire hydrant sits at the end of a row of cars parked on a street.

**Adopted scope:** principal scene-object colors

**Extracted A:** traffic vehicles; colors unspecified

**Extracted B:** red fire hydrant

**Recorded reason, verbatim:**

> The first caption supplies no object color information. / First caption provides no comparable object color.

**Audit explanation:** The recorded scope concerns principal street object colors, with traffic vehicles in A and a fire hydrant in B. Caption A describes traffic, people, a sidewalk and rain without assigning an object color. Caption B explicitly identifies a red fire hydrant. A therefore lacks the color information needed for its adopted referent.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 148. train_5027: number of frames

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** a white bathroom with a tub, a sink and wood framed picture under the sink mirror

**Caption B:** A bathrobe with a curtain covered bathtub next to a sink and a toilet.

**Adopted scope:** picture frame count

**Extracted A:** 1 wood picture frame

**Extracted B:** no frames established

**Recorded reason, verbatim:**

> The second caption does not establish any picture-frame count. / Second caption supplies no frames whose count can be extracted.

**Audit explanation:** The quantity condition counts picture frames. Caption A establishes one wood framed picture beneath a mirror in a bathroom. Caption B describes a bathrobe, curtain covered bathtub, sink and toilet, leaving picture frames and their quantity unreported. Its bathroom inventory supplies no frame count or established absence of frames.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 149. train_5054: color of animal

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** White and brown goats in a pen looking at a white, brown and black dog.

**Caption B:** Two adult horses stand on either side of a young colt in a field.

**Adopted scope:** principal animal colors

**Extracted A:** white and brown goats; dog also black

**Extracted B:** horse colors unspecified

**Recorded reason, verbatim:**

> Second caption establishes no animal color information. / Second caption gives no animal color for comparison.

**Audit explanation:** The requested feature is animal color. Caption A supplies white and brown for its goats and white, brown and black for the dog they face. Caption B describes two adult horses and a young colt in a field with their colors unstated. Choosing among A's animals leaves the same missing color information in B.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 150. train_5171: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A toilet is built into a larger seat with two rolls of toilet paper on it.

**Caption B:** A white toilet with a small sink behind it in a very small space.

**Adopted scope:** principal toilet color

**Extracted A:** unspecified

**Extracted B:** white

**Recorded reason, verbatim:**

> The first caption supplies no toilet color information. / First caption provides no comparable object color.

**Audit explanation:** The principal shared object is the toilet, and the condition requests its color. Caption A describes a toilet built into a larger seat with two paper rolls, leaving toilet color unstated. Caption B explicitly describes a white toilet beside a small sink. Construction details in A provide no recoverable toilet color.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 151. train_5251: number of people

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3, S4.

**Caption A:** A walkway between to building made to look like a train car on railroad tracks.

**Caption B:** A bunch of train box cars on a track and people are walking on the sidewalk.

**Adopted scope:** all people count

**Extracted A:** no people established

**Extracted B:** plural walking people

**Recorded reason, verbatim:**

> First caption supplies no reliable people count. / First caption establishes no people count or explicit absence.

**Audit explanation:** The condition counts people. Caption A describes a walkway between buildings styled like a train car on tracks, leaving any people unreported. Caption B explicitly describes plural people walking beside train box cars. B supplies coarse quantity information, while the walkway in A establishes neither a people count nor an absence of people.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 152. train_5292: height of man

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Spatial relation/posture. **Policy:** S1, S3, S4.

**Caption A:** A man performing a skate board trick in front of various people in wooden chairs and another man holding a skateboard.

**Caption B:** A skate boarder in the air, mid jump, as his board is flipped upside down.

**Adopted scope:** principal man physical height

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Neither caption establishes the man's physical height or comparable elevation. / Neither caption establishes the man's stature or exact elevation.

**Audit explanation:** The current recorded scope interprets height as the principal man's physical stature. Caption A describes a man performing a skateboard trick before seated people. Caption B places a skateboarder in the air, mid jump. Each leaves stature unstated, while B separately supplies coarse elevation information relevant to another possible height reading.

**Policy check:** Check recorded rationale.

**Review issue:** The recorded rationale says comparable elevation is unavailable in both captions. B explicitly places the skateboarder in the air, mid jump.

**Question for your review:** Should height retain the recorded stature scope, with the elevation claim corrected, or refer to elevation during the trick?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 153. train_5331: number of animals

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** An open blue suitcase sits next to a wastebasket and a plastic bag filled with clothing.

**Caption B:** One cat is sitting in a suitcase and the the other cat is on the bed.

**Adopted scope:** all animal count

**Extracted A:** no animals established

**Extracted B:** 2 cats

**Recorded reason, verbatim:**

> The first caption provides no established animal count. / First caption provides no animals whose count is extractable.

**Audit explanation:** The feature counts all animals. Caption A describes an open blue suitcase beside a wastebasket and a clothing bag, leaving animals unreported. Caption B identifies one cat in a suitcase and another on the bed, establishing two animals. A's object inventory supplies no animal quantity or established zero for comparison.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 154. train_5351: number of people

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3, S6.

**Caption A:** A truck driving through and intersection waiting on a pedestrian to finish crossing the street.

**Caption B:** A very busy city street with a multitude of streetlights and buildings in the background.

**Adopted scope:** all people count

**Extracted A:** 1 pedestrian

**Extracted B:** no people established

**Recorded reason, verbatim:**

> Busy street does not establish any pedestrian count. / Second caption supplies no people count or established absence.

**Audit explanation:** The requested feature counts people. Caption A explicitly describes one pedestrian crossing before a truck. Caption B describes a very busy city street with streetlights and buildings, leaving people unreported. Busy can describe traffic or general activity and supplies no direct human quantity, so B lacks a recoverable people count.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 155. train_5388: color of train

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A train on tracks with gravel, and trees, grass and telephone wires and two workers in background.

**Caption B:** A white and yellow train and a red and yellow train hooked to each other on a track.

**Adopted scope:** train colors

**Extracted A:** unspecified

**Extracted B:** white/yellow and red/yellow

**Recorded reason, verbatim:**

> The first caption supplies no train color information. / First caption does not provide a train color.

**Audit explanation:** The condition requests train colors. Caption A places a train on tracks among gravel, trees, grass, wires and workers, leaving the train's appearance uncolored. Caption B explicitly describes a white and yellow train linked to a red and yellow train. A's surrounding scenery supplies no color for its train.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 156. train_5464: color of vehicle

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** Cars driving on the street and people walking on the sidewalk in a city.

**Caption B:** On a gray and rainy day a black car drives down a city street.

**Adopted scope:** cars' color

**Extracted A:** unspecified

**Extracted B:** black

**Recorded reason, verbatim:**

> First caption supplies no vehicle color. / Only the second supplies any vehicle color information.

**Audit explanation:** The principal comparable vehicles are the cars. Caption A describes cars driving through a city while people walk on a sidewalk, leaving all car colors unstated. Caption B explicitly describes a black car on a gray rainy day. B's black vehicle color has no recoverable vehicle color counterpart in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 157. train_5581: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** The snowboarder flew through the air while the sun sets on the horizon .

**Caption B:** A snowboarder is sliding along , balanced on a yellow beam .

**Adopted scope:** principal snowboard color

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> First caption establishes no relevant object color. / First caption supplies no object color for comparison.

**Audit explanation:** The current recorded object scope selects the snowboard associated with each snowboarder. Caption A describes airborne snowboarding at sunset, leaving the board's color unstated. Caption B describes balancing along a yellow beam, also leaving board color unstated. Yellow belongs to the beam, a separate object outside the adopted snowboard scope.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 158. train_5735: dog's level of training

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Other. **Policy:** S3, S6.

**Caption A:** A black and white dog running from under a yellow cover with a person behind them .

**Caption B:** A small dog with a ball in its mouth running through a course .

**Adopted scope:** dog training level

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Running under cover or through courses establishes no training level. / Neither description establishes a specific level of dog training.

**Audit explanation:** The requested feature is the dog's training level. Caption A describes a dog running from beneath a cover with a person behind it. Caption B describes a dog carrying a ball through a course. These actions establish behavior and setting while leaving any training stage or comparative proficiency category unestablished.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 159. train_5771: number of toys

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** Two large dogs are playing in a large grassy area .

**Caption B:** a black and a white dog play with a rope toy in a backyard

**Adopted scope:** number of toys

**Extracted A:** no toy entity mentioned

**Extracted B:** one rope toy

**Recorded reason, verbatim:**

> The first caption does not establish a toy count. / First caption establishes playing but no toy count.

**Audit explanation:** The condition counts toys used by the dogs. Caption A establishes two dogs playing in grass, leaving toys and their quantity unreported. Caption B explicitly describes a rope toy used by two dogs, supplying one toy. Playing alone supplies no toy count or established absence for A's scene.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 160. train_5787: skill level of subject

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Other. **Policy:** S1, S3, S4, S5, S6.

**Caption A:** a surfer is riding the waves whilst another surfer sits on his board waiting .

**Caption B:** A boy in red shorts rides a yellow bodyboard on a breaking wave .

**Adopted scope:** subject's skill level

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Neither caption directly establishes the participants' level of skill. / Wave riding alone does not establish comparative skill levels.

**Audit explanation:** The requested feature is the active subject's skill level. Caption A describes a surfer riding waves while another waits. Caption B describes a boy riding a bodyboard on a breaking wave. The current exclusion treats these demonstrated activities as insufficient to establish skill categories, even though each supplies evidence of basic wave riding ability.

**Policy check:** Review ordinary inference.

**Review issue:** Successfully riding waves in both captions may support a coarse ability inference. The excluded rationale assumes a more specific proficiency scale than the condition states.

**Question for your review:** Can demonstrated wave riding supply coarse skill information here, or must skill level explicitly distinguish proficiency categories?

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 161. train_5793: positions players are playing

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S3.

**Caption A:** A batter swinging at a pitch with a catcher preparing to receive the pitch .

**Caption B:** Two baseball players on a field , with four spectators , and a crowd .

**Adopted scope:** players' positions

**Extracted A:** batter and catcher

**Extracted B:** two unspecified baseball positions

**Recorded reason, verbatim:**

> Second caption establishes no baseball player positions. / Second caption identifies players without stating their fielding roles.

**Audit explanation:** The requested feature concerns the baseball roles played by the players. Caption A explicitly identifies a batter swinging and a catcher preparing to receive. Caption B identifies two baseball players alongside spectators and a crowd, leaving their roles unstated. Spectator and crowd counts supply no positional role information for those players.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 162. train_5802: color of animal

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A little boy is playing with his dog in the backyard as the snow melts .

**Caption B:** A brown dog carrying a Frisbee runs through the snow .

**Adopted scope:** dog coat color

**Extracted A:** unspecified

**Extracted B:** brown

**Recorded reason, verbatim:**

> First caption supplies no animal color information. / Only the second supplies the dogs fur color.

**Audit explanation:** The principal animal in each caption is the dog, and the feature concerns coat color. Caption A describes a boy playing with his dog while snow melts, leaving the dog's color unstated. Caption B explicitly describes a brown dog carrying a Frisbee. Snow in A provides environmental information outside the dog's color scope.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 163. train_5859: color of dog

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** Long-haired dog moves quickly beneath two poles .

**Caption B:** A brown dog with a blue bandanna is jumping over grass .

**Adopted scope:** dog coat color

**Extracted A:** unspecified

**Extracted B:** brown

**Recorded reason, verbatim:**

> Long hair provides no information about coat color. / Only the second supplies the dogs fur color.

**Audit explanation:** The condition specifically requests dog color. Caption A describes a long-haired dog moving beneath poles, establishing coat length while leaving its color unstated. Caption B explicitly describes a brown dog wearing a blue bandanna. Brown supplies B's coat color, while the bandanna color and A's coat length concern separate appearance features.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 164. train_5863: proximity to water

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Spatial relation/posture. **Policy:** S1, S3.

**Caption A:** A person on a bike rides through a dirt course near the water .

**Caption B:** One biker wearing a black helmet riding on a dirt hill .

**Adopted scope:** distance to water

**Extracted A:** near water

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption supplies no information about nearby water. / Second caption provides no water proximity information.

**Audit explanation:** The requested spatial relation is the rider's proximity to water. Caption A explicitly places a person biking through a dirt course near water. Caption B describes a helmeted biker on a dirt hill, leaving water and its distance unreported. A dirt hill alone supplies no water proximity value or established separation from water.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 165. train_5911: dog's mouth contents

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Composition/contents. **Policy:** S1, S3.

**Caption A:** A male weimaraner with a clipped tail is walking through a river .

**Caption B:** A white dog treads the water with sticks in its mouth .

**Adopted scope:** dog's mouth contents

**Extracted A:** unspecified

**Extracted B:** sticks

**Recorded reason, verbatim:**

> The first caption supplies no information about mouth contents. / First caption does not establish the dog's mouth contents.

**Audit explanation:** The feature concerns the dog's mouth contents. Caption A identifies a male weimaraner with a clipped tail walking through a river, leaving its mouth contents unreported. Caption B explicitly places sticks in a white dog's mouth while it treads water. A's breed, tail and river information supplies neither contents nor an empty-mouth value.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 166. train_5933: type of surface

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S3, S4, S5.

**Caption A:** A man in white playing tennis is still in midair after jumping to hit the ball .

**Caption B:** A male tennis player prepares a left-handed forehand while playing on clay .

**Adopted scope:** tennis playing surface

**Extracted A:** unspecified

**Extracted B:** clay

**Recorded reason, verbatim:**

> The first caption does not identify the playing surface. / First caption does not identify the court surface.

**Audit explanation:** The current scope requests the tennis playing surface. Caption A describes a man airborne after jumping to hit a tennis ball, leaving court material unstated. Caption B explicitly places a tennis player on clay. The exclusion treats A's general tennis setting as insufficient surface type information. It supports an ordinary court inference.

**Policy check:** Review ordinary inference.

**Review issue:** Tennis ordinarily supplies a court setting. A coarse court surface category compared with clay may retain partial information if surface type permits that abstraction level.

**Question for your review:** Does an inferred tennis court supply sufficient coarse surface information alongside clay, or does this feature require a surface material?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 167. train_6025: name of dog

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S3, S6.

**Caption A:** A harnessed dog leaps over a log as another dog follows behind .

**Caption B:** a dog jumps over another dog as both animals are trying to catch the same ball .

**Adopted scope:** dog's proper name

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Neither caption provides a personal name for the dog. / Neither caption supplies an individual name or specific dog identity.

**Audit explanation:** The feature requests a dog's personal name. Caption A describes a harnessed dog leaping over a log with another following. Caption B describes one dog jumping over another as both pursue a ball. These role and action descriptions identify scene participants while supplying no proper name for any dog in either caption.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 168. train_6383: color of animal

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A dog jumps a man 's leg to take a Frisbee from his hand .

**Caption B:** A fast black and white dog is running to catch a red Frisbee .

**Adopted scope:** dog coat color

**Extracted A:** unspecified

**Extracted B:** black and white

**Recorded reason, verbatim:**

> The first caption supplies no information about dog color. / First caption does not give the dog's color.

**Audit explanation:** The requested feature is the dog's coat color. Caption A describes a dog jumping a man's leg to take a Frisbee from his hand, leaving the dog's appearance uncolored. Caption B explicitly describes a black and white dog pursuing a red Frisbee. The Frisbee's red color belongs to a separate object.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 169. train_6391: sentiment of people

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Emotion/sentiment. **Policy:** S1, S3, S6.

**Caption A:** Man kicking another man in the face in a karate competition .

**Caption B:** During a martial arts match , a man attempts to kick the other in the face .

**Adopted scope:** people's emotional sentiment

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Attempted sporting kicks do not directly establish emotional sentiment. / Fighting actions alone do not establish emotional sentiment.

**Audit explanation:** The condition asks for the participants' emotional sentiment. Caption A describes a face kick in a karate competition. Caption B describes an attempted face kick during a martial arts match. Each establishes a sporting action, leaving emotions unexpressed. Assigning anger, enjoyment or another sentiment from those competitive actions would require additional assumptions.

**Policy check:** Policy consistent.

**History:** supplied source rating 5; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 170. train_6553: location of action

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Location/scene. **Policy:** S1, S3, S4, S5.

**Caption A:** A young boy jumping into a pool that says " no diving " .

**Caption B:** One teenager taking a risk by diving on his side .

**Adopted scope:** water-entry location

**Extracted A:** swimming pool

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Second gives diving action without establishing a location or waterbody.

**Audit explanation:** The recorded scope concerns the water-entry location. Caption A explicitly places a boy jumping into a pool marked no diving. Caption B describes a teenager taking a risk by diving on his side, leaving the waterbody unnamed. The exclusion treats B's activity description as insufficient location information despite a possible ordinary water-entry inference.

**Policy check:** Review ordinary inference.

**Review issue:** Diving on one's side can ordinarily suggest entry into water, potentially supplying a coarser setting than A's named pool. A specific pool remains unestablished in B.

**Question for your review:** May diving supply a coarse water setting for this location comparison, or must the waterbody be identified?

**History:** supplied source rating 4; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 171. train_6589: color of dress

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A little girl in a white sundress smiles and slides down a blue slide .

**Caption B:** A little girl makes a goofy face and does a half push up in the grass .

**Adopted scope:** specified dress color

**Extracted A:** white sundress

**Extracted B:** no dress described

**Recorded reason, verbatim:**

> Second caption supplies no dress color information. / Second caption supplies no dress or dress color information.

**Audit explanation:** The requested feature specifically concerns a dress's color. Caption A explicitly describes a little girl wearing a white sundress while using a blue slide. Caption B describes a girl making a face and doing a half push up in grass, leaving clothing unstated. Its required dress referent and dress color remain unestablished.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 172. train_6613: breed of animal

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S3, S6.

**Caption A:** A gray dog is jumping toward a black and white dog in the snow .

**Caption B:** A brown dog carrying a Frisbee runs through the snow .

**Adopted scope:** dog breed

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Neither caption establishes a dog's breed. / Neither caption establishes a specific breed of dog.

**Audit explanation:** The condition requests animal breed within dog scenes. Caption A describes a gray dog jumping toward a black and white dog in snow. Caption B describes a brown dog carrying a Frisbee through snow. Both establish species and coat colors while leaving breeds unreported, and those colors alone establish no particular breed.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 173. train_6636: temperament of dogs

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Emotion/sentiment. **Policy:** S3, S6.

**Caption A:** A brown and white dog is running across the grass .

**Caption B:** Two dogs run along a grassy field while one bites the other .

**Adopted scope:** dogs' temperament

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Running and biting do not establish comparable temperaments. / First running action does not establish the dogs temperament.

**Audit explanation:** The requested feature is the dogs' temperament. A describes a brown and white dog running across grass; B describes two running dogs with one biting the other. These actions leave enduring dispositions unspecified in both captions, and biting can accompany several temperaments or interactions.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 174. train_6661: absence of umbrella

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S3.

**Caption A:** A lady walks in the rain with a yellow umbrella .

**Caption B:** Woman walking in the rain and unicycle standing next to a pole .

**Adopted scope:** umbrella absence

**Extracted A:** false, umbrella present

**Extracted B:** unknown

**Recorded reason, verbatim:**

> Final blind invalid consensus: A disproves umbrella absence; B never establishes whether an umbrella is absent. / Umbrella present first; second does not establish umbrella absence. / A explicitly includes an umbrella; B does not establish umbrella absence.

**Audit explanation:** The condition concerns umbrella absence. A establishes an umbrella through the lady's yellow umbrella in the rain. B describes a woman walking in rain beside a unicycle and pole, leaving umbrella possession unreported. The current exclusion follows the unavailable presence or absence value in B.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 175. train_6751: color of dogs

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** a dog jumps over another dog as both animals are trying to catch the same ball .

**Caption B:** A brown dog in a pink shirt chews something white while a brown dog in yellow watches .

**Adopted scope:** dog coat colors

**Extracted A:** unspecified

**Extracted B:** brown

**Recorded reason, verbatim:**

> The first caption supplies no dog color information. / First caption provides no animal colors to compare.

**Audit explanation:** The comparable feature is the dogs' coat color. A identifies two dogs jumping and pursuing the same ball while leaving their coats undescribed. B calls both dogs brown and separately describes pink and yellow clothing. The current exclusion follows the wholly unavailable coat color in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 176. train_6770: action of girl

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Action/activity. **Policy:** S1, S3, S4.

**Caption A:** A little girl in a pink shirt and a little girl in an orange shirt sitting in the grass .

**Caption B:** This young girl is enjoying the innocence of childhood and warm weather .

**Adopted scope:** girl's physical action

**Extracted A:** sitting in grass

**Extracted B:** enjoying weather; bodily action unspecified

**Recorded reason, verbatim:**

> Enjoying weather supplies no recoverable physical action to compare with sitting.

**Audit explanation:** The recorded scope limits the requested action to the girls' physical activity. A explicitly describes sitting in grass; B describes a young girl enjoying childhood and warm weather without describing a bodily action. This exclusion depends on treating enjoyment as insufficient activity information under that narrower scope.

**Policy check:** Review scope or feature.

**Review issue:** The condition says action of girl; B supplies enjoying childhood and weather, which may count as a described activity under a broader action reading.

**Question for your review:** Should action include the stated activity of enjoying the weather, or require an observable bodily action?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 177. train_6975: material of ground

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Composition/contents. **Policy:** S1, S3, S6.

**Caption A:** Asian kids sitting on a mat playing with a toy .

**Caption B:** Several children sitting on the floor in a metal building .

**Adopted scope:** material of supporting ground surface

**Extracted A:** mat material unspecified

**Extracted B:** floor material unspecified

**Recorded reason, verbatim:**

> Metal building does not establish floor material. / Neither caption establishes the material composing the ground surface.

**Audit explanation:** The requested feature is the material composing the children's supporting surface. A places children on a mat without identifying its fabric or substance. B places children on a floor inside a metal building; metal describes the building, leaving the floor's material unavailable as well.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 178. train_6993: location description

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Location/scene. **Policy:** S3.

**Caption A:** A large brown dog is running through a grassy backyard .

**Caption B:** A brown greyhound is wearing a blue muzzle and blue collar .

**Adopted scope:** dog's location

**Extracted A:** grassy backyard

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Muzzle and collar do not establish location. / Only the first supplies the dogs location description.

**Audit explanation:** The requested location belongs to the principal dog. A supplies a grassy backyard as the running dog's setting. B identifies a brown greyhound wearing a blue muzzle and collar, giving appearance and equipment information while leaving the surrounding place unspecified. The current exclusion follows B's unavailable location description.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 179. train_7063: competitiveness level of persons

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Other. **Policy:** S3, S6.

**Caption A:** Several bicyclists wearing helmets ride by to the right .

**Caption B:** A group of cyclists riding their bikes in a marathon .

**Adopted scope:** participants' competitiveness level

**Extracted A:** unspecified

**Extracted B:** competitive marathon

**Recorded reason, verbatim:**

> First riders' competitive status is not established. / First caption supplies no competitive context or athlete level.

**Audit explanation:** The requested feature is the cyclists' competitiveness level. A describes helmeted bicyclists riding to the right without a competitive event or performance level. B places cyclists in a marathon, providing competitive context. The current exclusion rests on the absence of comparable competitiveness information for A's riders.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 180. train_7141: object travelled past

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Spatial relation/posture. **Policy:** S1, S3.

**Caption A:** A group of people are running through a street .

**Caption B:** Marathon runners are running past a glass building .

**Adopted scope:** object passed by runners

**Extracted A:** no passed object described

**Extracted B:** glass building

**Recorded reason, verbatim:**

> The first caption does not identify an object traveled past. / First caption describes the route but no object traveled past.

**Audit explanation:** The condition requests an object the runners travel past. A supplies a street as the route through which a group runs, leaving any passed landmark unidentified. B explicitly supplies a glass building as the object marathon runners pass. The current exclusion follows the missing passed object in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 181. train_7143: presence of tye-dye t-shirt

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S3.

**Caption A:** Man in a colorful tye-dye t-shirt doing a trick on his skateboard .

**Caption B:** A young man is doing a skating trip on a skateboard ramp .

**Adopted scope:** tie-dye shirt presence

**Extracted A:** present

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Final blind invalid consensus: Tie-dye clothing is explicit in A but neither confirmed nor denied in B. / Tie-dye shirt is present first; second leaves clothing pattern unknown. / A specifies the shirt; B leaves clothing pattern unreported.

**Audit explanation:** The requested feature is presence of a tie dye shirt. A explicitly describes the skateboarder's colorful tye-dye t-shirt. B describes a young man performing on a skateboard ramp with his clothing unreported. B therefore leaves the requested shirt's presence or absence unavailable for comparison.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 182. train_7260: profession of person

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S3, S6.

**Caption A:** a person doing the backstroke in a swimming pool

**Caption B:** A professional swimmer racing to the finish line .

**Adopted scope:** person's profession

**Extracted A:** unspecified

**Extracted B:** professional swimmer

**Recorded reason, verbatim:**

> Swimming alone does not establish a professional occupation. / Swimming activity alone does not establish the first persons profession.

**Audit explanation:** The requested feature is the person's profession. A describes someone performing the backstroke in a swimming pool, an activity compatible with many occupations. B explicitly calls its swimmer professional. The current exclusion follows the unavailable occupation in A, since participation in swimming supplies an activity alone.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 183. train_7271: movement of people

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Action/activity. **Policy:** S1, S3.

**Caption A:** two people are nearing the top of an escalator .

**Caption B:** Several people look down from above the first floor .

**Adopted scope:** people bodily locomotion

**Extracted A:** ascending toward escalator top

**Extracted B:** looking down; locomotion unspecified

**Recorded reason, verbatim:**

> Gaze direction supplies no locomotion value for the second people.

**Audit explanation:** The recorded feature is bodily locomotion of the people. A describes two people nearing the top of an escalator, supplying upward progression. B describes several people looking down from above the first floor, supplying gaze direction and position while leaving their locomotion unspecified. The current exclusion uses that missing movement value.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status agreement, rating 2. Current decision pathway: focused_semantic_adjudication.

### 184. train_7313: presence of trees

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S3.

**Caption A:** A man on a bicycle jumps over jagged rocks amongst tall pine trees .

**Caption B:** a guy on a bike jumping from one large rock to another

**Adopted scope:** tree presence

**Extracted A:** present

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Final blind invalid consensus: A explicitly contains pine trees; B never establishes trees or their absence. / Pine trees present first; second does not establish trees absence. / A explicitly includes pine trees; B supplies no tree presence information.

**Audit explanation:** The condition requests tree presence. A explicitly places the jumping cyclist among tall pine trees and jagged rocks. B describes a cyclist jumping between large rocks with the surrounding vegetation unreported. The current exclusion follows B's unavailable tree presence value; rocks alone leave room for several surrounding settings.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 185. train_7423: absence of hard hats

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S3, S6.

**Caption A:** Workers are wearing hard hats at a construction site while building something with wood .

**Caption B:** Construction workers hammer nails on the unfinished roof of a house .

**Adopted scope:** hard-hat absence

**Extracted A:** false, hard hats present

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Final blind invalid consensus: A disproves hard-hat absence; B gives no headwear information. / First workers wear hard hats; second workers headwear is unspecified. / A explicitly includes hard hats; B does not establish their absence.

**Audit explanation:** The feature is absence of hard hats among the construction workers. A explicitly describes workers wearing hard hats while building with wood. B describes roof workers hammering nails, leaving headwear unreported. The current exclusion follows the unknown absence value in B, since construction work alone leaves actual equipment uncertain.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 186. train_7466: absence of snowshoes

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S3.

**Caption A:** A young boy and his father use snowshoes to walk in the snow .

**Caption B:** Two kids play a game together with sticks in the snow .

**Adopted scope:** snowshoe absence for participants

**Extracted A:** false: snowshoes used

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Final blind invalid consensus: A disproves snowshoe absence; B gives no snowshoe information. / First snowshoes are present; second children footwear is unspecified. / A explicitly includes snowshoes; B does not establish their absence.

**Audit explanation:** The requested feature is snowshoe absence for the participants. A explicitly states that a boy and his father use snowshoes while walking in snow. B describes two children playing with sticks in snow and leaves footwear unspecified. The current exclusion follows the unavailable snowshoe presence or absence value in B.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 187. train_7543: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A man in a green jacket and brown pants is pictured in midair on a snowboard .

**Caption B:** A young snowboarder catches some air on his black snowboard .

**Adopted scope:** principal snowboard color

**Extracted A:** unspecified

**Extracted B:** black

**Recorded reason, verbatim:**

> Shared snowboard color is unstated first; clothing colors cannot substitute.

**Audit explanation:** The adopted comparable object is the snowboard in each caption. A describes its rider's green jacket and brown pants while leaving the board's color unspecified. B explicitly calls the snowboard black. The current exclusion follows A's missing snowboard color, with the rider's clothing colors belonging to a separate referent.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 188. train_7559: color of uniform

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S3.

**Caption A:** a baseball player jumps against the fence to make a catch

**Caption B:** A baseball player in a white and red uniform is sliding to base .

**Adopted scope:** baseball player's uniform color

**Extracted A:** unspecified

**Extracted B:** white and red

**Recorded reason, verbatim:**

> First caption does not establish any uniform color. / Only the second specifies any uniform color.

**Audit explanation:** The requested feature is the baseball player's uniform color. A describes a player jumping against a fence to catch a ball without describing uniform colors. B supplies a white and red uniform for a player sliding to base. The current exclusion follows the unavailable clothing color in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 189. train_7607: speed of cyclists

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Other. **Policy:** S3, S5, S6.

**Caption A:** A group of mountain bikers race each other down a dirt hill .

**Caption B:** Two people ride bicycles over a bumpy racetrack .

**Adopted scope:** cyclists' speed

**Extracted A:** racing speed

**Extracted B:** unspecified riding speed

**Recorded reason, verbatim:**

> Racing and riding alone do not establish comparable cycling speeds. / Race participation alone does not establish comparable cyclist speeds.

**Audit explanation:** The feature is cycling speed. A describes mountain bikers racing downhill, supplying a racing context. B describes two people riding over a bumpy racetrack without expressing pace. The current exclusion treats that riding context as insufficient speed information. Ordinary track riding may suggest a coarse pace for review.

**Policy check:** Review ordinary inference.

**Review issue:** Both captions supply sporting cycling contexts; downhill racing in A and a bumpy racetrack in B may support coarse speed information despite unavailable exact pace.

**Question for your review:** Does riding on the bumpy racetrack provide an ordinary coarse speed inference under the permitted context rule?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 190. train_7833: type of construction work

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S3, S4, S5.

**Caption A:** The construction worker noticed the crooked board .

**Caption B:** Two construction workers are bent over and straddling a metal I-beam .

**Adopted scope:** construction task type

**Extracted A:** unspecified: noticing board

**Extracted B:** unspecified: straddling I-beam

**Recorded reason, verbatim:**

> Neither caption clearly establishes a comparable construction-work subtype. / Neither identifies a specific construction work discipline reliably.

**Audit explanation:** The recorded feature is a construction task subtype. A describes a worker noticing a crooked board, and B describes workers bent over while straddling a metal I-beam. The exclusion treats both tasks as unavailable. Their board and beam references supply coarse material or structural context for a possible broader work-type reading.

**Policy check:** Review scope or feature.

**Review issue:** Board work and a metal I-beam may support coarse construction categories; the recorded rationale requires a specific discipline despite the policy permitting partial type information.

**Question for your review:** Should type of construction work include coarse wood or structural metal work, or require an identified task?

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 191. train_7856: intent to injure

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Purpose/function. **Policy:** S3, S6.

**Caption A:** Two men kickbox in a ring , one man punching the other .

**Caption B:** A boxer in red lands a glancing blow off of a boxer in white .

**Adopted scope:** fighters' intent to injure

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Combat sport participation does not establish an intent to injure. / Competitive strikes do not establish an intent to injure.

**Audit explanation:** The requested feature is intent to injure. A describes kickboxers punching in a ring; B describes one boxer landing a glancing blow on another. Both captions identify sporting strikes while leaving the participants' injurious intent unexpressed. The current exclusion avoids assigning a psychological intention from participation in combat sports.

**Policy check:** Policy consistent.

**History:** supplied source rating 5; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 192. train_7861: type of animals

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S2, S3, S4, S6.

**Caption A:** a small black and white jumping to catch something in its mouth .

**Caption B:** A dog flies through the air , preparing to catch a ball .

**Adopted scope:** principal animal type

**Extracted A:** animal noun omitted; type unavailable

**Extracted B:** dog

**Recorded reason, verbatim:**

> Malformed first caption does not reliably identify animal type. / First caption omits an animal noun; species cannot be established.

**Audit explanation:** The requested feature is animal type. A describes something small, black and white jumping to catch something in its mouth, with the animal noun omitted. B explicitly identifies a dog catching a ball. The recorded exclusion requires an identified species, leaving the recoverability of a broader animal category open to review.

**Policy check:** Review scope or feature.

**Review issue:** Jumping and catching something in its mouth support an animate referent in A; the type policy allows a general category compared with a specific subtype.

**Question for your review:** Is a coarse animal category recoverable from A's malformed description for the established type comparison?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 193. train_7872: place of action

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Location/scene. **Policy:** S3, S6.

**Caption A:** Many people wearing numbers , hats and jackets are running in a race .

**Caption B:** Runners , some in costume , in a St Paddy 's day Marathon run in the streets as people watch .

**Adopted scope:** race location

**Extracted A:** unspecified

**Extracted B:** streets

**Recorded reason, verbatim:**

> The first caption does not identify where the race occurs. / First caption does not establish the place of racing.

**Audit explanation:** The condition requests the place where the running occurs. A describes numbered runners wearing hats and jackets in a race, giving event and attire information without a location. B explicitly places a St Paddy's Day marathon in streets. The current exclusion follows A's unavailable race setting.

**Policy check:** Policy consistent.

**History:** supplied source rating 4; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 194. train_7892: type of construction work

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S3.

**Caption A:** A worker in safety clothes is standing up on the wooded edge of the construction .

**Caption B:** 8 construction workers high up in the air putting up scaffolding .

**Adopted scope:** construction task type

**Extracted A:** unspecified standing at edge

**Extracted B:** erecting scaffolding

**Recorded reason, verbatim:**

> Standing at construction does not establish a specific construction task. / First does not identify a particular construction task.

**Audit explanation:** The requested feature is the type of construction task. A places a worker in safety clothing standing on a construction edge, leaving the task unidentified. B explicitly describes workers putting up scaffolding. The current exclusion follows the absence of a construction activity subtype for A's standing worker.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 195. train_7921: color of animal

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A dog catches a flying disk in a yard with a tree .

**Caption B:** A black dog standing in a field is holding a bird in his mouth .

**Adopted scope:** principal dog's coat color

**Extracted A:** unspecified

**Extracted B:** black

**Recorded reason, verbatim:**

> First caption supplies no animal color information. / Only the second supplies the dogs fur color.

**Audit explanation:** The principal comparable animal is the dog in each caption. A describes a dog catching a flying disk in a yard with a tree, leaving its coat color unreported. B explicitly calls its dog black. The current exclusion follows the unavailable coat color for A's dog.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 196. train_7963: motion of animal

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Action/activity. **Policy:** S1, S3.

**Caption A:** A dog is in some water with a tree branch in its mouth .

**Caption B:** A dog drags a white rag through an almost-dried up creek .

**Adopted scope:** principal dog's motion

**Extracted A:** unspecified while in water

**Extracted B:** moving while dragging rag

**Recorded reason, verbatim:**

> Being in water holding a branch does not establish locomotion.

**Audit explanation:** The condition concerns the dog's motion. A places a dog in water with a branch in its mouth, supplying location and possession while leaving movement unspecified. B describes a dog dragging a rag through a creek, supplying movement. The current exclusion follows the unavailable motion value in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 197. train_7975: position of arms

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Spatial relation/posture. **Policy:** S3, S6.

**Caption A:** Kayak rider raises arms as he 's splashed with water .

**Caption B:** A person white-water rafting in turbulent water .

**Adopted scope:** principal person's arm position

**Extracted A:** raised

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption does not establish the person's arm position. / Second caption does not describe the person's arms.

**Audit explanation:** The requested feature is the person's arm position. A explicitly describes a kayak rider raising his arms while water splashes him. B describes white water rafting in turbulent water without any arm description. The current exclusion follows B's unavailable arm position, since rafting allows several arm postures.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 198. train_8052: attire of person

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A man on a brown horse is preparing to lasso a bull , while another man on a white horse corrals the bull .

**Caption B:** Cowboy with a purple shirt and black vest trying to hold on during a wild horse ride .

**Adopted scope:** principal horseback riders' attire

**Extracted A:** unspecified

**Extracted B:** purple shirt and black vest

**Recorded reason, verbatim:**

> The first caption supplies no information about human clothing. / First caption gives no rider clothing to compare.

**Audit explanation:** The requested feature is the horseback riders' attire. A describes two men lassoing and corralling a bull, specifying their horses' brown and white coats while leaving human clothing unreported. B specifies a cowboy's purple shirt and black vest. The current exclusion follows A's missing attire description.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 199. train_8053: color of horse

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A man on a brown horse is preparing to lasso a bull , while another man on a white horse corrals the bull .

**Caption B:** Cowboy with a purple shirt and black vest trying to hold on during a wild horse ride .

**Adopted scope:** horses' coat colors

**Extracted A:** brown and white

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption supplies no horse color information. / Second caption does not describe the horse's color.

**Audit explanation:** The requested feature is horse coat color. A explicitly describes a brown horse and a white horse carrying men handling a bull. B describes a cowboy in a purple shirt and black vest riding a wild horse, leaving that horse's coat unspecified. The current exclusion follows B's missing horse color.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 200. train_8274: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3, S6.

**Caption A:** A big dog carries a stick across a frozen pond .

**Caption B:** Two dogs , one holding something in its mouth , in the snow .

**Adopted scope:** principal dogs' or carried object's color

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Neither caption establishes a carried object's color. / Neither caption gives the carried objects color.

**Audit explanation:** The recorded scope considers the principal dogs or their carried objects. A describes a dog carrying a stick over a frozen pond; B describes dogs in snow with one holding something. Neither caption supplies a dog or carried object color. The snowy and frozen surroundings belong to separate referents.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 201. train_8373: location

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Location/scene. **Policy:** S1, S3, S4.

**Caption A:** Young white male child with blond-hair in a red shirt coloring with crayons outside with an adult .

**Caption B:** A young child sits in a highchair and draws colorful squiggles on a white piece of paper .

**Adopted scope:** principal child's location

**Extracted A:** outside

**Extracted B:** highchair; surrounding location unspecified

**Recorded reason, verbatim:**

> Second gives a highchair position but no comparable environmental location.

**Audit explanation:** The recorded location feature is the child's surrounding environment. A explicitly places a child coloring outside. B places a drawing child in a highchair and leaves the wider setting unreported. The exclusion follows that environmental reading, while B's highchair supplies an explicit positional location under a broader reading of the condition.

**Policy check:** Review scope or feature.

**Review issue:** The unqualified condition location can include the explicitly supplied highchair; the recorded rationale narrows the feature to environmental setting.

**Question for your review:** Should location include furniture-level placement when one caption gives outside and the other gives a highchair?

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 202. train_8487: intentions of spectators

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Purpose/function. **Policy:** S1, S3, S6.

**Caption A:** A baseball player swings the bat as a catcher and umpire watch .

**Caption B:** Two baseball players on a field , with four spectators , and a crowd .

**Adopted scope:** spectators' intentions

**Extracted A:** no spectators described; catcher and umpire watch

**Extracted B:** unspecified spectator intent

**Recorded reason, verbatim:**

> The first caption does not establish spectators or their intentions. / First names officials and players rather than spectators with intentions.

**Audit explanation:** The condition concerns spectators' intentions. A describes a batter, catcher and umpire, whose explicit player and official roles supply a different scope from spectators. B mentions four spectators and a crowd without describing their intentions. The current exclusion therefore involves missing spectator referents in A and unavailable intentions in B.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 203. train_8568: location

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Location/scene. **Policy:** S1, S3, S4.

**Caption A:** The skateboarder does a jump near a traffic cone .

**Caption B:** A young man is jumping in the air with his skateboard .

**Adopted scope:** skateboarder's location

**Extracted A:** near traffic cone

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption does not establish a location to compare. / Second caption does not establish a comparable location.

**Audit explanation:** The recorded feature is the skateboarder's surrounding location. A places a jump near a traffic cone. B describes a young man jumping in the air with a skateboard, leaving the wider setting unreported. The exclusion follows that setting interpretation. The phrase in the air gives an explicit spatial location.

**Policy check:** Review scope or feature.

**Review issue:** B supplies in the air as a spatial location, while the recorded rationale requires surrounding setting for the generic condition location.

**Question for your review:** Should generic location admit the stated airborne position alongside A's position near a cone?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 204. train_8581: performer's age

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Age. **Policy:** S3, S6.

**Caption A:** A gymnast wearing a maroon and black outfit has just completed a routine and is posting on the gym mat .

**Caption B:** A young rhythmic gymnastic is watching a yellow hula hoop go by during her routine .

**Adopted scope:** principal gymnast's age

**Extracted A:** unspecified

**Extracted B:** young

**Recorded reason, verbatim:**

> The first caption provides no performer age information. / First caption provides no performer age to compare.

**Audit explanation:** The requested feature is the gymnast's age. A describes maroon and black clothing and completion of a routine on a gym mat, leaving age unreported. B explicitly calls its rhythmic gymnast young. The current exclusion follows the unavailable age category in A, since gymnast alone permits multiple ages.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 205. train_8650: speed of players

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Other. **Policy:** S3, S5, S6.

**Caption A:** A baseball player in blue scoring run by crossing home plate .

**Caption B:** Baseball players walk as a group on the field , and some jump to celebrate .

**Adopted scope:** baseball players' speed

**Extracted A:** crossing plate, speed unspecified

**Extracted B:** walking and jumping

**Recorded reason, verbatim:**

> Scoring a run does not establish the first player's actual speed. / Scoring a run does not establish the player's actual speed.

**Audit explanation:** The requested feature is player speed. A describes a baseball player scoring by crossing home plate without stating a pace. B explicitly describes walking players and some jumping in celebration. The current exclusion treats A's scoring movement as speed information wholly unavailable, leaving possible coarse sporting context for review.

**Policy check:** Review ordinary inference.

**Review issue:** Crossing home plate while scoring may supply an ordinary coarse movement pace; the recorded exclusion treats speed as wholly unavailable despite that activity context.

**Question for your review:** Can crossing home plate in this scoring context support a coarse speed value comparable with walking?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 206. train_8780: uniqueness of bike

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S3.

**Caption A:** A man is racing an unusual type of bike with many people watching him .

**Caption B:** A cyclist wearing a red and black jersey is competing in a race .

**Adopted scope:** bike's unusualness

**Extracted A:** explicitly unusual bike

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption gives no evidence about bike uniqueness. / Second caption does not establish whether bike is unusual.

**Audit explanation:** The requested feature is the bike's uniqueness. A explicitly calls the racing man's bike an unusual type. B describes a cyclist's red and black jersey and race participation, leaving the bicycle's distinctiveness unreported. The current exclusion follows the unavailable unusualness value for B's bicycle.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 207. train_8791: temperament of horse

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Emotion/sentiment. **Policy:** S3, S6.

**Caption A:** Two men on horses compete to see who can rope the calf first .

**Caption B:** A rodeo rider is riding a bucking horse in an arena .

**Adopted scope:** horse's temperament

**Extracted A:** unspecified

**Extracted B:** resisting by bucking

**Recorded reason, verbatim:**

> First caption does not establish the horses' temperament. / First caption gives no specific horse temperament for comparison.

**Audit explanation:** The requested feature is horse temperament. A describes two men on horses competing to rope a calf, leaving their horses' dispositions unspecified. B describes a bucking horse in a rodeo, supplying resistant behavior. The current exclusion follows A's unavailable temperament, with ordinary ridden participation providing insufficient evidence of a particular disposition.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 208. train_8799: object in dog's mouth

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S2, S3.

**Caption A:** A white dog jumps above a red Frisbee that is rolling along the surface of a low cut field .

**Caption B:** A black and white dog is catching a red and green object in his mouth .

**Adopted scope:** object in dog's mouth

**Extracted A:** none described: Frisbee rolls on ground

**Extracted B:** red and green object being caught

**Recorded reason, verbatim:**

> The first dog has no established object in its mouth. / First caption establishes no object inside the dog's mouth.

**Audit explanation:** The requested referent is an object in the dog's mouth. A places a red Frisbee rolling on the field below a jumping white dog, establishing an object elsewhere in the scene. B explicitly describes a red and green object being caught in the dog's mouth. The required mouth-held referent is unavailable in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 209. train_8829: relationship of players

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Other. **Policy:** S1, S3, S4, S5.

**Caption A:** A baseball pitcher prepares to pitch the ball to the batter .

**Caption B:** one baseball player running toward a base with another waiting on the base

**Adopted scope:** players' team relationship

**Extracted A:** pitcher and opposing batter

**Extracted B:** runner and base player; affiliation unspecified

**Recorded reason, verbatim:**

> Final blind invalid consensus: A establishes pitcher versus batter; B does not establish teammates or opponents. / Waiting player may be teammate or opponent; relationship cannot resolve. / B does not establish whether the waiting player is teammate or opponent.

**Audit explanation:** The recorded feature is the players' team relationship. A gives a pitcher preparing to pitch to a batter, supplying opposing baseball roles. B describes one player running toward a base and another waiting there, leaving team affiliation unspecified. The exclusion depends on team affiliation being the intended meaning of relationship.

**Policy check:** Review scope or feature.

**Review issue:** Both captions give functional relationships between baseball roles; the generic condition relationship of players may permit those recoverable interactions beyond team affiliation.

**Question for your review:** Should relationship compare the described functional player interactions, or specifically teammates versus opponents?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 210. train_9039: presence of hard hat

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S3, S6.

**Caption A:** Construction worker in a hard hat and yellow neon vest , working on stairs .

**Caption B:** A worker stands on a scaffolding to repair a brick building .

**Adopted scope:** worker's hard-hat presence

**Extracted A:** present

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Final blind invalid consensus: Hard hat is explicit in A; B never establishes headwear or its absence. / Hard hat explicit first; scaffolding work does not establish headwear. / A explicitly includes a hard hat; B leaves head protection unreported.

**Audit explanation:** The requested feature is a hard hat's presence on the worker. A explicitly describes a hard hat and yellow neon vest while the worker works on stairs. B describes a worker repairing a brick building from scaffolding, leaving headwear unspecified. The current exclusion follows B's unavailable hard hat presence value.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 211. train_9077: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** Person with an orange backpack watching the surrounding hills .

**Caption B:** A hiker walks on rocky ground at the base of a foggy mountain .

**Adopted scope:** principal portable object's color

**Extracted A:** orange backpack

**Extracted B:** no portable object described

**Recorded reason, verbatim:**

> The second caption supplies no comparable object color. / Second caption does not establish a comparable object color.

**Audit explanation:** The adopted comparable object is the principal portable item accompanying the person. A explicitly supplies an orange backpack on a person watching hills. B describes a hiker, rocky ground and a foggy mountain without identifying a comparable portable object or its color. The current exclusion follows that unavailable object and color in B.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 212. train_9146: results of sport

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Other. **Policy:** S3, S6.

**Caption A:** A cowboy is falling off a bull and looks like he might get trampled .

**Caption B:** A man is competing in a bareback bronco riding competition during a rodeo in front of a crowd .

**Adopted scope:** sporting outcome

**Extracted A:** falling off bull; possible trampling

**Extracted B:** result unspecified

**Recorded reason, verbatim:**

> Second caption gives no result of the ride. / Second caption describes participation without establishing a sporting outcome.

**Audit explanation:** The requested feature is the sporting outcome. A describes a cowboy falling from a bull and possibly facing trampling, supplying an immediate ride outcome. B describes a man's participation in a bareback bronco competition before a crowd, leaving how the ride ends unspecified. The current exclusion follows B's missing result.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 213. train_9223: animal proximity

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Spatial relation/posture. **Policy:** S3, S6.

**Caption A:** A brown dog and a black dog are together in the tall grass .

**Caption B:** One dog wades in the water while another dog is on land .

**Adopted scope:** principal dogs' mutual proximity

**Extracted A:** together

**Extracted B:** distance unspecified; one in water and one on land

**Recorded reason, verbatim:**

> Land-versus-water placement does not establish the second dogs' mutual separation.

**Audit explanation:** The requested feature is the dogs' mutual proximity. A explicitly describes a brown dog and a black dog together in tall grass. B places one dog in water and another on land without giving their separation. The current exclusion follows the unavailable mutual distance in B, since those locations allow adjacent or distant dogs.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 214. train_9329: elevation of performance

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Spatial relation/posture. **Policy:** S3, S6.

**Caption A:** A biker reaches the apex of his ramp while onlookers watch his feat .

**Caption B:** A male is doing a trick on his bicycle while others watch him and take pictures .

**Adopted scope:** performer's elevation

**Extracted A:** at ramp apex

**Extracted B:** unspecified during bicycle trick

**Recorded reason, verbatim:**

> The second caption supplies no comparable performance elevation. / Second caption does not establish performance elevation.

**Audit explanation:** The requested feature is performance elevation. A places a biker at the apex of a ramp while onlookers watch. B describes a bicycle trick observed and photographed by others, leaving the cyclist's height unspecified. The current exclusion follows B's missing elevation, since a bicycle trick can occur at several heights.

**Policy check:** Policy consistent.

**History:** supplied source rating 4; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 215. train_9407: focus of worker

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Action/activity. **Policy:** S1, S3, S6.

**Caption A:** Construction worker in orange vest and white hard hat with a shovel .

**Caption B:** Workers in hard hats and orange vests laying cement tiles over the floor .

**Adopted scope:** workers attention target

**Extracted A:** unspecified; holds shovel

**Extracted B:** cement floor tiles

**Recorded reason, verbatim:**

> A shovel alone does not establish the first worker's focus. / First does not establish the worker's immediate focus or task.

**Audit explanation:** The recorded feature is the worker's immediate attention target or task focus. A describes safety clothing and a shovel without stating what the worker is attending to or doing. B explicitly describes laying cement tiles on a floor. The current exclusion follows A's unavailable focus, since possessing a shovel leaves the immediate task uncertain.

**Policy check:** Policy consistent.

**History:** supplied source rating 4; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 216. train_9456: people's intentions

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Purpose/function. **Policy:** S3, S6.

**Caption A:** The sun shines bright on the snow surrounding a few people .

**Caption B:** Two hikers with backpacks crossing a snow field .

**Adopted scope:** people immediate intention

**Extracted A:** unspecified

**Extracted B:** crossing snow field on hike

**Recorded reason, verbatim:**

> The first caption does not establish the people's intentions. / First caption supplies no intentions for the people.

**Audit explanation:** A describes sunshine, snow, and a few people, supplying their surroundings without a purpose or intended next action. B describes hikers crossing a snow field, providing an immediate travel goal. The current exclusion rests on the absence of recoverable intentions for A's people.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 217. train_9538: sentiment

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Emotion/sentiment. **Policy:** S3, S6.

**Caption A:** several diferent colored dogs running through the grass

**Caption B:** A dog chases a toy in the grass with its owner in the background .

**Adopted scope:** scene emotional sentiment

**Extracted A:** unexpressed

**Extracted B:** unexpressed

**Recorded reason, verbatim:**

> Neither caption clearly establishes an emotional tone or sentiment. / Running and chasing do not establish emotional sentiment.

**Audit explanation:** A describes several dogs running through grass, while B describes a dog chasing a toy with its owner nearby. These actions establish movement and play context. Neither caption supplies an explicit emotional tone or a sufficiently determinate emotional state for the requested scene sentiment.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 218. train_9616: men's occupation

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S3, S6.

**Caption A:** A man dressed as a cowboy holds a rope in his teeth as he ropes a calf .

**Caption B:** Two men wearing earring hats and ponchos are on horses surrounding a bull .

**Adopted scope:** men's occupations

**Extracted A:** cowboy-like calf roping

**Extracted B:** horsemen surrounding bull; occupation unstated

**Recorded reason, verbatim:**

> The second men's clothing and proximity to a bull do not establish their occupations.

**Audit explanation:** A describes a man dressed as a cowboy roping a calf, and B describes mounted men in hats and ponchos surrounding a bull. The current rationale identifies B's missing occupation. Both captions primarily establish clothing and actions, leaving actual employment dependent on an occupational inference.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 219. train_9689: presence of audience

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S3.

**Caption A:** A group of bicyclers that are going down the road .

**Caption B:** Two bicycle racers are speeding down a street in front of spectators .

**Adopted scope:** audience presence

**Extracted A:** unspecified

**Extracted B:** present

**Recorded reason, verbatim:**

> Final blind invalid consensus: B explicitly includes spectators; A never establishes audience presence or absence. / Spectators establish audience second; first leaves audience presence unspecified. / B explicitly includes spectators; A supplies no audience presence information.

**Audit explanation:** B explicitly describes bicycle racers passing spectators, establishing an audience. A describes bicyclers going down a road and supplies no audience information. The road setting permits spectators or an empty roadside, so the current exclusion reflects an unavailable audience presence value in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 220. train_9698: name of location

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Location/scene. **Policy:** S1, S3, S6.

**Caption A:** Kid in a skate park doing a trick with his skateboard .

**Caption B:** A skateboarding soaring through the air in front of a blue building .

**Adopted scope:** named venue or site type

**Extracted A:** skate park

**Extracted B:** building frontage, venue unspecified

**Recorded reason, verbatim:**

> A building in the background does not identify the second site's venue type.

**Audit explanation:** A places the child and skateboard trick in a skate park, supplying a venue category under the recorded location scope. B places an airborne skateboarder in front of a blue building. That background building leaves the actual skating venue or site name unspecified.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 221. train_9719: presence of hat

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Presence/absence. **Policy:** S3.

**Caption A:** A little girl sitting in a small chair outdoors .

**Caption B:** A little girl in a hat and red pants balances on tightropes .

**Adopted scope:** principal girl hat presence

**Extracted A:** unspecified

**Extracted B:** present

**Recorded reason, verbatim:**

> Final blind invalid consensus: B explicitly includes a hat; A never establishes headwear or its absence. / Hat is explicit second; first does not establish headwear absence. / B explicitly includes a hat; A leaves hat presence unreported.

**Audit explanation:** B explicitly gives the little girl a hat while she balances on tightropes. A describes a little girl sitting in a small chair outdoors and gives no headwear information. The current exclusion treats A's hat presence as unavailable because an unmentioned hat has no established absence.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 222. train_9751: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3, S7.

**Caption A:** Two toddlers are sitting in a plastic playpen with a blue floor .

**Caption B:** Two boys in tent-like area , with colorful balls on floor .

**Adopted scope:** play area floor color

**Extracted A:** blue

**Extracted B:** unspecified; colorful balls on floor

**Recorded reason, verbatim:**

> Final blind invalid consensus: Blue modifies A’s floor; B colors balls, leaving corresponding object color unavailable. / Object lacks stable referent between playpen, floor, tent, and balls.

**Audit explanation:** Under the recorded floor scope, A supplies a blue playpen floor. B describes colorful balls lying on a floor inside a tent-like area, assigning color to the balls and leaving the floor color unavailable. This missing corresponding floor color supplies the concrete basis for the current exclusion.

**Policy check:** Review scope or feature.

**Review issue:** The rationale also invokes unstable object scope. A floor scope is recorded and materially different comparison outcomes are absent from the record.

**Question for your review:** Should the explanation use the recorded floor scope alone, or should a different principal object be specified?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 223. train_9759: color of surfing material

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A surfer is riding a wave in a large body of water .

**Caption B:** A surfer on a whiteboard about to fall off as a wave crashes around him .

**Adopted scope:** surfboard color

**Extracted A:** unspecified

**Extracted B:** white

**Recorded reason, verbatim:**

> The first caption does not establish the surfboard's color. / First caption does not establish surfing equipment color.

**Audit explanation:** A describes a surfer riding a wave and supplies no color for the surfing equipment. B describes a surfer on a whiteboard, interpreted in the recorded scope as a white surfboard. The current exclusion therefore concerns the absent surfboard color in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 224. train_9779: color of clothes

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S3, S6.

**Caption A:** A person wearing a Red Bull ski helmet and ski suit snowboard .

**Caption B:** A man in a green jacket and brown pants is pictured in midair on a snowboard .

**Adopted scope:** principal clothing colors

**Extracted A:** unspecified

**Extracted B:** green and brown

**Recorded reason, verbatim:**

> A brand name does not establish actual clothing colors. / Brand wording does not establish actual clothing colors.

**Audit explanation:** B identifies green and brown clothing on its snowboarder through a green jacket and brown pants. A names a Red Bull ski helmet and a ski suit. The brand wording supplies an identity cue while actual clothing colors remain unavailable for the requested comparison.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 225. train_9787: color of dog

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A black dog with a red collar stands outside with his paws in water .

**Caption B:** A dog with a stick in its mouth runs through the rocks in shallow water .

**Adopted scope:** principal dog coat color

**Extracted A:** black

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption supplies no dog color information. / Second caption provides no dog color to compare.

**Audit explanation:** A explicitly describes a black dog with a red collar, making black the principal dog's coat color. B describes a dog carrying a stick through shallow water and rocks without any coat color. The current exclusion rests on the unavailable dog color in B.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 226. train_9791: hand position

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Spatial relation/posture. **Policy:** S3, S6.

**Caption A:** A young girl in a white shirt and blue shorts riding high on a swing .

**Caption B:** A young girl closes her eyes and releases her hands as she enjoys the swing set .

**Adopted scope:** principal girl hand position

**Extracted A:** unspecified

**Extracted B:** released from swing

**Recorded reason, verbatim:**

> Riding high on swing does not establish hand position. / Only the second establishes the position of the girls hands.

**Audit explanation:** B says the girl releases her hands while enjoying the swing set, giving a recoverable hand position relative to the swing. A describes a girl riding high on a swing and identifies clothing colors. Her hand placement remains unspecified despite the shared swinging activity.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 227. train_9795: cost of boats

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Other. **Policy:** S3, S6.

**Caption A:** Local villagers are preparing for a fishing trip on this gorgeous fishing boat .

**Caption B:** Six men , two wearing hats , are sitting in a small boat on the water .

**Adopted scope:** principal boat monetary cost

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Neither caption provides a boat price or reliable cost information. / Neither caption establishes any boat price or cost.

**Audit explanation:** A calls the fishing boat gorgeous and describes villagers preparing for a trip. B describes six men sitting in a small boat. Appearance, size, and use provide no monetary price or dependable cost estimate, leaving the requested boat cost unavailable in both captions.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 228. train_9831: gender

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Gender. **Policy:** S1, S3.

**Caption A:** A young woman with a ponytail climbs a white stone structure .

**Caption B:** A person in a red shirt climbing up a rock face covered in assist handles .

**Adopted scope:** principal climber gender

**Extracted A:** female

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption does not establish the climber's gender. / Second caption does not establish the climber's gender.

**Audit explanation:** A identifies its climber as a young woman, supplying a female gender value. B identifies its climber as a person in a red shirt climbing a handled rock face. That person description and activity leave gender unavailable, which supports the current exclusion under the recorded scope.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 229. train_9937: interaction between dogs

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Action/activity. **Policy:** S1, S3.

**Caption A:** Black dog is submissive on ground to brown dog .

**Caption B:** A big dog drinks as a little dog gets down off a deck .

**Adopted scope:** dog-to-dog interaction

**Extracted A:** submission to other dog

**Extracted B:** separate drinking and stepping down

**Recorded reason, verbatim:**

> Second dogs have separate actions without an established interaction.

**Audit explanation:** A explicitly relates the black dog to the brown dog through submission on the ground. B describes one dog drinking and another stepping down from a deck. These individual actions leave any dog-to-dog interaction unspecified, so B lacks the requested relational behavior under the recorded scope.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 230. train_9946: activity of person

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Action/activity. **Policy:** S1, S3, S4.

**Caption A:** The little girl in the pool is wearing a red swimsuit .

**Caption B:** a smiling toddler in a pink swimsuit is laying in the water .

**Adopted scope:** principal child activity

**Extracted A:** being in pool; activity unspecified

**Extracted B:** lying in water

**Recorded reason, verbatim:**

> First pool presence does not establish any specific activity.

**Audit explanation:** A places a little girl in a pool and describes her red swimsuit, while B describes a toddler lying in water. The current exclusion requires a specific activity or posture, treating A's pool presence as insufficient. A still supplies a coarse state of being in the pool.

**Policy check:** Review scope or feature.

**Review issue:** The broad activity condition may accommodate pool participation or a stated scene activity; the recorded rationale requires a more specific movement or posture.

**Question for your review:** Should activity include the recoverable state of being in the pool, or require an explicit bodily action?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 231. train_10037: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3, S7.

**Caption A:** A person in face paint and an orange oversized cowboy hat rides his bike on a trail .

**Caption B:** A woman in black bicycle gear and a white helmet pedals hard uphill on her bike .

**Adopted scope:** principal bicycle color

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Final blind invalid consensus: Generic object does not select corresponding headwear versus other colored clothing. / Object does not specify headwear or clothing, yielding competing comparisons.

**Audit explanation:** The recorded scope selects each principal bicycle. A colors the rider's oversized hat orange, while B colors the rider's gear black and helmet white. Neither caption supplies bicycle color. The current exclusion is supported by those missing bicycle colors under the adopted comparable object scope.

**Policy check:** Review scope or feature.

**Review issue:** The rationale invokes competing headwear and clothing references, while the recorded scope already selects bicycles. Scope ambiguity requires material alternatives unresolved by the principal entity convention.

**Question for your review:** Should this case use the recorded bicycle scope and explain the absent bicycle colors?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 232. train_10111: color of person's shirt

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S3, S6.

**Caption A:** A young child having fun in his Superman shirt .

**Caption B:** Little blond-hair boy in orange shirt playing with toys .

**Adopted scope:** principal child shirt color

**Extracted A:** unspecified Superman shirt

**Extracted B:** orange

**Recorded reason, verbatim:**

> A Superman design does not reliably establish the shirt's color. / Character design alone does not establish the shirt color.

**Audit explanation:** B explicitly gives the boy an orange shirt. A identifies the young child's shirt through a Superman design and gives no fabric color. A character associated with familiar colors can appear on shirts of many colors, leaving the requested shirt color unavailable in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 233. train_10153: gender of surfer

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Gender. **Policy:** S1, S3.

**Caption A:** A surfer is riding a wave in a large body of water .

**Caption B:** A man in a dark bodysuit is surfing through the spray of a powerful wave .

**Adopted scope:** principal surfer gender

**Extracted A:** unspecified

**Extracted B:** male

**Recorded reason, verbatim:**

> Only the second caption establishes the surfer's gender. / First caption does not establish the surfer's gender.

**Audit explanation:** A identifies a surfer riding a wave without any gender term or gendered pronoun. B identifies a man surfing through powerful wave spray. The requested principal surfer gender is therefore available in B and wholly unavailable in A, which supplies the current exclusion reason.

**Policy check:** Policy consistent.

**History:** supplied source rating 4; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 234. train_10219: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A boy with an orange shirt lies on a bodyboard in the surf .

**Caption B:** A man is riding the oceans waves on his surfboard .

**Adopted scope:** principal ridden board color

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Neither caption establishes a comparable board color. / Second caption supplies no color for a comparable object.

**Audit explanation:** A describes a boy lying on a bodyboard and assigns orange to his shirt. B describes a man riding waves on a surfboard. Under the recorded ridden board scope, both captions leave board color unspecified; the clothing color belongs to a separate entity.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 235. train_10241: position of person

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Spatial relation/posture. **Policy:** S1, S3, S5.

**Caption A:** A closeup of a man skateboarding in a skate park .

**Caption B:** A skateboarding soaring through the air in front of a blue building .

**Adopted scope:** principal skateboarder position

**Extracted A:** unspecified skating position

**Extracted B:** airborne

**Recorded reason, verbatim:**

> First skateboarder's body position is not specified or directly inferable.

**Audit explanation:** B describes a skateboarder soaring through the air, providing an airborne position. A describes a man skateboarding at a skate park in closeup. The current exclusion interprets position as bodily or airborne posture and treats A's general skateboarding description as supplying no sufficiently specific position.

**Policy check:** Review ordinary inference.

**Review issue:** Ordinary skateboarding may supply a coarse riding posture, and the general word position also permits scene placement. The exclusion depends on the required position detail.

**Question for your review:** Can ordinary riding posture count as position here, or is airborne versus grounded position the intended feature?

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 236. train_10299: clothing worn by boy

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S3, S6.

**Caption A:** A young boy is holding his breath while he jumps into water .

**Caption B:** The boy wearing swimming trunks is jumping off a pier into a lake .

**Adopted scope:** principal boy clothing

**Extracted A:** unspecified

**Extracted B:** swimming trunks

**Recorded reason, verbatim:**

> Jumping into water does not establish clothing type. / Only the second identifies the boys clothing.

**Audit explanation:** B explicitly describes the boy wearing swimming trunks as he jumps from a pier into a lake. A describes a boy holding his breath and jumping into water. Jumping into water leaves clothing type open, so the current exclusion reflects missing clothing information in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 237. train_10380: type of trick

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S3, S4.

**Caption A:** a bicyclist wearing a helmet jumping a trick on his back tire

**Caption B:** A man in beige pants does a trick on a bicycle .

**Adopted scope:** specific bicycle-trick type

**Extracted A:** rear-wheel jump maneuver

**Extracted B:** unspecified bicycle trick

**Recorded reason, verbatim:**

> The second establishes that a trick occurs without supplying its type.

**Audit explanation:** A describes a bicycle maneuver involving a jump on the back tire. B describes a man doing a trick on a bicycle without specifying the maneuver. The current exclusion treats B's general bicycle trick category as lacking the specific trick type requested by the recorded scope.

**Policy check:** Review scope or feature.

**Review issue:** Both captions establish a bicycle trick category. The policy permits partial type information and differences in specificity, so requiring a named or specific maneuver merits review.

**Question for your review:** Does the general bicycle trick category provide enough recoverable type information for this condition?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 238. train_10421: number of spectators

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** Two long distance bikers riding side by side on a two lane road .

**Caption B:** Two bicycle racers are speeding down a street in front of spectators .

**Adopted scope:** spectator count

**Extracted A:** no spectator entity established

**Extracted B:** multiple spectators; exact count unspecified

**Recorded reason, verbatim:**

> First caption does not establish any spectator count. / First caption gives no spectator count or established absence.

**Audit explanation:** B explicitly includes spectators watching bicycle racers, supplying a plural spectator quantity. A describes two long distance bikers riding side by side on a road and mentions no spectators. Its two riders cannot supply the requested audience count, and audience absence is also unestablished.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 239. train_10449: height of location

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Location/scene. **Policy:** S1, S3, S6.

**Caption A:** A man on a bicycle jumping off a dirt ramp with one foot on the ground

**Caption B:** One helmeted man on a mountain bike is coming down a steep , rocky path .

**Adopted scope:** terrain elevation

**Extracted A:** unspecified dirt ramp elevation

**Extracted B:** unspecified rocky path elevation

**Recorded reason, verbatim:**

> Neither caption establishes comparable location elevation. / Terrain descriptions do not establish comparable absolute location heights.

**Audit explanation:** A describes a dirt ramp used for a bicycle jump, and B describes a steep rocky path descended by a mountain biker. The recorded feature is terrain elevation. Ramp shape and path steepness establish terrain form without supplying either location's absolute or comparable elevation.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 240. train_10483: age of player

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Age. **Policy:** S1, S3.

**Caption A:** A teenager dressed in a baseball uniform attempting to hit a baseball during a game .

**Caption B:** A baseball player in a red and white uniform runs while onlookers watch the game from outside the fence .

**Adopted scope:** principal baseball player age category

**Extracted A:** teenager

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption does not establish the player's age. / Second caption does not establish the player's age.

**Audit explanation:** A explicitly calls its baseball player a teenager, giving an age category. B describes a baseball player in a red and white uniform running during a watched game. Uniform, player role, and onlookers leave that player's age category unspecified, supporting the current exclusion.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 241. train_10505: temperament of animals

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Emotion/sentiment. **Policy:** S1, S3, S6.

**Caption A:** A cowboy is desperately grasping too the reigns off a horse that is trying to buck him off at a rodeo .

**Caption B:** A man and a boy riding brown horses are roping a white steer in a corral .

**Adopted scope:** ridden horses temperament

**Extracted A:** bucking resistant horse

**Extracted B:** unspecified while ridden

**Recorded reason, verbatim:**

> Being ridden while roping does not establish the second horses' temperament. / Roping scene does not establish the ridden horses' temperament.

**Audit explanation:** A describes a horse trying to buck its cowboy rider off, supporting a resistant temperament in the recorded scope. B describes brown horses being ridden while their riders rope a steer. Participation in that action leaves the horses' temperament unspecified, which is the current exclusion basis.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 242. train_10529: Slope of walking path

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Spatial relation/posture. **Policy:** S1, S3, S6.

**Caption A:** Three people in coats walking along a snow strewn trail on a mountain .

**Caption B:** Men in pants and coats walk up a steep and narrow road .

**Adopted scope:** walking-path gradient

**Extracted A:** unspecified mountain-trail slope

**Extracted B:** steep ascending road

**Recorded reason, verbatim:**

> Being on a mountain does not establish the local trail's slope.

**Audit explanation:** B explicitly describes people walking up a steep road, supplying an ascending gradient. A places walkers on a snow strewn mountain trail. Mountain terrain can contain level and sloping trail segments, so A leaves the local walking path gradient unavailable under the recorded feature.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 243. train_10537: type of instrument

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Identity/type. **Policy:** S1, S3, S4.

**Caption A:** A band of two men playing guitars and a man playing the drums , are singing on a stage .

**Caption B:** A music venue with an awesome light show and three band members playing instruments .

**Adopted scope:** band's instrument types

**Extracted A:** guitars and drums

**Extracted B:** unspecified instruments

**Recorded reason, verbatim:**

> The second identifies no recoverable instrument type.

**Audit explanation:** A identifies guitars and drums played by band members on a stage. B describes three band members playing instruments at a music venue. The current exclusion requires instrument subtypes and treats B's broad musical instrument category as insufficient to extract the requested instrument types.

**Policy check:** Review scope or feature.

**Review issue:** B supplies the general musical instrument category. The frozen policy allows general categories versus specific subtypes to carry partial type information, making the required abstraction level consequential.

**Question for your review:** Should the general musical instrument category count as partial type information for this comparison?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 244. train_10663: location of skate park

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Location/scene. **Policy:** S1, S3.

**Caption A:** A boy in a white shirt does a trick on his skateboard at a skate park .

**Caption B:** a roller-blader grinds a rail at an indoor skate park .

**Adopted scope:** skate park indoor/outdoor location

**Extracted A:** unspecified

**Extracted B:** indoors

**Recorded reason, verbatim:**

> The first caption does not specify the park's location setting. / First caption does not establish indoor versus outdoor location.

**Audit explanation:** B explicitly places its rollerblader at an indoor skate park, establishing an indoor setting. A places a boy's skateboard trick at a skate park without locating that park indoors or outdoors. Under the recorded setting scope, A lacks the requested indoor versus outdoor value.

**Policy check:** Policy consistent.

**History:** supplied source rating 4; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 245. train_10782: color of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A person wearing a white hat is riding a horse like a bull at a rodeo .

**Caption B:** A bull is charging a matador in rodeo , while three other men look at the animal .

**Adopted scope:** principal ridden or confronted animal color

**Extracted A:** horse color unspecified

**Extracted B:** bull color unspecified

**Recorded reason, verbatim:**

> Second caption supplies no comparable object color. / Second caption supplies no object color for comparison.

**Audit explanation:** The adopted scope compares the principal animals: A's ridden horse and B's charging bull. A supplies white for the rider's hat, while B supplies no color. Both animal coat colors remain unspecified, so the current exclusion has missing color information on both sides under this scope.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 246. train_10833: distance travelled

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S3, S6.

**Caption A:** Someone leaps across the beach in a sign of joy !

**Caption B:** Girl jumping on the beach with water in the background .

**Adopted scope:** principal person distance traveled

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Neither caption provides an extractable distance traveled. / Neither caption provides the distance traveled while jumping.

**Audit explanation:** A describes someone leaping across a beach in joy, while B describes a girl jumping on a beach with water behind her. Both captions establish jumping and a beach setting. Neither supplies a travel distance, extent, or dependable comparison of the distance covered.

**Policy check:** Policy consistent.

**History:** supplied source rating 4; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 247. train_10849: animal size

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A black dog has its mouth open while leaning to the side .

**Caption B:** A small black dog playing with a ball in the grass .

**Adopted scope:** principal dog size

**Extracted A:** unspecified

**Extracted B:** small

**Recorded reason, verbatim:**

> First caption provides no information on dog size. / Only the second supplies any animal size information.

**Audit explanation:** B describes a small black dog playing with a ball, supplying a small size value for the animal. A describes a black dog leaning sideways with its mouth open. Its coat color and posture leave size unavailable, which is the current exclusion reason.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 248. train_10850: location name

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Location/scene. **Policy:** S1, S3, S6.

**Caption A:** A brown dog running with a long stick in his mouth .

**Caption B:** A dark brown dog jumps behind a young girl in shorts .

**Adopted scope:** principal dog geographic location

**Extracted A:** unspecified

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Neither caption provides a name or identifiable type of location. / Neither caption identifies the location's name.

**Audit explanation:** A describes a brown dog running with a stick, and B describes a dark brown dog jumping behind a girl. Those actions and relative positions give no geographic name or identifiable location category. The requested principal dog location remains unavailable in both captions.

**Policy check:** Policy consistent.

**History:** supplied source rating 2; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 249. train_10882: address of place

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Location/scene. **Policy:** S1, S3, S6.

**Caption A:** People are gathered on a city street with police vehicles arriving .

**Caption B:** People going about their business at the corner of 5th Avenue and W 58th streets .

**Adopted scope:** scene street address

**Extracted A:** unspecified city street

**Extracted B:** 5th Avenue and W 58th Street

**Recorded reason, verbatim:**

> First caption provides no street address information. / Only the second supplies a specific street address.

**Audit explanation:** B locates the people at the corner of 5th Avenue and W 58th streets, giving a specific street address description. A places people and arriving police vehicles on a city street. That broad setting leaves the requested street address unavailable for A.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 250. train_10938: size of object

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** Little boy in his bathing suit tentatively preparing to step in the rocky-lined stream .

**Caption B:** A boy is laying on a large river rock with his feet in the water on a sunny day .

**Adopted scope:** principal water-edge rocks size

**Extracted A:** unspecified stream-edge rocks

**Extracted B:** large river rock

**Recorded reason, verbatim:**

> First caption does not establish rock size. / Only the second supplies size of the relevant rocks.

**Audit explanation:** B describes the boy lying on a large river rock, supplying size for the relevant rock. A describes a rocky-lined stream and a boy preparing to enter it. The presence of lining rocks supplies no rock size, leaving A without the requested object size value.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 251. train_10939: sentiment of people

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Emotion/sentiment. **Policy:** S1, S3, S6.

**Caption A:** Little boy in his bathing suit tentatively preparing to step in the rocky-lined stream .

**Caption B:** A boy is laying on a large river rock with his feet in the water on a sunny day .

**Adopted scope:** principal boy emotional state

**Extracted A:** tentative or hesitant

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> Reclining in sunshine does not establish the second boy's sentiment. / Second caption gives no reliable indication of the boys emotion.

**Audit explanation:** A describes the boy tentatively preparing to enter a stream, giving a hesitant emotional cue. B describes a boy lying on a river rock with his feet in water on a sunny day. Posture and sunshine leave his emotional state unspecified under the recorded sentiment scope.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 252. train_11010: clothing style

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3, S4.

**Caption A:** A girl in a red dress is surrounded by a lot of other people holding their hands up .

**Caption B:** A crowd of people with their arms in the air , many wearing hats of various kinds .

**Adopted scope:** people's overall clothing style

**Extracted A:** red dress on girl; style unstated

**Extracted B:** varied hats on crowd; style unstated

**Recorded reason, verbatim:**

> Garment names alone do not establish comparable overall styles such as casual, formal, or costume.

**Audit explanation:** A identifies a red dress on a girl among people raising their hands. B identifies varied hats worn by members of a crowd. The current exclusion interprets clothing style as an overall category such as casual, formal, or costume, leaving that category unspecified in both captions.

**Policy check:** Review scope or feature.

**Review issue:** The captions contain recoverable garment descriptions. A broader clothing style reading could compare dress and hat based appearance; the recorded rationale narrows style to overall dress categories.

**Question for your review:** Should clothing style require an overall dress category, or can the stated garment choices supply partial style information?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 253. train_11015: hair condition

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A bald guitarist in all black clothing playing his guitar with his band .

**Caption B:** A man wearing a black t-shirt is playing seven string bass a stage .

**Adopted scope:** principal musician hair condition

**Extracted A:** bald

**Extracted B:** unspecified

**Recorded reason, verbatim:**

> The second caption supplies no information about hair condition. / Second caption provides no hair condition for comparison.

**Audit explanation:** A explicitly identifies a bald guitarist wearing black clothing, giving a hair condition value. B identifies a man in a black T-shirt playing a seven string bass on a stage. Clothing and instrument descriptions leave the second musician's hair condition unavailable for comparison.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 254. train_11111: color of animal

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Color/appearance. **Policy:** S1, S3.

**Caption A:** A dog playing in the snow , ready to catch a toy

**Caption B:** A dark dog jumps across the snow near the woods .

**Adopted scope:** principal dog coat color

**Extracted A:** unspecified

**Extracted B:** dark

**Recorded reason, verbatim:**

> First caption supplies no animal color information. / Only the second supplies the dogs fur color.

**Audit explanation:** B identifies its jumping dog as dark, giving a coarse coat color value. A describes a dog playing in snow and preparing to catch a toy. Snow describes the environment and supplies no dog color, leaving the principal animal's coat color unavailable in A.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 255. train_11135: number of person

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Count/quantity. **Policy:** S1, S3.

**Caption A:** Athletes on numbered horses congregate in a field .

**Caption B:** A group of greyhounds racing with jerseys and muzzles .

**Adopted scope:** all described humans

**Extracted A:** multiple mounted athletes

**Extracted B:** no human entity established

**Recorded reason, verbatim:**

> The second caption establishes dogs but no human count. / Second caption supplies no people whose number can be extracted.

**Audit explanation:** A describes athletes mounted on numbered horses, establishing multiple human participants. B describes greyhounds racing in jerseys and muzzles and establishes no human entity. The requested person count cannot be extracted from B's dog group, and unmentioned humans have no established count or absence.

**Policy check:** Policy consistent.

**History:** supplied source rating 1; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 256. train_11223: gender

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Gender. **Policy:** S1, S3.

**Caption A:** A surfer wearing a wetsuit and using a light colored board catches some air .

**Caption B:** The sun gives the waves a green hue as this surfer displays his skills .

**Adopted scope:** principal surfer gender

**Extracted A:** unspecified

**Extracted B:** male

**Recorded reason, verbatim:**

> Only the second caption establishes the surfer's gender. / First surfer's gender cannot be extracted reliably.

**Audit explanation:** B describes a surfer displaying his skills, providing a masculine pronoun under the recorded gender extraction. A describes a surfer wearing a wetsuit and using a light colored board. Equipment, clothing, and the surfing action leave A's principal surfer gender unavailable for comparison.

**Policy check:** Policy consistent.

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: fresh_review_confirms_current_label.

### 257. train_11335: woman stance

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Spatial relation/posture. **Policy:** S1, S3, S5.

**Caption A:** Women riding a horse carrying the American flag , both rider and horse dressed patriotically .

**Caption B:** A blond woman in a green and gray uniform balances on a horse as she shows the American flag off to the crowd .

**Adopted scope:** female rider's stance

**Extracted A:** mounted on horse, exact stance unstated

**Extracted B:** balancing on horse, exact stance unstated

**Recorded reason, verbatim:**

> Riding and balancing do not reliably establish seated versus standing stance for the comparison.

**Audit explanation:** A describes a woman riding a horse with an American flag, and B describes a woman balancing on a horse while showing the flag. The current exclusion requires seated versus standing stance. Both captions explicitly establish being mounted while leaving the exact stance unstated.

**Policy check:** Review ordinary inference.

**Review issue:** Ordinary horse riding can support a seated posture, and mounted position is recoverable in both captions. Requiring exact seated versus standing detail may exceed the condition's necessary precision.

**Question for your review:** Should ordinary riding posture or the shared mounted position supply stance information here?

**History:** supplied source rating 4; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

### 258. train_11341: means of flotation

**Current status:** invalid. **Current rating:** excluded/null. **Family:** Purpose/function. **Policy:** S1, S3, S4, S5.

**Caption A:** A man and a small girl floating on an innertube .

**Caption B:** A man is helping his child float along in the pool .

**Adopted scope:** physical means supporting flotation

**Extracted A:** inner tube

**Extracted B:** man helps child float, actual buoyancy support unstated

**Recorded reason, verbatim:**

> Helping a child float does not establish whether support comes from arms, swimming, or a flotation device.

**Audit explanation:** A explicitly describes an inner tube supporting a man and a small girl. B describes a man helping his child float in a pool. The current exclusion seeks the physical buoyancy mechanism and treats B's stated human assistance as insufficient to establish the child's flotation means.

**Policy check:** Review scope or feature.

**Review issue:** B explicitly identifies a helper, supplying a coarse means of support even though arm support, swimming assistance, and flotation equipment remain unspecified.

**Question for your review:** Can assistance from the man count as partial flotation means, or must the actual buoyancy mechanism be identified?

**History:** supplied source rating 3; version-3 status invalid, rating null. Current decision pathway: focused_semantic_adjudication.

## Verbatim policy archive

This archived text preserves the wording used in the audit, including historical terminology. The navigation codes above provide the current validation terminology.

### Rubric, verbatim

> # Development audit: entity scope and missing information
> 
> Read only the assigned part*_inputs.json and this rubric. The inputs contain captions, condition and row ID. Original labels, previous judgments and encoder predictions are withheld. Do not inspect other workspace sources or retrieve labels. Your task is semantic annotation, not prediction matching.
> 
> For every example, first identify the requested entity/role and feature, extract its two relevant values, then rate their conditional similarity. Record the scope explicitly. Condition scope controls which mentions count.
> 
> ## Entity scope
> 
> * Explicit role words constrain scope. Riders count people actually riding in the described scene. A surfer explicitly catching a wave counts as an active rider; another surfer merely present in the ocean does not automatically count as an active rider. Players exclude explicitly described spectators. People includes all mentioned humans when no narrower role is specified; animals excludes people.
> * Resolve clear coreference. A member described within a previously counted group adds no new entity. A singular noun phrase denotes one described entity. Different species do not change an animal total. A quantity condition compares quantity independently of species/type.
> * For generic color/type/activity of an object/person, use the principal comparable entities described by the captions. Incidental collars, snow and background objects do not displace the principal dogs under dog color or generic object color. Specify the adopted referent. Flag materially competing equally salient referents for resolution.
> * Conditions naming only an entity default to its type. Keep abstraction level consistent across captions. A general category compared with a specific subtype lacks some relevant specificity; use the graded rubric rather than automatically treating a subtype difference as total dissimilarity.
> 
> ## Rating rules
> 
> * Binary feature comparisons use 1/3/5: 5 for established equality, 1 for established inequality, 3 for possible equality given underspecification. Exact counts, categorical gender, and age-category equality use this rule. For example, exact three versus several gives 3. Mixed known/unknown group genders can give 3 when both captions establish relevant gender information and the remaining group members are unspecified. Missing precision is not itself grounds for exclusion.
> * Color combinations and genuinely graded features can require 1..5. For graded similarity: 5 fully equivalent on the condition; 4 mostly equivalent with small relevant differences; 3 roughly equivalent with substantial relevant differences or missing specificity; 2 different with only a broad relevant category in common; 1 different on the requested aspect. Guitar versus violin under instrument type is 2. Explain the semantic comparison.
> * Distinguish partial feature information from wholly absent feature information. Exact three versus several has recoverable count information in both captions and gives 3. All women versus a woman plus an opponent of unspecified gender has gender information in both captions and can give 3. A blue bus versus a bus whose color is completely unstated lacks color information in one caption and is invalid under Tu. A merely mentioned person gives no recoverable gender value by itself. If the requested feature cannot be extracted or directly inferred from either member of the pair, or a required entity is absent/inapplicable, mark invalid with a concrete reason. Broad descriptions such as cluttered desk or unmade bed can support direct coarse content inference; decide semantically. A presence condition may establish a negative when supported; mere silence does not prove absence.
> * Permit ordinary direct high-confidence context: pie/cake as desserts, ordinary sidewalk as level, tennis equipment from tennis, bathroom from toilet/sink, and standard scene/activity implications. Avoid speculative proper identities, unusual situations and unsupported fine details. Treat common context consistently.
> * Uncertainty about fine detail differs from uncertainty about the condition's actual referent. Use status needs_scope only when materially different plausible referents/features yield different ratings that the frozen conventions cannot resolve. Supply the best proposed rating and alternatives. A difficult decision or an alternative imaginable in an unusual world is not by itself a scope dispute.
> 
> ## User-adjudicated anchors
> 
> These are semantic policy anchors: pie versus cake under meal type=5; level sidewalk versus ascending stairs under ground angle=1; one active wave rider versus two surfers with one explicitly catching a wave under number of riders=5. These anchor labels stay fixed by user adjudication.
> 
> ## Output
> 
> Write an exhaustive JSON list, in assigned input order, to the assigned part*_review.json:
> 
> {"row_id":"...", "scope":"requested referent/feature, concise", "value_a":"...", "value_b":"...", "status":"rated|invalid|needs_scope", "rating":1..5|null, "confidence":"high|medium|low", "rationale":"one short concrete explanation", "issue_tags":["role_scope|entity_scope|counting|missing_value|direct_inference|graded_type|none"]}
> 
> For invalid, rating is null. For needs_scope, include "alternatives" listing different readings/ratings. Use manual semantic judgment for every row. Scripts may format or validate judgments; do not substitute lexical heuristics or default labels for reading captions. Work in batches of roughly 75 to 105 examples and save complete reviewed prefixes after each batch. This is an assistant-model review, not human annotation. Do not run any model API, GPU or training job.
> 
> Validity clarification (frozen before second review and model rescoring): wholly absent requested feature information in even one caption is invalid under Tu. Partial recoverable values in both captions can justify 3. The earlier draft wording allowing all wholly unknown attributes to become 3 was too permissive and is superseded by this paragraph.

### Resolution policy, verbatim

```json
{
  "version": 4,
  "coverage": "All 1830 development comparisons, including accepted and excluded cases",
  "initial_review": "Six isolated model contexts; source captions and condition only; previous labels and encoder scores withheld",
  "scope_first": "Record requested referent, feature and extracted values before rating",
  "anchors": {
    "train_72": 5,
    "train_7753": 1,
    "train_8859": 5
  },
  "second_review": "Every disagreement with current V3 rating/disposition and every needs_scope result receives focused semantic review with model predictions withheld",
  "disagreement_handling": "Resolve from the frozen rubric and concrete semantic values. Reader disagreement alone never establishes input ambiguity.",
  "ambiguity_exclusion": "Requires recorded materially competing referents or feature interpretations that the frozen scope conventions cannot resolve",
  "invalid_exclusion": "Requires concrete absent/inapplicable entity or requested feature information wholly unavailable in at least one caption; partial recoverable values in both captions can justify 3.",
  "label_freeze": "Complete all semantic resolutions and hash the final audit before rescoring models",
  "preservation": "Original labels, V1/V2/V3 versions, raw votes, fresh reviews, adjudication rationale and user anchors are preserved",
  "provenance": "Assistant-model audit with three user-adjudicated anchors",
  "validity_clarification": "Preserve Tu invalidity for wholly absent requested attributes in one caption. Broader first-draft missing-value wording was superseded before final adjudication and model scoring.",
  "grade_calibration": "Retain the current V3 numeric grade when focused review explicitly classifies the difference as calibration-only and both compared entities/features are unchanged; preserve the alternative judgment in evidence.",
  "final_quality_check": "Root manually checks proposed new exclusions and materially changed scopes before the audit hash is frozen."
}
```

## Provenance

- Source audit: [version 4.1 at commit 2fba6fac](https://github.com/pvd232/JEP/blob/2fba6facd338afe79d00507d5904b954fb301600/training_outputs/csts_validation_audit_v4_1_20261027.json).
- Source captions, exact conditions, original ratings and groups: original prepared validation partition from the pinned LivNLP released training CSV.
- Policy reference: [Tu et al., ACL 2024](https://aclanthology.org/2024.acl-long.64/), sections 3.2 and 3.3; graded scale from [Deshpande et al., EMNLP 2023](https://aclanthology.org/2023.emnlp-main.345/), Appendix C.2.
- Frozen audit SHA-256: `845ed43db26743496fbd73dd4e6453d7dd18fb54002f3d8b2a07d3fd7655c412`.
- Rubric SHA-256: `4e7b62643dace110988018c844d6c679089058619ea994439b2b957c74a61841`.
- [Machine-readable audit](csts_validation_exclusions_full_audit_v4_1_20261027.json).

The next cleanup stage follows your adjudications. This report changes documentation only.
