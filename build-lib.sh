#!/bin/dash

go clean -modcache -cache
go mod tidy

TARGET="macos"
ARCH="arm64"
OUTPUT="build"

LDFLAGS="-s -w -buildid="
TAGS="with_gvisor,with_quic,with_wireguard,with_dhcp,with_ech,with_low_memory"

CGO_ENABLED=1 GOOS=darwin GOARCH=$ARCH go build -v \
    -buildmode=c-shared \
    -trimpath \
    -buildvcs=false \
    -ldflags="$LDFLAGS" \
    -tags="$TAGS" \
    -o "$OUTPUT/$TARGET/$ARCH/libqbox.dylib" \
    ./export/ffi.go