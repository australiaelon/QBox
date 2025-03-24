#!/bin/dash

go clean -cache
go clean -modcache
go mod tidy

LDFLAGS="-s -w -buildid="
TAGS="with_gvisor,with_quic,with_wireguard,with_dhcp,with_ech,with_low_memory"

go build -v \
    -trimpath \
    -buildvcs=false \
    -tags="$TAGS" \
    -ldflags="$LDFLAGS" \
    -o qbox \
    ./cmd/qbox