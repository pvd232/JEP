# Saved-checkpoint answer inspection: FLAN and Qwen

Qwen learned to generate held-out evidence answers, and its alignment with those answers weakened during subsequent rating training.

This diagnostic used **50 English development passage-condition prompts from 50 source groups**, with four saved checkpoints and **200 generated answers**. The fixed cohort contains accepted cached teacher targets, with at most two prompts per condition. Each prompt was excluded from training by passage-condition identity and source group. Model training and test-set tuning were outside this inspection. The existing Spanish expert-reviewed set remains unavailable.

## Observed answer behavior

| Model | Exact teacher matches after evidence training | After rating training | Teacher token F1, before → after |
|---|---:|---:|---:|
| FLAN-T5-small | 29/50 | 22/50 | 0.792 → 0.698 |
| Qwen3-Embedding-8B | 33/50 | 9/50 | 0.854 → 0.458 |

These values measure agreement with the cached teacher targets. Expert-judged correctness remains unevaluated. The normalized exact-match calculation lowercases text and tokenizes words and numbers; the token F1 counts token overlap. [Summary](summary.json) and [raw generations](generations.jsonl) contain the measurements.

Within Qwen, mean teacher-answer cross-entropy changed from **0.152 to 4.860** after rating training. Within FLAN, the corresponding change was **0.195 to 0.543**. Compare changes within a model: the models use different tokenizers, which limits interpretation of absolute cross-entropy differences between models.

Qwen's frozen generation head was identical before and after rating training. The before/after generations therefore expose a change in how the updated backbone and adapters interact with that head. This observation supports investigating interference between the evidence and rating objectives. Whether Qwen retained the underlying facts, and whether preserving generation would improve similarity, remain separate questions.

## Source-based reading of the answers

The generated answers show both valid shortening and failures to preserve the requested attribute. These examples have different implications:

| Case | Condition | Qwen after evidence training | Qwen after rating training | Reading |
|---|---|---|---|---|
| 28 | Color of object | colorful | balls | Changes from color to object identity |
| 8 | Activity of players | navigates the football past opposing players | football | Changes from activity to sport |
| 14 | Advertisement on vehicle | a Coca Cola advertisement on the side of the bus | advertisement on vehicle | Echoes the question and omits the brand |
| 4 | Quantity of food | Full enumeration of four donuts | four | Valid answer becomes more direct |
| 45 | Type of vehicle | A red car | car | Valid answer drops an irrelevant color |

Qwen also changed to Chinese or mixed Chinese/English in cases 27 and 41. The underlying meanings remain related to the passages; the language shift is a separate generation-format change.

Some teacher answers are broader than the condition requires. Case 43 asks for animal type. The teacher copies a complete caption about a cat sleeping in a shoe box. Both models later answer “cat.” Case 12 names bicycles and a bus, while the condition merely asks for transportation type. The teacher and models choose different supported vehicles. Case 16 mentions two people plus a separate couple, making the intended counting scope unclear.

The notes for all 50 cases are an assistant's qualitative review. Human and expert accuracy assessments remain outstanding.

## Why the two encoders can perform differently

Both systems encode a passage under a condition. Their capacity and training history differ. The loaded FLAN system has **77,026,688 parameters including its projection**. The loaded Qwen backbone and adapters have **7,597,966,336 parameters**, about **99 times** as many. Qwen's restored frozen generation head adds 621,219,840 parameters during answer inspection. [Checkpoint metadata](summary.json) records the counts.

FLAN-T5 was trained for text generation; the Qwen embedding release was developed for embedding and ranking tasks. The shared “encoder” role permits different learned vector geometries and similarity performance. The [FLAN model card](https://huggingface.co/google/flan-t5-small) and [Qwen embedding model card](https://huggingface.co/Qwen/Qwen3-Embedding-8B) describe those intended tasks.

Capacity and task-aligned pretraining are plausible contributors to Qwen's stronger similarity result. Our experiments compare complete model-and-training recipes; the relative contributions remain unresolved. FLAN received six evidence epochs and Qwen two; their accepted training subsets and fine-tuning procedures also differ.

Qwen produced useful held-out answers after evidence training. This supplies evidence that the generation objective was learnable in the implemented setup. It gives a narrower lead to investigate, namely the later change in answer-generation behavior during rating training. The lack of a demonstrated Qwen similarity gain remains a separate result.

## Checkpoint and inference checks

The evidence-phase checkpoints are the terminal weights actually passed into rating training. Their SHA-256 values match the rating phase's recorded initial checkpoint identity. The later checkpoints are the validation-selected models used in the completed experiments.

| Model | Terminal evidence epoch | Selected rating-phase epoch |
|---|---:|---:|
| FLAN-T5-small | 6 | 28 |
| Qwen3-Embedding-8B | 2 | 5 |

Inference used each model's native training input format, greedy decoding and a 64-token output limit. Qwen's cached and full-prefix decoding produced the same first four greedy tokens on a smoke-check prompt. All inference used gradient-disabled inference mode. Source split, teacher cache, generation-head and checkpoint identities were checked. Compilation and Ruff's syntax/undefined-name checks passed for the inspection script.

The source code is [inspect_saved_answers.py](inspect_saved_answers.py). The [manifest](manifest.json) fixes the 50 prompts. The [raw outputs](generations.jsonl) preserve every generated answer and per-answer teacher loss.

## Scope

The cohort is deliberately limited to accepted teacher targets in the existing English development split. Population accuracy and training-seed variation remain unmeasured. The 50 source-group-separated examples support inspecting behavior; the cause of the downstream similarity difference remains unresolved.

The completed [Qwen similarity report](../csts_qwen_evidence_report.md) found test Spearman 0.788505 for ratings-only and 0.783645 for evidence followed by ratings, with an evidence-minus-control paired 95% interval of [−0.013408, +0.003454]. The [FLAN experiment report](https://github.com/pvd232/JEP/blob/experiment/csts-tranche3-evidence-controls-20261024/training_outputs/csts_tranche3_report.md) found a positive evidence effect in its matched controls. Both are single-seed findings.

## All 50 cases

### Case 01: type of food item

> The specialty pizza apears to have thin crust, very little sauce, shaved meat, and goat cheese.

Teacher target: `specialty pizza`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `specialty pizza` | `specialty pizza` |
| Qwen | `specialty pizza` | `pizza` |

Both models identify pizza. Qwen's later answer drops the modifier “specialty” while preserving the food type.

### Case 02: food

> A glass table with a spinach pizza, a bottle of wine, and two filled glasses.

Teacher target: `spinach pizza`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `spinach pizza` | `spinach pizza` |
| Qwen | `spinach pizza` | `wine` |

Qwen changes from spinach pizza to wine after rating training. Both items occur in the passage; the later answer shifts away from the intended food item.

### Case 03: name of object

> Several kites being flown in the sky that are attached to each other by strings.

Teacher target: `kites`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `kites` | `kites` |
| Qwen | `kites` | `kite` |

“Kite” and “kites” preserve the requested object type. A plural difference changes exact teacher agreement.

### Case 04: quantity of food

> A chocolate glazed donut and a peanut donut and sprinkled donut and cinnamon donut

Teacher target: `A chocolate glazed donut and a peanut donut and sprinkled donut and cinnamon donut`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `A chocolate glazed donut and a peanut donut and sprinkled donut and cinnamon donut` | `chocolate glazed donut and a peanut donut and sprinkled donut and cinnamon donut` |
| Qwen | `A chocolate glazed donut and a peanut donut and sprinkled donut and cinnamon donut` | `four` |

The caption enumerates four donuts. Qwen's later answer “four” answers the quantity directly; exact agreement with the teacher's full enumeration penalizes this valid answer.

### Case 05: number of animals

> The silhouettes of five horses stand in a field as a mountain range is seen off in the distance.

Teacher target: `five horses`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `five horses` | `five horses` |
| Qwen | `five horses` | `five` |

Qwen's later “five” preserves the requested animal count.

### Case 06: type of food

> A couple of hot dogs with a potato and a fork and knife on a plate.

Teacher target: `hot dogs`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `hot dogs` | `hot dogs` |
| Qwen | `A couple of hot dogs` | `hot dogs` |

All answers identify hot dogs. The potato creates another food item in the caption, so the condition could support more than one target.

### Case 07: object shape

> A diamond shaped sign is sitting in the middle of the street as cars are riding on the side.

Teacher target: `diamond shaped`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `diamond shaped` | `diamond` |
| Qwen | `diamond shaped sign` | `diamond shaped` |

All outputs preserve the diamond shape. Extra words such as “sign” affect teacher agreement while preserving the shape.

### Case 08: activity of players

> A Pee Wee league football player wearing a purple jersey navigates the football past opposing players in white jerseys .

Teacher target: `navigates the football past opposing players`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `navigates the football past opposing players` | `navigates the football past opponents in white jerseys` |
| Qwen | `navigates the football past opposing players` | `football` |

Qwen changes from the players' action to “football” after rating training. The later answer names the sport and omits the requested activity. FLAN preserves the action.

### Case 09: sport

> A man in a green jacket and brown pants is pictured in midair on a snowboard .

Teacher target: `snowboard`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `snowboard` | `snowboard` |
| Qwen | `snowboard` | `snowboard` |

All outputs identify the snowboard activity or equipment named in the passage.

### Case 10: activity of people

> The woman is feeding a baby sitting on a table near a cake and balloons.

Teacher target: `feeding a baby`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `feeding a baby sitting on a table near a cake and balloons` | `feeding a baby sitting on a table near a cake and balloons` |
| Qwen | `feeding a baby` | `feeding` |

All outputs retain feeding. Qwen's later answer drops the patient; FLAN includes additional scene details.

### Case 11: location as science lab

> A scientist wears latex gloves while handling samples and scientific equipment behind a glass shield .

Teacher target: `behind a glass shield`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `behind a glass shield` | `behind a glass shield` |
| Qwen | `behind a glass shield` | `lab` |

The teacher gives an explicit spatial phrase. Qwen later says “lab,” a plausible inference from the scientific scene that is absent as an explicit source word. The condition itself is underspecified.

### Case 12: type of transportation

> A line of bicycles beside a street where a bus is stopping for passengers.

Teacher target: `bicycles`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `bus` | `bus` |
| Qwen | `buses` | `bus` |

The passage contains bicycles and a bus. The teacher selects bicycles; both models choose a bus. The generic condition leaves the target entity ambiguous.

### Case 13: motion of person

> A young girl in a white shirt and blue shorts riding high on a swing .

Teacher target: `riding high on a swing`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `riding high` | `riding high` |
| Qwen | `riding high on a swing` | `swing` |

Qwen changes from “riding high on a swing” to “swing.” The later output loses the explicit riding action, though “swing” can also name the motion. FLAN retains “riding high.”

### Case 14: advertisement on vehicle

> A street with two cars and a bus in between the cars with a Coca Cola advertisement on the side of the bus.

Teacher target: `Coca Cola advertisement on the side of the bus`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `Coca Cola advertisement` | `Coca Cola` |
| Qwen | `a Coca Cola advertisement on the side of the bus` | `advertisement on vehicle` |

Qwen's later output echoes the condition and omits Coca Cola. FLAN keeps the advertised brand.

### Case 15: type of game

> A man is catching a Frisbee in the foreground while a group of people in the background appear to be running somewhere.

Teacher target: `A man is catching a Frisbee in the foreground while a group of people in the background appear to be running somewhere`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `Frisbee` | `Frisbee` |
| Qwen | `Frisbee` | `Frisbee` |

Both models answer “Frisbee.” The teacher target copies the full caption, which adds information beyond the game type.

### Case 16: number of people

> Two people lay on towels on a beach while a couple strolls by the water.

Teacher target: `Two people`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `Two people` | `Two people` |
| Qwen | `Two people` | `Two` |

The caption contains two people on towels and a couple by the water. The teacher's count covers the first group. The intended counting group is unspecified.

### Case 17: species of animal

> A herd of zebra standing next to each other in a green grass covered field.

Teacher target: `A herd of zebra`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `A herd of zebra` | `zebra` |
| Qwen | `A herd of zebra` | `zebra` |

“Zebra” is sufficient for the species question. Longer teacher-like spans add herd information.

### Case 18: occupation of worker

> Outdoor workers repair a sidewalk using a jackhammer in the United Kingdom .

Teacher target: `Outdoor workers`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `Outdoor workers` | `Outdoor workers` |
| Qwen | `Outdoor workers` | `workers` |

The source identifies outdoor workers repairing a sidewalk. Their precise occupational title is unspecified. Later “workers” is less specific.

### Case 19: type of animal

> A man in a black vest with gray jeans with a red side flag holding onto a horse while 2 men watches and 1 man keeps time .

Teacher target: `a horse`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `horse` | `horse` |
| Qwen | `a horse` | `horse` |

“Horse” preserves the animal type. The teacher's article changes the automatic match.

### Case 20: name of game

> A group of football players running down the field .

Teacher target: `football`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `football` | `football` |
| Qwen | `football` | `football` |

All outputs identify football.

### Case 21: animals color

> A small black dog playing with a ball in the grass .

Teacher target: `small black dog`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `black` | `black` |
| Qwen | `small black dog` | `black` |

“Black” directly answers the color question. The teacher also includes the dog's size and type. Qwen's shorter later answer improves condition focus despite lowering exact agreement.

### Case 22: Slope of walking path

> Men in pants and coats walk up a steep and narrow road .

Teacher target: `steep and narrow road`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `steep and narrow road` | `steep and narrow road` |
| Qwen | `steep and narrow` | `steep and narrow` |

All outputs retain the steep slope. Narrowness is additional source information.

### Case 23: location

> The skateboarder does a jump near a traffic cone .

Teacher target: `near a traffic cone`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `near a traffic cone` | `near a traffic cone` |
| Qwen | `near a traffic cone` | `cone` |

Qwen shortens “near a traffic cone” to “cone,” losing the explicit spatial relation.

### Case 24: type of electronic equipment

> A laptop set up on a stand with a standard keyboard and mouse hooked up to it.

Teacher target: `A laptop set up on a stand with a standard keyboard and mouse hooked up to it`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `laptop` | `laptop` |
| Qwen | `laptop` | `laptop` |

“Laptop” is a supported main object. The teacher copies the whole caption, including a stand, keyboard and mouse.

### Case 25: number of children

> Two young kids on a break from swimming sitting on a log .

Teacher target: `Two young kids`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `Two young kids` | `Two young kids` |
| Qwen | `Two young kids` | `two` |

Qwen's later “two” preserves the children's count.

### Case 26: sport

> One rugby player trying to catch the player with the ball .

Teacher target: `rugby`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `rugby` | `rugby` |
| Qwen | `rugby` | `rugby` |

All outputs identify rugby.

### Case 27: hand action

> A baseball player in the act of pick up a baseball with his hand .

Teacher target: `in the act of pick up a baseball with his hand`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `pick up a baseball with his hand` | `pick up` |
| Qwen | `pick up a baseball with his hand` | `捡球` |

Qwen changes to Chinese “捡球” after rating training, meaning picking up a ball. The meaning is supported; the output language changes. FLAN's later answer shortens the action.

### Case 28: color of object

> Two boys in tent-like area , with colorful balls on floor .

Teacher target: `colorful balls`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `colorful balls` | `colorful` |
| Qwen | `colorful` | `balls` |

Qwen changes from the color property “colorful” to the object name “balls” after rating training. FLAN preserves the color property.

### Case 29: name of game

> A woman jumping up to a hit a tennis ball on a tennis court.

Teacher target: `tennis`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `tennis` | `tennis` |
| Qwen | `tennis` | `tennis` |

All outputs identify tennis.

### Case 30: athlete's surroundings

> The skateboarder is leaping over a green barrel .

Teacher target: `leaping over a green barrel`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `is leaping over a green barrel` | `is leaping over a green barrel` |
| Qwen | `green barrel` | `green barrel` |

“Green barrel” supplies the requested surroundings. The teacher and FLAN also include the skateboarder's action.

### Case 31: color of vehicle

> An orange  bus parked in front of a church with a tall clock tower.

Teacher target: `orange`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `orange` | `orange` |
| Qwen | `orange` | `orange` |

All outputs identify orange.

### Case 32: type of area in home

> A sofa and coffee table in one room that opens up into the bedroom

Teacher target: `one room that opens up into the bedroom`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `bedroom` | `bedroom` |
| Qwen | `one room that opens up into the bedroom` | `bedroom` |

The caption names a bedroom adjacent to an unspecified room. The condition leaves the intended room unclear. Short “bedroom” answers identify the only explicitly named room type.

### Case 33: view of animal

> A view of a dog with his head sticking out of a car window through a mirror.

Teacher target: `A view of a dog with his head sticking out of a car window through a mirror`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `A view of a dog` | `sticking out of a car window through a mirror` |
| Qwen | `A view of a dog with his head sticking out of a car window through a mirror` | `mirror` |

Qwen later names the mirror. FLAN's terminal pretraining answer omits the mirror, while its later answer includes it. The teacher copies the whole caption.

### Case 34: type of vessel

> Six men , two wearing hats , are sitting in a small boat on the water .

Teacher target: `small boat`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `small boat` | `small boat` |
| Qwen | `small boat` | `boat` |

“Boat” preserves the vessel type; “small” is an additional size attribute.

### Case 35: type of activity

> A black and white image of a young man riding a skateboard in an emptied-out pool.

Teacher target: `riding a skateboard`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `riding a skateboard` | `riding a skateboard` |
| Qwen | `riding a skateboard` | `skateboarding` |

“Skateboarding” and “riding a skateboard” express the same supported activity.

### Case 36: animal type

> A dog sleeping on a couch with head hanging over the edge next to a person.

Teacher target: `A dog sleeping on a couch`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `A dog sleeping on a couch with head hanging over the edge next to a person` | `dog` |
| Qwen | `A dog` | `dog` |

“Dog” answers the animal-type question directly. FLAN's terminal pretraining answer copies the full caption; its later answer becomes concise.

### Case 37: place bathroom

> A bathroom with a curtain over the bathtub next to a sink and toilet.

Teacher target: `A bathroom with a curtain over the bathtub next to a sink and toilet`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `next to a sink and toilet` | `next to a sink and toilet` |
| Qwen | `A bathroom with a curtain over the bathtub next to a sink and toilet` | `bathroom` |

The condition is ambiguous. Qwen later gives the room type “bathroom”; FLAN gives a position relative to fixtures.

### Case 38: age of girl

> This young girl is enjoying the innocence of childhood and warm weather .

Teacher target: `young`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `young girl` | `childhood` |
| Qwen | `young` | `child` |

The source supplies a qualitative age description; the numerical age is unspecified. “Young,” “childhood,” and “child” retain that information with different wording.

### Case 39: people on street

> A group of people walking on a walkway filled with clocks mounted on poles.

Teacher target: `A group of people`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `A group of people` | `walking` |
| Qwen | `A group of people walking on a walkway filled with clocks mounted on poles` | `walkers` |

The condition leaves the choice between people and their activity unspecified. Qwen's initial full-caption answer and later “walkers” differ in specificity.

### Case 40: type of sport

> A woman in a red shirt and white skirt playing tennis with a blue racket .

Teacher target: `playing tennis`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `playing tennis` | `tennis` |
| Qwen | `playing tennis` | `tennis` |

“Tennis” directly answers the sport question. Exact agreement with “playing tennis” penalizes this valid shortening.

### Case 41: type of sport

> A group of greyhounds racing with jerseys and muzzles .

Teacher target: `greyhounds racing`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `racing` | `greyhounds` |
| Qwen | `greyhounds racing` | `灰hound赛跑` |

FLAN changes from racing to the animal name “greyhounds,” losing the explicit sport. Qwen's later mixed Chinese/English output retains a racing meaning while changing language and form.

### Case 42: locomotion

> A large group of people walking on a dirt path in the woods with trees on both sides .

Teacher target: `walking`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `walking` | `walking` |
| Qwen | `walking` | `walking` |

All outputs identify walking.

### Case 43: type of animal

> A black and gray cat sleeps in a shoe box on a desk near a keyboard.

Teacher target: `A black and gray cat sleeps in a shoe box on a desk near a keyboard`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `A black and gray cat` | `cat` |
| Qwen | `A black and gray cat` | `cat` |

“Cat” directly answers the animal-type question. The teacher target copies the whole caption.

### Case 44: number of animals

> Two dogs are standing in snow , the smaller one barking at the larger one .

Teacher target: `Two dogs`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `Two dogs` | `Two dogs` |
| Qwen | `Two dogs` | `two` |

Qwen's later “two” preserves the dogs' count.

### Case 45: type of vehicle

> A red car is near a red stoplight on a street that has tall buildings.

Teacher target: `A red car`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `red car` | `car` |
| Qwen | `A red car` | `car` |

“Car” directly answers the vehicle-type question. “Red” is optional for this condition, so shorter later answers are valid.

### Case 46: means of traversal

> Person in black jacket and green pants skiing downhill

Teacher target: `skiing downhill`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `skiing downhill` | `skiing downhill` |
| Qwen | `skiing` | `skiing` |

Skiing is the traversal method. Downhill direction is additional supported information.

### Case 47: type of meat

> A plate that has two hot dogs, corn on the cob, some pasta, and noodles.

Teacher target: `hot dogs`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `two hot dogs, corn on the cob, some pasta, and noodles` | `hot dogs` |
| Qwen | `two hot dogs` | `hot dogs` |

The source names hot dogs; their meat species is unspecified. FLAN's terminal pretraining answer lists additional foods, while its later answer focuses on hot dogs.

### Case 48: reason for gathering

> A group of people sitting in a restaurant about to have a meal together.

Teacher target: `about to have a meal together`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `about to have a meal together` | `about to have a meal` |
| Qwen | `about to have a meal together` | `meal` |

Qwen's later “meal” names the gathering's purpose in abbreviated form. The longer phrase explicitly describes the joint activity.

### Case 49: type of food

> there is a large pie on a white plate and a bowl next to it

Teacher target: `a large pie`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `large pie` | `pie` |
| Qwen | `large pie` | `pie` |

“Pie” preserves the food type. Size and article differences change teacher agreement.

### Case 50: location of people

> A surfer in blue trunks catches a small wave while two other surfers float in the water .

Teacher target: `while two other surfers float in the water`

| Model | After evidence training | After rating training |
|---|---|---|
| FLAN | `in the water` | `in the water` |
| Qwen | `A surfer in blue trunks catches a small wave while two other surfers float in the water` | `water` |

“Water” and “in the water” preserve the explicit location of the two floating surfers. The teacher and Qwen's initial answer copy a longer clause or full caption.

