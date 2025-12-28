import {
  Button,
  Flex,
  FlexItem,
  FormGroup,
  FormHelperText,
  HelperText,
  HelperTextItem,
  Label,
  Menu,
  MenuContent,
  MenuItem,
  MenuList,
  TextInput,
} from "@patternfly/react-core";
import { CheckIcon, PlusCircleIcon } from "@patternfly/react-icons";
import { useEffect, useRef, useState } from "react";

const STANDARD_GROUPS = ["admins", "users", "guests"];

export interface GroupInputProps {
  value: string[];
  onChange: (groups: string[]) => void;
  availableGroups?: string[];
  isLoading?: boolean;
  isDisabled?: boolean;
  error?: string;
}

export function GroupInput({
  value,
  onChange,
  availableGroups = [],
  isLoading = false,
  isDisabled = false,
  error,
}: GroupInputProps) {
  const [inputValue, setInputValue] = useState("");
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Custom groups from API (excluding standard groups)
  const customGroupsFromApi = availableGroups.filter((g) => !STANDARD_GROUPS.includes(g));

  // Filter suggestions for autocomplete: custom groups + any input match
  const suggestions = customGroupsFromApi.filter(
    (group) => !value.includes(group) && group.toLowerCase().includes(inputValue.toLowerCase())
  );

  // Show menu when typing and there are suggestions
  useEffect(() => {
    if (inputValue.length > 0 && suggestions.length > 0) {
      setIsMenuOpen(true);
    } else {
      setIsMenuOpen(false);
    }
  }, [inputValue, suggestions.length]);

  const addGroup = (group: string) => {
    const trimmedGroup = group.trim().toLowerCase();
    if (trimmedGroup && !value.includes(trimmedGroup)) {
      onChange([...value, trimmedGroup]);
    }
    setInputValue("");
    setIsMenuOpen(false);
    inputRef.current?.focus();
  };

  const removeGroup = (group: string) => {
    onChange(value.filter((g) => g !== group));
  };

  const toggleStandardGroup = (group: string) => {
    if (isDisabled) return;
    if (value.includes(group)) {
      removeGroup(group);
    } else {
      addGroup(group);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && inputValue.trim()) {
      event.preventDefault();
      addGroup(inputValue);
    } else if (event.key === "Escape") {
      setIsMenuOpen(false);
    }
  };

  const handleInputChange = (_event: React.FormEvent, newValue: string) => {
    setInputValue(newValue);
  };

  const handleMenuSelect = (
    _event: React.MouseEvent | undefined,
    itemId: string | number | undefined
  ) => {
    if (typeof itemId === "string") {
      addGroup(itemId);
    }
  };

  // Custom groups that are selected (not standard groups)
  const selectedCustomGroups = value.filter((g) => !STANDARD_GROUPS.includes(g));

  return (
    <FormGroup label="Groups" fieldId="groups">
      <Flex direction={{ default: "column" }} gap={{ default: "gapSm" }}>
        {/* Standard groups as toggleable chips + custom groups as removable labels */}
        <FlexItem>
          <Flex
            gap={{ default: "gapSm" }}
            alignItems={{ default: "alignItemsCenter" }}
            flexWrap={{ default: "wrap" }}
          >
            {/* Standard groups - always visible, clickable to toggle */}
            {STANDARD_GROUPS.map((group) => {
              const isSelected = value.includes(group);
              return (
                <FlexItem key={group}>
                  <Label
                    color={isSelected ? "blue" : "grey"}
                    icon={isSelected ? <CheckIcon /> : <PlusCircleIcon />}
                    onClick={() => toggleStandardGroup(group)}
                    style={{
                      cursor: isDisabled ? "not-allowed" : "pointer",
                      opacity: isDisabled ? 0.6 : 1,
                    }}
                  >
                    {group}
                  </Label>
                </FlexItem>
              );
            })}

            {/* Custom groups - removable labels */}
            {selectedCustomGroups.map((group) => (
              <FlexItem key={group}>
                <Label color="blue" onClose={isDisabled ? undefined : () => removeGroup(group)}>
                  {group}
                </Label>
              </FlexItem>
            ))}
          </Flex>
        </FlexItem>

        {/* Custom group input with autocomplete */}
        <FlexItem>
          <div style={{ position: "relative" }}>
            <Flex gap={{ default: "gapSm" }}>
              <FlexItem grow={{ default: "grow" }}>
                <TextInput
                  ref={inputRef}
                  id="groups-input"
                  type="text"
                  value={inputValue}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyDown}
                  onFocus={() => {
                    if (inputValue.length > 0 && suggestions.length > 0) {
                      setIsMenuOpen(true);
                    }
                  }}
                  placeholder={isLoading ? "Loading..." : "Add custom group..."}
                  isDisabled={isDisabled || isLoading}
                  aria-label="Add custom group"
                />
              </FlexItem>
              <FlexItem>
                <Button
                  variant="secondary"
                  onClick={() => addGroup(inputValue)}
                  isDisabled={!inputValue.trim() || isDisabled || isLoading}
                >
                  Add
                </Button>
              </FlexItem>
            </Flex>

            {/* Suggestions dropdown */}
            {isMenuOpen && suggestions.length > 0 && (
              <div
                style={{
                  position: "absolute",
                  top: "100%",
                  left: 0,
                  right: 0,
                  zIndex: 1000,
                  marginTop: "4px",
                }}
              >
                <Menu onSelect={handleMenuSelect} isScrollable>
                  <MenuContent>
                    <MenuList>
                      {suggestions.map((group) => (
                        <MenuItem key={group} itemId={group}>
                          {group}
                        </MenuItem>
                      ))}
                    </MenuList>
                  </MenuContent>
                </Menu>
              </div>
            )}
          </div>
        </FlexItem>
      </Flex>

      {error && (
        <FormHelperText>
          <HelperText>
            <HelperTextItem variant="error">{error}</HelperTextItem>
          </HelperText>
        </FormHelperText>
      )}
    </FormGroup>
  );
}
