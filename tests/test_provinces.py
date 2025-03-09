import re

import pytest
from playwright.async_api import expect


class TestProvinces:
    @pytest.mark.asyncio
    async def test_provinces_page_elements(self, page):
        """Test main elements of the provinces page."""
        await page.get_by_role("link", name="Browse Provinces").click()

        await expect(page).to_have_title(
            "Philippine Provinces - Browse Postal Codes by Province"
        )
        await expect(
            page.get_by_role("heading", name="Explore Philippine Provinces")
        ).to_be_visible()

        search_input = page.get_by_role("textbox")
        await expect(search_input).to_be_visible()
        await expect(search_input).to_have_attribute(
            "placeholder", "Type a province name..."
        )

        # Region filter
        region_filter = page.get_by_role("combobox", name="Filter by region")
        await expect(region_filter).to_be_visible()

    @pytest.mark.asyncio
    async def test_provinces_search_functionality(self, page):
        """Test provinces search behavior."""
        await page.get_by_role("link", name="Browse Provinces").click()

        search_input = page.get_by_role("textbox")
        clear_button = page.get_by_role("button", name="Clear province search")

        await search_input.fill("BATANGAS")
        await expect(search_input).to_have_value("BATANGAS")

        await clear_button.click()
        await expect(search_input).to_have_value("")

        provinces_grid = page.get_by_role("list", name="Provinces list")
        await expect(provinces_grid).to_be_visible()

    @pytest.mark.asyncio
    async def test_province_page_content(self, page):
        """Test content and structure of the provinces page."""
        await page.get_by_role("link", name="Browse Provinces").click()

        # Verify list container and grid
        provinces_grid = page.get_by_role("List", name="Provinces list")
        await expect(provinces_grid).to_be_visible()

        # Verify province cards
        province_cards = provinces_grid.get_by_role("listitem")
        count = await province_cards.count()
        assert count > 0

        # Verify first card elements
        first_card = province_cards.first
        await expect(first_card.get_by_role("heading")).to_be_visible()
        await expect(
            first_card.get_by_text("Explore cities and municipalities")
        ).to_be_visible()
        await expect(first_card).to_have_attribute(
            "href", re.compile(r"^/municipalities\?province=.*")
        )

        await expect(first_card).to_have_attribute("hx-boost", "true")

    @pytest.mark.asyncio
    async def test_province_navigation(self, page):
        """Test clicking a province navigates to municipalities page with correct selection."""
        await page.get_by_role("link", name="Browse Provinces").click()

        province_cards = page.get_by_role("listitem")
        first_province = province_cards.first
        province_name = await first_province.get_by_role("heading").text_content()

        await first_province.click()

        # Verify URL and page navigation
        await expect(page).to_have_url(
            re.compile(rf"^.*/municipalities\?province={province_name.strip()}")
        )

        # Verify page heading
        await expect(
            page.get_by_role("heading", name="Cities & Municipalities")
        ).to_be_visible()

        # Verify province is selected in dropdown
        province_select = page.get_by_role("combobox", name="Filter by province")
        await expect(province_select).to_have_value(province_name.strip())

        # Verify municipalities grid is displayed with filtered results
        municipalities_grid = page.get_by_role("list", name="Municipalities list")
        await expect(municipalities_grid).to_be_visible()

    @pytest.mark.asyncio
    async def test_clear_search_resets_all_filters(self, page):
        """Test clear search button resets all filters and displays full province grid."""
        await page.get_by_role("link", name="Browse Provinces").click()

        region_select = page.get_by_role("combobox", name="Filter by region")
        await region_select.select_option("CAR (Cordillera Administrative Region)")

        # Set initial filters
        search_input = page.get_by_role("textbox")
        await search_input.fill("Ifugao")

        # Clear filters
        clear_button = page.get_by_role("button", name="Clear province search")
        await clear_button.click()

        # Add delay for HTMX response
        await page.wait_for_timeout(500)

        # Verify search input is cleared
        await expect(search_input).to_have_value("")

        # Verify region select is reset
        await expect(region_select).to_have_value("")

        # Verify provinces grid shows all provinces
        provinces_grid = page.get_by_role("List", name="Provinces list")
        await expect(provinces_grid).to_be_visible()

        province_cards = provinces_grid.get_by_role("listitem")
        count = await province_cards.count()
        assert count > 10
