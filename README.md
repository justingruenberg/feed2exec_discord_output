# feed2exec_discord_output

Just a [feed2exec](https://feed2exec.readthedocs.io/en/stable/) plugin hacked together to send Reddit RSS to a discord, using the webhooks.

## Install Steps

- Create and activate venv

  ```bash
  python3 -m venv <venv name>
  source <venv name>/bin/activate
  ```

- Install packages
  
  ```bash
  pip install -r requirements.txt
  ```

- Install plugin
  Copy the plugin to somewhere on the venv python path. The python path can be found with:

  ```bash
  python3 -c "import sys; print(sys.path)"
  ```

- Add and configure feed

  ```bash
  feed2exec add <feed name> <feed url>
  ```

  Modify the feed2exec config at ```~/.config/feed2exec.ini``` and add keys under the ```<feed name>``` header:
  
  - ```output=discord_output```
  - ```webhook=<webhook url from discord>``` 
  - ```user=<display username>``` (optional, omiting this will use whatever is configured in the webhook).

- Setup Crontab
  Create a crontab to execute the following command periodically:

  ```bash
  /path/to/venv/bin/python3 -m feed2exec fetch
  ```
