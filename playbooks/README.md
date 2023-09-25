[Ansible](https://docs.ansible.com/ansible/latest/index.html) playbooks located in this directory
are used by Blender Studio staff to manage installation and continuous deployment of this project.

While the playbooks can be used as reference for **another** production or staging installation
(e.g. you can find all the required packages in `install.yaml`, templates of web server configuration
under `templates/` and variables such as domain names or paths where back-end code is located in `vars_common.yaml`),
they will not provide you with a working installation if you run them "as is".

It should be possible, however, to adjust the playbooks by copying a directory under `environments/`
and adjusting variables in that directory.
Refer to [Ansible documentation](https://docs.ansible.com/ansible/latest/network/getting_started/first_inventory.html#build-your-inventory)
for details about inventory variables.

# Deployment playbooks

The target system is assumed to be Ubuntu 22.04 LTS.
The playbooks have not been tested with other distros or releases,
and will most likely fail due to differences in configuration paths and so on.

To avoid adding more dependencies to the project itself, `ansible` uses its own `virtualenv`.
To set it up use the following commands:

    virtualenv .venv -p python
    source .venv/bin/activate
    pip install -r requirements.txt

## First time install

First time installation requires a few additional variables (see the list in `vars_common.yaml`)
that should be encrypted with Ansible Vault and stored in `environments/<env>/group_vars/all/99_vault.yaml`
before `install.yaml` can be run.
See the section below for more details about encrypting with Ansible Vault.

One of these variables is `meili_master_key`, which can be generated using the following command:

    head /dev/urandom | tr -dc A-Za-z0-9 | head -c32

After encrypting `meili_master_key` and saving in the above mentioned `99_vault.yaml`,
run the installation playbooks:

    ./ansible.sh -i environments/production install.yaml --vault-id production@prompt
    ./ansible.sh -i environments/production setup_certificate.yaml

These vaulted variables are written to the configuration files at the target host,
so they shouldn't be required after the installation is complete,
unless you need to rewrite those files for some reason.

The installation playbook creates a `.env` configuration file, but it doesn't set values
for all of the variables listed in it (such as AWS or Coconut credentials, and `DATABASE_URL`).
This means that you need to fill those in manually, by connecting to the production machine,
editing it and then restarting the affected services:

    sudo -Hu studio-production vim /opt/blender-studio-production/.env
    sudo systemctl restart blender-studio-production
    sudo systemctl restart blender-studio-production-background

### Encrypting variables

Let's say one of the config templates used by `install.yaml` refers to a variable named `sentry_dsn`,
and for **production** we want this variable to have the following value: `https://foo@bar.example.com/1234`.
To encrypt this value, use the following command:

    echo -n 'https://foo@bar.example.com/1234' | ansible-vault encrypt_string --vault-id production@prompt --stdin-name 'sentry_dsn'

Store the output of the above command in `environments/production/group_vars/all/99_vault.yaml`
(not tracked by this repository):

```
# environments/production/group_vars/all/99_vault.yaml
...
sentry_dsn: !vault |
      $ANSIBLE_VAULT;1.2;AES256;production
      foo5643bbar56563663265653430636530deadbeef65353534643361616238346264343763356362
      ..
      6439356237386bar303062393861626639613531326363380a653266646534383831666364663964
...
```

Any playbook that uses this variable will need to be able to decrypt it,
so use `--vault-id production@prompt`: this will make Ansible prompt for a Vault password.

If a playbook you are running and its templates don't use any encrypted variables,
`--vault-id` parameter doesn't need to be added to the command.

## Deploy

Except for error page templates, which are part of the playbooks,
the playbooks do not deploy local uncommitted changes.
When you need to deploy something, make sure to commit and push your changes both to
`main` and `production`:

1. commit and push your changes to `main`;
2. push the same exact changes to `production` using the following:

```
git checkout production
git pull
git merge --ff-only main
git push
```

3. navigate to the playbooks and run `deploy.yaml`

```
./ansible.sh -i environments/production deploy.yaml
```
