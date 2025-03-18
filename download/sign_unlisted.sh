#!/bin/sh

source .env
web-ext sign -s . -a artifacts --api-key="$WEB_EXT_API_KEY" --api-secret="$WEB_EXT_API_SECRET" --channel="$WEB_EXT_CHANNEL"