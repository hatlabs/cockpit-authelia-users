/**
 * API wrapper for backend communication via cockpit.spawn().
 * All operations require superuser privileges.
 */

import type { User, UserInput, CreateUserInput, ApiError } from "./types";

declare const cockpit: {
  spawn: (
    command: string[],
    options?: { superuser?: string; err?: string }
  ) => {
    then: (
      onSuccess: (output: string) => void,
      onError: (error: { message: string; exit_status?: number }) => void
    ) => void;
    input: (data: string) => void;
  };
};

const BRIDGE_COMMAND = "cockpit-authelia-users-bridge";

/**
 * Execute a bridge command and return the parsed JSON result.
 */
async function execute<T>(args: string[], input?: string): Promise<T> {
  return new Promise((resolve, reject) => {
    const proc = cockpit.spawn([BRIDGE_COMMAND, ...args], {
      superuser: "require",
      err: "message",
    });

    if (input) {
      proc.input(input);
    }

    proc.then(
      (output: string) => {
        try {
          resolve(JSON.parse(output) as T);
        } catch {
          reject(new Error(`Invalid JSON response: ${output}`));
        }
      },
      (error: { message: string; exit_status?: number }) => {
        // Try to parse error as JSON
        try {
          const apiError = JSON.parse(error.message) as ApiError;
          reject(new Error(apiError.message));
        } catch {
          reject(new Error(error.message));
        }
      }
    );
  });
}

/**
 * List all users.
 */
export async function listUsers(): Promise<User[]> {
  return execute<User[]>(["list-users"]);
}

/**
 * Get a single user by ID.
 */
export async function getUser(userId: string): Promise<User> {
  return execute<User>(["get-user", userId]);
}

/**
 * Create a new user.
 */
export async function createUser(data: CreateUserInput): Promise<User> {
  return execute<User>(["create-user"], JSON.stringify(data));
}

/**
 * Update an existing user.
 */
export async function updateUser(userId: string, data: UserInput): Promise<User> {
  return execute<User>(["update-user", userId], JSON.stringify(data));
}

/**
 * Delete a user.
 */
export async function deleteUser(userId: string): Promise<{ success: boolean }> {
  return execute<{ success: boolean }>(["delete-user", userId]);
}

/**
 * List all unique groups.
 */
export async function listGroups(): Promise<string[]> {
  return execute<string[]>(["list-groups"]);
}
