#!/usr/bin/env bash
# Safely unmount the Orion home directory from the local repo.

MOUNT_POINT="$HOME/Parallel_Processing_Systems/orion_home"

if mount | grep -q "$MOUNT_POINT"; then
  echo "Unmounting Orion from $MOUNT_POINT ..."
  fusermount -u "$MOUNT_POINT" && echo "Unmount successful."
else
  echo "Orion is not currently mounted at $MOUNT_POINT."
fi
