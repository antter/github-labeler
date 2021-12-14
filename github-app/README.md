# github-issue-labeler

> A GitHub App built with [Probot](https://github.com/probot/probot) that is a prototype of an app built for labelling github issues

## Setup

```sh
# Install dependencies
npm install

# Run the bot
npm start
```

## Docker

```sh
# 1. Build container
docker build -t github-issue-labeler .

# 2. Start container
docker run -e APP_ID=<app-id> -e PRIVATE_KEY=<pem-value> github-issue-labeler
```

## Contributing

If you have suggestions for how github-issue-labeler could be improved, or want to report a bug, open an issue! We'd love all and any contributions.

For more, check out the [Contributing Guide](CONTRIBUTING.md).

## License

[ISC](LICENSE) © 2021 anthony ter-saakov <anthonytersaakov@gmail.com>
