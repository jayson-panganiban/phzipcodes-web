import re

import pytest
from playwright.async_api import expect


class TestRegions:
    @pytest.mark.asyncio
    async def test_regions_page_elements(self, page):
        """Test main elements of the regions page."""
        await page.get_by_role("link", name="Browse Regions").click()

        await expect(page).to_have_title(
            "Philippine Regions - Browse Zip Codes by Region"
        )
        await expect(
            page.get_by_role("heading", name="Explore Philippine Regions")
        ).to_be_visible()

        search_input = page.get_by_role("textbox")
        await expect(search_input).to_be_visible()
        await expect(search_input).to_have_attribute(
            "placeholder", "Type a region name..."
        )

    @pytest.mark.asyncio
    async def test_regions_search_functionality(self, page):
        """Test regions search behavior."""
        await page.get_by_role("link", name="Browse Regions").click()

        search_input = page.get_by_role("textbox")
        clear_button = page.get_by_role("button", name="Clear region search")

        await search_input.fill("CALABARZON")
        await expect(search_input).to_have_value("CALABARZON")

        results_grid = page.get_by_role("list", name="Regions list")
        await expect(results_grid).to_be_visible()
        results_card = results_grid.get_by_role("listitem").first
        await expect(results_card.get_by_role("heading")).to_have_text(
            "CAR (Cordillera Administrative Region) "
        )
        await expect(
            results_card.get_by_text("View all provinces in this region")
        ).to_be_visible()

        await clear_button.click()
        await expect(search_input).to_have_value("")

        regions_grid = page.get_by_role("list", name="Regions list")
        await expect(regions_grid).to_be_visible()

    @pytest.mark.asyncio
    async def test_region_page_content(self, page):
        """Test content and structure of the regions page."""
        await page.get_by_role("link", name="Browse Regions").click()

        # Verify regions content
        regions_grid = page.get_by_role("list", name="Regions list")
        await expect(regions_grid).to_be_visible()

        # Verify region cards
        region_cards = regions_grid.get_by_role("listitem")
        count = await region_cards.count()
        assert count > 0

        # Verify first card elements
        first_card = region_cards.first
        await expect(first_card.get_by_role("heading")).to_be_visible()
        await expect(
            first_card.get_by_text("View all provinces in this region")
        ).to_be_visible()
        await expect(first_card).to_have_attribute(
            "href", re.compile(r"^/provinces\?region=.*")
        )

    @pytest.mark.asyncio
    async def test_region_navigation(self, page):
        """Test clicking a region navigates to provinces page."""
        await page.get_by_role("link", name="Browse Regions").click()

        region_cards = page.get_by_role("listitem")
        first_region = region_cards.first
        region_name = await first_region.get_by_role("heading").text_content()

        await first_region.click()

        await expect(page).to_have_url(re.compile(r"^.*/provinces\?region=.*"))
        region_select = page.get_by_role("combobox", name="Filter by region")
        await expect(region_select).to_have_value(region_name.strip())
        await expect(page.get_by_role("list")).to_be_visible()
