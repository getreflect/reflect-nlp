// Package middleware defines possible middleware
// that can be used by the router.
package middleware

import (
	"net"
	"net/http"
	"sync"
	"time"

	"golang.org/x/time/rate"

	log "github.com/sirupsen/logrus"
)

// UserExpiryTime is the time before deleting user from User Map
const UserExpiryTime time.Duration = 3 * time.Minute

// MapRefreshRate is how often we check the map for expired users
const MapRefreshRate time.Duration = 1 * time.Minute

// AvgTokenRate is the limit of average token consumption
const AvgTokenRate rate.Limit = 1

// MaxTokenRate is the limit of spike token consumption
const MaxTokenRate int = 2

// User holds the rate limiter for each visitor and the last time that the visitor was seen.
type User struct {
	limiter  *rate.Limiter
	LastSeen time.Time
}

// Users is an in memory map of IP -> *User
var Users = make(map[string]*User)

var mu sync.RWMutex

// Run a background goroutine to remove old entries from the visitors map.
func init() {
	log.Info("Started background goroutine...")
	go cleanupVisitors()
}

func getUser(ip string) (*User, bool) {
	mu.RLock()
	defer mu.RUnlock()

	user, exists := Users[ip]
	return user, exists
}

func createNewLimiterForUser(ip string) *rate.Limiter {
	mu.Lock()
	defer mu.Unlock()

	limiter := rate.NewLimiter(AvgTokenRate, MaxTokenRate)

	Users[ip] = &User{limiter, time.Now()}
	return limiter
}

func updateLastSeen(u *User) {
	mu.Lock()
	defer mu.Unlock()
	u.LastSeen = time.Now()
}

func getLimiter(ip string) *rate.Limiter {
	user, exists := getUser(ip)

	// check if IP in map
	if !exists {
		return createNewLimiterForUser(ip)
	}

	// Update the last seen time for the visitor.
	updateLastSeen(user)
	return user.limiter
}

// Every minute check the map for visitors that haven't been seen for
// more than 3 minutes and delete the entries.
func cleanupVisitors() {
	for {
		time.Sleep(MapRefreshRate)

		mu.Lock()

		// iterate users
		for ip, v := range Users {

			// check if expired
			if time.Now().Sub(v.LastSeen) > UserExpiryTime {
				// delete user with that IP if expired
				delete(Users, ip)
			}
		}

		mu.Unlock()
	}
}

func getIP(r *http.Request) string {
	ip := r.Header.Get("X-REAL-IP")
	if ip == "" {
		ip = r.Header.Get("X-FORWARDED-FOR")
	}
	if ip == "" {
		ip, _, _ = net.SplitHostPort(r.RemoteAddr)
	}
	return ip
}

// RateLimit is a middleware to prevent a single IP from performing too many reqs
func RateLimit(req http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		ip := getIP(r)

		log.Infof("Received request: %s", ip)

		limiter := getLimiter(ip)

		// if rate limited, return 429
		if !limiter.Allow() {
			http.Error(w, http.StatusText(429), http.StatusTooManyRequests)
			return
		}

		// else continue
		req.ServeHTTP(w, r)
	}
}
