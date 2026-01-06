# Steamy

Steamy is a program that allows you to replace all display images in your Steam library with booru images. Alongside downloading generic images for every game, Steamy also supports configuring specific games to download targetted images. The images can then be turned off and saved to a backup folder at the click of a button, or redownloaded if you didn't like the ones that were chosen.

There is no adult content included in the Steamy installation, but the implication is that you'd be downloading 18+ images from boorus, so this program is intended for adults only. We even named the button to initiate the process "Pornify", so there's no mystery there.

# Installation

asdfg write installation here when its finalized

By default, Steamy only supports Danbooru. Rule34 and E621 both require API keys to download images from their servers. We highly recommend providing an API key for at least one other booru as Danbooru only supports a maximum of two tags for search queries. If you want to use these boorus, you need to make an account on these sites and generate a key. Rule34 does not require an email to sign up, but E621 does. For those who prefer the imageset of Danbooru but want more tags, we may add Gelbooru support in the future!

To get your Rule34 API Key, go to https://rule34.xxx/index.php?page=account&s=options. Under "API Access Credentials", click "Generate New Key". The key comes in the format `&api_key=<api_key>&user_id=<user_id>`, so you will have to take out the API key and user ID (*not* your username!) from this and put it into Steamy. Make sure you don't copy `&api_key=` and `&user_id=` while doing this.

To get your E621 API Key, go to https://e621.net/users/settings, then click "View" under "API Key". You may have to generate a new key, but it should be smooth sailing from here.

# Customization

By default Steamy should detect every game you own and overwrite their images, but if you want a game to have art with specific tags, you can add it in yourself. There are no plans for there to be a GUI editor for this, but it is fairly simple to do with only a few steps.

Firstly, you can run **Dump Game Library** in the **Tools** tab, selecting which folder you want to save the resulting JSON file to. It will go through every one of your Steam games and tie the game ID to the game's name. This can take over an hour if you have a good amount of games, but shouldn't take up too much processing power so you can safely leave it on in the background. The process is deliberately rate limited so that Steam doesn't block your requests.

Once finished, you can then open up `resources/game_database.json` and add any games from your newly created `dumped_game_database.json` into there. You can use prior entries as an example for doing this, but this is a full list of potential parameters you can give an entry:
```
    "<id>": {
      "name": <name>
      "danbooru": <danbooru>
      "rule34": <rule34>
      "e621": <e621>
      "ignore": <true>
    },
```
Example:
```
    "1840": {
      "name": "Source Filmmaker",
      "danbooru": "source_filmmaker_(medium)",
      "rule34": "source_filmmaker",
      "e621": "source_filmmaker"
    },
```
Most of the tags should be fairly self explanatory, but `ignore` is for games that should be skipped- things like 18+ games that already have horny art, etc.

Additionally, there is a "Search" function that allows you to search Steam and print the results in a text box for you to copy. This is handy if you don't own a game but know you want to add it. The "CC" code is country code, and a full list can be found [here](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). The search function only shows a maximum of 10 games at the moment, this is due to a limitation of the Steam store API.

Feel free to submit pull requests with your added games, but only do this if you know what you're doing and have tested out the tags on your end. **Please do not contact us elsewhere or submit an issue if you would like games added**, submitting them via changes to `game_database.json` is the most surefire way to get them added to the main branch.

# License

Steamy is licensed under the GNU Affero General Public License version 3 or any later version. But as a whole in combination with PyQt6, Steamy is provided under the terms of the GNU AGPL version 3 only.
