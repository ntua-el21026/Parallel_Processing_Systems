#!/usr/bin/env bash
# Safely unmount and remove the Orion home directory mount point from the local repo.

MOUNT_POINT="$HOME/Parallel_Processing_Systems/orion_home"

# Check if currently mounted
if mount | grep -q "$MOUNT_POINT"; then
  echo "Unmounting Orion from $MOUNT_POINT ..."
  if fusermount -u "$MOUNT_POINT"; then
    echo "Unmount successful."
  else
    echo "Warning: Unmount failed."
    exit 1
  fi
else
  echo "Orion is not currently mounted at $MOUNT_POINT."
fi

# Remove the mount folder if it exists
if [ -d "$MOUNT_POINT" ]; then
  echo "Removing mount directory: $MOUNT_POINT ..."
  if rmdir "$MOUNT_POINT" 2>/dev/null; then
    echo "Directory removed successfully."
  else
    echo "Directory not empty or could not be removed. Use 'rm -rf $MOUNT_POINT' if needed."
  fi
else
  echo "Mount directory does not exist."
fi
