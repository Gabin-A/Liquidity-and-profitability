import math
from dataclasses import dataclass
from typing import Optional


import numpy as np
import pandas as pd
import streamlit as st


# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(
page_title="Economies-of-Scale Growth Simulator",
page_icon="📈",
layout="wide",
)


# ---------------------- DEFAULTS & UTILS -----------------


def default_anchors() -> pd.DataFrame:
"""Return default anchors used when no CSV is uploaded."""
return pd.DataFrame({
"Units_Anchor": [1, 20, 50],
"PerUnitMargin": [2500.0, 2500.0, 4200.0],
})


@dataclass
class SimParams:
unit_cost: float
starting_cash: float
overhead_per_month: float
horizon_months: int
max_new_units_per_month: Optional[int]
hold_flat_above_max: bool
lead_time_months: int = 0 # units purchased activate after this many months


@dataclass
class SimResult:
monthly: pd.DataFrame
milestones: pd.DataFrame




def normalize_anchors(df: pd.DataFrame) -> pd.DataFrame:
if "Units_Anchor" not in df.columns or "PerUnitMargin" not in df.columns:
raise ValueError("Anchors must have columns: Units_Anchor, PerUnitMargin")
df = df.dropna(subset=["Units_Anchor", "PerUnitMargin"]).copy()
df["Units_Anchor"] = df["Units_Anchor"].astype(int)
df["PerUnitMargin"] = df["PerUnitMargin"].astype(float)
df = df.sort_values("Units_Anchor").drop_duplicates("Units_Anchor", keep="last")
if df.empty:
raise ValueError("Provide at least one anchor row.")
return df.reset_index(drop=True)




def per_unit_margin_from_anchors(units: int, anchors: pd.DataFrame, hold_flat: bool) -> float:
"""Piecewise-linear interpolation of per-unit margin as a function of fleet size."""
U = anchors["Units_Anchor"].to_numpy()
M = anchors["PerUnitMargin"].to_numpy()


# Below minimum
if units <= U[0]:
return float(M[0])


# Between anchors
for i in range(len(U) - 1):
if U[i] <= units <= U[i + 1]:
u0, m0 = U[i], M[i]
u1, m1 = U[i + 1], M[i + 1]
if u1 == u0:
return float(m1)
w = (units - u0) / (u1 - u0)
return float(m0 * (1 - w) + m1 * w)


# Above maximum
if hold_flat:
return float(M[-1])


# Extrapolate using last slope if possible, else flat
if len(U) >= 2 and (U[-1] - U[-2]) != 0:
slope = (M[-1] - M[-2]) / (U[-1] - U[-2])
return float(M[-1] + slope * (units - U[-1]))
return float(M[-1])




st.exception(e)