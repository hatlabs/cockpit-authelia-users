import {
  ActionGroup,
  Button,
  Form,
  FormGroup,
  FormHelperText,
  HelperText,
  HelperTextItem,
  PageSection,
  Spinner,
  Switch,
  TextInput,
  Title,
} from "@patternfly/react-core";
import { useCallback, useEffect, useState } from "react";

import { createUser, getUser, listGroups, updateUser } from "../lib/api";
import type { UserInput } from "../lib/types";
import type { FormErrors, FormState } from "../lib/validation";
import { hasErrors, validateUserForm } from "../lib/validation";
import { ErrorAlert } from "../components/ErrorAlert";
import { GroupInput } from "../components/GroupInput";

export interface UserFormViewProps {
  mode: "create" | "edit";
  userId?: string;
  onSave: () => void;
  onCancel: () => void;
}

const initialFormState: FormState = {
  user_id: "",
  displayname: "",
  email: "",
  password: "",
  confirmPassword: "",
  disabled: false,
  groups: [],
};

export function UserFormView({ mode, userId, onSave, onCancel }: UserFormViewProps) {
  const [form, setForm] = useState<FormState>(initialFormState);
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(mode === "edit");
  const [saving, setSaving] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [availableGroups, setAvailableGroups] = useState<string[]>([]);
  const [groupsLoading, setGroupsLoading] = useState(true);

  // Load user data in edit mode
  const fetchUser = useCallback(async () => {
    if (mode !== "edit" || !userId) return;

    setLoading(true);
    setLoadError(null);
    try {
      const user = await getUser(userId);
      setForm({
        user_id: user.user_id,
        displayname: user.displayname,
        email: user.email,
        password: "",
        confirmPassword: "",
        disabled: user.disabled,
        groups: user.groups,
      });
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : "Failed to load user");
    } finally {
      setLoading(false);
    }
  }, [mode, userId]);

  // Load available groups
  const fetchGroups = useCallback(async () => {
    setGroupsLoading(true);
    try {
      const groups = await listGroups();
      setAvailableGroups(groups);
    } catch {
      // Silently fail - default groups will still be available
    } finally {
      setGroupsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUser();
    fetchGroups();
  }, [fetchUser, fetchGroups]);

  const handleFieldChange = (field: keyof FormState, value: string | boolean | string[]) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    // Clear field error when user types
    if (errors[field as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    // Validate form
    const validationErrors = validateUserForm(form, mode);
    if (hasErrors(validationErrors)) {
      setErrors(validationErrors);
      return;
    }

    setSaving(true);
    setErrors({});

    try {
      if (mode === "create") {
        await createUser({
          user_id: form.user_id,
          displayname: form.displayname,
          email: form.email,
          password: form.password,
          disabled: form.disabled,
          groups: form.groups,
        });
      } else {
        if (!userId) {
          throw new Error("userId is required for edit mode");
        }
        // Only include password if provided
        const updateData: UserInput = {
          displayname: form.displayname,
          email: form.email,
          disabled: form.disabled,
          groups: form.groups,
        };
        if (form.password) {
          updateData.password = form.password;
        }
        await updateUser(userId, updateData);
      }
      onSave();
    } catch (err) {
      setErrors({
        submit: err instanceof Error ? err.message : "Failed to save user",
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <PageSection>
        <Title headingLevel="h1" style={{ marginBottom: "1rem" }}>
          {mode === "create" ? "Create User" : "Edit User"}
        </Title>
        <div style={{ display: "flex", justifyContent: "center", padding: "2rem" }}>
          <Spinner size="lg" />
        </div>
      </PageSection>
    );
  }

  if (loadError) {
    return (
      <PageSection>
        <Title headingLevel="h1" style={{ marginBottom: "1rem" }}>
          Edit User
        </Title>
        <ErrorAlert error={loadError} onRetry={fetchUser} />
        <div style={{ marginTop: "1rem" }}>
          <Button variant="link" onClick={onCancel}>
            Back to list
          </Button>
        </div>
      </PageSection>
    );
  }

  return (
    <PageSection>
      <Title headingLevel="h1" style={{ marginBottom: "1rem" }}>
        {mode === "create" ? "Create User" : `Edit User: ${userId}`}
      </Title>

      {errors.submit && (
        <div style={{ marginBottom: "1rem" }}>
          <ErrorAlert
            error={errors.submit}
            onDismiss={() => setErrors((prev) => ({ ...prev, submit: undefined }))}
          />
        </div>
      )}

      <Form onSubmit={handleSubmit} style={{ maxWidth: "600px" }}>
        {/* Username */}
        <FormGroup label="Username" isRequired={mode === "create"} fieldId="user_id">
          <TextInput
            id="user_id"
            type="text"
            value={form.user_id}
            onChange={(_event, value) => handleFieldChange("user_id", value)}
            isDisabled={mode === "edit"}
            validated={errors.user_id ? "error" : "default"}
            aria-label="Username"
          />
          {errors.user_id && (
            <FormHelperText>
              <HelperText>
                <HelperTextItem variant="error">{errors.user_id}</HelperTextItem>
              </HelperText>
            </FormHelperText>
          )}
          {mode === "create" && !errors.user_id && (
            <FormHelperText>
              <HelperText>
                <HelperTextItem>
                  1-64 characters, letters, numbers, underscore, or hyphen
                </HelperTextItem>
              </HelperText>
            </FormHelperText>
          )}
        </FormGroup>

        {/* Display Name */}
        <FormGroup label="Display Name" isRequired fieldId="displayname">
          <TextInput
            id="displayname"
            type="text"
            value={form.displayname}
            onChange={(_event, value) => handleFieldChange("displayname", value)}
            validated={errors.displayname ? "error" : "default"}
            aria-label="Display name"
          />
          {errors.displayname && (
            <FormHelperText>
              <HelperText>
                <HelperTextItem variant="error">{errors.displayname}</HelperTextItem>
              </HelperText>
            </FormHelperText>
          )}
        </FormGroup>

        {/* Email */}
        <FormGroup label="Email" isRequired fieldId="email">
          <TextInput
            id="email"
            type="email"
            value={form.email}
            onChange={(_event, value) => handleFieldChange("email", value)}
            validated={errors.email ? "error" : "default"}
            aria-label="Email"
          />
          {errors.email && (
            <FormHelperText>
              <HelperText>
                <HelperTextItem variant="error">{errors.email}</HelperTextItem>
              </HelperText>
            </FormHelperText>
          )}
        </FormGroup>

        {/* Password */}
        <FormGroup label="Password" isRequired={mode === "create"} fieldId="password">
          <TextInput
            id="password"
            type="password"
            value={form.password}
            onChange={(_event, value) => handleFieldChange("password", value)}
            validated={errors.password ? "error" : "default"}
            aria-label="Password"
          />
          {errors.password && (
            <FormHelperText>
              <HelperText>
                <HelperTextItem variant="error">{errors.password}</HelperTextItem>
              </HelperText>
            </FormHelperText>
          )}
          {mode === "edit" && !errors.password && (
            <FormHelperText>
              <HelperText>
                <HelperTextItem>Leave blank to keep current password</HelperTextItem>
              </HelperText>
            </FormHelperText>
          )}
        </FormGroup>

        {/* Confirm Password - only show if password is being set */}
        {form.password && (
          <FormGroup label="Confirm Password" isRequired fieldId="confirmPassword">
            <TextInput
              id="confirmPassword"
              type="password"
              value={form.confirmPassword}
              onChange={(_event, value) => handleFieldChange("confirmPassword", value)}
              validated={errors.confirmPassword ? "error" : "default"}
              aria-label="Confirm password"
            />
            {errors.confirmPassword && (
              <FormHelperText>
                <HelperText>
                  <HelperTextItem variant="error">{errors.confirmPassword}</HelperTextItem>
                </HelperText>
              </FormHelperText>
            )}
          </FormGroup>
        )}

        {/* Groups */}
        <GroupInput
          value={form.groups}
          onChange={(groups) => handleFieldChange("groups", groups)}
          availableGroups={availableGroups}
          isLoading={groupsLoading}
        />

        {/* Account Active Toggle */}
        <FormGroup label="Account Status" fieldId="account-active">
          <Switch
            id="account-active"
            label={form.disabled ? "Account disabled" : "Account active"}
            isChecked={!form.disabled}
            onChange={(_event, checked) => handleFieldChange("disabled", !checked)}
          />
        </FormGroup>

        {/* Actions */}
        <ActionGroup>
          <Button variant="primary" type="submit" isLoading={saving} isDisabled={saving}>
            {mode === "create" ? "Create User" : "Save Changes"}
          </Button>
          <Button variant="link" onClick={onCancel} isDisabled={saving}>
            Cancel
          </Button>
        </ActionGroup>
      </Form>
    </PageSection>
  );
}
