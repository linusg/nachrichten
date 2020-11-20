# nachrichten

Quickly get the URL of the latest [ZDF heute](https://www.zdf.de/nachrichten/heute-19-uhr) or [Tagesschau](https://www.tagesschau.de) (German news) video.

## Why?

I'm watching German news almost daily, and having to visit zdf.de or tagesschau.de, finding the right video, clicking it, being redirected to another page *every single time* is annoying - especially as the front page quite often shows yesterday's video...

(╯°□°)╯︵ ┻━┻

This usually takes more than two minutes, as I'll have to wait for the browser loading bunch of JavaScript and thumbnails and then still need to find the right entry on the page. This script? Less than a second.

## Installation

Python >= 3.8 is required.

- Clone the repository
- Install dependencies: `pip3 install -r requirements.txt`
- Place `nachrichten.py` in `~/.local/bin` or similar, if you want

## Usage

There's no configuration at all, the script will always attempt to grab the latest video of the current day in highest quality.

The video URL will be printed to standard output if found, an error message with exit code 1 otherwise.

For Tagesschau:

```console
$ python3 nachrichten.py tagesschau
https://download.media.tagesschau.de/video/2020/1119/TV-20201119-2021-2200.webxl.h264.mp4
```

For ZDF heute:

```console
$ python3 nachrichten.py heute
https://downloadzdf-a.akamaihd.net/mp4/zdf/20/11/201119_sendung_h19/3/201119_sendung_h19_3328k_p15v15.mp4
```

This means you can directly open the video in VLC for example:

```console
vlc $(python3 nachrichten.py tagesschau)
```

## Aliases

I'm lazy, so I have two aliases for watching the German news.

```shell
tagesschau='vlc $(python3 /path/to/nachrichten.py tagesschau)'
heute='vlc $(python3 /path/to/nachrichten.py heute)'
```

## Redirect server

[`server.py`](./server.py) is a simple [Flask](https://flask.palletsprojects.com) web app that will 302-redirect `/tagesschau` and `/heute` to the current videos - useful for when you need a permanent URL ([ht @codingcatgirl](https://twitter.com/codingcatgirl/status/1329616222909063168)).
