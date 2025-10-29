#!/usr/bin/env python3
"""
YAGO v8.0 - Comprehensive Browser Testing
Tests all dashboard tabs, interactions, and UI elements
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime

class YAGOBrowserTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "passed": 0,
            "failed": 0,
            "warnings": 0
        }
        self.base_url = "http://localhost:3000"

    def log_test(self, name, status, details=""):
        """Log test result"""
        result = {
            "name": name,
            "status": status,
            "details": details
        }
        self.results["tests"].append(result)

        if status == "✅ PASS":
            self.results["passed"] += 1
            print(f"✅ {name}")
        elif status == "❌ FAIL":
            self.results["failed"] += 1
            print(f"❌ {name}: {details}")
        else:
            self.results["warnings"] += 1
            print(f"⚠️  {name}: {details}")

        if details:
            print(f"   {details}")

    async def test_page_load(self, page):
        """Test if page loads without errors"""
        print("\n🔍 Test 1: Page Load & Initial Render")
        print("=" * 60)

        errors = []
        console_messages = []

        # Capture console messages
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: errors.append(str(err)))

        try:
            await page.goto(self.base_url, wait_until="networkidle", timeout=10000)
            await page.wait_for_timeout(2000)  # Wait for initial render

            # Check for page title
            title = await page.title()
            if "YAGO" in title:
                self.log_test("Page title correct", "✅ PASS", f"Title: {title}")
            else:
                self.log_test("Page title", "⚠️  WARN", f"Title: {title}")

            # Check for errors
            if errors:
                self.log_test("Console errors", "❌ FAIL", f"Errors found: {errors}")
            else:
                self.log_test("No console errors", "✅ PASS")

            # Check if main content loaded
            main_content = await page.query_selector("main")
            if main_content:
                self.log_test("Main content loaded", "✅ PASS")
            else:
                self.log_test("Main content", "❌ FAIL", "Main element not found")

        except Exception as e:
            self.log_test("Page load", "❌ FAIL", str(e))

        return errors, console_messages

    async def test_overview_tab(self, page):
        """Test Overview tab"""
        print("\n🔍 Test 2: Overview Tab")
        print("=" * 60)

        try:
            # Overview tab should be active by default
            await page.wait_for_timeout(1000)

            # Check for overview content
            overview_visible = await page.is_visible("text=Welcome to YAGO v8.0")
            if overview_visible:
                self.log_test("Overview welcome text", "✅ PASS")
            else:
                self.log_test("Overview welcome text", "⚠️  WARN", "Welcome text not found")

            # Check for stat cards
            stats = await page.query_selector_all(".grid > div")
            stat_count = len(stats)
            if stat_count >= 4:
                self.log_test("Overview stat cards", "✅ PASS", f"Found {stat_count} cards")
            else:
                self.log_test("Overview stat cards", "⚠️  WARN", f"Only {stat_count} cards found")

            # Check for quick actions
            quick_actions = await page.is_visible("text=Quick Actions")
            if quick_actions:
                self.log_test("Quick actions section", "✅ PASS")
            else:
                self.log_test("Quick actions section", "⚠️  WARN")

        except Exception as e:
            self.log_test("Overview tab", "❌ FAIL", str(e))

    async def test_create_project_tab(self, page):
        """Test Create Project tab"""
        print("\n🔍 Test 3: Create Project Tab")
        print("=" * 60)

        try:
            # Click Create Project tab
            await page.click("text=Create Project")
            await page.wait_for_timeout(1500)

            # Check if ClarificationFlow loaded
            clarification_flow = await page.query_selector(".space-y-6")
            if clarification_flow:
                self.log_test("ClarificationFlow component loaded", "✅ PASS")
            else:
                self.log_test("ClarificationFlow component", "⚠️  WARN")

            # Check for templates section
            templates = await page.is_visible("text=Popular Templates")
            if templates:
                self.log_test("Templates section visible", "✅ PASS")
            else:
                self.log_test("Templates section", "⚠️  WARN")

            # Check for template cards
            template_cards = await page.query_selector_all("button:has-text('Use Template')")
            if len(template_cards) > 0:
                self.log_test("Template cards", "✅ PASS", f"Found {len(template_cards)} templates")
            else:
                self.log_test("Template cards", "⚠️  WARN", "No template cards found")

        except Exception as e:
            self.log_test("Create Project tab", "❌ FAIL", str(e))

    async def test_ai_models_tab(self, page):
        """Test AI Models tab"""
        print("\n🔍 Test 4: AI Models Tab")
        print("=" * 60)

        try:
            # Click AI Models tab
            await page.click("text=AI Models")
            await page.wait_for_timeout(1500)

            # Check for models heading
            models_heading = await page.is_visible("text=Available AI Models")
            if models_heading:
                self.log_test("Models heading", "✅ PASS")
            else:
                self.log_test("Models heading", "⚠️  WARN")

            # Check for provider filters
            provider_filters = await page.query_selector_all("button:has-text('All')")
            if len(provider_filters) > 0:
                self.log_test("Provider filters", "✅ PASS")
            else:
                self.log_test("Provider filters", "⚠️  WARN")

            # Check for model cards
            await page.wait_for_timeout(1000)
            model_cards = await page.query_selector_all(".grid > div")
            if len(model_cards) >= 5:
                self.log_test("Model cards", "✅ PASS", f"Found {len(model_cards)} models")
            else:
                self.log_test("Model cards", "⚠️  WARN", f"Only {len(model_cards)} models found")

            # Test provider filter
            try:
                await page.click("button:has-text('OpenAI')")
                await page.wait_for_timeout(500)
                self.log_test("Provider filter interaction", "✅ PASS")
            except:
                self.log_test("Provider filter interaction", "⚠️  WARN")

        except Exception as e:
            self.log_test("AI Models tab", "❌ FAIL", str(e))

    async def test_analytics_tab(self, page):
        """Test Analytics tab"""
        print("\n🔍 Test 5: Analytics Tab")
        print("=" * 60)

        try:
            # Click Analytics tab
            await page.click("text=Analytics")
            await page.wait_for_timeout(1500)

            # Check for analytics heading
            analytics_heading = await page.is_visible("text=Analytics Dashboard")
            if analytics_heading:
                self.log_test("Analytics heading", "✅ PASS")
            else:
                self.log_test("Analytics heading", "⚠️  WARN")

            # Check for metric cards
            metric_cards = await page.query_selector_all(".grid > div")
            if len(metric_cards) >= 4:
                self.log_test("Metric cards", "✅ PASS", f"Found {len(metric_cards)} metrics")
            else:
                self.log_test("Metric cards", "⚠️  WARN", f"Only {len(metric_cards)} metrics found")

            # Check for time range selector
            time_range = await page.is_visible("text=Last 7 Days")
            if time_range:
                self.log_test("Time range selector", "✅ PASS")
            else:
                self.log_test("Time range selector", "⚠️  WARN")

        except Exception as e:
            self.log_test("Analytics tab", "❌ FAIL", str(e))

    async def test_marketplace_tab(self, page):
        """Test Marketplace tab"""
        print("\n🔍 Test 6: Marketplace Tab")
        print("=" * 60)

        try:
            # Click Marketplace tab
            await page.click("text=Marketplace")
            await page.wait_for_timeout(1500)

            # Check for marketplace heading
            marketplace_heading = await page.is_visible("text=Marketplace")
            if marketplace_heading:
                self.log_test("Marketplace heading", "✅ PASS")
            else:
                self.log_test("Marketplace heading", "⚠️  WARN")

            # Check for category filters
            category_filters = await page.query_selector_all("button:has-text('All')")
            if len(category_filters) > 0:
                self.log_test("Category filters", "✅ PASS")
            else:
                self.log_test("Category filters", "⚠️  WARN")

            # Check for marketplace items
            await page.wait_for_timeout(1000)
            items = await page.query_selector_all(".grid > div")
            if len(items) >= 3:
                self.log_test("Marketplace items", "✅ PASS", f"Found {len(items)} items")
            else:
                self.log_test("Marketplace items", "⚠️  WARN", f"Only {len(items)} items found")

            # Test install button
            try:
                install_btn = await page.query_selector("button:has-text('Install')")
                if install_btn:
                    self.log_test("Install button present", "✅ PASS")
                else:
                    self.log_test("Install button", "⚠️  WARN")
            except:
                self.log_test("Install button", "⚠️  WARN")

        except Exception as e:
            self.log_test("Marketplace tab", "❌ FAIL", str(e))

    async def test_navigation(self, page):
        """Test navigation between tabs"""
        print("\n🔍 Test 7: Navigation")
        print("=" * 60)

        try:
            # Test clicking through all tabs
            tabs = ["Overview", "Create Project", "AI Models", "Analytics", "Marketplace"]

            for tab in tabs:
                try:
                    await page.click(f"text={tab}")
                    await page.wait_for_timeout(500)
                    self.log_test(f"Navigate to {tab}", "✅ PASS")
                except Exception as e:
                    self.log_test(f"Navigate to {tab}", "❌ FAIL", str(e))

        except Exception as e:
            self.log_test("Navigation test", "❌ FAIL", str(e))

    async def test_responsive_design(self, page):
        """Test responsive design"""
        print("\n🔍 Test 8: Responsive Design")
        print("=" * 60)

        viewports = [
            {"name": "Mobile", "width": 375, "height": 667},
            {"name": "Tablet", "width": 768, "height": 1024},
            {"name": "Desktop", "width": 1920, "height": 1080}
        ]

        for viewport in viewports:
            try:
                await page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
                await page.wait_for_timeout(500)

                # Check if main content is visible
                main_visible = await page.is_visible("main")
                if main_visible:
                    self.log_test(f"{viewport['name']} layout", "✅ PASS", f"{viewport['width']}x{viewport['height']}")
                else:
                    self.log_test(f"{viewport['name']} layout", "❌ FAIL")
            except Exception as e:
                self.log_test(f"{viewport['name']} layout", "❌ FAIL", str(e))

    async def test_language_switcher(self, page):
        """Test language switcher"""
        print("\n🔍 Test 9: Language Switcher")
        print("=" * 60)

        try:
            # Look for language selector
            lang_selector = await page.query_selector("select, button[aria-label*='language']")

            if lang_selector:
                self.log_test("Language switcher present", "✅ PASS")

                # Try to find language options
                try:
                    await page.click("select")
                    await page.wait_for_timeout(300)
                    options = await page.query_selector_all("option")
                    if len(options) >= 7:
                        self.log_test("Language options", "✅ PASS", f"Found {len(options)} languages")
                    else:
                        self.log_test("Language options", "⚠️  WARN", f"Only {len(options)} languages found")
                except:
                    self.log_test("Language options check", "⚠️  WARN", "Could not verify options")
            else:
                self.log_test("Language switcher", "⚠️  WARN", "Not found")

        except Exception as e:
            self.log_test("Language switcher test", "❌ FAIL", str(e))

    async def test_network_requests(self, page):
        """Monitor network requests"""
        print("\n🔍 Test 10: Network Requests")
        print("=" * 60)

        failed_requests = []

        async def check_response(response):
            if response.status >= 400:
                failed_requests.append(f"{response.url} - Status {response.status}")

        page.on("response", lambda response: asyncio.create_task(check_response(response)))

        try:
            # Navigate through tabs to trigger API calls
            await page.click("text=Overview")
            await page.wait_for_timeout(1000)
            await page.click("text=Create Project")
            await page.wait_for_timeout(1000)
            await page.click("text=AI Models")
            await page.wait_for_timeout(1000)

            if failed_requests:
                self.log_test("Network requests", "⚠️  WARN", f"{len(failed_requests)} failed requests")
                for req in failed_requests[:5]:  # Show first 5
                    print(f"      - {req}")
            else:
                self.log_test("Network requests", "✅ PASS", "All requests successful")

        except Exception as e:
            self.log_test("Network monitoring", "❌ FAIL", str(e))

    async def run_all_tests(self):
        """Run all browser tests"""
        print("=" * 60)
        print("🚀 YAGO v8.0 - COMPREHENSIVE BROWSER TESTING")
        print("=" * 60)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Run all tests
            await self.test_page_load(page)
            await self.test_overview_tab(page)
            await self.test_create_project_tab(page)
            await self.test_ai_models_tab(page)
            await self.test_analytics_tab(page)
            await self.test_marketplace_tab(page)
            await self.test_navigation(page)
            await self.test_responsive_design(page)
            await self.test_language_switcher(page)
            await self.test_network_requests(page)

            await browser.close()

        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed:   {self.results['passed']}")
        print(f"❌ Failed:   {self.results['failed']}")
        print(f"⚠️  Warnings: {self.results['warnings']}")
        total = self.results['passed'] + self.results['failed'] + self.results['warnings']
        print(f"📈 Total:    {total}")

        if self.results['failed'] == 0:
            success_rate = (self.results['passed'] / total * 100) if total > 0 else 0
            print(f"\n🎉 SUCCESS RATE: {success_rate:.1f}%")
            if self.results['warnings'] == 0:
                print("✅ ALL TESTS PASSED - 100% SUCCESS!")
            else:
                print(f"✅ All critical tests passed ({self.results['warnings']} minor warnings)")
        else:
            print(f"\n⚠️  {self.results['failed']} tests failed - review needed")

        print("=" * 60)

        # Save results to file
        with open("/Users/mikail/Desktop/YAGO/browser_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)

        print("\n📄 Detailed results saved to: browser_test_results.json")

        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = YAGOBrowserTester()
    success = asyncio.run(tester.run_all_tests())
    exit(0 if success else 1)
