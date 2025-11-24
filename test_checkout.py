import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_discount_code_save15():
    """
    Test Case: Verify applying the valid discount code "SAVE15" successfully
    applies a 15% discount to the cart total.
    """
    driver = None
    try:
        print("🚀 Initializing Chrome Driver...")
        
        # --- FIX: Automatically find and install Chrome Driver ---
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)

        # Construct the absolute path to the checkout.html file
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, 'checkout.html')
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"checkout.html not found at {file_path}. Did you copy it to the main folder?")

        driver.get(f'file:///{file_path}')
        driver.maximize_window()
        print("✅ Navigated to checkout page.")

        # 2. Pre-requisite: Add items to the cart
        # Add Wireless Mouse ($25) - Using explicit wait for stability
        mouse_add_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Add to Cart ($25)')]"))
        )
        mouse_add_button.click()
        print("✅ Added Wireless Mouse to cart.")
        
        # Add Mechanical Keyboard ($80)
        keyboard_add_button = driver.find_element(By.XPATH, "//button[contains(text(),'Add to Cart ($80)')]")
        keyboard_add_button.click()
        print("✅ Added Mechanical Keyboard to cart.")
        
        time.sleep(1) # Visual Wait

        # Get the initial cart total
        cart_total_element = driver.find_element(By.ID, "cart-total")
        initial_cart_total = float(cart_total_element.text)
        print(f"💰 Initial Cart Total: ${initial_cart_total}")

        # 3. Apply Discount
        discount_code_input = driver.find_element(By.ID, "discount-code")
        apply_discount_button = driver.find_element(By.ID, "apply-discount")
        
        discount_code = "SAVE15"
        discount_code_input.clear()
        discount_code_input.send_keys(discount_code)
        print(f"⌨️ Entered discount code: {discount_code}")
        
        apply_discount_button.click()
        print("🖱️ Clicked 'Apply' button.")

        # Wait for the total to change (Logic: 15% off)
        WebDriverWait(driver, 10).until(
            lambda d: float(d.find_element(By.ID, "cart-total").text) < initial_cart_total
        )
        print("✅ Cart total updated.")

        # 4. Verification
        actual_cart_total = float(driver.find_element(By.ID, "cart-total").text)
        discount_msg = driver.find_element(By.ID, "discount-msg").text

        print(f"💰 New Total: ${actual_cart_total}")
        print(f"📝 Message: {discount_msg}")

        # Assertions
        if "15% Off" in discount_msg and actual_cart_total < initial_cart_total:
            print("\n🎉 TEST PASSED: Discount code 'SAVE15' worked perfectly!")
        else:
            print("\n❌ TEST FAILED: Calculations or Message incorrect.")

    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")

    finally:
        if driver:
            print("\nClosing browser in 5 seconds...")
            time.sleep(5)
            driver.quit()

if __name__ == "__main__":
    test_discount_code_save15()