"""Resolve local .env and shell overrides into the effective model settings."""
import os
import math
from copy import deepcopy

from dotenv import load_dotenv

from .common import ROOT, read_json


def _number(name, default, cast, minimum=None, maximum=None):
    raw = os.getenv(name)
    value = default if raw is None or raw == "" else cast(raw)
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("%s must be finite" % name)
    if minimum is not None and value < minimum or maximum is not None and value > maximum:
        raise ValueError("%s must be between %s and %s" % (name, minimum, maximum))
    return value


def model_settings():
    # Existing shell values win; .env only supplies values that are unset.
    load_dotenv(ROOT / ".env", override=False)
    config = deepcopy(read_json(ROOT / "config/models.json"))
    for alias, model in config["models"].items():
        key = alias.upper()
        model["id"] = os.getenv("FOLKLORE_%s_MODEL" % key) or model["id"]
        if "reasoning_effort" in model:
            effort = os.getenv("FOLKLORE_%s_REASONING_EFFORT" % key) or model["reasoning_effort"]
            if effort not in ("low", "medium", "high", "xhigh", "max"):
                raise ValueError("FOLKLORE_%s_REASONING_EFFORT is not supported" % key)
            model["reasoning_effort"] = effort
        if "thinking_level" in model:
            level = os.getenv("FOLKLORE_%s_THINKING_LEVEL" % key) or model["thinking_level"]
            if level not in ("low", "medium", "high"):
                raise ValueError("FOLKLORE_%s_THINKING_LEVEL must be low, medium, or high" % key)
            model["thinking_level"] = level
    generation = config["generation"]
    generation["max_tokens"] = _number("FOLKLORE_MAX_TOKENS", generation["max_tokens"], int, minimum=1)
    generation["temperature"] = _number("FOLKLORE_TEMPERATURE", generation["temperature"], float, minimum=0, maximum=1)
    transport = config["transport"]
    transport["max_attempts"] = _number("FOLKLORE_MAX_ATTEMPTS", transport["max_attempts"], int, minimum=1)
    transport["initial_backoff_seconds"] = _number("FOLKLORE_INITIAL_BACKOFF_SECONDS", transport["initial_backoff_seconds"], float, minimum=0)
    transport["timeout_seconds"] = _number("FOLKLORE_TIMEOUT_SECONDS", transport["timeout_seconds"], float, minimum=1)
    return config
