package db

import (
	"context"
	"database/sql"
	"errors"
	"time"

	log "github.com/sirupsen/logrus"

	_ "github.com/go-sql-driver/mysql"
)

// url, intent, date
const InsertQuery string = "INSERT INTO intents VALUES(?, ?, ?)"

var db *sql.DB

// connection is down
var connected bool

var NotConnected error = errors.New("No connection to database")

const RetryTimeout time.Duration = 10 * time.Second
const PingTimeout time.Duration = 3 * time.Second
const DevEnv = false

// insert log entry to cloudsql db
func LogIntent(url, intent string) error {
	if connected {
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

	return NotConnected
}

func connectDB() *sql.DB {
	var connstr string
	if DevEnv {
		connstr = "root@tcp(localhost)/intents"
	} else {
		connstr = "application:appPass123@tcp(localhost)/intents"
	}

	log.Infof("Attempting connection to database [%s]", connstr)
	db, _ = sql.Open("mysql", connstr)
	return db
}

func init() {
	connected = false
	db = connectDB()

	go func() {
		for {
			ctx, cancel := context.WithTimeout(context.Background(), PingTimeout)
			defer cancel()

			// ping database
			err := db.PingContext(ctx)

			// if no connection, set channel, log, and attempt to reconnect
			if err != nil {
				connected = false
				log.Errorf("Connection broke: %s, attempting reconnect.", err.Error())
				db = connectDB()
			} else {
				connected = true
			}

			time.Sleep(RetryTimeout)
		}
	}()
}
