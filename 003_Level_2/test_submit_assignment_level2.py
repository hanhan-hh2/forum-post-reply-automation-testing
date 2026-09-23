"""
Data-driven automation test for Submit Assignment feature
Website: https://school.moodledemo.net
Assignment URL: https://school.moodledemo.net/mod/assign/view.php?id=573
Python 3 + Selenium 4 + unittest
"""

import unittest
import csv
import os
import time
import tempfile
import configparser

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# ============================================================
# CONFIGURATION
# ============================================================
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

if not config.sections():
    raise FileNotFoundError("Khong tim thay config.ini — dat file cung thu muc voi file .py")

BASE_URL       = config["site"]["base_url"]
ASSIGNMENT_URL = config["site"]["assignment_url"]
USERNAME       = config["credentials"]["username"]
PASSWORD       = config["credentials"]["password"]
TEST_DATA_FILE = config["settings"]["test_data_file"]
WAIT_TIMEOUT   = int(config["settings"]["wait_timeout"])

BTN_ADD        = config["buttons"]["add_submission"]
BTN_REMOVE     = config["buttons"]["remove_submission"]
BTN_CONTINUE   = config["buttons"]["continue"]
BTN_SAVE       = config["buttons"]["save_changes"]
BTN_EDIT       = config["buttons"]["edit_submission"]

# ============================================================
# HELPER: Tao file tam dung kich thuoc va dung loai
# ============================================================
def create_temp_file(size_kb: int, file_type: str) -> str:
    suffix = file_type if file_type.startswith(".") else f".{file_type}"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

    if size_kb == 0:
        tmp.write(b"")
    elif suffix == ".pdf":
        header = (
            b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n"
            b"xref\n0 1\n0000000000 65535 f \n"
            b"trailer\n<< /Size 1 /Root 1 0 R >>\nstartxref\n9\n%%EOF\n"
        )
        target = size_kb * 1024
        tmp.write(header)
        remaining = target - len(header)
        if remaining > 0:
            tmp.write(b" " * remaining)
    elif suffix == ".doc":
        header = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 24
        target = size_kb * 1024
        tmp.write(header)
        remaining = target - len(header)
        if remaining > 0:
            tmp.write(b"\x00" * remaining)
    elif suffix == ".jpg":
        header = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00"
        target = size_kb * 1024
        tmp.write(header)
        remaining = target - len(header)
        if remaining > 0:
            tmp.write(b"\x00" * remaining)
    elif suffix == ".docx":
        header = b"PK\x03\x04" + b"\x00" * 26
        target = size_kb * 1024
        tmp.write(header)
        remaining = target - len(header)
        if remaining > 0:
            tmp.write(b"\x00" * remaining)
    else:
        tmp.write(b"\x00" * size_kb * 1024)

    tmp.close()
    return tmp.name

# ============================================================
# HELPER: Doc test data tu CSV
# ============================================================
def load_test_data(csv_file: str) -> list:
    test_cases = []
    with open(csv_file, newline="", encoding="utf-8-sig") as f:
        sample = f.read(1024)
        f.seek(0)
        delimiter = "\t" if "\t" in sample else ","
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            test_cases.append(row)
    return test_cases

# ============================================================
# BASE TEST CLASS
# ============================================================
class BaseTest(unittest.TestCase):

    def setUp(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, WAIT_TIMEOUT)
        self.temp_files = []

    def tearDown(self):
        for f in self.temp_files:
            if os.path.exists(f):
                os.remove(f)
        self.driver.quit()

    def login(self):
        driver = self.driver
        driver.get(f"{BASE_URL}/login/index.php")
        driver.delete_all_cookies()
        driver.get(f"{BASE_URL}/login/index.php")
        self.wait.until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").clear()
        driver.find_element(By.ID, "username").send_keys(USERNAME)
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
        driver.find_element(By.ID, "loginbtn").click()
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class,'usermenu')]")
        ))

    def go_to_assignment(self):
        self.driver.get(ASSIGNMENT_URL)
        self.wait.until(EC.presence_of_element_located((By.ID, "region-main")))

    def remove_existing_submission(self):
        driver = self.driver
        try:
            remove_btn = driver.find_elements(
                By.XPATH, f"//button[contains(text(),'{BTN_REMOVE}')]"
            )
            if remove_btn:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", remove_btn[0])
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", remove_btn[0])
                continue_btn = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, f"//button[contains(text(),'{BTN_CONTINUE}')]")
                ))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_btn)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", continue_btn)
                self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, f"//button[contains(text(),'{BTN_ADD}')]")
                ))
                time.sleep(1)
        except Exception:
            pass

    def upload_file(self, file_path: str):
        driver = self.driver
        wait = self.wait

        add_file_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class,'fp-btn-add')]/a")
        ))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_file_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", add_file_btn)
        time.sleep(1.5)

        upload_tab = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class,'fp-repo')]//a[.//span[contains(@class,'fp-repo-name') "
                       "and contains(text(),'Upload a file')]]")
        ))
        driver.execute_script("arguments[0].click();", upload_tab)
        time.sleep(1.5)

        file_input = wait.until(EC.presence_of_element_located(
            (By.NAME, "repo_upload_file")
        ))
        driver.execute_script("""
            var el = arguments[0];
            el.style.display = 'block';
            el.style.visibility = 'visible';
            el.style.opacity = '1';
            el.style.width = '1px';
            el.style.height = '1px';
            el.style.position = 'relative';
        """, file_input)
        time.sleep(0.3)
        file_input.send_keys(file_path)
        time.sleep(0.5)

        upload_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(@class,'fp-upload-btn')]")
        ))
        upload_btn.click()

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class,'filemanager')]//span[contains(@class,'fp-filename') and string-length(text()) > 0]")
                )
            )
        except TimeoutException:
            pass
        time.sleep(1)

    def handle_upload_dialog(self) -> str:
        driver = self.driver
        try:
            dialogs = driver.find_elements(
                By.XPATH,
                "//div[contains(@class,'moodle-dialogue-wrap') and not(contains(@style,'display: none')) and not(contains(@class,'hidden'))]"
            )
            for dialog in dialogs:
                if not dialog.is_displayed():
                    continue
                try:
                    title = dialog.find_element(By.XPATH, ".//h5 | .//h4").text.strip()
                except Exception:
                    title = ""

                if not title:
                    continue

                if "File type not accepted" in title or "not accepted" in title.lower():
                    try:
                        ok_btn = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, "//input[@value='OK' and contains(@class,'btn')] | //button[text()='OK']")
                            )
                        )
                        driver.execute_script("arguments[0].click();", ok_btn)
                        time.sleep(1)
                    except Exception:
                        pass
                    return "file_type_error"

                elif "Error" in title or "error" in title.lower():
                    try:
                        close_btn = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, "//button[contains(@class,'closebutton')]")
                            )
                        )
                        driver.execute_script("arguments[0].click();", close_btn)
                        time.sleep(1)
                    except Exception:
                        pass
                    return "file_too_large"

        except Exception:
            pass
        return ""

    def get_error_message(self) -> str:
        driver = self.driver
        try:
            err = driver.find_elements(
                By.XPATH, "//div[contains(@class,'alert-danger') and contains(.,'Nothing was submitted')]"
            )
            if err:
                return "Nothing was submitted"
        except Exception:
            pass
        return ""

    def get_submission_status(self) -> str:
        try:
            el = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "td.submissionstatussubmitted, td.submissionstatus")
            ))
            return el.text.strip()
        except TimeoutException:
            return ""

# ============================================================
# TEST CLASS
# ============================================================
class TestAddSubmission(BaseTest):

    @classmethod
    def setUpClass(cls):
        cls.test_cases = load_test_data(TEST_DATA_FILE)

    def run_test_case(self, tc: dict):
        driver     = self.driver
        tc_id      = tc["TC_ID"]
        tc_name    = tc["TC_Name"]
        action     = tc["Action"].strip().lower()
        action_url = tc["Action_URL"].strip()
        has_file   = tc["Has_File"].strip().lower() == "yes"
        size_kb    = int(tc["File_Size_KB"]) if tc["File_Size_KB"].strip() else 0
        file_type  = tc["File_Type"].strip()
        comment    = tc["Comment"].strip()
        expected   = tc["Expected_Result"].strip().upper()

        print(f"\n{'='*60}")
        print(f"Running: {tc_id} - {tc_name}")
        print(f"  File: {size_kb}KB {file_type or 'N/A'} | Expected: {expected}")

        # 1. Login va cleanup
        self.login()
        self.go_to_assignment()
        self.remove_existing_submission()

        # ── REMOVE flow ──────────────────────────────────────────────
        if action == "remove":
            # Tao submission truoc de co thu remove
            self.go_to_assignment()
            add_url = f"{ASSIGNMENT_URL}&action=editsubmission"
            driver.get(add_url)
            self.wait.until(EC.presence_of_element_located((By.ID, "id_submitbutton")))
            time.sleep(1)

            file_path = create_temp_file(500, ".pdf")
            self.temp_files.append(file_path)
            self.upload_file(file_path)

            save_btn = self.wait.until(EC.presence_of_element_located((By.ID, "id_submitbutton")))
            driver.execute_script("arguments[0].click();", save_btn)
            time.sleep(2)

            # Lay remove link tren trang (da co sesskey san)
            self.go_to_assignment()
            try:
                remove_link = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//a[contains(@href,'removesubmission')]")
                ))
                remove_url = remove_link.get_attribute("href")
            except TimeoutException:
                remove_btn = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, f"//button[contains(text(),'{BTN_REMOVE}')]")
                ))
                driver.execute_script("arguments[0].click();", remove_btn)
                remove_url = None

            if remove_url:
                driver.get(remove_url)
                time.sleep(1.5)

            # Confirm
            confirm_btn = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, f"//button[contains(text(),'{BTN_CONTINUE}')]")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", confirm_btn)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", confirm_btn)
            time.sleep(2)

            if expected == "PASS":
                try:
                    self.wait.until(EC.presence_of_element_located(
                        (By.XPATH, f"//button[contains(text(),'{BTN_ADD}')]")
                    ))
                    print(f"  PASS (submission da bi xoa)")
                except TimeoutException:
                    self.fail(f"{tc_id} FAIL: Khong thay nut {BTN_ADD} sau khi remove")
            return

        # ── ADD flow ─────────────────────────────────────────────────
        self.go_to_assignment()
        driver.get(action_url)
        self.wait.until(EC.presence_of_element_located((By.ID, "id_submitbutton")))
        time.sleep(1)

        if has_file and size_kb > 0 and file_type:
            file_path = create_temp_file(size_kb, file_type)
            self.temp_files.append(file_path)
            self.upload_file(file_path)

            dialog_result = self.handle_upload_dialog()

            if dialog_result == "file_type_error":
                if expected == "FAIL":
                    print(f"  PASS (file type bi tu choi dung nhu mong doi)")
                    return
                else:
                    self.fail(f"{tc_id}: Expected PASS nhung file type bi tu choi")

            elif dialog_result == "file_too_large":
                if expected == "FAIL":
                    print(f"  PASS (file qua lon bi tu choi dung nhu mong doi)")
                    return
                else:
                    self.fail(f"{tc_id}: Expected PASS nhung file bi tu choi do qua lon")

        if comment:
            try:
                comment_box = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//textarea[@name='content']")
                ))
                comment_box.clear()
                comment_box.send_keys(comment)
            except (NoSuchElementException, TimeoutException):
                pass

        try:
            save_btn = self.wait.until(EC.presence_of_element_located(
                (By.ID, "id_submitbutton")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_btn)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", save_btn)
            time.sleep(2)
        except TimeoutException:
            self.fail(f"{tc_id}: Khong tim thay nut {BTN_SAVE}")

        error_after_save = self.get_error_message()
        status = self.get_submission_status()
        print(f"  Status: '{status}' | Error: '{error_after_save}'")

        if expected == "PASS":
            self.assertIn(
                "submitted for grading",
                status.lower(),
                f"{tc_id} FAIL: Expected 'Submitted for grading' nhung status = '{status}'"
            )
            print(f"  PASS")
        else:
            has_error = bool(error_after_save) or "submitted for grading" not in status.lower()
            self.assertTrue(
                has_error,
                f"{tc_id} FAIL: Expected loi nhung status = '{status}'"
            )
            print(f"  PASS (loi dung nhu mong doi)")

    def test_add_submission(self):
        results = {"pass": 0, "fail": 0}
        for tc in self.test_cases:
            try:
                self.run_test_case(tc)
                results["pass"] += 1
            except AssertionError as e:
                print(f"  FAIL: {e}")
                results["fail"] += 1
            except Exception as e:
                print(f"  ERROR: {e}")
                results["fail"] += 1
            finally:
                try:
                    self.go_to_assignment()
                    self.remove_existing_submission()
                except Exception:
                    pass

        print(f"\n{'='*60}")
        print(f"TONG KET: PASS={results['pass']} | FAIL={results['fail']}")

# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    unittest.main(verbosity=2)