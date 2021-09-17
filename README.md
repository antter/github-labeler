# Github Labeler


Github Labeler is a project that will be a model for automatically labelling issues (and possibly PRs!) with the necessary tags.

A lot of work has been already done in this direction, however it only exists for the three most common tags i.e. **bug**, **feature** and **question**. Using models like fastText and multiple binary classification models instead of one multi-label model we aim to create a model that can tag issues with all labels that are used. The aim is for this model to be integrated in a bot that can automatically tag issues.
