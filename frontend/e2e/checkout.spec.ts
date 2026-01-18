import { test, expect } from '@playwright/test';

/**
 * E2E tests for the complete checkout flow
 */

test.describe('Checkout Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the storefront homepage
    await page.goto('/');
  });

  test('should complete full checkout with MTN Mobile Money', async ({ page }) => {
    // Step 1: Browse products
    await test.step('Browse and select product', async () => {
      // Wait for products to load
      await page.waitForSelector('[data-testid="product-card"]', { timeout: 10000 });

      // Click on first product
      await page.click('[data-testid="product-card"]:first-child');

      // Wait for product detail page
      await expect(page).toHaveURL(/\/products\/.+/);
    });

    // Step 2: Add to cart
    await test.step('Add product to cart', async () => {
      // Check if variant selection is needed
      const variantSelector = page.locator('[data-testid="variant-selector"]');
      if (await variantSelector.isVisible()) {
        await variantSelector.first().click();
      }

      // Click add to cart
      await page.click('[data-testid="add-to-cart"]');

      // Verify cart badge updates
      await expect(page.locator('[data-testid="cart-badge"]')).toContainText('1');
    });

    // Step 3: View cart
    await test.step('View shopping cart', async () => {
      await page.click('[data-testid="cart-link"]');
      await expect(page).toHaveURL(/\/cart/);

      // Verify cart has items
      await expect(page.locator('[data-testid="cart-item"]')).toHaveCount(1);
    });

    // Step 4: Proceed to checkout
    await test.step('Proceed to checkout', async () => {
      await page.click('[data-testid="checkout-button"]');
      await expect(page).toHaveURL(/\/checkout/);
    });

    // Step 5: Fill delivery information
    await test.step('Fill delivery information', async () => {
      // Fill customer details
      await page.fill('[name="email"]', 'test@example.com');
      await page.fill('[name="firstName"]', 'John');
      await page.fill('[name="lastName"]', 'Doe');
      await page.fill('[name="phone"]', '256700123456');

      // Select district
      await page.selectOption('[name="district"]', { label: 'Kampala' });

      // Fill landmark
      await page.fill('[name="landmark"]', 'Near Central Market');

      // Select delivery method
      await page.click('[data-testid="delivery-method-home"]');

      // Continue to payment
      await page.click('[data-testid="continue-to-payment"]');
    });

    // Step 6: Select payment method
    await test.step('Select MTN Mobile Money payment', async () => {
      // Wait for payment section
      await page.waitForSelector('[data-testid="payment-method"]');

      // Select MTN Mobile Money
      await page.click('[data-testid="payment-mtn-momo"]');

      // Fill phone number
      await page.fill('[name="paymentPhone"]', '256700123456');

      // Verify order summary is visible
      await expect(page.locator('[data-testid="order-summary"]')).toBeVisible();
    });

    // Step 7: Place order
    await test.step('Place order', async () => {
      // Click place order button
      await page.click('[data-testid="place-order"]');

      // Wait for order confirmation or payment prompt
      await page.waitForSelector('[data-testid="order-confirmation"], [data-testid="payment-pending"]', {
        timeout: 15000
      });

      // Verify order number is displayed
      const orderNumber = await page.locator('[data-testid="order-number"]').textContent();
      expect(orderNumber).toBeTruthy();
      expect(orderNumber).toMatch(/^#\d+/);
    });
  });

  test('should validate required fields in checkout', async ({ page }) => {
    // Add a product to cart first
    await page.goto('/products');
    await page.click('[data-testid="product-card"]:first-child');
    await page.click('[data-testid="add-to-cart"]');
    await page.click('[data-testid="cart-link"]');
    await page.click('[data-testid="checkout-button"]');

    // Try to submit without filling required fields
    await page.click('[data-testid="continue-to-payment"]');

    // Verify validation errors are shown
    await expect(page.locator('[data-error="email"]')).toBeVisible();
    await expect(page.locator('[data-error="firstName"]')).toBeVisible();
    await expect(page.locator('[data-error="phone"]')).toBeVisible();
  });

  test('should validate Uganda phone number format', async ({ page }) => {
    // Navigate to checkout
    await page.goto('/products');
    await page.click('[data-testid="product-card"]:first-child');
    await page.click('[data-testid="add-to-cart"]');
    await page.click('[data-testid="cart-link"]');
    await page.click('[data-testid="checkout-button"]');

    // Fill with invalid phone numbers
    const invalidPhones = ['123456', '0700123456', '256'];

    for (const phone of invalidPhones) {
      await page.fill('[name="phone"]', phone);
      await page.click('[data-testid="continue-to-payment"]');

      // Verify error message
      const phoneError = page.locator('[data-error="phone"]');
      await expect(phoneError).toBeVisible();
      await expect(phoneError).toContainText(/256/i);
    }

    // Fill with valid phone
    await page.fill('[name="phone"]', '256700123456');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="firstName"]', 'John');
    await page.fill('[name="lastName"]', 'Doe');

    // Error should disappear
    await expect(page.locator('[data-error="phone"]')).not.toBeVisible();
  });

  test('should update delivery fee based on district selection', async ({ page }) => {
    // Navigate to checkout with item
    await page.goto('/products');
    await page.click('[data-testid="product-card"]:first-child');
    await page.click('[data-testid="add-to-cart"]');
    await page.click('[data-testid="cart-link"]');
    await page.click('[data-testid="checkout-button"]');

    // Select Kampala
    await page.selectOption('[name="district"]', { label: 'Kampala' });

    // Get delivery fee
    const kampalaFee = await page.locator('[data-testid="delivery-fee"]').textContent();
    expect(kampalaFee).toContain('UGX');

    // Select a different district
    await page.selectOption('[name="district"]', { label: 'Jinja' });

    // Verify delivery fee changed
    const jinjaFee = await page.locator('[data-testid="delivery-fee"]').textContent();
    expect(jinjaFee).toContain('UGX');
    expect(jinjaFee).not.toBe(kampalaFee);
  });

  test('should allow switching payment methods', async ({ page }) => {
    // Navigate to checkout
    await page.goto('/products');
    await page.click('[data-testid="product-card"]:first-child');
    await page.click('[data-testid="add-to-cart"]');
    await page.click('[data-testid="cart-link"]');
    await page.click('[data-testid="checkout-button"]');

    // Fill required fields
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="firstName"]', 'John');
    await page.fill('[name="lastName"]', 'Doe');
    await page.fill('[name="phone"]', '256700123456');
    await page.selectOption('[name="district"]', { label: 'Kampala' });

    await page.click('[data-testid="continue-to-payment"]');

    // Select MTN
    await page.click('[data-testid="payment-mtn-momo"]');
    await expect(page.locator('[name="paymentPhone"]')).toBeVisible();

    // Switch to Airtel
    await page.click('[data-testid="payment-airtel-money"]');
    await expect(page.locator('[name="paymentPhone"]')).toBeVisible();

    // Switch to Cash
    await page.click('[data-testid="payment-cash"]');
    await expect(page.locator('[data-testid="cash-payment-info"]')).toBeVisible();
  });

  test('should persist cart across page refreshes', async ({ page }) => {
    // Add product to cart
    await page.goto('/products');
    await page.click('[data-testid="product-card"]:first-child');
    await page.click('[data-testid="add-to-cart"]');

    // Verify cart badge
    await expect(page.locator('[data-testid="cart-badge"]')).toContainText('1');

    // Refresh page
    await page.reload();

    // Cart should still have item
    await expect(page.locator('[data-testid="cart-badge"]')).toContainText('1');

    // Navigate to cart
    await page.click('[data-testid="cart-link"]');
    await expect(page.locator('[data-testid="cart-item"]')).toHaveCount(1);
  });

  test('should allow quantity adjustment in cart', async ({ page }) => {
    // Add product to cart
    await page.goto('/products');
    await page.click('[data-testid="product-card"]:first-child');
    await page.click('[data-testid="add-to-cart"]');

    // Go to cart
    await page.click('[data-testid="cart-link"]');

    // Get initial total
    const initialTotal = await page.locator('[data-testid="cart-total"]').textContent();

    // Increase quantity
    await page.click('[data-testid="increase-quantity"]');

    // Wait for update
    await page.waitForTimeout(500);

    // Verify quantity changed
    await expect(page.locator('[data-testid="item-quantity"]')).toContainText('2');

    // Verify total updated
    const newTotal = await page.locator('[data-testid="cart-total"]').textContent();
    expect(newTotal).not.toBe(initialTotal);

    // Decrease quantity
    await page.click('[data-testid="decrease-quantity"]');
    await page.waitForTimeout(500);

    // Verify back to original
    await expect(page.locator('[data-testid="item-quantity"]')).toContainText('1');
  });

  test('should allow removing items from cart', async ({ page }) => {
    // Add product to cart
    await page.goto('/products');
    await page.click('[data-testid="product-card"]:first-child');
    await page.click('[data-testid="add-to-cart"]');

    // Go to cart
    await page.click('[data-testid="cart-link"]');

    // Verify item exists
    await expect(page.locator('[data-testid="cart-item"]')).toHaveCount(1);

    // Remove item
    await page.click('[data-testid="remove-item"]');

    // Confirm removal if there's a dialog
    const confirmButton = page.locator('[data-testid="confirm-remove"]');
    if (await confirmButton.isVisible()) {
      await confirmButton.click();
    }

    // Wait for update
    await page.waitForTimeout(500);

    // Verify cart is empty
    await expect(page.locator('[data-testid="empty-cart"]')).toBeVisible();
    await expect(page.locator('[data-testid="cart-badge"]')).not.toBeVisible();
  });
});

test.describe('Guest Checkout', () => {
  test('should allow checkout as guest', async ({ page }) => {
    // Add product
    await page.goto('/products');
    await page.click('[data-testid="product-card"]:first-child');
    await page.click('[data-testid="add-to-cart"]');
    await page.click('[data-testid="cart-link"]');

    // Proceed to checkout
    await page.click('[data-testid="checkout-button"]');

    // Should not require login
    await expect(page).toHaveURL(/\/checkout/);

    // Should have guest checkout form
    await expect(page.locator('[name="email"]')).toBeVisible();
  });
});

test.describe('Authenticated Checkout', () => {
  test('should pre-fill user details for logged-in users', async ({ page }) => {
    // Login first (assuming login functionality exists)
    await page.goto('/login');
    await page.fill('[name="email"]', 'customer@test.com');
    await page.fill('[name="password"]', 'testpass123');
    await page.click('[data-testid="login-button"]');

    // Add product
    await page.goto('/products');
    await page.click('[data-testid="product-card"]:first-child');
    await page.click('[data-testid="add-to-cart"]');
    await page.click('[data-testid="cart-link"]');
    await page.click('[data-testid="checkout-button"]');

    // Email should be pre-filled
    const emailValue = await page.inputValue('[name="email"]');
    expect(emailValue).toBe('customer@test.com');
  });
});
