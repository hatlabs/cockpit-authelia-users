import { createRoot } from "react-dom/client";
import { useState, useEffect, useCallback } from "react";
import { Page, PageSection } from "@patternfly/react-core";

// Import both PatternFly CSS files
// patternfly-base.css contains design tokens (--pf-t--global--* variables)
// patternfly.css contains component styles that reference those tokens
// Both are required for proper styling!
import "@patternfly/patternfly/patternfly-base.css";
import "@patternfly/patternfly/patternfly.css";

// Import dark theme support (must be after PatternFly CSS)
import "./dark-theme";

// Import our custom CSS overrides LAST so they take precedence over PatternFly defaults
import "./authelia-users.css";

import { UserListView } from "./views/UserListView";
import { UserFormView } from "./views/UserFormView";

// Import types to ensure cockpit global is available
import "./lib/types";

type ViewState = { type: "list" } | { type: "create" } | { type: "edit"; userId: string };

/**
 * Parse cockpit.location.path to determine current view state.
 * URL structure:
 *   [] or [''] -> list view
 *   ['create'] -> create view
 *   ['edit', userId] -> edit view
 */
function parseRoute(): ViewState {
  const path = cockpit.location.path;

  if (path.length === 0 || (path.length === 1 && path[0] === "")) {
    return { type: "list" };
  }

  if (path[0] === "create") {
    return { type: "create" };
  }

  if (path[0] === "edit" && path[1]) {
    return { type: "edit", userId: path[1] };
  }

  // Default to list view for unknown routes
  return { type: "list" };
}

/**
 * Navigate to a new route using cockpit.location.
 */
function navigateTo(path: string[]) {
  cockpit.location.go(path);
}

function App() {
  const [view, setView] = useState<ViewState>(parseRoute);

  // Handle location changes (browser back/forward buttons)
  useEffect(() => {
    const handleLocationChange = () => {
      setView(parseRoute());
    };

    cockpit.addEventListener("locationchanged", handleLocationChange);
    return () => {
      cockpit.removeEventListener("locationchanged", handleLocationChange);
    };
  }, []);

  const handleCreateUser = useCallback(() => {
    navigateTo(["create"]);
  }, []);

  const handleEditUser = useCallback((userId: string) => {
    navigateTo(["edit", userId]);
  }, []);

  const handleBack = useCallback(() => {
    // Use browser history back for natural navigation
    window.history.back();
  }, []);

  return (
    <Page id="authelia-users" className="pf-m-no-sidebar">
      <PageSection hasBodyWrapper={false}>
        {view.type === "list" && (
          <UserListView onCreateUser={handleCreateUser} onEditUser={handleEditUser} />
        )}
        {view.type === "create" && (
          <UserFormView mode="create" onSave={handleBack} onCancel={handleBack} />
        )}
        {view.type === "edit" && (
          <UserFormView
            mode="edit"
            userId={view.userId}
            onSave={handleBack}
            onCancel={handleBack}
          />
        )}
      </PageSection>
    </Page>
  );
}

const container = document.getElementById("root");
if (container) {
  const root = createRoot(container);
  root.render(<App />);
}
