## Audio metadata extractors

Scripts for intrinsic *WAV* metadata extraction.

## Description

Small set of tools for custom *WAV* metadata extraction contained in the commentary section of RIFF headers.

## Install
In order to use the *wamd* extractor for wildlife acoustics recordings, *guano* must be installed:

```
pip install guano

```
## Usage

For each submodule there is a *get_info* function that accepts a path and returns custom metadata as a dictionary. Example:

```
from audio.amoth_info import get_info

path = '/path/to/wav/mywav.wav'
info = get_info(path)

```


