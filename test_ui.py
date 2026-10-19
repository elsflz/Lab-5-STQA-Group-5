
"""Lab 5: Web UI Automation using Selenium and Pytest."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.login_page import LoginPage
from pages.task_page import NewTaskPage, TaskListPage

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo1234"


def test_login_with_valid_credentials(driver, base_url):
    login_page = LoginPage(driver, base_url)
    login_page.open()
    login_page.login(DEMO_USERNAME, DEMO_PASSWORD)

    # Wait for the new-task form to appear
    title_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(NewTaskPage.TITLE_INPUT)
    )

    assert title_input.is_displayed()


def test_login_with_invalid_credentials(driver, base_url):
    login_page = LoginPage(driver, base_url)
    login_page.open()
    login_page.login("demo", "wrong-password")

    error = login_page.wait_for_error()
    assert "Invalid username or password" in error.text


def test_create_task(driver, base_url):
    login_page = LoginPage(driver, base_url)
    login_page.open()
    login_page.login(DEMO_USERNAME, DEMO_PASSWORD)

    new_task_page = NewTaskPage(driver, base_url)
    new_task_page.open()
    new_task_page.create_task(
        title="Prepare slides",
        priority="2",
        due_date="2026-12-01",
        hours="3"
    )

    new_task_page.wait_for_success()

    success_banner = driver.find_element(
        *NewTaskPage.SUCCESS_BANNER
    )
    assert success_banner.is_displayed()


def test_mark_task_complete_and_logout(driver, base_url):
    login_page = LoginPage(driver, base_url)
    login_page.open()
    login_page.login(DEMO_USERNAME, DEMO_PASSWORD)

    # Create a task before marking it complete
    new_task_page = NewTaskPage(driver, base_url)
    new_task_page.open()
    new_task_page.create_task(
        title="Complete STQA Lab 5",
        priority="3",
        due_date="2026-12-01",
        hours="2"
    )
    new_task_page.wait_for_success()

    # Open the task list
    task_list_page = TaskListPage(driver, base_url)
    task_list_page.open()

    # Find the row containing the task we created
    task_row = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//tr[.//*[contains(text(), 'Complete STQA Lab 5')]]"
            )
        )
    )

    # Find the Complete button inside that row
    complete_button = task_row.find_element(
        By.CSS_SELECTOR,
        "button[data-task-id]"
    )

    # Get the actual task ID
    task_id = complete_button.get_attribute("data-task-id")
    assert task_id is not None

    # Mark the task as completed
    task_list_page.mark_complete(task_id)

    # Wait until its status changes to Completed
    task_list_page.wait_until_completed(task_id)

    # Verify the task is completed
    status = driver.find_element(
        *TaskListPage.status_cell(task_id)
    )
    assert "Completed" in status.text

    # Click the logout link
    driver.find_element(By.ID, "logout-link").click()

    # Wait until the login page appears
    WebDriverWait(driver, 10).until(
        EC.url_contains("/login")
    )

    # Verify logout was successful
    assert "/login" in driver.current_url
