# Alafi
Simple exchange 

## Requirements
- [Task](https://taskfile.dev/installation/)
- [PDM](https://pdm-project.org/en/latest/#installation)

## How to setup local environment?
1. Clone the repository.
2. Run `pdm install -G:all --dev` to install the dependencies.

## How to Run?
1. Create a `.config.yaml` file from the `.config.yaml.example` file.
2. Run `task serve` to start the development server.
3. For simultaneous settle, run `task settle` in another process.

## How to Test?
1. Run `task test` to run the tests.

