# Product Specifications for E-Shop Checkout

## 1. Cart Logic
- Users can add items to the cart.
- The total price must update immediately upon addition.

## 2. Discount Policy
- **Code:** "SAVE15"
- **Effect:** Applies a 15% discount on the current cart total.
- **Constraint:** Only one discount code can be applied per session.
- **Invalid Code:** If any other code is entered, the system must show an "Invalid Coupon" message.

## 3. Shipping Methods
- **Standard Shipping:** Free of charge.
- **Express Shipping:** Adds a flat fee of $10 to the total order (Note: Logic handled by backend, but UI selects it).

## 4. Payment Methods
- Supported methods: Credit Card, PayPal.