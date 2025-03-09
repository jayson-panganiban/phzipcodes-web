import pytest
from playwright.async_api import expect


class TestHome:
    @pytest.mark.asyncio
    async def test_header_elements(self, page):
        """Test header navigation elements."""
        # Logo and home link
        home_link = page.get_by_role("link", name="Home")
        await expect(home_link).to_be_visible()
        await expect(home_link).to_have_attribute("href", "/")
        logo = page.get_by_role("img", name="Philippine")
        await expect(logo).to_be_visible()
        await expect(logo).to_have_attribute("src", "/static/icons/philippines.svg")
        await expect(page.get_by_text("PH Zipcodes")).to_be_visible()

        # Navigation links
        contact_link = page.get_by_role("link", name="Contact")
        await expect(contact_link).to_be_visible()
        await expect(contact_link).to_have_attribute("href", "/contact")

    @pytest.mark.asyncio
    async def test_footer_elements(self, page):
        """Test footer elements and links."""
        # Verify footer structure
        footer = page.get_by_role("contentinfo", name="Site footer")
        await expect(footer).to_be_visible()

        # Copyright text
        copyright_text = page.get_by_text("© 2024 PHZipcodes")
        await expect(copyright_text).to_be_visible()
        await expect(copyright_text).to_have_attribute("aria-label", "Copyright")

        # Footer link
        github_link = page.get_by_role("link", name="View source code")
        await expect(github_link).to_be_visible()
        await expect(github_link).to_have_attribute(
            "href", "https://github.com/jayson-panganiban/phzipcodes-web"
        )
        await expect(github_link).to_have_attribute("target", "_blank")
        await expect(github_link).to_have_attribute("rel", "noopener noreferrer")

    @pytest.mark.asyncio
    async def test_main_content(self, page):
        """Test main content area and search functionality."""
        # Title and meta tags
        await expect(page).to_have_title(
            "Philippine Zip Codes - Fast & Official Postal Code Search"
        )

        # Search functionality
        search_input = page.get_by_role("searchbox")
        await expect(search_input).to_be_visible()
        await expect(search_input).to_have_attribute(
            "placeholder", "Enter location or zipcode..."
        )
        await expect(
            page.get_by_role("button", name="Search locations or zipcode")
        ).to_be_visible()
        clear_button = page.get_by_role("button", name="Clear search input")
        await clear_button.click()

        # Add delay for HTMX response
        await page.wait_for_timeout(500)

        await expect(search_input).to_have_value("")

        # Navigation cards
        nav_cards = {
            "Browse Regions": "/regions",
            "Browse Provinces": "/provinces",
            "Browse Municipalities": "/municipalities",
        }

        for text, href in nav_cards.items():
            card = page.get_by_role("link", name=text)
            await expect(card).to_be_visible()
            await expect(card).to_have_attribute("href", href)

    @pytest.mark.asyncio
    async def test_preloaded_assets(self, page):
        """Test critical preloaded assets."""
        preloaded_icons = [
            "/static/icons/magnifying-glass-light.svg",
            "/static/icons/backspace-light.svg",
            "/static/icons/island-duotone.svg",
            "/static/icons/map-trifold-duotone.svg",
            "/static/icons/city-duotone.svg",
        ]

        for icon in preloaded_icons:
            link = page.locator(f"link[rel='preload'][href='{icon}']")
            await expect(link).to_be_attached()

    @pytest.mark.asyncio
    async def test_search_and_clear_functionality(self, page):
        """Test search functionality and clear button."""

        # Get the search input
        search_input = page.get_by_role("searchbox", name="Search locations")

        # Verify initial state
        await expect(search_input).to_be_visible()
        await expect(search_input).to_have_value("")

        # Type a search query
        test_query = "Manila"
        await search_input.type(test_query)
        await expect(search_input).to_have_value(test_query)

        # Wait for search results
        results_container = page.locator("#results")

        # Check if results are displayed
        results_header = page.locator("#results-header")
        await expect(results_header).to_be_visible()

        # Get the clear button and click it
        clear_button = page.get_by_role("button", name="Clear search input")
        await expect(clear_button).to_be_visible()
        await clear_button.click()

        # Verify that the input is cleared
        await expect(search_input).to_have_value("")

        # Verify results are no longer visible
        await expect(results_container.locator("div")).to_have_count(0)

    @pytest.mark.asyncio
    async def test_search_with_zipcode(self, page):
        """Test searching with a zipcode."""

        # Get the search input
        search_input = page.get_by_role("searchbox", name="Search locations")

        # Type a zipcode
        test_zipcode = "1000"
        await search_input.type(test_zipcode)
        await expect(search_input).to_have_value(test_zipcode)

        # Wait for search results
        results_container = page.locator("#results")

        # Check if results are displayed
        zip_badge = page.locator(".zip-badge")
        await expect(zip_badge).to_be_visible()

        # Verify the zipcode is found in the results
        await expect(page.locator(".zip-badge")).to_contain_text(test_zipcode)

        # Clear the search using the clear button
        clear_button = page.get_by_role("button", name="Clear search input")
        await clear_button.click()

        # Verify that the search is reset
        await expect(search_input).to_have_value("")
        await expect(results_container.locator("div")).to_have_count(0)
