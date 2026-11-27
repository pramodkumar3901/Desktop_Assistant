# Blip

A tiny, over-eager AI robot that walks along the bottom of your screen: a 3D
screen-faced robot with glowing eyes, in the spirit of the animated office
assistants of the 90s. It wants very badly to help and almost never does.

![Blip walking in through a door, strolling side-on, moonwalking, gliding and
parachuting down after being thrown, a mini Blip walking in for a second Claude Code
session and out again when it's done, a compact suggestion card, then Blip leaving
through a door](docs/blip-demo.gif)

**Start and stop:** double-click **`Start Blip.cmd`** (or `blip.pyw`). Blip walks in through a
door that opens in a bottom corner of the screen. Right-click Blip and choose **Bye, Blip
(quit)** and it walks out through a door before closing. `blip_control.pyw` does the rest:

| Command | Does |
| --- | --- |
| `pythonw blip_control.pyw start` | Opens Blip (does nothing if it's already running) |
| `pythonw blip_control.pyw stop` | Closes Blip |
| `pythonw blip_control.pyw restart` | Closes and reopens it, back on the main screen |
| `pythonw blip_control.pyw reset` | Forgets the accessory, size and Quiet mode, then restarts |

For one-click shortcuts, make a Windows shortcut to each command (right-click in the
folder → New → Shortcut, and paste the command with the full path to `blip_control.pyw`).

**Hide or show:** press **Ctrl+Alt+Q** anywhere. Blip walks out through its door, and
the same keys bring it back.

**Tray icon:** Blip puts its robot face in the notification area (the icons by the clock;
it may be in the overflow arrow, and you can drag it out). Left-click it to find Blip (or bring
it back). Right-click it for **Hide Blip / Show Blip** (it leaves or returns through a door),
**Find Blip** and the same menu as right-clicking Blip. The icon is `blip.ico`, drawn by
`tools/make_icon.py`.

| You do | Blip does |
| --- | --- |
| Move the mouse close | Stops, turns its eyes and head toward it (and wakes up if napping). Stay a while and it gets heart eyes |
| Click Blip | Jumps and encourages you |
| Drag Blip | Hangs from where you grabbed it and swings as you move it, legs dangling; let go and it falls, lands and is dizzy |
| Throw Blip | Flick it as you let go and it flies, bouncing off the screen edges. If the fall gets dangerous it opens a **parachute**, or a **hang-glider** when it's flying sideways fast, and lands safely; a low throw makes it skid |
| Right-click Blip | The menu below |
| Click a speech card | Closes it (buttons do their own thing) |

The right-click menu, in three groups:

| Menu | Holds |
| --- | --- |
| **Rewrite copied text** | Improve it, Make it shorter, More professional, Friendlier, Fix grammar only, Undo last rewrite |
| **Talk to me** | Encourage me, Say something funny, Check in on me, Humour, Do something random, Moonwalk for me, Take a corner break |
| **Claude Code** | Connected to Claude Code, Show alerts, A mini Blip for each extra session, What can you do?, Send a test alert |
| **Look** | Accessory (Rotate, Nothing, Laptop, Phone, Music player, Coffee mug) and Size (Tiny, the default; Medium; Large) |
| **Updates** | The version, Update automatically, Check for updates now |
| **Quiet mode** | No random antics |
| **Bye, Blip (quit)** | Walks out through a door and closes Blip |

## Draft helper

Improve any text without pasting it into a chat:

1. Copy your draft (Ctrl+C) from anywhere.
2. Press **Ctrl+Alt+I**, or right-click Blip → **Rewrite copied text** and pick a style:
   Improve it, Make it shorter, More professional, Friendlier, or Fix grammar only.
3. Blip types on its laptop for a few seconds, then puts the rewrite on your clipboard.
   Press Ctrl+V to paste.

The card that appears has **Show all** (read, tweak and copy the full rewrite), **Try again**
(another version) and **Undo** (puts your original back on the clipboard). Nothing is sent
to Claude until you ask; each rewrite is one Claude request. Drafts up to 12,000 characters.

## Accessories

Blip holds one accessory at a time (right-click → **Accessory**). By default it
**rotates**: every few minutes it hops and swaps to a different one.

- **Laptop:** open on the floor beside Blip, which leans over and types; tucked shut
  under its arm while walking.
- **Phone:** held up, with notification cards on its screen.
- **Music player:** wired to its headphones, with a little equaliser.
- **Coffee mug:** with steam rising.

While walking, Blip carries it out ahead in its leading hand and swings the other arm.
It also picks one up when it fits the moment: the laptop while it's working on something,
the phone when Claude Code needs you, the music player while it dances. Your choice is
remembered in `blip_settings.json`.

**Faces:** normal, happy, love, excited, wink, smug, curious, thinking, surprised,
worried, sad, crying, angry, dizzy, sleeping and loading.

Every 25–70 seconds it does something on its own:

- **Thinks** (dots over its head), then shares an AI thought
- **Glitches**, then apologizes for what it hallucinated
- **Naps** because it's "rate limited"
- **Dances**
- **Installs a pointless update** (with a progress bar)
- **Loads** with spinning eyes
- **Rides a skateboard** across the screen
- **Takes a corner break**: strolls to a bottom corner, sits with its back against the
  screen's edge and dozes (Zzz, wakes if your mouse comes near) or thinks, then gets up
  (also in **Talk to me → Take a corner break**)
- **Moonwalks**: faces one way and glides the other, up on its toes (also in **Talk to me → Moonwalk for me**)
- **Pulls a face** (heart eyes, a wink, a scowl, tears...) and sometimes explains it
- **Offers help nobody asked for**: "It looks like you're...", with
  **Yes please!** and **No thanks** buttons

Tick **Quiet mode** in the right-click menu to stop the random antics.

## Skills: add your own moves

Blip can learn new dances, moves and routines without an update. Each one is a small JSON
file: drop it in `my_skills` (right-click Blip, **Skills**, **Open my skills folder**) and
Blip picks it up while running. It comes with **The Robot**, **Disco**, **Floss**,
**Big wave** and **Stretch break**. A skill can run from the menu, at random, on a timer, at
a time of day or when Claude Code finishes. Skills are data, never code.
See [docs/skills.md](docs/skills.md) to write one, or ask Claude to write it for you.

## Updates

Blip keeps itself up to date from this repo's
[GitHub releases](https://github.com/pramodkumar3901/Desktop_Assistant/releases). Shortly
after it starts, and every 6 hours after that, it checks for a newer release:

1. It says the new version is out and downloads it, with a progress bar over its laptop
   (click Blip to see how far it's got).
2. It waits until you're not busy: no draft, Claude session, mini Blips or open menu.
3. It says it's installing, walks out through a door, swaps in the new files and
   restarts.
4. It walks back in through a door saying which version it is now, with the release's
   first note.

The download is checked before anything is replaced, and the old files are kept in
`.update_backup/`. Your settings are never touched. If the folder is a **git clone**, Blip
fast-forwards it to the release tag instead, but only when it's on `main` with no changes
of yours. Otherwise it just tells you a new version is out, with a link to what's new.

Right-click Blip → **Updates** shows the version, turns **Update automatically** off or on
and has **Check for updates now**.

**Making a release:** bump `VERSION` near the top of `blip.pyw`, merge it, then publish a
release tagged to match:

```
gh release create v1.1.0 --title "Blip 1.1.0" --notes "- What changed, first line is what Blip says"
```

## Needs

- Windows and Python 3 (standard library only, nothing to install)
- The `claude` command, signed in

## About the lines

- Claude writes them, through `claude -p` with tools and customizations turned off.
- One call fetches 4 lines of each kind, plus 3 for each reaction (after a moonwalk, a
  parachute landing, waking up, walking in through the door...), in about 30–40 seconds.
  Until they arrive, reactions use built-in lines.
- **Humour** (right-click → **Talk to me → Humour**): Gentle (the default), Nerdy, Absurd,
  Dry, Punny, or **Mixed**, which picks a style at random for each line and sometimes blends
  two. Changing it fetches a fresh batch and tells you a joke in the new style.
- Blip remembers the last 60 things it said (`blip_recent.json`) and asks Claude not to
  repeat them or reuse their jokes, and drops any line that does.
- A call happens at startup and when you ask for a line that has run out.
  Random antics only trigger one at most every 10 minutes; in between they
  fall back to built-in lines. These calls count against your Claude usage.
- For these lines, the only things sent are the day and time, the humour style and Blip's own recent lines. Blip does not
  read your screen or keyboard; it reads the clipboard only when you ask for a rewrite.
- The model is `claude-opus-5-5`. Set the `BLIP_MODEL` environment variable to
  use another one.
- If a call fails, Blip says so and writes the reason to `blip.log`.

## Claude Code

Right-click Blip → **Claude Code** → **Connected to Claude Code**. This works for Claude
Code in the terminal and in the desktop app (both read the same settings). Once connected:

- **Working:** while Claude works on your prompt, Blip types on its laptop.
- **Done:** Blip hops and says which project is ready.
- **Needs you:** Blip waves its phone for 25 seconds when a session asks permission or
  waits for your answer.
- Each card says where it came from: **Terminal**, **Desktop app** or **VS Code**.
- **Claude can talk through Blip:** ask Claude things like "ping me through Blip when the
  tests pass". New sessions are told how, and run `blip_say.py`. You can run it yourself
  too: `python blip_say.py "Lunch!"`.

**Mini Blips (one per session).** When more than one session is working at once, Blip
takes the first and calls in a small clone of itself for each extra one (up to 6), which
walks in through a door at the nearer corner. A clone sits beside Blip typing on its laptop; click it to see its project and how long
it's been working. When its session needs you, the clone waves its phone. When the
session finishes, the clone tells you, hangs around for a few seconds, then walks out
through a door at the nearer corner. Right-click a clone to send it home early. Turn the feature off
with **Claude Code → A mini Blip for each extra session**; Blip then reports every
session itself.

The same menu has **Show alerts** (mute without disconnecting), **What can you do with
Claude Code?** and **Send a test alert**.

How it works:

- Connecting adds `blip_hook.py` hooks to `~/.claude/settings.json` (UserPromptSubmit,
  Stop, Notification, SessionStart, SessionEnd) and leaves every other setting and hook
  alone. Disconnecting removes only Blip's hooks. Before each change the old file is
  saved as `settings.json.blip-backup`.
- New sessions pick up the change; sessions already open may need a restart.
- The hooks pass the event to Blip on this PC only. They run in the background (the
  SessionStart one takes a moment) and do nothing if Blip isn't running.
- Blip writes its random port and a secret token to `blip_alerts.json`; only a message
  with that token is accepted.

## Screens

Blip walks along the bottom of every screen, just above the taskbar, turned three-quarters
toward where it's going (it turns back to face you when it stops). At an edge shared
with another screen it leaps across and lands on that screen's floor; at an outer edge it
hops and turns around. You can also drag it onto another screen. It resizes to match each
screen's display scaling, and notices screens being plugged in or rearranged.
