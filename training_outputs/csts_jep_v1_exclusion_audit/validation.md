# Full audit of excluded validation comparisons

**Snapshot:** `jep-csts-v1`. All **254 exclusions** appear below. Authors and peers are separate assistant contexts. The [audit index](../../datasets/csts-jep-revision-v1/EXCLUSIONS.md) defines the policy codes.

## Cases flagged for review

| ID | Check | Review question |
|---|---|---|
| `train_2038` | Review exclusion policy | Does B’s computer workspace supply partial room-function information under the approved computer-context convention? |
| `train_8568` | Review exclusion policy | Should generic location include B’s explicit airborne position, or does the condition require surrounding venue or ground features? |
| `train_10241` | Review exclusion policy | Does ordinary ground-supported skateboarding provide a comparable position, as allowed in the training audit, or is explicit posture required? |
| `train_11335` | Review exclusion policy | Do riding and balancing supply partial stance information, or must seated versus standing be explicitly recoverable? |
| `train_11341` | Review exclusion policy | Can the man’s stated assistance supply a partial flotation means, or must the physical buoyancy mechanism be identified? |

## All 254 excluded comparisons

### 001. train_51: `color of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A number of locomotive train engines and cars on multiple set of train tracks.
>
> **Caption B:** A blue and yellow train passing under a large tree with factories in the background.
>
> **Adopted scope:** train colors
>
> **Extracted A:** unspecified
>
> **Extracted B:** blue and yellow
>
> **Recorded reason, verbatim:** First caption supplies no vehicle color information. / Only the second supplies the vehicles colors.

**Audit explanation:** A leaves train colors unspecified. B identifies blue and yellow.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 002. train_95: `color of sheets`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bed with white sheets and pillow, and a box of tissue on the headboard.
>
> **Caption B:** A bedroom with a bed and a nightstand that has a red phone and a lamp on it.
>
> **Adopted scope:** bed sheet color
>
> **Extracted A:** white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption supplies no sheet color information. / Second caption does not establish the bed sheet color.

**Audit explanation:** B leaves sheet color unspecified. Red describes a separate phone.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 003. train_102: `action of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A busy street with many business off to the side with a large clock.
>
> **Caption B:** A group of people walking on a walkway filled with clocks mounted on poles.
>
> **Adopted scope:** activity of described people
>
> **Extracted A:** no people described
>
> **Extracted B:** walking
>
> **Recorded reason, verbatim:** Busy street does not establish a specific human activity. / First caption gives no actor or human activity to compare.

**Audit explanation:** A's street description leaves a person performing an action unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 004. train_103: `people on street`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A busy street with many business off to the side with a large clock.
>
> **Caption B:** A group of people walking on a walkway filled with clocks mounted on poles.
>
> **Adopted scope:** type of people on street/walkway
>
> **Extracted A:** no people described
>
> **Extracted B:** group of people, subtype unspecified
>
> **Recorded reason, verbatim:** First caption supplies no explicitly described people entity. / A busy street alone does not explicitly establish people.

**Audit explanation:** A's busy street supplies buildings. The required people remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 005. train_150: `color of bus`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A large green and white double decker bus parked to another green and white double decker bus.
>
> **Caption B:** A bus is driving out of a parking lot and getting on the main road.
>
> **Adopted scope:** bus colors
>
> **Extracted A:** green and white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption supplies no bus color information. / Second caption does not establish the bus color.

**Audit explanation:** B's bus color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 006. train_180: `room decor style`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The bedroom is decorated in modern style with hardwood floor, and painted walls with one having a contrasting color.
>
> **Caption B:** A living room with brown leather furniture and a fire place and a book shelf.
>
> **Adopted scope:** room decoration style
>
> **Extracted A:** modern with hardwood and contrasting painted wall
>
> **Extracted B:** leather furniture, fireplace and bookshelves; style unspecified
>
> **Recorded reason, verbatim:** Leather furnishings do not establish a comparable overall decor style.

**Audit explanation:** B's furniture leaves the overall decor category unspecified under the user-confirmed style scope.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`. User-confirmed exclusion.

### 007. train_278: `type of food packaging`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A packed lunch consisting of two wraps, an orange with blueberries, raspberries, and carrots with broccoli 
>
> **Caption B:** A couple of yellow containers filled with rice and vegetables next to a clear container filled with even more vegetables.
>
> **Adopted scope:** packed-food packaging type
>
> **Extracted A:** packed lunch, packaging unspecified
>
> **Extracted B:** yellow and clear containers
>
> **Recorded reason, verbatim:** The first caption does not identify a packaging type. / Packed lunch does not specify a particular packaging type.

**Audit explanation:** A's packed lunch leaves its enclosing vessel or material unspecified. B identifies containers.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `4.0`. User-confirmed exclusion.

### 008. train_287: `next action of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The batter has just hit the baseball, and is ready to run to first base.
>
> **Caption B:** A man holding a baseball bat with two hands at a professional ball game.
>
> **Adopted scope:** principal person next action
>
> **Extracted A:** ready to run to first base
>
> **Extracted B:** next action unstated while holding bat
>
> **Recorded reason, verbatim:** Holding a bat at a game does not establish the next particular action.

**Audit explanation:** B's batter holds a bat. His next action remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 009. train_293: `presence of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A city with lots of tall buildings and a cat stopped at a traffic light.
>
> **Caption B:** A busy downtown intersection with street signs, pedestrian crossing signal, and large commercial buildings.
>
> **Adopted scope:** animal presence
>
> **Extracted A:** present: cat
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Final blind invalid consensus: Animal present in A; B never establishes animal presence or absence. / A cat is present; animal presence is unspecified downtown. / A explicitly includes a cat; B supplies no animal presence information.

**Audit explanation:** Animal presence remains unknown in B's intersection scene.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 010. train_326: `color of capped wave`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** a man lays down on a surf board as he paddles through the water
>
> **Caption B:** A man wearing a wet suit surfboarding on top of a white capped wave.
>
> **Adopted scope:** wave-cap color
>
> **Extracted A:** no capped wave described
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** The first caption does not establish any capped-wave color. / First caption mentions water but no colored wave cap.

**Audit explanation:** A describes water and a surfboard. A wave cap with comparable color remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 011. train_332: `color of blanketed sky`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A surfer surfs in the ocean as many kites fly in the cloudy sky.
>
> **Caption B:** A lone kite is flying above the water and under a blue blanketed sky.
>
> **Adopted scope:** sky color
>
> **Extracted A:** cloudy, color unspecified
>
> **Extracted B:** blue
>
> **Recorded reason, verbatim:** Cloud cover does not reliably establish sky color. / Cloud cover alone does not uniquely establish the skys color.

**Audit explanation:** A specifies cloud cover. Sky hue remains unspecified under the user-confirmed color rule.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`. User-confirmed exclusion.

### 012. train_588: `brightness`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A close up of a traffic light indicates a green light and a protected left turn.
>
> **Caption B:** There is a sign in a foreign language and a street light in this picture.
>
> **Adopted scope:** principal light illumination/brightness
>
> **Extracted A:** green signal illuminated; intensity unspecified
>
> **Extracted B:** street light, illumination unspecified
>
> **Recorded reason, verbatim:** Neither caption establishes a comparable level of brightness. / Light presence alone does not establish comparable brightness.

**Audit explanation:** A's green signal leaves intensity unspecified. B's street light leaves illumination level unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 014. train_625: `type of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** There are various food items including pickles, tomatoes, carrots, broccoli; as well as a sippy cup, spoon, fork, and whale napkin.
>
> **Caption B:** A glass of juice sits between two plates of food near pizza hut napkins on a dark yellow tablecloth.
>
> **Adopted scope:** food types
>
> **Extracted A:** pickles, tomatoes, carrots and broccoli
>
> **Extracted B:** food on two plates, types unspecified
>
> **Recorded reason, verbatim:** Second has unidentified food; branded napkins do not establish food types.

**Audit explanation:** B leaves food types unspecified. The napkins identify a restaurant brand.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`. User-confirmed exclusion.

### 015. train_630: `type of wine in glass`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Red wine pours in a glass; another glass is beside it and cheese straws in the back.
>
> **Caption B:** Three different types of wine in three wine glasses on a white piece of paper on a bar.
>
> **Adopted scope:** wine type
>
> **Extracted A:** red wine
>
> **Extracted B:** three distinct wine types, identities unspecified
>
> **Recorded reason, verbatim:** Second establishes three wines without identifying any wine type.

**Audit explanation:** B establishes three wines. Their types remain unnamed.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`. User-confirmed exclusion.

### 016. train_631: `types of wine`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Red wine pours in a glass; another glass is beside it and cheese straws in the back.
>
> **Caption B:** Three different types of wine in three wine glasses on a white piece of paper on a bar.
>
> **Adopted scope:** wine type collection
>
> **Extracted A:** red wine
>
> **Extracted B:** three distinct unnamed wine types
>
> **Recorded reason, verbatim:** Second establishes diversity without providing comparable wine-type identities.

**Audit explanation:** B supplies wine diversity and count. The required wine identities remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`. User-confirmed exclusion.

### 017. train_694: `layout of bedroom`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A bedroom with an open suitcase on the floor and a laptop on a chair
>
> **Caption B:** A carpeted bedroom has different wood toned furniture, a small lamp, and a yellow striped pillow.
>
> **Adopted scope:** bedroom layout
>
> **Extracted A:** suitcase on floor, laptop on chair
>
> **Extracted B:** furniture and accessories, positions unspecified
>
> **Recorded reason, verbatim:** Second identifies furnishings but supplies no comparable spatial layout.

**Audit explanation:** B lists bedroom furnishings. Their positions remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 018. train_731: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person is crossing a brick road in an area with residential buildings and lots of trees.
>
> **Caption B:** A traffic light sitting next to a tree on the side of a street.
>
> **Adopted scope:** number of people
>
> **Extracted A:** 1
>
> **Extracted B:** no people described
>
> **Recorded reason, verbatim:** Second caption supplies no people count or established absence. / Second caption establishes no people count or explicit absence.

**Audit explanation:** B's traffic-light scene leaves the number of people present unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 019. train_737: `age of player`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A baseball player wearing green and white standing next to a baseball player wearing red and gray on a baseball field.
>
> **Caption B:** A young baseball player gets ready to swing for the ball while two men watch.
>
> **Adopted scope:** principal players age category
>
> **Extracted A:** unspecified
>
> **Extracted B:** young player
>
> **Recorded reason, verbatim:** The first caption does not establish the players' age range. / First caption does not establish player ages.

**Audit explanation:** A's baseball players have unspecified ages.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 020. train_805: `sidewalk`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A rainy view of some people crossing a street with a red traffic light.
>
> **Caption B:** A brick laid sidewalk that is wet from rain, with a woman walking on the sidewalk and holding an umbrella.
>
> **Adopted scope:** sidewalk type
>
> **Extracted A:** no sidewalk described
>
> **Extracted B:** brick sidewalk
>
> **Recorded reason, verbatim:** Crossing a street does not establish a sidewalk to compare. / Crossing a street does not establish a sidewalk to compare.

**Audit explanation:** A describes street crossing. A comparable sidewalk remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 021. train_822: `activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Person in jeans and painted toe nails in a hotel room, sitting on the bed. 
>
> **Caption B:** A bed in a room with some lights on the side of the bed
>
> **Adopted scope:** person activity
>
> **Extracted A:** sitting on bed
>
> **Extracted B:** no person described
>
> **Recorded reason, verbatim:** Second caption describes furniture without a person's activity. / The second description lacks an actor with an activity.

**Audit explanation:** B describes a bed and lights. A person performing an activity remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 022. train_881: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A puppy all dressed up with a nice red tie with hearts on it.
>
> **Caption B:** A brown tabby cat wearing shirt collar and a neck tie wearing a cute expression.
>
> **Adopted scope:** animals clothing color
>
> **Extracted A:** red tie
>
> **Extracted B:** collar and tie, colors unspecified
>
> **Recorded reason, verbatim:** Second caption gives no color for the clothing. / Only the first supplies the color of clothing.

**Audit explanation:** B leaves the collar and tie colors unspecified. Brown describes the cat's coat.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 023. train_922: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bunch of train box cars on a track and people are walking on the sidewalk.
>
> **Caption B:** A truck and luggage sitting on a cart by the dining saloon car of a train.
>
> **Adopted scope:** number of people
>
> **Extracted A:** plural walking people, total unspecified
>
> **Extracted B:** no people described
>
> **Recorded reason, verbatim:** Second caption does not establish a people count. / Second description gives no person count or established absence.

**Audit explanation:** B's train-side luggage scene leaves the number of people present unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 024. train_979: `colors`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A plate with an iced and decorated cake next to a bowl of oranges.
>
> **Caption B:** Large multi-layered white frosted cake being cut with green plastic knife on striped table cloth.
>
> **Adopted scope:** principal cake color
>
> **Extracted A:** unspecified
>
> **Extracted B:** white frosting
>
> **Recorded reason, verbatim:** No first cake color is specified or reliably inferable.

**Audit explanation:** A leaves cake color unspecified. Oranges describe nearby fruit.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 025. train_1068: `sentiment of man`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man sits on a couch smiling next to a dog as a boy plays a video game.
>
> **Caption B:** A man in a gray tank top lays on a couch with a cute black and white dog.
>
> **Adopted scope:** man's sentiment
>
> **Extracted A:** happy/smiling
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Second man's posture does not establish sentiment. / The second mans emotional state cannot be extracted reliably.

**Audit explanation:** B's reclining man has an unspecified emotional state.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `4.0`.

### 026. train_1074: `type of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The bowl of food on the table is next to a couple of forks and glasses.
>
> **Caption B:** A close up shot of a plate with eggs and fruit on a table.
>
> **Adopted scope:** food type
>
> **Extracted A:** unspecified food
>
> **Extracted B:** eggs and fruit
>
> **Recorded reason, verbatim:** First caption names food without identifying its type.

**Audit explanation:** A leaves its bowl contents' food type unspecified. B identifies eggs and fruit.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`. User-confirmed exclusion.

### 028. train_1082: `name of activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a piece of cheese and carrot sitting on a tiny little saucer with a cup next to it
>
> **Caption B:** The core of an apple and peels with a knife on a cutting board
>
> **Adopted scope:** human food-related activity
>
> **Extracted A:** no activity described
>
> **Extracted B:** apple cut/peeled, actor not described
>
> **Recorded reason, verbatim:** First static food arrangement does not establish any named activity.

**Audit explanation:** A presents a static food arrangement. A named human activity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`. User-confirmed exclusion.

### 029. train_1089: `advertisement on vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A street with two cars and a bus in between the cars with a Coca Cola advertisement on the side of the bus.
>
> **Caption B:** A white metro bus with pink and purple trim drives down a city street in front of a glass building.
>
> **Adopted scope:** vehicle advertisement content
>
> **Extracted A:** Coca-Cola advertisement
>
> **Extracted B:** no advertisement described
>
> **Recorded reason, verbatim:** Colored bus trim does not establish advertising content. / Second caption supplies no advertising text or established absence.

**Audit explanation:** B's colored bus trim leaves advertising content unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 030. train_1130: `color of paper`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A room with a bed and a large sliding glass door to an outdoor deck.
>
> **Caption B:** A bed with white sheets and pillow, and a box of tissue on the headboard.
>
> **Adopted scope:** paper color
>
> **Extracted A:** no paper described
>
> **Extracted B:** tissues, color not explicit
>
> **Recorded reason, verbatim:** Neither caption establishes a comparable paper color. / Neither caption provides a comparable paper color value.

**Audit explanation:** A leaves paper unestablished. B's tissue box leaves a comparable paper color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 031. train_1132: `type of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Rough wood-frame furniture with striped cushions, in a bright room with a white tile floor.
>
> **Caption B:** A living room with a couch next to a chair in front of a TV.
>
> **Adopted scope:** room type
>
> **Extracted A:** furnished room, subtype unspecified
>
> **Extracted B:** living room
>
> **Recorded reason, verbatim:** Final blind invalid consensus: Cushioned wooden furniture does not establish A’s room type sufficiently. / Generic cushioned furniture does not establish the first room type. / Cushioned furniture and tile do not establish A's particular room type.

**Audit explanation:** A's furnishings leave room function unspecified under the user-confirmed room-type scope.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`. User-confirmed exclusion.

### 032. train_1133: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Rough wood-frame furniture with striped cushions, in a bright room with a white tile floor.
>
> **Caption B:** A living room with a couch next to a chair in front of a TV.
>
> **Adopted scope:** principal furniture color
>
> **Extracted A:** unspecified; striped cushions without hues
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption supplies no comparable object color. / Second caption gives no object colors to compare.

**Audit explanation:** Both captions leave principal furniture colors unspecified. Stripes describe pattern. White describes a separate floor.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 033. train_1183: `number of seats`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A room with a bed, matching curtains, and some chairs with clothes in them.
>
> **Caption B:** A bedroom with a bed and a nightstand that has a red phone and a lamp on it.
>
> **Adopted scope:** number of chair seats
>
> **Extracted A:** multiple chairs, exact count unspecified
>
> **Extracted B:** no seats described
>
> **Recorded reason, verbatim:** Second caption mentions no seats or established absence. / Second description does not establish any chair count or absence.

**Audit explanation:** B's bed and nightstand leave the chair-seat count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 034. train_1193: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A train track with a green caboose car and a silver and yellow train.
>
> **Caption B:** A train departs one one side of the tracks as people wait on the opposite side.
>
> **Adopted scope:** number of people
>
> **Extracted A:** no people described
>
> **Extracted B:** waiting people, plural count unspecified
>
> **Recorded reason, verbatim:** The first caption provides no extractable number of people. / First caption provides no people to count.

**Audit explanation:** A's train scene leaves the number of people present unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 035. train_1223: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman sitting in the snow with her snowboard on and a man standing next to a snowboard.
>
> **Caption B:** A snowboarder wearing a yellow coat and brown pants rides down a snow covered hill.
>
> **Adopted scope:** people's clothing colors
>
> **Extracted A:** unspecified
>
> **Extracted B:** yellow coat and brown pants
>
> **Recorded reason, verbatim:** The first caption supplies no clothing color information. / First caption provides no clothing colors to compare.

**Audit explanation:** A's snowboarders have unspecified clothing colors.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 036. train_1228: `color`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white dish with half eaten food above a plate with puffs and steak.
>
> **Caption B:** Glasses of wine sit in the middle of a table behind a plate of dessert.
>
> **Adopted scope:** principal dish/food color
>
> **Extracted A:** white dish; food colors unstated
>
> **Extracted B:** dish and food colors unstated
>
> **Recorded reason, verbatim:** Second caption provides no comparable object color. / Second caption supplies no comparable dish or food color.

**Audit explanation:** B leaves dish and food colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 037. train_1251: `color of ornamental clock`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An ornate clock beneath an arch flanked by statues and a locomotive bas relief.
>
> **Caption B:** A blue ornamental clock adorned with an eagle is hung on a white columned building.
>
> **Adopted scope:** clock color
>
> **Extracted A:** unspecified
>
> **Extracted B:** blue
>
> **Recorded reason, verbatim:** First caption provides no clock color information. / Only the second supplies the ornamental clocks color.

**Audit explanation:** A's ornamental clock color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 038. train_1256: `number of dish`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A table setting with a candle and a glass with limes on the side.
>
> **Caption B:** A tall case of flowers on an elaborate dining area sit alongside two wine glasses and a dish.
>
> **Adopted scope:** number of serving dishes, excluding drinking glasses
>
> **Extracted A:** no dish described
>
> **Extracted B:** 1 dish
>
> **Recorded reason, verbatim:** The first caption does not establish a dish count. / First caption names no dish whose count can be extracted.

**Audit explanation:** A's glass and candle leave serving-dish count unspecified under the scope excluding drinking glasses.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 039. train_1257: `presence of dish`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A table setting with a candle and a glass with limes on the side.
>
> **Caption B:** A tall case of flowers on an elaborate dining area sit alongside two wine glasses and a dish.
>
> **Adopted scope:** serving dish presence
>
> **Extracted A:** unspecified
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** Final blind invalid consensus: A mentions a glass but never establishes presence or absence of dishes. / A dish is explicit only in the second caption.

**Audit explanation:** A's drinking glass leaves serving-dish presence unknown under the adopted dish scope.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 040. train_1295: `color of cat`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cat and a bird are by a plate with chips and a sandwich on it.
>
> **Caption B:** A black cat sitting on a table next to a bowl of chicken soup.
>
> **Adopted scope:** cat coat color
>
> **Extracted A:** unspecified
>
> **Extracted B:** black
>
> **Recorded reason, verbatim:** The first caption supplies no cat color information. / First caption does not establish the cat color.

**Audit explanation:** A's cat coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 041. train_1339: `number of phones`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bedroom with a bed and a nightstand that has a red phone and a lamp on it.
>
> **Caption B:** A neatly-made bed with a gold and white bedspread flanked by lamps and a large wood headboard.
>
> **Adopted scope:** number of phones
>
> **Extracted A:** 1
>
> **Extracted B:** no phone described
>
> **Recorded reason, verbatim:** The second caption does not establish any phone count. / Second caption provides no phones whose count is extractable.

**Audit explanation:** B's bedroom fixtures leave phone count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 042. train_1355: `presence of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bedroom contains a dresser and mirror, a side table and lamp and a twin bed with matching bed covers and pillows.
>
> **Caption B:** A bed sitting on top of white drawers and topped with a stuffed animal next to a cat.
>
> **Adopted scope:** animal presence
>
> **Extracted A:** unspecified
>
> **Extracted B:** present: cat
>
> **Recorded reason, verbatim:** Final blind invalid consensus: A never establishes animal presence or absence; B explicitly includes a cat. / Cat presence is explicit; the bedroom description leaves animals unspecified. / B explicitly includes a cat; A leaves animal presence unreported.

**Audit explanation:** A's bedroom description leaves animal presence unknown. B explicitly includes a cat.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 043. train_1392: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person wearing a shirt of pink, blue and white, wearing a brown tie with a picture ladybug on it.
>
> **Caption B:** Up close shot of a mans shirt, necktie, and two pens in his pocket
>
> **Adopted scope:** shirt and tie colors
>
> **Extracted A:** pink, blue and white shirt; brown tie
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption supplies no clothing color information. / Second caption supplies no comparable clothing colors.

**Audit explanation:** B's shirt and necktie colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 044. train_1393: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person wearing a shirt of pink, blue and white, wearing a brown tie with a picture ladybug on it.
>
> **Caption B:** Up close shot of a mans shirt, necktie, and two pens in his pocket
>
> **Adopted scope:** shirt and tie colors
>
> **Extracted A:** pink, blue and white shirt; brown tie
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption supplies no clothing color information. / Second caption supplies no comparable clothing colors.

**Audit explanation:** B's shirt and necktie colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 045. train_1405: `number of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The overhead view of a tiled bathroom  with a tub, shower, toilet, bidet, and sink.
>
> **Caption B:** This is a well designed bathroom that is plain and elegant at the same time.
>
> **Adopted scope:** number of bathroom objects
>
> **Extracted A:** 5 named fixtures
>
> **Extracted B:** no objects identified
>
> **Recorded reason, verbatim:** Five fixtures are listed first; the second provides no object count. / Second caption provides no countable bathroom objects.

**Audit explanation:** B describes bathroom elegance. Its fixture count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 046. train_1421: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A sketched drawing of a boy in a blue shirt on his skateboard at a city park.
>
> **Caption B:** a person riding a skate board in front of a wall covered in grafitti
>
> **Adopted scope:** principal skateboard color
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption supplies no comparable object color. / Second caption gives no comparable object color.

**Audit explanation:** Both skateboard colors remain unspecified. Blue describes the drawn boy's shirt.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 047. train_1428: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** View from doorway and of door to small room with tiled floor and a toilet.
>
> **Caption B:** This appears to be a small bathroom, with a blue rug and toilet cover.
>
> **Adopted scope:** principal bathroom fixture colors
>
> **Extracted A:** unspecified
>
> **Extracted B:** toilet-cover and rug blue; toilet color unspecified
>
> **Recorded reason, verbatim:** First caption supplies no comparable object color. / First caption supplies no object color for comparison.

**Audit explanation:** A leaves bathroom-fixture colors unspecified. B identifies blue accessories.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 048. train_1447: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The elephant with a sit on his back ready for  people to ride on it.
>
> **Caption B:** A man leading an elephant across a dirt yard with another elephant in the background.
>
> **Adopted scope:** number of people actually described in scene
>
> **Extracted A:** prospective riders only; no present people established
>
> **Extracted B:** 1 man
>
> **Recorded reason, verbatim:** Readiness for people does not establish present people or their count. / Readiness for riders does not establish an actual people count.

**Audit explanation:** A describes prospective elephant riders. The number of people currently present remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 049. train_1469: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A narrow street in a city with automobiles parked on the side and a blue "Police" sign in the middle.
>
> **Caption B:** The city is busy with traffic today as people wait to board the bus.
>
> **Adopted scope:** number of people
>
> **Extracted A:** no people described
>
> **Extracted B:** waiting people, plural total unspecified
>
> **Recorded reason, verbatim:** First caption provides no people count or established absence. / First caption establishes no people count or explicit absence.

**Audit explanation:** A's parked-vehicle scene leaves the number of people present unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 050. train_1476: `name of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bedroom with an open suitcase on the floor and a laptop on a chair
>
> **Caption B:** A room is very messy as it may be inhabited by a college student
>
> **Adopted scope:** place/room type
>
> **Extracted A:** bedroom
>
> **Extracted B:** messy room, residential subtype uncertain
>
> **Recorded reason, verbatim:** College inhabitant speculation does not establish bedroom function. / Second caption does not establish a specific room function.

**Audit explanation:** B's messy room and possible college inhabitant leave bedroom function unspecified under the user-confirmed scope.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`. User-confirmed exclusion.

### 051. train_1477: `name of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bedroom with an open suitcase on the floor and a laptop on a chair
>
> **Caption B:** A room is very messy as it may be inhabited by a college student
>
> **Adopted scope:** named object types
>
> **Extracted A:** suitcase, laptop and chair
>
> **Extracted B:** messy room, no object types named
>
> **Recorded reason, verbatim:** Second caption identifies no comparable individual object types. / Second caption gives no objects whose types can be compared.

**Audit explanation:** B's messy-room description leaves individual object types unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 052. train_1493: `animal near person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A person standing in the ocean holding a surfboard while a dog stands on it.
>
> **Caption B:** A man with a surf board is standing on the beach with other people.
>
> **Adopted scope:** animal near person type
>
> **Extracted A:** dog
>
> **Extracted B:** no animal described
>
> **Recorded reason, verbatim:** The second caption establishes no animal near the person. / Second caption supplies no nearby animal to compare.

**Audit explanation:** B's people and surfboard leave a nearby animal unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 053. train_1504: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A train pumps out steam while going down a track on a cloudy day.
>
> **Caption B:** The train is on the railroad and the passengers are waiting for it to stop.
>
> **Adopted scope:** number of people
>
> **Extracted A:** no people described
>
> **Extracted B:** passengers, plural number unspecified
>
> **Recorded reason, verbatim:** First caption supplies no people count or established absence. / First caption establishes no people count or explicit absence.

**Audit explanation:** A's moving train leaves the number of people present unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 054. train_1550: `beverage temperature`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a plate covered with bananas with a coffee cup filled with some type of beverage
>
> **Caption B:** A plate with a couple of scones and a kettle that may be tea.
>
> **Adopted scope:** beverage temperature
>
> **Extracted A:** unspecified drink in coffee cup; temperature unknown
>
> **Extracted B:** possible tea in kettle; temperature unknown
>
> **Recorded reason, verbatim:** Containers and possible tea do not establish beverage temperature. / Neither vessel establishes the beverage's actual temperature.

**Audit explanation:** Both beverage temperatures remain unspecified. Vessel names identify containers.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 055. train_1599: `presence of grass`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a train is on it's tracks next to a dirt road and grassy patch
>
> **Caption B:** a train making it's way down a track with smoke coming out of the stack
>
> **Adopted scope:** grass presence
>
> **Extracted A:** present: grassy patch
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Final blind invalid consensus: Grass is explicit in A and neither confirmed nor denied in B. / Grass is explicit beside the first train, unspecified beside second. / A explicitly includes grass; B supplies no grass presence information.

**Audit explanation:** B's train scene leaves grass presence unknown.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 056. train_1680: `color of bowl`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A white bowl sitting on top of a table next to carrots and cabbage.
>
> **Caption B:** A plate of food with lemon wedges on the plate and on the table.
>
> **Adopted scope:** bowl color
>
> **Extracted A:** white
>
> **Extracted B:** no bowl described; plate instead
>
> **Recorded reason, verbatim:** Second caption describes plate, not required bowl entity. / Second caption lacks the required bowl and its color.

**Audit explanation:** B identifies a plate. The required bowl and its color remain unavailable.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 057. train_1681: `name of vegetables`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white bowl sitting on top of a table next to carrots and cabbage.
>
> **Caption B:** A plate of food with lemon wedges on the plate and on the table.
>
> **Adopted scope:** vegetable names
>
> **Extracted A:** carrots and cabbage
>
> **Extracted B:** no vegetables identified; lemon wedges are fruit
>
> **Recorded reason, verbatim:** Second caption supplies no named vegetable type. / Second caption names fruit but supplies no vegetable type.

**Audit explanation:** B identifies lemon wedges and generic food. A vegetable type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 058. train_1693: `person's age`

**Current status:** `excluded_ambiguous`. **Semantic rating:** `excluded/null`. **Policy:** `S7`.

> **Caption A:** Dogs and child on the floor in front of an adult seated on a couch.
>
> **Caption B:** A man in a gray tank top lays on a couch with a cute black and white dog.
>
> **Adopted scope:** age of first caption person: foreground child or couch adult
>
> **Extracted A:** child and adult
>
> **Extracted B:** adult man
>
> **Recorded reason, verbatim:** The first scene has both a foreground child and a couch adult; either can be compared with the second man, yielding different age ratings.

**Audit explanation:** A includes a foreground child and a couch adult. Comparing either with B's adult man changes the age judgment.

**Recorded scope readings:**

> - **foreground child:** different age categories. A: child. B: adult man.
> - **couch adult:** same age category. A: adult. B: adult man.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`. User-confirmed exclusion.

### 060. train_1870: `activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two motorcycles are near a curve in the road in front of a two story house.
>
> **Caption B:** a rider on a motorcycle gives a thumbs up as he drives on a street
>
> **Adopted scope:** principal motorcycle activity
>
> **Extracted A:** near road curve; motion unspecified
>
> **Extracted B:** riding and giving thumbs up
>
> **Recorded reason, verbatim:** Motorcycles being near a road curve does not establish an activity.

**Audit explanation:** A places motorcycles near a curve. Their activity and motion remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 061. train_1875: `perspective of batter in sport`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A crowd is watching a batter getting ready to take aim at a pitch.
>
> **Caption B:** A shot from behind of a batter poised, waiting for the ball to be thrown.
>
> **Adopted scope:** camera perspective on batter
>
> **Extracted A:** unspecified
>
> **Extracted B:** from behind
>
> **Recorded reason, verbatim:** Audience presence does not establish camera position. / Only the second establishes the visual perspective on the batter.

**Audit explanation:** A's spectators leave camera position relative to the batter unspecified. B supplies a rear view.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `4.0`.

### 062. train_1906: `absence of hand towel`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A kitchen with two sinks with a dish rack in one and dirty dishes in another.
>
> **Caption B:** The stove is shiny and has a hand-towel with an A hanging off its handle.
>
> **Adopted scope:** whether hand towel is absent
>
> **Extracted A:** unknown
>
> **Extracted B:** not absent: towel present
>
> **Recorded reason, verbatim:** Final blind invalid consensus: A gives no towel information; B explicitly contradicts towel absence. / Second towel defeats absence; first caption never establishes towel absence. / A does not establish towel absence; B explicitly includes a towel.

**Audit explanation:** A's sinks and dishes leave towel presence unknown. B explicitly includes a hand towel.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 063. train_2021: `type of signals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A view of a city street with oncoming traffic taken through metal posts of a sign.
>
> **Caption B:** This stop light is advanced in that it has red turn signals and green as well
>
> **Adopted scope:** traffic signal type
>
> **Extracted A:** unspecified sign seen through its posts
>
> **Extracted B:** illuminated red and green turn signals
>
> **Recorded reason, verbatim:** An unspecified sign does not establish a traffic-signal type in the first caption.

**Audit explanation:** A's unspecified road sign leaves illuminated traffic-signal type unavailable under the user-confirmed scope.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`. User-confirmed exclusion.

### 065. train_2023: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A photo of a computer screen with furniture in the background and sunlight beaming through the window.
>
> **Caption B:** A room with a plant, television, a stack of books and someone with their feet up in it. 
>
> **Adopted scope:** number of people
>
> **Extracted A:** no person described
>
> **Extracted B:** one person
>
> **Recorded reason, verbatim:** First caption provides no people count or explicit absence. / First caption gives no person count or explicit absence.

**Audit explanation:** A's computer and furnishings leave the number of people present unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 066. train_2038: `type of area involved`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** White vertical blinds hang in the windows of a white room with wood flooring, with a bed, a lamp, and a bookshelf with a small television on top of it.
>
> **Caption B:** A room with two pictures on the wall and a table with a computer monitor on it.  A wooden floor and a table with a yellow bowl and a grey and white rug.
>
> **Adopted scope:** room type
>
> **Extracted A:** bedroom
>
> **Extracted B:** room with tables and computer, function unspecified
>
> **Recorded reason, verbatim:** First implies bedroom; second furnishings do not establish a room function.

**Audit explanation:** B's computer workspace supplies partial room-function information under the approved computer-context rule. The current exclusion therefore needs policy review.

**Policy check:** Review exclusion policy. **Peer:** `writer_test`.

**Review question:** Does B’s computer workspace supply partial room-function information under the approved computer-context convention?

**History:** supplied source rating `4.0`.

### 067. train_2146: `style of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A vintage-styled attic bathroom is painted a great shade of green, and has a claw-foot tub.
>
> **Caption B:** A bathroom with two sinks, a rug, shower curtain and a tub in it. 
>
> **Adopted scope:** bathroom style
>
> **Extracted A:** vintage attic bathroom, green, claw-foot tub
>
> **Extracted B:** style unspecified; standard bathroom fixtures
>
> **Recorded reason, verbatim:** Fixtures alone do not establish second room's style. / Only the first establishes a room decor style.

**Audit explanation:** B lists bathroom fixtures. Its decor style remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 068. train_2149: `number of slices`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A glass table with a spinach pizza, a bottle of wine, and two filled glasses.
>
> **Caption B:** Two slices of pizza on a plate next to a box of bread sticks.
>
> **Adopted scope:** pizza slice count
>
> **Extracted A:** unspecified for pizza
>
> **Extracted B:** two slices
>
> **Recorded reason, verbatim:** Whole pizza description does not establish any slice count. / First caption identifies pizza without establishing a slice count.

**Audit explanation:** A's pizza description leaves slicing status and slice count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 069. train_2183: `type of fruit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A woman sits near a table with a cake and a bowl of oranges.
>
> **Caption B:** A little girl wears a pink and white striped shirt sits in front of a large cake with chocolate icing.
>
> **Adopted scope:** fruit type
>
> **Extracted A:** oranges
>
> **Extracted B:** no fruit described
>
> **Recorded reason, verbatim:** The second caption supplies no fruit entity or type. / Second caption provides no fruit to compare.

**Audit explanation:** B's cake scene leaves the required fruit entity unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 070. train_2203: `presence of liquid`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Plate of food ready to be served, each has a fried egg on top.
>
> **Caption B:** A table set for breakfast with tea an two plates with eggs and sausages.
>
> **Adopted scope:** presence of liquid
>
> **Extracted A:** unspecified
>
> **Extracted B:** present: tea
>
> **Recorded reason, verbatim:** Final blind invalid consensus: A gives no liquid information; B explicitly supplies tea. / Tea establishes liquid; an egg dish establishes no liquid presence. / Tea establishes liquid in B; A leaves liquid presence unspecified.

**Audit explanation:** A's egg dishes leave liquid presence unknown. B explicitly includes tea.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 071. train_2228: `number of ring binder`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Knitting yarn, a spool of thread, a book, a remote control, a clip board, and three ring binder are on a couch. 
>
> **Caption B:** A wooden desk with a lot of clutter on it and a desktop computer and monitor on the desk.
>
> **Adopted scope:** ring-binder count
>
> **Extracted A:** one three-ring binder
>
> **Extracted B:** no binder described among unspecified clutter
>
> **Recorded reason, verbatim:** The second caption provides no ring-binder count. / Three-ring describes binder design; second gives no binder count.

**Audit explanation:** B's desk clutter leaves ring-binder count unspecified. A's three-ring wording identifies binder design.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 072. train_2237: `number of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** two photos of an old street with horses and a new street with a truck
>
> **Caption B:** A series of two photographs one showing a city in the past and the other in the future.
>
> **Adopted scope:** animal count in photographs
>
> **Extracted A:** plural horses, exact number unspecified
>
> **Extracted B:** no animals described
>
> **Recorded reason, verbatim:** The second caption gives no animal count. / Second caption supplies no animals whose count is extractable.

**Audit explanation:** B's historical photographs leave animal identities and count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 073. train_2294: `type of flowers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two cats playing on a table with a vase and flowers in the middle.
>
> **Caption B:** A black and white cat napping in front of a mural of autumn flowers and leaves.
>
> **Adopted scope:** flower type
>
> **Extracted A:** unspecified flowers in vase
>
> **Extracted B:** autumn flowers depicted in mural, species unspecified
>
> **Recorded reason, verbatim:** Neither caption identifies a comparable botanical flower type. / First flower varieties are missing; second describes painted flowers.

**Audit explanation:** Both captions leave botanical flower varieties unspecified. B identifies depicted autumn flowers.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 074. train_2359: `number of cups`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bowl of food sitting on top of a table on a blue plate.
>
> **Caption B:** a plate covered with bananas with a coffee cup filled with some type of beverage
>
> **Adopted scope:** number of cups
>
> **Extracted A:** no cup described
>
> **Extracted B:** one coffee cup
>
> **Recorded reason, verbatim:** The first caption establishes a bowl, not a cup count. / First caption names bowl and plate but no cup.

**Audit explanation:** A's bowl and plate leave cup count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 075. train_2367: `player's action`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A tennis player and a ball on a court that is surrounded by a fence.
>
> **Caption B:** A man in blue shorts and a loose fitting shirt swinging a tennis racket.
>
> **Adopted scope:** principal player's action
>
> **Extracted A:** unspecified on court
>
> **Extracted B:** swinging racket
>
> **Recorded reason, verbatim:** The first caption provides no player action to compare. / First caption names a player but no current action.

**Audit explanation:** A identifies a tennis player on court. The player's current action remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 076. train_2379: `size of floral arrangement`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A large floral arrangement sitting on a table in the entryway of a house.
>
> **Caption B:** A bouquet of flowers is stuffed inside an arrangement of wine glasses on a table.
>
> **Adopted scope:** floral arrangement size
>
> **Extracted A:** large
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Second caption supplies no reliable floral arrangement size. / Only the first gives floral arrangement size; second omits it.

**Audit explanation:** B places a bouquet among glasses. Its size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 077. train_2385: `size of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman squatting down and reaching out to touch an elephants trunk that is pointed towards her.
>
> **Caption B:** A man leading an elephant across a dirt yard with another elephant in the background.
>
> **Adopted scope:** elephants' size
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption establishes the elephant's size. / Neither description gives the animals size with sufficient specificity.

**Audit explanation:** Both captions leave the elephants' actual sizes unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `5.0`.

### 078. train_2440: `color of sky`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A clock tower and several buildings against a background of a partly cloudy blue sky.
>
> **Caption B:** People satnding next to a a building with a clock at the top of it.
>
> **Adopted scope:** sky color
>
> **Extracted A:** partly cloudy blue
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Second caption provides no information about sky color. / Second caption provides no sky color for comparison.

**Audit explanation:** B's clock-building scene leaves sky color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 079. train_2494: `consciousness`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A person in a gray and black hooded jacket working with a laptop computer.
>
> **Caption B:** A close up of a desk looking at the keyboard and mouse and monitor.
>
> **Adopted scope:** person's consciousness
>
> **Extracted A:** awake, working on laptop
>
> **Extracted B:** no person described
>
> **Recorded reason, verbatim:** The second caption contains no person whose consciousness can be evaluated. / Second caption provides no person whose consciousness is assessable.

**Audit explanation:** B shows desk equipment. A person with an assessable consciousness remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 080. train_2671: `number of bottles`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Tea, a tea cup, a teddy bear, and a tea brewer sit on a countertop. 
>
> **Caption B:** A teddy bear sitting next to a cup on a saucer with a tea towel and two bottles in the background.
>
> **Adopted scope:** bottle count
>
> **Extracted A:** no bottles described
>
> **Extracted B:** two bottles
>
> **Recorded reason, verbatim:** First caption supplies no bottle count or established absence. / First caption establishes no bottle count or explicit absence.

**Audit explanation:** A's tea equipment and teddy bear leave bottle count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 081. train_2679: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Various tools are sitting on a table with a notepad and pen ready for note taking.
>
> **Caption B:** A hand, in a claw like position, hovers over a pair of scissors with black handles.
>
> **Adopted scope:** principal tool color
>
> **Extracted A:** unspecified
>
> **Extracted B:** black handles on scissors
>
> **Recorded reason, verbatim:** First caption does not establish a comparable object color. / Only the second supplies a relevant tool color.

**Audit explanation:** A's tool colors remain unspecified. B identifies black scissor handles.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 082. train_2763: `number of towels`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A pot and pan sitting on a stove top under a microwave next to a collection of knives.
>
> **Caption B:** The stove is shiny and has a hand-towel with an A hanging off its handle.
>
> **Adopted scope:** towel count
>
> **Extracted A:** no towel described
>
> **Extracted B:** one hand towel
>
> **Recorded reason, verbatim:** The first caption provides no information about towel count. / First caption provides no towels whose count is extractable.

**Audit explanation:** A's stove and cookware leave towel count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 083. train_2850: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A living room with a television, desk, chairs, and a person with a blue shirt leaning over the desk.
>
> **Caption B:** A man is seen in the mirror and there is a lot of clothes on top of a chair
>
> **Adopted scope:** person's clothing color
>
> **Extracted A:** blue shirt
>
> **Extracted B:** unspecified clothing colors
>
> **Recorded reason, verbatim:** Second caption supplies no clothing color information. / Only the first supplies a color of clothing.

**Audit explanation:** B's clothes and reflected man have unspecified clothing colors.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `4.0`.

### 084. train_2851: `type of chair`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A living room with a television, desk, chairs, and a person with a blue shirt leaning over the desk.
>
> **Caption B:** A man is seen in the mirror and there is a lot of clothes on top of a chair
>
> **Adopted scope:** chair type
>
> **Extracted A:** unspecified chairs
>
> **Extracted B:** unspecified chair
>
> **Recorded reason, verbatim:** Neither caption establishes a particular subtype of the mentioned chairs.

**Audit explanation:** Both captions leave chair subtypes unspecified under the adopted subtype scope.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 085. train_2863: `illumination near bed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The twin bed is neatly made with white sheets and a pair of pillows.
>
> **Caption B:** A bedroom with a bed and a nightstand that has a red phone and a lamp on it.
>
> **Adopted scope:** illumination near bed
>
> **Extracted A:** unspecified
>
> **Extracted B:** lamp on bedside nightstand
>
> **Recorded reason, verbatim:** The first caption supplies no information about illumination near the bed. / First caption provides no illumination source near the bed.

**Audit explanation:** A's bed linen leaves nearby illumination unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 086. train_2881: `speed of trains`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A train pumps out steam while going down a track on a cloudy day.
>
> **Caption B:** A group of people at a train station next to a red and black train.
>
> **Adopted scope:** train speed or motion rate
>
> **Extracted A:** moving, exact speed unspecified
>
> **Extracted B:** speed and motion unspecified at station
>
> **Recorded reason, verbatim:** Neither caption provides enough information to compare train speed. / Neither caption establishes the trains' comparative speed.

**Audit explanation:** B's station scene leaves train motion and speed unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 087. train_2989: `number of tables`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A laptop on a bed with a picture of a Reggae man behind it.
>
> **Caption B:** An empty blue bed sitting next to a small wooden table with an open laptop.
>
> **Adopted scope:** table count
>
> **Extracted A:** no table described
>
> **Extracted B:** one small table
>
> **Recorded reason, verbatim:** First caption provides no table count or established absence. / First caption establishes no table count or explicit absence.

**Audit explanation:** A's laptop on a bed leaves table count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 088. train_2994: `number of drinking glasses`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Three used clear drinking glasses sit next a plate on a counter with a lit tealight candle.
>
> **Caption B:** A sink is in the corner of a room lighted by lamps and candles.
>
> **Adopted scope:** drinking-glass count
>
> **Extracted A:** three
>
> **Extracted B:** no drinking glasses described
>
> **Recorded reason, verbatim:** The second caption does not establish any drinking-glass count. / Second caption gives no drinking glasses to count.

**Audit explanation:** B's sink and lighting leave drinking-glass count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 089. train_3038: `color of building`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A busy street with many business off to the side with a large clock.
>
> **Caption B:** A gold clock sticking out of the side of a tan building with sky in the background.
>
> **Adopted scope:** building color
>
> **Extracted A:** unspecified
>
> **Extracted B:** tan
>
> **Recorded reason, verbatim:** The first caption does not establish any building color. / First caption does not establish a building color.

**Audit explanation:** A's building colors remain unspecified. B explicitly identifies tan.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 090. train_3103: `size of device`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A building with a glass ceiling and a large clock mounted inside of it.
>
> **Caption B:** a clock hanging down off a brick wall in a row of circular hanging light shades
>
> **Adopted scope:** clock size
>
> **Extracted A:** large
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption does not establish the clock's size. / Second caption does not establish the clock's size.

**Audit explanation:** B's hanging clock size remains unspecified. A explicitly describes a large clock.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 091. train_3108: `type of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Food with a metal utensil under it with a cup on the side of the plate.
>
> **Caption B:** A closeup view of a pizza on a table with a beer behind it.
>
> **Adopted scope:** food type
>
> **Extracted A:** unspecified food
>
> **Extracted B:** pizza
>
> **Recorded reason, verbatim:** Generic food does not establish the first food type.

**Audit explanation:** A's food category remains unspecified. B identifies pizza.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 092. train_3109: `number of dishes`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Food with a metal utensil under it with a cup on the side of the plate.
>
> **Caption B:** A closeup view of a pizza on a table with a beer behind it.
>
> **Adopted scope:** dish count
>
> **Extracted A:** one plate and one cup: two
>
> **Extracted B:** no dish described
>
> **Recorded reason, verbatim:** The second caption does not establish a comparable dish count. / Second caption names pizza and beer but no serving dishes.

**Audit explanation:** B's pizza and beer leave serving-container count unspecified. A identifies a plate and cup.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `4.0`.

### 093. train_3153: `presence of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A guy on a skateboard doing tricks at a city skate park as others look on.
>
> **Caption B:** Four people and a dog watching a young man do stunts on a skateboard.
>
> **Adopted scope:** nonhuman animal presence
>
> **Extracted A:** unspecified
>
> **Extracted B:** present: dog
>
> **Recorded reason, verbatim:** Final blind invalid consensus: A never establishes animal presence or absence; B explicitly includes a dog. / Second caption establishes a dog; first leaves animal presence unspecified. / B explicitly includes a dog; A supplies no animal presence information.

**Audit explanation:** A's skatepark scene leaves animal presence unknown. B explicitly includes a dog.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 094. train_3165: `type of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Three people standing on a grass covered hill and controlling kite string that are connected to a large stork.
>
> **Caption B:** A quite big flock of large birds are flying over what appears to be a kite.
>
> **Adopted scope:** type of actual animal
>
> **Extracted A:** stork-shaped kite controlled by strings
>
> **Extracted B:** large birds, species unspecified
>
> **Recorded reason, verbatim:** The ordinary string-controlled stork reading is an artificial kite rather than an actual animal.

**Audit explanation:** The adopted string-controlled-stork reading identifies an artificial kite. An actual animal remains unavailable in A.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 095. train_3183: `countertop`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A free standing tub in a bathroom well lit from the light coming through the window.
>
> **Caption B:** A vanity and counter top with a sink and a commode in the corner.
>
> **Adopted scope:** countertop type
>
> **Extracted A:** no countertop described
>
> **Extracted B:** vanity countertop
>
> **Recorded reason, verbatim:** The first caption supplies no countertop entity for comparison. / First caption does not provide a countertop to compare.

**Audit explanation:** A's bathtub scene leaves a countertop entity unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 096. train_3207: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man riding atop an elephant while the elephant plays with a soccer ball.
>
> **Caption B:** An elephant with a red bench on its back and a red and yellow blanket over it's body.
>
> **Adopted scope:** people count
>
> **Extracted A:** one rider
>
> **Extracted B:** no person described
>
> **Recorded reason, verbatim:** Second caption supplies no people count or established absence. / Second caption establishes no rider count or explicit absence.

**Audit explanation:** B's elephant bench leaves the number of people present unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 097. train_3208: `color of wine`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Three goblets with white, red, and blush wines in them are lined up on the table.
>
> **Caption B:** A place setting with empty wine glasses has a piece of paper at the table.
>
> **Adopted scope:** wine color
>
> **Extracted A:** white, red and blush
>
> **Extracted B:** no wine in the empty glasses
>
> **Recorded reason, verbatim:** The second scene establishes empty glasses without wine color to compare. / Second explicitly contains no wine whose color can be compared.

**Audit explanation:** B's explicitly empty glasses leave the required wine entity unavailable.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 098. train_3209: `wine on table`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Three goblets with white, red, and blush wines in them are lined up on the table.
>
> **Caption B:** A place setting with empty wine glasses has a piece of paper at the table.
>
> **Adopted scope:** type of wine on table under entity-only default
>
> **Extracted A:** white, red and blush wine
>
> **Extracted B:** empty wine glasses, no wine
>
> **Recorded reason, verbatim:** Explicitly empty glasses supply no wine entity or wine type to compare.

**Audit explanation:** The entity-only wine condition concerns wine type. B's empty glasses leave wine unavailable.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 099. train_3217: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog lies on its side and digs in the sand at the beach.
>
> **Caption B:** A white, brown and black dog holding a green ball while standing in the ocean.
>
> **Adopted scope:** dog coat color
>
> **Extracted A:** unspecified
>
> **Extracted B:** white, brown and black
>
> **Recorded reason, verbatim:** The first caption supplies no dog color information. / First caption does not establish the dog's color.

**Audit explanation:** A's beach dog has an unspecified coat color.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 100. train_3228: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A tan stuffed teddy bear sits on a blue couch beside a red checkered pillow.
>
> **Caption B:** A black and brown dogs lays his head on a pillow on a bed.
>
> **Adopted scope:** actual animal color
>
> **Extracted A:** tan teddy-bear toy, no actual animal
>
> **Extracted B:** black and brown dog
>
> **Recorded reason, verbatim:** The first entity is a toy, not an actual animal. / First has a toy rather than an actual animal.

**Audit explanation:** A identifies a stuffed teddy-bear toy. An actual animal remains unavailable under the adopted color scope.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 101. train_3229: `animal species`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A tan stuffed teddy bear sits on a blue couch beside a red checkered pillow.
>
> **Caption B:** A black and brown dogs lays his head on a pillow on a bed.
>
> **Adopted scope:** actual animal species
>
> **Extracted A:** teddy-bear toy, no actual animal
>
> **Extracted B:** dog
>
> **Recorded reason, verbatim:** The first caption contains no actual animal species entity. / An actual animal species is absent from first caption.

**Audit explanation:** A identifies a teddy-bear toy. An actual animal species remains unavailable.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 102. train_3234: `type of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A rolling wooden bed bed and platform with a marker drawing chalk board attached to one side of the platform.
>
> **Caption B:** A bedroom with a bed and a nightstand that has a red phone and a lamp on it.
>
> **Adopted scope:** room type
>
> **Extracted A:** no room specified for rolling bed/platform
>
> **Extracted B:** bedroom
>
> **Recorded reason, verbatim:** The first unusual structure does not establish a room type. / First object description does not reliably establish a room type.

**Audit explanation:** A's rolling bed-and-platform structure leaves surrounding room function unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 103. train_3262: `size of bus`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bus is driving out of a parking lot and getting on the main road.
>
> **Caption B:** A blue and white double decker bus parked in front of a tall building.
>
> **Adopted scope:** bus size
>
> **Extracted A:** unspecified
>
> **Extracted B:** tall double-decker form
>
> **Recorded reason, verbatim:** The first bus's size or deck count is unavailable. / First bus size cannot be reliably determined.

**Audit explanation:** A's bus size and deck count remain unspecified. B identifies a double-decker form.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `4.0`.

### 104. train_3293: `color of cloth`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** This is a well designed bathroom that is plain and elegant at the same time.
>
> **Caption B:** A nice clean bathroom with a white towel on the corner of the sink.
>
> **Adopted scope:** cloth color
>
> **Extracted A:** no cloth described
>
> **Extracted B:** white towel
>
> **Recorded reason, verbatim:** The first caption supplies no cloth entity or color. / First caption supplies no cloth whose color can be compared.

**Audit explanation:** A's bathroom description leaves a cloth entity and its color unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 105. train_3363: `activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog laying on top of a cat, as the cat tries to push it away.
>
> **Caption B:** Close up back and back of head of a cat in dark with two rectangles of light on ground in front.
>
> **Adopted scope:** principal cat's activity
>
> **Extracted A:** pushing dog away
>
> **Extracted B:** activity unspecified in rear close-up
>
> **Recorded reason, verbatim:** Second specifies appearance and viewpoint without establishing an animal activity.

**Audit explanation:** B's rear close-up leaves the cat's activity unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 106. train_3478: `location of ball`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** The tennis player is crouched down, making an effort to hit a low ball.
>
> **Caption B:** A man in white shorts and a white shirt hitting a ball with a racket.
>
> **Adopted scope:** ball position
>
> **Extracted A:** low near ground
>
> **Extracted B:** unspecified relative height while struck
>
> **Recorded reason, verbatim:** Hitting with racket does not establish ball height. / Only the first establishes the balls height or location.

**Audit explanation:** B's racket strike leaves ball height unspecified under the adopted vertical-position scope.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 107. train_3518: `type of drink`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a plate with a sandwich on it on a wooden table next to a tall glass
>
> **Caption B:** A meal of a lunch meat sandwich and iced tea is on the table.
>
> **Adopted scope:** drink type
>
> **Extracted A:** no drink contents specified for tall glass
>
> **Extracted B:** iced tea
>
> **Recorded reason, verbatim:** A tall glass does not establish drink type. / Only the second identifies the type of beverage.

**Audit explanation:** A's tall glass leaves drink contents unspecified. B identifies iced tea.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 108. train_3534: `size of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A small living area contains the kitchen, dining room table, living room furniture and a view into the bathroom.
>
> **Caption B:** A metal cart stands in a modern kitchen with hardwood floors and wooden cabinets.
>
> **Adopted scope:** room size
>
> **Extracted A:** small living area
>
> **Extracted B:** kitchen size unspecified
>
> **Recorded reason, verbatim:** Second caption provides no room-size information. / Only the first supplies a room size description.

**Audit explanation:** B's kitchen size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 109. train_3567: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** There is a snow boarder doing stunts on a snow board and some people walking near him.
>
> **Caption B:** A snowboarder wearing a yellow coat and brown pants rides down a snow covered hill.
>
> **Adopted scope:** principal sporting object's color: snowboard
>
> **Extracted A:** unspecified snowboard color
>
> **Extracted B:** unspecified snowboard color
>
> **Recorded reason, verbatim:** The first caption supplies no comparable object color. / First caption supplies no comparable object colors.

**Audit explanation:** Both principal snowboard colors remain unspecified. B's stated colors identify clothing.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 110. train_3582: `address of street`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A street pole with a street sign on it that says B 86 Street, and a lamp post in the distance.
>
> **Caption B:** A row of parking meters on the side of a street next to a building.
>
> **Adopted scope:** street address/name
>
> **Extracted A:** B 86 Street
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Second caption provides no street address. / Only the first supplies a street name or address.

**Audit explanation:** B's street name or address remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 111. train_3618: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog with a ball running along the edge of the ocean at the beach.
>
> **Caption B:** A black and white dog stands beside a green and pink Frisbee on a sunny day.
>
> **Adopted scope:** principal dog color
>
> **Extracted A:** unspecified
>
> **Extracted B:** black and white
>
> **Recorded reason, verbatim:** The first caption supplies no dog color information. / First caption does not describe the dog's color.

**Audit explanation:** A's ocean-side dog has an unspecified coat color.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 112. train_3619: `color of dog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog with a ball running along the edge of the ocean at the beach.
>
> **Caption B:** A black and white dog stands beside a green and pink Frisbee on a sunny day.
>
> **Adopted scope:** dog coat color
>
> **Extracted A:** unspecified
>
> **Extracted B:** black and white
>
> **Recorded reason, verbatim:** The first caption supplies no dog color information. / First caption does not describe the dog's color.

**Audit explanation:** A's ocean-side dog has an unspecified coat color.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 113. train_3623: `view of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** The dog is getting a breathe of fresh air while riding in the car.
>
> **Caption B:** A view of a dog with his head sticking out of a car window through a mirror.
>
> **Adopted scope:** viewpoint on dog
>
> **Extracted A:** unspecified
>
> **Extracted B:** mirror reflection of head at window
>
> **Recorded reason, verbatim:** The first caption does not establish the observer's view of the dog. / First caption does not establish the viewing perspective.

**Audit explanation:** A leaves the observer’s viewpoint unspecified in the car-riding dog scene.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 114. train_3625: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A tennis court with a person in shorts and a hat jumping up and swinging the tennis racquet.
>
> **Caption B:** The girl is wearing a red and white tennis dress and has her racquet ready to hit.
>
> **Adopted scope:** tennis clothing color
>
> **Extracted A:** unspecified
>
> **Extracted B:** red and white
>
> **Recorded reason, verbatim:** First caption gives no color for comparable objects. / First caption supplies no relevant object color to compare.

**Audit explanation:** A's shorts and hat have unspecified colors under the adopted clothing scope.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 115. train_3627: `sentiment of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A girl has a spoon in her mouth in front of her lunch at school.
>
> **Caption B:** A young boy who is using a fork and knife to eat a pizza.
>
> **Adopted scope:** people emotional sentiment
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Eating descriptions establish neither person's emotional state. / Neither description establishes a reliable emotional state for comparison.

**Audit explanation:** Both eating descriptions leave the children's emotional states unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 116. train_3650: `number of bookshelves`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** From this vantage point it is easy to see the wall of windows and the patio outside.
>
> **Caption B:** a room with a couch chair bookshelf and a window view of the city
>
> **Adopted scope:** bookshelf count
>
> **Extracted A:** no bookshelf established
>
> **Extracted B:** 1 bookshelf
>
> **Recorded reason, verbatim:** First caption supplies no bookshelf count or established absence. / First caption establishes no bookshelf count or explicit absence.

**Audit explanation:** A's windows and patio view leave bookshelf count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 117. train_3708: `color of bathroom features`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A large bathroom with marble countertops and a standup shower with a glass door.
>
> **Caption B:** Three piece bathroom photo with granite countertop and multi colored beige tile around the tub.
>
> **Adopted scope:** bathroom fixture colors
>
> **Extracted A:** unspecified
>
> **Extracted B:** beige and multicolored tile
>
> **Recorded reason, verbatim:** Marble material does not reliably establish bathroom feature colors. / Material names do not establish first bathroom feature colors.

**Audit explanation:** A's marble and glass identify materials. Bathroom-feature hues remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 118. train_3784: `type of view`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A view of a living room and dining room from up on another floor
>
> **Caption B:** A room with a fire place, chair, couch, two lamps, tables, television and ottomans. 
>
> **Adopted scope:** viewpoint on room
>
> **Extracted A:** from an upper floor
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption does not establish a comparable viewing angle. / Second caption does not specify a viewing perspective.

**Audit explanation:** B's furniture list leaves observer position unspecified. A identifies an upper-floor view.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 119. train_3799: `number of pictures`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A room with two beds, two lamps, two pictures and a telephone in it. 
>
> **Caption B:** A motel large motel room with a flat screen television, chairs, table and a bed.
>
> **Adopted scope:** picture count
>
> **Extracted A:** 2
>
> **Extracted B:** no pictures established
>
> **Recorded reason, verbatim:** Second caption establishes no number of pictures. / Second caption establishes no picture count or explicit absence.

**Audit explanation:** B's motel furniture leaves picture count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 120. train_3811: `chopped vegetables`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** The core of an apple and peels with a knife on a cutting board
>
> **Caption B:** A bunch of chopped uncooked vegetables together including potatoes, carrots and other types of vegetables.
>
> **Adopted scope:** chopped vegetable type
>
> **Extracted A:** no vegetables: apple remains
>
> **Extracted B:** potatoes, carrots and other vegetables
>
> **Recorded reason, verbatim:** The first caption does not provide a chopped-vegetable entity. / First caption contains no chopped vegetables to compare.

**Audit explanation:** A identifies apple remains. The required chopped vegetables remain unavailable.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 121. train_3820: `color of river`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a train is on it's tracks next to a dirt road and grassy patch
>
> **Caption B:** A train on a rail line on the bridge on top of a river
>
> **Adopted scope:** river color
>
> **Extracted A:** no river established
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption establishes a comparable river color. / Neither caption supplies a comparable river color value.

**Audit explanation:** A leaves a river unestablished. B leaves river color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 122. train_3899: `type of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Two traffic lights are suspended above a road with parked cars, surrounded by buildings, with a person crossing it
>
> **Caption B:** A traffic light on a busy street with the word "TAXI" printed on it.
>
> **Adopted scope:** vehicle type
>
> **Extracted A:** cars
>
> **Extracted B:** no vehicle established; TAXI is printed text
>
> **Recorded reason, verbatim:** The word TAXI on a light does not establish a taxi vehicle. / TAXI lettering does not establish an actual vehicle's presence.

**Audit explanation:** B identifies TAXI lettering on a light. An actual vehicle remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 123. train_3951: `number of vehicles`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An old television set and a car is visible on the screen and a light is reflecting off of it.
>
> **Caption B:** A photo of a TV set net to a wood vanity and stool with a green wall behind both.
>
> **Adopted scope:** depicted vehicle count
>
> **Extracted A:** 1 car shown on TV
>
> **Extracted B:** no vehicle established
>
> **Recorded reason, verbatim:** Second caption provides no vehicle information or established absence. / Second scene does not establish vehicle presence or absence.

**Audit explanation:** B's television and furniture leave depicted vehicle count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 124. train_4076: `name of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A room with a leather chair and a clock on the wall behind the chair.
>
> **Caption B:** The view of a dining room an a living room, where a woman is sitting on the couch.
>
> **Adopted scope:** room function type
>
> **Extracted A:** room with chair and clock; function unavailable
>
> **Extracted B:** dining room and living room
>
> **Recorded reason, verbatim:** A chair and wall clock do not establish the room's function.

**Audit explanation:** A's chair and clock leave room function unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 125. train_4079: `number of legs of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A desk with a bunch of items that would be found in the purse on the desk.
>
> **Caption B:** The table has weapons and other items that can be used to make a weapon.
>
> **Adopted scope:** principal furniture leg count
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption establishes the furniture's number of legs. / Furniture names do not reliably establish an exact leg count.

**Audit explanation:** Both furniture leg counts remain unspecified. Desk and table names identify furniture categories.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 126. train_4097: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A refrigerator with the door open in one picture and closed in the other.
>
> **Caption B:** A refrigerator has magnets and papers and food on top of it in the corner of a yellow tiled kitchen
>
> **Adopted scope:** refrigerator color
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption supplies the refrigerator's color. / Neither caption establishes the refrigerator's color.

**Audit explanation:** Both refrigerator colors remain unspecified. Yellow describes B's kitchen tiles.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 127. train_4113: `color of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Several buses travelling in one direction and a cab travelling in the opposite direction.
>
> **Caption B:** A row of red and yellow buses with people standing around and a few merchandise stands and parked motorbikes.
>
> **Adopted scope:** principal bus colors
>
> **Extracted A:** unspecified
>
> **Extracted B:** red and yellow
>
> **Recorded reason, verbatim:** The first caption supplies no vehicle color information. / First caption does not establish vehicle colors.

**Audit explanation:** A's buses and cab have unspecified colors.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 128. train_4206: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A pizza sitting on top of a wooden cutting board next to a white plate.
>
> **Caption B:** A hot pizza on the table is loaded with pepperoni and cheese and sausage.
>
> **Adopted scope:** principal pizza color
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption does not establish a comparable object color. / Second caption does not establish a comparable object color.

**Audit explanation:** Both principal pizza colors remain unspecified. White describes A's separate plate.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 129. train_4234: `animal's age`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A kitten coming indoors through a cat door near a toy on a string
>
> **Caption B:** A grey cat looks up and meows, as the cat wears a purple leash.
>
> **Adopted scope:** cat age category
>
> **Extracted A:** kitten: juvenile
>
> **Extracted B:** cat; age unspecified
>
> **Recorded reason, verbatim:** Cat does not reliably establish adult age. / Only the first establishes a specific animal age category.

**Audit explanation:** B's cat age remains unspecified. A explicitly identifies a juvenile kitten.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 130. train_4279: `color of plate`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two white plates have hash browns and an egg dish on them as they sit on a brown table.
>
> **Caption B:** A man in a restaurant sitting in front of a plate of breakfast food.
>
> **Adopted scope:** plate color
>
> **Extracted A:** white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Second caption does not establish plate color. / Only the first supplies a color for the plates.

**Audit explanation:** B's breakfast plate color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 131. train_4307: `number of bottles`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two bottles of wine on a table with a half full glass of red wine.
>
> **Caption B:** Several wine glasses have just a little bit of wine in each of them.
>
> **Adopted scope:** wine bottle count
>
> **Extracted A:** 2 bottles
>
> **Extracted B:** no bottles established
>
> **Recorded reason, verbatim:** The second caption does not establish any bottle count. / Second caption describes glasses without establishing bottle count.

**Audit explanation:** B's wine glasses leave bottle count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 132. train_4421: `number of buckets`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bathroom with toilet, sink with cabinet and wall mirror, and three bucket containers on the floor.
>
> **Caption B:** A toilet and a bidet are in a beige tiled bathroom with a shower stall.
>
> **Adopted scope:** bucket count
>
> **Extracted A:** 3 buckets
>
> **Extracted B:** no buckets established
>
> **Recorded reason, verbatim:** The second caption does not establish any bucket count. / Second caption provides no buckets whose count is extractable.

**Audit explanation:** B's bathroom fixtures leave bucket count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 133. train_4488: `presence of instrument`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A guitar case, a backpack, and a suitcase all placed next to each other.
>
> **Caption B:** A pile of luggage waiting to be picked up and taken to their destination.
>
> **Adopted scope:** musical instrument presence
>
> **Extracted A:** guitar case only; instrument unconfirmed
>
> **Extracted B:** luggage only; instrument unconfirmed
>
> **Recorded reason, verbatim:** Final blind invalid consensus: A guitar case does not establish an instrument; B supplies no instrument information. / A guitar case establishes neither its contents nor an instrument. / A guitar case does not establish an instrument inside either luggage collection.

**Audit explanation:** A's guitar case leaves its contents unknown. B's luggage leaves instrument presence unknown.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 134. train_4489: `presence of suitcase`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A guitar case, a backpack, and a suitcase all placed next to each other.
>
> **Caption B:** A pile of luggage waiting to be picked up and taken to their destination.
>
> **Adopted scope:** suitcase presence
>
> **Extracted A:** explicitly present
>
> **Extracted B:** luggage present, suitcase presence unestablished
>
> **Recorded reason, verbatim:** Generic luggage does not establish that a suitcase is present.

**Audit explanation:** B's generic luggage leaves suitcase presence unknown.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 135. train_4538: `color of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bedroom with polar bear wallpaper and a nightstand that has many drawers and a Smurf figurine on top.
>
> **Caption B:** A bathroom with a white and checkered bathtub wall and white cabinets with miscellaneous items on it.
>
> **Adopted scope:** room colors
>
> **Extracted A:** unspecified; polar bear wallpaper gives no color
>
> **Extracted B:** white and checkered
>
> **Recorded reason, verbatim:** Wallpaper subject does not establish the first room's actual colors. / Wallpaper motif does not establish the room's actual colors.

**Audit explanation:** A's polar-bear wallpaper identifies a motif. Actual room colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 136. train_4586: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A slice of pizza on a white plate with a knife and fork laying on the plate.
>
> **Caption B:** Food with a metal utensil under it with a cup on the side of the plate.
>
> **Adopted scope:** food plate color
>
> **Extracted A:** white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption does not establish a comparable object color. / Second caption does not establish a comparable object color.

**Audit explanation:** B's plate color remains unspecified. A explicitly identifies white.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 137. train_4587: `food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A slice of pizza on a white plate with a knife and fork laying on the plate.
>
> **Caption B:** Food with a metal utensil under it with a cup on the side of the plate.
>
> **Adopted scope:** principal food type
>
> **Extracted A:** pizza
>
> **Extracted B:** food, identifiable dish category unavailable
>
> **Recorded reason, verbatim:** B provides no recoverable food category beyond the word food.

**Audit explanation:** B's food category remains unspecified beyond the word food. A identifies pizza.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 138. train_4659: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two kites in the air with swirly tails against a blue sky, over a green hill, and beach with people.
>
> **Caption B:** A man standing in a grass field and flying a multi-colored kite in the sky above him.
>
> **Adopted scope:** principal kite colors
>
> **Extracted A:** unspecified
>
> **Extracted B:** multicolored
>
> **Recorded reason, verbatim:** First caption specifies landscape colors but no kite color.

**Audit explanation:** A's kite colors remain unspecified. Its stated hues describe the landscape.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 139. train_4743: `presence of flag near desk`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A laptop, cell phone, and mouse sit on a cluttered desk near a California flag.
>
> **Caption B:** An office workspace with two screens, a laptop, an ergonomic keyboard and other electronics.
>
> **Adopted scope:** flag presence near desk
>
> **Extracted A:** California flag present
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Final blind invalid consensus: A flag is present in A; B never establishes flag presence or absence. / Flag is explicit near first desk, unspecified near second workspace. / A specifies a flag near the desk; B leaves flag presence unreported.

**Audit explanation:** B's workspace leaves flag presence near the desk unknown.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 140. train_4745: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bathroom features a door with a window, a towel rack, a stack of towls and cabinets.
>
> **Caption B:** Some white towels hanging under a white vanity next to a glass shower unit.
>
> **Adopted scope:** principal bathroom object colors
>
> **Extracted A:** unavailable
>
> **Extracted B:** white towels and vanity
>
> **Recorded reason, verbatim:** A supplies no comparable object colors.

**Audit explanation:** A's bathroom-object colors remain unspecified. B identifies white towels and vanity.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 141. train_4802: `time of day`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An asian child is eating noodles with a fork with help using his own hands in the kitchen.
>
> **Caption B:** A small child in a high chair with a large pile of food in front of them.
>
> **Adopted scope:** time of day
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption establishes any time of day. / Neither caption supplies a time of day or direct clue.

**Audit explanation:** Both food descriptions leave time of day unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 142. train_4811: `position of racket`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** The girl is wearing a red and white tennis dress and has her racquet ready to hit.
>
> **Caption B:** A tennis player has lowered her racket to return the ball with a scoop.
>
> **Adopted scope:** racket's spatial position
>
> **Extracted A:** ready to hit, physical position unavailable
>
> **Extracted B:** lowered for scoop return
>
> **Recorded reason, verbatim:** Readiness does not identify the first racket's spatial position.

**Audit explanation:** A's racket readiness leaves spatial height and orientation unspecified. B identifies a lowered racket.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 143. train_4823: `color of t-shirt`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A girl in a pink t-shirt and white tennis shoes holds out her racket.
>
> **Caption B:** A woman jumping up to a hit a tennis ball on a tennis court.
>
> **Adopted scope:** T-shirt color
>
> **Extracted A:** pink
>
> **Extracted B:** no T-shirt established
>
> **Recorded reason, verbatim:** Second caption supplies no shirt color. / Only the first supplies the color of a shirt.

**Audit explanation:** B's T-shirt entity and color remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 144. train_4913: `number of beverages`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Bottles of booze sit in the background behind a sandwich and a bit of beets.
>
> **Caption B:** a sandwhich cut into half with olives and  a pickel sitting on a plate
>
> **Adopted scope:** beverage count
>
> **Extracted A:** plural bottles of booze; exact count unknown
>
> **Extracted B:** no beverages established
>
> **Recorded reason, verbatim:** Second caption supplies no beverage count or explicit absence. / Second caption gives no beverage count or explicit absence.

**Audit explanation:** B's sandwich scene leaves beverage count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 145. train_4923: `object child is holding`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A young child looks at the camera as he holds a tennis racket on the court.
>
> **Caption B:** The boy have brought several tennis balls with him to to tennis court in order to practice  his serve.
>
> **Adopted scope:** object held by child
>
> **Extracted A:** tennis racket
>
> **Extracted B:** tennis balls brought; current held object unspecified
>
> **Recorded reason, verbatim:** Bringing tennis balls does not establish the object currently held.

**Audit explanation:** B describes bringing tennis balls. The boy's currently held object remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 146. train_4978: `color of scissors`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man holding a large pair of red scissors in front of a crowd.
>
> **Caption B:** A large group of business men about the cut the ribbon at a grand opening.
>
> **Adopted scope:** ceremonial scissors color
>
> **Extracted A:** red
>
> **Extracted B:** unspecified; scissors inferred from ribbon cutting
>
> **Recorded reason, verbatim:** Second caption does not establish any scissors color. / Red is given only first; second gives no scissor color.

**Audit explanation:** B's ribbon-cutting context implies scissors. Their color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 147. train_4988: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A street with a lot of traffic next to a sidewalk filled with people on a rainy day.
>
> **Caption B:** A red fire hydrant sits at the end of a row of cars parked on a street.
>
> **Adopted scope:** principal scene-object colors
>
> **Extracted A:** traffic vehicles; colors unspecified
>
> **Extracted B:** red fire hydrant
>
> **Recorded reason, verbatim:** The first caption supplies no object color information. / First caption provides no comparable object color.

**Audit explanation:** A's traffic scene leaves relevant object colors unspecified. B identifies a red hydrant.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 148. train_5027: `number of frames`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a white bathroom with a tub, a sink and wood framed picture under the sink mirror
>
> **Caption B:** A bathrobe with a curtain covered bathtub next to a sink and a toilet.
>
> **Adopted scope:** picture frame count
>
> **Extracted A:** 1 wood picture frame
>
> **Extracted B:** no frames established
>
> **Recorded reason, verbatim:** The second caption does not establish any picture-frame count. / Second caption supplies no frames whose count can be extracted.

**Audit explanation:** B's bathroom fixtures leave picture-frame count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 149. train_5054: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** White and brown goats in a pen looking at a white, brown and black dog.
>
> **Caption B:** Two adult horses stand on either side of a young colt in a field.
>
> **Adopted scope:** principal animal colors
>
> **Extracted A:** white and brown goats; dog also black
>
> **Extracted B:** horse colors unspecified
>
> **Recorded reason, verbatim:** Second caption establishes no animal color information. / Second caption gives no animal color for comparison.

**Audit explanation:** B's horses have unspecified coat colors.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 150. train_5171: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A toilet is built into a larger seat with two rolls of toilet paper on it.
>
> **Caption B:** A white toilet with a small sink behind it in a very small space.
>
> **Adopted scope:** principal toilet color
>
> **Extracted A:** unspecified
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** The first caption supplies no toilet color information. / First caption provides no comparable object color.

**Audit explanation:** A's toilet color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 151. train_5251: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A walkway between to building made to look like a train car on railroad tracks.
>
> **Caption B:** A bunch of train box cars on a track and people are walking on the sidewalk.
>
> **Adopted scope:** all people count
>
> **Extracted A:** no people established
>
> **Extracted B:** plural walking people
>
> **Recorded reason, verbatim:** First caption supplies no reliable people count. / First caption establishes no people count or explicit absence.

**Audit explanation:** A's walkway scene leaves the number of people present unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 152. train_5292: `height of man`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man performing a skate board trick in front of various people in wooden chairs and another man holding a skateboard.
>
> **Caption B:** A skate boarder in the air, mid jump, as his board is flipped upside down.
>
> **Adopted scope:** principal man physical height
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption establishes the man's physical height or comparable elevation. / Neither caption establishes the man's stature or exact elevation.

**Audit explanation:** Both men's physical statures remain unspecified. B's airborne elevation concerns a separate feature under the adopted body-height scope.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 153. train_5331: `number of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An open blue suitcase sits next to a wastebasket and a plastic bag filled with clothing.
>
> **Caption B:** One cat is sitting in a suitcase and the the other cat is on the bed.
>
> **Adopted scope:** all animal count
>
> **Extracted A:** no animals established
>
> **Extracted B:** 2 cats
>
> **Recorded reason, verbatim:** The first caption provides no established animal count. / First caption provides no animals whose count is extractable.

**Audit explanation:** A's suitcase scene leaves animal count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 154. train_5351: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A truck driving through and intersection waiting on a pedestrian to finish crossing the street.
>
> **Caption B:** A very busy city street with a multitude of streetlights and buildings in the background.
>
> **Adopted scope:** all people count
>
> **Extracted A:** 1 pedestrian
>
> **Extracted B:** no people established
>
> **Recorded reason, verbatim:** Busy street does not establish any pedestrian count. / Second caption supplies no people count or established absence.

**Audit explanation:** B's busy street leaves pedestrian count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 155. train_5388: `color of train`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A train on tracks with gravel, and trees, grass and telephone wires and two workers in background.
>
> **Caption B:** A white and yellow train and a red and yellow train hooked to each other on a track.
>
> **Adopted scope:** train colors
>
> **Extracted A:** unspecified
>
> **Extracted B:** white/yellow and red/yellow
>
> **Recorded reason, verbatim:** The first caption supplies no train color information. / First caption does not provide a train color.

**Audit explanation:** A's train colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 156. train_5464: `color of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Cars driving on the street and people walking on the sidewalk in a city.
>
> **Caption B:** On a gray and rainy day a black car drives down a city street.
>
> **Adopted scope:** cars' color
>
> **Extracted A:** unspecified
>
> **Extracted B:** black
>
> **Recorded reason, verbatim:** First caption supplies no vehicle color. / Only the second supplies any vehicle color information.

**Audit explanation:** A's vehicle colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 157. train_5581: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The snowboarder flew through the air while the sun sets on the horizon .
>
> **Caption B:** A snowboarder is sliding along , balanced on a yellow beam .
>
> **Adopted scope:** principal snowboard color
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** First caption establishes no relevant object color. / First caption supplies no object color for comparison.

**Audit explanation:** Both principal snowboard colors remain unspecified. Yellow describes B's beam.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 158. train_5735: `dog's level of training`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black and white dog running from under a yellow cover with a person behind them .
>
> **Caption B:** A small dog with a ball in its mouth running through a course .
>
> **Adopted scope:** dog training level
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Running under cover or through courses establishes no training level. / Neither description establishes a specific level of dog training.

**Audit explanation:** Both dogs' training levels remain unspecified despite their course-related actions.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 159. train_5771: `number of toys`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two large dogs are playing in a large grassy area .
>
> **Caption B:** a black and a white dog play with a rope toy in a backyard
>
> **Adopted scope:** number of toys
>
> **Extracted A:** no toy entity mentioned
>
> **Extracted B:** one rope toy
>
> **Recorded reason, verbatim:** The first caption does not establish a toy count. / First caption establishes playing but no toy count.

**Audit explanation:** A's playing dogs leave toy count unspecified. B identifies one rope toy.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 160. train_5787: `skill level of subject`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a surfer is riding the waves whilst another surfer sits on his board waiting .
>
> **Caption B:** A boy in red shorts rides a yellow bodyboard on a breaking wave .
>
> **Adopted scope:** subject's skill level
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption directly establishes the participants' level of skill. / Wave riding alone does not establish comparative skill levels.

**Audit explanation:** Both wave-riding participants have unspecified skill levels.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 161. train_5793: `positions players are playing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A batter swinging at a pitch with a catcher preparing to receive the pitch .
>
> **Caption B:** Two baseball players on a field , with four spectators , and a crowd .
>
> **Adopted scope:** players' positions
>
> **Extracted A:** batter and catcher
>
> **Extracted B:** two unspecified baseball positions
>
> **Recorded reason, verbatim:** Second caption establishes no baseball player positions. / Second caption identifies players without stating their fielding roles.

**Audit explanation:** B's baseball players have unspecified positions. A identifies a batter and catcher.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 162. train_5802: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A little boy is playing with his dog in the backyard as the snow melts .
>
> **Caption B:** A brown dog carrying a Frisbee runs through the snow .
>
> **Adopted scope:** dog coat color
>
> **Extracted A:** unspecified
>
> **Extracted B:** brown
>
> **Recorded reason, verbatim:** First caption supplies no animal color information. / Only the second supplies the dogs fur color.

**Audit explanation:** A's dog coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 163. train_5859: `color of dog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Long-haired dog moves quickly beneath two poles .
>
> **Caption B:** A brown dog with a blue bandanna is jumping over grass .
>
> **Adopted scope:** dog coat color
>
> **Extracted A:** unspecified
>
> **Extracted B:** brown
>
> **Recorded reason, verbatim:** Long hair provides no information about coat color. / Only the second supplies the dogs fur color.

**Audit explanation:** A's long-haired dog has an unspecified coat color.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 164. train_5863: `proximity to water`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A person on a bike rides through a dirt course near the water .
>
> **Caption B:** One biker wearing a black helmet riding on a dirt hill .
>
> **Adopted scope:** distance to water
>
> **Extracted A:** near water
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption supplies no information about nearby water. / Second caption provides no water proximity information.

**Audit explanation:** B's dirt-hill scene leaves water proximity unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 165. train_5911: `dog's mouth contents`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A male weimaraner with a clipped tail is walking through a river .
>
> **Caption B:** A white dog treads the water with sticks in its mouth .
>
> **Adopted scope:** dog's mouth contents
>
> **Extracted A:** unspecified
>
> **Extracted B:** sticks
>
> **Recorded reason, verbatim:** The first caption supplies no information about mouth contents. / First caption does not establish the dog's mouth contents.

**Audit explanation:** A's river-walking dog has unspecified mouth contents.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 166. train_5933: `type of surface`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in white playing tennis is still in midair after jumping to hit the ball .
>
> **Caption B:** A male tennis player prepares a left-handed forehand while playing on clay .
>
> **Adopted scope:** tennis playing surface
>
> **Extracted A:** unspecified
>
> **Extracted B:** clay
>
> **Recorded reason, verbatim:** The first caption does not identify the playing surface. / First caption does not identify the court surface.

**Audit explanation:** A's tennis action leaves court-surface type unspecified. B identifies clay.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 167. train_6025: `name of dog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A harnessed dog leaps over a log as another dog follows behind .
>
> **Caption B:** a dog jumps over another dog as both animals are trying to catch the same ball .
>
> **Adopted scope:** dog's proper name
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption provides a personal name for the dog. / Neither caption supplies an individual name or specific dog identity.

**Audit explanation:** Both dogs' proper names remain unspecified under the adopted name scope.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 168. train_6383: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog jumps a man 's leg to take a Frisbee from his hand .
>
> **Caption B:** A fast black and white dog is running to catch a red Frisbee .
>
> **Adopted scope:** dog coat color
>
> **Extracted A:** unspecified
>
> **Extracted B:** black and white
>
> **Recorded reason, verbatim:** The first caption supplies no information about dog color. / First caption does not give the dog's color.

**Audit explanation:** A's Frisbee-catching dog has an unspecified coat color.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 169. train_6391: `sentiment of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Man kicking another man in the face in a karate competition .
>
> **Caption B:** During a martial arts match , a man attempts to kick the other in the face .
>
> **Adopted scope:** people's emotional sentiment
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Attempted sporting kicks do not directly establish emotional sentiment. / Fighting actions alone do not establish emotional sentiment.

**Audit explanation:** Both competitive kicking actions leave emotional sentiment unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `5.0`.

### 170. train_6553: `location of action`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young boy jumping into a pool that says " no diving " .
>
> **Caption B:** One teenager taking a risk by diving on his side .
>
> **Adopted scope:** water-entry location
>
> **Extracted A:** swimming pool
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Second gives diving action without establishing a location or waterbody.

**Audit explanation:** B's dive leaves the surrounding location and water body unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `4.0`.

### 171. train_6589: `color of dress`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A little girl in a white sundress smiles and slides down a blue slide .
>
> **Caption B:** A little girl makes a goofy face and does a half push up in the grass .
>
> **Adopted scope:** specified dress color
>
> **Extracted A:** white sundress
>
> **Extracted B:** no dress described
>
> **Recorded reason, verbatim:** Second caption supplies no dress color information. / Second caption supplies no dress or dress color information.

**Audit explanation:** B's girl has an unestablished dress entity and color. A identifies a white sundress.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 172. train_6613: `breed of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A gray dog is jumping toward a black and white dog in the snow .
>
> **Caption B:** A brown dog carrying a Frisbee runs through the snow .
>
> **Adopted scope:** dog breed
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption establishes a dog's breed. / Neither caption establishes a specific breed of dog.

**Audit explanation:** Both dog breeds remain unspecified. Coat colors identify appearance.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 173. train_6636: `temperament of dogs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A brown and white dog is running across the grass .
>
> **Caption B:** Two dogs run along a grassy field while one bites the other .
>
> **Adopted scope:** dogs' temperament
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Running and biting do not establish comparable temperaments. / First running action does not establish the dogs temperament.

**Audit explanation:** A's running dog has an unspecified temperament.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 174. train_6661: `absence of umbrella`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A lady walks in the rain with a yellow umbrella .
>
> **Caption B:** Woman walking in the rain and unicycle standing next to a pole .
>
> **Adopted scope:** umbrella absence
>
> **Extracted A:** false, umbrella present
>
> **Extracted B:** unknown
>
> **Recorded reason, verbatim:** Final blind invalid consensus: A disproves umbrella absence; B never establishes whether an umbrella is absent. / Umbrella present first; second does not establish umbrella absence. / A explicitly includes an umbrella; B does not establish umbrella absence.

**Audit explanation:** B's rainy scene leaves umbrella absence unresolved. A includes a yellow umbrella.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 175. train_6751: `color of dogs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a dog jumps over another dog as both animals are trying to catch the same ball .
>
> **Caption B:** A brown dog in a pink shirt chews something white while a brown dog in yellow watches .
>
> **Adopted scope:** dog coat colors
>
> **Extracted A:** unspecified
>
> **Extracted B:** brown
>
> **Recorded reason, verbatim:** The first caption supplies no dog color information. / First caption provides no animal colors to compare.

**Audit explanation:** A's jumping dogs have unspecified coat colors.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 176. train_6770: `action of girl`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A little girl in a pink shirt and a little girl in an orange shirt sitting in the grass .
>
> **Caption B:** This young girl is enjoying the innocence of childhood and warm weather .
>
> **Adopted scope:** girl's physical action
>
> **Extracted A:** sitting in grass
>
> **Extracted B:** enjoying weather; bodily action unspecified
>
> **Recorded reason, verbatim:** Enjoying weather supplies no recoverable physical action to compare with sitting.

**Audit explanation:** B describes enjoyment. Bodily action remains unspecified under the adopted physical-action scope.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 177. train_6975: `material of ground`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Asian kids sitting on a mat playing with a toy .
>
> **Caption B:** Several children sitting on the floor in a metal building .
>
> **Adopted scope:** material of supporting ground surface
>
> **Extracted A:** mat material unspecified
>
> **Extracted B:** floor material unspecified
>
> **Recorded reason, verbatim:** Metal building does not establish floor material. / Neither caption establishes the material composing the ground surface.

**Audit explanation:** A identifies a mat. B identifies a floor. Both supporting-surface materials remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 178. train_6993: `location description`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A large brown dog is running through a grassy backyard .
>
> **Caption B:** A brown greyhound is wearing a blue muzzle and blue collar .
>
> **Adopted scope:** dog's location
>
> **Extracted A:** grassy backyard
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Muzzle and collar do not establish location. / Only the first supplies the dogs location description.

**Audit explanation:** B's muzzle and collar leave the dog's location unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 179. train_7063: `competitiveness level of persons`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Several bicyclists wearing helmets ride by to the right .
>
> **Caption B:** A group of cyclists riding their bikes in a marathon .
>
> **Adopted scope:** participants' competitiveness level
>
> **Extracted A:** unspecified
>
> **Extracted B:** competitive marathon
>
> **Recorded reason, verbatim:** First riders' competitive status is not established. / First caption supplies no competitive context or athlete level.

**Audit explanation:** A's cyclists have an unspecified competitive status.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 180. train_7141: `object travelled past`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A group of people are running through a street .
>
> **Caption B:** Marathon runners are running past a glass building .
>
> **Adopted scope:** object passed by runners
>
> **Extracted A:** no passed object described
>
> **Extracted B:** glass building
>
> **Recorded reason, verbatim:** The first caption does not identify an object traveled past. / First caption describes the route but no object traveled past.

**Audit explanation:** A's running route leaves any passed object unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 181. train_7143: `presence of tye-dye t-shirt`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Man in a colorful tye-dye t-shirt doing a trick on his skateboard .
>
> **Caption B:** A young man is doing a skating trip on a skateboard ramp .
>
> **Adopted scope:** tie-dye shirt presence
>
> **Extracted A:** present
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Final blind invalid consensus: Tie-dye clothing is explicit in A but neither confirmed nor denied in B. / Tie-dye shirt is present first; second leaves clothing pattern unknown. / A specifies the shirt; B leaves clothing pattern unreported.

**Audit explanation:** B's skateboard trick leaves tie-dye shirt presence unknown.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 182. train_7260: `profession of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a person doing the backstroke in a swimming pool
>
> **Caption B:** A professional swimmer racing to the finish line .
>
> **Adopted scope:** person's profession
>
> **Extracted A:** unspecified
>
> **Extracted B:** professional swimmer
>
> **Recorded reason, verbatim:** Swimming alone does not establish a professional occupation. / Swimming activity alone does not establish the first persons profession.

**Audit explanation:** A describes swimming activity. A professional occupation remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 183. train_7271: `movement of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** two people are nearing the top of an escalator .
>
> **Caption B:** Several people look down from above the first floor .
>
> **Adopted scope:** people bodily locomotion
>
> **Extracted A:** ascending toward escalator top
>
> **Extracted B:** looking down; locomotion unspecified
>
> **Recorded reason, verbatim:** Gaze direction supplies no locomotion value for the second people.

**Audit explanation:** B specifies gaze direction. Bodily locomotion remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 184. train_7313: `presence of trees`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man on a bicycle jumps over jagged rocks amongst tall pine trees .
>
> **Caption B:** a guy on a bike jumping from one large rock to another
>
> **Adopted scope:** tree presence
>
> **Extracted A:** present
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Final blind invalid consensus: A explicitly contains pine trees; B never establishes trees or their absence. / Pine trees present first; second does not establish trees absence. / A explicitly includes pine trees; B supplies no tree presence information.

**Audit explanation:** B's bike jump leaves tree presence unknown. A identifies pine trees.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 185. train_7423: `absence of hard hats`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Workers are wearing hard hats at a construction site while building something with wood .
>
> **Caption B:** Construction workers hammer nails on the unfinished roof of a house .
>
> **Adopted scope:** hard-hat absence
>
> **Extracted A:** false, hard hats present
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Final blind invalid consensus: A disproves hard-hat absence; B gives no headwear information. / First workers wear hard hats; second workers headwear is unspecified. / A explicitly includes hard hats; B does not establish their absence.

**Audit explanation:** B's roof work leaves hard-hat absence unresolved. A explicitly includes hard hats.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 186. train_7466: `absence of snowshoes`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young boy and his father use snowshoes to walk in the snow .
>
> **Caption B:** Two kids play a game together with sticks in the snow .
>
> **Adopted scope:** snowshoe absence for participants
>
> **Extracted A:** false: snowshoes used
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Final blind invalid consensus: A disproves snowshoe absence; B gives no snowshoe information. / First snowshoes are present; second children footwear is unspecified. / A explicitly includes snowshoes; B does not establish their absence.

**Audit explanation:** B's snow play leaves snowshoe absence unresolved. A identifies snowshoe use.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 187. train_7543: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a green jacket and brown pants is pictured in midair on a snowboard .
>
> **Caption B:** A young snowboarder catches some air on his black snowboard .
>
> **Adopted scope:** principal snowboard color
>
> **Extracted A:** unspecified
>
> **Extracted B:** black
>
> **Recorded reason, verbatim:** Shared snowboard color is unstated first; clothing colors cannot substitute.

**Audit explanation:** A's clothing colors leave snowboard color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 188. train_7559: `color of uniform`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a baseball player jumps against the fence to make a catch
>
> **Caption B:** A baseball player in a white and red uniform is sliding to base .
>
> **Adopted scope:** baseball player's uniform color
>
> **Extracted A:** unspecified
>
> **Extracted B:** white and red
>
> **Recorded reason, verbatim:** First caption does not establish any uniform color. / Only the second specifies any uniform color.

**Audit explanation:** A's baseball player has unspecified uniform colors.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 189. train_7607: `speed of cyclists`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A group of mountain bikers race each other down a dirt hill .
>
> **Caption B:** Two people ride bicycles over a bumpy racetrack .
>
> **Adopted scope:** cyclists' speed
>
> **Extracted A:** racing speed
>
> **Extracted B:** unspecified riding speed
>
> **Recorded reason, verbatim:** Racing and riding alone do not establish comparable cycling speeds. / Race participation alone does not establish comparable cyclist speeds.

**Audit explanation:** B's racetrack riding leaves actual cycling pace unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 190. train_7833: `type of construction work`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The construction worker noticed the crooked board .
>
> **Caption B:** Two construction workers are bent over and straddling a metal I-beam .
>
> **Adopted scope:** construction task type
>
> **Extracted A:** unspecified: noticing board
>
> **Extracted B:** unspecified: straddling I-beam
>
> **Recorded reason, verbatim:** Neither caption clearly establishes a comparable construction-work subtype. / Neither identifies a specific construction work discipline reliably.

**Audit explanation:** A identifies noticing a board. B identifies straddling a beam. Construction task types remain unspecified under the adopted scope.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 191. train_7856: `intent to injure`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two men kickbox in a ring , one man punching the other .
>
> **Caption B:** A boxer in red lands a glancing blow off of a boxer in white .
>
> **Adopted scope:** fighters' intent to injure
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Combat sport participation does not establish an intent to injure. / Competitive strikes do not establish an intent to injure.

**Audit explanation:** Both sporting strikes leave intent to injure unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `5.0`.

### 192. train_7861: `type of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a small black and white jumping to catch something in its mouth .
>
> **Caption B:** A dog flies through the air , preparing to catch a ball .
>
> **Adopted scope:** principal animal type
>
> **Extracted A:** animal noun omitted; type unavailable
>
> **Extracted B:** dog
>
> **Recorded reason, verbatim:** Malformed first caption does not reliably identify animal type. / First caption omits an animal noun; species cannot be established.

**Audit explanation:** A's missing animal noun leaves animal type unresolved despite color and catching details.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 193. train_7872: `place of action`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Many people wearing numbers , hats and jackets are running in a race .
>
> **Caption B:** Runners , some in costume , in a St Paddy 's day Marathon run in the streets as people watch .
>
> **Adopted scope:** race location
>
> **Extracted A:** unspecified
>
> **Extracted B:** streets
>
> **Recorded reason, verbatim:** The first caption does not identify where the race occurs. / First caption does not establish the place of racing.

**Audit explanation:** A's race location remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `4.0`.

### 194. train_7892: `type of construction work`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A worker in safety clothes is standing up on the wooded edge of the construction .
>
> **Caption B:** 8 construction workers high up in the air putting up scaffolding .
>
> **Adopted scope:** construction task type
>
> **Extracted A:** unspecified standing at edge
>
> **Extracted B:** erecting scaffolding
>
> **Recorded reason, verbatim:** Standing at construction does not establish a specific construction task. / First does not identify a particular construction task.

**Audit explanation:** A's worker stands at a construction edge. The construction task remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 195. train_7921: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog catches a flying disk in a yard with a tree .
>
> **Caption B:** A black dog standing in a field is holding a bird in his mouth .
>
> **Adopted scope:** principal dog's coat color
>
> **Extracted A:** unspecified
>
> **Extracted B:** black
>
> **Recorded reason, verbatim:** First caption supplies no animal color information. / Only the second supplies the dogs fur color.

**Audit explanation:** A's disk-catching dog has an unspecified coat color.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 196. train_7963: `motion of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog is in some water with a tree branch in its mouth .
>
> **Caption B:** A dog drags a white rag through an almost-dried up creek .
>
> **Adopted scope:** principal dog's motion
>
> **Extracted A:** unspecified while in water
>
> **Extracted B:** moving while dragging rag
>
> **Recorded reason, verbatim:** Being in water holding a branch does not establish locomotion.

**Audit explanation:** A's dog holds a branch in water. Its locomotion remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 197. train_7975: `position of arms`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Kayak rider raises arms as he 's splashed with water .
>
> **Caption B:** A person white-water rafting in turbulent water .
>
> **Adopted scope:** principal person's arm position
>
> **Extracted A:** raised
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption does not establish the person's arm position. / Second caption does not describe the person's arms.

**Audit explanation:** B's rafting description leaves arm position unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 198. train_8052: `attire of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man on a brown horse is preparing to lasso a bull , while another man on a white horse corrals the bull .
>
> **Caption B:** Cowboy with a purple shirt and black vest trying to hold on during a wild horse ride .
>
> **Adopted scope:** principal horseback riders' attire
>
> **Extracted A:** unspecified
>
> **Extracted B:** purple shirt and black vest
>
> **Recorded reason, verbatim:** The first caption supplies no information about human clothing. / First caption gives no rider clothing to compare.

**Audit explanation:** A's horseback riders have unspecified clothing.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 199. train_8053: `color of horse`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man on a brown horse is preparing to lasso a bull , while another man on a white horse corrals the bull .
>
> **Caption B:** Cowboy with a purple shirt and black vest trying to hold on during a wild horse ride .
>
> **Adopted scope:** horses' coat colors
>
> **Extracted A:** brown and white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption supplies no horse color information. / Second caption does not describe the horse's color.

**Audit explanation:** B's horse coat color remains unspecified. The stated colors identify the cowboy's clothes.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 200. train_8274: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A big dog carries a stick across a frozen pond .
>
> **Caption B:** Two dogs , one holding something in its mouth , in the snow .
>
> **Adopted scope:** principal dogs' or carried object's color
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption establishes a carried object's color. / Neither caption gives the carried objects color.

**Audit explanation:** Both carried-object colors remain unspecified. Snow and ice identify surroundings.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 201. train_8373: `location`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Young white male child with blond-hair in a red shirt coloring with crayons outside with an adult .
>
> **Caption B:** A young child sits in a highchair and draws colorful squiggles on a white piece of paper .
>
> **Adopted scope:** principal child's location
>
> **Extracted A:** outside
>
> **Extracted B:** highchair; surrounding location unspecified
>
> **Recorded reason, verbatim:** Second gives a highchair position but no comparable environmental location.

**Audit explanation:** B supplies a highchair position. The surrounding indoor or outdoor setting remains unspecified under the adopted environmental-location reading.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 202. train_8487: `intentions of spectators`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A baseball player swings the bat as a catcher and umpire watch .
>
> **Caption B:** Two baseball players on a field , with four spectators , and a crowd .
>
> **Adopted scope:** spectators' intentions
>
> **Extracted A:** no spectators described; catcher and umpire watch
>
> **Extracted B:** unspecified spectator intent
>
> **Recorded reason, verbatim:** The first caption does not establish spectators or their intentions. / First names officials and players rather than spectators with intentions.

**Audit explanation:** A identifies players and an official. Spectators remain unestablished. B's spectator intentions remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 203. train_8568: `location`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The skateboarder does a jump near a traffic cone .
>
> **Caption B:** A young man is jumping in the air with his skateboard .
>
> **Adopted scope:** skateboarder's location
>
> **Extracted A:** near traffic cone
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption does not establish a location to compare. / Second caption does not establish a comparable location.

**Audit explanation:** B explicitly places the skateboarder in the air. The intended location feature needs review because the exclusion concerns unavailable surroundings.

**Policy check:** Review exclusion policy. **Peer:** `writer_test`.

**Review question:** Should generic location include B’s explicit airborne position, or does the condition require surrounding venue or ground features?

**History:** supplied source rating `3.0`.

### 204. train_8581: `performer's age`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A gymnast wearing a maroon and black outfit has just completed a routine and is posting on the gym mat .
>
> **Caption B:** A young rhythmic gymnastic is watching a yellow hula hoop go by during her routine .
>
> **Adopted scope:** principal gymnast's age
>
> **Extracted A:** unspecified
>
> **Extracted B:** young
>
> **Recorded reason, verbatim:** The first caption provides no performer age information. / First caption provides no performer age to compare.

**Audit explanation:** A's gymnast age remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 205. train_8650: `speed of players`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A baseball player in blue scoring run by crossing home plate .
>
> **Caption B:** Baseball players walk as a group on the field , and some jump to celebrate .
>
> **Adopted scope:** baseball players' speed
>
> **Extracted A:** crossing plate, speed unspecified
>
> **Extracted B:** walking and jumping
>
> **Recorded reason, verbatim:** Scoring a run does not establish the first player's actual speed. / Scoring a run does not establish the player's actual speed.

**Audit explanation:** A's scoring action leaves actual player speed unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 206. train_8780: `uniqueness of bike`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man is racing an unusual type of bike with many people watching him .
>
> **Caption B:** A cyclist wearing a red and black jersey is competing in a race .
>
> **Adopted scope:** bike's unusualness
>
> **Extracted A:** explicitly unusual bike
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption gives no evidence about bike uniqueness. / Second caption does not establish whether bike is unusual.

**Audit explanation:** B's race participation leaves the bike's unusualness unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 207. train_8791: `temperament of horse`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two men on horses compete to see who can rope the calf first .
>
> **Caption B:** A rodeo rider is riding a bucking horse in an arena .
>
> **Adopted scope:** horse's temperament
>
> **Extracted A:** unspecified
>
> **Extracted B:** resisting by bucking
>
> **Recorded reason, verbatim:** First caption does not establish the horses' temperament. / First caption gives no specific horse temperament for comparison.

**Audit explanation:** A's calf-roping scene leaves horse temperaments unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 208. train_8799: `object in dog's mouth`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A white dog jumps above a red Frisbee that is rolling along the surface of a low cut field .
>
> **Caption B:** A black and white dog is catching a red and green object in his mouth .
>
> **Adopted scope:** object in dog's mouth
>
> **Extracted A:** none described: Frisbee rolls on ground
>
> **Extracted B:** red and green object being caught
>
> **Recorded reason, verbatim:** The first dog has no established object in its mouth. / First caption establishes no object inside the dog's mouth.

**Audit explanation:** A places the Frisbee on the ground. An object in the dog's mouth remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 209. train_8829: `relationship of players`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A baseball pitcher prepares to pitch the ball to the batter .
>
> **Caption B:** one baseball player running toward a base with another waiting on the base
>
> **Adopted scope:** players' team relationship
>
> **Extracted A:** pitcher and opposing batter
>
> **Extracted B:** runner and base player; affiliation unspecified
>
> **Recorded reason, verbatim:** Final blind invalid consensus: A establishes pitcher versus batter; B does not establish teammates or opponents. / Waiting player may be teammate or opponent; relationship cannot resolve. / B does not establish whether the waiting player is teammate or opponent.

**Audit explanation:** B's waiting base player has an unspecified team relationship to the runner under the adopted affiliation scope.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 210. train_9039: `presence of hard hat`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Construction worker in a hard hat and yellow neon vest , working on stairs .
>
> **Caption B:** A worker stands on a scaffolding to repair a brick building .
>
> **Adopted scope:** worker's hard-hat presence
>
> **Extracted A:** present
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Final blind invalid consensus: Hard hat is explicit in A; B never establishes headwear or its absence. / Hard hat explicit first; scaffolding work does not establish headwear. / A explicitly includes a hard hat; B leaves head protection unreported.

**Audit explanation:** B's scaffolding work leaves hard-hat presence unknown.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 211. train_9077: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Person with an orange backpack watching the surrounding hills .
>
> **Caption B:** A hiker walks on rocky ground at the base of a foggy mountain .
>
> **Adopted scope:** principal portable object's color
>
> **Extracted A:** orange backpack
>
> **Extracted B:** no portable object described
>
> **Recorded reason, verbatim:** The second caption supplies no comparable object color. / Second caption does not establish a comparable object color.

**Audit explanation:** B identifies a hiker. A portable object and its color remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 212. train_9146: `results of sport`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cowboy is falling off a bull and looks like he might get trampled .
>
> **Caption B:** A man is competing in a bareback bronco riding competition during a rodeo in front of a crowd .
>
> **Adopted scope:** sporting outcome
>
> **Extracted A:** falling off bull; possible trampling
>
> **Extracted B:** result unspecified
>
> **Recorded reason, verbatim:** Second caption gives no result of the ride. / Second caption describes participation without establishing a sporting outcome.

**Audit explanation:** B's rodeo participation leaves the ride's outcome unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 213. train_9223: `animal proximity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A brown dog and a black dog are together in the tall grass .
>
> **Caption B:** One dog wades in the water while another dog is on land .
>
> **Adopted scope:** principal dogs' mutual proximity
>
> **Extracted A:** together
>
> **Extracted B:** distance unspecified; one in water and one on land
>
> **Recorded reason, verbatim:** Land-versus-water placement does not establish the second dogs' mutual separation.

**Audit explanation:** B's water-versus-land positions leave the dogs' mutual distance unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 214. train_9329: `elevation of performance`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A biker reaches the apex of his ramp while onlookers watch his feat .
>
> **Caption B:** A male is doing a trick on his bicycle while others watch him and take pictures .
>
> **Adopted scope:** performer's elevation
>
> **Extracted A:** at ramp apex
>
> **Extracted B:** unspecified during bicycle trick
>
> **Recorded reason, verbatim:** The second caption supplies no comparable performance elevation. / Second caption does not establish performance elevation.

**Audit explanation:** B's bicycle trick leaves performer elevation unspecified. A identifies a ramp apex.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `4.0`.

### 215. train_9407: `focus of worker`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Construction worker in orange vest and white hard hat with a shovel .
>
> **Caption B:** Workers in hard hats and orange vests laying cement tiles over the floor .
>
> **Adopted scope:** workers attention target
>
> **Extracted A:** unspecified; holds shovel
>
> **Extracted B:** cement floor tiles
>
> **Recorded reason, verbatim:** A shovel alone does not establish the first worker's focus. / First does not establish the worker's immediate focus or task.

**Audit explanation:** A's shovel leaves the worker's immediate task and attention target unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `4.0`.

### 216. train_9456: `people's intentions`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The sun shines bright on the snow surrounding a few people .
>
> **Caption B:** Two hikers with backpacks crossing a snow field .
>
> **Adopted scope:** people immediate intention
>
> **Extracted A:** unspecified
>
> **Extracted B:** crossing snow field on hike
>
> **Recorded reason, verbatim:** The first caption does not establish the people's intentions. / First caption supplies no intentions for the people.

**Audit explanation:** A's snow scene leaves people's intentions unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 217. train_9538: `sentiment`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** several diferent colored dogs running through the grass
>
> **Caption B:** A dog chases a toy in the grass with its owner in the background .
>
> **Adopted scope:** scene emotional sentiment
>
> **Extracted A:** unexpressed
>
> **Extracted B:** unexpressed
>
> **Recorded reason, verbatim:** Neither caption clearly establishes an emotional tone or sentiment. / Running and chasing do not establish emotional sentiment.

**Audit explanation:** Both dog actions leave emotional sentiment unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 218. train_9616: `men's occupation`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man dressed as a cowboy holds a rope in his teeth as he ropes a calf .
>
> **Caption B:** Two men wearing earring hats and ponchos are on horses surrounding a bull .
>
> **Adopted scope:** men's occupations
>
> **Extracted A:** cowboy-like calf roping
>
> **Extracted B:** horsemen surrounding bull; occupation unstated
>
> **Recorded reason, verbatim:** The second men's clothing and proximity to a bull do not establish their occupations.

**Audit explanation:** B's horsemen have unspecified occupations despite their clothing and proximity to a bull.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 219. train_9689: `presence of audience`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A group of bicyclers that are going down the road .
>
> **Caption B:** Two bicycle racers are speeding down a street in front of spectators .
>
> **Adopted scope:** audience presence
>
> **Extracted A:** unspecified
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** Final blind invalid consensus: B explicitly includes spectators; A never establishes audience presence or absence. / Spectators establish audience second; first leaves audience presence unspecified. / B explicitly includes spectators; A supplies no audience presence information.

**Audit explanation:** A's cyclists leave audience presence unknown.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 220. train_9698: `name of location`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Kid in a skate park doing a trick with his skateboard .
>
> **Caption B:** A skateboarding soaring through the air in front of a blue building .
>
> **Adopted scope:** named venue or site type
>
> **Extracted A:** skate park
>
> **Extracted B:** building frontage, venue unspecified
>
> **Recorded reason, verbatim:** A building in the background does not identify the second site's venue type.

**Audit explanation:** B's building backdrop leaves venue type unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 221. train_9719: `presence of hat`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A little girl sitting in a small chair outdoors .
>
> **Caption B:** A little girl in a hat and red pants balances on tightropes .
>
> **Adopted scope:** principal girl hat presence
>
> **Extracted A:** unspecified
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** Final blind invalid consensus: B explicitly includes a hat; A never establishes headwear or its absence. / Hat is explicit second; first does not establish headwear absence. / B explicitly includes a hat; A leaves hat presence unreported.

**Audit explanation:** A's seated girl leaves hat presence unknown.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 222. train_9751: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two toddlers are sitting in a plastic playpen with a blue floor .
>
> **Caption B:** Two boys in tent-like area , with colorful balls on floor .
>
> **Adopted scope:** play area floor color
>
> **Extracted A:** blue
>
> **Extracted B:** unspecified; colorful balls on floor
>
> **Recorded reason, verbatim:** Final blind invalid consensus: Blue modifies A’s floor; B colors balls, leaving corresponding object color unavailable. / Object lacks stable referent between playpen, floor, tent, and balls.

**Audit explanation:** B identifies colorful balls. The corresponding floor color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 223. train_9759: `color of surfing material`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A surfer is riding a wave in a large body of water .
>
> **Caption B:** A surfer on a whiteboard about to fall off as a wave crashes around him .
>
> **Adopted scope:** surfboard color
>
> **Extracted A:** unspecified
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** The first caption does not establish the surfboard's color. / First caption does not establish surfing equipment color.

**Audit explanation:** A's surfboard color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 224. train_9779: `color of clothes`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person wearing a Red Bull ski helmet and ski suit snowboard .
>
> **Caption B:** A man in a green jacket and brown pants is pictured in midair on a snowboard .
>
> **Adopted scope:** principal clothing colors
>
> **Extracted A:** unspecified
>
> **Extracted B:** green and brown
>
> **Recorded reason, verbatim:** A brand name does not establish actual clothing colors. / Brand wording does not establish actual clothing colors.

**Audit explanation:** A's Red Bull branding leaves ski-suit colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 225. train_9787: `color of dog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black dog with a red collar stands outside with his paws in water .
>
> **Caption B:** A dog with a stick in its mouth runs through the rocks in shallow water .
>
> **Adopted scope:** principal dog coat color
>
> **Extracted A:** black
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption supplies no dog color information. / Second caption provides no dog color to compare.

**Audit explanation:** B's dog coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 226. train_9791: `hand position`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A young girl in a white shirt and blue shorts riding high on a swing .
>
> **Caption B:** A young girl closes her eyes and releases her hands as she enjoys the swing set .
>
> **Adopted scope:** principal girl hand position
>
> **Extracted A:** unspecified
>
> **Extracted B:** released from swing
>
> **Recorded reason, verbatim:** Riding high on swing does not establish hand position. / Only the second establishes the position of the girls hands.

**Audit explanation:** A's elevated swing leaves the girl's hand position unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 227. train_9795: `cost of boats`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Local villagers are preparing for a fishing trip on this gorgeous fishing boat .
>
> **Caption B:** Six men , two wearing hats , are sitting in a small boat on the water .
>
> **Adopted scope:** principal boat monetary cost
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption provides a boat price or reliable cost information. / Neither caption establishes any boat price or cost.

**Audit explanation:** Both boats' prices remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 228. train_9831: `gender`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young woman with a ponytail climbs a white stone structure .
>
> **Caption B:** A person in a red shirt climbing up a rock face covered in assist handles .
>
> **Adopted scope:** principal climber gender
>
> **Extracted A:** female
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption does not establish the climber's gender. / Second caption does not establish the climber's gender.

**Audit explanation:** B's climber gender remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 229. train_9937: `interaction between dogs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Black dog is submissive on ground to brown dog .
>
> **Caption B:** A big dog drinks as a little dog gets down off a deck .
>
> **Adopted scope:** dog-to-dog interaction
>
> **Extracted A:** submission to other dog
>
> **Extracted B:** separate drinking and stepping down
>
> **Recorded reason, verbatim:** Second dogs have separate actions without an established interaction.

**Audit explanation:** B describes separate drinking and stepping-down actions. A dog-to-dog interaction remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 230. train_9946: `activity of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The little girl in the pool is wearing a red swimsuit .
>
> **Caption B:** a smiling toddler in a pink swimsuit is laying in the water .
>
> **Adopted scope:** principal child activity
>
> **Extracted A:** being in pool; activity unspecified
>
> **Extracted B:** lying in water
>
> **Recorded reason, verbatim:** First pool presence does not establish any specific activity.

**Audit explanation:** A's girl is in a pool. Her activity and posture remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 231. train_10037: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person in face paint and an orange oversized cowboy hat rides his bike on a trail .
>
> **Caption B:** A woman in black bicycle gear and a white helmet pedals hard uphill on her bike .
>
> **Adopted scope:** principal bicycle color
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Final blind invalid consensus: Generic object does not select corresponding headwear versus other colored clothing. / Object does not specify headwear or clothing, yielding competing comparisons.

**Audit explanation:** Both principal bicycle colors remain unspecified. The stated colors identify clothing and headwear.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 232. train_10111: `color of person's shirt`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young child having fun in his Superman shirt .
>
> **Caption B:** Little blond-hair boy in orange shirt playing with toys .
>
> **Adopted scope:** principal child shirt color
>
> **Extracted A:** unspecified Superman shirt
>
> **Extracted B:** orange
>
> **Recorded reason, verbatim:** A Superman design does not reliably establish the shirt's color. / Character design alone does not establish the shirt color.

**Audit explanation:** A's Superman design leaves actual shirt color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 233. train_10153: `gender of surfer`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A surfer is riding a wave in a large body of water .
>
> **Caption B:** A man in a dark bodysuit is surfing through the spray of a powerful wave .
>
> **Adopted scope:** principal surfer gender
>
> **Extracted A:** unspecified
>
> **Extracted B:** male
>
> **Recorded reason, verbatim:** Only the second caption establishes the surfer's gender. / First caption does not establish the surfer's gender.

**Audit explanation:** A's surfer gender remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `4.0`.

### 234. train_10219: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A boy with an orange shirt lies on a bodyboard in the surf .
>
> **Caption B:** A man is riding the oceans waves on his surfboard .
>
> **Adopted scope:** principal ridden board color
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption establishes a comparable board color. / Second caption supplies no color for a comparable object.

**Audit explanation:** Both ridden-board colors remain unspecified. Orange identifies A's shirt.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 235. train_10241: `position of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A closeup of a man skateboarding in a skate park .
>
> **Caption B:** A skateboarding soaring through the air in front of a blue building .
>
> **Adopted scope:** principal skateboarder position
>
> **Extracted A:** unspecified skating position
>
> **Extracted B:** airborne
>
> **Recorded reason, verbatim:** First skateboarder's body position is not specified or directly inferable.

**Audit explanation:** A's skateboarding may support ordinary ground-supported riding under the training audit's inference rule. Exclusion for missing position needs policy review.

**Policy check:** Review exclusion policy. **Peer:** `writer_test`.

**Review question:** Does ordinary ground-supported skateboarding provide a comparable position, as allowed in the training audit, or is explicit posture required?

**History:** supplied source rating `2.0`.

### 236. train_10299: `clothing worn by boy`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young boy is holding his breath while he jumps into water .
>
> **Caption B:** The boy wearing swimming trunks is jumping off a pier into a lake .
>
> **Adopted scope:** principal boy clothing
>
> **Extracted A:** unspecified
>
> **Extracted B:** swimming trunks
>
> **Recorded reason, verbatim:** Jumping into water does not establish clothing type. / Only the second identifies the boys clothing.

**Audit explanation:** A's water jump leaves the boy's clothing unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 237. train_10380: `type of trick`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a bicyclist wearing a helmet jumping a trick on his back tire
>
> **Caption B:** A man in beige pants does a trick on a bicycle .
>
> **Adopted scope:** specific bicycle-trick type
>
> **Extracted A:** rear-wheel jump maneuver
>
> **Extracted B:** unspecified bicycle trick
>
> **Recorded reason, verbatim:** The second establishes that a trick occurs without supplying its type.

**Audit explanation:** B identifies a bicycle trick. Its specific maneuver remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 238. train_10421: `number of spectators`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two long distance bikers riding side by side on a two lane road .
>
> **Caption B:** Two bicycle racers are speeding down a street in front of spectators .
>
> **Adopted scope:** spectator count
>
> **Extracted A:** no spectator entity established
>
> **Extracted B:** multiple spectators; exact count unspecified
>
> **Recorded reason, verbatim:** First caption does not establish any spectator count. / First caption gives no spectator count or established absence.

**Audit explanation:** A's two cyclists leave spectator count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 239. train_10449: `height of location`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man on a bicycle jumping off a dirt ramp with one foot on the ground
>
> **Caption B:** One helmeted man on a mountain bike is coming down a steep , rocky path .
>
> **Adopted scope:** terrain elevation
>
> **Extracted A:** unspecified dirt ramp elevation
>
> **Extracted B:** unspecified rocky path elevation
>
> **Recorded reason, verbatim:** Neither caption establishes comparable location elevation. / Terrain descriptions do not establish comparable absolute location heights.

**Audit explanation:** Both terrain descriptions leave absolute location elevation unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 240. train_10483: `age of player`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A teenager dressed in a baseball uniform attempting to hit a baseball during a game .
>
> **Caption B:** A baseball player in a red and white uniform runs while onlookers watch the game from outside the fence .
>
> **Adopted scope:** principal baseball player age category
>
> **Extracted A:** teenager
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption does not establish the player's age. / Second caption does not establish the player's age.

**Audit explanation:** B's baseball player age remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 241. train_10505: `temperament of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cowboy is desperately grasping too the reigns off a horse that is trying to buck him off at a rodeo .
>
> **Caption B:** A man and a boy riding brown horses are roping a white steer in a corral .
>
> **Adopted scope:** ridden horses temperament
>
> **Extracted A:** bucking resistant horse
>
> **Extracted B:** unspecified while ridden
>
> **Recorded reason, verbatim:** Being ridden while roping does not establish the second horses' temperament. / Roping scene does not establish the ridden horses' temperament.

**Audit explanation:** B's roping scene leaves the ridden horses' temperaments unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 242. train_10529: `Slope of walking path`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Three people in coats walking along a snow strewn trail on a mountain .
>
> **Caption B:** Men in pants and coats walk up a steep and narrow road .
>
> **Adopted scope:** walking-path gradient
>
> **Extracted A:** unspecified mountain-trail slope
>
> **Extracted B:** steep ascending road
>
> **Recorded reason, verbatim:** Being on a mountain does not establish the local trail's slope.

**Audit explanation:** A's mountain setting leaves the local trail gradient unspecified. B identifies a steep ascent.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 243. train_10537: `type of instrument`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A band of two men playing guitars and a man playing the drums , are singing on a stage .
>
> **Caption B:** A music venue with an awesome light show and three band members playing instruments .
>
> **Adopted scope:** band's instrument types
>
> **Extracted A:** guitars and drums
>
> **Extracted B:** unspecified instruments
>
> **Recorded reason, verbatim:** The second identifies no recoverable instrument type.

**Audit explanation:** B leaves instrument types unspecified. A identifies guitars and drums.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 244. train_10663: `location of skate park`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A boy in a white shirt does a trick on his skateboard at a skate park .
>
> **Caption B:** a roller-blader grinds a rail at an indoor skate park .
>
> **Adopted scope:** skate park indoor/outdoor location
>
> **Extracted A:** unspecified
>
> **Extracted B:** indoors
>
> **Recorded reason, verbatim:** The first caption does not specify the park's location setting. / First caption does not establish indoor versus outdoor location.

**Audit explanation:** A's skate park leaves indoor or outdoor location unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `4.0`.

### 245. train_10782: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person wearing a white hat is riding a horse like a bull at a rodeo .
>
> **Caption B:** A bull is charging a matador in rodeo , while three other men look at the animal .
>
> **Adopted scope:** principal ridden or confronted animal color
>
> **Extracted A:** horse color unspecified
>
> **Extracted B:** bull color unspecified
>
> **Recorded reason, verbatim:** Second caption supplies no comparable object color. / Second caption supplies no object color for comparison.

**Audit explanation:** Both principal animals' coat colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 246. train_10833: `distance travelled`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Someone leaps across the beach in a sign of joy !
>
> **Caption B:** Girl jumping on the beach with water in the background .
>
> **Adopted scope:** principal person distance traveled
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption provides an extractable distance traveled. / Neither caption provides the distance traveled while jumping.

**Audit explanation:** Both jumping descriptions leave traveled distance unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `4.0`.

### 247. train_10849: `animal size`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black dog has its mouth open while leaning to the side .
>
> **Caption B:** A small black dog playing with a ball in the grass .
>
> **Adopted scope:** principal dog size
>
> **Extracted A:** unspecified
>
> **Extracted B:** small
>
> **Recorded reason, verbatim:** First caption provides no information on dog size. / Only the second supplies any animal size information.

**Audit explanation:** A's dog size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 248. train_10850: `location name`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A brown dog running with a long stick in his mouth .
>
> **Caption B:** A dark brown dog jumps behind a young girl in shorts .
>
> **Adopted scope:** principal dog geographic location
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption provides a name or identifiable type of location. / Neither caption identifies the location's name.

**Audit explanation:** Both dogs' geographic locations remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `2.0`.

### 249. train_10882: `address of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** People are gathered on a city street with police vehicles arriving .
>
> **Caption B:** People going about their business at the corner of 5th Avenue and W 58th streets .
>
> **Adopted scope:** scene street address
>
> **Extracted A:** unspecified city street
>
> **Extracted B:** 5th Avenue and W 58th Street
>
> **Recorded reason, verbatim:** First caption provides no street address information. / Only the second supplies a specific street address.

**Audit explanation:** A's city street leaves its address unspecified. B identifies a specific intersection.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 250. train_10938: `size of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Little boy in his bathing suit tentatively preparing to step in the rocky-lined stream .
>
> **Caption B:** A boy is laying on a large river rock with his feet in the water on a sunny day .
>
> **Adopted scope:** principal water-edge rocks size
>
> **Extracted A:** unspecified stream-edge rocks
>
> **Extracted B:** large river rock
>
> **Recorded reason, verbatim:** First caption does not establish rock size. / Only the second supplies size of the relevant rocks.

**Audit explanation:** A's stream-side rocks have unspecified sizes.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 251. train_10939: `sentiment of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Little boy in his bathing suit tentatively preparing to step in the rocky-lined stream .
>
> **Caption B:** A boy is laying on a large river rock with his feet in the water on a sunny day .
>
> **Adopted scope:** principal boy emotional state
>
> **Extracted A:** tentative or hesitant
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Reclining in sunshine does not establish the second boy's sentiment. / Second caption gives no reliable indication of the boys emotion.

**Audit explanation:** B's reclining boy has an unspecified emotional state.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 252. train_11010: `clothing style`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A girl in a red dress is surrounded by a lot of other people holding their hands up .
>
> **Caption B:** A crowd of people with their arms in the air , many wearing hats of various kinds .
>
> **Adopted scope:** people's overall clothing style
>
> **Extracted A:** red dress on girl; style unstated
>
> **Extracted B:** varied hats on crowd; style unstated
>
> **Recorded reason, verbatim:** Garment names alone do not establish comparable overall styles such as casual, formal, or costume.

**Audit explanation:** Both overall clothing-style categories remain unspecified under the adopted style scope.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 253. train_11015: `hair condition`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bald guitarist in all black clothing playing his guitar with his band .
>
> **Caption B:** A man wearing a black t-shirt is playing seven string bass a stage .
>
> **Adopted scope:** principal musician hair condition
>
> **Extracted A:** bald
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption supplies no information about hair condition. / Second caption provides no hair condition for comparison.

**Audit explanation:** B's musician has an unspecified hair condition.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 254. train_11111: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog playing in the snow , ready to catch a toy
>
> **Caption B:** A dark dog jumps across the snow near the woods .
>
> **Adopted scope:** principal dog coat color
>
> **Extracted A:** unspecified
>
> **Extracted B:** dark
>
> **Recorded reason, verbatim:** First caption supplies no animal color information. / Only the second supplies the dogs fur color.

**Audit explanation:** A's dog coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 255. train_11135: `number of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Athletes on numbered horses congregate in a field .
>
> **Caption B:** A group of greyhounds racing with jerseys and muzzles .
>
> **Adopted scope:** all described humans
>
> **Extracted A:** multiple mounted athletes
>
> **Extracted B:** no human entity established
>
> **Recorded reason, verbatim:** The second caption establishes dogs but no human count. / Second caption supplies no people whose number can be extracted.

**Audit explanation:** B's greyhounds leave the number of people present unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `1.0`.

### 256. train_11223: `gender`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A surfer wearing a wetsuit and using a light colored board catches some air .
>
> **Caption B:** The sun gives the waves a green hue as this surfer displays his skills .
>
> **Adopted scope:** principal surfer gender
>
> **Extracted A:** unspecified
>
> **Extracted B:** male
>
> **Recorded reason, verbatim:** Only the second caption establishes the surfer's gender. / First surfer's gender cannot be extracted reliably.

**Audit explanation:** A's surfer gender remains unspecified. B uses a male pronoun.

**Policy check:** Policy consistent. **Peer:** `writer_test`.

**History:** supplied source rating `3.0`.

### 257. train_11335: `woman stance`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Women riding a horse carrying the American flag , both rider and horse dressed patriotically .
>
> **Caption B:** A blond woman in a green and gray uniform balances on a horse as she shows the American flag off to the crowd .
>
> **Adopted scope:** female rider's stance
>
> **Extracted A:** mounted on horse, exact stance unstated
>
> **Extracted B:** balancing on horse, exact stance unstated
>
> **Recorded reason, verbatim:** Riding and balancing do not reliably establish seated versus standing stance for the comparison.

**Audit explanation:** Both captions supply mounted activity. Exact seated or standing stance remains unresolved. The scope of partial stance information needs review.

**Policy check:** Review exclusion policy. **Peer:** `writer_test`.

**Review question:** Do riding and balancing supply partial stance information, or must seated versus standing be explicitly recoverable?

**History:** supplied source rating `4.0`.

### 258. train_11341: `means of flotation`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man and a small girl floating on an innertube .
>
> **Caption B:** A man is helping his child float along in the pool .
>
> **Adopted scope:** physical means supporting flotation
>
> **Extracted A:** inner tube
>
> **Extracted B:** man helps child float, actual buoyancy support unstated
>
> **Recorded reason, verbatim:** Helping a child float does not establish whether support comes from arms, swimming, or a flotation device.

**Audit explanation:** B identifies the man's assistance. Its physical support mechanism remains unspecified. The scope of partial flotation means needs review.

**Policy check:** Review exclusion policy. **Peer:** `writer_test`.

**Review question:** Can the man’s stated assistance supply a partial flotation means, or must the physical buoyancy mechanism be identified?

**History:** supplied source rating `3.0`.
