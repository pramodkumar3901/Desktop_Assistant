# Skills: new moves, dances and routines

A skill is a small JSON file. Put it in the `my_skills` folder (right-click Blip →
**Skills** → **Open my skills folder**) and Blip picks it up within a couple of seconds,
with no restart and no update. Editing or deleting the file works the same way.

Skills are data, not code: they can only combine what's listed here.

| Folder | What it's for |
|---|---|
| `skills/` | The ones that come with Blip. Updates may change them. |
| `my_skills/` | Yours. Updates never touch it. A skill here replaces a built-in one with the same `name`. |

Don't edit files in `skills/` on a git clone: Blip won't update a copy with local changes.
Copy the file to `my_skills/` and edit the copy.

## A whole skill

```json
{
  "name": "Water break",
  "when": { "every_minutes": 60 },
  "moves": {
    "cheer": {
      "length": 0.8, "repeat": 4, "face": "excited",
      "keys": [
        { "t": 0.0, "hand_left": [44, 38], "hand_right": [44, 38], "lift": 0 },
        { "t": 0.4, "hand_left": [40, 14], "hand_right": [40, 14], "lift": 24 }
      ]
    }
  },
  "do": [
    { "say": ["Water time!", "Your cells filed a complaint. Drink."] },
    { "move": "cheer" }
  ]
}
```

`name` and `do` are needed. `when` and `moves` are optional.

## When it runs

Every skill is in the **Skills** menu, where you can run it or switch it off. `when`
makes it also run by itself:

| Entry | Meaning |
|---|---|
| `"random": 0.6` | Now and then, among Blip's own antics. 0 to 5; Blip's antics are 1 to 3. Quiet mode stops these. |
| `"every_minutes": 60` | On a timer, counted from when Blip started or the skill was added. |
| `"at": "17:30"` | Once a day at this time (24-hour clock), if Blip is running. |
| `"claude": "done"` | When Claude Code finishes a task. `"prompt"`: when you send it one. |

A skill that's due waits until Blip is free, for up to 10 minutes. Picking Blip up,
or asking it for something else, stops a skill.

## Steps (`do`)

Each step has exactly one of these:

| Step | Meaning |
|---|---|
| `{"move": "cheer"}` | Perform a move from `moves` (or write the move right there). |
| `{"act": "dance"}` | One of Blip's own: `think`, `glitch`, `nap`, `dance`, `update`, `spin`, `skate`, `moonwalk`, `lean`, `skip` (a skipping rope). |
| `{"say": ["one", "two"]}` | Say one of these lines. Add `"seconds"` to set how long it waits. |
| `{"mood": "love", "seconds": 3}` | Show a face. |
| `{"jump": true}` | Hop. |
| `{"turn_around": true}` | Face the other way. |
| `{"wait": 2}` | Pause, in seconds. |

A `say` step can carry a button that opens a web page when you click it:
`{"say": "Stand-up time", "link": {"label": "Join", "url": "https://example.com"}}`

Faces: `normal`, `happy`, `excited`, `love`, `wink`, `smug`, `curious`, `angry`,
`cry`, `dizzy`, `surprised`, `sad`, `worried`, `sleep`, `think`, `talk`, `spin`,
`glitch`.

## Moves

A move is a list of **keys**: poses at set times. Blip glides smoothly between them.

| Move entry | Meaning |
|---|---|
| `length` | Seconds in one cycle (0.2 to 30). |
| `repeat` | How many cycles (up to 40; a move lasts 90 seconds at most). |
| `keys` | The poses. Each needs `t`, the time within the cycle. |
| `face` | The face during the move. A key can also set `face`. |
| `effect` | `music`, `sparkles`, `hearts` or `zzz`. |
| `prop` | `true` keeps the accessory in Blip's hands, if the move doesn't use them. |

Each key can set any of these. A part you never mention keeps its normal behaviour.
Out-of-range numbers are pulled back into range.

| Part | Values | Meaning |
|---|---|---|
| `hand_left`, `hand_right` | `[out, up]`: −16 to 52, −16 to 48 | Hand position from the shoulder. Resting is `[6, -11]`. Beside the head, use `out` of 40 or more so the hand clears the headphones. |
| `foot_left`, `foot_right` | `[sideways, up]`: −22 to 22, 0 to 18 | Positive sideways is to the right. |
| `tilt` | −30 to 30 | Head tilt in degrees; positive is to the right. |
| `roll` | −28 to 28 | The whole body leans from the feet, in degrees. |
| `turn` | −1 to 1 | Turn three-quarters: `1` toward the way Blip faces, `-1` away. |
| `squat` | 0 to 1 | Crouch. |
| `sway` | −20 to 20 | Slide the body side to side. |
| `lift` | 0 to 90 | Rise off the floor. |
| `x` | −300 to 300 | Travel along the floor, measured from where the move began; positive is forward. |

`left` and `right` mean the left and right of the screen. Distances are in Blip's own
units (Blip is about 105 tall), so a move looks the same at every size.

A cycle flows on into the next one, so the last key leads back to the first. To keep
travelling with each repeat, give `x` a key at the very start (`"t": 0`) and one at
the very end (`"t"` equal to `length`). Otherwise `x` goes back to the first key's spot.

## If a file is wrong

Blip skips it, says what's wrong, and writes the same to `blip.log`. The Skills menu
shows how many files have a problem.

## Asking Claude to write one

Give Claude Code this page and say what you want, for example: *"Write a Blip skill in
my_skills: a sneaky tiptoe across the floor that ends in a bow."*

## What still needs a Blip update

New kinds of triggers or effects, new props, and anything Blip's body can't do with the
parts above, such as a full flip.
