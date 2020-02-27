// Package routes defines routes for the app
package routes

import (
	"bytes"
	"context"
	"encoding/csv"
	"encoding/json"
	"io/ioutil"
	"net/http"
	"net/url"
	"time"

	log "github.com/sirupsen/logrus"

	"github.com/jackyzha0/reflect-nlp/ingress/db"
)

// APIURL is the address for the nlp service
const APIURL string = "http://nlp-service:30000"

// HealthStatus represents health of ingress (this) and nlp service
type HealthStatus struct {
	ProxyAlive bool `json:"proxyAlive"`
	ModelAlive bool `json:"modelAlive"`
}

// Intent represents a single user intent
type Intent struct {
	Intent string `json:"intent" bson:"intent"`
	URL    string `json:"url" bson:"url"`
}

// Export returns all intents as a CSV
func Export(w http.ResponseWriter, r *http.Request) {
	rows, err := db.FetchIntents()

	if err != nil {
		log.Warnf("Error exporting intents to CSV: %s", err.Error())
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	b := &bytes.Buffer{}
	wr := csv.NewWriter(b)

	for _, intent := range rows {
		record := []string{intent.Url, intent.Intent, intent.Time}
		wr.Write(record)
	}

	wr.Flush()

	w.Header().Set("Content-Type", "text/csv")
	w.Header().Set("Content-Disposition", "attachment;filename=intents.csv")
	w.Write(b.Bytes())
}

// Infer unpacks the intent and sends it downstream for inference
func Infer(w http.ResponseWriter, r *http.Request) {
	// check if json
	decoder := json.NewDecoder(r.Body)
	var intent Intent

	err := decoder.Decode(&intent)
	if err != nil {
		log.Errorf("Received non-JSON response body: %s", r.Body)
		http.Error(w, "Received non-JSON response body", http.StatusBadRequest)
		return
	}

	// log attempt to cloud sql
	err = db.LogIntent(intent.URL, intent.Intent)
	if err != nil {
		log.Errorf("Error saving intent to CloudSQL: %s", err.Error())
	}

	// proxy req to python server
	log.Infof("Processing intent '%s'", intent.Intent)
	intentValues := url.Values{"intent": {intent.Intent}}
	resp, err := http.PostForm(APIURL+"/api", intentValues)
	if err != nil {
		log.Infof("Error when getting downstream, got response %+v", err)
		http.Error(w, "Error when getting downstream", http.StatusInternalServerError)
		return
	}

	// read response body
	defer resp.Body.Close()
	bodyBytes, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Fatalf("Got error reading response body: %s", err.Error())
	}

	// bubble response from python
	w.WriteHeader(resp.StatusCode)
	w.Write(bodyBytes)
}

// helper for checking downstream health
func checkDownStreamHealth() bool {
	ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
	defer cancel()
	req, err := http.NewRequest("GET", APIURL, nil)

	if err != nil {
		log.Errorf("Request error: %+v", err)
	}

	resp, err := http.DefaultClient.Do(req.WithContext(ctx))

	if err != nil || resp.StatusCode != http.StatusOK {
		log.Errorf("Error when getting downstream, got response %+v", err)
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
