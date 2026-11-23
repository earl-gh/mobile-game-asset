# Anatomy-first blockout (organic assets)

Read this before stage 1 for any character, creature or other organic asset. The blockout's job is believable anatomy; topology and texture come after it, never mixed into it. The anatomy gate (section 4) must pass before stage 3.

Confidence tags: [S] sourced, [C] common artist practice, [J] judgment. Tolerances and several ratios are untested starting points. Numbers are starting values, not laws: always prefer measurements taken from the user's reference image over this table.

## 1. Method (do in this order)

1. **Pick the closest real analog by body plan, not by name.** Why: every creature is a variation of an existing skeleton; a wrong analog poisons every later ratio. Write down: analog, stance (plantigrade / digitigrade / unguligrade / sprawl / biped / winged), size class.
2. **Collect reference first:** one side and one front orthographic (or pose-matched photo) of the analog's skeleton plus one of the live animal. Set both as image planes at the same scale. Why: the overlay is the only objective check you have.
3. **Place skeleton landmarks as empties/low-poly bones before any mass.** Name them (`L_shoulder_joint`, `pelvis_hip_joint`, `skull_occiput`, `sternum_tip`, `withers`, `ischial_tuberosity`, ...). Place joint centers first, then bone ends: Why: joints are where silhouette bends and where the rig will later pivot; they must be right before topology.
4. **Primary forms on the skeleton:** skull (cranium + muzzle/jaw), rib cage (egg/barrel, widest behind the shoulder), pelvis (wedge), then connect with spine curve. Check the spine curve in side view (neck-withers-loin-sacrum-tail) before continuing.
5. **Major muscle volumes anchored to bone landmarks:** shoulder/scapula mass, deltoid/forearm group, chest, thigh/gluteal mass, calf. Draw each along its origin-to-insertion line; large volumes cross joints only at tendons. Why: muscle flow along the line explains where bulges and valleys go.
6. **Limbs and neck as chains of correct-count segments** (see 3). Keep distal segments (below elbow/knee) thin and tendon-like; mass lives proximally.
7. **Silhouette checks** (side, front, back, top, 3/4): flat black fill at thumbnail size must still read as the analog or the intended exaggeration. Mirror test: apply Mirror modifier on X, compare L/R, then check pose asymmetry only after the base is symmetrical.
8. **Deferred (do not touch in blockout):** edge flow/topology, creases, wrinkles, scales/fur, texture, secondary muscles, tendons, final hands/paws, eyes/teeth detail. Blockout = 5-15 primitives or a single voxel/low-poly mesh per major form; a boolean/union or shrinkwrap comes after the gate passes.
9. **How artists verify during blockout:** (a) skeleton visible through a 40-60% transparent mass (viewport X-ray) so landmarks protrude where bone is subcutaneous (spine of scapula, olecranon, greater trochanter, iliac crest, sternum, calcaneus/hock point, ischium); (b) segment length ratios against the table; (c) joint angles in a neutral standing pose; (d) orthographic overlay of analog silhouette. [C] (Polycount/80.lv/CGChannel/Proko workflows all use skeleton-first, landmark-first, silhouette-from-every-angle; CreativeBloq: a wrong skeleton throws off everything above it)

## 2a. Adult human biped (head units = chin-to-crown, H = height)

| Item | Value | Tag |
|---|---|---|
| Height | average 7.5 heads; idealized 8; heroic 8.5 | [S] |
| Landmarks below chin (Loomis) | nipples 1 head, navel 2, crotch 3 (crotch = near half height, greater trochanter level) | [S] |
| Legs, floor to crotch | 3.5-4 heads | [S] |
| Knee height | about 2 heads above floor (just over 2 in 8-head figure) | [C] |
| Arm (shoulder to fingertip) | about 3 heads; wrist at crotch level, fingertips mid-thigh when hanging; elbow near navel/waist | [S]/[C] |
| Hand length | about face length (chin to hairline) | [S] |
| Shoulder width (idealized male) | 2 1/3 heads; hips 1.5 heads (female hip:shoulder width about 1:1.03, male 1:1.18) | [S] |
| Thigh length | 0.24-0.245 H | [S] (Drillis-Contini via Dempster/Plagenhoef table) |
| Shank ~ thigh; upper arm 0.186 H; forearm 0.146 H; hand 0.108 H | thigh:shank ~ 1:1, upper arm:forearm ~ 1.25:1 | [C] low (recalled, not re-verified) |
| Vertebrae | 7 cervical, 12 thoracic, 5 lumbar, 5 sacral (fused) | [S] |
Stance: foot flat (plantigrade), knee straight about 175-180 deg, vertical line from ear through shoulder, hip, knee to ankle. [C]

## 2b. Digitigrade quadruped (canid / felid class). WH = withers height (ground to withers)

| Item | Value | Tag |
|---|---|---|
| Body length (point of shoulder to point of buttock) | about 1.1-1.18 x WH (canid, breed standard states "10:9 to 8.5"; ambiguous); felid and light sighthounds closer to 1.0-1.1 | [S] breed std, one breed / [J] |
| Chest (brisket) depth | 45-48% of WH, so brisket sits about at elbow, elbow at about 50-55% WH from ground | [S] (GSD standard) / [J] |
| Foreleg length vs chest depth | foreleg slightly longer than chest depth | [S] |
| Head length | about 0.35-0.42 WH; skull (cranium) about 50% of head length, muzzle other 50% | [S] skull ratio / [J] range |
| Neck | carried about 45 deg above horizontal; length about 0.8-1.0 head length | [S] angle / [J] |
| Humerus / radius / metacarpal III | about 31% / 30% / 12% WH | [S] derived from Harcourt 1974 regressions, mid-size dogs |
| Femur / tibia / metatarsal III | about 33% / 34% / 13% WH (metatarsal slightly longer than metacarpal) | [S] derived |
| Scapula length | about equal to humerus length | [S] (breed ideal), true skeletons vary +/-15% |
| Femur : tibia | about 1:1 (tibia slightly longer in running types) | [S] |
| Standing angles, interior, 180 = straight | scapula 45 deg to horizontal; scapula-humerus about 90-110; elbow 135-150; carpus about 180; hip 105-125; stifle 145 (range 130-157); hock 134 (range 122-148) | stifle, hock [S] (Giansetto 2022, 1 study, breed varies); scapula 45 and shoulder 90 [S] breed std; elbow, carpus, hip [J] low |
| Vertebrae | dog 7C 13T 7L 3S, tail 20-23; cat 7C 13T 7L 3S, tail 19-23 | [S] |
| Tail | reaches about the hock (dog); cat tail about 0.8-1.0 x body length | [S] dog / [J] low cat |
| Mass | front limbs carry about 60% of weight: COM sits just behind the scapulae at about 55% WH | [S] 60% / [J] position |
| Spine curve | neck rises from withers, back near level or slightly sloping, croup 20-30 deg down, tail follows; felids have a more arched flexible lumbar curve | [C] |
| Shoulder girdle | no functional clavicle in dogs (scapula floats on muscle sling); cats have a vestigial free clavicle | [S] |
Felid limb bones scale near-isometrically with size across species, so one proportion set can be rescaled for any felid size. [S] (Doube 2009, Day & Jayne 2007, via abstracts)

## 2c. Other body plans: what to look up, what to measure

For each: find a skeleton photo or museum mount in side view, measure every segment as a % of withers/hip height or trunk length, record the neutral joint angles, and write the numbers down in the same units as 2b.
- **Plantigrade quadruped (bear, rodent, primate on all fours):** heel (calcaneus) and carpal pad contact the ground; measure heel length, humerus:radius, shoulder:hip height ratio, front-heavy mass. Limbs shorter and thicker than digitigrade. [C]
- **Bird-like biped (theropod, ratite, any bird):** the long "reverse knee" is the ankle (intertarsal) joint; the true knee is hidden in feathers/body at the femur. Segments: femur (short), tibiotarsus (long), tarsometatarsus (long, vertical), toes. Measure femur:tibiotarsus:tarsometatarsus, center of mass above the toes, tail counterbalance. Cervical vertebrae 8 to 25, pygostyle tail. [S]
- **Reptilian sprawl:** humerus and femur held about horizontal out from the body, elbow/knee about 90 deg bent, belly near ground; trunk is long, ribs on most trunk vertebrae. Measure limb segment : snout-vent length, tail:SVL (tail often 1-1.5 SVL [J] low), clearance. Lateral spine undulation is the movement cue. [C]
- **Winged (bird, bat, dragon, pterosaur):** wing is a forelimb: humerus, radius+ulna, carpus, long hand/finger(s); flight muscle (pectorals+supracoracoideus) is 25-40% of a flying bird's mass and anchors on a keeled sternum, so a flyer needs a deep chest. Six-limb fantasy: wings must have their own shoulder girdle, not share the arm's. [S] 25-40%
- **Serpentine:** one long vertebral chain with ribs along nearly its whole length, no sternum, no limbs; measure length:girth, taper, head:neck diameter. Vertebra count is large (dozens to hundreds). [C]
- **Insectoid / arthropod:** three tagmata (head, thorax, abdomen); three leg pairs from the thorax; each leg = coxa, trochanter, femur, tibia, tarsus, pretarsus. Keep joints in that order; the long visible "thigh/shin" are femur and tibia. [S] (Wikipedia, insect morphology)

## 3. Plausibility rules for fantasy and stylized designs

1. **Conserve bone-segment count per limb** (e.g. humerus + radius/ulna + hand; femur + tibia + foot). Add digits, joints or whole limb pairs only with a reason. Why: players read the extra segment as wrong because motion will not make sense.
2. **Put joints where the analog has them** (shoulder at the top of the scapula, elbow near brisket level, knee near belly level, hock point at the calcaneus). Allowed bend ranges follow the analog's (elbow and knee hinge one way; hips and shoulders ball-and-socket). Test by posing the blockout at the extremes.
3. **Balance mass over support:** the center of mass projected to the ground must fall inside the polygon of the feet (biped: over the foot base; quadruped: between fore and hind feet and nearer the front). Compensate big heads, wings, tails with posture or counter-mass.
4. **Muscle flow along origin to insertion**: bulges are widest mid-belly and taper to tendons; groups wrap around bones, they do not cross free space. Shapes that ignore this look inflated, not strong.
5. **Safe exaggeration (stylized game art):** [J] keep each segment ratio within +/-20% of the analog for realistic-stylized, +/-35% for strong stylization, keep segment count and joint order unchanged, keep the exaggeration to 1-2 features (head, hands/feet, torso or limb length) so the rest stays anatomical. Humans: heroic 8-8.5 heads [S]; stylized 5.5-7 heads; chibi 2-4 heads [C]. A bigger head needs a shorter neck, wider shoulders or a smaller body to still read as a body.
6. **When the design is not a single analog (hybrid):** pick the analog per region (head, torso, limbs), join at the shared skeleton landmark, and keep each region's numbers from its own analog.

## 4. Anatomy GATE (script on blockout plus a rendered ortho overlay; fail = fix before topology)

Tolerances are [J] starting points; relax by a stated amount only with a stated reason.

| # | Check | Pass |
|---|---|---|
| 1 | Segment count per limb equals analog (or the design brief says otherwise) | exact |
| 2 | Segment length ratios (each joint-to-joint length / reference length: WH, trunk length or H) vs table | within +/-15% (realistic), +/-30% (stylized) |
| 3 | Proportional pairs: scapula~humerus, femur~tibia, humerus~radius | within +/-20% of the analog ratio |
| 4 | Head-to-body: head units for biped, head length / WH for quadruped | within the analog range or the declared stylization band |
| 5 | Neutral standing joint angles (3 points per joint from the script) | within +/-15 deg of the analog; no hyperextension past 180 |
| 6 | Extreme pose angles (flex/extend each joint) | inside analog range; no segment passes through the torso |
| 7 | COM (volume-weighted centroid of the mass objects) projected to ground | inside the foot support polygon, no more than 10% of foot span from center for bipeds |
| 8 | Symmetry: mirror and compare vertex positions in X | max asymmetry < 1% of height for the base pose |
| 9 | Landmark presence: every named landmark exists and lies inside or on the mass (bone inside skin), not more than 15% of local thickness off the surface | all present |
| 10 | Silhouette overlay: render side and front ortho with analog skeleton/outline image at same scale; compute IoU or edge distance | IoU >= 0.7 vs the intended design silhouette (>= 0.8 if photoreal analog) |
| 11 | Mass bands: thickness proximal > distal for every limb; rib cage widest between 40-60% of its length | true |
| 12 | Scale sanity: total height (m) within the analog's real range unless declared | true |
