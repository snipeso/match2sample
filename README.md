# Match2Sample

## how to run

- in terminal write:
- `export participant=P00 session=0`
- `exp-match2sample`

## How to make it executable

1. make sure there is the file exp-match2sample
2. run `code ~/.bashrc` in terminal
3. add at the bottom: `export PATH=~/Projects/match2sample/:$PATH`

Then from a new terminal, you can run directly `exp-match2sample` and it starts!

## How to reproduce the env

- run `cp {env} .`
- run `pyvenv env`

## Design

- 3 seconds to memorize either 1, 3 or 6 symbols
- 7 seconds retention
- 3 seconds reponse (maybe do 2 6 and 2?)
- 10 trials of each size, so 30 per block, tot 3 blocks

## Todo

- check literature again
- set a mask! to avoid after-images helping memory
- make demo version
- reset kb rt
- prolong break
- counterbalance matches and not, such that half of match trials are per level

### Eventual TODOs

## Notes

## Credits

Stimuli come from the "aurebesh alphabet" used in Star Wars
