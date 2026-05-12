# Shopping Cart Requirements

## FR-001: Add to Cart

- Authenticated users can add products to their cart from any product listing or detail page.
- Each product can be added multiple times; the quantity increments with each addition.
- Maximum quantity per line item is 99. Attempting to exceed this displays: "Maximum quantity reached for this item."
- Out-of-stock products show a disabled "Add to Cart" button and the label "Out of Stock."
- Adding an item shows a cart icon badge with the updated total item count.

## FR-002: View Cart

- Users can view all items in their cart, including product name, image, unit price, quantity, and line total.
- The cart displays an order summary: subtotal, estimated tax (10%), and total.
- An empty cart displays: "Your cart is empty" with a "Continue Shopping" link.
- Cart contents persist across sessions (stored per user account).

## FR-003: Update Cart

- Users can change the quantity of any item by editing the quantity field or using +/– controls.
- Setting quantity to 0 or clicking "Remove" removes the item from the cart with an undo option (available for 5 seconds).
- Price totals update in real time when quantities change.
- If a product goes out of stock while in the cart, it is flagged with: "This item is no longer available" and excluded from the order total.

## FR-004: Checkout

- Users must be logged in to proceed to checkout.
- The "Proceed to Checkout" button is disabled when the cart is empty.
- Guest users clicking "Proceed to Checkout" are redirected to login, then returned to cart.
- Users must provide a shipping address and select a payment method before placing an order.
- On successful order placement, cart is cleared and user sees an order confirmation page with an order number.
