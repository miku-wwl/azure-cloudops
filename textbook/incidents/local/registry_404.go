// registry_404 is a loopback-only, deterministic OCI Distribution API fixture.
// It serves successful /v2/ discovery and an actual HTTP 404 for every image
// manifest, allowing kubelet/containerd failure evidence without contacting a
// public registry or representing the fixture as Azure Container Registry.
package main

import (
	"encoding/json"
	"flag"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
)

type requestLog struct {
	At        string `json:"at_utc"`
	Method    string `json:"method"`
	Path      string `json:"path"`
	Status    int    `json:"status"`
	ErrorCode string `json:"error_code,omitempty"`
}

func main() {
	listen := flag.String("listen", "127.0.0.1:5000", "loopback registry endpoint")
	logFile := flag.String("log", "/tmp/ir07-registry.jsonl", "request log path inside the disposable node")
	flag.Parse()
	file, err := os.OpenFile(*logFile, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0600)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()
	logger := log.New(file, "", 0)
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		status := http.StatusNotFound
		errorCode := ""
		if r.URL.Path == "/v2/" {
			status = http.StatusOK
			w.Header().Set("Docker-Distribution-Api-Version", "registry/2.0")
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(status)
			_, _ = w.Write([]byte("{}\n"))
		} else if strings.Contains(r.URL.Path, "/manifests/") {
			errorCode = "MANIFEST_UNKNOWN"
			w.Header().Set("Docker-Distribution-Api-Version", "registry/2.0")
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(status)
			_, _ = w.Write([]byte(`{"errors":[{"code":"MANIFEST_UNKNOWN","message":"manifest unknown: synthetic local fixture"}]}`))
		} else {
			w.WriteHeader(status)
		}
		entry, _ := json.Marshal(requestLog{At: time.Now().UTC().Format(time.RFC3339Nano), Method: r.Method, Path: r.URL.Path, Status: status, ErrorCode: errorCode})
		logger.Print(string(entry))
	})
	log.Fatal(http.ListenAndServe(*listen, nil))
}
