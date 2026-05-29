/**
 * View-level tests for admin gating in UserListView. Verifies that the
 * Create button (both toolbar and empty-state paths) and the row-action
 * dropdown items are disabled when the Cockpit session is in Limited
 * Access mode, and enabled once admin permission is granted.
 */

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../src/lib/api", () => ({
  listUsers: vi.fn(),
  deleteUser: vi.fn(),
  updateUser: vi.fn(),
}));

import { UserListView } from "../src/views/UserListView";
import { listUsers } from "../src/lib/api";
import { installFakePermission, mockCockpit } from "./setup";

const sampleUsers = [
  {
    user_id: "alice",
    displayname: "Alice",
    email: "alice@example.com",
    disabled: false,
    groups: ["admins"],
  },
];

describe("UserListView admin gating", () => {
  beforeEach(() => {
    vi.mocked(listUsers).mockResolvedValue(sampleUsers);
  });

  afterEach(() => {
    vi.clearAllMocks();
    delete mockCockpit.permission;
  });

  it("disables the toolbar Create button in Limited Access mode", async () => {
    installFakePermission(false);
    render(<UserListView onCreateUser={vi.fn()} onEditUser={vi.fn()} />);

    const createButton = await screen.findByRole("button", { name: /create user/i });
    expect(createButton).toHaveAttribute("aria-disabled", "true");
  });

  it("enables the toolbar Create button when admin is allowed", async () => {
    installFakePermission(true);
    render(<UserListView onCreateUser={vi.fn()} onEditUser={vi.fn()} />);

    const createButton = await screen.findByRole("button", { name: /create user/i });
    expect(createButton).not.toHaveAttribute("aria-disabled", "true");
  });

  it("does not invoke onCreateUser when the disabled button is clicked", async () => {
    installFakePermission(false);
    const onCreateUser = vi.fn();
    const user = userEvent.setup();
    render(<UserListView onCreateUser={onCreateUser} onEditUser={vi.fn()} />);

    const createButton = await screen.findByRole("button", { name: /create user/i });
    await user.click(createButton);
    expect(onCreateUser).not.toHaveBeenCalled();
  });

  it("disables the empty-state Create button when no users exist in Limited Access mode", async () => {
    vi.mocked(listUsers).mockResolvedValue([]);
    installFakePermission(false);
    render(<UserListView onCreateUser={vi.fn()} onEditUser={vi.fn()} />);

    const createButton = await screen.findByRole("button", { name: /create user/i });
    expect(createButton).toHaveAttribute("aria-disabled", "true");
  });

  it("disables the row action dropdown items in Limited Access mode", async () => {
    installFakePermission(false);
    const user = userEvent.setup();
    render(<UserListView onCreateUser={vi.fn()} onEditUser={vi.fn()} />);

    const actionsToggle = await screen.findByRole("button", { name: /actions for alice/i });
    await user.click(actionsToggle);

    for (const label of [/edit/i, /disable/i, /delete/i]) {
      const item = await screen.findByRole("menuitem", { name: label });
      expect(item).toHaveAttribute("aria-disabled", "true");
    }
  });

  it("enables the row action dropdown items when admin is allowed", async () => {
    installFakePermission(true);
    const user = userEvent.setup();
    render(<UserListView onCreateUser={vi.fn()} onEditUser={vi.fn()} />);

    const actionsToggle = await screen.findByRole("button", { name: /actions for alice/i });
    await user.click(actionsToggle);

    await waitFor(async () => {
      const editItem = await screen.findByRole("menuitem", { name: /edit/i });
      expect(editItem).not.toHaveAttribute("aria-disabled", "true");
    });
  });
});
