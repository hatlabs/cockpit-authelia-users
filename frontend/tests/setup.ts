import "@testing-library/jest-dom";

// Mock cockpit object
const mockCockpit = {
  spawn: vi.fn(),
  location: {
    path: "/authelia-users",
    go: vi.fn(),
  },
};

// Make cockpit available globally
(globalThis as Record<string, unknown>).cockpit = mockCockpit;

export { mockCockpit };
