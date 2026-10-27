# Full audit of excluded test comparisons

**Snapshot:** `jep-csts-v1`. All **404 exclusions** appear below. Authors and peers are separate assistant contexts. The [audit index](../../datasets/csts-jep-revision-v1/EXCLUSIONS.md) defines the policy codes.

## Cases flagged for review

| ID | Check | Review question |
|---|---|---|
| `evaluation_855` | Check recorded value | A leaves slicing state unspecified. Should Extracted A describe only the unstated slice count? |
| `evaluation_1884` | Review exclusion policy | Should the stature reading follow frozen train_11207, or should stature and jump elevation remain competing features? |
| `evaluation_2450` | Review exclusion policy | Does the stated three-color coat supply partial color information under the colorful convention accepted for train_10852? |

## All 404 excluded comparisons

### 001. evaluation_0: `number of persons`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person standing on a sidewalk holding a sandwich that has carrots on it.
>
> **Caption B:** A dish served containing pickles, tomatoes, and bread with a side of french fries.
>
> **Adopted scope:** person count
>
> **Extracted A:** one
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The food-only second caption supplies neither a person nor a supported zero count.

**Audit explanation:** B describes food. Human presence and person count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 002. evaluation_4: `people's demeanor`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An older man holding a glass of wine while standing between two beautiful ladies.
>
> **Caption B:** a group of people gather around a table with bottles and glasses of wine.
>
> **Adopted scope:** people demeanor
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Holding wine and gathering do not identify an emotional or behavioral demeanor.

**Audit explanation:** Holding wine and gathering identify actions. Both groups' demeanor remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 003. evaluation_5: `number of bottles`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An older man holding a glass of wine while standing between two beautiful ladies.
>
> **Caption B:** a group of people gather around a table with bottles and glasses of wine.
>
> **Adopted scope:** bottle count
>
> **Extracted A:** unspecified
>
> **Extracted B:** plural bottles
>
> **Recorded reason, verbatim:** A wine glass does not establish any bottle count in the first scene.

**Audit explanation:** A identifies a wine glass. Bottle count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 004. evaluation_7: `animal presence`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A monkey mug in front of a computer with a stuffed penguin beside it.
>
> **Caption B:** A laptop computer sitting on top of a table next to two computer monitors.
>
> **Adopted scope:** animal presence
>
> **Extracted A:** animal-shaped objects
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Animal-shaped objects are not actual animals, and the second gives no animal-presence information.

**Audit explanation:** A describes animal-shaped objects. Actual animal presence remains unspecified in both captions.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 005. evaluation_20: `number of people in room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a room with a brown sofa,computer on a table next to a window and a red book shelf
>
> **Caption B:** A bedroom with a purple light behind on the wall and flowers in front of a bed area that is on the floor.
>
> **Adopted scope:** room people count
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither furnished room establishes occupants or their absence.

**Audit explanation:** Both room descriptions leave human presence and person count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 006. evaluation_23: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A fire hydrant at a crossroads intersection. The hydrant looks like its fading with age.
>
> **Caption B:** There is a large access panel in the sidewalk next to the fire hydrant.
>
> **Adopted scope:** people count
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Hydrant descriptions do not supply a human count or supported absence.

**Audit explanation:** Both hydrant descriptions leave human presence and person count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 007. evaluation_26: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A red and a black laptop on a round black table near two people sitting down.
>
> **Caption B:** Some sort of mechanical device with a key board is hooked up to something like a tablet.
>
> **Adopted scope:** people count
>
> **Extracted A:** two
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second equipment description contains no recoverable person count.

**Audit explanation:** B describes equipment. Human presence and person count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 008. evaluation_28: `type of meal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** This dinner platter has roast beef and mashed potatoes with gravy, vegetables, greens, and bread.
>
> **Caption B:** Food sirs on a blue paisley plate on top of a Christmas themed table cloth.
>
> **Adopted scope:** meal type
>
> **Extracted A:** roast dinner
>
> **Extracted B:** unspecified food
>
> **Recorded reason, verbatim:** A Christmas tablecloth and unspecified food do not establish the second meal's course or category.

**Audit explanation:** B leaves the meal category unspecified. Christmas tablecloth decoration concerns another object.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 009. evaluation_29: `variety of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** This dinner platter has roast beef and mashed potatoes with gravy, vegetables, greens, and bread.
>
> **Caption B:** Food sirs on a blue paisley plate on top of a Christmas themed table cloth.
>
> **Adopted scope:** food variety types
>
> **Extracted A:** beef potatoes vegetables greens and bread
>
> **Extracted B:** food types unstated
>
> **Recorded reason, verbatim:** Generic food supplies no food-type identities in the second caption.

**Audit explanation:** B leaves food identities unspecified, preventing comparison with A's named foods.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 010. evaluation_31: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A black and white photo of surfers walking along the shore with their surfboards.
>
> **Caption B:** A person on a surfboard with their hands up at the peak of a small wave in the water.
>
> **Adopted scope:** surfboard color
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Monochrome photography does not specify surfboard colors, and neither caption supplies them.

**Audit explanation:** Both surfboard colors remain unspecified. Monochrome photographic style leaves actual board colors unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 011. evaluation_33: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A bicycle in a store window reflecting images of the cars and building across from it.
>
> **Caption B:** A blue bike is chained to a pole while a brown and black dog sits in a window.
>
> **Adopted scope:** bike color
>
> **Extracted A:** unspecified
>
> **Extracted B:** blue
>
> **Recorded reason, verbatim:** The first bicycle's color is unstated; the reflection adds no bicycle color.

**Audit explanation:** A leaves bicycle color unspecified. B identifies a blue bicycle.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 012. evaluation_43: `different activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An interesting living room with futuristic furniture and garish curtains with metallic red polka dots.
>
> **Caption B:** A flat screen TV sitting on top of a wooden table in front of a window.
>
> **Adopted scope:** activity
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither static room description establishes an activity.

**Audit explanation:** Both furnished-room descriptions leave activity unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 013. evaluation_57: `material of walls`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A hotel bedroom with stone walls, a bed with plain white linen, and a wall-mounted heating and air conditioning unit.
>
> **Caption B:** A bed with a white comforter sits in a room with red print on the walls.
>
> **Adopted scope:** wall material
>
> **Extracted A:** stone
>
> **Extracted B:** unspecified printed walls
>
> **Recorded reason, verbatim:** A red print describes surface appearance, not the wall's construction material.

**Audit explanation:** B identifies printed walls. Their construction material remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 014. evaluation_61: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A surf board sticking up out of the sand in front of the shoreline.
>
> **Caption B:** A beach with two surfers holding boards and single board laying in the sand.
>
> **Adopted scope:** people count
>
> **Extracted A:** unspecified
>
> **Extracted B:** two surfers
>
> **Recorded reason, verbatim:** A lone board does not establish whether or how many people are present.

**Audit explanation:** A identifies a board. Human presence and person count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 015. evaluation_63: `name of action`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dining table next to a den with chairs, a couch and a television.
>
> **Caption B:** A view of the inside of a house with chair, television, clock, pictures, and other items.
>
> **Adopted scope:** action
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The furnishings and views describe no action.

**Audit explanation:** Both furniture descriptions leave an action being performed unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 016. evaluation_65: `kitchen`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** An oak table and chairs in a dining room, with an open doorway into the kitchen.
>
> **Caption B:** Three couches positioned around a coffee table near a window in a living room.
>
> **Adopted scope:** kitchen type
>
> **Extracted A:** kitchen adjoining dining room
>
> **Extracted B:** absent
>
> **Recorded reason, verbatim:** A living room description supplies no kitchen entity or information about its presence.

**Audit explanation:** B establishes a living room. The required kitchen remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 017. evaluation_73: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A blond haired woman surf in blue short holds her board near the shore.
>
> **Caption B:** A person carrying a surfboard into the waves near another person floating on a surfboard.
>
> **Adopted scope:** surfboard color
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Blue shorts describe clothing; no surfboard color is given in either caption.

**Audit explanation:** Both surfboard colors remain unspecified. Blue describes the woman's shorts.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 018. evaluation_78: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a bench sitting in a yard with a little pond and a lot of pretty flowers
>
> **Caption B:** The wooden bench is framed by a pair of bushes and a young tree.
>
> **Adopted scope:** bench color
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified wood
>
> **Recorded reason, verbatim:** The first gives no color, and wooden material alone does not establish a bench color.

**Audit explanation:** Both bench colors remain unspecified. Wood identifies material.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 019. evaluation_88: `grazes in field`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The sun shines over the tree top while a horse grazes in a field.
>
> **Caption B:** A group of live stock some sheep geese and cows are outside in a field.
>
> **Adopted scope:** grazing in field
>
> **Extracted A:** horse grazing
>
> **Extracted B:** livestock in field, grazing unstated
>
> **Recorded reason, verbatim:** The second animals' field presence does not establish that they are grazing.

**Audit explanation:** B locates livestock in a field. Grazing remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 020. evaluation_89: `activity of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The sun shines over the tree top while a horse grazes in a field.
>
> **Caption B:** A group of live stock some sheep geese and cows are outside in a field.
>
> **Adopted scope:** animal activity
>
> **Extracted A:** grazing
>
> **Extracted B:** standing outdoors unspecified activity
>
> **Recorded reason, verbatim:** The second caption places animals in a field without specifying an activity.

**Audit explanation:** B locates livestock outdoors. Their activity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 021. evaluation_92: `color of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cluttered office space with a work desk under bare windows and tightly crowded furniture.
>
> **Caption B:** A pea green room with a couch, a table, a TV and a bookshelf.
>
> **Adopted scope:** room color
>
> **Extracted A:** unspecified
>
> **Extracted B:** pea green
>
> **Recorded reason, verbatim:** The first office description contains no room color.

**Audit explanation:** A describes clutter and furniture. Room color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 022. evaluation_99: `presence of toilet`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man setting in a bathroom with black and white tiles and a sink.
>
> **Caption B:** a male in a black shirt taking a photo in a mirror and a sink
>
> **Adopted scope:** toilet presence
>
> **Extracted A:** bathroom without toilet mention
>
> **Extracted B:** sink mirror without toilet mention
>
> **Recorded reason, verbatim:** Bathroom context alone does not establish a described toilet, and neither caption supplies one.

**Audit explanation:** Both bathroom descriptions leave toilet presence unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 023. evaluation_102: `size of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A small dog that is lying down half in the back crack of a sofa
>
> **Caption B:** A cat is curled up in it's cat bed and peeking over the top.
>
> **Adopted scope:** animal size
>
> **Extracted A:** small
>
> **Extracted B:** unspecified cat
>
> **Recorded reason, verbatim:** Curling up in a cat bed provides posture but no body-size or build descriptor.

**Audit explanation:** B identifies a cat. Its size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 024. evaluation_107: `name of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** Three slices of french toast and hash browns are cooking on a kitchen grill.
>
> **Caption B:** Dozens of hot dogs cooking on a commercial stovetop next to a pot of chili
>
> **Adopted scope:** animal type
>
> **Extracted A:** absent
>
> **Extracted B:** absent hotdogs are food
>
> **Recorded reason, verbatim:** Hot dogs are food; neither caption identifies an actual animal.

**Audit explanation:** Both captions establish food. The required actual animal remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 025. evaluation_113: `name of plaid pattern`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** a man in a red and white plaid shirt a sandwich and some French fries
>
> **Caption B:** A hotdog with onions on its wrapper by a soda cup on a table.
>
> **Adopted scope:** plaid pattern
>
> **Extracted A:** red white plaid
>
> **Extracted B:** absent
>
> **Recorded reason, verbatim:** Only the first supplies any plaid pattern; the second has none.

**Audit explanation:** B describes food and a cup. A plaid item and its pattern remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 026. evaluation_115: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bed in a bedroom next to a black shelf with a TV on it.
>
> **Caption B:** A child's bedroom with two single beds, stuffed animals, decorative pillows and a wooden desk and chair.
>
> **Adopted scope:** people count
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Beds and bedroom furnishings supply no person count.

**Audit explanation:** Both bedroom descriptions leave human presence and person count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 027. evaluation_119: `reason for riding`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Police officers on motorcycles on roadway with large patriotic flags on back of motorcycles at outdoor event.
>
> **Caption B:** A lot of bikers with similar bikes and gear are moving in formation up the street.
>
> **Adopted scope:** riding purpose
>
> **Extracted A:** patriotic event police participation
>
> **Extracted B:** formation ride unspecified purpose
>
> **Recorded reason, verbatim:** Riding in formation does not establish why the second group rides.

**Audit explanation:** B's formation ride leaves the purpose of riding unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 028. evaluation_121: `color of boat`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An orange and blue passenger boat floats in the canal, making it's way past other boats that are docked there.
>
> **Caption B:** A boat docked at a pier with a red bench and steps to a house.
>
> **Adopted scope:** boat color
>
> **Extracted A:** orange blue
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The red bench is separate from the second boat, whose color is unstated.

**Audit explanation:** B gives bench color. Boat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 029. evaluation_124: `number of animals`

**Current status:** `excluded_scope`. **Semantic rating:** `excluded/null`. **Policy:** `S7`.

> **Caption A:** A horse is running through water that seems to be marked in some way.
>
> **Caption B:** A man rides a horse while a crows watches from the other side of a pond.
>
> **Adopted scope:** nonhuman animal count with unresolved corrupted source word
>
> **Extracted A:** one horse
>
> **Extracted B:** one horse plus either a crow or a human crowd
>
> **Recorded reason, verbatim:** The source phrase 'a crows watches' admits both crow and crowd repairs, which change the requested animal count. The captions do not determine which repair is intended.

**Audit explanation:** B's corrupted phrase admits crow and crowd readings, producing two animals or one. The intended count remains unresolved.

**Recorded scope readings:**

> - **crowd repair:** rating 5.
> - **crow repair:** rating 1.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 030. evaluation_133: `presence of television`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Living room scene, light/off white tones, brown coffee table in front of fire place, well lit, sunlight coming in from windows.
>
> **Caption B:** a living room with a cow pattern throw rug, a couch, a television and a fireplace.
>
> **Adopted scope:** TV presence
>
> **Extracted A:** unspecified
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** The first living room does not state whether a television is present.

**Audit explanation:** A describes a living room. Television presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 031. evaluation_139: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A blender covered with green ooze next to a cup with even more green ooze.
>
> **Caption B:** A kitchen stove with a pan on it, and a counter full of kitchenware.
>
> **Adopted scope:** object color
>
> **Extracted A:** green coating on blender
>
> **Extracted B:** unspecified stove
>
> **Recorded reason, verbatim:** The first green coating is observable, but the second appliance has no color information.

**Audit explanation:** B identifies a stove and kitchenware. Their colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 032. evaluation_140: `number of people observed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A city scene features public transit, cars, bikers and pedestrians surrounded by traffic signals and crosswalks.
>
> **Caption B:** A white van is riding past on a city street with residential and storefront buildings in the background.
>
> **Adopted scope:** people count
>
> **Extracted A:** multiple bikers pedestrians
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** A moving van does not supply the number of observed people in the second caption.

**Audit explanation:** B describes a moving van. Human presence and person count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 033. evaluation_145: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a woman sitting next to a table, with an open laptop in the other chair
>
> **Caption B:** A table with green tablecloth and three chairs in the corner of a room with a laptop on the table.
>
> **Adopted scope:** people count
>
> **Extracted A:** one woman
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second table and chairs description does not establish occupants or zero occupants.

**Audit explanation:** B describes furniture and a laptop. Human presence and person count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 034. evaluation_146: `color of counter`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** a nice black back splash a plant  some body oils and a black Kleenex box
>
> **Caption B:** a plain white bathroom with small personal care items lined on the bare white counter
>
> **Adopted scope:** counter color
>
> **Extracted A:** unspecified black backsplash
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** The black backsplash is not the countertop; the first counter color remains unstated.

**Audit explanation:** A gives backsplash and tissue-box colors. Counter color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 035. evaluation_152: `contents on tray`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A plastic tray that has a plate with food and a mug on it.
>
> **Caption B:** A cup of coffee and a do nut covered in springles  sit on a plate in a coffee shop.
>
> **Adopted scope:** tray contents
>
> **Extracted A:** plate food mug
>
> **Extracted B:** no tray stated
>
> **Recorded reason, verbatim:** The second specifies a plate but no tray whose contents could be extracted.

**Audit explanation:** B establishes food on a plate. A tray and its contents remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 036. evaluation_155: `structure function`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The damaged facade of an elderly building is marked by a number of pipes, a sign and an ornamental iron grate.
>
> **Caption B:** An old wall with mud plaster and a road sign board in front of it.
>
> **Adopted scope:** structure function
>
> **Extracted A:** unspecified building
>
> **Extracted B:** unspecified wall
>
> **Recorded reason, verbatim:** Neither building description states its use or function.

**Audit explanation:** Both structure descriptions leave function unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 037. evaluation_158: `presence of traffic signs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A red car and red stoplight stand out in a black and white urban scene.
>
> **Caption B:** A stop sign stands at an empty intersection with a lot of bushes and trees.
>
> **Adopted scope:** presence of traffic signs
>
> **Extracted A:** traffic signal stated, sign presence unstated
>
> **Extracted B:** stop sign present
>
> **Recorded reason, verbatim:** A traffic light does not establish a traffic sign, and silence does not establish its absence.

**Audit explanation:** A establishes a traffic light. Traffic-sign presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 038. evaluation_159: `color of car`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A red car and red stoplight stand out in a black and white urban scene.
>
> **Caption B:** A stop sign stands at an empty intersection with a lot of bushes and trees.
>
> **Adopted scope:** car color
>
> **Extracted A:** red
>
> **Extracted B:** car absent
>
> **Recorded reason, verbatim:** The second intersection description supplies no car to compare.

**Audit explanation:** B identifies an intersection and sign. A car and its color remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 039. evaluation_175: `size of pizza`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** What appears to be a small pizza is topped with some sort of leafy tooping.
>
> **Caption B:** A pizza sitting on top of a white plate on top of brown paper.
>
> **Adopted scope:** pizza size
>
> **Extracted A:** small
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The plate and paper do not establish the second pizza's size.

**Audit explanation:** B identifies a pizza. Its size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 040. evaluation_176: `action at location`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A picture of street signs and lamp carve out the building across the streets structural details .
>
> **Caption B:** A street sign at Seymour street and a traffic light stand in front of a skyscraper.
>
> **Adopted scope:** location action
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither static street description establishes an action at the location.

**Audit explanation:** Both street-sign scenes leave an action taking place unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 041. evaluation_184: `color of jacket`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man is dressed in a blazer, tie, and khakis in front of a building.
>
> **Caption B:** This shows a man from the neck down wearing a bright red jacket, gingham checked shirt and tie.
>
> **Adopted scope:** jacket color
>
> **Extracted A:** unspecified blazer
>
> **Extracted B:** red
>
> **Recorded reason, verbatim:** A blazer's color is not supplied by the first caption.

**Audit explanation:** A identifies a blazer. Its color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 042. evaluation_187: `number of beverages`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A lunch tray filled with a variety of dinner foods such as spaghetti, and mashed pototoes with corn.
>
> **Caption B:** A black table holds white bowls and plates and different foods as water glasses also sit on the table.
>
> **Adopted scope:** beverage count
>
> **Extracted A:** unspecified
>
> **Extracted B:** plural water glasses
>
> **Recorded reason, verbatim:** The first lunch tray has no beverage or drinking vessel to support beverage inference.

**Audit explanation:** A describes tray food. Beverage count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 043. evaluation_189: `occupancy of bed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a person in bed with a sheet over them and lights on the bed on.
>
> **Caption B:** A bed in a bedroom covered in clutter between two tables with lamps on them.
>
> **Adopted scope:** human occupancy of bed
>
> **Extracted A:** occupied by person
>
> **Extracted B:** clutter present, human occupancy unstated
>
> **Recorded reason, verbatim:** Clutter on a bed does not establish whether a person occupies it.

**Audit explanation:** B establishes bed clutter. Human occupancy remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 044. evaluation_190: `activity of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A man sitting in a chair on top of a beach under an umbrella.
>
> **Caption B:** A pair of chairs shaded by a large orange umbrella on a sunny beach
>
> **Adopted scope:** people activity
>
> **Extracted A:** sitting
>
> **Extracted B:** no people stated
>
> **Recorded reason, verbatim:** Chairs and shade do not establish people performing an activity in the second scene.

**Audit explanation:** B identifies chairs and an umbrella. People and their activity remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 045. evaluation_191: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A man sitting in a chair on top of a beach under an umbrella.
>
> **Caption B:** A pair of chairs shaded by a large orange umbrella on a sunny beach
>
> **Adopted scope:** umbrella color
>
> **Extracted A:** unspecified
>
> **Extracted B:** orange
>
> **Recorded reason, verbatim:** Only the second umbrella's color is provided.

**Audit explanation:** A leaves umbrella color unspecified. B identifies orange.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 046. evaluation_195: `size of clock`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A photo taken in the night of a tall building in the distance with an illuminated clock.
>
> **Caption B:** there is a tall tower that has a clock at the top of it
>
> **Adopted scope:** clock size
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Tall buildings do not identify the clocks' sizes.

**Audit explanation:** Both clock sizes remain unspecified. Tower dimensions concern the surrounding structure.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 047. evaluation_200: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Fluffy pins back his ears and growls a warning at the weird cat in the mirror.
>
> **Caption B:** a cat sitting  in front of a mirror in front of a person holding a camera.
>
> **Adopted scope:** people count
>
> **Extracted A:** unspecified
>
> **Extracted B:** one
>
> **Recorded reason, verbatim:** The first cat-and-mirror scene supplies no human count.

**Audit explanation:** A describes a cat and reflection. Person count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 048. evaluation_202: `reflective quality of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman sits on the floor in front of a bookcase typing on a laptop.
>
> **Caption B:** A laptop keyboard with its reflection of it and a book in the screen.
>
> **Adopted scope:** laptop reflectivity
>
> **Extracted A:** unspecified
>
> **Extracted B:** reflection in screen
>
> **Recorded reason, verbatim:** No reflection or reflective property is stated for the first laptop.

**Audit explanation:** A describes laptop use. Laptop reflectivity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 049. evaluation_205: `color of cat`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A cat reaches up a paw to touch a dog on a television screen.
>
> **Caption B:** A black and white cat sitting in front of a computer looking at the mouse.
>
> **Adopted scope:** cat color
>
> **Extracted A:** unspecified
>
> **Extracted B:** black white
>
> **Recorded reason, verbatim:** The first cat has no stated color.

**Audit explanation:** A identifies a cat. Coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 050. evaluation_206: `types of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Corn on the cob, salad, and a potato dish are being served on a table.
>
> **Caption B:** A plate of food, dishes with food, and a pot of flowers sitting on top of a table.
>
> **Adopted scope:** food types
>
> **Extracted A:** corn salad and potatoes
>
> **Extracted B:** food types unstated
>
> **Recorded reason, verbatim:** The second caption names only food, not any requested food type.

**Audit explanation:** B identifies food in dishes. Food categories remain unnamed.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 051. evaluation_212: `name of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A small child opening their mouth for a donut that is being dangled above them.
>
> **Caption B:** A little girl sitting at a table with a half eaten donut in front of her.
>
> **Adopted scope:** person name
>
> **Extracted A:** unnamed child
>
> **Extracted B:** unnamed girl
>
> **Recorded reason, verbatim:** Neither child has a personal name in the captions.

**Audit explanation:** Both children's personal names remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 052. evaluation_221: `number of kitchen appliances`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A kitchen with nice wooden cabinets and flooring, but with one cabinet door missing.
>
> **Caption B:** A kitchen that has a grey tile floor with granite counter top and a silver stove and a silver refrigerator.
>
> **Adopted scope:** appliance count
>
> **Extracted A:** unspecified
>
> **Extracted B:** stove refrigerator two
>
> **Recorded reason, verbatim:** Cabinets and floors do not establish any kitchen appliance count in the first.

**Audit explanation:** A identifies cabinets and flooring. Kitchen-appliance count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 053. evaluation_235: `number of appliances`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** View of a kitchen island with a sink in the middle and a book case at the end cap.
>
> **Caption B:** A kitchen has white cabinets, wood floors, pots above the sink, and black appliances.
>
> **Adopted scope:** appliance count
>
> **Extracted A:** unspecified
>
> **Extracted B:** plural appliances
>
> **Recorded reason, verbatim:** A sink and kitchen island do not identify a count of appliances.

**Audit explanation:** A identifies an island, sink and bookcase. Kitchen-appliance count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 054. evaluation_236: `room decor and furniture style`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A large room with tile flooring and four pieces of furniture on a Persian style carpet.
>
> **Caption B:** A room decorated with multiple rocking chairs and lots of art on the walls.
>
> **Adopted scope:** room decor and furniture style
>
> **Extracted A:** Persian-style rug with otherwise unspecified furniture
>
> **Extracted B:** rocking chairs and wall art, overall style unstated
>
> **Recorded reason, verbatim:** Specific furnishing types alone do not establish a comparable overall decor style.

**Audit explanation:** B identifies rocking chairs and art. Overall decor and furniture style remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 055. evaluation_237: `position of art`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A large room with tile flooring and four pieces of furniture on a Persian style carpet.
>
> **Caption B:** A room decorated with multiple rocking chairs and lots of art on the walls.
>
> **Adopted scope:** art position
>
> **Extracted A:** unspecified
>
> **Extracted B:** walls
>
> **Recorded reason, verbatim:** The first supplies furniture and a carpet but no artwork position.

**Audit explanation:** A identifies furniture and carpet. Artwork and its position remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 056. evaluation_245: `interaction of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two pictures of a white and black spotted cat and a orange, white and black spotted cat in front of a bathroom mirror.
>
> **Caption B:** Two cats one on their back, one over top of the other, playing together on a bed.
>
> **Adopted scope:** animal interaction
>
> **Extracted A:** none specified mirror photos
>
> **Extracted B:** playing together
>
> **Recorded reason, verbatim:** Two cats described in photographs need not be interacting; no first-side interaction is stated.

**Audit explanation:** A locates cats near a mirror. Their interaction remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 057. evaluation_249: `number of men`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man with a bat raring back as another man holds up his glove.
>
> **Caption B:** A pitch just about to cross a plate and a second before the hitter decides to swing or not.
>
> **Adopted scope:** men count
>
> **Extracted A:** two
>
> **Extracted B:** hitter gender unspecified
>
> **Recorded reason, verbatim:** Hitter identifies a role but does not establish male gender.

**Audit explanation:** B identifies a hitter. Male gender and men count remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 058. evaluation_257: `presence of toys`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A teddy bear sitting on the edge of a toilet seat in a bathroom.
>
> **Caption B:** A porcelain toilet with a square lid in a bathroom with blue tiled walls.
>
> **Adopted scope:** toy presence
>
> **Extracted A:** teddy bear
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second bathroom description neither supplies a toy nor supports its absence.

**Audit explanation:** B describes a toilet. Toy presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 059. evaluation_262: `color of sky`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman with her arms above her head holding into strings for a kite shaped like a hamburger.
>
> **Caption B:** Man playing with kite far up in the sky, showing only the deep blue sky.
>
> **Adopted scope:** sky color
>
> **Extracted A:** unspecified
>
> **Extracted B:** deep blue
>
> **Recorded reason, verbatim:** The first kite description does not supply a sky color.

**Audit explanation:** A describes kite flying. Sky color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 060. evaluation_267: `type of cooking`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** In this house with low ceilings, the man is cooking  on an old  iron stove
>
> **Caption B:** A man with an apron in a kitchen with fridge and bottles of wine
>
> **Adopted scope:** cooking type
>
> **Extracted A:** stove cooking unspecified method
>
> **Extracted B:** apron kitchen unspecified cooking
>
> **Recorded reason, verbatim:** An apron in a kitchen does not establish the second cooking method or action.

**Audit explanation:** B establishes an apron and kitchen. Ongoing cooking and cooking method remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 061. evaluation_274: `type of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A couch sitting in a living room under a clock on a wood floor.
>
> **Caption B:** A bright, sunny room containing chairs, a table, a plant and some other items
>
> **Adopted scope:** room type
>
> **Extracted A:** living room
>
> **Extracted B:** furnished room uncertain subtype
>
> **Recorded reason, verbatim:** Chairs, table and plant alone do not establish a room function, following confirmed #31.

**Audit explanation:** B's chairs, table and plant leave room function unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 062. evaluation_276: `drink`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A table topped with two white plates of food next to glasses filled with drinks.
>
> **Caption B:** A plate full of cut salad with a fork and a glass full of cold drink with ice.
>
> **Adopted scope:** drink type
>
> **Extracted A:** unspecified beverages
>
> **Extracted B:** cold beverage with contents unspecified
>
> **Recorded reason, verbatim:** The first only repeats the beverage category and supplies no drink type.

**Audit explanation:** Both drink types remain unspecified. Coldness and ice identify temperature and presentation.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 063. evaluation_278: `room size`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** This rustic style kitchen has storage for lots of cookware and  gadgets for the avid cook.
>
> **Caption B:** A narrow kitchen and dining room utilizes the flow of neutral paint to offset clutter.
>
> **Adopted scope:** room size
>
> **Extracted A:** unspecified
>
> **Extracted B:** narrow
>
> **Recorded reason, verbatim:** Ample storage does not determine the first room's size or width.

**Audit explanation:** A describes storage and rustic style. Room size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 064. evaluation_290: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A picture taken of the nose of an airplane which is sitting on a runway.
>
> **Caption B:** A plane parked in front of a yellow line with people leaving the plane.
>
> **Adopted scope:** people count
>
> **Extracted A:** unspecified
>
> **Extracted B:** plural people
>
> **Recorded reason, verbatim:** An aircraft nose on a runway does not establish a person count.

**Audit explanation:** A describes an airplane. Human presence and person count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 065. evaluation_296: `gps location`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a dual shot featuring a bathroom containing a toilet, a sink, and a shower.
>
> **Caption B:** Part of a living room with a mirror sitting on a mantel over an unused fireplace.
>
> **Adopted scope:** GPS location
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither interior supplies GPS coordinates or geographic identity.

**Audit explanation:** Both domestic interiors leave geographic coordinates unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 066. evaluation_299: `room state`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A messy kitchen with a table, stove, open cabinet doors and books on the table.
>
> **Caption B:** View of a kitchen and computer with a sheet of plywood on the back of a counter.
>
> **Adopted scope:** room state
>
> **Extracted A:** messy
>
> **Extracted B:** unspecified plywood on counter
>
> **Recorded reason, verbatim:** Plywood behind a counter does not establish how tidy the second room is.

**Audit explanation:** B's plywood and computer leave kitchen cleanliness and tidiness unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 067. evaluation_301: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bear with a scuffed up nose looks just over an old tree log.
>
> **Caption B:** A brown bear sits on its bottom with its back again a big rock at the zoo.
>
> **Adopted scope:** bear color
>
> **Extracted A:** unspecified
>
> **Extracted B:** brown
>
> **Recorded reason, verbatim:** A scuffed nose does not supply the first bear's color.

**Audit explanation:** A describes a bear's nose and location. Coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 068. evaluation_306: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young man wearing a green shirt and black shorts skateboards in a skateboarding park.
>
> **Caption B:** A skateboarder on a concrete ramp doing a trick where he is in the air with the board.
>
> **Adopted scope:** clothing color
>
> **Extracted A:** green black
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second skateboarder has no clothing colors stated.

**Audit explanation:** B identifies a skateboarder. Clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 069. evaluation_313: `size of pizza`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A pizza cut four ways with one big slice equal to half the pie.
>
> **Caption B:** A delicious single pizza on a pizza pan waiting for someone to taste it.
>
> **Adopted scope:** pizza size
>
> **Extracted A:** unspecified whole size
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** A slice's proportion of a pizza does not establish the whole pizza's size.

**Audit explanation:** Both whole-pizza sizes remain unspecified. Relative slice fractions leave overall scale unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 070. evaluation_315: `size of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A living room with a large open floor plan that leads to sliding glass doors and a patio.
>
> **Caption B:** A living room with a couch and pillows in front of a flat screen Tv.
>
> **Adopted scope:** room size
>
> **Extracted A:** large
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second living room has no size descriptor.

**Audit explanation:** B describes furniture. Living-room size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 071. evaluation_327: `size of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A kitchen features brown wooden cabinets, polished stone counter tops, hardwood floors, and stainless steel appliances.
>
> **Caption B:** A large kitchen with two white ovens sitting next to a white microwave oven.
>
> **Adopted scope:** room size
>
> **Extracted A:** unspecified
>
> **Extracted B:** large
>
> **Recorded reason, verbatim:** The first kitchen's materials and appliances do not establish room size.

**Audit explanation:** A lists materials and appliances. Kitchen size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 072. evaluation_338: `type of material`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man pulls a suitcase and a woman pulls a bag with a child on it.
>
> **Caption B:** A man pushing a cart with luggage on top of it in an airport.
>
> **Adopted scope:** material
>
> **Extracted A:** unspecified luggage material
>
> **Extracted B:** unspecified luggage material
>
> **Recorded reason, verbatim:** Neither caption identifies luggage material.

**Audit explanation:** Both luggage materials remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 073. evaluation_341: `amount of focus`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A tennis player with a skip in his step is aiming to hit the ball.
>
> **Caption B:** A man is standing on a tennis court celebrating with a racket in the air.
>
> **Adopted scope:** focus amount
>
> **Extracted A:** aiming focused
>
> **Extracted B:** celebration unspecified focus
>
> **Recorded reason, verbatim:** Celebration does not state how focused the second player is.

**Audit explanation:** B identifies celebration. The player's degree of focus remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 074. evaluation_350: `presence of electronics`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A plate of pizza sits on a table near a plate of vegetables and french fries.
>
> **Caption B:** A desk with a keyboard on it and several containers of food in front of the keyboard.
>
> **Adopted scope:** electronics presence
>
> **Extracted A:** unspecified
>
> **Extracted B:** keyboard
>
> **Recorded reason, verbatim:** The first meal-table caption supplies no electronics-presence information.

**Audit explanation:** A describes food and a table. Electronics presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 075. evaluation_355: `presence of human`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a black shirt is lying on a bed with his two cats.
>
> **Caption B:** A bed with a red sheet set with a laptop and covers on it.
>
> **Adopted scope:** human presence
>
> **Extracted A:** man present
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second bed's laptop and covers do not establish human absence.

**Audit explanation:** B describes a bed and laptop. Human presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 076. evaluation_359: `action of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a zebra up close to a car window with a person taking a photo
>
> **Caption B:** A group of adult zebra's and one young zebra standing in a open field.
>
> **Adopted scope:** animal action
>
> **Extracted A:** zebra close to window, action unstated
>
> **Extracted B:** zebras standing
>
> **Recorded reason, verbatim:** Proximity to a car does not determine whether the first zebra is standing, approaching or performing another action.

**Audit explanation:** A locates a zebra near a window. The zebra's action remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 077. evaluation_360: `type of computer`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man sitting on a  chair while holding a cat and a laptop computer.
>
> **Caption B:** Here is acat that has fallen asleep on the lap of someone who is working on a computer.
>
> **Adopted scope:** computer subtype
>
> **Extracted A:** laptop
>
> **Extracted B:** computer subtype unstated
>
> **Recorded reason, verbatim:** A cat on the worker's lap does not establish where or what type the computer is.

**Audit explanation:** B establishes computer use. Computer subtype remains unspecified despite the cat's position on a lap.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 078. evaluation_362: `color of objects`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A living room area with a couch, loveseat, table and small bookcase in the center of the room.
>
> **Caption B:** A tidy room has a white sofa, monitor, window and a coffee table with a glass of wine on it.
>
> **Adopted scope:** furnishing colors
>
> **Extracted A:** unspecified
>
> **Extracted B:** white sofa
>
> **Recorded reason, verbatim:** The first furnishings have no stated colors.

**Audit explanation:** A describes furnishings. Their colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 079. evaluation_371: `activity of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Several no parking signs arranged on a pole near a city street with a large building behind them.
>
> **Caption B:** A street sign informing the public to walk their bikes across the street rather than ride them.
>
> **Adopted scope:** person activity
>
> **Extracted A:** none stated
>
> **Extracted B:** none stated
>
> **Recorded reason, verbatim:** A sign's instruction does not establish that a person is performing it.

**Audit explanation:** Both signs state rules. People and their current actions remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 080. evaluation_375: `name of baby`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A baby laying on it's back with a piece of lettuce in it's mouth.
>
> **Caption B:** A blue eyed baby eating a cut in half banana while wearing a bib.
>
> **Adopted scope:** baby name
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither baby is personally named.

**Audit explanation:** Both babies' personal names remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 081. evaluation_376: `bread type`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white plate topped with a hamburger and fried egg next to a pile of fries.
>
> **Caption B:** A large sandwich, fries, and a soda sit on a table in a restaurant.
>
> **Adopted scope:** bread type
>
> **Extracted A:** hamburger bun
>
> **Extracted B:** sandwich bread type unstated
>
> **Recorded reason, verbatim:** The second sandwich does not identify its bread type.

**Audit explanation:** B identifies a sandwich. Bread type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 082. evaluation_377: `type of dishware`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white plate topped with a hamburger and fried egg next to a pile of fries.
>
> **Caption B:** A large sandwich, fries, and a soda sit on a table in a restaurant.
>
> **Adopted scope:** dishware
>
> **Extracted A:** plate
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second table meal does not specify a serving vessel; a table is not dishware.

**Audit explanation:** B places food on a table. Dishware type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 083. evaluation_379: `items on plate`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A rare piece of steak and some cooked vegetables on a plate with a knife and fork.
>
> **Caption B:** A ham on a cutting board with slicing knife and fork with bowls of carrots and acorn squash nearby.
>
> **Adopted scope:** plate contents
>
> **Extracted A:** steak vegetables
>
> **Extracted B:** no plate stated cutting board bowls
>
> **Recorded reason, verbatim:** The second foods are on a board and in bowls, with no plate contents established.

**Audit explanation:** B establishes food on a cutting board and in bowls. Plate contents remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 084. evaluation_380: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A women sits in bed with her white dog and she is looking at her cat.
>
> **Caption B:** A dog and a girl sit on a couch and the girl is covered by a blanket.
>
> **Adopted scope:** animal color
>
> **Extracted A:** white dog cat unspecified
>
> **Extracted B:** dog unspecified
>
> **Recorded reason, verbatim:** The second dog has no color descriptor.

**Audit explanation:** B identifies a dog. Coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 085. evaluation_382: `color of fruit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman carries a basket of bananas on her head while some men stand around.
>
> **Caption B:** A truck laden with green bananas on the road next to a small market
>
> **Adopted scope:** banana color
>
> **Extracted A:** unspecified
>
> **Extracted B:** green
>
> **Recorded reason, verbatim:** Bananas can have several ripeness colors; the first color is not recoverable.

**Audit explanation:** A identifies bananas. Their color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 086. evaluation_384: `color of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A narrow bathroom with a white toilet and a black towel hanging from a rack.
>
> **Caption B:** A blue bathroom stall with the door open so you can see the  toilet.
>
> **Adopted scope:** room color
>
> **Extracted A:** unspecified
>
> **Extracted B:** blue
>
> **Recorded reason, verbatim:** Fixture and towel colors do not identify the first room's color.

**Audit explanation:** A gives toilet and towel colors. Bathroom color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 087. evaluation_385: `color of bathroom`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A narrow bathroom with a white toilet and a black towel hanging from a rack.
>
> **Caption B:** A blue bathroom stall with the door open so you can see the  toilet.
>
> **Adopted scope:** bathroom color
>
> **Extracted A:** unspecified
>
> **Extracted B:** blue
>
> **Recorded reason, verbatim:** The first describes white and black contents but no bathroom surface color.

**Audit explanation:** A identifies a white toilet and black towel. Bathroom color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 088. evaluation_386: `stage of construction`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** an unfinished set of rooms in a house with construction materials on the floor
>
> **Caption B:** A white kitchen with cabinets left open, cardboard boxes on the floor, and bags of trash.
>
> **Adopted scope:** construction stage
>
> **Extracted A:** unfinished
>
> **Extracted B:** unspecified cluttered kitchen
>
> **Recorded reason, verbatim:** Boxes and trash may accompany construction or ordinary use, so they do not establish a construction stage.

**Audit explanation:** B's boxes, trash and open cabinets leave construction stage unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 089. evaluation_387: `state of completion`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** an unfinished set of rooms in a house with construction materials on the floor
>
> **Caption B:** A white kitchen with cabinets left open, cardboard boxes on the floor, and bags of trash.
>
> **Adopted scope:** completion state
>
> **Extracted A:** unfinished
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** A cluttered kitchen does not establish whether construction is finished.

**Audit explanation:** B describes clutter. Construction completion remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 090. evaluation_390: `type of airplane`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The back end of a plane's tail section on the tarmac of an airport.
>
> **Caption B:** An older bomber type airplane with two engines flying in the sky above the clouds.
>
> **Adopted scope:** airplane subtype
>
> **Extracted A:** airplane subtype unstated
>
> **Extracted B:** older bomber
>
> **Recorded reason, verbatim:** The first tail section and airport location do not establish an airplane subtype.

**Audit explanation:** A identifies an airplane tail and airport. Airplane subtype remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 091. evaluation_395: `color of train`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A commuter train on tracks is at a train station with only one of its two lights on
>
> **Caption B:** A yellow train is approaching on a track as people are waiting on a the platform on the side.
>
> **Adopted scope:** train color
>
> **Extracted A:** unspecified
>
> **Extracted B:** yellow
>
> **Recorded reason, verbatim:** The first train's light status supplies no body color.

**Audit explanation:** A describes train lights. Train color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 092. evaluation_403: `vehicle height`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A double-decker bus in a shopping district of a European city with an imposing castle in the background.
>
> **Caption B:** a bus in the middle of the street on a corner in a neighboorhood
>
> **Adopted scope:** bus height
>
> **Extracted A:** two decks
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The generic second bus does not reveal its deck count or height.

**Audit explanation:** B identifies a bus. Its height and deck count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 093. evaluation_412: `person explaining`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** This is a very good day for kite flying of the beach as this man will tell you.
>
> **Caption B:** The sky at the beach is filed with neon kites including turtle and fish shaped ones.
>
> **Adopted scope:** explaining person
>
> **Extracted A:** man implied narrator
>
> **Extracted B:** none described
>
> **Recorded reason, verbatim:** The second kite scene provides no explaining person.

**Audit explanation:** B describes kites. An explaining person remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 094. evaluation_419: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Three horses are in a vast meadow and two of the horses are running.
>
> **Caption B:** A brown horse standing in the middle of a field with trees in the background.
>
> **Adopted scope:** animal color
>
> **Extracted A:** unspecified
>
> **Extracted B:** brown
>
> **Recorded reason, verbatim:** The first horses have no stated colors.

**Audit explanation:** A identifies three horses. Their colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 095. evaluation_420: `floor material`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a bathroom with a sink, mirror on a tiled floor with a door open
>
> **Caption B:** A bedroom includes a neatly made bed with several cloth items in disarray near the bottom.
>
> **Adopted scope:** floor material
>
> **Extracted A:** tile
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second bedroom gives no floor material.

**Audit explanation:** B describes a bedroom. Floor material remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 096. evaluation_425: `amount of brightness`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S6`.

> **Caption A:** A room with a lot of windows, a table with a vase, and chairs.
>
> **Caption B:** A long dark wood dining table and matching chairs is the focal point of a sunlight dining room.
>
> **Adopted scope:** room brightness
>
> **Extracted A:** many windows but actual illumination unstated
>
> **Extracted B:** sunlit
>
> **Recorded reason, verbatim:** Window count establishes potential light, not the room's actual brightness.

**Audit explanation:** A's windows identify possible light sources. Actual room brightness remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 097. evaluation_432: `name of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A little baby about to get into a backpack with a lot of goodies in it.
>
> **Caption B:** A baby holding a tooth brush and tooth paste setting on a clothes washer.
>
> **Adopted scope:** person name
>
> **Extracted A:** unspecified baby
>
> **Extracted B:** unspecified baby
>
> **Recorded reason, verbatim:** Neither caption gives the baby's personal name.

**Audit explanation:** Both babies' personal names remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 098. evaluation_436: `type of items on bed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A laptop is on the bed in a room full of books and clothes.
>
> **Caption B:** A bed in a bedroom  that has lots of things sitting on top of it.
>
> **Adopted scope:** types of objects on bed
>
> **Extracted A:** laptop
>
> **Extracted B:** unnamed things
>
> **Recorded reason, verbatim:** Lots of things gives quantity but no recoverable item type.

**Audit explanation:** B's unnamed things leave object types unspecified for comparison with A's laptop.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 099. evaluation_455: `name of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A huge crowd of people with several of them flying kites in an open field.
>
> **Caption B:** A crowded park on a cloudy day shows many kites flying in the air like colorful dots.
>
> **Adopted scope:** people names
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither crowd includes personal names.

**Audit explanation:** Both groups' personal names remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 100. evaluation_459: `action of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The tail of an airplane looks like a plane in itself reaching up into the sky.
>
> **Caption B:** While the airplane is on the runway, some people are seated in folding chairs in the shadow of its wing.
>
> **Adopted scope:** aircraft action
>
> **Extracted A:** tail extending upward
>
> **Extracted B:** on runway stationary
>
> **Recorded reason, verbatim:** The tail's upward orientation does not establish what the first aircraft is doing.

**Audit explanation:** A describes the tail's upward shape. The airplane's action remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 101. evaluation_461: `presence of mirror`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a bathroom with a sink, mirror on a tiled floor with a door open
>
> **Caption B:** A bathroom with a walk in shower tub next to a sink and a toilet.
>
> **Adopted scope:** mirror presence
>
> **Extracted A:** present
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second bathroom supplies no mirror-presence information.

**Audit explanation:** B describes bathroom fixtures. Mirror presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 102. evaluation_473: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A table of delicious snacks sitting on a table that are ready to eat.
>
> **Caption B:** A table full of slices of pizza on plates with people in the background.
>
> **Adopted scope:** people count
>
> **Extracted A:** unspecified
>
> **Extracted B:** plural people
>
> **Recorded reason, verbatim:** The first snack table has no stated people or supported zero count.

**Audit explanation:** A describes snacks and a table. Human presence and person count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 103. evaluation_477: `shape of vegetables`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A decorative carrot with a bell pepper cut on top resembles a palm tree.
>
> **Caption B:** The person is using a knife to prepare a carrot that is red onions.
>
> **Adopted scope:** vegetable shape
>
> **Extracted A:** palm-tree sculpture
>
> **Extracted B:** unspecified preparation
>
> **Recorded reason, verbatim:** The second preparation description does not identify the resulting vegetable shape.

**Audit explanation:** B describes vegetable preparation. The resulting shape remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 104. evaluation_492: `type of pizza`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A square cut pizza with an assortment of toppings such as cheese and olives.
>
> **Caption B:** A whole uncut pizza on a table next to a stuffed monkey and a fork and knife.
>
> **Adopted scope:** pizza variety
>
> **Extracted A:** cheese and olive toppings
>
> **Extracted B:** variety or toppings unstated
>
> **Recorded reason, verbatim:** The second only identifies pizza and supplies no requested pizza variety.

**Audit explanation:** B identifies a pizza. Variety and toppings remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 105. evaluation_493: `shape of pizza`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A square cut pizza with an assortment of toppings such as cheese and olives.
>
> **Caption B:** A whole uncut pizza on a table next to a stuffed monkey and a fork and knife.
>
> **Adopted scope:** pizza shape
>
> **Extracted A:** square-cut slices
>
> **Extracted B:** unspecified whole shape
>
> **Recorded reason, verbatim:** Square cutting describes pieces; the second whole pizza's outline is unstated.

**Audit explanation:** B identifies a whole, uncut pizza. Its overall shape remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 106. evaluation_495: `presence of dining area`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A kitchen and dining area with wood floors and wood cabinets, with no seperating wall for the two areas.
>
> **Caption B:** A large kitchen with two white ovens sitting next to a white microwave oven.
>
> **Adopted scope:** dining-area presence
>
> **Extracted A:** present
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second kitchen does not establish whether a dining area exists.

**Audit explanation:** B identifies a kitchen. Dining-area presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 107. evaluation_512: `size of furniture used for rest`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bed with a person half peeking over the top with one hand on bed.
>
> **Caption B:** A room with a bookcase, several books, a television and a couch in it.
>
> **Adopted scope:** resting furniture size
>
> **Extracted A:** unspecified bed
>
> **Extracted B:** unspecified couch
>
> **Recorded reason, verbatim:** Neither the bed nor couch has a size or build descriptor.

**Audit explanation:** Both resting-furniture sizes remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 108. evaluation_513: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bed with a person half peeking over the top with one hand on bed.
>
> **Caption B:** A room with a bookcase, several books, a television and a couch in it.
>
> **Adopted scope:** people count
>
> **Extracted A:** one
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second room's furnishings do not supply a human count.

**Audit explanation:** B describes furniture. Human presence and person count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 109. evaluation_516: `number of dogs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A water bowl for a pet that has a dog sitting up with the bowl on his stomach as a holder.
>
> **Caption B:** a close up of a dog jumping in the air with a frisbee in its mouth
>
> **Adopted scope:** live dog count
>
> **Extracted A:** dog-shaped bowl holder
>
> **Extracted B:** one live dog
>
> **Recorded reason, verbatim:** A dog-shaped bowl holder does not establish an actual dog to count.

**Audit explanation:** A identifies a dog-shaped bowl holder. A live dog to count remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 110. evaluation_517: `dog holding property`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A water bowl for a pet that has a dog sitting up with the bowl on his stomach as a holder.
>
> **Caption B:** a close up of a dog jumping in the air with a frisbee in its mouth
>
> **Adopted scope:** live dog held object
>
> **Extracted A:** decorative dog bowl holder
>
> **Extracted B:** frisbee
>
> **Recorded reason, verbatim:** The first holder is a decorative dog representation, not a live dog holding an object.

**Audit explanation:** A identifies a decorative bowl holder. A live dog holding an object remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 111. evaluation_519: `bottle of wine`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person sitting down with a laptop on a lap pillow in their lap.
>
> **Caption B:** there is a bottle of whine next to a lap top on a desk
>
> **Adopted scope:** wine bottle
>
> **Extracted A:** absent
>
> **Extracted B:** wine bottle
>
> **Recorded reason, verbatim:** No wine bottle is established in the first caption.

**Audit explanation:** A describes laptop use. Wine-bottle presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 112. evaluation_529: `name of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A various containers, an address plate, and some old books fill a wooden shelf.
>
> **Caption B:** a living room containing a sofa, coffee table, lamp, end table, bookshelf and picnic basket
>
> **Adopted scope:** place or room type
>
> **Extracted A:** shelf and belongings without room-function cues
>
> **Extracted B:** living room
>
> **Recorded reason, verbatim:** Generic shelf furnishings do not establish a functional room type.

**Audit explanation:** A's shelf and belongings leave room function and place type unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 113. evaluation_533: `gender`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a blue shirt and jeans doing a trick on a skateboard.
>
> **Caption B:** A person on a skateboard in the air over steps outside with water spraying in background.
>
> **Adopted scope:** gender
>
> **Extracted A:** male
>
> **Extracted B:** unspecified person
>
> **Recorded reason, verbatim:** The second person has no recoverable gender description.

**Audit explanation:** B identifies a person. Gender remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 114. evaluation_538: `size of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A locomotive is stopped at the tracks while steam rolls up from under it.
>
> **Caption B:** A red and black old style steam train inside of a large train station.
>
> **Adopted scope:** vehicle size
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Steam and locomotive style do not supply vehicle size.

**Audit explanation:** Both train sizes remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 115. evaluation_541: `size of bed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bedroom with a beige wall, beige and gray comforter, and a cranberry colored bolster pillow.
>
> **Caption B:** Hotel room with a very large bed and a mounted television located on the wall.
>
> **Adopted scope:** bed size
>
> **Extracted A:** unspecified
>
> **Extracted B:** very large
>
> **Recorded reason, verbatim:** Bedding colors do not establish the first bed's size.

**Audit explanation:** A gives bedding colors. Bed size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 116. evaluation_543: `type of furniture`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A video game shown on a flat screen TV in a room with brown carpet and drapes.
>
> **Caption B:** A small family room with several seats, a table, a footstool and a television set.
>
> **Adopted scope:** furniture type
>
> **Extracted A:** unspecified TV and textiles
>
> **Extracted B:** seats table footstool
>
> **Recorded reason, verbatim:** The first lists electronics and textiles but no furniture type to compare with seats and tables.

**Audit explanation:** A establishes a television and textiles. Furniture type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 117. evaluation_548: `longest dimension of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A variety of fruit - including oranges, apples, pears, and Kiwi fruit - sit in a cardboard box.
>
> **Caption B:** A platter of plums, pears, grapes, carrots and bananas is sitting on a table.
>
> **Adopted scope:** longest dimension
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption supplies dimensions of the relevant containers or foods.

**Audit explanation:** Both captions leave the relevant objects' dimensions and longest extent unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 118. evaluation_553: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Cat sleeping on top of a suitcase that is resting on top of a table.
>
> **Caption B:** A grey and white striped cat sitting on a chair cushion on a wooden chair.
>
> **Adopted scope:** animal color
>
> **Extracted A:** unspecified
>
> **Extracted B:** gray white
>
> **Recorded reason, verbatim:** The first cat's color is absent.

**Audit explanation:** A describes a cat sleeping on luggage. Coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 119. evaluation_554: `number of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A picture of a large wooden boat sitting on the edge of the water.
>
> **Caption B:** A group of boats at a dock as sea birds sit on the surface.
>
> **Adopted scope:** animal count
>
> **Extracted A:** unspecified
>
> **Extracted B:** plural seabirds
>
> **Recorded reason, verbatim:** The first boat scene contains no animal-count information.

**Audit explanation:** A describes a boat. Animal count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 120. evaluation_557: `color of ocean`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bunch of the same boats lined up beside each other in the ocean.
>
> **Caption B:** A large number of identical wooden boats float close to each other on the water.
>
> **Adopted scope:** ocean color
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither ocean or water description gives a color.

**Audit explanation:** Both water colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 121. evaluation_561: `activity of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A view of a runway and a single passenger plane that is on it.
>
> **Caption B:** a large plane a small plane a bus and work trucks on the airfield
>
> **Adopted scope:** vehicle activity
>
> **Extracted A:** on runway unspecified motion
>
> **Extracted B:** on airfield unspecified motion
>
> **Recorded reason, verbatim:** Being on a runway or airfield supplies location but no vehicle action or motion state.

**Audit explanation:** Runway and airfield locations leave vehicle action and movement unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 122. evaluation_562: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An old black and white picture has a horse and buggy on the street.
>
> **Caption B:** An antique photograph of a Victorian street scene, with horse-drawn carriages going down a wide street.
>
> **Adopted scope:** horse color
>
> **Extracted A:** unspecified monochrome photo
>
> **Extracted B:** unspecified old photo
>
> **Recorded reason, verbatim:** Old or monochrome photographs do not identify horse coat colors.

**Audit explanation:** Both historical-photograph descriptions leave horse coat color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 123. evaluation_565: `name of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young boy in a bib eating a meal in a highchair raises a plastic spoon to his mouth.
>
> **Caption B:** A boy in a yellow shirt sits in front of a plate of food.
>
> **Adopted scope:** person name
>
> **Extracted A:** unspecified boy
>
> **Extracted B:** unspecified boy
>
> **Recorded reason, verbatim:** Neither boy has a personal name in the text.

**Audit explanation:** Both boys' personal names remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 124. evaluation_569: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A person in the snow holding skies with other people sitting in the background.
>
> **Caption B:** A woman in a red suit on skis holds ski poles and has snow surrounding her.
>
> **Adopted scope:** equipment color
>
> **Extracted A:** unspecified skis
>
> **Extracted B:** unspecified skis
>
> **Recorded reason, verbatim:** The red suit does not supply ski-equipment colors; neither caption states them.

**Audit explanation:** Both ski-equipment colors remain unspecified. Red describes B's suit.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 125. evaluation_571: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A yellow Labrador Retriever and an Irish Setter play with a Frisbee in a fenced backyard.
>
> **Caption B:** A dog in the air trying to catch a frisbee with people in back.
>
> **Adopted scope:** dog color
>
> **Extracted A:** yellow and setter coat
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second dog's coat color is unstated.

**Audit explanation:** B identifies a dog. Coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 126. evaluation_575: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S6`.

> **Caption A:** A man dressed in a bunny costume on skis amid a large group of skiers.
>
> **Caption B:** A child in a pink suit  and an adult in a blue jacket downhill skiing.
>
> **Adopted scope:** clothing color
>
> **Extracted A:** unspecified bunny costume
>
> **Extracted B:** pink blue
>
> **Recorded reason, verbatim:** A bunny costume does not imply a particular clothing color.

**Audit explanation:** A identifies a bunny costume. Clothing color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 127. evaluation_579: `size of objects`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A baby is sitting on the floor with a ball in his hand and a phone to his ear.
>
> **Caption B:** A little baby with blue eyes looks up as he holds a teddy bear.
>
> **Adopted scope:** object size
>
> **Extracted A:** unspecified ball phone
>
> **Extracted B:** unspecified teddy
>
> **Recorded reason, verbatim:** The child's age and handling do not establish the objects' sizes.

**Audit explanation:** Both captions leave held-object sizes unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 128. evaluation_591: `type of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A chefs knife and a cutting board with uncut mushrooms and half of an onion.
>
> **Caption B:** Various ingredients sit on a kitchen table top as if being prepared to be cooked.
>
> **Adopted scope:** food type
>
> **Extracted A:** mushrooms and onion
>
> **Extracted B:** unnamed cooking ingredients
>
> **Recorded reason, verbatim:** Ingredients provides a role, not the requested food identities.

**Audit explanation:** B identifies cooking ingredients. Their food category remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 129. evaluation_611: `name of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young girl sitting a table with a flower turned on its bloom and scissors nearby.
>
> **Caption B:** A kitchen table with tall floral bouquet, small creamer and a bowl of oranges.
>
> **Adopted scope:** room name/type
>
> **Extracted A:** unspecified
>
> **Extracted B:** kitchen
>
> **Recorded reason, verbatim:** The first table and craft materials do not establish an indoor room or its function.

**Audit explanation:** A's table, flower and scissors leave room function unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 130. evaluation_619: `animal's stance`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black dog chest high in water holding a plastic bottle in its mouth
>
> **Caption B:** a bulldog wearing a red life jacket and standing on a blue surfboard in a body of water.
>
> **Adopted scope:** dog stance
>
> **Extracted A:** chest-deep water unspecified stance
>
> **Extracted B:** standing on board
>
> **Recorded reason, verbatim:** Chest-deep water could involve standing or swimming and does not supply the first dog's stance.

**Audit explanation:** A's chest-deep dog could be standing, swimming or adopting another stance. Its stance remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 131. evaluation_626: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** Zoomed in view of the toppings of a pizza including pepperoni and black olives.
>
> **Caption B:** Closeup of a white and blue plate with two slices of pizza on it.
>
> **Adopted scope:** pizza color
>
> **Extracted A:** black olives partial
>
> **Extracted B:** unspecified pizza color
>
> **Recorded reason, verbatim:** The blue-white colors belong to the second plate, not the pizza.

**Audit explanation:** B gives plate colors. Pizza color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 132. evaluation_633: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A pizza of which one-eight piece is missing  on a plate,held by an old person.
>
> **Caption B:** A small pizza with cheese with a touch of herbs on a counter top.
>
> **Adopted scope:** people count
>
> **Extracted A:** one
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second pizza description supplies no person count.

**Audit explanation:** B identifies a pizza on a counter. Person count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 133. evaluation_637: `number of chairs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A small bedroom suite in a hotel setting with a bed, small table and two chairs.
>
> **Caption B:** A hotel room decorated in silver and white has a large mirror over the headboard of the bed.
>
> **Adopted scope:** chair count
>
> **Extracted A:** two
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second hotel room has no chair-count information.

**Audit explanation:** B describes a hotel room. Chair count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 134. evaluation_638: `signs outside`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A stone wall is constructed all around the corner house where greenery is neatly trimmed.
>
> **Caption B:** A no parking and No Left Turn sign sits on the side walk of the neighborhood.
>
> **Adopted scope:** sign presence
>
> **Extracted A:** unspecified
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** The first house exterior does not state whether signs exist.

**Audit explanation:** A describes a wall and greenery. Sign presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 135. evaluation_639: `exterior feature of house`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A stone wall is constructed all around the corner house where greenery is neatly trimmed.
>
> **Caption B:** A no parking and No Left Turn sign sits on the side walk of the neighborhood.
>
> **Adopted scope:** house exterior
>
> **Extracted A:** stone wall trimmed greenery
>
> **Extracted B:** no house exterior described
>
> **Recorded reason, verbatim:** Neighborhood signs do not identify a particular house's exterior features.

**Audit explanation:** B identifies neighborhood signs. A comparable house exterior remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 136. evaluation_654: `name of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A guy sitting at a dining table with plates of food in front of him.
>
> **Caption B:** a man in a red and white plaid shirt a sandwich and some French fries
>
> **Adopted scope:** place type
>
> **Extracted A:** dining table setting
>
> **Extracted B:** unspecified location
>
> **Recorded reason, verbatim:** The malformed second description supplies food and clothing but no venue.

**Audit explanation:** B identifies a man and food. Surrounding place type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 137. evaluation_666: `type of street sign`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A TRIANGULAR AND A ROUND ROAD SIGN, ONE INDICATING THE PERCENTAGE OF DECLINE IN THE ROAD
>
> **Caption B:** A close up of a street light sign with an airplane in the background.
>
> **Adopted scope:** street-sign type
>
> **Extracted A:** road-decline warning
>
> **Extracted B:** unspecified street-light sign
>
> **Recorded reason, verbatim:** The second does not identify a sign message or reliable specific sign type.

**Audit explanation:** B's street-light sign leaves its message and subtype unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 138. evaluation_667: `shape of street sign`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A TRIANGULAR AND A ROUND ROAD SIGN, ONE INDICATING THE PERCENTAGE OF DECLINE IN THE ROAD
>
> **Caption B:** A close up of a street light sign with an airplane in the background.
>
> **Adopted scope:** sign shape
>
> **Extracted A:** triangular round
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second sign's outline is not described.

**Audit explanation:** B identifies a sign. Its shape remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 139. evaluation_681: `mirror in bathroom`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bathroom has a marble countertop, white cabinet and floor, red rug, and rust-colored shower curtain.
>
> **Caption B:** This bathroom has a sink, a toilet, a shower, and mirror covering the whole wall.
>
> **Adopted scope:** mirror presence
>
> **Extracted A:** unspecified
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** The first bathroom gives no mirror-presence information.

**Audit explanation:** A describes bathroom furnishings. Mirror presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 140. evaluation_686: `color of couches`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A beautiful young lady sitting on a red couch holding a plate of food and a drink.
>
> **Caption B:** A young woman on a leather couch full of clutter plays an interactive video game.
>
> **Adopted scope:** couch color
>
> **Extracted A:** red
>
> **Extracted B:** unspecified leather
>
> **Recorded reason, verbatim:** Leather identifies couch material, not its color.

**Audit explanation:** B identifies a leather couch. Its color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 141. evaluation_691: `color of objects`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** One person on skis standing up and another person on a snowboard sitting down on a slope.
>
> **Caption B:** A young man wearing an orange jacket while standing on top of a snow covered ski slope.
>
> **Adopted scope:** equipment color
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The only color is a jacket color; the sports objects' colors are absent.

**Audit explanation:** Both ski-equipment colors remain unspecified. Orange describes clothing.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 142. evaluation_692: `type of carrier`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cart is loaded with luggage at a station while an attendant sits on a bench.
>
> **Caption B:** A woman is using a cellphone while sitting at a group of benches with luggage nearby.
>
> **Adopted scope:** luggage carrier
>
> **Extracted A:** cart
>
> **Extracted B:** unspecified near benches
>
> **Recorded reason, verbatim:** Luggage near benches does not identify a carrier in the second scene.

**Audit explanation:** B locates luggage near benches. A luggage carrier remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 143. evaluation_699: `gender of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person playing tennis on a hard surface court, with a chain link fence separating the two courts.
>
> **Caption B:** A boy in black shorts jumps and holds his tennis racket in the air.
>
> **Adopted scope:** gender
>
> **Extracted A:** unspecified person
>
> **Extracted B:** male boy
>
> **Recorded reason, verbatim:** The first generic tennis player has no gender information.

**Audit explanation:** A identifies a person. Gender remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 144. evaluation_705: `color of bed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bedroom with one bed, a small television on a set of drawers and two chairs and a small table.
>
> **Caption B:** a bedroom with a white chair a table and a brown blue and white bed
>
> **Adopted scope:** bed color
>
> **Extracted A:** unspecified
>
> **Extracted B:** brown blue white
>
> **Recorded reason, verbatim:** The first bed's color is unstated.

**Audit explanation:** A identifies a bed. Its color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 145. evaluation_707: `age of giraffe`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young giraffe opts for a snack of grass instead of walking to the trees in the distance.
>
> **Caption B:** A giraffe standing on the grass bending one leg out and stretching its neck towards the ground.
>
> **Adopted scope:** giraffe age
>
> **Extracted A:** young
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second giraffe's posture does not establish its age.

**Audit explanation:** B describes giraffe posture. Age remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 146. evaluation_712: `type of plants`

**Current status:** `split restriction`. **Semantic rating:** `4`. **Policy:** `X1`.

> **Caption A:** A wooden bench surrounded by shrubbery and flowers on the side of a house.
>
> **Caption B:** A scene displays a vast array of flower pots in front of a decorated building.
>
> **Adopted scope:** plant type
>
> **Extracted A:** shrubs flowers
>
> **Extracted B:** potted flowers
>
> **Recorded reason, verbatim:** shares a canonical caption with original training

**Audit explanation:** A canonical caption is shared with original training, so this semantically rated row is withheld from the test export.

**Split evidence:** `train_4484` (training), `train_4485` (training).

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 147. evaluation_713: `position of plants`

**Current status:** `split restriction`. **Semantic rating:** `3`. **Policy:** `X1`.

> **Caption A:** A wooden bench surrounded by shrubbery and flowers on the side of a house.
>
> **Caption B:** A scene displays a vast array of flower pots in front of a decorated building.
>
> **Adopted scope:** plant position
>
> **Extracted A:** around bench beside house
>
> **Extracted B:** pots in front of building
>
> **Recorded reason, verbatim:** shares a canonical caption with original training

**Audit explanation:** A canonical caption belongs to original training, preventing this semantically rated row's inclusion in the test export.

**Split evidence:** `train_4484` (training), `train_4485` (training).

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 148. evaluation_718: `material of floor`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog eats out of a bowl on a mat on a wood floor.
>
> **Caption B:** Large white dog laying on the kitchen floor in front of the stove chewing on a pan.
>
> **Adopted scope:** floor material
>
> **Extracted A:** wood
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** A kitchen location does not determine the second floor's material.

**Audit explanation:** B identifies a kitchen floor. Its material remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 149. evaluation_723: `activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white bath tub sitting in a living room next to a christmas tree.
>
> **Caption B:** A Christmas tree behind a table next to a book shelf and a wood burning stove.
>
> **Adopted scope:** activity
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither furnishings description supplies an activity.

**Audit explanation:** Both room arrangements leave an activity being performed unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 150. evaluation_729: `arrangement of furniture in room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A living room with the furniture arranged along the walls with a throw rug in the center of the room.
>
> **Caption B:** A brown and white living room couch and ottoman, with a view into a dining area.
>
> **Adopted scope:** furniture arrangement
>
> **Extracted A:** along walls rug center
>
> **Extracted B:** couch ottoman locations unspecified
>
> **Recorded reason, verbatim:** The second names couch and ottoman without stating their placement relative to the room.

**Audit explanation:** B identifies a couch and ottoman. Their arrangement within the room remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 151. evaluation_735: `color of wall`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bookshelf with cassettes and books on the first shelf and dictionaries with other books on the lower shelf.
>
> **Caption B:** A flat screen tv on a wooden shelf in front of a green wall.
>
> **Adopted scope:** wall color
>
> **Extracted A:** unspecified
>
> **Extracted B:** green
>
> **Recorded reason, verbatim:** The first shelf description contains no wall color.

**Audit explanation:** A identifies shelving and books. Wall color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 152. evaluation_738: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young child standing in a kitchen with the refrigerator door open and the child is leaning into the refrigerator with their back.
>
> **Caption B:** A view of a kitchen with a white refrigerator and wood cabinets and a potted plant sitting on a white shelf.
>
> **Adopted scope:** people count
>
> **Extracted A:** one child
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second kitchen has no person-count information.

**Audit explanation:** B describes kitchen furnishings. Human presence and person count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 153. evaluation_758: `food toppings`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Different foods, including pizza displayed for eating and a person with tongs serving the food.
>
> **Caption B:** A partially eaten taco pizza is in the foreground, while another type of pizza is in the background.
>
> **Adopted scope:** toppings
>
> **Extracted A:** unspecified pizza toppings
>
> **Extracted B:** taco pizza toppings
>
> **Recorded reason, verbatim:** The first pizza has no stated topping information.

**Audit explanation:** A identifies pizza. Toppings remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 154. evaluation_769: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** This is an image of the feet of a person  laying on a bed with pillow.
>
> **Caption B:** A living room with a large window, a poster, a couch and a monitor.
>
> **Adopted scope:** people count
>
> **Extracted A:** one
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second room does not establish occupants or their absence.

**Audit explanation:** B describes a living room. Human presence and person count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 155. evaluation_782: `color of fruit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** people standing around in front of building with a lot of green bananas sitting around
>
> **Caption B:** a kitchen with a bunch of food in boxes and bananas hanging from hooks
>
> **Adopted scope:** fruit color
>
> **Extracted A:** green
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Hanging bananas do not identify their color or ripeness.

**Audit explanation:** B identifies bananas. Their color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 156. evaluation_789: `contents of dish`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A plate topped with toast and eggs sitting next to a cup of coffee.
>
> **Caption B:** Food on a plate, a drink in a cup on a saucer, and sunglasses on a table.
>
> **Adopted scope:** food contents of dish
>
> **Extracted A:** toast and eggs
>
> **Extracted B:** unnamed food
>
> **Recorded reason, verbatim:** The second does not identify the food contents requested.

**Audit explanation:** B's unnamed food leaves dish contents unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 157. evaluation_796: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cake that has a glaze over it, set on a plate with eight lighted candles on top.
>
> **Caption B:** A little girl sits in darkness behind a birthday cake with lots of lit candles.
>
> **Adopted scope:** people count
>
> **Extracted A:** unspecified
>
> **Extracted B:** one girl
>
> **Recorded reason, verbatim:** The first cake description does not establish how many people are present.

**Audit explanation:** A describes a cake. Person count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 158. evaluation_799: `animal's attention`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A side view of a giraffe as it stares down at the ground, in the middle of the field.
>
> **Caption B:** In the foreground of a forest-like area with tall trees, a giraffe stands on short grass, straddling a stretch of wire cable.
>
> **Adopted scope:** animal attention
>
> **Extracted A:** looking at ground
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second giraffe's location and leg posture do not identify its attention target.

**Audit explanation:** B describes giraffe position and surroundings. Its attention target remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 159. evaluation_800: `name of bird`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A close up of a table and chairs with a bird on the table.
>
> **Caption B:** A bird sitting on top of a white bowl next to a bird on a white plate.
>
> **Adopted scope:** bird type or common name
>
> **Extracted A:** unnamed bird
>
> **Extracted B:** unnamed birds
>
> **Recorded reason, verbatim:** Neither caption supplies a bird type beyond repeating bird.

**Audit explanation:** Both captions identify generic birds. Bird types and common names remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 160. evaluation_803: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** a man and women sitting on a motorcycle with an American flag on the back
>
> **Caption B:** a male and a female riding on a white and black motorcycle and cars
>
> **Adopted scope:** motorcycle color
>
> **Extracted A:** unspecified
>
> **Extracted B:** white black
>
> **Recorded reason, verbatim:** The first flag does not establish the motorcycle's own color.

**Audit explanation:** A identifies a motorcycle. Its color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 161. evaluation_805: `color of computer`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** a white keyboard sitting next to a white computer mouse on a mouse pad.
>
> **Caption B:** A laptop with ear buds draped over it sits next to a desktop computer.
>
> **Adopted scope:** computer color
>
> **Extracted A:** white peripherals no computer color
>
> **Extracted B:** unspecified computers
>
> **Recorded reason, verbatim:** White input devices do not establish a computer body's color, and the second colors are unstated.

**Audit explanation:** A gives peripheral colors. Computer colors remain unspecified in both captions.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 162. evaluation_811: `color of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A red and yellow train traveling down train tracks near a field covered with snow.
>
> **Caption B:** a close up of a train on a train track with a sky background
>
> **Adopted scope:** train color
>
> **Extracted A:** red yellow
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second train has no stated color.

**Audit explanation:** B identifies a train. Its color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 163. evaluation_812: `cutting`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The skillet mixture of sliced meat and carrots is .being stirred with a wooden fork.
>
> **Caption B:** Carrots and ham on a table with the ham setting on a cutting board .
>
> **Adopted scope:** cutting activity
>
> **Extracted A:** sliced ingredients being stirred
>
> **Extracted B:** ham on cutting board
>
> **Recorded reason, verbatim:** Already sliced food and a cutting board do not establish an ongoing cutting action in both scenes.

**Audit explanation:** Stirring sliced ingredients and placing ham on a cutting board leave an ongoing cutting action unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 164. evaluation_817: `presence of easel`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The bedroom adorned with posters and signs and bed next to the two windows.
>
> **Caption B:** A dark room with a large window and no curtain, an easel and assorted furniture.
>
> **Adopted scope:** easel presence
>
> **Extracted A:** unspecified
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** The first bedroom supplies no easel-presence information.

**Audit explanation:** A describes bedroom furnishings. Easel presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 165. evaluation_823: `vehicle elevation`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A train traveling on top of a railway that runs above ground through a city.
>
> **Caption B:** Commuter train with graffiti travels down a section of tracks through an urban area.
>
> **Adopted scope:** rail elevation
>
> **Extracted A:** elevated
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second urban tracks do not establish a height relative to ground.

**Audit explanation:** B identifies urban tracks. Their height relative to the ground remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 166. evaluation_826: `size of objects`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person is behind a large teddy bear next to a basket of small teddy bears.
>
> **Caption B:** A group of cute stuffed animals sit on a shelf next to a mint green wall.
>
> **Adopted scope:** toy sizes
>
> **Extracted A:** large and small bears
>
> **Extracted B:** unspecified stuffed animals
>
> **Recorded reason, verbatim:** The second stuffed animals have no size descriptors.

**Audit explanation:** B identifies stuffed animals. Their sizes remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 167. evaluation_828: `color of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A red and pink bicycle are parked on a pole next to a yellow bus.
>
> **Caption B:** A long row of bicycles are lined up by a curb as a yellow tram is near a building.
>
> **Adopted scope:** principal bicycle colors
>
> **Extracted A:** red pink
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The yellow tram is incidental to the principal bicycles, whose second-side colors are absent.

**Audit explanation:** B gives tram color. Principal bicycle colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 168. evaluation_833: `position of bear`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A large bear standing on a small cliff and two smaller bears climbing down the cliff.
>
> **Caption B:** A brown bear looks out over the forest floor in the bright beams of sunlight.
>
> **Adopted scope:** bear location
>
> **Extracted A:** on and descending a cliff
>
> **Extracted B:** looking over forest floor from unspecified position
>
> **Recorded reason, verbatim:** Looking out over a forest floor does not mean standing on that floor.

**Audit explanation:** B identifies what the bear looks over. The bear's own position remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 169. evaluation_855: `number of pizza slices`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A pizza has been prepared and is ready to go into the pizza oven.
>
> **Caption B:** A pepperoni mushroom pizza with one slice taken out, and a pie server resting on the plate.
>
> **Adopted scope:** pizza slice count
>
> **Extracted A:** uncut count unstated
>
> **Extracted B:** remaining slice count unstated
>
> **Recorded reason, verbatim:** Prepared pizza and one removed piece do not supply the two total slice counts requested.

**Audit explanation:** A leaves slice count unspecified. B identifies one missing slice and leaves the remaining count unspecified.

**Policy check:** Check recorded value. **Peer:** `writer_validation`.

**Review question:** A leaves slicing state unspecified. Should Extracted A describe only the unstated slice count?

**History:** supplied source rating `-1.0`.

### 170. evaluation_857: `number of seats`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A kitchen with two chairs and a refrigerator with a lot of paper posted on it.
>
> **Caption B:** Fridge in the corner of this kitchen on same side as the sink next to deck doors
>
> **Adopted scope:** seat count
>
> **Extracted A:** two chairs
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second kitchen gives no seating-count information.

**Audit explanation:** B describes kitchen fixtures. Seat count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 171. evaluation_859: `repair needs of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a close up of a toilet in a bath room with tiled walls and floors
>
> **Caption B:** A bathroom in need of repair has a hole in the wall and insulation showing.
>
> **Adopted scope:** repair need
>
> **Extracted A:** unspecified
>
> **Extracted B:** repair needed wall hole
>
> **Recorded reason, verbatim:** The first tiled bathroom's repair condition is unstated.

**Audit explanation:** A identifies tiles and a toilet. Repair needs remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 172. evaluation_861: `number of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A vintage photograph of city with electricity poles in the middle of the street.
>
> **Caption B:** an old black and white photo of a number or animals on a city street
>
> **Adopted scope:** animal count
>
> **Extracted A:** unspecified
>
> **Extracted B:** plural
>
> **Recorded reason, verbatim:** The first urban photograph description supplies no animal count.

**Audit explanation:** A describes a street. Animal count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 173. evaluation_864: `sentiment of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A elderly woman sits next to a huge pile of green and yellow bananas.
>
> **Caption B:** A woman stares at the camera with a basket of bananas on her head.
>
> **Adopted scope:** people sentiment
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Sitting and staring do not establish either woman's sentiment.

**Audit explanation:** Sitting beside bananas and staring at a camera leave both women's sentiments unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 174. evaluation_865: `color of bananas`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A elderly woman sits next to a huge pile of green and yellow bananas.
>
> **Caption B:** A woman stares at the camera with a basket of bananas on her head.
>
> **Adopted scope:** banana color
>
> **Extracted A:** green yellow
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second bananas have no stated color.

**Audit explanation:** B identifies bananas. Their color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 175. evaluation_867: `name of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A partially eaten taco pizza is in the foreground, while another type of pizza is in the background.
>
> **Caption B:** a pizza with a piece cut out of it sitting on some wax paper
>
> **Adopted scope:** place type
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither pizza caption provides a venue or place category.

**Audit explanation:** Both pizza descriptions leave the surrounding place type unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 176. evaluation_878: `state of ball`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man playing tennis on a tennis court with a racket in his hand.
>
> **Caption B:** A tennis player is holding his hand up to guard himself from the flying ball.
>
> **Adopted scope:** ball state
>
> **Extracted A:** tennis ball state unstated
>
> **Extracted B:** flying
>
> **Recorded reason, verbatim:** General tennis play does not fix the first ball's instantaneous state.

**Audit explanation:** A establishes tennis play. The ball's current state and motion remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 177. evaluation_881: `width of street or path`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A picture of a street in an Asian country with car, motorcycle and clothes on the line
>
> **Caption B:** An alley way with several pieces of discarded furnuiture and a teddy bear hanging from a clothes line.
>
> **Adopted scope:** path width
>
> **Extracted A:** unspecified street
>
> **Extracted B:** alley narrow inferred
>
> **Recorded reason, verbatim:** The first street's width is not provided.

**Audit explanation:** A identifies a street. Its width remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 178. evaluation_911: `type of silverware`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A piece of burnt pizza with a spoonful of dessert sitting on top of it.
>
> **Caption B:** Some sort of pizza looking dish served on a square plate with a fork and knife.
>
> **Adopted scope:** silverware
>
> **Extracted A:** not explicitly present spoonful measure
>
> **Extracted B:** fork knife
>
> **Recorded reason, verbatim:** Spoonful is an amount expression and does not establish a present utensil.

**Audit explanation:** A's spoonful measures dessert quantity. The presence of a spoon or another utensil remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 179. evaluation_915: `number of poster bed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** Pink four poster bed with a canopy in a room with other vintage furniture.
>
> **Caption B:** The furniture looks like either a futon or a couch with a plain blanket.
>
> **Adopted scope:** poster-bed count
>
> **Extracted A:** one
>
> **Extracted B:** none applicable stated
>
> **Recorded reason, verbatim:** The second establishes no poster bed to count.

**Audit explanation:** B identifies a futon or couch. A poster bed to count remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 180. evaluation_921: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cat hissing as it attempts to fit itself into a bowl that it is to big to fit in.
>
> **Caption B:** A black cat with a red tag sitting down with a bookshelf in the background.
>
> **Adopted scope:** animal color
>
> **Extracted A:** unspecified
>
> **Extracted B:** black
>
> **Recorded reason, verbatim:** The first cat's size relative to a bowl does not supply its color.

**Audit explanation:** A describes a cat's actions. Coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 181. evaluation_927: `alertness level`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person sleeping with a pillow over their head and a book on their chest.
>
> **Caption B:** A person enjoying a lazy day in bed with their bedroom curtains wide open.
>
> **Adopted scope:** alertness
>
> **Extracted A:** sleeping
>
> **Extracted B:** unspecified lazy relaxation
>
> **Recorded reason, verbatim:** A lazy day in bed does not establish whether the person is awake or asleep.

**Audit explanation:** B describes a lazy day in bed. The person's alertness remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 182. evaluation_934: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** a white plate with some shrimp and broccoli and another plate with bread and cheese
>
> **Caption B:** A full plate with a serving spoon laying on it sitting on a table.
>
> **Adopted scope:** plate color
>
> **Extracted A:** white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second plate has no stated color.

**Audit explanation:** B identifies a plate. Its color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 183. evaluation_935: `contents of dish`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a white plate with some shrimp and broccoli and another plate with bread and cheese
>
> **Caption B:** A full plate with a serving spoon laying on it sitting on a table.
>
> **Adopted scope:** food contents of dish
>
> **Extracted A:** shrimp broccoli bread and cheese
>
> **Extracted B:** full plate with unnamed food
>
> **Recorded reason, verbatim:** Plate fullness supports amount but not food-content identities.

**Audit explanation:** B identifies a full plate. Food contents remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 184. evaluation_937: `food item`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** a laptop on a table surrounded by a coffee cup, a vase, and some little cupcakes
>
> **Caption B:** A desktop computer monitor, printer, and keyboard with a mouse on top of a desk.
>
> **Adopted scope:** food
>
> **Extracted A:** coffee cupcakes
>
> **Extracted B:** none stated
>
> **Recorded reason, verbatim:** The second computer desk lists no food or drink.

**Audit explanation:** B lists computer equipment. A food item to compare remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 185. evaluation_949: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A kitten rubbing against the legs of a person wearing blue jeans and new balance sneakers.
>
> **Caption B:** A cat with its eyes barely open has its arm across a computer mouse.
>
> **Adopted scope:** principal animal color
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The jeans' color does not specify either principal cat's coat.

**Audit explanation:** Both principal cat coat colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 186. evaluation_954: `name of persons`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A professional skateboarder leaps over a bunch of over skateboards while a crowd watches.
>
> **Caption B:** A youth achieves an impressive skateboard trick in front of a crowd of onlookers.
>
> **Adopted scope:** person names
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither skateboarder or crowd member is personally named.

**Audit explanation:** Both captions leave personal names unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 187. evaluation_955: `type of skateboarding trick`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A professional skateboarder leaps over a bunch of over skateboards while a crowd watches.
>
> **Caption B:** A youth achieves an impressive skateboard trick in front of a crowd of onlookers.
>
> **Adopted scope:** skateboarding trick type
>
> **Extracted A:** jump over skateboards
>
> **Extracted B:** unnamed impressive trick
>
> **Recorded reason, verbatim:** Impressive evaluates the trick but does not identify its type.

**Audit explanation:** B calls the trick impressive. Maneuver type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 188. evaluation_957: `actions of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A group of Giraffe, an Ostrich and a pair of zebras in a habitat.
>
> **Caption B:** Two giraffes in a field one eating from a tree and the other with next bent down.
>
> **Adopted scope:** animal action
>
> **Extracted A:** unspecified habitat presence
>
> **Extracted B:** eating and bending
>
> **Recorded reason, verbatim:** Animal presence in a habitat does not establish an action.

**Audit explanation:** A locates animals in a habitat. Their actions remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 189. evaluation_960: `type of food item`

**Current status:** `split restriction`. **Semantic rating:** `3`. **Policy:** `X1`.

> **Caption A:** A meal in a basket with checkered paper consisting of chips and a burger.
>
> **Caption B:** A hot dog with cheese and sauce and fries with ketchup on the side.
>
> **Adopted scope:** food item
>
> **Extracted A:** burger chips
>
> **Extracted B:** hotdog fries
>
> **Recorded reason, verbatim:** shares a canonical caption with original training

**Audit explanation:** A canonical caption belongs to original training, so this semantically rated comparison is withheld from the test export.

**Split evidence:** `train_1318` (training), `train_1319` (training), `train_3308` (training), `train_3309` (training), `train_4058` (training), `train_4059` (training), `train_954` (training), `train_955` (training).

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 190. evaluation_961: `name of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A meal in a basket with checkered paper consisting of chips and a burger.
>
> **Caption B:** A hot dog with cheese and sauce and fries with ketchup on the side.
>
> **Adopted scope:** place type
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Serving style alone does not identify either venue.

**Audit explanation:** Both captions leave place type unspecified beyond immediate food presentation.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 191. evaluation_969: `absence of bicycle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a cluttered room with a laptop computer on one table and a lot of furniture
>
> **Caption B:** A view of a bedroom shows a bed right next to a desk by a bicycle.
>
> **Adopted scope:** bike absence
>
> **Extracted A:** unknown
>
> **Extracted B:** bike present so false
>
> **Recorded reason, verbatim:** A bicycle omitted from the first description is not established absent.

**Audit explanation:** A describes a furnished room. Bicycle absence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 192. evaluation_973: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A young woman in a white tank top, blue jean shorts, holding a skate board.
>
> **Caption B:** A person doing a jumping trick on a skateboard, and the skateboard is upside down.
>
> **Adopted scope:** skateboard color
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The supplied colors are clothing colors; neither skateboard has a color.

**Audit explanation:** Both skateboard colors remain unspecified. Clothing hues concern another object.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 193. evaluation_986: `motion of objects`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A fishing boat that is pulling into the harbor after a night of fishing.
>
> **Caption B:** A wooden bench in front of a body of water with boats in the water.
>
> **Adopted scope:** boat motion
>
> **Extracted A:** entering harbor
>
> **Extracted B:** boats on water unspecified motion
>
> **Recorded reason, verbatim:** Boats simply in the water may be moving or moored; the second action is unstated.

**Audit explanation:** B locates boats on water. Their movement remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 194. evaluation_990: `location of traffic lights`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A hanging traffic light at an intersection with another traffic light visible in the distance.
>
> **Caption B:** street scene with bus in middle of road next to man with his hand raised
>
> **Adopted scope:** traffic-light location
>
> **Extracted A:** intersection
>
> **Extracted B:** no lights stated
>
> **Recorded reason, verbatim:** The second street scene establishes no traffic light to locate.

**Audit explanation:** B describes a street scene. A traffic light and its location remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 195. evaluation_1000: `animal's size`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a cat sticking its front paws on a window ledge as he looks outside
>
> **Caption B:** A large cat sitting on top of a wooden shelf next to a bottle.
>
> **Adopted scope:** cat size
>
> **Extracted A:** unspecified
>
> **Extracted B:** large
>
> **Recorded reason, verbatim:** A cat's window posture does not determine its body size.

**Audit explanation:** A describes a cat at a window. Its size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 196. evaluation_1002: `color of toilet bowl`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a toilet and a bathroom counter with a sink on it in a bathroom
>
> **Caption B:** A white toilet bowl is surrounded by a toilet paper rack and a white trash can.
>
> **Adopted scope:** toilet color
>
> **Extracted A:** unspecified
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** The first toilet has no stated color.

**Audit explanation:** A identifies a toilet. Bowl color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 197. evaluation_1004: `size of clock`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** People are walking around a buildings and there is big clock in the middle
>
> **Caption B:** a pub restaurant clock with roman numerals attached to the side of a building
>
> **Adopted scope:** clock size
>
> **Extracted A:** big
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second clock's mounting and numerals do not establish its size.

**Audit explanation:** B identifies a mounted clock. Its size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 198. evaluation_1009: `absence of knife`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A wooden cutting board with a knife and several pieces of fruit on it.
>
> **Caption B:** a counter top with two bowls of fruits and a banana in a glass of liquid.
>
> **Adopted scope:** knife absence
>
> **Extracted A:** false knife present
>
> **Extracted B:** unknown
>
> **Recorded reason, verbatim:** The first knife is present; the second's silence does not establish knife absence.

**Audit explanation:** B describes fruit and containers. Knife absence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 199. evaluation_1010: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A chair with the arms and legs of s stuffed animal in a child's room.
>
> **Caption B:** a little girl on a bed with a brown bear and small white teddy bear
>
> **Adopted scope:** people count
>
> **Extracted A:** unspecified
>
> **Extracted B:** one girl
>
> **Recorded reason, verbatim:** A child's room does not establish a child currently present.

**Audit explanation:** A identifies furniture and a stuffed toy. Person count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 200. evaluation_1012: `number of lighted candles`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cat standing up in front of a mirror on the back of a door.
>
> **Caption B:** A cat laying down and looking into a three panel mirror, with two lighted candles.
>
> **Adopted scope:** lit candle count
>
> **Extracted A:** unspecified
>
> **Extracted B:** two
>
> **Recorded reason, verbatim:** The first mirror scene supplies no candle count.

**Audit explanation:** A describes a cat and mirror. Lighted-candle count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 201. evaluation_1015: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A street scene with people walking on the sidewalk and a car on the road.
>
> **Caption B:** An intersection with a market, street light and a street sign on one corner.
>
> **Adopted scope:** people count
>
> **Extracted A:** plural
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second intersection description supplies no human count.

**Audit explanation:** B describes an intersection. Person count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 202. evaluation_1016: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An icy highway with no travelers on it and three traffic lights hanging above the lanes.
>
> **Caption B:** an image of a stop sign that is posted in the three way zone
>
> **Adopted scope:** people count
>
> **Extracted A:** zero travelers
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Explicitly no travelers is recoverable in the first, but the second has no human-presence information.

**Audit explanation:** B describes a road sign. Person count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 203. evaluation_1017: `number of ways`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An icy highway with no travelers on it and three traffic lights hanging above the lanes.
>
> **Caption B:** an image of a stop sign that is posted in the three way zone
>
> **Adopted scope:** road branches
>
> **Extracted A:** unspecified highway lanes
>
> **Extracted B:** three-way zone
>
> **Recorded reason, verbatim:** Lane and signal counts do not establish the number of connecting road branches.

**Audit explanation:** A's highway lanes leave the number of intersecting road branches unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 204. evaluation_1019: `color of cat`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** a black and white picture of a golden retriever laying on the leg of its owner.
>
> **Caption B:** Fluffy orange cat and big grey dog curled up together in a dog bed.
>
> **Adopted scope:** cat color
>
> **Extracted A:** cat absent
>
> **Extracted B:** orange
>
> **Recorded reason, verbatim:** The first animal is a dog, with no cat to compare.

**Audit explanation:** A identifies a dog. A cat and its color remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 205. evaluation_1020: `type of bird`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white and brown sandpiper with a long, black beak lifts up one leg.
>
> **Caption B:** A black bird with a red bill standing in the sand and water next to the waves.
>
> **Adopted scope:** bird type
>
> **Extracted A:** sandpiper
>
> **Extracted B:** black bird with red bill, species unstated
>
> **Recorded reason, verbatim:** Coat and bill colors do not reliably identify the second bird type.

**Audit explanation:** B gives plumage and bill colors. Bird type and species remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 206. evaluation_1022: `urban location`

**Current status:** `split restriction`. **Semantic rating:** `5`. **Policy:** `X1`.

> **Caption A:** a city bus on the side of the road with a couple of people walking
>
> **Caption B:** A white metro bus with pink and purple trim drives down a city street in front of a glass building.
>
> **Adopted scope:** urban location
>
> **Extracted A:** city roadside
>
> **Extracted B:** city street
>
> **Recorded reason, verbatim:** shares a canonical caption with original validation

**Audit explanation:** A canonical caption is shared with original validation, so this semantically rated comparison is withheld from the test export.

**Split evidence:** `train_1088` (validation), `train_1089` (validation).

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 207. evaluation_1023: `roadside`

**Current status:** `split restriction`. **Semantic rating:** `3`. **Policy:** `X1`.

> **Caption A:** a city bus on the side of the road with a couple of people walking
>
> **Caption B:** A white metro bus with pink and purple trim drives down a city street in front of a glass building.
>
> **Adopted scope:** road position
>
> **Extracted A:** roadside
>
> **Extracted B:** on city street
>
> **Recorded reason, verbatim:** shares a canonical caption with original validation

**Audit explanation:** A canonical caption belongs to original validation, preventing this semantically rated row's inclusion in the test export.

**Split evidence:** `train_1088` (validation), `train_1089` (validation).

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 208. evaluation_1027: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person sitting in a chair with a laptop and other computers in the background.
>
> **Caption B:** A desktop computer monitor, printer, and keyboard with a mouse on top of a desk.
>
> **Adopted scope:** people count
>
> **Extracted A:** one
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second desktop equipment scene gives no human count.

**Audit explanation:** B describes a computer setup. Person count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 209. evaluation_1032: `absence of skyscrapers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A view of a street sign with a building and bridge in the background.
>
> **Caption B:** Street signs at the intersection of Trinity and Liberty against a backdrop of skyscrapers.
>
> **Adopted scope:** skyscraper absence
>
> **Extracted A:** unknown building height
>
> **Extracted B:** false skyscrapers present
>
> **Recorded reason, verbatim:** An unspecified first building could be tall; skyscraper absence is not established.

**Audit explanation:** A identifies a building. Skyscraper absence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 210. evaluation_1039: `size of bed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a room with a small bed well made and many pics on the wall
>
> **Caption B:** A picture of a man and woman is next to a wire frame bed post in a bedroom.
>
> **Adopted scope:** bed size
>
> **Extracted A:** small
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second bed frame provides no bed-size information.

**Audit explanation:** B identifies part of a bed. Bed size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 211. evaluation_1050: `number of beverages`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A table containing orange juice, a cup of coffee and other breakfast related items.
>
> **Caption B:** A pink table cloth on top of a table topped with bowls and plates of food.
>
> **Adopted scope:** beverage count
>
> **Extracted A:** juice coffee two
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second bowls and plates supply no beverage vessel or drink to count.

**Audit explanation:** B lists food containers. Beverage count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 212. evaluation_1056: `closeness of walls`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** This open floor plan has a refrigerator and area rug, but little other furniture.
>
> **Caption B:** A mostly empty room features several boxes on top of a hard wood floor.
>
> **Adopted scope:** wall proximity
>
> **Extracted A:** open floor plan
>
> **Extracted B:** unspecified room dimensions
>
> **Recorded reason, verbatim:** The second room's low object density does not establish wall spacing.

**Audit explanation:** B identifies a mostly empty room. Wall spacing remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 213. evaluation_1064: `presence of meat`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A plate full of cut salad with a fork and a glass full of cold drink with ice.
>
> **Caption B:** A dish which contains broccoli, cauliflower and meat is pictured on top of a wooden tray.
>
> **Adopted scope:** meat presence
>
> **Extracted A:** unknown salad
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** An unspecified salad can include meat, so the first supplies no supported meat presence or absence.

**Audit explanation:** A identifies salad. Meat presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 214. evaluation_1066: `person with boat`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A sail boat out in the sea with a few other types of boats
>
> **Caption B:** A boat speeding across a large lake pulling a skier with a snow capped mountain in the background.
>
> **Adopted scope:** person with boat
>
> **Extracted A:** unspecified
>
> **Extracted B:** skier
>
> **Recorded reason, verbatim:** A sailboat's existence does not establish a described person associated with it.

**Audit explanation:** A identifies boats. An accompanying person remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 215. evaluation_1067: `speed of boat`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A sail boat out in the sea with a few other types of boats
>
> **Caption B:** A boat speeding across a large lake pulling a skier with a snow capped mountain in the background.
>
> **Adopted scope:** boat speed
>
> **Extracted A:** unspecified
>
> **Extracted B:** fast
>
> **Recorded reason, verbatim:** The first sailboat could be stationary or moving at an unspecified speed.

**Audit explanation:** A locates a sailboat at sea. Its speed remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 216. evaluation_1078: `color of horses`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A parade of brown horses walk down a street while traffic sits in the opposite lane.
>
> **Caption B:** A group of men riding horses in regal red and gold outfits in a city street.
>
> **Adopted scope:** horse color
>
> **Extracted A:** brown
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Red and gold describe riders' outfits, leaving second horse colors unknown.

**Audit explanation:** B gives rider outfit colors. Horse coat colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 217. evaluation_1085: `size of sign`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A stop sign that has a smaller sign that says "all way" underneath it.
>
> **Caption B:** A dark area that has several images of stop signs and other street signs.
>
> **Adopted scope:** sign size
>
> **Extracted A:** main sign and smaller subsidiary
>
> **Extracted B:** unspecified image sizes
>
> **Recorded reason, verbatim:** No size is supplied for the second sign images.

**Audit explanation:** B describes sign images. Their sizes remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 218. evaluation_1092: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** Three men and a woman by a laptop in a room in purple lighting.
>
> **Caption B:** A group of men, seated around a table that contains mugs, water bottles and laptops.
>
> **Adopted scope:** object color
>
> **Extracted A:** unspecified laptop
>
> **Extracted B:** unspecified laptops
>
> **Recorded reason, verbatim:** Purple illumination does not establish the laptops' own colors.

**Audit explanation:** Both laptop colors remain unspecified. Purple describes room lighting.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 219. evaluation_1095: `activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An elephant that is playing with an object that is hanging from above it.
>
> **Caption B:** Two grown elephants in the middle of the habitat and a baby elephant right behind them.
>
> **Adopted scope:** activity
>
> **Extracted A:** playing hanging object
>
> **Extracted B:** habitat position only
>
> **Recorded reason, verbatim:** The second elephants' positions do not establish an activity.

**Audit explanation:** B identifies elephant positions. Their activity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 220. evaluation_1096: `number of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** Someone is holding an long hot dog in front of a box of stuffed animals.
>
> **Caption B:** Two hot dogs with toppings are next to a drink in a styrofoam cup.
>
> **Adopted scope:** live animal count
>
> **Extracted A:** stuffed toys only
>
> **Extracted B:** hotdogs only
>
> **Recorded reason, verbatim:** Stuffed animals and hot dogs provide no actual animal count.

**Audit explanation:** Both captions identify food or stuffed toys. Live animals to count remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 221. evaluation_1097: `animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** Someone is holding an long hot dog in front of a box of stuffed animals.
>
> **Caption B:** Two hot dogs with toppings are next to a drink in a styrofoam cup.
>
> **Adopted scope:** animal type
>
> **Extracted A:** stuffed animals
>
> **Extracted B:** hotdogs food
>
> **Recorded reason, verbatim:** Neither caption establishes actual animals rather than toys or food.

**Audit explanation:** A establishes stuffed toys and B establishes food. Actual animals to classify remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 222. evaluation_1107: `number of towels`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A stack of towels in a bathroom with one laid out on the floor.
>
> **Caption B:** A fully tiled bathroom with a bathtub and bowl type sink, and a wooden framed mirror.
>
> **Adopted scope:** towel count
>
> **Extracted A:** stack plus one
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second bathroom gives no towel-count information.

**Audit explanation:** B describes bathroom fixtures. Towel count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 223. evaluation_1109: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black and white cat that is sitting under an open umbrella that is laid on the floor.
>
> **Caption B:** A cat staring at a camera laying on a floor next to a shoe.
>
> **Adopted scope:** animal color
>
> **Extracted A:** black white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second cat has no color description.

**Audit explanation:** B identifies a cat. Coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 224. evaluation_1113: `quantity of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A laptop computer, some speakers, a cellphone, empty pill package, and bowl of chili are on a narrow table.
>
> **Caption B:** A soda can is next to the computer keyboard and a mouse with a wrist guard.
>
> **Adopted scope:** quantity of meal food excluding beverages
>
> **Extracted A:** one bowl of chili
>
> **Extracted B:** soda beverage only, no food established
>
> **Recorded reason, verbatim:** Under ordinary caption food-versus-drink usage, the second contains a beverage but no comparable food amount.

**Audit explanation:** Under the recorded meal-food scope, B establishes a soda beverage. A comparable food amount remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 225. evaluation_1115: `type of building`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The side window of a house that appears to have graffiti painted on it.
>
> **Caption B:** A bathroom with a wall mounted toilet and sink, photographed from outside a window.
>
> **Adopted scope:** building type
>
> **Extracted A:** house
>
> **Extracted B:** bathroom in building of unspecified type
>
> **Recorded reason, verbatim:** A bathroom is a room function and does not establish the enclosing building type.

**Audit explanation:** B identifies a bathroom. Its building type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 226. evaluation_1125: `name of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Close-up of a man on a tennis court preparing to strike an approaching ball.
>
> **Caption B:** A boy in black shorts jumps and holds his tennis racket in the air.
>
> **Adopted scope:** person name
>
> **Extracted A:** unspecified man
>
> **Extracted B:** unspecified boy
>
> **Recorded reason, verbatim:** Neither player has a personal name.

**Audit explanation:** Both people's names remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 227. evaluation_1128: `position of man`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A close up of a man in a light blue business shirt and a black neck tie.
>
> **Caption B:** A man wearing a suit and tie holding his arm up to his chest.
>
> **Adopted scope:** man posture
>
> **Extracted A:** unspecified closeup
>
> **Extracted B:** arm raised to chest
>
> **Recorded reason, verbatim:** A close-up does not identify the first man's bodily posture.

**Audit explanation:** A gives a clothing close-up. The man's bodily posture remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 228. evaluation_1143: `amount of noise made by person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An eclectic woman is using her phone while smoking amongst a crowd of people.
>
> **Caption B:** A woman in a red jacket carrying a red purse looks at her red phone.
>
> **Adopted scope:** person noise
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Phone use and smoking do not establish sound intensity.

**Audit explanation:** Both phone-use descriptions leave the amount of noise unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 229. evaluation_1145: `person's age`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young man is at  a skateboard park getting ready to go down a slope.
>
> **Caption B:** A person that is up in the air and doing a trick on their skateboard.
>
> **Adopted scope:** age category
>
> **Extracted A:** young man
>
> **Extracted B:** unspecified person
>
> **Recorded reason, verbatim:** The second person has no age information.

**Audit explanation:** B identifies a person. Age category remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 230. evaluation_1147: `activity of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A man is taking a picture in the bathroom mirror with a lot of equipment around.
>
> **Caption B:** A bathroom with a sink and a metal shelf holding bathroom supplies over a toilet.
>
> **Adopted scope:** people activity
>
> **Extracted A:** taking photo
>
> **Extracted B:** no person stated
>
> **Recorded reason, verbatim:** The second bathroom contains no described person or human activity.

**Audit explanation:** B describes bathroom fixtures. People and their activity remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 231. evaluation_1153: `number of transport vehicles`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A boat in a canal and a peddled bike taxi cart in snow with residences.
>
> **Caption B:** a long river with buildings surrounding it and a bike rack on side walk
>
> **Adopted scope:** transport count
>
> **Extracted A:** boat bike taxi two
>
> **Extracted B:** no vehicles stated bike rack only
>
> **Recorded reason, verbatim:** A bike rack does not establish that a bicycle or other transport vehicle is present.

**Audit explanation:** B identifies a bicycle rack. Transport vehicles and their count remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 232. evaluation_1155: `location of items`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** All of the fruits and vegetables are in black and white except for the cluster of bananas two the right.
>
> **Caption B:** A display at a grocery store filled with lots of fresh fruits and avocados.
>
> **Adopted scope:** item location
>
> **Extracted A:** unspecified
>
> **Extracted B:** grocery display
>
> **Recorded reason, verbatim:** Right-side image placement does not identify the first foods' physical venue.

**Audit explanation:** A describes selective produce coloring. Item location remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 233. evaluation_1165: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A light colored dog with a tennis ball in it's mouth and a persons head next to it.
>
> **Caption B:** A dog is riding in a car and is seen through a rear view mirror.
>
> **Adopted scope:** animal color
>
> **Extracted A:** light
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The reflected second dog has no coat-color description.

**Audit explanation:** B describes a dog's reflection. Coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 234. evaluation_1167: `action of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A male afraid to touch the elephant, and a female is smiling taking picture with the elephant.
>
> **Caption B:** A captive elephant eats grass as children sit atop it, waiting for a ride; the elephant is guided by a person on the ground.
>
> **Adopted scope:** elephant action
>
> **Extracted A:** unspecified beside visitors
>
> **Extracted B:** eating grass
>
> **Recorded reason, verbatim:** The visitors' reactions do not identify the first elephant's action.

**Audit explanation:** A describes visitors' reactions. The elephant's action remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 235. evaluation_1177: `animal size`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog with it's paw on a remote control in a room with a television.
>
> **Caption B:** A large brown dog laying on top of a bed next to a pillow.
>
> **Adopted scope:** animal size
>
> **Extracted A:** unspecified
>
> **Extracted B:** large
>
> **Recorded reason, verbatim:** The first dog's paw position supplies no size information.

**Audit explanation:** A identifies a dog. Its size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 236. evaluation_1185: `presence of desk`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A laptop on a desk in front of a window with many pink sticky notes.
>
> **Caption B:** A coffee table has a laptop, mp3 player, books, stapler and paper lying on it.
>
> **Adopted scope:** desk presence
>
> **Extracted A:** present
>
> **Extracted B:** coffee table only
>
> **Recorded reason, verbatim:** A coffee table does not establish whether a separate desk exists.

**Audit explanation:** B identifies a coffee table. Desk presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 237. evaluation_1189: `nearness of walls`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A table and bench sitting next to a couple of pots by a fireplace.
>
> **Caption B:** A living room with a large fire place and a painting on it's wall.
>
> **Adopted scope:** wall spacing
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption supplies distances between room walls.

**Audit explanation:** Both room descriptions leave wall spacing unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 238. evaluation_1191: `size of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A stove in a kitchen that is lit by the sun through the window.
>
> **Caption B:** A kitchen area with a stovetop oven and white counter space that extends down the length of the kitchen.
>
> **Adopted scope:** room size
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Sunlight and a counter spanning the kitchen do not establish either room's dimensions.

**Audit explanation:** Both kitchen sizes remain unspecified. Counter length leaves overall room dimensions unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 239. evaluation_1193: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black and white image of a tall tower with clouds in the background
>
> **Caption B:** A huge ornate building and a tower with a clock next to the water.
>
> **Adopted scope:** structure color
>
> **Extracted A:** unspecified monochrome photo
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Monochrome photography and building scale do not supply real structure colors.

**Audit explanation:** Both structure colors remain unspecified. Monochrome photographic style leaves actual building hues unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 240. evaluation_1205: `presence of wine glass`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a wine glass next to a plate with some fish and veggies on it
>
> **Caption B:** A plate of food on a place mat on a wooden table with a fork and spoon.
>
> **Adopted scope:** wine-glass presence
>
> **Extracted A:** present
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second meal description provides no wine-glass information.

**Audit explanation:** B describes food and cutlery. Wine-glass presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 241. evaluation_1213: `maturation of fruit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S6`.

> **Caption A:** A person is taking an apple from several boxes of apples that are for sale.
>
> **Caption B:** A tree branch with various green and red colored fruit hanging in bunches with the sunlight coming from behind the apples.
>
> **Adopted scope:** fruit maturation state
>
> **Extracted A:** market apples, maturity not explicit
>
> **Extracted B:** red and green tree apples, maturity not established
>
> **Recorded reason, verbatim:** Apple color can reflect variety, and sales or tree location does not reliably identify both ripeness states.

**Audit explanation:** Market sale and red or green skin leave apple maturation unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 242. evaluation_1221: `wearing scarf`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young woman in designer eyeglasses wears a scarf and carries an umbrella over her head.
>
> **Caption B:** A person walks between buildings on a city street and carries a red umbrella.
>
> **Adopted scope:** scarf wearing
>
> **Extracted A:** yes
>
> **Extracted B:** unknown
>
> **Recorded reason, verbatim:** The second person's unspecified clothing does not establish scarf presence or absence.

**Audit explanation:** B identifies a person and umbrella. Scarf wearing remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 243. evaluation_1222: `activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bench sitting positioned next to a body of water on a snowy day.
>
> **Caption B:** A pond in the woods with a small dock and boats at the dock.
>
> **Adopted scope:** activity
>
> **Extracted A:** none stated
>
> **Extracted B:** none stated
>
> **Recorded reason, verbatim:** Both descriptions are static settings without an activity.

**Audit explanation:** Both waterside arrangements leave activity unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 244. evaluation_1223: `color of water`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bench sitting positioned next to a body of water on a snowy day.
>
> **Caption B:** A pond in the woods with a small dock and boats at the dock.
>
> **Adopted scope:** water color
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither water body has a stated color.

**Audit explanation:** Both water colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 245. evaluation_1225: `content visible on screens`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A computer screen showing photos on it while a smokestack is visible out the window
>
> **Caption B:** Two lap top computers are open and on side by side on a desk.
>
> **Adopted scope:** screen content
>
> **Extracted A:** photos
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second open laptops have no described screen content.

**Audit explanation:** B identifies open laptops. Screen contents remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 246. evaluation_1228: `design of tie`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A button down shirt with a tie and flower pinned to the lapel of a jacket.
>
> **Caption B:** A person in a green shirt and wide, brown belt is wearing a yellow polka-dotted tie with a cat embroidered on it.
>
> **Adopted scope:** tie design
>
> **Extracted A:** unspecified
>
> **Extracted B:** yellow dotted cat embroidery
>
> **Recorded reason, verbatim:** The first flower is on the lapel and supplies no tie design.

**Audit explanation:** A identifies a tie. Its design remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 247. evaluation_1236: `activity of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A view looking outside a train window by a table with a flower vase.
>
> **Caption B:** A train traveling under a setting sun in a pink and orange cloudy sky.
>
> **Adopted scope:** people activity
>
> **Extracted A:** none stated
>
> **Extracted B:** none stated
>
> **Recorded reason, verbatim:** A camera viewpoint through a train window does not establish a described person's activity.

**Audit explanation:** Both train descriptions leave people and their activity unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 248. evaluation_1237: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A view looking outside a train window by a table with a flower vase.
>
> **Caption B:** A train traveling under a setting sun in a pink and orange cloudy sky.
>
> **Adopted scope:** train color
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Pink and orange describe the sky, not the train.

**Audit explanation:** Both train colors remain unspecified. Pink and orange describe B's sky.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 249. evaluation_1258: `name of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** Man with turban taxiing woman in sheer veil atop an elephant with decorated brow and trunk top.
>
> **Caption B:** A cement elephant with large tusks is the focal point of this outdoor arrangement that includes palm trees and big rocks.
>
> **Adopted scope:** animal type
>
> **Extracted A:** live elephant
>
> **Extracted B:** cement elephant statue
>
> **Recorded reason, verbatim:** A cement elephant is a representation rather than an actual animal.

**Audit explanation:** B identifies a cement elephant statue. An actual animal to classify remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 250. evaluation_1270: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A black and white cat that is sitting under an open umbrella that is laid on the floor.
>
> **Caption B:** A cat resting comfortably on a red piece of luggage next to a wooden rail.
>
> **Adopted scope:** animal color
>
> **Extracted A:** black white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The red luggage does not identify the second cat's color.

**Audit explanation:** B gives luggage color. Cat coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 251. evaluation_1271: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A black and white cat that is sitting under an open umbrella that is laid on the floor.
>
> **Caption B:** A cat resting comfortably on a red piece of luggage next to a wooden rail.
>
> **Adopted scope:** animal color
>
> **Extracted A:** black white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second cat lacks a coat-color description.

**Audit explanation:** B identifies a cat. Red describes luggage, leaving cat coat color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 252. evaluation_1277: `contents of receptacle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A bag with a laptop, money, phone, keys and pens lying next to it.
>
> **Caption B:** The carry-on bag holds many essentials, such as an umbrella, toiletries, and some books.
>
> **Adopted scope:** contents inside bags
>
> **Extracted A:** items lying next to bag, contents unstated
>
> **Extracted B:** umbrella toiletries books inside bag
>
> **Recorded reason, verbatim:** Objects beside the first bag do not establish its internal contents.

**Audit explanation:** A locates items beside the bag. Its internal contents remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 253. evaluation_1284: `nearness of walls`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An old cluttered bathroom with a blue toilet, yellow bidet, yellow bathtub, and dark tiled walls.
>
> **Caption B:** A urinal high off the floor next to a urinal low to the floor.
>
> **Adopted scope:** wall spacing
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Fixture heights and clutter do not determine distances between walls.

**Audit explanation:** Both bathroom descriptions leave wall spacing unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 254. evaluation_1287: `size of object on table or desk`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** There is a small cell phone, a pack of gum, and a set of headphones on the table.
>
> **Caption B:** A pair of glasses sitting on a desk next to a cell phone and laptop.
>
> **Adopted scope:** object size
>
> **Extracted A:** small phone
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second phone and laptop lack size descriptions.

**Audit explanation:** B identifies desk objects. Their sizes remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 255. evaluation_1288: `size of bed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A large white bed topped with a white blanket and pillows under framed pictures.
>
> **Caption B:** A room with a bed, several pillows, a headboard and a lamp in it.
>
> **Adopted scope:** bed size
>
> **Extracted A:** large
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second bed has no size or build descriptor.

**Audit explanation:** B identifies a bed. Its size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 256. evaluation_1290: `size of clock`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A stone church steeple with a clock points upwards to a bright blue sky with clouds.
>
> **Caption B:** A very tall brick clock tower with a clock on each of it's sides.
>
> **Adopted scope:** clock size
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Steeple and tower height do not determine clock-face size.

**Audit explanation:** Both clock sizes remain unspecified. Tower heights concern the surrounding structures.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 257. evaluation_1294: `size of furniture`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A long table with various food items on the table including grapes, cheese and crackers, sandwiches, oranges and beverages.
>
> **Caption B:** A dining table with bare plates and plates of food on a colorful table cloth.
>
> **Adopted scope:** table size
>
> **Extracted A:** long
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second dining table has no size descriptor.

**Audit explanation:** B identifies a dining table. Its size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 258. evaluation_1298: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** People are walking around a buildings and there is big clock in the middle
>
> **Caption B:** A close up of the front of a building with a piece of art with a clock.
>
> **Adopted scope:** people count
>
> **Extracted A:** plural
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second building close-up supplies no people count.

**Audit explanation:** B describes a building and clock. Person count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 259. evaluation_1302: `action`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The rear view of a silver car under a very cloudy sky at an intersection.
>
> **Caption B:** A stop sign with two orange flags waving in the breeze on a stormy day.
>
> **Adopted scope:** action
>
> **Extracted A:** car motion unstated
>
> **Extracted B:** flags waving
>
> **Recorded reason, verbatim:** The first car's location does not establish an action.

**Audit explanation:** A locates a car at an intersection. Its action and movement remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 260. evaluation_1306: `type of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** this is a old photo of a railroad with a large building behind it
>
> **Caption B:** An old-time sepia photo of a street with a horse and buggy riding by
>
> **Adopted scope:** vehicle type
>
> **Extracted A:** no vehicle stated railroad only
>
> **Extracted B:** horse buggy
>
> **Recorded reason, verbatim:** Railroad tracks alone do not establish a train or other vehicle.

**Audit explanation:** A establishes a railroad. A vehicle to identify remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 261. evaluation_1315: `name of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** During a baseball game, a pitcher is throwing the ball while the batter is preparing to swing at it.
>
> **Caption B:** This photo from the stands shows a batter at plate waiting for the pitcher.
>
> **Adopted scope:** person name
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** No baseball participant is personally named.

**Audit explanation:** Both captions leave personal names unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 262. evaluation_1324: `transport vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A large gray and black suitcase in a parking lot, next to a vehicle
>
> **Caption B:** A view of the Tarmac of an airport with a jet and multiple service vehicles.
>
> **Adopted scope:** transport vehicle type
>
> **Extracted A:** unspecified vehicle beside suitcase
>
> **Extracted B:** jet and service vehicles
>
> **Recorded reason, verbatim:** The first only repeats the target category vehicle without supplying a vehicle type.

**Audit explanation:** A locates a vehicle beside luggage. Vehicle type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 263. evaluation_1326: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A road sign that reads "STOP here on RED" on the shoulder of a rural highway.
>
> **Caption B:** A stop sign with two orange flags waving in the breeze on a stormy day.
>
> **Adopted scope:** sign color
>
> **Extracted A:** unspecified RED is text
>
> **Extracted B:** red stop sign inferred
>
> **Recorded reason, verbatim:** The word RED in an instruction does not establish the sign's actual color.

**Audit explanation:** A's RED belongs to the sign's instruction. The sign's physical color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 264. evaluation_1336: `color of product packaging`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** Sweet treats rest temptingly on round, white plates as two bottles of beverage are nestled among them.
>
> **Caption B:** A plate full of food sitting on a table with other items and cash.
>
> **Adopted scope:** serving-package color
>
> **Extracted A:** white plates
>
> **Extracted B:** unspecified plate
>
> **Recorded reason, verbatim:** The second serving plate or packaging color is unstated.

**Audit explanation:** B identifies a plate. Its color remains unspecified under the recorded serving-package scope.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 265. evaluation_1347: `name of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman is sitting in a booth at a restaurant with empty dishes while on her laptop.
>
> **Caption B:** A woman looking at a laptop, with the sun cause a glare on the screen.
>
> **Adopted scope:** place
>
> **Extracted A:** restaurant booth
>
> **Extracted B:** unspecified sunny setting
>
> **Recorded reason, verbatim:** Sun glare on a laptop does not identify the second person's venue.

**Audit explanation:** B identifies a woman and laptop. Surrounding place type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 266. evaluation_1357: `name of places`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An old man with a dog and another man with a bowl in bed.
>
> **Caption B:** the men are sitting with their legs up and a dog is with them.
>
> **Adopted scope:** place
>
> **Extracted A:** bed
>
> **Extracted B:** seating location unspecified
>
> **Recorded reason, verbatim:** Raised legs and a dog do not identify the second men's resting place.

**Audit explanation:** B describes seated men. Their furniture and place remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 267. evaluation_1358: `size of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A small red couch in a living room with a coffee table topped with a flat screen tv
>
> **Caption B:** A living room with a lot of items including boxes, a sofa and entertainment system among other things.
>
> **Adopted scope:** furniture size
>
> **Extracted A:** small couch
>
> **Extracted B:** unspecified sofa
>
> **Recorded reason, verbatim:** The second sofa has no size or build information.

**Audit explanation:** B identifies a sofa. Its size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 268. evaluation_1362: `bicycle usage`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A street sign telling bicyclists to use the sidewalk with a stop sign at a street corner.
>
> **Caption B:** A person on their bike going through a green light with a bus nearby
>
> **Adopted scope:** bicycle use
>
> **Extracted A:** instruction only no observed cyclist
>
> **Extracted B:** riding through intersection
>
> **Recorded reason, verbatim:** An instruction for bicyclists does not establish actual bicycle use in the first scene.

**Audit explanation:** A states a cycling instruction. Actual observed bicycle use remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 269. evaluation_1363: `method of riding`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A street sign telling bicyclists to use the sidewalk with a stop sign at a street corner.
>
> **Caption B:** A person on their bike going through a green light with a bus nearby
>
> **Adopted scope:** riding method
>
> **Extracted A:** instruction sidewalk
>
> **Extracted B:** riding roadway
>
> **Recorded reason, verbatim:** The first sign specifies a rule, not an observed rider's method.

**Audit explanation:** A states a sidewalk instruction. An actual cyclist's riding method remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 270. evaluation_1369: `name of woman`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman is selling peppers at a local food market .
>
> **Caption B:** Asian market where women are selling various meats .
>
> **Adopted scope:** woman name
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither seller has a personal name.

**Audit explanation:** Both women's names remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 271. evaluation_1377: `presence of umpire`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A girl in dark blue baseball uniform throws a ball while two other baseball players runs around .
>
> **Caption B:** The number ten player on the white softball team gets tagged at base by a girl on the other team .
>
> **Adopted scope:** umpire presence
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither game description establishes an umpire's presence or absence.

**Audit explanation:** Both game descriptions leave umpire presence unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 272. evaluation_1405: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A bird is splashing in the water next to the swimming dog wearing the blue collar .
>
> **Caption B:** There is a brown dog swimming outside with a tennis ball in its mouth .
>
> **Adopted scope:** principal dog color
>
> **Extracted A:** unspecified
>
> **Extracted B:** brown
>
> **Recorded reason, verbatim:** Blue describes the collar, leaving the first dog's coat color unknown.

**Audit explanation:** A gives collar color. Principal dog coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 273. evaluation_1411: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A jockey in blue rides a horse at a galloping pace .
>
> **Caption B:** A woman on a gray and white horse is jumping over an obstacle .
>
> **Adopted scope:** horse color
>
> **Extracted A:** unspecified
>
> **Extracted B:** gray white
>
> **Recorded reason, verbatim:** The jockey's blue clothing does not identify the first horse's color.

**Audit explanation:** A gives jockey clothing color. Horse coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 274. evaluation_1415: `number of people watching`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Cowboy riding a bucking horse in a rodeo competition .
>
> **Caption B:** A rodeo star rides a bucking bronco as the large crowd watches them .
>
> **Adopted scope:** watcher count
>
> **Extracted A:** unspecified
>
> **Extracted B:** large crowd
>
> **Recorded reason, verbatim:** Rodeo competition does not give the first spectator count.

**Audit explanation:** A identifies a rider. Observer count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 275. evaluation_1417: `items held by children`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a casual short-sleeve button down shirt and glasses holding a little boy wearing a blue hat and chewing on a multicolored toy .
>
> **Caption B:** A man sits on top of a blue ball , and holds an infant , while a smiling toddler behind him hangs onto his back .
>
> **Adopted scope:** child-held items
>
> **Extracted A:** toy
>
> **Extracted B:** none stated
>
> **Recorded reason, verbatim:** The second children hold a person but no comparable nonhuman item is described.

**Audit explanation:** B identifies children. Objects held by a child remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 276. evaluation_1467: `location`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog leaps over a wooden fence as another is about to .
>
> **Caption B:** Two different breeds of brown and white dogs play on the beach .
>
> **Adopted scope:** location
>
> **Extracted A:** wooden fence unspecified setting
>
> **Extracted B:** beach
>
> **Recorded reason, verbatim:** A wooden fence does not identify the first broader setting to compare with a beach.

**Audit explanation:** A identifies a wooden-fence obstacle. The recorded broader surrounding location remains unspecified for comparison with B's beach.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 277. evaluation_1495: `brightness of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A skateboarder high in the air above an indoor ramp .
>
> **Caption B:** A skateboarder is balancing on a wooden box in a dark room .
>
> **Adopted scope:** room brightness
>
> **Extracted A:** unspecified indoor
>
> **Extracted B:** dark
>
> **Recorded reason, verbatim:** An indoor ramp does not establish the first room's brightness.

**Audit explanation:** A identifies an indoor ramp. Room brightness remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 278. evaluation_1506: `type of bird`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Long-necked , flying white bird grazes water with black legs .
>
> **Caption B:** A large bird spreading his wings in flight over a body of water .
>
> **Adopted scope:** bird type
>
> **Extracted A:** long-necked white bird, type unstated
>
> **Extracted B:** large bird, type unstated
>
> **Recorded reason, verbatim:** Size, color and flight description do not identify the requested bird subtype in both captions.

**Audit explanation:** Both bird descriptions leave type and species unspecified despite appearance and flight details.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 279. evaluation_1512: `ambiance of location`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A lady is at a bowling alley and throwing a red ball and there is a lady on the projector screen .
>
> **Caption B:** A woman wearing a green shirt is attending cosmic bowling at the MonsterBowl .
>
> **Adopted scope:** location ambiance
>
> **Extracted A:** unspecified bowling alley
>
> **Extracted B:** cosmic bowling lighting
>
> **Recorded reason, verbatim:** A standard bowling location does not establish the first scene's lighting or ambiance.

**Audit explanation:** A identifies bowling and a projection screen. Venue ambiance remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 280. evaluation_1532: `sentiment of dogs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two dog play with ball while one makes a big jump
>
> **Caption B:** A brown dog is doing amazing stunts in the dog show .
>
> **Adopted scope:** dog sentiment
>
> **Extracted A:** playful
>
> **Extracted B:** stunt performance unspecified emotion
>
> **Recorded reason, verbatim:** Performing stunts does not establish the second dog's emotional state.

**Audit explanation:** B evaluates the dog's stunts. Its emotion remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 281. evaluation_1569: `method of cooking`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person is cutting a piece of fish on a wooden block that is itself on top of a grill .
>
> **Caption B:** There is a man with a green t-shirt cooking hamburgers and hotdogs outside on a grill .
>
> **Adopted scope:** cooking method
>
> **Extracted A:** cutting fish at grill
>
> **Extracted B:** grilling
>
> **Recorded reason, verbatim:** Cutting fish on a board above a grill does not establish the first cooking method.

**Audit explanation:** A identifies fish cutting above a grill. Cooking method remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 282. evaluation_1599: `clothing of boys`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Young boy in a red shirt and white socks jumps down an inflatable slide .
>
> **Caption B:** A young boy poses behind the netting of an enclosed play area while three other children play .
>
> **Adopted scope:** boys clothing
>
> **Extracted A:** red shirt white socks
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second boys' clothing is unspecified.

**Audit explanation:** B identifies children. Their clothing remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 283. evaluation_1600: `distance player has to cross`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young baseball player leans in to catch the ball with his gloved right hand .
>
> **Caption B:** The boy in the green and yellow shirt has a glove on and is going towards the ball .
>
> **Adopted scope:** travel distance
>
> **Extracted A:** unspecified reach
>
> **Extracted B:** unspecified approach
>
> **Recorded reason, verbatim:** Neither reach nor approach description gives a travel distance.

**Audit explanation:** Both captions leave the boy's required travel or reach distance unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 284. evaluation_1633: `weather conditions`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bike rider in red rides through the trees down a snowy hill .
>
> **Caption B:** A mountain biker is riding along a heavy dirt trail in a wooded area .
>
> **Adopted scope:** weather
>
> **Extracted A:** snowy cold
>
> **Extracted B:** unspecified wooded dirt trail
>
> **Recorded reason, verbatim:** Dirt and woodland specify terrain but not the second weather conditions.

**Audit explanation:** B identifies wooded dirt terrain. Weather conditions remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 285. evaluation_1641: `hair type of persons`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man holds an upset-looking baby in front of a house .
>
> **Caption B:** Balding man holding toddler high up outdoors on a cloudy day .
>
> **Adopted scope:** adult hair
>
> **Extracted A:** unspecified
>
> **Extracted B:** balding
>
> **Recorded reason, verbatim:** The first man's hair is not described.

**Audit explanation:** A identifies a man. His hair remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 286. evaluation_1665: `color of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A dog runs on wet sand as a man in yellow pants walks further back .
>
> **Caption B:** A tan dog and a black dog with stick in mouth walking in water .
>
> **Adopted scope:** animal color
>
> **Extracted A:** unspecified
>
> **Extracted B:** tan black
>
> **Recorded reason, verbatim:** The first dog's coat color is unstated; the yellow pants belong to a person.

**Audit explanation:** A gives trouser color. Dog coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 287. evaluation_1683: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A toddler plays in a water fountain with his mouth open and ready for a drink .
>
> **Caption B:** A child in an orange shirt is holding a toy dog with his mouth wide open , standing in the sprinklers .
>
> **Adopted scope:** principal object color
>
> **Extracted A:** unspecified
>
> **Extracted B:** orange shirt
>
> **Recorded reason, verbatim:** No relevant first-side object color is supplied.

**Audit explanation:** A identifies fountain play. Relevant object color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 288. evaluation_1695: `type of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A man watches eagerly as his black dog leaps into the water .
>
> **Caption B:** A dog enjoys playing in the water at the edge of a field .
>
> **Adopted scope:** person type
>
> **Extracted A:** adult man
>
> **Extracted B:** no person stated
>
> **Recorded reason, verbatim:** The second caption gives no human whose type can be compared.

**Audit explanation:** B describes a dog. People to classify remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 289. evaluation_1705: `place they are jumping`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young boy jumps into the air using a trampoline .
>
> **Caption B:** A boy leaping in the air towards a soccer ball .
>
> **Adopted scope:** jumping place
>
> **Extracted A:** trampoline
>
> **Extracted B:** unspecified soccer setting
>
> **Recorded reason, verbatim:** The second jump's surface or location is not specified by the soccer ball.

**Audit explanation:** B identifies a soccer ball. The boy's jumping place remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 290. evaluation_1717: `color of shirt`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A small toddler wearing a stripe shirts and purple pants runs happily down a sidewalk .
>
> **Caption B:** A little girl in a floral print shirt is walking across a paved walkway .
>
> **Adopted scope:** shirt color
>
> **Extracted A:** unspecified stripes
>
> **Extracted B:** unspecified floral pattern
>
> **Recorded reason, verbatim:** Striped and floral identify patterns but no shirt hues.

**Audit explanation:** Both shirt hues remain unspecified. Stripes and floral prints identify patterns, and purple describes trousers.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 291. evaluation_1727: `apparel of individuals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person maneuvers rapids while riding a watercraft .
>
> **Caption B:** A person in an orange kayak navigates white water rapids .
>
> **Adopted scope:** apparel
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither person's clothing is described; orange belongs to the kayak.

**Audit explanation:** Both people's clothing remains unspecified. Orange describes B's kayak.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 292. evaluation_1735: `skateboard trick`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A young man in a blue hoodie doing a flip off of a half-wall that is covered in graffiti .
>
> **Caption B:** A young man in a black hat and white t-shirt is suspended in their air on his skateboard .
>
> **Adopted scope:** skateboard trick
>
> **Extracted A:** no skateboard stated
>
> **Extracted B:** airborne skateboard stunt
>
> **Recorded reason, verbatim:** An unaided flip is possible in the first, which supplies no skateboard.

**Audit explanation:** A identifies a flip. A skateboard and skateboard trick remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 293. evaluation_1740: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A child in a red parka slides down a snowy hill .
>
> **Caption B:** A small girl and a small boy use shovels to play in the snow .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** red
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second children's clothing colors are unstated.

**Audit explanation:** B identifies children playing in snow. Clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 294. evaluation_1753: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two dogs are playing with each other on a beach by the ocean .
>
> **Caption B:** A long-distance shot of a beach with people and animals .
>
> **Adopted scope:** people count
>
> **Extracted A:** unspecified
>
> **Extracted B:** plural
>
> **Recorded reason, verbatim:** The first dog-only scene gives no people count.

**Audit explanation:** A describes dogs. Person count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 295. evaluation_1792: `species of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white and black bird stretches its wings in midair .
>
> **Caption B:** Two seagulls on water , foreground bird has object held in beak .
>
> **Adopted scope:** animal species
>
> **Extracted A:** bird with species unstated
>
> **Extracted B:** seagulls
>
> **Recorded reason, verbatim:** Color and flight provide no species identity for the first bird.

**Audit explanation:** A gives bird colors and movement. Species remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 296. evaluation_1805: `presence of band`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in clown makeup and a suit is performing on stage .
>
> **Caption B:** A man is on stage singing , while the band plays behind him .
>
> **Adopted scope:** band presence
>
> **Extracted A:** unspecified
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** The first stage performance gives no information about a band.

**Audit explanation:** A identifies a stage performer. Band presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 297. evaluation_1819: `presence of observers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A rock climber checks his rope before holding on to the next spot on the rock .
>
> **Caption B:** A man in a blue shirt climbs a rock while people behind him in red shirts watch .
>
> **Adopted scope:** observer presence
>
> **Extracted A:** unspecified
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** The first climber's description supplies no observer-presence information.

**Audit explanation:** A identifies a climber. Observer presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 298. evaluation_1820: `color`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A man in a blue jacket riding a dog sled over a snow covered plain .
>
> **Caption B:** Two groups of huskies are running in the snow , each group pulling a man .
>
> **Adopted scope:** principal clothing color
>
> **Extracted A:** blue
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second riders' clothing colors are unstated.

**Audit explanation:** B identifies sledding participants. Their clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 299. evaluation_1827: `number of bushes`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bicyclist is attempting a trick over a jump nearby a bush and wooden building .
>
> **Caption B:** Man doing a trick on his bike by jumping in the air while he is on it .
>
> **Adopted scope:** bush count
>
> **Extracted A:** one
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second bicycle jump supplies no bush count.

**Audit explanation:** B describes a bicycle trick. Bush count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 300. evaluation_1839: `type of aerial recreation`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Someone is hang gliding or parachuting down by a large body of water with green hills all around .
>
> **Caption B:** This active person is sky flying in the beautiful and clam blue sky .
>
> **Adopted scope:** aerial recreation
>
> **Extracted A:** hanggliding or parachuting
>
> **Extracted B:** sky flying unspecified
>
> **Recorded reason, verbatim:** Generic sky flying does not identify a type or method of aerial recreation.

**Audit explanation:** B identifies generic sky flying. The form of aerial recreation remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 301. evaluation_1852: `color of outfit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A BMX bike rider in a black and red uniform on a dirt bike .
>
> **Caption B:** A motorcycle rider navigating his bike over a stone obstacle .
>
> **Adopted scope:** outfit color
>
> **Extracted A:** black red
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second rider's outfit has no colors stated.

**Audit explanation:** B identifies a motorcycle rider. Outfit colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 302. evaluation_1884: `height of animal`

**Current status:** `excluded_scope`. **Semantic rating:** `excluded/null`. **Policy:** `S7`.

> **Caption A:** A dog is jumping in the air in a field of grass .
>
> **Caption B:** The black dog jumps out of the snow to catch an object .
>
> **Adopted scope:** animal height: stature versus elevation
>
> **Extracted A:** dog jumping in grass, stature unstated
>
> **Extracted B:** dog jumping out of snow, stature unstated
>
> **Recorded reason, verbatim:** This duplicates the ambiguity approved for train_6591. Stature is missing in both captions, while elevation has partial airborne information; plausible readings change validity.

**Audit explanation:** Animal height admits stature and jump-elevation readings. Stature remains unspecified, while both captions supply only coarse airborne elevation.

**Recorded scope readings:**

> - **animal body stature:** invalid.
> - **animal elevation above supporting surface:** rating 3.

**Policy check:** Review exclusion policy. **Peer:** `writer_validation`.

**Review question:** Should the stature reading follow frozen train_11207, or should stature and jump elevation remain competing features?

**History:** supplied source rating `5.0`.

### 303. evaluation_1893: `starting point of jump`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A child jumps off of a swing while it is in motion .
>
> **Caption B:** A kid in a blue top leaps into a raked pile of leaves in front of trees .
>
> **Adopted scope:** jump origin
>
> **Extracted A:** swing
>
> **Extracted B:** unspecified near leaf pile
>
> **Recorded reason, verbatim:** A leaf pile identifies the landing destination, not the second jump's origin.

**Audit explanation:** B identifies a jump destination. The starting point remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 304. evaluation_1909: `team affiliation`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A boy shutting his eyes mid swing during a baseball game .
>
> **Caption B:** A boy playing for the Giants baseball team swinging at a baseball .
>
> **Adopted scope:** team affiliation
>
> **Extracted A:** unspecified
>
> **Extracted B:** Giants
>
> **Recorded reason, verbatim:** The first player's team affiliation is not supplied.

**Audit explanation:** A identifies a baseball player. Team affiliation remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 305. evaluation_1919: `surface color`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog runs on the green grass near a wooden fence .
>
> **Caption B:** A black and white dog chasing a tan and white dog across a path .
>
> **Adopted scope:** surface color
>
> **Extracted A:** green grass
>
> **Extracted B:** unspecified path
>
> **Recorded reason, verbatim:** The second path's surface color is unstated.

**Audit explanation:** B identifies a path. Surface color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 306. evaluation_1943: `color`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** a man is climbing a wall with blue , orange and purple pegs in it .
>
> **Caption B:** A climber in a red shirt is secured by a rope as he looks down a crevasse .
>
> **Adopted scope:** climber clothing color
>
> **Extracted A:** unspecified
>
> **Extracted B:** red
>
> **Recorded reason, verbatim:** The first colors belong to climbing pegs, not the climber's clothing.

**Audit explanation:** A gives climbing-peg colors. Climber clothing color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 307. evaluation_1944: `type of bird`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Black bird flying with a leafy branch in its mouth .
>
> **Caption B:** A white and black bird stretches its wings in midair .
>
> **Adopted scope:** bird subtype
>
> **Extracted A:** black bird, subtype unstated
>
> **Extracted B:** black-white bird, subtype unstated
>
> **Recorded reason, verbatim:** Coat colors do not identify either requested bird type.

**Audit explanation:** Both bird subtypes remain unspecified. Plumage colors leave species identity unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 308. evaluation_1981: `gender`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a man wearing a white helmet is abseiling down a sandy colored rock face .
>
> **Caption B:** A person is climbing a cliff wall , over a rocky shore , using a rope .
>
> **Adopted scope:** gender
>
> **Extracted A:** male
>
> **Extracted B:** unspecified person
>
> **Recorded reason, verbatim:** The second climber has no gender description.

**Audit explanation:** B identifies a person. Gender remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 309. evaluation_1983: `person doing cooking`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** One man cooking food on a grill for a lot of people , possibly a party or a big family .
>
> **Caption B:** A man in a Las Vegas t-shirt smiles while meat is being cooked on a grill in the background .
>
> **Adopted scope:** cook type
>
> **Extracted A:** man
>
> **Extracted B:** cook unspecified man nearby
>
> **Recorded reason, verbatim:** Standing near cooking meat does not establish that the second man is its cook.

**Audit explanation:** B locates a man near cooking meat. The cook's identity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 310. evaluation_1985: `presence of cart`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman with flowers looking at the produce section in a grocery .
>
> **Caption B:** Man pushing shopping cart in a grocery store and shopping .
>
> **Adopted scope:** cart presence
>
> **Extracted A:** unspecified
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** The first grocery shopper is not stated to have a cart.

**Audit explanation:** A identifies grocery shopping. Cart presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 311. evaluation_1995: `absence of backpack`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A snowshoer wearing a red jacket and black pants descends a snowy slope .
>
> **Caption B:** Trekking through the snow in the mountains with a full size backpack on .
>
> **Adopted scope:** backpack absence
>
> **Extracted A:** unknown
>
> **Extracted B:** false backpack present
>
> **Recorded reason, verbatim:** The first snowshoer's description does not establish backpack absence.

**Audit explanation:** A describes a snowshoer. Backpack absence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 312. evaluation_1996: `invalid`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Asian friends standing in the street in busy part of town .
>
> **Caption B:** A group of girls in black and white spotted skirts cross a street .
>
> **Adopted scope:** invalid condition
>
> **Extracted A:** no semantic feature
>
> **Extracted B:** no semantic feature
>
> **Recorded reason, verbatim:** The literal condition invalid supplies no semantic feature to compare.

**Audit explanation:** The literal condition invalid leaves the requested comparison feature undefined.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 313. evaluation_2015: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A climber with a yellow backpack walks along the ridge of a snowy mountainside .
>
> **Caption B:** A person in a red hat with a huge backpack going hiking .
>
> **Adopted scope:** backpack color
>
> **Extracted A:** yellow
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Red belongs to the hat, leaving the second backpack color unstated.

**Audit explanation:** B gives hat color and backpack size. Backpack color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 314. evaluation_2023: `animal's focus`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The dog rounds the curve coming out of the woods .
>
> **Caption B:** A dog approachs a small creature in a barren , snowy field .
>
> **Adopted scope:** animal attention
>
> **Extracted A:** unspecified while rounding curve
>
> **Extracted B:** small creature
>
> **Recorded reason, verbatim:** Rounding a curve supplies movement but no target of the first dog's attention.

**Audit explanation:** A describes a dog's route. Its attention target remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 315. evaluation_2027: `gender`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person in a red shirt doing tricks on a bicycle .
>
> **Caption B:** A man on a bike rides on the ramp and flips his bike as he comes down .
>
> **Adopted scope:** gender
>
> **Extracted A:** unspecified person
>
> **Extracted B:** male
>
> **Recorded reason, verbatim:** The first person has no stated gender.

**Audit explanation:** A identifies a person. Gender remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 316. evaluation_2039: `listening to music`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a purple hat , white shirt , wearing earbuds , listening to music , sitting outside a city building .
>
> **Caption B:** A person wearing a shirt with a rainbow on it sits on a sidewalk with legs crossed .
>
> **Adopted scope:** music listening
>
> **Extracted A:** yes
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second seated person is not described listening to music.

**Audit explanation:** B describes a seated person. Music listening remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 317. evaluation_2043: `gear worn`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young male with a black helmet and elbow guards does a bike trick .
>
> **Caption B:** A guy in a yellow shirt with a bike gets very high in the air .
>
> **Adopted scope:** protective gear
>
> **Extracted A:** helmet elbow guards
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second yellow shirt does not establish any protective gear.

**Audit explanation:** B gives shirt color. Protective gear remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 318. evaluation_2061: `gender of audience`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A group of people listen to man standing at a podium .
>
> **Caption B:** Man in white t-shirt giving speech to a group of men .
>
> **Adopted scope:** audience gender
>
> **Extracted A:** unspecified group
>
> **Extracted B:** men
>
> **Recorded reason, verbatim:** The first audience is a group without gender information.

**Audit explanation:** A identifies an audience. Audience members' genders remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 319. evaluation_2073: `color of bull`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A man wearing yellow and blue is riding a large , bucking bull .
>
> **Caption B:** A bull rider , in full padding and wearing a helmet , rides a large brown and white bull .
>
> **Adopted scope:** bull color
>
> **Extracted A:** unspecified
>
> **Extracted B:** brown white
>
> **Recorded reason, verbatim:** Yellow and blue describe the rider, leaving the first bull's color unstated.

**Audit explanation:** A gives rider clothing colors. Bull coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 320. evaluation_2078: `color of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** There is a rider on a dirt bike in race gear on a paved track .
>
> **Caption B:** Someone on a white motorcycle wearing black and red driving down a road .
>
> **Adopted scope:** vehicle color
>
> **Extracted A:** unspecified
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** The first dirt bike's color is not supplied.

**Audit explanation:** A identifies a dirt bike. Its color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 321. evaluation_2082: `type of skateboarding trick`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Young male nose sliding a skateboard down a 3-step rail .
>
> **Caption B:** A skateboarder doing a trick off a quarter pipe .
>
> **Adopted scope:** skateboarding maneuver type
>
> **Extracted A:** nose slide
>
> **Extracted B:** unspecified trick off quarter pipe
>
> **Recorded reason, verbatim:** The obstacle identifies where the second trick occurs but not its maneuver type.

**Audit explanation:** B identifies a trick's obstacle. Maneuver type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 322. evaluation_2086: `type of produce`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Asian marketplace vendor looking over her wide selection of vegetables .
>
> **Caption B:** A man is sitting behind a large collection of produce .
>
> **Adopted scope:** produce type
>
> **Extracted A:** vegetables
>
> **Extracted B:** unspecified produce
>
> **Recorded reason, verbatim:** Generic produce does not identify a produce subtype, unlike the explicit vegetables in the first.

**Audit explanation:** B identifies generic produce. Produce category remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 323. evaluation_2101: `color of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The big brown dog looks at the small black dog in tall grass .
>
> **Caption B:** A dog walks in the grass towards a dog lying down .
>
> **Adopted scope:** animal colors
>
> **Extracted A:** brown black
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither second-side dog's color is stated.

**Audit explanation:** B identifies dogs. Coat colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 324. evaluation_2114: `presence of snow`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A reddish brown dog runs across the snow with a snowball in its mouth .
>
> **Caption B:** Two brown dogs trot along frozen ground in a rural setting .
>
> **Adopted scope:** snow presence
>
> **Extracted A:** yes
>
> **Extracted B:** frozen ground unspecified snow
>
> **Recorded reason, verbatim:** Frozen ground can be bare, so the second snow presence is unknown.

**Audit explanation:** B identifies frozen ground. Snow presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 325. evaluation_2119: `position of dogs relative to one another`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black dog is chasing another dog along the beach .
>
> **Caption B:** Two dogs are making a turn on a soft sand beach .
>
> **Adopted scope:** dogs' positions relative to each other
>
> **Extracted A:** one behind the other in a chase
>
> **Extracted B:** both turning, arrangement unspecified
>
> **Recorded reason, verbatim:** A shared turn gives no relative ordering or separation between the second pair.

**Audit explanation:** B says both dogs turn. Their positions relative to each other remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 326. evaluation_2151: `object a child is holding`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A child holding snow in his hand amongst a snowy background .
>
> **Caption B:** a small boy in a blue jacket climbs into a power wheels vehicle
>
> **Adopted scope:** held object
>
> **Extracted A:** snow
>
> **Extracted B:** unspecified climbing into toy car
>
> **Recorded reason, verbatim:** Climbing into a toy vehicle does not establish an object held in the child's hands.

**Audit explanation:** B identifies entry into a toy vehicle. The child's held object remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 327. evaluation_2165: `absence of blue goggles`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A girl , wearing blue goggles and a striped swimsuit , plays in a swimming pool .
>
> **Caption B:** The little girl in her bathing suit stands near the sprinkers and squeals .
>
> **Adopted scope:** goggle absence
>
> **Extracted A:** false blue goggles present
>
> **Extracted B:** unknown
>
> **Recorded reason, verbatim:** The second girl's clothing description does not establish absence of blue goggles.

**Audit explanation:** B identifies a swimsuit. Blue-goggle absence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 328. evaluation_2176: `actions of individuals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young Asian girl and her doll on a shaded grassy lawn .
>
> **Caption B:** A little oriental girl glancing upward toward her right .
>
> **Adopted scope:** girl action
>
> **Extracted A:** unspecified with doll
>
> **Extracted B:** glancing upward
>
> **Recorded reason, verbatim:** Being with a doll on a lawn does not identify a first-side action.

**Audit explanation:** A locates a girl with a doll. The girl's action remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 329. evaluation_2178: `shirt color`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person on a brown horse wearing jeans , a plaid shirt , and a cowboy hat attempts to lasso a running calf .
>
> **Caption B:** A cowboy wearing a purple shirt and white hate hangs onto his bucking horse while a crowd watches in the background .
>
> **Adopted scope:** shirt color
>
> **Extracted A:** unspecified plaid
>
> **Extracted B:** purple
>
> **Recorded reason, verbatim:** Plaid identifies a pattern rather than the first shirt's color.

**Audit explanation:** A identifies a plaid shirt. Its colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 330. evaluation_2183: `background`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A small black and white dog jumps with red plastic fence in background .
>
> **Caption B:** A dog jumps up to catch an orange and blue tennis ball .
>
> **Adopted scope:** background
>
> **Extracted A:** red fence
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second dog jump has no described background.

**Audit explanation:** B describes a jumping dog. Background scenery remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 331. evaluation_2203: `age of skateboarders`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A child skateboarding and doing a trick in midair .
>
> **Caption B:** A skateboarder is riding his board on a ramp in a skate park .
>
> **Adopted scope:** skateboarder age
>
> **Extracted A:** child
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second skateboarder has no age descriptor.

**Audit explanation:** B identifies a skateboarder. Age category remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 332. evaluation_2213: `background`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A surfer in white striped wetsuit bottoms rides a wave .
>
> **Caption B:** The surfer is riding a wave with a mountain in the background .
>
> **Adopted scope:** background scenery
>
> **Extracted A:** unstated
>
> **Extracted B:** mountain
>
> **Recorded reason, verbatim:** The first gives surfing action without comparable background scenery.

**Audit explanation:** A identifies surfing. Background scenery remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 333. evaluation_2216: `specific activity involving football players`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Oklahoma University football players in front of a crowd of Sooners fans and next to three referees .
>
> **Caption B:** Football players in blue and orange uniforms are huddled together and hugging each other .
>
> **Adopted scope:** specific football-player activity
>
> **Extracted A:** no activity specified
>
> **Extracted B:** huddling and hugging
>
> **Recorded reason, verbatim:** The first players' positions among fans and referees do not establish a specific activity.

**Audit explanation:** A locates players near fans and referees. The players' activity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 334. evaluation_2219: `sentiment of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A kid on a mountain bike performing a trick high above the ground in a wooded setting .
>
> **Caption B:** A boy is flying in midair while snowboarding in a hilly and wooded area .
>
> **Adopted scope:** person sentiment
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Performing aerial tricks does not identify either child's feelings.

**Audit explanation:** Both airborne sporting actions leave participant sentiment unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 335. evaluation_2221: `Activity of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Little by and little girl wearing martial arts gown with yellow belts .
>
> **Caption B:** Two young girls sparring in white martial arts outfits while a third person watches from the side .
>
> **Adopted scope:** people's physical activity
>
> **Extracted A:** wearing martial-arts uniforms, action unstated
>
> **Extracted B:** sparring while another watches
>
> **Recorded reason, verbatim:** Uniforms establish a sport context but no action being performed by the first children.

**Audit explanation:** A identifies martial-arts clothing. The children's physical activity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 336. evaluation_2226: `position of swimmer's hands`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A female professional swimmer is in the middle of taking a breath in-between strokes during a heat .
>
> **Caption B:** A smiling girl is wearing a Speedo swimming suit , goggles and cap with her hands on her forehead .
>
> **Adopted scope:** swimmer hand position
>
> **Extracted A:** unstated between strokes
>
> **Extracted B:** on forehead
>
> **Recorded reason, verbatim:** Breathing between swimming strokes does not specify the first swimmer's hand positions.

**Audit explanation:** A identifies breathing between strokes. Hand positions remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 337. evaluation_2243: `color`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A big black dog bares its teeth while running through the snow .
>
> **Caption B:** A dog , wearing a coat , looks up from the snow .
>
> **Adopted scope:** principal dog color
>
> **Extracted A:** black
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second dog's coat garment does not identify its fur color.

**Audit explanation:** B identifies a dog wearing a coat. The dog's fur color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 338. evaluation_2253: `person's age`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Person on snow skis airborne over snow with green tree in the background .
>
> **Caption B:** A little kid dressed in cold-weather gear is at the top of the snow mound .
>
> **Adopted scope:** person age
>
> **Extracted A:** unstated
>
> **Extracted B:** little child
>
> **Recorded reason, verbatim:** The first skier's age is unstated.

**Audit explanation:** A identifies a skier. Age remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 339. evaluation_2259: `adversity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black dog and a brindle dog wrestle in the dry grass beside a body of water .
>
> **Caption B:** A brown dog is rolling over in the grass while a white and brown dog stands next to it .
>
> **Adopted scope:** adversity between dogs
>
> **Extracted A:** wrestling interaction
>
> **Extracted B:** rolling beside standing dog, conflict unspecified
>
> **Recorded reason, verbatim:** Rolling beside a standing dog does not establish an adverse interaction or its explicit absence.

**Audit explanation:** B identifies rolling and standing dogs. Adversity between them remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 340. evaluation_2273: `gender`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a white baseball uniform picking up a baseball .
>
> **Caption B:** A baseball player is throwing a pitch from the mound .
>
> **Adopted scope:** person gender
>
> **Extracted A:** man
>
> **Extracted B:** baseball player, gender unstated
>
> **Recorded reason, verbatim:** A baseball-player role does not identify the second person's gender.

**Audit explanation:** B identifies a baseball player. Gender remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 341. evaluation_2274: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Snowy mountainside with snow gear and poles in forefront .
>
> **Caption B:** A skier goes down a hill with a mountain as a backdrop .
>
> **Adopted scope:** people count
>
> **Extracted A:** no people established by equipment-only scene
>
> **Extracted B:** one skier
>
> **Recorded reason, verbatim:** Equipment alone establishes neither a person nor a supported zero count.

**Audit explanation:** A describes snow equipment. Human presence and person count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 342. evaluation_2281: `temperament of dogs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Brown dog and German shepherd standing near each other in the grass near water .
>
> **Caption B:** Two dogs with the same coloring look like they are going to bite each other in the face .
>
> **Adopted scope:** dog temperament
>
> **Extracted A:** unstated while standing together
>
> **Extracted B:** apparently aggressive, about to bite
>
> **Recorded reason, verbatim:** The first dogs' proximity gives no temperament information.

**Audit explanation:** A identifies dogs standing nearby. Temperament remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 343. evaluation_2285: `gender of group members`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A mid sized mixed gender choir sings while the director motions to keep beat .
>
> **Caption B:** A man standing in a white shirt is conducting a small group of violin players .
>
> **Adopted scope:** performing group members' genders
>
> **Extracted A:** mixed choir
>
> **Extracted B:** violin players' genders unstated
>
> **Recorded reason, verbatim:** The condition targets the choir and violin group members; the male conductor does not identify the violinists' genders.

**Audit explanation:** B identifies a male conductor. The violinists' genders remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 344. evaluation_2300: `color of surfing material`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A man rides a surfboard through rough white and blue water .
>
> **Caption B:** a guy riding a gnarly five foot wave all the way to the shore
>
> **Adopted scope:** surfing material/equipment color
>
> **Extracted A:** board color unstated; water white/blue
>
> **Extracted B:** board and water colors unstated
>
> **Recorded reason, verbatim:** Board colors are missing in both, and only the first water has stated colors.

**Audit explanation:** A's colors describe water. B leaves equipment and water colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 345. evaluation_2304: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A blond toddler wearing a blue sweater , riding on a wooden toy .
>
> **Caption B:** The small child is leaning back in a child swing .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** blue sweater
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second child's clothing color is absent.

**Audit explanation:** B identifies a child. Clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 346. evaluation_2341: `color of pants`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A soccer player wearing a gray shirt and black pants throwing a soccer ball .
>
> **Caption B:** A man with a number 3 soccer uniform kicking a soccer ball .
>
> **Adopted scope:** pants color
>
> **Extracted A:** black
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second player's uniform number supplies no pants color.

**Audit explanation:** B identifies a soccer uniform. Trouser color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 347. evaluation_2345: `size of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A small white dogs leaps over the back of a larger dog to chase his toy .
>
> **Caption B:** One brown and one white dog running through a field .
>
> **Adopted scope:** animal sizes
>
> **Extracted A:** small dog and larger dog
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Neither second dog has a size or build descriptor.

**Audit explanation:** B gives dog colors. Dog sizes remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 348. evaluation_2351: `color of dog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** White and brown dog with mouth open running on grass .
>
> **Caption B:** A dog with a red collar and its tongue hanging out runs through tall grass .
>
> **Adopted scope:** dog coat color
>
> **Extracted A:** white and brown
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Red describes a collar, not the second dog's fur.

**Audit explanation:** B gives collar color. Dog coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 349. evaluation_2357: `color of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two tan and white dogs look at each other in an outdoor setting .
>
> **Caption B:** Two dogs confront each other in the middle of a field
>
> **Adopted scope:** animal colors
>
> **Extracted A:** tan and white
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second dogs have no supplied coat colors.

**Audit explanation:** B identifies dogs. Coat colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 350. evaluation_2364: `type of market`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** Women wait under their umbrellas for customers at a fresh food market .
>
> **Caption B:** Four people in a tropical area with fruit that has been picked or harvested .
>
> **Adopted scope:** market type
>
> **Extracted A:** fresh-food market
>
> **Extracted B:** harvested-fruit scene, market unestablished
>
> **Recorded reason, verbatim:** Harvested fruit and people do not establish that the second scene is a market.

**Audit explanation:** B identifies harvested fruit. A market to classify remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 351. evaluation_2365: `type of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Women wait under their umbrellas for customers at a fresh food market .
>
> **Caption B:** Four people in a tropical area with fruit that has been picked or harvested .
>
> **Adopted scope:** food type
>
> **Extracted A:** fresh food, category unspecified
>
> **Extracted B:** fruit
>
> **Recorded reason, verbatim:** Freshness does not identify a food type; the first has only generic food.

**Audit explanation:** A identifies food freshness. Food category remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 352. evaluation_2369: `color of outfit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A male tennis player wearing a blue shirt and white shorts is depicted in action on a teal tennis court .
>
> **Caption B:** A tennis playing man jumps in the air , preparing to hit the ball to the other court .
>
> **Adopted scope:** outfit color
>
> **Extracted A:** blue and white
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second tennis player's outfit colors are unstated.

**Audit explanation:** B identifies a tennis player. Outfit colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 353. evaluation_2372: `action of players`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Three football players tackle another player who is holding a ball .
>
> **Caption B:** A group of football players in red and white uniforms .
>
> **Adopted scope:** player action
>
> **Extracted A:** tackling ball carrier
>
> **Extracted B:** unstated group action
>
> **Recorded reason, verbatim:** The second group is identified only through people and uniforms, with no player action.

**Audit explanation:** B identifies a football-player group. The players' action remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 354. evaluation_2375: `color of wearings`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** Young boy kicks a red and white soccer ball on a grassy field
>
> **Caption B:** A little boy wearing a green jersey playing soccer .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** unstated; ball red/white
>
> **Extracted B:** green jersey
>
> **Recorded reason, verbatim:** The red-white ball does not establish the first child's clothing color.

**Audit explanation:** A gives ball colors. Clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 355. evaluation_2377: `fur color`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a fluffy brown , white and black running on a path
>
> **Caption B:** A shaggy dog runs down a dirt trail in a lush forest .
>
> **Adopted scope:** fur color
>
> **Extracted A:** brown, white and black
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Shaggy fur describes texture, not color.

**Audit explanation:** B identifies shaggy fur. Fur color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 356. evaluation_2387: `motion`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Someone in yellow pants is on a ramp over the snow .
>
> **Caption B:** Man in puffy yellow jacket on skis on a mountain .
>
> **Adopted scope:** person motion
>
> **Extracted A:** unstated on ramp
>
> **Extracted B:** unstated on skis
>
> **Recorded reason, verbatim:** Being on a ramp or wearing skis does not establish actual movement.

**Audit explanation:** Ramp location and ski equipment leave both people's current movement unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 357. evaluation_2393: `sentiment of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man on a motorcycle riding on a track and waving .
>
> **Caption B:** A motorcyclist is leaning into a curve with his motorcycle
>
> **Adopted scope:** people sentiment
>
> **Extracted A:** unstated while waving
>
> **Extracted B:** unstated while riding
>
> **Recorded reason, verbatim:** Waving or leaning through a turn does not establish a person's emotional sentiment.

**Audit explanation:** Waving and cornering leave both riders' sentiments unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 358. evaluation_2403: `mood of music`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Concert in what seems to be a very small venue with a fair amount of people .
>
> **Caption B:** A rock concert in a darkly lit room in the middle of the lead singer belting out a verse .
>
> **Adopted scope:** music mood
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated despite rock genre and belting
>
> **Recorded reason, verbatim:** Neither venue scale nor rock genre establishes the music's mood.

**Audit explanation:** Venue size, rock genre and forceful singing leave the music's mood unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 359. evaluation_2405: `type of bicycle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bicyclist performing a trick over a heavily graffitied wall .
>
> **Caption B:** A man on a BMX bike performs a trick on a jump .
>
> **Adopted scope:** bicycle subtype
>
> **Extracted A:** bicycle used for trick, subtype unstated
>
> **Extracted B:** BMX bicycle
>
> **Recorded reason, verbatim:** Performing a trick does not reliably distinguish BMX from other stunt-capable bicycle types.

**Audit explanation:** A establishes bicycle stunt use. Bicycle subtype remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 360. evaluation_2415: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A dog is carrying a yellow rope across rocks covered in seaweed .
>
> **Caption B:** A small black and white dog carries a stick while swimming .
>
> **Adopted scope:** object color
>
> **Extracted A:** dog color unstated; rope yellow
>
> **Extracted B:** dog black/white; stick color unstated
>
> **Recorded reason, verbatim:** Dog color is missing first, while carried-object color is missing second; neither coherent scope supplies both colors.

**Audit explanation:** A leaves dog color unspecified, and B leaves stick color unspecified. The shared color comparison remains unavailable.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 361. evaluation_2417: `type of construction`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Men in orange vests are at work on a construction site .
>
> **Caption B:** The constructions workers are smoothing out freshly poured concrete .
>
> **Adopted scope:** construction type
>
> **Extracted A:** unstated
>
> **Extracted B:** concrete finishing
>
> **Recorded reason, verbatim:** A construction site and worker uniforms do not identify the construction task or type.

**Audit explanation:** A identifies construction work. Construction task and type remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 362. evaluation_2419: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A basketball player wearing a white uniform is dribbling the ball on the court .
>
> **Caption B:** A man in a USA team shirt is about to dunk a basketball .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** white
>
> **Extracted B:** unstated USA shirt color
>
> **Recorded reason, verbatim:** A USA team label does not determine the second shirt's color.

**Audit explanation:** B identifies a USA team shirt. Its color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 363. evaluation_2421: `position in the air`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A basketball player jumps up with the ball as two others watch .
>
> **Caption B:** The young Anderson player is attempting to shoot while his opponent and teammate look on .
>
> **Adopted scope:** principal player's airborne position
>
> **Extracted A:** jumping
>
> **Extracted B:** shooting attempt, elevation unstated
>
> **Recorded reason, verbatim:** A shooting attempt can occur with or without leaving the ground.

**Audit explanation:** B identifies a shooting attempt. Airborne position remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 364. evaluation_2425: `type of surfing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man windsurfs , putting his off hand into the water .
>
> **Caption B:** A surfboard is shown gliding through the water with a person standing on it .
>
> **Adopted scope:** surfing subtype
>
> **Extracted A:** windsurfing
>
> **Extracted B:** standing surfboard travel with propulsion unstated
>
> **Recorded reason, verbatim:** The second establishes board travel but no requested wind, wave or paddle surfing subtype.

**Audit explanation:** B identifies surfboard travel. Propulsion and surfing subtype remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 365. evaluation_2437: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A dog shows his teeth while playing with another dog .
>
> **Caption B:** A dog runs in the grss with a green toy in its mouth .
>
> **Adopted scope:** object color
>
> **Extracted A:** unstated dog/object colors
>
> **Extracted B:** green toy; dog color unstated
>
> **Recorded reason, verbatim:** The first supplies no object or animal color.

**Audit explanation:** A leaves dog and object colors unspecified. B identifies a green toy.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 366. evaluation_2442: `distance of skier`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A skier with ski sticks is cutting into the snow as he makes a sharp turn .
>
> **Caption B:** A person is seen in the distance skiing down a very steep mountain .
>
> **Adopted scope:** skier viewing distance
>
> **Extracted A:** unstated
>
> **Extracted B:** far away
>
> **Recorded reason, verbatim:** Describing a turn does not establish the first skier's distance from the viewer.

**Audit explanation:** A describes a skiing turn. Viewing distance remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 367. evaluation_2447: `size of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The brown dog is standing on the beach as the waves lap up around its feet .
>
> **Caption B:** A small furry brown dog is running on the shore of the ocean .
>
> **Adopted scope:** animal size
>
> **Extracted A:** unstated
>
> **Extracted B:** small
>
> **Recorded reason, verbatim:** The first dog has no size or build descriptor.

**Audit explanation:** A identifies a brown dog. Its size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 368. evaluation_2450: `color of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two tri-colored short dogs run away from the camera in the trees .
>
> **Caption B:** Two beige dogs are playing in the grass near a doghouse .
>
> **Adopted scope:** animal coat colors
>
> **Extracted A:** three unnamed colors
>
> **Extracted B:** beige
>
> **Recorded reason, verbatim:** Three-color diversity does not identify any hue for the requested coat-color comparison.

**Audit explanation:** A identifies three unnamed coat colors. B identifies beige. Whether color-count information supports a partial comparison requires policy review.

**Policy check:** Review exclusion policy. **Peer:** `writer_validation`.

**Review question:** Does the stated three-color coat supply partial color information under the colorful convention accepted for train_10852?

**History:** supplied source rating `1.0`.

### 369. evaluation_2455: `gender of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person walks down a wet city street holding an umbrella .
>
> **Caption B:** A woman dressed in a red coat is walking down a rainy street .
>
> **Adopted scope:** person gender
>
> **Extracted A:** unstated person
>
> **Extracted B:** woman
>
> **Recorded reason, verbatim:** The first generic person has no gender information.

**Audit explanation:** A identifies a person. Gender remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 370. evaluation_2469: `distance covered`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A brown dog chases a tattered ball around the yard .
>
> **Caption B:** A large brown dog is playing in the dirt and grass .
>
> **Adopted scope:** distance covered
>
> **Extracted A:** unstated while chasing ball
>
> **Extracted B:** unstated while playing
>
> **Recorded reason, verbatim:** Neither chasing nor playing supplies a travel distance.

**Audit explanation:** Chasing and playing leave both dogs' traveled distances unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 371. evaluation_2471: `animal's focus`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two light tan dogs of the same breed but different size are running in the woods .
>
> **Caption B:** Two dogs in a rocky field , face to face , with a stick between them .
>
> **Adopted scope:** animal focus
>
> **Extracted A:** unstated during running
>
> **Extracted B:** each other and intervening stick
>
> **Recorded reason, verbatim:** Running through woods does not identify the first dogs' attention target.

**Audit explanation:** A describes running dogs. Their attention target remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 372. evaluation_2480: `motion of girl`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A girl swimming with an innertube saying something .
>
> **Caption B:** A young girl in a pink swimsuit at the bottom of a water slide .
>
> **Adopted scope:** girl motion
>
> **Extracted A:** swimming
>
> **Extracted B:** unstated at slide bottom
>
> **Recorded reason, verbatim:** Being at a slide's bottom does not establish the girl's current motion.

**Audit explanation:** B locates a girl at a slide's bottom. Current motion remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 373. evaluation_2501: `trick or stunt being performed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A skateboarder does a trick off a dock while a photographer documents it .
>
> **Caption B:** Here is a young man skateboarding up the side of a skate pit .
>
> **Adopted scope:** specific skateboarding stunt
>
> **Extracted A:** unnamed trick off dock
>
> **Extracted B:** riding up skate-pit side
>
> **Recorded reason, verbatim:** The first launch location does not identify which trick or stunt is performed.

**Audit explanation:** A identifies a dock launch. The specific skateboarding trick remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 374. evaluation_2521: `color of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A male biker jumping a ramp in a contest or crossing the finish line .
>
> **Caption B:** A white , male , professional biker riding on the countryside .
>
> **Adopted scope:** person skin color
>
> **Extracted A:** unstated
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** The first rider's skin color is not supplied.

**Audit explanation:** A identifies a male biker. Skin color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 375. evaluation_2553: `sentiment of crowd`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A skateboarder performs a trick in front of a large crowd .
>
> **Caption B:** A crowd watches a many on a bicycle performing a stunt .
>
> **Adopted scope:** crowd sentiment
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Watching a performance does not establish crowd emotion.

**Audit explanation:** Both watching crowds leave sentiment unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 376. evaluation_2557: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The base runner attempts to make it safely to the bag .
>
> **Caption B:** A boy in a maroon shirt and cap with gloves playing in a baseball ground .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** unstated
>
> **Extracted B:** maroon shirt
>
> **Recorded reason, verbatim:** The first runner has no clothing-color information.

**Audit explanation:** A identifies a base runner. Clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 377. evaluation_2559: `attitude of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman and a man are playing the guitar while another man is singing .
>
> **Caption B:** A musical act wearing clown makeup is performing with a guitar .
>
> **Adopted scope:** people attitude
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated despite clown makeup
>
> **Recorded reason, verbatim:** Guitar performance and clown makeup do not establish personal attitude.

**Audit explanation:** Both musical performances leave performers' attitudes unspecified. Clown makeup identifies appearance.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 378. evaluation_2581: `position of the ball relative to the players`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two opposing male players are chasing the ball in field hockey .
>
> **Caption B:** A man reaches across another while playing a sport outside .
>
> **Adopted scope:** ball position relative to players
>
> **Extracted A:** ahead of chasing players
>
> **Extracted B:** ball not described
>
> **Recorded reason, verbatim:** The second generic sport description establishes no ball to locate.

**Audit explanation:** B identifies a sporting movement. A ball and its relative position remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 379. evaluation_2595: `variety of customers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Lots of people in a farmers market shopping for fruits and vegetables .
>
> **Caption B:** Ethnic people visiting picking fresh food to buy .
>
> **Adopted scope:** customer variety
>
> **Extracted A:** unstated demographic variety
>
> **Extracted B:** ethnic people, groups unspecified
>
> **Recorded reason, verbatim:** Crowd size does not establish demographic variety, and the second ethnic groups are also unnamed.

**Audit explanation:** Both descriptions leave distinct customer groups and demographic variety unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 380. evaluation_2608: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A lone fisherman casts off a rock with a city visible across the water .
>
> **Caption B:** A man in a blue raincoat standing in some water fishing .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** unstated
>
> **Extracted B:** blue raincoat
>
> **Recorded reason, verbatim:** The first fisherman's clothing color is unstated.

**Audit explanation:** A identifies a fisherman. Clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 381. evaluation_2612: `color of shirt`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A boy in a tie dyed shirt is riding a skateboard down a railing .
>
> **Caption B:** A boy in dark pants and green t-shirt rides his bike up a ramp .
>
> **Adopted scope:** shirt hue
>
> **Extracted A:** tie-dye treatment, hues unstated
>
> **Extracted B:** green
>
> **Recorded reason, verbatim:** A dye pattern does not identify the first shirt's actual colors.

**Audit explanation:** A identifies tie-dye treatment. Shirt hues remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 382. evaluation_2639: `number of riders`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** Two cowboys attempting to lasso a cow in a rodeo .
>
> **Caption B:** A man rides a horse while attempting to lasso a small bull .
>
> **Adopted scope:** rider count
>
> **Extracted A:** riding not established for roping cowboys
>
> **Extracted B:** one horse rider
>
> **Recorded reason, verbatim:** Roping cowboys may stand on the ground; riding is not established in the first.

**Audit explanation:** A identifies cowboys roping a cow. Actual riding and rider count remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 383. evaluation_2647: `item ingested`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A little kid plays on the equipment at the park .
>
> **Caption B:** Young female child swinging in a swing with a sippy cup .
>
> **Adopted scope:** item ingested
>
> **Extracted A:** no ingestion established
>
> **Extracted B:** beverage implied by sippy cup, contents unspecified
>
> **Recorded reason, verbatim:** The first play scene supplies neither an ingestible item nor ingestion activity.

**Audit explanation:** A identifies playground activity. An ingested item remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 384. evaluation_2655: `experience level`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A trials biker doing a stunt on a graffiti-filled wall .
>
> **Caption B:** Man on a bike doing a trick at a bike park wearing jeans and black t-shirt .
>
> **Adopted scope:** rider experience level
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Performing a trick does not establish training or experience level.

**Audit explanation:** Both stunt and clothing descriptions leave rider experience level unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `4.0`.

### 385. evaluation_2665: `color of balls`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The pitbull returns the chewed up soccer ball in the snow .
>
> **Caption B:** Two tan dogs run in the snow carrying red balls in their mouths .
>
> **Adopted scope:** ball color
>
> **Extracted A:** unstated soccer-ball color
>
> **Extracted B:** red
>
> **Recorded reason, verbatim:** Soccer-ball identity does not uniquely determine the first ball's color.

**Audit explanation:** A identifies a soccer ball. Its color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 386. evaluation_2676: `type of board`

**Current status:** `excluded_scope`. **Semantic rating:** `excluded/null`. **Policy:** `S7`.

> **Caption A:** A young man is catching some air while ride a wave board .
>
> **Caption B:** A surfer on a blue surfboard is falling off of it as he hits a wave .
>
> **Adopted scope:** board type under wave-board term
>
> **Extracted A:** wave board, potentially water board or casterboard
>
> **Extracted B:** surfboard
>
> **Recorded reason, verbatim:** The term wave board can denote different equipment, and the first gives no surface to resolve it.

**Audit explanation:** Wave board admits land-casterboard and water-board readings. A's unspecified surface leaves equipment type unresolved.

**Recorded scope readings:**

> - **wave board is a land casterboard:** rating 2.
> - **wave board is a water wave-riding board:** rating 3.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 387. evaluation_2677: `type of water sport`

**Current status:** `excluded_scope`. **Semantic rating:** `excluded/null`. **Policy:** `S7`.

> **Caption A:** A young man is catching some air while ride a wave board .
>
> **Caption B:** A surfer on a blue surfboard is falling off of it as he hits a wave .
>
> **Adopted scope:** sport implied by wave-board term
>
> **Extracted A:** possibly wave boarding, but water use unestablished
>
> **Extracted B:** surfing
>
> **Recorded reason, verbatim:** A water-board reading gives a related sport, while the land casterboard reading supplies no water sport.

**Audit explanation:** Wave board admits land skating and water boarding. A leaves the occurrence of a water sport unresolved.

**Recorded scope readings:**

> - **wave board is a land casterboard:** invalid.
> - **wave board is a water wave-riding board:** rating 3.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `5.0`.

### 388. evaluation_2679: `skating trick`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man does a skating trick off of graffiti-filled stairs .
>
> **Caption B:** A man skateboarding outside balancing his skateboard on a beam .
>
> **Adopted scope:** specific skating maneuver
>
> **Extracted A:** unnamed trick off stairs
>
> **Extracted B:** balancing skateboard on beam
>
> **Recorded reason, verbatim:** The first stairs describe an obstacle without identifying the actual trick.

**Audit explanation:** A identifies stairs and a skating trick. The actual maneuver remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 389. evaluation_2689: `absence of cellphone`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman stands outside a store while other people pass by .
>
> **Caption B:** A woman is talking on a cellphone on the curb in front of a restaurant .
>
> **Adopted scope:** cellphone absence
>
> **Extracted A:** unestablished
>
> **Extracted B:** phone explicitly present
>
> **Recorded reason, verbatim:** The first woman's unspecified possessions do not establish cellphone absence.

**Audit explanation:** A describes a woman outside a store. Cellphone absence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 390. evaluation_2691: `color of field`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S6`.

> **Caption A:** A little boy in a bright green field has kicked a soccer ball very high in the air .
>
> **Caption B:** A boy in an orange shirt and baseball cap sits in a grassy field next to a black ball .
>
> **Adopted scope:** field color
>
> **Extracted A:** bright green
>
> **Extracted B:** grassy, hue unstated
>
> **Recorded reason, verbatim:** Grass identifies vegetation but does not reliably establish its current color.

**Audit explanation:** B identifies grass. Its actual hue remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `2.0`.

### 391. evaluation_2709: `age of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A boy is flying in midair while snowboarding in a hilly and wooded area .
>
> **Caption B:** A person wearing a black sweatshirt and red pants is riding on a snowboard on a green box .
>
> **Adopted scope:** person age
>
> **Extracted A:** boy
>
> **Extracted B:** unstated person
>
> **Recorded reason, verbatim:** The second snowboarder is a person of unstated age.

**Audit explanation:** B identifies a person. Age category remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 392. evaluation_2742: `type of ball`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a little toddler is playing with a small ball on the grass .
>
> **Caption B:** A blond boy wearing a blue shirt and yellow shorts king a soccer ball .
>
> **Adopted scope:** ball type
>
> **Extracted A:** small ball, type unspecified
>
> **Extracted B:** soccer ball
>
> **Recorded reason, verbatim:** Small size does not identify a ball subtype to compare with soccer ball.

**Audit explanation:** A identifies a small ball. Ball type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 393. evaluation_2751: `size of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A gray water fowl with black and white markings is flying near water .
>
> **Caption B:** A tall bird is standing on the sand beside the ocean .
>
> **Adopted scope:** animal size
>
> **Extracted A:** unstated
>
> **Extracted B:** tall
>
> **Recorded reason, verbatim:** Waterfowl type alone does not establish the first bird's body size.

**Audit explanation:** A gives waterfowl colors. Bird size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 394. evaluation_2757: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** a swimmer wearing a black hat and goggles is doing the butterfly stroke .
>
> **Caption B:** A child with goggles and a swim cap swimming in a pool .
>
> **Adopted scope:** principal swim gear color
>
> **Extracted A:** black cap
>
> **Extracted B:** cap/goggle colors unstated
>
> **Recorded reason, verbatim:** The second cap and goggles have no colors stated.

**Audit explanation:** B identifies a swim cap and goggles. Their colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 395. evaluation_2764: `method of performance`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman in a blue leotard performing on the balancing beam for gymnastics .
>
> **Caption B:** A young lady at a gymnastic event waiting to begin her performance .
>
> **Adopted scope:** performance method
>
> **Extracted A:** balance-beam gymnastics
>
> **Extracted B:** gymnastics, apparatus unspecified
>
> **Recorded reason, verbatim:** Waiting at a gymnastics event does not identify the apparatus or method of the future performance.

**Audit explanation:** B establishes gymnastics. Apparatus and performance method remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 396. evaluation_2767: `location`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white and brown dog is leaping through the air .
>
> **Caption B:** A dog gets ready to catch something in the grass .
>
> **Adopted scope:** scene location
>
> **Extracted A:** unstated beyond airborne jump
>
> **Extracted B:** grassy setting
>
> **Recorded reason, verbatim:** An airborne leap gives no surrounding landscape or site for the first dog.

**Audit explanation:** A establishes airborne movement. The surrounding scene location remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 397. evaluation_2780: `color of pants`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Shirtless man with blank pants engaged in skateboarding upon a cityscape .
>
> **Caption B:** A male kid skateboarding down a sidewalk wearing a white striped shirt and black pants .
>
> **Adopted scope:** pants color
>
> **Extracted A:** unstated; blank does not fix a hue
>
> **Extracted B:** black
>
> **Recorded reason, verbatim:** Blank could be a typo or an unpatterned description; it does not literally establish black pants.

**Audit explanation:** A's word blank leaves trouser hue unspecified. A black reading requires a source-text correction.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 398. evaluation_2784: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** a black dog is running with a green toy between its paws .
>
> **Caption B:** A dog with a red collar and its tongue hanging out runs through tall grass .
>
> **Adopted scope:** principal dog's color
>
> **Extracted A:** black
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The red collar does not supply the second dog's coat color.

**Audit explanation:** B gives collar color. Principal dog coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 399. evaluation_2807: `position of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two men one in orange shirt , who is ahead , and one in green shirt running a race .
>
> **Caption B:** People are running a race while being filmed by a person on a bike .
>
> **Adopted scope:** runners relative positions
>
> **Extracted A:** one ahead of other
>
> **Extracted B:** relative ordering unstated
>
> **Recorded reason, verbatim:** The second runners' ordering and spacing are unstated despite the filming cyclist.

**Audit explanation:** B identifies runners. Their relative positions and ordering remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 400. evaluation_2813: `presence of man`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A lot of people at the market looking at various different things .
>
> **Caption B:** A man in a green shirt and black pants looks into a shop on a crowded market street .
>
> **Adopted scope:** man presence
>
> **Extracted A:** people with genders unstated
>
> **Extracted B:** man explicitly present
>
> **Recorded reason, verbatim:** A generic group of people does not establish a male member.

**Audit explanation:** A identifies people. Male presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `3.0`.

### 401. evaluation_2815: `existence of toy`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The dark brown dog is playing with the light brown dog .
>
> **Caption B:** On grass , two brown dogs tussle for orange toy .
>
> **Adopted scope:** toy presence
>
> **Extracted A:** unestablished during play
>
> **Extracted B:** orange toy present
>
> **Recorded reason, verbatim:** Dog play does not imply use of a toy or establish its absence.

**Audit explanation:** A identifies playing dogs. Toy presence remains unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 402. evaluation_2817: `color of shirt`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1,S3`.

> **Caption A:** A skateboarder does a jump on a skateboard over a red object as a man in a khaki top and black hat videotapes him in an area that appears to be a park .
>
> **Caption B:** A young man wearing black pants and a pink shirt , with arms spread wide , is leaping through the air with his skateboard over a concrete embankment .
>
> **Adopted scope:** principal skateboarder's shirt color
>
> **Extracted A:** unstated; videographer wears khaki
>
> **Extracted B:** pink
>
> **Recorded reason, verbatim:** Khaki describes the observer's shirt, leaving the first skateboarder's shirt color unknown.

**Audit explanation:** A gives videographer clothing color. Principal skateboarder shirt color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.

### 403. evaluation_2819: `speed of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Brown dog with objest in mouth moving toward camera .
>
> **Caption B:** a closeup photo of a small dog with a holey ball in his mouth .
>
> **Adopted scope:** animal speed
>
> **Extracted A:** moving, speed unspecified
>
> **Extracted B:** no motion established
>
> **Recorded reason, verbatim:** The second close-up establishes holding a ball but no movement or speed state.

**Audit explanation:** B provides a dog close-up. Motion and speed remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `-1.0`.

### 404. evaluation_2829: `motion of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young girl enjoying a beautiful day on the beach .
>
> **Caption B:** A surfer takes on a high wave beyond a rocky beach .
>
> **Adopted scope:** person motion
>
> **Extracted A:** unstated while enjoying beach
>
> **Extracted B:** surfing wave
>
> **Recorded reason, verbatim:** Enjoying a day at the beach does not identify the first girl's motion.

**Audit explanation:** A identifies beach enjoyment. The girl's movement remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_validation`.

**History:** supplied source rating `1.0`.
