#!/usr/bin/env python3
"""One Euro Filter — Casiez et al. https://github.com/casiez/OneEuroFilter"""
from __future__ import annotations

import math


def _alpha(cutoff: float, dt: float) -> float:
    tau = 1.0 / (2.0 * math.pi * cutoff)
    return 1.0 / (1.0 + tau / dt)


class LowPassFilter:
    def __init__(self) -> None:
        self.hatx: float | None = None

    def filter(self, x: float, alpha: float) -> float:
        if self.hatx is None:
            self.hatx = x
            return x
        self.hatx = alpha * x + (1.0 - alpha) * self.hatx
        return self.hatx

    def reset(self) -> None:
        self.hatx = None


class OneEuroFilter:
    def __init__(self, mincutoff: float = 1.0, beta: float = 0.007, dcutoff: float = 1.0) -> None:
        self.mincutoff = float(mincutoff)
        self.beta = float(beta)
        self.dcutoff = float(dcutoff)
        self.x_filt = LowPassFilter()
        self.dx_filt = LowPassFilter()
        self.last_t: float | None = None
        self.last_x: float | None = None

    def reset(self) -> None:
        self.x_filt.reset()
        self.dx_filt.reset()
        self.last_t = None
        self.last_x = None

    def __call__(self, t: float, x: float) -> float:
        if self.last_t is None or self.last_x is None:
            self.last_t = t
            self.last_x = x
            self.x_filt.filter(x, 1.0)
            self.dx_filt.filter(0.0, 1.0)
            return x
        dt = t - self.last_t
        if dt <= 0:
            dt = 1e-6
        dx = (x - self.last_x) / dt
        edx = self.dx_filt.filter(dx, _alpha(self.dcutoff, dt))
        cutoff = self.mincutoff + self.beta * abs(edx)
        hatx = self.x_filt.filter(x, _alpha(cutoff, dt))
        self.last_t = t
        self.last_x = x
        return hatx
