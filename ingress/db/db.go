package db

import (
	"database/sql"
	"fmt"
	"time"

	log "github.com/sirupsen/logrus"

	_ "github.com/go-sql-driver/mysql"
)

var db sql.DB

// insert log entry to cloudsql db
func LogIntent(url, intent string) error {
	dt := time.Now().String()
	qString := fmt.Sprintf("INSERT INTO intents VALUES(%s, %s, %s)", url, intent, dt)
	log.Infof("Performing DB query: %s", qString)

	insertOp, err := db.Query(qString)
	defer insertOp.Close()

	return err
}

func init() {
	// private ip, nice try
	db, err := sql.Open("mysql", "root@unix(/cloudsql/reflect-backend:us-central1:reflect-db)/intents")

	// if there is an error opening the connection, handle it
	if err != nil {
		log.Fatalf("Fatal error %s", err.Error())
	}

	// check connection
	err = db.Ping()
	if err != nil {
		log.Fatalf("Fatal error %s", err.Error())
	}
}
