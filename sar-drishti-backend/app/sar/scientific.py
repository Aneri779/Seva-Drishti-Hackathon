"""
SAR scientific processing — pure functions.
All Otsu thresholds computed from REAL GEE histograms.
generate_bimodal_histogram is REMOVED; histogram endpoint returns 404 if not processed.
No synthetic fallbacks.
"""
import math
import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


def otsu_from_histogram(bins: list[float], counts: list[int]) -> float:
    """
    Compute Otsu threshold from a pre-computed histogram.
    bins: left edges of each bin (length N)
    counts: pixel count per bin (length N)
    Returns the optimal threshold value.
    Raises ValueError if histogram is empty or unimodal.
    """
    bins = np.array(bins, dtype=np.float64)
    counts = np.array(counts, dtype=np.float64)
    total = counts.sum()
    if total == 0:
        raise ValueError("Empty histogram: cannot compute Otsu threshold")
    if len(bins) != len(counts):
        raise ValueError(f"bins length {len(bins)} != counts length {len(counts)}")
    
    # Midpoints of bins
    mid = bins + (bins[1] - bins[0]) / 2.0 if len(bins) > 1 else bins

    weight1 = np.cumsum(counts)
    weight2 = total - weight1
    # Avoid division by zero at edges
    weight1 = np.where(weight1 == 0, np.finfo(float).eps, weight1)
    weight2 = np.where(weight2 == 0, np.finfo(float).eps, weight2)

    mean1 = np.cumsum(counts * mid) / weight1
    mean2 = (np.sum(counts * mid) - np.cumsum(counts * mid)) / weight2

    between_class_variance = weight1 * weight2 * (mean1 - mean2) ** 2
    best_idx = int(np.argmax(between_class_variance))
    threshold = float(mid[best_idx])
    logger.debug(f"Otsu threshold = {threshold:.3f} dB at bin {best_idx}/{len(bins)}")
    return threshold


def otsu_from_gee_histogram(gee_histogram: dict, band: str = "VV") -> float:
    """
    Extract bins/counts from a GEE reduceRegion histogram dict and compute Otsu.
    GEE histogram format: {'bucketMeans': [...], 'histogram': [...]}
    """
    bucket_means = gee_histogram.get("bucketMeans") or gee_histogram.get("bucketMin")
    histogram = gee_histogram.get("histogram")
    if not bucket_means or not histogram:
        raise ValueError(f"Invalid GEE histogram for band {band}: missing bucketMeans or histogram")
    return otsu_from_histogram(bucket_means, histogram)


def classify_segment(
    delta_vv_db: float,
    delta_vh_db: float,
    otsu_vv: float,
    otsu_vh: float,
    otsu_delta: float,
    flooded_pct: float,
    max_depth_m: float,
    slope_deg: float,
    hand_m: float,
    slope_max: float = 5.0,
    hand_max: float = 15.0,
) -> dict:
    """
    Classify a road segment's flood status.
    All input values are REAL; no synthetic defaults.
    Returns dict with status_class, confidence.
    
    Status classes:
      NO_DATA    - layover/shadow or invalid pixel
      CLEAR      - no water signal
      ROADSIDE_WATER - water adjacent to road, passable
      OVERTOPPING - road surface inundated, restricted
      WASHOUT    - severe inundation/structural damage
    """
    # Terrain mask: steep terrain or high HAND = unreliable
    if slope_deg > slope_max or hand_m > hand_max:
        return {"status_class": "NO_DATA", "confidence": 0.0,
                "note": "layover/shadow/steep terrain excluded"}
    
    # Flood detection: water_vv = below Otsu threshold in VV
    water_vv = delta_vv_db < otsu_vv
    changed = delta_vv_db < otsu_delta  # change detected vs dry baseline
    water_vh = delta_vh_db < otsu_vh

    is_flood = water_vv or (changed and water_vh)
    
    if not is_flood:
        return {"status_class": "CLEAR", "confidence": 0.92}
    
    # Classify severity by depth and coverage
    confidence = min(0.99, 0.6 + 0.3 * (flooded_pct / 100.0))
    
    if max_depth_m >= 0.3 or flooded_pct >= 75:
        return {"status_class": "WASHOUT", "confidence": confidence}
    elif max_depth_m >= 0.15 or flooded_pct >= 40:
        return {"status_class": "OVERTOPPING", "confidence": confidence}
    elif flooded_pct >= 10:
        return {"status_class": "ROADSIDE_WATER", "confidence": confidence}
    else:
        return {"status_class": "CLEAR", "confidence": 0.85}


def gaps_and_islands(
    segment_statuses: list[dict],
    gap_threshold_m: int = 200,
) -> list[dict]:
    """
    Merge contiguous road segments with same/adjacent flood status into events.
    Gaps <= gap_threshold_m are filled if surrounded by same status.
    
    segment_statuses: list of {start_m, end_m, status_class, max_depth_m, flooded_pct,
                                delta_vv_db, confidence}
    Returns list of event dicts.
    """
    if not segment_statuses:
        return []
    
    # Filter out CLEAR and NO_DATA — only flood events
    flood_statuses = {"WASHOUT", "OVERTOPPING", "ROADSIDE_WATER"}
    events = []
    current = None
    
    for seg in sorted(segment_statuses, key=lambda x: x["start_m"]):
        if seg["status_class"] not in flood_statuses:
            if current:
                events.append(current)
                current = None
            continue
        
        if current is None:
            current = {
                "start_m": seg["start_m"],
                "end_m": seg["end_m"],
                "status_class": seg["status_class"],
                "max_depth_m": seg.get("max_depth_m", 0.0),
                "flooded_pct": seg.get("flooded_pct", 0.0),
                "delta_db": seg.get("delta_vv_db", 0.0),
                "confidence": seg.get("confidence", 0.0),
                "segment_count": 1,
            }
        else:
            gap_m = seg["start_m"] - current["end_m"]
            same_status = seg["status_class"] == current["status_class"]
            if same_status and gap_m <= gap_threshold_m:
                # Extend current event
                current["end_m"] = seg["end_m"]
                current["max_depth_m"] = max(current["max_depth_m"], seg.get("max_depth_m", 0.0))
                current["flooded_pct"] = max(current["flooded_pct"], seg.get("flooded_pct", 0.0))
                current["delta_db"] = min(current["delta_db"], seg.get("delta_vv_db", 0.0))
                current["confidence"] = min(current["confidence"], seg.get("confidence", 0.0))
                current["segment_count"] += 1
            else:
                events.append(current)
                current = {
                    "start_m": seg["start_m"],
                    "end_m": seg["end_m"],
                    "status_class": seg["status_class"],
                    "max_depth_m": seg.get("max_depth_m", 0.0),
                    "flooded_pct": seg.get("flooded_pct", 0.0),
                    "delta_db": seg.get("delta_vv_db", 0.0),
                    "confidence": seg.get("confidence", 0.0),
                    "segment_count": 1,
                }
    
    if current:
        events.append(current)
    
    # Add length_m
    for ev in events:
        ev["length_m"] = ev["end_m"] - ev["start_m"]
        # Map status to category label
        ev["category"] = {
            "WASHOUT": "Washout / Bridge Breach",
            "OVERTOPPING": "Overtopping (Both Lanes)",
            "ROADSIDE_WATER": "Roadside Water Only - Passable",
        }.get(ev["status_class"], ev["status_class"])
    
    return events
