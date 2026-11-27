// health_server is a tiny deterministic HTTP workload used only inside E8's
// disposable local containers. It has no external dependencies or credentials.
package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"time"
)

func main() {
	listen := flag.String("listen", "127.0.0.1:18080", "listen address")
	release := flag.String("release", "local", "synthetic release identifier")
	status := flag.Int("status", http.StatusOK, "response status for /probe")
	body := flag.String("body", "azure-cloudops-local-probe", "synthetic response body")
	flag.Parse()
	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("X-Release", *release)
		w.WriteHeader(http.StatusOK)
		_, _ = fmt.Fprintln(w, "healthy")
	})
	mux.HandleFunc("/probe", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("X-Release", *release)
		w.WriteHeader(*status)
		_, _ = fmt.Fprintln(w, *body)
	})
	server := &http.Server{Addr: *listen, Handler: mux, ReadHeaderTimeout: 2 * time.Second}
	log.Fatal(server.ListenAndServe())
}
