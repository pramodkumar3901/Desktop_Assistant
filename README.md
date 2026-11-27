# Blip

A tiny, over-eager AI robot that walks along the bottom of your screen: a 3D
screen-faced robot with glowing eyes, in the spirit of the animated office
assistants of the 90s. It wants very badly to help and almost never does.

![Blip walking with its music player, cheering you on, getting heart eyes, typing a
draft rewrite on its laptop, then splitting off a mini Blip for a second Claude Code
session that reports back and merges in](docs/blip-demo.gif)

**Start and stop:** double-click `blip.pyw` to start it, or right-click Blip and choose
**Bye, Blip (quit)** to close it. `blip_control.pyw` does the rest:

| Command | Does |
| --- | --- |
| `pythonw blip_control.pyw start` | Opens Blip (does nothing if it's already running) |
| `pythonw blip_control.pyw stop` | Closes Blip |
| `pythonw blip_control.pyw restart` | Closes and reopens it, back on the main screen |
| `pythonw blip_control.pyw reset` | Forgets the accessory, size and Quiet mode, then restarts |

For one-click shortcuts, make a Windows shortcut to each command (right-click in the
folder → New → Shortcut, and paste the command with the full path to `blip_control.pyw`).

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
| **Talk to me** | Encourage me, Say something funny, Check in on me, Do something random |
| **Claude Code** | Connected to Claude Code, Show alerts, A mini Blip for each extra session, What can you do?, Send a test alert |
| **Look** | Accessory (Rotate, Nothing, Laptop, Phone, Music player, Coffee mug) and Size (Normal, Medium, Half) |
| **Quiet mode** | No random antics |
| **Bye, Blip (quit)** | Closes Blip |

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

- **Laptop:** open on the floor beside Blip, which leans over and types; carried shut
  under its arm while walking.
- **Phone:** held up, with notification cards on its screen.
- **Music player:** wired to its headphones, with a little equaliser.
- **Coffee mug:** with steam rising.

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
- **Moonwalks**: faces one way and glides the other, up on its toes (also in **Talk to me → Moonwalk for me**)
- **Pulls a face** (heart eyes, a wink, a scowl, tears...) and sometimes explains it
- **Offers help nobody asked for**: "It looks like you're...", with
  **Yes please!** and **No thanks** buttons

Tick **Quiet mode** in the right-click menu to stop the random antics.

## Needs

- Windows and Python 3 (standard library only, nothing to install)
- The `claude` command, signed in

## About the lines

- Claude writes them, through `claude -p` with tools and customizations turned off.
- One call fetches 4 lines of each kind (about 20 seconds).
- A call happens at startup and when you ask for a line that has run out.
  Random antics only trigger one at most every 10 minutes; in between they
  fall back to built-in lines. These calls count against your Claude usage.
- For these lines, the only thing sent about you is the day and time. Blip does not
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
takes the first and pops out a small clone of itself for each extra one (up to 6). A
clone sits beside Blip typing on its laptop; click it to see its project and how long
it's been working. When its session needs you, the clone waves its phone. When the
session finishes, the clone tells you, hangs around for a few seconds, then hurries back
and merges into Blip. Right-click a clone to send it back early. Turn the feature off
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

Blip walks along the bottom of every screen, just above the taskbar. At an edge shared
with another screen it leaps across and lands on that screen's floor; at an outer edge it
hops and turns around. You can also drag it onto another screen. It resizes to match each
screen's display scaling, and notices screens being plugged in or rearranged.
