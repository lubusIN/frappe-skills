```markdown
# Cypress UI Testing Reference

## Overview
Frappe uses Cypress for end-to-end UI testing. Cypress tests simulate real user interactions with the Desk interface.

## Setup

### Prerequisites
```bash
# Install Cypress for your app
cd apps/my_app
npm install cypress --save-dev

# Or use bench setup
bench setup requirements --dev
```

### Directory Structure
```
my_app/
├── cypress/
│   ├── fixtures/         # Test data files
│   ├── integration/      # Test files
│   │   └── my_app/
│   │       └── sample_doc.js
│   ├── plugins/          # Cypress plugins
│   ├── support/          # Custom commands
│   │   ├── commands.js
│   │   └── index.js
│   └── videos/           # Test recordings
├── cypress.json          # Cypress config
└── package.json
```

### Configuration
```json
// cypress.json
{
  "baseUrl": "http://testsite.localhost:8000",
  "projectId": "my_app",
  "viewportWidth": 1280,
  "viewportHeight": 720,
  "defaultCommandTimeout": 10000,
  "retries": {
    "runMode": 2,
    "openMode": 0
  },
  "env": {
    "adminUser": "Administrator",
    "adminPassword": "admin"
  }
}
```

## Running Tests

### Via Bench
```bash
# Run all UI tests for app
bench --site testsite run-ui-tests my_app

# Run in headless mode
bench --site testsite run-ui-tests my_app --headless

# Run specific test file
bench --site testsite run-ui-tests my_app --spec "cypress/integration/my_app/sample_doc.js"
```

### Via Cypress CLI
```bash
# Open Cypress Test Runner
npx cypress open

# Run headless
npx cypress run

# Run specific test
npx cypress run --spec "cypress/integration/my_app/*.js"
```

## Writing Tests

### Basic Test Structure
```javascript
// cypress/integration/my_app/sample_doc.js

context("Sample Doc", () => {
    before(() => {
        cy.login();
        cy.visit("/app/sample-doc");
    });

    it("creates a new Sample Doc", () => {
        cy.click_list_row_checkbox(0);
        cy.get(".primary-action").contains("New").click();
        
        cy.fill_field("title", "Test Document");
        cy.fill_field("status", "Open", "Select");
        
        cy.get_field("title").should("have.value", "Test Document");
        
        cy.get(".primary-action").contains("Save").click();
        
        cy.get_frm().should("contain", "Test Document");
    });

    it("updates an existing Sample Doc", () => {
        cy.visit("/app/sample-doc/Test Document");
        
        cy.fill_field("status", "In Progress", "Select");
        cy.get(".primary-action").contains("Save").click();
        
        cy.get_field("status").should("have.value", "In Progress");
    });
});
```

### Frappe Custom Commands

```javascript
// cypress/support/commands.js

// Login command
Cypress.Commands.add("login", (user, password) => {
    cy.request({
        url: "/api/method/login",
        method: "POST",
        body: {
            usr: user || Cypress.env("adminUser"),
            pwd: password || Cypress.env("adminPassword")
        }
    });
});

// Fill field by fieldname
Cypress.Commands.add("fill_field", (fieldname, value, fieldtype = "Data") => {
    if (fieldtype === "Select") {
        cy.get(`[data-fieldname="${fieldname}"]`).click();
        cy.get(`.frappe-control[data-fieldname="${fieldname}"] .awesomplete`)
            .find("li")
            .contains(value)
            .click();
    } else if (fieldtype === "Link") {
        cy.get(`[data-fieldname="${fieldname}"] input`).type(value);
        cy.get(".awesomplete li").contains(value).click();
    } else if (fieldtype === "Check") {
        if (value) {
            cy.get(`[data-fieldname="${fieldname}"] input`).check();
        } else {
            cy.get(`[data-fieldname="${fieldname}"] input`).uncheck();
        }
    } else {
        cy.get(`[data-fieldname="${fieldname}"] input, [data-fieldname="${fieldname}"] textarea`)
            .clear()
            .type(value);
    }
});

// Get field value
Cypress.Commands.add("get_field", (fieldname) => {
    return cy.get(`[data-fieldname="${fieldname}"] input, [data-fieldname="${fieldname}"] textarea`);
});

// Get form element
Cypress.Commands.add("get_frm", () => {
    return cy.get(".frappe-form");
});

// Click primary action button
Cypress.Commands.add("click_primary_action", () => {
    cy.get(".primary-action").click();
});

// Click list row checkbox
Cypress.Commands.add("click_list_row_checkbox", (index) => {
    cy.get(`.list-row:nth-child(${index + 1}) .list-row-checkbox`).click();
});

// Wait for indicator to disappear
Cypress.Commands.add("wait_for_ajax", () => {
    cy.get(".indicator-pill").should("not.exist");
});
```

## Common Test Patterns

### Form Operations
```javascript
// Create new document
it("creates new document", () => {
    cy.visit("/app/customer/new-customer-1");
    cy.fill_field("customer_name", "Acme Corp");
    cy.fill_field("customer_type", "Company", "Select");
    cy.get(".primary-action").contains("Save").click();
    cy.url().should("not.contain", "new-customer-1");
});

// Edit document
it("edits existing document", () => {
    cy.visit("/app/customer/CUST-001");
    cy.fill_field("customer_name", "Acme Corporation");
    cy.get(".primary-action").contains("Save").click();
    cy.get(".msgprint").should("contain", "Saved");
});

// Delete document
it("deletes document", () => {
    cy.visit("/app/customer/CUST-TO-DELETE");
    cy.get(".menu-btn-group").click();
    cy.get(".dropdown-menu").contains("Delete").click();
    cy.get(".modal-footer").contains("Yes").click();
});
```

### List Operations
```javascript
// Filter list
it("filters list by status", () => {
    cy.visit("/app/sales-order");
    cy.get(".filter-section").click();
    cy.fill_field("status", "Draft", "Select");
    cy.get(".filter-action-buttons").contains("Apply").click();
    cy.get(".list-row").should("have.length.greaterThan", 0);
});

// Bulk action
it("performs bulk action", () => {
    cy.visit("/app/todo");
    cy.click_list_row_checkbox(0);
    cy.click_list_row_checkbox(1);
    cy.get(".actions-btn-group").click();
    cy.get(".dropdown-menu").contains("Delete").click();
});
```

### Dialog Interactions
```javascript
it("handles dialog prompt", () => {
    cy.visit("/app/sales-order/SO-001");
    cy.get(".custom-actions").contains("Request Approval").click();
    
    // Fill dialog fields
    cy.get(".modal-dialog [data-fieldname='reason'] textarea")
        .type("Urgent customer request");
    
    // Click dialog action
    cy.get(".modal-dialog .btn-primary").contains("Submit").click();
    
    cy.get(".msgprint").should("contain", "Request sent");
});
```

### Child Table Operations
```javascript
it("adds child table rows", () => {
    cy.visit("/app/sales-order/new-sales-order-1");
    
    // Add row
    cy.get("[data-fieldname='items'] .grid-add-row").click();
    
    // Fill child row
    cy.get("[data-fieldname='items'] .grid-row:last-child")
        .find("[data-fieldname='item_code'] input")
        .type("ITEM-001");
    
    cy.get(".awesomplete li").first().click();
    
    cy.get("[data-fieldname='items'] .grid-row:last-child")
        .find("[data-fieldname='qty'] input")
        .clear()
        .type("5");
});
```

## Test Data Management

### Fixtures
```javascript
// cypress/fixtures/customer.json
{
    "customer_name": "Test Customer",
    "customer_type": "Company",
    "territory": "All Territories"
}
```

```javascript
// Using fixtures
it("creates customer from fixture", function() {
    cy.fixture("customer").then((customer) => {
        cy.visit("/app/customer/new-customer-1");
        cy.fill_field("customer_name", customer.customer_name);
        cy.fill_field("customer_type", customer.customer_type, "Select");
    });
});
```

### API Setup
```javascript
// Create test data via API
before(() => {
    cy.request({
        method: "POST",
        url: "/api/resource/Customer",
        body: {
            customer_name: "Cypress Test Customer",
            customer_type: "Company"
        }
    });
});

// Cleanup via API
after(() => {
    cy.request({
        method: "DELETE",
        url: "/api/resource/Customer/Cypress Test Customer"
    });
});
```

## Best Practices

### Selectors
```javascript
// ❌ Fragile selectors
cy.get(".btn-primary-dark").click();
cy.get("div > ul > li:nth-child(3)").click();

// ✅ Robust selectors
cy.get("[data-fieldname='customer']").click();
cy.get(".primary-action").contains("Save").click();
cy.get("[data-page-container]").contains("Customer").click();
```

### Waits
```javascript
// ❌ Fixed waits (slow, unreliable)
cy.wait(5000);

// ✅ Conditional waits
cy.get(".indicator-pill").should("not.exist");
cy.get("[data-fieldname='name']").should("be.visible");
cy.url().should("contain", "/app/customer/");
```

### Test Independence
```javascript
// ❌ Tests depend on each other
it("creates customer", () => { /* creates CUST-001 */ });
it("edits customer", () => { /* assumes CUST-001 exists */ });

// ✅ Independent tests
beforeEach(() => {
    // Create fresh test data
    cy.request("POST", "/api/resource/Customer", {...});
});

afterEach(() => {
    // Cleanup
    cy.request("DELETE", "/api/resource/Customer/Test Customer");
});
```

Sources: UI Testing, Cypress Documentation (official docs)
```