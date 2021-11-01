# Get Started

In this project we can create models to assign labels to issues in repositories. Check out the [content page](content.md) for a detailed overview of this project.

## Try it out yourself

There are interactive and reproducible notebooks for this entire [project](https://github.com/aicoe-aiops/github-labeler) available for anyone to start using on the public [JupyterHub](https://jupyterhub-opf-jupyterhub.apps.zero.massopen.cloud/hub/login) instance on the [Massachusetts Open Cloud](https://massopen.cloud/) (MOC) right now!

1. To get started, access [JupyterHub](https://jupyterhub-opf-jupyterhub.apps.zero.massopen.cloud/), select log in with `moc-sso` and sign in using your Google Account.
2. After signing in, on the spawner page, please select the `Data Science Base` in the JupyterHub Notebook Image section from the dropdown and select a `Medium` container size and hit `Start` to start your server.
3. Once your server has spawned, you should open a terminal and run the command `git clone https://github.com/aicoe-aiops/github-labeler.git`.
4. Then, run the commands `cd github-labeler` followed by `pipenv install` in order to install all the required packages.
5. Rename the `.env.example` file to just `.env` and fill in your desired environment variables.
5. Now you are ready to run whatever code you wish. Check out the [content](./content.md) page with project blog and notebooks to see what features you can play around with.


If you need more help navigating the Operate First environment, we have a few [short videos](https://www.youtube.com/playlist?list=PL8VBRDTElCWpneB4dBu4u1kHElZVWfAwW) to help you get started.
