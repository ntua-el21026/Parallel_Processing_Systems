#!/usr/bin/env bash
# Mount orion home directory into the local repo under orion_home/

MOUNT_POINT="$HOME/Parallel_Processing_Systems/orion_home"
REMOTE="parlab05@orion.cslab.ece.ntua.gr:/home/parallel/parlab05"
KEY_PATH="/mnt/c/Users/peppa/.ssh/ntua_parlab_rsa"

mkdir -p "$MOUNT_POINT"

if mount | grep -q "$MOUNT_POINT"; then
  echo "Already mounted: $MOUNT_POINT"
else
  echo "Mounting Orion → $MOUNT_POINT ..."
  sshfs -o IdentityFile="$KEY_PATH" \
        -o IdentitiesOnly=yes \
        -o reconnect,ServerAliveInterval=15,ServerAliveCountMax=3 \
        "$REMOTE" "$MOUNT_POINT"
  echo "Mounted successfully."
fi
