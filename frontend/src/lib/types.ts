/**
 * User data as returned from the backend API.
 * Password hash is never included.
 */
export interface User {
  user_id: string;
  displayname: string;
  email: string;
  disabled: boolean;
  groups: string[];
}

/**
 * User data for update operations.
 * All fields are optional for partial updates.
 * Password is plaintext (hashed by backend).
 */
export interface UserInput {
  displayname?: string;
  email?: string;
  password?: string;
  disabled?: boolean;
  groups?: string[];
}

/**
 * User data for create operations.
 * Includes user_id which is required for new users.
 */
export interface CreateUserInput {
  user_id: string;
  displayname: string;
  email: string;
  password: string;
  disabled?: boolean;
  groups?: string[];
}

/**
 * Error response from the backend.
 */
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

/**
 * Reactive permission handle returned by `cockpit.permission()`.
 * `allowed` is `null` until Cockpit resolves the state; treat null as "not yet allowed".
 */
export interface CockpitPermission {
  allowed: boolean | null;
  addEventListener: (event: "changed", callback: () => void) => void;
  removeEventListener: (event: "changed", callback: () => void) => void;
  close: () => void;
}

/**
 * Global type extensions for Cockpit environment.
 */
declare global {
  interface Window {
    debugging?: string | string[];
  }

  /**
   * Cockpit API types for location and navigation.
   */
  const cockpit: {
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
    location: {
      path: string[];
      options: Record<string, string>;
      go: (path: string[], options?: Record<string, string>) => void;
    };
    addEventListener: (event: "locationchanged", callback: () => void) => void;
    removeEventListener: (event: "locationchanged", callback: () => void) => void;
    permission?: (options: { admin: boolean }) => CockpitPermission;
  };
}
