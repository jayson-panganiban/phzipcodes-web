from collections.abc import Sequence
from typing import TypedDict

import phzipcodes
from fastapi import APIRouter, Request, Response
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
async def home(request: Request) -> Response:
    response = templates.TemplateResponse("index.html", {"request": request})
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response


@router.get("/search", response_class=HTMLResponse)
async def search_zipcodes(request: Request, q: str = "") -> HTMLResponse:
    """Search zipcodes by query string."""
    if len(q) < 2:
        return templates.TemplateResponse(
            "partials/results.html", {"request": request, "results": []}
        )

    results: list[ZipCode] = []

    if q:
        if q.isdigit():
            zipcode = phzipcodes.find_by_zip(q)
            if zipcode:
                results = [zipcode]
        else:
            results = list(phzipcodes.search(q))

    response = templates.TemplateResponse(
        "partials/results.html",
        {"request": request, "results": results},
    )
    response.headers["Cache-Control"] = "private, max-age=0"
    return response


@router.get("/regions", response_class=HTMLResponse)
async def regions_page(request: Request) -> Response:
    """Render regions page with all Philippine regions."""
    regions: list[str] = phzipcodes.get_regions()
    response = templates.TemplateResponse(
        "regions.html",
        {
            "request": request,
            "regions": regions,
        },
    )
    response.headers["Cache-Control"] = "public, max-age=86400"
    return response


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
async def provinces_page(request: Request, region: str = "") -> Response:
    """Render provinces page with all Philippine provinces."""
    provinces: list[str] = []
    regions = phzipcodes.get_regions()

    if region:
        provinces = phzipcodes.get_provinces(region)
    else:
        for r in regions:
            provinces.extend(p for p in phzipcodes.get_provinces(r) if p)

    response = templates.TemplateResponse(
        "provinces.html",
        {
            "request": request,
            "provinces": set(provinces),
            "regions": regions,
            "selected_region": region,
        },
    )
    response.headers["Cache-Control"] = "public, max-age=86400"
    return response


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
async def municipalities_page(request: Request, province: str = "") -> Response:
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

    response = templates.TemplateResponse(
        "municipalities.html",
        {
            "request": request,
            "municipalities": municipalities,
            "provinces": provinces,
            "selected_province": province,
        },
    )
    response.headers["Cache-Control"] = "public, max-age=86400"
    return response


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
async def contact_page(request: Request) -> Response:
    """Render contact page."""
    response = templates.TemplateResponse("contact.html", {"request": request})
    response.headers["Cache-Control"] = "public, max-age=86400"
    return response
