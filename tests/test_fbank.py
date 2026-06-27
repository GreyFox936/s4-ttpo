"""Selenium тесты"""

from __future__ import annotations

from urllib.parse import urlencode

from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


WAIT = 5
TRANSFER_BUTTON_XPATH = "//button[normalize-space()='Перевести'] | //*[@role='button' and normalize-space()='Перевести']"


def open_app(driver, base_url: str, *, balance: int = 30000, reserved: int = 20001) -> None:
    query = urlencode({"balance": balance, "reserved": reserved})
    driver.get(f"{base_url}/?{query}")


def click_account(driver, account_name: str) -> None:
    account_title = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.XPATH, f"//h2[normalize-space()='{account_name}']"))
    )
    account_title.click()


def get_card_input(driver):
    return WebDriverWait(driver, WAIT).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='0000 0000 0000 0000']"))
    )


def get_amount_input(driver):
    return WebDriverWait(driver, WAIT).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='1000']"))
    )


def fill_card_number(driver, card_number: str = "1111222233334444"):
    card = get_card_input(driver)
    card.send_keys(card_number)
    return card


def set_amount(driver, amount: str):
    amount_input = get_amount_input(driver)
    amount_input.send_keys(Keys.CONTROL, "a")
    amount_input.send_keys(Keys.BACKSPACE)
    amount_input.send_keys(amount)
    return amount_input


def has_transfer_button(driver) -> bool:
    return bool(driver.find_elements(By.XPATH, TRANSFER_BUTTON_XPATH))


def wait_for_transfer_button(driver):
    return WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.XPATH, TRANSFER_BUTTON_XPATH))
    )


def wait_until_no_transfer_button(driver) -> None:
    WebDriverWait(driver, WAIT).until(
        lambda browser: len(browser.find_elements(By.XPATH, TRANSFER_BUTTON_XPATH)) == 0
    )


def test_accounts_are_displayed(driver, base_url):
    """Smoke на главной странице видны основные счета."""
    open_app(driver, base_url, balance=30000, reserved=20001)

    assert "F-Bank" in driver.find_element(By.TAG_NAME, "body").text
    assert driver.find_element(By.XPATH, "//h2[normalize-space()='Рубли']").is_displayed()
    assert driver.find_element(By.XPATH, "//h2[normalize-space()='Доллары']").is_displayed()
    assert driver.find_element(By.XPATH, "//h2[normalize-space()='Евро']").is_displayed()
    assert driver.find_element(By.ID, "rub-sum").text == "30'000"
    assert driver.find_element(By.ID, "rub-reserved").text == "20'001"


def test_ruble_transfer_form_opens_after_account_selection(driver, base_url):
    """Smoke: выбор рублёвого счёта открывает форму перевода"""
    open_app(driver, base_url)
    click_account(driver, "Рубли")

    assert "Перевод на карту" in driver.find_element(By.TAG_NAME, "body").text
    assert get_card_input(driver).is_displayed()


def test_card_number_is_formatted_for_16_digits(driver, base_url):
    """Валидируем: 16 цифр карты форматируются группами по четыре"""
    open_app(driver, base_url)
    click_account(driver, "Рубли")

    card = fill_card_number(driver, "1111222233334444")

    assert card.get_attribute("value") == "1111 2222 3333 4444"
    assert get_amount_input(driver).is_displayed()


def test_valid_ruble_transfer_is_accepted(driver, base_url):
    """Позитивный сценарий: валидный рублёвый перевод отправляется"""
    open_app(driver, base_url, balance=5000, reserved=0)
    click_account(driver, "Рубли")
    fill_card_number(driver)
    set_amount(driver, "1000")

    assert driver.find_element(By.ID, "comission").text == "100"

    button = wait_for_transfer_button(driver)
    button.click()

    alert = WebDriverWait(driver, WAIT).until(lambda browser: browser.switch_to.alert)
    assert "принят банком" in alert.text
    alert.accept()


def test_insufficient_funds_message_is_shown(driver, base_url):
    """Негативный сценарий: перевод сверх доступной суммы блокируеться"""
    open_app(driver, base_url, balance=1000, reserved=0)
    click_account(driver, "Рубли")
    fill_card_number(driver)
    set_amount(driver, "5000")

    wait_until_no_transfer_button(driver)
    assert "Недостаточно средств на счете" in driver.find_element(By.TAG_NAME, "body").text


def test_defect_negative_transfer_amount_must_be_rejected(driver, base_url):
    """DEF-001: приложение принимает отрицательную сумму перевода"""
    open_app(driver, base_url, balance=5000, reserved=0)
    click_account(driver, "Рубли")
    fill_card_number(driver)
    set_amount(driver, "-1000")

    assert not has_transfer_button(driver), (
        "Отрицательная сумма должна отклоняться но кнопка перевода отображается"
    )


def test_defect_transfer_allowed_when_amount_plus_commission_equals_available_balance(driver, base_url):
    """DEF-002: перевод блокируется когда сумма с комиссией ровно равна доступному остатку"""
    open_app(driver, base_url, balance=1100, reserved=0)
    click_account(driver, "Рубли")
    fill_card_number(driver)
    set_amount(driver, "1000")

    assert has_transfer_button(driver), (
        "Перевод должен быть доступен если усмма с комиссией равна доступному остатку "
        "1000 + 100 == 1100"
    )


def test_defect_card_number_must_not_accept_more_than_16_digits(driver, base_url):
    """DEF-003: поле номера карты принимает 17 цифр вместо ограничения в 16"""
    open_app(driver, base_url, balance=5000, reserved=0)
    click_account(driver, "Рубли")

    card = fill_card_number(driver, "11112222333344445")
    actual_digits = card.get_attribute("value").replace(" ", "")

    assert actual_digits == "1111222233334444", (
        "Поле карты должно игнорировать 17-ю цифру или отклонять значение "
        f"фактически ведено {len(actual_digits)} цифр - {actual_digits}"
    )


def test_defect_currency_transfer_must_use_selected_account_balance(driver, base_url):
    """DEF-004: выбран долларовый счёт но доступность перевода считается по рублёвому балансу"""
    open_app(driver, base_url, balance=0, reserved=0)
    click_account(driver, "Доллары")
    fill_card_number(driver)
    set_amount(driver, "50")

    assert has_transfer_button(driver), (
        "На выбранном долларовом счёте отображается 100, поэтому перевод 50 usd должен быть доступен "
        "Если переводы в валюте не поддерживаются интерфейс должен явно сообщать об этом"
    )
