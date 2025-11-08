# Scripts Overview

This folder contains four utility shell scripts designed to simplify file synchronization and remote access between the local WSL environment, Orion, and Scirouter servers used for the *Parallel Computing Systems* course at NTUA.

Each script is self-contained and portable. They rely on your configured SSH keys and do not require any passwords during normal operation.

---

## 1. mount_orion.sh

**Purpose:**
Mount your Orion home directory into your local GitHub repository using SSHFS, so you can directly browse, edit, and copy files under `~/Parallel_Processing_Systems/orion_home`.

**Usage:**

```bash
./mount_orion.sh
```

**Description:**
This script mounts `/home/parallel/parlab05` from `orion.cslab.ece.ntua.gr` into:

```
~/Parallel_Processing_Systems/orion_home
```

It uses your key at `C:/Users/peppa/.ssh/ntua_parlab_rsa` through the WSL path `/mnt/c/...`.
Once mounted, you can work with remote files as if they were local.

**Unmount:**

```bash
fusermount -u ~/Parallel_Processing_Systems/orion_home
```

---

## 2. unmount_orion.sh

**Purpose:**
Safely unmount the Orion remote filesystem from your local repository.

**Usage:**

```bash
./unmount_orion.sh
```

**Description:**
The script checks if the Orion mount is active and unmounts it cleanly using `fusermount -u`.
If the mount is not found, it exits without error.
The new version also deletes the folder mounted.

---

## 3. push_to_scirouter.sh

**Location:** `/home/parlab05/push_to_scirouter.sh` (on Orion)

**Purpose:**
Copy a directory from Orion to your home on Scirouter.

**Usage:**

```bash
~/push_to_scirouter.sh <source_dir> [destination_name]
```

**Example:**

```bash
~/push_to_scirouter.sh ~/a2
~/push_to_scirouter.sh ~/a2 a2_backup
```

**Description:**
Copies the specified folder from Orion to the same-named (or custom-named) folder in your Scirouter home directory using:

```bash
scp -rp
```

This preserves file permissions and timestamps.
The script depends on the SSH alias `scirouter` configured in `~/.ssh/config`.

---

## 4. push_to_orion.sh

**Location:** `/home/parlab05/push_to_orion.sh` (on Scirouter)

**Purpose:**
Copy a directory from Scirouter to your home on Orion.

**Usage:**

```bash
~/push_to_orion.sh <source_dir> [destination_name]
```

**Example:**

```bash
~/push_to_orion.sh ~/a2
~/push_to_orion.sh ~/a2 a2_results
```

**Description:**
Copies the specified folder from Scirouter to the same-named (or custom-named) folder in your Orion home using `scp -rp`.
Relies on the SSH alias `orion` in your configuration.

---

## Notes

- All scripts assume working SSH key authentication between your local system, Orion, and Scirouter.
- The mount point `orion_home/` should be listed in your `.gitignore` to prevent accidental Git commits.
- You can modify the paths and usernames inside the scripts to fit your environment if needed.
- The scripts are designed to be idempotent, meaning re-running them will not create duplicates.

---

## Example Workflow

1. Mount Orion home locally for development:

   ```bash
   ./mount_orion.sh
   ```

2. Work locally and sync code to Orion via the mounted folder or Git.

3. From Orion, push your directory to Scirouter:

   ```bash
   ~/push_to_scirouter.sh ~/a2
   ```

4. Execute your jobs on Scirouter and retrieve results:

   ```bash
   ~/push_to_orion.sh ~/a2
   ```

5. Unmount Orion when finished:

   ```bash
   ./unmount_orion.sh
   ```

---

**Author:** Michail-Athanasios Peppas
**Institution:** National Technical University of Athens (NTUA), School of Electrical & Computer Engineering
**Course:** Parallel Computing Systems
**Year:** 2025
