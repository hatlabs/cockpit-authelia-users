import {
  Dropdown,
  DropdownItem,
  DropdownList,
  EmptyState,
  EmptyStateBody,
  EmptyStateFooter,
  Label,
  MenuToggle,
  MenuToggleElement,
  PageSection,
  Title,
  Toolbar,
  ToolbarContent,
  ToolbarItem,
} from "@patternfly/react-core";
import { EllipsisVIcon, PlusCircleIcon, UserIcon } from "@patternfly/react-icons";
import { Table, Tbody, Td, Th, Thead, Tr } from "@patternfly/react-table";
import { useCallback, useEffect, useState } from "react";

import { deleteUser, listUsers, updateUser } from "../lib/api";
import type { User } from "../lib/types";
import { AdminGatedButton, ADMIN_REQUIRED_TOOLTIP } from "../components/AdminGatedButton";
import { ConfirmDialog } from "../components/ConfirmDialog";
import { ErrorAlert } from "../components/ErrorAlert";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { useAdminPermission } from "../hooks/useAdminPermission";

export interface UserListViewProps {
  onCreateUser: () => void;
  onEditUser: (userId: string) => void;
}

export function UserListView({ onCreateUser, onEditUser }: UserListViewProps) {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionInProgress, setActionInProgress] = useState<string | null>(null);
  const [openActionMenu, setOpenActionMenu] = useState<string | null>(null);
  const { allowed: isAdminAllowed } = useAdminPermission();
  const isAdminRequired = isAdminAllowed !== true;

  // Delete confirmation dialog state
  const [deleteDialog, setDeleteDialog] = useState<{
    isOpen: boolean;
    user: User | null;
  }>({ isOpen: false, user: null });

  // Toggle disabled confirmation dialog state
  const [toggleDialog, setToggleDialog] = useState<{
    isOpen: boolean;
    user: User | null;
  }>({ isOpen: false, user: null });

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listUsers();
      setUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load users");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleDelete = async () => {
    const user = deleteDialog.user;
    if (!user) return;

    setActionInProgress(user.user_id);
    setDeleteDialog({ isOpen: false, user: null });

    try {
      await deleteUser(user.user_id);
      setUsers((prev) => prev.filter((u) => u.user_id !== user.user_id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete user");
    } finally {
      setActionInProgress(null);
    }
  };

  const handleToggleDisabled = async () => {
    const user = toggleDialog.user;
    if (!user) return;

    setActionInProgress(user.user_id);
    setToggleDialog({ isOpen: false, user: null });

    try {
      const updated = await updateUser(user.user_id, { disabled: !user.disabled });
      setUsers((prev) => prev.map((u) => (u.user_id === user.user_id ? updated : u)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update user status");
    } finally {
      setActionInProgress(null);
    }
  };

  if (loading) {
    return (
      <PageSection>
        <Title headingLevel="h1" style={{ marginBottom: "1rem" }}>
          Authelia Users
        </Title>
        <LoadingSkeleton rows={5} />
      </PageSection>
    );
  }

  if (error && users.length === 0) {
    return (
      <PageSection>
        <Title headingLevel="h1" style={{ marginBottom: "1rem" }}>
          Authelia Users
        </Title>
        <ErrorAlert error={error} onRetry={fetchUsers} />
      </PageSection>
    );
  }

  if (users.length === 0) {
    return (
      <PageSection>
        <Title headingLevel="h1" style={{ marginBottom: "1rem" }}>
          Authelia Users
        </Title>
        <EmptyState titleText="No users found" headingLevel="h2" icon={UserIcon}>
          <EmptyStateBody>
            Create your first user to get started with Authelia authentication.
          </EmptyStateBody>
          <EmptyStateFooter>
            <AdminGatedButton
              variant="primary"
              onClick={onCreateUser}
              isAdminRequired={isAdminRequired}
              icon={<PlusCircleIcon />}
            >
              Create User
            </AdminGatedButton>
          </EmptyStateFooter>
        </EmptyState>
      </PageSection>
    );
  }

  return (
    <PageSection>
      <Title headingLevel="h1" style={{ marginBottom: "1rem" }}>
        Authelia Users
      </Title>

      {error && (
        <div style={{ marginBottom: "1rem" }}>
          <ErrorAlert error={error} onDismiss={() => setError(null)} />
        </div>
      )}

      <Toolbar>
        <ToolbarContent>
          <ToolbarItem>
            <AdminGatedButton
              variant="primary"
              onClick={onCreateUser}
              isAdminRequired={isAdminRequired}
              icon={<PlusCircleIcon />}
            >
              Create User
            </AdminGatedButton>
          </ToolbarItem>
        </ToolbarContent>
      </Toolbar>

      <Table aria-label="Users table">
        <Thead>
          <Tr>
            <Th>Username</Th>
            <Th>Display Name</Th>
            <Th>Email</Th>
            <Th>Groups</Th>
            <Th>Status</Th>
            <Th screenReaderText="Actions" />
          </Tr>
        </Thead>
        <Tbody>
          {users.map((user) => (
            <Tr key={user.user_id} style={user.disabled ? { opacity: 0.6 } : undefined}>
              <Td dataLabel="Username">{user.user_id}</Td>
              <Td dataLabel="Display Name">{user.displayname}</Td>
              <Td dataLabel="Email">{user.email}</Td>
              <Td dataLabel="Groups">{user.groups.length > 0 ? user.groups.join(", ") : "—"}</Td>
              <Td dataLabel="Status">
                {user.disabled ? (
                  <Label color="orange">Disabled</Label>
                ) : (
                  <Label color="green">Active</Label>
                )}
              </Td>
              <Td dataLabel="Actions" isActionCell>
                <Dropdown
                  isOpen={openActionMenu === user.user_id}
                  onOpenChange={(isOpen) => setOpenActionMenu(isOpen ? user.user_id : null)}
                  toggle={(toggleRef: React.Ref<MenuToggleElement>) => (
                    <MenuToggle
                      ref={toggleRef}
                      variant="plain"
                      onClick={() =>
                        setOpenActionMenu(openActionMenu === user.user_id ? null : user.user_id)
                      }
                      isExpanded={openActionMenu === user.user_id}
                      isDisabled={actionInProgress === user.user_id}
                      aria-label={`Actions for ${user.user_id}`}
                    >
                      <EllipsisVIcon />
                    </MenuToggle>
                  )}
                  popperProps={{ position: "right" }}
                >
                  <DropdownList>
                    <DropdownItem
                      key="edit"
                      isAriaDisabled={isAdminRequired}
                      tooltipProps={
                        isAdminRequired ? { content: ADMIN_REQUIRED_TOOLTIP } : undefined
                      }
                      onClick={() => {
                        setOpenActionMenu(null);
                        onEditUser(user.user_id);
                      }}
                    >
                      Edit
                    </DropdownItem>
                    <DropdownItem
                      key="toggle"
                      isAriaDisabled={isAdminRequired}
                      tooltipProps={
                        isAdminRequired ? { content: ADMIN_REQUIRED_TOOLTIP } : undefined
                      }
                      onClick={() => {
                        setOpenActionMenu(null);
                        setToggleDialog({ isOpen: true, user });
                      }}
                    >
                      {user.disabled ? "Enable" : "Disable"}
                    </DropdownItem>
                    <DropdownItem
                      key="delete"
                      isAriaDisabled={isAdminRequired}
                      tooltipProps={
                        isAdminRequired ? { content: ADMIN_REQUIRED_TOOLTIP } : undefined
                      }
                      onClick={() => {
                        setOpenActionMenu(null);
                        setDeleteDialog({ isOpen: true, user });
                      }}
                      isDanger
                    >
                      Delete
                    </DropdownItem>
                  </DropdownList>
                </Dropdown>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>

      {/* Delete confirmation dialog */}
      <ConfirmDialog
        isOpen={deleteDialog.isOpen}
        title="Delete User"
        message={
          <>
            Are you sure you want to delete user <strong>{deleteDialog.user?.user_id}</strong>? This
            action cannot be undone.
          </>
        }
        confirmLabel="Delete"
        variant="danger"
        isLoading={actionInProgress === deleteDialog.user?.user_id}
        onConfirm={handleDelete}
        onCancel={() => setDeleteDialog({ isOpen: false, user: null })}
      />

      {/* Toggle disabled confirmation dialog */}
      <ConfirmDialog
        isOpen={toggleDialog.isOpen}
        title={toggleDialog.user?.disabled ? "Enable User" : "Disable User"}
        message={
          toggleDialog.user?.disabled ? (
            <>
              Enable user <strong>{toggleDialog.user?.user_id}</strong>? They will be able to log in
              again.
            </>
          ) : (
            <>
              Disable user <strong>{toggleDialog.user?.user_id}</strong>? They will not be able to
              log in until re-enabled.
            </>
          )
        }
        confirmLabel={toggleDialog.user?.disabled ? "Enable" : "Disable"}
        variant={toggleDialog.user?.disabled ? "default" : "warning"}
        isLoading={actionInProgress === toggleDialog.user?.user_id}
        onConfirm={handleToggleDisabled}
        onCancel={() => setToggleDialog({ isOpen: false, user: null })}
      />
    </PageSection>
  );
}
