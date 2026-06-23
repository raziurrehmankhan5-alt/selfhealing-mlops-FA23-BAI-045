import pytest
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

@pytest.fixture
def driver():
    """Setup headless Chrome driver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()

class TestUI:

    def test_frontend_sentiment(self, driver):
        """Test frontend loads, accepts input, and displays result."""
        # Load the page
        driver.get(f"{BASE_URL}/")
        
        # Find text input by exact ID
        text_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "text-input"))
        )
        
        # Find submit button by exact ID
        submit_btn = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "submit-btn"))
        )
        
        # Find result output div by exact ID
        result_output = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "result-output"))
        )
        
        # Send test text
        test_text = "Spotlessly clean rooms with attentive staff and superb amenities throughout"
        text_input.send_keys(test_text)
        
        # Click submit
        submit_btn.click()
        
        # Wait for result to be non-empty
        WebDriverWait(driver, 5).until(
            lambda d: d.find_element(By.ID, "result-output").text != ""
        )
        
        # Get result text
        result_text = result_output.text
        
        # Assert result contains sentiment label or confidence
        assert result_text, "Result output is empty"
        assert "POSITIVE" in result_text or "NEGATIVE" in result_text or "Confidence" in result_text, \
            f"Result does not contain expected sentiment or confidence: {result_text}"
