/**
 * View-level tests for admin gating + listGroups error surfacing in
 * UserFormView. Verifies the submit button is gated when not admin and
 * that a listGroups rejection produces an inline error instead of the
 * previous silent failure.
 */

import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../src/lib/api", () => ({
  createUser: vi.fn(),
  getUser: vi.fn(),
  listGroups: vi.fn(),
  updateUser: vi.fn(),
}));

import { UserFormView } from "../src/views/UserFormView";
import { listGroups } from "../src/lib/api";
import { installFakePermission, mockCockpit } from "./setup";

describe("UserFormView admin gating", () => {
  beforeEach(() => {
    vi.mocked(listGroups).mockResolvedValue(["admins", "users"]);
  });

  afterEach(() => {
    vi.clearAllMocks();
    delete mockCockpit.permission;
  });

  it("disables the submit button in Limited Access mode", async () => {
    installFakePermission(false);
    render(<UserFormView mode="create" onSave={vi.fn()} onCancel={vi.fn()} />);

    const submit = await screen.findByRole("button", { name: /create user/i });
    expect(submit).toHaveAttribute("aria-disabled", "true");
  });

  it("enables the submit button when admin is allowed", async () => {
    installFakePermission(true);
    render(<UserFormView mode="create" onSave={vi.fn()} onCancel={vi.fn()} />);

    const submit = await screen.findByRole("button", { name: /create user/i });
    expect(submit).not.toHaveAttribute("aria-disabled", "true");
  });
});

describe("UserFormView listGroups error surfacing", () => {
  afterEach(() => {
    vi.clearAllMocks();
    delete mockCockpit.permission;
  });

  it("surfaces a listGroups rejection inline instead of failing silently", async () => {
    vi.mocked(listGroups).mockRejectedValue(new Error("Not permitted to perform this action."));
    installFakePermission(true);

    render(<UserFormView mode="create" onSave={vi.fn()} onCancel={vi.fn()} />);

    expect(await screen.findByText(/could not load groups/i)).toBeInTheDocument();
    expect(
      await screen.findByText(/not permitted to perform this action/i)
    ).toBeInTheDocument();
  });

  it("still renders the form when listGroups fails", async () => {
    vi.mocked(listGroups).mockRejectedValue(new Error("boom"));
    installFakePermission(true);

    render(<UserFormView mode="create" onSave={vi.fn()} onCancel={vi.fn()} />);

    expect(await screen.findByRole("textbox", { name: /username/i })).toBeInTheDocument();
    expect(await screen.findByRole("textbox", { name: /display name/i })).toBeInTheDocument();
  });
});
