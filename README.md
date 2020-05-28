# Tiny URL
Service which generates Tiny URLs

# Description
Python Flask service that creates and serves Tiny URLs.  Uses Rust Python bindings for speedy shortner.

# Requirements

Python 3.7+ (https://www.python.org/downloads/)
Docker 18+ (https://docs.docker.com/engine/install/ubuntu/)
Rust 1.42.0+ (https://www.rust-lang.org/tools/install)

# Building

## Build Dev

Build pip dependencies dev

```
make build-dev
```

## Build Production

Build pip dependencies production

```
make build
```

# Running

## Running Development Mode

```
make run HOST=<host ip or 0.0.0.0>
```

## Running Production Deployment

```
<Todo>
```

# Routes

Index
```
/
```
HTML Index for users to create Tiny Urls

Lookup
```
/<lookup key>/
```
Provide key that was provided when URL was created to redirect to that URL

Add
```
/add/
```
Creates Tiny URL.  Requires POST with formdata ?url=<encoded url>

Stats
```
/stats/
```
Collected stats for short url

# Tests

To run unit tests:

```
make test
```
