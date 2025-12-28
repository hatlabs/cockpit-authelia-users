import { describe, it, expect, vi, beforeEach } from "vitest";
import { mockCockpit } from "./setup";

// Import after mocking
import { listUsers, getUser, createUser, updateUser, deleteUser, listGroups } from "../src/lib/api";

describe("API wrapper", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("listUsers", () => {
    it("calls bridge with list-users command", async () => {
      const mockUsers = [
        { user_id: "john", displayname: "John Doe", email: "john@example.com", disabled: false, groups: ["users"] },
      ];

      mockCockpit.spawn.mockReturnValue({
        then: (onSuccess: (output: string) => void) => {
          onSuccess(JSON.stringify(mockUsers));
        },
        input: vi.fn(),
      });

      const result = await listUsers();

      expect(mockCockpit.spawn).toHaveBeenCalledWith(
        ["cockpit-authelia-users-bridge", "list-users"],
        { superuser: "require", err: "message" }
      );
      expect(result).toEqual(mockUsers);
    });
  });

  describe("getUser", () => {
    it("calls bridge with get-user command", async () => {
      const mockUser = { user_id: "john", displayname: "John Doe", email: "john@example.com", disabled: false, groups: [] };

      mockCockpit.spawn.mockReturnValue({
        then: (onSuccess: (output: string) => void) => {
          onSuccess(JSON.stringify(mockUser));
        },
        input: vi.fn(),
      });

      const result = await getUser("john");

      expect(mockCockpit.spawn).toHaveBeenCalledWith(
        ["cockpit-authelia-users-bridge", "get-user", "john"],
        { superuser: "require", err: "message" }
      );
      expect(result).toEqual(mockUser);
    });
  });

  describe("createUser", () => {
    it("calls bridge with create-user command and sends JSON input", async () => {
      const newUser = {
        user_id: "newuser",
        displayname: "New User",
        email: "new@example.com",
        password: "secret123",
      };
      const mockResult = { user_id: "newuser", displayname: "New User", email: "new@example.com", disabled: false, groups: [] };
      const mockInput = vi.fn();

      mockCockpit.spawn.mockReturnValue({
        then: (onSuccess: (output: string) => void) => {
          onSuccess(JSON.stringify(mockResult));
        },
        input: mockInput,
      });

      const result = await createUser(newUser);

      expect(mockCockpit.spawn).toHaveBeenCalledWith(
        ["cockpit-authelia-users-bridge", "create-user"],
        { superuser: "require", err: "message" }
      );
      expect(mockInput).toHaveBeenCalledWith(JSON.stringify(newUser));
      expect(result).toEqual(mockResult);
    });
  });

  describe("updateUser", () => {
    it("calls bridge with update-user command and sends JSON input", async () => {
      const updateData = { displayname: "Updated Name" };
      const mockResult = { user_id: "john", displayname: "Updated Name", email: "john@example.com", disabled: false, groups: [] };
      const mockInput = vi.fn();

      mockCockpit.spawn.mockReturnValue({
        then: (onSuccess: (output: string) => void) => {
          onSuccess(JSON.stringify(mockResult));
        },
        input: mockInput,
      });

      const result = await updateUser("john", updateData);

      expect(mockCockpit.spawn).toHaveBeenCalledWith(
        ["cockpit-authelia-users-bridge", "update-user", "john"],
        { superuser: "require", err: "message" }
      );
      expect(mockInput).toHaveBeenCalledWith(JSON.stringify(updateData));
      expect(result).toEqual(mockResult);
    });
  });

  describe("deleteUser", () => {
    it("calls bridge with delete-user command", async () => {
      const mockResult = { success: true };

      mockCockpit.spawn.mockReturnValue({
        then: (onSuccess: (output: string) => void) => {
          onSuccess(JSON.stringify(mockResult));
        },
        input: vi.fn(),
      });

      const result = await deleteUser("john");

      expect(mockCockpit.spawn).toHaveBeenCalledWith(
        ["cockpit-authelia-users-bridge", "delete-user", "john"],
        { superuser: "require", err: "message" }
      );
      expect(result).toEqual(mockResult);
    });
  });

  describe("listGroups", () => {
    it("calls bridge with list-groups command", async () => {
      const mockGroups = ["admins", "users", "guests"];

      mockCockpit.spawn.mockReturnValue({
        then: (onSuccess: (output: string) => void) => {
          onSuccess(JSON.stringify(mockGroups));
        },
        input: vi.fn(),
      });

      const result = await listGroups();

      expect(mockCockpit.spawn).toHaveBeenCalledWith(
        ["cockpit-authelia-users-bridge", "list-groups"],
        { superuser: "require", err: "message" }
      );
      expect(result).toEqual(mockGroups);
    });
  });
});
