package db

import (
	"context"
	"database/sql"
	"errors"
	"time"

	log "github.com/sirupsen/logrus"

	// import mysql driver
	_ "github.com/go-sql-driver/mysql"
)

// InsertQuery is a prepared SQL query of form url, intent, date
const InsertQuery string = "INSERT INTO intents VALUES(?, ?, ?)"

var db *sql.DB

var connected bool
// ErrNotConnected should be thrown when there is no established connection to the database
var ErrNotConnected error = errors.New("No connection to database")

// RetryTimeout is the time to wait before reattempting database connection
const RetryTimeout time.Duration = 10 * time.Second
// PingTimeout is the time to wait before cancelling database ping context
const PingTimeout time.Duration = 3 * time.Second
// DevEnv toggles between SQL addresses for local or prod development
const DevEnv = false

type Intent struct {
	Url string
	Intent string
	Time string
}

// FetchIntents returns a query containing all intents
func FetchIntents() ([]Intent, error) {
	if connected {
		rows, err := db.Query("SELECT * FROM intents")
		defer rows.Close()

		intents := []Intent{}

		for rows.Next() {
			i := Intent{}
			if err := rows.Scan(&i.Url, &i.Intent, &i.Time); err != nil {
				log.Fatal(err)
			} else {
				intents = append(intents, i)
			}
		}

		return intents, err
	}

	return nil, ErrNotConnected
}

// LogIntent inserts log entry into cloudsql db
func LogIntent(url, intent string) error {
	if connected {
		dt := time.Now().Truncate(time.Minute).String()

		q, err := db.Prepare(InsertQuery)
		defer q.Close()

		if err != nil {
			log.Warnf("Erroring logging intent: %s", err.Error())
		} else {
			log.Infof("Performing insert op")
			_, err = q.Exec(url, intent, dt)

			if err != nil {
				log.Warnf("Erroring logging intent: %s", err.Error())
			}
		}

		return err
	}
	return ErrNotConnected
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

func createTable() error {
	ctx, cancel := context.WithTimeout(context.Background(), PingTimeout)
	defer cancel()

	// ping database
	err := db.PingContext(ctx)

	if err != nil {
		return err
	}

	connected = true

	_, err = db.Exec("CREATE TABLE IF NOT EXISTS intents (url varchar(255), intent varchar(255), date varchar(255));")
	return err
}

func init() {
	connected = false
	db = connectDB()
	err := createTable()

	if err != nil {
		panic(err)
	}

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
