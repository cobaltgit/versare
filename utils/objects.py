from __future__ import annotations

import re
from datetime import timedelta

import discord


class BaseEmbed(discord.Embed):
    """Base embed class"""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.timestamp = discord.utils.utcnow()


# original code from https://github.com/Sly0511/TroveBot/blob/master/utils/CustomObjects.py#L26-L75
class TimeConverter:
    """Convert human readable time to a datetime object"""

    def __init__(self, input, fuzzy: bool = True) -> None:
        self.fuzzy = fuzzy
        if isinstance(input, (int, float)) or input.isdigit():
            self.seconds = int(input)
        elif isinstance(input, str):
            parts = self._get_time_parts(input)
            result = self._parts_to_int(parts)
            self.seconds = result
        else:
            raise ValueError("Wrong Input")
        self._seconds = self.seconds
        self.delta = timedelta(seconds=self.seconds)

    @property
    def _periods(self) -> dict[str, int]:
        return {
            "year": 31557600 if self.fuzzy else 31536000,
            "month": 2629800 if self.fuzzy else 2592000,
            "week": 604800,
            "day": 86400,
            "hour": 3600,
            "minute": 60,
            "second": 1,
        }

    def _get_time_parts(self, input) -> list[str]:
        regex = r"((?!0)[0-9]+) ?(?:(y(?:ears?)?)|(months?)|(w(?:eeks?)?)|(d(?:ays?)?)|(h(?:ours?)?)|(m(?:inutes?)?)|(s(?:econds?)?))"
        result = re.findall(regex, input, re.IGNORECASE)
        if not result:
            raise ValueError("No time parts detected.")
        return result

    def _parts_to_int(self, parts) -> int:
        seconds = 0
        for part in parts:
            broken_part = part[1:]
            for i in range(len(broken_part)):
                if broken_part[i]:
                    seconds += int(part[0]) * list(self._periods.values())[i]
        return seconds

    def _naturaldelta(self) -> list[str]:
        strings = []
        used_units = []
        for name, value in self._periods.items():
            if self._seconds < value:
                continue
            if len(used_units) == 3:
                break
            used_units.append(name)
            time, self._seconds = divmod(self._seconds, value)
            strings.append(f"{time} {name}" + ("s" if time != 1 else ""))
        return strings

    def __str__(self) -> str:
        return ", ".join(self._naturaldelta())
