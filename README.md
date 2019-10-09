# Asyncio Wiki Parser

> Recursive parser to crawl wikipedia links in depths

## MVP Release v1.0

### How to Run (Guide):

1. Clone or download this repo.
2. Go to repo folder
3. Run `python3 main.py --depth 2 --url 'https://en.wikipedia.org/wiki/Horizon_Guyot'`. Depth and url - are parameters, so you could choose them on your own.
4. Wait until process ends.
5. Enjoy your crawled data at `crawl.db` file.

#### Warning: The more depth - the longer it will crawl, for example depth of 2 from given url takes about 12 minutes to be done and collects more than 20000 of urls. Every increment of depth will significanllty increase processing time.

### Added notification to be sure that data is crawling and script works. (A bit noisy, but at least gives us understanding what is going on)