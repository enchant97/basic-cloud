# Basic Cloud
A 'Cloud' application with a web interface and web API. This allows you to run your own basic cloud that forgets about most of the useless features.

You could even pair this with a NAS for a fancy web interface and network shares.

> Take note this project is currently in early stages of development, this warning will be removed when v1.0 is released

## Features
- User Accounts
- Personal and shared share
- Fancy web interface using modern technology
- Fast-Api server that allows communication between companion apps (and the web interface)
- File
    - Uploading
    - Downloading
    - Deletion
- Folder
    - Creation
    - Downloading
    - Contents Viewing
    - Deletion

## Companion Apps
These are apps that are written separately from this project but will communicate with the API server.

> These are completely optional as the built-in web interface has all important features.

| Platform | Interface | Language | Repo |
|:---------|:----------|:---------|:-----|
| Desktop  | GUI/CLI   | C# .Net  | [here](https://github.com/enchant97/basic-cloud-companion) |

## More Docs
[here](docs/index.md)

## License
Copyright (C) 2021 Leo Spratt

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
