from collections.abc import Sequence
from typing import TypedDict

import phzipcodes
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from phzipcodes import ZipCode

from app.config import settings

router = APIRouter()
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


class Municipality(TypedDict):
    name: str
    zipcode: str
    province: str


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Render home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/search", response_class=HTMLResponse)
async def search_zipcodes(request: Request, q: str = "") -> HTMLResponse:
    """Search zipcodes by query string."""
    results: list[ZipCode] = []
    if q:
        if q.isdigit():
            zipcode = phzipcodes.find_by_zip(q)
            if zipcode:
                results = [zipcode]
        else:
            results = list(phzipcodes.search(q))

    return templates.TemplateResponse(
        "partials/results.html",
        {"request": request, "results": results},
    )


@router.get("/regions", response_class=HTMLResponse)
async def regions_page(request: Request) -> HTMLResponse:
    """Render regions page with all Philippine regions."""
    regions: list[str] = phzipcodes.get_regions()
    return templates.TemplateResponse(
        "regions.html",
        {
            "request": request,
            "regions": regions,
        },
    )


@router.get("/regions/search", response_class=HTMLResponse)
async def search_regions(request: Request, q: str = "") -> HTMLResponse:
    """Search and filter regions."""
    regions: list[str] = phzipcodes.get_regions()
    if q:
        regions = [r for r in regions if q.lower() in r.lower()]
    return templates.TemplateResponse(
        "partials/regions_grid.html", {"request": request, "regions": regions}
    )


@router.get("/provinces", response_class=HTMLResponse)
async def provinces_page(request: Request, region: str = "") -> HTMLResponse:
    """Render provinces page with all Philippine provinces."""
    provinces: list[str] = []
    regions = phzipcodes.get_regions()

    if region:
        provinces = phzipcodes.get_provinces(region)
    else:
        for r in regions:
            provinces.extend(p for p in phzipcodes.get_provinces(r) if p)

    return templates.TemplateResponse(
        "provinces.html",
        {
            "request": request,
            "provinces": set(provinces),
            "regions": regions,
        },
    )


@router.get("/provinces/search", response_class=HTMLResponse)
async def search_provinces(
    request: Request, q: str = "", region: str = ""
) -> HTMLResponse:
    """Search and filter provinces by name and region."""
    provinces: list[str] = []

    if region:
        provinces = phzipcodes.get_provinces(region)
    else:
        for r in phzipcodes.get_regions():
            provinces.extend(p for p in phzipcodes.get_provinces(r) if p)

    if q:
        provinces = [p for p in provinces if q.lower() in p.lower()]

    return templates.TemplateResponse(
        "partials/provinces_grid.html",
        {"request": request, "provinces": set(provinces)},
    )


@router.get("/municipalities", response_class=HTMLResponse)
async def municipalities_page(request: Request, province: str = "") -> HTMLResponse:
    """Render municipalities page with all cities and municipalities."""
    municipalities: list[Municipality] = []
    provinces: list[str] = []

    results: Sequence[ZipCode] = phzipcodes.search("")

    for result in results:
        if result.city_municipality and result.province:
            municipalities.append(
                {
                    "name": result.city_municipality,
                    "zipcode": result.code,
                    "province": result.province,
                }
            )
            provinces.append(result.province)

    if province:
        municipalities = [m for m in municipalities if m["province"] == province]

    municipalities.sort(key=lambda x: x["name"])
    provinces = sorted(set(provinces))

    return templates.TemplateResponse(
        "municipalities.html",
        {
            "request": request,
            "municipalities": municipalities,
            "provinces": provinces,
            "selected_province": province,
        },
    )


@router.get("/municipalities/search", response_class=HTMLResponse)
async def search_municipalities(
    request: Request, q: str = "", province: str = ""
) -> HTMLResponse:
    """Search and filter municipalities by name and province."""
    results: Sequence[ZipCode] = phzipcodes.search(q) if q else phzipcodes.search("")

    if province:
        results = [r for r in results if r.province == province]

    municipalities: list[Municipality] = [
        {
            "name": r.city_municipality,
            "province": r.province,
            "zipcode": r.code,
        }
        for r in results
        if r.city_municipality and r.province
    ]

    municipalities.sort(key=lambda x: x["name"])

    return templates.TemplateResponse(
        "partials/municipalities_grid.html",
        {"request": request, "municipalities": municipalities},
    )


@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request) -> HTMLResponse:
    """Render contact page."""
    return templates.TemplateResponse("contact.html", {"request": request})
