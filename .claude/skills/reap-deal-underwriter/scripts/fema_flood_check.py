#!/usr/bin/env python3
"""
fema_flood_check.py -- verify physical/environmental risk claims
(claim-verification.md category 6) against FEMA's National Flood Hazard
Layer (NFHL), instead of trusting an OM's silence or narrative on flood risk.

Usage:
    python fema_flood_check.py --address "7746 Menomonee River Parkway, Wauwatosa, WI"
    python fema_flood_check.py --lat 43.0642 --lon -88.0201

Two free, unauthenticated public services, chained:
    1. Census Geocoder  -- address -> lat/lon (skip with --lat/--lon directly)
    2. FEMA NFHL MapServer, "Flood Hazard Zones" layer (28) -- point -> zone

No feature returned at a point does not necessarily mean "no flood risk" --
NFHL layer 28 is built from mapped Special Flood Hazard Areas (SFHAs); an
unmapped location can be genuine low-risk Zone X, or simply outside current
NFHL digitized coverage. This script reports that distinction explicitly
rather than silently treating "no feature" as "no risk."
"""
import argparse
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _http import VerificationError, emit, fail, get_json, now_iso  # noqa: E402

GEOCODER_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
NFHL_FLOOD_ZONES_QUERY_URL = "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer/28/query"

# FLD_ZONE codes where SFHA_TF == 'T' (Special Flood Hazard Area, i.e. the
# 100-year/1%-annual-chance floodplain) vs. minimal-risk zones.
HIGH_RISK_HINT = "Special Flood Hazard Area (1% annual chance / '100-year' floodplain)"
MINIMAL_RISK_HINT = "outside the mapped Special Flood Hazard Area"


def geocode(address):
    params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "format": "json",
    }
    data = get_json(GEOCODER_URL, params=params)
    matches = data.get("result", {}).get("addressMatches") or []
    if not matches:
        raise VerificationError(f"Census Geocoder found no match for address '{address}'")
    coords = matches[0]["coordinates"]
    return coords["y"], coords["x"], matches[0].get("matchedAddress", address)  # lat, lon


def query_flood_zone(lat, lon):
    params = {
        "geometry": f"{lon},{lat}",
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "FLD_ZONE,ZONE_SUBTY,SFHA_TF",
        "returnGeometry": "false",
        "f": "json",
    }
    data = get_json(NFHL_FLOOD_ZONES_QUERY_URL, params=params)
    if "error" in data:
        raise VerificationError(f"FEMA NFHL query error: {data['error']}")
    return data.get("features") or []


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--address", help="Street address to geocode then check")
    parser.add_argument("--lat", type=float, help="Latitude (skips geocoding)")
    parser.add_argument("--lon", type=float, help="Longitude (skips geocoding)")
    args = parser.parse_args(argv)

    if args.lat is not None and args.lon is not None:
        lat, lon, matched_address = args.lat, args.lon, None
    elif args.address:
        try:
            lat, lon, matched_address = geocode(args.address)
        except VerificationError as exc:
            fail(str(exc), address=args.address)
            return
    else:
        fail("must pass either --address or both --lat and --lon")
        return

    try:
        features = query_flood_zone(lat, lon)
    except VerificationError as exc:
        fail(str(exc), lat=lat, lon=lon)
        return

    result = {
        "address": args.address,
        "matched_address": matched_address,
        "lat": lat,
        "lon": lon,
        "source": "FEMA National Flood Hazard Layer (NFHL)",
        "source_url": "https://msc.fema.gov/portal/search",
        "retrieved_at": now_iso(),
    }

    if not features:
        result.update(
            {
                "sfha": None,
                "flood_zone": None,
                "note": (
                    "No NFHL flood-hazard-zone feature found at this point. This can mean genuine "
                    f"minimal risk (unmapped Zone X) or a gap in NFHL digitized coverage -- {MINIMAL_RISK_HINT}, "
                    "but confirm on the FEMA Flood Map Service Center (msc.fema.gov) before treating "
                    "this as a clean bill of health."
                ),
            }
        )
    else:
        attrs = features[0]["attributes"]
        is_sfha = attrs.get("SFHA_TF") == "T"
        result.update(
            {
                "sfha": is_sfha,
                "flood_zone": attrs.get("FLD_ZONE"),
                "zone_subtype": attrs.get("ZONE_SUBTY"),
                "note": HIGH_RISK_HINT if is_sfha else MINIMAL_RISK_HINT,
            }
        )
        if len(features) > 1:
            result["additional_zones_at_point"] = [
                f["attributes"].get("FLD_ZONE") for f in features[1:]
            ]

    emit(result)


if __name__ == "__main__":
    main()
