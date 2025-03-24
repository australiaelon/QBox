//go:build !with_qbox

package main

import (
	_ "github.com/sagernet/sing-box/protocol/naive"
	_ "github.com/sagernet/sing-box/protocol/shadowsocks"
	_ "github.com/sagernet/sing-box/protocol/shadowtls"
	_ "github.com/sagernet/sing-box/protocol/ssh"
	_ "github.com/sagernet/sing-box/protocol/tor"
	_ "github.com/sagernet/sing-box/protocol/trojan"
	_ "github.com/sagernet/sing-box/protocol/vless"
	_ "github.com/sagernet/sing-box/protocol/vmess"
)

func init() {
}