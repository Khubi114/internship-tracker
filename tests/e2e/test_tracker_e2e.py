
import os
import uuid
from datetime import date

from playwright.sync_api import expect


BASE_URL = os.environ["E2E_BASE_URL"].rstrip("/")


# Test 1: Verify homepage loads
def test_homepage(page):
    page.goto(BASE_URL)

    expect(
        page.get_by_role(
            "heading",
            name="Student Internship Application Tracker"
        )
    ).to_be_visible()

    expect(
        page.get_by_role("heading", name="Add New Application")
    ).to_be_visible()

    expect(
        page.get_by_role("heading", name="My Applications")
    ).to_be_visible()


# Test 2: Add, edit, update and delete an application
def test_application_workflow(page):
    company = f"E2E Test {uuid.uuid4().hex[:8]}"

    page.goto(BASE_URL)

    # Add a new application
    page.locator("#company").fill(company)
    page.locator("#position").fill("Software Intern")
    page.locator("#application_date").fill(
        date.today().isoformat()
    )
    page.locator("#status").select_option("Applied")
    page.locator("#notes").fill("Playwright E2E test")

    page.get_by_role(
        "button", name="Add Application"
    ).click()

    # Verify the application was created
    row = page.get_by_role("row").filter(has_text=company)

    expect(row).to_be_visible()
    expect(row).to_contain_text("Software Intern")

    try:
        # Open the Edit page
        row.get_by_role("link", name="Edit").click()

        expect(
            page.get_by_role("heading", name="Edit Application")
        ).to_be_visible()

        # Edit the position
        page.locator("#position").fill("AI Intern")

        page.get_by_role(
            "button", name="Save Changes"
        ).click()

        # Verify the updated position
        row = page.get_by_role("row").filter(has_text=company)
        expect(row).to_contain_text("AI Intern")

        # Update status using the table dropdown
        with page.expect_navigation():
            row.locator('select[name="status"]').select_option(
                "Interview"
            )

        # Verify status was saved
        row = page.get_by_role("row").filter(has_text=company)
        expect(
            row.locator('select[name="status"]')
        ).to_have_value("Interview")

    finally:
        # Clean up the test record, even if an assertion fails
        page.goto(BASE_URL)
        test_row = page.get_by_role("row").filter(
            has_text=company
        )

        if test_row.count() > 0:
            test_row.get_by_role(
                "button", name="Delete"
            ).click()

            expect(
                page.get_by_role("row").filter(has_text=company)
            ).to_have_count(0)
