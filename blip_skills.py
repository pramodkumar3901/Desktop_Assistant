"""Blip's skills: new moves, dances and routines described in JSON files.

A skill is data, never code: it can only combine the things listed here, so adding
one can't harm the PC. Blip reads the files again whenever they change, so a new or
edited skill works without restarting or updating Blip.

Two folders are read:
  skills/      the ones that come with Blip (updates may change them)
  my_skills/   yours; never touched by updates, and wins over a same-named one

docs/skills.md describes the file format.
"""

import json
import math
import re
from pathlib import Path

MAX_BYTES = 64 * 1024
MAX_SKILLS = 60
MAX_STEPS = 30
MAX_KEYS = 80
MAX_TEXT = 200
MAX_SECONDS = 90          # one move, all its repeats included
BLEND = 0.25              # seconds to ease into and out of a move

# Pose channels a keyframe can set, with their limits. Distances are in Blip's own
# units (it is about 105 tall), so a move looks the same at every size.
NUMBERS = {
    "x": (-300, 300),     # travel along the floor; positive is the way Blip faces
    "lift": (0, 90),      # height off the floor
    "sway": (-20, 20),    # slide the body without moving its spot
    "tilt": (-30, 30),    # head tilt, degrees; positive is to the right
    "roll": (-28, 28),    # the whole body leaning from the feet, degrees
    "turn": (-1, 1),      # turned three-quarters: -1 away from the way it faces
    "squat": (0, 1),      # 0 standing, 1 crouched right down
}
PAIRS = {
    # feet: [sideways, height off the floor]; positive sideways is to the right
    "foot_left": ((-22, 22), (0, 18)),
    "foot_right": ((-22, 22), (0, 18)),
    # hands: [outward from the shoulder, upward from the shoulder]
    "hand_left": ((-16, 52), (-16, 48)),
    "hand_right": ((-16, 52), (-16, 48)),
}
HAND_REST = (6.0, -11.0)

FACES = ("normal", "happy", "excited", "love", "wink", "smug", "curious", "angry",
         "cry", "dizzy", "surprised", "sad", "worried", "sleep", "think", "talk",
         "spin", "glitch")
EFFECTS = ("music", "sparkles", "hearts", "zzz")
ACTS = ("think", "glitch", "nap", "dance", "update", "spin", "skate", "moonwalk", "lean")
EVENTS = ("done", "prompt")  # Claude Code: a task finished / you sent a prompt


class SkillError(ValueError):
    """What's wrong with a skill file, in words for whoever wrote it."""


def number(value, low, high, what):
    if isinstance(value, bool) or not isinstance(value, (int, float)) \
            or not math.isfinite(value):
        raise SkillError(f"{what} must be a number")
    return float(min(high, max(low, value)))


def text(value, what, limit=MAX_TEXT):
    if not isinstance(value, str) or not value.strip():
        raise SkillError(f"{what} must be some text")
    return value.strip()[:limit]


def choice(value, allowed, what):
    if value not in allowed:
        raise SkillError(f"{what} {value!r} is not one of: {', '.join(allowed)}")
    return value


def only(table, allowed, what):
    if not isinstance(table, dict):
        raise SkillError(f"{what} must be a {{...}} block")
    unknown = sorted(set(table) - set(allowed))
    if unknown:
        raise SkillError(f"{what} has unknown entries: {', '.join(unknown)}")
    return table


class Move:
    """A keyframed animation: poses at set times, smoothly joined, maybe repeated."""

    def __init__(self, data):
        only(data, ("length", "repeat", "face", "effect", "prop", "keys"), "a move")
        self.length = number(data.get("length", 1.0), 0.2, 30, "length")
        self.repeat = int(number(data.get("repeat", 1), 1, 40, "repeat"))
        self.seconds = min(MAX_SECONDS, self.length * self.repeat)
        self.face = None
        if data.get("face") is not None:
            self.face = choice(data["face"], FACES, "face")
        self.effect = None
        if data.get("effect") is not None:
            self.effect = choice(data["effect"], EFFECTS, "effect")
        self.prop = bool(data.get("prop", False))  # keep holding the accessory
        keys = data.get("keys")
        if not isinstance(keys, list) or not 1 <= len(keys) <= MAX_KEYS:
            raise SkillError(f"a move needs 1 to {MAX_KEYS} keys")
        self.tracks = {}  # channel -> [(time, value or (a, b))]
        self.faces = []   # [(time, face)]
        for key in keys:
            only(key, ("t", "face", *NUMBERS, *PAIRS), "a key")
            t = number(key.get("t"), 0, self.length, "a key's t")
            if "face" in key:
                self.faces.append((t, choice(key["face"], FACES, "face")))
            for name, value in key.items():
                if name in NUMBERS:
                    value = number(value, *NUMBERS[name], name)
                elif name in PAIRS:
                    if not isinstance(value, list) or len(value) != 2:
                        raise SkillError(f"{name} must be two numbers, like [6, -11]")
                    value = tuple(number(v, *limits, name)
                                  for v, limits in zip(value, PAIRS[name]))
                else:
                    continue
                self.tracks.setdefault(name, []).append((t, value))
        for track in self.tracks.values():
            track.sort(key=lambda item: item[0])
        self.faces.sort()

    def value(self, name, t):
        """The channel at time t within one cycle. A cycle runs on into the next, so
        after the last key it heads back toward the first."""
        track = self.tracks[name]
        if len(track) == 1:
            return track[0][1]
        points = ([(track[-1][0] - self.length, track[-1][1])] + track
                  + [(track[0][0] + self.length, track[0][1])])
        for (t0, a), (t1, b) in zip(points, points[1:]):
            if t0 <= t < t1:
                k = (t - t0) / (t1 - t0)
                k = 0.5 - 0.5 * math.cos(math.pi * k)  # ease in and out
                if isinstance(a, tuple):
                    return tuple(x + (y - x) * k for x, y in zip(a, b))
                return a + (b - a) * k
        return track[-1][1]

    def travelled(self, elapsed, done):
        """How far earlier cycles took Blip. A cycle whose x has a key at its start
        and one at its end carries on from where the last one finished."""
        track = self.tracks["x"]
        if track[0][0] > 0 or track[-1][0] < self.length:
            return 0.0
        cycles = (math.ceil(self.seconds / self.length) - 1 if done
                  else int(elapsed // self.length))
        return cycles * (track[-1][1] - track[0][1])

    def pose(self, elapsed):
        """Every channel the move uses at `elapsed` seconds, eased in and out, plus
        "face". Travel (x) is exempt from the easing, so Blip stays where it got to."""
        elapsed = min(max(elapsed, 0.0), self.seconds)
        done = elapsed >= self.seconds
        t = self.length if done else elapsed % self.length
        weight = min(1.0, elapsed / BLEND, max(0.0, self.seconds - elapsed) / BLEND)
        pose = {}
        for name in self.tracks:
            value = self.value(name, t)
            if name == "x":
                pose[name] = value + self.travelled(elapsed, done)
            elif name.startswith("hand"):
                pose[name] = tuple(r + (v - r) * weight for r, v in zip(HAND_REST, value))
            elif name in PAIRS:
                pose[name] = tuple(v * weight for v in value)
            else:
                pose[name] = value * weight
        face = self.face
        for at, name in self.faces:
            if t >= at:
                face = name
        if face:
            pose["face"] = face
        return pose


class Skill:
    """One skill file: a name, when to run it by itself, and its steps."""

    def __init__(self, data, source="skill", library=None):
        only(data, ("name", "when", "moves", "do"), "the skill")
        self.name = text(data.get("name"), "name", 40)
        self.source = source
        self.moves = {}
        moves = data.get("moves") or {}
        if not isinstance(moves, dict):
            raise SkillError("moves must be a {...} block")
        for key, move in moves.items():
            self.moves[key] = Move(move)
        when = only(data.get("when") or {}, ("random", "every_minutes", "at", "claude"),
                    "when")
        self.random = (number(when["random"], 0, 5, "random")
                       if "random" in when else 0.0)
        self.every = (number(when["every_minutes"], 1, 24 * 60, "every_minutes") * 60
                      if "every_minutes" in when else None)
        self.at = None
        if "at" in when:
            found = re.fullmatch(r"([01]?\d|2[0-3]):([0-5]\d)", str(when["at"]))
            if not found:
                raise SkillError('at must be a time like "17:30"')
            self.at = f"{int(found[1]):02}:{found[2]}"
        self.claude = (choice(when["claude"], EVENTS, "claude")
                       if "claude" in when else None)
        steps = data.get("do")
        if not isinstance(steps, list) or not 1 <= len(steps) <= MAX_STEPS:
            raise SkillError(f'"do" needs a list of 1 to {MAX_STEPS} steps')
        self.steps = [self.step(step) for step in steps]

    def step(self, data):
        """Check one step; return (kind, value, options)."""
        kinds = ("move", "act", "mood", "say", "jump", "wait", "turn_around")
        only(data, kinds + ("seconds", "link"), "a step")
        found = [k for k in kinds if k in data]
        if len(found) != 1:
            raise SkillError(f"each step needs exactly one of: {', '.join(kinds)}")
        kind, value, options = found[0], data[found[0]], {}
        if "seconds" in data:
            options["seconds"] = number(data["seconds"], 0.5, 30, "seconds")
        if "link" in data:
            link = only(data["link"], ("label", "url"), "link")
            url = text(link.get("url"), "the link's url", 500)
            if kind != "say" or not re.match(r"https?://", url, re.I):
                raise SkillError("a link goes with say, and must start with http(s)://")
            options["link"] = (text(link.get("label"), "the link's label", 24), url)
        if kind == "move":
            if isinstance(value, str):
                if value not in self.moves:
                    raise SkillError(f"there is no move called {value!r} in this file")
                value = self.moves[value]
            else:
                value = Move(value)
        elif kind == "act":
            choice(value, ACTS, "act")
        elif kind == "mood":
            choice(value, FACES, "mood")
        elif kind == "say":
            lines = value if isinstance(value, list) else [value]
            if not 1 <= len(lines) <= 30:
                raise SkillError("say needs 1 to 30 lines to pick from")
            value = [text(line, "a line to say") for line in lines]
        elif kind == "wait":
            value = number(value, 0.1, 30, "wait")
        return kind, value, options


class Library:
    """The skills on disk, read again whenever a file is added, changed or removed."""

    def __init__(self, folders):
        self.folders = [Path(f) for f in folders]
        self.skills = {}    # name -> Skill
        self.problems = {}  # file name -> what's wrong with it
        self.stamp = None

    def files(self):
        found = []
        for folder in self.folders:
            try:
                found.extend(sorted(folder.glob("*.json")))
            except OSError:
                pass
        return found

    def refresh(self):
        """Reload if anything changed. True when it did."""
        files = self.files()
        stamp = []
        for path in files:
            try:
                info = path.stat()
            except OSError:
                continue
            stamp.append((str(path), info.st_mtime_ns, info.st_size))
        if stamp == self.stamp:
            return False
        self.stamp = stamp
        skills, problems = {}, {}
        for path in files:
            try:
                if path.stat().st_size > MAX_BYTES:
                    raise SkillError("the file is too big")
                data = json.loads(path.read_text(encoding="utf-8-sig"))
                skill = Skill(data, source=str(path))
                if skill.name not in skills and len(skills) >= MAX_SKILLS:
                    raise SkillError(f"only {MAX_SKILLS} skills fit")
                skills[skill.name] = skill  # a later folder wins
            except (OSError, ValueError, TypeError, RecursionError) as error:
                problems[f"{path.parent.name}/{path.name}"] = str(error)
        self.skills, self.problems = skills, problems
        return True
