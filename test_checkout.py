
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def run_test():
    """
    Automates the test case: "Add items to cart (e.g., total $105).
    Enter "save15" (lowercase) into the discount code field and click "Apply"."
    Verifies that an invalid coupon message is displayed and the total remains unchanged.
    """
    
    # --- 1. Setup: Determine HTML file path ---
    html_file_name = 'checkout.html'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_assets_dir = os.path.join(current_dir, 'project_assets')

    html_file_path = None
    if os.path.exists(os.path.join(current_dir, html_file_name)):
        html_file_path = os.path.join(current_dir, html_file_name)
    elif os.path.exists(os.path.join(project_assets_dir, html_file_name)):
        html_file_path = os.path.join(project_assets_dir, html_file_name)
    else:
        raise FileNotFoundError(f"'{html_file_name}' not found in current directory or 'project_assets' folder.")

    file_url = f"file:///{html_file_path}"
    print(f"Loading HTML file from: {file_url}")

    # --- 2. Setup: Initialize WebDriver ---
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        wait = WebDriverWait(driver, 10)
        
        driver.get(file_url)
        print("Browser opened and navigated to checkout page.")

        # --- Test Case Steps ---

        # 1. Add Wireless Mouse ($25)
        print("Adding Wireless Mouse to cart...")
        mouse_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='item']/span[text()='Wireless Mouse']/following-sibling::button")))
        mouse_button.click()

        # 2. Add Mechanical Keyboard ($80)
        print("Adding Mechanical Keyboard to cart...")
        keyboard_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='item']/span[text()='Mechanical Keyboard']/following-sibling::button")))
        keyboard_button.click()

        # 3. Verify initial cart total ($105)
        cart_total_element = wait.until(EC.visibility_of_element_located((By.ID, "cart-total")))
        initial_cart_total = float(cart_total_element.text)
        print(f"Current Cart Total: ${initial_cart_total}")
        assert initial_cart_total == 105.0, f"Expected initial cart total $105, but got ${initial_cart_total}"
        print("Assertion Passed: Initial cart total is $105.")

        # 4. Enter "save15" (lowercase) into the discount code field
        print("Entering 'save15' (lowercase) into discount code field...")
        discount_code_input = wait.until(EC.visibility_of_element_located((By.ID, "discount-code")))
        discount_code_input.send_keys("save15")

        # 5. Click "Apply"
        print("Clicking 'Apply' discount button...")
        apply_discount_button = wait.until(EC.element_to_be_clickable((By.ID, "apply-discount")))
        apply_discount_button.click()

        # 6. Assert that "Invalid Coupon" message is displayed
        discount_msg_element = wait.until(EC.visibility_of_element_located((By.ID, "discount-msg")))
        wait.until(EC.text_to_be_present_in_element((By.ID, "discount-msg"), "Invalid Coupon"))
        
        actual_discount_message = discount_msg_element.text
        print(f"Discount Message: '{actual_discount_message}'")
        assert "Invalid Coupon" in actual_discount_message, \
            f"Expected discount message to contain 'Invalid Coupon', but got '{actual_discount_message}'"
        print("Assertion Passed: 'Invalid Coupon' message is displayed.")

        # 7. Assert that the cart total remains $105 (no discount applied)
        updated_cart_total = float(cart_total_element.text)
        print(f"Updated Cart Total after invalid discount attempt: ${updated_cart_total}")
        assert updated_cart_total == 105.0, \
            f"Expected cart total to remain $105 after invalid discount, but got ${updated_cart_total}"
        print("Assertion Passed: Cart total remains $105 as expected.")

        print("\nTEST CASE PASSED: Successfully verified adding items and handling an invalid lowercase discount code.")

    except Exception as e:
        print(f"\nTEST CASE FAILED: An error occurred - {e}")
    finally:
        if driver:
            print("Closing browser.")
            driver.quit()

if __name__ == "__main__":
    run_test()
