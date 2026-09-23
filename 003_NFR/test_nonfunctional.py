"""
Non-functional Testing: Security Testing
Website: https://school.moodledemo.net
Testing approach: Verify that unauthenticated users cannot access submission form
or perform submission actions.
Python 3 + Selenium 4 + unittest
"""

import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# ============================================================
# CONFIGURATION
# ============================================================
BASE_URL     = "https://school.moodledemo.net"
WAIT_TIMEOUT = 10

# URLs va ket qua mong doi khi chua dang nhap
PROTECTED_URLS = [
    {
        "name": "Add/Edit submission form",
        "url": "https://school.moodledemo.net/mod/assign/view.php?id=573&action=editsubmission",
        "blocked_element": "id_submitbutton",   # Form submission khong duoc hien
        "description": "Unauthenticated user should not see submission form"
    },
    {
        "name": "Remove submission confirm page",
        "url": "https://school.moodledemo.net/mod/assign/view.php?id=573&action=removesubmissionconfirm",
        "blocked_element": "id_submitbutton",
        "description": "Unauthenticated user should not see remove confirmation form"
    },
    {
        "name": "Assignment view page",
        "url": "https://school.moodledemo.net/mod/assign/view.php?id=573",
        "blocked_element": "id_submitbutton",
        "description": "Unauthenticated user should not see Add submission button"
    },
]

# ============================================================
# TEST CLASS
# ============================================================
class TestSecurity(unittest.TestCase):

    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, WAIT_TIMEOUT)

    def tearDown(self):
        self.driver.quit()

    def test_unauthenticated_cannot_submit(self):
        """
        Security Test: Unauthenticated users cannot access submission actions.
        Expected: submission form (id_submitbutton) is NOT present on page.
        """
        driver = self.driver
        results = {"pass": 0, "fail": 0}

        print(f"\n{'='*60}")
        print("Security Testing: Unauthenticated Access Control")
        print(f"{'='*60}")

        for item in PROTECTED_URLS:
            name    = item["name"]
            url     = item["url"]
            blocked = item["blocked_element"]

            print(f"\nTesting: {name}")
            print(f"  URL: {url}")
            print(f"  Expected: '{blocked}' should NOT be accessible")

            # Dam bao chua dang nhap
            driver.delete_all_cookies()
            driver.get(url)
            time.sleep(2)

            current_url = driver.current_url
            print(f"  Landed on: {current_url}")

            # Kiem tra form submission CO hien ra khong
            form_accessible = False
            try:
                el = driver.find_element(By.ID, blocked)
                form_accessible = el.is_displayed()
            except Exception:
                form_accessible = False

            if not form_accessible:
                print(f"  PASS: Submission form not accessible for unauthenticated user")
                results["pass"] += 1
            else:
                print(f"  FAIL: Submission form IS accessible without login")
                results["fail"] += 1

        print(f"\n{'='*60}")
        print(f"TONG KET Security Testing: PASS={results['pass']} | FAIL={results['fail']}")
        print(f"{'='*60}")

        self.assertEqual(
            results["fail"], 0,
            f"Co {results['fail']} URL bi lo hong bao mat: submission form hien thi khi chua dang nhap"
        )

# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    unittest.main(verbosity=2)