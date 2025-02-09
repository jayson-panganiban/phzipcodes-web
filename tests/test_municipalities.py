import re

import pytest
from playwright.async_api import expect


class TestMunicipalities:
    @pytest.mark.asyncio
    async def test_mobile_view(self, mobile_page):
        """Test mobile view elements and behavior."""
        await mobile_page.get_by_role("link", name="Browse Municipalities").click()

        # Verify mobile navigation
        mobile_filters = mobile_page.get_by_role(
            "navigation", name="Mobile province filters"
        )
        await expect(mobile_filters).to_be_visible()

        # Verify mobile search
        search_container = mobile_page.locator("#search-container")
        await expect(search_container).to_be_visible()

        # Desktop elements should be hidden
        province_filter = mobile_page.locator("#province-filter")
        await expect(province_filter).to_be_hidden()

    @pytest.mark.asyncio
    async def test_desktop_view(self, desktop_page):
        """Test desktop view elements and behavior."""
        await desktop_page.get_by_role("link", name="Browse Municipalities").click()

        # Verify desktop filters
        desktop_filters = desktop_page.get_by_role("search", name="Municipality search")
        await expect(desktop_filters).to_be_visible()

        # Verify province filter
        province_filter = desktop_page.locator("#province-filter")
        await expect(province_filter).to_be_visible()

        # Mobile elements should be hidden
        mobile_filters = desktop_page.locator("#mobile-filters")
        await expect(mobile_filters).to_be_hidden()

    @pytest.mark.asyncio
    async def test_municipalities_page_elements(self, page):
        """Test main elements of the municipalities page."""
        await page.get_by_role("link", name="Browse Municipalities").click()

        await expect(page).to_have_title(
            "Philippine Cities & Municipalities - Complete Zip Code Directory"
        )

        # Verify page header
        page_header = page.get_by_role("banner", name="Page header")
        await expect(page_header).to_be_visible()
        await expect(
            page_header.get_by_role("heading", name="Cities & Municipalities")
        ).to_be_visible()

        # Search input and buttons
        search_input = page.get_by_role("textbox")
        await expect(search_input).to_be_visible()
        await expect(page.get_by_role("button", name="Submit search")).to_be_visible()
        await expect(page.get_by_role("button", name="Clear search")).to_be_visible()
        await expect(search_input).to_have_attribute(
            "placeholder", "Type a municipality name..."
        )

    @pytest.mark.asyncio
    async def test_municipalities_search_functionality(self, page):
        """Test municipalities search behavior."""
        await page.get_by_role("link", name="Browse Municipalities").click()

        search_input = page.get_by_role("textbox")
        clear_button = page.get_by_role("button", name="Clear search")

        await search_input.fill("MAKATI")
        await expect(search_input).to_have_value("MAKATI")

        await clear_button.click()
        await expect(search_input).to_have_value("")

        municipalities = page.get_by_role("list", name="Municipalities list")
        await expect(municipalities).to_be_visible()

    @pytest.mark.asyncio
    async def test_municipality_page_content(self, page):
        """Test content and structure of the municipalities page."""
        await page.get_by_role("link", name="Browse Municipalities").click()

        # Verify municipality cards
        municipalities = page.get_by_role("list", name="Municipalities list")
        await expect(municipalities).to_be_visible()

        municipality_cards = municipalities.get_by_role("listitem")
        count = await municipality_cards.count()
        assert count > 0

        # Verify first card elements
        first_card = municipality_cards.first
        await expect(first_card.get_by_role("heading")).to_be_visible()
        await expect(first_card.get_by_text(re.compile(r"\d{4}"))).to_be_visible()
        await expect(first_card).to_have_attribute("tabindex", "0")

        # Verify province and zipcode sections
        province_section = first_card.locator('[aria-label^="Province:"]')
        await expect(province_section).to_be_visible()

        zipcode_section = first_card.locator('[aria-label^="Zip code:"]')
        await expect(zipcode_section).to_be_visible()
        await expect(zipcode_section).to_contain_text(re.compile(r"\d{4}"))

    @pytest.mark.asyncio
    async def test_province_filter(self, page):
        """Test province filter functionality."""
        await page.get_by_role("link", name="Browse Municipalities").click()

        province_select = page.get_by_role("combobox", name="Filter by province")
        await province_select.select_option("Metro Manila")
        await expect(province_select).to_have_value("Metro Manila")

        # wait for the province filter to be applied
        await page.wait_for_timeout(1000)

        municipalities = page.get_by_role("list", name="Municipalities list")
        await expect(municipalities).to_be_visible()

        # Get all municipality cards and await the result
        municipality_cards = await municipalities.get_by_role("listitem").all()
        count = len(municipality_cards)
        assert count > 0

        # Verify filtered municipalities are from Metro Manila
        for municipality in municipality_cards:
            province_text = await municipality.get_by_text(
                "Metro Manila"
            ).text_content()
            assert province_text == "Metro Manila"

    @pytest.mark.asyncio
    async def test_clear_search_resets_all_filters(self, page):
        """Test clear search button resets all filters."""
        await page.get_by_role("link", name="Browse Municipalities").click()

        # Set initial filters
        province_select = page.get_by_role("combobox", name="Filter by province")
        await province_select.select_option("Cavite")
        await expect(province_select).to_have_value("Cavite")

        search_input = page.get_by_role("textbox")
        await search_input.fill("Dasmariñas")

        # Clear filters
        clear_button = page.get_by_role("button", name="Clear search")
        await clear_button.click()

        # Add delay for HTMX response
        await page.wait_for_timeout(500)

        # Verify search input is cleared
        await expect(search_input).to_have_value("")

        # Verify province select is reset
        await expect(province_select).to_have_value("")

        # Verify municipalities grid shows all municipalities
        municipalities = page.get_by_role("list", name="Municipalities list")
        await expect(municipalities).to_be_visible()

        municipality_cards = municipalities.get_by_role("listitem")
        count = await municipality_cards.count()
        assert count > 10
