package main

// #include <stdlib.h>
// #include <stdint.h>
import "C"

import (
	"unsafe"
	"github.com/australiaelon/QBox/libqbox"
)

//export QBoxStart
func QBoxStart(configBase64 *C.char) C.uint64_t {
	configStr := C.GoString(configBase64)
	instanceID, err := libqbox.StartWithBase64Config(configStr)
	if err != nil {
		return 0
	}

	return C.uint64_t(instanceID)
}

//export QBoxStop
func QBoxStop(instanceID C.uint64_t) C.int {
	id := uint64(instanceID)
	err := libqbox.Stop(id)
	if err != nil {
		return C.int(0)
	}

	return C.int(1)
}

//export QBoxVersion
func QBoxVersion() *C.char {
    versionBase64, err := libqbox.GetVersionBase64()
	if err != nil {
		return C.CString("")
	}

	return C.CString(versionBase64)
}

//export QBoxFreeString
func QBoxFreeString(str *C.char) {
	if str != nil {
		C.free(unsafe.Pointer(str))
	}
}

func main() {
	// This needs to be here for CGO
}