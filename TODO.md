- [ ] Setup testing scripts
- [ ] Catch XML Parsing errors (plugin?)
- [ ] Select all in changelist
- [ ] Save diff to patch (file or database?)
- [ ] Save changelist diff to patch
- [ ] Add notes to individual files or changelist (put 'em in a database)
- [ ] Arrowbox direction and placement logic needs refinement
- [ ] Support "D" attribute on elements and test Deleted files
- [-] Add type annotations (in progress)
- [ ] Fix "Absolute template path names are deprecated" message spamming output
- [ ] Cleanup toast message formatting
- [ ] Handle merge conflicts...
  - `svn status -u --xml` will provide details on what files have been updated in the repo
  - `svn update --action <ACTION>` - Specifies an action for automatic conflict resolution
  - Using the above, could postpone every conflict, identify and load interactively?
  - For now, just fail if possible conflict exists
- [ ] Support for `svn relocate`
- [ ] Add application logging (spec. viewing `svn ...` commands in dev)
- [x] Get logs for individual path or ~~revision~~
- [x] Sorting on log page retain URL parameters...
- [x] Poppers z-index issues
- [x] Toast messages passed through page reloads (session)
- [x] Get diff for path from log
- [x] Change `Repo` to `dataclass`
- [x] Revert changes
- [x] Sorting on log page
- [x] Changelist sorting stability
- [x] Changelist show all diff button
- [x] Poppers overflow issue
- [x] Changelist hiding
- [x] Firefox drag and drop doesn't work - loads icon instead...
- [x] "Enter" on changelist input submit
- [x] Make it generally more compact
- [x] Create arrowbox like element for various dialogs / etc
- [x] Escape HTML in logs
- [x] Respect line breaks in logs
- [x] Debug add to changelist not returning successfully
- [x] Debug check in not returning successfully
- [x] ESC should close side panel, deselecting all
- [x] Add messaging banner
- [x] Make top nav bar fixed
- [x] Implement log caching
