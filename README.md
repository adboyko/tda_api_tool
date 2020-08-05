## TDAmeritrade API Reader

### What is it?
This tool latches into a TDA Developer app and, using TDA's OAUTH, leverages 
your Brokerage account to collect price data for desired tickers.

### What isn't it?
A full-fledge, production ready utility developed by a professional.
I'm still learning. Input is welcome. Forks and PRs are welcome.

### How to use it?
- Clone this repo
- Preferably, set up a venv for the local clone
- `pip install -r requirements.txt`
- On first run: `python tdam.py`
  - Subsequent runs will give Help Dialog if already OAUTH'd
- For help dialog:
  - `python tdam.py`,
  - `python tdam.py -h`, or
  - `python tdam.py --help`

Be sure to routinely check for updates with `git pull`!

### Planned TODOs:
- [ ] Add symbol memory storage (DB or file?)
- [ ] Add ticker price history storage 
- [ ] Output data to an excel sheet on demand
- [ ] Learn UI and draw data in realtime
- [ ] Learn how to write tests and implement them here