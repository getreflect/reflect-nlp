package db

import (
	"database/sql"
	"time"

	log "github.com/sirupsen/logrus"

	_ "github.com/go-sql-driver/mysql"
)

// url, intent, date
const InsertQuery string = "INSERT INTO intents VALUES(?, ?, ?)"

var db *sql.DB

// insert log entry to cloudsql db
func LogIntent(url, intent string) error {
	dt := time.Now().Truncate(time.Minute).String()

	q, err := db.Prepare(InsertQuery)
	defer q.Close()

	if err != nil {
		log.Warnf("Erroring logging intent: %s", err.Error())
	}

	log.Infof("Performing insert op")
	_, err = q.Exec(url, intent, dt)

	if err != nil {
		log.Warnf("Erroring logging intent: %s", err.Error())
	}

	return err
}

func init() {
	// uses Cloud SQL Proxy Docker image
	db, _ = sql.Open("mysql", "/intents")

	// check connection
	err := db.Ping()
	if err != nil {
		log.Fatalf("Fatal error %s", err.Error())
	}
}
