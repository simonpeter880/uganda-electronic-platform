import { test, expect } from '@playwright/test';

/**
 * E2E tests for mobile money payment flows
 */

test.describe('Mobile Money Payments', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: Add product to cart and navigate to payment
    await page.goto('/products');
    await page.click('[data-testid="product-card"]:first-child');
    await page.click('[data-testid="add-to-cart"]');
    await page.click('[data-testid="cart-link"]');
    await page.click('[data-testid="checkout-button"]');

    // Fill delivery info
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="firstName"]', 'John');
    await page.fill('[name="lastName"]', 'Doe');
    await page.fill('[name="phone"]', '256700123456');
    await page.selectOption('[name="district"]', { label: 'Kampala' });
    await page.fill('[name="landmark"]', 'Test Landmark');

    await page.click('[data-testid="continue-to-payment"]');
  });

  test('should display MTN Mobile Money payment option', async ({ page }) => {
    const mtnOption = page.locator('[data-testid="payment-mtn-momo"]');
    await expect(mtnOption).toBeVisible();
    await expect(mtnOption).toContainText(/MTN/i);
  });

  test('should display Airtel Money payment option', async ({ page }) => {
    const airtelOption = page.locator('[data-testid="payment-airtel-money"]');
    await expect(airtelOption).toBeVisible();
    await expect(airtelOption).toContainText(/Airtel/i);
  });

  test('should validate MTN phone number format', async ({ page }) => {
    await page.click('[data-testid="payment-mtn-momo"]');

    // Test invalid formats
    const invalidPhones = [
      '0700123456',  // Local format
      '256',         // Incomplete
      '123456789',   // Wrong format
      '257700123456' // Wrong country code
    ];

    for (const phone of invalidPhones) {
      await page.fill('[name="paymentPhone"]', phone);
      await page.click('[data-testid="place-order"]');

      // Should show validation error
      await expect(page.locator('[data-error="paymentPhone"]')).toBeVisible();
    }

    // Test valid format
    await page.fill('[name="paymentPhone"]', '256700123456');
    // Error should disappear
    await expect(page.locator('[data-error="paymentPhone"]')).not.toBeVisible();
  });

  test('should show payment instructions after order placement', async ({ page }) => {
    await page.click('[data-testid="payment-mtn-momo"]');
    await page.fill('[name="paymentPhone"]', '256700123456');
    await page.click('[data-testid="place-order"]');

    // Wait for confirmation page
    await page.waitForSelector('[data-testid="payment-instructions"]', { timeout: 15000 });

    // Should show MTN payment instructions
    await expect(page.locator('[data-testid="payment-instructions"]')).toContainText(/Enter your PIN/i);
    await expect(page.locator('[data-testid="payment-instructions"]')).toContainText(/MTN/i);
  });

  test('should display order number after payment initiation', async ({ page }) => {
    await page.click('[data-testid="payment-mtn-momo"]');
    await page.fill('[name="paymentPhone"]', '256700123456');
    await page.click('[data-testid="place-order"]');

    // Wait for order confirmation
    await page.waitForSelector('[data-testid="order-number"]', { timeout: 15000 });

    const orderNumber = await page.locator('[data-testid="order-number"]').textContent();
    expect(orderNumber).toMatch(/^#\d+/);
  });

  test('should allow checking payment status', async ({ page }) => {
    await page.click('[data-testid="payment-mtn-momo"]');
    await page.fill('[name="paymentPhone"]', '256700123456');
    await page.click('[data-testid="place-order"]');

    // Wait for confirmation page
    await page.waitForSelector('[data-testid="payment-pending"]', { timeout: 15000 });

    // Should have a "Check Status" button
    const checkStatusButton = page.locator('[data-testid="check-payment-status"]');
    await expect(checkStatusButton).toBeVisible();

    // Click to check status
    await checkStatusButton.click();

    // Should show loading or status update
    await expect(page.locator('[data-testid="status-checking"]')).toBeVisible();
  });

  test('should handle Airtel Money payment flow', async ({ page }) => {
    await page.click('[data-testid="payment-airtel-money"]');
    await page.fill('[name="paymentPhone"]', '256750123456');
    await page.click('[data-testid="place-order"]');

    // Wait for confirmation
    await page.waitForSelector('[data-testid="payment-instructions"]', { timeout: 15000 });

    // Should show Airtel-specific instructions
    await expect(page.locator('[data-testid="payment-instructions"]')).toContainText(/Airtel/i);
  });

  test('should display transaction reference', async ({ page }) => {
    await page.click('[data-testid="payment-mtn-momo"]');
    await page.fill('[name="paymentPhone"]', '256700123456');
    await page.click('[data-testid="place-order"]');

    // Wait for confirmation
    await page.waitForSelector('[data-testid="transaction-reference"]', { timeout: 15000 });

    const transactionRef = await page.locator('[data-testid="transaction-reference"]').textContent();
    expect(transactionRef).toBeTruthy();
    expect(transactionRef).toHaveLength.greaterThan(5);
  });

  test('should show payment amount in confirmation', async ({ page }) => {
    // Get cart total first
    await page.goto('/cart');
    const cartTotal = await page.locator('[data-testid="cart-total"]').textContent();

    // Continue to checkout
    await page.click('[data-testid="checkout-button"]');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="firstName"]', 'John');
    await page.fill('[name="lastName"]', 'Doe');
    await page.fill('[name="phone"]', '256700123456');
    await page.selectOption('[name="district"]', { label: 'Kampala' });
    await page.click('[data-testid="continue-to-payment"]');

    await page.click('[data-testid="payment-mtn-momo"]');
    await page.fill('[name="paymentPhone"]', '256700123456');
    await page.click('[data-testid="place-order"]');

    // Check amount in confirmation
    await page.waitForSelector('[data-testid="payment-amount"]', { timeout: 15000 });
    const paymentAmount = await page.locator('[data-testid="payment-amount"]').textContent();

    expect(paymentAmount).toContain('UGX');
  });
});

test.describe('Cash on Delivery', () => {
  test('should allow cash payment selection', async ({ page }) => {
    await page.goto('/products');
    await page.click('[data-testid="product-card"]:first-child');
    await page.click('[data-testid="add-to-cart"]');
    await page.click('[data-testid="cart-link"]');
    await page.click('[data-testid="checkout-button"]');

    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="firstName"]', 'John');
    await page.fill('[name="lastName"]', 'Doe');
    await page.fill('[name="phone"]', '256700123456');
    await page.selectOption('[name="district"]', { label: 'Kampala' });
    await page.click('[data-testid="continue-to-payment"]');

    // Select cash payment
    await page.click('[data-testid="payment-cash"]');

    // Should show cash payment info
    await expect(page.locator('[data-testid="cash-payment-info"]')).toBeVisible();
    await expect(page.locator('[data-testid="cash-payment-info"]')).toContainText(/delivery/i);
  });

  test('should not require phone number for cash payment', async ({ page }) => {
    await page.goto('/products');
    await page.click('[data-testid="product-card"]:first-child');
    await page.click('[data-testid="add-to-cart"]');
    await page.click('[data-testid="cart-link"]');
    await page.click('[data-testid="checkout-button"]');

    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="firstName"]', 'John');
    await page.fill('[name="lastName"]', 'Doe');
    await page.fill('[name="phone"]', '256700123456');
    await page.selectOption('[name="district"]', { label: 'Kampala' });
    await page.click('[data-testid="continue-to-payment"]');

    await page.click('[data-testid="payment-cash"]');

    // Payment phone field should not be required
    await expect(page.locator('[name="paymentPhone"]')).not.toBeVisible();

    // Should be able to place order
    await page.click('[data-testid="place-order"]');
    await expect(page.locator('[data-testid="order-confirmation"]')).toBeVisible({ timeout: 15000 });
  });
});

test.describe('Payment Error Handling', () => {
  test('should handle network errors gracefully', async ({ page }) => {
    // Simulate offline mode
    await page.context().setOffline(true);

    await page.goto('/products');
    await page.click('[data-testid="product-card"]:first-child');
    await page.click('[data-testid="add-to-cart"]');
    await page.click('[data-testid="cart-link"]');
    await page.click('[data-testid="checkout-button"]');

    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="firstName"]', 'John');
    await page.fill('[name="lastName"]', 'Doe');
    await page.fill('[name="phone"]', '256700123456');
    await page.selectOption('[name="district"]', { label: 'Kampala' });
    await page.click('[data-testid="continue-to-payment"]');

    await page.click('[data-testid="payment-mtn-momo"]');
    await page.fill('[name="paymentPhone"]', '256700123456');
    await page.click('[data-testid="place-order"]');

    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('[data-testid="error-message"]')).toContainText(/network|connection/i);

    // Restore connection
    await page.context().setOffline(false);
  });

  test('should allow retry after failed payment', async ({ page }) => {
    await page.goto('/products');
    await page.click('[data-testid="product-card"]:first-child');
    await page.click('[data-testid="add-to-cart"]');
    await page.click('[data-testid="cart-link"]');
    await page.click('[data-testid="checkout-button"]');

    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="firstName"]', 'John');
    await page.fill('[name="lastName"]', 'Doe');
    await page.fill('[name="phone"]', '256700123456');
    await page.selectOption('[name="district"]', { label: 'Kampala' });
    await page.click('[data-testid="continue-to-payment"]');

    await page.click('[data-testid="payment-mtn-momo"]');
    await page.fill('[name="paymentPhone"]', '256700123456');

    // Simulate failure (if there's a retry button after error)
    await page.click('[data-testid="place-order"]');

    // If error occurs, retry button should be available
    const retryButton = page.locator('[data-testid="retry-payment"]');
    if (await retryButton.isVisible({ timeout: 5000 })) {
      await retryButton.click();
      await expect(page.locator('[data-testid="payment-processing"]')).toBeVisible();
    }
  });
});
