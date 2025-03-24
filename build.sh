#!/bin/dash

go clean -cache
go clean -modcache
go mod tidy

TAGS="with_gvisor,with_quic,with_wireguard,with_ech,with_utls,with_clash_api"
LDFLAGS="-s -w -buildid="

go build -v \
    -trimpath \
    -buildvcs=false \
    -tags="$TAGS" \
    -ldflags="$LDFLAGS" \
    -o qbox \
    ./cmd/qbox

TARGET="macos"
ARCH="arm64"
OUTPUT="build"
TAGS="with_quic,with_wireguard,with_dhcp,with_low_memory"
LDFLAGS="-s -w -buildid="

CGO_ENABLED=1 GOOS=darwin GOARCH=$ARCH go build -v \
    -buildmode=c-shared \
    -trimpath \
    -buildvcs=false \
    -ldflags="$LDFLAGS" \
    -tags="$TAGS" \
    -o "$OUTPUT/$TARGET/$ARCH/libqbox.dylib" \
    ./export/ffi.go

TARGET="macos"
ARCH="arm64"
OUTPUT="build"
TAGS="with_qbox,with_quic,with_wireguard,with_dhcp,with_low_memory"
LDFLAGS="-s -w -buildid="

CGO_ENABLED=1 GOOS=darwin GOARCH=$ARCH go build -v \
    -buildmode=c-shared \
    -trimpath \
    -buildvcs=false \
    -ldflags="$LDFLAGS" \
    -tags="$TAGS" \
    -o "$OUTPUT/$TARGET/$ARCH/libqbox.dylib" \
    ./export/ffi.go