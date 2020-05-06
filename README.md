![Python Versions](https://img.shields.io/static/v1?label=python&message=3.6%20|%203.7%20|%203.8&color=orange)
![Python Packages](https://img.shields.io/static/v1?label=packages&message=pygame&color=D532D6)

# r/place viewer

A video-like viewer for Reddit's 2017 april fools, r/place.

#### A quick explanation of r/place:
> There is an empty canvas.\
> You may place a tile upon it, but you must wait to place another.\
> Individually you can create something.\
> Together you can create something more.

The experiment started the 31/03/2017 at 17:00 UTC and ran for 72 hours total.

The final result looks like this:

![r/place final image](/screenshots/final.png)


## Full data

*full_data.txt* is an edited version of r/place's data, where unused fields have been removed to save space.

You can download the raw data from reddit's official release [here](https://www.reddit.com/r/redditdata/comments/6640ru/place_datasets_april_fools_2017/).

## Run it

Download/clone the project and run it with python.
```console
$ python place_viewer.py
```

Requirements: **Python 3.6 or higher**\
Packages:
- pygame

(*check requirements.txt for details*)

```console
$ pip install -r requirements.txt
```

#### On first run:

First time you run the program, it will pre-generate an image cache from the full data. This process can take a couple of minutes.

If you ever wish to regenerate the cache, use the *gen* arg. (This will fully delete the old cache)
```console
$ python place_viewer.py gen
```

## Controls

- **Space** to pause/play
- **Left/Right arrows** to jump through time (add **shift** for a shorter jump)
- **Up/Down arrows** to change real-time speed
- Drag your mouse to zoom in, **right-click** to zoom out

## Screenshots

![Screenshot 1](/screenshots/place_viewer-1.png?raw=true)
![Screenshot 2](/screenshots/place_viewer-2.png?raw=true)
![Screenshot 3](/screenshots/place_viewer-3.png?raw=true)
![Screenshot 4](/screenshots/place_viewer-4.png?raw=true)

