# E2E Testing Strategy for Market Outlook Dashboard

## 1. Objective
Ensure the stability and reliability of the "Weekly Intelligence" dashboard, specifically the AI-generated outlooks (Weekly, Monthly, Seasonality), following the UI refactoring.

## 2. Recommended Framework: Playwright
We recommend using **Playwright** for E2E testing due to its excellent cross-browser support, auto-waiting features, and ability to handle asynchronous AI data loading.

### Setup Instructions
```bash
npm install -D @playwright/test
npx playwright install
```

## 3. Key Test Scenarios

### A. Core Navigation & Rendering
- **Scenario**: User switches between "Weekly", "Monthly", and "Seasonality" types.
- **Assertion**: Correct tab is active, and the "Generate" button is visible.
- **Assertion**: Header color and icon change based on the selected type (Blue/Weekly, Purple/Monthly, Indigo/Seasonality).

### B. AI Generation Flow
- **Scenario**: User clicks "Generate" button.
- **Assertion**: "Analyzing..." loader appears.
- **Assertion**: "This may take 30-60 seconds" message is displayed.
- **Scenario**: API returns successful data.
- **Assertion**: Loading state disappears, and professional dashboard views (Layer 1 header, Tabs, Stats) appear.

### C. Tabbed View Interactivity
- **Scenario**: Weekly Analysis - User clicks through tabs ('Overview', 'Sectors', 'Risk', 'Agent Details').
- **Assertion**: Content changes appropriately for each tab.
- **Assertion**: Gauges and StatCards render with numerical values or 'N/A'.

### D. Data Consistency & Edge Cases
- **Scenario**: Ticker or Sector context changes.
- **Assertion**: Analysis state is reset, and "Generate" button reappears.
- **Scenario**: API returns an error.
- **Assertion**: Red error alert appears with descriptive error message.

## 4. Test Structure (Example - Playwright)
```typescript
import { test, expect } from '@playwright/test';

test.describe('Market Outlook Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/market-outlook');
  });

  test('should generate weekly analysis and show tabs', async ({ page }) => {
    // Select Weekly
    await page.click('text=Weekly AI Outlook');
    
    // Trigger Generation
    await page.click('button:has-text("Generate")');
    
    // Wait for analysis to complete (handle timeout)
    await expect(page.locator('text=Weekly AI Thesis')).toBeVisible({ timeout: 60000 });
    
    // Check Tabs
    await page.click('text=Sectors');
    await expect(page.locator('text=Sector Allocation Matrix')).toBeVisible();
    
    // Verify Stance Badge
    await expect(page.locator('[data-testid="stance-badge"]')).toBeVisible();
  });
});
```

## 5. Continuous Integration (GitHub Actions)
Integrate tests into `.github/workflows/e2e.yml` to run on every Pull Request to ensure UI changes don't break the data consumption flow.
