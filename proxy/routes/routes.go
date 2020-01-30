// Package routes defines routes for the app
package routes

import (
	"net/http"
	"encoding/json"

	// log "github.com/sirupsen/logrus"
)

type HealthStatus struct {
	ProxyAlive bool `json:"proxyAlive"`
	ModelAlive bool `json:"modelAlive"`
}

// Infer unpacks the intent and sends it downstream to inference
func Infer(w http.ResponseWriter, r *http.Request) {

}

func checkDownStreamHealth() bool {
	resp, err := http.Get(":80")
	if err != nil  || resp.StatusCode != http.StatusOK {
		return false
	}
	return true
}

// Health returns health of proxy and downstream
func Health(w http.ResponseWriter, r *http.Request) {
    data := HealthStatus{ModelAlive: checkDownStreamHealth(), ProxyAlive: true}
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(data)
}