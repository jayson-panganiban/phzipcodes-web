import pytest
from playwright.async_api import expect


class TestContact:
    @pytest.mark.asyncio
    async def test_contact_page_elements(self, page):
        """Test main elements of the contact page."""
        await page.get_by_role("link", name="Contact").click()

        await expect(page).to_have_title("Say Hi! - Philippine Zipcodes")

        # Verify site header banner
        site_header = page.get_by_role("banner", name="Site header")
        await expect(site_header).to_be_visible()

        # Verify page header banner
        page_header = page.get_by_role("banner", name="Page header")
        await expect(page_header).to_be_visible()
        await expect(
            page_header.get_by_role("heading", name="Let's Connect!")
        ).to_be_visible()

        # Verify site navigation
        site_nav = page.get_by_role("navigation", name="Site navigation")
        await expect(site_nav).to_be_visible()

        # Verify contact options navigation
        contact_nav = page.get_by_role("navigation", name="Contact options")
        await expect(contact_nav).to_be_visible()

        # Verify complementary section
        await expect(page.get_by_role("complementary")).to_be_visible()

    @pytest.mark.asyncio
    async def test_contact_links(self, page):
        """Test contact links and their attributes."""
        await page.get_by_role("link", name="Contact").click()

        support_me = page.get_by_role("link", name="Support via Buy Me a Coffee").nth(1)
        await expect(support_me).to_be_visible()
        await expect(support_me).to_have_attribute(
            "href", "https://buymeacoffee.com/jsonpanganiban"
        )
        contact_links = {
            "Send email": "mailto:jsoncp@proton.me",
            "Connect on LinkedIn": "https://linkedin.com/in/jayson-panganiban",
            "View GitHub profile": "https://github.com/jayson-panganiban",
        }

        for name, href in contact_links.items():
            link = page.get_by_role("link", name=name)
            await expect(link).to_be_visible()
            await expect(link).to_have_attribute("href", href)

    @pytest.mark.asyncio
    async def test_contact_navigation(self, page):
        """Test contact navigation structure and content."""
        await page.get_by_role("link", name="Contact").click()

        nav = page.get_by_role("navigation", name="Contact options")
        await expect(nav).to_have_attribute("aria-label", "Contact options")

        # Verify external links have proper attributes
        external_links = nav.get_by_role("link")
        for link in await external_links.all():
            if await link.get_attribute("target") == "_blank":
                await expect(link).to_have_attribute("rel", "noopener noreferrer")
