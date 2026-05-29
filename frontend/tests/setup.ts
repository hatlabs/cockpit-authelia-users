import "@testing-library/jest-dom";

import type { CockpitPermission } from "../src/lib/types";

type CockpitGlobal = typeof globalThis & { cockpit?: typeof cockpit };

/**
 * Configurable permission factory used by `cockpit.permission({ admin: true })`.
 * Defaults to admin-allowed so tests that don't care about gating get the
 * unprivileged-action path "just works" behaviour.
 *
 * Tests that need to exercise the Limited Access path should call
 * `installFakePermission({ allowed: false })` in a `beforeEach` and use the
 * returned helper to emit `changed` events.
 */
export interface FakePermissionControls {
  permission: CockpitPermission;
  emitChanged: (next: boolean | null) => void;
}

/** Build a fake CockpitPermission without installing it on the global mock. */
export function makeFakePermission(initial: boolean | null): FakePermissionControls {
  const listeners = new Set<() => void>();
  const permission: CockpitPermission = {
    allowed: initial,
    addEventListener: vi.fn((event: "changed", cb: () => void) => {
      if (event === "changed") listeners.add(cb);
    }),
    removeEventListener: vi.fn((event: "changed", cb: () => void) => {
      if (event === "changed") listeners.delete(cb);
    }),
    close: vi.fn(() => listeners.clear()),
  };
  return {
    permission,
    emitChanged: (next) => {
      permission.allowed = next;
      for (const cb of listeners) cb();
    },
  };
}

/** Build a fake permission and install it as the `cockpit.permission()` factory. */
export function installFakePermission(initial: boolean | null): FakePermissionControls {
  const handle = makeFakePermission(initial);
  mockCockpit.permission = vi.fn(() => handle.permission);
  return handle;
}

// Mock cockpit object
const mockCockpit: {
  spawn: ReturnType<typeof vi.fn>;
  location: { path: string; go: ReturnType<typeof vi.fn> };
  permission?: ReturnType<typeof vi.fn>;
} = {
  spawn: vi.fn(),
  location: {
    path: "/authelia-users",
    go: vi.fn(),
  },
};

// Make cockpit available globally
(globalThis as CockpitGlobal).cockpit = mockCockpit as unknown as typeof cockpit;

export { mockCockpit };
