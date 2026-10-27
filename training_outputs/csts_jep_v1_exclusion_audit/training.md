# Full audit of excluded training comparisons

**Snapshot:** `jep-csts-v1`. All **929 exclusions** appear below. Authors and peers are separate assistant contexts. The [audit index](../../datasets/csts-jep-revision-v1/EXCLUSIONS.md) defines the policy codes.

## Cases flagged for review

| ID | Check | Review question |
|---|---|---|
| `train_205` | Review exclusion policy | Should product color cover the named chair and cabinet or the computers? |
| `train_688` | Review exclusion policy | Should the described speakers count under the recorded electronic-device scope? |
| `train_689` | Review exclusion policy | Which electronic-device type should the described speakers supply? |
| `train_778` | Review exclusion policy | Should the condition include the animal represented by the teddy bear? |
| `train_779` | Review exclusion policy | Should the recorded bear-figure count include teddy bears? |

## All 929 excluded comparisons

### 001. train_24: `type of building`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A tub is sitting in the middle of the room while the curtains are drawn open.
>
> **Caption B:** Big bed with a roof has a mirror on the center of bed roof
>
> **Adopted scope:** type or function of the building
>
> **Extracted A:** tub room; building function unspecified
>
> **Extracted B:** bedroom; building function unspecified
>
> **Recorded reason, verbatim:** Room furnishings establish room use, not the type of the containing building; residential and commercial accommodation remain unestablished.

**Audit explanation:** Both captions leave the containing building's type unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 002. train_26: `building purpose`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bicycle and a tricycle decorated with flowers in front of a florists shop.
>
> **Caption B:** Several bicycles are parked next to the window of a brown brick building that has flower boxes on the window.
>
> **Adopted scope:** building purpose
>
> **Extracted A:** florist shop
>
> **Extracted B:** brick building with flower boxes
>
> **Recorded reason, verbatim:** Flower boxes outside a building do not establish its commercial purpose.

**Audit explanation:** B's brick building and flower boxes leave the building's purpose unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 003. train_47: `location of person relative to ground`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Black and white close up of the feet for a skateboarder doing a trick.
>
> **Caption B:** A skateboard flying through the air and a person preparing to land on the skateboard.
>
> **Adopted scope:** skateboarder ground relation
>
> **Extracted A:** doing trick; elevation unspecified
>
> **Extracted B:** airborne preparing landing
>
> **Recorded reason, verbatim:** Doing a skateboard trick alone does not establish elevation in the first caption.

**Audit explanation:** A's skateboard trick leaves the skateboarder's elevation unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 004. train_49: `proximity of player to ball`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A male tennis player on a court with a tennis racket in the foreground.
>
> **Caption B:** The man in the red shirt is going to hit the ball with his racket.
>
> **Adopted scope:** player-ball proximity
>
> **Extracted A:** ball unspecified
>
> **Extracted B:** about to hit ball
>
> **Recorded reason, verbatim:** The first caption provides no ball or ball-relative distance.

**Audit explanation:** A leaves the ball's position and its distance from the player unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 005. train_64: `relative location of toilet within bathroom`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** The water tank for the toilet is separate from the toilet and is in a corner.
>
> **Caption B:** A bathroom that has a white toilet and white sink next to a glass doot shower.
>
> **Adopted scope:** toilet location within bathroom
>
> **Extracted A:** separate tank in corner; toilet placement unspecified
>
> **Extracted B:** next to sink and shower
>
> **Recorded reason, verbatim:** The tank's corner position cannot be assigned to the separate toilet.

**Audit explanation:** A locates the separate tank in a corner. The toilet's location remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 006. train_75: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A guy in pink shorts prepares to hit a tennis ball with a racket.
>
> **Caption B:** A man with a tennis racket serving a tennis ball, on a hard surface tennis court.
>
> **Adopted scope:** clothing color
>
> **Extracted A:** pink shorts
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Only one caption supplies clothing color.

**Audit explanation:** B leaves clothing color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 007. train_76: `material of objects`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Kitchen scene light brown wood wood counter tops and floor with mostly brown dog with white accents.
>
> **Caption B:** A kitchen has cabinet doors ajar and a view of  grass outside the window.
>
> **Adopted scope:** room-object material
>
> **Extracted A:** wood counters and floor
>
> **Extracted B:** cabinet materials unspecified
>
> **Recorded reason, verbatim:** Cabinet doors can have different materials; the second does not establish wood.

**Audit explanation:** B leaves cabinet-door material unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 008. train_79: `size of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A smiling lady holding food in her hand towards a large giraffe looming over her.
>
> **Caption B:** a woman looking into the camera while a giraffe goes for a leaf to eat
>
> **Adopted scope:** giraffe size
>
> **Extracted A:** large looming
>
> **Extracted B:** giraffe with unspecified size
>
> **Recorded reason, verbatim:** The second giraffe has no individual size or body-build description; species alone does not recover that value.

**Audit explanation:** B leaves giraffe size unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 009. train_82: `type of wearings`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A pretty young lady laying back on a red couch holding her hairless cat.
>
> **Caption B:** A woman dressed in a sweater and jeans, sitting on a futon couch with a cat in her lap
>
> **Adopted scope:** woman clothing type
>
> **Extracted A:** unspecified
>
> **Extracted B:** sweater and jeans
>
> **Recorded reason, verbatim:** The first woman's clothes are unstated.

**Audit explanation:** A leaves the woman's clothing unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 010. train_97: `color of clock`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a close up of a vase in front of a clock on a desk
>
> **Caption B:** A black clock on a wall with a black and white decor item below it.
>
> **Adopted scope:** clock color
>
> **Extracted A:** unspecified
>
> **Extracted B:** black
>
> **Recorded reason, verbatim:** The first clock has no color description.

**Audit explanation:** A leaves clock color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 011. train_105: `location of tennis court`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A shiny new racket looks down upon the worn shoes of a tennis player.
>
> **Caption B:** A guy playing tennis in a city court is about to hit the ball.
>
> **Adopted scope:** court location
>
> **Extracted A:** unspecified
>
> **Extracted B:** city court
>
> **Recorded reason, verbatim:** The first caption does not locate the court.

**Audit explanation:** A's tennis equipment leaves the court's location unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 012. train_110: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cat playing with a drip of water from a faucet in a sink.
>
> **Caption B:** A black and white cat sitting on to of a table drinking from a glass.
>
> **Adopted scope:** cat color
>
> **Extracted A:** unspecified
>
> **Extracted B:** black and white
>
> **Recorded reason, verbatim:** No color is supplied for the first cat.

**Audit explanation:** A leaves cat color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 013. train_119: `animal's demeanor`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cat is sitting on a chair with its head turned to the side.
>
> **Caption B:** A dark grey cat is lounging on the sofa while staring angrily at the camera.
>
> **Adopted scope:** cat demeanor
>
> **Extracted A:** sitting with head turned
>
> **Extracted B:** angry stare
>
> **Recorded reason, verbatim:** Head orientation and sitting do not establish an emotional demeanor.

**Audit explanation:** A gives posture and head direction. The cat's demeanor remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 014. train_127: `color of traffic light`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A red traffic light at a snowy corner with Christmas lights in the distance.
>
> **Caption B:** a busy street intersection at dusk with all of the cars with their headlights on
>
> **Adopted scope:** traffic-light color
>
> **Extracted A:** red
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption supplies no traffic-signal color.

**Audit explanation:** B's traffic and headlights leave traffic-light color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 015. train_131: `type of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A vase sitting on a table near some chairs and in front of some nicnacs and a lamp.
>
> **Caption B:** A room with two large red chairs, a fireplace mantal, flatscreen television and multiple bookshelves with various books.
>
> **Adopted scope:** room type
>
> **Extracted A:** furnished domestic sitting space
>
> **Extracted B:** living room with fireplace TV and bookshelves
>
> **Recorded reason, verbatim:** A table, chairs and ornaments alone do not identify room function, following confirmed #31.

**Audit explanation:** A's ordinary furnishings leave the room's function unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 016. train_139: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A light on a pole with a chain hanging from it beside a blue door
>
> **Caption B:** A street light that is displaying a red light with the figure of a person.
>
> **Adopted scope:** principal light color
>
> **Extracted A:** unspecified
>
> **Extracted B:** red
>
> **Recorded reason, verbatim:** Blue describes the door rather than the first light.

**Audit explanation:** A colors the door blue. The pole light's color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 017. train_143: `animal presence`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A room with a wooden table surrounded by chairs and a dog laying on the floor.
>
> **Caption B:** Porcelain sinks lined up in one room with two men sitting in the next.
>
> **Adopted scope:** animal presence
>
> **Extracted A:** dog present
>
> **Extracted B:** animals unmentioned
>
> **Recorded reason, verbatim:** People and sinks in the second scene do not establish absence of animals.

**Audit explanation:** B leaves animal presence unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 018. train_167: `presence of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** close up of a plate with food on it and wine glasses near by
>
> **Caption B:** A place setting on a table with two forks, plate, two bowls and wine glasses.
>
> **Adopted scope:** food presence
>
> **Extracted A:** food present
>
> **Extracted B:** empty or filled dishes unspecified
>
> **Recorded reason, verbatim:** Dishes in a place setting do not establish whether food has been served.

**Audit explanation:** B lists dishes and glasses. Their food contents remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 019. train_196: `color of light`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A light shines red as the sky is a greenish blue color in the background.
>
> **Caption B:** A traffic signal and some street lights with a little sun shining behind them.
>
> **Adopted scope:** signal color
>
> **Extracted A:** red
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second traffic signal's active color is unstated.

**Audit explanation:** B leaves traffic-signal and streetlight colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 020. train_200: `number of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A sandwich on a long roll and french fries are in an oblong plate.
>
> **Caption B:** A sausage dog is seen coated with relishes, sauces, and on top of a brown bun.
>
> **Adopted scope:** animal count
>
> **Extracted A:** no animals established
>
> **Extracted B:** sausage dog is food
>
> **Recorded reason, verbatim:** A sausage dog on a bun is food, so neither scene establishes animals to count.

**Audit explanation:** Both captions describe food, including a hotdog. Actual animal presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 021. train_205: `color of product`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A desk has a black chair near it and a monitor and laptop on it.
>
> **Caption B:** a work space office with a desktop and chair and a blue file cabinet
>
> **Adopted scope:** product color
>
> **Extracted A:** black chair; electronics unspecified
>
> **Extracted B:** blue file cabinet
>
> **Recorded reason, verbatim:** Selecting unrelated colored chair and cabinet would not establish comparable principal computer colors.

**Audit explanation:** The recorded exclusion restricts products to computers. The broader product-color scope also includes A's black chair and B's blue cabinet. Scope requires review.

**Policy check:** Review exclusion policy. **Peer:** `writer_b`.

**Review question:** Should product color cover the named chair and cabinet or the computers?

**History:** supplied source rating `3.0`.

### 022. train_221: `location of truck`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Legos build into a truck with a trailer on the back of it .
>
> **Caption B:** A perfectly painted truck carrying a matching boat look like die cast toys on a roadway.
>
> **Adopted scope:** truck location
>
> **Extracted A:** unspecified
>
> **Extracted B:** roadway
>
> **Recorded reason, verbatim:** The first toy truck has no described setting.

**Audit explanation:** A leaves the Lego truck's location unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 023. train_228: `activity of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A woman in a yellow car holds a dachshund in her lap a she smokes a cigarette.
>
> **Caption B:** a dog sitting in the driver's seat of the car like it wants to drive
>
> **Adopted scope:** human activity
>
> **Extracted A:** woman smoking and holding dog
>
> **Extracted B:** no human mentioned
>
> **Recorded reason, verbatim:** The second caption describes no human whose activity can be compared.

**Audit explanation:** B describes a dog in a car. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 024. train_229: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman in a yellow car holds a dachshund in her lap a she smokes a cigarette.
>
> **Caption B:** a dog sitting in the driver's seat of the car like it wants to drive
>
> **Adopted scope:** car color
>
> **Extracted A:** yellow
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second car's color is absent.

**Audit explanation:** B leaves vehicle color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 025. train_236: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** a man sitting on a couch with a silver laptop in a living room
>
> **Caption B:** A computer desk topped with a monitor and a keyboard next to a  mouse.
>
> **Adopted scope:** people count
>
> **Extracted A:** one man
>
> **Extracted B:** no person established
>
> **Recorded reason, verbatim:** A computer desk alone does not establish a person or a supported zero count.

**Audit explanation:** B lists computer equipment. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 026. train_241: `type of Italian dish`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Three plates of Italian food and a glass and bottle of wine on a table.
>
> **Caption B:** A slightly pair of cooked  pizzas sit on a wooden platter on a wooden table.
>
> **Adopted scope:** Italian dish type
>
> **Extracted A:** unspecified Italian food
>
> **Extracted B:** pizza
>
> **Recorded reason, verbatim:** The condition already fixes Italian cuisine and asks the dish type, which the first caption does not identify.

**Audit explanation:** A identifies Italian food. Its specific dish type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 027. train_245: `cleanliness of toilet seat`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A corner of a restroom with a toilet tank and somewhat dirty toilet bowl without a lid.
>
> **Caption B:** A bathroom that has a toilet with a black toilet seat and white brick style walls.
>
> **Adopted scope:** toilet-seat cleanliness
>
> **Extracted A:** dirty bowl; lid absent
>
> **Extracted B:** black seat; cleanliness unspecified
>
> **Recorded reason, verbatim:** A dirty bowl does not establish seat cleanliness, and black is a seat color rather than dirt.

**Audit explanation:** A describes bowl dirt. Seat cleanliness remains unspecified in both captions.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 028. train_303: `name of child`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A kid is running on the beach, pulling along his kite in the sky.
>
> **Caption B:** Young child looks up as a woman flies a kite in front of her.
>
> **Adopted scope:** child proper name
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither child is given a personal name.

**Audit explanation:** Both captions leave the child's name unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 029. train_307: `number of vehicles`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A road sign by the side of the road in the middle of nowhere.
>
> **Caption B:** A red stop sign next to a street with a red car driving over it.
>
> **Adopted scope:** vehicle count
>
> **Extracted A:** no vehicles established
>
> **Extracted B:** one car
>
> **Recorded reason, verbatim:** A road with no stated vehicle does not establish a vehicle count of zero.

**Audit explanation:** A describes a roadside sign. Vehicle presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 030. train_323: `type of seating`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A room with a couch several chairs and a sink and vanity in the corner.
>
> **Caption B:** Bedroom, king sized bed in light brown tone bed cover, small table for writing, probably hotel room.
>
> **Adopted scope:** seating furniture
>
> **Extracted A:** couch and chairs
>
> **Extracted B:** no seating furniture specified
>
> **Recorded reason, verbatim:** A bed and writing table do not establish a chair or other seating furniture in the second.

**Audit explanation:** B lists a bed and writing table. Seating furniture remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 031. train_331: `origin of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A foot long hotdog on a  bun behind held by a hand at a baseball game.
>
> **Caption B:** A hot dog sitting on a bun next to a hamburger and onion rings.
>
> **Adopted scope:** food origin
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption states a geographic or production origin for the actual food.

**Audit explanation:** Both captions leave food origin unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 032. train_353: `action of cutting`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A photograph of sewing supplies including:  scissors, a tape measure, buttons and a needle & thread.
>
> **Caption B:** A pair of scissors sits tucked into a holder on a piece of wood.
>
> **Adopted scope:** cutting action
>
> **Extracted A:** supplies displayed
>
> **Extracted B:** scissors stored
>
> **Recorded reason, verbatim:** Displayed or stored scissors do not establish an ongoing cutting action.

**Audit explanation:** Both captions display or store scissors. A cutting action remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 033. train_356: `length of footgear`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man on skis is being pulled forward by a man on a horse
>
> **Caption B:** A man carries a snowboard in his arms as he walks across the snow.
>
> **Adopted scope:** footgear length
>
> **Extracted A:** skis worn; length unspecified
>
> **Extracted B:** footwear unspecified; snowboard carried
>
> **Recorded reason, verbatim:** The second person carries a board but has no described footgear or footgear length.

**Audit explanation:** Both captions leave footgear length unspecified. B carries the snowboard.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 034. train_363: `number of chairs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A desk holding a laptop with extra keyboard, mouse, speakers, telephone and empty wine glass.
>
> **Caption B:**  A computer monitor, speaker, laptop and a mouse is sitting on wooden table with a raggedy arm chair in front.
>
> **Adopted scope:** chair count
>
> **Extracted A:** no chair established
>
> **Extracted B:** one armchair
>
> **Recorded reason, verbatim:** A desk setup does not establish a chair when none is mentioned.

**Audit explanation:** A lists desk contents. Chair presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 035. train_365: `color of plate`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A plate with a hot dog on a bun, french fries, and other food on a black plate. 
>
> **Caption B:** A hotdog covered in relish and onions sitting next to a container of bean covered fritos.
>
> **Adopted scope:** plate color
>
> **Extracted A:** black
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Only the first plate has a specified color.

**Audit explanation:** B leaves plate color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 036. train_391: `type of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman in a restaurant with pizza with lettuce on top in front of her
>
> **Caption B:** A lady in a blue dress is posing for the camera in front of her plate of food.
>
> **Adopted scope:** food type
>
> **Extracted A:** pizza with lettuce
>
> **Extracted B:** unspecified plated food
>
> **Recorded reason, verbatim:** The second caption names only food without identifying any type, following confirmed #14 and #26.

**Audit explanation:** B identifies generic plated food. Its type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 037. train_409: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Two sheep dogs keep on eye on a couple of sheep during a competition.
>
> **Caption B:** A few people of various ages with their sheep being judged while a crowd of people watch.
>
> **Adopted scope:** people count
>
> **Extracted A:** no people specified
>
> **Extracted B:** people and crowd
>
> **Recorded reason, verbatim:** A competition description without a human mention does not supply a count of people.

**Audit explanation:** A describes sheepdogs and sheep. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 038. train_411: `color of scooter`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An orange and white scooter carrying two passengers drives down a wet street while the passenger of the scooter holds a purple umbrella.
>
> **Caption B:** A row of scooters drive between a row of cars being driven and a row of parked cars.
>
> **Adopted scope:** scooter color
>
> **Extracted A:** orange and white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second scooters have no stated colors.

**Audit explanation:** B leaves scooter colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 039. train_413: `presence of umpire`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A professional baseball player steps into the batter's box in front of a catcher and umpire.
>
> **Caption B:** A man in a white uniform holds a bat with two other men on a baseball field.
>
> **Adopted scope:** umpire presence
>
> **Extracted A:** explicit umpire
>
> **Extracted B:** two other men; roles unspecified
>
> **Recorded reason, verbatim:** The two other men have no specified roles, so umpire presence is not established.

**Audit explanation:** B leaves the additional men's roles unspecified. Umpire presence remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 040. train_417: `number of vehicles`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A camping area with a man next to a barbecue grill and two motorcycles parked on the dirt.
>
> **Caption B:** a red and white tent in the middle of a bare tree filled forest.
>
> **Adopted scope:** vehicle count
>
> **Extracted A:** two motorcycles
>
> **Extracted B:** no vehicles established
>
> **Recorded reason, verbatim:** A tent scene does not establish absence or count of vehicles.

**Audit explanation:** B describes a forest tent. Vehicle presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 041. train_442: `lighting`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bed in a dark room in front of a window with the sun shining in.
>
> **Caption B:** a bedroom with yellow walls, a white bed with a wooden head board next to a window and a small sink.
>
> **Adopted scope:** room lighting
>
> **Extracted A:** dark with sunlight entering
>
> **Extracted B:** window present; illumination unspecified
>
> **Recorded reason, verbatim:** A window's presence does not establish current illumination.

**Audit explanation:** B identifies a window. Room illumination remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 042. train_447: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman smiles while she sits in front of a dish on the table.
>
> **Caption B:** A woman sitting at an outside patio table under a blue umbrella, eating food.
>
> **Adopted scope:** object color
>
> **Extracted A:** unspecified
>
> **Extracted B:** blue umbrella
>
> **Recorded reason, verbatim:** The first caption supplies no object colors.

**Audit explanation:** A leaves its dish and other principal object colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 043. train_463: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black cat sitting on the end of a couch next to shoe covered feet.
>
> **Caption B:** A fat cat laying on the floor with his head laying on someone's foot.
>
> **Adopted scope:** cat color
>
> **Extracted A:** black
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Fat describes build, not coat color.

**Audit explanation:** B leaves cat color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 044. train_467: `number of flowers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A blue bottle, white bird, metal tin, and a photo of a flower arranged on a shelf.
>
> **Caption B:** a table with three different vases on it, one with red and white flowers 
>
> **Adopted scope:** physical flower count
>
> **Extracted A:** flower depicted in a photograph; actual flower not established
>
> **Extracted B:** plural actual flowers in a vase
>
> **Recorded reason, verbatim:** A photograph of a flower is a representation, not an established physical flower in the arrangement.

**Audit explanation:** A establishes a flower photograph. An actual flower in the arrangement remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 045. train_480: `food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A plate of meat with tomatoes, a handful of grapes, and a bowl of cucumbers.
>
> **Caption B:** A white and blue plate sitting on top of a table next to a knife and fork.
>
> **Adopted scope:** food type
>
> **Extracted A:** meat tomatoes grapes cucumbers
>
> **Extracted B:** no food stated
>
> **Recorded reason, verbatim:** A plate and cutlery do not establish food on the second plate.

**Audit explanation:** B lists a plate and utensils. Food presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 046. train_481: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A plate of meat with tomatoes, a handful of grapes, and a bowl of cucumbers.
>
> **Caption B:** A white and blue plate sitting on top of a table next to a knife and fork.
>
> **Adopted scope:** principal plate color
>
> **Extracted A:** unspecified
>
> **Extracted B:** white and blue
>
> **Recorded reason, verbatim:** The first plate color is unstated; food colors cannot substitute for it.

**Audit explanation:** A leaves plate color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 047. train_487: `presence of tomatoes`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** An egg inside a bread end shares a saucer with a fork and three cherry tomatoes.
>
> **Caption B:** A white plate topped with toast and fruit  with an egg and carrots next to strawberries.
>
> **Adopted scope:** tomato presence
>
> **Extracted A:** tomatoes present
>
> **Extracted B:** tomatoes unmentioned
>
> **Recorded reason, verbatim:** An ingredient list without tomatoes does not establish their absence.

**Audit explanation:** B leaves tomato presence unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 048. train_493: `type of side`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A tray holds a hotdog and french fries and there is a cup in the background.
>
> **Caption B:** A close up of a person holding a hot dog in front of the camera.
>
> **Adopted scope:** side dish type
>
> **Extracted A:** fries
>
> **Extracted B:** no side stated
>
> **Recorded reason, verbatim:** The second caption gives no side dish.

**Audit explanation:** B describes a hotdog. An accompanying side dish remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 049. train_499: `color of jacket`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a red jacket is on a snowboard on a series of small hills that are covered with snow.
>
> **Caption B:** A man catches some air and kicks up snow while snowboarding down a snowy slope.
>
> **Adopted scope:** jacket color
>
> **Extracted A:** red
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second jacket has no stated color.

**Audit explanation:** B leaves jacket color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 050. train_505: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** The street sign has on outline of a man with a question mark on it.
>
> **Caption B:** a traffic sign two people walking and a van in front of a large building
>
> **Adopted scope:** actual people count
>
> **Extracted A:** only a depicted man on sign
>
> **Extracted B:** two people walking
>
> **Recorded reason, verbatim:** A person printed on a sign is not an established actual person for the human count.

**Audit explanation:** A establishes a man depicted on a sign. Actual human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 051. train_513: `color of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Four airplanes flying in formation with white smoke coming out of the back of them.
>
> **Caption B:** a red airplane flying in the sky leaving a trail of bright blue smoke behind it.
>
> **Adopted scope:** airplane color
>
> **Extracted A:** unspecified
>
> **Extracted B:** red
>
> **Recorded reason, verbatim:** White describes smoke rather than the first airplanes.

**Audit explanation:** A colors the smoke white. The airplanes' colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 052. train_525: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A bathroom sink, with a bottle of liquid by it and a mirror above it.
>
> **Caption B:** A person taking a picture of a bathroom with a toilet and a bowl sink.
>
> **Adopted scope:** people count
>
> **Extracted A:** no person established
>
> **Extracted B:** one photographer
>
> **Recorded reason, verbatim:** The first room description establishes no person to count.

**Audit explanation:** A lists bathroom fixtures. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 053. train_563: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A red plate topped with a cut in half pizza with an egg on it.
>
> **Caption B:** A piece of pizza with broccoli on it is sitting on a paper plate.
>
> **Adopted scope:** plate color
>
> **Extracted A:** red
>
> **Extracted B:** paper plate; color unspecified
>
> **Recorded reason, verbatim:** Paper specifies material, not the second plate's color.

**Audit explanation:** B identifies a paper plate. Plate color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 054. train_577: `type of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A man sitting with a laptop computer in his lap and feet on his desk.
>
> **Caption B:** A person has their feet up on a desk near a piece of pizza.
>
> **Adopted scope:** food type
>
> **Extracted A:** no food stated
>
> **Extracted B:** pizza
>
> **Recorded reason, verbatim:** The first caption provides no food item.

**Audit explanation:** A describes laptop use. Food presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 055. train_592: `shoes on ground`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A panorama style picture of a bathroom with a pair of shoes on the ground.
>
> **Caption B:** A bathroom with two urinals on the wall next to one another, a sink and a mirror.
>
> **Adopted scope:** shoes on floor
>
> **Extracted A:** present
>
> **Extracted B:** unmentioned
>
> **Recorded reason, verbatim:** The second bathroom does not establish absence of shoes.

**Audit explanation:** B leaves the presence of shoes on the ground unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 056. train_596: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a couple of baseball players talk as another one runs in the back ground
>
> **Caption B:** An umpire stands behind a catcher and a baseball player in a white and red uniform holds a bat.
>
> **Adopted scope:** player uniform color
>
> **Extracted A:** unspecified
>
> **Extracted B:** white and red
>
> **Recorded reason, verbatim:** The first players' uniform colors are unstated.

**Audit explanation:** A leaves uniform and other principal object colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 057. train_605: `color of vegetable`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bowl is filled with crumbs and is on a plate with carrots and other vegetables.
>
> **Caption B:** A close up image of a plate with vegetables and fried food arranged on it.
>
> **Adopted scope:** vegetable colors
>
> **Extracted A:** orange carrots with others unspecified
>
> **Extracted B:** unspecified vegetables
>
> **Recorded reason, verbatim:** The second caption does not identify vegetable colors or varieties that would supply them.

**Audit explanation:** B leaves vegetable colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 058. train_607: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A card table desk with a laptop and metal chair sitting in front of a window.
>
> **Caption B:** Little girl sits in a folding chair, with a bag of m&m's, while looking at something on the laptop
>
> **Adopted scope:** people count
>
> **Extracted A:** no person stated
>
> **Extracted B:** one girl
>
> **Recorded reason, verbatim:** A workstation alone does not establish a person.

**Audit explanation:** A describes a desk setup. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 059. train_611: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The large living room has many pieces of furniture and lit candles in it.
>
> **Caption B:** a red leather sofa and chair in front of a fireplace and a big screen tv
>
> **Adopted scope:** furniture color
>
> **Extracted A:** unspecified
>
> **Extracted B:** red leather
>
> **Recorded reason, verbatim:** The first furniture colors are absent.

**Audit explanation:** A leaves furniture colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 060. train_612: `color of album`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A large training coming down the track with lots of snow on the ground
>
> **Caption B:** Black and white photo of a steam engine riding on the train tracks by a pond.
>
> **Adopted scope:** image color style
>
> **Extracted A:** unspecified
>
> **Extracted B:** black and white
>
> **Recorded reason, verbatim:** Only the second photograph's color style is specified.

**Audit explanation:** A leaves image color style unspecified. B explicitly identifies black-and-white photography.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 061. train_627: `color of plate`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A fork sticking through a chunk of cake on top of a green plate.
>
> **Caption B:** An orange cake with whipped cream frosting sits on a plate beside a book on the table.
>
> **Adopted scope:** plate color
>
> **Extracted A:** green
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second plate has no specified color.

**Audit explanation:** B leaves plate color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 062. train_658: `animals are roaming`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Sheep in a field along with a man, a cow and a farm building
>
> **Caption B:** a number of animals on the side of a mountain with a sky background
>
> **Adopted scope:** animal roaming activity
>
> **Extracted A:** sheep and cow present; motion unspecified
>
> **Extracted B:** animals on mountainside; motion unspecified
>
> **Recorded reason, verbatim:** Animals being present in a field or mountain setting does not establish roaming activity.

**Audit explanation:** Both captions locate animals. Roaming or other movement remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 063. train_659: `type of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Sheep in a field along with a man, a cow and a farm building
>
> **Caption B:** a number of animals on the side of a mountain with a sky background
>
> **Adopted scope:** animal types
>
> **Extracted A:** sheep and cow
>
> **Extracted B:** unspecified animals
>
> **Recorded reason, verbatim:** The second caption supplies only generic animals, without an identifiable animal type.

**Audit explanation:** B identifies generic animals. Their types remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 064. train_685: `gender of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A painting of a black individual with a red umbrella on a concrete wall.
>
> **Caption B:** An image of the city with rain coming down and a woman with an umbrella.
>
> **Adopted scope:** person gender
>
> **Extracted A:** individual unspecified
>
> **Extracted B:** woman
>
> **Recorded reason, verbatim:** The first person's gender is unspecified; race does not supply it.

**Audit explanation:** A's depicted individual has unspecified gender.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 065. train_688: `objects near device`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A big monitor on a white desk with a white mouse and a glass on the desk.
>
> **Caption B:** The computer desk is next to a shelf with speakers and books on it.
>
> **Adopted scope:** items near an established electronic device
>
> **Extracted A:** mouse and glass near monitor
>
> **Extracted B:** speakers and books near computer desk; device not described
>
> **Recorded reason, verbatim:** A computer desk does not establish an actual device in the second scene for the requested near-device relation.

**Audit explanation:** The recorded exclusion treats B's device as missing. B explicitly includes speakers, creating a conflict with the electronic-device scope that requires review.

**Policy check:** Review exclusion policy. **Peer:** `writer_b`.

**Review question:** Should the described speakers count under the recorded electronic-device scope?

**History:** supplied source rating `4.0`.

### 066. train_689: `type of device`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A big monitor on a white desk with a white mouse and a glass on the desk.
>
> **Caption B:** The computer desk is next to a shelf with speakers and books on it.
>
> **Adopted scope:** electronic device type
>
> **Extracted A:** monitor
>
> **Extracted B:** device unspecified; computer desk described
>
> **Recorded reason, verbatim:** The second names a computer desk but does not establish a computer or another target device.

**Audit explanation:** The recorded exclusion treats B's device type as missing. B explicitly identifies speakers, creating an electronic-device scope conflict that requires review.

**Policy check:** Review exclusion policy. **Peer:** `writer_b`.

**Review question:** Which electronic-device type should the described speakers supply?

**History:** supplied source rating `4.0`.

### 067. train_733: `perspective`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A batter that is up at the plate to bat at a baseball game.
>
> **Caption B:** A baseball player is ready to take his best swing in front of the crowd.
>
> **Adopted scope:** camera perspective
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption specifies camera viewpoint.

**Audit explanation:** Both captions leave camera viewpoint unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 068. train_749: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in the ocean wearing a black wet suit, and holding a white and red surf board. 
>
> **Caption B:** A man holding a surfboard near the shore, with  a couple surfers in the background.
>
> **Adopted scope:** clothing color
>
> **Extracted A:** black wetsuit
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Only the first surfer's clothing color is specified.

**Audit explanation:** B leaves clothing colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 069. train_759: `Presence of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** there is a dark photo of a train that is coming up the tracks
>
> **Caption B:** An old time steam engine with a group of people next to it and an old train station.
>
> **Adopted scope:** people presence
>
> **Extracted A:** unmentioned
>
> **Extracted B:** group present
>
> **Recorded reason, verbatim:** A train-only caption does not establish absence of people.

**Audit explanation:** A describes a train. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 070. train_760: `presence of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A side view of the cab and part of the trailer of a tractor trailer truck
>
> **Caption B:** In a car mirror you can see a dog with his head out of the window.
>
> **Adopted scope:** animal presence
>
> **Extracted A:** unmentioned
>
> **Extracted B:** dog present
>
> **Recorded reason, verbatim:** A truck-only description does not establish animal presence or absence.

**Audit explanation:** A describes a truck. Animal presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 071. train_761: `number of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A side view of the cab and part of the trailer of a tractor trailer truck
>
> **Caption B:** In a car mirror you can see a dog with his head out of the window.
>
> **Adopted scope:** animal count
>
> **Extracted A:** unavailable
>
> **Extracted B:** one dog
>
> **Recorded reason, verbatim:** The first scene does not establish an animal count of zero.

**Audit explanation:** A describes a truck. Animal count remains unavailable.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 072. train_773: `material of surfboard`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A surfer watches the waves while sitting on his surf board on the beach.
>
> **Caption B:** A surfer in a wet suit stands next to the water with his board.
>
> **Adopted scope:** surfboard material
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither surfboard has a specified material.

**Audit explanation:** Both captions leave surfboard material unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 073. train_778: `type of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Four teddy bears from font sitting on ledge with patchwork grass of countryside behind them, and blue sky with clouds.
>
> **Caption B:** An old teddy bear left out on the ledge of a little stone wall
>
> **Adopted scope:** represented animal type
>
> **Extracted A:** teddy bears
>
> **Extracted B:** teddy bear
>
> **Recorded reason, verbatim:** The described teddy bears are toys, not actual animals under the frozen animal-scope convention.

**Audit explanation:** The recorded exclusion applies actual-animal eligibility. Both captions identify toy bears under the recorded represented-animal scope. That scope conflict requires review.

**Policy check:** Review exclusion policy. **Peer:** `writer_b`.

**Review question:** Should the condition include the animal represented by the teddy bear?

**History:** supplied source rating `5.0`.

### 074. train_779: `number of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Four teddy bears from font sitting on ledge with patchwork grass of countryside behind them, and blue sky with clouds.
>
> **Caption B:** An old teddy bear left out on the ledge of a little stone wall
>
> **Adopted scope:** bear-figure count
>
> **Extracted A:** four
>
> **Extracted B:** one
>
> **Recorded reason, verbatim:** Toy-bear counts do not establish counts of actual animals for this condition.

**Audit explanation:** The recorded exclusion applies actual-animal eligibility. The recorded bear-figure scope supplies four versus one. That scope conflict requires review.

**Policy check:** Review exclusion policy. **Peer:** `writer_b`.

**Review question:** Should the recorded bear-figure count include teddy bears?

**History:** supplied source rating `1.0`.

### 075. train_795: `perspective of view`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The baseball batter in the maroon helmet and jersey is swinging at a pitch.
>
> **Caption B:** Looking through a chain link fence behind home plate at a baseball game in progress.
>
> **Adopted scope:** viewpoint
>
> **Extracted A:** unspecified
>
> **Extracted B:** behind home plate through fence
>
> **Recorded reason, verbatim:** The first caption does not establish the camera's viewpoint.

**Audit explanation:** A describes a batter. Camera viewpoint remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 076. train_799: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A guy wearing a green hoodie jumping over a fire hydrant on a skateboard.
>
> **Caption B:** Night time with a skateboarder doing a jumping trick in the air while another person is recording him.
>
> **Adopted scope:** clothing color
>
> **Extracted A:** green hoodie
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second skateboarder's clothes have no stated color.

**Audit explanation:** B leaves clothing color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 077. train_807: `type of area within house`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A before and after picture featuring a very messy room and then the same room cleaned up a bit.
>
> **Caption B:** a television desk and bed adjacent to a kitchen with fridge and stove showing
>
> **Adopted scope:** home area type
>
> **Extracted A:** unspecified domestic room
>
> **Extracted B:** combined bedroom/kitchen area
>
> **Recorded reason, verbatim:** A messy room gives no functional room type, following confirmed #50.

**Audit explanation:** A describes changing tidiness. The room's function remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 078. train_818: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person in a brown coat and white pants on a snowboard people in the background skiing and snowboarding.
>
> **Caption B:** A man is skiing on a powdery slope with a blue sky in the background.
>
> **Adopted scope:** clothing color
>
> **Extracted A:** brown and white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Blue describes the sky, not the second skier's clothing.

**Audit explanation:** B leaves clothing colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 079. train_825: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A bedroom with a bed that has a large wooden frame with decorative carvings.
>
> **Caption B:** A woman sticking her head through a window into an old style baby and bed room.
>
> **Adopted scope:** people count
>
> **Extracted A:** none established
>
> **Extracted B:** one woman
>
> **Recorded reason, verbatim:** Bedroom furniture alone does not establish a person count.

**Audit explanation:** A describes a bedroom. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 080. train_827: `color of surface`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** There are plums, cherries, blueberries, tomato, cucumber, fish, lettuce, and carrots in this dish.
>
> **Caption B:** A blue lunch tray filled with a yellow plate with salad and a bowl of dressing.
>
> **Adopted scope:** dish surface color
>
> **Extracted A:** unspecified
>
> **Extracted B:** yellow plate blue tray
>
> **Recorded reason, verbatim:** The first serving surface has no stated color.

**Audit explanation:** A lists food items. The supporting dish's color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 081. train_829: `arrangement of street signs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** a street sign for George st and Jefferson st with a stop sign underneath
>
> **Caption B:** A photo of a street lamp with a street light and a street sign.
>
> **Adopted scope:** sign arrangement
>
> **Extracted A:** stop beneath street names
>
> **Extracted B:** unspecified relation
>
> **Recorded reason, verbatim:** The second sign's position relative to other signs is not supplied.

**Audit explanation:** B identifies a street sign. Its arrangement relative to other signs remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 082. train_834: `number of wheels`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A plane being loaded or unloaded is parked in an empty area with a car in the background.
>
> **Caption B:** A plane is being wash on the runway while another plane sit in a distant.
>
> **Adopted scope:** wheel count
>
> **Extracted A:** plane and car; plane gear unknown
>
> **Extracted B:** two planes; gear unknown
>
> **Recorded reason, verbatim:** Aircraft type and landing-gear wheel counts are not specified sufficiently to derive totals.

**Audit explanation:** Both captions leave aircraft wheel counts unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 083. train_855: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** An airplane parked on the tarmac with the door open and steps attached to the door.
>
> **Caption B:** A kid waits at the top of a ladder going up into an airplane.
>
> **Adopted scope:** people count
>
> **Extracted A:** no person established
>
> **Extracted B:** one child
>
> **Recorded reason, verbatim:** Open aircraft stairs do not establish a person when none is described.

**Audit explanation:** A describes a parked airplane and stairs. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 084. train_871: `presence of human`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** The person is holding a fork and butter knife over a plate of food.
>
> **Caption B:** A plate with pancakes and blueberries with a side of bacon and sliced peaches
>
> **Adopted scope:** human presence
>
> **Extracted A:** person present
>
> **Extracted B:** unmentioned
>
> **Recorded reason, verbatim:** A food-only plate description does not establish a human or supported absence.

**Audit explanation:** B lists breakfast foods. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 085. train_899: `activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A bath and shower is ready for use with a towel and soap left on the side.
>
> **Caption B:** there is a bathroom with white tile floors and a pattern on the walls
>
> **Adopted scope:** ongoing activity
>
> **Extracted A:** bath prepared but unused
>
> **Extracted B:** room description
>
> **Recorded reason, verbatim:** A room being ready for use does not establish an ongoing activity.

**Audit explanation:** Both captions describe bathroom fixtures. Current bathroom activity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 086. train_902: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A brown dog is sitting a rug staring at the person taking the picture
>
> **Caption B:** The dogs coloring makes it look like he is actually a part of the couch.
>
> **Adopted scope:** dog color
>
> **Extracted A:** brown
>
> **Extracted B:** matches unspecified couch color
>
> **Recorded reason, verbatim:** Matching an unspecified couch color supplies no actual coat-color value.

**Audit explanation:** B says the dog matches its couch. Both colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 087. train_905: `type of building`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A blow dryer is sittin on a towel and next to a sock, on a sink.
>
> **Caption B:** A white walled bathroom with six rolls of toilet paper next to a white toilet.
>
> **Adopted scope:** building type
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Bathroom contents do not determine whether the building is residential, commercial or another type.

**Audit explanation:** Both captions leave the containing building's type unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 088. train_913: `number of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A chocolate covered donut and a donut with sugar sprinkled on top sit  on a serving plate.
>
> **Caption B:** The human hand picks up a Krispy Kreme donut right out of the box.
>
> **Adopted scope:** person count
>
> **Extracted A:** no person established
>
> **Extracted B:** one person via hand
>
> **Recorded reason, verbatim:** The first food-only caption establishes no person count.

**Audit explanation:** A describes doughnuts. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 089. train_927: `identity of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Man in T-shirt sitting on one end of a wooden bench, in an urban area.
>
> **Caption B:** An outdoor park area with a bench that has a man laying on his back and sleeping.
>
> **Adopted scope:** person identity
>
> **Extracted A:** unnamed man
>
> **Extracted B:** unnamed man
>
> **Recorded reason, verbatim:** Neither man is identified personally.

**Audit explanation:** Both captions leave the man's personal identity unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 090. train_932: `activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A photo of a flat screen television and a laptop in the living room.
>
> **Caption B:** A person is resting their leg on the coffee table and is watching television.
>
> **Adopted scope:** human activity
>
> **Extracted A:** devices pictured without person
>
> **Extracted B:** watching TV
>
> **Recorded reason, verbatim:** Devices being photographed do not establish a person performing a comparable activity.

**Audit explanation:** A shows electronic devices. Human activity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 091. train_941: `quantity of bread`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A loaf of bread and some meat and vegetables are on a blue plate.
>
> **Caption B:** Carrots, meat and greens sitting in a bowl next to a container of sauce.
>
> **Adopted scope:** bread quantity
>
> **Extracted A:** one loaf
>
> **Extracted B:** bread unmentioned
>
> **Recorded reason, verbatim:** The second food list does not establish a bread amount or supported zero.

**Audit explanation:** B lists meat and vegetables. Bread presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 092. train_951: `color of organic object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A vase with leaves sticking out of it and it has rocks in it
>
> **Caption B:** Black Mediterranean vase with brown vines, in from on wall with earth style art work.
>
> **Adopted scope:** plant color
>
> **Extracted A:** leaves color unstated
>
> **Extracted B:** brown vines
>
> **Recorded reason, verbatim:** Leaves need not be green, and their color is not described in the first.

**Audit explanation:** A identifies leaves. Their color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 093. train_953: `color of Frisbee`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A partial view of a man showing his leg and arm only holding on to a yellow Frisbee.
>
> **Caption B:** A man in the air with his hands together as a Frisbee is flying toward him.
>
> **Adopted scope:** disc color
>
> **Extracted A:** yellow
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second disc's color is unstated.

**Audit explanation:** B leaves Frisbee color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 094. train_960: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog laying in a grey chair with a ottoman with three remote controls in front.
>
> **Caption B:** A brown and white dog sitting on a couch with a partially concealed man.
>
> **Adopted scope:** dog color
>
> **Extracted A:** unspecified
>
> **Extracted B:** brown and white
>
> **Recorded reason, verbatim:** Grey describes the chair rather than the first dog's coat.

**Audit explanation:** A colors the chair grey. Dog color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 095. train_982: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A pan of food on the burner of a stove being whipped with an electric mixer.
>
> **Caption B:** A table with a green mix in the bowl and a scale on the table
>
> **Adopted scope:** food mixture color
>
> **Extracted A:** unspecified
>
> **Extracted B:** green
>
> **Recorded reason, verbatim:** The first food mixture has no stated color.

**Audit explanation:** A leaves its food mixture and principal object colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 096. train_983: `type of dish`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A pan of food on the burner of a stove being whipped with an electric mixer.
>
> **Caption B:** A table with a green mix in the bowl and a scale on the table
>
> **Adopted scope:** prepared dish type
>
> **Extracted A:** unspecified food mixture
>
> **Extracted B:** unspecified green mix
>
> **Recorded reason, verbatim:** Both are unnamed mixtures; color and preparation equipment do not identify a dish type, following the confirmed generic-food boundary.

**Audit explanation:** Both captions identify unnamed mixtures. Food-dish types remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 097. train_1009: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bedroom with a bed that has a stripped pink, green and white comforter. 
>
> **Caption B:** Bunk beds in a bedroom with a bag on top of the bottom bunk.
>
> **Adopted scope:** bedding color
>
> **Extracted A:** pink green white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second bedding has no supplied color.

**Audit explanation:** B leaves bed and bedding colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 098. train_1014: `Presence of shoes on floor`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A kitchen in a home with a large number of shoes on the floor.
>
> **Caption B:** A view of a living room with a view of the kitchen as well.
>
> **Adopted scope:** floor-shoe presence
>
> **Extracted A:** present
>
> **Extracted B:** unmentioned
>
> **Recorded reason, verbatim:** A view of rooms does not establish shoes absent.

**Audit explanation:** B leaves the presence of shoes on the floor unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 099. train_1016: `type of dish`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A table that have  a plates of food , silverware , and two glasses filled with tea and a jar filled with flowers.
>
> **Caption B:** A doughnut on a plate beside a cup of coffee in front of a potted plant and plush lamb on a table cloth.
>
> **Adopted scope:** food dish
>
> **Extracted A:** unspecified plated food
>
> **Extracted B:** doughnut
>
> **Recorded reason, verbatim:** Unidentified plated food supplies no food-dish type under the user's confirmed boundary.

**Audit explanation:** A identifies generic plated food. Its dish type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 100. train_1020: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a desk with a red chair a phone a keyboard books and a laptop
>
> **Caption B:** A home office with two computers sits by a window with a view of trees.
>
> **Adopted scope:** furniture color
>
> **Extracted A:** red chair
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second office furniture has no comparable color information.

**Audit explanation:** B leaves office-object colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 101. train_1022: `activity of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Double Decker red bus on street, British driving side with buildings of European design.
>
> **Caption B:** A group of red buses driving down  a street next to a person crossing it.
>
> **Adopted scope:** human activity
>
> **Extracted A:** no human described
>
> **Extracted B:** person crossing street
>
> **Recorded reason, verbatim:** A bus scene does not establish a described person's activity.

**Audit explanation:** A describes a bus and buildings. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 102. train_1029: `point of reference for baseball swing`

**Current status:** `excluded_scope`. **Semantic rating:** `excluded/null`. **Policy:** `S7`.

> **Caption A:** Two frames at a professional baseball game showing a swing for a pitched ball.
>
> **Caption B:** A man getting ready to swing at a fast ball and a catcher waiting to catch the ball
>
> **Adopted scope:** unresolved meaning of point of reference
>
> **Extracted A:** swing in progress
>
> **Extracted B:** preparing to swing
>
> **Recorded reason, verbatim:** The condition does not identify whether point of reference refers to action phase or to viewpoint. The first is a swing versus preparation comparison; camera viewpoint is unavailable. A shared sport does not choose the requested feature.

**Audit explanation:** Swing phase yields active swing versus preparation. Camera reference yields unavailable viewpoints. The condition leaves the intended feature unresolved.

**Recorded scope readings:**

> - **swing phase:** rating 2. A: swing in progress. B: preparing to swing.
> - **camera viewpoint:** invalid. A: viewpoint unstated. B: viewpoint unstated.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 103. train_1035: `name of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young man wearing blue jeans hovers on his skateboard in the air over a red blockade.
>
> **Caption B:** A skateboarder hangs in the air above a board that is spinning beneath him.
>
> **Adopted scope:** person name
>
> **Extracted A:** unnamed
>
> **Extracted B:** unnamed
>
> **Recorded reason, verbatim:** Neither caption supplies a personal name.

**Audit explanation:** Both captions leave the skateboarder's name unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 104. train_1051: `number of men standing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** vintage image of two men standing near a plan and a cart on a tarmac
>
> **Caption B:** An airplane in the middle of a field with some jeeps parked near it
>
> **Adopted scope:** men count
>
> **Extracted A:** two
>
> **Extracted B:** no men described
>
> **Recorded reason, verbatim:** The second caption establishes no men or explicit zero people.

**Audit explanation:** B describes aircraft and jeeps. Standing men remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 105. train_1072: `activity of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** We are looking at the head of a horse with cliffs in the background.
>
> **Caption B:** A pair of horses are stand near each other, one is brown and one is black.
>
> **Adopted scope:** horse activity
>
> **Extracted A:** head shown without action
>
> **Extracted B:** standing
>
> **Recorded reason, verbatim:** Showing a horse's head does not identify its activity.

**Audit explanation:** A shows the horse's head. Its activity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 106. train_1079: `type of water`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** This is a person in a boat by himself in a lake by a tree.
>
> **Caption B:** A lone boaters glide on top of the water with hills and valleys behind  the water.
>
> **Adopted scope:** waterbody type
>
> **Extracted A:** lake
>
> **Extracted B:** water, body type unspecified
>
> **Recorded reason, verbatim:** Hills and valleys behind water do not identify the second waterbody type.

**Audit explanation:** B identifies water. Its waterbody type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 107. train_1101: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A small passenger airplane with it's landing gear extended and parked on the ground.
>
> **Caption B:** This is a plane on the tarmac with a ladder leading up to the door and people walking around it.
>
> **Adopted scope:** people count
>
> **Extracted A:** unavailable
>
> **Extracted B:** plural people
>
> **Recorded reason, verbatim:** A parked aircraft alone establishes no people count.

**Audit explanation:** A describes a parked airplane. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 108. train_1108: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A pair of pants lay on a table at the foot of a bed.
>
> **Caption B:** a bed with a black and white pillow and two lights and a chair
>
> **Adopted scope:** object color
>
> **Extracted A:** unspecified
>
> **Extracted B:** black-white pillow
>
> **Recorded reason, verbatim:** No first-caption object color is supplied.

**Audit explanation:** A leaves pants, table, and bed colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 109. train_1139: `type of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** The bicyclist is sitting on the back of the decorative bench to check her phone.
>
> **Caption B:** A barefoot woman sits on a bench using her cell phone on a sunny day.
>
> **Adopted scope:** vehicle type
>
> **Extracted A:** bicycle implied by bicyclist
>
> **Extracted B:** no vehicle established
>
> **Recorded reason, verbatim:** The second woman has no vehicle established.

**Audit explanation:** B describes phone use. Vehicle presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 110. train_1141: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A stop light that is flashing green in front of a group of people.
>
> **Caption B:** A traffic light with a red light and an arrow pointing to the right.
>
> **Adopted scope:** people count
>
> **Extracted A:** group
>
> **Extracted B:** no people established
>
> **Recorded reason, verbatim:** No people are established in the second signal-only description.

**Audit explanation:** B describes a traffic light. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 111. train_1156: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a lady bending over a rail looking at a white sheep and a black sheep
>
> **Caption B:** Two lambs are shown in their habitat while a woman caresses a lamb's head.
>
> **Adopted scope:** animal color
>
> **Extracted A:** white and black
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Lambs' coats have no colors supplied.

**Audit explanation:** B leaves lamb colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 112. train_1169: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cowboy secures a saddlebag on the side of a white and brown horse.
>
> **Caption B:** In front of a metal half-cylindrical structure and red metal fence, a woman leads a horse on foot.
>
> **Adopted scope:** horse color
>
> **Extracted A:** white and brown
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second horse's color is missing.

**Audit explanation:** B colors nearby structures. Horse color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 113. train_1180: `name of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** The painting shows zebras of adult and young zebras in the field of tall grass.
>
> **Caption B:** some zebras standing together, with one looking in a different direction than the others 
>
> **Adopted scope:** actual animal type
>
> **Extracted A:** painted zebras
>
> **Extracted B:** real zebras
>
> **Recorded reason, verbatim:** Painted zebras do not establish actual animals under the literal-animal convention.

**Audit explanation:** A establishes painted zebras. Actual animals remain unestablished under the adopted literal-animal scope.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `5.0`.

### 114. train_1181: `behavior of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** The painting shows zebras of adult and young zebras in the field of tall grass.
>
> **Caption B:** some zebras standing together, with one looking in a different direction than the others 
>
> **Adopted scope:** actual animal behavior
>
> **Extracted A:** painted zebras
>
> **Extracted B:** standing and looking
>
> **Recorded reason, verbatim:** The first contains represented animals rather than an actual animal action.

**Audit explanation:** A establishes painted zebras. Actual animal behavior remains unavailable under the adopted literal-animal scope.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 115. train_1184: `name of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a man on a skateboard doing a trick in the air at an indoor skate park
>
> **Caption B:** A young man is in the middle of trying to pull off a successful skateboarding trick.
>
> **Adopted scope:** place type
>
> **Extracted A:** indoor skatepark
>
> **Extracted B:** site unspecified
>
> **Recorded reason, verbatim:** An unspecified skateboard trick does not identify its venue.

**Audit explanation:** B describes a skateboard trick. Its location remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 116. train_1187: `ski poles`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A young boy is holding a pair of ski poles while standing on a pair of skis.
>
> **Caption B:** A boy dressed in cold weather gear rides a skate board on a path.
>
> **Adopted scope:** ski-pole presence/type
>
> **Extracted A:** ski poles present
>
> **Extracted B:** skateboarding without poles mentioned
>
> **Recorded reason, verbatim:** The second skateboard scene establishes no ski poles.

**Audit explanation:** B describes skateboarding. Ski-pole presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 117. train_1191: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman in glasses wears a white t-shirt and a black puppy lays on a white blanket.
>
> **Caption B:** A women is laying with pillows around her head as a little dog peeks its head out from underneath.
>
> **Adopted scope:** dog color
>
> **Extracted A:** black
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second dog's color is missing.

**Audit explanation:** B leaves dog color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 118. train_1203: `number of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Blue two story double deck bus traveling down a road with another bus in view.
>
> **Caption B:** a man at a bus stop is waiting to get on to the bus
>
> **Adopted scope:** person count
>
> **Extracted A:** no people established
>
> **Extracted B:** one man
>
> **Recorded reason, verbatim:** Buses alone do not establish a described person count.

**Audit explanation:** A describes buses. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 119. train_1211: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A dirt ground area with trees and bushes surrounding two small elephants and three men.
>
> **Caption B:** Two elephants are in front of a muddy waterway trampling in the wet dirt.
>
> **Adopted scope:** people count
>
> **Extracted A:** three men
>
> **Extracted B:** no people established
>
> **Recorded reason, verbatim:** The second elephants' scene has no people established.

**Audit explanation:** B describes elephants. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 120. train_1217: `proximity of device`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A keyboard and mouse that appears to be hooked up to an external usb device.
>
> **Caption B:** A keyboard seen from the left side with the right edge too far away to be seen.
>
> **Adopted scope:** camera-device proximity
>
> **Extracted A:** unspecified
>
> **Extracted B:** close left-side view
>
> **Recorded reason, verbatim:** The first keyboard has no camera-distance information.

**Audit explanation:** A leaves camera-to-keyboard distance unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 121. train_1245: `color of items`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Three gourmet pizzas sitting on a table in front of a person wearing a gray T-shirt with the word, "Purdue" on it.
>
> **Caption B:** A pizza sits on a white plate while a pizza cutter sits on top of it.
>
> **Adopted scope:** comparable food-vessel color
>
> **Extracted A:** unspecified
>
> **Extracted B:** white plate
>
> **Recorded reason, verbatim:** The gray shirt and white plate color different incidental items; comparable pizza or vessel colors are not supplied in both.

**Audit explanation:** A colors a person's shirt. Comparable food-vessel colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 122. train_1253: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A Sumo wrestler's upper body is sticking out of the wall and holding a sink in a bathroom.
>
> **Caption B:** A bathroom with a glass shower enclosure and a large bathtub beneath two windows.
>
> **Adopted scope:** actual people count
>
> **Extracted A:** sumo-shaped fixture representation
>
> **Extracted B:** no person established
>
> **Recorded reason, verbatim:** The second bathroom establishes no person, and the first describes a wrestler-shaped fixture rather than a comparable actual occupant.

**Audit explanation:** B describes bathroom fixtures. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 123. train_1261: `type of decoration`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A city walkway area with people standing and sitting near a street post and buildings around the area.
>
> **Caption B:** A clock sticking out off the side of a building on a city street.
>
> **Adopted scope:** decoration type
>
> **Extracted A:** no decoration specified
>
> **Extracted B:** building clock
>
> **Recorded reason, verbatim:** No decoration is identified in the walkway scene.

**Audit explanation:** A identifies street structures. A decorative object remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 124. train_1271: `motion of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A black dog wearing a Santa hat in a room with gift wrappings on the floor.
>
> **Caption B:** A dog lying on a rug under a wooden table turns to look at the camera.
>
> **Adopted scope:** dog motion
>
> **Extracted A:** wearing hat; motion unspecified
>
> **Extracted B:** turning head while lying
>
> **Recorded reason, verbatim:** Wearing a hat does not establish the first dog's motion; the second explicitly turns its head.

**Audit explanation:** A describes the dog's hat. Dog motion remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 125. train_1277: `color of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A mostly black, white and grey bedroom save for two bright red pillows on a bed
>
> **Caption B:** Small computer monitor sitting in front of a bed and window in a bedroom.
>
> **Adopted scope:** room colors
>
> **Extracted A:** black white grey red
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second bedroom has no stated color palette.

**Audit explanation:** B leaves bedroom colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 126. train_1287: `identity of persons`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Three skiers smiling for the camera while standing in their skis on packed snow.
>
> **Caption B:** A group of men standing next to each other on a snow covered slope.
>
> **Adopted scope:** people identities
>
> **Extracted A:** unnamed skiers
>
> **Extracted B:** unnamed men
>
> **Recorded reason, verbatim:** Neither group has identifying personal names or identities beyond generic participant descriptions.

**Audit explanation:** Both captions leave personal identities unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 127. train_1297: `activity of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A giraffe standing next to a man holding a stick with a ball on it.
>
> **Caption B:** Two giraffes are in the foreground and there is a zebra in the background.
>
> **Adopted scope:** animal activity
>
> **Extracted A:** standing
>
> **Extracted B:** positions only; activity unspecified
>
> **Recorded reason, verbatim:** The second caption supplies animal positions but no recoverable activity.

**Audit explanation:** B locates giraffes in the foreground. Their activity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 128. train_1321: `Animals near water`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a number of animals near a shallow body of water with trees in the background
>
> **Caption B:** Two adult elephants and a younger one are crossing a small spot of water.
>
> **Adopted scope:** type of animals near water
>
> **Extracted A:** unspecified animals
>
> **Extracted B:** elephants
>
> **Recorded reason, verbatim:** Generic animals provides no animal category to compare with elephants; waterside location does not supply the missing type.

**Audit explanation:** A identifies generic animals. Their types remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 129. train_1324: `people's sentiment`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man with a kite next to a bunch of other people flying kites.
>
> **Caption B:** A man throwing a frisbee at a father walking along with his two children.
>
> **Adopted scope:** people emotion
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Kite flying and Frisbee throwing do not establish either group's feelings.

**Audit explanation:** Both captions leave the people's sentiments unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 130. train_1334: `type of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A stuffed animal is placed at the top of a steering wheel in a car.
>
> **Caption B:** A rearview mirror view of a dog holding it's head out a car window.
>
> **Adopted scope:** actual animal type
>
> **Extracted A:** stuffed toy
>
> **Extracted B:** dog
>
> **Recorded reason, verbatim:** The first entity is a stuffed toy, so a comparable actual animal is absent.

**Audit explanation:** A establishes a stuffed toy. An actual animal remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 131. train_1352: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Brown cow is looking toward the camera while the other two cow are eating grass.
>
> **Caption B:** Three cows standing together in a field, one is starting directly at the camera.
>
> **Adopted scope:** cow color
>
> **Extracted A:** brown principal cow
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second caption supplies no cow color.

**Audit explanation:** B leaves cow color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 132. train_1359: `presence of shelves`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Pictures of a refrigerator, a microwave oven, a washing machine and a robot vacuum.
>
> **Caption B:** A washer and drying sitting between a set of drawers and beneath some shelves filled with bottles.
>
> **Adopted scope:** shelf presence
>
> **Extracted A:** unmentioned
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** Shelves are unmentioned in the appliance pictures, so their absence cannot be assumed.

**Audit explanation:** A lists appliance pictures. Shelf presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 133. train_1376: `contents of dish`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The person is holding a fork and butter knife over a plate of food.
>
> **Caption B:** A table has two cups and three plates and the plates hold eggs, sausage and some bread.
>
> **Adopted scope:** dish contents
>
> **Extracted A:** unspecified food
>
> **Extracted B:** eggs sausage bread
>
> **Recorded reason, verbatim:** Generic food supplies no dish-content identities, following confirmed #14 and #26.

**Audit explanation:** A identifies generic food. Dish contents remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 134. train_1387: `background of objects`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A sign that has arrows pointing in opposite directions, one of the arrows has a dog sticker on it.
>
> **Caption B:** A close up of a stop sign, with autumn leaves changing in the background.
>
> **Adopted scope:** sign background
>
> **Extracted A:** unspecified
>
> **Extracted B:** autumn leaves
>
> **Recorded reason, verbatim:** The first sign's background is not described.

**Audit explanation:** A describes a sign. Its background remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 135. train_1395: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a cow stands in front of tall stacks of hay on a grassy field
>
> **Caption B:** Brown cow is looking toward the camera while the other two cow are eating grass.
>
> **Adopted scope:** cow color
>
> **Extracted A:** unspecified
>
> **Extracted B:** brown principal cow
>
> **Recorded reason, verbatim:** The first cow has no color description.

**Audit explanation:** A leaves cow color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 136. train_1396: `food items`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Looking down on a table with two people sitting at the table having cake and hot beverages.
>
> **Caption B:** A dinner table is decorated with white cups, plates and a vase with flowers in it.
>
> **Adopted scope:** food items
>
> **Extracted A:** cake and hot beverages
>
> **Extracted B:** dishware flowers; food unstated
>
> **Recorded reason, verbatim:** The second table describes dishware and flowers without an identified food item.

**Audit explanation:** B lists cups, plates, and flowers. Food presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 137. train_1407: `type of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person sitting on the end of a bench with a passenger train pulled up to the platform.
>
> **Caption B:** A lone young girl sits on a park bench watching boats in the harbor.
>
> **Adopted scope:** person category
>
> **Extracted A:** unspecified person
>
> **Extracted B:** young girl
>
> **Recorded reason, verbatim:** The first caption gives only person, with no person subtype or role beyond sitting; young girl is a more specific category only in the second.

**Audit explanation:** A's generic person leaves age, gender, and person category unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 138. train_1419: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A persons feet up and resting on a chair next to a black cat.
>
> **Caption B:** Woman's foot wearing shoe with cat face on it next to an actual cat
>
> **Adopted scope:** cat color
>
> **Extracted A:** black
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The actual cat's color is unmentioned in the second caption.

**Audit explanation:** B leaves actual cat color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 139. train_1423: `color of toilet`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white toilet sitting in front of a picture of a tall building on display.
>
> **Caption B:** Small toilet in a tiny room next to a plunger and a waste basket.
>
> **Adopted scope:** toilet color
>
> **Extracted A:** white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Small size does not identify the second toilet's color.

**Audit explanation:** B leaves toilet color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 140. train_1424: `sentiment of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A wedding couple standing by their cake, looking at bicycle decorations on the perimeter.
>
> **Caption B:** A man and a woman cutting a cake with a knife as a boy looks on.
>
> **Adopted scope:** people sentiment
>
> **Extracted A:** wedding context without explicit emotion
>
> **Extracted B:** cutting cake without emotion
>
> **Recorded reason, verbatim:** Wedding context and cake cutting provide actions, without stated or strongly implied emotion.

**Audit explanation:** Both captions describe wedding or cake activities. The people's sentiments remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 141. train_1431: `type of variation`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A sandwich consisting of crusty bread, greens, ham, and pickles, on a plate with french fries.
>
> **Caption B:** A sandwich is sitting on a paper with a bite taken out of it.
>
> **Adopted scope:** sandwich recipe variation
>
> **Extracted A:** ham greens pickles on crusty bread
>
> **Extracted B:** recipe variation unspecified
>
> **Recorded reason, verbatim:** The second sandwich has a bite but no ingredient or recipe variation, so its sandwich subtype cannot be compared with the specified ham-and-pickle version.

**Audit explanation:** B identifies a bitten sandwich. Its ingredients and recipe variation remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 142. train_1435: `presence of chain link fence`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A boy playing tennis on a hard surface tennis court with a chain link fence behind him.
>
> **Caption B:** A tennis player hits a tennis ball with a racket on an outdoor tennis court.
>
> **Adopted scope:** fence presence
>
> **Extracted A:** chain-link present
>
> **Extracted B:** unmentioned
>
> **Recorded reason, verbatim:** An outdoor tennis court does not establish a chain-link fence when none is mentioned.

**Audit explanation:** B leaves chain-link fence presence unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 143. train_1437: `gender`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person in a purple coat at the top of a ski slope and a ski lift on the side.
>
> **Caption B:** A downhill skier skis down the mountain with ski lifts running in the background.
>
> **Adopted scope:** person gender
>
> **Extracted A:** person unspecified
>
> **Extracted B:** skier unspecified
>
> **Recorded reason, verbatim:** Neither person nor skier supplies gender.

**Audit explanation:** Both captions leave the person's gender unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 144. train_1445: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cat laying on his back is looking at the camera through a magnifying glass.
>
> **Caption B:** A white cat with brown and black accents lay on a wood table with her head close to a computer mouse.
>
> **Adopted scope:** cat color
>
> **Extracted A:** unspecified
>
> **Extracted B:** white brown black
>
> **Recorded reason, verbatim:** The first cat has no stated coat color.

**Audit explanation:** A leaves cat color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 145. train_1459: `gender of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A skier stands at the top of a slope with white mountains in the background.
>
> **Caption B:** a man standing near the top of a snowy mountain on a somewhat cloudy day
>
> **Adopted scope:** person gender
>
> **Extracted A:** skier unspecified
>
> **Extracted B:** man
>
> **Recorded reason, verbatim:** The first skier's gender is unspecified.

**Audit explanation:** A identifies a skier. Gender remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 146. train_1471: `location of table`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a table with a cloth on it has a meal and drinks on it
>
> **Caption B:** Three tiers of plates with different sandwiches on it, on a table in a restaurant.
>
> **Adopted scope:** table location
>
> **Extracted A:** unspecified
>
> **Extracted B:** restaurant
>
> **Recorded reason, verbatim:** A cloth and meal do not establish where the first table is located.

**Audit explanation:** A describes tabletop contents. The table's location remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 147. train_1473: `meaning of sign`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The street sign has on outline of a man with a question mark on it.
>
> **Caption B:** a road sign that shows no animal,a motor bike or a car should pass
>
> **Adopted scope:** sign meaning
>
> **Extracted A:** person with question mark; meaning unclear
>
> **Extracted B:** no passage for listed entities
>
> **Recorded reason, verbatim:** The first sign's question-mark graphic does not establish a definite instruction or meaning.

**Audit explanation:** A's person outline and question mark leave the sign's meaning unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 148. train_1496: `color of product`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bed, with folded bedding, in a room with a sliding door and a deck.
>
> **Caption B:** A white bed sitting inside of a room next to a light on the wall.
>
> **Adopted scope:** bed color
>
> **Extracted A:** unspecified
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** The first bed has no color description.

**Audit explanation:** A leaves bed color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 149. train_1511: `objects with chocolate`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Two plain chocolate covered donuts, two white powdered covered donuts and two peanut covered chocolate donuts.
>
> **Caption B:** The two plates each have cakes, pastries, and a bowl of fruit on them. 
>
> **Adopted scope:** chocolate-bearing food
>
> **Extracted A:** four chocolate donuts
>
> **Extracted B:** chocolate unmentioned
>
> **Recorded reason, verbatim:** The second cakes and pastries have no stated chocolate, so chocolate-bearing food cannot be identified.

**Audit explanation:** B identifies cakes and pastries. Chocolate-coated items remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 150. train_1518: `color of apron`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman with a red apron, standing in the kitchen and using a grater.
>
> **Caption B:** This is a picture of two women cooking a meal. One is pulling something out of the oven.
>
> **Adopted scope:** apron color
>
> **Extracted A:** red
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second cooking scene never identifies an apron or its color.

**Audit explanation:** B leaves apron color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 151. train_1541: `age of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black horse and a white horse look at the camera in a field.
>
> **Caption B:** A baby horse stands next to it's mother as she grazes on some grass.
>
> **Adopted scope:** horse ages
>
> **Extracted A:** unspecified
>
> **Extracted B:** foal and mother
>
> **Recorded reason, verbatim:** The first horses' coat colors do not reveal ages.

**Audit explanation:** A leaves both horses' ages unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 152. train_1543: `vehicle with brake lights`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A snow covered area with a car with it's brake lights on in the distance.
>
> **Caption B:** A snowy field with a yellow fire hydrant with the number six on it, and frozen over trees and shrubs.
>
> **Adopted scope:** vehicle with brake lights
>
> **Extracted A:** car present
>
> **Extracted B:** no vehicle established
>
> **Recorded reason, verbatim:** The second caption describes no vehicle with brake lights.

**Audit explanation:** B describes snow, trees, and a hydrant. A vehicle with brake lights remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 153. train_1546: `type of object with clock`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** a tall pole with a clock on the top saying its 5 o clock
>
> **Caption B:** The tree has been decorated with ornaments has a large clock in the background.
>
> **Adopted scope:** clock support object
>
> **Extracted A:** pole
>
> **Extracted B:** clock support unspecified
>
> **Recorded reason, verbatim:** The second clock's supporting object is not identified; a nearby decorated tree is not stated to hold it.

**Audit explanation:** B places a clock in the background. Its supporting object remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 154. train_1557: `number of bottles`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** View of a kitchen with a stove with a shelf off bottles above and lights under the upper cabinets.
>
> **Caption B:** A stainless steel range with a floral kitchen towel hanging from the oven door.
>
> **Adopted scope:** bottle count
>
> **Extracted A:** plural bottles
>
> **Extracted B:** no bottles stated
>
> **Recorded reason, verbatim:** The second stove scene supplies no bottle count or supported absence.

**Audit explanation:** B describes a range and towel. Bottle presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 155. train_1568: `presence of birds`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Surfers in the waves in the background, and birds in the foreground on the beach.
>
> **Caption B:** Two men are walking away from the water on a beach and are carrying surfboards.
>
> **Adopted scope:** bird presence
>
> **Extracted A:** present
>
> **Extracted B:** unmentioned
>
> **Recorded reason, verbatim:** No bird is mentioned in the second beach scene, which does not establish absence.

**Audit explanation:** B describes surfers. Bird presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 156. train_1576: `number of beds`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A hospital room with a large clock mounted on a wall next to medical equipment.
>
> **Caption B:** A woman in bule scrubs stands next to a patient lying in a bed.
>
> **Adopted scope:** bed count
>
> **Extracted A:** none specified
>
> **Extracted B:** one occupied bed
>
> **Recorded reason, verbatim:** A hospital room does not fix its number of beds when no bed is stated.

**Audit explanation:** A's hospital room description leaves bed count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 157. train_1578: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A old photo showing a pitch being thrown and a hitter at the ready.
>
> **Caption B:** A baseball player in a blue and white striped uniform holds his bat with his knees bent.
>
> **Adopted scope:** uniform color
>
> **Extracted A:** unspecified
>
> **Extracted B:** blue and white
>
> **Recorded reason, verbatim:** The first uniform or other comparable object's color is not described.

**Audit explanation:** A leaves uniform and principal object colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 158. train_1584: `cleanliness of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A pristine living area with a couch, chair, coffee table, fireplace and white rug, with dark wood floors.
>
> **Caption B:** A picture of a great room that included a kitchen, dining room and living area.
>
> **Adopted scope:** room cleanliness
>
> **Extracted A:** pristine
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second room's combined functions do not establish cleanliness.

**Audit explanation:** B identifies room functions. Cleanliness remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 159. train_1585: `size of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A pristine living area with a couch, chair, coffee table, fireplace and white rug, with dark wood floors.
>
> **Caption B:** A picture of a great room that included a kitchen, dining room and living area.
>
> **Adopted scope:** room size
>
> **Extracted A:** unspecified
>
> **Extracted B:** large combined great room
>
> **Recorded reason, verbatim:** The first living area's furniture and pristine condition do not establish its size.

**Audit explanation:** A's furniture inventory leaves room size unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 160. train_1623: `power source`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A toaster oven with two levels of trays inside and a glass window door on the front.
>
> **Caption B:** An oven that is slightly opened revealing that some food is baking in it.
>
> **Adopted scope:** power source
>
> **Extracted A:** toaster oven electric inferred
>
> **Extracted B:** oven source unspecified
>
> **Recorded reason, verbatim:** The ordinary oven could use gas or electricity; its source is unreported.

**Audit explanation:** B identifies an oven. Its power source remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 161. train_1626: `actions`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** An exotic pizza sits on a plate, with cheese and bits of meat on top.
>
> **Caption B:** A hand holds a slice of pizza near a pan with the pizza on it.
>
> **Adopted scope:** food-related action
>
> **Extracted A:** no agent action stated
>
> **Extracted B:** holding a pizza slice
>
> **Recorded reason, verbatim:** A pizza resting on a plate supplies no food-related agent action, while the second explicitly has a hand holding a slice.

**Audit explanation:** A describes a plated pizza. An agent's action remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 162. train_1641: `color of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The cars and trucks are headed down the one way street with a view of the scenic valley and mountain range.
>
> **Caption B:** Many vehicles are waiting for their green light, while the left lane has an arrow. 
>
> **Adopted scope:** vehicle colors
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither caption provides vehicle colors; the green traffic light is not a vehicle color.

**Audit explanation:** Both captions leave vehicle colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 163. train_1643: `location of toilet`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** It's one of the toilets that you can either warm up or cool down.
>
> **Caption B:** A toilet with the seat up next to a trash pail filled with paper.
>
> **Adopted scope:** toilet location
>
> **Extracted A:** unspecified
>
> **Extracted B:** beside wastebasket
>
> **Recorded reason, verbatim:** Heating or cooling the toilet seat does not establish the first toilet's location.

**Audit explanation:** A describes temperature controls. Toilet location remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 164. train_1661: `brightness of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person placing their hand on the bottom of the bed in a dark room.
>
> **Caption B:** A black and white photo of a person resting with feet on the coffee table watching a flat screen tv.
>
> **Adopted scope:** room brightness
>
> **Extracted A:** dark
>
> **Extracted B:** black-white image; illumination unspecified
>
> **Recorded reason, verbatim:** A black-and-white photograph does not establish the second room's brightness.

**Audit explanation:** B specifies monochrome photography. Room brightness remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 165. train_1665: `light source`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A empty dorm room with a lamp and set of curtains up on the window
>
> **Caption B:** A bed has a white cover and a desk has a laptop in a tidy room.
>
> **Adopted scope:** lighting source
>
> **Extracted A:** lamp and window
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** No lighting source is given in the second room.

**Audit explanation:** B lists bedroom furnishings. A light source remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 166. train_1669: `color of objects`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** View into a living room with a cathedral ceiling and a wood storage unit.
>
> **Caption B:** A white room with a fireplace, television, chair, and couch arranged around a table.
>
> **Adopted scope:** room-object colors
>
> **Extracted A:** unspecified wood storage
>
> **Extracted B:** white room
>
> **Recorded reason, verbatim:** The first storage unit's material does not specify its color.

**Audit explanation:** A supplies storage-unit material. Object colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 167. train_1670: `name of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** There is a full point of view of a room in a well lit zone. 
> 
>
> **Caption B:** A small bathroom with a white toilet, a makeup mirror, and a picture on the wall.
>
> **Adopted scope:** place type
>
> **Extracted A:** indoor room
>
> **Extracted B:** bathroom
>
> **Recorded reason, verbatim:** A well-lit room does not establish functional place type, following confirmed #50.

**Audit explanation:** A identifies a room. Its function and place type remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 168. train_1671: `location of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** There is a full point of view of a room in a well lit zone. 
> 
>
> **Caption B:** A small bathroom with a white toilet, a makeup mirror, and a picture on the wall.
>
> **Adopted scope:** object location
>
> **Extracted A:** no object identified
>
> **Extracted B:** toilet mirror picture positions
>
> **Recorded reason, verbatim:** The first sentence identifies a room but no comparable object whose location can be extracted.

**Audit explanation:** A identifies a room. The object to be located remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 169. train_1688: `presence of bread`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A sandwich on a plate next to a banana and pretzels on another plate.
>
> **Caption B:** A tray of french fries next to a tray of hot dogs and rice.
>
> **Adopted scope:** bread presence
>
> **Extracted A:** sandwich bread
>
> **Extracted B:** hotdogs without explicit buns
>
> **Recorded reason, verbatim:** Hotdogs served with rice do not necessarily include buns, so bread presence is not established in the second.

**Audit explanation:** B's hotdogs and rice leave bread presence unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 170. train_1689: `amount of fruit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A sandwich on a plate next to a banana and pretzels on another plate.
>
> **Caption B:** A tray of french fries next to a tray of hot dogs and rice.
>
> **Adopted scope:** fruit amount
>
> **Extracted A:** one banana
>
> **Extracted B:** no fruit stated
>
> **Recorded reason, verbatim:** The second meal gives no fruit quantity or supported absence.

**Audit explanation:** B lists hotdogs, fries, and rice. Fruit presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 171. train_1695: `type of seating`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A row of people sit on a orange bench in front of a table of food and pans.
>
> **Caption B:** A group of women sitting at a round table in a restaurant; one man.
>
> **Adopted scope:** seat type
>
> **Extracted A:** bench
>
> **Extracted B:** seat unspecified at table
>
> **Recorded reason, verbatim:** Sitting at a table does not identify whether the second seats are chairs or a bench.

**Audit explanation:** B seats people at a table. Seating type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 172. train_1723: `color of sundress`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A surfer stands at the shore looking at the waves with surf board in stow on the beach.
>
> **Caption B:** a woman in a white sundress is standing on a sunlit beach between two surfboards
>
> **Adopted scope:** sundress color
>
> **Extracted A:** no sundress stated
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** No sundress is mentioned for the first surfer.

**Audit explanation:** A describes a surfer. Sundress presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 173. train_1739: `place of standing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man holding a pair of skis standing next to two children who are also holding skis.
>
> **Caption B:** A man is smiling while he has his arm around a woman and a little girl on the top of a snowy mountain.
>
> **Adopted scope:** standing location
>
> **Extracted A:** unspecified
>
> **Extracted B:** snowy mountaintop
>
> **Recorded reason, verbatim:** Holding skis alone does not establish where the first group is standing.

**Audit explanation:** A places people beside each other. Their standing location remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 174. train_1788: `animal on computer screen`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A coffee cup, a bowl of orange peels, and a laptop sitting on a desk with a dog in the background.
>
> **Caption B:** A cat at a laptop computer with it's paw close to the computer and a cat on the computer screen.
>
> **Adopted scope:** animal on screen
>
> **Extracted A:** screen content unmentioned
>
> **Extracted B:** cat shown
>
> **Recorded reason, verbatim:** A dog behind a desk is not an animal shown on a screen; the first screen content is unreported.

**Audit explanation:** A places a dog in the background. The computer-screen content remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 175. train_1814: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman wearing a red wig with a hat with feathers and goggles on top of her head.
>
> **Caption B:** A woman in a purple victorian dress, hat, and a mask carries an umbrella.
>
> **Adopted scope:** clothing color
>
> **Extracted A:** wig red; clothing unspecified
>
> **Extracted B:** purple dress
>
> **Recorded reason, verbatim:** The first states the wig's color but no color for its hat or other clothing; the second explicitly colors the dress purple.

**Audit explanation:** A colors the wig red. Clothing color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 176. train_1825: `toys' accessories`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a group of stuffed teddy bears sitting on a bed next to a wall
>
> **Caption B:** Three stuffed animals one has a key around it's neck and one is wearing a red jacket.
>
> **Adopted scope:** toy accessories
>
> **Extracted A:** unspecified
>
> **Extracted B:** key and jacket
>
> **Recorded reason, verbatim:** The first teddy bears have no stated accessories.

**Audit explanation:** A identifies teddy bears. Their accessories remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 177. train_1851: `direction of travel`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A red and black train is traveling down the train tracks near a body of water.
>
> **Caption B:** A train with a colorful tagged front and seemingly white sides is coming around the bend.
>
> **Adopted scope:** travel direction
>
> **Extracted A:** along tracks; direction unspecified
>
> **Extracted B:** coming round bend
>
> **Recorded reason, verbatim:** Travel along tracks does not specify a comparable orientation or path direction in the first caption.

**Audit explanation:** A describes travel along tracks. Direction of travel remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 178. train_1856: `material enclosure is made of`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Polar bear at zoo looking at a metal rail in the middle of a pit.
>
> **Caption B:** A bear stands alone in a cement enclosure while people look down upon it.
>
> **Adopted scope:** enclosure material
>
> **Extracted A:** metal rail within pit; walls unknown
>
> **Extracted B:** cement enclosure
>
> **Recorded reason, verbatim:** A metal rail inside a pit does not establish what the enclosure itself is made from.

**Audit explanation:** A identifies an internal metal rail. The enclosure's material remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 179. train_1869: `number of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A woman and a cat reflected in a mirror made of three circular sections
>
> **Caption B:** a reflection of a person in a bathroom flashing a light into a mirror
>
> **Adopted scope:** animal count
>
> **Extracted A:** one cat
>
> **Extracted B:** no animal established
>
> **Recorded reason, verbatim:** The second reflection establishes no animal count or supported absence.

**Audit explanation:** B describes a reflected person. Nonhuman animal presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 180. train_1872: `name of fruit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A round table with two rounded plates that have various types of fruit on them and covered in plastic wrap.
>
> **Caption B:** A bowl of fruit sitting on a table to include a banana, kiwi, apples, and oranges. 
>
> **Adopted scope:** fruit kinds
>
> **Extracted A:** unnamed varied fruits
>
> **Extracted B:** banana, kiwi, apples, and oranges
>
> **Recorded reason, verbatim:** Various fruits states diversity without naming a fruit kind, so no first-caption fruit type can be compared with the listed banana, kiwi, apples, and oranges.

**Audit explanation:** A identifies varied fruit. Individual fruit names remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 181. train_1873: `type of fruit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A round table with two rounded plates that have various types of fruit on them and covered in plastic wrap.
>
> **Caption B:** A bowl of fruit sitting on a table to include a banana, kiwi, apples, and oranges. 
>
> **Adopted scope:** fruit types
>
> **Extracted A:** various unspecified
>
> **Extracted B:** banana kiwi apple orange
>
> **Recorded reason, verbatim:** Various unnamed fruits do not identify fruit types, analogous to confirmed unnamed-wine exclusions.

**Audit explanation:** A identifies varied fruit. Fruit types remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 182. train_1878: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A young girl is looking at a pile of glazed donuts with pink frosting.
>
> **Caption B:** Various doughnuts lay on a napkin and include a doughnut with coconut and one glazed and one chocolate.
>
> **Adopted scope:** people count
>
> **Extracted A:** one girl
>
> **Extracted B:** no person established
>
> **Recorded reason, verbatim:** The second food-only caption does not establish a person count.

**Audit explanation:** B describes doughnuts. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `5.0`.

### 183. train_1883: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman using an umbrella is standing next to a guard on a horse.
>
> **Caption B:** A law official is on a brown horse in front of a building where many people are gathered.
>
> **Adopted scope:** horse color
>
> **Extracted A:** unspecified
>
> **Extracted B:** brown
>
> **Recorded reason, verbatim:** The first horse has no stated coat color.

**Audit explanation:** A leaves horse color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 184. train_1896: `color of shorts`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in checkered blue shorts stands near a baby elephant and she has her trunk on his shoulder.
>
> **Caption B:** an elephant walking down the sidewalk with people riding on the back of it
>
> **Adopted scope:** shorts color
>
> **Extracted A:** blue checked
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second elephant riders' shorts and colors are unmentioned.

**Audit explanation:** B leaves riders' shorts colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 185. train_1903: `type of building`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A living room area with two couches and a storage bin in the middle of the room with a dinosaur figure on the storage box.
>
> **Caption B:** A room that appears small, bleak and barren holds a low bed with a quilt, a window with  blinds, and a small T.V.on a tiny stand.
>
> **Adopted scope:** building type
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Room interiors do not establish whether either building is a house, apartment block, hotel, or another building type.

**Audit explanation:** Both room descriptions leave the containing building's type unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 186. train_1911: `activity involving objects`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** This is an image of several bowls and plates on a table with flowers.
>
> **Caption B:** Cut up vegetables on a plate near dressing and chips and a stack of plates.
>
> **Adopted scope:** activity with dishes
>
> **Extracted A:** displayed dishes
>
> **Extracted B:** food/dishes displayed
>
> **Recorded reason, verbatim:** Both descriptions present dishes and food without an agent performing an activity involving them.

**Audit explanation:** Both captions describe arranged dishes. Activity involving those dishes remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 187. train_1926: `place animals eat from`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A zebra foal feeding on hay in a trough while an older zebra eats hay from the ground.
>
> **Caption B:** Two zebra standing next to each other in front of a cart full of dry hay.
>
> **Adopted scope:** actual place animals eat from
>
> **Extracted A:** foal feeds from trough; older zebra eats from ground
>
> **Extracted B:** zebras stand in front of a hay cart; eating unstated
>
> **Recorded reason, verbatim:** The hay cart is a potential feeding source, but the second caption never establishes feeding or its actual source. An available food arrangement cannot substitute for the requested eating relation.

**Audit explanation:** B places zebras before a hay cart. Eating from the cart remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 188. train_1930: `type of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A living room with a couch and a laptop computer resting on the couch.
>
> **Caption B:** A small room with a bay window and white walls and a few clothes strewn chairs
>
> **Adopted scope:** room type
>
> **Extracted A:** living room
>
> **Extracted B:** furnished domestic room with chairs and clothing
>
> **Recorded reason, verbatim:** Chairs and scattered clothing do not establish a room function, following confirmed #31 and #50.

**Audit explanation:** B's chairs, clothing, and window leave the room's function unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 189. train_1931: `room size`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A living room with a couch and a laptop computer resting on the couch.
>
> **Caption B:** A small room with a bay window and white walls and a few clothes strewn chairs
>
> **Adopted scope:** room size
>
> **Extracted A:** unspecified
>
> **Extracted B:** small
>
> **Recorded reason, verbatim:** The first living room has no stated size.

**Audit explanation:** A leaves room size unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 190. train_1943: `presence of toilet`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A bathroom for a doll house with a bathtub, toilet, cabinet and painted tiles.
>
> **Caption B:** A bathroom with the toilet and sink side by side with a mirror on the wall.
>
> **Adopted scope:** actual toilet presence
>
> **Extracted A:** dollhouse model toilet
>
> **Extracted B:** real toilet
>
> **Recorded reason, verbatim:** A dollhouse miniature is not an actual toilet for the literal toilet-presence condition.

**Audit explanation:** A establishes a dollhouse miniature. An actual toilet remains unestablished under the adopted literal-object scope.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 191. train_1945: `activity of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A persons legs stretched out on a bed as a person watches television in a darkened bedroom.
>
> **Caption B:** a bed an pillow in the foreground with a tv on in the background
>
> **Adopted scope:** human activity
>
> **Extracted A:** watching television
>
> **Extracted B:** TV on; person unstated
>
> **Recorded reason, verbatim:** A television being on does not establish a person or human activity in the second caption.

**Audit explanation:** B describes an operating television. Human presence and activity remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 192. train_1970: `room type`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A room that has a wood burning stove in the corner along with a television and wooden cabinets and counter top area.
>
> **Caption B:** A room with a guitar case, a clock, a table and a picture on the wall.
>
> **Adopted scope:** room type
>
> **Extracted A:** furnished room with stove TV cabinets and counter
>
> **Extracted B:** furnished room with guitar case table clock and wall picture
>
> **Recorded reason, verbatim:** A clock, table and guitar case do not establish the second room's function; generic furnishings are insufficient.

**Audit explanation:** B's guitar case, table, clock, and picture leave room function unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 193. train_1971: `closeness of walls`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A room that has a wood burning stove in the corner along with a television and wooden cabinets and counter top area.
>
> **Caption B:** A room with a guitar case, a clock, a table and a picture on the wall.
>
> **Adopted scope:** wall spacing
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Furniture and wall decorations in neither room establish distances between walls.

**Audit explanation:** Both captions leave the distance between the room's walls unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 194. train_1980: `appearance of train`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A large piece of machinery sits on a rail road track in a rural setting.
>
> **Caption B:** Detailed drawn color graphic of old train steam engine on the tracks with steam coming out the pipes on top.
>
> **Adopted scope:** actual train appearance
>
> **Extracted A:** rail machinery
>
> **Extracted B:** drawn steam-engine graphic
>
> **Recorded reason, verbatim:** The second train is a drawn representation rather than a comparable actual train appearance.

**Audit explanation:** B establishes a drawn train. Actual train appearance remains unavailable under the adopted literal-object scope.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 195. train_1981: `railroad tracks`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A large piece of machinery sits on a rail road track in a rural setting.
>
> **Caption B:** Detailed drawn color graphic of old train steam engine on the tracks with steam coming out the pipes on top.
>
> **Adopted scope:** actual tracks
>
> **Extracted A:** railroad tracks
>
> **Extracted B:** drawn tracks
>
> **Recorded reason, verbatim:** The second tracks occur within a drawing, so actual tracks are not established in both captions.

**Audit explanation:** B establishes drawn tracks. Actual tracks remain unestablished under the adopted literal-object scope.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 196. train_1996: `direction of giraffe`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A giraffe kneeling down on its front legs on sand in a fenced in area.
>
> **Caption B:** A cavern and many large rocks are part of the habitat that a giraffe appears to be looking at.
>
> **Adopted scope:** giraffe orientation
>
> **Extracted A:** kneeling downward
>
> **Extracted B:** looking toward rocks/cavern
>
> **Recorded reason, verbatim:** Kneeling specifies posture rather than a comparable gaze or facing direction toward the rocks and cavern.

**Audit explanation:** A supplies kneeling posture. Facing or gaze direction remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 197. train_2001: `number of floors`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A table and chairs is in a large room with a fireplace and couch.
>
> **Caption B:** A open area with seating on the bottom floor and a balcony on the upper floor.
>
> **Adopted scope:** floor count
>
> **Extracted A:** one room shown; floors unspecified
>
> **Extracted B:** two levels
>
> **Recorded reason, verbatim:** Seeing a single room does not establish the number of floors in the first building.

**Audit explanation:** A shows one room. The building's floor count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 198. train_2002: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man with no shirt on and wearing neon green pants jumping on a ski slope.
>
> **Caption B:** A shirtless male skier jumped in the air on his skis in the snow.
>
> **Adopted scope:** clothing color
>
> **Extracted A:** neon green pants
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second skier's clothing color is unreported despite both men being shirtless.

**Audit explanation:** B leaves clothing color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 199. train_2004: `type of bird`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** 4 seagulls stand on rusty rods with people in a boat in the background.
>
> **Caption B:** A sun is setting in the distance over a sea as a bird is standing on a wooden pillar.
>
> **Adopted scope:** bird type
>
> **Extracted A:** seagulls
>
> **Extracted B:** unspecified bird
>
> **Recorded reason, verbatim:** Generic bird does not identify the requested bird type in the second.

**Audit explanation:** B identifies a bird. Its type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 200. train_2007: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Three road signs on a wooden stand at the side of a city street.
>
> **Caption B:** A stop light that is flashing green in front of a group of people.
>
> **Adopted scope:** people count
>
> **Extracted A:** none established
>
> **Extracted B:** group
>
> **Recorded reason, verbatim:** The first caption establishes no person whose number can be compared; street context does not imply a count.

**Audit explanation:** A describes road signs. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 201. train_2035: `color of hydrant`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A white fire hydrant sitting outside a building with a mural painted on it.
>
> **Caption B:** A red stop sign leaning to the left in front of a red brick building.
>
> **Adopted scope:** hydrant color
>
> **Extracted A:** white
>
> **Extracted B:** no hydrant
>
> **Recorded reason, verbatim:** The second caption does not contain a hydrant whose color could be compared.

**Audit explanation:** B describes a stop sign and building. Hydrant presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 202. train_2045: `contents of dish`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a close up of a palte of food and a drink next to it
>
> **Caption B:** A plate of food with broccoli and what appears to be a meat of some type.
>
> **Adopted scope:** dish contents
>
> **Extracted A:** unspecified food
>
> **Extracted B:** broccoli and meat
>
> **Recorded reason, verbatim:** Generic food does not establish dish contents, following the confirmed type-information boundary.

**Audit explanation:** A identifies generic food. Dish contents remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 203. train_2053: `action of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A bus on the side of the street with a bunch of people in it
>
> **Caption B:** A red two level bus with front damage to it being towed down a street.
>
> **Adopted scope:** bus activity
>
> **Extracted A:** roadside location with occupants; action unstated
>
> **Extracted B:** being towed down a street
>
> **Recorded reason, verbatim:** A bus located at the side of a street with passengers has no stated movement or stopping action. Location alone does not establish a parked state.

**Audit explanation:** A gives the bus's roadside location and occupants. Bus activity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 204. train_2063: `activity of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A bus is in the street next to a sidewalk as a man is walking.
>
> **Caption B:** A bus is stopped on the side of the road to pick up passengers.
>
> **Adopted scope:** bus activity
>
> **Extracted A:** in street; movement unspecified
>
> **Extracted B:** stopped boarding passengers
>
> **Recorded reason, verbatim:** The first gives the bus location but no movement, stopping or passenger-handling action.

**Audit explanation:** A locates a bus in the street. Its movement and passenger handling remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 205. train_2064: `activity in bathroom`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A bathroom with a toilet, a sink, trash can, a towel rack and a mirror.
>
> **Caption B:** A person taking a picture of a bathroom with a toilet and a bowl sink.
>
> **Adopted scope:** bathroom activity
>
> **Extracted A:** room contents only
>
> **Extracted B:** taking photograph
>
> **Recorded reason, verbatim:** The first caption only inventories bathroom contents and establishes no human activity.

**Audit explanation:** A lists bathroom fixtures. Bathroom activity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 206. train_2085: `activity of cattle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** a man is milking a black cow and a stone fence is in the background
>
> **Caption B:** A herd of cattle in a fenced in field of grass and trees and shrubs.
>
> **Adopted scope:** cattle activity
>
> **Extracted A:** being milked
>
> **Extracted B:** present in field; action unspecified
>
> **Recorded reason, verbatim:** The second only locates cattle in a field and does not establish their activity.

**Audit explanation:** B locates cattle in a field. Their activity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 207. train_2087: `furniture arrangement`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A bedroom that has a bed and wooden night stand with a lamp on it, a book and binoculars.
>
> **Caption B:** A room with a bed, several pillows, two lamps and a window in it. 
>
> **Adopted scope:** furniture arrangement
>
> **Extracted A:** nightstand beside bed
>
> **Extracted B:** relative lamp positions unstated
>
> **Recorded reason, verbatim:** The second inventories room contents without identifying the arrangement of the lamps or other furniture.

**Audit explanation:** B inventories furniture and lamps. Their spatial arrangement remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 208. train_2096: `presence of petals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A conical glass with a rose plant in it and a ribbon around it.
>
> **Caption B:** A group of three vases filled with purple flowers on top of a table.
>
> **Adopted scope:** petal presence
>
> **Extracted A:** rose plant; bloom unstated
>
> **Extracted B:** flowers with petals
>
> **Recorded reason, verbatim:** A rose plant does not establish that a bloom and its petals are present; the second explicitly has flowers.

**Audit explanation:** A identifies a rose plant. Bloom and petal presence remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 209. train_2130: `name of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A baby sleeps next to a stuffed teddy bear the same size as him.
>
> **Caption B:** A baby is staring at the viewer with a large bow tie on its chest.
>
> **Adopted scope:** person proper name
>
> **Extracted A:** unnamed baby
>
> **Extracted B:** unnamed baby
>
> **Recorded reason, verbatim:** Neither baby has a stated personal name.

**Audit explanation:** Both captions leave the baby's name unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 210. train_2133: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cat is spread out on the blue carpet and someone is trying to pull their tennis shoe from underneath him.
>
> **Caption B:** an orange black and white cat is laying on a controller and a white couch
>
> **Adopted scope:** principal cats color
>
> **Extracted A:** cat color unspecified
>
> **Extracted B:** orange, black and white cat
>
> **Recorded reason, verbatim:** The principal objects are the cats. The first cat has no stated color; substituting the blue carpet for it would compare a background support instead.

**Audit explanation:** A colors the carpet blue. The principal cat's color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 211. train_2135: `number of beverages`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A meat sandwich is resting beside a mound of spinach and red lettuce leaves.
>
> **Caption B:** A closeup of a sandwich on a plate, with a coffee cup in the back.
>
> **Adopted scope:** beverage count
>
> **Extracted A:** none stated
>
> **Extracted B:** coffee cup
>
> **Recorded reason, verbatim:** The first caption establishes no beverage to count.

**Audit explanation:** A lists a sandwich and vegetables. Beverage presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 212. train_2156: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** There is a man sitting in a chair with his feet on his desk
>
> **Caption B:** A yellow figure is placed in front of the mouse on the computer desk.
>
> **Adopted scope:** object color
>
> **Extracted A:** unspecified
>
> **Extracted B:** yellow figure
>
> **Recorded reason, verbatim:** The first supplies no object color.

**Audit explanation:** A leaves chair, desk, and other principal object colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 213. train_2162: `person's attention`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** a baby sitting in a chair  and resting next to a stuffed teddy bear.
>
> **Caption B:** A baby is staring at the viewer with a large bow tie on its chest.
>
> **Adopted scope:** baby attention
>
> **Extracted A:** resting without gaze target
>
> **Extracted B:** looking at viewer
>
> **Recorded reason, verbatim:** Resting does not establish the first baby's attention target.

**Audit explanation:** A supplies a resting posture. The baby's attention target remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 214. train_2179: `color of bus`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A school bus is stopped with flashing lights and the door open at the sidewalk of a fire lane.
>
> **Caption B:** A white bus driving down a street next to the side of a road.
>
> **Adopted scope:** bus color
>
> **Extracted A:** school bus color unstated
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** School-bus identity alone does not establish a color in the first caption.

**Audit explanation:** A identifies a school bus. Its color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 215. train_2181: `fridge status`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A little girl wearing a red dress removes a large plastic container from a refrigerator
>
> **Caption B:** There is a young child sitting on the floor in front of the refrigerator.
>
> **Adopted scope:** fridge open/closed state
>
> **Extracted A:** open during removal
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second does not establish whether the refrigerator door is open or closed.

**Audit explanation:** B places a child before the refrigerator. The refrigerator's open or closed state remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 216. train_2186: `color of plate`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A slab of fish and a mound of broccoli are seated on a plate.
>
> **Caption B:** A green plate holds a healthy meal of chicken, broccoli, carrots and green beans.
>
> **Adopted scope:** plate color
>
> **Extracted A:** unspecified
>
> **Extracted B:** green
>
> **Recorded reason, verbatim:** The first plate has no stated color.

**Audit explanation:** A leaves plate color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 217. train_2189: `age of person holding brush`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** The lady in the picture is holding a little girl and fixing her hair.
>
> **Caption B:** A baby plays with brush while mother waits for her hair to be brushed.
>
> **Adopted scope:** brush-holder age
>
> **Extracted A:** brush unmentioned
>
> **Extracted B:** baby
>
> **Recorded reason, verbatim:** Fixing hair does not establish a brush or its holder; the first could use hands.

**Audit explanation:** A describes hair fixing. The brush-holder role and corresponding age remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 218. train_2217: `type of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Three bowls of various foods is located at a table with people in the background.
>
> **Caption B:** Several plates full of food, along with bowls, glasses, and drinks are on a large table.
>
> **Adopted scope:** food type
>
> **Extracted A:** various unspecified foods
>
> **Extracted B:** unspecified food assortment
>
> **Recorded reason, verbatim:** Neither caption identifies any food types; vessel counts do not supply them.

**Audit explanation:** Both captions identify generic food assortments. Food types remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 219. train_2227: `type of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A teddy bear in black chair leaning on keyboard with computer monitor on desk.
>
> **Caption B:** A cat sitting on a desk with its tail hanging over a keyboard .
>
> **Adopted scope:** actual animal type
>
> **Extracted A:** teddy toy
>
> **Extracted B:** cat
>
> **Recorded reason, verbatim:** The first bear is a stuffed toy, not an actual animal under the condition.

**Audit explanation:** A establishes a teddy-bear toy. Actual animal presence remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 220. train_2235: `size of bed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bed with a lot of pillows near a window showing a city view.
>
> **Caption B:** Hotel room with large bed, desk with TV, esk and phone and closed drapes.
>
> **Adopted scope:** bed size
>
> **Extracted A:** unspecified
>
> **Extracted B:** large
>
> **Recorded reason, verbatim:** The first gives no bed size; many pillows do not determine it.

**Audit explanation:** A leaves bed size unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 221. train_2238: `state of kitchen`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man standing in a kitchen looking at the open drawer on the oven.
>
> **Caption B:** A well used kitchen with oak cabinets and a big window over the sink.
>
> **Adopted scope:** kitchen state
>
> **Extracted A:** man viewing oven drawer; condition unstated
>
> **Extracted B:** well used
>
> **Recorded reason, verbatim:** The first describes a person looking at an oven drawer without establishing the kitchen's general condition.

**Audit explanation:** A describes a man viewing an oven drawer. The kitchen's overall condition remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 222. train_2246: `shape of pizza`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** There is a round homemade pizza in the foreground and a rectangular pizza in the background.
>
> **Caption B:** a closeup of a pizza covered with meat, basil leaves, cheese, and marinara sauce
>
> **Adopted scope:** pizza shape
>
> **Extracted A:** round and rectangular
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second pizza's shape is unstated.

**Audit explanation:** B lists pizza toppings. Pizza shape remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 223. train_2247: `shape of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** There is a round homemade pizza in the foreground and a rectangular pizza in the background.
>
> **Caption B:** a closeup of a pizza covered with meat, basil leaves, cheese, and marinara sauce
>
> **Adopted scope:** food shape
>
> **Extracted A:** round and rectangular pizzas
>
> **Extracted B:** shape unspecified
>
> **Recorded reason, verbatim:** The second supplies no food-shape information.

**Audit explanation:** B lists toppings. Food shape remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 224. train_2299: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A surfer is walking toward the water with board in tow with the horizon in the background.
>
> **Caption B:** A lone surfboard at the end of the day with the white capped waves rolling in.
>
> **Adopted scope:** people count
>
> **Extracted A:** one surfer
>
> **Extracted B:** no person established
>
> **Recorded reason, verbatim:** The second caption establishes a board but no person whose count can be compared.

**Audit explanation:** B establishes a surfboard and waves. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 225. train_2312: `direction of travel`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A red van driving towards a large white water tower at the end of a street.
>
> **Caption B:** A red stop light and a restricted lane sign, with an American flag in the background.
>
> **Adopted scope:** travel direction
>
> **Extracted A:** toward water tower
>
> **Extracted B:** no traveler
>
> **Recorded reason, verbatim:** The second has traffic signs but no traveler or direction of motion.

**Audit explanation:** B describes traffic fixtures. A traveler's direction remains unavailable.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 226. train_2321: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Several plates full of food, along with bowls, glasses, and drinks are on a large table.
>
> **Caption B:** The group of people are sitting down at the table sharing a meal together.
>
> **Adopted scope:** people count
>
> **Extracted A:** no people stated
>
> **Extracted B:** group
>
> **Recorded reason, verbatim:** Serving dishes alone do not establish a number of people in the first caption.

**Audit explanation:** A lists tableware and food. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 227. train_2331: `number of sail boat`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Person on a beach watching a single-sail boat out past the surf at sunset.
>
> **Caption B:** A sandy terrain with footprints has a mirage of water in the near distance.
>
> **Adopted scope:** sailboat count
>
> **Extracted A:** one
>
> **Extracted B:** no boat stated
>
> **Recorded reason, verbatim:** The second establishes no sailboat to count.

**Audit explanation:** B describes sand and a mirage. Sailboat presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 228. train_2341: `type of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** a blocked off area of road, and a couple of road signs with arrows pointing to a open area of road.
>
> **Caption B:** A taxi van following a double decker bus on a road while another bus is coming the opposite direction.
>
> **Adopted scope:** vehicle type
>
> **Extracted A:** no vehicle stated
>
> **Extracted B:** taxi van and buses
>
> **Recorded reason, verbatim:** Road signs alone do not identify an actual vehicle type in the first caption.

**Audit explanation:** A describes barriers and road signs. Vehicle presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 229. train_2357: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A woman looks at her cell phone while her cat stands on her shoulder.
>
> **Caption B:** A black and white cat sits near a pile of clothes and has one eye closed.
>
> **Adopted scope:** people count
>
> **Extracted A:** one woman
>
> **Extracted B:** no person stated
>
> **Recorded reason, verbatim:** The second contains a cat but no stated person.

**Audit explanation:** B describes a cat and clothing. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 230. train_2369: `presence of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** a close up of a bench near a tree with a view of water
>
> **Caption B:** A couple of people sitting on a bench in a park next to a large body of water.
>
> **Adopted scope:** people presence
>
> **Extracted A:** unmentioned
>
> **Extracted B:** couple present
>
> **Recorded reason, verbatim:** The first leaves people unmentioned and does not establish their absence.

**Audit explanation:** A describes a bench and scenery. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 231. train_2370: `food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A plate full of a breakfast food and a container of juice to the side.
>
> **Caption B:** A kitchen with a lot of food on the counter & food being prepared on the stove top.
>
> **Adopted scope:** food type
>
> **Extracted A:** breakfast food
>
> **Extracted B:** unspecified cooking foods
>
> **Recorded reason, verbatim:** The second caption names only generic food without a type.

**Audit explanation:** B identifies generic cooking food. Food type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 232. train_2373: `traffic lights`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A no left turn sign, a fire hydrant, a walk sign and a traffic light are at a corner.
>
> **Caption B:** A photo of a street lamp with a street light and a street sign.
>
> **Adopted scope:** traffic-control lights
>
> **Extracted A:** explicit traffic light and walk signal
>
> **Extracted B:** street illumination and street sign; traffic-control light unestablished
>
> **Recorded reason, verbatim:** A street lamp or illuminating streetlight is not enough to establish a traffic-control light in the second caption.

**Audit explanation:** B establishes a streetlamp and sign. A traffic-control light remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 233. train_2386: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** There is a door with scrollwork on it on a blue and white building with a red bench out front.
>
> **Caption B:** Scissors and other implements hang from hooks next to an open window with a removable screen.
>
> **Adopted scope:** object colors
>
> **Extracted A:** blue white building red bench
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second supplies no comparable object color.

**Audit explanation:** B leaves implement, hook, and window colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 234. train_2400: `person's sentiment`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman on a train turns her head and looks out the window as a school bus is in the distance.
>
> **Caption B:** A man is looking out a train window with his arms folded on the window sill and an elbow hanging out.
>
> **Adopted scope:** person emotion
>
> **Extracted A:** looking out; emotion unstated
>
> **Extracted B:** looking out; emotion unstated
>
> **Recorded reason, verbatim:** Looking through a window does not establish either person's emotional sentiment.

**Audit explanation:** Both captions supply outward gaze. The people's sentiments remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 235. train_2419: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A tiger cat laying on to of a table next to a potted plant.
>
> **Caption B:** A grey tabby cat curled up, sleeping on a brown and beige printed overstuffed chair.
>
> **Adopted scope:** cat color
>
> **Extracted A:** tiger pattern; base color unspecified
>
> **Extracted B:** grey tabby
>
> **Recorded reason, verbatim:** Tiger pattern does not determine the first cat's coat hue.

**Audit explanation:** A supplies a tiger pattern. The cat's coat hue remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 236. train_2439: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young child is watching a kite in the air on a soccer field.
>
> **Caption B:** A colorful kite flies into some trees near where people are playing some type of game.
>
> **Adopted scope:** kite color
>
> **Extracted A:** unspecified
>
> **Extracted B:** colorful
>
> **Recorded reason, verbatim:** The first kite has no stated color.

**Audit explanation:** A leaves kite color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 237. train_2456: `object animal's focused on`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A black and white cat is sitting in a dark spot behind a fruit bowl.
>
> **Caption B:** a close up of a cat at a table with a plate in front of it
>
> **Adopted scope:** cat attention target
>
> **Extracted A:** behind bowl; gaze unstated
>
> **Extracted B:** plate in front; gaze unstated
>
> **Recorded reason, verbatim:** A nearby bowl or plate does not establish either cat's attention target.

**Audit explanation:** Both captions locate cats beside objects. Their attention targets remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 238. train_2461: `activity of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Large clock on a building with a statue of a skeleton and a man working working.
>
> **Caption B:** There is a close of pic of one of many clocks on a building
>
> **Adopted scope:** clock activity or operating state
>
> **Extracted A:** clock present on building; operation unstated
>
> **Extracted B:** clock present on building; operation unstated
>
> **Recorded reason, verbatim:** The captions identify mounted clocks but do not describe their operation or movement. Replacing current activity with an object's usual function would change the requested feature.

**Audit explanation:** Both captions identify mounted clocks. Clock operation remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 239. train_2465: `number of beverages`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A tuna fish sandwich is sitting next to a large group of french fries.
>
> **Caption B:** A sandwich is on a white plate near two forks and a glass of milk.
>
> **Adopted scope:** beverage count
>
> **Extracted A:** no drink or vessel
>
> **Extracted B:** one glass of milk
>
> **Recorded reason, verbatim:** The first supplies no beverage or beverage vessel.

**Audit explanation:** A describes a sandwich and fries. Beverage presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 240. train_2477: `name of plate`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A man eating a sandwich, their is also a bowl of soup on the table.
>
> **Caption B:** A sliced sandwich on a white plate with a bite taken out of it.
>
> **Adopted scope:** plate type
>
> **Extracted A:** sandwich support unstated
>
> **Extracted B:** white plate
>
> **Recorded reason, verbatim:** The first mentions a soup bowl but no plate for the sandwich.

**Audit explanation:** A establishes a soup bowl. A plate supporting the sandwich remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 241. train_2498: `purpose of activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A funny picture of a guy dressed like Jesus caring a surfboard on the beach.
>
> **Caption B:** A boy that is out in pretty choppy water is holding onto his surf board.
>
> **Adopted scope:** person purpose
>
> **Extracted A:** costumed surfboard pose
>
> **Extracted B:** holding board in surf
>
> **Recorded reason, verbatim:** Costume and holding a board do not establish an intended purpose for the first activity; a motive cannot be supplied from these static details.

**Audit explanation:** A supplies a costume and surfboard. The activity's intended purpose remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 242. train_2509: `proximity to vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A view of the back of a pick up truck with a hole in it.
>
> **Caption B:** A truck beside an old, weathered red shed on cleared land on the edge of a forest.
>
> **Adopted scope:** camera-truck proximity
>
> **Extracted A:** back view; distance unstated
>
> **Extracted B:** truck near shed; camera distance unstated
>
> **Recorded reason, verbatim:** Neither caption establishes camera-to-truck distance; a rear view is a viewpoint, not a proximity measurement.

**Audit explanation:** Both truck descriptions leave camera-to-vehicle distance unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 243. train_2511: `size of fridge`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A mini fridge with a lamp on top of it next to a couch.
>
> **Caption B:** A kitchen with cabinets and no door, a refrigerator and a garbage can in it. 
>
> **Adopted scope:** refrigerator size
>
> **Extracted A:** mini fridge
>
> **Extracted B:** refrigerator in kitchen, size unspecified
>
> **Recorded reason, verbatim:** Kitchen placement does not establish refrigerator size; the first has an explicit mini-size value only.

**Audit explanation:** B identifies a refrigerator. Its size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 244. train_2517: `activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A girl with arms crossed leaning on counter over a rectangular pizza, by a wall calendar and containers.
>
> **Caption B:** A whole cheese pizza is sitting on a plate with a knife and fork sticking out of the bottom of the crust.
>
> **Adopted scope:** human activity
>
> **Extracted A:** girl leaning on counter
>
> **Extracted B:** no person stated
>
> **Recorded reason, verbatim:** The second static pizza arrangement supplies no person or human action.

**Audit explanation:** B describes pizza and utensils. Human activity remains unavailable.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 245. train_2528: `type of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A museum dislplay of a dining table with chairs in front of a wooden fireplace.
>
> **Caption B:** a desk with a planter and a  chair and a lot of windows in the room
>
> **Adopted scope:** functional room type
>
> **Extracted A:** museum display
>
> **Extracted B:** room with desk, chair and planter, function unspecified
>
> **Recorded reason, verbatim:** The museum is explicit, but generic furniture and windows do not establish the second room's function under the user-confirmed boundary.

**Audit explanation:** B's desk, chair, planter, and windows leave room function unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 246. train_2531: `type of position`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A tortoseshell cat lies on the seat of an office chair behind a human.
>
> **Caption B:** A cat is looking in the mirror at a front side that doesn't look anything like the back side.
>
> **Adopted scope:** cat posture
>
> **Extracted A:** lying on chair
>
> **Extracted B:** looking in mirror; posture unspecified
>
> **Recorded reason, verbatim:** Looking in a mirror does not establish a body posture comparable with lying down.

**Audit explanation:** B supplies mirror viewing. The cat's body posture remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 247. train_2539: `color of cat`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cat is sound asleep at the end of a bed with pictures in the background.
>
> **Caption B:** A gray and black striped tabby cat laying on its back in a chair.
>
> **Adopted scope:** cat color
>
> **Extracted A:** unspecified
>
> **Extracted B:** grey and black
>
> **Recorded reason, verbatim:** The sleeping cat's coat color is unstated.

**Audit explanation:** A leaves cat color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 248. train_2571: `presence of boy and man riding`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An elephant in a lake spray uses its trunk to spray water at a person standing on its back.
>
> **Caption B:** A man and a boy riding on the back of an elephant in the water.
>
> **Adopted scope:** male adult-and-boy riding presence
>
> **Extracted A:** one gender-unspecified person
>
> **Extracted B:** man and boy
>
> **Recorded reason, verbatim:** The first supplies only a person of unknown gender and age, not an established man-and-boy pair riding.

**Audit explanation:** A identifies one person of unspecified age and gender. The requested boy-and-man roles remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 249. train_2587: `material`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bend with two posts and a wooden headboard against a wall with striped wallpaper design.
>
> **Caption B:** A bed with a white bedspread and four pillows a white dresser with an alarm clock on top and other things.
>
> **Adopted scope:** bed-frame material
>
> **Extracted A:** wood
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second bed frame's material is unstated; white describes color, not material.

**Audit explanation:** B colors furniture white. Furniture material remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 250. train_2589: `type of drink`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A plate with a cookie and ice cream on it sits next to a wine glass.
>
> **Caption B:** A piece of cake and coffee is featured next to a close up fork.
>
> **Adopted scope:** drink type
>
> **Extracted A:** wine glass; contents unknown
>
> **Extracted B:** coffee
>
> **Recorded reason, verbatim:** A wine glass does not establish its contents, so the first drink type is unavailable.

**Audit explanation:** A identifies a wine glass. Its drink contents remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 251. train_2597: `number of objects present`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A huge crowd of people standing on a corner of a very busy intersection.
>
> **Caption B:** This is a picture of a car going by in a very busy city.
>
> **Adopted scope:** nonhuman principal physical object count
>
> **Extracted A:** crowd and intersection, no countable nonhuman objects established
>
> **Extracted B:** one car
>
> **Recorded reason, verbatim:** The frozen object-count convention excludes people; a busy intersection does not establish an unstated inventory of nonhuman objects.

**Audit explanation:** A supplies a crowd and intersection. Discrete nonhuman objects remain unspecified under the adopted count scope.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 252. train_2604: `presence of power lines`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A clock tower that looks rather plain is streaked with the image of power lines.
>
> **Caption B:** A street sign holds several signs and stands next to a rust colored building.
>
> **Adopted scope:** power-line presence
>
> **Extracted A:** present
>
> **Extracted B:** unmentioned
>
> **Recorded reason, verbatim:** The second street scene does not establish power-line absence.

**Audit explanation:** B describes signs and a building. Power-line presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 253. train_2618: `name of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A couch with a laptop on it and clothes and pillows sitting on it.
>
> **Caption B:** A small room with a bay window and white walls and a few clothes strewn chairs
>
> **Adopted scope:** functional room name
>
> **Extracted A:** couch and laptop support a partial domestic work or lounge setting
>
> **Extracted B:** chairs, clothes and bay window; room function unspecified
>
> **Recorded reason, verbatim:** The second has generic furnishings but no recoverable functional room type, matching the user-confirmed furniture-only exclusion.

**Audit explanation:** B's chairs, clothing, and bay window leave room function unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 254. train_2619: `type of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A couch with a laptop on it and clothes and pillows sitting on it.
>
> **Caption B:** A small room with a bay window and white walls and a few clothes strewn chairs
>
> **Adopted scope:** clothing type
>
> **Extracted A:** unspecified clothes
>
> **Extracted B:** unspecified clothes
>
> **Recorded reason, verbatim:** Neither caption identifies garment types beyond generic clothes.

**Audit explanation:** Both captions identify generic clothing. Clothing types remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 255. train_2634: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A captive elephant is forced to do tricks for the guy at the circus.
>
> **Caption B:** This elephant is standing with its front legs on one stool and its back legs on another stool.
>
> **Adopted scope:** people count
>
> **Extracted A:** one man
>
> **Extracted B:** no person stated
>
> **Recorded reason, verbatim:** The second elephant scene supplies no person count.

**Audit explanation:** B describes an elephant balancing on stools. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 256. train_2642: `color of cat`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Grey cat sitting on the ground looking in the direction of a television control.
>
> **Caption B:** A black and white picture of a cat on a chair staring out a window.
>
> **Adopted scope:** cat color
>
> **Extracted A:** grey
>
> **Extracted B:** monochrome image; coat unspecified
>
> **Recorded reason, verbatim:** A black-and-white photograph does not establish the second cat's actual coat color.

**Audit explanation:** B specifies monochrome photography. The cat's coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 257. train_2677: `person's age`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** People watching a skate board rider do a jump in a skate board park.
>
> **Caption B:** The young is riding his skateboard  at the edge of the skateboard deck loaded with graffiti.
>
> **Adopted scope:** skateboarder age
>
> **Extracted A:** unspecified
>
> **Extracted B:** young
>
> **Recorded reason, verbatim:** The first skateboarder's age is unstated.

**Audit explanation:** A identifies a skateboard rider. Age remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 258. train_2682: `name of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A smiling man wearing a cowboy hat poses with his horse also wearing a cowboy hat.
>
> **Caption B:** A cowboy secures a saddlebag on the side of a white and brown horse.
>
> **Adopted scope:** person name
>
> **Extracted A:** unnamed man
>
> **Extracted B:** unnamed cowboy
>
> **Recorded reason, verbatim:** Neither caption supplies a personal name.

**Audit explanation:** Both captions leave the man's name unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 259. train_2694: `top of building`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An ornate clock fastened to the side of a building with a wire apparatus.
>
> **Caption B:** The tower has a cross on its top and a clock on the sides.
>
> **Adopted scope:** building-top feature
>
> **Extracted A:** clock on side; top unspecified
>
> **Extracted B:** cross
>
> **Recorded reason, verbatim:** A clock on the side of a building does not identify a feature on its top.

**Audit explanation:** A locates a clock on the building's side. The building's top remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 260. train_2697: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white bull dog hanging out of a car window with a red bandanna around his neck.
>
> **Caption B:** A dog with its head looking out of the back of a pick up truck's cab
>
> **Adopted scope:** dog color
>
> **Extracted A:** white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second dog's coat color is absent.

**Audit explanation:** B leaves dog color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 261. train_2701: `presence of picture`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A bunch of yellow bananas with a picture of a girl on top of them.
>
> **Caption B:** A bowl of fruit with bananas hanging from the bowl and a candle sconce hanging on the wall.
>
> **Adopted scope:** picture presence
>
> **Extracted A:** girl picture present
>
> **Extracted B:** unmentioned
>
> **Recorded reason, verbatim:** The second fruit arrangement does not establish whether a picture is absent.

**Audit explanation:** B lists fruit and a wall sconce. Picture presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 262. train_2710: `time of day`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young man on a skate board caught in mid air while doing a jump
>
> **Caption B:** a young skateboarder doing a trick off a ramp in the dim evening light
>
> **Adopted scope:** time of day
>
> **Extracted A:** unspecified
>
> **Extracted B:** evening
>
> **Recorded reason, verbatim:** The first skateboard scene gives no time of day.

**Audit explanation:** A leaves time of day unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 263. train_2735: `safety of project`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A tree grinder parked on the side of a street next to orange cones.
>
> **Caption B:** There is a large pile of dirt in the street, indicating that construction or landscaping is taking place.
>
> **Adopted scope:** work-site safety
>
> **Extracted A:** cones present
>
> **Extracted B:** safety measures unspecified
>
> **Recorded reason, verbatim:** The second worksite's safety measures or safety level are not described.

**Audit explanation:** B establishes a dirt pile. Project safety and safety measures remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 264. train_2739: `food item`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** This appears to be a couple, formally dressed, making a plate for each other. 
>
> **Caption B:** a man and a woman standing near a table with a cake on the table
>
> **Adopted scope:** food item
>
> **Extracted A:** unspecified plated food
>
> **Extracted B:** cake
>
> **Recorded reason, verbatim:** Making a plate does not identify a food item in the first caption.

**Audit explanation:** A describes making plates. The served food remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 265. train_2740: `presence of refreshments`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A table with an open book, newspapers, three remote controls, a bottle of water and a glass.
>
> **Caption B:** Notebooks and various other personal items sitting on a desk next to a computer.
>
> **Adopted scope:** refreshment presence
>
> **Extracted A:** water present
>
> **Extracted B:** unmentioned
>
> **Recorded reason, verbatim:** Notebooks and unspecified personal items do not establish refreshments present or absent.

**Audit explanation:** B lists notebooks and personal items. Refreshment presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 266. train_2751: `number of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A cat is perched up on a toilet in a charming bathroom with polka dot floors.
>
> **Caption B:** A bathroom with white tile flooring and a backsplash, and floral designed wall paper at the top of the walls.
>
> **Adopted scope:** animal count
>
> **Extracted A:** one cat
>
> **Extracted B:** none established
>
> **Recorded reason, verbatim:** The second bathroom description supplies no animal count.

**Audit explanation:** B describes bathroom surfaces. Animal presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 267. train_2758: `style of furniture`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A casual yet sophisticated living room has overstuffed black leather couches and a natural wood coffee table.
>
> **Caption B:** A living room near an open window has furniture and an area rug on the floor.
>
> **Adopted scope:** furniture style
>
> **Extracted A:** casual sophisticated leather/wood
>
> **Extracted B:** style unspecified
>
> **Recorded reason, verbatim:** Generic furniture and a rug do not establish the second furniture style, following the user-confirmed style boundary.

**Audit explanation:** B identifies generic furniture. Furniture style remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 268. train_2759: `location of living room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A casual yet sophisticated living room has overstuffed black leather couches and a natural wood coffee table.
>
> **Caption B:** A living room near an open window has furniture and an area rug on the floor.
>
> **Adopted scope:** living-room location
>
> **Extracted A:** unspecified relative location
>
> **Extracted B:** by open window
>
> **Recorded reason, verbatim:** The first living room's position relative to windows or other surroundings is unstated.

**Audit explanation:** A leaves the living room's relative location unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 269. train_2768: `color of ball`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A male tennis player is reaching up with one hand and has a tennis racquet in his other hand.
>
> **Caption B:** A man wearing white throws a tennis ball in the air in preparation for a serve on a grass court.
>
> **Adopted scope:** ball color
>
> **Extracted A:** unstated tennis ball
>
> **Extracted B:** unstated tennis ball
>
> **Recorded reason, verbatim:** Neither caption supplies the tennis ball's actual color, and the first does not explicitly describe a ball.

**Audit explanation:** Both captions leave tennis-ball color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 270. train_2781: `color of meat`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The fresh seafood is served on a bun and cocktail sauce garnish,  fries, and a pickle spear.
>
> **Caption B:** A chopped meat sandwich topped with a slice of cheese is served with a side of fries.
>
> **Adopted scope:** meat color
>
> **Extracted A:** seafood color unspecified
>
> **Extracted B:** chopped meat color unspecified
>
> **Recorded reason, verbatim:** Neither seafood nor chopped meat is assigned a color in the captions.

**Audit explanation:** Both captions leave meat color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 271. train_2783: `number of electronics`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A man and a dog in a living room with couches, a coffee table, and a closet.
>
> **Caption B:** The living room is rather sparsely furnished, but has electronics, magazines, a gold fish bowl and slippers.
>
> **Adopted scope:** electronics count
>
> **Extracted A:** none specified
>
> **Extracted B:** plural electronics
>
> **Recorded reason, verbatim:** The first room lists no electronics whose count can be extracted.

**Audit explanation:** A lists living-room furniture. Electronic-device presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 272. train_2790: `color of urinals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Two white urinals can be seen as you enter the door with a sign on it.
>
> **Caption B:** A hotel bathroom with the shower curtain open and fresh towels stacked above the toilet and laid across the bathtub.
>
> **Adopted scope:** urinal color
>
> **Extracted A:** white
>
> **Extracted B:** no urinals stated
>
> **Recorded reason, verbatim:** The second bathroom describes a toilet and tub, not any urinal whose color can be compared.

**Audit explanation:** B identifies a toilet and bathtub. Urinal presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 273. train_2792: `type of dessert`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A paper machet cake with a stuffed horse toy in a fence on top.
>
> **Caption B:** A white plate topped with a small cake covered in chocolate, candy and candles.
>
> **Adopted scope:** actual dessert type
>
> **Extracted A:** papier-mache model cake
>
> **Extracted B:** edible cake
>
> **Recorded reason, verbatim:** A papier-mache cake is a model, so the first actual-dessert requirement is inapplicable.

**Audit explanation:** A establishes a papier-mâché cake model. An edible dessert remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 274. train_2793: `food decorations`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A paper machet cake with a stuffed horse toy in a fence on top.
>
> **Caption B:** A white plate topped with a small cake covered in chocolate, candy and candles.
>
> **Adopted scope:** edible food decorations
>
> **Extracted A:** toy horse on model cake
>
> **Extracted B:** chocolate candy candles
>
> **Recorded reason, verbatim:** The first decorations sit on a model rather than real food.

**Audit explanation:** A places decorations on a model cake. Decorations on real food remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 275. train_2799: `type of view`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man squatting in the air above an upside-down skateboard in the air above pavement with paved wall and trees behind.
>
> **Caption B:** A fish eye lens view of a young man doing a trick on a skateboard.
>
> **Adopted scope:** camera view type
>
> **Extracted A:** ordinary view unspecified
>
> **Extracted B:** fisheye lens
>
> **Recorded reason, verbatim:** The first image's lens or optical viewpoint is not supplied.

**Audit explanation:** A describes the skateboarder's surroundings. Camera-view type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 276. train_2803: `type of cuisine`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a salad, and a fish sandwich, with a side of tartar sauce on a plate.
>
> **Caption B:** Some Mexican food, including a salad and burrito, with some fruit juice, are ready to be eaten. 
>
> **Adopted scope:** cuisine
>
> **Extracted A:** fish sandwich; cuisine unspecified
>
> **Extracted B:** Mexican
>
> **Recorded reason, verbatim:** Fish sandwich with tartar sauce does not establish a unique national cuisine comparable with explicit Mexican food.

**Audit explanation:** A identifies a fish sandwich and tartar sauce. National cuisine remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 277. train_2816: `activity of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Two men try and control a balloon kite on the ground at a beach.
>
> **Caption B:** Some of the balloons in the air are very large next to the kites.
>
> **Adopted scope:** human activity
>
> **Extracted A:** controlling grounded kite
>
> **Extracted B:** objects airborne; people unstated
>
> **Recorded reason, verbatim:** Airborne objects alone do not establish any described person's action in the second scene.

**Audit explanation:** B describes airborne balloons and kites. Human presence and activity remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 278. train_2817: `size of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two men try and control a balloon kite on the ground at a beach.
>
> **Caption B:** Some of the balloons in the air are very large next to the kites.
>
> **Adopted scope:** kite/balloon size
>
> **Extracted A:** unspecified
>
> **Extracted B:** large balloons relative to kites
>
> **Recorded reason, verbatim:** The first kite has no stated size.

**Audit explanation:** A leaves balloon-kite size unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 279. train_2819: `time of day`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person on a snowy sidewalk at night bends over to adjust their snowboard.
>
> **Caption B:** A man is standing outside in the snow near a house and covered cars.
>
> **Adopted scope:** time of day
>
> **Extracted A:** night
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second snow scene does not establish a time of day.

**Audit explanation:** B leaves time of day unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 280. train_2827: `activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A computer desk topped with a monitor and a keyboard next to a mouse.
>
> **Caption B:** A cluttered room with a dog laying on the floor and a laptop sitting on a untidy table.
>
> **Adopted scope:** human activity
>
> **Extracted A:** equipment only
>
> **Extracted B:** dog lying; no person
>
> **Recorded reason, verbatim:** Computer equipment and a resting dog do not establish a human computer activity.

**Audit explanation:** A lists computer equipment. Activity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 281. train_2870: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A man pulling two pieces of luggage with a kid hanging on to each piece.
>
> **Caption B:** A baby stroller is loaded with a handbag as a suitcase and empty carrier sit alongside.
>
> **Adopted scope:** people count
>
> **Extracted A:** man and two children: three
>
> **Extracted B:** no people stated
>
> **Recorded reason, verbatim:** A stroller and luggage do not establish any person count in the second scene.

**Audit explanation:** B lists luggage and carriers. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 282. train_2871: `people's activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A man pulling two pieces of luggage with a kid hanging on to each piece.
>
> **Caption B:** A baby stroller is loaded with a handbag as a suitcase and empty carrier sit alongside.
>
> **Adopted scope:** people activity
>
> **Extracted A:** pulling luggage/hanging on
>
> **Extracted B:** no people stated
>
> **Recorded reason, verbatim:** The second static luggage scene supplies no person's activity.

**Audit explanation:** B lists luggage and carriers. Human activity remains unavailable.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 283. train_2875: `type of boat`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A small boat and large buoys stuck in the sand by a stone wall
>
> **Caption B:** A boat sitting on top of a shore next to a body of water.
>
> **Adopted scope:** boat subtype
>
> **Extracted A:** boat beached beside buoys, subtype unspecified
>
> **Extracted B:** boat beached on shore, subtype unspecified
>
> **Recorded reason, verbatim:** Neither caption identifies a boat subtype; beaching and small size do not name the requested type.

**Audit explanation:** Both captions identify beached boats. Boat subtypes remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 284. train_2903: `name of action`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** An older toothbrush and a newer one sitting on the edge of a sink.
>
> **Caption B:** A toilet with accessories sitting next to it and toilet paper on the roll near by.
>
> **Adopted scope:** action
>
> **Extracted A:** objects resting
>
> **Extracted B:** objects resting
>
> **Recorded reason, verbatim:** Both captions merely locate objects and establish no named human action.

**Audit explanation:** Both captions locate bathroom objects. An action remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 285. train_2915: `person at beach`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dark-haired boy on the beach  attends to a colorful kite whilst clad in swim trunks.
>
> **Caption B:** A man wearing a black baseball cap and shorts holding a baseball bat while standing in the sand.
>
> **Adopted scope:** person located at a beach
>
> **Extracted A:** boy explicitly on beach
>
> **Extracted B:** man standing on sand, beach unestablished
>
> **Recorded reason, verbatim:** Sand alone does not establish the second person's beach location, unlike the explicit first setting.

**Audit explanation:** B places a man on sand. Beach location remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 286. train_2967: `color of table`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A refrigerator that is in a kitchen that has a worn down yellow table.
>
> **Caption B:** An area of the kitchen has a gas range with a pot and tea pot below a microwave.
>
> **Adopted scope:** table color
>
> **Extracted A:** yellow
>
> **Extracted B:** no table stated
>
> **Recorded reason, verbatim:** The second kitchen contains no stated table or table color.

**Audit explanation:** B describes kitchen appliances. A table remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 287. train_2969: `color of clock`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Four different views of a building with column, steeple, carved details, and clock showing 12:13, three of the views are up close details, and one view of entire front view.
>
> **Caption B:** A clock that is red and white. It appears to be above a door and has statues all above the clock.
>
> **Adopted scope:** clock color
>
> **Extracted A:** unspecified
>
> **Extracted B:** red and white
>
> **Recorded reason, verbatim:** The first clock has no stated color.

**Audit explanation:** A leaves clock color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 288. train_3009: `presence of plate with food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** a serving table at a function with a few dishes and stacks of plates
>
> **Caption B:** Kitchen with a plate of food made up of different items sitting on the counter.
>
> **Adopted scope:** presence of a plate holding food
>
> **Extracted A:** serving dishes and stacked plates, filled plate unestablished
>
> **Extracted B:** explicit plate of food
>
> **Recorded reason, verbatim:** The first does not connect food to a plate; stacked plates and unspecified serving dishes do not establish a filled plate.

**Audit explanation:** A identifies stacked plates and serving dishes. Food on a plate remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 289. train_3027: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A picture of a white bathroom with a hanging overhead lamp, a radiator, and a striped shower curtain.
>
> **Caption B:** A bathroom with a large circular mirror above a large vanity sink, with a shower and tub to the side of it.
>
> **Adopted scope:** bathroom colors
>
> **Extracted A:** white and striped curtain
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second bathroom supplies no colors for its fixtures or surfaces.

**Audit explanation:** B leaves fixture and principal bathroom-object colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 290. train_3044: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A outdoor area produce market that has bananas hanging from strings and other fruit on tables, along with a scale.
>
> **Caption B:** A woman in a yellow shirt and a man in a white shirt at a store with fresh produce.
>
> **Adopted scope:** people count
>
> **Extracted A:** none stated
>
> **Extracted B:** woman and man: two
>
> **Recorded reason, verbatim:** The first produce display supplies no person count.

**Audit explanation:** A describes market produce and a scale. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 291. train_3049: `use of electronic`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A room with a woman standing in front of a television playing a video game.
>
> **Caption B:** A cluttered living room with a large couch, a flat screen and glass doors.
>
> **Adopted scope:** TV use
>
> **Extracted A:** video game
>
> **Extracted B:** use unspecified
>
> **Recorded reason, verbatim:** A television present in a room does not establish its current use in the second caption.

**Audit explanation:** B identifies a television. Its current use remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 292. train_3053: `color of passenger plane`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white and gray passenger plane has just landed or is about to take off.
>
> **Caption B:** A picture of a plane in the sky with polka dots on the end of the plane.
>
> **Adopted scope:** plane colors
>
> **Extracted A:** white and grey
>
> **Extracted B:** polka dots without colors
>
> **Recorded reason, verbatim:** Polka dots identify pattern, not the second airplane's colors.

**Audit explanation:** B supplies polka dots. Airplane colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 293. train_3055: `number of appliances`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** a dog in a kitchen with a microwave above a stove with a sink
>
> **Caption B:** There is a kitchen with wood cabinets and an island with a white top
>
> **Adopted scope:** appliance count
>
> **Extracted A:** microwave stove
>
> **Extracted B:** no appliances named
>
> **Recorded reason, verbatim:** Cabinets and island do not establish any second kitchen appliance count.

**Audit explanation:** B lists cabinets and an island. Appliances remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 294. train_3058: `whether cat is alive`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A cat standing on the back of the passenger side seat of a car.
>
> **Caption B:** A stuffed animal is placed at the top of a steering wheel in a car.
>
> **Adopted scope:** cat alive status
>
> **Extracted A:** live cat
>
> **Extracted B:** stuffed animal not established cat
>
> **Recorded reason, verbatim:** The stuffed toy is not established as a cat and is not a live animal.

**Audit explanation:** B establishes an unspecified stuffed toy. An actual cat's living status remains unavailable.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 295. train_3059: `animal inside of a car`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A cat standing on the back of the passenger side seat of a car.
>
> **Caption B:** A stuffed animal is placed at the top of a steering wheel in a car.
>
> **Adopted scope:** actual car animal
>
> **Extracted A:** cat
>
> **Extracted B:** stuffed toy
>
> **Recorded reason, verbatim:** A stuffed toy does not satisfy the literal animal-in-car condition.

**Audit explanation:** B establishes a stuffed toy. Actual animal presence remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 296. train_3081: `color of airplane`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A Virgin America airplane parked at an airport with a purple sunset in the background.
>
> **Caption B:** A blue, red and white jet airplane flying in a mostly clear blue sky.
>
> **Adopted scope:** airplane colors
>
> **Extracted A:** airline named; paint unspecified
>
> **Extracted B:** blue red white
>
> **Recorded reason, verbatim:** Airline branding does not establish the first aircraft's actual paint colors.

**Audit explanation:** A names the airline and colors the sunset. Airplane color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 297. train_3093: `Location of water`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** One elephant is enjoying the water from the waterfall and the other elephant is enjoying standing in the water.
>
> **Caption B:** An elephant reaching out with its trunk to a person with his hand in a bucket.
>
> **Adopted scope:** water location
>
> **Extracted A:** waterfall and pool
>
> **Extracted B:** bucket contents unstated
>
> **Recorded reason, verbatim:** A hand in a bucket does not establish that the bucket contains water.

**Audit explanation:** B identifies a bucket. Water inside the bucket remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 298. train_3098: `room configuration`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** This is a small studio apartment, and the bedroom and living space is in one room. 
>
> **Caption B:** This living room has a sectional couch, a coffee table, a shelf with movies, and a spiral candle holder on the wall.
>
> **Adopted scope:** combined versus separated room configuration
>
> **Extracted A:** bedroom and living area explicitly combined in studio
>
> **Extracted B:** living-room furniture, relation to sleeping area unspecified
>
> **Recorded reason, verbatim:** The second does not establish a dedicated separated room or any comparable multiroom configuration.

**Audit explanation:** B inventories a living room. Its relationship to sleeping areas remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 299. train_3107: `person's age`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A girl holding an umbrella, reading the paper, and listening to headphones on a street corner.
>
> **Caption B:** a female in a blue shirt and a black umbrella a street and people
>
> **Adopted scope:** person age
>
> **Extracted A:** girl
>
> **Extracted B:** female of unspecified age
>
> **Recorded reason, verbatim:** Female identifies gender but does not establish the second person's age.

**Audit explanation:** B identifies a female. Age category remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 300. train_3110: `person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A person curled up next to a suitcase on the floor near a collection of clothes and other personal items.
>
> **Caption B:** There is a messy living room area with some things thrown on the floor and coffee table
>
> **Adopted scope:** person type/presence
>
> **Extracted A:** person present
>
> **Extracted B:** no person stated
>
> **Recorded reason, verbatim:** A messy living room alone does not establish a described person.

**Audit explanation:** B describes a messy room. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 301. train_3111: `location of table`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A person curled up next to a suitcase on the floor near a collection of clothes and other personal items.
>
> **Caption B:** There is a messy living room area with some things thrown on the floor and coffee table
>
> **Adopted scope:** table location
>
> **Extracted A:** no table stated
>
> **Extracted B:** living room
>
> **Recorded reason, verbatim:** The first caption has no table to locate.

**Audit explanation:** A describes a person and luggage. A table remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 302. train_3121: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman under covers reading a book with a black cat grooming itself beside her in the bed.
>
> **Caption B:** A little girl sleeping next to a cat on a bed covered with pink and white sheets.
>
> **Adopted scope:** cat color
>
> **Extracted A:** black
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Pink and white describe bedding, not the second cat's color.

**Audit explanation:** B colors the sheets. Cat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 303. train_3131: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in yellow doing a trick with his skis down the side of a mountain.
>
> **Caption B:** A snow skateboarder going down a slope with the ski lift in the background.
>
> **Adopted scope:** clothing color
>
> **Extracted A:** yellow
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second snowboarder's clothing color is absent.

**Audit explanation:** B leaves clothing color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 304. train_3144: `color of purse`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A yellow and orange cat laying next to a black purse on a floor.
>
> **Caption B:** A cat with a serious look sitting on a suit case flap on a bed.
>
> **Adopted scope:** bag color
>
> **Extracted A:** black purse
>
> **Extracted B:** suitcase color unspecified
>
> **Recorded reason, verbatim:** The second suitcase is neither an established purse nor supplied with a color.

**Audit explanation:** B's suitcase color remains unspecified under the recorded bag-color scope.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 305. train_3158: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The sky is cloudy but umbrellas are up in a black and white photo.
>
> **Caption B:** An aerial view of umbrellas that are red and yellow and green and yellow.
>
> **Adopted scope:** umbrella colors
>
> **Extracted A:** monochrome image; actual hues unknown
>
> **Extracted B:** red yellow green
>
> **Recorded reason, verbatim:** A monochrome photograph does not supply the first umbrellas' actual colors.

**Audit explanation:** A specifies monochrome photography. Actual umbrella hues remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 306. train_3161: `number of surfaces`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A picture of seven tomatoes, one melon, a sack of grapes, a bag of carrots, two onions and peppers or cucumbers.
>
> **Caption B:** Fruits and vegetables are on a gray surface and include apples, oranges, bananas, cauliflower and other items.
>
> **Adopted scope:** support-surface count
>
> **Extracted A:** surface unstated
>
> **Extracted B:** one grey surface
>
> **Recorded reason, verbatim:** The first arrangement supplies no supporting-surface count.

**Audit explanation:** A lists produce. Supporting surfaces remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `5.0`.

### 307. train_3172: `object used by people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A man taking a picture of his friend on the beach with a para sail.
>
> **Caption B:** A surf board is perched on the beach while two people explore the ocean without it.
>
> **Adopted scope:** objects actually used by the people
>
> **Extracted A:** camera for photographing and parasail associated with friend
>
> **Extracted B:** surfboard explicitly left unused; no used object described
>
> **Recorded reason, verbatim:** The second people explore without the surfboard, so it cannot supply the requested used-object value.

**Audit explanation:** B explicitly leaves its surfboard unused. An object used by the people remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 308. train_3179: `location in room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** An old fireplace is in the middle of the living room near a computer desk and stairs.
>
> **Caption B:** A room with a wooden floor, a heater and a office chair, a table and windows with curtains that are open.
>
> **Adopted scope:** fixture location
>
> **Extracted A:** central fireplace near desk/stairs
>
> **Extracted B:** heater placement unspecified
>
> **Recorded reason, verbatim:** The second heater's location within the room is not supplied.

**Audit explanation:** B lists a heater and furniture. Their locations within the room remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 309. train_3184: `color of plate`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white plate with a piece of cake next to a puff of whipped cream.
>
> **Caption B:** a plate with a sandwich on it with a side of salad and ketchup
>
> **Adopted scope:** plate color
>
> **Extracted A:** white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second plate has no stated color.

**Audit explanation:** B leaves plate color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 310. train_3192: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** two horse riders wearing green and white and the horses are brown and black
>
> **Caption B:** A horse race with the number four horse and jockey ahead of another horse, on a grass track.
>
> **Adopted scope:** rider clothing color
>
> **Extracted A:** green and white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second jockey's outfit colors are unstated.

**Audit explanation:** B leaves jockey clothing colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 311. train_3193: `presence of horse number`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** two horse riders wearing green and white and the horses are brown and black
>
> **Caption B:** A horse race with the number four horse and jockey ahead of another horse, on a grass track.
>
> **Adopted scope:** horse-number presence
>
> **Extracted A:** unmentioned
>
> **Extracted B:** number four
>
> **Recorded reason, verbatim:** The first horses' numbers are unmentioned, which does not establish absence.

**Audit explanation:** A leaves any number displayed on the horse unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 312. train_3225: `size of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A house with a satellite dish has a clock at the top of it.
>
> **Caption B:** A giant clock is on the wall of a brick building between two windows.
>
> **Adopted scope:** clock size
>
> **Extracted A:** unspecified
>
> **Extracted B:** giant
>
> **Recorded reason, verbatim:** Placing a clock on a house does not establish its size.

**Audit explanation:** A leaves clock size unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 313. train_3231: `location of rooms`

**Current status:** `excluded_scope`. **Semantic rating:** `excluded/null`. **Policy:** `S7`.

> **Caption A:** A table set for two with a man in the kitchen next to it
>
> **Caption B:** a bathroom with a silver mirror above a white sink with a wood countertop
>
> **Adopted scope:** room location: category versus physical placement
>
> **Extracted A:** kitchen scene; placement within building unstated
>
> **Extracted B:** bathroom scene; placement within building unstated
>
> **Recorded reason, verbatim:** A household-location-category reading compares kitchen and bathroom as different. A literal location-of-rooms reading asks their placement within a building, which is wholly missing. Both are ordinary plausible feature interpretations.

**Audit explanation:** Room category yields kitchen versus bathroom. Placement within the building remains unspecified for both rooms. The intended feature remains unresolved.

**Recorded scope readings:**

> - **household room category:** rating 1. A: kitchen. B: bathroom.
> - **placement within building:** invalid. A: placement unstated. B: placement unstated.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 314. train_3237: `cleanliness of kitchen`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Pots and utensils hanging from the ceiling in a kitchen with an oven, microwave and dishwasher.
>
> **Caption B:** A wooden floor inside of a kitchen next to a stove top oven .
>
> **Adopted scope:** kitchen cleanliness
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Appliances, hanging utensils and wood floor do not establish cleanliness in either kitchen.

**Audit explanation:** Both captions leave kitchen cleanliness unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 315. train_3259: `player's position related to net`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A tennis player on a clay court reacting to a shot at the net.
>
> **Caption B:** A young man prepares to hit a tennis ball as it comes towards him.
>
> **Adopted scope:** player-net proximity
>
> **Extracted A:** at net
>
> **Extracted B:** net position unstated
>
> **Recorded reason, verbatim:** The second player prepares for a ball but has no stated relation to the net.

**Audit explanation:** B describes a tennis shot. The player's position relative to the net remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 316. train_3275: `number of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A young girl lays on her side in a bed while using a computer.
>
> **Caption B:** A girl sleeping on one end of a couch with a cat sleeping on the other end.
>
> **Adopted scope:** animal count
>
> **Extracted A:** none established
>
> **Extracted B:** one cat
>
> **Recorded reason, verbatim:** The computer-using girl has no described animal; the other scene has one cat.

**Audit explanation:** A describes a girl and computer. Nonhuman animal presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 317. train_3277: `color of dog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A beagle with a red collar is looking out over a body of water.
>
> **Caption B:** A white dog with it's head hanging out of the side of a window.
>
> **Adopted scope:** dog coat color
>
> **Extracted A:** beagle color unspecified
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** A beagle's collar color does not supply the dog's coat color.

**Audit explanation:** A colors the collar red. Beagle coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 318. train_3284: `type of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A group of three toilets with a person standing in front of the middle one.
>
> **Caption B:** A man sits at a table and points at a toilet seat by the table.
>
> **Adopted scope:** room type
>
> **Extracted A:** toilet area ordinarily a restroom
>
> **Extracted B:** table-based indoor area with toilet seat
>
> **Recorded reason, verbatim:** A toilet seat beside a table does not establish the second room's function, following confirmed #31.

**Audit explanation:** B supplies a table and detached toilet seat. Room function remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 319. train_3285: `number of toilets`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A group of three toilets with a person standing in front of the middle one.
>
> **Caption B:** A man sits at a table and points at a toilet seat by the table.
>
> **Adopted scope:** whole-toilet count
>
> **Extracted A:** three
>
> **Extracted B:** detached toilet seat only
>
> **Recorded reason, verbatim:** A toilet seat beside the table does not establish a complete toilet to count.

**Audit explanation:** B identifies a detached toilet seat. A whole toilet remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 320. train_3301: `proximity of person to skateboard`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A person laying on the ground and a skateboard is a distance from him.
>
> **Caption B:** An outdoor park area with a bench that has a man laying on his back and sleeping.
>
> **Adopted scope:** person-skateboard distance
>
> **Extracted A:** separated by distance
>
> **Extracted B:** no skateboard stated
>
> **Recorded reason, verbatim:** The second caption supplies no skateboard for a distance comparison.

**Audit explanation:** B describes a sleeping man. A skateboard and its distance remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 321. train_3305: `location in skate park`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young man on a skate board caught in mid air while doing a jump
>
> **Caption B:** A skateboarder wearing a hoodie flies off a ramp with a rail in the background.
>
> **Adopted scope:** skatepark location
>
> **Extracted A:** airborne but exact site unspecified
>
> **Extracted B:** off ramp
>
> **Recorded reason, verbatim:** The first airborne skateboarder has no specified skatepark feature or location within a park.

**Audit explanation:** A's airborne jump leaves skatepark location unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 322. train_3325: `identity of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A baseball game with the pitcher in throwing motion and the batter swinging his bat at the ball.
>
> **Caption B:** A man is holding a bat to swing as a man holds out his glove behind him.
>
> **Adopted scope:** person identity
>
> **Extracted A:** unnamed players
>
> **Extracted B:** unnamed men
>
> **Recorded reason, verbatim:** The baseball participants are unnamed, so individual identity is unavailable.

**Audit explanation:** Both captions leave the players' personal identities unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 323. train_3332: `proximity of man to ground`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A man sitting and looking at a monitor with a pen in his mouth.
>
> **Caption B:** Man laying on floor, in front of bed, with a laptop on his lap
>
> **Adopted scope:** man's proximity to floor
>
> **Extracted A:** sitting, support and floor relation unstated
>
> **Extracted B:** lying on floor
>
> **Recorded reason, verbatim:** Sitting alone does not establish whether the first man is on the floor or elevated on a seat.

**Audit explanation:** A supplies a seated posture. Support and ground-relative distance remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 324. train_3333: `location of screen`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A man sitting and looking at a monitor with a pen in his mouth.
>
> **Caption B:** Man laying on floor, in front of bed, with a laptop on his lap
>
> **Adopted scope:** screen placement
>
> **Extracted A:** monitor position unstated
>
> **Extracted B:** laptop on lap
>
> **Recorded reason, verbatim:** Looking at a monitor supplies no support or placement for the first screen; the other laptop rests on a lap.

**Audit explanation:** A leaves monitor position unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 325. train_3340: `quantity of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A dish with food is sitting in a toaster oven that has its door partially open.
>
> **Caption B:** The kitchen has a built-in oven and microwave next to a tall built-in wine rack.
>
> **Adopted scope:** food quantity
>
> **Extracted A:** one dish of food
>
> **Extracted B:** no food stated
>
> **Recorded reason, verbatim:** The second kitchen describes appliances and a wine rack but no quantity of food.

**Audit explanation:** B lists kitchen appliances. Food presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 326. train_3342: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a man and child riding a sled across a frozen lake using an umbrella as a sail.
>
> **Caption B:** A person in a black snowsuit pulls a kid on a sleigh who is holding a birghtly colored umbrella.
>
> **Adopted scope:** umbrella color
>
> **Extracted A:** unspecified
>
> **Extracted B:** brightly colored
>
> **Recorded reason, verbatim:** The first umbrella has no color information; the black snowsuit belongs to a person in the other scene.

**Audit explanation:** A leaves umbrella and principal object colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 327. train_3355: `presence of spectators`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A woman in a black tennis outfit playing tennis on a red clay court.
>
> **Caption B:** A tennis player serving the ball on the courts as spectators watch from the stands.
>
> **Adopted scope:** spectator presence
>
> **Extracted A:** unmentioned
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** The first tennis caption does not establish spectator presence or absence.

**Audit explanation:** A describes a tennis player. Spectator presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 328. train_3359: `name of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a person waiting to perform a trick on a skateboard at a skate park
>
> **Caption B:** a person with ripped pants and one leg up and one down, falling off of a skateboard.
>
> **Adopted scope:** place type
>
> **Extracted A:** skatepark
>
> **Extracted B:** site unspecified
>
> **Recorded reason, verbatim:** Only the first caption identifies a skate park; the fall's location is unspecified.

**Audit explanation:** B describes a skateboard fall. Place remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 329. train_3369: `color of fire truck`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A red and white fire truck is parked on the side of the road.
>
> **Caption B:** A couple of fire trucks from the City of Seattle at a fire station.
>
> **Adopted scope:** truck color
>
> **Extracted A:** red and white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Seattle fire trucks are named without color; municipal identity does not supply their paint colors.

**Audit explanation:** B names the trucks' city. Truck colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 330. train_3371: `kitchen`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A kitchen has green shutter doors, a gas range, a small table, and wooden cabinets.
>
> **Caption B:** A coffee table and a checkered rug is in between a couch and a love seat.
>
> **Adopted scope:** kitchen type
>
> **Extracted A:** kitchen
>
> **Extracted B:** living-room seating scene
>
> **Recorded reason, verbatim:** The second caption describes living-room seating but no kitchen entity.

**Audit explanation:** B describes living-room seating. Kitchen presence remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 331. train_3377: `size of bus`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Part of a double decker bus stands on display in front of a building.
>
> **Caption B:** A bus with blue and yellow on it, sitting on the side of the road.
>
> **Adopted scope:** bus size
>
> **Extracted A:** partial double-decker
>
> **Extracted B:** bus size unspecified
>
> **Recorded reason, verbatim:** The second bus has no size value; its color and roadside location do not supply one.

**Audit explanation:** B identifies a bus. Bus size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 332. train_3381: `type of aerial objects`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A lot of different colored kites flying in a cloudy blue sky over a beach and ocean.
>
> **Caption B:** People are walking around a field waving flags and watching flying things in the air.
>
> **Adopted scope:** type of flying object
>
> **Extracted A:** kites
>
> **Extracted B:** unspecified flying things
>
> **Recorded reason, verbatim:** The second caption does not identify what is flying, so the requested object type is unavailable.

**Audit explanation:** B identifies flying things. The types of flying objects remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 333. train_3384: `age of structures`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A street in an older town with older building down both sides as traffic passes by.
>
> **Caption B:** A view of a city with a bridge crossing over water and a clock tower.
>
> **Adopted scope:** structure age
>
> **Extracted A:** old buildings
>
> **Extracted B:** age unspecified
>
> **Recorded reason, verbatim:** The second bridge and clock tower have no stated or directly established age.

**Audit explanation:** B identifies structures. Their ages remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 334. train_3403: `Presence of napkin`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** I table with a cup of coffee and a doughnut with sprinkles on it.
>
> **Caption B:** A laptop and papers are on a desk with a donut, napkin, and mug of coffee.
>
> **Adopted scope:** napkin presence
>
> **Extracted A:** unmentioned
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** The first table description does not establish whether a napkin is present.

**Audit explanation:** A describes coffee and a doughnut. Napkin presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 335. train_3405: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A red Umbrella and white chair sitting on the beach in front of a cloudy, blue sky. 
>
> **Caption B:** An umbrella is standing in the sand at the end of the path next to an ocean.
>
> **Adopted scope:** umbrella color
>
> **Extracted A:** red
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second umbrella has no specified color.

**Audit explanation:** B leaves umbrella color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 336. train_3409: `type of object`

**Current status:** `excluded_scope`. **Semantic rating:** `excluded/null`. **Policy:** `S7`.

> **Caption A:** A meal of a noodle bowl with chop sticks and a drink sits on a table.
>
> **Caption B:** A spoon blacked in a bowl of soup containing noodles, peppers, and green onions.
>
> **Adopted scope:** principal comparable dining object
>
> **Extracted A:** noodle bowl with chopsticks
>
> **Extracted B:** noodle soup bowl with spoon
>
> **Recorded reason, verbatim:** The first centers a noodle-bowl meal with chopsticks, while the second introduces a spoon in a noodle-soup bowl. Comparable food vessels support 5, but the salient utensils or bowl-versus-spoon foreground objects support 2. The generic object condition and mixed foregrounding do not select a stable referent without adding an assumption.

**Audit explanation:** The bowls match as noodle bowls. The utensils differ as chopsticks versus a spoon. The intended object referent remains unresolved.

**Recorded scope readings:**

> - **principal comparable bowls:** rating 5. A: noodle bowl. B: noodle soup bowl.
> - **eating utensils:** rating 2. A: chopsticks. B: spoon.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 337. train_3424: `number of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A dog is standing and looking through the threshold into a room with sinks and and a mirror
>
> **Caption B:** A bathroom with a sink, a mirror, and the image of a toilet in the mirror.
>
> **Adopted scope:** animal count
>
> **Extracted A:** one dog
>
> **Extracted B:** no animal stated
>
> **Recorded reason, verbatim:** The second bathroom caption supplies no animal to count.

**Audit explanation:** B describes bathroom fixtures. Animal presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 338. train_3429: `view of sign`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A stop light at a street with a marijuana leaf on the green sign.
>
> **Caption B:** A close up photograph of a sign relating to a round about with arrows going a circle.
>
> **Adopted scope:** sign viewpoint
>
> **Extracted A:** unspecified
>
> **Extracted B:** close-up
>
> **Recorded reason, verbatim:** The first street-sign caption does not describe the camera distance or viewpoint.

**Audit explanation:** A leaves viewing distance and sign framing unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 339. train_3444: `name of places`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A close up of the sign at the intersection of Broadway and Wall St, in New York city
>
> **Caption B:** a stop and go light and a building with a bicycle painted on it
>
> **Adopted scope:** place names
>
> **Extracted A:** Broadway / Wall St / New York City
>
> **Extracted B:** not provided
>
> **Recorded reason, verbatim:** The condition requests names of places. The second caption gives a light and building but no place name; substituting place type changes the requested feature.

**Audit explanation:** B identifies traffic fixtures and a building. Place name remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 340. train_3451: `number of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** a pepperoni and black olive pizza sitting in front of two dogs on the couch
>
> **Caption B:** A large pizza sits on a white plate on a table next to a plate of salad.
>
> **Adopted scope:** animal count
>
> **Extracted A:** two dogs
>
> **Extracted B:** none stated
>
> **Recorded reason, verbatim:** The second pizza scene supplies no animal count.

**Audit explanation:** B describes pizza and salad. Animal presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 341. train_3456: `number of beverages`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A plate with a hot dog with condiments on it, next to waffle-cut fries.
>
> **Caption B:** A tray holds a hotdog and french fries and there is a cup in the background.
>
> **Adopted scope:** beverage count
>
> **Extracted A:** no beverage or vessel
>
> **Extracted B:** cup implies one meal drink
>
> **Recorded reason, verbatim:** The first meal contains no beverage or drink vessel; the second meal's cup can support one beverage.

**Audit explanation:** A describes hotdogs and fries. A beverage or drink vessel remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 342. train_3473: `type of event`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bowl of different types of fruit displayed on a table during a party.
>
> **Caption B:** A bowl containing peaches, oranges, bananas, apples, and pears sits next to a picture and bottle. 
>
> **Adopted scope:** event type
>
> **Extracted A:** party
>
> **Extracted B:** event unspecified
>
> **Recorded reason, verbatim:** The second fruit arrangement has no named occasion or event.

**Audit explanation:** B identifies a fruit arrangement. Event type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 343. train_3484: `Presence of drink`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A black and white image of some electronics near a pen and cup of coffee.
>
> **Caption B:** A dark room is lit up with a small desk lamp positioned over a laptop computer.
>
> **Adopted scope:** drink presence
>
> **Extracted A:** coffee present
>
> **Extracted B:** no drink/vessel stated
>
> **Recorded reason, verbatim:** The laptop-and-lamp caption establishes no beverage or supported absence of one.

**Audit explanation:** B describes a laptop and lamp. Drink presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 344. train_3493: `color of t-shirt`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man holds a tennis racket as he wears blue shorts and a white t-shirt.
>
> **Caption B:** A double image of a male tennis player attempting to hit a tennis ball.
>
> **Adopted scope:** shirt color
>
> **Extracted A:** white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second tennis player's shirt color is unspecified.

**Audit explanation:** B leaves T-shirt color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 345. train_3495: `size of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young girl in a winter coat and sunglasses holds a racquet on an indoor court
>
> **Caption B:** A girl balancing an over sized tennis ball on a racket while a man and woman walk side by side behind her.
>
> **Adopted scope:** size of described tennis equipment
>
> **Extracted A:** racquet, size unstated; no ball mentioned
>
> **Extracted B:** oversized tennis ball and unsized racket
>
> **Recorded reason, verbatim:** The first caption provides no equipment-size value or tennis ball; choosing the common rackets also leaves size unstated.

**Audit explanation:** A leaves racquet size unspecified. A ball comparable with B's large tennis ball remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 346. train_3507: `number of beverages`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A person eating at a restaurant with a plate of pancakes, fruit and bacon and eggs
>
> **Caption B:** A plate of food and a cup of coffee that appears to be breakfast.
>
> **Adopted scope:** beverage count
>
> **Extracted A:** no drink/vessel stated
>
> **Extracted B:** one coffee cup
>
> **Recorded reason, verbatim:** The first breakfast mentions no drink or drink vessel; the second explicitly includes one coffee.

**Audit explanation:** A describes breakfast foods. A beverage or drink vessel remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 347. train_3508: `activity of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A museum display of a large silver plane next to a small black and yellow plane.
>
> **Caption B:** A group of people are looking at a chrome airplane in front of a hangar.
>
> **Adopted scope:** people activity
>
> **Extracted A:** no people described
>
> **Extracted B:** viewing airplane
>
> **Recorded reason, verbatim:** The museum-plane display has no described people or activity to compare with viewing the plane.

**Audit explanation:** A describes displayed airplanes. Human presence and activity remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 348. train_3509: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A museum display of a large silver plane next to a small black and yellow plane.
>
> **Caption B:** A group of people are looking at a chrome airplane in front of a hangar.
>
> **Adopted scope:** people count
>
> **Extracted A:** none established
>
> **Extracted B:** group
>
> **Recorded reason, verbatim:** An aircraft museum display does not establish any people in the first caption.

**Audit explanation:** A describes displayed airplanes. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 349. train_3511: `presence of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A person sitting in a chair with a laptop and a dog laying beside them.
>
> **Caption B:** A guy on a couch with a laptop and a big book in his lap.
>
> **Adopted scope:** animal presence
>
> **Extracted A:** dog present
>
> **Extracted B:** unmentioned
>
> **Recorded reason, verbatim:** The second laptop user has no stated animal; absence cannot be inferred from omission.

**Audit explanation:** B describes a laptop user. Animal presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 350. train_3513: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A man is sitting on the edge of a train track, touching a locomotive.
>
> **Caption B:** A set of train tracks with a train engine and passenger cars parked on the track.
>
> **Adopted scope:** people count
>
> **Extracted A:** one man
>
> **Extracted B:** none stated
>
> **Recorded reason, verbatim:** The second train scene states no person count.

**Audit explanation:** B describes trains and tracks. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 351. train_3521: `type of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Bowls of candy and nuts sit beside a large vase of flowers and plates.
>
> **Caption B:** A green and white table topped with blue glass plates and a vase filled with flowers.
>
> **Adopted scope:** food type
>
> **Extracted A:** candy nuts
>
> **Extracted B:** no food stated
>
> **Recorded reason, verbatim:** The second table has plates and flowers without identified food.

**Audit explanation:** B lists tableware and flowers. Food presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 352. train_3536: `location name`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man wearing a brown shirt and blue jeans is in the kitchen with a pepperoni pizza
>
> **Caption B:** A papa johns pizza sitting in a box next to a cup of garlic sauce and a pepperoncini.
>
> **Adopted scope:** food venue
>
> **Extracted A:** kitchen
>
> **Extracted B:** boxed pizza venue unknown
>
> **Recorded reason, verbatim:** Pizza branding and its box do not establish the second food's venue.

**Audit explanation:** B identifies a branded pizza box. The venue remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 353. train_3537: `color of shirt`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A man wearing a brown shirt and blue jeans is in the kitchen with a pepperoni pizza
>
> **Caption B:** A papa johns pizza sitting in a box next to a cup of garlic sauce and a pepperoncini.
>
> **Adopted scope:** shirt color
>
> **Extracted A:** brown
>
> **Extracted B:** no shirt/person stated
>
> **Recorded reason, verbatim:** The second caption mentions no person or shirt whose color could be compared.

**Audit explanation:** B describes boxed pizza. A person and shirt remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 354. train_3542: `activity of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A person sitting down with a laptop on their lap in front of a smart phone in a living room with a TV on.
>
> **Caption B:** A living room area that has a desk with a desktop computer, and a television in the corner of the room.
>
> **Adopted scope:** people activity
>
> **Extracted A:** sitting with laptop
>
> **Extracted B:** no people stated
>
> **Recorded reason, verbatim:** The second furnished living room contains no stated person or human action.

**Audit explanation:** B lists room contents. Human presence and activity remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 355. train_3565: `number of vehicles`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A STOP sign on a pole in the dirt by a road and a sidewalk, with a car and building in background.
>
> **Caption B:** A silver and yellow fire hydrant in the grass near a traffic sign in the street on a wood pole.
>
> **Adopted scope:** vehicle count
>
> **Extracted A:** one car
>
> **Extracted B:** no vehicle stated
>
> **Recorded reason, verbatim:** The second hydrant scene supplies no vehicle count.

**Audit explanation:** B describes a hydrant and sign. Vehicle presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 356. train_3568: `reflection of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:**  A man lies in bed resting while a small black and white cat wearing a cone, lies on top of him
>
> **Caption B:** A black cat is lying down, with part of its body being reflected in the glass surface to its left.
>
> **Adopted scope:** cat reflection
>
> **Extracted A:** unmentioned
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** The first cat has no stated reflection or reflecting surface.

**Audit explanation:** A describes a cat lying on a man. An animal reflection remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 357. train_3575: `number of cakes`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Husband and wife at a wedding reception ready to jointly cut the wedding cake.
>
> **Caption B:** A quite happy couple appear to be in the middle of their wedding ceremony.
>
> **Adopted scope:** cake count
>
> **Extracted A:** one wedding cake
>
> **Extracted B:** cake unmentioned
>
> **Recorded reason, verbatim:** A wedding ceremony alone does not establish a cake count.

**Audit explanation:** B describes a wedding ceremony. Cake presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `5.0`.

### 358. train_3586: `nearness of window`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A compute on a desk in front of a window with the shades drawn.
>
> **Caption B:** A desk holding a laptop with extra keyboard, mouse, speakers, telephone and empty wine glass.
>
> **Adopted scope:** window proximity
>
> **Extracted A:** desk in front of window
>
> **Extracted B:** window unstated
>
> **Recorded reason, verbatim:** The second desk has no stated window or proximity to one.

**Audit explanation:** B lists desk equipment. A window and its nearness remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 359. train_3597: `Vehicles in area`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A street with park cars and a mailbox on the corner and lots of buildings.
>
> **Caption B:** A an intersection with a traffic signal and crossing sign near a rural development with brick houses.
>
> **Adopted scope:** vehicle presence/type
>
> **Extracted A:** parked cars
>
> **Extracted B:** no vehicles stated
>
> **Recorded reason, verbatim:** The second road intersection establishes no vehicle despite its traffic signs.

**Audit explanation:** B describes an intersection. Vehicle presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 360. train_3599: `name of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A room with lots of china and what appears to be Thai art on the walls.
>
> **Caption B:** Interior photo showing a toilet, desk and chair and objects hanging on the walls.
>
> **Adopted scope:** functional place category
>
> **Extracted A:** room function unspecified; china and wall art
>
> **Extracted B:** interior containing toilet, desk, and chair
>
> **Recorded reason, verbatim:** China and wall art do not establish the first room's function; generic decoration is insufficient to compare with the bathroom-related second interior.

**Audit explanation:** A supplies china and wall art. Room function and place name remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 361. train_3603: `place of sitting`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A woman wearing sunglasses and with a hat on her knees laying on a bench in front of a tree.
>
> **Caption B:** A woman sits on a beach in a floral print dress and holds a black umbrella.
>
> **Adopted scope:** place occupied while sitting
>
> **Extracted A:** no sitting person; woman lying on bench
>
> **Extracted B:** woman sitting on beach
>
> **Recorded reason, verbatim:** The first woman is lying rather than sitting, so the requested sitting role is not present in both captions.

**Audit explanation:** A describes a woman lying on a bench. The requested sitting relation remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 362. train_3605: `size of container`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** there is a whine glass and a tall glass sitting on a bar table
>
> **Caption B:** A glass with a quarter of a cup of wine on top of a table.
>
> **Adopted scope:** glass size
>
> **Extracted A:** one tall plus wine glass
>
> **Extracted B:** glass size unspecified
>
> **Recorded reason, verbatim:** A quarter cup of wine measures contents, not the capacity or size of its glass.

**Audit explanation:** B states wine quantity. Glass size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 363. train_3610: `type of game controllers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two men have game controllers in their hands and are playing an interactive game.
>
> **Caption B:** A young man sitting next to a young woman both of which are holding Nintendo Wii controllers.
>
> **Adopted scope:** game-controller subtype
>
> **Extracted A:** unspecified game controllers
>
> **Extracted B:** Nintendo Wii controllers
>
> **Recorded reason, verbatim:** Interactive game describes the game, without identifying a controller subtype comparable to Nintendo Wii controllers.

**Audit explanation:** A identifies generic controllers. Controller type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 364. train_3614: `number of seats`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A wall of window stands near a brown couch and a wood coffee table and book shelves.
>
> **Caption B:** The living room is rather sparsely furnished, but has electronics, magazines, a gold fish bowl and slippers.
>
> **Adopted scope:** seat count
>
> **Extracted A:** one couch
>
> **Extracted B:** seats unmentioned
>
> **Recorded reason, verbatim:** Sparse furnishing and electronics do not identify any seat count in the second room.

**Audit explanation:** B lists living-room contents. Seats remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 365. train_3637: `presence of fire hydrant`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A kid with a bat in their hand swinging at a ball on top of a red and white fire hydrant.
>
> **Caption B:** A person spraying water from a hose, onto an umbrella being held by a child.
>
> **Adopted scope:** hydrant presence
>
> **Extracted A:** present
>
> **Extracted B:** unmentioned
>
> **Recorded reason, verbatim:** The hose scene does not mention a hydrant or establish its absence.

**Audit explanation:** B describes a hose spraying an umbrella. Hydrant presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 366. train_3659: `animal's age`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A kitten plays on a hardwood floor while a larger couch stands on a couch.
>
> **Caption B:** A cat laying on a couch with a sheet and a remote on it.
>
> **Adopted scope:** cat age
>
> **Extracted A:** kitten plus larger cat
>
> **Extracted B:** age unspecified
>
> **Recorded reason, verbatim:** The second cat has no age description, so its age cannot be compared with the kitten.

**Audit explanation:** B identifies a cat. Age remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 367. train_3667: `presence of cars`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A bench next to a city street filled with cars with their lights on.
>
> **Caption B:** A silver and red fire hydrant sitting on a sidewalk next to a street.
>
> **Adopted scope:** car presence
>
> **Extracted A:** present
>
> **Extracted B:** unmentioned
>
> **Recorded reason, verbatim:** The second street scene does not state any car presence or supported absence.

**Audit explanation:** B describes a hydrant and street. Car presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 368. train_3682: `view of toilet`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black and white photo of a dirty bathroom with focus on the toilet.
>
> **Caption B:** A toilet mounted on a plywood base and an old bathtub with a plywood side.
>
> **Adopted scope:** toilet viewpoint
>
> **Extracted A:** focused monochrome photo
>
> **Extracted B:** viewpoint unspecified
>
> **Recorded reason, verbatim:** The second toilet's mounting materials do not establish the photographic viewpoint or view treatment.

**Audit explanation:** B identifies a mounted toilet. Viewing perspective remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 369. train_3683: `plywood mounted toilet`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black and white photo of a dirty bathroom with focus on the toilet.
>
> **Caption B:** A toilet mounted on a plywood base and an old bathtub with a plywood side.
>
> **Adopted scope:** plywood toilet mounting
>
> **Extracted A:** mount material unspecified
>
> **Extracted B:** plywood base
>
> **Recorded reason, verbatim:** The first toilet's mounting material is unreported.

**Audit explanation:** A leaves toilet mounting material and plywood-base presence unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 370. train_3699: `elevation of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A man in a red tee shirt in the middle of a skating trick
>
> **Caption B:** A man in the air with a skateboard in front of a cement wall.
>
> **Adopted scope:** person elevation
>
> **Extracted A:** trick phase without height
>
> **Extracted B:** airborne
>
> **Recorded reason, verbatim:** Being in the middle of a skating trick does not establish whether the first rider is airborne or grounded.

**Audit explanation:** A describes a skating trick. The person's elevation remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 371. train_3706: `layout of area`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** a toilet in a small and cramped area with a door next to it
>
> **Caption B:** A bathroom with wall papered walls, a toilet with a wood lid and two rolls of tissue.
>
> **Adopted scope:** toilet-area layout
>
> **Extracted A:** cramped beside door
>
> **Extracted B:** arrangement unspecified
>
> **Recorded reason, verbatim:** The second fixture and wallpaper descriptions do not establish the bathroom's layout or spacing.

**Audit explanation:** B lists fixtures and wallpaper. Spatial arrangement remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 372. train_3710: `presence of beach`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A beach area with people on the sand and various types of kites flying in the sky above.
>
> **Caption B:** A sandy terrain with footprints has a mirage of water in the near distance.
>
> **Adopted scope:** beach presence
>
> **Extracted A:** beach explicitly present
>
> **Extracted B:** sandy terrain with mirage; beach status unspecified
>
> **Recorded reason, verbatim:** Sand and a mirage do not establish a beach or its absence; the second caption lacks confirmed shoreline information.

**Audit explanation:** B establishes sand and a mirage. Beach location remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 373. train_3711: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A beach area with people on the sand and various types of kites flying in the sky above.
>
> **Caption B:** A sandy terrain with footprints has a mirage of water in the near distance.
>
> **Adopted scope:** people count
>
> **Extracted A:** plural people
>
> **Extracted B:** footprints without people
>
> **Recorded reason, verbatim:** Footprints do not establish currently present people or their count.

**Audit explanation:** B establishes footprints from prior passage. Current human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 374. train_3713: `color of sauce`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A hand holding a sandwich on hot dog bug slathered with green and white sauce.
>
> **Caption B:** A cheesy sandwich on a sub bun is sitting alongside french fries and waiting for the taking.
>
> **Adopted scope:** sauce color
>
> **Extracted A:** green and white
>
> **Extracted B:** cheese but sauce color unspecified
>
> **Recorded reason, verbatim:** The second sandwich supplies no sauce color; cheese does not identify one.

**Audit explanation:** B identifies cheese. Sauce color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 375. train_3744: `state of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** This disgusting public restroom is getting cleaned but it needs a lot of work.
>
> **Caption B:** A bathroom with blue walls has a window, a sink, a bathub, and a toilet.
>
> **Adopted scope:** room condition
>
> **Extracted A:** dirty being cleaned
>
> **Extracted B:** cleanliness unspecified
>
> **Recorded reason, verbatim:** Blue walls and a fixture list do not establish cleanliness in the second bathroom.

**Audit explanation:** B lists fixtures and wall color. Room condition remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 376. train_3752: `size of objects`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** room with a view has chairs, large table display with an array of objects on it
>
> **Caption B:** A room with a sunny window contains a plush desk chair and a wooden set of chairs and table with a laptop.
>
> **Adopted scope:** furniture size
>
> **Extracted A:** large table
>
> **Extracted B:** furniture dimensions unstated
>
> **Recorded reason, verbatim:** The second supplies no furniture dimensions or size description.

**Audit explanation:** B leaves furniture size and dimensions unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 377. train_3757: `items on table`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a close up of many different items on table with a cloth on top
>
> **Caption B:** An open book, stack of papers and magazines, beverages, and TV remotes on a coffee table.
>
> **Adopted scope:** table items
>
> **Extracted A:** unspecified assortment
>
> **Extracted B:** books papers drinks remotes
>
> **Recorded reason, verbatim:** The first caption names only generic items without any object identity to compare.

**Audit explanation:** A identifies an assortment. Tabletop item identities remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 378. train_3758: `presence of plate on table`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Three bowls of various foods is located at a table with people in the background.
>
> **Caption B:** a close up of a plate with a glass on it on a table
>
> **Adopted scope:** plate presence
>
> **Extracted A:** bowls only
>
> **Extracted B:** plate present
>
> **Recorded reason, verbatim:** Bowls do not establish either a plate or its absence in the first caption.

**Audit explanation:** A establishes bowls. Plate presence on the table remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 379. train_3759: `type of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Three bowls of various foods is located at a table with people in the background.
>
> **Caption B:** a close up of a plate with a glass on it on a table
>
> **Adopted scope:** food type
>
> **Extracted A:** various foods
>
> **Extracted B:** plate and glass without food
>
> **Recorded reason, verbatim:** The second plate-and-glass description establishes no food type.

**Audit explanation:** B establishes a plate and glass. Food presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 380. train_3762: `readiness of bathroom amenities`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bath and shower is ready for use with a towel and soap left on the side.
>
> **Caption B:** A small bathroom with a vanity on one side and the shower on the other.
>
> **Adopted scope:** bathroom amenity readiness
>
> **Extracted A:** explicitly ready with towel and soap
>
> **Extracted B:** shower and vanity present; readiness unstated
>
> **Recorded reason, verbatim:** Installed bathroom fixtures alone do not establish their readiness for use; only the first explicitly supplies that state.

**Audit explanation:** B locates bathroom fixtures. Their readiness for use remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 381. train_3776: `colors present in photo`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A vintage photo of a jockey sitting on a horse is colored black and white.
>
> **Caption B:** Old photo of a small boy wearing a cap gun and holster astride a dog.
>
> **Adopted scope:** photo colors
>
> **Extracted A:** black and white
>
> **Extracted B:** old image without color description
>
> **Recorded reason, verbatim:** An old photograph need not be monochrome; the second gives no photo colors.

**Audit explanation:** B calls the photograph old. Its color style remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 382. train_3803: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A fenced in area with a giraffe reaching it's neck and head over a fence that separates it from people.
>
> **Caption B:** A giraffe eats leaves from a tree as two ostriches stand in the background.
>
> **Adopted scope:** people count
>
> **Extracted A:** plural people
>
> **Extracted B:** no people stated
>
> **Recorded reason, verbatim:** The second supplies no people count.

**Audit explanation:** B describes a giraffe and ostriches. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 383. train_3805: `color of flag`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A street corner with a crosswalk and a building with a neon sign in the distance.
>
> **Caption B:** A corner store is has a red, white and blue flag in front of it.
>
> **Adopted scope:** flag color
>
> **Extracted A:** no flag stated
>
> **Extracted B:** red white blue
>
> **Recorded reason, verbatim:** The first establishes no flag whose color can be compared.

**Audit explanation:** A describes a street corner. Flag presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 384. train_3807: `obstruction of view`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A picture of a baseball game through a screen and someone's shadow blocking the view.
>
> **Caption B:** A baseball player is ready to swing at the ball as the catcher and umpire crouch behind him.
>
> **Adopted scope:** view obstruction
>
> **Extracted A:** screen and shadow
>
> **Extracted B:** obstruction unstated
>
> **Recorded reason, verbatim:** The second does not establish a clear or obstructed view; absence of an obstruction description is not proof of clarity.

**Audit explanation:** B leaves viewing obstruction unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 385. train_3813: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Woman cuddling a cat while sitting on a bed next to a lap top.
>
> **Caption B:** A gray tiger cat sleeping on top of a red and white checkered blanket.
>
> **Adopted scope:** people count
>
> **Extracted A:** one woman
>
> **Extracted B:** no person stated
>
> **Recorded reason, verbatim:** The second supplies no person or supported zero-person count.

**Audit explanation:** B describes a sleeping cat. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 386. train_3829: `type of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** There is a man eating at the table, And a cup of coffee alongside a croissant.
>
> **Caption B:** A table with plates and bowls of food on it and cups of coffee on saucers with spoons next to them.
>
> **Adopted scope:** food type
>
> **Extracted A:** croissant
>
> **Extracted B:** unspecified foods in plates and bowls
>
> **Recorded reason, verbatim:** The second supplies no food type beyond the target word food.

**Audit explanation:** B identifies generic plated and bowled food. Food types remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 387. train_3835: `type of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A plate of food on a counter and a bowl of food next to it.
>
> **Caption B:** a salad, and a fish sandwich, with a side of tartar sauce on a plate.
>
> **Adopted scope:** food type
>
> **Extracted A:** unspecified plate and bowl foods
>
> **Extracted B:** salad fish sandwich and tartar sauce
>
> **Recorded reason, verbatim:** The first supplies no food type beyond food in vessels.

**Audit explanation:** A identifies generic plated and bowled food. Food types remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 388. train_3843: `presence of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Above view of fruits and vegetables in wooden box with cat looking upwards as if to say, "what I'm I supposed to do with this?"
>
> **Caption B:** A variety of fruits and vegetables are displayed on a table with an orange and red table cloth.
>
> **Adopted scope:** animal presence
>
> **Extracted A:** cat present
>
> **Extracted B:** no animal presence information
>
> **Recorded reason, verbatim:** The second food display establishes neither animal presence nor absence.

**Audit explanation:** B describes produce. Animal presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 389. train_3877: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A man in a green shirt and straw hat on top of an elephant.
>
> **Caption B:** The elephant has a bird sitting on it's trunk and hay on it's back.
>
> **Adopted scope:** number of people
>
> **Extracted A:** one man
>
> **Extracted B:** no human described
>
> **Recorded reason, verbatim:** The second establishes no human count.

**Audit explanation:** B describes an elephant and bird. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 390. train_3886: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog on one side of a glass door and a cat on the other side.
>
> **Caption B:** A gray cat sitting on a blanket next to an orange and white cat.
>
> **Adopted scope:** animal colors
>
> **Extracted A:** no dog or cat colors supplied
>
> **Extracted B:** gray and orange-white cats
>
> **Recorded reason, verbatim:** The first supplies no dog or cat color.

**Audit explanation:** A leaves dog and cat coat colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 391. train_3889: `people's focus`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A person on skis looking at the view of a mountain and a lake from a hill top.
>
> **Caption B:** A group of people in ski gear on slope next to trees and mountains.
>
> **Adopted scope:** object of people's attention
>
> **Extracted A:** mountain and lake view
>
> **Extracted B:** attention unspecified
>
> **Recorded reason, verbatim:** The second specifies no object of the people's attention.

**Audit explanation:** B locates people on a slope. Their attention targets remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 392. train_3891: `number of toys`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A still life with a bowl of fruit and an iphone showing a photo of the arrangement.
>
> **Caption B:** there is a apple and two oranges and a stuffed animal on the bed
>
> **Adopted scope:** number of toys
>
> **Extracted A:** no toy established
>
> **Extracted B:** one stuffed animal
>
> **Recorded reason, verbatim:** Fruit and an iPhone do not establish a toy or a supported zero-toy count.

**Audit explanation:** A describes fruit and a phone. Toy presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 393. train_3906: `action performed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A woman holding a can of paint and a paintbrush next to a stop sign.
>
> **Caption B:** A stop sign with the word Stop Them on it below a one way.
>
> **Adopted scope:** person action
>
> **Extracted A:** holding paint can and brush
>
> **Extracted B:** no person action described
>
> **Recorded reason, verbatim:** The second describes altered sign text without establishing a currently performed person action.

**Audit explanation:** B describes signs. Human presence and action remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 394. train_3907: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A woman holding a can of paint and a paintbrush next to a stop sign.
>
> **Caption B:** A stop sign with the word Stop Them on it below a one way.
>
> **Adopted scope:** number of people
>
> **Extracted A:** one woman
>
> **Extracted B:** no people described
>
> **Recorded reason, verbatim:** The second has no people count or supported absence.

**Audit explanation:** B describes signs. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 395. train_3911: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A view outside a train window as it passes through the scenic mountain countryside.
>
> **Caption B:** This is a black and white photo of a train sitting on the tracks.
>
> **Adopted scope:** train color
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated despite monochrome photograph
>
> **Recorded reason, verbatim:** Neither train's actual color is given; photographic monochrome is not object color.

**Audit explanation:** Both captions leave train color unspecified. B supplies monochrome photographic style.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 396. train_3912: `variety of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A large pizza sits on a table, and a man has a piece on his plate.
>
> **Caption B:** Plates full of food sitting on top of a dinner table with red cloth.
>
> **Adopted scope:** food variety
>
> **Extracted A:** pizza
>
> **Extracted B:** unspecified foods on plates
>
> **Recorded reason, verbatim:** Generic foods on plates do not establish food varieties.

**Audit explanation:** B identifies generic plated food. Food variety remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 397. train_3916: `identity of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A baby in a high chair in front of a table with a variety of food lined out.
>
> **Caption B:** A boy holding a spoon up to his mouth and eating out of a bowl.
>
> **Adopted scope:** personal identity
>
> **Extracted A:** unnamed baby
>
> **Extracted B:** unnamed boy
>
> **Recorded reason, verbatim:** The captions do not identify either person by identity or name.

**Audit explanation:** Both captions leave the child's personal identity unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 398. train_3917: `name of dishes`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A baby in a high chair in front of a table with a variety of food lined out.
>
> **Caption B:** A boy holding a spoon up to his mouth and eating out of a bowl.
>
> **Adopted scope:** names of prepared dishes
>
> **Extracted A:** variety of unnamed food
>
> **Extracted B:** unnamed bowl contents
>
> **Recorded reason, verbatim:** A variety of food and unnamed bowl contents do not supply named dishes.

**Audit explanation:** Both captions leave the foods served to the child unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 399. train_3930: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A green bus stands on a speed bump while mountains are seen in the background.
>
> **Caption B:** A passenger bus that has some drawings of people on the side of it.
>
> **Adopted scope:** bus color
>
> **Extracted A:** green
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Drawings on the second bus do not supply its body color.

**Audit explanation:** B describes drawings on a bus. Bus color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 400. train_3931: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A green bus stands on a speed bump while mountains are seen in the background.
>
> **Caption B:** A passenger bus that has some drawings of people on the side of it.
>
> **Adopted scope:** actual people count
>
> **Extracted A:** none established
>
> **Extracted B:** drawings of people only
>
> **Recorded reason, verbatim:** Neither caption establishes actual people to count; drawn people are representations.

**Audit explanation:** A leaves human presence unspecified. B establishes drawings of people. Actual people remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 401. train_3943: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bathroom with a vanity, a towel rack, a urinal and a toilet and a black cat.
>
> **Caption B:** A cat standing on a bathroom sink in front of a butterfly shower curtain.
>
> **Adopted scope:** cat color
>
> **Extracted A:** black
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second cat's color is unstated.

**Audit explanation:** B leaves cat color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 402. train_3952: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bathroom sink with several toiletries, large vanity mirror, lights, and two floral decorations on the wall.
>
> **Caption B:** There is a bathroom with a toilet,sink, and a shower with a glass door.
>
> **Adopted scope:** bathroom object colors
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Neither caption supplies fixture colors.

**Audit explanation:** Both captions leave principal bathroom-fixture colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 403. train_3966: `items with stove`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** The interior of a room with a cooking area with a gas stove top.
>
> **Caption B:** A stainless steel stove and oven next to a rack full of spice bottles and oils.
>
> **Adopted scope:** items accompanying stove
>
> **Extracted A:** none specified
>
> **Extracted B:** spice and oil rack plus oven
>
> **Recorded reason, verbatim:** The first mentions only the stove and cooking area, without accompanying items to compare.

**Audit explanation:** A identifies a stove. Accompanying items remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 404. train_3973: `type of seating`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** a living room with a couch tv and a wooden floor with an open window
>
> **Caption B:** A person works at a computer in the desk area of a living room.
>
> **Adopted scope:** seating type
>
> **Extracted A:** couch
>
> **Extracted B:** no seating specified
>
> **Recorded reason, verbatim:** Working at a computer does not establish a seat type.

**Audit explanation:** B describes computer work. Seating furniture and type remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 405. train_3979: `condition of beds`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An unmade double bed with clothes on it and a single bed in a motel room.
>
> **Caption B:** A room with two side by side beds, one of the nightstand lamps are on.
>
> **Adopted scope:** bed condition
>
> **Extracted A:** unmade with clothes
>
> **Extracted B:** condition unspecified
>
> **Recorded reason, verbatim:** Side-by-side placement does not establish the second beds' made or tidy condition.

**Audit explanation:** B locates beds. Their condition remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 406. train_3982: `position of ball`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Man in a green and yellow baseball uniform watching a ball in the air.
>
> **Caption B:** A baseball player is at bat while a catcher and umpire wait behind him.
>
> **Adopted scope:** ball position
>
> **Extracted A:** in air
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second does not locate a ball.

**Audit explanation:** B describes waiting players. The ball's position remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 407. train_3989: `Presence of plate with food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Several plates full of food, along with bowls, glasses, and drinks are on a large table.
>
> **Caption B:** People standing besides a table full of food eating from bowls with chop sticks.
>
> **Adopted scope:** presence of food-filled plates
>
> **Extracted A:** explicit plates of food
>
> **Extracted B:** bowls of food but no plate information
>
> **Recorded reason, verbatim:** Food in bowls does not establish food-filled plates in the second.

**Audit explanation:** B establishes food in bowls. Food on a plate remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 408. train_4028: `breed of dog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog looks in from an open window with his paws on the windowsill.
>
> **Caption B:** A dog with a collar sits in the front, passenger seat of a black car.
>
> **Adopted scope:** dog breed
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Neither caption supplies a dog breed.

**Audit explanation:** Both captions leave dog breed unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 409. train_4034: `number of persons`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** The little boy is petting the giraffe whose head come over the zoo enclosure.
>
> **Caption B:** A giraffe that is standing on all fours on a dirt surface, in a fenced in area.
>
> **Adopted scope:** number of people
>
> **Extracted A:** one boy
>
> **Extracted B:** no person information
>
> **Recorded reason, verbatim:** The second giraffe enclosure description establishes no person count.

**Audit explanation:** B describes a giraffe enclosure. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 410. train_4037: `type of television`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A living room with a fire place as television in a box sitting on the floor.
>
> **Caption B:** A living room filled with furniture and a white couch in front of a large flat screen TV.
>
> **Adopted scope:** television subtype
>
> **Extracted A:** TV in a box; screen subtype unstated
>
> **Extracted B:** large flat-screen TV
>
> **Recorded reason, verbatim:** A box may be packaging and supplies no television subtype. The explicit type condition requires subtype information in both captions; generic TV alone is insufficient.

**Audit explanation:** A identifies a boxed television. Its screen type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 411. train_4048: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Some hot dogs in buns that have been wrapped in bacon and covered with cheese.
>
> **Caption B:** A hot dog in a paper boat sitting on a person's jeans clad legs.
>
> **Adopted scope:** number of people
>
> **Extracted A:** no person information
>
> **Extracted B:** one person whose legs support food
>
> **Recorded reason, verbatim:** The first hot-dog description establishes no person count.

**Audit explanation:** A describes hotdogs. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 412. train_4071: `number of pillow`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A bed with four pillows, the sheets are blue and the frame is made of wood.
>
> **Caption B:** A small room with a wood floor and a bed in the corner under a window.
>
> **Adopted scope:** pillow count
>
> **Extracted A:** four
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second bed has no stated pillow count; four pillows cannot be compared with silence.

**Audit explanation:** B describes a bed. Pillow presence and count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 413. train_4073: `player's stance`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A tennis player on a clay court reacting to a shot at the net.
>
> **Caption B:** A man's feet are off the ground with a shadow of a tennis racquet.
>
> **Adopted scope:** player stance
>
> **Extracted A:** reacting, stance unspecified
>
> **Extracted B:** airborne
>
> **Recorded reason, verbatim:** Reacting to a shot gives no bodily stance comparable with explicitly airborne feet.

**Audit explanation:** A describes reaction to a shot. Body stance remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 414. train_4086: `occupation`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A police car parked on the side of a road near a fire hydrant.
>
> **Caption B:** A motorcycle officer is standing next to a woman with a three wheel bike.
>
> **Adopted scope:** person occupation
>
> **Extracted A:** no person described
>
> **Extracted B:** police officer
>
> **Recorded reason, verbatim:** A police vehicle alone does not describe a person whose occupation can be compared.

**Audit explanation:** A establishes a police car. A person whose occupation can be compared remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 415. train_4094: `level of enjoyment`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person running in a field with a kite low to the ground behind them.
>
> **Caption B:** A man in a white shirt and red pants lifts his hand toward a hovering Frisbee.
>
> **Adopted scope:** person enjoyment
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Running with a kite and reaching for a Frisbee do not establish enjoyment levels.

**Audit explanation:** Both captions leave enjoyment unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 416. train_4095: `height level of person's view`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A person running in a field with a kite low to the ground behind them.
>
> **Caption B:** A man in a white shirt and red pants lifts his hand toward a hovering Frisbee.
>
> **Adopted scope:** gaze height
>
> **Extracted A:** unstated
>
> **Extracted B:** hand raised, gaze unstated
>
> **Recorded reason, verbatim:** Neither caption supplies the height of the person's gaze; object height is not gaze height.

**Audit explanation:** Both captions leave the height or direction of the person's gaze unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 417. train_4109: `absence of tomato`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A sandwich with potato chips on the side lettuce on the side with a cherry tomato.
>
> **Caption B:** Someone holding a sandwhich in their hands and the sandwhich has been half ate
>
> **Adopted scope:** tomato absence
>
> **Extracted A:** tomato present
>
> **Extracted B:** unknown
>
> **Recorded reason, verbatim:** The first includes tomato, but the half-eaten sandwich description does not establish tomato presence or absence.

**Audit explanation:** B identifies a partly eaten sandwich. Tomato presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 418. train_4121: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A plate of food on a white plate sitting on a red and white placemat.
>
> **Caption B:** a person in a blue shirt  is eating at a table and a drink
>
> **Adopted scope:** people count
>
> **Extracted A:** unstated
>
> **Extracted B:** one
>
> **Recorded reason, verbatim:** A food-only scene does not provide a person count comparable with the one explicit diner.

**Audit explanation:** A describes plated food. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 419. train_4124: `number of propellers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A view of an airplane with four propellers in the sky in the clouds.
>
> **Caption B:** A large US Air Force plane is sitting in a field of mulch for display.
>
> **Adopted scope:** propeller count
>
> **Extracted A:** four
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The displayed Air Force plane has no recoverable propeller count or propulsion type.

**Audit explanation:** B identifies an aircraft. Propeller count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 420. train_4136: `lighting at traffic light`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a crosswalk with a green traffic signal and a white bicycle symbol lit up
>
> **Caption B:** View of a traffic light at a street corner from the side of a building.
>
> **Adopted scope:** signal lighting
>
> **Extracted A:** green and white lit
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second traffic light's illuminated color or state is wholly unstated.

**Audit explanation:** B locates a traffic light. Its illumination remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 421. train_4137: `actions being performed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** a crosswalk with a green traffic signal and a white bicycle symbol lit up
>
> **Caption B:** View of a traffic light at a street corner from the side of a building.
>
> **Adopted scope:** signal action
>
> **Extracted A:** illuminated signal
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The first signal is lit, while a view of the second does not establish its operating action.

**Audit explanation:** B locates a traffic light. Its operating state and action remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 422. train_4141: `color of plate`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white plate with a pizza with two slices missing, beside a plate with half a pizza
>
> **Caption B:** A person with a pizza hut receipt and a fan of pizza and a pepsi.
>
> **Adopted scope:** plate color
>
> **Extracted A:** white
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** No plate or plate color is specified with the Pizza Hut meal.

**Audit explanation:** B leaves plate color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 423. train_4150: `color of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A colorful kitchen with a sink, a fruit bowl and a soda bottle on the counter.
>
> **Caption B:** A small portable set of burners with a tea kettle are on the counter top of a neat, clean efficiency kitchen.
>
> **Adopted scope:** kitchen color
>
> **Extracted A:** colorful
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** A clean efficiency kitchen gives no color value to compare with colorful.

**Audit explanation:** B leaves kitchen colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 424. train_4151: `type of kitchen`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A colorful kitchen with a sink, a fruit bowl and a soda bottle on the counter.
>
> **Caption B:** A small portable set of burners with a tea kettle are on the counter top of a neat, clean efficiency kitchen.
>
> **Adopted scope:** kitchen type
>
> **Extracted A:** kitchen, unspecified subtype
>
> **Extracted B:** efficiency kitchen
>
> **Recorded reason, verbatim:** Color and generic kitchen contents do not identify a kitchen subtype to compare with efficiency kitchen.

**Audit explanation:** A identifies a kitchen. Kitchen subtype remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 425. train_4157: `age of rider`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The young boy is skateboard very high up on the side of a wall.
>
> **Caption B:** A stunt skate boarder is performing stunt on a ramp of a skate park.
>
> **Adopted scope:** rider age
>
> **Extracted A:** young boy
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The stunt skateboarder's age is unspecified, unlike the young boy's.

**Audit explanation:** B identifies a stunt skateboarder. Age remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 426. train_4161: `presence of person in bed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A bed with pillows and a brown blanket is sitting against a stone wall.
>
> **Caption B:** A black and white photo of a man sleeping in a bed in an adobe-styled bedroom.
>
> **Adopted scope:** person in bed
>
> **Extracted A:** not established
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** The first bed description does not assert an empty bed, so occupant absence cannot be inferred.

**Audit explanation:** A describes bedding. Human presence in the bed remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 427. train_4173: `type of meal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Food sitting on a napkin next to a loaf of bread on a cutting board.
>
> **Caption B:** A sandwich on a white plate with utensils rapped in a napkin and lettuce on the side.
>
> **Adopted scope:** meal category
>
> **Extracted A:** unspecified
>
> **Extracted B:** sandwich meal
>
> **Recorded reason, verbatim:** Unspecified food beside a loaf does not establish the meal category given by a sandwich meal.

**Audit explanation:** A identifies generic food and bread. Meal type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 428. train_4176: `items in bathroom`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white toilet sitting in a bathroom with a paper on top of it.
>
> **Caption B:** There is a clean bathroom with a thin red line running down the side.
>
> **Adopted scope:** bathroom contents
>
> **Extracted A:** toilet and paper
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second bathroom has no named fixtures or contents; cleanliness supplies no item value.

**Audit explanation:** B describes cleanliness and a stripe. Bathroom items remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 429. train_4177: `white toilet`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A white toilet sitting in a bathroom with a paper on top of it.
>
> **Caption B:** There is a clean bathroom with a thin red line running down the side.
>
> **Adopted scope:** white toilet
>
> **Extracted A:** white toilet present
>
> **Extracted B:** toilet unmentioned
>
> **Recorded reason, verbatim:** The second caption supplies neither a toilet nor its color.

**Audit explanation:** B describes a clean bathroom. White-toilet presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 430. train_4199: `presence of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A man in a wet suit walks across a crowded beach on a sunny day.
>
> **Caption B:** Several beach umbrellas and beach chairs in the sand on a beach near the ocean.
>
> **Adopted scope:** person presence
>
> **Extracted A:** present
>
> **Extracted B:** unknown
>
> **Recorded reason, verbatim:** Chairs and umbrellas do not establish either people present or an empty beach.

**Audit explanation:** B describes beach furniture. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 431. train_4211: `room size`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A small bathroom with a vanity on one side and the shower on the other.
>
> **Caption B:** A bathroom with a white toilet sitting next to a sink under a mirror.
>
> **Adopted scope:** room size
>
> **Extracted A:** small
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The toilet-and-sink bathroom has no recoverable room-size description.

**Audit explanation:** B locates bathroom fixtures. Room size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 432. train_4226: `structure of building`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A close of of a street light with a brick building in the background.
>
> **Caption B:** This is a photo of a building with a large clock in the front of it.
>
> **Adopted scope:** building structure
>
> **Extracted A:** brick
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Brick provides construction information, whereas a clock on the facade does not establish the second building's structure.

**Audit explanation:** B identifies a building with a clock. Construction material and structure remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 433. train_4237: `number of passengers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An urban scene showing stores, building numbers, a bus, and most prominently a women's lavatories sign.
>
> **Caption B:** A double decker bus in London has stopped to pick up and drop off people.
>
> **Adopted scope:** passenger count
>
> **Extracted A:** unstated
>
> **Extracted B:** plural people, count unknown
>
> **Recorded reason, verbatim:** The first bus description supplies no passenger presence or count.

**Audit explanation:** A identifies a bus. Passenger count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 434. train_4238: `activity of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** An Apple laptop next to an iPod, wallet, tablet, laptop bag, and a phone.
>
> **Caption B:** a laptop a mouse a cup and a pair of eye glasses on a dexk
>
> **Adopted scope:** laptop activity
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Neither laptop's operating activity is given by the lists of surrounding objects.

**Audit explanation:** Both captions leave electronic-object activity unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 435. train_4248: `motorcycle on road`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Two motorcycles with a man sitting on one and a man standing next to him while they shake hands
>
> **Caption B:** A black motorcycle on the side of the road parked next to a car.
>
> **Adopted scope:** motorcycles located on a road
>
> **Extracted A:** motorcycles stationary with men, road unspecified
>
> **Extracted B:** motorcycle parked beside road
>
> **Recorded reason, verbatim:** The explicit road-placement predicate is unavailable in the first caption; motorcycle type alone does not establish it.

**Audit explanation:** A establishes motorcycles beside men. Their road location remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 436. train_4266: `material of floor`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A photo of someone's room with a small television, a mirrored wall, white curtains, and random things througout, 
>
> **Caption B:** A small end table sits at the back of a big shiny wood floor.
>
> **Adopted scope:** floor material
>
> **Extracted A:** unstated
>
> **Extracted B:** wood
>
> **Recorded reason, verbatim:** The first room description says nothing about its floor material.

**Audit explanation:** A leaves floor material unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 437. train_4267: `type of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A photo of someone's room with a small television, a mirrored wall, white curtains, and random things througout, 
>
> **Caption B:** A small end table sits at the back of a big shiny wood floor.
>
> **Adopted scope:** functional room type
>
> **Extracted A:** room with television, mirror and curtains; partial function clues
>
> **Extracted B:** end table and wood floor; function unstated
>
> **Recorded reason, verbatim:** The end table and floor do not identify a room function; the user retained the analogous generic-furnishings exclusion.

**Audit explanation:** B's end table and wooden floor leave room function unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 438. train_4286: `type of bird`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A sparrow sits on a wood post, with a grassy field in the background.
>
> **Caption B:** A bird sits up right and the picture is framed by the leaves from the bush.
>
> **Adopted scope:** bird type
>
> **Extracted A:** sparrow
>
> **Extracted B:** unspecified bird
>
> **Recorded reason, verbatim:** Generic bird provides no bird subtype to compare with sparrow.

**Audit explanation:** B identifies a bird. Bird type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 439. train_4287: `object bird is on`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A sparrow sits on a wood post, with a grassy field in the background.
>
> **Caption B:** A bird sits up right and the picture is framed by the leaves from the bush.
>
> **Adopted scope:** bird support
>
> **Extracted A:** wood post
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Leaves framing the second picture do not identify the bird's supporting perch.

**Audit explanation:** B describes a seated bird. Its supporting object remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 440. train_4292: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white with brown spots dog lays on the side of a road near a cow.
>
> **Caption B:** A cow looking into camera on city street with buildings, three people and car in background.
>
> **Adopted scope:** principal animal color
>
> **Extracted A:** white and brown dog
>
> **Extracted B:** cow color unstated
>
> **Recorded reason, verbatim:** The second cow's color is wholly unstated.

**Audit explanation:** B leaves cow color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 441. train_4313: `state of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a kitchen with a bunch of empty bottles sitting on the counter and the floor
>
> **Caption B:** A kitchen that has a stove top and sink, along with lower cabinets and a shelf.
>
> **Adopted scope:** room state
>
> **Extracted A:** cluttered with bottles
>
> **Extracted B:** state unspecified
>
> **Recorded reason, verbatim:** The second list of fixtures does not establish cleanliness or clutter comparable with bottles on counter and floor.

**Audit explanation:** B inventories kitchen fixtures. Kitchen condition remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 442. train_4326: `type of food served`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A plate of various types of food is on a plate next to some silverware.
>
> **Caption B:** There is a plate with a sandwich and salad near a cup of coffee.
>
> **Adopted scope:** food type
>
> **Extracted A:** varied unspecified food
>
> **Extracted B:** sandwich and salad
>
> **Recorded reason, verbatim:** “Various types of food” does not identify any food category comparable with sandwich and salad.

**Audit explanation:** A identifies generic varied food. Served food types remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 443. train_4348: `color of building`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a parking meter stands in front of a door on a green building with two windows
>
> **Caption B:** This is a picture of a fire hydrant that is in front of an old building.
>
> **Adopted scope:** building color
>
> **Extracted A:** green
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The old building has no specified color.

**Audit explanation:** B leaves building color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 444. train_4352: `activity of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A man in a wheelchair sits with family around a television in a living room.
>
> **Caption B:** Two men and a woman in a room with a plaid couch and a striped couch and a wooden coffee table.
>
> **Adopted scope:** people activity
>
> **Extracted A:** sitting around television
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second caption locates people in a room but gives none of their actions.

**Audit explanation:** B locates three people in a room. Their activity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 445. train_4361: `location`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A trio of images of food including bell peppers, watermelon, milk, and chopped meat
>
> **Caption B:** A kitchen counter displaying a bread box, blender and many different fruits and vegetables.
>
> **Adopted scope:** physical location
>
> **Extracted A:** unstated, image collage
>
> **Extracted B:** kitchen counter
>
> **Recorded reason, verbatim:** The collage gives no physical food setting comparable with the explicitly named kitchen counter.

**Audit explanation:** A presents food images in a collage. The food's physical location remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 446. train_4365: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** a young child resting in a bed with an open door in the background
>
> **Caption B:** a laptop is sitting on a bed with a bunch of books on the cabinets against the wall
>
> **Adopted scope:** person count
>
> **Extracted A:** one child
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The laptop-and-books caption does not establish a person count, including zero.

**Audit explanation:** B lists bedroom objects. Human presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 447. train_4380: `animal type`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a black and yellow with white paws a sleep on the couch next to the tv remotw
>
> **Caption B:** Black cat on a comforter with a duvet that has red cherries holding a television remote.
>
> **Adopted scope:** animal type
>
> **Extracted A:** paws, species unstated
>
> **Extracted B:** cat
>
> **Recorded reason, verbatim:** Paws establish an animal but the corrupted first caption supplies no species, unlike the explicit cat.

**Audit explanation:** A supplies colors and paws. Animal species remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 448. train_4383: `type of food`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** People standing besides a table full of food eating from bowls with chop sticks.
>
> **Caption B:** Two men standing around a pizza on the counter, one wearing an oven mitt.
>
> **Adopted scope:** food type
>
> **Extracted A:** unspecified chopstick food
>
> **Extracted B:** pizza
>
> **Recorded reason, verbatim:** Eating with chopsticks does not establish which food is eaten in the first caption.

**Audit explanation:** A identifies generic food eaten with chopsticks. Food type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 449. train_4399: `color of flower`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Street signs and a fire hydrant near a bush with purple flowers in it.
>
> **Caption B:** A street sign with a number on it and is mounted to a long pole
>
> **Adopted scope:** flower color
>
> **Extracted A:** purple
>
> **Extracted B:** no flower described
>
> **Recorded reason, verbatim:** The second caption contains no flower whose color can be extracted.

**Audit explanation:** B describes a street sign. Flower presence remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 450. train_4419: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black cat on top of a microwave which is on top of a refrigerator.
>
> **Caption B:** A kitten with its head in a medical cone balancing upon the back of a chair.
>
> **Adopted scope:** animal color
>
> **Extracted A:** black
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** No color is supplied for the kitten.

**Audit explanation:** B leaves kitten color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `1.0`.

### 451. train_4451: `Presence of hotdog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** There is a plate that has fries, a hotdog along with onions, tomatoes and relish packages.
>
> **Caption B:** A sandwich is on a plate with french fries and lettuce and red onion.
>
> **Adopted scope:** hot-dog presence
>
> **Extracted A:** present
>
> **Extracted B:** sandwich type unspecified
>
> **Recorded reason, verbatim:** An unspecified sandwich does not establish whether a hot dog is absent.

**Audit explanation:** B identifies a sandwich. Hotdog presence within the sandwich remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 452. train_4471: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black, gray and white kitten rests on a bed while sitting on a cell phone.
>
> **Caption B:** A domestic short haired cat resting on the edge of a desk near breath mints.
>
> **Adopted scope:** animal color
>
> **Extracted A:** black, grey, white
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Short-haired describes coat length, not the second cat's color.

**Audit explanation:** B describes coat length. Cat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 453. train_4479: `person's clothing color`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person with snow skis on going through a brush area of snow and bushes.
>
> **Caption B:** Person with red goggles and back ski suit standing on skies in the snow.
>
> **Adopted scope:** clothing color
>
> **Extracted A:** unstated
>
> **Extracted B:** black suit and red goggles
>
> **Recorded reason, verbatim:** The first skier's clothing color is wholly unspecified.

**Audit explanation:** A leaves clothing color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 454. train_4481: `name of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young boy with an arm cast playing a video game with a woman.
>
> **Caption B:** Two people look at each other as they play Wii in their living room.
>
> **Adopted scope:** place
>
> **Extracted A:** unstated
>
> **Extracted B:** living room
>
> **Recorded reason, verbatim:** Playing a video game without any named room or furnishings does not establish the first place type.

**Audit explanation:** A describes videogame players. Their location remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 455. train_4485: `type of flora`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A boat sits in the water in front of a brick two story house.
>
> **Caption B:** A wooden bench surrounded by shrubbery and flowers on the side of a house.
>
> **Adopted scope:** flora
>
> **Extracted A:** unstated
>
> **Extracted B:** shrubs and flowers
>
> **Recorded reason, verbatim:** The first scene contains no stated vegetation type.

**Audit explanation:** A describes a boat and house. Flora remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 456. train_4486: `color of uniform`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A baseball player stands at home base holding a bat as spectators look on.
>
> **Caption B:** A man in a white uniform on the homeplate with two men in black shirts and masks.
>
> **Adopted scope:** uniform color
>
> **Extracted A:** unstated
>
> **Extracted B:** white and black
>
> **Recorded reason, verbatim:** The first baseball player's uniform color is not given.

**Audit explanation:** A leaves uniform color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 457. train_4507: `activity of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** People shopping at a busy fruit market with yellow signs displaying the prices for each fruit.
>
> **Caption B:** A display in a grocery store filled with lots of fresh fruits and vegetables.
>
> **Adopted scope:** people activity
>
> **Extracted A:** shopping
>
> **Extracted B:** no people described
>
> **Recorded reason, verbatim:** The grocery display does not describe people or a people's activity.

**Audit explanation:** B describes a produce display. Human presence and activity remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 458. train_4510: `contents of plate`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person sitting in front of a plate full of food and some glasses.
>
> **Caption B:** A close-up of a plate with mushrooms, carrots, tomatoes, broccoli, and cauliflower on it.
>
> **Adopted scope:** plate contents
>
> **Extracted A:** food unspecified
>
> **Extracted B:** mixed vegetables and mushrooms
>
> **Recorded reason, verbatim:** The first plate's contents are only generic food, following confirmed #14 and #26.

**Audit explanation:** A identifies generic food. Plate contents remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 459. train_4511: `content of plate`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person sitting in front of a plate full of food and some glasses.
>
> **Caption B:** A close-up of a plate with mushrooms, carrots, tomatoes, broccoli, and cauliflower on it.
>
> **Adopted scope:** plate contents
>
> **Extracted A:** food with no identified category/components
>
> **Extracted B:** mushrooms, carrots, tomatoes, broccoli, cauliflower
>
> **Recorded reason, verbatim:** This repeats the exact captions and extracted values of invalid train_4510 under synonymous content/contents of plate. Generic food does not identify the requested contents under the confirmed user boundaries.

**Audit explanation:** A leaves its food category and plate ingredients unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 460. train_4514: `type of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A table topped with teddy bears and huge cones in front of a curtain.
>
> **Caption B:** Canopy bed with white curtain red bedspread, red ascent pieces and lots of stuffed animal.
>
> **Adopted scope:** stuffed animal type
>
> **Extracted A:** teddy bears
>
> **Extracted B:** unspecified stuffed animals
>
> **Recorded reason, verbatim:** Teddy bears and stuffed animals are toys, so the literal-animal condition is inapplicable.

**Audit explanation:** B identifies generic stuffed animals. Their represented animal types remain unspecified under the recorded stuffed-animal scope.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `4.0`.

### 461. train_4515: `type of activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A table topped with teddy bears and huge cones in front of a curtain.
>
> **Caption B:** Canopy bed with white curtain red bedspread, red ascent pieces and lots of stuffed animal.
>
> **Adopted scope:** scene activity
>
> **Extracted A:** static arrangement of toys on a table
>
> **Extracted B:** static furnishing of a bed
>
> **Recorded reason, verbatim:** Neither caption supplies an action; assuming somebody displaying or arranging the objects would invent an activity.

**Audit explanation:** Both captions describe static toy and furnishing arrangements. Activity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 462. train_4516: `type of dessert`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dessert has been made in a fish bowl and is sitting on the table with a glass of wine.
>
> **Caption B:** A piece of cake with white frosting on a plate with a fork and a stack of books next to it.
>
> **Adopted scope:** dessert subtype
>
> **Extracted A:** dessert in a fish bowl, subtype unspecified
>
> **Extracted B:** cake
>
> **Recorded reason, verbatim:** A bowl supplies serving form but does not identify the dessert type, just as generic food in a bowl supplies no food subtype.

**Audit explanation:** A identifies a dessert. Dessert type remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 463. train_4533: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A girl is sitting in a black chair playing the wii while another guy looks on.
>
> **Caption B:** A man standing next to a man sitting on a foot stool holding a Nintendo Wii controller.
>
> **Adopted scope:** object color
>
> **Extracted A:** black chair
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second caption supplies no object color comparable with the black chair.

**Audit explanation:** B leaves principal object colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `3.0`.

### 464. train_4553: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man holding a board in the water with palm trees in the distance.
>
> **Caption B:** a male surfer in a blue shirt is carrying a yellow and red board
>
> **Adopted scope:** board color
>
> **Extracted A:** unstated
>
> **Extracted B:** yellow and red
>
> **Recorded reason, verbatim:** The first board's color is absent.

**Audit explanation:** A leaves board color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 465. train_4561: `objects on desk`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A smart phone, radio and a microphone sitting on top of a laptop computer.
>
> **Caption B:** A desk with many items on it, such as a book, pens, and a Nerf gun.
>
> **Adopted scope:** objects located on a desk
>
> **Extracted A:** electronics on a laptop, desk not established
>
> **Extracted B:** book, pens and Nerf gun on a desk
>
> **Recorded reason, verbatim:** The first supporting object is a laptop and no desk is supplied, so the explicit desk-location condition cannot be established.

**Audit explanation:** A places electronics on a laptop. A supporting desk remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_b`.

**History:** supplied source rating `2.0`.

### 466. train_4563: `type of space`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An empty room with a wooden floor and white walls and another room has a light on and cupboards.
>
> **Caption B:** A picture of a small living room with black couch and brown entertainment unit.
>
> **Adopted scope:** functional room type
>
> **Extracted A:** empty room beside another room with cupboards; function unspecified
>
> **Extracted B:** living room
>
> **Recorded reason, verbatim:** A bare room and adjoining cupboards do not establish the main room function; generic indoor space alone is insufficient.

**Audit explanation:** The first empty room's floor and walls leave its function unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 467. train_4567: `person's elevation`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Bundled against the weather, a snowboarder prepares to do a trick in the early morning.
>
> **Caption B:** a person on a snowboard in the air with a snow mountainside in the background
>
> **Adopted scope:** person elevation
>
> **Extracted A:** unspecified
>
> **Extracted B:** airborne above slope
>
> **Recorded reason, verbatim:** Preparing a trick does not specify the first snowboarder's height or whether already airborne.

**Audit explanation:** The first snowboarder's elevation remains unspecified during preparation for a trick.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 468. train_4583: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in light colored clothing walks beside a bike as a red train is on the train tracks near him.
>
> **Caption B:** A number of rail lines on a bend and a train on one of them
>
> **Adopted scope:** people count
>
> **Extracted A:** one
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The railway-only caption supplies no people count.

**Audit explanation:** The second railway scene leaves the current people count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 469. train_4592: `object that opens vertically`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A refrigerator/freezer combo has the freezer on the bottom with a slide out drawer.
>
> **Caption B:** The kitchen with stainless steel refrigerator, dishes on the counter, a range, and a baby seat.
>
> **Adopted scope:** vertical-opening object
>
> **Extracted A:** drawer opens horizontally
>
> **Extracted B:** opening direction unstated
>
> **Recorded reason, verbatim:** A slide-out bottom drawer is horizontal, and the other refrigerator's opening direction is unspecified; the requested vertical-opening object is not established.

**Audit explanation:** The first freezer drawer slides horizontally. The second refrigerator's opening direction remains unspecified, leaving the required vertically opening object unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 470. train_4601: `presence of a baby`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A baby plays at a closed toilet bowl and grabs at a towel from the rack.
>
> **Caption B:** A white toilet has its lid down and a roll of toilet paper next to it.
>
> **Adopted scope:** baby presence
>
> **Extracted A:** present
>
> **Extracted B:** unknown
>
> **Recorded reason, verbatim:** The second toilet scene does not establish a baby absent, only unmentioned.

**Audit explanation:** Baby presence remains unknown in the second toilet scene.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 471. train_4626: `activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A man standing in a kitchen looking at the open drawer on the oven.
>
> **Caption B:** A kitchen has cabinet doors ajar and a view of  grass outside the window.
>
> **Adopted scope:** person activity
>
> **Extracted A:** looking at oven drawer
>
> **Extracted B:** no person described
>
> **Recorded reason, verbatim:** The second scene has open cabinets but no actor or activity comparable with the man looking.

**Audit explanation:** The second kitchen scene leaves a human actor and corresponding activity unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 472. train_4632: `types of fruits`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A picture of plate with peanut butter and honey toast and a bowl of fruit.
>
> **Caption B:** Banana, strawberry, and blueberry baked fruit roll with a side of dip or syrup.
>
> **Adopted scope:** fruit varieties
>
> **Extracted A:** unnamed fruit
>
> **Extracted B:** banana, strawberry and blueberry
>
> **Recorded reason, verbatim:** The first names only the target category fruit without any recoverable variety, analogous to unnamed wine types.

**Audit explanation:** The first caption's generic fruit leaves its varieties unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 473. train_4650: `number of humans`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog holding a frisbee in his mouth and standing in a yard full of leaves.
>
> **Caption B:** A Frisbee with a woman's right hand on one side and a dog's head on the other
>
> **Adopted scope:** human count
>
> **Extracted A:** unstated
>
> **Extracted B:** one woman
>
> **Recorded reason, verbatim:** The first dog scene has no stated human count; the woman's hand establishes one human only in the second.

**Audit explanation:** The first dog scene leaves human presence and count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 474. train_4653: `presence of fruit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman in a zebra print shirt standing in front of a farmers market.
>
> **Caption B:** a store with a lot of fruit for sale out front on the sidewalk
>
> **Adopted scope:** fruit presence
>
> **Extracted A:** farmers market, fruit unspecified
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** A farmers market can sell many products, so it does not establish fruit presence in the first scene.

**Audit explanation:** The first farmers market leaves fruit presence unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 475. train_4665: `type of skateboarding trick`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man doing tricks on a skate board and a bunch of people watching
>
> **Caption B:** A boy in the middle of doing a kick flip on a skate board.
>
> **Adopted scope:** trick type
>
> **Extracted A:** unspecified tricks
>
> **Extracted B:** kickflip
>
> **Recorded reason, verbatim:** Unspecified skateboard tricks provide no trick subtype to compare with kickflip.

**Audit explanation:** The first unnamed skateboard tricks leave trick subtype unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 476. train_4683: `mood of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bunch of skiers with the same team uniforms seem to be waiting in line.
>
> **Caption B:** Man in middle podium holding skis in air, with two other skiers on the sides.
>
> **Adopted scope:** people mood
>
> **Extracted A:** unstated
>
> **Extracted B:** celebratory inferred
>
> **Recorded reason, verbatim:** Waiting in line does not supply the skiers' mood.

**Audit explanation:** The first skiers' mood remains unspecified while they wait in line.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 477. train_4687: `size of laptop`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A mans hands holding a cell phone and a females hands at a laptop
>
> **Caption B:** A mini laptop sitting on a table with someones arms on their big laptop
>
> **Adopted scope:** laptop size
>
> **Extracted A:** unstated
>
> **Extracted B:** mini and big
>
> **Recorded reason, verbatim:** The first laptop has no size description comparable with mini and big.

**Audit explanation:** The first laptop's size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 478. train_4696: `object near monitor`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A computer desk with a cat standing on top of it next to a monitor.
>
> **Caption B:** A black and white stepping on a keyboard next to a monitor and CPU
>
> **Adopted scope:** entity near monitor
>
> **Extracted A:** cat
>
> **Extracted B:** black-and-white entity unspecified
>
> **Recorded reason, verbatim:** The second malformed caption omits the entity noun; black-and-white appearance and stepping do not establish its object type.

**Audit explanation:** The second caption omits the noun identifying the black-and-white entity near the monitor.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 479. train_4697: `animal species`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A computer desk with a cat standing on top of it next to a monitor.
>
> **Caption B:** A black and white stepping on a keyboard next to a monitor and CPU
>
> **Adopted scope:** animal species
>
> **Extracted A:** cat
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second caption does not identify a species, so a cat cannot be assumed from context alone.

**Audit explanation:** The second black-and-white entity's animal species remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 480. train_4703: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A gropu of people, including one with a walker, stand by a bus on a street.
>
> **Caption B:** A city street with a restaurant sign and many other signs on the street.
>
> **Adopted scope:** people count
>
> **Extracted A:** group
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The signs-only city street gives no human count.

**Audit explanation:** The second street's signs leave people presence and count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 481. train_4706: `number of lamps`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bedroom with a large, unmade be, a ceiling fan and other bedroom items
>
> **Caption B:** A man looking at a bed in a room with a flower comforter and two lamps on either side.
>
> **Adopted scope:** lamp count
>
> **Extracted A:** unstated
>
> **Extracted B:** two
>
> **Recorded reason, verbatim:** Unspecified bedroom items do not establish any lamp count in the first caption.

**Audit explanation:** The first generic bedroom items leave lamp presence and count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 482. train_4718: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in uniform standing in front of a blue bus on the road.
>
> **Caption B:** A line of buses on either side of a median in a bus station.
>
> **Adopted scope:** bus color
>
> **Extracted A:** blue
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The line of buses has no stated color.

**Audit explanation:** The second buses' colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 483. train_4719: `activity of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A man in uniform standing in front of a blue bus on the road.
>
> **Caption B:** A line of buses on either side of a median in a bus station.
>
> **Adopted scope:** people activity
>
> **Extracted A:** standing
>
> **Extracted B:** no people described
>
> **Recorded reason, verbatim:** The second bus scene contains no described person or personal activity.

**Audit explanation:** The second bus-station scene leaves people and their activities unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 484. train_4734: `Size of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A kitchen with very dirty walls, a broken cabinet, and several things on the counter.
>
> **Caption B:** A tiny kitchen made of wood with a small white stove and a window.
>
> **Adopted scope:** room size
>
> **Extracted A:** unstated
>
> **Extracted B:** tiny
>
> **Recorded reason, verbatim:** Dirty walls and broken cabinets provide condition information, not room size.

**Audit explanation:** The first kitchen's dirty walls and broken cabinet leave its size unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 485. train_4785: `type of room`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A room set up with a glass table and four toilets for chairs with the lids down.
>
> **Caption B:** The inside of a bathroom with sink and toilet and a sculpture above the toilet.
>
> **Adopted scope:** functional room type
>
> **Extracted A:** table with toilets used as chairs; room function unspecified
>
> **Extracted B:** bathroom
>
> **Recorded reason, verbatim:** The unconventional table-and-chair installation does not identify a functional room category; the toilets are explicitly used as chairs.

**Audit explanation:** The first toilets serve as chairs, leaving the room's function unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 486. train_4819: `color of umbrella`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Pedestrians walk down an urban street holding umbrellas, near a car, garbage bags, skyscrapers, and an American flag.
>
> **Caption B:** a woman with a tan umbrella walking in the rain past a yellow fire hydrant.
>
> **Adopted scope:** umbrella color
>
> **Extracted A:** unstated
>
> **Extracted B:** tan
>
> **Recorded reason, verbatim:** No umbrella color is stated for the first pedestrians.

**Audit explanation:** The first pedestrians' umbrella colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 487. train_4821: `presence of figure of person light`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A plethora of traffic lights on a pole that looks like a tree of sorts.
>
> **Caption B:** A street light that is displaying a red light with the figure of a person.
>
> **Adopted scope:** person-figure light presence
>
> **Extracted A:** unstated
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** Generic traffic lights do not establish whether a person-figure signal is present.

**Audit explanation:** The first traffic-light cluster leaves human-figure signal presence unknown.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 488. train_4839: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** This bedroom has an old window seat to sit on and look out of.
>
> **Caption B:** A man looking at a bed in a room with a flower comforter and two lamps on either side.
>
> **Adopted scope:** people count
>
> **Extracted A:** unstated
>
> **Extracted B:** one man
>
> **Recorded reason, verbatim:** A window seat intended for sitting does not establish any person present or count.

**Audit explanation:** The first window seat establishes furniture. Current people presence and count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 489. train_4855: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man  stands in the distance holds up an umbrella on a city street.
>
> **Caption B:** A black and white photo of a women walking in the rain with an umbrella.
>
> **Adopted scope:** umbrella color
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated in monochrome image
>
> **Recorded reason, verbatim:** Neither umbrella has a stated color; a monochrome photograph does not determine the object's actual color.

**Audit explanation:** Both umbrellas' actual colors remain unspecified. Monochrome photography records image style.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 490. train_4861: `color of objects`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** This living room has a sectional couch, a coffee table, a shelf with movies, and a spiral candle holder on the wall.
>
> **Caption B:** A living room featuring black and white furniture with red ascents and a TV turned on.
>
> **Adopted scope:** furniture colors
>
> **Extracted A:** unstated
>
> **Extracted B:** black, white, red
>
> **Recorded reason, verbatim:** The first furnishings have no recoverable color descriptions.

**Audit explanation:** The first living-room furnishings' colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 491. train_4881: `color of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two bikes are sitting near a building with one being blue, and the other is orange. 
>
> **Caption B:** A white surfboard is strapped onto a bicycle that is with another bicycle on a corner by a pole.
>
> **Adopted scope:** bicycle colors
>
> **Extracted A:** blue and orange
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** White describes the surfboard, leaving the second bicycles' colors unknown.

**Audit explanation:** The second bicycles' colors remain unspecified. White describes the attached surfboard.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 492. train_4900: `stage of preparation`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man is standinb by a grill in a kitchen with a stack of plates near him.
>
> **Caption B:** there is a chef that is in the kitchen , he is seen smiling
>
> **Adopted scope:** preparation stage
>
> **Extracted A:** standing by grill
>
> **Extracted B:** smiling chef
>
> **Recorded reason, verbatim:** Standing near a grill and smiling in a kitchen do not identify a preparation stage.

**Audit explanation:** Both standing near a grill and smiling in a kitchen leave food-preparation stage unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 493. train_4901: `person's intention`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man is standinb by a grill in a kitchen with a stack of plates near him.
>
> **Caption B:** there is a chef that is in the kitchen , he is seen smiling
>
> **Adopted scope:** person intention
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Neither caption states or directly establishes the person's intention.

**Audit explanation:** Both men's intentions remain unspecified during the described kitchen activities.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 494. train_4957: `type of decorations`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** this bathroom has a shower with glass doors and a black an white sink
>
> **Caption B:** A bathroom toilet, with a candle on a fish decoration, toilet paper roll, and shower.
>
> **Adopted scope:** decorations
>
> **Extracted A:** unspecified
>
> **Extracted B:** candle and fish decoration
>
> **Recorded reason, verbatim:** Shower doors and a sink are fixtures, not a described decorative treatment comparable with the fish ornament and candle.

**Audit explanation:** The first fixtures leave a decorative treatment unspecified. The second scene supplies a candle and fish ornament.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 495. train_4963: `color of train`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two trains are coming down the tracks, a steam engine and a modern train.
>
> **Caption B:** A bright red train is moving down the tracks with several cars following it.
>
> **Adopted scope:** train color
>
> **Extracted A:** unstated
>
> **Extracted B:** red
>
> **Recorded reason, verbatim:** Steam and modern engine types do not specify either train's color in the first.

**Audit explanation:** The first trains' colors remain unspecified by their steam and modern engine types.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 496. train_4985: `decorations in bathroom`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bathroom has a painting on it's floor to make it look like it's in the sky.
>
> **Caption B:** A toilet sitting next to a sink and across from a bathtub in a bathroom.
>
> **Adopted scope:** bathroom decoration
>
> **Extracted A:** sky floor painting
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second lists bathroom fixtures but no decorative feature comparable with the sky floor painting.

**Audit explanation:** The second bathroom fixtures leave decorative features unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 497. train_4993: `objects on table`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A beautiful pizza on the outside table with a tall mug of beer and a bowl of salad
>
> **Caption B:** A pizza sitting on top of a white plate covered in cheese and toppings.
>
> **Adopted scope:** objects located on a table
>
> **Extracted A:** pizza, beer mug, salad bowl on outside table
>
> **Extracted B:** pizza on a white plate; table unstated
>
> **Recorded reason, verbatim:** The table relation is required by the condition. A plate of pizza does not establish a table or objects on it; comparing meal objects discards the requested location. This follows invalid train_4561 objects on desk.

**Audit explanation:** The second pizza rests on a plate, leaving a table and the required objects-on-table relation unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 498. train_5017: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A pretty young woman sitting at a table next to a man holding a bottle of wine.
>
> **Caption B:** A glass of red wine and a glass of white wine on a restaurant table.
>
> **Adopted scope:** people count
>
> **Extracted A:** two
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Two wine glasses do not establish any person count in the second scene.

**Audit explanation:** The second wine-glass scene leaves people presence and count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 499. train_5021: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cat playing with purple crock shoes, laying amongst many wires and electric guitars.
>
> **Caption B:** A man sitting in a leather chair with a white cat laying on top of it.
>
> **Adopted scope:** animal color
>
> **Extracted A:** unstated
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** Purple describes shoes, not the first cat, whose color remains unstated.

**Audit explanation:** The first cat's color remains unspecified. Purple describes the shoes.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 500. train_5029: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bus parked in a parking spot while a man gets on the bus
>
> **Caption B:** A double deck bus with the words "WELCOME TO EARLY YEARS PLAYBUS" on the front.
>
> **Adopted scope:** people count
>
> **Extracted A:** one
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The playbus description supplies no people count.

**Audit explanation:** The second playbus's lettering leaves people count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 501. train_5033: `name of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man hangs in the air while doing a trick on his skate board.
>
> **Caption B:** The young boy is skateboard very high up on the side of a wall.
>
> **Adopted scope:** place
>
> **Extracted A:** unstated
>
> **Extracted B:** wall, broader place unknown
>
> **Recorded reason, verbatim:** Neither caption identifies the broader activity venue; a wall alone is not a named place.

**Audit explanation:** The first trick's venue remains unspecified. The second wall leaves the broader place category unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 502. train_5045: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a woman with a tan umbrella walking in the rain past a yellow fire hydrant.
>
> **Caption B:** A person knelt down with a hand bag and umbrella on a rainy sidewalk.
>
> **Adopted scope:** umbrella color
>
> **Extracted A:** tan
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second umbrella has no stated color.

**Audit explanation:** The second umbrella's color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 503. train_5047: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A girl sitting on a counter next to a blender, some cups and a microwave.
>
> **Caption B:** An assortment of items on top of a desk, one of which is a laptop computer.
>
> **Adopted scope:** people count
>
> **Extracted A:** one
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The object-covered desk gives no person count.

**Audit explanation:** The second desk and its contents leave people presence and count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 504. train_5051: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bedroom with a bed next to a window that has items on the bed, and there are lights on buildings outside the window.
>
> **Caption B:** The silhouette of someone lying on a bed reading a book with an umbrella hung on the window at their feet
>
> **Adopted scope:** people count
>
> **Extracted A:** unstated
>
> **Extracted B:** one
>
> **Recorded reason, verbatim:** The first bedroom scene does not establish people present or absent.

**Audit explanation:** The first bedroom scene leaves people presence and count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 505. train_5056: `food on table`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Sliced red tomatoes sit next to a wine glass and a bottle of wine.
>
> **Caption B:** A black table with fruits and vegetables on it next to a yellow wall.
>
> **Adopted scope:** food located on a table
>
> **Extracted A:** tomatoes beside wineglass and bottle; table unstated
>
> **Extracted B:** fruit and vegetables explicitly on black table
>
> **Recorded reason, verbatim:** A tabletop is not established by tomatoes, a bottle and a wineglass. The required table relation is unavailable in the first caption; follow the same boundary as train_4993.

**Audit explanation:** The first tomatoes and wine vessels leave a table and the required food-on-table relation unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 506. train_5066: `speed of skiers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Many skiers with orange vests are standing or skiing along a snowy path bordered with evergreens.
>
> **Caption B:** A group of men standing next to each other on a snow covered slope.
>
> **Adopted scope:** speed of explicitly established skiers
>
> **Extracted A:** skiers standing or skiing
>
> **Extracted B:** men standing on snow, skier role unestablished
>
> **Recorded reason, verbatim:** Snow-covered terrain alone does not establish that the second group are skiers, so the requested role is unavailable.

**Audit explanation:** The second men stand on snow. Their skier role remains unestablished, leaving skier speed unavailable.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 507. train_5075: `decoration of cake`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A piece of chocolate shaped like a Star Wars space ship and another piece of chocolate cake.
>
> **Caption B:** A small chocolate cake with a dob of cream on a plate with a fork
>
> **Adopted scope:** cake decoration
>
> **Extracted A:** unstated, separate shaped chocolate
>
> **Extracted B:** cream dollop
>
> **Recorded reason, verbatim:** The spaceship-shaped chocolate is a separate piece, so it does not establish decoration on the first cake.

**Audit explanation:** The first spaceship-shaped chocolate is separate from the cake, leaving the cake's decoration unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 508. train_5077: `sentiment of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a couple in the living room talking while the guy holds a laptop in his lap
>
> **Caption B:** Two women and one man are sitting at a table and they are all looking into open laptop computers.
>
> **Adopted scope:** people sentiment
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Talking or viewing laptops does not establish the people's sentiment.

**Audit explanation:** Both groups' sentiment remains unspecified during conversation or laptop viewing.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 509. train_5086: `activity of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A picture taken through a window that is drenched in rain distorting the image.
>
> **Caption B:** A blurry image seen through a rainy window of a person holding a light blue umbrella.
>
> **Adopted scope:** people activity
>
> **Extracted A:** no person described
>
> **Extracted B:** holding umbrella
>
> **Recorded reason, verbatim:** A rain-distorted view contains no described person in the first caption.

**Audit explanation:** The first rain-distorted window view leaves a human actor and activity unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 510. train_5087: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A picture taken through a window that is drenched in rain distorting the image.
>
> **Caption B:** A blurry image seen through a rainy window of a person holding a light blue umbrella.
>
> **Adopted scope:** umbrella color
>
> **Extracted A:** no umbrella described
>
> **Extracted B:** light blue
>
> **Recorded reason, verbatim:** The first rainy-window caption supplies neither an umbrella nor its color.

**Audit explanation:** The first rainy-window view leaves an umbrella and its color unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 511. train_5105: `number of items on bed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The rolled up towels on the bed have a pair of glasses on them.
>
> **Caption B:** A view of a king size bed, that appear to be in a hotel.
>
> **Adopted scope:** bed-item count
>
> **Extracted A:** plural towels and glasses
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second bed has no stated items on it to count.

**Audit explanation:** The second hotel bed's accompanying item count remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 512. train_5114: `color of object in image`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Black and white close up of the feet for a skateboarder doing a trick.
>
> **Caption B:** A man skateboarding and doing a jumping trick in the air, over a railing.
>
> **Adopted scope:** object color
>
> **Extracted A:** unstated in monochrome photo
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Monochrome photography does not supply actual skateboard color, and the other caption also omits it.

**Audit explanation:** Both objects' actual colors remain unspecified. The first monochrome photograph records image style.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 513. train_5133: `proximity to base`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A young kid with a helmet is up for bat in a game of baseball.
>
> **Caption B:** a small boy wearing a baseball uniform runs through a gate, preparing to play baseball
>
> **Adopted scope:** base proximity
>
> **Extracted A:** at batting home plate
>
> **Extracted B:** gate, base distance unknown
>
> **Recorded reason, verbatim:** Running through a gate supplies no recoverable distance from a baseball base.

**Audit explanation:** The second boy's gate location leaves his distance from a baseball base unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 514. train_5144: `species of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bird sitting on top of a piece of wood next to flowers and a body of water.
>
> **Caption B:** A picture of a small bird hiding in the middle of some berry bushes.
>
> **Adopted scope:** animal species
>
> **Extracted A:** bird, species unidentified
>
> **Extracted B:** small bird, species unidentified
>
> **Recorded reason, verbatim:** The explicit species condition requires species information. A generic bird and a small generic bird provide no species identities; the prior rationale acknowledges this missing feature.

**Audit explanation:** Both captions identify generic birds, leaving animal species unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 515. train_5146: `activity of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A group of people wait at a crosswalk by a lighted building at night.
>
> **Caption B:** A view of a city at night featuring heavy bus traffic and street lights.
>
> **Adopted scope:** people activity
>
> **Extracted A:** waiting at crossing
>
> **Extracted B:** no people described
>
> **Recorded reason, verbatim:** The second city-traffic scene gives no described people whose action can be compared.

**Audit explanation:** The second city-traffic scene leaves a human actor and activity unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 516. train_5151: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The human hand picks up a Krispy Kreme donut right out of the box.
>
> **Caption B:** A chocolate covered donut and a donut with sugar sprinkled on top sit  on a serving plate.
>
> **Adopted scope:** people count
>
> **Extracted A:** one implied by hand
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** A human hand establishes one person only in the first; the second pastry scene gives no people count.

**Audit explanation:** The second donut plate leaves people presence and count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 517. train_5152: `types of street signs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** street signs on metal poles on the side of a street in front of green bushes.
>
> **Caption B:** The stop sign has the word war written on it, there is also a yellow sign underneath it.
>
> **Adopted scope:** sign type
>
> **Extracted A:** street signs unspecified
>
> **Extracted B:** modified stop sign and yellow sign
>
> **Recorded reason, verbatim:** The first supplies only generic street signs without sign-type identities.

**Audit explanation:** The first generic street signs leave sign types unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 518. train_5153: `number of poles`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** street signs on metal poles on the side of a street in front of green bushes.
>
> **Caption B:** The stop sign has the word war written on it, there is also a yellow sign underneath it.
>
> **Adopted scope:** pole count
>
> **Extracted A:** plural poles
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second describes two signs but does not establish their mounting poles or pole count.

**Audit explanation:** The second signs' mounting poles and pole count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 519. train_5165: `Presence of electronics`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black and white image of some electronics near a pen and cup of coffee.
>
> **Caption B:** A piece of paper that has a hole punch, scissors, and a pencil on top of it.
>
> **Adopted scope:** electronics presence
>
> **Extracted A:** present
>
> **Extracted B:** unknown
>
> **Recorded reason, verbatim:** Paper, scissors and pencil do not assert that electronics are absent from the second scene.

**Audit explanation:** Electronics presence remains unknown in the second stationery scene.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 520. train_5166: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A TV stands in a corner on top of a small wooden entertainment center.
>
> **Caption B:** Television and VCR console flanked by tan leather recliner and white plastic cube side table.
>
> **Adopted scope:** principal electronic color
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Neither television's color is given; tan and white describe nearby furniture.

**Audit explanation:** Both television colors remain unspecified. Tan and white describe nearby furniture.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 521. train_5177: `body posture`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman holding a baby sit at a table with a partially eaten pizza.
>
> **Caption B:** A baby wearing a tie eats with his hands in front of an adult.
>
> **Adopted scope:** body posture of described people
>
> **Extracted A:** woman seated holding baby
>
> **Extracted B:** baby eating in front of adult; both postures unstated
>
> **Recorded reason, verbatim:** The second caption supplies eating activity and relative location, but no comparable body posture for either person. Eating can occur sitting or standing and does not itself recover the requested posture.

**Audit explanation:** The second baby's eating and position before an adult leave both people's body postures unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 522. train_5181: `location of signs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A street sign that has the names of two streets and a right turn only sign on the pole.
>
> **Caption B:** a bunch of signs that  could be confusing to some people and a temp gage
>
> **Adopted scope:** sign location
>
> **Extracted A:** on pole
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second group of signs has no given mounting or physical location.

**Audit explanation:** The second signs' mounting and physical location remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 523. train_5200: `direction of plane`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A large passenger jet flying through a blue sky with it's landing gear down.
>
> **Caption B:** A large Delta passenger airplane ascending into the air with the nose of the plane pointing upward.
>
> **Adopted scope:** plane direction
>
> **Extracted A:** unspecified flight
>
> **Extracted B:** ascending
>
> **Recorded reason, verbatim:** Landing gear down does not establish the first plane's direction; it may occur during ascent or descent.

**Audit explanation:** The first jet's lowered landing gear leaves ascent, descent or level flight unresolved.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 524. train_5204: `name of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The man holds a cell phone with a plate of food next to a dessert.
>
> **Caption B:** A man sitting at a table eating a slice of cake with whipped cream.
>
> **Adopted scope:** person identity/name
>
> **Extracted A:** unnamed man
>
> **Extracted B:** unnamed man
>
> **Recorded reason, verbatim:** Neither man is given a personal name, which this condition requires.

**Audit explanation:** Both men's personal names remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 525. train_5213: `weight of items`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A sink with one basin but two faucets in front of a large mirror.
>
> **Caption B:** An open shower with a towel on the edge of the tub next to a toilet.
>
> **Adopted scope:** item weight
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** No comparative weights are supplied for the fixtures in either caption.

**Audit explanation:** Both sets of fixture weights remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 526. train_5241: `type of reflection`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** an image of a dog riding in the car with its head out the window
>
> **Caption B:** A man taking a picture of himself and a dog, as reflected in a side view mirror.
>
> **Adopted scope:** reflection type
>
> **Extracted A:** no reflection stated
>
> **Extracted B:** side-mirror reflection
>
> **Recorded reason, verbatim:** The first is an image of a dog in a car, with no reflection established.

**Audit explanation:** The first dog image leaves a reflection unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 527. train_5252: `type of flower`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Several boot designed flower planters on sticks with different types of flowers in them.
>
> **Caption B:** a table with three different vases on it, one with red and white flowers 
>
> **Adopted scope:** flower type
>
> **Extracted A:** different varieties unspecified
>
> **Extracted B:** variety unspecified
>
> **Recorded reason, verbatim:** Neither caption identifies any flower variety; unspecified different types and colors alone do not supply it.

**Audit explanation:** Both captions leave flower varieties unspecified. The second supplies flower colors only.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 528. train_5253: `color of flower`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Several boot designed flower planters on sticks with different types of flowers in them.
>
> **Caption B:** a table with three different vases on it, one with red and white flowers 
>
> **Adopted scope:** flower color
>
> **Extracted A:** unstated
>
> **Extracted B:** red and white
>
> **Recorded reason, verbatim:** The first flowers have no stated color.

**Audit explanation:** The first flowers' colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 529. train_5254: `method of carrying`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Elephants walking together down an unpaved path with a small shop in the background.
>
> **Caption B:** Elephants carry people dressed in green on howdahs as they walk down a street.
>
> **Adopted scope:** carrying method
>
> **Extracted A:** no load/carriage described
>
> **Extracted B:** people in howdahs
>
> **Recorded reason, verbatim:** Walking elephants do not establish a carried load or carrying method in the first.

**Audit explanation:** The first walking elephants leave a carried load and carrying method unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 530. train_5263: `type of view`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a traffic sign displaying a forked path to the left with roundabout, and a forked path to the right
>
> **Caption B:** A very close up view of a traffic signal with blue sky behind it.
>
> **Adopted scope:** view type
>
> **Extracted A:** unspecified
>
> **Extracted B:** close-up
>
> **Recorded reason, verbatim:** The first sign's content is described without a viewing distance comparable with the close-up.

**Audit explanation:** The first sign's viewing distance remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 531. train_5265: `body posture`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Here is various different images of people taking care of and spending time with an elephant.
>
> **Caption B:** an elephant walking down the sidewalk with people riding on the back of it
>
> **Adopted scope:** people posture
>
> **Extracted A:** unstated during care
>
> **Extracted B:** seated riding inferred
>
> **Recorded reason, verbatim:** Caring for and spending time with an elephant does not establish the people's body posture.

**Audit explanation:** The first people's elephant-care activity leaves their body postures unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 532. train_5278: `type of oven`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Guy stands in front of brick oven as he cuts a pizza up into slices
>
> **Caption B:** A pile of dough sitting on cookie sheet sitting in front of a oven.
>
> **Adopted scope:** oven subtype
>
> **Extracted A:** brick oven
>
> **Extracted B:** oven, subtype unspecified
>
> **Recorded reason, verbatim:** The second repeats oven without a recoverable oven subtype; the target noun alone is insufficient.

**Audit explanation:** The second oven's subtype remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 533. train_5286: `cat in street`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A cat sits in the foreground looking at the camera while a bright yellow motor cycle is in the background.
>
> **Caption B:** a cute cat standing by a street sign sitting on the back of a rusty blue truck
>
> **Adopted scope:** cat situated in a street setting
>
> **Extracted A:** cat with a motorcycle behind it, street unestablished
>
> **Extracted B:** cat on truck beside street sign
>
> **Recorded reason, verbatim:** A motorcycle alone does not establish the first cat's street location, so the explicit spatial predicate lacks support.

**Audit explanation:** The first cat's background motorcycle leaves the required street location unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 534. train_5290: `color of water`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A beach scene with people in the water and a kite in the sky.
>
> **Caption B:** A sandy terrain with footprints has a mirage of water in the near distance.
>
> **Adopted scope:** water color
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated mirage
>
> **Recorded reason, verbatim:** Neither the real water nor the mirage is assigned a color.

**Audit explanation:** Both the first water and second mirage have unspecified colors.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 535. train_5291: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A beach scene with people in the water and a kite in the sky.
>
> **Caption B:** A sandy terrain with footprints has a mirage of water in the near distance.
>
> **Adopted scope:** people count
>
> **Extracted A:** plural people
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Footprints indicate prior passage, not a current person count in the second scene.

**Audit explanation:** The second footprints establish prior passage. Current people presence and count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 536. train_5295: `color of dog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog is sitting on the passenger seat of a vehicle parked near a waterfront
>
> **Caption B:** A white dog hanging it's head out the side of a car door window.
>
> **Adopted scope:** dog color
>
> **Extracted A:** unstated
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** The first dog's color is not stated.

**Audit explanation:** The first dog's coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 537. train_5320: `action of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** two zebras close to one another in a field with trees in the background
>
> **Caption B:** A zebra and its child standing in a grassy field under the shade of a tree
>
> **Adopted scope:** animal action
>
> **Extracted A:** being near each other, stance unknown
>
> **Extracted B:** standing
>
> **Recorded reason, verbatim:** Spatial closeness of the first zebras does not determine whether they stand, walk or perform another action.

**Audit explanation:** The first zebras' closeness establishes relative position. Their actions and stance remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 538. train_5341: `type of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A truck is on the road near traffic lights that are on the cement.
>
> **Caption B:** A red and white no parking sign sitting on the side of a street.
>
> **Adopted scope:** vehicle type
>
> **Extracted A:** truck
>
> **Extracted B:** no vehicle described
>
> **Recorded reason, verbatim:** A no-parking sign does not establish any described vehicle in the second caption.

**Audit explanation:** The second parking restriction sign leaves a vehicle and corresponding type unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 539. train_5352: `name of elephant`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Looking up the trunk and head of an elephant to tourists riding on its head
>
> **Caption B:** A man sitting on top of an elephant that is standing in the mud.
>
> **Adopted scope:** individual elephant name
>
> **Extracted A:** unnamed elephant
>
> **Extracted B:** unnamed elephant
>
> **Recorded reason, verbatim:** The condition already identifies elephant and asks its individual name; neither caption supplies one.

**Audit explanation:** Both elephants' individual names remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `5.0`.

### 540. train_5353: `name of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Looking up the trunk and head of an elephant to tourists riding on its head
>
> **Caption B:** A man sitting on top of an elephant that is standing in the mud.
>
> **Adopted scope:** place
>
> **Extracted A:** unstated
>
> **Extracted B:** muddy ground
>
> **Recorded reason, verbatim:** Looking upward at an elephant and riders does not identify the first physical place.

**Audit explanation:** The first upward view of an elephant and riders leaves physical place information unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 541. train_5366: `color of playing costume`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The tennis player in the blue t-shirt is hitting a ball with the racket.
>
> **Caption B:** A boy playing tennis on a hard surface tennis court with a chain link fence behind him.
>
> **Adopted scope:** sports-clothing color
>
> **Extracted A:** blue
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second tennis player's outfit color is absent.

**Audit explanation:** The second tennis player's clothing color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 542. train_5368: `number of dish`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Small vase with water and flowers make the center piece for this table next to fork and salt and pepper shaker.
>
> **Caption B:** A lot of oranges are on a plate, with some having spilled onto a table.
>
> **Adopted scope:** dish count
>
> **Extracted A:** no serving dish described
>
> **Extracted B:** one plate
>
> **Recorded reason, verbatim:** A flower vase, fork and shakers do not establish a food-serving dish count.

**Audit explanation:** The first flower vase, fork and shakers leave food-serving dishes and their count unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 543. train_5369: `table centerpiece`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Small vase with water and flowers make the center piece for this table next to fork and salt and pepper shaker.
>
> **Caption B:** A lot of oranges are on a plate, with some having spilled onto a table.
>
> **Adopted scope:** table centerpiece type
>
> **Extracted A:** flowers in a vase explicitly used as centerpiece
>
> **Extracted B:** oranges on a plate, centerpiece role unestablished
>
> **Recorded reason, verbatim:** Ordinary food on a table is not automatically a centerpiece; the second caption does not supply the required display role.

**Audit explanation:** The second oranges and plate have an unestablished table-centerpiece role.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 544. train_5411: `color of device`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black laptop sitting on a desk across from some people at other working areas.
>
> **Caption B:** A laptop is on a table and chairs next to it looking down the hall is a bookshelf full of books.
>
> **Adopted scope:** device color
>
> **Extracted A:** black
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second laptop has no stated color.

**Audit explanation:** The second laptop's color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 545. train_5421: `style of decor`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Picture of a tab tub where the wall is open exposing wood studs and a shop vacuum is in the tub.
>
> **Caption B:** A small bathroom features a painting of birch trees, a beveled mirror and a sink cabinet with multi-pane glass windows. 
>
> **Adopted scope:** overall decor style category
>
> **Extracted A:** renovation with exposed studs, style unspecified
>
> **Extracted B:** painting and decorative fixtures, style unspecified
>
> **Recorded reason, verbatim:** Construction state and named ornaments do not establish an overall decor style such as modern or traditional.

**Audit explanation:** Both bathrooms' overall decor styles remain unspecified despite construction details and individual ornaments.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 546. train_5425: `number of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person's lap is visible in front of a television and a bright lamp.
>
> **Caption B:** A TV stands in a corner on top of a small wooden entertainment center.
>
> **Adopted scope:** people count
>
> **Extracted A:** one
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second television scene contains no described person count.

**Audit explanation:** The second television scene leaves people presence and count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 547. train_5435: `number of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two gondoliers have people in them as rowers stand on the back of them with long poles.
>
> **Caption B:** Small boat in canal between two buildings, two riders and dog standing on bow.
>
> **Adopted scope:** animal count
>
> **Extracted A:** unstated
>
> **Extracted B:** one dog
>
> **Recorded reason, verbatim:** No animal count is available from the first boats-and-people description.

**Audit explanation:** The first boats and rowers leave animal presence and count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 548. train_5448: `color of hat`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A boy with a hat on and a bat, glove and ball in his hands. 
>
> **Caption B:** A child in a blue hat, black shirt and jeans hitting a green ball with a bat. 
>
> **Adopted scope:** hat color
>
> **Extracted A:** unstated
>
> **Extracted B:** blue
>
> **Recorded reason, verbatim:** The first hat's color is absent.

**Audit explanation:** The first hat's color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 549. train_5451: `presence of plants`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a wall with some green plants and a white steeple with a black clock
>
> **Caption B:** A clock tower on top of a building with some statues and a bell on top.
>
> **Adopted scope:** plant presence
>
> **Extracted A:** present
>
> **Extracted B:** unknown
>
> **Recorded reason, verbatim:** The clock tower scene does not establish whether plants are absent.

**Audit explanation:** Plant presence remains unknown in the second clock-tower scene.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 550. train_5458: `name of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A mouse with trackball sits next to another mouse, a remote control and a laptop.
>
> **Caption B:** A picture of a dark room with a laptop and clock illuminated by a desk lamp.
>
> **Adopted scope:** place
>
> **Extracted A:** unspecified surface
>
> **Extracted B:** dark room
>
> **Recorded reason, verbatim:** The first device list gives no room or supporting place to compare with the dark room.

**Audit explanation:** The first device list leaves a room or supporting place unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 551. train_5479: `speed of official's movement`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A baseball player in a green jersey is in the middle of a play , with the official standing in the frame .
>
> **Caption B:** A baseball player attempting to score a run before the catcher tags the player out .
>
> **Adopted scope:** official movement
>
> **Extracted A:** standing
>
> **Extracted B:** official unmentioned
>
> **Recorded reason, verbatim:** The second catcher is a player, and no official is described whose speed can be extracted.

**Audit explanation:** The second catcher is a player. An official and corresponding movement speed remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 552. train_5507: `speed of dogs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The brown and white dog ran through the green grass .
>
> **Caption B:** Two dogs play with an orange toy in tall grass .
>
> **Adopted scope:** dog speed
>
> **Extracted A:** running
>
> **Extracted B:** playing, speed unspecified
>
> **Recorded reason, verbatim:** Playing with a toy does not establish a locomotion speed for the second dogs.

**Audit explanation:** The second dogs' toy play leaves locomotion speed unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 553. train_5515: `color of outfit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Cyclists compete in a race that takes them on a dirt mountain road .
>
> **Caption B:** man in blue , orange and white outfit with black and white helmet riding bike in race .
>
> **Adopted scope:** outfit colors
>
> **Extracted A:** unstated
>
> **Extracted B:** blue, orange, white
>
> **Recorded reason, verbatim:** The first cyclists' outfit colors are unspecified.

**Audit explanation:** The first cyclists' clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 554. train_5516: `color of dog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** White dog in midair next to a large yellow ball .
>
> **Caption B:** A dog stands on his hind legs amid a shower of tennis balls .
>
> **Adopted scope:** dog color
>
> **Extracted A:** white
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second dog's coat color is absent.

**Audit explanation:** The second dog's coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 555. train_5517: `activity of ball`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** White dog in midair next to a large yellow ball .
>
> **Caption B:** A dog stands on his hind legs amid a shower of tennis balls .
>
> **Adopted scope:** ball motion
>
> **Extracted A:** unstated beside airborne dog
>
> **Extracted B:** falling/showering
>
> **Recorded reason, verbatim:** An airborne dog beside a ball does not establish the ball's own motion.

**Audit explanation:** The first dog's airborne position leaves the neighboring ball's motion unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 556. train_5574: `race of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Chinese or Japanese shopping downtown in the streets .
>
> **Caption B:** In a busy Asian city , two women walk and talk together .
>
> **Adopted scope:** people ethnicity
>
> **Extracted A:** Chinese/Japanese described
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The first names a Chinese or Japanese identity; an Asian city alone does not establish the second women's ethnicity.

**Audit explanation:** The second women's ethnicity remains unspecified by the Asian city setting.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 557. train_5597: `movement relative to water`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A little girl runs along the beach toward a man who admires the sky .
>
> **Caption B:** A girl in pink runs away from a wave coming onto the shore .
>
> **Adopted scope:** water-relative movement
>
> **Extracted A:** along beach toward man
>
> **Extracted B:** away from incoming wave
>
> **Recorded reason, verbatim:** Running toward a man along the beach does not specify motion toward or away from the water.

**Audit explanation:** The first girl's movement toward or away from water remains unspecified during her approach to the man.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 558. train_5602: `activity of persons`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A group of mountain climbers rests at the summit .
>
> **Caption B:** A mountain climber on a snowy plain near a mountaintop .
>
> **Adopted scope:** climber activity
>
> **Extracted A:** resting
>
> **Extracted B:** unspecified presence
>
> **Recorded reason, verbatim:** The second climber is merely located near a mountaintop without a current activity.

**Audit explanation:** The second climber's current activity remains unspecified near the summit.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 559. train_5607: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Woman with pink polka dot backpack holding a child .
>
> **Caption B:** A man in a white shirt with a child on his shoulders .
>
> **Adopted scope:** adult clothing color
>
> **Extracted A:** unstated; backpack pink
>
> **Extracted B:** white shirt
>
> **Recorded reason, verbatim:** Pink describes a backpack, leaving the first person's clothing color unstated.

**Audit explanation:** The first woman's clothing color remains unspecified. Pink describes the backpack.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 560. train_5615: `color`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man is playing an electric guitar , while another man is playing another instrument .
>
> **Caption B:** Two musicians in white suits play guitars while surrounded by associated gear and a red curtain .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** unstated
>
> **Extracted B:** white suits
>
> **Recorded reason, verbatim:** The first musicians have no stated clothing color.

**Audit explanation:** The first musicians' clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 561. train_5660: `type of stunt`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bicyclist is jumping on ramp covered with graffiti .
>
> **Caption B:** on a gorges sunny day , young man doing a trick on a BMX bike .
>
> **Adopted scope:** stunt
>
> **Extracted A:** bicycle ramp jump
>
> **Extracted B:** BMX trick unspecified
>
> **Recorded reason, verbatim:** A generic BMX trick does not identify a stunt type to compare with a ramp jump.

**Audit explanation:** The second unnamed BMX trick leaves stunt type unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 562. train_5671: `length of hair`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two women with short hair and miniature hats put on a show in public .
>
> **Caption B:** These women look like Wiccans performing a ceremonial dance .
>
> **Adopted scope:** hair length
>
> **Extracted A:** short
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second women's ceremonial activity does not supply hair length.

**Audit explanation:** The second women's hair length remains unspecified during ceremonial dancing.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 563. train_5675: `type of fabric`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman in a surgical mask holds a very small baby .
>
> **Caption B:** A nurse placing a blanket around a newborn baby .
>
> **Adopted scope:** fabric type
>
> **Extracted A:** unstated
>
> **Extracted B:** blanket material unstated
>
> **Recorded reason, verbatim:** Neither caption identifies fabric material; a blanket alone does not specify its fabric.

**Audit explanation:** Both fabric materials remain unspecified, including the second blanket's fabric.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 564. train_5723: `color of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A small dog lands on a big dog trying to get a disc .
>
> **Caption B:** A brown and white dog stands on the sand to look at another dog .
>
> **Adopted scope:** animal colors
>
> **Extracted A:** unstated
>
> **Extracted B:** brown/white, other unknown
>
> **Recorded reason, verbatim:** Small and big describe dog size; neither first animal is given a color.

**Audit explanation:** The first dogs' coat colors remain unspecified by their small and big sizes.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 565. train_5731: `sentiment of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man jumps over another man doing a back flip .
>
> **Caption B:** The man is performing a trick off a ramp with a bicycle .
>
> **Adopted scope:** person sentiment
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Neither acrobatic activity establishes the person's emotion.

**Audit explanation:** Both acrobatic scenes leave the men's emotions unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 566. train_5739: `interaction between players`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** In a football match , a Panthers player falls forward into a somersault while gripping the football .
>
> **Caption B:** A football player is tackling another football player of the opposing team .
>
> **Adopted scope:** player interaction
>
> **Extracted A:** falling alone, other player absent
>
> **Extracted B:** tackling opponent
>
> **Recorded reason, verbatim:** The first describes one player falling, without any interaction with another player.

**Audit explanation:** The first player's fall leaves an interaction with another player unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 567. train_5741: `sentiment of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A skateboarder casts a shadow jumping down stairs .
>
> **Caption B:** A person wearing rollerblades is skating along side a railing .
>
> **Adopted scope:** sentiment
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Skating and jumping give no sentiment value in either caption.

**Audit explanation:** Both skating activities leave sentiment unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 568. train_5745: `wrist-wear`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An upside down man in a black shirt with red wristbands .
>
> **Caption B:** A young man in a grassy park caught midair , upside down in the middle of flip .
>
> **Adopted scope:** wrist wear
>
> **Extracted A:** red wristbands
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second man has no specified wrist accessory.

**Audit explanation:** The second flipping man's wrist-wear remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 569. train_5752: `number of bicycles`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A person rides their bicycle onto a rock and balances on one wheel .
>
> **Caption B:** person wearing a helmet on a four wheeled bike in air
>
> **Adopted scope:** bicycle count
>
> **Extracted A:** one bicycle
>
> **Extracted B:** four-wheeled bike, non-bicycle
>
> **Recorded reason, verbatim:** The second explicitly describes a four-wheeled bike, not a bicycle, so the required vehicle is unavailable.

**Audit explanation:** The second vehicle has four wheels, leaving a bicycle and corresponding bicycle count unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `5.0`.

### 570. train_5755: `type of ground`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A child , backlit by the sun , jumping in the air , with the ocean in the background .
>
> **Caption B:** Young woman in summer clothes jumping up and down on rocky shoreline .
>
> **Adopted scope:** ground type
>
> **Extracted A:** unspecified coastal ground
>
> **Extracted B:** rocky shore
>
> **Recorded reason, verbatim:** An ocean in the background does not specify the child's supporting ground material.

**Audit explanation:** The first ocean backdrop leaves the child's supporting ground type unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 571. train_5765: `color of outfit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man is riding a BMX bike with a forest in the background .
>
> **Caption B:** A man in a red outfit jumps his motocross bike down the hill .
>
> **Adopted scope:** outfit color
>
> **Extracted A:** unstated
>
> **Extracted B:** red
>
> **Recorded reason, verbatim:** The first rider has no stated outfit color.

**Audit explanation:** The first BMX rider's clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 572. train_5785: `color of outfit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** People are watching a snowboarder perform a trick in the air .
>
> **Caption B:** A snowboarder in green pants boards down a snowy mountain .
>
> **Adopted scope:** athlete outfit color
>
> **Extracted A:** unstated
>
> **Extracted B:** green pants
>
> **Recorded reason, verbatim:** The first snowboarder's outfit color is not supplied.

**Audit explanation:** The first snowboarder's clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 573. train_5798: `size of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The big , black , running dog is wearing a strap around its chest .
>
> **Caption B:** A black dog walking in dirt has a soccer ball in his mouth .
>
> **Adopted scope:** dog size
>
> **Extracted A:** big
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Holding an unscaled soccer ball does not reliably establish the second dog's body size.

**Audit explanation:** The second dog's body size remains unspecified by its coat and soccer ball.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 574. train_5805: `age of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** There is a child on a sled type machine , in the snow .
>
> **Caption B:** A skier is coming down the slope and stirring up a lot of snow behind him .
>
> **Adopted scope:** person age
>
> **Extracted A:** child
>
> **Extracted B:** unstated skier
>
> **Recorded reason, verbatim:** The skier's age is unspecified in the second caption.

**Audit explanation:** The second skier's age remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 575. train_5816: `absence of helmet`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person in purple shorts riding a bike up a mountain .
>
> **Caption B:** A man wearing a helmet is riding his bike down rocky terrain .
>
> **Adopted scope:** helmet absence
>
> **Extracted A:** unknown
>
> **Extracted B:** helmet present
>
> **Recorded reason, verbatim:** The first rider's helmet is unmentioned, which does not establish its absence.

**Audit explanation:** The first rider's helmet status remains unknown.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 576. train_5845: `distance covered by dogs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A little white and brown dog is running in the water .
>
> **Caption B:** Three dogs in different shades of brown are playing in the water .
>
> **Adopted scope:** distance covered
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Running and playing supply no distance traveled in either caption.

**Audit explanation:** Both dogs' water activities leave distance traveled unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 577. train_5857: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Men dressed in red and men dressed in white are playing a game of soccer .
>
> **Caption B:** Soccer players are shaking each others hands on the soccer field .
>
> **Adopted scope:** clothing colors
>
> **Extracted A:** red and white
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second soccer players' clothing colors are unspecified.

**Audit explanation:** The second soccer players' clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 578. train_5887: `person's eyewear`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Child is splashing around in a green and blue pool .
>
> **Caption B:** A little boy in glasses jumps into a spray of water .
>
> **Adopted scope:** eyewear
>
> **Extracted A:** unstated
>
> **Extracted B:** glasses
>
> **Recorded reason, verbatim:** The first child has no stated eyewear.

**Audit explanation:** The first child's eyewear remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 579. train_5907: `direction of biking`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in aerodynamic gear riding a professional mountain bike through a forest .
>
> **Caption B:** A mountain biker wearing a colorful helmet rides downhill .
>
> **Adopted scope:** cycling direction
>
> **Extracted A:** through forest, slope direction unknown
>
> **Extracted B:** downhill
>
> **Recorded reason, verbatim:** Traveling through forest does not establish uphill or downhill direction.

**Audit explanation:** The first cyclist's forest location leaves uphill or downhill direction unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 580. train_5908: `people's spatial orientation`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Many people on a roller coaster ride are flipped upside down over a white track .
>
> **Caption B:** People are riding the Cyclone thrill ride at the Coney Island amusement park .
>
> **Adopted scope:** people orientation
>
> **Extracted A:** upside down
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Naming a roller coaster does not fix the riders' orientation at that moment.

**Audit explanation:** The named roller coaster leaves its riders' current spatial orientation unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 581. train_5909: `people's attitudes`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Many people on a roller coaster ride are flipped upside down over a white track .
>
> **Caption B:** People are riding the Cyclone thrill ride at the Coney Island amusement park .
>
> **Adopted scope:** people attitudes
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Neither ride description establishes the people's attitude or feeling.

**Audit explanation:** Both roller-coaster scenes leave the riders' attitudes and feelings unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 582. train_5929: `color of shirt`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Toddler boy wearing airplane shirt , in stroller with large beads .
>
> **Caption B:** There is a little boy in a red shirt and a dirty face and he is smiling .
>
> **Adopted scope:** shirt color
>
> **Extracted A:** unstated
>
> **Extracted B:** red
>
> **Recorded reason, verbatim:** An airplane graphic identifies a shirt motif, not its color.

**Audit explanation:** The first shirt's airplane motif leaves its color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 583. train_5931: `animal's stance`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog stands on his hind legs while another dog looks on .
>
> **Caption B:** One tan dog with a stick and one mostly black dog .
>
> **Adopted scope:** animal stance
>
> **Extracted A:** hind-leg standing
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second dogs' possession and colors do not establish their stance.

**Audit explanation:** The second dogs' stance remains unspecified by their colors and stick possession.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 584. train_5948: `game being played`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The young man dives on the field during a sporting event .
>
> **Caption B:** A rugby player running the ball between two downed opponents .
>
> **Adopted scope:** game identity
>
> **Extracted A:** unspecified sporting event on field
>
> **Extracted B:** rugby
>
> **Recorded reason, verbatim:** Diving during a field sporting event does not identify any game type; a location alone is not a recoverable game subtype.

**Audit explanation:** The first field sporting event leaves game identity unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 585. train_5954: `name of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** There is a cowboy in a rodeo trying to lasso a calf .
>
> **Caption B:** Two men on horses chasing an animal at a rodeo .
>
> **Adopted scope:** animal being chased or lassoed, aligned by its action role
>
> **Extracted A:** calf
>
> **Extracted B:** unnamed chased animal
>
> **Recorded reason, verbatim:** The calf is the target of the cowboy's lasso, and the unnamed animal is the target of the riders' chase. These are the comparable principal animal roles. Substituting the riding horses would compare a mount with the chase target. The second target has no stated animal type.

**Audit explanation:** The second chase target's animal type remains unspecified. The named horses carry the riders.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 586. train_5967: `manner of game playing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A big brown dog plays with a smaller gray dog on the grass .
>
> **Caption B:** Two shaggy yellow dogs playing in a rough manner .
>
> **Adopted scope:** play manner
>
> **Extracted A:** playing unspecified
>
> **Extracted B:** rough play
>
> **Recorded reason, verbatim:** Playing alone does not establish the requested manner of play, such as roughness.

**Audit explanation:** The first dogs' generic playing leaves play manner unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 587. train_5981: `color of outfit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A little girl giggles and smiles happily as she kneels on her bed .
>
> **Caption B:** One young girl dressed in red polka dot outfit plays with toy .
>
> **Adopted scope:** outfit color
>
> **Extracted A:** unstated
>
> **Extracted B:** red
>
> **Recorded reason, verbatim:** The first girl's happy expression gives no outfit color.

**Audit explanation:** The first girl's happy expression leaves her outfit color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 588. train_5985: `orientation of snowboarder`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person on a yellow snowboard does some tricks in the snow .
>
> **Caption B:** A snowboarder soars off a jump upside down at the mountain resort 's terrain park .
>
> **Adopted scope:** body orientation
>
> **Extracted A:** unspecified trick
>
> **Extracted B:** upside down
>
> **Recorded reason, verbatim:** Doing unspecified tricks does not determine the first snowboarder's orientation.

**Audit explanation:** The first snowboarder's unspecified tricks leave body orientation unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 589. train_5991: `color of horse`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a young boy wearing a cowboy hat and riding on a horse
>
> **Caption B:** Fellow cowboys watch as a colleague rides a black airborne horse .
>
> **Adopted scope:** horse color
>
> **Extracted A:** unstated
>
> **Extracted B:** black
>
> **Recorded reason, verbatim:** The first horse has no stated color.

**Audit explanation:** The first horse's color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 590. train_6021: `person's age`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young man does tricks with his bike on a course .
>
> **Caption B:** A person doing a bicycle trick over a wooden ramp .
>
> **Adopted scope:** person age
>
> **Extracted A:** young adult
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second cyclist has no recoverable age description.

**Audit explanation:** The second cyclist's age remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 591. train_6069: `intention of skaters`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The two boys are wearing ice skates and hockey equipment .
>
> **Caption B:** Children skating while people watch on the side .
>
> **Adopted scope:** skater intention
>
> **Extracted A:** hockey participation inferred
>
> **Extracted B:** skating, purpose unspecified
>
> **Recorded reason, verbatim:** Generic skating does not establish the second participants' purpose or intention.

**Audit explanation:** The second children's generic skating leaves their intentions unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 592. train_6077: `positioning of racers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Bicyclist pull ahead of other racers with the crowd cheering wildly .
>
> **Caption B:** Many bicyclists are racing down a very narrow city street .
>
> **Adopted scope:** racer positioning
>
> **Extracted A:** one ahead of others
>
> **Extracted B:** relative order unstated
>
> **Recorded reason, verbatim:** A narrow street does not specify the relative ordering of the second racers.

**Audit explanation:** The second racers' relative order remains unspecified on the narrow street.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 593. train_6085: `names of persons`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Four black children sit in the sand with various empty food containers .
>
> **Caption B:** A black woman and two black children are sitting in a thatched tent .
>
> **Adopted scope:** personal names
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Neither caption supplies any person's individual name.

**Audit explanation:** Both groups' personal names remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 594. train_6123: `absence of blue ball`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Three dogs on grass , one with a blue ball in its mouth .
>
> **Caption B:** Three dogs run on wide , grassy , outdoor area .
>
> **Adopted scope:** blue-ball absence
>
> **Extracted A:** ball present
>
> **Extracted B:** unknown
>
> **Recorded reason, verbatim:** The second dogs' running does not establish absence of a blue ball.

**Audit explanation:** The second dogs' running leaves blue-ball presence unknown.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 595. train_6161: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Man in white shirt and tan pants is putting new shingles on roof .
>
> **Caption B:** Under sunny skies , a worker helps in the framing of new building .
>
> **Adopted scope:** construction-object color
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** White and tan describe clothing, not the construction materials, whose colors are unavailable in both captions.

**Audit explanation:** Both sets of construction materials have unspecified colors. White and tan describe clothing.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 596. train_6185: `object in dog's mouth`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A dog with a collar and tag runs with its tongue out on a path .
>
> **Caption B:** The dog is running with a yellow ball in his mouth .
>
> **Adopted scope:** object carried in the dog's mouth
>
> **Extracted A:** tongue extended, no carried object established
>
> **Extracted B:** yellow ball
>
> **Recorded reason, verbatim:** A tongue is the dog's body part, not an independently carried object; the first mouth-object value is unavailable.

**Audit explanation:** The first extended tongue is a body part. A separately carried mouth object remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 597. train_6189: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A boy with scruffy , dark hair is skateboarding on the sidewalk .
>
> **Caption B:** a boy on skateboard is making a jump from a blue bench beside a white wall .
>
> **Adopted scope:** skateboard color
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Hair, bench and wall colors do not supply either skateboard's color.

**Audit explanation:** Both skateboards' colors remain unspecified by nearby hair, bench and wall colors.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 598. train_6201: `size of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A large yellow dog and a small white dog in the grass .
>
> **Caption B:** Black dog jumping over a white dog in a snowy path .
>
> **Adopted scope:** dog size
>
> **Extracted A:** large and small
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Jumping over another dog does not establish the second dogs' body sizes.

**Audit explanation:** The second dogs' jumping relation leaves their body sizes unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 599. train_6206: `height of grass`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The large brown dog is running through the grass with a large stick in its mouth .
>
> **Caption B:** A dog with floppy ears runs on the grass , a fence behind it .
>
> **Adopted scope:** grass height
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Neither grass description gives its height.

**Audit explanation:** Both grass heights remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 600. train_6209: `color of outfit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman in a white top and blue shorts is playing tennis .
>
> **Caption B:** In an athletic stance , the woman awaits the tennis ball .
>
> **Adopted scope:** outfit color
>
> **Extracted A:** white and blue
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second tennis player's outfit colors are not provided.

**Audit explanation:** The second tennis player's clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 601. train_6237: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Man in a red shirt and olive colored cargo shorts trying to rock climb .
>
> **Caption B:** a man with a red headband climbing a rock cliff looming over greenery .
>
> **Adopted scope:** clothing colors
>
> **Extracted A:** red shirt and olive shorts
>
> **Extracted B:** clothes unstated, red headband
>
> **Recorded reason, verbatim:** The red headband is an accessory; the second person's clothing colors are unstated.

**Audit explanation:** The second person's red headband leaves clothing colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 602. train_6263: `location of activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white dog wearing a blue collar runs for a green ball .
>
> **Caption B:** A white racing dog with a muzzle is racing around the turn of a dirt track .
>
> **Adopted scope:** activity location
>
> **Extracted A:** unstated
>
> **Extracted B:** dirt race track
>
> **Recorded reason, verbatim:** Running for a ball does not identify the first dog's activity location.

**Audit explanation:** The first dog's running toward a ball leaves its activity setting unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 603. train_6271: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white dog runs over a snowy field or lawn , with a log in his jaws .
>
> **Caption B:** A dog , trailing a leash , chases a tennis ball across a grassy area .
>
> **Adopted scope:** animal color
>
> **Extracted A:** white
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second dog's coat color is unstated.

**Audit explanation:** The second dog's coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 604. train_6283: `setting of motorcycle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An individual adorned in white rides a motorcycle .
>
> **Caption B:** A motorcycle racer going down a steep , dirt hill .
>
> **Adopted scope:** riding setting
>
> **Extracted A:** unstated
>
> **Extracted B:** steep dirt hill
>
> **Recorded reason, verbatim:** The first motorcycle rider has no stated terrain or setting.

**Audit explanation:** The first motorcycle rider's terrain and setting remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 605. train_6293: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The man wearing a green jacket is riding a bike through deep snow .
>
> **Caption B:** A guy snowboarding down a pole that is on top of a blue vehicle into the snow .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** green
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Blue refers to a vehicle, leaving the second person's clothing color unavailable.

**Audit explanation:** The second snowboarder's clothing colors remain unspecified. Blue describes the vehicle.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 606. train_6300: `color of umbrellas`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A couple walks through the rain with their child holding umbrellas .
>
> **Caption B:** A woman walks down the road in all black as she holds a red umbrella over her head in the rain .
>
> **Adopted scope:** umbrella color
>
> **Extracted A:** unstated
>
> **Extracted B:** red
>
> **Recorded reason, verbatim:** The first umbrellas have no specified colors.

**Audit explanation:** The first umbrellas' colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 607. train_6303: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young child wearing a yellow wetsuit rides on a surfboard .
>
> **Caption B:** A surfer in a wetsuit balances on his board amidst ocean spray .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** yellow
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second wetsuit has no stated color.

**Audit explanation:** The second wetsuit's color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 608. train_6323: `type of construction`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** 5 men in yellow vest working at construction site .
>
> **Caption B:** Workman on a scaffold are finishing a ceiling of a building .
>
> **Adopted scope:** construction type
>
> **Extracted A:** unspecified construction
>
> **Extracted B:** ceiling finishing
>
> **Recorded reason, verbatim:** Generic construction work does not identify a construction type or task.

**Audit explanation:** The first generic construction work leaves construction type and task unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 609. train_6329: `presence or absence of singing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man playing acoustic guitar in front of a shop window .
>
> **Caption B:** A man with a mustache and a guitar sings for tips on the street .
>
> **Adopted scope:** singing presence
>
> **Extracted A:** unknown
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** Playing guitar does not establish that singing is absent in the first scene.

**Audit explanation:** The first guitarist's singing status remains unknown.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 610. train_6337: `presence of flag`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A performer riding a horse , while waving the American flag and wearing green .
>
> **Caption B:** A rodeo rider on a bucking horse with a clown in the background .
>
> **Adopted scope:** flag presence
>
> **Extracted A:** present
>
> **Extracted B:** unknown
>
> **Recorded reason, verbatim:** The second rodeo scene does not establish flag absence.

**Audit explanation:** Flag presence remains unknown in the second rodeo scene.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 611. train_6345: `pattern of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The soccer player in the checked shirt is moving the ball pursued by the players on the other team .
>
> **Caption B:** Three soccer players , two in orange one in yellow , running for the ball on a soccer field .
>
> **Adopted scope:** clothing pattern
>
> **Extracted A:** checked
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Orange and yellow specify colors, not a clothing pattern comparable with checks.

**Audit explanation:** The second soccer players' orange and yellow clothing leaves clothing pattern unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 612. train_6351: `event horse riding is taking place in`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Man wearing a helmet , riding a horse with trees in the background .
>
> **Caption B:** A horse with a rider on top are jumping over a fence in a equestrian event .
>
> **Adopted scope:** riding event
>
> **Extracted A:** unspecified riding
>
> **Extracted B:** equestrian competition
>
> **Recorded reason, verbatim:** Ordinary riding near trees does not establish an equestrian event or competition in the first.

**Audit explanation:** The first horse rider's event or competition remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 613. train_6362: `color of outfit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A line of bicyclists in a race rode past interested spectators a mere few feet away .
>
> **Caption B:** A group of people in colored outfits ride bikes around a track .
>
> **Adopted scope:** outfit colors
>
> **Extracted A:** unstated
>
> **Extracted B:** various colors unspecified
>
> **Recorded reason, verbatim:** The first cyclists have no described outfit color.

**Audit explanation:** The first cyclists' clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 614. train_6375: `strength of grip`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a climber wearing a red headband is pulling himself up some gray rocks high above some green foliage .
>
> **Caption B:** The rock climber is climbing up a steep mountain with very little grip on it .
>
> **Adopted scope:** grip strength
>
> **Extracted A:** pulling up, strength unstated
>
> **Extracted B:** very little grip
>
> **Recorded reason, verbatim:** Pulling oneself up does not quantify grip strength or the available holds relative to very little grip.

**Audit explanation:** The first climber's upward movement leaves grip strength unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 615. train_6412: `object stood upon`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A man is standing in a boat on a river surrounded by trees .
>
> **Caption B:** This shows five men in a motorized boat on the water surrounded by forest .
>
> **Adopted scope:** standing support
>
> **Extracted A:** boat
>
> **Extracted B:** boat, standing unspecified
>
> **Recorded reason, verbatim:** The second boat occupants are not stated to stand, so an object stood upon cannot be extracted.

**Audit explanation:** The second boat occupants' standing role remains unestablished, leaving the requested standing support unavailable.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 616. train_6421: `orientation of heads`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two men wearing wrestling gear with their heads pressed together .
>
> **Caption B:** Two opposing wrestlers competing to pin one another .
>
> **Adopted scope:** head orientation
>
> **Extracted A:** pressed together
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Attempting a wrestling pin does not establish the second wrestlers' head orientation.

**Audit explanation:** The second wrestlers' attempted pin leaves head orientation unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 617. train_6433: `direction of person's face relative to water`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A boy diving backward off a pier in a large lake .
>
> **Caption B:** A person does a flip by two sailboats and a lake .
>
> **Adopted scope:** face-water orientation
>
> **Extracted A:** backward diving
>
> **Extracted B:** flip orientation unspecified
>
> **Recorded reason, verbatim:** A flip does not specify the face's momentary direction relative to water in the second scene.

**Audit explanation:** The second person's flip leaves the face's momentary direction relative to water unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 618. train_6437: `location of race`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Three people race their bicycles in competition in the forest .
>
> **Caption B:** Several cyclists wearing different colors riding bikes on pavement .
>
> **Adopted scope:** location of a race
>
> **Extracted A:** bicycle competition in forest
>
> **Extracted B:** cyclists riding on pavement, race unestablished
>
> **Recorded reason, verbatim:** The second caption establishes cycling but no race, so the requested event's location cannot be extracted.

**Audit explanation:** The second cyclists' pavement location leaves a race event and its location relation unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 619. train_6446: `breed of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The white dog is standing in the water with a stick in its mouth .
>
> **Caption B:** A Dalmatian breed dog paddles through deep water .
>
> **Adopted scope:** dog breed
>
> **Extracted A:** unstated
>
> **Extracted B:** Dalmatian
>
> **Recorded reason, verbatim:** White coat color does not identify the first dog's breed.

**Audit explanation:** The first dog's white coat leaves breed unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 620. train_6471: `position of skateboarder`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person on a skateboard is in the air while performing a skateboarding trick .
>
> **Caption B:** Skateboarder wearing shades in front of a wall that looks like fishscales .
>
> **Adopted scope:** skater ground position
>
> **Extracted A:** airborne
>
> **Extracted B:** unspecified before wall
>
> **Recorded reason, verbatim:** Being in front of a wall does not determine the second skateboarder's elevation or stance.

**Audit explanation:** The second skateboarder's wall-relative location leaves elevation and stance unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 621. train_6505: `type of martial arts`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in blue competes against a man in white during a taekwondo match .
>
> **Caption B:** Two young men are fighting with each other in a martial arts competition .
>
> **Adopted scope:** martial-art type
>
> **Extracted A:** taekwondo
>
> **Extracted B:** unspecified martial art
>
> **Recorded reason, verbatim:** Generic martial arts does not identify the requested martial-art discipline.

**Audit explanation:** The second generic martial-arts competition leaves discipline unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 622. train_6508: `number of animals.`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man standing on a ladder holding a wooden beam .
>
> **Caption B:** A man using a scaffold to work on the roof of a building .
>
> **Adopted scope:** animal count
>
> **Extracted A:** no animal described
>
> **Extracted B:** no animal described
>
> **Recorded reason, verbatim:** Neither caption describes nonhuman animals, so animal count is unavailable rather than zero.

**Audit explanation:** Both work scenes leave nonhuman animal presence and count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `5.0`.

### 623. train_6517: `type of bike`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A shirtless guy on a BMX bike is in the process of jumping a hill on his BMX bike .
>
> **Caption B:** A young man in a plaid shirt is popping a wheelie with his bike .
>
> **Adopted scope:** bike subtype
>
> **Extracted A:** BMX bike
>
> **Extracted B:** bike used for a wheelie, subtype unspecified
>
> **Recorded reason, verbatim:** A wheelie can be performed on many bike types and does not identify a comparable BMX subtype.

**Audit explanation:** The second bike's wheelie leaves bike subtype unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 624. train_6526: `action of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The firefighters outdoors in the bush , and shrubs .
>
> **Caption B:** A fireman pulling out a firehose next to a blue car engulfed in flames .
>
> **Adopted scope:** firefighter action
>
> **Extracted A:** unstated outdoors
>
> **Extracted B:** deploying hose
>
> **Recorded reason, verbatim:** Firefighters located among bushes have no stated current action.

**Audit explanation:** The first firefighters' location among bushes leaves their current action unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 625. train_6535: `breed of dogs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** two bulldogs running togerther in the grass with their tongue 's hanging out .
>
> **Caption B:** Two black dogs are bearing their teeth beside a white couch .
>
> **Adopted scope:** dog breed
>
> **Extracted A:** bulldog
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Black coat color does not identify the second dogs' breed.

**Audit explanation:** The second dogs' black coats leave breed unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 626. train_6565: `object seen`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The baby is mesmerized and intrigued by his image in the water .
>
> **Caption B:** A child with shoulder-length brown hair is playing in water outdoors .
>
> **Adopted scope:** seen object
>
> **Extracted A:** own reflection
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Playing in water does not identify what the second child is looking at.

**Audit explanation:** The second child's water play leaves its visual attention target unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 627. train_6568: `profession of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A skateboard is grinding on a curb with his skateboard .
>
> **Caption B:** The skateboarder is doing a trick off the side of a half pipe
>
> **Adopted scope:** profession
>
> **Extracted A:** skater, profession unknown
>
> **Extracted B:** skater, profession unknown
>
> **Recorded reason, verbatim:** Skateboarding establishes an activity, not a paid profession, in either caption.

**Audit explanation:** Both skateboarding activities leave paid profession unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 628. train_6571: `surfer's position`

**Current status:** `excluded_scope`. **Semantic rating:** `excluded/null`. **Policy:** `S7`.

> **Caption A:** A surfer is riding a vast wave that is every surfer 's dream come true .
>
> **Caption B:** A surfer flips his board so it is perpendicular to the ocean .
>
> **Adopted scope:** surfer position: posture versus location
>
> **Extracted A:** riding a large wave; exact posture unstated
>
> **Extracted B:** flips a perpendicular board; body position unstated
>
> **Recorded reason, verbatim:** The condition can mean body posture or location relative to wave/board. The captions describe activity and board orientation without fixing a common position feature; different plausible readings change validity or grade.

**Audit explanation:** Position has competing readings. Body posture remains unavailable, while relation to the surfing surface supports a partial comparison.

**Recorded scope readings:**

> - **surfer body posture:** invalid.
> - **surfer relation to surfing surface or maneuver:** rating 3.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 629. train_6591: `height of dog`

**Current status:** `excluded_scope`. **Semantic rating:** `excluded/null`. **Policy:** `S7`.

> **Caption A:** White dog with dark markings jumping to catch an object .
>
> **Caption B:** A white dog is running through the water onto the shore .
>
> **Adopted scope:** dog height: stature versus elevation
>
> **Extracted A:** jumping; stature unstated
>
> **Extracted B:** running through water toward shore; stature unstated
>
> **Recorded reason, verbatim:** Height can mean body stature, for which neither caption gives information, or elevation, inferred from jumping versus running. The frozen conventions do not settle this feature ambiguity.

**Audit explanation:** Height has competing readings. Body stature remains unspecified, while elevation contrasts jumping with running.

**Recorded scope readings:**

> - **dog body stature:** invalid.
> - **dog elevation above supporting surface:** rating 1.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 630. train_6595: `presence of white shorts`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man wearing a red shirt and white shorts is playing soccer .
>
> **Caption B:** Guy in red uniform bouncing a soccer ball off his head .
>
> **Adopted scope:** white-shorts presence
>
> **Extracted A:** present
>
> **Extracted B:** unknown red uniform extent
>
> **Recorded reason, verbatim:** A red uniform does not specify whether the second person's shorts are white.

**Audit explanation:** The second red uniform leaves the shorts' white-color status unknown.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 631. train_6601: `number of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A firetruck rushes to the scene of an accident .
>
> **Caption B:** A fireman begins to cross the street towards the fire .
>
> **Adopted scope:** people count
>
> **Extracted A:** unmentioned vehicle occupants
>
> **Extracted B:** one fireman
>
> **Recorded reason, verbatim:** A firetruck alone does not establish its occupants or a person count.

**Audit explanation:** The first firetruck leaves human occupants and their count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 632. train_6616: `presence of wetsuit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person dressed in a long-sleeve gray and black wetsuit keeps balance while surfing .
>
> **Caption B:** Swimmers by a nearby wave along with one surfer on the wave .
>
> **Adopted scope:** wetsuit presence
>
> **Extracted A:** present
>
> **Extracted B:** unknown
>
> **Recorded reason, verbatim:** A surfer does not necessarily wear a wetsuit, so the second wetsuit presence is unknown.

**Audit explanation:** The second surfer's wetsuit status remains unknown.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 633. train_6622: `color of accessories worn`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man with scarf on his head and white shirt cooking at an outside event .
>
> **Caption B:** Two men and a woman in white aprons prepare a plate of food in a kitchen .
>
> **Adopted scope:** accessory colors
>
> **Extracted A:** scarf color unstated
>
> **Extracted B:** white aprons
>
> **Recorded reason, verbatim:** The white shirt does not establish the first scarf's color.

**Audit explanation:** The first scarf's accessory color remains unspecified. White describes the shirt.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 634. train_6640: `items being sold`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Street vendors sell various wards , including pineapples and soccer balls .
>
> **Caption B:** Items are being sold in the open market by it 's vendors .
>
> **Adopted scope:** sold items
>
> **Extracted A:** pineapples and soccer balls
>
> **Extracted B:** goods unspecified
>
> **Recorded reason, verbatim:** Generic goods do not identify the items being sold in the second.

**Audit explanation:** The second vendors' unnamed goods leave sold-item identities unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 635. train_6642: `intention of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in an orange hooded sweatshirt climbing a wall of ice with a forest in the background .
>
> **Caption B:** A silhouetted figure stands at the top of a snow-covered peak at the end of some tracks .
>
> **Adopted scope:** person intention
>
> **Extracted A:** climb ice wall
>
> **Extracted B:** unstated atop peak
>
> **Recorded reason, verbatim:** Standing at a peak does not establish the second person's current intention.

**Audit explanation:** The second person's intention remains unspecified atop the snowy peak.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 636. train_6645: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A girl basketball player in a white jersey is in the process of making a move with the ball around an opposing player in a blue jersey .
>
> **Caption B:** A basketball player dribbles with authority and skill up the court as a defender gets ready to stop his attempt at scoring .
>
> **Adopted scope:** clothing colors
>
> **Extracted A:** white and blue
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second basketball players have no stated clothing colors.

**Audit explanation:** The second basketball players' clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 637. train_6671: `color of clothes`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young child with snow on his face gets out of a blue sled .
>
> **Caption B:** A snowboarder wearing a red coat is going down a snow-covered slope .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** unstated
>
> **Extracted B:** red
>
> **Recorded reason, verbatim:** Blue describes the sled, not the first child's clothes.

**Audit explanation:** The first child's clothing colors remain unspecified. Blue describes the sled.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 638. train_6675: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Dog jumping to catch falling snow out in the woods .
>
> **Caption B:** A medium sized brown dog is running through an open white wooded area .
>
> **Adopted scope:** animal color
>
> **Extracted A:** unstated
>
> **Extracted B:** brown
>
> **Recorded reason, verbatim:** The first dog has no specified coat color.

**Audit explanation:** The first dog's coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 639. train_6709: `color of clothes`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man holding a suitcase walks alone towards an escalator in a dimly-lit area .
>
> **Caption B:** A man in a gray suit standing in front of a red and white moving train .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** unstated
>
> **Extracted B:** grey
>
> **Recorded reason, verbatim:** The first man's clothing color is unstated.

**Audit explanation:** The first man's clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 640. train_6725: `location of event`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A group of students listens avidly during a classroom lecture or demonstration .
>
> **Caption B:** A group of people sit in chairs while listening to a speaker .
>
> **Adopted scope:** event location
>
> **Extracted A:** classroom
>
> **Extracted B:** seated gathering, venue unspecified
>
> **Recorded reason, verbatim:** An audience seated before a speaker does not establish a classroom or any particular venue type.

**Audit explanation:** The second audience and speaker leave event venue type unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 641. train_6739: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Surfer performing one of his moves on a nice sunny day with a scene in the background .
>
> **Caption B:** A surfer wearing a black and red wetsuit on a white surfboard , slices through the waves on a bright blue ocean .
>
> **Adopted scope:** surfboard color
>
> **Extracted A:** unstated
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** The first surfer's board has no stated color.

**Audit explanation:** The first surfboard's color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 642. train_6745: `height of dog`

**Current status:** `excluded_scope`. **Semantic rating:** `excluded/null`. **Policy:** `S7`.

> **Caption A:** The black dogs try to wrestle the dog away from each other .
>
> **Caption B:** The black dog is jumping over a fence with a bird in its mouth .
>
> **Adopted scope:** dog height: stature versus elevation
>
> **Extracted A:** wrestling, stature unstated
>
> **Extracted B:** jumping over fence, stature unstated
>
> **Recorded reason, verbatim:** This duplicates the ambiguity approved for train_6591. Stature is wholly missing; an elevation reading infers different ground-relative positions. The condition does not specify which feature.

**Audit explanation:** Height has competing readings. Body stature remains unspecified, while elevation contrasts ordinary wrestling with a fence jump.

**Recorded scope readings:**

> - **dog body stature:** invalid.
> - **dog elevation above supporting ground:** rating 1.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 643. train_6757: `emotion of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A girl wearing a lime green shirt , jeans and bowling shoes is trying to knock down the last three pins .
>
> **Caption B:** A girl dressed all in pink is jumping up in the air with her arms spread wide at a bowling alley .
>
> **Adopted scope:** person emotion
>
> **Extracted A:** unstated focused activity
>
> **Extracted B:** possible excitement
>
> **Recorded reason, verbatim:** Trying to hit bowling pins does not establish the first girl's emotional state.

**Audit explanation:** The first girl's bowling attempt leaves her emotional state unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 644. train_6765: `levelness of surface man is on`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man is standing on a rock in front of a mountainous area .
>
> **Caption B:** A man at the top of a mountain in a large mountain range .
>
> **Adopted scope:** support levelness
>
> **Extracted A:** rock slope unstated
>
> **Extracted B:** summit slope unstated
>
> **Recorded reason, verbatim:** A rock or mountain summit does not determine the angle of the local supporting surface.

**Audit explanation:** Both rocks and mountain summits leave the local supporting surface's angle unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 645. train_6810: `number of observers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A bicycle rider takes a daring jump as his friends watch .
>
> **Caption B:** A man is doing tricks on a bike and is very high in the air .
>
> **Adopted scope:** observer count
>
> **Extracted A:** plural friends
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second cyclist has no described observers to count.

**Audit explanation:** The second cyclist's observer presence and count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 646. train_6812: `type of stunt location`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a lone bicyclist jumping a trick along a bike jumping path .
>
> **Caption B:** A mountain biker is in the midair in the middle of a stunt .
>
> **Adopted scope:** stunt setting
>
> **Extracted A:** bike jumping path
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** A mountain-biker label specifies the rider or bike, not the actual stunt venue.

**Audit explanation:** The second mountain-biker description leaves the actual stunt venue unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 647. train_6813: `type of bicycle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a lone bicyclist jumping a trick along a bike jumping path .
>
> **Caption B:** A mountain biker is in the midair in the middle of a stunt .
>
> **Adopted scope:** bicycle subtype
>
> **Extracted A:** bicycle on a jumping path, subtype unspecified
>
> **Extracted B:** mountain bike
>
> **Recorded reason, verbatim:** Jumping on a path does not identify a bicycle subtype comparable with mountain bike.

**Audit explanation:** The first cyclist's jumping path leaves bicycle subtype unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 648. train_6837: `rider's purpose`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person is riding a white horse while jumping obstacles .
>
> **Caption B:** A woman in a purple riding uniform rides a horse through a field .
>
> **Adopted scope:** rider purpose
>
> **Extracted A:** obstacle jumping
>
> **Extracted B:** field riding, specific aim unspecified
>
> **Recorded reason, verbatim:** Riding through a field does not establish the rider's purpose or goal.

**Audit explanation:** The second woman's field riding leaves her purpose or goal unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 649. train_6865: `location relative to structure`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Two brown and white dogs in the grass near a stone structure .
>
> **Caption B:** A large and small dog interact in a grassy field .
>
> **Adopted scope:** structure-relative location
>
> **Extracted A:** near stone structure
>
> **Extracted B:** no structure described
>
> **Recorded reason, verbatim:** No reference structure is described in the second field scene.

**Audit explanation:** The second grassy field leaves a reference structure unestablished for the required relative location.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 650. train_6881: `surface traversed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Guy with black shirt and blue jeans performing tricks in a skateboard
>
> **Caption B:** A skateboard is grinding on a curb with his skateboard .
>
> **Adopted scope:** traversed surface
>
> **Extracted A:** unstated
>
> **Extracted B:** curb
>
> **Recorded reason, verbatim:** Unspecified skateboard tricks do not identify the first traversed or supporting surface.

**Audit explanation:** The first unspecified skateboard tricks leave the traversed surface unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 651. train_6927: `Position of person relative to pool`

**Current status:** `excluded_scope`. **Semantic rating:** `excluded/null`. **Policy:** `S7`.

> **Caption A:** A girl in a swimming pool looks on while a boy in a mask jumps in from a diving board .
>
> **Caption B:** A young child is wearing blue goggles and sitting in a float in a pool .
>
> **Adopted scope:** people-pool position
>
> **Extracted A:** one in pool, one jumping in
>
> **Extracted B:** on float in pool
>
> **Recorded reason, verbatim:** The first caption explicitly describes two people with different pool positions: the girl is already inside and the boy is jumping in. The unqualified singular person does not settle which position to compare with the floating child. This is the same material multiple-person referent problem preserved by the user-confirmed validation age-scope exclusion.

**Audit explanation:** The first girl's in-pool position and boy's entry compete as referents. Selecting either or both changes the comparison with the floating child.

**Recorded scope readings:**

> - **principal girl already in pool:** rating 5. A: in pool. B: in pool on float.
> - **boy entering from diving board:** rating 1. A: jumping from board into pool. B: sitting inside pool on float.
> - **all first-caption people:** rating 3. A: one in pool and one jumping in. B: one floating in pool.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 652. train_6945: `distance covered`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog wearing an orange vest scampers playfully across the grass .
>
> **Caption B:** A tan dog runs down a wooden staircase to the green grass .
>
> **Adopted scope:** distance traveled
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Scampering and descending stairs do not specify comparable travel distances.

**Audit explanation:** Both scampering across grass and descending stairs leave comparable travel distances unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 653. train_6955: `man's occupation`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a collared shirt is working next to a small lamp .
>
> **Caption B:** A man sitting at his work station making jewelery .
>
> **Adopted scope:** occupation
>
> **Extracted A:** unspecified worker
>
> **Extracted B:** jeweler inferred
>
> **Recorded reason, verbatim:** Working by a lamp does not establish an occupation comparable with jewelry making.

**Audit explanation:** The first man's work beside a lamp leaves occupation unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 654. train_6963: `time limit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Man on horse wearing white hat attempting to lasso small animal .
>
> **Caption B:** A cowboy riding a horse at a rodeo with 8 seconds on the clock .
>
> **Adopted scope:** time limit
>
> **Extracted A:** unstated
>
> **Extracted B:** eight seconds on clock
>
> **Recorded reason, verbatim:** The first gives no time limit, and a clock reading alone does not necessarily state a limit second.

**Audit explanation:** The first rodeo scene leaves a time limit unspecified. The second clock reading also leaves a limit unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 655. train_6994: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Boy in red and blue flowered trunks jumps into pool holding green ball .
>
> **Caption B:** Boy , of age approximately 10 years old , lunging into pristine pool on hot summer day .
>
> **Adopted scope:** held-object color
>
> **Extracted A:** green ball
>
> **Extracted B:** object unmentioned
>
> **Recorded reason, verbatim:** The second boy carries no described object whose color could match the green ball.

**Audit explanation:** The second caption leaves any held object and its color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 656. train_7012: `color of shirt`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man sleeping on the ground against a door with plastic bags by his foot .
>
> **Caption B:** A man wearing a maroon shirt tied around his face is laying on the cement
>
> **Adopted scope:** shirt color
>
> **Extracted A:** unstated
>
> **Extracted B:** maroon
>
> **Recorded reason, verbatim:** The first man's shirt color is unstated.

**Audit explanation:** The first man's shirt color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 657. train_7015: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A snowboarder at the top of a slope reaches down to grab his board while in midair .
>
> **Caption B:** A man in a red jacket and sunglasses is snowboarding down a snowy mountain .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** unstated
>
> **Extracted B:** red
>
> **Recorded reason, verbatim:** The first snowboarder has no stated clothing color.

**Audit explanation:** The first snowboarder's clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 658. train_7027: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A snowboarder in an orange coat is in the middle of a jump .
>
> **Caption B:** A snowboarder grabbing the snowboard while in the air on a snowy mountain .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** orange
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second snowboarder's clothing color is absent.

**Audit explanation:** The second snowboarder's clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 659. train_7033: `color of dress`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The woman is holding a baby girl wearing a striped dress .
>
> **Caption B:** Child in a pink dress with white flowers enjoying her birthday .
>
> **Adopted scope:** dress color
>
> **Extracted A:** unstated striped dress
>
> **Extracted B:** pink/white
>
> **Recorded reason, verbatim:** Striped describes pattern without identifying the first dress's colors.

**Audit explanation:** The first dress's stripes identify pattern, leaving colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 660. train_7045: `number of girls`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A woman looking in a telescope to look at something really small , most likely some sort of science lab .
>
> **Caption B:** Two girls , one blond and one african american , watching a brunette-haired girl use a microscope to look at something .
>
> **Adopted scope:** girls count
>
> **Extracted A:** adult woman, child count unavailable
>
> **Extracted B:** three girls
>
> **Recorded reason, verbatim:** The first describes an adult woman, not any child girl whose count can be compared with the three girls.

**Audit explanation:** The first caption describes an adult woman. The required child girls remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 661. train_7050: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person on a green board is snowboarding in midair .
>
> **Caption B:** A person riding a snowboard goes over a snowy ramp .
>
> **Adopted scope:** board color
>
> **Extracted A:** green
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second snowboard's color is not stated.

**Audit explanation:** The second snowboard's color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 662. train_7052: `place of activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two dogs , one large and one small , are playing together in the grass .
>
> **Caption B:** A small dog lands on a big dog trying to get a disc .
>
> **Adopted scope:** activity place
>
> **Extracted A:** grass
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Landing on another dog identifies a target but not the second scene's physical setting.

**Audit explanation:** The second dog's landing target leaves the physical activity setting unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 663. train_7084: `color of playing ball`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The small dog is playing with a large ball on the grass .
>
> **Caption B:** Two small white dogs are in a yard chasing a red ball .
>
> **Adopted scope:** ball color
>
> **Extracted A:** unstated
>
> **Extracted B:** red
>
> **Recorded reason, verbatim:** The first ball's size is supplied, but its color is not.

**Audit explanation:** The first ball's size leaves its color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 664. train_7099: `color of dogs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog runs with another dog in the background holding a ball in its mouth .
>
> **Caption B:** Two small white dogs are in a yard chasing a red ball .
>
> **Adopted scope:** dog colors
>
> **Extracted A:** unstated
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** The first dogs have no stated coat colors.

**Audit explanation:** The first dogs' coat colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 665. train_7117: `type of accessory`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A climber with a backpack accends a snow covered mountain .
>
> **Caption B:** A woman in a striped shirt climbs up a mountain .
>
> **Adopted scope:** accessory
>
> **Extracted A:** backpack
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second woman's striped shirt does not establish a climbing accessory.

**Audit explanation:** The second climber's shirt leaves an accessory unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 666. train_7129: `view from bridge`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man and woman stop to take in the view from a bridge .
>
> **Caption B:** A couple gazing out into the ocean from a bridge .
>
> **Adopted scope:** bridge view
>
> **Extracted A:** unspecified scenery
>
> **Extracted B:** ocean
>
> **Recorded reason, verbatim:** The first bridge view does not identify what scenery is visible.

**Audit explanation:** The first bridge view leaves visible scenery unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 667. train_7152: `dogs playing together`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two dogs play with a red plastic toy in the tall grass .
>
> **Caption B:** A brown dog and a black dog are together in tall grass .
>
> **Adopted scope:** dogs playing together
>
> **Extracted A:** dogs explicitly playing with toy
>
> **Extracted B:** dogs together, activity unspecified
>
> **Recorded reason, verbatim:** Togetherness supplies spatial relation but does not establish the required playing action in the second caption.

**Audit explanation:** The second dogs' togetherness establishes proximity. Joint playing remains unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 668. train_7160: `animal being ridden`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** An older man watching as a younger man fiddles with something on his horse .
>
> **Caption B:** A bucking bronco causes a rodeo rider to lose his grip .
>
> **Adopted scope:** animal currently being ridden
>
> **Extracted A:** horse being adjusted or handled, mounted riding unestablished
>
> **Extracted B:** bucking horse ridden by rodeo rider
>
> **Recorded reason, verbatim:** Fiddling with something on a horse does not establish that the first man is riding it.

**Audit explanation:** The first man's horse handling leaves mounted riding unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 669. train_7179: `presence or absence of snow`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person walks up a white sandy hill against the blue sky .
>
> **Caption B:** A lone skier is making their way up a mountain .
>
> **Adopted scope:** snow presence
>
> **Extracted A:** sand, snow not stated
>
> **Extracted B:** snow inferred skiing
>
> **Recorded reason, verbatim:** A sandy hill does not explicitly establish the absence of snow across the scene.

**Audit explanation:** The first sandy hill leaves snow presence unknown across the scene.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 670. train_7209: `action`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A child is on the beach next to a red canvas folding chair .
>
> **Caption B:** An excited boy playing in the surf with a body board .
>
> **Adopted scope:** person action
>
> **Extracted A:** unstated presence
>
> **Extracted B:** bodyboard play
>
> **Recorded reason, verbatim:** Being beside a beach chair does not identify the first child's action.

**Audit explanation:** The first child's beach-chair location leaves its action unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 671. train_7233: `type of bike`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The young man is performing a summersault in the air with a bicycle .
>
> **Caption B:** on a gorges sunny day , young man doing a trick on a BMX bike .
>
> **Adopted scope:** bike subtype
>
> **Extracted A:** bicycle used for somersault, subtype unspecified
>
> **Extracted B:** BMX bike
>
> **Recorded reason, verbatim:** An aerial somersault does not uniquely establish the first bicycle's subtype.

**Audit explanation:** The first cyclist's somersault leaves bicycle subtype unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 672. train_7257: `color of outfit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A girl in a pink suit chases a gull on a beach .
>
> **Caption B:** A girl in a swimsuit is jumping high , near water .
>
> **Adopted scope:** outfit color
>
> **Extracted A:** pink
>
> **Extracted B:** unstated swimsuit color
>
> **Recorded reason, verbatim:** The second swimsuit's color is not supplied.

**Audit explanation:** The second swimsuit's color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 673. train_7267: `color of dogs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two small dogs pursuing a ball across a grassy field .
>
> **Caption B:** A white dog carries a yellow toy while another dog follows .
>
> **Adopted scope:** dog colors
>
> **Extracted A:** unstated
>
> **Extracted B:** white dog and unspecified follower
>
> **Recorded reason, verbatim:** Neither dog in the first caption is assigned a color.

**Audit explanation:** Both first-caption dogs' coat colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 674. train_7285: `dog's behavior at beach`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A light brown dog is splashing in the water with its paw .
>
> **Caption B:** A brown dog making a funny face while standing on a beach .
>
> **Adopted scope:** dog behavior specifically at a beach
>
> **Extracted A:** splashing in water, beach unestablished
>
> **Extracted B:** standing on a beach making a face
>
> **Recorded reason, verbatim:** Water alone does not establish the first scene's required beach setting.

**Audit explanation:** The first dog's water activity leaves the required beach setting unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 675. train_7305: `people's ages`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A group of people are paddling their way across the water .
>
> **Caption B:** Children in life jackets while paddling a boat .
>
> **Adopted scope:** people age
>
> **Extracted A:** unstated group ages
>
> **Extracted B:** children
>
> **Recorded reason, verbatim:** The first group's ages are wholly unstated.

**Audit explanation:** The first paddlers' ages remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 676. train_7315: `relation of observers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A baseball catcher stands ready to catch a throw , while his team looks on .
>
> **Caption B:** A crowd watches a baseball game as a man makes it to the base while another man tries to get the ball .
>
> **Adopted scope:** observers' relation to player
>
> **Extracted A:** teammates
>
> **Extracted B:** crowd with unspecified relationship
>
> **Recorded reason, verbatim:** A general crowd does not establish the spectators' personal or team relation to the player.

**Audit explanation:** The second crowd's personal or team relationship with the player remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 677. train_7317: `type of bicycle race`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Olympic bicyclists round a corner during competition .
>
> **Caption B:** A man comes around the corner in a bicycle race .
>
> **Adopted scope:** bicycle race subtype or competition level
>
> **Extracted A:** Olympic bicycle race
>
> **Extracted B:** bicycle race, subtype unspecified
>
> **Recorded reason, verbatim:** The second repeats bicycle race without identifying its subtype or competitive level.

**Audit explanation:** The second bicycle race's subtype and competition level remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 678. train_7335: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A supermarket isle with a woman holding a list and a man looking off to the right .
>
> **Caption B:** A woman in a green striped shirt is standing in front of a produce section in a store .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** unstated
>
> **Extracted B:** green-striped shirt
>
> **Recorded reason, verbatim:** The first shoppers' clothing colors are absent.

**Audit explanation:** The first shoppers' clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 679. train_7340: `nationality of persons`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Asian people walking down the street of a market with their purchases .
>
> **Caption B:** People are walking on a paved slope surrounded by Chinese vendors .
>
> **Adopted scope:** nationality of described persons
>
> **Extracted A:** Asian regional descriptor, no nationality
>
> **Extracted B:** Chinese vendors; focal walkers nationality unstated
>
> **Recorded reason, verbatim:** Regional/ethnic description Asian does not establish nationality. The second gives vendor identity while leaving the walkers unspecified. The requested nationality is unavailable rather than partially measured as the same feature.

**Audit explanation:** The first Asian descriptor supplies regional or ethnic information. Nationality remains unspecified there and for the second walkers.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 680. train_7367: `color of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A wet German Shepherd runs along the waves on a beach .
>
> **Caption B:** A big brown dog is jumping in the water and has his mouth wide open .
>
> **Adopted scope:** animal colors
>
> **Extracted A:** unstated
>
> **Extracted B:** brown
>
> **Recorded reason, verbatim:** German Shepherd breed alone does not identify this individual dog's coat colors.

**Audit explanation:** The first German Shepherd's individual coat colors remain unspecified by breed alone.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 681. train_7377: `rider's sentiment`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** This dirt biker is enjoying the race at the racetrack in Atlanta .
>
> **Caption B:** A man on a bike throws up dirt during a motor cross event .
>
> **Adopted scope:** rider sentiment
>
> **Extracted A:** enjoyment
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Riding while throwing up dirt does not establish the second rider's sentiment.

**Audit explanation:** The second rider's motocross activity leaves emotional sentiment unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 682. train_7385: `color of shirt`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a black jacket plays a black electric guitar and sings .
>
> **Caption B:** Man with sweaty hair wearing white shirt with skull on it playing guitar .
>
> **Adopted scope:** shirt color
>
> **Extracted A:** unstated; only jacket black
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** A black jacket does not establish the color of a shirt beneath it.

**Audit explanation:** The first black jacket leaves the shirt's color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 683. train_7391: `physical action`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** little kid in red snowsuit with hello kitty mittens
>
> **Caption B:** a child in a red coat is holding an armful of snow in front of a house .
>
> **Adopted scope:** child physical action
>
> **Extracted A:** unstated
>
> **Extracted B:** holding snow
>
> **Recorded reason, verbatim:** The first child is described only by clothing, without an action.

**Audit explanation:** The first child's clothing leaves physical action unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 684. train_7393: `color of lights`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a blue shirt is singing and playing guitar on a stage in front of a drummer .
>
> **Caption B:** A band , including a keyboard player , guitarist , and drummer , perform on a stage illuminated by pink lights .
>
> **Adopted scope:** light color
>
> **Extracted A:** unstated
>
> **Extracted B:** pink
>
> **Recorded reason, verbatim:** The first stage has no stated lighting color.

**Audit explanation:** The first stage's lighting colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 685. train_7403: `scenery type`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man riding a horse and leading other horses through beautiful scenery .
>
> **Caption B:** A line of horses is walking down a road past a broken-down car .
>
> **Adopted scope:** scenery type
>
> **Extracted A:** beautiful, type unstated
>
> **Extracted B:** road with broken-down car
>
> **Recorded reason, verbatim:** Beautiful is an evaluation, not an identifiable scenery type.

**Audit explanation:** The first scenery's beauty describes evaluation, leaving scenery type unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 686. train_7407: `family in kitchen`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A boy in a flowered apron standing at a stove while a woman stirs a pot in the background .
>
> **Caption B:** A young man and mother in the kitchen washing and drying the dishes .
>
> **Adopted scope:** family relationship in kitchen
>
> **Extracted A:** boy and woman, relationship unstated
>
> **Extracted B:** young man and mother
>
> **Recorded reason, verbatim:** A domestic boy/woman pair does not establish family relationship. Kitchen context is recoverable, but the requested family role is wholly unprovided in the first caption.

**Audit explanation:** The first boy and woman have an unestablished family relationship despite their kitchen setting.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 687. train_7433: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A baseball player in gray is getting ready to catch the ball .
>
> **Caption B:** A baseball player is swinging at a baseball thrown by a pitcher .
>
> **Adopted scope:** principal sporting object's color
>
> **Extracted A:** ball color unstated
>
> **Extracted B:** ball color unstated
>
> **Recorded reason, verbatim:** Gray describes a player's uniform, and neither baseball is given a color.

**Audit explanation:** Both baseballs' colors remain unspecified. Gray describes a player's uniform.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 688. train_7439: `type of winter clothing worn`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a red winter hat is wearing snowshoes while looking at a green pine tree .
>
> **Caption B:** A person is bundled up in cold weather gear near a snow-covered mountain .
>
> **Adopted scope:** winter clothing type
>
> **Extracted A:** winter hat and snowshoes
>
> **Extracted B:** unspecified cold-weather gear
>
> **Recorded reason, verbatim:** Generic cold-weather gear does not identify the requested winter garment types.

**Audit explanation:** The second generic cold-weather gear leaves winter garment types unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 689. train_7453: `color of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Three dogs greeting each other in a field of green grass .
>
> **Caption B:** A large , brown , fluffy dog with a small white and brown dog on a dirt surface .
>
> **Adopted scope:** place color
>
> **Extracted A:** green grass
>
> **Extracted B:** dirt with color unstated
>
> **Recorded reason, verbatim:** Dirt can have multiple colors, so its material alone does not establish a hue comparable with explicit green grass.

**Audit explanation:** The second dirt surface's hue remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 690. train_7469: `shirt's color`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The man on the bicycle is doing a stunt through the air .
>
> **Caption B:** A man wearing a yellow shirt is doing a trick high in the air with his bike .
>
> **Adopted scope:** shirt color
>
> **Extracted A:** unstated
>
> **Extracted B:** yellow
>
> **Recorded reason, verbatim:** The first rider's shirt color is not given.

**Audit explanation:** The first cyclist's shirt color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 691. train_7487: `position of man relative to ground`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a red jacket looking out over snow-covered mountains .
>
> **Caption B:** A snowboarder performs a flip with a snow-covered mountain vista in the background .
>
> **Adopted scope:** man's elevation relative to ground
>
> **Extracted A:** unstated while looking out
>
> **Extracted B:** airborne flip
>
> **Recorded reason, verbatim:** Looking at mountain scenery does not establish the first man's ground contact or elevation.

**Audit explanation:** The first man's mountain viewing leaves ground contact and elevation unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 692. train_7537: `shape of mouth`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young girl with a sippy cup swings on a swing in a park .
>
> **Caption B:** A child is making a ridiculous face with an open mouth on the swings .
>
> **Adopted scope:** mouth shape
>
> **Extracted A:** unstated
>
> **Extracted B:** open mouth
>
> **Recorded reason, verbatim:** Holding a sippy cup does not establish the first child's mouth shape.

**Audit explanation:** The first girl's sippy cup leaves mouth shape unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 693. train_7553: `wrestling moves performed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two men are wrestling , one has the other pinned to the floor and the man on the floor is wincing in pain .
>
> **Caption B:** Two men are wrestling without any shirts on while a judge or ref of some sort starts to interfere .
>
> **Adopted scope:** wrestling move
>
> **Extracted A:** pin
>
> **Extracted B:** unspecified wrestling
>
> **Recorded reason, verbatim:** General wrestling and referee interference do not identify the second wrestling move.

**Audit explanation:** The second wrestling scene leaves a specific move unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 694. train_7589: `race of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a climber is scaling a reddish colored rock face .
>
> **Caption B:** A young white man is climbing a mountain with a rope as a guide .
>
> **Adopted scope:** person race
>
> **Extracted A:** unstated
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** The first climber's race is unstated.

**Audit explanation:** The first climber's race remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 695. train_7609: `person's age`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The skateboarder is doing a trick off the side of a half pipe
>
> **Caption B:** A young man goes air-born while his skateboard spins underneath him .
>
> **Adopted scope:** person age
>
> **Extracted A:** unstated
>
> **Extracted B:** young man
>
> **Recorded reason, verbatim:** Skateboarder alone does not establish the first person's age.

**Audit explanation:** The first skateboarder's age remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 696. train_7612: `formality of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Little girls who are dressed up play in the falling autumn leaves .
>
> **Caption B:** Two little girls wearing bright dresses are blowing bubbles with bubble wands .
>
> **Adopted scope:** clothing formality
>
> **Extracted A:** dressed up
>
> **Extracted B:** bright dresses, formality unspecified
>
> **Recorded reason, verbatim:** Bright dresses do not establish clothing formality, analogous to the confirmed decor-style boundary.

**Audit explanation:** The second bright dresses leave clothing formality unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 697. train_7619: `presence of horse`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in an orange wrap clothing is being driven by a man on a motorbike .
>
> **Caption B:** A man on a motorbike is leading the horse with another man on its back .
>
> **Adopted scope:** horse presence
>
> **Extracted A:** unestablished
>
> **Extracted B:** horse present
>
> **Recorded reason, verbatim:** No horse is mentioned first, but that does not establish absence.

**Audit explanation:** Horse presence remains unknown in the first motorcycle scene.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 698. train_7622: `type of bike`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man wearing dark sunglasses is jumping his bike over a road , in a forest .
>
> **Caption B:** A guy standing on a moving dirt bike while wearing blue , black and yellow .
>
> **Adopted scope:** bike subtype
>
> **Extracted A:** bike jumping over a road, subtype unspecified
>
> **Extracted B:** dirt bike
>
> **Recorded reason, verbatim:** Jumping a bike in a forest does not identify the first bike's subtype.

**Audit explanation:** The first forest bicycle jump leaves bike subtype unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 699. train_7633: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person in a black coat playing Frisbee with a dog near a wooded area .
>
> **Caption B:** A large black and white dog jumps up to get something held by a woman wearing a black jacket .
>
> **Adopted scope:** animal color
>
> **Extracted A:** unstated
>
> **Extracted B:** black and white
>
> **Recorded reason, verbatim:** Black describes the first person's coat, not the dog's color.

**Audit explanation:** The first dog's coat color remains unspecified. Black describes the person's coat.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 700. train_7642: `types of wares`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** People are trying to sell various items in a small village .
>
> **Caption B:** Street vendor selling some type of beverage in a different country .
>
> **Adopted scope:** wares type
>
> **Extracted A:** various unspecified items
>
> **Extracted B:** beverage
>
> **Recorded reason, verbatim:** Various unnamed items supplies no merchandise category comparable with a beverage.

**Audit explanation:** The first unnamed items leave merchandise category unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 701. train_7651: `expertise of rider`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The trick bicyclist gets airborne off the ramp .
>
> **Caption B:** A boy on his bike leaping over a hill with trees in the background .
>
> **Adopted scope:** rider expertise
>
> **Extracted A:** unstated stunt proficiency level
>
> **Extracted B:** unstated stunt proficiency level
>
> **Recorded reason, verbatim:** Completing a jump does not identify either rider's overall expertise level.

**Audit explanation:** Both riders' jumps leave overall expertise level unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 702. train_7655: `size of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog shaking off water after playing in the water with a Frisbee .
>
> **Caption B:** Small dog catching a ball in its mouth on a beach .
>
> **Adopted scope:** animal size
>
> **Extracted A:** unstated
>
> **Extracted B:** small
>
> **Recorded reason, verbatim:** Shaking water off does not establish the first dog's size.

**Audit explanation:** The first dog's shaking activity leaves body size unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 703. train_7669: `location of counter`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman in a white shirt stands behind a counter , in the kitchen of an empty restaurant with brick walls .
>
> **Caption B:** A woman with brown hair is standing behind a counter holding plastic wrap .
>
> **Adopted scope:** counter location
>
> **Extracted A:** restaurant kitchen
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Plastic wrap does not establish whether the second counter is in a restaurant kitchen or another location.

**Audit explanation:** The second counter's room or venue remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 704. train_7670: `What is shoveled`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A child wearing a brown coat and red cap is standing on a dirty pile of snow on a city sidewalk .
>
> **Caption B:** scene of a person shoveling snow citizens walking around in a cold winter environment
>
> **Adopted scope:** material being shoveled
>
> **Extracted A:** no shoveling established
>
> **Extracted B:** snow
>
> **Recorded reason, verbatim:** Standing on a snow pile does not establish that anything is being shoveled in the first scene.

**Audit explanation:** The first child's standing on snow leaves shoveling and the material being shoveled unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 705. train_7677: `type of play`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog with a red object in its mouth is hurrying down a smooth path near grass and another dog .
>
> **Caption B:** Two smaller dogs and one larger dog with a puffy white tail are playing in a field .
>
> **Adopted scope:** dog play type
>
> **Extracted A:** running with object
>
> **Extracted B:** playing, action unspecified
>
> **Recorded reason, verbatim:** The second dogs' generic play does not identify a type of play.

**Audit explanation:** The second dogs' generic play leaves play type unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 706. train_7684: `location of interaction`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** There are two people talking in a market filled with many fruits and foods .
>
> **Caption B:** A man with glasses is walking in a crowded market with fruit being sold in stands .
>
> **Adopted scope:** location of a described interaction
>
> **Extracted A:** two people talking in a food market
>
> **Extracted B:** man walking in market, interaction unestablished
>
> **Recorded reason, verbatim:** The second supplies a location but no interpersonal interaction to which the requested location can be assigned.

**Audit explanation:** The second man's market walk leaves an interpersonal interaction and its location relation unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 707. train_7687: `type of shop`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** An old man is selling his wares on a street floor .
>
> **Caption B:** The man in the white hat has various items on the sidewalk .
>
> **Adopted scope:** shop or vending type
>
> **Extracted A:** street-floor vendor selling wares
>
> **Extracted B:** man beside items on sidewalk, selling role unspecified
>
> **Recorded reason, verbatim:** A sidewalk collection of items does not by itself establish a shop or sale activity.

**Audit explanation:** The second sidewalk items leave a shop or vending activity unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 708. train_7723: `position on field`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A college football and cal is kicking a field goal .
>
> **Caption B:** Football players charge toward each other on the green field .
>
> **Adopted scope:** position on field
>
> **Extracted A:** field-goal attempt, exact position unspecified
>
> **Extracted B:** charging on field, position unspecified
>
> **Recorded reason, verbatim:** A field-goal attempt and charging do not supply comparable named or relative field locations.

**Audit explanation:** Both football actions leave comparable field positions unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 709. train_7733: `dog's attention`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog runs holding a yellow dog toy in fall , bench in the background .
>
> **Caption B:** The brown , white and black dog runs on a gravel surface .
>
> **Adopted scope:** dog attention target
>
> **Extracted A:** carried toy
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Running on gravel does not identify the second dog's attention target.

**Audit explanation:** The second dog's gravel running leaves its attention target unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 710. train_7743: `object being jumped over`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A boy is outside jumping over a flower bush on a skateboard .
>
> **Caption B:** Skateboarder in jeans and t-shirt performing jump .
>
> **Adopted scope:** obstacle jumped over
>
> **Extracted A:** flower bush
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second jump has no specified obstacle comparable with a flower bush.

**Audit explanation:** The second skateboard jump leaves an obstacle unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 711. train_7765: `weather conditions`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two climbers are wearing backpacks ascending a very snowy mountain .
>
> **Caption B:** Two people are hiking on a rocky trail through the mountains .
>
> **Adopted scope:** weather conditions
>
> **Extracted A:** snowy
>
> **Extracted B:** unstated on rocky trail
>
> **Recorded reason, verbatim:** A rocky mountain trail gives no weather condition to compare with explicit snowy surroundings.

**Audit explanation:** The second rocky mountain trail leaves weather and temperature unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 712. train_7776: `color of vehicles`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Many people , all wearing helmets , are racing around a corner in a professional motorcycle race .
>
> **Caption B:** Two people in helmets on motorcycles racing , one purple ( in front ) and the other green , leaning into a turn .
>
> **Adopted scope:** vehicle colors
>
> **Extracted A:** unstated
>
> **Extracted B:** purple and green
>
> **Recorded reason, verbatim:** The first motorcycles have no stated colors.

**Audit explanation:** The first motorcycles' colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 713. train_7799: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in black and white swimming trunks dives into some murky water .
>
> **Caption B:** The person wearing shorts and a shirt is jumping off a dock , into the water .
>
> **Adopted scope:** principal clothing color
>
> **Extracted A:** black and white trunks
>
> **Extracted B:** shorts and shirt with colors unstated
>
> **Recorded reason, verbatim:** The second person's shorts and shirt have no stated colors.

**Audit explanation:** The second person's shorts and shirt colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 714. train_7804: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A boy in a red , white , and blue striped shirt holding and examining a bug .
>
> **Caption B:** A young boy that 's about two is staring at either a rock or sea shell in wonder .
>
> **Adopted scope:** examined object color
>
> **Extracted A:** bug color unstated
>
> **Extracted B:** rock or shell color unstated
>
> **Recorded reason, verbatim:** The bug and rock or shell have no colors; the first shirt's colors do not answer the object condition.

**Audit explanation:** Both examined objects' colors remain unspecified. The first shirt's colors describe clothing.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 715. train_7831: `color of jersey`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A basketball player rejects another basketball players shot in midair right below the basket .
>
> **Caption B:** The man in the white jersey is trying to score and his opponent is trying to catch the ball .
>
> **Adopted scope:** jersey color
>
> **Extracted A:** unstated
>
> **Extracted B:** white
>
> **Recorded reason, verbatim:** The first jerseys have no stated color.

**Audit explanation:** The first players' jersey colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 716. train_7837: `size of pool`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A child plays in a pool while wearing orange floaties .
>
> **Caption B:** A small child is being splashed by water from an inflatable pool .
>
> **Adopted scope:** pool size
>
> **Extracted A:** unstated
>
> **Extracted B:** small inflatable pool implied
>
> **Recorded reason, verbatim:** A child's floaties do not establish the first pool's size.

**Audit explanation:** The first child's floaties leave pool size unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 717. train_7858: `material of object`

**Current status:** `excluded_scope`. **Semantic rating:** `excluded/null`. **Policy:** `S7`.

> **Caption A:** A person is walking by a store window featuring a red dress .
>
> **Caption B:** A couple is looking in a window at a man dressing the mannequin .
>
> **Adopted scope:** shared display-window material
>
> **Extracted A:** glass window
>
> **Extracted B:** glass window
>
> **Recorded reason, verbatim:** A shop display window is the shared structure in both captions, while a dress and a mannequin or clothing are the displayed objects. Neither the unqualified material condition nor the display descriptions select the structure over its contents. The ordinary glass-window reading gives agreement; the display-object reading lacks specified material.

**Audit explanation:** Object has competing referents. The display windows share inferred glass material, while the displayed dress and mannequin or clothing have unspecified materials.

**Recorded scope readings:**

> - **shared shop display windows:** rating 5. A: glass window. B: glass window.
> - **displayed dress and mannequin or clothing:** invalid. A: dress material unspecified. B: mannequin or clothing material unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 718. train_7863: `animal's intention`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a black and white dog is running though water whilst bearing its teeth .
>
> **Caption B:** Dog is swimming through water with a piece of wood in its mouth .
>
> **Adopted scope:** animal intention
>
> **Extracted A:** unstated despite bared teeth
>
> **Extracted B:** unstated while carrying wood
>
> **Recorded reason, verbatim:** Bared teeth and carrying wood do not establish the dogs' intended purpose.

**Audit explanation:** Both dogs' behaviors leave intended purposes unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 719. train_7891: `color of dogs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A brown dog wears a blue muzzle as it runs in the grass .
>
> **Caption B:** A muzzled greyhound dog wearing yellow and black is running on the track .
>
> **Adopted scope:** dog coat color
>
> **Extracted A:** brown
>
> **Extracted B:** unstated; yellow/black worn gear
>
> **Recorded reason, verbatim:** Yellow and black describe worn gear, not the second dog's coat.

**Audit explanation:** The second greyhound's coat color remains unspecified. Yellow and black describe worn gear.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 720. train_7927: `number of observers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man rides his mountain bike with mountains in the background .
>
> **Caption B:** A person on a dirt bike is riding up a hill while people watch on the side .
>
> **Adopted scope:** observer count
>
> **Extracted A:** observers not established
>
> **Extracted B:** multiple watchers
>
> **Recorded reason, verbatim:** The first rider has no stated observers; silence does not establish zero.

**Audit explanation:** The first mountain-bike scene leaves observer presence and count unknown.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 721. train_7959: `appearance of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in front of an Asian shop of some sort working on a bicycle .
>
> **Caption B:** A man in a red shirt is doing something with a bicycle tire .
>
> **Adopted scope:** person appearance
>
> **Extracted A:** unstated beyond man
>
> **Extracted B:** red shirt
>
> **Recorded reason, verbatim:** The first man's location and work do not establish an appearance feature comparable with the red shirt.

**Audit explanation:** The first man's location and bicycle work leave an appearance feature unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 722. train_7973: `color of bicycle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A little boy rides his bike among shadows next to a round metal table .
>
> **Caption B:** A little girl with braided pigtails riding a pink bike .
>
> **Adopted scope:** bicycle color
>
> **Extracted A:** unstated
>
> **Extracted B:** pink
>
> **Recorded reason, verbatim:** The first bicycle's color is unstated.

**Audit explanation:** The first bicycle's color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 723. train_7981: `social interaction`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A baby in a bouncy seat and a standing boy surrounded by toys .
>
> **Caption B:** Two young boys playing , with the younger boy sitting and smiling .
>
> **Adopted scope:** social interaction
>
> **Extracted A:** co-presence without interaction described
>
> **Extracted B:** boys playing
>
> **Recorded reason, verbatim:** Co-presence near toys does not establish that the first children interact socially.

**Audit explanation:** The first children's co-presence near toys leaves social interaction unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 724. train_7985: `purpose of ride`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man riding a red and white bike on sunny day .
>
> **Caption B:** A bicyclist rounds a turn , followed by a cameraman .
>
> **Adopted scope:** ride purpose
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated despite following cameraman
>
> **Recorded reason, verbatim:** Neither sunny weather nor a following cameraman identifies the reason for riding.

**Audit explanation:** Both bicycle rides' purposes remain unspecified despite sunny weather and a following cameraman.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 725. train_8005: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man is about to fall off his surfboard in a wave .
>
> **Caption B:** A man is surfing in a bodysuit in beautiful blue water .
>
> **Adopted scope:** principal surfboard color
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Water color does not supply either surfboard's color.

**Audit explanation:** Both surfboards' colors remain unspecified. Blue describes the second water.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 726. train_8017: `force moving water`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Child in kiddie pool splashes water , sticks out tongue .
>
> **Caption B:** The little boy in red is getting drenched with water .
>
> **Adopted scope:** force moving water
>
> **Extracted A:** child splashing
>
> **Extracted B:** source of drenching unstated
>
> **Recorded reason, verbatim:** Getting drenched does not identify what force or agent moved the water.

**Audit explanation:** The second boy's drenching leaves the water-moving force or agent unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 727. train_8044: `condition of track`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A muzzled greyhound dog is running around a track .
>
> **Caption B:** Dog with muzzle and sweater marked 5 runs on dirt track .
>
> **Adopted scope:** track condition
>
> **Extracted A:** unstated
>
> **Extracted B:** dirt
>
> **Recorded reason, verbatim:** A generic track lacks the second track's dirt-surface information.

**Audit explanation:** The first track's surface condition remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 728. train_8045: `animal breed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A muzzled greyhound dog is running around a track .
>
> **Caption B:** Dog with muzzle and sweater marked 5 runs on dirt track .
>
> **Adopted scope:** dog breed
>
> **Extracted A:** greyhound
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Muzzle and race jersey do not determine dog breed.

**Audit explanation:** The second dog's muzzle and numbered sweater leave breed unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 729. train_8057: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a person in a red jacket standing on a mountain looking out over a grand view of mountains and plains .
>
> **Caption B:** Distant person with blue backpack hiking in rocky area , mountains in background .
>
> **Adopted scope:** person clothing color
>
> **Extracted A:** red jacket
>
> **Extracted B:** clothing unstated; blue backpack
>
> **Recorded reason, verbatim:** The second clothing is uncolored; its blue backpack is separate equipment.

**Audit explanation:** The second person's clothing colors remain unspecified. Blue describes the backpack.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 730. train_8081: `position of ball`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A baseball player in a gray uniform throws a ball to a teammate .
>
> **Caption B:** A young person in a baseball uniform has their arm extended .
>
> **Adopted scope:** ball position
>
> **Extracted A:** in a throw toward teammate
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Arm extension supplies no location for a second ball.

**Audit explanation:** The second person's extended arm leaves a ball position unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 731. train_8097: `number of riders`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Two men in western attire with a brown horse kicking into the air .
>
> **Caption B:** A man in a white cowboy hat trying to tie up a calf at a rodeo .
>
> **Adopted scope:** active rider count
>
> **Extracted A:** riding not established
>
> **Extracted B:** riding not established
>
> **Recorded reason, verbatim:** Neither caption establishes anyone mounted or actively riding.

**Audit explanation:** Both horse-related scenes leave mounted riders and their count unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 732. train_8099: `change in elevation`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person is riding a dirt bike across a dirt covered path .
>
> **Caption B:** A mountain biker jumps off of a fence while going downhill .
>
> **Adopted scope:** elevation change
>
> **Extracted A:** unstated on dirt path
>
> **Extracted B:** downhill and fence jump
>
> **Recorded reason, verbatim:** Travel across a dirt path does not establish ascent, descent or level grade.

**Audit explanation:** The first rider's dirt-path travel leaves ascent, descent or level movement unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 733. train_8112: `confidence in activity performed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cowboy wearing a pink shirt attempting to ride a bucking horse .
>
> **Caption B:** A man in a black vest is riding a bucking horse at a rodeo .
>
> **Adopted scope:** rider confidence
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Neither attempting a ride nor remaining on a horse establishes confidence.

**Audit explanation:** Both riders' bucking-horse activities leave confidence unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 734. train_8121: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog runs on the grass in a yard , a gazebo in the background .
>
> **Caption B:** A black dog chasing a brown and white dog very quickly over a lawn .
>
> **Adopted scope:** dog coat color
>
> **Extracted A:** unstated
>
> **Extracted B:** black and brown-white
>
> **Recorded reason, verbatim:** The first caption supplies no dog coat color.

**Audit explanation:** The first dog's coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 735. train_8123: `gender of snowboarder`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man on a snowboard travels downhill towards the camera .
>
> **Caption B:** A snowboarder in green pants boards down a snowy mountain .
>
> **Adopted scope:** snowboarder gender
>
> **Extracted A:** male
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second rider has no gendered noun or pronoun.

**Audit explanation:** The second snowboarder's gender remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 736. train_8135: `presence of sunglasses`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A silhouetted figure stands at the top of a snow-covered peak at the end of some tracks .
>
> **Caption B:** A woman wearing a black hat and white sunglasses walks up a snowy and steep path .
>
> **Adopted scope:** person sunglasses presence
>
> **Extracted A:** unstated
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** Silhouette information does not establish sunglasses absence.

**Audit explanation:** The first silhouette leaves sunglasses presence unknown.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 737. train_8139: `light in images`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A fireman is on a ladder leaning on a charred and smoking house .
>
> **Caption B:** A fireman searching for something using a flashlight .
>
> **Adopted scope:** scene light
>
> **Extracted A:** unstated
>
> **Extracted B:** flashlight illumination
>
> **Recorded reason, verbatim:** Charred and smoking describe the house, not first-scene illumination.

**Audit explanation:** The first charred and smoking house leaves scene illumination unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 738. train_8149: `presence of audience`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A skateboarder does a trick in the air , another watches and so does a crowd .
>
> **Caption B:** A boy is performing a skateboarding trick with trees in the background .
>
> **Adopted scope:** audience presence
>
> **Extracted A:** crowd and another watcher
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** A tree background does not establish whether spectators are absent.

**Audit explanation:** The second skateboarder's tree backdrop leaves audience presence unknown.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 739. train_8175: `dog breed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two large black and brown dogs run through the tall grass .
>
> **Caption B:** Five muzzled greyhounds are running in a grassy field .
>
> **Adopted scope:** dog breed
>
> **Extracted A:** unstated
>
> **Extracted B:** greyhound
>
> **Recorded reason, verbatim:** Large size and brown/black coats do not identify a breed.

**Audit explanation:** The first dogs' size and coat colors leave breed unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 740. train_8199: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A football player in blue and one in red play in a game .
>
> **Caption B:** The football player gets ready to throw the ball .
>
> **Adopted scope:** player clothing or ball color
>
> **Extracted A:** blue and red clothing
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second caption gives neither clothing nor ball color.

**Audit explanation:** The second football scene leaves clothing and ball colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 741. train_8239: `experience of fatherhood`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The man is holding a baby near a carnival game .
>
> **Caption B:** A new dad sees that his fatherhood is continuing .
>
> **Adopted scope:** fatherhood experience
>
> **Extracted A:** not established
>
> **Extracted B:** new father
>
> **Recorded reason, verbatim:** Holding a baby does not establish fatherhood, much less its duration.

**Audit explanation:** The first man's baby holding leaves fatherhood and its duration unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 742. train_8255: `ethnicity of persons`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young African American boy bounces a soccer ball off his head as another beach visitor observes .
>
> **Caption B:** The little boy in red trunks is attempting to catch a soccer ball that is coming towards him .
>
> **Adopted scope:** person ethnicity
>
> **Extracted A:** African American
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second boy's ethnicity is wholly unstated.

**Audit explanation:** The second boy's ethnicity remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 743. train_8268: `position of rider`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person is riding his bicycle and is flying through the air on it .
>
> **Caption B:** A BMX cyclist is doing a stunt on a riverbank across the river from a factory .
>
> **Adopted scope:** rider position
>
> **Extracted A:** airborne
>
> **Extracted B:** unspecified stunt posture
>
> **Recorded reason, verbatim:** A BMX stunt alone does not establish the rider's airborne status or posture.

**Audit explanation:** The second BMX stunt leaves the rider's airborne status and posture unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 744. train_8277: `time of play`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** two black and white dogs running in a flowery field
>
> **Caption B:** A distorted photo of a playing dog in a flower field
>
> **Adopted scope:** play time
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Neither caption supplies a time of day or play duration.

**Audit explanation:** Both captions leave play time or duration unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 745. train_8299: `animal's expression`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Brown dog with mouth open and ears in air running .
>
> **Caption B:** The short-haired dog is running across a grassy yard .
>
> **Adopted scope:** dog expression
>
> **Extracted A:** open mouth and raised ears
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second dog has no facial-expression information.

**Audit explanation:** The second dog's running leaves facial expression unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 746. train_8303: `weather condition`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white dog with black spots runs through a field covered in snow .
>
> **Caption B:** A single tan-and-white dog dashes through tall green grass .
>
> **Adopted scope:** weather
>
> **Extracted A:** cold snowy field
>
> **Extracted B:** grass, weather unstated
>
> **Recorded reason, verbatim:** Green grass alone does not establish weather or temperature.

**Audit explanation:** The second green grass leaves weather and temperature unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 747. train_8319: `motion of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Musicians preparing to entertain people in a club .
>
> **Caption B:** Performers making music on a guitar and keyboard .
>
> **Adopted scope:** people motion
>
> **Extracted A:** preparing, movement unstated
>
> **Extracted B:** playing instruments
>
> **Recorded reason, verbatim:** Preparing to entertain supplies no recoverable physical motion.

**Audit explanation:** The first musicians' preparation leaves physical motion unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 748. train_8323: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Three small dogs stand in the sand and stare at each other .
>
> **Caption B:** A black and white dog is playing or fighting with a brown dog in grass .
>
> **Adopted scope:** dog colors
>
> **Extracted A:** unstated
>
> **Extracted B:** black-white and brown
>
> **Recorded reason, verbatim:** The first dogs' coat colors are wholly unstated.

**Audit explanation:** The first dogs' coat colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 749. train_8328: `person's occupation`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Guy in an orange vest on a lawn tractor mowing his lawn on a sunny day
>
> **Caption B:** A man with a green jacket and headphones cutting grass .
>
> **Adopted scope:** occupation
>
> **Extracted A:** mowing own lawn
>
> **Extracted B:** cutting grass
>
> **Recorded reason, verbatim:** Mowing one's own lawn does not establish a paid occupation.

**Audit explanation:** Both mowing descriptions establish activities. Paid occupation remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 750. train_8345: `speed of water`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man wearing a helmet and life-vest kayaking in the water .
>
> **Caption B:** This person in a yellow kayak is riding the rapids .
>
> **Adopted scope:** water speed
>
> **Extracted A:** unstated
>
> **Extracted B:** fast rapids
>
> **Recorded reason, verbatim:** A helmet and life vest do not establish the first water's current speed.

**Audit explanation:** The first kayaker's helmet and life vest leave water-current speed unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 751. train_8352: `race of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young black child stands on the edge of a body of water near buckets .
>
> **Caption B:** An african family are standing in front of some makeshift houses .
>
> **Adopted scope:** people race
>
> **Extracted A:** Black child
>
> **Extracted B:** African family, race unspecified
>
> **Recorded reason, verbatim:** African geographical identity does not establish the family's race.

**Audit explanation:** The second family's African geographic identity leaves race unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 752. train_8355: `age group`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** An adult baseball player sliding onto the base while his opponent attempts to tag him .
>
> **Caption B:** A baseball player rounds the bases while another makes a leaping dive for the ball .
>
> **Adopted scope:** players' age
>
> **Extracted A:** adult
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second baseball players have no age information.

**Audit explanation:** The second baseball players' ages remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 753. train_8364: `presence of adults`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Boy in a black and white soccer uniform kicking the ball with other players nearby .
>
> **Caption B:** Two men and four boys play outdoors in close range of a soccer goal net .
>
> **Adopted scope:** adult presence
>
> **Extracted A:** boy and players of unknown age
>
> **Extracted B:** 2 men present
>
> **Recorded reason, verbatim:** Unknown-age players do not establish an adult's presence or absence.

**Audit explanation:** The first players' unknown ages leave adult presence unknown.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 754. train_8371: `clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The small child with a red helmet rides a scooter on a sidewalk .
>
> **Caption B:** A small girl playing , on the sidewalk , with a stick .
>
> **Adopted scope:** child clothing
>
> **Extracted A:** red helmet
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second child has no clothing description.

**Audit explanation:** The second girl's clothing remains undescribed.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 755. train_8390: `instruments used`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A group of people wearing orange and black play various types of drums as others watch .
>
> **Caption B:** An eclectic group of musicians and actors perform for a group of tourists .
>
> **Adopted scope:** instruments
>
> **Extracted A:** drums
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Musicians and actors do not identify any second instrument type.

**Audit explanation:** The second performers' instruments remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 756. train_8431: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person with a yellow and black striped snowboard jumps on the snowy hill .
>
> **Caption B:** A man wearing a bright orange jacket makes a jump on his snowboard .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** unstated; board yellow-black
>
> **Extracted B:** orange jacket
>
> **Recorded reason, verbatim:** Snowboard color does not establish the first rider's clothing color.

**Audit explanation:** The first rider's clothing colors remain unspecified. Yellow and black describe the board.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 757. train_8439: `presence of bracelet`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A mother holds her newborn as she sits with a smiling nurse in the hospital bed .
>
> **Caption B:** A young woman holding a newborn in her arms while still wearing her hospital bracelet laying on a hospital bed .
>
> **Adopted scope:** bracelet presence
>
> **Extracted A:** unstated
>
> **Extracted B:** hospital bracelet
>
> **Recorded reason, verbatim:** The first caption does not establish whether a bracelet is present.

**Audit explanation:** Bracelet presence remains unknown in the first hospital scene.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 758. train_8447: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A little boy wearing green shorts kicking a soccer ball .
>
> **Caption B:** Number 13 kicks a soccer ball towards the goal during children 's soccer game .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** green shorts
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** A uniform number does not establish its color.

**Audit explanation:** The second uniform number leaves clothing color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 759. train_8465: `bicycle type`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A biker dressed in orange and navy is competitively riding a red and white bike .
>
> **Caption B:** A person riding their bicycle up a dirt mound while two other people are in the background watching .
>
> **Adopted scope:** bicycle use/type
>
> **Extracted A:** bicycle used competitively; design subtype unstated
>
> **Extracted B:** bicycle on dirt mound; design subtype unstated
>
> **Recorded reason, verbatim:** Competition and a dirt mound do not identify bicycle design subtypes; generic bicycle alone supplies no bicycle type.

**Audit explanation:** Both cycling contexts leave bicycle design subtypes unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 760. train_8529: `colors`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A mother in blue holds her child outside of a white tent .
>
> **Caption B:** African women looking down at baby on a red blanket .
>
> **Adopted scope:** principal adults' clothing colors
>
> **Extracted A:** blue
>
> **Extracted B:** unstated; blanket red
>
> **Recorded reason, verbatim:** Blanket color does not supply the women's clothing colors.

**Audit explanation:** The second women's clothing colors remain unspecified. Red describes the blanket.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 761. train_8538: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A toddler in a blue dress holding himself up on a rock .
>
> **Caption B:** A young little girl in a dress stands and admires a creek .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** blue
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second dress has no stated color.

**Audit explanation:** The second girl's dress color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 762. train_8549: `intention of players`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A goalie blocking the goal with assistance from a teammate during a hockey game .
>
> **Caption B:** A hockey player in black and white collides with another player wearing blue .
>
> **Adopted scope:** player intention
>
> **Extracted A:** preventing goal
>
> **Extracted B:** collision, intention unknown
>
> **Recorded reason, verbatim:** Collision alone does not establish whether a player intends defense or attack.

**Audit explanation:** The second hockey collision leaves defensive or attacking intent unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 763. train_8561: `presence of microphone`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a black t-shirt and jeans playing electric guitar and grooving to the music .
>
> **Caption B:** A long-haired man stands at a microphone playing a pink Hello Kitty guitar .
>
> **Adopted scope:** microphone presence
>
> **Extracted A:** unstated
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** Guitar playing without microphone mention does not establish absence.

**Audit explanation:** Microphone presence remains unknown in the first guitar scene.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 764. train_8573: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** football team in blue and yellow uniforms handing football off to running back .
>
> **Caption B:** A Sooners football player is tackling an opposing player .
>
> **Adopted scope:** uniform color
>
> **Extracted A:** blue-yellow
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The team name does not establish the specific uniform colors worn.

**Audit explanation:** The second team name leaves the actual uniform colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 765. train_8576: `color of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black and tan puppy is biting the ear of a brown dog .
>
> **Caption B:** Two dogs biting each other playfully while jumping
>
> **Adopted scope:** animal colors
>
> **Extracted A:** black-tan and brown
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Neither second dog's color is supplied.

**Audit explanation:** The second dogs' coat colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 766. train_8584: `type of martial arts`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two Olympic martial arts competitors go after each other in an international martial arts spectacle .
>
> **Caption B:** Man does a flying kick to his opponent in a karate competition inside a gym with referee looking on .
>
> **Adopted scope:** martial art
>
> **Extracted A:** Olympic martial art unspecified
>
> **Extracted B:** karate
>
> **Recorded reason, verbatim:** Olympic event status does not identify the martial-art discipline.

**Audit explanation:** The first Olympic event status leaves martial-art discipline unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 767. train_8585: `skill level of competitors`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two Olympic martial arts competitors go after each other in an international martial arts spectacle .
>
> **Caption B:** Man does a flying kick to his opponent in a karate competition inside a gym with referee looking on .
>
> **Adopted scope:** competitor skill
>
> **Extracted A:** Olympic elite
>
> **Extracted B:** competition, level unspecified
>
> **Recorded reason, verbatim:** An unspecified competition and kick do not establish a comparable skill level.

**Audit explanation:** The second karate competition and kick leave competitor skill level unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 768. train_8598: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Snowboarder in yellow pants and white helmet in midair .
>
> **Caption B:** Brown ramp structure with a person on ski 's in midair .
>
> **Adopted scope:** principal athlete's clothing color
>
> **Extracted A:** yellow-white
>
> **Extracted B:** unstated; ramp brown
>
> **Recorded reason, verbatim:** Brown describes a ramp, not the second athlete's clothing.

**Audit explanation:** The second athlete's clothing colors remain unspecified. Brown describes the ramp.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 769. train_8634: `weather conditions`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Person in wetsuit on top of a surfboard in the water .
>
> **Caption B:** two people jumpinjg over a large wave at the beach
>
> **Adopted scope:** weather conditions
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Surfing and beach play do not establish either weather condition.

**Audit explanation:** Both water activities leave weather conditions unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 770. train_8653: `presence of dog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Group of people standing on a snow covered ground , some are holding brooms , there is a dog with the group .
>
> **Caption B:** Two men and one woman trying to sled in show , using coats and plastic instead of sleigh .
>
> **Adopted scope:** dog presence
>
> **Extracted A:** present
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second snow scene does not establish a dog's absence.

**Audit explanation:** Dog presence remains unknown in the second sledding scene.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 771. train_8660: `stage of meal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Several people are at a restaurant looking at red menus .
>
> **Caption B:** A group of people are sitting around a table with wine .
>
> **Adopted scope:** meal stage
>
> **Extracted A:** menu selection before ordering food
>
> **Extracted B:** wine on table; meal stage unstated
>
> **Recorded reason, verbatim:** Wine on a table does not establish a particular meal stage; choosing from menus supplies one only in the first caption.

**Audit explanation:** The second group's wine leaves meal stage unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 772. train_8668: `roughness of dogs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A heavily scarred pitbull attempts to take a playtoy from another pitbull .
>
> **Caption B:** Two dogs engaged in physical contact with a man in the background .
>
> **Adopted scope:** dog roughness
>
> **Extracted A:** scarred, taking toy
>
> **Extracted B:** physical contact unspecified
>
> **Recorded reason, verbatim:** Physical contact alone establishes neither rough play nor a rough body condition.

**Audit explanation:** The second dogs' physical contact leaves play roughness and bodily condition unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 773. train_8669: `presence of human`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A heavily scarred pitbull attempts to take a playtoy from another pitbull .
>
> **Caption B:** Two dogs engaged in physical contact with a man in the background .
>
> **Adopted scope:** human presence
>
> **Extracted A:** unstated
>
> **Extracted B:** man present
>
> **Recorded reason, verbatim:** The first dogs' scene does not establish human absence.

**Audit explanation:** Human presence remains unknown in the first dogs' scene.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 774. train_8673: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white clad rider atop a horse jumping over a series of poles .
>
> **Caption B:** A horse with a man on it is jumping over hurdles .
>
> **Adopted scope:** object color
>
> **Extracted A:** white rider clothing
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second scene supplies no comparable object color.

**Audit explanation:** The second horse-jumping scene leaves comparable object color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 775. train_8681: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young man in a black shirt and brown pants is skateboarding .
>
> **Caption B:** A man flies through the air on his skateboard above a white staircase .
>
> **Adopted scope:** principal skater's clothing color
>
> **Extracted A:** black-brown
>
> **Extracted B:** unstated; staircase white
>
> **Recorded reason, verbatim:** Stair color does not supply the second skater's clothing color.

**Audit explanation:** The second skateboarder's clothing colors remain unspecified. White describes the staircase.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 776. train_8683: `color of dogs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A little dog plays with a colorful ball in the sand .
>
> **Caption B:** The large brown and white dog splashes on the shore .
>
> **Adopted scope:** dog color
>
> **Extracted A:** unstated
>
> **Extracted B:** brown-white
>
> **Recorded reason, verbatim:** The ball's colors do not establish the first dog's color.

**Audit explanation:** The first dog's coat color remains unspecified by the ball's colors.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 777. train_8691: `color of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two dogs walk over the gravel yard inside a gated area .
>
> **Caption B:** The big black dog is behind the little black dog .
>
> **Adopted scope:** animal colors
>
> **Extracted A:** unstated
>
> **Extracted B:** black
>
> **Recorded reason, verbatim:** The first dogs have no coat colors supplied.

**Audit explanation:** The first dogs' coat colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 778. train_8701: `color of child's clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young child playing with pink , purple , and green blocks , sitting in a green chair at a mahogany table .
>
> **Caption B:** A child in a blue scarf and a tan outfit plays with plastic toys on a rug nearby a soft chair .
>
> **Adopted scope:** child clothing color
>
> **Extracted A:** unstated
>
> **Extracted B:** blue-tan
>
> **Recorded reason, verbatim:** Chair and block colors do not establish the first child's clothing color.

**Audit explanation:** The first child's clothing colors remain unspecified. The chair and blocks supply other colors.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 779. train_8706: `sentiment of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in winter gear and a ski mask lays upon a pile of snow .
>
> **Caption B:** A couple is playing in the snow and he has either fallen or is going to make an angel .
>
> **Adopted scope:** people sentiment
>
> **Extracted A:** unstated
>
> **Extracted B:** playful
>
> **Recorded reason, verbatim:** Lying in snow does not establish the first man's feelings.

**Audit explanation:** The first man's lying in snow leaves emotional state unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 780. train_8719: `place of performing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person performing tricks on a bicycle in a skate park .
>
> **Caption B:** The boy is doing a stunt through the air , on a bicycle .
>
> **Adopted scope:** performance location
>
> **Extracted A:** skate park
>
> **Extracted B:** airborne, venue unstated
>
> **Recorded reason, verbatim:** Airborne posture does not identify the second stunt's venue.

**Audit explanation:** The second cyclist's airborne position leaves performance venue unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 781. train_8727: `football play type`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A football player passes the football to a teammate as the crowd looks on .
>
> **Caption B:** Oklahoma University 's Sooners football team playing against a rival .
>
> **Adopted scope:** football play
>
> **Extracted A:** pass
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** A general football matchup does not identify a particular play.

**Audit explanation:** The second general football matchup leaves play type unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 782. train_8733: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A small brown dog running with a multicolored ball in his mouth .
>
> **Caption B:** A dog with long hair and a red vest runs in the grass .
>
> **Adopted scope:** dog coat color
>
> **Extracted A:** brown
>
> **Extracted B:** unstated; vest red
>
> **Recorded reason, verbatim:** A red vest does not establish the second dog's coat color.

**Audit explanation:** The second dog's coat color remains unspecified. Red describes the vest.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 783. train_8735: `size of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog runs through the forest with something in its mouth .
>
> **Caption B:** A black dog runs on green grass towards the camera .
>
> **Adopted scope:** principal dog size
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Neither dog has size information.

**Audit explanation:** Both dogs' body sizes remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 784. train_8744: `color of water`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person is diving into blue water on a rocky shore .
>
> **Caption B:** Two males on a rock over water , one in midair jumping into the water .
>
> **Adopted scope:** water color
>
> **Extracted A:** blue
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second water's color is wholly unspecified.

**Audit explanation:** The second water's color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 785. train_8747: `color of dress`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Closeup of a skier with his poles out wide to the side .
>
> **Caption B:** A person dressed in red and gray is skiing down a snowy slope .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** unstated
>
> **Extracted B:** red-gray
>
> **Recorded reason, verbatim:** The first skier's outfit has no supplied color.

**Audit explanation:** The first skier's outfit colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 786. train_8819: `type of surfboard`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A surfer on a red surfboard jumps over a high wave in the ocean .
>
> **Caption B:** Guy in black wetsuit is riding a wave with a white surfboard .
>
> **Adopted scope:** surfboard type
>
> **Extracted A:** surfboard, subtype unstated
>
> **Extracted B:** surfboard, subtype unstated
>
> **Recorded reason, verbatim:** Both captions repeat surfboard without a recoverable surfboard subtype; color and jumping do not supply one.

**Audit explanation:** Both surfboards' subtypes remain unspecified by their colors and surfing maneuvers.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 787. train_8841: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a white helmet and huge backpack is rock climbing .
>
> **Caption B:** There is a person scaling a very steep rock wall .
>
> **Adopted scope:** object color
>
> **Extracted A:** white helmet
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second climber/scene has no supplied object color.

**Audit explanation:** The second climbing scene leaves comparable object color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 788. train_8855: `color of costume`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The girl is twirling long , colorful streamers .
>
> **Caption B:** The girl in a bright pink skirt dances near a stroller .
>
> **Adopted scope:** costume color
>
> **Extracted A:** unstated; streamers colorful
>
> **Extracted B:** pink skirt
>
> **Recorded reason, verbatim:** Colorful streamers do not establish the first costume color.

**Audit explanation:** The first girl's costume color remains unspecified. The streamers supply colors.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 789. train_8863: `emotional atmosphere`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a black helmet and white jersey is paddling along high waves .
>
> **Caption B:** A kayaker is battling waves in a purple boat while wearing rain gear .
>
> **Adopted scope:** emotional atmosphere
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Rough water does not establish the people's emotional state.

**Audit explanation:** Both rough-water paddling scenes leave emotional atmosphere unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 790. train_8864: `vehicle elevation`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A rider stands for a moment above his dirk bike .
>
> **Caption B:** A motocross rider at night high in the air above the dirt .
>
> **Adopted scope:** vehicle elevation
>
> **Extracted A:** unstated beneath standing rider
>
> **Extracted B:** high airborne
>
> **Recorded reason, verbatim:** Standing above a bike does not locate that bike relative to the ground.

**Audit explanation:** The first rider's position above the bike leaves the bike's ground-relative elevation unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 791. train_8875: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A motorcycle racer going down a steep , dirt hill .
>
> **Caption B:** Am motor cross rider in a green suit is riding his bike on a dirt road .
>
> **Adopted scope:** object color
>
> **Extracted A:** unstated
>
> **Extracted B:** green suit
>
> **Recorded reason, verbatim:** The first rider and vehicle have no color information.

**Audit explanation:** The first motocross scene leaves rider and vehicle colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 792. train_8895: `color of dog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A brown dog with large ears is shaking its self while standing on sand .
>
> **Caption B:** A dog running and jumping in the mud , with a person walking behind it .
>
> **Adopted scope:** dog color
>
> **Extracted A:** brown
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second dog's coat color is missing.

**Audit explanation:** The second dog's coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 793. train_8897: `color of equipment`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** This man is wearing green and black equipment to ride his dirt bike .
>
> **Caption B:** A young man is standing while riding his motorized bike .
>
> **Adopted scope:** riding equipment color
>
> **Extracted A:** green-black
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second rider's equipment colors are missing.

**Audit explanation:** The second rider's equipment colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 794. train_8898: `reason for physical activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two people wearing snowshoes jump into the air to pose for a photo .
>
> **Caption B:** Two people jumping up with snow covered mountains in the background .
>
> **Adopted scope:** reason for jumping
>
> **Extracted A:** posing for photo
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** A jump in scenic mountains does not establish its purpose.

**Audit explanation:** The second jump's scenic backdrop leaves purpose unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 795. train_8922: `clothing color`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young girl in a blue and pink bathing suit runs around a pool .
>
> **Caption B:** A girl is screaming as she comes off the water slide .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** blue-pink
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Coming down a water slide does not supply clothing color.

**Audit explanation:** The second girl's water-slide activity leaves clothing colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 796. train_8951: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** two men outside one working with a pole in hand .
>
> **Caption B:** Two workers in yellow vests try to fix something .
>
> **Adopted scope:** object color
>
> **Extracted A:** unstated
>
> **Extracted B:** yellow vests
>
> **Recorded reason, verbatim:** The first workers/tools have no specified colors.

**Audit explanation:** The first workers and pole have unspecified colors.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 797. train_8965: `gender of child`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A child in swimming trunks jumping into the ocean .
>
> **Caption B:** A little girl in a striped bathing suit jumps in the ocean .
>
> **Adopted scope:** child gender
>
> **Extracted A:** unstated
>
> **Extracted B:** female
>
> **Recorded reason, verbatim:** Swimming trunks alone do not establish the child's gender.

**Audit explanation:** The first child's swimming trunks leave gender unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 798. train_8978: `ability to climb`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person looking out and standing on top of a rock .
>
> **Caption B:** Woman with a hat on climbing a cliff near a large body of water .
>
> **Adopted scope:** climbing ability
>
> **Extracted A:** standing on rock, ability unknown
>
> **Extracted B:** climbing cliff
>
> **Recorded reason, verbatim:** Standing on a rock does not establish climbing ability.

**Audit explanation:** The first person's standing atop a rock leaves climbing ability unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 799. train_8991: `object jumped from`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** The skateboarder wearing jeans and a white shirt jumps a ramp .
>
> **Caption B:** a skateboarder jumping on a wall with a mountain in the background
>
> **Adopted scope:** object jumped from
>
> **Extracted A:** ramp-associated jump
>
> **Extracted B:** jumping on a wall; launch source unstated
>
> **Recorded reason, verbatim:** The explicit from condition requests the origin. Jumping on a wall may identify a target or supporting obstacle without establishing a launch point; associated object is not the requested relation.

**Audit explanation:** The second wall-associated jump leaves its launch source unspecified, which the jumped-from relation requires.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 800. train_9030: `intensity of game`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A group of soccer players are grabbing on to each other as they go for the ball .
>
> **Caption B:** Four men are playing soccer , two in white jerseys , one in a red jersey and a goalie in the background .
>
> **Adopted scope:** game intensity
>
> **Extracted A:** physical grabbing contest
>
> **Extracted B:** playing, intensity unspecified
>
> **Recorded reason, verbatim:** Ordinary soccer participation does not establish the second game's intensity.

**Audit explanation:** The second ordinary soccer participation leaves game intensity unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 801. train_9043: `color of cars`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Bright blue car going down a dirt road , as onlookers watch .
>
> **Caption B:** A racing car is driving around a wet track with its headlights on .
>
> **Adopted scope:** car color
>
> **Extracted A:** bright blue
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Headlights and a wet track do not identify car color.

**Audit explanation:** The second car's headlights and wet track leave body color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 802. train_9081: `weather animal is in`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A brown dog jumps over the dead plants in a snowy field .
>
> **Caption B:** A brown dog is carrying a stick too big for him over grass .
>
> **Adopted scope:** weather
>
> **Extracted A:** snowy cold context
>
> **Extracted B:** grass, weather unspecified
>
> **Recorded reason, verbatim:** Grass does not establish weather or temperature.

**Audit explanation:** The second grassy location leaves weather and temperature unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 803. train_9144: `foot coverings`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Children are playing under an umbrella in a body of water .
>
> **Caption B:** Children play barefoot in the sand next to a rusting oil pipeline .
>
> **Adopted scope:** foot coverings
>
> **Extracted A:** unstated
>
> **Extracted B:** bare feet
>
> **Recorded reason, verbatim:** Water play does not establish the first children's footwear.

**Audit explanation:** The first children's water play leaves footwear unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 804. train_9145: `wetness of children's feet`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Children are playing under an umbrella in a body of water .
>
> **Caption B:** Children play barefoot in the sand next to a rusting oil pipeline .
>
> **Adopted scope:** feet wetness
>
> **Extracted A:** in water, wet implied
>
> **Extracted B:** sand, wetness unknown
>
> **Recorded reason, verbatim:** Sand may be wet or dry; second foot wetness is unavailable.

**Audit explanation:** The second children's foot wetness remains unspecified because sand supports wet and dry possibilities.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 805. train_9150: `lighting around person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man wearing black pants , an orange and brown striped shirt , and a black bandanna in a " just thrown a bowling ball " stance .
>
> **Caption B:** A silhouette stands at the top of a bowling lane as the ball is about to impact the pins while neon lights race overhead .
>
> **Adopted scope:** lighting
>
> **Extracted A:** unstated
>
> **Extracted B:** neon lights and silhouette
>
> **Recorded reason, verbatim:** The first bowling stance and clothes supply no lighting information.

**Audit explanation:** The first bowler's stance and clothing leave lighting unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 806. train_9152: `speed of child`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The girl with the blue bucket splashes beneath the pier .
>
> **Caption B:** A child slides down a slide and into the water .
>
> **Adopted scope:** child speed
>
> **Extracted A:** splashing, travel speed unknown
>
> **Extracted B:** sliding
>
> **Recorded reason, verbatim:** Splashing does not establish the child's travel speed.

**Audit explanation:** The first girl's splashing leaves travel speed unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 807. train_9172: `rider's activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A view from the top of a skateboarder at the top of a ramp .
>
> **Caption B:** A teenage boy is performing a trick with his skateboard .
>
> **Adopted scope:** skater activity
>
> **Extracted A:** at ramp top, action unspecified
>
> **Extracted B:** performing trick
>
> **Recorded reason, verbatim:** A skateboarder's location at ramp top does not establish a current action.

**Audit explanation:** The first skateboarder's ramp-top location leaves current action unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 808. train_9185: `presence of observers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man is pulling tricks on his rollerblades in a indoor skate park .
>
> **Caption B:** Person doing a trick on a skateboard in a skate park while people watch .
>
> **Adopted scope:** observer presence
>
> **Extracted A:** unstated
>
> **Extracted B:** people watching
>
> **Recorded reason, verbatim:** No observer mention does not establish their absence.

**Audit explanation:** Observer presence remains unknown in the first indoor skate-park scene.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 809. train_9207: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog runs in a field with its tongue sticking out .
>
> **Caption B:** A white dog with a black patch goes through an obstacle .
>
> **Adopted scope:** dog color
>
> **Extracted A:** unstated
>
> **Extracted B:** white-black
>
> **Recorded reason, verbatim:** The first dog's coat color is wholly unspecified.

**Audit explanation:** The first dog's coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 810. train_9226: `absence of shirt`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A climber hangs from a rock face over blue water .
>
> **Caption B:** The climber is hanging off a vertical cliff with gear but no shirt .
>
> **Adopted scope:** shirt absence
>
> **Extracted A:** unstated
>
> **Extracted B:** explicit shirtless
>
> **Recorded reason, verbatim:** The first climber's shirt presence is unestablished.

**Audit explanation:** The first climber's shirt status remains unknown.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 811. train_9265: `contents of mouth`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A long-haired dog walks out of the water and licks his nose .
>
> **Caption B:** A black dog is swimming in green water with something in its mouth .
>
> **Adopted scope:** mouth contents
>
> **Extracted A:** tongue licking nose, held object unknown
>
> **Extracted B:** unspecified held object
>
> **Recorded reason, verbatim:** Licking a nose does not establish a held mouth-content object.

**Audit explanation:** The first dog's tongue action leaves an independently held mouth object unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 812. train_9267: `perspective`

**Current status:** `excluded_scope`. **Semantic rating:** `excluded/null`. **Policy:** `S7`.

> **Caption A:** A male dressed in a sports outfit tries to catch a baseball .
>
> **Caption B:** A man in a blue jersey and red hat is about to throw a baseball .
>
> **Adopted scope:** perspective: camera viewpoint versus participant role
>
> **Extracted A:** catching baseball; photographic viewpoint unstated
>
> **Extracted B:** about to throw baseball; photographic viewpoint unstated
>
> **Recorded reason, verbatim:** The unqualified condition can request photographic viewpoint, which is missing, or participant-role perspective, where receiver and thrower differ. The frozen conventions do not select a feature.

**Audit explanation:** Perspective has competing readings. Camera viewpoint remains unspecified, while participant role distinguishes receiving and throwing.

**Recorded scope readings:**

> - **photographic camera viewpoint:** invalid.
> - **baseball participant-role perspective:** rating 1.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 813. train_9279: `activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The snowboarder is wearing a red jacket and black helmet .
>
> **Caption B:** A group of people watching a snowboarder perform a trick .
>
> **Adopted scope:** principal athlete activity
>
> **Extracted A:** snowboarder, action unspecified
>
> **Extracted B:** performing snowboard trick
>
> **Recorded reason, verbatim:** Calling someone a snowboarder and describing their clothes does not establish a current activity.

**Audit explanation:** The first snowboarder's clothing and sport label leave current activity unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 814. train_9297: `presence of sweatshirt`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A little girl plays with an miniature electric circuit consisting of three light bulbs and a battery .
>
> **Caption B:** A young girl in a white zip up sweatshirt plays with a train set on a table .
>
> **Adopted scope:** sweatshirt presence
>
> **Extracted A:** unstated
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** An electronics activity does not establish sweatshirt presence or absence.

**Audit explanation:** Sweatshirt presence remains unknown in the first electronics scene.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 815. train_9301: `time of day`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Small boy and girl in the grass , the boy kneeling being fed something by the girl .
>
> **Caption B:** Four black children smiling and eating their lunch on the ground .
>
> **Adopted scope:** time of day
>
> **Extracted A:** unstated
>
> **Extracted B:** lunchtime
>
> **Recorded reason, verbatim:** The first feeding scene has no time-of-day information.

**Audit explanation:** The first children's feeding scene leaves time of day unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 816. train_9310: `color of baseball uniform`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A pitcher is getting ready to throw a ball during a baseball game .
>
> **Caption B:** A man in a gray baseball uniform and a black hat is catching a ball in a baseball mit .
>
> **Adopted scope:** baseball uniform color
>
> **Extracted A:** unstated
>
> **Extracted B:** gray-black
>
> **Recorded reason, verbatim:** The first baseball uniform has no color information.

**Audit explanation:** The first pitcher's uniform colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 817. train_9323: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black dog chasing a brown and white dog very quickly over a lawn .
>
> **Caption B:** Two dogs play with an orange toy in tall grass .
>
> **Adopted scope:** dog colors
>
> **Extracted A:** black and brown-white
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Toy color does not establish second dog colors.

**Audit explanation:** The second dogs' coat colors remain unspecified. Orange describes their toy.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 818. train_9327: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman shows a dog with very long hair at a dog show .
>
> **Caption B:** A black and white dog performs a jump with his owner looking on .
>
> **Adopted scope:** dog color
>
> **Extracted A:** unstated
>
> **Extracted B:** black-white
>
> **Recorded reason, verbatim:** Long hair does not establish the first dog's color.

**Audit explanation:** The first dog's long hair leaves coat color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 819. train_9348: `speed of rider`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cowboy is being thrown from a large brown bull .
>
> **Caption B:** A man is riding a horse in a western rodeo competition .
>
> **Adopted scope:** rider speed
>
> **Extracted A:** being thrown
>
> **Extracted B:** riding, pace unspecified
>
> **Recorded reason, verbatim:** Generic rodeo riding gives no recoverable speed.

**Audit explanation:** The second rider's generic rodeo participation leaves movement speed unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 820. train_9349: `sentiment of rider`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cowboy is being thrown from a large brown bull .
>
> **Caption B:** A man is riding a horse in a western rodeo competition .
>
> **Adopted scope:** rider sentiment
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Neither rider has explicit or directly recoverable sentiment.

**Audit explanation:** Both rodeo scenes leave rider sentiment unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 821. train_9380: `existence of a toy`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The little white dog is trying to bite onto the stick that the black dog is carrying .
>
> **Caption B:** The black dog playfully bites the yellow dog near the furniture .
>
> **Adopted scope:** toy presence
>
> **Extracted A:** stick used in play
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Play biting does not establish a toy's presence or absence.

**Audit explanation:** Toy presence remains unknown during the second dogs' playful biting.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 822. train_9404: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young woman is jumping up to hit a volleyball while playing beach volleyball .
>
> **Caption B:** Female volleyball player dressed in blue anticipates a ball .
>
> **Adopted scope:** object color
>
> **Extracted A:** unstated
>
> **Extracted B:** blue clothing
>
> **Recorded reason, verbatim:** The first player/equipment has no color supplied.

**Audit explanation:** The first volleyball scene leaves player and equipment colors unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 823. train_9411: `sentiment of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The musicians are rehearsing for the event , possibly at school or even a concert
>
> **Caption B:** An ensemble of children are playing classical instruments at a concert .
>
> **Adopted scope:** people sentiment
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Rehearsal or concert performance does not establish feelings.

**Audit explanation:** Both musical activities leave participants' feelings unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 824. train_9440: `surrounding landscape`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** White dog traveling alone down a paved path through some woods
>
> **Caption B:** A black dog with brown markings wearing a red vest trots down a path .
>
> **Adopted scope:** surrounding landscape
>
> **Extracted A:** woods
>
> **Extracted B:** unstated beyond path
>
> **Recorded reason, verbatim:** The second path's surrounding landscape is wholly unstated.

**Audit explanation:** The second path's surrounding landscape remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 825. train_9480: `breed of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A hairy dog tries to follow its owner around an obstacle course .
>
> **Caption B:** There is a brown and white dog jumping off of a seesaw .
>
> **Adopted scope:** animal breed
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Hairiness and colors do not identify either dog's breed.

**Audit explanation:** Both dogs' hair and coat colors leave breed unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 826. train_9495: `presence of crowd`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** the band is getting ready for tonight 's show with a pre-show run through .
>
> **Caption B:** A band is putting on a light show and a performance in front of a crowd .
>
> **Adopted scope:** crowd presence
>
> **Extracted A:** unstated
>
> **Extracted B:** crowd present
>
> **Recorded reason, verbatim:** Rehearsal does not establish crowd absence.

**Audit explanation:** Crowd presence remains unknown during the first band's rehearsal.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 827. train_9525: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A girl with black hair and jeans is rolling a ball to knock down three pins in a bowling alley .
>
> **Caption B:** Someone dressed in a gray top looks on as the bowl rolls down the lane on lane eight at the colorful bowling alley .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** jeans, shirt color unstated
>
> **Extracted B:** gray top
>
> **Recorded reason, verbatim:** Jeans do not determine a color, and black describes hair.

**Audit explanation:** The first girl's clothing colors remain unspecified. Black describes hair, and jeans identify garment type.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 828. train_9553: `position of men in relation to boat`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** Fishermen work their nets closer to shore while a boat sits in the water connected to the nets .
>
> **Caption B:** One man without a shirt and a man with a hat steering are in a small boat .
>
> **Adopted scope:** men relative to boat
>
> **Extracted A:** working nets near shore, location uncertain
>
> **Extracted B:** inside boat
>
> **Recorded reason, verbatim:** Working nets near shore does not place the fishermen inside or outside the connected boat.

**Audit explanation:** The first fishermen's position inside or outside the connected boat remains unspecified during their net work near shore.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 829. train_9560: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A girl dressed in a lavender sweater holds a boy 's footwear as they both sit on a tan carpet .
>
> **Caption B:** the little boy sitting next to the girl is covering his face with his hand .
>
> **Adopted scope:** object color
>
> **Extracted A:** lavender sweater, tan carpet
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second caption supplies no object color.

**Audit explanation:** The second scene leaves comparable object color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 830. train_9564: `number of observers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Man raising his arms triumphantly as he leads the pack in a bike race .
>
> **Caption B:** Crowds cheer on cyclists as they complete a race to the finish .
>
> **Adopted scope:** observer count
>
> **Extracted A:** unstated
>
> **Extracted B:** crowds
>
> **Recorded reason, verbatim:** Other racers do not establish observers, and no absence is stated.

**Audit explanation:** The first pack consists of racers. Observer presence and count remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 831. train_9581: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young person in a baseball uniform has their arm extended .
>
> **Caption B:** a boy in an orange jersey is about to pitch a baseball .
>
> **Adopted scope:** object color
>
> **Extracted A:** unstated
>
> **Extracted B:** orange jersey
>
> **Recorded reason, verbatim:** The first player's equipment/clothing colors are unspecified.

**Audit explanation:** The first baseball player's clothing and equipment colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 832. train_9591: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a plaid red shirt casts his fishing line out into the water .
>
> **Caption B:** Fisherman wearing a poncho and hat sitting at the edge of the water .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** red plaid
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Poncho and hat types do not identify their colors.

**Audit explanation:** The second poncho and hat have unspecified colors.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 833. train_9593: `color of outfit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two men in a red uniform and a blue uniform combat in karate in a gymnasium .
>
> **Caption B:** Two people wrestling while someone else stands above them .
>
> **Adopted scope:** outfit colors
>
> **Extracted A:** red-blue
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** No second outfit color is supplied.

**Audit explanation:** The second wrestlers' outfit colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 834. train_9623: `type of musical instrument`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Three men are playing music for people , and look very focused on what they are doing .
>
> **Caption B:** A man wearing all black plays a coffee-burst bass guitar with a band .
>
> **Adopted scope:** instrument type
>
> **Extracted A:** unstated
>
> **Extracted B:** bass guitar
>
> **Recorded reason, verbatim:** Playing music does not identify any first instrument type.

**Audit explanation:** The first men's musical performance leaves instrument type unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 835. train_9624: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two little boys , from the waist up , in a martial arts match , one delivering a punch and the other blocking .
>
> **Caption B:** A dark-haired young boy and a little blond girl are dressed in karate outfits with yellow belts .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** unstated
>
> **Extracted B:** yellow belts
>
> **Recorded reason, verbatim:** No color is supplied for the first martial-arts outfits.

**Audit explanation:** The first martial-arts outfits' colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 836. train_9642: `breed of dog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A tan curly-haired dog jumps in the snow with a stick in its mouth .
>
> **Caption B:** A brown dog with a tennis ball its mouth rolling on its back on a grassy surface .
>
> **Adopted scope:** dog breed
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Curly hair and brown color do not identify dog breeds.

**Audit explanation:** Both dogs' hair and coat colors leave breeds unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 837. train_9677: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A male runner wearing a red shirt grimaces as he is overtaken by another male runner who is wearing the number 161 on his chest .
>
> **Caption B:** An athlete is running down the road with the number " 12 " taped to the front of his shirt .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** red
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** A race number does not supply shirt color.

**Audit explanation:** The second runner's race number leaves shirt color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 838. train_9687: `method of swinging`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A child pushes another that is sitting in a swing near playground equipment .
>
> **Caption B:** Kids wearing jackets and hats swinging on tire swing in snow
>
> **Adopted scope:** swing propulsion
>
> **Extracted A:** another child pushing
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second caption does not identify what propels the swing.

**Audit explanation:** The second tire swing's propulsion method remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 839. train_9701: `facial expression`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A female in a lime green shirt is rolling a bowling ball at three pins .
>
> **Caption B:** A woman laughing and having fun at a bowling alley .
>
> **Adopted scope:** facial expression
>
> **Extracted A:** unstated
>
> **Extracted B:** laughing
>
> **Recorded reason, verbatim:** The first bowling action does not supply facial expression.

**Audit explanation:** The first woman's bowling action leaves facial expression unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 840. train_9724: `animal breed`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A white dog wearing a red collar is jumping up from the grass .
>
> **Caption B:** A dog stands on his hind legs amid a shower of tennis balls .
>
> **Adopted scope:** animal breed
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Neither caption identifies a dog breed.

**Audit explanation:** Both dogs' breeds remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 841. train_9747: `people's sentiment`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** People are gathered by a tree beside a line of white tents .
>
> **Caption B:** A group of colorfully dressed people is surrounded by white smoke .
>
> **Adopted scope:** people sentiment
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Gathering and smoke give no recoverable sentiment.

**Audit explanation:** Both groups' gatherings and surroundings leave sentiment unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 842. train_9749: `relationship of players`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A boy in a green uniform is kicking a soccer ball in a game while two others stand behind him .
>
> **Caption B:** Guy in white trying to score in soccer while being blocked by two guys in orange and black
>
> **Adopted scope:** players' team relationship
>
> **Extracted A:** unspecified
>
> **Extracted B:** opponents blocking scorer
>
> **Recorded reason, verbatim:** The first other players' affiliations are unspecified.

**Audit explanation:** The first additional soccer players' team affiliations remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 843. train_9761: `position of ball relative to players`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two volleyball girls team both jumping for a double high-five
>
> **Caption B:** A girl in a white shirt and black shorts hitting a volleyball .
>
> **Adopted scope:** ball position
>
> **Extracted A:** unstated
>
> **Extracted B:** at hitting player
>
> **Recorded reason, verbatim:** High-fiving players do not establish a ball's position.

**Audit explanation:** The first players' high-five leaves ball position unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 844. train_9770: `aids used (or absence of aids) to read book`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a green coat using a magnifying glass to read a book while sitting on a bench .
>
> **Caption B:** The elderly gentleman in public is reading a book on the bench .
>
> **Adopted scope:** reading aid presence/type
>
> **Extracted A:** magnifying glass
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Reading without a named aid does not establish aid absence.

**Audit explanation:** The second man's reading-aid status remains unknown.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 845. train_9772: `location`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A group of bike riders are riding in an athletic event .
>
> **Caption B:** A group of cyclists ride their bikes on a road .
>
> **Adopted scope:** cycling location
>
> **Extracted A:** athletic event, venue unspecified
>
> **Extracted B:** road
>
> **Recorded reason, verbatim:** An athletic event supplies no physical cycling venue.

**Audit explanation:** The first athletic event leaves physical cycling location unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 846. train_9783: `shoppers' focus`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** People are walking around a mall type place with a pink tiled floor .
>
> **Caption B:** 2 friends are looking at clothes at a stand while at a shopping mall .
>
> **Adopted scope:** shoppers' focus
>
> **Extracted A:** unstated while walking
>
> **Extracted B:** clothes
>
> **Recorded reason, verbatim:** Walking in a mall does not identify what shoppers attend to.

**Audit explanation:** The first mall visitors' walking leaves their attention target unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 847. train_9837: `focus of children's attention`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A classroom of small children looking at an African American teacher .
>
> **Caption B:** Children are performing activities inside a classroom .
>
> **Adopted scope:** children attention
>
> **Extracted A:** teacher
>
> **Extracted B:** unspecified activities
>
> **Recorded reason, verbatim:** Unspecified activities do not identify the children's focus of attention in the second.

**Audit explanation:** The second children's unspecified activities leave their attention target unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 848. train_9843: `Presence of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A brown and white dog with a brown and black bandanna running very fast .
>
> **Caption B:** A boy wearing a red shirt runs across the grass with a furry dog .
>
> **Adopted scope:** people presence
>
> **Extracted A:** unstated
>
> **Extracted B:** boy present
>
> **Recorded reason, verbatim:** A dog-only description does not establish that people are absent.

**Audit explanation:** People presence remains unknown in the first dog scene.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 849. train_9877: `continent`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A group of African merchants sell a variety of vegetables in a market .
>
> **Caption B:** Produce market in India protected by umbrella shades .
>
> **Adopted scope:** market continent
>
> **Extracted A:** African merchants, market location unspecified
>
> **Extracted B:** India, Asia
>
> **Recorded reason, verbatim:** Merchants' origin does not fix the market's continent.

**Audit explanation:** The first merchants' African identity leaves the market's continent unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 850. train_9885: `movement`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Woman with red headwrap at a market with a woman with a brown headwrap .
>
> **Caption B:** Women with head coverings walking through a outdoor market
>
> **Adopted scope:** movement
>
> **Extracted A:** at market, motion unstated
>
> **Extracted B:** walking
>
> **Recorded reason, verbatim:** Being at a market does not establish movement.

**Audit explanation:** The first women's market location leaves movement unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 851. train_9893: `color of snowboard`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A person on a green board is snowboarding in midair .
>
> **Caption B:** An individual skating on a beautiful snowy clear day .
>
> **Adopted scope:** snowboard color
>
> **Extracted A:** green
>
> **Extracted B:** no snowboard identified
>
> **Recorded reason, verbatim:** The second identifies no snowboard or snowboard color.

**Audit explanation:** The second skating scene leaves a snowboard and its color unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 852. train_9896: `size of dog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A big brown dog is jumping in the water and has his mouth wide open .
>
> **Caption B:** An open-mouthed dog is running through the water .
>
> **Adopted scope:** dog size
>
> **Extracted A:** big
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** An open mouth gives no second-dog size information.

**Audit explanation:** The second dog's open mouth leaves body size unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 853. train_9901: `exit of dog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A brown dog shakes off water after exiting a natural pond .
>
> **Caption B:** A small dog is jumping on the dirt in front of some water
>
> **Adopted scope:** dog exit state
>
> **Extracted A:** just exited pond
>
> **Extracted B:** near water, exit unstated
>
> **Recorded reason, verbatim:** Being near water does not establish that the dog just exited it.

**Audit explanation:** The second dog's proximity to water leaves a recent exit unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 854. train_9924: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in swimming trunks plays in the ocean 's waves .
>
> **Caption B:** A man in a black suit is surfing along a crashing wave .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** unstated
>
> **Extracted B:** black
>
> **Recorded reason, verbatim:** The first swim trunks have no color supplied.

**Audit explanation:** The first swim trunks' colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 855. train_9949: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The young man with black pants and a white t-shirt is riding along the top of the wall with his skateboard .
>
> **Caption B:** The skateboarder is balancing himself and his skateboard on the edge of a brick wall .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** black-white
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second skater's clothes have no supplied colors.

**Audit explanation:** The second skateboarder's clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 856. train_9963: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a snowboarder is performing a jump whilst riding on a pink snowboard .
>
> **Caption B:** A snowboarder is standing on top of a platform in the snow .
>
> **Adopted scope:** board color
>
> **Extracted A:** pink
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second snowboard color is unstated.

**Audit explanation:** The second snowboard's color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 857. train_9977: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A small dog runs in a field , with a toy in its mouth .
>
> **Caption B:** A brown dog walks in the grass with its tongue hanging out .
>
> **Adopted scope:** animal color
>
> **Extracted A:** unstated
>
> **Extracted B:** brown
>
> **Recorded reason, verbatim:** The first dog's coat color is missing.

**Audit explanation:** The first dog's coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 858. train_10010: `position of vehicle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person rides their bicycle onto a rock and balances on one wheel .
>
> **Caption B:** The boy on the bike is wearing safety glasses and a helmet .
>
> **Adopted scope:** vehicle position
>
> **Extracted A:** balanced on one wheel on rock
>
> **Extracted B:** under rider, orientation unstated
>
> **Recorded reason, verbatim:** Being on a bike does not specify the second vehicle's orientation.

**Audit explanation:** The second boy's position on a bike leaves the vehicle's orientation unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 859. train_10022: `action of dogs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Three small dogs , two white and one black and white , on a sidewalk .
>
> **Caption B:** A white dog is walking through the leafy grass while a brown dog is about to bite it .
>
> **Adopted scope:** dog action
>
> **Extracted A:** on sidewalk, action unspecified
>
> **Extracted B:** walking and preparing to bite
>
> **Recorded reason, verbatim:** A sidewalk location does not establish the first dogs' action.

**Audit explanation:** The first dogs' sidewalk location leaves current action unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 860. train_10035: `ball position`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A baseball player is mid-swing , while the catcher behind him hold out his glove .
>
> **Caption B:** A baseball pitcher in white uniform winds up for a pitch .
>
> **Adopted scope:** ball position
>
> **Extracted A:** unstated during swing
>
> **Extracted B:** pitcher's hand during windup
>
> **Recorded reason, verbatim:** A batter's mid-swing pose does not locate the first ball.

**Audit explanation:** The first batter's mid-swing pose leaves ball position unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 861. train_10052: `presence of observers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cowboy in a rodeo trying to beat the 8 second clock .
>
> **Caption B:** A cowboy holds on to a brown stallion during a rodeo as bystanders watch .
>
> **Adopted scope:** observer presence
>
> **Extracted A:** unstated
>
> **Extracted B:** bystanders watching
>
> **Recorded reason, verbatim:** A rodeo alone does not establish explicit observers or their absence.

**Audit explanation:** Observer presence remains unknown in the first rodeo scene.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 862. train_10096: `nature of skating surface`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Person doing a trick on a skateboard in a skate park while people watch .
>
> **Caption B:** Skateboarder on a ramp as seen through a chain link fence .
>
> **Adopted scope:** skating surface nature
>
> **Extracted A:** surface unspecified within skate park
>
> **Extracted B:** ramp
>
> **Recorded reason, verbatim:** Skate park names a venue but supplies neither surface material nor shape; second specifies a ramp.

**Audit explanation:** The first skate park names a venue, leaving skating surface shape and material unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 863. train_10103: `presence of observers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man wades in the water and watches a waterfall .
>
> **Caption B:** A waterfall splashes into a pool at the bottom of a steep grassy hill .
>
> **Adopted scope:** observer presence
>
> **Extracted A:** man watching
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second waterfall scene does not establish observer absence.

**Audit explanation:** Observer presence remains unknown in the second waterfall scene.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 864. train_10121: `presence of green shoes`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A little kid jumps up into the air above the ocean .
>
> **Caption B:** A child hold green shoes is walking in the sand by the water .
>
> **Adopted scope:** green shoe presence
>
> **Extracted A:** unstated
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** The jumping child has no footwear information.

**Audit explanation:** The first jumping child's footwear and green-shoe presence remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 865. train_10135: `intensity of activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A small child wades through the water while being guided by another person .
>
> **Caption B:** Colorful rings spraying water at little girl wearing swimsuit .
>
> **Adopted scope:** activity intensity
>
> **Extracted A:** gentle guided wading
>
> **Extracted B:** sprinkler exposure, intensity unstated
>
> **Recorded reason, verbatim:** Water spraying a girl does not establish her activity's intensity.

**Audit explanation:** The second girl's sprinkler exposure leaves her own activity intensity unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 866. train_10173: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The dog is jumping over the hurdles beside a woman .
>
> **Caption B:** A black dog jumps in the air over the red hurdle .
>
> **Adopted scope:** animal color
>
> **Extracted A:** unstated
>
> **Extracted B:** black
>
> **Recorded reason, verbatim:** The first dog's color is missing.

**Audit explanation:** The first dog's coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 867. train_10221: `surface type`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Several bikers on a stone road , with spectators watching .
>
> **Caption B:** There is a bicycle race with a few people watching .
>
> **Adopted scope:** surface type
>
> **Extracted A:** stone road
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** A bicycle race alone does not identify road surface material.

**Audit explanation:** The second bicycle race leaves surface material unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 868. train_10247: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Many people in orange jackets are working in the subway station .
>
> **Caption B:** Electrical workers inspect underground power cables .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** orange
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second workers' clothing colors are unavailable.

**Audit explanation:** The second electrical workers' clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `1.0`.

### 869. train_10253: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person wearing beige snow clothes is flying in the air on a snowboard .
>
> **Caption B:** A snowboarder flies through the air on a red snowboard in front of a snowy landscape .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** beige
>
> **Extracted B:** unstated; board red
>
> **Recorded reason, verbatim:** A red board does not identify the snowboarder's clothing color.

**Audit explanation:** The second snowboarder's clothing colors remain unspecified. Red describes the board.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 870. train_10272: `color of hair`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man with graying hair and beard is playing with a child in a red top .
>
> **Caption B:** A grown man is using the vacuum next to a little boy with a pretend vacuum .
>
> **Adopted scope:** adult hair color
>
> **Extracted A:** graying
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The second adult's hair color is missing.

**Audit explanation:** The second adult's hair color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 871. train_10296: `color of wetsuit`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a blue wetsuit standing on a blue surfboard in front of a small wave in the ocean .
>
> **Caption B:** A person is being pulled by watercraft across the gleaming water .
>
> **Adopted scope:** wetsuit color
>
> **Extracted A:** blue
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** The towed person's wetsuit and its color are not established.

**Audit explanation:** The second towed person's wetsuit and its color remain unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 872. train_10306: `presence of engine`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person is surfing on a wave while another person heads towards it .
>
> **Caption B:** A surfer catches a wave as a man on a jet ski looks on in case of an accident .
>
> **Adopted scope:** engine presence
>
> **Extracted A:** unstated
>
> **Extracted B:** jet-ski engine inferred
>
> **Recorded reason, verbatim:** Surfing alone does not establish engine absence from the scene.

**Audit explanation:** Engine presence remains unknown in the first surfing scene.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 873. train_10325: `presence of leopard`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S1, S3`.

> **Caption A:** A girl with leopard knee crouches while rollerskating down the track .
>
> **Caption B:** Women in roller derby are in the middle of a bout .
>
> **Adopted scope:** leopard presence
>
> **Extracted A:** leopard-pattern knee item, actual animal absent
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Leopard pattern does not establish a real leopard, and second presence is unmentioned.

**Audit explanation:** The first leopard-pattern knee item represents an animal. Actual leopard presence remains unestablished in both scenes.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 874. train_10351: `orientation of skateboard`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Young skateboarding boy flips his board while performing a stunt .
>
> **Caption B:** A boy does a skateboard jump at a skateboard park .
>
> **Adopted scope:** board orientation
>
> **Extracted A:** flipping
>
> **Extracted B:** jumping, orientation unspecified
>
> **Recorded reason, verbatim:** A jump alone does not establish skateboard orientation.

**Audit explanation:** The second skateboard jump leaves board orientation unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 875. train_10355: `color of surfboard`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A child in orange is on a boogie board in the waves .
>
> **Caption B:** Young man rides ocean wave on yellow surfboard .
>
> **Adopted scope:** board color
>
> **Extracted A:** unstated; child orange
>
> **Extracted B:** yellow
>
> **Recorded reason, verbatim:** Orange describes the child's clothes, not the board.

**Audit explanation:** The first board's color remains unspecified. Orange describes the child.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 876. train_10441: `absence of protective vest`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cowboy in the rodeo arena holds on tightly as the bucking bronco tries to throw him off , while rodeo helpers and the audience look on .
>
> **Caption B:** A man in a protective vest and caged hockey mask holds on to a brown horse and it jumps and bucks at a rodeo .
>
> **Adopted scope:** absence of protective vest
>
> **Extracted A:** vest status unstated
>
> **Extracted B:** protective vest present
>
> **Recorded reason, verbatim:** No vest mention does not establish that the first rider lacks one.

**Audit explanation:** The first rodeo rider's protective-vest status remains unknown.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 877. train_10461: `animal's gait`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a brown dog coming out of an orange and yellow tunnel
>
> **Caption B:** A brown dog walks in the grass with its tongue hanging out .
>
> **Adopted scope:** dog gait
>
> **Extracted A:** coming out, gait unspecified
>
> **Extracted B:** walking
>
> **Recorded reason, verbatim:** Coming out of a tunnel does not identify walking, running or another gait.

**Audit explanation:** The first dog's exit from a tunnel leaves gait unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 878. train_10476: `breed of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black dog with a red collar plays in the snow .
>
> **Caption B:** A brown dog walking on a snowy surface near snow covered trees .
>
> **Adopted scope:** dog breed
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Colors and snowy location do not identify breeds.

**Audit explanation:** Both dogs' coat colors and snowy locations leave breed unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 879. train_10489: `time of day`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A worker makes repairs in the wheel of a bulldozer during winter .
>
> **Caption B:** A roadwork crew is resurfacing a road at night , wearing high-visibility clothing .
>
> **Adopted scope:** time of day
>
> **Extracted A:** unspecified; winter only
>
> **Extracted B:** night
>
> **Recorded reason, verbatim:** Winter identifies a season, not time of day.

**Audit explanation:** The first repair scene's winter leaves time of day unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 880. train_10524: `existence of cows`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Isuzu truck driving by while a man with some cows drive the opposite way .
>
> **Caption B:** A woman in a colorful outfit is walking by a white truck filled with bottles .
>
> **Adopted scope:** cows present
>
> **Extracted A:** cows described
>
> **Extracted B:** cow presence unspecified
>
> **Recorded reason, verbatim:** A truck full of bottles does not establish cow absence elsewhere.

**Audit explanation:** Cow presence remains unknown in the second bottle-truck scene.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 881. train_10543: `vocal activity`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A little girl in jeans and a blue striped shirt is swinging on the swing with her hands out .
>
> **Caption B:** A girl sings on the swing set in the park , behind the leaves of the tree .
>
> **Adopted scope:** vocal activity
>
> **Extracted A:** unspecified
>
> **Extracted B:** singing
>
> **Recorded reason, verbatim:** Swinging alone does not establish any vocal activity.

**Audit explanation:** The first girl's swinging leaves vocal activity unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 882. train_10550: `age of performers`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A child sleds over a mound of snow as others watch him .
>
> **Caption B:** Skier on a snowy hill has his boots check by a red-vested man
>
> **Adopted scope:** principal performer age
>
> **Extracted A:** child
>
> **Extracted B:** skier age unspecified
>
> **Recorded reason, verbatim:** The second athlete's age is unknown; the assistant's adulthood does not supply it.

**Audit explanation:** The second skier's age remains unspecified. The assistant's adulthood describes a separate person.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 883. train_10591: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** someone working in a restaurant that has dishes set out like a buffet .
>
> **Caption B:** A man , wearing a green shirt , is cooking food in a restaurant .
>
> **Adopted scope:** worker clothing color
>
> **Extracted A:** unspecified
>
> **Extracted B:** green
>
> **Recorded reason, verbatim:** The first restaurant worker's clothing color is unspecified.

**Audit explanation:** The first restaurant worker's clothing color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 884. train_10606: `attire of person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man is riding a board in the ocean and is being pulled from above .
>
> **Caption B:** Topless person surfing , shot captured in midair .
>
> **Adopted scope:** person attire
>
> **Extracted A:** unspecified
>
> **Extracted B:** topless
>
> **Recorded reason, verbatim:** The first person's clothing/torso covering is unstated.

**Audit explanation:** The first ocean rider's clothing and torso covering remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 885. train_10609: `location of action`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A skateboarder jumps off his skateboard in midair in hopes of landing back on it .
>
> **Caption B:** A skateboarder is doing a kick flip across a concrete gap .
>
> **Adopted scope:** action location
>
> **Extracted A:** surrounding location unstated beyond midair
>
> **Extracted B:** concrete gap
>
> **Recorded reason, verbatim:** Midair gives elevation without identifying the first surrounding venue or ground feature.

**Audit explanation:** The first skateboarder's airborne position leaves surrounding venue or ground feature unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 886. train_10638: `proximity to trees`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young man is airborne as he goes over a bike dirt track .
>
> **Caption B:** A boy on his bike leaping over a hill with trees in the background .
>
> **Adopted scope:** proximity to trees
>
> **Extracted A:** trees not described
>
> **Extracted B:** trees behind rider
>
> **Recorded reason, verbatim:** The first scene gives no trees or tree-distance information.

**Audit explanation:** The first dirt-track scene leaves trees and tree proximity unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 887. train_10659: `player's attitude`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Woman tennis player wearing a light blue tennis outfit winds up to hit the tennis ball as the crowd watches .
>
> **Caption B:** The tennis player is enjoying her game while the crowd watch her every move .
>
> **Adopted scope:** player attitude
>
> **Extracted A:** unspecified
>
> **Extracted B:** enjoying game
>
> **Recorded reason, verbatim:** A tennis windup does not establish the first player's attitude.

**Audit explanation:** The first tennis player's windup leaves attitude unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 888. train_10665: `colors around person`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A blond woman playing tennis , in front of a blue advertising background .
>
> **Caption B:** woman tennis player in a green and red dress balancing a ball on the racket .
>
> **Adopted scope:** colors around person
>
> **Extracted A:** blue advertising backdrop
>
> **Extracted B:** surrounding colors unspecified; dress green and red
>
> **Recorded reason, verbatim:** Dress colors do not establish colors in the second person's surroundings.

**Audit explanation:** The second person's surrounding colors remain unspecified. Green and red describe the dress.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 889. train_10667: `color of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A rodeo man is roping a calf during a competition .
>
> **Caption B:** Little cowboy , waiting to ride a large , beauty brown and white bull .
>
> **Adopted scope:** animal color
>
> **Extracted A:** calf color unspecified
>
> **Extracted B:** brown and white
>
> **Recorded reason, verbatim:** The first calf's color is missing.

**Audit explanation:** The first calf's coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 890. train_10671: `species of animals`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two dogs are running and barking at each other .
>
> **Caption B:** A black animal and a white animal in motion in close quarters .
>
> **Adopted scope:** animal species
>
> **Extracted A:** dogs
>
> **Extracted B:** species unspecified
>
> **Recorded reason, verbatim:** Black and white animals have no identified species.

**Audit explanation:** The second black and white animals' species remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 891. train_10673: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young skateboarder is grinding on a rusty rail at night .
>
> **Caption B:** An action shot of a kid in green performing a skateboard trick off some steps .
>
> **Adopted scope:** principal board or obstacle color
>
> **Extracted A:** rust-colored rail; board unstated
>
> **Extracted B:** object colors unstated; clothing green
>
> **Recorded reason, verbatim:** Second clothing green does not supply board or obstacle color.

**Audit explanation:** The second board and obstacle colors remain unspecified. Green describes the child.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 892. train_10677: `color of players`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in blue competes against a man in white during a taekwondo match .
>
> **Caption B:** Two competitors compete at a martial arts tournament .
>
> **Adopted scope:** players clothing colors
>
> **Extracted A:** blue and white
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second competitors' outfits have no colors supplied.

**Audit explanation:** The second martial-arts competitors' clothing colors remain unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 893. train_10716: `speed of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The young man is performing a summersault in the air with a bicycle .
>
> **Caption B:** A cyclist is performing a jumping stunt in a skate and cycle park .
>
> **Adopted scope:** cyclist speed
>
> **Extracted A:** unspecified during aerial stunt
>
> **Extracted B:** unspecified during jump
>
> **Recorded reason, verbatim:** Aerial maneuvers do not establish either rider's speed.

**Audit explanation:** Both cyclists' aerial maneuvers leave speed unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 894. train_10717: `rotation of body`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** The young man is performing a summersault in the air with a bicycle .
>
> **Caption B:** A cyclist is performing a jumping stunt in a skate and cycle park .
>
> **Adopted scope:** body rotation
>
> **Extracted A:** somersault
>
> **Extracted B:** rotation unspecified
>
> **Recorded reason, verbatim:** An unspecified jumping stunt does not establish body rotation.

**Audit explanation:** The second unspecified bicycle jump leaves body rotation unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 895. train_10722: `type of martial art`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two black belt experts demonstrating karate moves .
>
> **Caption B:** Martial artists are sparring against one another .
>
> **Adopted scope:** martial art type
>
> **Extracted A:** karate
>
> **Extracted B:** unspecified martial art
>
> **Recorded reason, verbatim:** Generic martial arts does not identify a martial-art discipline.

**Audit explanation:** The second generic martial artists' sparring leaves discipline unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 896. train_10724: `type of martial arts`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** 4 children - who appear to be about 10-11 years old - are practicing judo .
>
> **Caption B:** People in white martial arts outfits are doing stretches .
>
> **Adopted scope:** martial art type
>
> **Extracted A:** judo
>
> **Extracted B:** unspecified martial art
>
> **Recorded reason, verbatim:** Martial-arts clothing does not identify which discipline the second people practice.

**Audit explanation:** The second white martial-arts outfits leave discipline unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 897. train_10771: `condition of field`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A large brown dog with a muzzle is racing in the mud .
>
> **Caption B:** A muzzled greyhound dog is running around a track .
>
> **Adopted scope:** field condition
>
> **Extracted A:** muddy
>
> **Extracted B:** track condition unspecified
>
> **Recorded reason, verbatim:** The second track's wetness/surface condition is unspecified.

**Audit explanation:** The second generic track leaves wetness and surface condition unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 898. train_10779: `setting of event`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A skateboarder getting ready to perform on a half-tube rink where there are trees in the background .
>
> **Caption B:** One man in a red sweatshirt skateboarding while a man in a blue sweatshirt films him .
>
> **Adopted scope:** event setting
>
> **Extracted A:** half-pipe rink with trees
>
> **Extracted B:** setting unspecified
>
> **Recorded reason, verbatim:** Filming a skater does not locate the second event.

**Audit explanation:** The second skateboarder's filming leaves event setting unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 899. train_10810: `nature of place`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A skateboarder in the air straddling his upside-down skateboard .
>
> **Caption B:** A skateboarder is does an " ollie " down a couple of stairs .
>
> **Adopted scope:** place type
>
> **Extracted A:** unspecified airborne setting
>
> **Extracted B:** stairs
>
> **Recorded reason, verbatim:** Airborne posture does not identify the first place type.

**Audit explanation:** The first skateboarder's airborne posture leaves place type unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 900. train_10811: `profession of persons`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A skateboarder in the air straddling his upside-down skateboard .
>
> **Caption B:** A skateboarder is does an " ollie " down a couple of stairs .
>
> **Adopted scope:** profession
>
> **Extracted A:** unspecified; skateboarding activity
>
> **Extracted B:** unspecified; skateboarding activity
>
> **Recorded reason, verbatim:** Skateboarding does not establish paid professional occupation.

**Audit explanation:** Both skateboarding activities leave paid profession unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `5.0`.

### 901. train_10838: `movement of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** People stand in front of artwork on the streets of an Asian city .
>
> **Caption B:** Two women look at a large display of Asian figures and buildings .
>
> **Adopted scope:** people movement
>
> **Extracted A:** standing
>
> **Extracted B:** looking, locomotion unstated
>
> **Recorded reason, verbatim:** Looking at a display does not establish the second people's locomotion.

**Audit explanation:** The second women's display viewing leaves locomotion unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 902. train_10861: `speed of children`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two girls are playing soccer with orange and white uniforms .
>
> **Caption B:** The children are running through the grass playing soccer .
>
> **Adopted scope:** children speed
>
> **Extracted A:** unspecified while playing soccer
>
> **Extracted B:** running
>
> **Recorded reason, verbatim:** Playing soccer does not establish a current movement speed.

**Audit explanation:** The first children's generic soccer play leaves current movement speed unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 903. train_10885: `type of riding surface`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man on a motorized bike rides across a dirt road .
>
> **Caption B:** A person on a dirt bike soaring through the air sideways .
>
> **Adopted scope:** riding surface type
>
> **Extracted A:** dirt road
>
> **Extracted B:** surface not identified during airborne riding
>
> **Recorded reason, verbatim:** Being airborne supplies no type of underlying or contacted riding surface.

**Audit explanation:** The second dirt bike's airborne position leaves the underlying or contacted riding surface unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 904. train_10887: `number of punches thrown`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two boxers fight in a well-lit ring surrounded by poorly-lit seating .
>
> **Caption B:** Two boxers are fighting , one is punching the other .
>
> **Adopted scope:** punches thrown count
>
> **Extracted A:** unspecified
>
> **Extracted B:** one described punch
>
> **Recorded reason, verbatim:** A generic fight supplies no number of punches.

**Audit explanation:** The first generic boxing fight leaves punch count unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 905. train_10935: `presence of foliage`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** a long city street surrounded by large buildings
>
> **Caption B:** There are trees outside of a building in the middle of downtown .
>
> **Adopted scope:** foliage presence
>
> **Extracted A:** unspecified
>
> **Extracted B:** trees present
>
> **Recorded reason, verbatim:** Large buildings do not establish foliage absence.

**Audit explanation:** Foliage presence remains unknown along the first building-lined street.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 906. train_10957: `skill level`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A cowboy riding a bucking white , black and brown horse .
>
> **Caption B:** A cowboy leans back as he tries to avoid being thrown by the bucking bronco .
>
> **Adopted scope:** skill level
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Riding or struggling with a bucking horse does not establish a skill level.

**Audit explanation:** Both bucking-horse activities leave rider skill level unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 907. train_10961: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** White man in a black suit is crossing a busy street .
>
> **Caption B:** A man in business attire stands a street corner .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** black suit
>
> **Extracted B:** business attire, color unstated
>
> **Recorded reason, verbatim:** Business attire does not determine its color.

**Audit explanation:** The second business attire leaves clothing color unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 908. train_10969: `color of object`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young man in a green t-shirt is stirring ingredients in a kitchen .
>
> **Caption B:** A young boy holds a blue sponge in his left hand and runs water into a soapy pan .
>
> **Adopted scope:** principal handled object color
>
> **Extracted A:** ingredients or mixing tool color unstated
>
> **Extracted B:** blue sponge
>
> **Recorded reason, verbatim:** Green shirt color does not identify the first handled objects' colors.

**Audit explanation:** The first handled ingredients and tool have unspecified colors. Green describes the shirt.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 909. train_11000: `size of dog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A black and white dog is playing with a ball on a lawn .
>
> **Caption B:** A small dog jumping an obstacle in a grassy field .
>
> **Adopted scope:** dog size
>
> **Extracted A:** unspecified
>
> **Extracted B:** small
>
> **Recorded reason, verbatim:** The first dog's color and ball play give no size.

**Audit explanation:** The first dog's coat colors and ball play leave body size unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 910. train_11033: `color of clothing`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A young man in a black shirt and brown pants is skateboarding .
>
> **Caption B:** A skateboarder slides down a stair rail in the dark .
>
> **Adopted scope:** clothing colors
>
> **Extracted A:** black and brown
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Darkness does not establish the second clothing's colors.

**Audit explanation:** The second skateboarder's clothing colors remain unspecified despite darkness.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 911. train_11043: `presence of ball`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Men playing a sports game with two men in white on top of a man in black .
>
> **Caption B:** Two soccer players from opposing teams trying to get control of the ball before the other player does .
>
> **Adopted scope:** ball presence
>
> **Extracted A:** unspecified sports game
>
> **Extracted B:** ball explicitly present
>
> **Recorded reason, verbatim:** An unspecified sports scrum could occur without a ball; presence is not established.

**Audit explanation:** The first unnamed sports game leaves ball presence unestablished.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 912. train_11067: `place of fighting`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A female martial artist kicking another female martial artist in the face
>
> **Caption B:** Two fighters are sparring in a gym full of onlookers .
>
> **Adopted scope:** fighting place
>
> **Extracted A:** unspecified
>
> **Extracted B:** gym
>
> **Recorded reason, verbatim:** The first fight has no venue information.

**Audit explanation:** The first martial-arts fight leaves venue unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 913. train_11084: `size of dog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A little tan dog with large ears running through the grass .
>
> **Caption B:** A brown dog is carrying a stick too big for him over grass .
>
> **Adopted scope:** dog size
>
> **Extracted A:** little
>
> **Extracted B:** body size unspecified relative to oversized stick
>
> **Recorded reason, verbatim:** An oversized stick does not establish the dog's absolute body size.

**Audit explanation:** The stick's size is relative to the dog. The dog's absolute body size remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 914. train_11131: `color of bicycle`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person riding a bicycle travels down an overgrown hill .
>
> **Caption B:** A young male on a black and red bicycle is riding across a mountainous terrain .
>
> **Adopted scope:** bicycle color
>
> **Extracted A:** unspecified
>
> **Extracted B:** black and red
>
> **Recorded reason, verbatim:** The first bicycle's color is missing.

**Audit explanation:** The first bicycle's color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 915. train_11139: `color of ball`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A boy holds a basketball during a game , while others watch .
>
> **Caption B:** A young boy in a red jersey jumps , about to throw a basketball in front of a crowd .
>
> **Adopted scope:** ball color
>
> **Extracted A:** unspecified
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** Neither basketball color is supplied; jersey red is unrelated.

**Audit explanation:** Both basketballs' colors remain unspecified. Red describes the second jersey.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 916. train_11143: `level of protection worn`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A boy in jeans , a helmet , and red shoes goes rock climbing indoors .
>
> **Caption B:** A small boy in shorts and a red shirt , airborne on an inflatable slide .
>
> **Adopted scope:** protective equipment level
>
> **Extracted A:** helmet
>
> **Extracted B:** protection unspecified
>
> **Recorded reason, verbatim:** Ordinary clothes do not establish absence of protective gear.

**Audit explanation:** The second ordinary clothes leave protective-equipment level unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 917. train_11149: `color of uniform`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Little boys in red and blue uniforms playing soccer at the park .
>
> **Caption B:** A young boy in a soccer uniform prepares to kick a soccer ball .
>
> **Adopted scope:** uniform color
>
> **Extracted A:** red and blue
>
> **Extracted B:** unspecified
>
> **Recorded reason, verbatim:** The second soccer uniform has no stated color.

**Audit explanation:** The second soccer uniform's color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 918. train_11159: `presence of yellow rods`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A girl in a pink shirt playing with a green ball .
>
> **Caption B:** A little girl in pink clothes holding yellow rods .
>
> **Adopted scope:** yellow rods presence
>
> **Extracted A:** unspecified
>
> **Extracted B:** present
>
> **Recorded reason, verbatim:** Playing with a green ball does not establish yellow rods absent.

**Audit explanation:** Yellow-rod presence remains unknown during the first girl's green-ball play.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 919. train_11199: `color of clothes`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Four men wearing T-shirts and playing musical instruments perform in a band .
>
> **Caption B:** A man in a plaid shirt is singing and playing the guitar .
>
> **Adopted scope:** clothing color
>
> **Extracted A:** unspecified T-shirts
>
> **Extracted B:** plaid pattern, colors unstated
>
> **Recorded reason, verbatim:** T-shirt and plaid descriptions do not supply comparable hues.

**Audit explanation:** Both T-shirt and plaid descriptions leave comparable clothing hues unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 920. train_11200: `purpose of participating in sport`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A snow border jumping up a half pipe doing a trick .
>
> **Caption B:** A teen performing a bike trick at a skate park .
>
> **Adopted scope:** purpose of sport participation
>
> **Extracted A:** motivation unspecified
>
> **Extracted B:** motivation unspecified
>
> **Recorded reason, verbatim:** Performing tricks alone does not identify a motivation for sport participation.

**Audit explanation:** Both athletes' tricks leave their motives for sport participation unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `4.0`.

### 921. train_11207: `height of animal`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A furry white dog is carrying a stick in its mouth through the grass .
>
> **Caption B:** A dog jumping up in the air next to a white house .
>
> **Adopted scope:** animal body stature under unqualified height of animal
>
> **Extracted A:** body height unstated
>
> **Extracted B:** body height unstated
>
> **Recorded reason, verbatim:** The unqualified height-of-animal condition follows the frozen height-of-man stature convention. Neither caption describes the dog's body height. Grounded versus airborne is a supported elevation comparison, but substituting height above ground would change the adopted feature scope.

**Audit explanation:** Both dogs' body statures remain unspecified under the recorded height scope. Jumping describes elevation.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 922. train_11208: `sentiment of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** People are having fun they are on the beach swimming
>
> **Caption B:** The man tossed a child into the swimming pool near the ocean .
>
> **Adopted scope:** people sentiment
>
> **Extracted A:** having fun
>
> **Extracted B:** sentiment unstated during toss
>
> **Recorded reason, verbatim:** Tossing a child into water does not by itself establish either person's sentiment.

**Audit explanation:** The second child's water toss leaves both people's feelings unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 923. train_11221: `sentiment of people`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two Chinese guys sitting in a Chinese restaurant .
>
> **Caption B:** Two asian chefs cooking with white suits and hats .
>
> **Adopted scope:** people sentiment
>
> **Extracted A:** unstated
>
> **Extracted B:** unstated
>
> **Recorded reason, verbatim:** Restaurant location and cooking supply no emotional states.

**Audit explanation:** Both restaurant scenes leave participants' sentiment unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 924. train_11261: `emotional display`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman laughing and having fun at a bowling alley .
>
> **Caption B:** A woman is watching her bowling ball roll down the lane towards the pins .
>
> **Adopted scope:** emotional display
>
> **Extracted A:** laughing and enjoyment
>
> **Extracted B:** emotion unstated
>
> **Recorded reason, verbatim:** Watching a ball does not establish the second woman's emotion.

**Audit explanation:** The second woman's bowling-ball watching leaves emotional display unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 925. train_11265: `intention of traveler`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A man in a blue shirt hikes through a nature trail .
>
> **Caption B:** A person carrying leaves and grass is walking down a path .
>
> **Adopted scope:** traveler intention
>
> **Extracted A:** hiking
>
> **Extracted B:** carrying vegetation, purpose unspecified
>
> **Recorded reason, verbatim:** Carrying vegetation while walking does not establish the traveler's purpose.

**Audit explanation:** The second traveler's vegetation and walking leave journey purpose unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 926. train_11272: `type of experiment`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A woman with brown hair is doing a science experiment while wearing goggles and a blue shirt .
>
> **Caption B:** A girl is working on some sort of lab experiment while another girl watches with a bored expression .
>
> **Adopted scope:** experiment type
>
> **Extracted A:** science experiment, specialty unspecified
>
> **Extracted B:** lab experiment, specialty unspecified
>
> **Recorded reason, verbatim:** Neither science or lab wording identifies the requested experiment type or specialty.

**Audit explanation:** Both generic science and lab experiments leave experimental type or specialty unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 927. train_11278: `age of dogs`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** Two small dogs follow a larger dog with a tennis ball
>
> **Caption B:** Three small puppies bite and play together in the grass .
>
> **Adopted scope:** dog age
>
> **Extracted A:** size specified but age unstated
>
> **Extracted B:** puppies
>
> **Recorded reason, verbatim:** Small/large dog sizes do not establish ages.

**Audit explanation:** The first dogs' small and large sizes leave ages unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `2.0`.

### 928. train_11290: `color of terrain`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A person parachuting down the site of a snow covered mountain .
>
> **Caption B:** A man with ice-climbing gear climbs on a sheet of ice .
>
> **Adopted scope:** terrain color
>
> **Extracted A:** snow, ordinarily white
>
> **Extracted B:** ice, precise appearance unspecified
>
> **Recorded reason, verbatim:** Ice alone does not establish a terrain hue; clear, white and bluish appearances are not a stated value.

**Audit explanation:** The second ice leaves terrain hue unspecified. The first snow supplies ordinary white coloring.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.

### 929. train_11303: `color of dog`

**Current status:** `invalid`. **Semantic rating:** `excluded/null`. **Policy:** `S3`.

> **Caption A:** A dog chases a stuffed animal attached to a string .
>
> **Caption B:** a brown and white dog chasing a ball on some grass .
>
> **Adopted scope:** dog color
>
> **Extracted A:** unspecified
>
> **Extracted B:** brown and white
>
> **Recorded reason, verbatim:** The first dog's coat color is missing.

**Audit explanation:** The first dog's coat color remains unspecified.

**Policy check:** Policy consistent. **Peer:** `writer_a`.

**History:** supplied source rating `3.0`.
