# albion-online-fishingbot
A python bot for fishing in albion online

This bot is by far from being perfect or performant, but hey, it's free and open source!

I combined some sources and tutorials and came to this version.

Feel free to use it, edit it, share it, but do note that you take full responsibility for your own actions.

# How to use it

Open cmd and cd into the repo directory, then use pip install -r requirements.txt

You need to install [VB-AUDIO](https://vb-audio.com/Cable/) and set it as default device for playback and recording devices in order for the bot to be able to detect when it cought a fish.

Then I recommend to set the game resolution to 1600 x 900 windowed.

Get close to a waterpool and run main.py

# Notes

You'll mainly look into main.py do_minigame() inside fishing_bot.py to make adjustments to your liking/use-case. 

The images which have _2 are made in 1600x900, the others are in 1024x728. Opencv matches the fishing bob better with the in-game images if they're of the same resolution.

# And another word

Don't expect updates on this code, but you can expect sooner or later some other bots using opencv and maybe even machine learning for gathering.

But if you find improvements to the code, you can make a pull request