# QuantAQ Command Line Interface (CLI)

[![PyPI version](https://badge.fury.io/py/quantaq-cli.svg)](https://badge.fury.io/py/quantaq-cli)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/quant-aq/cli/blob/master/LICENSE)
![run and build](https://github.com/quant-aq/cli/workflows/run%20and%20build/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/quant-aq/cli/branch/master/graph/badge.svg)](https://codecov.io/gh/quant-aq/cli)

This package provides easy-to-use tools to munge data associated with QuantAQ air quality sensors. 

## Documentation

Full documentation can be found [here](https://quant-aq.github.io/cli/).

## Dependencies

This tool is built for Python 3.6.1+ and has the following key dependencies

```
python = "^3.6.1"
pandas = "^1.0.4"
click = "^7.1.2"
pyarrow = "^0.17.1"
```

More details can be found in the `pyproject.toml` file at the base of this repository.

## Installation

Install from PyPI

```sh
$ pip install quantaq-cli
```

It can also be added as a dependency using Poetry

```sh
$ poetry add quantaq-cli
```


If you would like to install locally, you can clone the repository and install directly with Poetry

```sh
$ poetry install
```

## Testing

All tests are automagically run via GitHub actions and reports are uploaded directly to codecov. For results to these runs, click on the badges at the top of this file. In addition, you can run tests locally


```sh
$ poetry run coverage run -m unittest discover
```

## Development

Development takes place on GitHub. Issues and bugs can be submitted and tracked via the [GitHub Issue Tracker](https://github.com/quant-aq/cli/issues) for this repository.


## License

Copyright 2020 QuantAQ, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

```
http://www.apache.org/licenses/LICENSE-2.0
```

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.