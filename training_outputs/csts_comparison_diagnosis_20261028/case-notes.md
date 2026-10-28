# What the examples suggest

These notes interpret examples from the [sentence pair review](cases.md). The review contains 35 selections from the frozen test. Human ratings retain their original values. Predictions below use the original 1 to 5 scale. A learned and fresh scores average their three saved models. The interpretation of each example is a hypothesis for review.

## Which things belong in the count

**evaluation_788, number of dishes.** One caption describes a plate and a cup. The other describes a plate, a cup and a saucer. Its human rating is 1. A with comparison scores 1.566 and fresh training averages 4.221. The additional saucer is a concrete difference to inspect. The learned correction changes A's score by about 0.034 points; A's cosine already separates the descriptions.

**evaluation_24, number of player.** One caption describes a female tennis player in front of an audience. The other describes a woman preparing to hit the ball while another woman watches. Its human rating is 5. Fresh training averages 4.318 and A with comparison scores 1.399. The relevant counting question is which people are players and which are spectators.

**evaluation_673, number of people.** One caption has children and an adult. The other has a girl and a woman. Its human rating is 1. Fresh training averages 1.721 and A with comparison scores 4.223. The plural children provides a lower bound on the first count. This is a useful example for reviewing whether a summary preserves quantifiers.

Together, these selections suggest reviewing the definition of the counted set, roles within that set and the information carried by plural expressions. They include successes from both encoder histories.

## Meaning supplied by the situation

**evaluation_1806, color of snow.** The captions describe a woman in a yellow jacket skiing and a snowboarder in white soaring through the air. The human rating is 5. A with comparison scores 4.715 and fresh training averages 2.684. The condition names snow, while the explicit colors describe clothing. Skiing and snowboarding supply a plausible shared snowy setting. The learned comparison raises A's score by about 0.126 points. This is a useful natural example for studying condition focus and background inference together.

**evaluation_862, position of ball.** One caption explicitly places a tennis ball in the air. The other describes a tennis player serving. The human rating is 5. A with comparison scores 3.004 and fresh training averages 2.284. A's cosine is 3.036. The comparison makes a small downward correction here. The relevant review question is what position the description of a serve supports.

These examples accompany the controlled color result: the existing encoder already ranks the proposed matching anchor first in all 30 implied color families. The learned comparisons strengthen their margins and also increase the benefit of explicit color words. The natural examples help us examine how this preference applies when the condition's object is implicit and other colored objects are present.

## Partial information

**evaluation_1647, number of people.** Two construction workers are compared with several people looking out from a building under construction. The human rating is 3. A's cosine scores 1.329. Its learned comparison raises that to 1.645. Fresh training averages 2.013. The comparison moves the rating toward the supplied intermediate target. A useful conditional summary would preserve the difference between an exact count and an unspecified plural count.

## Language and event timing

**evaluation_675, activity of people.** One caption describes skiers wearing bright colors and standing out from a white mountain. The other explicitly describes people skiing down a slope. The human rating is 5, while both model families score about 1.3. Standing out is an idiom about visual prominence. The activity implied by the noun skiers is another interpretation to review against the annotation policy.

**evaluation_1813, ball out of play.** One caption describes putting a soccer ball back into play. The other describes kicking a ball toward a teammate. The human rating is 1. A's cosine scores 4.856 and its learned comparison averages 5.011. Fresh training averages 4.422. The condition raises a timing question: the earlier state of the ball, the transition into play and the resulting state are distinct parts of the event. The unrestricted learned score can extend beyond the nominal rating range.

## Working interpretation

The comparison produces a small improvement from the information in A's existing vectors. The counting and spatial examples also expose larger differences between the encoder histories. Condition scope, roles, quantifiers, implied settings and event timing are concrete targets for the next review of conditional summarization examples.

The controlled color findings concern score margins and preference strength on the proposed labels. The [label review](implied-label-review.md) presents all 30 implied families for human adjudication. The [methods](../../plans/csts-comparison-diagnostics-methods.md) describe the frozen models, CPU comparison fit and exploratory scope.
