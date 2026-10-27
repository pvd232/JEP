# Questions for adjudication

**Dataset:** [JEP C-STS revision 1](README.md). The 13 questions below preserve the published labels pending your decisions. Refer to each case by its source ID.

| ID | Split | Supplied score | V1 audited score | Condition | Question |
|---|---|---|---|---|---|
| `train_205` | training | 3/5 | excluded/null | color of product | Should product color cover the named chair and cabinet or the computers? |
| `train_688` | training | 4/5 | excluded/null | objects near device | Should the described speakers count under the recorded electronic-device scope? |
| `train_689` | training | 4/5 | excluded/null | type of device | Which electronic-device type should the described speakers supply? |
| `train_778` | training | 5/5 | excluded/null | type of animal | Should the condition include the animal represented by the teddy bear? |
| `train_779` | training | 1/5 | excluded/null | number of animals | Should the recorded bear-figure count include teddy bears? |
| `train_2038` | validation | 4/5 | excluded/null | type of area involved | Does B’s computer workspace supply partial room-function information under the approved computer-context convention? |
| `train_8568` | validation | 3/5 | excluded/null | location | Should generic location include B’s explicit airborne position, or does the condition require surrounding venue or ground features? |
| `train_10241` | validation | 2/5 | excluded/null | position of person | Does ordinary ground-supported skateboarding provide a comparable position, as allowed in the training audit, or is explicit posture required? |
| `train_11335` | validation | 4/5 | excluded/null | woman stance | Do riding and balancing supply partial stance information, or must seated versus standing be explicitly recoverable? |
| `train_11341` | validation | 3/5 | excluded/null | means of flotation | Can the man’s stated assistance supply a partial flotation means, or must the physical buoyancy mechanism be identified? |
| `evaluation_855` | test | -1 (source invalid marker) | excluded/null | number of pizza slices | A leaves slicing state unspecified. Should Extracted A describe only the unstated slice count? |
| `evaluation_1884` | test | 5/5 | excluded/null | height of animal | Should the stature reading follow frozen train_11207, or should stature and jump elevation remain competing features? |
| `evaluation_2450` | test | 1/5 | excluded/null | color of animals | Does the stated three-color coat supply partial color information under the colorful convention accepted for train_10852? |

### train_205: `color of product`

**Supplied similarity score:** `3/5`. **V1 audited score:** `excluded/null`.

**Current status:** `invalid`. **Check:** Review exclusion policy.

> **Caption A:** A desk has a black chair near it and a monitor and laptop on it.
>
> **Caption B:** a work space office with a desktop and chair and a blue file cabinet
>
> **Adopted scope:** product color
>
> **Extracted A:** black chair; electronics unspecified
>
> **Extracted B:** blue file cabinet

**Audit explanation:** The recorded exclusion restricts products to computers. The broader product-color scope also includes A's black chair and B's blue cabinet. Scope requires review.

**Peer:** `writer_b`.

**Decision needed:** Should product color cover the named chair and cabinet or the computers?

### train_688: `objects near device`

**Supplied similarity score:** `4/5`. **V1 audited score:** `excluded/null`.

**Current status:** `invalid`. **Check:** Review exclusion policy.

> **Caption A:** A big monitor on a white desk with a white mouse and a glass on the desk.
>
> **Caption B:** The computer desk is next to a shelf with speakers and books on it.
>
> **Adopted scope:** items near an established electronic device
>
> **Extracted A:** mouse and glass near monitor
>
> **Extracted B:** speakers and books near computer desk; device not described

**Audit explanation:** The recorded exclusion treats B's device as missing. B explicitly includes speakers, creating a conflict with the electronic-device scope that requires review.

**Peer:** `writer_b`.

**Decision needed:** Should the described speakers count under the recorded electronic-device scope?

### train_689: `type of device`

**Supplied similarity score:** `4/5`. **V1 audited score:** `excluded/null`.

**Current status:** `invalid`. **Check:** Review exclusion policy.

> **Caption A:** A big monitor on a white desk with a white mouse and a glass on the desk.
>
> **Caption B:** The computer desk is next to a shelf with speakers and books on it.
>
> **Adopted scope:** electronic device type
>
> **Extracted A:** monitor
>
> **Extracted B:** device unspecified; computer desk described

**Audit explanation:** The recorded exclusion treats B's device type as missing. B explicitly identifies speakers, creating an electronic-device scope conflict that requires review.

**Peer:** `writer_b`.

**Decision needed:** Which electronic-device type should the described speakers supply?

### train_778: `type of animal`

**Supplied similarity score:** `5/5`. **V1 audited score:** `excluded/null`.

**Current status:** `invalid`. **Check:** Review exclusion policy.

> **Caption A:** Four teddy bears from font sitting on ledge with patchwork grass of countryside behind them, and blue sky with clouds.
>
> **Caption B:** An old teddy bear left out on the ledge of a little stone wall
>
> **Adopted scope:** represented animal type
>
> **Extracted A:** teddy bears
>
> **Extracted B:** teddy bear

**Audit explanation:** The recorded exclusion applies actual-animal eligibility. Both captions identify toy bears under the recorded represented-animal scope. That scope conflict requires review.

**Peer:** `writer_b`.

**Decision needed:** Should the condition include the animal represented by the teddy bear?

### train_779: `number of animals`

**Supplied similarity score:** `1/5`. **V1 audited score:** `excluded/null`.

**Current status:** `invalid`. **Check:** Review exclusion policy.

> **Caption A:** Four teddy bears from font sitting on ledge with patchwork grass of countryside behind them, and blue sky with clouds.
>
> **Caption B:** An old teddy bear left out on the ledge of a little stone wall
>
> **Adopted scope:** bear-figure count
>
> **Extracted A:** four
>
> **Extracted B:** one

**Audit explanation:** The recorded exclusion applies actual-animal eligibility. The recorded bear-figure scope supplies four versus one. That scope conflict requires review.

**Peer:** `writer_b`.

**Decision needed:** Should the recorded bear-figure count include teddy bears?

### train_2038: `type of area involved`

**Supplied similarity score:** `4/5`. **V1 audited score:** `excluded/null`.

**Current status:** `invalid`. **Check:** Review exclusion policy.

> **Caption A:** White vertical blinds hang in the windows of a white room with wood flooring, with a bed, a lamp, and a bookshelf with a small television on top of it.
>
> **Caption B:** A room with two pictures on the wall and a table with a computer monitor on it.  A wooden floor and a table with a yellow bowl and a grey and white rug.
>
> **Adopted scope:** room type
>
> **Extracted A:** bedroom
>
> **Extracted B:** room with tables and computer, function unspecified

**Audit explanation:** B's computer workspace supplies partial room-function information under the approved computer-context rule. The current exclusion therefore needs policy review.

**Peer:** `writer_test`.

**Decision needed:** Does B’s computer workspace supply partial room-function information under the approved computer-context convention?

### train_8568: `location`

**Supplied similarity score:** `3/5`. **V1 audited score:** `excluded/null`.

**Current status:** `invalid`. **Check:** Review exclusion policy.

> **Caption A:** The skateboarder does a jump near a traffic cone .
>
> **Caption B:** A young man is jumping in the air with his skateboard .
>
> **Adopted scope:** skateboarder's location
>
> **Extracted A:** near traffic cone
>
> **Extracted B:** unspecified

**Audit explanation:** B explicitly places the skateboarder in the air. The intended location feature needs review because the exclusion concerns unavailable surroundings.

**Peer:** `writer_test`.

**Decision needed:** Should generic location include B’s explicit airborne position, or does the condition require surrounding venue or ground features?

### train_10241: `position of person`

**Supplied similarity score:** `2/5`. **V1 audited score:** `excluded/null`.

**Current status:** `invalid`. **Check:** Review exclusion policy.

> **Caption A:** A closeup of a man skateboarding in a skate park .
>
> **Caption B:** A skateboarding soaring through the air in front of a blue building .
>
> **Adopted scope:** principal skateboarder position
>
> **Extracted A:** unspecified skating position
>
> **Extracted B:** airborne

**Audit explanation:** A's skateboarding may support ordinary ground-supported riding under the training audit's inference rule. Exclusion for missing position needs policy review.

**Peer:** `writer_test`.

**Decision needed:** Does ordinary ground-supported skateboarding provide a comparable position, as allowed in the training audit, or is explicit posture required?

### train_11335: `woman stance`

**Supplied similarity score:** `4/5`. **V1 audited score:** `excluded/null`.

**Current status:** `invalid`. **Check:** Review exclusion policy.

> **Caption A:** Women riding a horse carrying the American flag , both rider and horse dressed patriotically .
>
> **Caption B:** A blond woman in a green and gray uniform balances on a horse as she shows the American flag off to the crowd .
>
> **Adopted scope:** female rider's stance
>
> **Extracted A:** mounted on horse, exact stance unstated
>
> **Extracted B:** balancing on horse, exact stance unstated

**Audit explanation:** Both captions supply mounted activity. Exact seated or standing stance remains unresolved. The scope of partial stance information needs review.

**Peer:** `writer_test`.

**Decision needed:** Do riding and balancing supply partial stance information, or must seated versus standing be explicitly recoverable?

### train_11341: `means of flotation`

**Supplied similarity score:** `3/5`. **V1 audited score:** `excluded/null`.

**Current status:** `invalid`. **Check:** Review exclusion policy.

> **Caption A:** A man and a small girl floating on an innertube .
>
> **Caption B:** A man is helping his child float along in the pool .
>
> **Adopted scope:** physical means supporting flotation
>
> **Extracted A:** inner tube
>
> **Extracted B:** man helps child float, actual buoyancy support unstated

**Audit explanation:** B identifies the man's assistance. Its physical support mechanism remains unspecified. The scope of partial flotation means needs review.

**Peer:** `writer_test`.

**Decision needed:** Can the man’s stated assistance supply a partial flotation means, or must the physical buoyancy mechanism be identified?

### evaluation_855: `number of pizza slices`

**Supplied similarity score:** `-1 (source invalid marker)`. **V1 audited score:** `excluded/null`.

**Current status:** `invalid`. **Check:** Check recorded value.

> **Caption A:** A pizza has been prepared and is ready to go into the pizza oven.
>
> **Caption B:** A pepperoni mushroom pizza with one slice taken out, and a pie server resting on the plate.
>
> **Adopted scope:** pizza slice count
>
> **Extracted A:** uncut count unstated
>
> **Extracted B:** remaining slice count unstated

**Audit explanation:** A leaves slice count unspecified. B identifies one missing slice and leaves the remaining count unspecified.

**Peer:** `writer_validation`.

**Decision needed:** A leaves slicing state unspecified. Should Extracted A describe only the unstated slice count?

### evaluation_1884: `height of animal`

**Supplied similarity score:** `5/5`. **V1 audited score:** `excluded/null`.

**Current status:** `excluded_scope`. **Check:** Review exclusion policy.

> **Caption A:** A dog is jumping in the air in a field of grass .
>
> **Caption B:** The black dog jumps out of the snow to catch an object .
>
> **Adopted scope:** animal height: stature versus elevation
>
> **Extracted A:** dog jumping in grass, stature unstated
>
> **Extracted B:** dog jumping out of snow, stature unstated

**Audit explanation:** Animal height admits stature and jump-elevation readings. Stature remains unspecified, while both captions supply only coarse airborne elevation.

**Peer:** `writer_validation`.

**Decision needed:** Should the stature reading follow frozen train_11207, or should stature and jump elevation remain competing features?

### evaluation_2450: `color of animals`

**Supplied similarity score:** `1/5`. **V1 audited score:** `excluded/null`.

**Current status:** `invalid`. **Check:** Review exclusion policy.

> **Caption A:** Two tri-colored short dogs run away from the camera in the trees .
>
> **Caption B:** Two beige dogs are playing in the grass near a doghouse .
>
> **Adopted scope:** animal coat colors
>
> **Extracted A:** three unnamed colors
>
> **Extracted B:** beige

**Audit explanation:** A identifies three unnamed coat colors. B identifies beige. Whether color-count information supports a partial comparison requires policy review.

**Peer:** `writer_validation`.

**Decision needed:** Does the stated three-color coat supply partial color information under the colorful convention accepted for train_10852?
