# Hearth Sync Protocol

To keep your privacy absolute, we use **Syncthing** (P2P) instead of cloud servers.

### Directions
1. Install Syncthing on this device and your backup device (PC/Mac).
2. Point Syncthing to watch these two folders:
   * `./hearth_writer/data` (Your writing, user profile, and memory)
   * `./hearth_writer/models` (Your AI weights)
3. Set the sync interval to "Watcher" (Real-time).

**Note:** Never sync the `cache` folder. It is meant to be transient.