from collections.abc import Sequence
from functools import lru_cache
from typing import Final, TypedDict

import phzipcodes  # type: ignore
from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from phzipcodes import ZipCode

from app.config import settings

# Router and template configuration
router = APIRouter()
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

# Cache Configuration
CACHE_SIZE: Final[int] = 256
CACHE_REGIONS: Final[int] = 128


# Type Definitions
class Municipality(TypedDict):
    name: str  # City or Municipality
    zipcode: str  # Zipcode
    province: str


# Cache-enabled data access functions
@lru_cache(maxsize=CACHE_REGIONS)
def get_regions() -> list[str]:
    """Retrieve and cache list of regions."""
    return phzipcodes.get_regions()


@lru_cache(maxsize=CACHE_SIZE)
def get_provinces(region: str) -> list[str]:
    """Retrieve and cache list of provinces for a region."""
    return phzipcodes.get_provinces(region)


def format_municipalities(results: Sequence[ZipCode]) -> list[Municipality]:
    """Format and sort municipality results."""
    return sorted(
        [
            Municipality(name=r.city_municipality, province=r.province, zipcode=r.code)
            for r in results
            if r.city_municipality and r.province
        ],
        key=lambda x: x["name"],
    )


# View Routes
@router.get("/sitemap.xml")
async def sitemap():
    """Serve sitemap.xml file."""
    return FileResponse(
        settings.STATIC_DIR / "sitemap.xml", media_type="application/xml"
    )


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> Response:
    """Render home page."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/search", response_class=HTMLResponse)
async def search_zipcodes(
    request: Request, q: str = Query(default="", min_length=2, max_length=50)
) -> HTMLResponse:
    """Search zipcodes by query string."""
    results: list[ZipCode] = []
    if q:
        if q.isdigit():
            zipcode = phzipcodes.find_by_zip(q)
            results = [zipcode] if zipcode else []
        else:
            results = list(phzipcodes.search(q))

    return templates.TemplateResponse(
        "partials/results.html",
        {"request": request, "results": results},
        headers={"Cache-Control": "private, max-age=0"},
    )


@router.get("/regions", response_class=HTMLResponse)
async def regions_page(request: Request) -> Response:
    """Render regions page."""
    regions: list[str] = get_regions()
    return templates.TemplateResponse(
        "regions.html",
        {"request": request, "regions": regions},
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/regions/search", response_class=HTMLResponse)
async def search_regions(
    request: Request, q: str = Query(default="", max_length=50)
) -> HTMLResponse:
    """Search regions by query string."""
    regions: list[str] = get_regions()
    if q:
        regions = [r for r in regions if q.lower() in r.lower()]
    return templates.TemplateResponse(
        "partials/regions_grid.html", {"request": request, "regions": regions}
    )


@router.get("/provinces", response_class=HTMLResponse)
async def provinces_page(request: Request, region: str = Query(default="")) -> Response:
    """Render provinces page."""
    provinces: set[str] = set()
    regions: list[str] = get_regions()

    if region and region not in regions:
        raise HTTPException(status_code=404, detail="Region not found")

    if region:
        provinces.update(get_provinces(region))
    else:
        for r in regions:
            provinces.update(p for p in get_provinces(r) if p)

    return templates.TemplateResponse(
        "provinces.html",
        {
            "request": request,
            "provinces": provinces,
            "regions": regions,
            "selected_region": region,
        },
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/provinces/search", response_class=HTMLResponse)
async def search_provinces(
    request: Request,
    q: str = Query(default="", max_length=50),
    region: str = Query(default=""),
) -> HTMLResponse:
    """Search provinces by query string and region."""
    provinces: set[str] = set()

    if region:
        provinces.update(get_provinces(region))
    else:
        for r in get_regions():
            provinces.update(p for p in get_provinces(r) if p)

    if q:
        provinces = {p for p in provinces if q.lower() in p.lower()}

    return templates.TemplateResponse(
        "partials/provinces_grid.html", {"request": request, "provinces": provinces}
    )


@router.get("/municipalities", response_class=HTMLResponse)
async def municipalities_page(
    request: Request, province: str = Query(default="")
) -> Response:
    """Render municipalities page."""
    results: Sequence[ZipCode] = phzipcodes.search("")
    municipalities: list[Municipality] = format_municipalities(results)
    provinces: set[str] = {m["province"] for m in municipalities}

    if province:
        municipalities = [m for m in municipalities if m["province"] == province]

    return templates.TemplateResponse(
        "municipalities.html",
        {
            "request": request,
            "municipalities": municipalities,
            "provinces": sorted(provinces),
            "selected_province": province,
        },
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/municipalities/search", response_class=HTMLResponse)
async def search_municipalities(
    request: Request,
    q: str = Query(default="", max_length=50),
    province: str = Query(default=""),
) -> HTMLResponse:
    """Search municipalities by query string and province."""
    results: Sequence[ZipCode] = phzipcodes.search(q) if q else phzipcodes.search("")

    if province:
        results = [r for r in results if r.province == province]

    municipalities: list[Municipality] = format_municipalities(results)

    return templates.TemplateResponse(
        "partials/municipalities_grid.html",
        {"request": request, "municipalities": municipalities},
    )


@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request) -> Response:
    """Render contact page."""
    return templates.TemplateResponse(
        "contact.html",
        {"request": request},
        headers={"Cache-Control": "public, max-age=86400"},
    )
