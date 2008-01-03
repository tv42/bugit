=========================
 Internal data structure
=========================

- ``.git/bugit/HEAD`` is symref points to ``refs/heads/bugit/master``

- ``.git/refs/heads/bugit/master`` stores "current state" of bugs

- caches etc may be stored in ``.git/bugit``

- inside the git filesystem:

  - subdirectories are tickets, named after their initial sha1

  - inside each subdirectory are files, one per variable, filename is
    variable name and content is value

  - variable names starting with ``.`` or ``_`` are forbidden

  - variable names containing ``/`` just map to subdirectories
